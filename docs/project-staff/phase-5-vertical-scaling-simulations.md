# Phase 5 – Vertical Scaling: Stress Simulation Endpoints

Expected outcome of every endpoint in `backend/app/api/simulation_router.py`, with a **single worker** and with **multiple workers**, and why.

All numbers below were **measured on 2026-10-13** on the dev stack (Docker Desktop, macOS), each after a fresh `down` → `up`. Absolute timings will vary per machine; the *ratios* between the cases are what matter.

---

## 1. Setups compared

| | Single worker (current default) | Multiple workers |
|---|---|---|
| uvicorn processes | 1 | 2 (`WEB_CONCURRENCY: "2"`) |
| `cpus` limit | `1.00` | `4.00` |
| `memory` limit | `256M` | `512M` |

### Single worker
This is what `docker-compose.dev.yml` runs today; nothing to edit:
```yaml
    deploy:
      resources:
        limits:
          cpus: '1.00'
          memory: 256M
```

### Multiple workers
uvicorn (0.40) reads `WEB_CONCURRENCY` as the default for `--workers`, so no Dockerfile change is needed. Edit the `backend:` service in `docker-compose.dev.yml` by hand:
```yaml
    environment:
      WEB_CONCURRENCY: "2"
    deploy:
      resources:
        limits:
          cpus: '4.00'
          memory: 512M
```
Raise `cpus` and `memory` together with the worker count. Each worker is a full copy of the app (~80 MB), and extra workers on 1 core just take turns on that core.

**Put the file back to the single-worker values when you're done.** Every "Single worker" run below assumes it.

### Restart command (run before every test)
Every section below starts with this. It stops the whole dev stack and starts it fresh, so no memory, threads or child processes are left over from the previous test, then waits until the API answers:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done
curl -s localhost:8000/api/v1/health/   # check cpu_limit_cores / memory_limit_mb match the setup
```
- `down` keeps the Postgres volume (no `-v`), so seeded data survives.
- `--build` is needed after editing Python files, because the code is copied into the image. It's fast when nothing changed (cached).
- In zsh, quote URLs that contain `?`, e.g. `curl -s "localhost:8000/api/v1/stress/cpu/sequential?tasks=8"`. Otherwise zsh fails with `no matches found`.

---

## 2. Background: where code runs

| Code | Runs on | Can run in parallel with other Python code in the same process? |
|---|---|---|
| `async def` endpoint | the worker's **event loop** (one thread) | no, and it blocks the loop until it hits an `await` |
| `def` endpoint | FastAPI's (anyio) thread pool, one thread per request | no, threads share one GIL |
| `run_in_executor(thread_pool, ...)` | a thread pool, one thread per task | no, same GIL |
| `run_in_executor(process_pool, ...)` | child processes, each with its own GIL | **yes**, if the container has spare cores |
| uvicorn worker | separate OS process, own event loop / thread pool / GIL / DB pool / memory | **yes**, if the container has spare cores |

A worker is an **OS process**. It is not bound to a CPU core. The OS scheduler places processes on whatever cores the container is allowed to use.

The thread-pool and process-pool endpoints create a **new pool inside every request** and shut it down when the request ends. Every call therefore pays the full cost of starting its threads or processes, like a one-off job would.

---

## 3. `GET /api/v1/stress/memory` – memory exhaustion

**What it does:** allocates 400 MB (40 × 10 MB `bytearray`) and keeps it in a module-level list, so it is **never freed** until the process dies. Each call adds another 400 MB.

### Single worker (256M)
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

curl -s localhost:8000/api/v1/stress/memory                                           # call 1
docker stats --no-stream grocery-api-dev
curl -s localhost:8000/api/v1/stress/memory                                           # call 2
docker inspect grocery-api-dev --format '{{.State.Status}} OOMKilled={{.State.OOMKilled}} exit={{.State.ExitCode}}'
```

| Call | Result |
|---|---|
| 1st | ✅ `200 {"allocated_mb": 400}`, container at `255.4MiB / 256MiB` |
| 2nd | ❌ connection dropped; container **OOM-killed** (`exit 137`, `OOMKilled=true`) and **stays down** |

**Why the 1st call survives:** Docker's default swap is `memory-swap = 2 × memory`. A `256M` container really has **256 MB RAM + 256 MB swap**. ~70 MB app + 400 MB = 470 MB fits into 512 MB, so ~130 MB is pushed to swap (`memory.swap.current = 134582272`). The process lives on, but it is slower because it is swapping.

**Why the 2nd call kills it:** 470 + 400 = 870 MB > 512 MB (RAM + swap), so the kernel's OOM killer kills the process. uvicorn **is** PID 1 here, so the whole container exits. The backend has no `restart:` policy, so nothing brings it back. The next restart command does.

### Multiple workers (512M)
Edit `docker-compose.dev.yml` to the multiple-workers values (§1), then:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

for i in 1 2 3 4; do curl -s -w " http=%{http_code}\n" localhost:8000/api/v1/stress/memory; done
docker logs grocery-api-dev 2>&1 | grep -E "died|Started server process"
curl -s localhost:8000/api/v1/health/
```

| Call | Result |
|---|---|
| 1st | ✅ `200 {"allocated_mb": 400}`, `511.9MiB / 512MiB` |
| 2nd | ✅ `200 {"allocated_mb": 800}`, same worker again, so its list grew to 800 MB (swapping) |
| 3rd | ❌ that request failed (`http=000`); **both** workers were OOM-killed (`Child process [8] died`, `[9] died`) |
| 4th | ✅ `200 {"allocated_mb": 400}`, served by a **new** worker; `/health` → `200` |

**Why the container survives:** the OOM killer kills the **worker processes**, not uvicorn's supervisor (PID 1). The supervisor sees `Child process died` and starts replacements. The container keeps running and recovers by itself.

**What is still lost:** every request in flight on the killed workers fails, and the cache/state in that process is gone.

### Lessons
- Running out of memory is a **hard crash**, not a slowdown. Watch `memory_percent` on `/health`.
- The memory limit you set is not all the memory the container can use: by default, swap gives it the same amount again.
- Multiple workers isolate failures: one bad request kills a worker, not the whole API.
- Each extra worker costs memory, so `memory` must scale with `workers`.

---

## 4. `GET /api/v1/stress/cpu` – CPU work in a `def` endpoint

**What it does:** 500,000 SHA-256 hashes (~0.16–0.19 s of one core). It is a plain `def`, so FastAPI runs it in its thread pool and the event loop stays free.

### Run it
Restart with the setup you want to test (§1), then send 2 requests ~50 ms apart:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

curl -s -o /dev/null -w "A=%{time_total}s\n" localhost:8000/api/v1/stress/cpu & sleep 0.05
curl -s -o /dev/null -w "B=%{time_total}s\n" localhost:8000/api/v1/stress/cpu & wait
```

### Results: 2 requests ~50 ms apart
| | Single worker, 1 CPU | Multiple workers, 4 CPU |
|---|---|---|
| request A | 0.28 s | **0.16 s** |
| request B | 0.28 s | **0.16 s** |

### Why
- **Single worker:** both requests run in two FastAPI threads of the **same process**, so they share one GIL and one core. They take turns, and both finish late, at about the same time.
- **Multiple workers:** each request is handled by a different worker process (own GIL) on its own core. Both run at full speed, in parallel.
- `/health` stays responsive in both cases, because the event loop is never blocked.

---

## 5. `GET /api/v1/stress/cpu/sequential` – blocking the event loop

**What it does:** runs the `/cpu` work 4 times in a row (`?tasks=1..16`) inside an `async def` **with no `await`**. This deliberately **blocks the event loop**.

### Run it
Restart with the setup you want to test (§1), then:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

# one request alone
curl -s localhost:8000/api/v1/stress/cpu/sequential

# 2 requests ~50 ms apart
curl -s -o /dev/null -w "A=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/sequential & sleep 0.05
curl -s -o /dev/null -w "B=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/sequential & wait

# is /health blocked while a long request runs?
curl -s -o /dev/null "localhost:8000/api/v1/stress/cpu/sequential?tasks=8" & sleep 0.2
curl -s -o /dev/null -w "health waited %{time_total}s\n" localhost:8000/api/v1/health/; wait
```

### Results
| | Single worker, 1 CPU | Multiple workers, 4 CPU |
|---|---|---|
| one request alone | ~0.63 s | ~0.63 s |
| 2 requests: A | **1.35 s** | 0.63 s |
| 2 requests: B | **1.30 s** | 0.63 s |
| `/health` while `?tasks=8` runs | **waited 1.19 s** | 0.11 s |

### Why
- **One request alone is the same in both setups.** The 4 tasks run one after another in one thread, so extra cores are unused. Vertical scaling doesn't make a single sequential request faster.
- **Single worker, 2 requests: both take ~2×.** B can't start until A's handler returns. A's response is also delayed, because the event loop picks up B's handler (already waiting) before it finishes sending A's response bytes. Blocking the loop hurts even the request that does the blocking.
- **Single worker, `/health` waits.** There is only one event loop and it is busy, so *every* request queues behind the blocking one.
- **Multiple workers:** the second request and `/health` are accepted by the other worker's free event loop, so nothing queues.
- **Caveat:** uvicorn does **not** load-balance between workers. Whichever worker accepts the connection first gets it. In 1 of 5 trials, two simultaneous requests landed on the **same** worker and both took 1.23 s, exactly like the single-worker case. `worker_pid` in the response shows which worker served it. Use a load balancer for even distribution (Phase 5, topic 19).

**Fix in real code:** don't block inside `async def`. Use `await` for I/O, a `def` endpoint, or `run_in_executor` for CPU work. Extra workers only hide the problem.

---

## 6. `GET /api/v1/stress/cpu/thread-pool` – threads share one GIL

**What it does:** an `async def` endpoint that creates a 4-thread pool for this request and sends 4 tasks to it with `await loop.run_in_executor(...)`. The endpoint only coordinates. The event loop is free while the threads work. Response shows `task_threads: 4`.

### Run it
Restart with the setup you want to test (§1), then:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

# one request alone
curl -s localhost:8000/api/v1/stress/cpu/thread-pool

# 2 requests ~50 ms apart
curl -s -o /dev/null -w "A=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/thread-pool & sleep 0.05
curl -s -o /dev/null -w "B=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/thread-pool & wait
```

### Results
| | Single worker, 1 CPU | Multiple workers, 4 CPU |
|---|---|---|
| one request alone | 0.63–0.68 s | **0.63–0.68 s** (no faster!) |
| 2 requests: A | 1.17–1.23 s | 0.63–0.64 s |
| 2 requests: B | 1.23–1.30 s | 0.66–0.68 s |

### Why
- **One request is ~the same as sequential, even with 4 CPUs.** All 4 threads live in one process with **one GIL**, so only one thread runs Python code at a time. Threads give concurrency (good for I/O waits), not parallelism for CPU-heavy Python.
- **Creating the pool per request costs almost nothing:** starting threads is cheap (same process, shared memory).
- **Single worker, 2 requests: both take ~2×.** Each request gets its own pool, so 8 threads compete for one GIL and one core, and both requests finish late, at about the same time.
- **Multiple workers:** each request is in its own worker (own GIL), so 2 cores are busy in parallel and neither waits. Each request is still not faster than ~0.63 s.
- Unlike `sequential`, the event loop is **not** blocked, so `/health` keeps answering with a single worker.

---

## 7. `GET /api/v1/stress/cpu/process-pool` – true parallelism

**What it does:** an `async def` endpoint that creates a 4-process pool for this request (each child has its own GIL), sends 4 tasks to it, and shuts it down when the request ends. Response shows `task_processes: 4`.

### Run it
Restart with the setup you want to test (§1), then:
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up -d --build
until curl -sf -o /dev/null localhost:8000/api/v1/health/; do sleep 1; done

# one request alone
curl -s localhost:8000/api/v1/stress/cpu/process-pool

# 2 requests ~50 ms apart
curl -s -o /dev/null -w "A=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/process-pool & sleep 0.05
curl -s -o /dev/null -w "B=%{time_total}s\n" localhost:8000/api/v1/stress/cpu/process-pool & wait
```

### Results
| | Single worker, 1 CPU | Multiple workers, 4 CPU |
|---|---|---|
| one request alone | 0.79–0.98 s (**slower** than sequential) | **0.43–0.55 s** (faster than sequential's 0.63 s) |
| 2 requests: A | 2.41–3.08 s | 1.01–1.05 s |
| 2 requests: B | 2.65–3.02 s | 0.95–1.05 s |
| memory after the requests | ~72 MB (back to idle) | ~163 MB (2 idle workers) |

### Why
- **4 CPUs, one request: faster, but not 4×.** 4 processes have 4 GILs, and the OS runs them on 4 cores at the same time, so the hashing itself runs in parallel. But each request also forks 4 new processes and shuts them down again. That startup cost is part of every request's time. With a pool kept alive between requests, the same work measured **0.17 s**; the difference is the price of starting processes.
- **1 CPU: slower than sequential.** 4 processes still have only **one** core, so they take turns. You also pay to start the processes and to pickle data between them. Processes without cores give no benefit and add overhead.
- **Single worker, 2 requests: ~4× slower than one alone.** 2 requests fork 8 child processes on **one** core: 8 process startups plus 8 tasks all queue for the same core.
- **Multiple workers, 2 requests: ~2× slower than one alone.** Each worker forks its own 4 children, so 8 processes start and run on 4 cores, and they contend. Pool size × concurrent requests should not exceed the cores you have.
- **Memory:** the child processes exist only during the request and are removed afterwards, so memory returns to idle. *During* the request they still count against the container's memory limit.

---

## 8. Summary

| Endpoint | 1 request, 1 → 4 CPU | 2 concurrent, 1 worker | 2 concurrent, 2 workers | Event loop blocked? |
|---|---|---|---|---|
| `/memory` | — | 2nd call OOM-kills the **container** | 3rd call OOM-kills the **workers**, container recovers | no |
| `/cpu` (`def`) | 0.19 → 0.16 s | both slow (0.28 s) | both fast (0.16 s) | no |
| `/cpu/sequential` | no change (0.63 s) | both ~2× (1.3 s) | both 0.63 s* | **yes** |
| `/cpu/thread-pool` | no change (~0.65 s) | both ~2× (1.2–1.3 s) | both ~0.65 s* | no |
| `/cpu/process-pool` | **0.8–1.0 → 0.4–0.55 s** | both ~3× (2.4–3.1 s) | both ~1.0 s (processes contend) | no |

\* only if the two requests land on different workers (uvicorn doesn't balance them).

### What this means for the roadmap block (topic 17, step 3)
1. **`--workers` = cores you *actually* have.** Use the container's `cpus` limit, not `os.cpu_count()` (which reports the Docker VM's 8). Workers only add throughput when the cores are there.
2. **Workers multiply memory.** ~80 MB per worker, plus any process-pool children while they run. Raise `memory` together with workers, or the container gets OOM-killed.
3. **Workers multiply DB connections.** `workers × (POOL_SIZE + MAX_OVERFLOW)` must stay below Postgres `max_connections` (100).
4. **Vertical scaling raises throughput (more requests at once), not single-request speed**, unless the request itself spreads its work across processes, and even then the cost of starting those processes eats part of the gain.
5. **Find the bottleneck first:** watch `cpu_percent` and `memory_percent` on `/api/v1/health/` (container-level since this phase) while k6 runs.
