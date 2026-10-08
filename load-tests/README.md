# Load Tests

Load tests for the grocery API using [k6](https://grafana.com/docs/k6/latest/), run in Docker.
The k6 runner (`docker/grocery-management-k6.yml`) is standalone: it is not part of the dev or prod compose stacks.

```
load-tests/
└── k6/
    ├── groceries-read.js   # read-path test (list + detail), p95 < 100ms thresholds
    └── results/            # summary.json from the last run (gitignored)
```

## Prerequisites

- Docker with Docker Compose v2
- The API running and published on host port `8000`. The dev stack is recommended, since it uses a local, seeded Postgres instead of Supabase:

```bash
# from the repo root
cp backend/.env.dev.sample backend/.env.dev   # first time only, then set SECRET_KEY
docker compose -f docker-compose.dev.yml up -d --build
```

### Seeding test data

The dev stack's `db-init` job runs migrations and seeds the `grocery` table with `SEED_GROCERY_COUNT` random rows (default `100000`).
To change the count, set it in `backend/.env.dev` (a shell variable is not forwarded to the container):

```bash
SEED_GROCERY_COUNT=500
```

Seeding is skipped if the table already has rows, so remove the volume to reseed:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

Use `500` for realistic results (the expected list ceiling) and a large count (e.g. `100000`) to stress the list endpoint.

## Running

From the repo root:

```bash
# default script: k6/groceries-read.js
docker compose -f docker/grocery-management-k6.yml run --rm k6

# a different script in load-tests/k6/
docker compose -f docker/grocery-management-k6.yml run --rm k6 run /scripts/<script>.js

# a different API target (default: http://host.docker.internal:8000)
BASE_URL=http://<host>:<port> docker compose -f docker/grocery-management-k6.yml run --rm k6
```

`load-tests/k6` is mounted read-only at `/scripts` and `load-tests/k6/results` at `/results`.
The default command writes the end-of-test summary to `load-tests/k6/results/summary.json`.

## `groceries-read.js`

Public GET endpoints only, so no auth token is needed.

| Scenario | Executor | Load | Endpoint |
|----------|----------|------|----------|
| `detail` | `ramping-vus` | 0 → 20 VUs (30s), hold 1m, → 0 (15s) | `GET /api/v1/groceries/{id}` |
| `list` | `constant-vus` | 2 VUs for 1m45s | `GET /api/v1/groceries/` |

- `setup()` fetches the list once and picks up to 500 ids for the `detail` scenario. It fails fast if the API is down or the table is empty.
- Every iteration sleeps 1s, so this measures latency under light load (~17 req/s), not maximum throughput.
- Requests send `Accept-Encoding: gzip` like a browser.

**Thresholds** (the run fails if any are missed):

| Metric | Threshold |
|--------|-----------|
| `http_req_duration{name:detail}` | p95 < 100ms |
| `http_req_duration{name:list}` | p95 < 100ms |
| `http_req_failed` | rate < 1% |

## Reading the results

- Look at the `{ name:detail }` and `{ name:list }` rows of `http_req_duration`. The overall row also includes the `setup` request.
- The list and detail endpoints are cached in Redis (5-min TTL) and the test sends no writes, so most requests measure the **cache path**. To measure the DB path, clear the cache before the run (`docker exec grocery_dev_redis redis-cli FLUSHALL`), and keep in mind it warms up within seconds.
- Results depend on the pool settings in `backend/.env.dev` (`POOL_SIZE`, `MAX_OVERFLOW`, `POOL_TIMEOUT`). Note them alongside any numbers you record.
- Recorded results are in `docs/project-goals/system-design-learning-roadmap.md`, Topic 16.

## Adding a test

Add a new `.js` file to `load-tests/k6/` and run it with `run /scripts/<file>.js` as shown above.
Read `BASE_URL` from `__ENV.BASE_URL` and tag requests with `tags: { name: '...' }` so you can set thresholds per endpoint.
