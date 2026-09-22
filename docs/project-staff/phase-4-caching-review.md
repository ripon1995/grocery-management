# Phase 4 Review — 14. Caching Strategies (+ 16. Latency Optimization)

Scope: reviews `docs/project-goals/system-design-learning-roadmap.md` Phase 4, primarily section **"14. Caching Strategies"**, against the real Redis cache-aside implementation added on top of the grocery list/detail endpoints. Also covers the `X-Response-Time` latency header from section **"16. Latency Optimization"** since it landed in the same batch of work. Findings below are grouped by topic, each with file:line, current behavior, and the concrete gap vs. the roadmap's success criteria.

Reviewed: 2026-08-28. Implementation commits: `a7c57fa` (redis docker setup), `b29c5f4` (redis client/service), `22bf48a`/`1d560b9` (list caching), `9cf19fc` (key helper), `01e1ffe` (detail caching), `942f9ba` (invalidate on update), `fab7526`/`fe67c8d`/`d39b424` (latency header middleware).

---

## Topic 14: Caching Strategies

### 14.1 List cache key ignores query filters — 🔴 Open (correctness bug)
**File:** `backend/app/features/grocery/service.py:120-133`, key defined at `backend/app/utils/redis_key_helper.py:6`

`list_all_groceries(filters)` reads and writes the grocery list under one static key, `RedisKeyHelper.GROCERIES` (`"groceries"`), regardless of the `GroceryFilterParams` (`type`, `current_seller`, `best_seller`, `category`, `should_include`, `search`) that the router (`routers/v1/router.py:55`) already accepts and passes in on every call.

**Concrete risk:** a request with `?category=FOOD` populates the `"groceries"` cache key with the filtered subset. The next unfiltered request (or a request with a *different* filter) hits the cache and gets back that filtered subset instead of its own result — wrong data returned, not just a wasted cache miss. This affects every combination of filter params sharing the single key.

**Fix direction:** derive the cache key from the filter params (e.g. hash or serialize `GroceryFilterParams` into the key: `groceries:{type}:{seller}:{category}:{search}...`), or only cache the unfiltered list and bypass the cache whenever `filters.has_conditions()` is true.

### 14.2 No cache invalidation on create — 🔴 Open (correctness bug)
**File:** `backend/app/features/grocery/service.py:153-156`

`create_grocery` writes to the database but never calls `remove_grocery_detail_from_redis` (or otherwise touches the `"groceries"` list key). A newly created item is invisible to `list_all_groceries` callers until the cache entry naturally expires (`REDIS_TTL=300s`).

**Fix direction:** invalidate (or repopulate) the `"groceries"` list cache key at the end of `create_grocery`, same as `update_grocery` already does for the detail+list keys.

### 14.3 No cache invalidation on delete — 🔴 Open (correctness bug)
**File:** `backend/app/features/grocery/service.py:169-173`

`delete_grocery` removes the row from Postgres but never invalidates `grocery:{id}:detail` or the `"groceries"` list key. A deleted item keeps being served from cache — `GET /groceries/{id}` returns a "found" response for an item that no longer exists, and it still shows up in list responses — until TTL expiry.

**Fix direction:** call `remove_grocery_detail_from_redis(grocery_id)` before/after the repository delete, mirroring `update_grocery`.

### 14.4 No cache invalidation on bulk update — 🔴 Open (correctness bug)
**File:** `backend/app/features/grocery/service.py:175-188`

`bulk_update_should_include` updates `should_include` on multiple rows directly via the repository but never invalidates the affected items' detail cache entries or the list cache. Stale `should_include` values can be served from cache for up to the full TTL after a bulk update.

**Fix direction:** invalidate the list cache key plus each updated grocery's detail key (`remove_grocery_detail_from_redis` per id, or a batched `delete` call) after a successful bulk update.

### 14.5 Empty list results are never cached — 🟡 Low priority (by design, undocumented)
**File:** `backend/app/features/grocery/service.py:131-133`

`if result: await self.add_grocery_list_to_redis(result)` — an empty grocery list is never written to cache, so every request against an empty/fully-filtered-out list falls through to the DB every time. Not a correctness bug, just a missed optimization; worth a one-line comment if intentional (e.g. avoiding caching `[]` under a shared key that Topic 14.1's fix will make filter-specific anyway).

---

## Topic 16: Latency Optimization

### 16.1 `X-Response-Time` header renders in scientific notation above 10ms — 🔴 Open (bug)
**File:** `backend/app/middleware/latency_header.py:11`

```python
response.headers["X-Response-Time"] = f"{latency:.2}ms"
```

`.2` (no type char) is Python's *general* format spec — 2 **significant figures**, not 2 decimal places. `RequestLoggerMiddleware` right next to it uses the correct `.2f` (`request_logger.py:29,36`). Verified:

| latency (ms) | `.2` (current) | `.2f` (intended) |
|---|---|---|
| 5.678 | `5.7ms` | `5.68ms` |
| 12.34 | `1.2e+01ms` | `12.34ms` |
| 123.456 | `1.2e+02ms` | `123.46ms` |

Any response taking ≥10ms — which is most of them — reports a header like `1.2e+02ms` instead of a readable millisecond value. Since the whole point of this header is human/dashboard-readable latency, this defeats its purpose for the majority of requests.

**Fix direction:** change the format spec to `.2f`.

---

## Summary

| # | File | Topic | Status |
|---|------|-------|--------|
| 14.1 | `features/grocery/service.py:120-133` | List cache key doesn't vary by filter params — wrong data can be served | 🔴 Open |
| 14.2 | `features/grocery/service.py:153-156` | No cache invalidation on create | 🔴 Open |
| 14.3 | `features/grocery/service.py:169-173` | No cache invalidation on delete | 🔴 Open |
| 14.4 | `features/grocery/service.py:175-188` | No cache invalidation on bulk update | 🔴 Open |
| 14.5 | `features/grocery/service.py:131-133` | Empty list results never cached | 🟡 Low priority |
| 16.1 | `middleware/latency_header.py:11` | `.2` format spec → scientific notation above 10ms | 🔴 Open |

**Assessment:** the cache-aside read path (list + detail, cache-hit-first with DB fallback) and the update-path invalidation are correctly implemented — that part matches the roadmap's Step 2/4 pattern (`system-design-learning-roadmap.md:751-821`). But 3 of the 4 mutation paths (create, delete, bulk-update) don't invalidate, and the list cache key is shared across all filter combinations. Given these are all correctness bugs affecting user-visible data (stale/wrong reads), **Topic 14 is not yet ready to mark ✅** — recommend fixing 14.1–14.4 before calling this done, since the "Success Criteria" of proper cache invalidation on updates (`system-design-learning-roadmap.md:842-845`) is explicitly not met for create/delete/bulk-update.

## Recommended next steps (priority order)
1. **14.1 — Filter-aware cache key**: highest priority — this is the one that can serve outright wrong data to unrelated requests, not just stale data.
2. **14.2 / 14.3 / 14.4 — Invalidate on create/delete/bulk-update**: same fix shape as the existing `update_grocery` → `remove_grocery_detail_from_redis` call; straightforward to close all three together.
3. **16.1 — Latency header format**: one-character fix (`.2` → `.2f`), independent of the caching work.
4. **14.5 — Cache empty results**: revisit once 14.1's key scheme is decided; low priority.
