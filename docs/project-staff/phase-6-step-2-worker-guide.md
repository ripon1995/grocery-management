# Phase 6 Step 2 – Building the explore worker, in versions

The worker takes jobs from `explore.jobs`, calls Gemini, and writes the results to the job in Redis.
Build it in four versions, each one a commit of its own (or one commit per mission in V3 and V4):

| Version | Goal | You've mastered it when |
|---|---|---|
| **V1 – Easy** | The smallest worker that works end to end. It has known weak spots, marked `⚠️ CLUE` in the code | you can trigger every clue on purpose and explain what went wrong |
| **V2 – Standard** | Fix every clue from V1 with the basic, fundamental patterns | every V1 clue check now behaves differently |
| **V3 – Hardening** | Small changes, one or two files each, that make the V2 worker safe to run for real | each mission's check passes |
| **V4 – Industry** | Bigger design changes: smarter retries, recovering failed jobs, splitting jobs into smaller messages | each mission's check passes |

Updated 2026-10-22, starting from commit `12b323d`.

---

## 1. Where you start

### Already in the code
| What | Where |
|---|---|
| `POST /market/explore` returns `202 {job_id, status, not_found_ids}` | `app/features/market/service.py`, `routers/v1/router.py` |
| The job is saved in Redis as `{job_id, status: pending, grocery_ids, results: []}` with a TTL of `EXPLORE_JOB_TTL_S`, then published to `explore.jobs` | `MarketJobQueueService.enqueue_job()` in `app/features/market/job_queue_service.py` |
| `explore.jobs` is declared durable at startup | `init_rabbitmq_client()` in `app/clients/rabbitmq_client.py` |
| Constants and statuses | `EXPLORE_JOBS_QUEUE` and `EXPLORE_JOB_KEY_PREFIX` in `app/common/constants.py`, `ExploreJobStatus` in `app/common/enums.py` |
| The Gemini call | still in `MarketService` as `__ask_gemini` and `__handle_gemini_error`, unused since the API stopped calling Gemini |

Nothing consumes `explore.jobs` yet, and the explore dialog in the UI doesn't work until the polling endpoint exists (section 6).

### Settings
In `backend/.env.dev`:
```
GEMINI_PROVIDER=fake
FAKE_GEMINI_LATENCY_S=2
FAKE_GEMINI_FAIL_RATE=0
```
After changing `.env.dev`, recreate the containers with `up -d`. A plain `restart` doesn't reload `env_file`.

### Check helpers (zsh)
Until the polling endpoint exists, the checks read the job straight from Redis.
```bash
# N grocery IDs as a JSON array
ids() { docker exec grocery_dev_postgres sh -c "psql -U \$POSTGRES_USER -d \$POSTGRES_DB -tAc 'select id from grocery limit ${1:-1}'" \
        | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read().split()))'; }

# start an explore of N groceries, print the job id
explore() { curl -s -X POST localhost/api/v1/market/explore -H 'Content-Type: application/json' \
        -d "{\"grocery_ids\":$(ids ${1:-1})}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["job_id"])'; }

# (status, number of results, attempts, error)
job() { docker exec grocery_dev_redis redis-cli GET "market:explore:job:$1" \
        | python3 -c 'import sys,json;j=json.loads(sys.stdin.read() or "null");print(j and (j["status"], len(j["results"]), j.get("attempts"), j.get("error")))'; }

queues() { docker exec grocery_dev_rabbitmq rabbitmqctl -q list_queues name messages_ready messages_unacknowledged; }
calls()  { docker exec grocery_dev_redis redis-cli GET fake_gemini:calls; }

# DB connections sitting inside an open transaction, and for how long
idle_tx() { docker exec grocery_dev_postgres sh -c "psql -U \$POSTGRES_USER -d \$POSTGRES_DB -c \"select pid, state, now() - xact_start as open_for from pg_stat_activity where state like 'idle in transaction%'\""; }
```

---

## 2. V1 – Easy

### What it does
```
 explore.jobs ──▶ worker
                    read the job from Redis → status = running
                    open a DB session, load the groceries
                    for each grocery: Gemini → append the result → save
                    status = done → ack
                    any exception → reject → RabbitMQ discards the message
```

### Steps
| # | What | Where |
|---|---|---|
| 1 | Move `EXPLORE_PROMPT`, `__ask_gemini` and `__handle_gemini_error` out of `MarketService` into a new `MarketExplorer` class with one public method, `explore_grocery(grocery)`. Then remove `gemini` from `MarketService.__init__` and from `get_market_service`. | `app/features/market/market_explorer.py` (new), `service.py`, `dependencies.py` |
| 2 | Add `get_job(job_id)` and `save_job(job)` | `MarketJobQueueService` |
| 3 | The consumer | `app/worker/explore_consumer.py` (new) |
| 4 | The entry point, run with `python -m app.worker` | `app/worker/__init__.py` (empty), `app/worker/__main__.py` (new) |
| 5 | A `worker` service in compose | `docker-compose.scale.yml`, `docker-compose.dev.yml` |

Remember: no functions inside methods. Helpers are private `__methods` on the class, and the RabbitMQ callback can be a bound method: `queue.consume(self.__on_message)`.

### Step 1: `MarketExplorer`
```python
# app/features/market/market_explorer.py
class MarketExplorer:
    """Asks Gemini for one grocery's shop offers. Used by the worker, not the API."""

    def __init__(self, gemini: genai.Client | FakeGeminiClient):
        self.gemini = gemini

    async def explore_grocery(self, grocery: Grocery) -> GroceryExploreResultSchema:
        offers = await self.__ask_gemini(grocery)   # raises GeminiException (or a subclass)
        return GroceryExploreResultSchema(
            grocery_id=grocery.id,
            offers=offers,
            cheapest=min(offers, key=lambda offer: offer.price, default=None),
        )

    # __ask_gemini and __handle_gemini_error: moved here unchanged
```
The `GeminiException` classes carry an HTTP `status_code` the worker doesn't use, but their `message` and `detail` are exactly what V2 stores in a failed job.

### Step 2: read and save the job
```python
async def get_job(self, job_id: str) -> dict | None:
    return await self.redis_service.get(self.__job_key(job_id))

async def save_job(self, job: dict) -> None:
    # set() also resets the TTL, so a long job doesn't expire while it's running
    await self.redis_service.set(self.__job_key(job['job_id']), job, ttl=settings.EXPLORE_JOB_TTL_S)
```
Pass the dict: `RedisService.set` already calls `json.dumps`. Store results with `result.model_dump(mode='json')`, because UUIDs aren't JSON.

### Step 3: the consumer
`message.process()` is aio-pika's easy helper: it acks when the block finishes, and when the block raises, it rejects the message and re-raises (aio-pika then logs the traceback).

```python
# app/worker/explore_consumer.py
class ExploreJobConsumer:
    def __init__(self, channel: AbstractRobustChannel, jobs: MarketJobQueueService, explorer: MarketExplorer):
        self.channel = channel
        self.jobs = jobs
        self.explorer = explorer

    async def start(self) -> None:
        queue = await self.channel.get_queue(EXPLORE_JOBS_QUEUE)
        await queue.consume(self.__on_message)
        # ⚠️ CLUE 1: no prefetch limit

    async def __on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):       # ack on success, reject on an exception
            body = json.loads(message.body)
            logger.info(f"⚙️ [WORKER] job {body['job_id']} received (redelivered={message.redelivered})")
            await self.__run_job(body['job_id'])

    async def __run_job(self, job_id: str) -> None:
        job = await self.jobs.get_job(job_id)            # ⚠️ CLUE 6: what if it's None?
        job['status'] = ExploreJobStatus.RUNNING.value
        await self.jobs.save_job(job)

        async with async_session_factory() as session:  # ⚠️ CLUE 2: how long is this open?
            groceries = await MarketRepository(session).get_groceries_by_ids([UUID(gid) for gid in job['grocery_ids']])
            for grocery in groceries:                     # ⚠️ CLUE 5: what if this job ran before?
                result = await self.explorer.explore_grocery(grocery)   # ⚠️ CLUE 3: what if this raises?
                job['results'].append(result.model_dump(mode='json'))
                await self.jobs.save_job(job)

        job['status'] = ExploreJobStatus.DONE.value
        await self.jobs.save_job(job)
        # ⚠️ CLUE 4: what does Redis say when something above raised?
```

### Step 4: `python -m app.worker`
```python
# app/worker/__main__.py
class Worker:
    def __init__(self):
        self.stop_event = asyncio.Event()

    async def run(self) -> None:
        configure_logging(level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
        await init_redis()            # same order as main.py: the fake Gemini needs Redis
        await init_gemini_client()
        await init_rabbitmq_client()  # also declares explore.jobs

        consumer = ExploreJobConsumer(
            get_rabbitmq_channel(),
            MarketJobQueueService(get_rabbitmq_channel(), RedisService(get_redis())),
            MarketExplorer(get_gemini_client()),
        )
        await consumer.start()
        logger.info("⚙️ [WORKER] waiting for explore jobs")
        await self.stop_event.wait()  # ⚠️ CLUE 7: nothing ever sets it


if __name__ == '__main__':
    asyncio.run(Worker().run())
```

### Step 5: compose
The worker is the API image with a different command. In `docker-compose.scale.yml`, next to `backend-1..3`:
```yaml
  worker:
    <<: *backend
    container_name: grocery-worker
    hostname: grocery-worker
    command: ["python", "-m", "app.worker"]
```
It has no port, and nginx doesn't route to it. For `docker-compose.dev.yml`, copy the `backend` service, drop `ports`, and add the same `command` and `container_name`.

### V1 checks: it works
| # | Check | Expect |
|---|---|---|
| 1 | `J=$(explore 3); job $J; sleep 7; job $J` | `pending` or `running` first, then `('done', 3, ...)` |
| 2 | `curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' -X POST localhost/api/v1/market/explore -H 'Content-Type: application/json' -d "{\"grocery_ids\":$(ids 50)}"` | `202` well under a second. Before: 504 after 60 s |
| 3 | `docker stop grocery-worker; for i in {1..5}; do explore 1; done; queues; docker start grocery-worker; sleep 15; queues` | 5 ready while the worker is down, 0 after it starts, all 5 jobs `done` |
| 4 | `FAKE_GEMINI_LATENCY_S=5`: `J=$(explore 4); sleep 8; docker kill grocery-worker; queues; docker start grocery-worker; sleep 25; job $J` | the message goes back to ready, it's redelivered (`redelivered=True` in the log), and the job ends `done` |

Check 4 is the core lesson of message queues: **the work survives the worker dying**, because the message was never acked.

### V1 clue checks: make each problem happen
| Clue | How to trigger it | What you'll see |
|---|---|---|
| **1. No prefetch** | `docker stop grocery-worker; for i in {1..5}; do explore 3; done; docker start grocery-worker; docker logs -f grocery-worker` | All 5 `received` lines at once, and their Gemini calls interleave. Without `prefetch_count`, RabbitMQ pushes every waiting message to the worker, and aio-pika runs each callback as its own task. 5 jobs hit Gemini at the same time, which burns the free-tier RPM. |
| **2. Session held during Gemini** | `FAKE_GEMINI_LATENCY_S=10`: `explore 3; sleep 2; idle_tx` | One connection `idle in transaction`, with `open_for` growing to about 30 s. The first `SELECT` opened a transaction, and it stays open through every Gemini call. That's Step 2's problem 2 again, only now inside the worker. |
| **3. No retry, and the work vanishes** | `FAKE_GEMINI_FAIL_RATE=0.5`: `for i in {1..5}; do explore 3; done; sleep 30; queues; docker logs grocery-worker \| grep -c Traceback` | Several tracebacks, and every queue at 0. One 503 on any grocery fails the whole job, and the rejected message is discarded: there's nowhere to look at it later. |
| **4. Failed job looks alive** | the same run: `job <a job id from a traceback>` | `('running', ...)` with no `error`. A polling client would wait until the TTL expires. |
| **5. Redelivery starts over** | V1 check 4, plus `before=$(calls)` first and `echo $(( $(calls) - before ))` at the end | 6 Gemini calls for 4 groceries. The redelivered job asked Gemini again for the grocery it already had. |
| **6. Expired job** | `docker stop grocery-worker; J=$(explore 1); docker exec grocery_dev_redis redis-cli DEL "market:explore:job:$J"; docker start grocery-worker; sleep 3; docker logs grocery-worker \| tail` | `TypeError: 'NoneType' object is not subscriptable`, and the message is discarded. In real life this happens when the worker is down longer than `EXPLORE_JOB_TTL_S`. |
| **7. Slow stop** | `J=$(explore 3); sleep 1; time docker stop grocery-worker` | About 10 s. In a container the worker is PID 1, and Linux ignores `SIGTERM` for PID 1 unless the process installs a handler, so Docker waits 10 s and then sends `SIGKILL`. |

### V1 done when
- [ ] V1 checks 1–4 pass.
- [ ] You've triggered all 7 clues and can say why each one happens.
- [ ] The Step 2 table in `phase-6-plan.md` has "response time", "worker down" and "restart during an explore" filled in.

---

## 3. V2 – Standard

### V2 setup: a retry queue and a dead-letter queue
Clue 3 needs two new queues:
- `explore.jobs.retry`: a waiting room with no consumer. Its messages expire after a delay and go back to `explore.jobs`.
- `explore.jobs.dlq`: where failed jobs end up, so you can look at them.

1. **Constants and settings:**
   - `app/common/constants.py`: `EXPLORE_JOBS_RETRY_QUEUE = 'explore.jobs.retry'` and `EXPLORE_JOBS_DLQ = 'explore.jobs.dlq'`.
   - `app/core/config.py`: `EXPLORE_MAX_RETRIES: int = 3` and `EXPLORE_RETRY_DELAY_S: int = 10`.
   - Also add both settings to `.env.dev.sample`.
   - Watch for trailing commas: `X = 'a',` is a tuple, and `X: int = 3,` makes `Settings()` fail at startup.
2. **Declare the queues.** A queue's arguments are fixed when it's created, and every declare must use the same arguments, or RabbitMQ closes the channel with `PRECONDITION_FAILED`. So the API and the worker declare them through one shared function, called from `init_rabbitmq_client` in place of the current `declare_queue`:
   ```python
   # app/clients/rabbitmq_client.py
   async def declare_explore_queues(channel: AbstractRobustChannel) -> None:
       await channel.declare_queue(EXPLORE_JOBS_DLQ, durable=True)

       await channel.declare_queue(EXPLORE_JOBS_RETRY_QUEUE, durable=True, arguments={
           'x-message-ttl': settings.EXPLORE_RETRY_DELAY_S * 1000,
           'x-dead-letter-exchange': '',                    # '' = the default exchange
           'x-dead-letter-routing-key': EXPLORE_JOBS_QUEUE,
       })

       # rejected messages (reject(requeue=False)) now go to the DLQ instead of being discarded
       await channel.declare_queue(EXPLORE_JOBS_QUEUE, durable=True, arguments={
           'x-dead-letter-exchange': '',
           'x-dead-letter-routing-key': EXPLORE_JOBS_DLQ,
       })
   ```
3. **One-time step:** the broker already has `explore.jobs` **without** these arguments, so the new declare fails. Delete it once before starting the new code:
   ```bash
   docker exec grocery_dev_rabbitmq rabbitmqctl delete_queue explore.jobs
   ```
   Changing `EXPLORE_RETRY_DELAY_S` later has the same effect on `explore.jobs.retry`: delete that queue after changing it.
4. **`MarketJobQueueService.publish_retry(body)`:** publish the body with `retry_count + 1` to `EXPLORE_JOBS_RETRY_QUEUE` through the default exchange, persistent, `mandatory=True`, with the same `correlation_id`. It's like `enqueue_job`, so the message format stays in one place.

### One fix per clue
| Clue | Fix | Where |
|---|---|---|
| 1 | `await self.channel.set_qos(prefetch_count=1)` before `consume` | `start()` |
| 2 | Load the groceries in a short `async with async_session_factory()` block that **returns** before the loop. `expire_on_commit=False` keeps `id`, `name` and `brand` readable after it closes; don't touch relationships. | a `__load_groceries()` static method |
| 3 | **Retries.** On a `GeminiException`, if `retry_count < EXPLORE_MAX_RETRIES`, call `publish_retry`, then ack the original. Otherwise mark the job failed and reject it, which now sends it to the DLQ. | a `__retry_or_fail()` method |
| 4 | Every failure path sets `status = failed` and `error = {message, detail}` before rejecting. For a non-Gemini exception (a bug), also `logger.exception(...)`. | `__on_message()` |
| 5 | Skip groceries whose id is already in `job['results']`, so a retry or redelivery resumes instead of restarting | `__run_job()` |
| 6 | `job is None` → log and return (the ack drops it). `status == done` → return (a redelivery of a finished job). | `__run_job()` |
| 7 | `loop.add_signal_handler(sig, self.stop_event.set)` for `SIGTERM` and `SIGINT`, then close the clients in reverse order (RabbitMQ, Gemini, Redis) and `engine.dispose()` | `Worker`: `__handle_signals()`, `__stop_clients()` |

Two more basics that come with the fixes:
- **Switch from `message.process()` to manual `ack()` / `reject()`.** A retry has to ack only **after** the retry is published: if the worker dies in between you get a harmless duplicate, never a lost job. `process()` can't express that order.
- **Parse the body inside the `try`.** If `json.loads` or `body['retry_count']` raises outside it, the message is neither acked nor rejected and stays unacked. With prefetch 1 that stalls the worker until it restarts.

### V2 checks
Run the V1 clue checks again; each one should now behave differently:

| Clue | Now expect |
|---|---|
| 1 | `received` lines one at a time, 2 s × 3 groceries apart |
| 2 | `idle_tx` shows nothing while Gemini runs |
| 3 | `FAKE_GEMINI_FAIL_RATE=0.5`, 10 × `explore 1`, `sleep 60`: nearly all `done`, some with `attempts` > 1. A job fails only if 4 attempts in a row fail (0.5⁴ ≈ 6 %). |
| 3 + 4 | `FAKE_GEMINI_FAIL_RATE=1.0`: `J=$(explore 1); sleep 45; job $J; queues` gives `('failed', 0, 4, {'message': 'Gemini is overloaded...'})` and 1 message in `explore.jobs.dlq`. Running `queues` every few seconds shows the message moving between `explore.jobs.retry` and `explore.jobs`. |
| 5 | V1 check 4 makes 5 Gemini calls, not 6 |
| 6 | the worker logs "expired", the queue goes back to 0, nothing is in the DLQ |
| 7 | `docker stop` takes about 1 s |

One read check for the plan's table, on the dev stack (one API, `POOL_SIZE=1`) with `FAKE_GEMINI_LATENCY_S=15`:
```bash
explore 1 >/dev/null; sleep 1
curl -s -o /dev/null -w 'GET detail: %{time_total}s\n' localhost:8000/api/v1/groceries/<OTHER_ID>
```
It takes milliseconds. To compare, `git checkout 792f9ed` (the simple version) and run the same check.

### V2 done when
- [ ] Every V1 clue now behaves as in the table above.
- [ ] The Step 2 "Check again" table in `phase-6-plan.md` is fully filled in.

---

## 4. V3 – Hardening

Small, separate changes on top of V2. Each mission starts with a problem you can trigger, and they're ordered from least to most code. Do them in any order.

| Mission | Problem it fixes | Size |
|---|---|---|
| H1. Several workers | jobs queue up behind one worker | compose only |
| H2. Timeouts on Gemini calls | one hung call freezes the worker | a few lines |
| H3. Poison messages | a malformed message is retried or crashes the worker | one model, one branch |
| H4. Graceful drain | `docker stop` cuts off the running job | the `Worker` class |
| H5. Health and visibility | a stuck worker or a growing DLQ goes unnoticed | a heartbeat, logs, one script |

### H1. Several workers (competing consumers)
**Problem:** one worker processes jobs one at a time, so 30 queued jobs take 30 × the job time.
**Do:** remove `container_name` from the worker service and run `docker compose -f docker-compose.scale.yml up -d --scale worker=3`. You don't change any code: with `prefetch_count=1`, RabbitMQ hands each message to whichever worker is free.
**Check:** stop the workers, queue 9 × `explore 3`, then start them. Everything finishes in about a third of the time, and the logs show the jobs shared between the 3 workers. Then set `FAKE_GEMINI_RPM=10`: 3 workers hit the limit 3× faster, which is why Step 3 needs a **shared** rate limit.

### H2. Timeouts on Gemini calls
**Problem:** a Gemini call that never answers blocks the worker forever. With prefetch 1, nothing else runs.
**Do:** add `GEMINI_TIMEOUT_S` to settings. In `MarketExplorer`, wrap the call in `asyncio.wait_for(..., timeout=settings.GEMINI_TIMEOUT_S)` and turn `asyncio.TimeoutError` into a `GeminiUnavailableException`, so V2's retry handles it like a 503.
**Check:** `FAKE_GEMINI_LATENCY_S=120`, `GEMINI_TIMEOUT_S=10`. The job retries after 10 s instead of hanging.

### H3. Poison messages
**Problem:** a malformed message (bad JSON, missing `job_id`) is retried as if it were a Gemini failure, or crashes the worker.
**Do:** validate the body with a Pydantic model, `ExploreJobMessage(job_id: str, grocery_ids: list[str], retry_count: int = 0)`. If it's invalid, log it and reject it straight to the DLQ, and never retry it.
**Check:** publish `{"oops": 1}` to `explore.jobs` from the RabbitMQ UI (`localhost:15672` → Queues → explore.jobs → Publish message). It lands in the DLQ at once, and the worker keeps running.

### H4. Graceful drain
**Problem:** V2 stops fast, but the running job is cut off and redelivered, so its Gemini call is repeated.
**Do:** keep the consumer tag that `queue.consume()` returns. On `SIGTERM`:
1. Stop taking new messages with `await queue.cancel(consumer_tag)`.
2. Wait for the running job to finish, with a timeout such as 25 s. An `asyncio.Event` that `__on_message` sets when it's idle works for this.
3. Close the clients.

Set `stop_grace_period: 30s` on the compose service so Docker waits that long before killing the worker.
**Check:** `J=$(explore 3); sleep 1; docker stop grocery-worker`. The job finishes as `done` before the worker exits, and nothing is redelivered.

### H5. Health and visibility
**Problem:** you only notice a stuck worker or a growing DLQ by looking.
**Do:**
- Put `job_id` in every worker log line.
- Heartbeat: the worker writes the current time to a Redis key every 10 s. Add a compose `healthcheck` that fails when the key is older than 30 s.
- Once a minute, log the queue depth. `await channel.declare_queue(name, passive=True)` doesn't create anything, and its `.declaration_result.message_count` is the number of ready messages.
- Write a small "is the DLQ empty?" check script.

**Check:** `docker ps` shows the worker as `healthy`. Pause it with `docker pause grocery-worker`, and after about 30 s it turns `unhealthy`.

### V3 done when
- [ ] The missions you picked pass their checks.

---

## 5. V4 – Industry

These change how jobs move through the queues, not just how one worker behaves. Do V3's H2 (timeouts) first, because I1 relies on timeouts being retried.

| Mission | Problem it fixes | Size |
|---|---|---|
| I1. Backoff, and respecting 429 | fixed-delay retries hammer an overloaded Gemini | more retry queues |
| I2. Replaying the DLQ | failed jobs stay failed after you fix the cause | a new script |
| I3. One message per grocery (fan-out) | long jobs exceed RabbitMQ's `consumer_timeout`; one slow grocery holds up the rest | a new message format, producer and consumer |

### I1. Backoff, and respecting 429
**Problem:** a fixed 10 s retry hammers Gemini while it's overloaded, and retrying a `429` quickly uses up even more quota.
**Do:** declare several retry queues (for example `explore.jobs.retry.10s`, `.60s` and `.5m`) and pick one by `retry_count`. For `GeminiRateLimitException`, always use the longest. Optionally use the `rabbitmq_delayed_message_exchange` plugin instead of several queues.
**Check:** `FAKE_GEMINI_RPM=3`, then 10 × `explore 1`. The calls spread out over minutes instead of failing in a burst. Compare `fake_gemini:calls` with the V2 result.

### I2. Replaying the DLQ
**Problem:** after you fix a bug or Gemini recovers, the failed jobs are stuck in the DLQ.
**Do:** write `python -m app.worker.replay_dlq`. It takes every DLQ message, publishes it back to `explore.jobs` with `retry_count` reset to 0, sets the job back to `pending` (clearing `error`), and only then acks the DLQ message.
**Check:** run the V2 clue 3 + 4 check with `FAKE_GEMINI_FAIL_RATE=1.0`, set it back to 0, run the replay, and all the jobs end `done`.

### I3. One message per grocery (fan-out)
**Problem:** RabbitMQ closes the channel if a message stays unacked longer than `consumer_timeout`, which defaults to 30 min. 100 groceries × 20 s with the real Gemini is 33 min: the job is redelivered, hits the timeout again, and loops. One slow grocery also delays all the others, and only one worker can work on a job.
**Do:**
- `enqueue_job` publishes **one message per grocery**: `{job_id, grocery_id}`.
- The worker saves that grocery's result into the job.
- The job is `done` when every grocery has a result. Two workers can finish at the same moment, so count with Redis instead of read-modify-write on the job: `HSET` the result, then `HLEN` against the number of groceries.
- Several workers (H1) can now share one job.

**Check:** see the problem first. Put `consumer_timeout = 60000` (1 min) in a `rabbitmq.conf` mounted into the broker, then run `explore 50` with `FAKE_GEMINI_LATENCY_S=2` before and after the change. Before: the channel is closed after a minute and the job loops. After: it finishes.

### V4 done when
- [ ] The missions you picked pass their checks.

### Further reading (no mission)
- **Quorum queues** (`x-queue-type: quorum`) with `x-delivery-limit`: the broker counts redeliveries itself and dead-letters a message that keeps crashing workers. This is the standard for highly available queues.
- **Transactional outbox:** `enqueue_job` writes to Redis, then publishes. These aren't atomic, which is why it deletes the job when the publish fails. When the job state lives in Postgres, the outbox pattern (write the message to a table in the same transaction, and have a relay publish it) makes the pair atomic.
- **Task frameworks** (Taskiq, arq, Celery): they package most of V2–V4. After writing it by hand, you'll know what their settings mean.

---

## 6. After the worker
- `GET /api/v1/jobs/{id}` (reads `get_job`) and polling in `MarketExploreDialog`. Explore works in the UI again after this.
- Step 3 adds the cache and rate limit. The cache check belongs in the worker's loop, before `explore_grocery`.
