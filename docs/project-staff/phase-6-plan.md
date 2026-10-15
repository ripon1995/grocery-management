# Phase 6 – Advanced Patterns: Implementation Plan

Phase 6 of `system-design-learning-roadmap.md` covers microservices, message queues, rate limiting, API gateway, WebSockets and webhooks.
Instead of building each pattern as an isolated demo, this phase builds **three real features** that need those patterns:

1. **Shopping-list export**: export every `should_include=True` item, grouped by shop.
2. **Explore an item**: pick a grocery, and Gemini (free tier) finds the cheapest price at Shwapno, Chaldal and Meena Bazar, plus any running campaign for it.
3. **Show campaigns**: a list of campaigns currently running at those three shops.

Plan written 2026-10-15.

---

## 1. How every topic is done: problem first, then fix

Each system design topic follows the same 5 parts:

1. **Simple version first.** Build the feature the obvious way, without the pattern.
2. **Problem.** Run a check (a curl, k6, `docker` or log command) that **shows the problem happening**. Record the numbers in the **Before** column.
3. **Fix.** Add the system design pattern.
4. **Check again.** Run **exactly the same** check and record the numbers in the **After** column.
5. **What's achieved.** What the app can do now that it couldn't before.

Commit the simple version on its own (e.g. `explore: naive sync version`) before adding the pattern. Then the "before" can be re-run later with `git checkout`.

All numbers in this doc are measured on the dev or scale stack, the same way as `docs/project-staff/phase-5-vertical-scaling-simulations.md`. Absolute numbers depend on the machine; the before/after difference is what matters.

### Helpers for the checks
| Helper | What it's for |
|---|---|
| **Fake Gemini** (`GEMINI_PROVIDER=fake`) | Acts like Gemini without spending real quota. Settings: `FAKE_GEMINI_LATENCY_S` (how long a call takes), `FAKE_GEMINI_RPM` (above this many calls a minute it returns `429 RESOURCE_EXHAUSTED` like the real one does), `FAKE_GEMINI_FAIL_RATE` (fraction of calls that fail). It counts every call in Redis (`fake_gemini:calls`), so you can see how many Gemini calls really happened. |
| **Webhook receiver** (`system-test/phase6/webhook_receiver.py`) | A tiny local server that logs what it receives. `FAIL_FIRST_N` makes it return `500` the first N times, `DELAY_S` makes it slow to answer. |
| `websocat` (`brew install websocat`) | Opens WebSocket connections from the terminal. |
| k6 (`docker/grocery-management-k6.yml`) | Load and burst checks. New scripts go in `load-tests/k6/`. |
| nginx access log | `docker logs grocery_dev_nginx` shows how many requests hit which path. |
| RabbitMQ UI | `localhost:15672`, shows messages waiting, unacked and in the dead-letter queue (DLQ). |

Switch to the real Gemini only for the accuracy checks in Steps 2 and 5.

---

## 2. Decisions

| Decision | Choice | Why |
|---|---|---|
| Shops in scope | **Shwapno, Chaldal, Meena Bazar** only | All three have online stores with prices. Local and Comilla shops can't be looked up online. |
| Per-user or shared? | **Shared.** Gemini results, the cache, campaigns and alerts are the same for everyone | Groceries have no `user_id`, and prices are the same for everyone. Sharing results saves free-tier quota. |
| Who can trigger Gemini calls | **Logged-in users only** | Results are shared, but every call spends quota. Read-only endpoints stay public like the current `GET`s. |
| Message queue | **RabbitMQ** (`aio-pika`) | The roadmap's choice for topic 22. Redis stays the cache and rate-limit store. |
| Gemini SDK | `google-genai`, model ID taken from the `GEMINI_MODEL` env var | Free-tier models and their limits change, so nothing is hard-coded. |
| How Gemini finds prices | **Search-grounded** answers (explore) / **extracting data from pages we download ourselves** (campaigns) | Gemini can't browse websites itself. Grounding lets it search Google; for campaigns, we download the offer pages and Gemini only turns the text into structured data. |
| Trust in Gemini output | A suggestion until a user applies it, and dropped if it has no source URL on the shop's own domain | Search-grounded prices can be stale or invented. |

### Free-tier limits (fill in before Step 2)
Copy them from Google's Gemini API rate-limits page for the chosen `GEMINI_MODEL`. The rate limiter in Step 3 is sized from these numbers.

| Limit | Value | Checked on |
|---|---|---|
| Requests / minute | _TBD_ | |
| Requests / day | _TBD_ | |
| Grounded (Search) requests / day | _TBD_ | |

---

## 3. Target architecture (end of Phase 6)

```
                    ┌────────────── nginx (gateway) ──────────────┐
 browser ──HTTP/WS──▶  /api/v1/groceries/*  → grocery-api-1..3      │
                    │  /api/v1/market/*     → market-intel-api      │
                    │  /ws/*                → market-intel-api      │
                    └──────────────────────────────────────────────┘
                              │                      │
                         Postgres ◀──────────────────┤
                              │                      │ publish
                           Redis  (cache, rate limits, job status, pub/sub)
                                                     │
                                               RabbitMQ
                                    ┌────────────────┼────────────────┐
                              explore.jobs     campaign.crawl     alerts.out
                                    │                │                │
                              market-intel-worker (Gemini, httpx, scheduler)
                                                                      │
                                                         webhook → Telegram / Slack
```

## 4. New data

- **`Seller` enum:** add `CHALDAL`. `MEENA` = Meena Bazar, `SHWAPNO` = Shwapno.
- **`price_observation`:** `grocery_id`, `seller`, `price`, `source` (`manual` / `gemini` / `campaign`), `source_url`, `observed_at`. One row for every price seen anywhere.
- **`campaign`:** `seller`, `title`, `product_name`, `discount_text`, `discount_percent`, `campaign_price`, `valid_until`, `source_url`, `fetched_at`, `content_hash` (unique), `matched_grocery_id`.

---

## 5. Step 1 – Shopping-list export (feature only, no new topic)

**Problem:** before going shopping, you scroll the list, filter `should_include`, and work out by hand what to buy at which shop and how much it will cost.

**Build:** `GET /api/v1/groceries/export?format=csv`. It includes only `should_include=True` items. Rows are grouped by `best_seller`, and `quantity_to_buy = max(low_stock_threshold - quantity_in_stock, 1)`. Each row has a line total, plus a subtotal for each shop and a grand total. There's an "Export list" button on `HomePage`.

**Check:**
```bash
curl -s -D - "localhost:8000/api/v1/groceries/export?format=csv" -o /tmp/list.csv | grep -i content-disposition
open /tmp/list.csv
```
Check one shop's subtotal by hand against the items in the UI.

### What's achieved
- [x] One click gives a shopping list split by shop, with a budget estimate. (2026-10-15: 28 included items → 6 shops, grand total 10238, matches a SQL cross-check)

---

## 6. Step 2 – Explore an item (Topic 22 Message Queues)

### Simple version
`POST /api/v1/market/explore {grocery_id}`. The endpoint reads the grocery, calls Gemini **inside the request**, saves the offers it finds and returns them.

### Problem
1. **The user waits for Gemini.** A grounded call takes 5–20 s, and the browser hangs the whole time.
2. **One slow request blocks the database for everyone.** The request reads the grocery first and then waits for Gemini **while still holding its DB connection**. The dev env has `POOL_SIZE=1, MAX_OVERFLOW=0`, so every other request on that instance waits up to `POOL_TIMEOUT` (30 s) for that connection.
3. **Failures lose the work.** If Gemini errors or times out, the user gets a `500`, nothing is retried, and they have to click again.
4. **A restart loses the work.** Redeploying or restarting the container in the middle of a request kills it.

### Show the problem (fake Gemini: `FAKE_GEMINI_LATENCY_S=15`)
```bash
# 1 + 2: start an explore, and at the same time time a normal read
curl -s -X POST localhost:8000/api/v1/market/explore -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' -d "{\"grocery_id\":\"$ID\"}" -w '\nexplore: %{time_total}s\n' &
sleep 1; curl -s -o /dev/null -w 'GET detail: %{time_total}s\n' localhost:8000/api/v1/groceries/$OTHER_ID
wait

# 3: FAKE_GEMINI_FAIL_RATE=0.5 → send 10 explores, count how many return 500

# 4: start an explore, then `docker restart grocery-api` after 3 s → curl fails, no result saved
```

### Fix
- **RabbitMQ** with an `explore.jobs` queue. The API only checks the request, publishes a message and returns **`202 {job_id}`** at once, **without** keeping a DB connection open.
- A **worker** container (`python -m app.worker`) takes the message, calls Gemini, saves the results and only then **acks** it.
- Failed messages are **retried 3 times**, then moved to **`explore.jobs.dlq`** (dead-letter queue).
- Job status is kept in Redis (`job:{id}`), and the frontend polls `GET /api/v1/jobs/{id}` (Step 4 replaces polling).

### Check again
The same commands, plus two queue-specific ones:
```bash
# worker down: jobs wait instead of failing
docker compose stop worker;  # send 5 explores → all 202, RabbitMQ UI shows 5 "Ready"
docker compose start worker  # all 5 complete

# worker killed mid-job: message is redelivered, not lost
docker kill <worker>         # during a job → restart → job completes
```

| Check | Before | After |
|---|---|---|
| `POST /market/explore` response time | ~15 s | _TBD_ (expect < 100 ms) |
| `GET /groceries/{id}` while an explore is running | _TBD_ (waits for the pool) | _TBD_ |
| 10 explores with a 50% Gemini failure rate → completed | _TBD_ | _TBD_ (all, through retries) |
| Restart during an explore → result saved? | no | yes (redelivered) |
| Worker down → explores accepted? | n/a | yes, they wait in the queue |

### Accuracy check (real Gemini, once)
Explore 5 well-known items and compare each price Gemini found with the shop's website.

| Item | Shop | Gemini price | Website price | Source URL real? |
|---|---|---|---|---|
| | | | | |

### What's achieved
- [ ] The cheapest of the 3 shops for any grocery, without opening 3 websites.
- [ ] Slow external calls are out of the request path. They no longer block the DB pool, survive failures and restarts, and wait when the worker is down.
- [ ] A measured figure for how accurate Gemini's prices are.

---

## 7. Step 3 – Protecting the Gemini quota (Topic 23 Rate Limiting, + caching)

### Problem
1. **A burst uses up the free tier for everyone.** Results are shared, but every click is a new Gemini call. Once Gemini starts returning `429`, explore fails for every user. With the daily cap, it stays broken until the quota resets. Retries make it worse, because retrying a `429` uses more quota.
2. **Duplicate work.** Two people (or two tabs) exploring the same item make two identical Gemini calls, and so does exploring it again 5 minutes later.
3. **A limiter inside one instance doesn't work behind the load balancer.** A simple in-memory counter (e.g. 5/min) is kept separately in each of the 3 API instances. Through nginx round-robin, 3 × 5 = 15 requests get through.
4. **Unlimited login attempts.** `POST /auth/login` accepts unlimited password guesses.

### Show the problem
```bash
# 1: fake Gemini with FAKE_GEMINI_RPM=10 → k6 explore-burst.js sends 30 explores (different items) in 1 min
#    count jobs that end in the DLQ with RESOURCE_EXHAUSTED; read redis fake_gemini:calls (includes wasted retries)

# 2: explore the same item twice, 2 s apart → fake_gemini:calls goes up by 2

# 3: simple in-memory limiter of 5/min, scale stack (3 instances behind nginx :80)
docker compose -f docker-compose.scale.yml up -d --build
for i in $(seq 1 20); do curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost/api/v1/market/explore ...; done | sort | uniq -c

# 4: 50 wrong passwords in a loop → all 401, nothing slows it down
```

### Fix
- **Global rate limits in Redis**, shared by all instances:
  - a token bucket per minute, set below the free-tier RPM
  - a daily counter, set below the daily cap, that resets when Gemini's quota resets
  - a per-IP limit (from `X-Real-IP`, which only nginx sets)
  - When a limit is hit, the API returns `429` with a `Retry-After` header **before** calling Gemini. The worker doesn't retry a Gemini `429` straight away; it waits and retries later.
- **Cache and dedupe:**
  - Results are cached per item (`market:explore:{grocery_id}`, 12 h), so a second explore within that time returns `200` from the cache.
  - If a job for the item is already running, the request joins it (`SET NX` lock): same `job_id`, one Gemini call.
  - Cache hits and joined jobs don't count against the limits.
- **Login limit:** 5 failed attempts per IP and username per 15 min → `429`.

### Check again
The same 4 checks.

| Check | Before | After |
|---|---|---|
| 30 explores in 1 min (RPM 10): jobs that failed with a Gemini 429 | _TBD_ | _TBD_ (expect 0, the extra requests get our 429 instead) |
| Gemini calls made for the burst (`fake_gemini:calls`) | _TBD_ | _TBD_ (≤ 10) |
| Same item twice → Gemini calls | 2 | 1 |
| Limit 5/min through nginx with 3 instances → allowed | 15 | 5 |
| Login attempts before being blocked | unlimited | 5 |

### What's achieved
- [ ] The shared quota can't be used up by a burst or one heavy user. Users get a clear "try again in N s" instead of a broken feature.
- [ ] Each item uses at most one Gemini call per cache period.
- [ ] Shown first-hand why limits must live in shared storage once you have more than one instance.
- [ ] Password guessing on login is blocked.

---

## 8. Step 4 – Live results (Topic 25 WebSockets)

### Problem
1. **Polling floods the API.** After Step 2 the browser asks `GET /jobs/{id}` every second. A 15 s explore is about 15 requests, and 20 open tabs is about 300 requests to deliver one result.
2. **Results arrive late.** A result can arrive up to one poll interval after the job finished.
3. **Other users don't see updates.** When someone else explores an item or a crawl finds a campaign, your page doesn't change until you refresh.
4. **A simple WebSocket breaks behind the load balancer.** In the simple version, each API instance keeps its WebSocket connections in memory. A browser connected to `grocery-api-2` never hears about a job submitted through `grocery-api-1`. On top of that, nginx doesn't pass WebSocket connections through yet, so the connection fails.

### Show the problem
```bash
# 1: one explore with polling, then count the polls
docker logs grocery_dev_nginx 2>&1 | grep -c '/api/v1/jobs/'

# 4a: through nginx before the Upgrade headers are added → the handshake fails
websocat ws://localhost/ws/market

# 4b: simple in-memory version, scale stack, nginx fixed:
#     open 3 websocat clients (round-robin puts one on each instance), trigger an explore → count who receives it
```

### Fix
- `WS /ws/market` pushes `explore.done` (and `campaign.new` from Step 6).
- The worker publishes events to a **Redis pub/sub** channel (`market.events`). **Every** API instance subscribes to it and forwards events to its own connected browsers, so it doesn't matter which instance a browser is on.
- nginx gets the WebSocket headers (`proxy_http_version 1.1`, `Upgrade`, `Connection "upgrade"`) and a long `proxy_read_timeout`. The server sends a ping every 30 s so idle connections aren't dropped.
- The frontend opens one socket and stops polling.

### Check again
The same commands.

| Check | Before | After |
|---|---|---|
| Requests to deliver one explore result (1 tab) | _TBD_ (~15) | 0 polls, 1 push |
| Time from job done to UI updated | up to 1 s | _TBD_ |
| WebSocket through nginx | handshake fails | connects |
| 3 clients on 3 instances → how many get the event | 1 | 3 |

### What's achieved
- [ ] Results and new campaigns appear on every open page as they happen, without refreshing.
- [ ] Learned why real-time features behind a load balancer need a shared channel (Redis pub/sub) between instances.

---

## 9. Step 5 – Show campaigns (Topic 22 again: scheduled jobs)

### Site survey (first)
| Shop | Offers page URL | Offers in plain HTML? (`curl` + grep) | robots.txt allows it? | Approach |
|---|---|---|---|---|
| Shwapno | _TBD_ | | | |
| Chaldal | _TBD_ | | | Probably rendered by JavaScript. Look for the JSON API the page calls; otherwise use Gemini grounded search for this shop |
| Meena Bazar | _TBD_ | | | |

### Simple version
`GET /api/v1/market/campaigns` downloads the 3 offer pages and asks Gemini to extract the campaigns **every time the page is opened**. A simple "run every day" loop starts inside each API instance when it boots.

### Problem
1. **The page times out.** 3 downloads + 3 Gemini extractions one after another take about 30–60 s, and nginx's default `proxy_read_timeout` (60 s) turns slow ones into `504`.
2. **Every page view uses quota and hits the shops.** 10 visits = 30 page downloads + 30 Gemini calls. The shops could block us.
3. **Duplicate rows.** Saving each crawl stores the same campaign again every time.
4. **The scheduled crawl runs 3 times.** On the scale stack, each of the 3 API instances runs its own daily loop.

### Show the problem (fake Gemini with `FAKE_GEMINI_LATENCY_S=20`; set the schedule to 1 min for the check)
```bash
curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' localhost/api/v1/market/campaigns   # expect 504 after ~60s
# open the page 5 times → redis fake_gemini:calls +15
# SELECT count(*) FROM campaigns;  before and after a second crawl → doubles
docker compose -f docker-compose.scale.yml logs | grep 'campaign crawl started' | wc -l       # per tick: 3
```

### Fix
- **Scheduled producer:** the worker publishes one `campaign.crawl` message per shop daily at 08:00 Asia/Dhaka. A Redis lock (`SET NX`) makes sure only one copy publishes, however many are running.
- **Crawl job:** download the page with `httpx`, Gemini extracts the campaigns, and they're saved with an upsert on `content_hash`, so the same campaign is never stored twice. Expired campaigns are hidden.
- **Reads come from storage:** `GET /campaigns` reads the DB through the Redis cache and never crawls. `POST /campaigns/refresh` (login required) is limited to 1 per shop per hour.
- **Matching:** campaigns are matched to your groceries by name and brand, and a matched `campaign_price` becomes a price observation.

### Check again
The same commands.

| Check | Before | After |
|---|---|---|
| `GET /campaigns` status / time | 504 / ~60 s | _TBD_ (expect 200, < 100 ms) |
| Gemini calls for 5 page views | 15 | 0 |
| Campaign rows after crawling the same pages twice | doubles | unchanged |
| Crawls per schedule tick with 3 instances | 3 | 1 |

### Coverage check (real sites, once)
For each shop: campaigns visible on the website vs campaigns saved by the crawler.

### What's achieved
- [ ] A campaigns page that opens instantly, refreshed daily, with campaigns linked to your own items.
- [ ] Learned to separate *producing* data (on a schedule, through the queue) from *reading* it (fast, cached), and to make scheduled work run once in a cluster.

---

## 10. Step 6 – Campaign alerts (Topic 26 Webhooks)

### Problem
- **No way to be told.** You only find out a list item is on offer if you open the app on the right day.

The simple fix is to have the crawler call Telegram/Slack **directly** right after matching. That brings 4 new problems:
1. **A slow or broken receiver slows or breaks the crawl.**
2. **Alerts get lost.** If the receiver is down at that moment, the alert is gone, because nothing retries it.
3. **Duplicate alerts.** Every re-crawl of the same campaign sends the alert again.
4. **Alerts can be faked.** The receiver can't tell a real alert from anyone else POSTing to it.

### Show the problem (local `webhook_receiver.py` as the target)
```bash
DELAY_S=30 python system-test/phase6/webhook_receiver.py     # crawl now takes 30 s longer per alert
FAIL_FIRST_N=2 python system-test/phase6/webhook_receiver.py # alert never arrives
# trigger the same crawl twice → receiver log shows 2 identical alerts
curl -X POST localhost:9000/hook -d '{"fake":"alert"}'        # accepted, nothing to reject it with
```

### Fix
- The crawler only publishes to an **`alerts.out`** queue. A separate consumer sends the webhook with **retries and backoff** (1 min, 5 min, 30 min), then sends it to the **DLQ**.
- **Dedupe:** at most one alert per campaign, using `SET NX` with a TTL until `valid_until`.
- **Signing:** the body is signed with **HMAC-SHA256** in an `X-Signature` header. The receiver checks it with the shared secret and rejects anything else.
- The same event also goes to the WebSocket (`campaign.new`), so open pages show a notification.

### Check again
The same 4 checks.

| Check | Before | After |
|---|---|---|
| Crawl time with a 30 s slow receiver | +30 s per alert | _TBD_ (unchanged) |
| Receiver fails the first 2 tries → alert delivered? | no | yes, on attempt 3 |
| Same campaign crawled twice → alerts | 2 | 1 |
| Unsigned or tampered POST | accepted | rejected (401) |

### What's achieved
- [ ] A Telegram/Slack message when something on your list goes on offer.
- [ ] Reliable outgoing webhooks: they don't slow the crawl, they retry, they're sent once, and they're signed.

---

## 11. Step 7 – market-intel service (Topic 21 Microservices, Topic 24 API Gateway)

### Problem (everything is still one app)
1. **Changing market code restarts the grocery API.** Editing a Gemini prompt means rebuilding and restarting `grocery-api-1..3`, and `/groceries` errors while they restart.
2. **A market config problem takes everything down.** If `GEMINI_API_KEY` is missing, `Settings()` fails at startup, so the whole API crash-loops. That includes groceries, login and export, which don't use Gemini at all.
3. **Every grocery instance carries market code.** `google-genai`, `aio-pika` and the crawler are in the grocery image and start with it.

### Show the problem
```bash
# 1: k6 groceries-read.js running while market code is redeployed
docker compose -f docker-compose.scale.yml up -d --build   # count k6 errors during the restart
# 2: remove GEMINI_API_KEY from .env.dev, restart → curl localhost/api/v1/groceries/ fails
# 3: docker images | grep grocery-api   (size); time from container start to /health OK
```

### Fix, part 1: microservices
- Move `features/market/` and the worker into a separate `market-intel` service, with its own Dockerfile, settings and requirements.
- It owns its own tables (`price_observation`, `campaign`) in the shared Postgres. It only reads `grocery`.

**The split itself creates new problems (the Topic 24 "before"):**
- The frontend now needs two base URLs, and two WebSocket/API origins.
- CORS has to be set up in two services.
- Both services' ports are open, so clients can bypass any shared protection.
- A request can't be followed across the two services' logs.

You can see this by running the split without nginx routing: the frontend needs `VITE_MARKET_API_URL`, the browser makes CORS preflight requests to the second origin, and `curl localhost:<market port>` works directly.

### Fix, part 2: API gateway (nginx)
- One origin. nginx routes by path:
  - `/api/v1/groceries/*` and `/api/v1/auth/*` → grocery API
  - `/api/v1/market/*`, `/api/v1/jobs/*` and `/ws/*` → market-intel
- Service ports are not published (same as `a9b1735` did for the load balancer).
- nginx adds an `X-Request-ID` to every request, and both services log it.
- Optional: an nginx `limit_req` on `/api/v1/auth/login` as a first line of defence.

### Check again
The same commands.

| Check | Before | After |
|---|---|---|
| k6 `/groceries` errors while market code is redeployed | _TBD_ | 0 |
| `GEMINI_API_KEY` missing → `/groceries` | down | works, and only `/market/*` returns 502/503 |
| Grocery API image size / startup | _TBD_ | _TBD_ |
| Base URLs the frontend needs | 2 | 1 |
| Direct access to a service port | open | refused |
| Follow one request across both services' logs | not possible | grep one `X-Request-ID` |

### What's achieved
- [ ] The slow, fragile parts (AI, crawling, webhooks) can fail or be redeployed without touching groceries, login or export.
- [ ] One entry point that handles routing, hides the services, and adds request IDs.
- [ ] Measured both sides of the trade-off: what the split fixes, and the new problems that made the gateway necessary.

---

## 12. Phase 6 tracker

| Step | Feature | Topic | Problem it solves | Status | Done on |
|---|---|---|---|---|---|
| 1 | Shopping-list export | – | Planning a shopping trip by hand | ✅ | 2026-10-15 |
| 2 | Explore an item | 22 | Requests waiting on Gemini, blocking the DB pool, losing work | ⬜ | |
| 3 | Quota protection | 23 | Bursts use up the free tier; duplicate calls; per-instance limits leak | ⬜ | |
| 4 | Live results | 25 | Polling floods the API; WebSockets break behind the load balancer | ⬜ | |
| 5 | Show campaigns | 22 | Crawling on page view times out; duplicate rows; schedule runs 3 times | ⬜ | |
| 6 | Campaign alerts | 26 | No notification; inline webhooks are slow, lost, duplicated, can be faked | ⬜ | |
| 7 | market-intel + gateway | 21, 24 | One deploy unit and one point of failure; the split's two-origin problems | ⬜ | |

**Phase 6 is done when** every step's Before/After table is filled in and every "What's achieved" box is ticked.

### Out of scope
- Per-user results or `user_id` on groceries (decided: shared).
- Headless-browser scraping.
- Shops other than Shwapno, Chaldal and Meena Bazar.
- Rate limiting by subscription tier (free vs premium) from the roadmap's topic 23 example.
