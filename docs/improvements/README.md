# Python Core Deep-Dive Review — `backend/`

Review of `backend/app` against the 7 topics in the [Deepen Core Python working
guide](../../../code/training-core/docs/python-core-deep-dive.md): async internals,
generators/iterators/context managers, decorators & metaclasses, type hints,
the memory model, concurrency primitives, and testing. Each section below
follows the guide's own framing — why the topic matters for this stack
(FastAPI + SQLAlchemy async + Redis), what the codebase currently does, and
the concrete fix — with `file:line` references throughout.

This complements `phase-4-caching-improvements.md` (Redis cache-invalidation
bugs) and `phase-3-databases-sql-review.md` — those cover *what* the cache/DB
layer does wrong; this doc covers *how idiomatically* the underlying Python is
written.

---

## 1. Async internals — blocking calls inside `async def`

The guide's headline risk is "you *will* eventually write an `async def`
endpoint that calls a blocking ... call and silently stall every other
request on that worker." This codebase hits that exact case.

### 1.1 Argon2 password hashing blocks the event loop on every register/login request
**Files:** `backend/app/utils/hashing.py:9-16`, called from
`backend/app/features/auth/service.py:68` (`register_user`) and `:76`
(`authenticate_user`) — both reached directly from the async router handlers
in `backend/app/features/auth/routers/v1/router.py:30-58`.

```python
# hashing.py — synchronous, CPU-bound by design
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)          # argon2, ~tens-to-hundreds of ms

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# service.py — called with a bare synchronous call inside async def
async def register_user(self, payload: UserCreateRequestSchema) -> UserCreateResponseSchema:
    ...
    hashed_password = hash_password(payload.password)   # blocks the loop
    ...

async def authenticate_user(self, payload: LoginRequestSchema) -> LoginResponseSchema:
    user = await self.repo.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password):  # blocks the loop
        raise UnauthorizedException()
```

Argon2 is deliberately slow and CPU-bound — that's the whole point of using
it for password hashing. Calling it synchronously from inside a coroutine
means the entire event loop (every other in-flight request on that worker,
not just this one) stalls for the duration of the hash/verify. Under any
concurrent load, `/register` and `/login` are the two endpoints most likely
to produce the "service is up but every request is slow" symptom the guide
calls out.

**Fix:** offload to a thread executor so the CPU-bound work doesn't block the loop:
```python
import asyncio

async def register_user(self, payload: UserCreateRequestSchema) -> UserCreateResponseSchema:
    ...
    loop = asyncio.get_running_loop()
    hashed_password = await loop.run_in_executor(None, hash_password, payload.password)
    ...

async def authenticate_user(self, payload: LoginRequestSchema) -> LoginResponseSchema:
    user = await self.repo.get_user_by_email(payload.email)
    loop = asyncio.get_running_loop()
    if not user or not await loop.run_in_executor(None, verify_password, payload.password, user.password):
        raise UnauthorizedException()
```
(Or wrap it once in `hashing.py` as `hash_password_async`/`verify_password_async` so every caller gets it for free.)

---

## 2. Generators, iterators & context managers

### 2.1 `get_db()` — solid example, worth keeping as the template
**File:** `backend/app/db/session.py:27-29`
```python
async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with async_session_factory() as session:
        yield session
```
This is the textbook FastAPI generator-dependency + context-manager pattern
from the guide's example (`timed_block`) — `async with` guarantees the
session is closed (and any uncommitted transaction rolled back) even if the
request handler raises. No changes needed here; it's the one place in the
codebase that already demonstrates the topic correctly.

### 2.2 The whole grocery table is materialized into memory — no pagination, no streaming
**Files:** `backend/app/features/grocery/repository.py:21-36`,
`backend/app/features/grocery/service.py:120-133`

```python
async def get_groceries(self, filters: GroceryFilterParams | None = None) -> Sequence[Grocery]:
    """Get all groceries, optionally filtered/searched — no pagination for now"""
    stmt = select(Grocery)
    ...
    result = await self.session.execute(stmt)
    return result.scalars().all()          # entire result set in memory, no LIMIT/OFFSET
```
`.scalars().all()` has no `LIMIT`, the service layer then builds a full
`list[GroceryListResponseSchema]` from it, and that whole list is
JSON-serialized into a single Redis key (`service.py:98-102`). This is
exactly the "list vs. generator" tradeoff the guide's export/streaming
example is built around — today it's fine at toy data volumes, but there's
no LIMIT/OFFSET ceiling at all, so both DB memory and the size of the Redis
value grow unbounded with inventory size. Notably, `backend/app/common/pagination.py`
already exists in the repo as an **empty (0-byte) stub** — pagination was
planned but never wired in.

**Fix:** add `limit`/`offset` (or keyset) params to `get_groceries` and page
the Redis cache key per page instead of caching one unbounded blob; fill in
the empty `common/pagination.py` module rather than leaving it dead weight.

---

## 3. Decorators & metaclasses

### 3.1 Zero custom decorators anywhere in the codebase — and the repository layer has the textbook use case sitting unaddressed
**File:** `backend/app/features/grocery/repository.py:68-115`

The same 5-line shape is repeated verbatim in `add_grocery`, `update_grocery`,
`delete_grocery`, and `bulk_update_should_include`:
```python
async def add_grocery(self, grocery: Grocery) -> Grocery:
    try:
        self.session.add(grocery)
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery
    except SQLAlchemyError as e:
        await self.session.rollback()
        raise DatabaseException('Failed to add grocery from database') from e
```
This is precisely the cross-cutting-concern scenario the guide's `@retry`
example targets — a `try/except/rollback/raise` block that every
DB-*writing* method needs identically. A grep across `backend/app` for any
`@decorator` beyond framework ones (`@staticmethod`, `@property`,
`@computed_field`, `@router.*`, `@dataclass`) or for `functools`/`retry`/
`lru_cache` returns nothing — the codebase has no home-grown decorators at
all, so nothing currently guards against a fifth method (e.g. a future
`restock_grocery`) being added without this error handling.

**Fix:**
```python
import functools
from sqlalchemy.exc import SQLAlchemyError

def handle_db_errors(message: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except SQLAlchemyError as e:
                await self.session.rollback()
                raise DatabaseException(message) from e
        return wrapper
    return decorator

class GroceryRepository:
    @handle_db_errors('Failed to add grocery from database')
    async def add_grocery(self, grocery: Grocery) -> Grocery:
        self.session.add(grocery)
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery
```
Cuts ~16 duplicated lines and makes "every write method rolls back and wraps
its error" a property of the decorator, not a convention every future PR has
to remember to copy-paste correctly.

---

## 4. Type hints end-to-end

No `mypy`/`pyright` config exists anywhere in the repo (checked for
`mypy.ini`, `pyproject.toml`, and CI steps — none found), so nothing
currently catches the mismatches below; they'd all be one-line fixes a
type-checker in CI would flag on the first run.

### 4.1 A signature that contradicts its own body
**File:** `backend/app/features/grocery/service.py:48-63`
```python
@staticmethod
def __update_best_price_and_best_seller(
        new_price: int,
        best_price: int,          # <- says "always an int"
        new_seller: Seller,
        best_seller: Seller,
) -> Tuple[int, Seller]:
    if best_price is None:        # <- but the very next line checks for None
        best_price = new_price
        best_seller = Seller.MEENA
        return best_price, best_seller
    ...
```
This is the guide's Q4 interview question made concrete: `mypy` would flag
`best_price is None` as an unreachable/impossible check against a bound
`int`, exactly the class of bug a runtime `isinstance` check wouldn't catch
until it silently returned the wrong value.

**Fix:** `best_price: int | None`.

### 4.2 Inconsistent annotations between sibling methods
**Files:** `backend/app/features/grocery/service.py:135` vs. `:169`;
`backend/app/features/auth/repository.py:11` vs.
`backend/app/features/grocery/repository.py:62`

```python
async def get_grocery_by_id(self, grocery_id) -> GroceryDetailResponseSchema:   # grocery_id: untyped
...
async def delete_grocery(self, grocery_id: str) -> None:                        # grocery_id: str
```
```python
async def get_user_by_email(self, email: str):            # no return type
...
async def get_by_id(self, grocery_id: str) -> Grocery | None:  # return type present
```
Same class, same kind of parameter, typed differently depending on which
method you're reading — the kind of drift a type checker in CI (per the
guide's Section 4 project) exists specifically to stop.

**Fix:** `grocery_id: str` on `get_grocery_by_id`; `-> User | None` on `get_user_by_email`.

### 4.3 Declared type doesn't match its own default value
**File:** `backend/app/features/grocery/models.py:70-74`
```python
best_price: Mapped[int] = mapped_column(
    Integer,
    nullable=True,
    default=0.0        # float default on an int-typed, Integer column
)
```
Harmless today only because `service.py`'s `__prepare_grocery` always
overwrites `best_price` before insert — but it's a one-character
inconsistency between the `Mapped[int]` annotation, the `Integer` column
type, and the literal default that a type checker would catch immediately
and a human reviewer easily won't.

**Fix:** `default=0`.

---

## 5. Memory model (mutable defaults, globals, `__slots__`)

Checked the whole of `backend/app` for the classic
`def f(x=[])`/`def f(x={})` mutable-default-argument bug and for class-level
mutable (`list`/`dict`) attributes — **none found**. `__slots__` isn't used
anywhere, but nothing in this codebase currently instantiates objects at the
scale (millions of rows in one process) where it would pay for itself, so
that's a non-issue for now, not a gap.

### 5.1 The Redis singleton can be silently re-initialized without closing the old connection
**File:** `backend/app/clients/redis_client.py:4-27`
```python
redis_client: Redis | None = None

async def init_redis() -> None:
    global redis_client
    client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    await client.ping()
    redis_client = client     # unconditional overwrite
```
This is the right pattern for a FastAPI lifespan-managed singleton (matches
the guide's point that module-level global state is normal, not automatically
a bug), but there's no guard against `init_redis()` running twice in the same
process — a second call silently replaces `redis_client` and orphans the
first client's connection pool instead of closing it first. Low severity
today (the lifespan context manager only calls it once), but worth guarding
before this is ever called from a test fixture or a hot-reload path.

**Fix:**
```python
async def init_redis() -> None:
    global redis_client
    if redis_client is not None:
        return
    ...
```

---

## 6. Concurrency primitives (`asyncio.gather`, `Lock`, `Queue`, `TaskGroup`)

A grep for `asyncio.gather`, `create_task`, `TaskGroup`, `Semaphore`, `Lock`,
and `Queue` across `backend/app` returns nothing — there's currently no
concurrent-fan-out I/O pattern in the codebase (no batch of outbound calls,
no producer/consumer queue), so most of the guide's Section 6 project
(rate-limited counters, bounded queues) doesn't map onto anything here yet.
One small, real opportunity exists today:

### 6.1 Two independent Redis deletes run sequentially where they could run concurrently
**File:** `backend/app/features/grocery/service.py:110-114`
```python
async def remove_grocery_detail_from_redis(self, grocery_id: str) -> None:
    grocery_detail_cache_key: str = RedisKeyHelper.GROCERY_DETAIL.build_key(grocery_id=grocery_id)
    await self.grocery_cache.delete(grocery_detail_cache_key)   # round-trip 1
    grocery_list_cache_key: str = RedisKeyHelper.GROCERIES.value
    await self.grocery_cache.delete(grocery_list_cache_key)     # round-trip 2, independent of the first
```
Neither `delete` depends on the other's result, so they currently pay two
sequential network round-trips for no correctness benefit.

**Fix:**
```python
import asyncio

async def remove_grocery_detail_from_redis(self, grocery_id: str) -> None:
    grocery_detail_cache_key = RedisKeyHelper.GROCERY_DETAIL.build_key(grocery_id=grocery_id)
    grocery_list_cache_key = RedisKeyHelper.GROCERIES.value
    await asyncio.gather(
        self.grocery_cache.delete(grocery_detail_cache_key),
        self.grocery_cache.delete(grocery_list_cache_key),
    )
```
This is also the pattern to reach for once `phase-4-caching-improvements.md`
Topic 1.4's fix (invalidating N grocery-detail keys after a bulk update) is
implemented — deleting N independent keys is a direct `asyncio.gather(*[...])`
fan-out, not a `for` loop of sequential `await`s.

---

## 7. Testing (`pytest`, fixtures, parametrize, mocking, coverage)

**This is the largest gap in the codebase relative to the guide.**

- **No test files exist.** `find backend -iname "*test*"` (excluding the
  venv) returns nothing — not one `test_*.py`, no `tests/` directory.
- **No testing dependency is even installed.** `backend/requirements.txt`
  has no `pytest`, `pytest-asyncio`, or `httpx`-based test client usage —
  the only test-adjacent thing already present is `httpx`, which is a
  runtime dependency of `fastapi`, not there for `TestClient`/`ASGITransport`
  usage.
- **No config exists for one:** no `pytest.ini`, `pyproject.toml`, or
  `conftest.py` anywhere in the repo.
- **CI deploys straight to production with no test gate.**
  `.github/workflows/deploy.yml` triggers `on: push: branches: [main]` and
  goes straight to `docker compose up -d --build` on the EC2 host — there is
  no `pytest` step, no lint step, nothing between "push to main" and
  "running in prod."

Given the guide's framing — TDD and "modern software quality technique" are
explicitly what the target role is graded on — this is the single highest-
leverage gap to close, and the codebase's own structure (service layer
already separated from the repository layer, repository already separated
from FastAPI/HTTP concerns, `RedisService`/`GroceryRepository` already
constructor-injected rather than imported directly) is already set up to
make mocking straightforward once tests exist. Concretely:

- `GroceryService(repo, grocery_cache)` and `AuthService(repo)` take their
  dependencies as constructor args (`service.py:41`, `auth/service.py:21`) —
  both are already trivially testable with fake/mock repos and no real DB or
  Redis needed for unit tests.
- The one thing standing in the way of *integration* tests against a real
  async DB session is that `db/session.py`'s `async_session_factory` is
  module-level and not itself overridable via a FastAPI dependency override
  fixture yet — worth keeping in mind when the first `conftest.py` is added,
  since `app.dependency_overrides[get_db] = ...` is the standard fix.

**Suggested first step:** add `pytest`, `pytest-asyncio`, and `httpx` (for
`ASGITransport`) to `requirements.txt`, add a `tests/` package mirroring
`app/features/*`, and add a `pytest` step to `deploy.yml` gating the deploy
job — even a handful of service-layer unit tests (mocking `repo`/
`grocery_cache`) would close most of the gap before touching integration
tests against Postgres/Redis.

---

## Summary

| # | Topic | File(s) | Finding |
|---|-------|---------|---------|
| 1.1 | Async internals | `utils/hashing.py:9-16`, `auth/service.py:68,76` | Argon2 hash/verify called synchronously inside `async def`, blocking the event loop on every register/login |
| 2.1 | Generators/context managers | `db/session.py:27-29` | Correct pattern already in use — no change needed |
| 2.2 | Generators/context managers | `grocery/repository.py:21-36`, `grocery/service.py:120-133` | Full table loaded into memory with no pagination/streaming; `common/pagination.py` is an empty stub |
| 3.1 | Decorators | `grocery/repository.py:68-115` | Zero custom decorators anywhere; identical try/rollback/raise block duplicated 4x — textbook `@handle_db_errors` case |
| 4.1 | Type hints | `grocery/service.py:48-63` | `best_price: int` but code branches on `best_price is None` |
| 4.2 | Type hints | `grocery/service.py:135,169`, `auth/repository.py:11` | Inconsistent/missing param & return annotations between sibling methods |
| 4.3 | Type hints | `grocery/models.py:70-74` | `Mapped[int]`/`Integer` column with a float (`0.0`) default |
| 5.1 | Memory model | `clients/redis_client.py:4-27` | Global Redis client can be silently re-initialized without closing the old connection (low severity) |
| 6.1 | Concurrency primitives | `grocery/service.py:110-114` | Two independent Redis deletes run sequentially instead of via `asyncio.gather` |
| 7 | Testing | whole repo, `.github/workflows/deploy.yml` | No tests, no test deps, no test config, no CI gate before deploying to production |
