# TypeScript Improvement Scopes — Day 3 & Day 4 Concepts

Scope: only improvements applying **Day 3 (Type Guards & Narrowing)** and **Day 4 (Typing Functions & Function Overloading)** concepts to `frontend/src`. Findings are grouped by topic, each with file:line, current behavior, and the concrete fix.

Reference material: `training-core/language-syntax/ts/src/day-3.ts` (typeof narrowing, user-defined type predicates, discriminated unions, `in` narrowing), `day-4.ts` (typed function signatures, optional/default/rest params, overloads, generic callback types).

---

## Topic 1: Type Guards & Narrowing

### 1.1 Unvalidated `JSON.parse` result used without narrowing
**File:** `frontend/src/api/axiosInstance.ts:24-25`

```ts
const parsedStorage = JSON.parse(authStorage);
const token = parsedStorage.state.token?.access_token;
```

`JSON.parse` returns `any`, so `parsedStorage.state.token` is accessed with zero shape validation. A malformed or tampered `localStorage` value would fail silently or throw deep in the call chain.

**Fix:** write a user-defined type predicate (Day 3, Exercise 2/4 style) and narrow before use:

```ts
function isAuthStorageShape(value: unknown): value is {state: {token?: {access_token?: string}}} {
    return typeof value === 'object' && value !== null && 'state' in value;
}

const parsed: unknown = JSON.parse(authStorage);
if (isAuthStorageShape(parsed)) {
    const token = parsed.state.token?.access_token;
    ...
}
```

### 1.2 Axios error payload passed to `BaseException` without validation
**File:** `frontend/src/api/axiosInstance.ts:56`, constructor at `frontend/src/api/types/common.ts:15-19`

`error.response?.data` is Axios's `any`-typed field, handed straight to `new BaseError(...)`. `BaseException`'s constructor trusts whatever shape it receives.

**Fix:** add `isBaseErrorResponse(data: unknown): data is Partial<BaseErrorResponse>` (an `isObject` + per-field `typeof` check, same pattern as day-3 Exercise 4's `isObject`/`safeAccess`) and narrow `error.response?.data` before constructing the error.

### 1.3 Unsafe `as` casts instead of type predicates for enum-like unions
**File:** `frontend/src/components/grocery_components/GroceryFilterBar.tsx:44-47`

```ts
if (type) filters.type = type as GroceryType;
if (currentSeller) filters.current_seller = currentSeller as Seller;
if (bestSeller) filters.best_seller = bestSeller as Seller;
if (category) filters.category = category as GroceryCategory;
```

`type`, `currentSeller`, `bestSeller`, `category` are plain `useState<string>` values force-cast to the const-object-derived unions from `constants/enums.ts:1-35`. Nothing verifies the string is actually a valid member — this is exactly the kind of assertion Day 3's type predicates are meant to replace.

**Fix:** add reusable predicates next to the enum definitions:

```ts
export function isGroceryType(v: string): v is GroceryType {
    return (Object.values(GroceryType) as string[]).includes(v);
}
```

and use `if (type && isGroceryType(type)) filters.type = type;` — same for `Seller` and `GroceryCategory`.

### 1.4 `catch (err: any)` with no narrowing before accessing `.message`
**File:** `frontend/src/store/useGroceryStore.ts:64-67` and `:74-77`

```ts
} catch (err: any) {
    console.log(err);
    set({error: err.message, isLoading: false});
}
```

`err` is typed `any` and `.message` is read with no check. The sibling handlers in the very same file (lines 87-97 and 108-116) correctly do `if (err instanceof BaseError)` first — these two are inconsistent and unsafe if a non-`BaseException` value is thrown (e.g. a network `TypeError`, where `.message` may still exist but `.error_code`/`.detail` won't).

**Fix:** change to `catch (err: unknown)` and mirror the `instanceof BaseError` narrowing already used elsewhere in the file (Day 3 `instanceof`-based narrowing).

### 1.5 Blanket `catch (err: any)` across the store
**File:** `frontend/src/store/useGroceryStore.ts:64, 74, 87, 108`

All four catch blocks type the caught error as `any`. TypeScript's safer default is `unknown`, forcing a narrowing step before any property access — which three of the four blocks already perform via `instanceof BaseError`. Switching the annotation to `unknown` makes the existing narrowing pattern the only way to reach `.message`/`.detail`, closing the gap in 1.4 at the type-checker level instead of relying on developer discipline.

### 1.6 Redundant type assertion where the type is already correct
**File:** `frontend/src/components/common/MonthlyGroceryAppSelectFieldSmall.tsx:17`

```ts
onChange(event.target.value as string);
```

MUI's `SelectChangeEvent` (non-multiple) already types `target.value` as `string`. The `as string` doesn't narrow anything — it just masks the compiler's ability to catch a real mismatch if the component's `onChange` prop type ever changes.

**Fix:** drop the cast — `onChange(event.target.value);`.

### 1.7 Repeated raw equality checks instead of a single narrowing point
**File:** `frontend/src/components/grocery_components/GroceryList.tsx:118-124`

`row.stock_status === GroceryStockStatus.IN_STOCK` is evaluated three separate times inline (icon choice, label text, color) to branch on what is effectively a two-member discriminated value.

**Fix:** narrow once per row (Day 3 discriminated-union style) — e.g. a small `getStockStatusView(status: GroceryStockStatus)` returning `{icon, label, color}` — instead of repeating the same comparison three times in JSX.

---

## Topic 2: Typing Functions & Function Overloading

### 2.1 Missing explicit return type + overload candidate
**File:** `frontend/src/constants/utils.ts:1`

```ts
export const formatDate = (dateInput: string | Date | undefined) => {
    if (!dateInput) return 'N/A';
    return new Date(dateInput).toLocaleDateString(...);
};
```

No explicit return type on a shared utility (relies on inference), and it accepts three distinct input shapes with different meanings (`Date`, `string`, `undefined`) — a direct match for Day 4 Exercise 3's overload pattern.

**Fix:** annotate the return type explicitly, and optionally split into overload signatures for clarity at call sites:

```ts
function formatDate(dateInput: Date): string;
function formatDate(dateInput: string): string;
function formatDate(dateInput: undefined): 'N/A';
function formatDate(dateInput: string | Date | undefined): string {
    if (!dateInput) return 'N/A';
    return new Date(dateInput).toLocaleDateString('en-US', {day: 'numeric', month: 'short', year: 'numeric'});
}
```

### 2.2 Loosely-typed curried field-change callbacks accept keys they shouldn't
**File:** `frontend/src/pages/UpdateGroceryPage.tsx:46, 53, 61` (same pattern in `AddGroceryPage.tsx:31,36` and `LoginPage.tsx:36`)

```ts
const handleStringChange = (field: keyof IPayloadGroceryItemUpdate) => (value: string) => {...};
const handleNumberChange = (field: keyof IPayloadGroceryItemUpdate) => (value: string) => {...};
const handleBooleanChange = (field: keyof IPayloadGroceryItemUpdate) => (value: string) => {...};
```

All three share the identical `(field: keyof T) => (value: string) => void` signature, but each is only valid for a subset of fields (string fields vs. numeric fields vs. boolean fields). Nothing at the type level stops `handleNumberChange('name')` from compiling even though `name` is a string field — the callback's generic typing (Day 4 Exercise 4 territory) doesn't actually constrain `field` to the fields it's meant for.

**Fix:** constrain `field` with a mapped/conditional generic helper instead of the bare `keyof T`, e.g.:

```ts
type KeysMatching<T, V> = { [K in keyof T]: T[K] extends V ? K : never }[keyof T];

const handleNumberChange = (field: KeysMatching<IPayloadGroceryItemUpdate, number>) => (value: string) => {...};
```

so a numeric-only field type is enforced at the call site, not just documented in a comment.

### 2.3 Comment acknowledging a typing gap in the same callback
**File:** `frontend/src/pages/UpdateGroceryPage.tsx:56`

```ts
// Use 'as any' to bypass strict dynamic key check if necessary
return {...prev, [field]: (Number(value) || 0)};
```

This comment documents the same root cause as 2.2 — the callback's signature doesn't actually guarantee `field` maps to a numeric property, so a cast was anticipated as a workaround. Fixing 2.2 removes the need for this comment and the `any` escape hatch entirely.

### 2.4 API response mapped via an implicitly-typed passthrough callback, with no shape guarantee
**File:** `frontend/src/api/endpoints/GroceryApi.ts:13-21` and `:43-49`

```ts
const grocery_list: IGroceryListItem[] = response.data.map(item => ({...item}));
```

Both `getGroceries` and `bulkUpdateShouldInclude` map a raw `GroceryListResponse` to `IGroceryListItem` via a blind spread inside an implicitly-typed `.map` callback. The callback's parameter/return typing offers no real defense — it's purely structural — against a malformed or incomplete API response.

**Fix:** name and type the mapper explicitly, matching Day 4's function-typing exercises (explicit param and return types on every function, not just arrow-inferred ones):

```ts
const toGroceryListItem = (item: GroceryListResponse): IGroceryListItem => ({...item});
const grocery_list: IGroceryListItem[] = response.data.map(toGroceryListItem);
```

This alone doesn't add runtime validation, but it makes the transform's input/output contract explicit and reusable across both call sites instead of duplicated inline.

### 2.5 Positional primitive params easy to transpose
**File:** `frontend/src/store/useGroceryStore.ts:99` (called from `frontend/src/pages/HomePage.tsx:55`)

```ts
bulkUpdateShouldIncludeItems: (grocery_ids: string[], should_include: boolean) => Promise<void>;
```

Two independent params of different primitive types aren't type-confusable today, but as a Day 4 function-signature exercise this is a good case for preferring a single well-typed parameter object over positional args, so intent is legible at the call site (`bulkUpdateShouldIncludeItems({groceryIds, shouldInclude: true})`) rather than requiring the reader to check the signature.

### 2.6 Inconsistent explicit vs. implicit parameter typing across sibling functions
**File:** `frontend/src/api/axiosInstance.ts:19` vs. `:48`

The request interceptor (`function (config) {...}`) leaves its parameter type implicit (inferred from Axios), while the response error interceptor (`(error: unknown) => {...}`) types its parameter explicitly. Both are interceptor callbacks in the same file — normalizing to explicit annotations on both (Day 4's emphasis on typing every function parameter) makes the contract consistent and self-documenting.

### 2.7 Duplicated inline callback-prop typing instead of a shared function type
**File:** `frontend/src/components/grocery_components/GroceryList.tsx:20-28, 31-35, 69-77`

`IGroceryTableProps` declares callback signatures like `onView: (grocery_id: string) => void`, and `GroceryTableRow`'s inline prop type (lines 72-76) re-declares the same callback shapes separately rather than reusing a shared named type.

**Fix:** extract a shared type (e.g. `type GroceryRowActions = Pick<IGroceryTableProps, 'onView' | 'onEdit' | 'onDelete'>`) and reuse it in `GroceryTableRow`'s props, so the two definitions can't drift apart — consistent with Day 4's typed-function-signature exercises (define the function type once, reuse it).

---

## Summary

| # | File | Topic |
|---|------|-------|
| 1.1 | `api/axiosInstance.ts:24-25` | Type predicate for parsed JSON |
| 1.2 | `api/axiosInstance.ts:56` | Type predicate for error payload |
| 1.3 | `components/grocery_components/GroceryFilterBar.tsx:44-47` | Type predicates instead of `as` casts |
| 1.4 | `store/useGroceryStore.ts:64-67, 74-77` | Missing `instanceof` narrowing before `.message` |
| 1.5 | `store/useGroceryStore.ts:64,74,87,108` | `any` → `unknown` in catch blocks |
| 1.6 | `components/common/MonthlyGroceryAppSelectFieldSmall.tsx:17` | Redundant assertion |
| 1.7 | `components/grocery_components/GroceryList.tsx:118-124` | Repeated equality checks vs. single narrowing point |
| 2.1 | `constants/utils.ts:1` | Missing return type / overload candidate |
| 2.2 | `pages/UpdateGroceryPage.tsx:46,53,61` (+ AddGroceryPage, LoginPage) | Unconstrained generic callback keys |
| 2.3 | `pages/UpdateGroceryPage.tsx:56` | `any`-escape comment tied to 2.2 |
| 2.4 | `api/endpoints/GroceryApi.ts:13-21,43-49` | Implicit mapper callback typing |
| 2.5 | `store/useGroceryStore.ts:99` | Positional params vs. typed options object |
| 2.6 | `api/axiosInstance.ts:19` vs. `:48` | Inconsistent param typing across sibling functions |
| 2.7 | `components/grocery_components/GroceryList.tsx:20-28,72-76` | Duplicated inline function-type declarations |
