# Improvement Scopes — Phase 4 Caching & Latency

Scope: improvements to the **Redis cache-aside implementation** (roadmap Phase 4, Topic 14: Caching Strategies) and the **latency header middleware** (Topic 16: Latency Optimization) in `backend/`. Findings are grouped by topic, each with file:line, current behavior, and the concrete fix.

Reference material: `docs/project-goals/system-design-learning-roadmap.md` Phase 4 (Topics 14 & 16); full review with severity/status tracking at `docs/project-staff/phase-4-caching-review.md`.

---

## Topic 1: Redis Cache Invalidation & Key Design (Day/Phase 4 — Caching Strategies)

### 1.1 List cache key ignores query filters — wrong data can be served across filter combinations
**Files:** `backend/app/features/grocery/service.py:120-133`, `backend/app/utils/redis_key_helper.py:6`

```python
async def list_all_groceries(self, filters: GroceryFilterParams | None = None) -> List[GroceryListResponseSchema]:
    grocery_list_cache_key: str = RedisKeyHelper.GROCERIES.value
    cached = await self.grocery_cache.get(grocery_list_cache_key)
    if cached:
        return [GroceryListResponseSchema.model_validate(item) for item in cached]
    groceries = await self.repo.get_groceries(filters)
    result = [GroceryListResponseSchema.model_validate(item) for item in groceries]
    if result:
        await self.add_grocery_list_to_redis(result)
    return result
```

`grocery_list_cache_key` is the single static key `"groceries"` regardless of `filters` (`type`/`current_seller`/`best_seller`/`category`/`should_include`/`search`, all wired through from `routers/v1/router.py:55`). A filtered request populates `"groceries"` with the filtered subset; the next request with *different* filters (or none) reads that same key back and gets the wrong result — not stale data, wrong data.

**Fix:** the simplest correct fix is to only use the cache for the unfiltered "get everything" case, and bypass it entirely whenever any filter/search is present (a per-filter-combination key would also work but then requires pattern-deleting every variant on invalidation — not worth the complexity here):

```python
async def list_all_groceries(self, filters: GroceryFilterParams | None = None) -> List[GroceryListResponseSchema]:
    use_cache = not (filters and (filters.has_conditions() or filters.search))
    grocery_list_cache_key: str = RedisKeyHelper.GROCERIES.value

    if use_cache:
        cached = await self.grocery_cache.get(grocery_list_cache_key)
        if cached:
            logger.info('Returning cached groceries')
            return [GroceryListResponseSchema.model_validate(item) for item in cached]

    groceries = await self.repo.get_groceries(filters)
    logger.info('Get groceries')
    result = [GroceryListResponseSchema.model_validate(item) for item in groceries]
    if use_cache and result:
        await self.add_grocery_list_to_redis(result)
    return result
```

### 1.2 `create_grocery` never invalidates the list cache
**File:** `backend/app/features/grocery/service.py:153-156`

```python
async def create_grocery(self, data: GroceryCreateSchema) -> GroceryCreateResponseSchema:
    grocery = self.__prepare_grocery(data)
    created_grocery = await self.repo.add_grocery(grocery)
    return GroceryCreateResponseSchema.model_validate(created_grocery)
```

A newly created item is invisible to `list_all_groceries` callers for up to `REDIS_TTL` (300s) — the write path never touches the `"groceries"` cache key that the read path just populated.

**Fix:**
```python
async def create_grocery(self, data: GroceryCreateSchema) -> GroceryCreateResponseSchema:
    grocery = self.__prepare_grocery(data)
    created_grocery = await self.repo.add_grocery(grocery)
    await self.grocery_cache.delete(RedisKeyHelper.GROCERIES.value)
    return GroceryCreateResponseSchema.model_validate(created_grocery)
```

### 1.3 `delete_grocery` never invalidates cache
**File:** `backend/app/features/grocery/service.py:169-173`

```python
async def delete_grocery(self, grocery_id: str) -> None:
    grocery = await self.repo.get_by_id(grocery_id)
    if grocery is None:
        raise ResourceNotFoundException(message=GROCERY_NOT_FOUND.format(grocery_id=grocery_id))
    await self.repo.delete_grocery(grocery)
```

The row is gone from Postgres but `grocery:{id}:detail` and the `"groceries"` list key still serve it — `GET /groceries/{id}` returns a cached "found" response for an item that no longer exists.

**Fix:** reuse the same invalidation helper `update_grocery` already calls:
```python
async def delete_grocery(self, grocery_id: str) -> None:
    grocery = await self.repo.get_by_id(grocery_id)
    if grocery is None:
        raise ResourceNotFoundException(message=GROCERY_NOT_FOUND.format(grocery_id=grocery_id))
    await self.repo.delete_grocery(grocery)
    await self.remove_grocery_detail_from_redis(grocery_id)
```

### 1.4 `bulk_update_should_include` never invalidates cache
**File:** `backend/app/features/grocery/service.py:175-188`

```python
async def bulk_update_should_include(
        self, data: GroceryBulkUpdateSchema
) -> List[GroceryUpdateResponseSchema]:
    updated_groceries = await self.repo.bulk_update_should_include(
        data.grocery_ids, data.should_include
    )
    found_ids = {grocery.id for grocery in updated_groceries}
    missing_ids = [str(gid) for gid in data.grocery_ids if gid not in found_ids]
    if missing_ids:
        logger.error(GROCERY_NOT_FOUND.format(grocery_id=", ".join(missing_ids)))
        raise ResourceNotFoundException(
            message=GROCERY_NOT_FOUND.format(grocery_id=", ".join(missing_ids))
        )
    return [GroceryUpdateResponseSchema.model_validate(grocery) for grocery in updated_groceries]
```

`should_include` is updated directly via the repository, bypassing `update_grocery` entirely — so none of the affected items' detail cache entries (or the list cache) get invalidated. Stale `should_include` values can be served for the full TTL after a bulk update.

**Fix:**
```python
async def bulk_update_should_include(
        self, data: GroceryBulkUpdateSchema
) -> List[GroceryUpdateResponseSchema]:
    updated_groceries = await self.repo.bulk_update_should_include(
        data.grocery_ids, data.should_include
    )
    found_ids = {grocery.id for grocery in updated_groceries}
    missing_ids = [str(gid) for gid in data.grocery_ids if gid not in found_ids]
    if missing_ids:
        logger.error(GROCERY_NOT_FOUND.format(grocery_id=", ".join(missing_ids)))
        raise ResourceNotFoundException(
            message=GROCERY_NOT_FOUND.format(grocery_id=", ".join(missing_ids))
        )

    for grocery in updated_groceries:
        await self.remove_grocery_detail_from_redis(str(grocery.id))

    return [GroceryUpdateResponseSchema.model_validate(grocery) for grocery in updated_groceries]
```

### 1.5 Empty list results are never cached
**File:** `backend/app/features/grocery/service.py:131-133`

```python
if result:
    await self.add_grocery_list_to_redis(result)
```

An empty grocery list is never written to cache, so every request against an empty (or, pre-1.1-fix, fully-filtered-out) list falls through to the DB every time. Not a correctness bug — just a missed cache-hit opportunity. Low priority; worth revisiting only if an empty-list endpoint turns out to be hit often, since caching `[]` needs a way to distinguish "cached empty list" from "cache miss" in `RedisService.get` (currently `None` means both "no value" and "falsy JSON value").

---

## Topic 2: Latency Header Formatting (Latency Optimization)

### 2.1 `X-Response-Time` header renders in scientific notation for any response ≥10ms
**File:** `backend/app/middleware/latency_header.py:11`

```python
response.headers["X-Response-Time"] = f"{latency:.2}ms"
```

`.2` with no type character is Python's *general* format spec — 2 **significant figures**, not 2 decimal places. The sibling `RequestLoggerMiddleware` right next to it gets this right with `.2f` (`request_logger.py:29,36`). Verified:

| latency (ms) | `.2` (current) | `.2f` (intended) |
|---|---|---|
| 5.678 | `5.7ms` | `5.68ms` |
| 12.34 | `1.2e+01ms` | `12.34ms` |
| 123.456 | `1.2e+02ms` | `123.46ms` |

Since most real responses take ≥10ms, the header is unreadable (scientific notation) for the majority of requests — defeating the point of a human/dashboard-facing latency header.

**Fix:**
```python
response.headers["X-Response-Time"] = f"{latency:.2f}ms"
```

---

## Summary

| # | File | Topic |
|---|------|-------|
| 1.1 | `features/grocery/service.py:120-133` | List cache key ignores filters — serves wrong data across filter combinations |
| 1.2 | `features/grocery/service.py:153-156` | No cache invalidation on create |
| 1.3 | `features/grocery/service.py:169-173` | No cache invalidation on delete |
| 1.4 | `features/grocery/service.py:175-188` | No cache invalidation on bulk update |
| 1.5 | `features/grocery/service.py:131-133` | Empty list results never cached (low priority) |
| 2.1 | `middleware/latency_header.py:11` | `.2` format spec → scientific notation above 10ms |
