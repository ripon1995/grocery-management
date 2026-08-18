# Improvement Scopes — Day 7 Concepts

Scope: improvements applying **TS Day 7 (Utility Types)** and **Python Day 7 (Lists)** concepts to the actual `frontend/` and `backend/` codebases. Findings are grouped by topic, each with file:line, current behavior, and the concrete fix.

Reference material: `training-core/language-syntax/ts/src/day-7.ts` (`Partial<T>`, `Required<T>`, `Readonly<T>`, `Pick<T,K>`, `Omit<T,K>`, `Record<K,V>`, combining `Partial` + `Pick`), `training-core/language-syntax/python/day-7.py` (indexing/slicing, `append`/`insert`/`remove`/`pop`, `count`/`index`/`sorted`, iterate-and-filter into a new list, menu-driven list mutation with `try`/`except ValueError` before removing).

---

## Topic 1: TypeScript Utility Types (Day 7)

### 1.1 `IGroceryDetailApiResponse` is a byte-for-byte manual clone of `IGroceryDetail`
**Files:** `frontend/src/api/types/responses/GroceryDetailResponse.ts:3-19` vs. `frontend/src/types/IGroceryDetail.ts:4-20`

```ts
// GroceryDetailResponse.ts
export interface IGroceryDetailApiResponse {
    id: string;
    name: string;
    brand: string;
    type: GroceryType;
    current_price: number;
    current_seller: Seller;
    low_stock_threshold: number;
    quantity_in_stock: number;
    should_include: boolean;
    category: GroceryCategory;
    best_price: number;
    best_seller: Seller;
    stock_status: GroceryStockStatus;
    created_at: Date,
    updated_at: Date
}
```

Every one of the 14 fields is retyped by hand instead of derived from `IGroceryDetail`, which declares the identical shape one directory up. This is exactly the gap Day 7 Exercise 1's `Readonly<User>` closes — an API response is also a natural `Readonly` candidate since callers shouldn't mutate it in place.

**Fix:**
```ts
import type {IGroceryDetail} from "../../../types/IGroceryDetail.ts";

export type IGroceryDetailApiResponse = Readonly<IGroceryDetail>;
```

### 1.2 `GroceryListResponse` duplicates `IGroceryListItem` field-for-field
**Files:** `frontend/src/api/types/responses/GroceryListResponse.ts:3-17` vs. `frontend/src/types/IGroceryList.ts:3-17`

Both interfaces independently declare the same 13 fields (they do currently agree with each other — `current_seller: string` in both — but that agreement is coincidental upkeep, not derivation; it only takes one of the two being edited in isolation to drift, and both already disagree with `IGroceryDetail.current_seller: Seller`). `GroceryApi.ts`'s `toGroceryListItem` mapper (`({...item})`) is a pure no-op that only exists because these are typed as two "different" shapes.

**Fix:**
```ts
export type GroceryListResponse = Readonly<IGroceryListItem>;
```
so the two can never diverge, and the no-op mapper in `GroceryApi.ts` can be deleted.

### 1.3 `IGroceryCreateItem` hand-duplicates a subset of `IGroceryDetail` instead of `Omit`
**File:** `frontend/src/api/types/requests/grocery/CreateGroceryItem.ts:4-13`

```ts
export interface IGroceryCreateItem {
    name: string;
    brand: string;
    type: GroceryType;
    current_price: number;
    current_seller: Seller;
    low_stock_threshold: number;
    quantity_in_stock: number;
    category: GroceryCategory;
}
```

This is `IGroceryDetail` minus `id`, `should_include`, `best_price`, `best_seller`, `stock_status`, `created_at`, `updated_at` — the "creation payload" pattern Day 7 Exercise 4 targets directly, currently maintained by manual retyping.

**Fix:**
```ts
import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";

export type IGroceryCreateItem = Omit<
    IGroceryDetail,
    'id' | 'should_include' | 'best_price' | 'best_seller' | 'stock_status' | 'created_at' | 'updated_at'
>;
```

### 1.4 `IPayloadGroceryItemUpdate` hand-duplicates almost the same subset
**File:** `frontend/src/api/types/requests/grocery/UpdateGroceryItem.ts:4-15`

Same issue as 1.3 one field over — this is `IGroceryDetail` minus only the derived/read-only fields (`best_price`, `best_seller`, `stock_status`, `created_at`, `updated_at`), maintained as an independent manual copy that has to be kept in sync by hand on every `IGroceryDetail` change.

**Fix:**
```ts
import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";

export type IPayloadGroceryItemUpdate = Omit<
    IGroceryDetail,
    'best_price' | 'best_seller' | 'stock_status' | 'created_at' | 'updated_at'
>;
```

### 1.5 `IGroceryFilterParams` is a manual `Partial<Pick<...>>` — the exact combination Day 7 Exercise 4 teaches
**File:** `frontend/src/api/types/requests/grocery/GroceryFilterParams.ts:4-11`

```ts
export interface IGroceryFilterParams {
    type?: GroceryType;
    current_seller?: Seller;
    best_seller?: Seller;
    category?: GroceryCategory;
    should_include?: boolean;
    search?: string;
}
```

Every field except `search` already exists on `IGroceryDetail`, just re-declared as optional by hand — precisely Day 7 Exercise 4's "`Partial` + `Pick` for a narrow update/query payload" lesson.

**Fix:**
```ts
import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";

export type IGroceryFilterParams =
    Partial<Pick<IGroceryDetail, 'type' | 'current_seller' | 'best_seller' | 'category' | 'should_include'>>
    & {search?: string};
```

### 1.6 `getStockStatusView` dispatches with a `switch`/`default` instead of a `Record<GroceryStockStatus, ...>` lookup
**File:** `frontend/src/components/grocery_components/GroceryList.tsx:37-52`

```ts
function getStockStatusView(status: GroceryStockStatus): Pick<ChipProps, 'icon' | 'label' | 'color'> {
    switch (status) {
        case GroceryStockStatus.IN_STOCK:
            return {icon: <ArrowUpwardIcon .../>, label: 'In Stock', color: 'success'}
        default:
            return {icon: <ArrowDownwardIcon .../>, label: 'Low Stock', color: 'error'};
    }
}
```

`GroceryStockStatus` (`constants/enums.ts:16-19`) is a known 2-member string-literal union. The return type already correctly uses `Pick<ChipProps, 'icon' | 'label' | 'color'>` — the missing piece is Day 7 Exercise 3's `Record<K, V>` lookup for the dispatch itself. A `switch`/`default` silently absorbs any future status added to the enum into "Low Stock" instead of failing to compile.

**Fix:**
```ts
const STOCK_STATUS_VIEW: Record<GroceryStockStatus, Pick<ChipProps, 'icon' | 'label' | 'color'>> = {
    [GroceryStockStatus.IN_STOCK]: {icon: <ArrowUpwardIcon .../>, label: 'In Stock', color: 'success'},
    [GroceryStockStatus.BELOW_STOCK]: {icon: <ArrowDownwardIcon .../>, label: 'Low Stock', color: 'error'},
};

const getStockStatusView = (status: GroceryStockStatus) => STOCK_STATUS_VIEW[status];
```

### 1.7 `ERROR_CODES` has no `as const`, so `toBaseError`'s `switch` dispatches on widened `string` with no exhaustiveness
**Files:** `frontend/src/constants/errorCodes.ts:1-5`, `frontend/src/api/exceptions/exceptionFactory.ts:7-23`

```ts
// errorCodes.ts
const ERROR_CODES = {
    RESOURCE_NOT_FOUND: "resource_not_found",
    INVALID_UUID: "invalid_uuid",
    UNAUTHORIZED: "unauthorized",
}
export default ERROR_CODES;
```

Unlike `GroceryType`/`Seller`/`GroceryCategory`/`GroceryStockStatus` in the same `constants` folder (all `as const`), `ERROR_CODES` values widen to `string` and there is no exported literal union for an error code — the same "map known keys to values" shape Day 7's `Record<K,V>` section targets, currently done with a `switch` in `exceptionFactory.ts`.

**Fix:**
```ts
// errorCodes.ts
const ERROR_CODES = {
    RESOURCE_NOT_FOUND: "resource_not_found",
    INVALID_UUID: "invalid_uuid",
    UNAUTHORIZED: "unauthorized",
} as const;
export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];
export default ERROR_CODES;

// exceptionFactory.ts
const ERROR_FACTORY: Record<ErrorCode, (payload: IBaseException) => BaseException> = {
    [ERROR_CODES.RESOURCE_NOT_FOUND]: (payload) => new NotFoundError(payload),
    [ERROR_CODES.INVALID_UUID]: (payload) => new InvalidUUIDError(payload),
    [ERROR_CODES.UNAUTHORIZED]: (payload) => new UnauthorizedException(payload),
};

export function toBaseError(payload?: IBaseException): BaseException {
    if (!payload) return new BaseException();
    const code = payload.error_code?.toLocaleLowerCase() as ErrorCode;
    return (ERROR_FACTORY[code] ?? ((p: IBaseException) => new BaseException(p)))(payload);
}
```

### 1.8 Route-table and enum constants declared without `as const` / `Readonly`
**Files:** `frontend/src/constants/apiEndpoints.ts:5-16`, `frontend/src/constants/enums.ts:51-54` (`YesNoChoice`)

```ts
const GROCERY_APIS = {
    GROCERY_LIST: `${GROCERIES}/`,
    ...
}
const AUTH_APIS = {
    LOGIN: `${AUTH}/login`
};
```

`GROCERY_APIS`/`AUTH_APIS` are plain mutable objects; `API_ENDPOINTS`'s own `as const` (`apiEndpoints.ts:19-22`) does not retroactively freeze the objects it references, only the outer wrapper — `API_ENDPOINTS.GROCERY` is still `typeof GROCERY_APIS`, a mutable type. Same gap on `YesNoChoice`, which — unlike every sibling in `enums.ts` — has no `as const` and no derived union type. This is config data that should never change at runtime, exactly Day 7's `Readonly<T>` case.

**Fix:**
```ts
const GROCERY_APIS = {
    GROCERY_LIST: `${GROCERIES}/`,
    GROCERY_ADD: `${GROCERIES}/`,
    GROCERY_DETAIL: `${GROCERIES}/:id`,
    GROCERY_UPDATE: `${GROCERIES}/:id`,
    GROCERY_DELETE: `${GROCERIES}/:id`,
    GROCERY_BULK_SHOULD_INCLUDE: `${GROCERIES}/bulk/should-include`,
} as const;

const AUTH_APIS = {LOGIN: `${AUTH}/login`} as const;
```
```ts
export const YesNoChoice = {YES: 'yes', NO: 'no'} as const;
export type YesNoChoice = typeof YesNoChoice[keyof typeof YesNoChoice];
```

---

## Topic 2: Python Lists (Day 7)

### 2.1 `bulk_update_should_include` commits the update *before* checking which ids actually existed — the inverse of Exercise 5's "check before you mutate"
**Files:** `backend/app/features/grocery/service.py:128-141`, `backend/app/features/grocery/repository.py:98-115`

```python
# repository.py
async def bulk_update_should_include(self, grocery_ids, should_include):
    stmt = update(Grocery).where(Grocery.id.in_(grocery_ids)).values(should_include=should_include).returning(Grocery)
    result = await self.session.execute(stmt)
    updated_groceries = result.scalars().all()
    await self.session.commit()          # <-- committed here
    return updated_groceries

# service.py
async def bulk_update_should_include(self, data):
    updated_groceries = await self.repo.bulk_update_should_include(data.grocery_ids, data.should_include)
    found_ids = {grocery.id for grocery in updated_groceries}
    missing_ids = [str(gid) for gid in data.grocery_ids if gid not in found_ids]   # <-- checked after
    if missing_ids:
        raise ResourceNotFoundException(...)
```

Exercise 5's `shopping_list.remove()` is wrapped in `try`/`except ValueError` precisely so a missing item is checked *before* acting on the list. Here it's backwards: the `UPDATE ... WHERE id IN (...)` runs and commits first, and only afterwards does the service build the `missing_ids` filtered list and raise. If 4 of 5 ids exist, those 4 are silently committed while the client receives a blanket 404 as if nothing happened.

**Fix:**
```python
# repository.py
async def get_existing_ids(self, grocery_ids: Sequence[UUID]) -> set[UUID]:
    stmt = select(Grocery.id).where(Grocery.id.in_(grocery_ids))
    result = await self.session.execute(stmt)
    return set(result.scalars().all())
```
```python
# service.py — check membership before mutating
async def bulk_update_should_include(self, data: GroceryBulkUpdateSchema) -> List[GroceryUpdateResponseSchema]:
    existing_ids = await self.repo.get_existing_ids(data.grocery_ids)
    missing_ids = [str(gid) for gid in data.grocery_ids if gid not in existing_ids]
    if missing_ids:
        message = GROCERY_NOT_FOUND.format(grocery_id=", ".join(missing_ids))
        logger.error(message)
        raise ResourceNotFoundException(message=message)

    updated_groceries = await self.repo.bulk_update_should_include(data.grocery_ids, data.should_include)
    return [GroceryUpdateResponseSchema.model_validate(grocery) for grocery in updated_groceries]
```
(this also drops the duplicate `", ".join(missing_ids)` call the original computed twice — once for the log, once for the exception message.)

### 2.2 `has_conditions()` builds a throwaway 5-element list just to feed `any()`
**File:** `backend/app/features/grocery/filters.py:24-31`

```python
def has_conditions(self) -> bool:
    return any([
        self.type is not None,
        self.current_seller is not None,
        self.best_seller is not None,
        self.category is not None,
        self.should_include is not None,
    ])
```

`any()`/`all()` are built to short-circuit over a lazy iterable; wrapping the arguments in `[...]` forces eager evaluation of all 5 booleans and allocates a list that's discarded immediately after. It's the inverse of Exercise 4's "build a list only when you need one to iterate again."

**Fix:**
```python
def has_conditions(self) -> bool:
    return any(
        value is not None
        for value in (self.type, self.current_seller, self.best_seller, self.category, self.should_include)
    )
```

### 2.3 `_build_search_conditions` concatenates two lists with `+` only to immediately unpack them with `*`
**File:** `backend/app/features/grocery/repository.py:48-60`

```python
search_conditions = (
        [field.ilike(term) for field in text_fields]
        + [cast(field, String).ilike(term) for field in cast_fields]
)
return or_(*search_conditions)
```

Two comprehensions build two temporary lists, `+` builds a third concatenated list, and then it's immediately unpacked with `*` into `or_()` — none of the intermediate lists are ever indexed or reused. Since the target is a one-shot unpack, generator expressions unpacked directly avoid three throwaway allocations.

**Fix:**
```python
return or_(
    *(field.ilike(term) for field in text_fields),
    *(cast(field, String).ilike(term) for field in cast_fields),
)
```

### 2.4 `get_groceries` has no slicing/windowing — the whole table is always returned as one list
**Files:** `backend/app/features/grocery/repository.py:21-27`, `backend/app/common/pagination.py` (present, empty)

```python
async def get_groceries(self, filters: GroceryFilterParams | None = None) -> Sequence[Grocery]:
    """Get all groceries, optionally filtered/searched — no pagination for now"""
    stmt = select(Grocery)
    ...
```

Day 7 Exercise 1's `movies[1:4]` slicing is the basic tool for taking a bounded window out of a list; there's a `common/pagination.py` file already scaffolded for exactly this and it's empty, with the docstring admitting "no pagination for now." Every call to list groceries loads and returns the full table as a single unbounded list — a real scaling gap directly tied to the slicing concept.

**Fix:**
```python
async def get_groceries(
        self,
        filters: GroceryFilterParams | None = None,
        skip: int = 0,
        limit: int = 50,
) -> Sequence[Grocery]:
    """Get groceries, optionally filtered/searched, windowed via skip/limit (server-side slice)."""
    stmt = select(Grocery)
    if filters:
        if filters.has_conditions():
            stmt = stmt.where(self._build_filter_conditions(filters))
        if filters.search:
            stmt = stmt.where(self._build_search_conditions(filters.search))
    stmt = stmt.offset(skip).limit(limit)
    result = await self.session.execute(stmt)
    return result.scalars().all()
```

### 2.5 `_build_filter_conditions` calls `getattr(filters, field)` twice per iteration inside the comprehension
**File:** `backend/app/features/grocery/repository.py:38-46`

```python
conditions = [
    getattr(Grocery, field) == getattr(filters, field)
    for field in filter_fields
    if getattr(filters, field) is not None
]
```

This is otherwise a correct "iterate & filter into a new list" comprehension (Exercise 4's pattern done right), but it recomputes `getattr(filters, field)` twice per field — once in the `if` guard, once in the value expression — redoing work a single pass could avoid.

**Fix:**
```python
conditions = [
    getattr(Grocery, field) == value
    for field in filter_fields
    if (value := getattr(filters, field)) is not None
]
```

---

## Summary

| # | File | Topic |
|---|------|-------|
| 1.1 | `api/types/responses/GroceryDetailResponse.ts:3-19` | Manual clone of `IGroceryDetail` instead of `Readonly<T>` |
| 1.2 | `api/types/responses/GroceryListResponse.ts:3-17` | Manual clone of `IGroceryListItem` instead of `Readonly<T>` |
| 1.3 | `api/types/requests/grocery/CreateGroceryItem.ts:4-13` | Hand-duplicated subset instead of `Omit<T,K>` |
| 1.4 | `api/types/requests/grocery/UpdateGroceryItem.ts:4-15` | Hand-duplicated subset instead of `Omit<T,K>` |
| 1.5 | `api/types/requests/grocery/GroceryFilterParams.ts:4-11` | Hand-duplicated optional subset instead of `Partial<Pick<T,K>>` |
| 1.6 | `components/grocery_components/GroceryList.tsx:37-52` | `switch`/`default` instead of `Record<GroceryStockStatus,...>` |
| 1.7 | `constants/errorCodes.ts:1-5`, `api/exceptions/exceptionFactory.ts:7-23` | Missing `as const`/`Record` dispatch for error codes |
| 1.8 | `constants/apiEndpoints.ts:5-16`, `constants/enums.ts:51-54` | Config constants missing `as const`/`Readonly` |
| 2.1 | `features/grocery/service.py:128-141`, `repository.py:98-115` | Bulk update commits before existence check (inverse of Exercise 5) |
| 2.2 | `features/grocery/filters.py:24-31` | Throwaway list built just to feed `any()` |
| 2.3 | `features/grocery/repository.py:48-60` | List concatenation + unpack instead of generator unpack |
| 2.4 | `features/grocery/repository.py:21-27` | No slicing/pagination — always returns unbounded list |
| 2.5 | `features/grocery/repository.py:38-46` | Redundant `getattr` call inside filter comprehension |
