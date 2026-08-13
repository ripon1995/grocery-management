# Phase 3 Review — 8. Databases (SQL)

Scope: reviews `docs/project-goals/system-design-learning-roadmap.md` Phase 3, section **"8. Databases (SQL)"** (marked ✅ Already Using) against the real backend schema, migrations, and data-access code. The roadmap's checkmark reflects that Postgres/Supabase is in use, not that the section's "Deep Dive Tasks" (schema review, relationships, transactions) are done — they aren't. Findings below are grouped by topic, each with file:line, current behavior, and the concrete gap vs. what the roadmap describes.

Reviewed: 2026-08-12. Follow-up pass 2026-08-13 after transaction/rollback, indexing, and connection-pool fixes landed (commits `cf509a9`…`90f78cd`) — see per-topic ✅/🟡 status markers and updated Summary table below.

---

## Topic 1: Schema vs. Roadmap's Described Schema

### 1.1 Table name mismatch
**File:** `backend/app/features/grocery/models.py:16`

The roadmap's example schema (`system-design-learning-roadmap.md:376`) names the table `groceries`. The actual table is `grocery` (singular) — cosmetic, but worth fixing in the doc so future sections don't reference a table that doesn't exist.

### 1.2 No `categories` table — `category` is a plain enum column
**File:** `backend/app/features/grocery/models.py:53-58`, enum defined at `backend/app/common/enums.py:18-23`, added via migration `backend/migrations/versions/5dc40e0c9376_add_category_column_to_grocery.py`

The roadmap's "Add Relationships" step (`system-design-learning-roadmap.md:388-399`) proposes a normalized `categories` table with `groceries.category_id UUID REFERENCES categories(id)`. That was never implemented — `category` is a Postgres `ENUM` type (`grocerycategory`: `TOILETRIES, FOOD, COOKIES, OIL, OTHER`) stored directly on `grocery`, with no lookup table and no FK.

**Assessment:** given the category set is small (5 fixed values) and doesn't need per-category metadata today, a full FK-normalized table may be over-engineering for current needs — see Topic 3 for the indexing alternative. Worth a deliberate decision either way rather than leaving it as an unstated gap.

### 1.3 `current_price` / `best_price` are `Integer`, not `DECIMAL`
**File:** `backend/app/features/grocery/models.py:32-35, 67-71`

The roadmap's example schema uses `price DECIMAL(10,2)` (`system-design-learning-roadmap.md:379`). The real columns are `Integer`, which drops fractional currency precision — fine only if prices are always stored as whole units (e.g. smallest currency unit / cents) by convention; there's no comment or naming (`current_price_cents`) confirming that convention is intentional.

### 1.4 No multi-tenancy — `Grocery` has no `user_id`
**File:** `backend/app/features/grocery/models.py:16-71`, `backend/app/features/auth/models.py:9-25`

Phase 2's "Step 4: Multi-Tenancy" (`system-design-learning-roadmap.md:336-350`) proposes `user_id = Column(UUID, ForeignKey("users.id"))` on `Grocery` so groceries are scoped per-user. The `User` table exists and auth is implemented, but `Grocery` still has no `user_id` column or relationship — every authenticated user currently sees the same shared grocery data. This is a functional gap, not just a system-design exercise, if per-user data isolation is an actual product requirement.

---

## Topic 2: Transactions & Rollback

### 2.1 No explicit transaction blocks or rollback handling anywhere — ✅ RESOLVED (2026-08-13)
**Files:** `backend/app/features/grocery/repository.py:67-114` (commits `cf509a9`, `0a17027`)

All four write paths (`add_grocery`, `update_grocery`, `delete_grocery`, `bulk_update_should_include`) now wrap their `commit()` in `try/except Exception: await self.session.rollback(); raise DatabaseException(...)`. `DatabaseException` (`backend/app/core/exceptions.py`) maps to a 400 with a `database_error` error code, so callers get a clean response instead of an unhandled exception on commit failure.

**Remaining gap:** no regression test forces a mid-transaction failure (e.g. constraint violation on one row in `bulk_update_should_include`) to assert no partial writes persist — the "Fix direction" below is only half-done. The `except Exception` also discards the original exception (no `raise ... from e` / no logging of the underlying `SQLAlchemyError`), so the real DB error is invisible in logs — minor, worth a follow-up if debugging commit failures becomes necessary.

<details>
<summary>Original finding (for reference)</summary>

The roadmap's Deep Dive Task 1 (`system-design-learning-roadmap.md:369-371`) asks to "test transactions with multiple grocery items" and "implement rollback on failure." Every write path in the codebase is a bare `await session.commit()` with no surrounding `async with session.begin():` block and no `try/except` → `rollback()`. Session lifecycle is handled only at the FastAPI-dependency level (`backend/app/db/session.py:24-26`, `async with async_session_factory() as session:`), which closes the session on exit but performs no explicit rollback if a commit raises mid-request.

**Concrete risk:** `bulk_update_should_include` (`repository.py:94`) updates multiple rows before a single commit — if the commit fails partway (e.g. a constraint violation on one row after others succeeded), there's no explicit rollback path exercised or tested; behavior currently depends entirely on SQLAlchemy's default session-closing semantics rather than an intentional transaction boundary.

**Fix direction:** wrap multi-row/multi-step writes in `async with session.begin():` and add a `try/except`→`rollback()` (or rely on `begin()`'s own automatic rollback-on-exception) with a regression test that forces a mid-transaction failure and asserts no partial writes persist.

</details>

---

## Topic 3: Indexing (blocked by Topic 1's schema questions, but tracked separately per roadmap)

### 3.1 Zero indexes beyond primary keys and unique constraints — ✅ RESOLVED (2026-08-13)
**Files:** `backend/app/features/grocery/models.py:27-61` (`type`, `current_seller`, `category` now `index=True`), migrations `85ef98a7301c_add_index_on_grocery_type_column.py` and `41ab5277874e_add_indexes_to_grocery_category_seller_.py` (commits `40af867`, `4b90df8`, `a58ed48`)

All three columns the repository filters/searches on (`repository.py:39-58`) are now indexed: `ix_grocery_type`, `ix_grocery_category`, `ix_grocery_current_seller`.

**Remaining gap (low priority):** no composite index for combined filters (e.g. `category` + `current_seller` together), and no `EXPLAIN ANALYZE` before/after evidence that the indexes are actually used by the planner at current row counts. Neither blocks closing this item — revisit only if query latency becomes a measured problem.

<details>
<summary>Original finding (for reference)</summary>

The only indexes that exist are the implicit ones Postgres creates for:
- `user.email` unique constraint (migration `9212f2069cff_user_model_created.py`)
- `user.username` unique constraint (migration `ff8c6088c88e_password_length_increased.py`)
- Primary key indexes on `id` for both tables

Meanwhile, `backend/app/features/grocery/repository.py:39-58` filters/searches directly on `category`, `type`, and `current_seller` — none of which are indexed. This is exactly the gap the roadmap's section 10 (`system-design-learning-roadmap.md:449-493`) describes, currently untouched. Low risk at today's data volume, but cheap to fix now and will matter as soon as the grocery table grows past a few thousand rows.

**Fix direction:** add `index=True` to `category`, `type`, and `current_seller` columns (or a composite index matching the most common filter combination), plus a migration; use `EXPLAIN ANALYZE` before/after to confirm the change matters at current + projected row counts before spending more effort here.

</details>

---

## Topic 4: Connection Pooling (Phase 4 territory, flagged here since it's adjacent to the DB layer review)

### 4.1 No pool tuning — using SQLAlchemy async engine defaults — 🟡 PARTIALLY RESOLVED (2026-08-13)
**File:** `backend/app/db/session.py:7-18` (commits `3ade2ec`, `90f78cd`)

```python
create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SHOW_SQL_LOG,
    future=True,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0},
)
```

`pool_size`, `max_overflow`, and `pool_timeout` are now configurable via `settings` (`POOL_SIZE`/`MAX_OVERFLOW`/`POOL_TIMEOUT` env vars) instead of silently defaulting.

**Remaining gap:** `pool_recycle` and `pool_pre_ping` are still unset. These specifically matter for Supabase's pooler (PgBouncer in front of Postgres can silently drop idle connections) — without `pool_pre_ping`, a stale connection surfaces as a request-time error rather than being transparently recycled. Worth adding once real traffic patterns are known; not urgent at current scale.

<details>
<summary>Original finding (for reference)</summary>

```python
create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SHOW_SQL_LOG,
    future=True,
    connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0},
)
```

No `pool_size`, `max_overflow`, `pool_recycle`, or `pool_pre_ping` set — the engine runs on SQLAlchemy's default `AsyncAdaptedQueuePool` settings. Not urgent at current scale, but worth deliberately setting once traffic/connection-count assumptions are known, rather than leaving it implicit (Supabase free-tier connection limits make this more likely to bite than usual).

</details>

---

## Summary

| # | File | Topic | Status |
|---|------|-------|--------|
| 1.1 | `features/grocery/models.py:17` | Table named `grocery`, not `groceries` as roadmap assumes | ⬜ Open (doc-only fix) |
| 1.2 | `features/grocery/models.py:55-58` | No `categories` table/FK — `category` is a plain enum column | ⬜ Open (deferred by design) |
| 1.3 | `features/grocery/models.py:33-35,70-73` | `current_price`/`best_price` are `Integer`, not `DECIMAL` | ⬜ Open |
| 1.4 | `features/grocery/models.py:16-73` | No `user_id` FK — no multi-tenancy despite `User` table existing | ⬜ Open |
| 2.1 | `features/grocery/repository.py:67-114` | No transaction blocks or rollback anywhere; bare `commit()` calls | ✅ Resolved (2026-08-13) |
| 3.1 | `features/grocery/models.py`, `migrations/versions/*.py` | No indexes beyond PK/unique constraints; filtered columns (`category`,`type`,`current_seller`) unindexed | ✅ Resolved (2026-08-13) |
| 4.1 | `db/session.py:7-18` | No connection pool tuning (`pool_size`/`max_overflow` unset) | 🟡 Partial (2026-08-13) — `pool_recycle`/`pool_pre_ping` still unset |

## Recommended next steps (priority order)
1. ~~**2.1 — Transactions/rollback**: correctness issue, independent of any schema debate. Fix first.~~ ✅ Done — see 2.1. Follow-up: add a regression test for mid-transaction failure.
2. **1.4 — Multi-tenancy**: if per-user data isolation is an actual product requirement (not just a learning exercise), this is a functional gap, not a nice-to-have. Still open — highest-priority remaining item.
3. ~~**3.1 — Indexing**: cheap, low-risk, add now before it's a measured problem.~~ ✅ Done — see 3.1.
4. **1.2 — Categories normalization**: defer until there's a concrete need for per-category metadata; an index on the existing enum column likely covers today's needs. Still deferred, unchanged.
5. **1.3 / 4.1**: revisit opportunistically — not urgent at current scale. 4.1 is now partially addressed (pool sizing); `pool_recycle`/`pool_pre_ping` and 1.3 (Integer→DECIMAL) remain untouched.
