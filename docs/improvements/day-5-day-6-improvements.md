# Improvement Scopes — Day 5 & Day 6 Concepts

Scope: improvements applying **TS Day 5 (Classes)**, **TS Day 6 (Generics)**, **Python Day 5 (Exceptions)**, and **Python Day 6 (Functions & Built-ins)** concepts to the actual `frontend/` and `backend/` codebases. Findings are grouped by topic, each with file:line, current behavior, and the concrete fix.

Reference material: `training-core/language-syntax/ts/src/day-5.ts` (parameter properties, inheritance/access modifiers, abstract classes, getters), `day-6.ts` (generic functions, `extends keyof`/constraint generics, generic classes, generic `apiRequest<T>`), `training-core/language-syntax/python/day-5.py` (try/except/else/finally, multiple except blocks per error type), `day-6.py` (typed function signatures, default parameters, built-ins).

---

## Topic 1: TypeScript Classes (Day 5)

### 1.1 No error-subclass hierarchy — backend's rich exception hierarchy collapses into one flat frontend class
**Files:** `frontend/src/api/types/common.ts:14-34` vs. `backend/app/core/exceptions.py:1-56`

The backend models errors with a proper `AppBaseException` hierarchy — `ResourceNotFoundException`, `InvalidUUIDException`, `ConflictException`, `UnauthorizedException`, `DatabaseException` — each with its own `status_code`/`error_code`/`message`. The frontend throws all of them through a single flat `BaseException`, then treats `error_code` as an opaque string wherever it's read (`useGroceryStore.ts:94,115`: `` `${err.error_code}: ${err.message}` ``). This is exactly the inverse of Day 5 Exercise 2/3 (`Employee extends Person`, `Circle`/`Rectangle extends Shape`) — there's no subclassing, so callers can't `instanceof`-narrow to give different UI treatment per error type (e.g. redirect-to-login on `UnauthorizedError` vs. a toast on `ConflictError`) the way `useGroceryStore.ts:65,77,92,113` already narrows generically to `BaseException`.

**Fix:** mirror the backend hierarchy with subclasses that carry their `error_code` as a literal instead of a plain `string`:

```ts
export class NotFoundError extends BaseError {}
export class ConflictError extends BaseError {}
export class UnauthorizedError extends BaseError {}

export function toBaseError(payload?: BaseErrorPayload): BaseError {
    switch (payload?.error_code) {
        case 'resource_not_found': return new NotFoundError(payload);
        case 'conflict': return new ConflictError(payload);
        case 'unauthorized': return new UnauthorizedError(payload);
        default: return new BaseError(payload);
    }
}
```

so `axiosInstance.ts:65` can construct the specific subclass and callers can write `if (err instanceof ConflictError)` instead of comparing `err.error_code === 'conflict'` by hand.

### 1.2 Constructor re-implements field defaults instead of using parameter properties / a single assignment
**File:** `frontend/src/api/types/common.ts:14-29`

```ts
export class BaseError extends Error implements BaseErrorPayload {
    status: string = 'Fail';
    error_code: string = 'INTERNAL_SERVER_ERROR';
    message: string = 'Something went wrong on our end.';
    detail: string = 'No additional details provided.';

    constructor(data?: Partial<BaseErrorPayload>) {
        super(data?.message || 'Something went wrong on our end.');
        this.name = 'BaseError';
        if (data) {
            this.status = data?.status || this.status;
            this.error_code = data?.error_code || this.error_code;
            this.message = data?.message || this.message;
            this.detail = data?.detail || this.detail;
        }
    }
    ...
```

Every field's default is declared twice: once as a property initializer, once again as the `|| this.x` fallback in the constructor body — plus the literal `'Something went wrong on our end.'` string is duplicated a third time in the `super()` call. Day 5 Exercise 1's parameter-properties pattern (`constructor(readonly id: number, public name: string, private age: number) {}`) exists precisely to collapse this kind of "declare + assign" duplication.

**Fix:** keep the field defaults as the single source of truth and merge with `Object.assign`:

```ts
constructor(data?: Partial<BaseErrorPayload>) {
    super(data?.message ?? BaseError.DEFAULT_MESSAGE);
    this.name = 'BaseError';
    Object.assign(this, data);
}
```

(swapping `||` for `??` also stops an intentional empty-string `detail` from being silently overwritten by the default, which the current `||` chain would do).

---

## Topic 2: TypeScript Generics (Day 6)

### 2.1 Every API function repeats the same `IApiResponse<T>` unwrap instead of a generic helper
**Files:** `frontend/src/api/endpoints/GroceryApi.ts:16-45`, `frontend/src/api/endpoints/AuthApi.ts:8-11`

```ts
const response = await axiosInstance.get<IApiResponse<GroceryListResponse[]>>(...);
return response.data.data...
```

This `axiosInstance.<method><IApiResponse<T>>(url, ...).then(res => res.data.data)` shape is repeated 6 times across the two files (`getGroceries`, `getGroceryDetail`, `bulkUpdateShouldInclude`, `login`, etc.) with only the type argument and HTTP verb changing — precisely the case Day 6 Exercise 4 targets with a single generic `apiRequest<T>(url): Promise<T>`.

**Fix:** extract generic wrappers once and call them everywhere instead of unwrapping `.data.data` by hand each time:

```ts
async function apiGet<T>(url: string, params?: object): Promise<T> {
    const response = await axiosInstance.get<IApiResponse<T>>(url, {params});
    return response.data.data;
}
async function apiMutate<T>(method: 'post' | 'put' | 'patch' | 'delete', url: string, body?: unknown): Promise<T> {
    const response = await axiosInstance[method]<IApiResponse<T>>(url, body);
    return response.data.data;
}
```

`getGroceries` becomes `apiGet<GroceryListResponse[]>(API_ENDPOINTS.GROCERY.GROCERY_LIST, filters).then(items => items.map(toGroceryListItem))`, and `login` becomes `apiGet<IUserLoginResponse>(...)`-shaped via `apiMutate`.

### 2.2 Repeated "find/replace by id" logic with no `HasId`-style generic constraint
**File:** `frontend/src/store/useGroceryStore.ts:83-91, 103-111`

```ts
deleteGroceryItem: ... groceries: state.groceries.filter((item) => item.id !== grocery_id) ...
bulkUpdateShouldIncludeItems: ...
    const updated_by_id = new Map(updated_items.map((item) => [item.id, item]));
    groceries: state.groceries.map((item) => updated_by_id.get(item.id) ?? item),
```

Both actions independently reimplement "operate on a collection keyed by `id`" — exactly what Day 6 Exercise 3's `Repository<T extends HasId>` (`add`, `getAll`, `findById`) is meant to generalize. There's no shared, typed notion of "a list of things with an `id`" anywhere in `frontend/src/types`.

**Fix:** add a small generic constraint + helpers (mirroring the training exercise) once, and reuse across both actions and any future list mutation:

```ts
interface HasId { id: string; }
function replaceById<T extends HasId>(items: T[], updates: Map<string, T>): T[] {
    return items.map((item) => updates.get(item.id) ?? item);
}
function removeById<T extends HasId>(items: T[], id: string): T[] {
    return items.filter((item) => item.id !== id);
}
```

### 2.3 `IApiResponse<T>` is the only generic in the codebase — no generic constraint usage (Exercise 2 pattern) anywhere
**File:** n/a (absence check across `frontend/src`)

`grep`ing the frontend for `<T` / `<T,` / `<T>` turns up exactly one generic (`IApiResponse<T>` at `frontend/src/types/IApiResponse.ts:1`). Day 6 Exercise 2's `getProperty<T, K extends keyof T>(obj: T, key: K)` constraint pattern has no counterpart here even though several components read one of several known keys off a typed object dynamically (e.g. the field-change handlers flagged in the earlier Day 3/4 doc, `pages/UpdateGroceryPage.tsx:46,53,61`). Worth revisiting those handlers through a `K extends keyof T` lens now that Day 6 covers it explicitly, rather than the `KeysMatching<T, V>` mapped type suggested previously — both are valid, but a constrained generic function is the more direct application of this week's material.

---

## Topic 3: Python Exceptions (Day 5)

### 3.1 Dead `except` clause — the exceptions it targets are already caught and converted one layer down
**File:** `backend/app/core/dependencies.py:19-24`, compare `backend/app/utils/jwt_helper.py:21-30`

```python
async def get_current_user(...) -> User:
    try:
        user_email = JWTHelper.verify_token(token)
        if user_email is None:
            raise UnauthorizedException()
    except (ExpiredSignatureError, InvalidTokenError):
        raise UnauthorizedException()
```

`JWTHelper.verify_token` already wraps its own `jwt.decode` call and converts `ExpiredSignatureError`/`InvalidTokenError` into `UnauthorizedException` before returning (`jwt_helper.py:23-30`). By the time control returns to `get_current_user`, those two exception types can never reach its `try` block — they're already `UnauthorizedException` by then. The outer `except (ExpiredSignatureError, InvalidTokenError)` is unreachable dead code, the opposite of Day 5 Exercise 4's point (catch the *specific* exception that can actually occur at that call site).

**Fix:** drop the outer `except` — `UnauthorizedException` (a plain `Exception` subclass) already propagates to FastAPI's registered handler (`exception_handlers.py:13`) without needing to be re-caught here:

```python
async def get_current_user(...) -> User:
    user_email = JWTHelper.verify_token(token)
    if user_email is None:
        raise UnauthorizedException()
    user = await AuthRepository(db).get_user_by_email(email=user_email)
    if user is None:
        raise UnauthorizedException()
    return user
```

### 3.2 `validate_uuid` catches `ValueError` but not the exception `UUID(None)` actually raises
**File:** `backend/app/utils/uuid_validation_helper.py:6-10`

```python
def validate_uuid(value):
    try:
        return UUID(value)
    except ValueError:
        raise InvalidUUIDException()
```

`uuid.UUID(...)` raises `ValueError` for a malformed *string*, but raises **`TypeError`** if `value` is `None` or another non-string type (`grocery_id` on `service.py:101-102` comes straight from a path param, so today it's always a `str` and safe — but the function itself makes no such guarantee and is a reusable helper). This is precisely Day 5 Exercise 4's "catch `IndexError` and `ValueError` separately" pattern — here only one of the two possible exception types is handled, and the other raise is left in the same `except` gap rather than getting its own clause.

**Fix:** add the second branch, and chain the original exception so the real cause survives in logs (`raise ... from e`):

```python
def validate_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except (ValueError, TypeError) as e:
        raise InvalidUUIDException() from e
```

### 3.3 Blanket `except Exception` in every repository method, masking unrelated bugs as "database errors"
**File:** `backend/app/features/grocery/repository.py:67-114` (`add_grocery`, `update_grocery`, `delete_grocery`, `bulk_update_should_include`)

```python
async def add_grocery(self, grocery: Grocery) -> Grocery:
    try:
        self.session.add(grocery)
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery
    except Exception:
        await self.session.rollback()
        raise DatabaseException('Failed to add grocery from database')
```

All four methods catch bare `Exception`, which is the opposite of Day 5's lesson (catch `ValueError`/`ZeroDivisionError`/`IndexError` specifically, not everything). A bug unrelated to the database — e.g. an `AttributeError` from a bad model field — gets silently reported to the client as a generic 400 "Database error", hiding the real defect. None of the four `raise DatabaseException(...)` calls chain the original exception either (`from e` is missing everywhere), so even in logs the true cause is discarded.

**Fix:** narrow to the SQLAlchemy exception base and chain the cause:

```python
from sqlalchemy.exc import SQLAlchemyError
...
except SQLAlchemyError as e:
    await self.session.rollback()
    raise DatabaseException('Failed to add grocery from database') from e
```

so a non-database bug fails loudly instead of being reclassified.

### 3.4 Two `except` branches with different exception types but identical, non-distinguishing bodies
**File:** `backend/app/utils/jwt_helper.py:21-30`

```python
except jwt.ExpiredSignatureError:
    raise UnauthorizedException()
except jwt.InvalidTokenError:
    raise UnauthorizedException()
```

Day 5 Exercise 4's point of separate `except` blocks is to give each error type its *own* message ("Index is wrong" vs. "String cannot be converted to int"). Here both branches do exactly the same thing, so the separation adds no value over `except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):` — and it throws away the one piece of information that would actually be useful to a caller (was the token *expired* vs. *malformed*?).

**Fix:** either collapse to one combined `except` for simplicity, or — closer to the exercise's intent — keep them separate but pass a distinguishing `message` into each `UnauthorizedException`:

```python
except jwt.ExpiredSignatureError as e:
    raise UnauthorizedException(message='Session expired, please log in again') from e
except jwt.InvalidTokenError as e:
    raise UnauthorizedException(message='Invalid token') from e
```

### 3.5 Custom exception class never calls `super().__init__(...)`
**File:** `backend/app/core/exceptions.py:11-22`

```python
class AppBaseException(Exception):
    ...
    def __init__(self, error_code=None, detail=None, message=None):
        if error_code is not None:
            self.error_code = error_code
        ...
```

`AppBaseException.__init__` never calls `super().__init__(...)`, so `Exception.args` stays empty and `str(exc)` / default `repr` / uncaught-exception tracebacks all print an empty message instead of something useful. This is the Python-exceptions counterpart to TS Day 5 Exercise 2's `super(id, name, age)` call in `Employee`'s constructor — a subclass constructor should still initialize what its parent expects.

**Fix:** forward the message to the base class:

```python
def __init__(self, error_code=None, detail=None, message=None):
    if message is not None:
        self.message = message
    super().__init__(self.message)
    if error_code is not None:
        self.error_code = error_code
    if detail is not None:
        self.detail = detail
```

---

## Topic 4: Python Functions & Built-ins (Day 6)

### 4.1 Nonsensical default parameter value on three router handlers
**File:** `backend/app/features/grocery/routers/v1/router.py:70, 107, 127`

```python
async def bulk_update_should_include(
        _current_user: User = Depends(get_current_user),
        data: GroceryBulkUpdateSchema = type[GroceryBulkUpdateSchema],
        grocery_service: GroceryService = Depends(get_grocery_service)
):
```

Same pattern repeats for `create_grocery` (`data: GroceryCreateSchema = type[GroceryCreateSchema]`) and `update_grocery` (`data: GroceryUpdateSchema = type[GroceryUpdateSchema]`). `type[GroceryBulkUpdateSchema]` is a `types.GenericAlias` object, not a `GroceryBulkUpdateSchema` instance — it is not a meaningful default value for this parameter, it just happens to work today because FastAPI always receives an actual request body and overrides it. This is a direct miss of Day 6 Exercise 3's point (a default parameter should be a valid, meaningful fallback value for that parameter's type, e.g. `power(base, exponent=2)`) — here the "default" isn't type-compatible with the parameter at all.

**Fix:** these body parameters shouldn't have a default — FastAPI infers "required JSON body" from the bare type annotation:

```python
async def bulk_update_should_include(
        _current_user: User = Depends(get_current_user),
        data: GroceryBulkUpdateSchema,
        grocery_service: GroceryService = Depends(get_grocery_service)
):
```

(if keeping it after the `Depends(...)` defaulted params requires reordering for valid Python syntax, use `Annotated[GroceryBulkUpdateSchema, Body()]` instead of a bare default.)

### 4.2 `verify_token`'s return type hint doesn't match what the function can actually return
**File:** `backend/app/utils/jwt_helper.py:22-26`

```python
@staticmethod
def verify_token(token: str) -> str:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    email: str = payload.get('sub')
    return email
```

`payload.get('sub')` is typed `str` here, but `dict.get` returns `X | None` when the key may be absent — Day 6's exercises are consistent about function signatures matching real return behavior (`safe_divide(a, b) -> float` in day-6.py actually returns `str` on the zero-division branch, which is itself a good negative example to contrast with). `-> str` overstates the guarantee; a caller relying on the annotation wouldn't realize a `None` is possible, and `dependencies.py:20-21` in fact defensively checks `if user_email is None` right after calling it — meaning the real contract is already `str | None`, just not written down.

**Fix:** `def verify_token(token: str) -> str | None:` to match the checked-for-`None` reality at the only call site.

---

## Summary

| # | File | Topic |
|---|------|-------|
| 1.1 | `api/types/common.ts:14-34` vs. `core/exceptions.py` | No error subclass hierarchy mirroring backend |
| 1.2 | `api/types/common.ts:14-29` | Constructor re-implements field defaults instead of parameter properties |
| 2.1 | `api/endpoints/GroceryApi.ts:16-45`, `AuthApi.ts:8-11` | Repeated `IApiResponse<T>` unwrap vs. generic `apiRequest<T>` |
| 2.2 | `store/useGroceryStore.ts:83-91,103-111` | Repeated find/replace-by-id logic, no `HasId` constraint |
| 2.3 | (absence check, `frontend/src`) | `IApiResponse<T>` is the only generic in the codebase |
| 3.1 | `core/dependencies.py:19-24` | Dead `except` clause — already caught one layer down |
| 3.2 | `utils/uuid_validation_helper.py:6-10` | Missing `TypeError` branch + no exception chaining |
| 3.3 | `features/grocery/repository.py:67-114` | Blanket `except Exception` masks unrelated bugs |
| 3.4 | `utils/jwt_helper.py:21-30` | Two except branches, identical non-distinguishing bodies |
| 3.5 | `core/exceptions.py:11-22` | Custom exception never calls `super().__init__()` |
| 4.1 | `routers/v1/router.py:70,107,127` | Type-incompatible default parameter value |
| 4.2 | `utils/jwt_helper.py:22-26` | Return type hint doesn't match actual `None`-possible return |
