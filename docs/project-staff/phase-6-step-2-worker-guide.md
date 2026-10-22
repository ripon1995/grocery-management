# Phase 6 Step 2 – Building the explore worker, in versions

The worker takes jobs from `explore.jobs`, calls Gemini, and writes the results to the job in Redis.
Build it in four versions, each one a commit of its own (or one commit per mission in V3 and V4):

| Version | Goal | You've mastered it when |
|---|---|---|
| **V1 – Easy** | The smallest worker that works end to end. It has known weak spots, marked `⚠️ CLUE` in the code | you can trigger every clue on purpose and explain what went wrong |
| **V2 – Standard** | Fix every clue from V1 with the basic, fundamental patterns | every V1 clue check now behaves differently |
| **V3 – Hardening** | Small changes, one or two files each, that make the V2 worker safe to run for real | each mission's test passes |
| **V4 – Industry** | Bigger design changes: smarter retries, recovering failed jobs, splitting jobs into smaller messages | each mission's test passes |

Every sub-step ends with the same parts:
- **Test:** what you're checking.
- **How:** the commands, using the helpers from section 1.
- **Expect:** what you should see.
- **Achieved:** what the system can do now that it couldn't before.

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
In `backend/.env.dev` (the scale stack's API and the worker both use it):
```
GEMINI_PROVIDER=fake
FAKE_GEMINI_LATENCY_S=2
FAKE_GEMINI_FAIL_RATE=0
```
The code is baked into the image, so after every code change **and** every `.env.dev` change, run `rebuild` (below). A plain `docker restart` doesn't reload `env_file`.

When a step says "`FAKE_GEMINI_LATENCY_S=5`, then …", set that line in `.env.dev`, run `rebuild`, and set it back afterwards.

### Check helpers (zsh)
Paste these into the terminal once per session. Until the polling endpoint exists, the checks read the job straight from Redis.
```bash
# rebuild and (re)start the scale stack after a code or .env.dev change
rebuild() { docker compose -f docker-compose.scale.yml up -d --build; }

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

# run a Python snippet (from a heredoc) inside the API container; $J is passed in as an env var
py() { docker exec -i -e J="$J" grocery-api-1 python -; }

# publish a raw message: publish '<json>' [queue]
publish() { docker exec -e PAYLOAD="$1" grocery_dev_rabbitmq sh -c \
        "rabbitmqadmin -u \$RABBITMQ_DEFAULT_USER -p \$RABBITMQ_DEFAULT_PASS publish exchange=amq.default routing_key=${2:-explore.jobs} payload=\"\$PAYLOAD\""; }
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

| Step | What | Where |
|---|---|---|
| 1 | `MarketExplorer`: the Gemini code, moved out of `MarketService` | `app/features/market/market_explorer.py` (new), `service.py`, `dependencies.py` |
| 2 | `get_job` / `save_job` | `MarketJobQueueService` |
| 3 | The consumer | `app/worker/explore_consumer.py` (new) |
| 4 | The entry point, `python -m app.worker` | `app/worker/__init__.py` (empty), `app/worker/__main__.py` (new) |
| 5 | A `worker` service in compose | `docker-compose.scale.yml`, `docker-compose.dev.yml` |

Remember: no functions inside methods. Helpers are private `__methods` on the class, and the RabbitMQ callback can be a bound method: `queue.consume(self.__on_message)`. The `async def main()` in the test snippets is a top-level function in a throwaway script, not app code.

### Step 1: `MarketExplorer`
Move `EXPLORE_PROMPT`, `__ask_gemini` and `__handle_gemini_error` out of `MarketService` into a new class. Then remove `gemini` from `MarketService.__init__` and from `get_market_service` in `dependencies.py`.
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

**Test:** `MarketExplorer` returns offers for one grocery on its own, and the API still accepts explores without Gemini.
**How:**
```bash
rebuild
py <<'EOF'
import asyncio, uuid
from app.clients.redis_client import init_redis, get_redis
from app.clients.fake_gemini_client import FakeGeminiClient
from app.features.grocery.models import Grocery
from app.features.market.market_explorer import MarketExplorer

async def main():
    await init_redis()
    explorer = MarketExplorer(FakeGeminiClient(get_redis()))
    result = await explorer.explore_grocery(Grocery(id=uuid.uuid4(), name='Miniket Rice', brand='Chashi'))
    print(result.model_dump_json(indent=2))

asyncio.run(main())
EOF
explore 2
```
**Expect:** after about 2 s, up to 3 offers and a `cheapest`; running it again gives the same offers, because the fake is deterministic. `explore 2` still prints a job id.
**Achieved:** the Gemini logic works outside an HTTP request, so a worker can use it, and the API no longer depends on Gemini at all.

### Step 2: read and save the job
Add to `MarketJobQueueService`, next to `__job_key`:
```python
async def get_job(self, job_id: str) -> dict | None:
    return await self.redis_service.get(self.__job_key(job_id))

async def save_job(self, job: dict) -> None:
    # set() also resets the TTL, so a long job doesn't expire while it's running
    await self.redis_service.set(self.__job_key(job['job_id']), job, ttl=settings.EXPLORE_JOB_TTL_S)
```
Pass the dict: `RedisService.set` already calls `json.dumps`. Store results with `result.model_dump(mode='json')`, because UUIDs aren't JSON.

**Test:** a job can be read, changed and saved, and saving resets its TTL.
**How:**
```bash
rebuild
J=$(explore 1); sleep 20
docker exec grocery_dev_redis redis-cli TTL "market:explore:job:$J"
py <<'EOF'
import asyncio, os
from app.clients.redis_client import init_redis, get_redis
from app.clients.rabbitmq_client import init_rabbitmq_client, get_rabbitmq_channel
from app.features.market.job_queue_service import MarketJobQueueService
from app.services.redis_service import RedisService

async def main():
    await init_redis()
    await init_rabbitmq_client()
    jobs = MarketJobQueueService(get_rabbitmq_channel(), RedisService(get_redis()))
    job = await jobs.get_job(os.environ['J'])
    print('read:', job['status'], type(job))
    job['status'] = 'running'
    await jobs.save_job(job)

asyncio.run(main())
EOF
job $J
docker exec grocery_dev_redis redis-cli TTL "market:explore:job:$J"
```
**Expect:**
- The first TTL is about 580.
- `read: pending <class 'dict'>`. If it says `str`, the job was JSON-encoded twice.
- `job $J` shows `('running', 0, None, None)`.
- The second TTL is back to about 600.

**Achieved:** the worker can update a job, and a long job stays in Redis as long as it keeps saving progress.

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

**Test:** the consumer turns the messages waiting in `explore.jobs` into finished jobs, before there's a worker process.
**How:**
```bash
rebuild
J=$(explore 3); queues
py <<'EOF'
import asyncio
from app.core.config import settings
from app.core.log_config import configure_logging
from app.clients.redis_client import init_redis, get_redis
from app.clients.gemini_client import init_gemini_client, get_gemini_client
from app.clients.rabbitmq_client import init_rabbitmq_client, get_rabbitmq_channel
from app.features.market.job_queue_service import MarketJobQueueService
from app.features.market.market_explorer import MarketExplorer
from app.services.redis_service import RedisService
from app.worker.explore_consumer import ExploreJobConsumer

async def main():
    configure_logging(level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
    await init_redis()
    await init_gemini_client()
    await init_rabbitmq_client()
    channel = get_rabbitmq_channel()
    consumer = ExploreJobConsumer(channel, MarketJobQueueService(channel, RedisService(get_redis())), MarketExplorer(get_gemini_client()))
    await consumer.start()
    await asyncio.sleep(20)    # let it work, then exit

asyncio.run(main())
EOF
queues; job $J
```
**Expect:** before, `explore.jobs` has the messages from steps 1–3 ready. During the snippet, a `received` line for each one. After, `explore.jobs` is at 0 and `job $J` is `('done', 3, None, None)`.
**Achieved:** the core of a queue consumer works: a message comes in, the Gemini results are saved to the job, and the message is acked.

### Step 4: `python -m app.worker`
Add an empty `app/worker/__init__.py`, and:
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

**Test:** the worker runs as a process of its own and keeps consuming until it's stopped.
**How:** run `rebuild`, then start the worker in the foreground in a **second terminal**:
```bash
docker exec -it grocery-api-1 python -m app.worker
```
Back in the first terminal:
```bash
J=$(explore 2); sleep 5; job $J
```
Stop the worker with Ctrl+C.
**Expect:** the second terminal logs "waiting for explore jobs" and then the job. `job $J` is `('done', 2, None, None)`. Ctrl+C stops it here, because inside `docker exec` the worker isn't PID 1; clue 7 shows the difference.
**Achieved:** a long-running consumer process built from the same code and settings as the API.

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

**Test:** the stack starts the worker, and it can be restarted without touching the API.
**How:**
```bash
rebuild
docker ps --filter name=grocery-worker --format '{{.Names}} {{.Status}}'
docker logs grocery-worker 2>&1 | grep -E "RABBITMQ|waiting"
docker restart grocery-worker
curl -s -o /dev/null -w '%{http_code}\n' localhost/api/v1/groceries/
```
**Expect:** `grocery-worker Up ...`, the "connected" and "waiting for explore jobs" lines, and `200` from the API throughout.
**Achieved:** the worker is part of the stack but deploys and restarts on its own. Now run the V1 checks.

### V1 checks: it works
| # | Test | How | Expect | Achieved |
|---|---|---|---|---|
| 1 | A job runs end to end | `J=$(explore 3); job $J; sleep 7; job $J` | `pending` or `running` first, then `('done', 3, ...)` | Explore works asynchronously, from request to results |
| 2 | The API answers at once | `curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' -X POST localhost/api/v1/market/explore -H 'Content-Type: application/json' -d "{\"grocery_ids\":$(ids 50)}"` | `202` well under a second. Before: 504 after 60 s | The request no longer waits for Gemini, whatever the job size |
| 3 | Jobs wait while the worker is down | `docker stop grocery-worker; for i in {1..5}; do explore 1; done; queues; docker start grocery-worker; sleep 15; queues` | 5 ready while the worker is down, 0 after it starts, all 5 jobs `done` | The API keeps accepting work when the worker is down: the queue is a buffer |
| 4 | A job survives the worker dying | `FAKE_GEMINI_LATENCY_S=5`, then `J=$(explore 4); sleep 8; docker kill grocery-worker; queues; docker start grocery-worker; sleep 25; job $J` | the message goes back to ready, it's redelivered (`redelivered=True` in the log), and the job ends `done` | No work is lost to a crash, because the message is only acked once the job is done |

Check 4 is the core lesson of message queues.

### V1 clue checks: make each problem happen
Each clue is a test you expect to show a problem. What you achieve is knowing why it happens; V2 fixes it.

| Clue | How to trigger it | What you'll see |
|---|---|---|
| **1. No prefetch** | `docker stop grocery-worker; for i in {1..5}; do explore 3; done; docker start grocery-worker; docker logs -f grocery-worker` | All 5 `received` lines at once, and their Gemini calls interleave. Without `prefetch_count`, RabbitMQ pushes every waiting message to the worker, and aio-pika runs each callback as its own task. 5 jobs hit Gemini at the same time, which burns the free-tier RPM. |
| **2. Session held during Gemini** | `FAKE_GEMINI_LATENCY_S=10`, then `explore 3; sleep 2; idle_tx` | One connection `idle in transaction`, with `open_for` growing to about 30 s. The first `SELECT` opened a transaction, and it stays open through every Gemini call. That's Step 2's problem 2 again, only now inside the worker. |
| **3. No retry, and the work vanishes** | `FAKE_GEMINI_FAIL_RATE=0.5`, then `for i in {1..5}; do explore 3; done; sleep 30; queues; docker logs grocery-worker \| grep -c Traceback` | Several tracebacks, and every queue at 0. One 503 on any grocery fails the whole job, and the rejected message is discarded: there's nowhere to look at it later. |
| **4. Failed job looks alive** | the same run: `job <a job id from a traceback>` | `('running', ...)` with no `error`. A polling client would wait until the TTL expires. |
| **5. Redelivery starts over** | V1 check 4, with `before=$(calls)` first and `echo $(( $(calls) - before ))` at the end | 6 Gemini calls for 4 groceries. The redelivered job asked Gemini again for the grocery it already had. |
| **6. Expired job** | `docker stop grocery-worker; J=$(explore 1); docker exec grocery_dev_redis redis-cli DEL "market:explore:job:$J"; docker start grocery-worker; sleep 3; docker logs grocery-worker \| tail` | `TypeError: 'NoneType' object is not subscriptable`, and the message is discarded. In real life this happens when the worker is down longer than `EXPLORE_JOB_TTL_S`. |
| **7. Slow stop** | `J=$(explore 3); sleep 1; time docker stop grocery-worker` | About 10 s. In a container the worker is PID 1, and Linux ignores `SIGTERM` for PID 1 unless the process installs a handler, so Docker waits 10 s and then sends `SIGKILL`. |

### V1 done when
- [ ] Steps 1–5 and V1 checks 1–4 pass.
- [ ] You've triggered all 7 clues and can say why each one happens.
- [ ] The Step 2 table in `phase-6-plan.md` has "response time", "worker down" and "restart during an explore" filled in.

---

## 3. V2 – Standard

V2 first adds a retry queue and a dead-letter queue (setup S1–S3), then fixes the V1 clues one at a time (F1–F9). Rebuild after each change.

### S1. Constants and settings
- `app/common/constants.py`: `EXPLORE_JOBS_RETRY_QUEUE = 'explore.jobs.retry'` and `EXPLORE_JOBS_DLQ = 'explore.jobs.dlq'`.
- `app/core/config.py`: `EXPLORE_MAX_RETRIES: int = 3` and `EXPLORE_RETRY_DELAY_S: int = 10`. Add both to `.env.dev.sample` too.
- Watch for trailing commas: `X = 'a',` is a tuple, and `X: int = 3,` makes `Settings()` fail at startup.

**Test:** the values load with the right types.
**How:**
```bash
rebuild
py <<'EOF'
from app.core.config import settings
from app.common.constants import EXPLORE_JOBS_RETRY_QUEUE, EXPLORE_JOBS_DLQ
print(repr(settings.EXPLORE_MAX_RETRIES), repr(settings.EXPLORE_RETRY_DELAY_S), repr(EXPLORE_JOBS_RETRY_QUEUE), repr(EXPLORE_JOBS_DLQ))
EOF
```
**Expect:** `3 10 'explore.jobs.retry' 'explore.jobs.dlq'`. A `(3,)` or `('explore.jobs.retry',)` means a stray comma.
**Achieved:** retry limits are configuration, shared by the API and the worker.

### S2. Declare the retry queue and the DLQ
- `explore.jobs.retry` is a waiting room with no consumer. Its messages expire after a delay and go back to `explore.jobs`.
- `explore.jobs.dlq` is where failed jobs end up, so you can look at them.

A queue's arguments are fixed when it's created, and every declare must use the same arguments, or RabbitMQ closes the channel with `PRECONDITION_FAILED`. So the API and the worker declare the queues through one shared function, called from `init_rabbitmq_client` in place of the current `declare_queue`:
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
The broker already has `explore.jobs` **without** these arguments, so the new declare fails until you delete the old queue once. Changing `EXPLORE_RETRY_DELAY_S` later has the same effect on `explore.jobs.retry`.

**Test:** first see the mismatch fail, then see the three queues created with their arguments.
**How:**
```bash
rebuild; sleep 5
docker logs grocery-api-1 2>&1 | grep -m1 PRECONDITION_FAILED
docker exec grocery_dev_rabbitmq rabbitmqctl delete_queue explore.jobs
rebuild; sleep 5
docker exec grocery_dev_rabbitmq rabbitmqctl -q list_queues name arguments
```
**Expect:** the first rebuild logs `PRECONDITION_FAILED` and the API doesn't start. After deleting the queue, the API starts and `list_queues` shows `explore.jobs` with `x-dead-letter-routing-key: explore.jobs.dlq`, `explore.jobs.retry` with `x-message-ttl: 10000`, and `explore.jobs.dlq` with no arguments.
**Achieved:** failed and retried messages have somewhere to go. You've also seen first-hand that queue settings are a contract every client has to share.

### S3. `MarketJobQueueService.publish_retry(body)`
Publish the body with `retry_count + 1` to `EXPLORE_JOBS_RETRY_QUEUE` through the default exchange, persistent, `mandatory=True`, with the same `correlation_id`. It's like `enqueue_job`, so the message format stays in one place.

**Test:** a retried message waits `EXPLORE_RETRY_DELAY_S` and then comes back to `explore.jobs` by itself.
**How:**
```bash
docker stop grocery-worker            # so nothing consumes the message when it comes back
J=$(explore 1)
py <<'EOF'
import asyncio, os
from app.clients.redis_client import init_redis, get_redis
from app.clients.rabbitmq_client import init_rabbitmq_client, get_rabbitmq_channel
from app.features.market.job_queue_service import MarketJobQueueService
from app.services.redis_service import RedisService

async def main():
    await init_redis()
    await init_rabbitmq_client()
    jobs = MarketJobQueueService(get_rabbitmq_channel(), RedisService(get_redis()))
    job = await jobs.get_job(os.environ['J'])
    await jobs.publish_retry({'job_id': job['job_id'], 'grocery_ids': job['grocery_ids'], 'retry_count': 0})

asyncio.run(main())
EOF
queues; sleep 11; queues
docker start grocery-worker
```
**Expect:** first 1 message in `explore.jobs.retry`. 11 s later it's gone from there, and `explore.jobs` has one more. In the UI (`localhost:15672` → Queues → explore.jobs → Get messages), the returned message has `retry_count: 1`.
**Achieved:** delayed retries without the worker sleeping: the broker holds the message, and the worker is free for other jobs meanwhile.

### F1. Prefetch (fixes clue 1)
**Do:** `await self.channel.set_qos(prefetch_count=1)` before `consume` in `start()`.
**Test:** queued jobs run one after another.
**How:** clue 1's commands.
**Expect:** `received` lines one at a time, about 6 s apart (3 groceries × 2 s). `queues` shows 1 unacked and the rest ready.
**Achieved:** the worker only takes what it can handle, and the rest waits in the queue, where other workers can take it (V3 H1).

### F2. Short DB session (fixes clue 2)
**Do:** a `__load_groceries()` static method that opens `async with async_session_factory()`, loads the groceries and **returns** before the Gemini loop. `expire_on_commit=False` keeps `id`, `name` and `brand` readable after the session closes; don't touch relationships.
**Test:** no connection stays open while Gemini runs.
**How:** clue 2's commands.
**Expect:** `idle_tx` shows no rows.
**Achieved:** a job holds a DB connection for milliseconds, not for its whole run, so the pool stays free however slow Gemini is.

### F3. Retries (fixes clue 3)
**Do:** a `__retry_or_fail()` method. On a `GeminiException`: if `retry_count < EXPLORE_MAX_RETRIES`, call `publish_retry`, then ack the original. Otherwise mark the job failed (F4) and reject it, which now sends it to the DLQ.
**Test:** failures that come and go recover by themselves, and failures that don't go away end in the DLQ.
**How:**
```bash
# FAKE_GEMINI_FAIL_RATE=0.5, then:
before=$(calls); JOBS=(); for i in {1..10}; do JOBS+=$(explore 1); done
sleep 60; for J in $JOBS; do job $J; done; queues; echo "Gemini calls: $(( $(calls) - before ))"

# FAKE_GEMINI_FAIL_RATE=1.0, then:
J=$(explore 1); for i in {1..9}; do queues; sleep 5; done; job $J
```
**Expect:**
- At 0.5: nearly all 10 jobs `done`, some with `attempts` > 1, and more than 10 Gemini calls. A job fails only if 4 attempts in a row fail (0.5⁴ ≈ 6 %).
- At 1.0: the message moves between `explore.jobs.retry` and `explore.jobs` 3 times, then sits in `explore.jobs.dlq`.

**Achieved:** short Gemini outages no longer fail jobs, and jobs that can't succeed are kept where you can inspect them instead of disappearing.

### F4. Mark failed jobs (fixes clue 4)
**Do:** every failure path in `__on_message()` sets `status = failed` and `error = {'message': e.message, 'detail': e.detail}`, saves, then rejects. For a non-Gemini exception (a bug), also call `logger.exception(...)`.
**Test:** a failed job says so, for both a Gemini failure and a bug.
**How:**
- Gemini failure: F3's `FAKE_GEMINI_FAIL_RATE=1.0` run, then `job $J`.
- Bug: temporarily add `raise RuntimeError('test bug')` at the top of the grocery loop, rebuild, then `J=$(explore 1); sleep 3; job $J; queues`. Remove the line afterwards.

**Expect:** `('failed', 0, 4, {'message': 'Gemini is overloaded right now...', ...})` for the Gemini case. For the bug: `failed` with the error, a traceback in the log, and the message in the DLQ.
**Achieved:** a client polling the job always learns the outcome, instead of waiting on `running` until the TTL expires.

### F5. Resume instead of restart (fixes clue 5)
**Do:** in `__run_job()`, skip groceries whose id is already in `job['results']`.
**Test:** a redelivered job doesn't ask Gemini again for groceries it already has.
**How:** V1 check 4, with `before=$(calls)` first and `echo $(( $(calls) - before ))` at the end.
**Expect:** 5 Gemini calls, not 6. Only the grocery that was in flight when the worker was killed is asked twice.
**Achieved:** processing a message twice is safe and cheap. RabbitMQ delivers at least once, so this is what makes redelivery acceptable.

### F6. Expired and finished jobs (fixes clue 6)
**Do:** in `__run_job()`: if `job is None`, log "expired" and return, so the ack drops the message. If `status == done`, return: it's a redelivery of a finished job.
**Test:** both cases are acked quietly, without a traceback or a Gemini call.
**How:**
```bash
# expired: clue 6's commands
# already done: send a finished job's message again
J=$(explore 1); sleep 4; job $J; before=$(calls)
publish "{\"job_id\":\"$J\",\"grocery_ids\":[],\"retry_count\":0}"
sleep 2; docker logs grocery-worker 2>&1 | tail -3; queues; echo "Gemini calls: $(( $(calls) - before ))"
```
**Expect:** an "expired" log line for the first case and an "already done" line for the second, every queue at 0 with nothing in the DLQ, and 0 new Gemini calls.
**Achieved:** stale and duplicate messages are harmless.

### F7. Fast, clean stop (fixes clue 7)
**Do:** in `Worker`, a `__handle_signals()` method that calls `loop.add_signal_handler(sig, self.stop_event.set)` for `SIGTERM` and `SIGINT`, and a `__stop_clients()` method that closes RabbitMQ, Gemini and Redis in that order, then calls `engine.dispose()`.
**Test:** `docker stop` returns quickly and the worker shuts down in order.
**How:**
```bash
J=$(explore 3); sleep 1; time docker stop grocery-worker
docker logs grocery-worker 2>&1 | tail -4
docker start grocery-worker; sleep 10; job $J
```
**Expect:** about 1 s instead of 10. The log ends with "stopping" and the clients closing. After the restart the job is redelivered, and thanks to F5 it finishes `done`.
**Achieved:** deploys and restarts are fast, and the worker is never killed in the middle of a write.

### F8. Manual ack and reject
**Do:** replace `message.process()` with explicit `await message.ack()` and `await message.reject(requeue=False)`. A retry must ack the original only **after** `publish_retry` has succeeded.
**Test:** no job is lost on the retry path.
**How:** F3's `FAKE_GEMINI_FAIL_RATE=0.5` run with 10 jobs.
**Expect:** every one of the 10 job ids ends `done` or `failed`; none is stuck at `pending` or `running`.
**Achieved:** you control exactly when the broker forgets a message. If the worker dies between publish and ack, you get a harmless duplicate, never a lost job.

### F9. Parse the body inside the `try`
**Do:** move `json.loads(message.body)` and reading `body['job_id']` / `body['retry_count']` inside the `try` in `__on_message()`, so a bad body is rejected like any other bug.
**Test:** a malformed message can't stall the worker.
**How:** `publish '{"oops": 1}'; sleep 2; queues; J=$(explore 1); sleep 4; job $J`
**Expect:** the bad message is in the DLQ with a logged error, and the next real job still ends `done`. Without this fix, the bad message stays unacked, and with prefetch 1 nothing else gets processed.
**Achieved:** one bad message can't take the worker down. V3 H3 refines this by not treating it as a bug.

### V2 read check, for the plan's table
**Test:** a normal read isn't slowed down by a running explore.
**How:** on the dev stack (one API, `POOL_SIZE=1`) with `FAKE_GEMINI_LATENCY_S=15`:
```bash
explore 1 >/dev/null; sleep 1
curl -s -o /dev/null -w 'GET detail: %{time_total}s\n' localhost:8000/api/v1/groceries/<OTHER_ID>
```
To compare, `git checkout 792f9ed` (the simple version) and run the same check.
**Expect:** milliseconds now. With the simple version it waits for the pool.
**Achieved:** the number for "GET /groceries/{id} while an explore is running" in the Step 2 table.

### V2 done when
- [ ] S1–S3 and F1–F9 pass their tests.
- [ ] The Step 2 "Check again" table in `phase-6-plan.md` is fully filled in.

---

## 4. V3 – Hardening

Small, separate changes on top of V2. Each mission starts with a problem you can trigger, and they're ordered from least to most code. Do them in any order.

| Mission | Problem it fixes | Size |
|---|---|---|
| H1. Several workers | jobs queue up behind one worker | compose only |
| H2. Timeouts on Gemini calls | one hung call freezes the worker | a few lines |
| H3. Poison messages | a malformed message is treated as a bug | one model, one branch |
| H4. Graceful drain | `docker stop` cuts off the running job | the `Worker` class |
| H5. Health and visibility | a stuck worker or a growing DLQ goes unnoticed | a heartbeat, logs, one script |

### H1. Several workers (competing consumers)
**Problem:** one worker processes jobs one at a time, so 30 queued jobs take 30 × the job time.
**Do:** remove `container_name` from the worker service and run `docker compose -f docker-compose.scale.yml up -d --scale worker=3`. You don't change any code: with `prefetch_count=1`, RabbitMQ hands each message to whichever worker is free. (The other commands in this guide use `grocery-worker`; with several workers, use `docker compose -f docker-compose.scale.yml logs worker` instead.)
**Test:** 3 workers share the queue, and the same work finishes about 3× faster.
**How:** run this once with `--scale worker=1` and once with `--scale worker=3`:
```bash
docker compose -f docker-compose.scale.yml stop worker
for i in {1..9}; do explore 3; done
time (docker compose -f docker-compose.scale.yml start worker; while [ "$(docker exec grocery_dev_rabbitmq rabbitmqctl -q list_queues name messages | awk '$1=="explore.jobs"{print $2}')" != "0" ]; do sleep 1; done)
docker compose -f docker-compose.scale.yml logs worker | grep received | awk '{print $1}' | sort | uniq -c
```
Then set `FAKE_GEMINI_RPM=10` and run it again with 3 workers.
**Expect:** about 54 s with 1 worker (9 jobs × 3 groceries × 2 s) and about 18 s with 3, with the `received` lines split roughly 3 / 3 / 3. With the RPM limit, 3 workers hit `429` 3× sooner, which is why Step 3 needs a **shared** rate limit.
**Achieved:** throughput scales by adding workers, with no code change. This is the competing-consumers pattern.

### H2. Timeouts on Gemini calls
**Problem:** a Gemini call that never answers blocks the worker forever. With prefetch 1, nothing else runs.
**Do:** add `GEMINI_TIMEOUT_S` to settings. In `MarketExplorer`, wrap the call in `asyncio.wait_for(..., timeout=settings.GEMINI_TIMEOUT_S)` and turn `asyncio.TimeoutError` into a `GeminiUnavailableException`, so V2's retry handles it like a 503.
**Test:** a hung call becomes a normal retry.
**How:** `FAKE_GEMINI_LATENCY_S=120` and `GEMINI_TIMEOUT_S=10`, then `J=$(explore 1); sleep 15; job $J; queues; docker logs grocery-worker 2>&1 | tail -3`
**Expect:** after 10 s, a timeout in the log and the message in `explore.jobs.retry`. After all the retries, the job is `failed` with a timeout error.
**Achieved:** the time any one call can take is bounded, so a hung dependency can't freeze the worker.

### H3. Poison messages
**Problem:** V2 rejects a malformed message as if it were a bug: a traceback, and no clear reason recorded.
**Do:** validate the body with a Pydantic model, `ExploreJobMessage(job_id: str, grocery_ids: list[str], retry_count: int = 0)`. If it's invalid, log one warning line with the reason, reject it straight to the DLQ, and never retry it.
**Test:** bad messages are recognised and set aside, while good ones keep flowing.
**How:** `publish '{"oops": 1}'; publish 'not json'; sleep 2; docker logs grocery-worker 2>&1 | tail -4; queues; J=$(explore 1); sleep 4; job $J`
**Expect:** two "invalid message" warnings with no tracebacks, 2 messages in the DLQ, and the real job `done`.
**Achieved:** bad input is isolated and labelled, and never mistaken for a Gemini problem.

### H4. Graceful drain
**Problem:** V2 stops fast, but the running job is cut off and redelivered, so its Gemini call is repeated.
**Do:** keep the consumer tag that `queue.consume()` returns. On `SIGTERM`:
1. Stop taking new messages with `await queue.cancel(consumer_tag)`.
2. Wait for the running job to finish, with a timeout such as 25 s. An `asyncio.Event` that `__on_message` sets when it's idle works for this.
3. Close the clients.

Set `stop_grace_period: 30s` on the compose service so Docker waits that long before killing the worker.
**Test:** a planned stop finishes the running job instead of cutting it off.
**How:** `before=$(calls); J=$(explore 3); sleep 1; time docker stop grocery-worker; job $J; queues; echo "Gemini calls: $(( $(calls) - before ))"`
**Expect:** `docker stop` takes about 5 s (the rest of the job), the job is `done`, nothing is waiting in `explore.jobs`, and exactly 3 Gemini calls were made.
**Achieved:** deploys don't waste work. Redelivery is left for real crashes.

### H5. Health and visibility
**Problem:** you only notice a stuck worker or a growing DLQ by looking.
**Do:**
- Put `job_id` in every worker log line.
- Heartbeat: the worker writes the current time to a Redis key every 10 s. Add a compose `healthcheck` that fails when the key is older than 30 s.
- Once a minute, log the queue depth. `await channel.declare_queue(name, passive=True)` doesn't create anything, and its `.declaration_result.message_count` is the number of ready messages.
- Write a small "is the DLQ empty?" check script that exits non-zero when it isn't.

**Test:** an unhealthy worker and a non-empty DLQ are detected without you reading logs.
**How:**
```bash
docker ps --filter name=grocery-worker --format '{{.Status}}'
docker pause grocery-worker; sleep 40
docker ps --filter name=grocery-worker --format '{{.Status}}'
docker unpause grocery-worker
J=$(explore 1); sleep 4; docker logs grocery-worker 2>&1 | grep -c "$J"
```
For the DLQ script, run F3's `FAKE_GEMINI_FAIL_RATE=1.0` check, then the script.
**Expect:** `(healthy)`, then `(unhealthy)` after the pause, several log lines carrying the job id, and the DLQ script exiting non-zero.
**Achieved:** problems are noticed by Docker and scripts, and every log line can be traced to a job.

### V3 done when
- [ ] The missions you picked pass their tests.

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
**Test:** retries spread out over time, and rate-limited jobs wait the longest.
**How:** `FAKE_GEMINI_RPM=3`, then run this with V2's code and again with backoff:
```bash
before=$(calls); for i in {1..10}; do explore 1; done
for i in {1..12}; do queues; sleep 30; done
echo "Gemini calls: $(( $(calls) - before ))"
```
**Expect:** with backoff, messages sit in the longer retry queues, and the calls are spread over several minutes, with fewer `429`s and fewer Gemini calls in total than V2.
**Achieved:** retries adapt to how Gemini is doing, and the free-tier quota isn't spent on calls that are bound to fail.

### I2. Replaying the DLQ
**Problem:** after you fix a bug or Gemini recovers, the failed jobs are stuck in the DLQ.
**Do:** write `python -m app.worker.replay_dlq`. It takes every DLQ message, publishes it back to `explore.jobs` with `retry_count` reset to 0, sets the job back to `pending` (clearing `error`), and only then acks the DLQ message.
**Test:** failed jobs can be brought back and finish once the cause is fixed.
**How:**
```bash
# FAKE_GEMINI_FAIL_RATE=1.0, then:
JOBS=(); for i in {1..3}; do JOBS+=$(explore 1); done; sleep 45; queues
# FAKE_GEMINI_FAIL_RATE=0, then:
docker exec grocery-worker python -m app.worker.replay_dlq
sleep 10; queues; for J in $JOBS; do job $J; done
```
**Expect:** 3 messages in the DLQ before the replay. After it, the DLQ is at 0 and all 3 jobs are `done`.
**Achieved:** recovering from an outage takes one command, and nobody has to explore again by hand.

### I3. One message per grocery (fan-out)
**Problem:** RabbitMQ closes the channel if a message stays unacked longer than `consumer_timeout`, which defaults to 30 min. 100 groceries × 20 s with the real Gemini is 33 min: the job is redelivered, hits the timeout again, and loops. One slow grocery also delays all the others, and only one worker can work on a job.
**Do:**
- `enqueue_job` publishes **one message per grocery**: `{job_id, grocery_id}`.
- The worker saves that grocery's result into the job.
- The job is `done` when every grocery has a result. Two workers can finish at the same moment, so count with Redis instead of read-modify-write on the job: `HSET` the result, then `HLEN` against the number of groceries.
- Several workers (H1) can now share one job.

**Test:** a job longer than `consumer_timeout` finishes, and several workers share one job.
**How:** first make the problem visible. Mount a `rabbitmq.conf` with `consumer_timeout = 60000` (1 min) into the broker and keep `FAKE_GEMINI_LATENCY_S=2`. Run this with the V2/V3 code, then again with fan-out and `--scale worker=3`:
```bash
J=$(explore 50); sleep 90; job $J
docker compose -f docker-compose.scale.yml logs worker | grep -i -m1 "timed out"
```
**Expect:** before, after about 1 min the broker closes the channel (`PRECONDITION_FAILED - delivery acknowledgement ... timed out`) and the job starts over and over. After, every message is acked within seconds, all 50 results arrive in about 35 s with 3 workers, and the job is `done` once.
**Achieved:** job size is no longer limited by how long one message may stay unacked, and one big job can be spread across many workers.

### V4 done when
- [ ] The missions you picked pass their tests.

### Further reading (no mission)
- **Quorum queues** (`x-queue-type: quorum`) with `x-delivery-limit`: the broker counts redeliveries itself and dead-letters a message that keeps crashing workers. This is the standard for highly available queues.
- **Transactional outbox:** `enqueue_job` writes to Redis, then publishes. These aren't atomic, which is why it deletes the job when the publish fails. When the job state lives in Postgres, the outbox pattern (write the message to a table in the same transaction, and have a relay publish it) makes the pair atomic.
- **Task frameworks** (Taskiq, arq, Celery): they package most of V2–V4. After writing it by hand, you'll know what their settings mean.

---

## 6. After the worker
- `GET /api/v1/jobs/{id}` (reads `get_job`) and polling in `MarketExploreDialog`. Explore works in the UI again after this.
- Step 3 adds the cache and rate limit. The cache check belongs in the worker's loop, before `explore_grocery`.
