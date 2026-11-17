# Chapter 93 — Project Handbook

> **Level:** 1–5 · **Track:** Shared · **Estimated reading time:** 8 h (building the projects: 10–100 h each)

Reading about a write-ahead log and writing one are different experiences. When you write it, you discover that a torn record at the end of the file is a normal event, that `fsync` costs milliseconds, and that "the replica is a little behind" means something very specific when the primary dies. This chapter turns the book into twenty build projects in four levels, so that you make those discoveries on your own laptop rather than in production or in an interview.

Each project is a scaled-down version of a system that the book designs at full size. The URL shortener of §52.4 handles 280,000 redirects per second; yours handles a few thousand on one machine, with the same mechanisms. What you lose in scale you gain in visibility: you can kill any process, delay any message, read every byte on disk and measure what happens.

**How to use the projects.** Pick a level that matches what you know, read the project's prerequisites and skim the owning sections, then work through the milestones in order. Each milestone ends with a **done when** statement: a check you can run, not a feeling. Keep two files next to your code from the first day: a one-page design document (requirements, the architecture redrawn in your own words, your decisions and why), and a results log that records every measurement with hardware, Python version, command line and date. The results log turns a toy into evidence; when an interviewer asks "how do you know?", you will have an answer (§93.7).

Each starter is a runnable core of 60–120 lines that demonstrates the central mechanism; it is not a solution, and the milestones replace almost all of it. Every starter was run with Python 3.13 on Linux and its output is quoted below it; seeds are fixed, so you should see the same output.

::: note
**Tooling assumptions for every project in this chapter.**

- **Language.** Python 3.11 or later, standard library first (`http.server`, `asyncio`, `socket`, `sqlite3`, `threading`, `heapq`, `hashlib`, `unittest`). Where a third-party package makes a milestone much easier (an HTTP client for load tests, a WebSocket library, a Prometheus client), the milestone says so and the package is optional. You may port any project to Go, Java or Rust once the Python version works; the measurements then change, and that comparison is itself instructive (§23.9).
- **Containers.** Docker is optional. It is useful for running a real Redis, PostgreSQL or Kafka next to your own implementation for comparison, and for running several copies of a node with separate network namespaces (§42.3). Nothing in the Beginner or Intermediate projects requires it.
- **Local only.** No cloud account, no paid service and no real e-mail, SMS or push provider. External systems are replaced by fakes you write, which is also the only way to inject their failures on demand.
- **Hardware.** One laptop or workstation with 4 or more cores and 8 GB of memory. Targets are stated for that machine. Loopback networking flatters latency (a round trip is tens of microseconds instead of the ~0.5 ms of a datacenter network, §4.17), so when a target concerns distribution rather than raw speed, the project asks you to add artificial delay.
:::

**Measuring honestly.** Report latency as percentiles (p50, p99), never as an average alone (§4.8, §40.5.2). Warm up before measuring, run each measurement at least three times and report the spread, and record whether your load generator is open-loop (sends at a fixed rate regardless of responses) or closed-loop (each worker waits for its previous response). Closed-loop generators hide queueing delay, a problem known as coordinated omission (§23.5). Every load-test target in this chapter is stated for an open-loop generator unless it says otherwise.

**Self-assessment.** Each project ends with a rubric of five dimensions scored 1–3: **1 — Working** (it runs and the happy path is correct), **2 — Solid** (failure cases handled, measured against the targets), **3 — Interview-ready** (you can explain each design choice, its alternative and the number that decided it). A total of 12 or more out of 15 means the project is ready to discuss in an interview; below 10 means a milestone was skipped.

**Table 93.1 — Project map.**

| § | Project | Level | Core concepts exercised | Owning chapters and case studies |
|---|---|---|---|---|
| 93.1.1 | REST API service | Beginner | Resource design, idempotency, pagination, persistence, observability | §8.6, §22.15, §40.4–40.5 |
| 93.1.2 | URL shortener | Beginner | ID generation, base62, cache-aside, redirect latency | §52.4, §17.10, §20.7 |
| 93.1.3 | Redis-style cache | Beginner | Wire protocol, TTL and expiry, eviction, persistence | §20.6, §20.8–20.9 |
| 93.1.4 | Rate limiter | Beginner | Token bucket, sliding window, distributed counters | §22.3–22.8, §52.6 |
| 93.1.5 | Load-balancer simulation | Beginner | Health checks, ejection, draining, retry budgets | §19.4–19.8, §22.12 |
| 93.2.1 | Message queue | Intermediate | Append-only log, offsets, consumer groups, acknowledgments | Ch 30, Ch 31 |
| 93.2.2 | Distributed key-value store | Intermediate | Consistent hashing, quorums, hinted handoff, rebalancing | §14.8, §27.7–27.9, §52.8 |
| 93.2.3 | Replicated database simulation | Intermediate | WAL shipping, replication lag, failover, fencing | §14.4, §27.4, §27.11, §26.13 |
| 93.2.4 | Notification service | Intermediate | Priority queues, deduplication, retries, preferences | §52.7, §30.10–30.11 |
| 93.2.5 | Real-time chat | Intermediate | Persistent connections, per-conversation ordering, sync | Ch 9, §53.4 |
| 93.3.1–93.3.5 | Job scheduler, event-driven microservices, real-time analytics, recommendation engine, distributed ML inference | Advanced | See §93.3 | §52.9, Ch 32, §56.7, Ch 68, Ch 66 |
| 93.4.1–93.4.5 | Distributed training, multi-tenant feature store, production RAG, LLM inference platform, multi-agent orchestration | Expert | See §93.4 | Ch 65, Ch 62, Ch 75, Ch 73, Ch 77 |

Beginner projects take roughly 10–20 hours each and Intermediate projects 20–40 hours. They build on each other: the rate limiter reuses the cache's TTL logic, the notification service sits on top of the message queue, and the chat server reuses the REST service's operational scaffolding. If you have time for only four of the first ten projects, build the REST API service, the Redis-style cache, the message queue and the distributed key-value store; together they exercise almost every Book I chapter that interviews probe.

## 93.1 Beginner projects

The five Beginner projects are single-process or single-machine systems. Each one isolates one idea that every larger design depends on: a well-behaved API, a collision-free identifier, a cache with expiry and eviction, admission control, and traffic distribution under failure. None needs consensus or replication, which keeps your attention on getting the mechanism right and measuring it.

### 93.1.1 REST API service

#### Goal and learning outcomes

Build a small task-tracking API (`/tasks`) that behaves like a production service: correct status codes, validated input, stable pagination, safe retries, durable writes, structured logs and metrics, and a measured capacity. The domain is deliberately boring so that every hour goes into the properties that make an API trustworthy. Almost every later project in this chapter exposes an HTTP interface, and they all reuse what you build here.

After this project you should be able to:

- Design resource URIs, methods and status codes that follow HTTP semantics, and explain which methods are safe and idempotent (§8.6.3).
- Make `POST` retry-safe with an idempotency key, including the concurrent-duplicate case (§22.15).
- Persist data in SQLite with transactions and survive `kill -9` without losing an acknowledged write.
- Instrument a service with request IDs, structured logs, a latency histogram and health endpoints, and shut it down gracefully.
- Run an open-loop load test, find the saturation point, and explain the result with Little's Law (§4.11).

#### Prerequisites

- Client–server model and statelessness — §8.3; the request–response lifecycle — §8.5.
- REST design: resources, methods, status codes, pagination, problem-details errors — §8.6.2–8.6.7.
- Idempotency keys — §22.15; timeouts — §22.11.
- Transactions and indexes — §11.7, §11.11; write-ahead logging and `fsync` — §13.5, §13.12.
- Structured logs, correlation IDs and metric types — §40.4.1–40.4.2, §40.5.1; percentiles — §4.8.

#### Specification

**Functional requirements.**

1. `POST /tasks` creates a task from `{"title": ..., "due": ...}`, returns `201 Created` with a `Location` header and the stored representation. A request carrying an `Idempotency-Key` header that has been seen before returns the original response and creates nothing. Reusing a key with a different body returns `422`.
2. `GET /tasks/{id}` returns `200` with an `ETag`, or `404`.
3. `GET /tasks?done=false&limit=50&cursor=...` returns a page and a `next_cursor`, which is `null` on the last page. `limit` is capped at 100.
4. `PATCH /tasks/{id}` with `If-Match` updates fields; a stale `ETag` returns `412 Precondition Failed` (optimistic concurrency).
5. `DELETE /tasks/{id}` returns `204`, and `204` again on repetition (idempotent).
6. All errors use `application/problem+json` (RFC 9457, §8.6.7). Oversized bodies (over 16 KB) return `413`; malformed JSON returns `400`; schema violations return `422`.
7. `GET /healthz` (process alive), `GET /readyz` (database reachable), `GET /metrics` (Prometheus text format, §40.8).

**Non-functional requirements.**

**Table 93.2 — REST API service: non-functional targets (one laptop, loopback).**

| Property | Target | How you verify it |
|---|---|---|
| Read latency | `GET /tasks/{id}` p99 ≤ 20 ms at 300 RPS for 60 s | Open-loop load test, latency histogram |
| Write latency | `POST /tasks` p99 ≤ 50 ms at 100 RPS with durable commits | Same, with SQLite `synchronous=FULL` |
| Errors under target load | 0 server errors (5xx) | Load-test report |
| Durability | No acknowledged `201` lost after `kill -9`, over 100 trials | Crash test script |
| Idempotency | 50 concurrent `POST`s with one key create exactly 1 task | Concurrency test |
| Graceful shutdown | On SIGTERM, in-flight requests complete; exit within 5 s | Shutdown test |
| Overload behavior | At 2× the saturation rate, p99 of accepted requests stays ≤ 200 ms; excess gets `503` with `Retry-After` | Overload test |

Out of scope: authentication (add it as an extension), multi-node deployment, and a user interface.

#### Architecture

**Figure 93.1 — REST API service: components and request path.**

```mermaid
flowchart LR
  LG([Load generator]) -->|HTTP/1.1| SRV
  CL([curl or test client]) -->|HTTP/1.1| SRV
  subgraph SRV[API process]
    MW["Middleware: request ID,<br/>size limit, timeout, metrics"] --> RT[Router]
    RT --> H[Task handlers]
    H --> REPO[Repository]
    H --> IDEM[Idempotency store]
  end
  REPO -->|SQL in a transaction| DB[(SQLite, WAL mode)]
  IDEM -->|same transaction| DB
  SRV -.->|JSON log lines| LOG[[Log file]]
  PROM{{Prometheus, optional}} -->|scrape /metrics| SRV
```

**Reading the diagram.** Clients (your load generator and ad-hoc `curl` calls) send synchronous HTTP/1.1 requests to a single API process. Inside it, every request first passes through middleware that assigns a request ID, rejects oversized bodies, starts a deadline timer and records a latency observation; the router then dispatches to a handler. Handlers reach SQL only through a repository, so SQLite can later be swapped for PostgreSQL. The idempotency store lives in the same SQLite file and, crucially, is written in the **same transaction** as the task it protects, so a crash can never leave a task without its idempotency record or vice versa. The storage boundary is the SQLite file in write-ahead-log mode (§13.5); everything above it is stateless and could be replicated behind a load balancer. The dotted arrow to the log file is asynchronous from the request's point of view: logging must never fail a request. Failure points to study: the database (locked, slow or full disk), the process (killed mid-request) and the client (retrying after a timeout). Scaling: run several API processes behind the load balancer of §93.1.5; the single SQLite writer then becomes the bottleneck, which is the motivation for a client–server database.

#### Milestones

1. **Core resource model (in memory).** Start from the starter code. Add `PATCH` with `ETag`/`If-Match`, `DELETE`, the `done` filter and the `400`/`413`/`422` distinctions. Write an OpenAPI description of the five operations (§8.16). *Done when:* a `unittest` suite of at least 20 cases covering every status code in the specification passes.
2. **Durable storage.** Replace the dictionaries with SQLite: a `tasks` table with an index on `(done, id)` for the filtered list, and an `idempotency_keys` table holding the key, a SHA-256 fingerprint of the request body, the status and the response body. Write both rows in one transaction. Enable WAL mode and `synchronous=FULL`. *Done when:* a script that starts the server, sends `POST`s in a loop, and kills the process with SIGKILL at a random moment finds every acknowledged task after restart in 100 out of 100 trials.
3. **Operability.** Emit one JSON log line per request (`ts`, `request_id`, `method`, `route`, `status`, `duration_ms`); accept an incoming `X-Request-ID` or generate one. Expose a request counter by route and status, and a latency histogram with buckets from 1 ms to 1 s, at `/metrics`. Add `/healthz` and `/readyz`. Handle SIGTERM by flipping `/readyz` to `503`, finishing in-flight requests and exiting. *Done when:* the shutdown test shows zero failed in-flight requests, and you can compute p99 from your histogram and compare it with the load generator's figure.
4. **Robustness under load.** Bound the number of concurrent requests (for example with a semaphore of 64) and reject excess with `503` and `Retry-After: 1` rather than queuing without limit (§22.9). Give every request a 2 s deadline. *Done when:* the overload test in the targets table passes.
5. **Capacity report.** Measure p50 and p99 against offered load from 100 RPS upward in steps of 100 until p99 exceeds 100 ms or errors appear. Plot or tabulate the curve, mark the knee, and explain it. *Done when:* your results log contains the curve for reads and for writes, and a one-paragraph explanation that names the bottleneck resource (CPU, the Python GIL, or SQLite's single writer) with evidence from a profile (§23.4).

#### Starter code

The starter serves `POST /tasks`, `GET /tasks/{id}` and a cursor-paginated list from memory, with problem-details errors and an idempotency key, then exercises itself with a few requests. It binds to port 0 so that the operating system picks a free port.

```python
"""Tasks API: a minimal REST service on the standard library (starter core)."""
import json, threading, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TASKS, IDEMPOTENCY, LOCK = {}, {}, threading.Lock()   # id -> task; key -> (status, body)

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, body, headers=None):
        data = json.dumps(body).encode()
        self.send_response(status)
        ctype = "application/problem+json" if status >= 400 else "application/json"
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def problem(self, status, title):                     # RFC 9457 error body
        self.send_json(status, {"type": "about:blank", "title": title, "status": status})

    def do_POST(self):
        if self.path != "/tasks":
            return self.problem(404, "Not Found")
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            title = body["title"].strip()
            assert 0 < len(title) <= 200
        except Exception:
            return self.problem(422, "title must be a 1-200 character string")
        key = self.headers.get("Idempotency-Key")
        with LOCK:
            if key in IDEMPOTENCY:                          # replay: same response, no new task
                return self.send_json(*IDEMPOTENCY[key])
            task = {"id": len(TASKS) + 1, "title": title, "done": False}
            TASKS[task["id"]] = task
            if key:
                IDEMPOTENCY[key] = (201, task)
        self.send_json(201, task, {"Location": f"/tasks/{task['id']}"})

    def do_GET(self):
        url = urlparse(self.path)
        parts = url.path.strip("/").split("/")
        if parts == ["tasks"]:                              # cursor pagination by id
            q = parse_qs(url.query)
            limit = min(int(q.get("limit", ["2"])[0]), 100)
            after = int(q.get("cursor", ["0"])[0])
            with LOCK:
                ids = sorted(i for i in TASKS if i > after)[:limit + 1]
                items = [TASKS[i] for i in ids[:limit]]
            nxt = str(ids[limit - 1]) if len(ids) > limit else None   # peek one extra
            return self.send_json(200, {"items": items, "next_cursor": nxt})
        if len(parts) == 2 and parts[0] == "tasks" and parts[1].isdigit():
            with LOCK:
                task = TASKS.get(int(parts[1]))
            return self.send_json(200, task) if task else self.problem(404, "Task not found")
        self.problem(404, "Not Found")

    def log_message(self, *args):                           # keep test output quiet
        pass

def call(base, method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)     # port 0 = any free port
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    for t in ["write spec", "add tests", "load test"]:
        print("POST", call(base, "POST", "/tasks", {"title": t}))
    print("POST retry", call(base, "POST", "/tasks", {"title": "pay"}, {"Idempotency-Key": "k1"}))
    print("POST retry", call(base, "POST", "/tasks", {"title": "pay"}, {"Idempotency-Key": "k1"}))
    print("POST bad ", call(base, "POST", "/tasks", {"title": ""})[0])
    print("GET  4   ", call(base, "GET", "/tasks/4"))
    print("GET  99  ", call(base, "GET", "/tasks/99"))
    page = call(base, "GET", "/tasks?limit=2")[1]
    print("page 1   ", [t["id"] for t in page["items"]], "next", page["next_cursor"])
    page = call(base, "GET", f"/tasks?limit=2&cursor={page['next_cursor']}")[1]
    print("page 2   ", [t["id"] for t in page["items"]], "next", page["next_cursor"])
    server.shutdown()
```

Output:

```text
POST (201, {'id': 1, 'title': 'write spec', 'done': False})
POST (201, {'id': 2, 'title': 'add tests', 'done': False})
POST (201, {'id': 3, 'title': 'load test', 'done': False})
POST retry (201, {'id': 4, 'title': 'pay', 'done': False})
POST retry (201, {'id': 4, 'title': 'pay', 'done': False})
POST bad  422
GET  4    (200, {'id': 4, 'title': 'pay', 'done': False})
GET  99   (404, {'type': 'about:blank', 'title': 'Task not found', 'status': 404})
page 1    [1, 2] next 2
page 2    [3, 4] next None
```

What to notice:

- The retried `POST` with `Idempotency-Key: k1` returns task 4 twice and creates nothing the second time. The check and the insert happen under one lock; in Milestone 2 that lock becomes a database transaction with a unique constraint on the key, which is what makes the concurrent-duplicate case safe across processes.
- The idempotency store does not yet fingerprint the body, so a client that reuses `k1` for a different task silently gets the old response. The specification requires `422` in that case (§22.15.3).
- The list endpoint fetches one row more than `limit`. If the extra row exists there is a next page; if not, `next_cursor` is `null`. Without this peek the last page would return a cursor that leads to an empty page.
- The cursor is the last ID seen, so a task inserted while the client is paging appears exactly once or not at all, never twice. Offset pagination (`?page=3`) would shift every later row by one and produce duplicates (§8.6.5).

#### Test plan and load-test targets

Write three layers of tests. **Unit and contract tests** (`unittest`, in-process server on port 0) cover every status code, every header (`Location`, `ETag`, `Retry-After`, `Content-Type`), pagination across 250 rows with concurrent inserts, and the problem-details body. **Concurrency tests** launch 50 threads that `POST` the same idempotency key and assert one row; launch 20 threads that `PATCH` the same task with the same `ETag` and assert exactly one `200` and 19 `412`s. **Process-level tests** start the server as a subprocess for the crash and shutdown cases.

For load, write a small open-loop generator: a scheduler thread that emits a request every $1/\lambda$ seconds into a pool of worker threads, recording each request's intended send time and its completion time. Measuring from the intended time, not the actual send time, is what avoids coordinated omission. Optional tools such as `wrk2` or `vegeta` do the same and are worth comparing with your own.

::: example
**Worked example — How many in-flight requests should the load test and the server allow?**

*Assumptions.* Target 300 RPS of `GET /tasks/{id}`; measured service time at low load about 5 ms per request (the starter measured roughly 5 ms p50 on loopback with the client in the same process).

1. By Little's Law (§4.11), the average number of requests in flight is $L = \lambda W = 300 \times 0.005 = 1.5$.
2. To leave room for bursts, give the load generator 10× that, 15 workers, so that it never becomes the bottleneck itself.
3. At 1,000 RPS with $W$ rising to 20 ms under contention, $L = 1{,}000 \times 0.020 = 20$ in flight, still below the server's concurrency limit of 64.
4. If $W$ reaches 200 ms during overload, $L = 1{,}000 \times 0.2 = 200$ would exceed 64, so about $200 - 64 = 136$ requests at any moment would be rejected with `503` instead of queuing.

*Interpretation.* The concurrency cap converts unbounded queueing delay into explicit rejections. *Engineering implication.* Size the cap from the latency you are willing to accept, not from the thread count you can afford: cap $= \lambda_{\max} \times W_{\text{target}}$.
:::

Record, for each step of offered load, the achieved throughput, p50, p99, the 5xx rate and the 503 rate. The project meets its targets when the read and write rows of Table 93.2 hold for three consecutive 60-second runs.

#### Failure-injection exercises

1. **Crash mid-write.** Send SIGKILL while 20 clients are posting. After restart, compare the set of acknowledged IDs (from client logs) with the database. Any missing ID is a durability bug; any extra row the client never saw acknowledged is fine (the client will retry with the same key and get the original response).
2. **Slow database.** Wrap every repository call in a configurable delay and set it to 300 ms. Observe the deadline firing, the concurrency limiter shedding load, and `/readyz` staying healthy. Decide whether a slow database should make the service "not ready", and write down your reasoning (§42.7.3).
3. **Locked database.** Open the SQLite file from a second process and hold a write transaction for 10 s. Your service should return `503` with `Retry-After`, not hang and not return `500`.
4. **Retry storm.** Make the client retry on timeout with no backoff while the database is slow. Measure how offered load multiplies, then add exponential backoff with full jitter (§22.12.2) and measure again.

#### Extensions

- Add bearer-token authentication with signed JSON Web Tokens and per-user task ownership (§8.11, §8.13); return `404`, not `403`, for other users' tasks so that IDs cannot be probed.
- Replace SQLite with PostgreSQL in Docker, add a connection pool, and repeat the capacity report; explain the change in the knee (§14.13.1).
- Add `ETag`-based conditional `GET` (`If-None-Match` → `304`) and measure bandwidth saved.
- Run three instances behind the load balancer of §93.1.5 and confirm that idempotency still holds when a retry lands on a different instance.

#### Self-assessment rubric

**Table 93.3 — REST API service: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| HTTP semantics | Correct happy-path codes | Every error code in the spec, problem-details bodies, `ETag`/`If-Match` | You can say which methods are idempotent and why `PATCH` is not by default |
| Retry safety | Idempotency key stored | Fingerprint check, same-transaction write, concurrent test passes | You can explain retention, key scope and what happens on a crash between commit and response |
| Durability | Data in SQLite | 100/100 crash trials pass | You can explain WAL mode, `synchronous=FULL` and their latency cost with your numbers |
| Operability | Logs printed | JSON logs, request IDs, histogram, health endpoints, graceful shutdown | You can find one slow request from a metric to its log line |
| Capacity | One load test run | Open-loop curve to the knee, overload test passes | You name the bottleneck with profile evidence and size the concurrency cap with Little's Law |

### 93.1.2 URL shortener

#### Goal and learning outcomes

Build a working URL shortener: an API that turns a long URL into a seven-character code, a redirect endpoint that answers in a few milliseconds, and click analytics that never slow the redirect. Section 52.4 designs this system for 280,000 redirects per second; your version runs on one machine, but it has the same three paths (create, redirect, analytics) and the same central decisions: how to generate codes that never collide and cannot be enumerated, how to keep the redirect path out of the database, and how to count clicks without putting a write on the read path.

After this project you should be able to:

- Compare random codes, hashed URLs, counters and keyed permutations as code generators, and predict the collision rate of random codes with the birthday bound (§17.10.2, §52.4.8).
- Implement cache-aside with LRU eviction and measure hit ratio as a function of cache size on a skewed trace (§20.3, §20.7.1).
- Separate a latency-critical read path from an asynchronous analytics path, and bound the analytics backlog.
- Choose between `301` and `302` redirects and explain what each does to caching and to analytics.

#### Prerequisites

- The full case study — §52.4, especially capacity (§52.4.4), code generation (§52.4.8) and failure scenarios (§52.4.11).
- Unique ID generation and the birthday bound — §17.10; counter blocks and ticket servers — §17.10.5.
- Cache hit ratio and popularity skew — §20.3.2–20.3.3; cache-aside and its races — §20.7.1–20.7.2; LRU and TinyLFU — §20.9.
- HTTP redirects and caching headers — §7.9.1, §21.6.1.
- The REST API service of §93.1.1 (reuse its server scaffolding, logging and load generator).

#### Specification

**Functional requirements.**

1. `POST /links` with `{"url": ..., "alias": optional, "expires_at": optional}` returns `201` with a seven-character base62 code. Only `http` and `https` URLs up to 2,048 characters are accepted; a custom alias that exists returns `409`.
2. `GET /{code}` returns a redirect with a `Location` header, or `404` for unknown, expired or disabled codes. The redirect status is configurable (`301` or `302`).
3. `GET /links/{code}/stats` returns total clicks and clicks per day, at most 60 s stale.
4. `DELETE /links/{code}` disables a link; the redirect must return `404` within 5 s on every instance, including from caches.
5. A fake abuse checker (a blocklist of domains) rejects bad destinations at creation time.

**Non-functional requirements.**

**Table 93.4 — URL shortener: non-functional targets (one laptop, loopback).**

| Property | Target | How you verify it |
|---|---|---|
| Redirect latency | p99 ≤ 15 ms over HTTP at 500 RPS, Zipf trace | Open-loop load test |
| Create latency | p99 ≤ 50 ms at 50 RPS, durable | Load test with SQLite `synchronous=FULL` |
| Cache effectiveness | Hit ratio ≥ 0.80 with a cache holding 20% of 100,000 links, 1 million-request Zipf (s = 1.0) trace | Trace replay against the cache alone |
| Uniqueness | Zero duplicate codes over 10 million generated codes | Generator test |
| Non-enumerability | No two consecutive creates produce codes sharing a 4-character prefix more often than chance | Statistical test on 100,000 codes |
| Analytics isolation | Redirect p99 unchanged (within 10%) when the click aggregator is stopped for 60 s | Failure-injection run |
| Click accuracy | Counts exact after the aggregator catches up, with no double counting after an aggregator crash | Replay and compare |

Out of scope: user accounts, QR codes and a dashboard user interface.

#### Architecture

**Figure 93.2 — URL shortener: create, redirect and click paths.**

```mermaid
flowchart LR
  U([Browser or test client]) -->|POST /links| API[Shortener API]
  U -->|GET /code| API
  API --> GEN["Code generator<br/>leased block + permutation"]
  GEN -->|lease 10,000 counters| ALLOC[(Range allocator row)]
  API -->|conditional insert| LS[(Link store, SQLite)]
  API --> LRU["In-process LRU cache"]
  LRU -->|miss| LS
  API -.->|click event| CQ[[Click log, append-only file]]
  CQ -.-> AGG[Click aggregator]
  AGG -->|batched upserts| CS[(Click counts)]
  API --> ABUSE{{Fake abuse checker}}
```

**Reading the diagram.** The shortener API serves both creates and redirects; in §52.4 these are separate fleets, and you can split them later. On create (solid arrows, synchronous), the API checks the destination with the fake abuse checker, takes the next value from the code generator and performs a conditional insert into the link store. The generator holds a block of 10,000 counter values leased from a single allocator row, so only one create in 10,000 touches the allocator, and it scrambles each counter with a keyed permutation so that consecutive links get unrelated codes (§52.4.8). On redirect, the API looks in an in-process LRU cache first and reads the link store only on a miss (cache-aside). The click path is dotted because it is asynchronous: the API appends one line per click to a log file and returns immediately; a separate aggregator reads the file, batches counts and upserts them into a click-counts table, remembering the file offset it has processed. Storage boundaries are the allocator row, the link store, the click log and the click-count table. Failure points: the allocator (creates stall after the current block runs out), the link store (redirects survive on cache hits only), the click log disk, and the aggregator (counts go stale but redirects are unaffected). Scaling: more API processes, each with its own block and cache; a shared Redis between the in-process cache and the store; and partitioning the link store by code (§52.4.12).

#### Milestones

1. **Create and redirect with random codes.** Wrap the starter's `Shortener` in the HTTP scaffolding from §93.1.1, persist to an SQLite file, and add URL validation, aliases and expiry. *Done when:* contract tests pass for every status code in the specification, and the `301`/`302` switch works.
2. **Collision-free, non-enumerable codes.** Replace random codes with leased counter blocks and a keyed permutation: implement the allocator row with compare-and-set (`UPDATE alloc SET next = next + 10000 WHERE next = ?`), and use the four-round Feistel permutation with cycle-walking from §52.4.8. *Done when:* 10 million generated codes are distinct, two processes generating in parallel never collide, and the prefix test in Table 93.4 passes.
3. **Cache and invalidation.** Measure hit ratio against cache size on the 1 million-request trace; then implement deletion so that a disabled link stops redirecting everywhere within 5 s. With one process, delete from the local cache; with several, either give cache entries a 5 s TTL or broadcast invalidations (§20.10). *Done when:* the hit-ratio target holds and a test that deletes a hot link sees `404` on all instances within 5 s.
4. **Asynchronous analytics.** Write clicks to an append-only log with one line per event; build the aggregator, which reads from a stored offset, adds counts in memory and commits the counts and the new offset in one SQLite transaction. *Done when:* killing the aggregator at random points and restarting it yields exactly the same final counts as an uninterrupted run, and stopping it for 60 s does not change redirect p99 by more than 10%.
5. **Capacity report.** Load-test redirects with the Zipf trace and creates at a fixed rate, simultaneously. *Done when:* your results log shows p50 and p99 for both paths at the targets, the measured hit ratio, and store reads per second, and you can scale the numbers to the §52.4.4 estimate (how many of your processes would 280,000 RPS need, and why that estimate is pessimistic for a compiled language).

#### Starter code

The starter uses random codes with a conditional insert and retry, an LRU cache in front of SQLite, and an in-memory click queue drained by an aggregator. To make collisions visible on a laptop it uses three-character codes ($62^3 = 238{,}328$ possible) for 20,000 links; production uses seven. It replays a 100,000-request Zipf trace at three cache sizes.

```python
"""URL shortener core: random codes with conditional insert, cache-aside redirects,
and an asynchronous click counter (starter)."""
import random, sqlite3
from collections import Counter, OrderedDict, deque
from itertools import accumulate

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
rng = random.Random(42)                     # production: use the secrets module

class Shortener:
    def __init__(self, code_len, cache_size):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE links (code TEXT PRIMARY KEY, url TEXT NOT NULL)")
        self.code_len, self.cache_size = code_len, cache_size
        self.cache = OrderedDict()              # code -> url, in LRU order
        self.clicks = deque()                   # click events awaiting the aggregator
        self.stats = Counter()

    def create(self, url):
        while True:
            code = "".join(rng.choice(ALPHABET) for _ in range(self.code_len))
            try:
                with self.db:                   # conditional insert: fails on duplicate
                    self.db.execute("INSERT INTO links VALUES (?, ?)", (code, url))
                return code
            except sqlite3.IntegrityError:
                self.stats["collisions"] += 1   # retry with a fresh random code

    def redirect(self, code):
        url = self.cache.get(code)
        if url is not None:
            self.cache.move_to_end(code)
            self.stats["hits"] += 1
        else:
            self.stats["misses"] += 1           # cache-aside: read store, then fill cache
            row = self.db.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
            if row is None:
                return 404, None
            url = row[0]
            self.cache[code] = url
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)  # evict least recently used
        self.clicks.append(code)                # never block the redirect on analytics
        return 301, url

    def flush_clicks(self, totals):             # the aggregator, run off the hot path
        while self.clicks:
            totals[self.clicks.popleft()] += 1

def zipf_trace(codes, n, s, seed):
    weights = [1 / (k + 1) ** s for k in range(len(codes))]
    return random.Random(seed).choices(codes, cum_weights=list(accumulate(weights)), k=n)

if __name__ == "__main__":
    for cache_size in (200, 1_000, 4_000):
        rng.seed(42)
        s = Shortener(code_len=3, cache_size=cache_size)   # 62^3 = 238,328 codes
        codes = [s.create(f"https://example.com/page/{i}") for i in range(20_000)]
        totals = Counter()
        for i, code in enumerate(zipf_trace(codes, 100_000, s=1.0, seed=7)):
            s.redirect(code)
            if i % 1_000 == 999:
                s.flush_clicks(totals)
        hit = s.stats["hits"] / (s.stats["hits"] + s.stats["misses"])
        print(f"cache={cache_size:>5}  hit ratio={hit:.3f}  store reads={s.stats['misses']:>6}"
              f"  collisions={s.stats['collisions']}  top link clicks={totals.most_common(1)[0][1]}")
    print("unknown code ->", s.redirect("-404")[0])   # "-" is not in the alphabet
```

Output:

```text
cache=  200  hit ratio=0.431  store reads= 56865  collisions=862  top link clicks=9495
cache= 1000  hit ratio=0.613  store reads= 38664  collisions=862  top link clicks=9495
cache= 4000  hit ratio=0.774  store reads= 22643  collisions=862  top link clicks=9495
unknown code -> 404
```

What to notice:

- 862 collisions for 20,000 inserts into a space of 238,328 codes. The worked example below predicts about 890, so the measurement matches the birthday arithmetic. Each collision costs one extra database round trip on the create path.
- A cache holding 1% of links (200) already absorbs 43% of redirects, and 20% of links (4,000) absorbs 77%. Popularity skew is what makes small caches effective (§20.3.3). Some misses are unavoidable **cold misses**: the first request for each link always goes to the store.
- `redirect` appends to the click queue and returns. If the aggregator stops, the queue grows but redirects are unaffected. In Milestone 4 the queue becomes a file, so a crash does not lose clicks, and the aggregator's offset makes replay safe.
- A miss for an unknown code is not cached, so every request for a nonexistent code reaches the store. That is the **cache penetration** problem (§20.12); caching negative results with a short TTL, or a Bloom filter of existing codes, fixes it.

::: example
**Worked example — Predicting collisions for random codes.**

*Assumptions.* Code space $N = 62^3 = 238{,}328$; $n = 20{,}000$ links created one after another, each retrying until it finds a free code.

1. When $i$ codes are taken, a fresh random code collides with probability $i/N$; the expected number of failed attempts before success is $\frac{i/N}{1 - i/N} = \frac{i}{N - i}$.
2. Summing over $i = 0 \ldots 19{,}999$ gives $\sum \frac{i}{N - i} \approx 889$ expected retries (computed exactly with Python).
3. The simpler birthday approximation, $n^2 / (2N) = 20{,}000^2 / 476{,}656 = 839$, is close because the space is only 8.4% full ($20{,}000 / 238{,}328$).
4. For seven characters, $N = 62^7 = 3.52 \times 10^{12}$. One million links give $10^{12} / (7.04 \times 10^{12}) = 0.14$ expected collisions in total.

*Interpretation.* Random codes are cheap at low fill and degrade smoothly as the space fills; the measured 862 agrees with the prediction within 3%. *Engineering implication.* Random codes are a defensible choice for your project's scale. The case for counter blocks plus a permutation (Milestone 2) is guaranteed uniqueness without a read-before-write, which matters when the store makes conditional inserts expensive (§52.4.8).
:::

#### Test plan and load-test targets

Unit tests cover base62 encoding (round trip for 0, 1, 61, 62 and $62^7 - 1$), the permutation (bijective on a sample, deterministic for a fixed key, different for a different key), URL validation (schemes, length, internationalized domain names) and alias conflicts. A property-based test inserts random sequences of create, redirect and delete operations and checks that every redirect agrees with a plain dictionary model.

For load, generate a 1 million-request trace from Zipf ($s = 1.0$) over 100,000 links, save it to a file, and replay it open-loop at 500 RPS. Report p50 and p99 for hits and misses separately: a blended percentile hides that misses are several times slower. Run creates at 50 RPS concurrently, since in production both paths share the machine. Finally, run the non-enumerability check: for 100,000 consecutive codes, count how often adjacent codes share their first four characters. With a good permutation the expected count is about $100{,}000 / 62^4 \approx 0.007$, so any nonzero count is a red flag.

#### Failure-injection exercises

1. **Store outage.** Make the link store raise an error on every read for 30 s. Hits must keep working; misses should return `503` (not `404`, which a browser may cache and which is simply wrong). Measure the fraction of redirects that still succeed and compare it with your hit ratio.
2. **Allocator outage.** Make the allocator unavailable. Creates continue until each process's block is exhausted; at 50 creates per second and 10,000 codes per block, that is $10{,}000 / 50 = 200$ s of runway per process. Verify the number, then decide what the API should return when the block runs out.
3. **Crash between lease and use.** Kill a process right after it leases a block. Its unused counters are lost forever. Compute how many codes per year a crash a day would waste and whether it matters against $62^7$.
4. **Aggregator crash during commit.** Kill the aggregator between reading events and committing. After restart, counts must be exact. Then deliberately break it by committing the offset *before* the counts, and observe lost clicks; commit counts before the offset without a transaction, and observe double counting (§30.8.1).

#### Extensions

- Add a shared Redis (Docker) between the in-process cache and SQLite, and measure the latency of each tier.
- Replace LRU with a W-TinyLFU admission filter and compare hit ratios on the same trace (§20.9.3).
- Record approximate unique visitors per link with HyperLogLog (§17.5) and compare its error with exact counting.
- Add a negative cache or a Bloom filter for unknown codes and measure store reads under a scan of random codes (§17.4).

#### Self-assessment rubric

**Table 93.5 — URL shortener: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Code generation | Random codes with retry | Leased blocks + keyed permutation; 10 million unique codes; parallel processes never collide | You can compare all five schemes of Table 52.3 with your collision and enumeration measurements |
| Redirect path | Redirect works | Cache-aside with eviction; hit-ratio target met; store outage degrades gracefully | You can explain `301` versus `302` for caching and analytics, and cache penetration with a fix |
| Invalidation | Delete removes the row | Disabled links stop within 5 s on every instance | You can state the staleness bound of your approach and its cost |
| Analytics | Counts update | File-backed log, offset in the same transaction, exact counts after crashes | You can explain why redirect latency is unaffected by aggregator failure, with data |
| Capacity | One load test | Hits and misses measured separately at target rates | You scale your numbers to §52.4.4 and identify what changes at 280,000 RPS |

### 93.1.3 Redis-style cache

#### Goal and learning outcomes

Build a single-node, in-memory key-value cache that speaks enough of the Redis wire protocol (RESP) for the real `redis-cli` and `redis-py` clients to talk to it. You will implement the parts of Redis that system-design interviews keep returning to: a single-threaded event loop, time-to-live (TTL) with lazy and active expiry, eviction under a memory limit, and optional persistence. Section 20.6 explains how Redis does each of these; this project makes you choose the same trade-offs yourself and measure them.

After this project you should be able to:

- Explain why a single-threaded event loop can serve tens of thousands of operations per second, and where it stops scaling (§20.6.1).
- Implement TTL with both lazy expiry (check on access) and active expiry (periodic sampling), and quantify how much memory each leaves to expired keys.
- Implement sampled approximate LRU eviction and compare it with exact LRU on a skewed trace (§20.9.4).
- Implement an append-only file (AOF) with a configurable `fsync` policy and state its data-loss window (§20.6.3).

#### Prerequisites

- Redis internals: event loop, data structures, persistence — §20.6.1–20.6.3; Memcached for contrast — §20.6.5.
- TTL — §20.8; eviction policies and Redis's approximations — §20.9.1, §20.9.4–20.9.5.
- Event-driven I/O and the cost of system calls — §6.7; TCP byte streams (why a read can return half a command) — §7.7.1.
- `fsync` and durability — §13.12; write-ahead logging — §13.5.
- Cache patterns that clients will use against your server — §20.7.

#### Specification

**Functional requirements.**

1. A TCP server on a configurable port that accepts RESP arrays of bulk strings and replies with simple strings, errors, integers, bulk strings and nulls.
2. Commands: `PING`, `GET`, `SET key value [EX seconds] [NX|XX]`, `DEL`, `EXISTS`, `EXPIRE`, `TTL`, `INCR`, `MGET`, `DBSIZE`, `INFO` (a few counters), plus one data structure of your choice (`LPUSH`/`LRANGE` or `HSET`/`HGET`).
3. Pipelining: a client may send many commands before reading any replies; replies come back in order.
4. `maxmemory` in bytes with policies `noeviction` (writes fail with an error) and `allkeys-lru` (sampled approximate LRU with configurable sample size).
5. Optional persistence: an AOF that logs every write command, with `appendfsync` set to `always`, `everysec` or `no`, replayed on startup.

**Non-functional requirements.**

**Table 93.6 — Redis-style cache: non-functional targets (one laptop, loopback, single event-loop thread).**

| Property | Target | How you verify it |
|---|---|---|
| Throughput, no pipelining | ≥ 10,000 `GET`/`SET` operations/s with 50 clients, p99 ≤ 5 ms | `redis-benchmark` from the Redis Docker image, or your own client |
| Throughput, pipelined | ≥ 40,000 operations/s with pipeline depth 16 | Same tool with pipelining enabled |
| Memory bound | Used memory (your accounting) never exceeds `maxmemory` by more than 1% | Fill test with values of random size |
| Expiry | After all TTLs elapse, ≥ 75% of expired keys are reclaimed within 1 s with no client traffic | Active-expiry test |
| Eviction quality | Hit ratio within 1 percentage point of exact LRU at 5 samples, on the Zipf trace | Trace replay |
| Durability with AOF `everysec` | Loses at most the last ~1 s of acknowledged writes on `kill -9` | Crash test with a write counter |
| Compatibility | `redis-cli` and `redis-py` work for every implemented command | Client tests |

Out of scope: replication, clustering, Lua scripting and transactions (`MULTI`).

#### Architecture

**Figure 93.3 — Redis-style cache: event loop, keyspace, expiry and persistence.**

```mermaid
flowchart LR
  C1([redis-cli]) -->|RESP over TCP| EL
  C2([redis-py or benchmark]) -->|RESP over TCP| EL
  subgraph P[Cache process, one thread]
    EL["Event loop<br/>asyncio"] --> PR["RESP parser<br/>per-connection buffer"]
    PR --> EX[Command executor]
    EX --> KS[("Keyspace dict<br/>+ expires dict")]
    EX --> EV["Evictor<br/>sampled LRU"]
    TM["Timer: active expiry<br/>10 times per second"] --> KS
  end
  EX -.->|append write commands| AOF[[Append-only file]]
  AOF -.->|replay on startup| EX
```

**Reading the diagram.** Clients speak RESP over TCP; each request is synchronous, but a client may pipeline many on one connection. Inside the process there is one thread. The event loop multiplexes all connections and keeps a byte buffer per connection, because TCP delivers a stream, not messages: a command may be split across reads, or several may arrive in one. The executor runs each command to completion against two dictionaries: the keyspace (key → value) and the expires dictionary (key → absolute expiry time), which holds only keys that have a TTL. Because there is one thread, no command needs a lock, and every command is atomic; the price is that one slow command (a `KEYS *` over a million keys) stalls every client. A timer performs active expiry; the evictor runs inside a write when memory is over the limit. Persistence is dotted because under `everysec` it is asynchronous with respect to the reply: commands are appended to the file and `fsync`ed once a second. The storage boundary is process memory, plus the AOF on disk if enabled. Failure points: the process (all data is lost without AOF), the disk (AOF writes stall the loop under `always`), and slow commands. Scaling: one node is bounded by one core; scaling out means partitioning keys across nodes with consistent hashing (§20.14), which is where the distributed key-value store of §93.2.2 begins.

#### Milestones

1. **Protocol and server.** Put the starter's executor behind an `asyncio` server with a per-connection buffer. Implement the full command list and RESP errors (`-ERR unknown command`). *Done when:* `redis-cli -p <port>` can run every command interactively, and a test that sends 1,000 pipelined commands in one `write` gets 1,000 replies in order.
2. **Expiry done properly.** Run `active_expire_cycle` ten times a second with a time budget (stop after, say, 25 ms), and make every read path apply lazy expiry. *Done when:* the expiry target holds for 100,000 keys with equal TTLs, and a test proves that an expired key is never returned, even if the active cycle has not yet reached it.
3. **Memory limit and eviction.** Account memory per key (key length + value length + a fixed per-entry overhead you estimate by measuring `sys.getsizeof` or `tracemalloc`). Implement `noeviction` and `allkeys-lru`, and replace the starter's $O(n)$ `list(self.data)` sampling with an $O(1)$ scheme (for example, a list of keys with swap-remove and an index map). *Done when:* the memory bound and eviction-quality targets hold, and eviction does not make `SET` p99 exceed 5 ms.
4. **Persistence.** Append each write command, in RESP form, to an AOF; implement the three `fsync` policies; replay on startup; tolerate a truncated last command. *Done when:* the crash test shows the expected loss window for each policy, and you have measured `SET` throughput under each.
5. **Benchmark and profile.** Run the throughput tests, profile the hot path, and make one evidence-backed optimization. *Done when:* your results log shows before and after numbers and names the dominant cost (parsing, dictionary operations or system calls).

#### Starter code

The starter contains a RESP parser for complete requests, a reply encoder, a command executor with TTL and lazy expiry, Redis's classic active-expiry loop (sample 20 keys with a TTL, delete the expired ones, repeat while more than 25% of the sample was expired), and sampled LRU eviction. A fake clock (`self.now`) replaces wall time so that runs are deterministic.

```python
"""Redis-style cache core: RESP parsing, TTL with lazy + active expiry, and
sampled (approximate) LRU eviction. A fake clock keeps runs deterministic."""
import random
from itertools import accumulate

def parse_resp(buf):
    """Parse one RESP array of bulk strings: *2\r\n$3\r\nGET\r\n$1\r\nk\r\n"""
    lines = buf.split(b"\r\n")
    n, out, i = int(lines[0][1:]), [], 1
    for _ in range(n):
        out.append(lines[i + 1].decode())      # lines[i] is the $len header
        i += 2
    return out

def encode(v):
    if v is None:
        return b"$-1\r\n"                       # null bulk string
    if isinstance(v, int):
        return b":%d\r\n" % v
    if v == "OK":
        return b"+OK\r\n"
    return b"$%d\r\n%s\r\n" % (len(v), v.encode())

class Cache:
    def __init__(self, max_keys, samples, rng):
        self.data, self.expires, self.used = {}, {}, {}    # value, expiry time, last access
        self.max_keys, self.samples, self.rng, self.now = max_keys, samples, rng, 0.0

    def _alive(self, k):                        # lazy expiry on every access
        if k in self.expires and self.expires[k] <= self.now:
            self._delete(k)
        return k in self.data

    def _delete(self, k):
        self.data.pop(k, None); self.expires.pop(k, None); self.used.pop(k, None)

    def execute(self, cmd, *args):
        cmd = cmd.upper()
        if cmd == "SET":
            k, v = args[0], args[1]
            if k not in self.data and len(self.data) >= self.max_keys:
                self._evict()
            self.data[k], self.used[k] = v, self.now
            self.expires.pop(k, None)
            if len(args) == 4 and args[2].upper() == "EX":
                self.expires[k] = self.now + float(args[3])
            return "OK"
        if cmd == "GET":
            if not self._alive(args[0]):
                return None
            self.used[args[0]] = self.now
            return self.data[args[0]]
        if cmd == "DEL":
            hit = self._alive(args[0]); self._delete(args[0]); return int(hit)
        if cmd == "TTL":
            if not self._alive(args[0]):
                return -2
            return int(self.expires[args[0]] - self.now) if args[0] in self.expires else -1
        raise ValueError("unknown command " + cmd)

    def _evict(self):                           # approximate LRU: oldest of a random sample
        keys = self.rng.sample(list(self.data), min(self.samples, len(self.data)))
        self._delete(min(keys, key=self.used.__getitem__))

    def active_expire_cycle(self, sample=20):   # periodic: sample keys that have a TTL
        while self.expires:
            keys = self.rng.sample(list(self.expires), min(sample, len(self.expires)))
            dead = [k for k in keys if self.expires[k] <= self.now]
            for k in dead:
                self._delete(k)
            if len(dead) <= sample // 4:        # stop when <= 25% of the sample expired
                return

if __name__ == "__main__":
    c = Cache(max_keys=1000, samples=5, rng=random.Random(1))
    for raw in [b"*3\r\n$3\r\nSET\r\n$4\r\nuser\r\n$3\r\nada\r\n",
                b"*5\r\n$3\r\nSET\r\n$3\r\notp\r\n$4\r\n9137\r\n$2\r\nEX\r\n$2\r\n30\r\n",
                b"*2\r\n$3\r\nTTL\r\n$3\r\notp\r\n", b"*2\r\n$3\r\nGET\r\n$3\r\notp\r\n"]:
        print(parse_resp(raw), "->", encode(c.execute(*parse_resp(raw))))
    c.now += 31
    print("after 31 s GET otp ->", encode(c.execute("GET", "otp")), " TTL user ->", c.execute("TTL", "user"))

    for i in range(900):                        # active expiry: 900 keys with 10 s TTL
        c.execute("SET", f"s{i}", "x", "EX", "10")
    c.now += 11
    before = len(c.data); c.active_expire_cycle(); print(f"active expiry: {before} keys -> {len(c.data)}")

    weights = list(accumulate(1 / (k + 1) for k in range(10_000)))   # Zipf(1.0) over 10k keys
    trace = random.Random(7).choices(range(10_000), cum_weights=weights, k=200_000)
    for samples in (1, 5, 10):
        c = Cache(max_keys=1000, samples=samples, rng=random.Random(1)); hits = 0
        for t, k in enumerate(trace):
            c.now = t * 0.001
            if c.execute("GET", str(k)) is None:
                c.execute("SET", str(k), "v")
            else:
                hits += 1
        print(f"approx LRU, {samples:>2} samples: hit ratio {hits / len(trace):.3f}")
```

Output:

```text
['SET', 'user', 'ada'] -> b'+OK\r\n'
['SET', 'otp', '9137', 'EX', '30'] -> b'+OK\r\n'
['TTL', 'otp'] -> b':30\r\n'
['GET', 'otp'] -> b'$4\r\n9137\r\n'
after 31 s GET otp -> b'$-1\r\n'  TTL user -> -1
active expiry: 901 keys -> 1
approx LRU,  1 samples: hit ratio 0.631
approx LRU,  5 samples: hit ratio 0.671
approx LRU, 10 samples: hit ratio 0.674
```

What to notice:

- `TTL` returns `-1` for a key without expiry and `-2` for a key that does not exist (or has expired); clients rely on that distinction. The one-time password `otp` disappears after 31 s on the next `GET` through lazy expiry, without any background work.
- Active expiry removed all 900 expired keys in one call because every sample was 100% expired, so the loop kept going. When few keys are expired, the loop stops after one sample of 20, which bounds its cost; the trade-off is that up to roughly 25% of keys with a TTL may be expired but still occupying memory.
- With one sample, "approximate LRU" is random eviction, and the hit ratio drops to 0.631. Five samples reach 0.671 and ten reach 0.674, while the same trace under exact LRU gives 0.675 (measured separately with an `OrderedDict`). Five samples is also Redis's default `maxmemory-samples` (§20.9.4): nearly all of LRU's benefit without a linked list threaded through every entry.
- `parse_resp` assumes a complete request in one buffer and splits on `\r\n`, which breaks for values that contain `\r\n`. A real parser reads the `$len` header and then exactly `len` bytes; Milestone 1 asks for that, and it is what makes RESP binary-safe.
- `rng.sample(list(self.data), ...)` copies every key on every eviction, which is $O(n)$. At a million keys this would dominate the event loop; Milestone 3 replaces it.

::: example
**Worked example — What each `appendfsync` policy costs and risks.**

*Assumptions.* A laptop SSD completes an `fsync` in about 2 ms (measure yours with a loop of small writes and `os.fsync`; values from 0.1 ms to 10 ms are common). The cache receives 10,000 `SET`s per second.

1. **`always`, one `fsync` per command.** With a single thread, each `SET` waits for its own `fsync`: at most $1 / 0.002 = 500$ `SET`s per second, 20 times below the offered load. Grouping all commands that arrived in one event-loop iteration into one `write` and one `fsync` (group commit) restores throughput: at 10,000 per second and one `fsync` every 2 ms, each `fsync` covers about $10{,}000 \times 0.002 = 20$ commands.
2. **`everysec`.** One `fsync` per second costs at most 2 ms per second of loop time (0.2%), and a crash loses at most the last ~1 s of acknowledged writes, about 10,000 `SET`s at this rate.
3. **`no`.** The operating system flushes when it chooses (often within 30 s on Linux); a power loss can lose that much, although a process crash alone loses nothing that reached the kernel's page cache (§6.6.6).

*Interpretation.* The policies trade throughput against the size of the loss window, and group commit changes the arithmetic of `always` dramatically. *Engineering implication.* For a cache, `everysec` or no persistence is usually right, because the source of truth lives elsewhere; measure all three and record the numbers so that you can defend the choice.
:::

#### Test plan and load-test targets

Unit tests drive the executor directly with the fake clock: every command's success and error replies, `SET` with `NX`/`XX`, `EX` overwritten by a plain `SET` (which must clear the TTL, as in Redis), `INCR` on a non-integer (error), and expiry exactly at the boundary instant. Protocol tests open a real socket and send a command one byte at a time, then 1,000 commands in one write, then a value containing `\r\n`; replies must be identical in all three cases. A **model-based test** generates random command sequences with a fixed seed and compares every reply with a plain Python dictionary model that implements the same semantics without eviction (set `maxmemory` high for this test).

For load, use `redis-benchmark` from the official Redis image in Docker, restricted to the commands you implement (for example `-t get,set -n 200000 -c 50`, then with `-P 16`). Run the same benchmark against real Redis on the same machine. Your server will be slower; the useful output is the ratio and an explanation of where the difference comes from (interpreted Python per command versus C, and allocation per request). Report the hit ratio from the trace replay for `samples` = 1, 3, 5 and 10, next to exact LRU.

#### Failure-injection exercises

1. **Slow command.** Implement `KEYS *` naively and call it on 1 million keys while `redis-benchmark` runs. Measure the p99 spike seen by every other client. This is the single-thread trade-off in one experiment; then implement a cursor-based `SCAN` and repeat.
2. **Crash with AOF.** Under each `fsync` policy, run a client that `INCR`s a counter and records each acknowledged value, kill the server with SIGKILL, restart it, and compare the recovered counter with the last acknowledged value. The gap is your measured loss window.
3. **Torn AOF tail.** Truncate the AOF in the middle of the last command. Startup must replay everything before it and discard the fragment with a warning, not refuse to start (§13.12).
4. **Memory pressure.** Set `maxmemory` to 50 MB and write 200 MB of values under `noeviction` (writes must fail cleanly with an error reply) and under `allkeys-lru` (memory stays bounded). Check that no client connection is dropped.

#### Extensions

- Add `allkeys-lfu` with a logarithmic counter and decay, as §20.9.4 describes, and compare it with LRU on a trace whose popular keys change halfway through.
- Add point-in-time snapshots (RDB-style): on Linux, `os.fork()` and let the child write the dictionary while the parent continues; measure the copy-on-write memory growth while writes continue (§6.6.5).
- Add primary–replica replication by streaming the AOF to a second process; this is a small preview of §93.2.3.
- Shard keys across three of your servers with client-side consistent hashing (§20.14) and measure how many keys move when you add a fourth.

#### Self-assessment rubric

**Table 93.7 — Redis-style cache: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Protocol | Commands work for complete requests | Partial reads, pipelining, binary-safe values; `redis-cli` and `redis-py` work | You can explain why a stream protocol needs length framing and how pipelining raises throughput |
| Expiry | Lazy expiry correct | Active expiry with a time budget meets the reclamation target | You can explain the 25% rule's trade-off between CPU and memory held by expired keys |
| Eviction | Some eviction under a limit | Memory accounting, $O(1)$ sampling, quality within 1 point of LRU | You can compare sampled LRU, exact LRU and LFU with your trace numbers |
| Persistence | AOF written | Three `fsync` policies, replay, torn-tail tolerance, measured loss windows | You can justify a policy for a cache versus a primary store using measured throughput |
| Performance | One benchmark run | Comparison with real Redis; profile; one optimization with before and after | You can explain where a single thread saturates and what Redis does about it (I/O threads, cluster) |

### 93.1.4 Rate limiter

#### Goal and learning outcomes

Build a rate limiter in two forms: a library that decides "allow or reject" in microseconds inside one process, and a shared service in front of several API instances that enforces one limit across all of them. Section 22.3–22.8 teaches the algorithms and §52.6 designs the distributed service at scale. Your job is to make the algorithms concrete, show their differences with traces you can replay, and then confront the problem that makes rate limiting a system-design question rather than a coding exercise: several servers must agree on a count without slowing every request down.

After this project you should be able to:

- Implement token bucket, fixed window, sliding-window log and sliding-window counter, and demonstrate each one's behavior at window boundaries and under bursts (§22.4–22.7).
- Return correct `429 Too Many Requests` responses with `Retry-After` and rate-limit headers (§22.3.4).
- Enforce a global limit across several processes with an atomic script in a shared store, and measure the latency it adds (§22.8.2).
- Compare centralized counting with local counting plus periodic synchronization, and quantify the over- or under-admission of each (§22.8.3).
- Decide, and defend, whether the limiter fails open or closed when its store is unavailable (§22.8.5, §52.6.11).

#### Prerequisites

- Rate limiting: purpose, placement, keys and headers — §22.3; the algorithms — §22.4–22.7; distributed limiting — §22.8.
- The case study — §52.6, especially detailed design (§52.6.8) and failure scenarios (§52.6.11).
- Load shedding and the difference from rate limiting — §22.9.
- Redis atomicity and single-threaded execution — §20.6.1 (or your own server from §93.1.3).
- The REST service of §93.1.1, which becomes the protected API.

#### Specification

**Functional requirements.**

1. A library with a common interface, `allow(key, cost=1, now=None) -> Decision(allowed, remaining, retry_after)`, and four algorithms: token bucket, fixed window, sliding-window log and sliding-window counter.
2. A rules file (YAML or JSON) mapping a key pattern to a limit: for example, 100 requests per minute per API key on `POST /tasks`, 1,000 per minute per API key overall, and 20 per second per client IP address for unauthenticated routes. A request is checked against every matching rule.
3. HTTP middleware for the §93.1.1 service that rejects with `429`, sets `Retry-After`, and includes remaining-quota headers on every response.
4. A distributed mode in which three API instances share counters in Redis (Docker) or in your §93.1.3 server, updated atomically by one script per request.
5. A configurable failure policy per rule: fail open (allow) or fail closed (reject) when the shared store is unreachable, with a local fallback limiter.

**Non-functional requirements.**

**Table 93.8 — Rate limiter: non-functional targets.**

| Property | Target | How you verify it |
|---|---|---|
| Local decision cost | ≤ 10 µs per `allow` call (p99) for 100,000 distinct keys | Micro-benchmark with `time.perf_counter_ns` |
| Distributed decision cost | Adds ≤ 2 ms at p99 to a request, loopback Redis | Load test with and without the limiter |
| Accuracy, single process | Over 60 s, allowed count ≤ limit × 60 s + burst | Replayed trace |
| Accuracy, three instances | Global allowed count within 5% of the limit when traffic is split unevenly (70/20/10) | Three-instance load test |
| Fairness | A client under its limit is never rejected because another client exceeds theirs | Mixed trace (greedy plus polite client) |
| Store outage | Fallback engaged within 1 s; no request blocks longer than the store timeout (50 ms) | Kill Redis during a load test |
| Memory | Bytes per tracked key measured and stated; idle keys expire after 2 windows | Memory test with 1 million keys |

#### Architecture

**Figure 93.4 — Rate limiter: local library and shared-counter mode in front of three API instances.**

```mermaid
flowchart LR
  C([Clients and load generator]) -->|HTTP| LB[Load balancer]
  LB --> A1["API instance 1<br/>limiter middleware"]
  LB --> A2["API instance 2<br/>limiter middleware"]
  LB --> A3["API instance 3<br/>limiter middleware"]
  A1 -->|EVALSHA token-bucket script| R[(Redis: one hash per key)]
  A2 -->|EVALSHA| R
  A3 -->|EVALSHA| R
  A1 --> FB["Local fallback limiter"]
  CFG[[Rules file]] -.->|reload on change| A1
  A1 -.->|429 and decision metrics| M{{Metrics}}
```

**Reading the diagram.** Clients send HTTP requests through a load balancer to three identical API instances (use the simulator of §93.1.5 or simply three ports and a client that rotates among them). In each instance, limiter middleware runs before the handler. It finds the rules that match the request, then, for each rule, makes one synchronous call to Redis that runs a stored script: read the key's bucket, refill it for the elapsed time, take a token if one is available and write it back. Because Redis executes a script atomically on one thread, two instances can never both take the last token. The middleware rejects with `429` if any rule says no. Each instance also holds a local fallback limiter (drawn for instance 1 only) that takes over when Redis is unreachable. The rules file is reloaded asynchronously (dotted). The storage boundary is Redis, which holds only soft state: if it is wiped, limits reset, which is acceptable. Failure points are Redis itself (outage or latency spike), the network to it, and clock disagreement between instances if the script uses the client's time instead of the server's. Scaling: partition keys across several Redis nodes by key hash (each key lives on one node, so no cross-node coordination is needed), or reduce calls with local counting and periodic synchronization (§22.8.3).

#### Milestones

1. **Algorithms and replay harness.** Extend the starter with the sliding-window log and a `Decision` result carrying `remaining` and `retry_after`. Build a harness that replays a trace file of `(time, key)` events against any limiter. *Done when:* the boundary-burst and greedy/polite experiments run for all four algorithms, and you can explain every number in the resulting table.
2. **HTTP integration.** Add middleware to the §93.1.1 service with rules from a file, `429` responses and headers. *Done when:* a test client that honors `Retry-After` is never rejected twice in a row, and the polite client in a mixed load test sees zero `429`s.
3. **Distributed counters.** Move the token bucket into a Redis script that uses Redis's own clock (`TIME`), not the caller's. Run three instances. *Done when:* the three-instance accuracy target holds with a 70/20/10 traffic split, and the added p99 latency is measured.
4. **Failure handling.** Give every Redis call a 50 ms timeout and a circuit breaker (§22.13); when it opens, switch to a local limiter that allows limit ÷ 3 per instance. *Done when:* killing Redis during a load test causes no request to wait longer than the timeout, and you have measured how far the fallback over- or under-admits.
5. **Local counting with synchronization.** Implement the alternative: each instance counts locally and every 100 ms adds its delta to a shared counter and reads the global total. *Done when:* your results log compares Redis calls per second, added latency and accuracy for the centralized and synchronized designs.

#### Starter code

The starter implements three algorithms with a common `allow(key, now)` method and drives them with a fake clock through two experiments: 20 requests packed across a window boundary, and a 60 s Poisson trace of a greedy client (30 RPS) next to a polite one (5 RPS), each limited to 10 requests per second.

```python
"""Rate limiter core: token bucket, fixed window and sliding-window counter,
driven by a fake clock so that every run is identical (starter)."""
import random

class TokenBucket:
    def __init__(self, rate, burst):
        self.rate, self.burst, self.state = rate, burst, {}       # key -> (tokens, last_ts)

    def allow(self, key, now):
        tokens, last = self.state.get(key, (self.burst, now))
        tokens = min(self.burst, tokens + (now - last) * self.rate)   # lazy refill
        ok = tokens >= 1
        self.state[key] = (tokens - 1 if ok else tokens, now)
        return ok

class FixedWindow:
    def __init__(self, limit, window):
        self.limit, self.window, self.counts = limit, window, {}  # (key, window#) -> count

    def allow(self, key, now):
        w = (key, int(now // self.window))
        if self.counts.get(w, 0) >= self.limit:
            return False
        self.counts[w] = self.counts.get(w, 0) + 1
        return True

class SlidingWindowCounter:
    """Weight the previous window's count by how much of it still overlaps."""
    def __init__(self, limit, window):
        self.limit, self.window, self.counts = limit, window, {}

    def allow(self, key, now):
        cur = int(now // self.window)
        overlap = 1 - (now % self.window) / self.window
        estimate = self.counts.get((key, cur - 1), 0) * overlap + self.counts.get((key, cur), 0)
        if estimate >= self.limit:
            return False
        self.counts[(key, cur)] = self.counts.get((key, cur), 0) + 1
        return True

def limiters():
    return {"token bucket": TokenBucket(rate=10, burst=10),
            "fixed window": FixedWindow(limit=10, window=1.0),
            "sliding counter": SlidingWindowCounter(limit=10, window=1.0)}

if __name__ == "__main__":
    # 1) Boundary burst: 20 requests between t=0.90 s and t=1.09 s (limit: 10 per second).
    times = [0.90 + i * 0.01 for i in range(20)]
    for name, lim in limiters().items():
        print(f"{name:<16} boundary burst: {sum(lim.allow('u1', t) for t in times):>2} of 20 allowed")
    # 2) Steady abuse: one client at 30 RPS (Poisson) for 60 s next to a polite one at 5 RPS.
    rng = random.Random(3)
    events, t = [], 0.0
    for key, rps in (("greedy", 30), ("polite", 5)):
        t = 0.0
        while (t := t + rng.expovariate(rps)) < 60:
            events.append((t, key))
    events.sort()
    for name, lim in limiters().items():
        ok = {"greedy": 0, "polite": 0}
        sent = {"greedy": 0, "polite": 0}
        for t, key in events:
            sent[key] += 1
            ok[key] += lim.allow(key, t)
        print(f"{name:<16} greedy {ok['greedy']:>4}/{sent['greedy']} allowed "
              f"({ok['greedy'] / 60:.1f}/s)  polite {ok['polite']}/{sent['polite']}")
```

Output:

```text
token bucket     boundary burst: 11 of 20 allowed
fixed window     boundary burst: 20 of 20 allowed
sliding counter  boundary burst: 11 of 20 allowed
token bucket     greedy  609/1824 allowed (10.2/s)  polite 283/283
fixed window     greedy  600/1824 allowed (10.0/s)  polite 283/283
sliding counter  greedy  597/1824 allowed (9.9/s)  polite 283/283
```

What to notice:

- The fixed window allows all 20 requests in 0.19 s, twice the limit, because ten land at the end of window 0 and ten at the start of window 1. This is the boundary problem of §22.6, reproduced in one line of output.
- The token bucket allows 11: the full burst of 10, plus the $0.19 \times 10 = 1.9$ tokens that refill during the burst, of which one is whole. The sliding-window counter also allows 11, because it weights the previous window's 10 by the fraction that still overlaps.
- Over 60 s every algorithm holds the greedy client to about 10 per second. The token bucket's 609 is $600$ plus most of the initial burst of 10: the long-run rate plus the burst allowance, exactly as designed.
- The polite client is never rejected by any algorithm because state is per key. A single shared bucket, a common bug, would let the greedy client starve the polite one.
- State grows forever: nothing removes old windows or idle buckets. In the distributed version, a TTL of two windows on each Redis key solves this; locally, you need your own expiry (reuse the idea from §93.1.3).

::: example
**Worked example — Why "each instance enforces limit ÷ N" goes wrong with uneven traffic.**

*Assumptions.* A client's limit is 100 RPS; it sends exactly 100 RPS; there are $N = 3$ instances; the load balancer's routing (for example, connection reuse) sends 70%, 20% and 10% of this client's requests to instances 1, 2 and 3.

1. Each instance enforces $100 / 3 = 33.3$ RPS locally.
2. Instance 1 receives 70 RPS and allows 33.3; instances 2 and 3 receive 20 and 10 RPS and allow all of them.
3. Allowed in total: $33.3 + 20 + 10 = 63.3$ RPS. The client is held to 63% of its paid-for limit while sending exactly its limit.
4. The opposite naive choice, each instance enforcing the full 100, would let a client spread evenly across instances send up to $3 \times 100 = 300$ RPS.

*Interpretation.* Purely local limiting is wrong in one direction or the other unless traffic is perfectly balanced per key. *Engineering implication.* Use shared counters (Milestone 3), or local counting that synchronizes often enough that the error is bounded (Milestone 5); and treat limit ÷ N as an emergency fallback only, which is exactly how Milestone 4 uses it.
:::

#### Test plan and load-test targets

Unit tests use the fake clock and check exact allowed counts for hand-computed traces: a full bucket, an empty bucket refilling, a request with `cost` larger than the burst (always rejected, with a clear error), clock going backward (treat as no elapsed time) and `retry_after` values that are exactly long enough. Property tests generate random traces and assert the accuracy bound: for any interval of length $T$, a token bucket never allows more than $\text{burst} + \text{rate} \times T$.

Load tests run in two configurations. Single process: an open-loop generator with 1,000 keys and a Zipf key distribution at 1,000 RPS, comparing p99 with the limiter on and off. Three instances: run the greedy/polite pattern with an uneven split and record the global allowed rate per key. Micro-benchmark `allow` for each algorithm at 100,000 keys to check the 10 µs target, and record bytes per key by measuring memory before and after inserting 1 million keys (`tracemalloc`).

#### Failure-injection exercises

1. **Store outage.** Stop the Redis container during a three-instance load test. Measure time to fallback, the error rate during the switch, and over-admission while the fallback is active. Repeat with fail-closed on a sensitive route (login) and fail-open on a read route, and justify each choice (§52.6.11).
2. **Store latency.** Add 30 ms of delay to Redis with `tc netem` in Docker, or with a delaying proxy written in `asyncio`. Show that the timeout and circuit breaker keep API p99 bounded.
3. **Clock skew.** Change the script to use each caller's clock and skew one instance by +2 s. Observe refills computed from mismatched times; then restore server-side `TIME` and confirm the effect disappears (§24.9).
4. **Retry amplification.** Make the clients ignore `Retry-After` and retry immediately. Measure the multiplication of offered load and the limiter's own cost, then add jittered backoff (§22.12.2).

#### Extensions

- Implement GCRA, the leaky bucket stored as a single timestamp per key, and compare its memory per key with the token bucket (§22.5.2).
- Add hierarchical limits (per user within per organization) and decide what `remaining` means when two limits apply.
- Add priority-based load shedding that rejects low-priority traffic first when the protected service's latency rises, and contrast it with per-client limits (§22.9.2).

#### Self-assessment rubric

**Table 93.9 — Rate limiter: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Algorithms | One algorithm works | Four algorithms; boundary and fairness traces explained | You can choose an algorithm for a given product requirement and justify it with your traces |
| HTTP behavior | Returns `429` | `Retry-After` and quota headers correct; polite clients unaffected | You can explain where in the stack to enforce limits and which key to use (§22.3.2–22.3.3) |
| Distributed accuracy | Shared counter used | Atomic script with server time; accuracy target met with uneven traffic | You can quantify the error of local, limit ÷ N and synchronized designs |
| Failure policy | Errors when the store is down | Timeout, circuit breaker, fallback; measured over-admission | You can defend fail-open versus fail-closed per route |
| Performance | Limiter works under load | Local and distributed costs measured; memory per key stated | You can size the Redis tier for §52.6's traffic from your numbers |

### 93.1.5 Load-balancer simulation

#### Goal and learning outcomes

Build a discrete-event simulator of a load balancer in front of a small fleet, and then a real reverse proxy that applies the same policies to live HTTP traffic. Section 19.4.5 already compares balancing algorithms on a healthy, heterogeneous fleet. This project concentrates on what happens when backends misbehave: a backend that crashes, one that stays up but becomes slow (a **gray failure**, §24.8), a rolling deployment, and a total outage that turns retries into a storm. Those are the situations in which a balancer earns its keep, and they are hard to study on real machines because they are rare and messy. A simulator makes them repeatable.

After this project you should be able to:

- Build an event-driven simulation with a fixed seed whose results you can reproduce and explain line by line.
- Implement passive health checking (outlier ejection) and active health checks, and measure detection time and the number of requests that hit a dead backend (§19.5).
- Show why error-based health checks miss gray failures, and fix it with a latency-aware policy (§19.4.3–19.4.4).
- Bound retry amplification with a retry budget, and demonstrate a retry storm without one (§22.12.3–22.12.4).
- Drain connections during a rolling deployment with zero failed requests (§19.8.4, §42.7.4).

#### Prerequisites

- Load-balancing algorithms, including power of two choices and EWMA — §19.4; the existing simulation — §19.4.5.
- Health checks — §19.5; balancer redundancy and connection draining — §19.8.
- Partial and gray failures, timeouts — §24.8.
- Retries, backoff, retry budgets and circuit breakers — §22.12–22.13.
- Percentiles and tail latency — §4.8, §23.6; queueing intuition — §4.10.

#### Specification

**Functional requirements.**

1. A simulator with configurable arrival process (Poisson, or replay from a trace), backends with service-time distributions and capacity (concurrent request slots with a FIFO queue), and a **scenario script** that changes backend state over time (`crash`, `slow`, `recover`, `drain`, `restart`).
2. Policies: round robin, weighted round robin, random, least outstanding requests, power of two choices, and power of two choices with EWMA latency.
3. Health checking: passive (eject after $k$ consecutive errors or when a backend's latency exceeds the fleet median by a factor), active (probe every $p$ seconds, mark down after $f$ failures, up after $s$ successes), and a maximum ejection percentage so that a fleet-wide problem does not eject everything.
4. Client behavior: timeouts, one retry to a different backend, and a retry budget (retries ≤ 10% of requests over a sliding 10 s window).
5. Output: per-second time series of throughput, error rate, p50 and p99 latency, retries and per-backend share, written to CSV for plotting.

**Non-functional requirements.**

**Table 93.10 — Load-balancer simulation: targets.**

| Property | Target | How you verify it |
|---|---|---|
| Reproducibility | Same seed and scenario give byte-identical CSV | Run twice, compare checksums |
| Simulator speed | ≥ 1 million simulated requests per minute of wall time | Timed run |
| Crash detection | Crashed backend receives ≤ 30 requests in total after the crash at 200 RPS, with one retry each | Crash scenario |
| Gray-failure handling | Slow backend's traffic share falls below 2% within 5 s; fleet p99 ≤ 60 ms | Slow-backend scenario |
| Rolling deployment | Zero failed requests while each of four backends is drained and restarted | Deploy scenario |
| Retry storm | During a full outage, total backend attempts ≤ 1.1 × client requests with the budget | Outage scenario, with and without budget |
| Real proxy overhead | Adds ≤ 2 ms at p50 and ≤ 10 ms at p99 at 300 RPS on loopback | Load test direct versus through the proxy |

#### Architecture

**Figure 93.5 — Load-balancer simulation: event loop, policies, health checking and scenario.**

```mermaid
flowchart LR
  GEN([Arrival generator]) --> EQ[["Event queue<br/>heap ordered by time"]]
  SCN[[Scenario script]] --> EQ
  EQ --> LB["Balancer: policy +<br/>health state"]
  LB -->|dispatch| B1[Backend 1]
  LB -->|dispatch| B2[Backend 2]
  LB -->|dispatch| B3[Backend 3]
  LB -->|dispatch| B4[Backend 4]
  B1 -.->|completion event| EQ
  B2 -.->|completion event| EQ
  HC["Active health checker"] -->|probe every p seconds| B3
  LB --> MET[("Metrics CSV<br/>per-second series")]
```

**Reading the diagram.** Everything happens in simulated time, driven by one event queue, a heap ordered by timestamp. The arrival generator inserts request arrivals; the scenario script inserts state changes such as "backend 2 becomes slow at $t$ = 40 s". The main loop pops the earliest event. For an arrival, the balancer chooses a backend using its policy and its health state, and the dispatch is treated as synchronous from the client's view (solid arrows). The backend computes a service time from its distribution and current state and schedules a completion event back into the queue (dotted, because it arrives later in simulated time; only two of these are drawn). Completion events update in-flight counts, EWMA latency and the passive health checker's error streaks. The active health checker is just another event source that probes backends periodically (drawn for one backend). There is no real network or storage; the only output is the metrics CSV. The failure points are the scenario's: crashes, slowness and drains, plus the balancer's own decisions (ejecting too eagerly can overload the survivors). Scaling the simulated system means more backends, or several balancers each with its own partial view.

#### Milestones

1. **Simulator with queues and time series.** Turn the starter into a proper event loop with arrival, completion and scenario events; give each backend a fixed number of concurrent slots and a FIFO queue, so that overload produces queueing delay, not just slow service. Emit the per-second CSV. *Done when:* the reproducibility target holds and a run with a healthy fleet at 70% utilization shows the p99 you expect from an M/M/c intuition (§4.10).
2. **Health checking.** Add active probes with up/down thresholds, passive ejection on errors and on latency outliers, and a maximum ejection percentage of 50%. *Done when:* the crash and gray-failure targets hold for at least two policies, and you can plot detection time against probe interval.
3. **Retries and budgets.** Add client timeouts, one retry and a retry budget. Script a 30 s total outage followed by recovery. *Done when:* without the budget, attempts during the outage roughly double the offered load; with it they stay within 10% above it, and the fleet recovers within 5 s of the outage ending.
4. **Rolling deployment.** Implement `drain` (no new requests; wait for in-flight ones to finish, up to a deadline) and slow start (ramp a restarted backend's weight up over 10 s, so that its cold caches are not hit with a full share at once). *Done when:* a four-backend rolling restart completes with zero failed requests.
5. **Real proxy.** Write an `asyncio` HTTP/1.1 reverse proxy that reuses the policy and health-check classes, start four copies of your §93.1.1 service, and inject the same failures for real: kill one with SIGKILL, add a 250 ms sleep to another. *Done when:* the real proxy's per-second series has the same shape as the simulator's for the same scenario, and you have explained every difference.

#### Starter code

The starter simulates four backends at 200 RPS for 60 s. Backend 1 crashes at $t$ = 20 s and fails fast; backend 2 becomes 250 ms slower at $t$ = 40 s. The client retries a failed request once on a random other backend. It compares round robin with and without passive ejection (three errors in a row eject a backend for 5 s), power of two choices on in-flight count, and power of two choices on EWMA latency × (in-flight + 1). The simulation is simplified: backends have unlimited concurrency, so there is no queueing yet.

```python
"""Load-balancer simulation core: four backends, one crashes at t=20 s and one turns
slow (a gray failure) at t=40 s. Compares policies with and without passive health
checks (outlier ejection). Event-driven, fixed seed, no real sockets (starter)."""
import heapq, random

DURATION, RPS, N = 60.0, 200, 4

def backend_state(i, t):
    if i == 1 and t >= 20: return "down"        # crashed: connection refused
    if i == 2 and t >= 40: return "slow"        # gray failure: alive but 250 ms slower
    return "ok"

class Balancer:
    def __init__(self, policy, eject, rng):
        self.policy, self.eject, self.rng = policy, eject, rng
        self.rr, self.inflight, self.done = -1, [0] * N, []   # done: (finish, server, latency)
        self.ewma = [0.010] * N                               # smoothed latency per backend
        self.errors_in_row, self.ejected_until = [0] * N, [0.0] * N

    def pick(self, now, exclude=None):
        while self.done and self.done[0][0] <= now:        # retire finished requests
            _, i, latency = heapq.heappop(self.done)
            self.inflight[i] -= 1
            self.ewma[i] = 0.8 * self.ewma[i] + 0.2 * latency  # learned only on completion
        live = [i for i in range(N) if self.ejected_until[i] <= now and i != exclude]
        live = live or [i for i in range(N) if i != exclude]   # never eject everyone
        if exclude is not None:
            return self.rng.choice(live)                     # a retry goes to a random other
        if self.policy == "round robin":
            self.rr += 1
            return live[self.rr % len(live)]
        a, b = self.rng.sample(live, 2) if len(live) > 1 else (live[0], live[0])
        if self.policy == "p2c-ewma":                        # latency-aware score
            score = lambda i: self.ewma[i] * (self.inflight[i] + 1)
            return a if score(a) <= score(b) else b
        return a if self.inflight[a] <= self.inflight[b] else b  # p2c: fewest in flight

    def record(self, i, now, latency, ok):
        self.inflight[i] += 1
        heapq.heappush(self.done, (now + latency, i, latency))
        self.errors_in_row[i] = 0 if ok else self.errors_in_row[i] + 1
        if self.eject and self.errors_in_row[i] >= 3:      # passive check: 3 errors in a row
            self.ejected_until[i], self.errors_in_row[i] = now + 5.0, 0

def serve(i, t, rng):
    state = backend_state(i, t)
    if state == "down":
        return 0.002, False                                 # fast failure
    base = rng.expovariate(1 / 0.010)                       # 10 ms mean service time
    return base + (0.250 if state == "slow" else 0.0), True

def run(policy, eject, seed=11):
    rng = random.Random(seed)
    lb, t, lat, failed, retries = Balancer(policy, eject, rng), 0.0, [], 0, 0
    while (t := t + rng.expovariate(RPS)) < DURATION:
        i = lb.pick(t)
        latency, ok = serve(i, t, rng)
        lb.record(i, t, latency, ok)
        if not ok:                                          # one retry on another backend
            retries += 1
            j = lb.pick(t + latency, exclude=i)
            extra, ok = serve(j, t + latency, rng)
            lb.record(j, t + latency, extra, ok)
            latency += extra
        failed += not ok
        lat.append(latency)
    lat.sort()
    p = lambda q: lat[int(q * (len(lat) - 1))] * 1000
    slow = sum(x > 0.100 for x in lat) / len(lat) * 100
    return (f"{policy:<11} eject={str(eject):<5} failed={failed} retries={retries:>4}"
            f"  >100ms={slow:4.1f}%  p50={p(.5):4.1f} ms  p99={p(.99):5.1f} ms")

if __name__ == "__main__":
    for policy, eject in [("round robin", False), ("round robin", True),
                          ("p2c", True), ("p2c-ewma", True)]:
        print(run(policy, eject))
```

Output:

```text
round robin eject=False failed=0 retries=1991  >100ms=11.2%  p50= 8.6 ms  p99=274.1 ms
round robin eject=True  failed=0 retries=  24  >100ms=11.2%  p50= 8.0 ms  p99=273.2 ms
p2c         eject=True  failed=0 retries=  24  >100ms= 1.7%  p50= 7.2 ms  p99=255.7 ms
p2c-ewma    eject=True  failed=0 retries=  24  >100ms= 0.1%  p50= 7.0 ms  p99= 48.1 ms
```

What to notice:

- Without ejection, 1,991 requests hit the crashed backend and had to be retried. With passive ejection only 24 did: three errors to trigger each ejection, eight 5 s ejections in 40 s. The worked example below derives both numbers. Because the failure is fast and the retry goes elsewhere, no request fails in any configuration; in production each of those 1,991 retries adds a round trip and load.
- Ejection does nothing for the slow backend, because it returns successes. Round robin keeps sending it a quarter of the traffic (after ejection, a third of the first attempts), so 11.2% of all requests take more than 100 ms and p99 is 274 ms. Error-based health checks are blind to gray failures.
- Power of two choices on in-flight count helps a lot (1.7% slow) but not completely. At 200 RPS the healthy backends often have zero or one request in flight, so a slow backend with one or two in flight does not look very different; about 5% of requests in the last 20 s still reach it.
- Adding EWMA latency to the score nearly eliminates slow requests (0.1%) and brings p99 down to 48 ms. The EWMA is updated only when a request completes, which is realistic: the balancer learns that a backend is slow only after waiting for it.

::: example
**Worked example — How many requests hit a dead backend?**

*Assumptions.* 200 RPS arriving, four backends, backend 1 dead from $t$ = 20 s to 60 s (40 s), fast failures.

1. Round robin without ejection sends 1/4 of first attempts to backend 1: $200 \times 40 \times 0.25 = 2{,}000$ failed attempts. The simulation measured 1,991; Poisson arrivals make the count vary slightly.
2. With passive ejection, each cycle is "three errors, then 5 s ejected". The errors arrive within a few tens of milliseconds (backend 1 gets about 50 RPS), so each cycle lasts about 5 s: $40 / 5 = 8$ cycles × 3 errors = 24 failed attempts, exactly as measured.
3. An active checker probing every 2 s with a threshold of two failures would detect the crash within 2–4 s, during which round robin sends $50 \times 4 = 200$ requests to the dead backend before the first ejection; afterwards, probes, not real requests, discover whether it is back.

*Interpretation.* Passive checks detect within a few requests but keep re-testing the dead backend with real traffic; active checks detect more slowly but test with probes. *Engineering implication.* Use both: passive ejection for fast reaction, active probes to decide readmission, which is what production proxies typically offer (§19.5.1).
:::

#### Test plan and load-test targets

Test the simulator like any other program. Unit tests check each policy on hand-built states (round robin skips ejected backends; power of two choices never picks the worse of two; weighted round robin produces the exact smooth sequence for weights 5, 1, 1). Conservation tests check that every request either completes or fails exactly once and that in-flight counts return to zero at the end. Statistical tests compare a healthy-fleet run with theory: with Poisson arrivals and exponential service at 70% utilization on one server, the mean time in system should be close to $1/(\mu - \lambda)$ (§4.10).

Then run every scenario in Table 93.10 for five seeds and report the mean and range of each metric. For the real proxy, load-test at 300 RPS directly against one backend and through the proxy with four backends; the difference in p50 and p99 is the proxy's overhead.

#### Failure-injection exercises

1. **Flapping backend.** Make a backend alternate between healthy and failing every 3 s. Tune ejection duration and readmission thresholds so that the error rate is low without permanently losing the backend; plot the trade-off.
2. **Correlated failure.** Crash two of four backends at once. The survivors now run at double load; if that exceeds their capacity, latency explodes and passive latency-based ejection may eject a third backend, making things worse. Show the cascade, then show how the maximum ejection percentage stops it.
3. **Retry storm and metastability.** In the full-outage scenario, set client retries to three with no budget and no backoff. Show that after the outage ends the fleet stays overloaded because retries keep the queues full, a metastable failure; then show that the retry budget breaks the loop (§22.12.3).
4. **Health-check lies.** Make a backend's `/healthz` return `200` while real requests fail (a dependency is down). Active checks alone keep it in rotation; passive checks catch it. Then decide what a health check should test (§19.5.2).

#### Extensions

- Add consistent hashing with bounded loads (§19.4.7) for a cache-like workload, and measure the trade-off between hit ratio (affinity) and balance.
- Model a multi-zone fleet with zone-aware routing, and simulate the loss of one zone (§19.9).
- Feed the simulator with the latency distribution you measured from the §93.1.1 service instead of an exponential distribution, and compare predictions with the real proxy.

#### Self-assessment rubric

**Table 93.11 — Load-balancer simulation: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Simulation correctness | Runs and prints metrics | Queues, conservation tests, reproducible CSV, healthy run matches queueing theory | You can explain every number in a run from first principles |
| Health checking | Ejection on errors | Active and passive checks, latency outliers, ejection cap; detection time measured | You can explain why gray failures defeat error-based checks and what detects them |
| Policies | Two policies | Six policies compared on every scenario | You can choose a policy for a fleet and defend it with your plots |
| Retries and overload | Retries implemented | Budget, outage and recovery measured; metastable storm demonstrated | You can explain metastability and three defenses against it |
| Real system | Simulator only | Real proxy, same scenarios, results compared | You can say where the simulator was wrong and why |

## 93.2 Intermediate projects

The Intermediate projects are distributed: several processes (or simulated nodes) that must cooperate while any of them may crash and any message may be delayed or lost. The main new skill is reasoning about state that lives in more than one place. Each project gives you a fault-injection harness from the start, because a distributed system that has only been run without failures has not really been tested. Run the nodes as separate processes on one machine, communicating over TCP or HTTP on different ports; Docker Compose is a convenient alternative that also lets you cut network links between containers.

### 93.2.1 Message queue

#### Goal and learning outcomes

Build a small durable message broker in the style of a partitioned log: producers append messages to topics split into partitions, the broker stores them in segment files on disk, and consumer groups read them by offset and commit their progress. Chapter 30 explains queues and delivery guarantees, and Chapter 31 explains how Kafka builds a log-based broker. Here you discover why the details matter: a torn record after a crash, a consumer that processed messages but died before committing, a rebalance that hands a partition to a new consumer while the old one is still working.

After this project you should be able to:

- Store messages in an append-only, checksummed segment format and recover correctly from a crash at any byte (§31.3, §13.12).
- Explain and demonstrate at-most-once and at-least-once delivery by moving one line of code (the commit) (§30.8, §31.8.2).
- Partition a topic by key, preserve per-key order, and explain why order across partitions is not preserved (§31.5.3, §30.9).
- Implement consumer groups with heartbeats, partition assignment and rebalancing, and measure the pause a rebalance causes (§31.7.2, §31.12).

#### Prerequisites

- Queues, acknowledgments and the visibility timeout — §30.4; delivery guarantees and where duplicates come from — §30.8; ordering — §30.9; poison messages and dead-letter queues — §30.10–30.11 (§30.11.2 has a runnable in-memory queue with visibility timeouts; this project builds the log-based alternative).
- The log abstraction, partitions, producers, consumer groups and offsets — §31.3, §31.5–31.8; retention and compaction — §31.10.
- `fsync`, checksums and torn writes — §13.12; log-structured storage — §13.7.
- The REST service (§93.1.1) for the broker's API, or raw TCP with length-prefixed frames.

#### Specification

**Functional requirements.**

1. Topics with a configurable number of partitions. `produce(topic, key, value)` chooses the partition by hashing the key (or round robin when the key is empty) and returns `(partition, offset)` once the record is durable.
2. Each partition is a directory of segment files (roll a new segment at 1 MB) plus a sparse offset index; startup recovery truncates a torn tail and rebuilds the index.
3. `fetch(topic, partition, offset, max_bytes, max_wait_ms)` returns records from `offset` onward; with long polling it waits up to `max_wait_ms` for new data instead of returning empty at once.
4. Consumer groups: consumers join with heartbeats; the broker assigns partitions (range or round robin) and reassigns them when a consumer joins, leaves or misses heartbeats for the session timeout. `commit(group, topic, partition, offset)` stores progress durably.
5. Retention by size and age: whole segments older than the limit are deleted.
6. A dead-letter topic: consumers in the client library move a message there after five failed processing attempts.

**Non-functional requirements.**

**Table 93.12 — Message queue: non-functional targets (one broker process, laptop SSD).**

| Property | Target | How you verify it |
|---|---|---|
| Producer throughput | ≥ 20,000 messages/s of 200 bytes with batching (one `fsync` per batch) | Producer benchmark |
| Unbatched durable produce | Measured and explained against your disk's `fsync` latency | Same benchmark, batch size 1 |
| End-to-end latency | p99 ≤ 50 ms from produce acknowledgment to consumer delivery at 1,000 messages/s | Timestamps in messages |
| Durability | No acknowledged message lost over 100 `kill -9` trials | Crash test |
| Ordering | Per-key order preserved for 1 million messages across 8 partitions | Consumer-side check |
| Rebalance | Partitions of a dead consumer resume elsewhere within the 10 s session timeout plus 2 s | Kill a consumer during a run |
| Duplicates | Only after a crash or rebalance, and every duplicate is detected by an idempotent consumer | Duplicate counter |

#### Architecture

**Figure 93.6 — Message queue: producers, partitioned log, consumer groups.**

```mermaid
flowchart LR
  P1([Producer A]) -->|produce key=order-17| BR
  P2([Producer B]) -->|produce batch| BR
  subgraph BR[Broker process]
    API[Request handler] --> PT{"hash of key<br/>mod partitions"}
    PT --> L0[["Partition 0<br/>segments + index"]]
    PT --> L1[["Partition 1<br/>segments + index"]]
    GC["Group coordinator<br/>heartbeats, assignment"]
    OFF[(Committed offsets)]
  end
  L0 -->|fetch from offset| C1([Consumer 1, group billing])
  L1 -->|fetch from offset| C2([Consumer 2, group billing])
  C1 -.->|heartbeat and commit| GC
  C2 -.->|heartbeat and commit| GC
  GC --> OFF
```

**Reading the diagram.** Producers send produce requests synchronously to the broker and wait for an acknowledgment that carries the record's partition and offset. The request handler hashes the key to pick a partition, so all messages with key `order-17` land in the same partition and keep their relative order. Each partition is an append-only log of segment files with a sparse offset index; together with the committed offsets, this is the storage boundary. Consumers pull: each one fetches from its current offset in the partitions assigned to it, with long polling so that an idle consumer does not spin. Members of one group split the partitions, so each partition has one reader per group; another group would read the same data with its own offsets. Heartbeats and commits (dotted) go to the group coordinator, which reassigns partitions when a heartbeat stops arriving and stores committed offsets durably. Failure points: the broker process (everything stops; acknowledged data must survive), the disk, a consumer that dies before committing (its messages are redelivered) and a consumer that is only slow (it may lose its partitions while still processing, creating duplicates). Scaling: more partitions for more consumer parallelism (§31.5.2), and several brokers with replicated partitions, which is §93.2.3's subject applied to a log.

#### Milestones

1. **Durable partition log.** Extend the starter to segments with rolling, a sparse index file per segment and offset lookup by binary search. *Done when:* a crash test that kills the broker at random moments during writes shows that every acknowledged offset is readable after restart, and that no partially written record is ever returned.
2. **Broker API and producers.** Expose produce and fetch over HTTP or TCP, with key hashing, batching (a producer sends up to 100 records or waits up to 5 ms, whichever comes first) and long-poll fetch. *Done when:* the throughput and end-to-end latency targets hold, and your results log shows throughput and p99 for batch sizes 1, 10, 100 and 1,000.
3. **Consumer groups.** Implement join, heartbeat, assignment and rebalancing with a generation number, so that a commit from a consumer of an old generation is rejected. *Done when:* the rebalance target holds and a commit from a zombie consumer is refused (§26.13 explains why the generation number acts as a fencing token).
4. **Delivery semantics.** Provide a client library with two modes: commit before processing (at-most-once) and commit after processing (at-least-once); write an idempotent consumer that deduplicates by message ID with a processed-ID table (§32.10). *Done when:* in crash tests, at-most-once loses some messages and never duplicates, at-least-once never loses and sometimes duplicates, and the idempotent consumer's side effects are exact.
5. **Retention, dead letters and lag.** Add retention by size and age, the dead-letter topic, and a lag metric per group and partition (log end offset minus committed offset). *Done when:* old segments disappear on schedule while consumers keep reading, poison messages end up in the dead-letter topic after five attempts, and a lag graph shows a backlog draining after a consumer outage.

#### Starter code

The starter is one partition: an append-only file of records, each with a 4-byte length, a 4-byte CRC32 and a JSON payload. On startup it scans the file and truncates a torn tail. A consumer group's offset is committed by writing a temporary file and renaming it, which is atomic on POSIX file systems. The demonstration simulates a broker crash in the middle of a write, then a consumer crash between processing and committing.

```python
"""Message-queue core: a durable append-only log with CRC-checked, length-prefixed
records, torn-tail recovery, and consumer-group offsets (starter)."""
import json, os, struct, tempfile, zlib

HEADER = struct.Struct(">II")                  # record length, CRC32 of the payload

class Log:
    def __init__(self, path):
        self.path, self.offsets = path, []      # offsets[i] = byte position of record i
        self.recover()
        self.f = open(path, "ab")

    def recover(self):
        """Scan the file; keep the longest valid prefix, truncate a torn tail."""
        if not os.path.exists(self.path):
            open(self.path, "wb").close()
        with open(self.path, "rb") as f:
            data = f.read()
        pos = 0
        while pos + HEADER.size <= len(data):
            length, crc = HEADER.unpack_from(data, pos)
            payload = data[pos + HEADER.size: pos + HEADER.size + length]
            if len(payload) < length or zlib.crc32(payload) != crc:
                break                           # torn or corrupt record: stop here
            self.offsets.append(pos)
            pos += HEADER.size + length
        if pos < len(data):
            print(f"  recovery: truncating {len(data) - pos} bytes of torn tail")
            with open(self.path, "r+b") as f:
                f.truncate(pos)

    def append(self, message, sync=True):
        payload = json.dumps(message).encode()
        self.offsets.append(self.f.tell())
        self.f.write(HEADER.pack(len(payload), zlib.crc32(payload)) + payload)
        self.f.flush()
        if sync:
            os.fsync(self.f.fileno())           # durable before we acknowledge
        return len(self.offsets) - 1            # the record's offset (its index)

    def read(self, offset, max_records=10):
        out = []
        with open(self.path, "rb") as f:
            for i in range(offset, min(offset + max_records, len(self.offsets))):
                f.seek(self.offsets[i])
                length, _ = HEADER.unpack(f.read(HEADER.size))
                out.append((i, json.loads(f.read(length))))
        return out

class ConsumerGroup:
    """Committed offset per group, stored atomically (write temp file, then rename)."""
    def __init__(self, path):
        self.path = path
        self.committed = json.load(open(path))["next"] if os.path.exists(path) else 0

    def commit(self, next_offset):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"next": next_offset}, f); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, self.path)              # atomic on POSIX
        self.committed = next_offset

if __name__ == "__main__":
    d = tempfile.mkdtemp()
    log = Log(os.path.join(d, "orders-0.log"))
    for i in range(5):
        log.append({"order": 100 + i, "amount": 10 * (i + 1)})
    log.f.write(HEADER.pack(50, 12345) + b'{"order": 1')   # simulate a crash mid-write
    log.f.close()

    print("restart broker:")
    log = Log(os.path.join(d, "orders-0.log"))
    print("  records after recovery:", len(log.offsets))
    print("  append ->", log.append({"order": 105, "amount": 60}))

    group = ConsumerGroup(os.path.join(d, "billing.offset"))
    batch = log.read(group.committed, max_records=4)
    print("consumer reads:", [m["order"] for _, m in batch])
    print("consumer crashes before commit; restarts")
    group = ConsumerGroup(os.path.join(d, "billing.offset"))
    batch = log.read(group.committed, max_records=4)
    print("consumer re-reads:", [m["order"] for _, m in batch], "(at-least-once)")
    group.commit(batch[-1][0] + 1)
    print("after commit, next read:", [m["order"] for _, m in log.read(group.committed)])
```

Output:

```text
restart broker:
  recovery: truncating 19 bytes of torn tail
  records after recovery: 5
  append -> 5
consumer reads: [100, 101, 102, 103]
consumer crashes before commit; restarts
consumer re-reads: [100, 101, 102, 103] (at-least-once)
after commit, next read: [104, 105]
```

What to notice:

- The simulated crash left a header that promised 50 bytes followed by only 11. Recovery reads records until the first one that is incomplete or fails its CRC, keeps that prefix and truncates the rest (19 bytes: an 8-byte header plus 11 payload bytes). Five acknowledged records survive and the next append gets offset 5, so offsets stay dense.
- `append` calls `fsync` before returning the offset. Acknowledging before `fsync` would make the broker faster and occasionally lose acknowledged messages after a power failure; batching (Milestone 2) lets you keep the `fsync` and amortize it.
- The consumer processed offsets 0–3 and crashed before committing, so after restart it read them again: **at-least-once** delivery. Committing before processing would have lost them instead. There is no third option without making processing idempotent or transactional with the commit (§31.11).
- An offset here is a record index, and the in-memory list `offsets` maps it to a byte position. That list is rebuilt by scanning the whole file at startup, which is fine for 1 MB and hopeless for 100 GB; the sparse index in Milestone 1 fixes it.
- The commit uses write-to-temporary, `fsync`, then `os.replace`. Overwriting the offset file in place could leave it half-written after a crash, and the consumer group would lose its position.

::: example
**Worked example — How long does a backlog take to drain?**

*Assumptions.* Producers write 1,000 messages/s steadily. The billing consumer group is down for 30 minutes. When it returns, its consumers can process 1,500 messages/s in total (§30.4.3 gives the general method).

1. Backlog accumulated: $1{,}000 \times 30 \times 60 = 1.8 \times 10^6$ messages.
2. While draining, new messages keep arriving, so the backlog shrinks at the *net* rate $1{,}500 - 1{,}000 = 500$ messages/s.
3. Drain time: $1.8 \times 10^6 / 500 = 3{,}600$ s, one hour, twice as long as the outage.
4. With 3,000 messages/s of consumer capacity, the net rate is 2,000/s and the drain takes $1.8 \times 10^6 / 2{,}000 = 900$ s, 15 minutes.

*Interpretation.* Recovery time depends on spare capacity, not total capacity: a consumer group running at 67% utilization needs twice the outage length to catch up. *Engineering implication.* Size consumer groups for drain time, not only for steady state, and make sure there are enough partitions to add consumers when you need them (§31.7.3). Retention must also outlast the worst outage plus its drain time, or the backlog is deleted before it is read.
:::

#### Test plan and load-test targets

Unit tests cover encoding and decoding, recovery at every possible truncation point of a three-record file (loop over all byte lengths), CRC detection of a flipped bit, index lookups at segment boundaries and the assignment algorithms. A **model-based test** runs random sequences of produce, fetch, commit, broker restart and consumer restart against your broker and against a trivially correct in-memory model, and checks that every fetched record matches the model and that offsets never go backward except to the committed position.

Load tests run producers at increasing rates with batch sizes 1, 10, 100 and 1,000, recording throughput, produce latency p99 and end-to-end p99 (each message carries its produce timestamp). Run a 1 million-message ordering test with 1,000 keys over 8 partitions and three consumers, and check per-key sequence numbers at the consumers.

#### Failure-injection exercises

1. **Crash during a batch.** Kill the broker while it writes a batch of 100 records. Decide, and test, whether a batch is all-or-nothing after recovery or may be partially present, and what producers see in each case.
2. **Zombie consumer.** Pause a consumer with SIGSTOP for longer than the session timeout, let its partitions move, then resume it with SIGCONT. It will try to commit; your generation check must refuse it. Count duplicates processed during the overlap.
3. **Poison message.** Produce a message that makes the consumer throw. Without a dead-letter path, the partition stalls forever behind it (head-of-line blocking); with one, it moves on after five attempts (§30.11).
4. **Slow consumer and retention.** Set retention to 5 minutes and stop a consumer for 10. On restart its committed offset no longer exists. Implement and justify the reset policy (earliest or latest) and record how many messages were lost.

#### Extensions

- Replicate each partition to a follower broker with an in-sync replica set and `acks=all`, following §31.9; then run §31.9.5's scenarios against your code.
- Add log compaction for keyed topics: keep only the latest value per key in closed segments (§31.10.2).
- Add idempotent producers: a producer ID and sequence number per partition, with the broker rejecting duplicates after a producer retry (§31.6.3).
- Implement a share-group (queue) mode where consumers acknowledge individual messages instead of committing offsets, and compare it with the visibility-timeout queue of §30.11.2 (§31.7.4).

#### Self-assessment rubric

**Table 93.13 — Message queue: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Storage | Append and read work | Segments, index, CRC, torn-tail recovery; 100/100 crash trials | You can explain what an acknowledgment promises under each `fsync` policy |
| Throughput | One producer works | Batching curve measured; targets met | You can explain the batching trade-off with your numbers and §31.13 |
| Consumer groups | Single consumer | Assignment, heartbeats, rebalancing, generation fencing | You can describe the duplicate window during a rebalance and how to shrink it |
| Delivery semantics | Messages delivered | At-most-once and at-least-once shown; idempotent consumer exact | You can explain why exactly-once needs cooperation from the consumer's side effects |
| Operations | Runs | Retention, dead letters, lag metric, drain measured | You can size partitions and consumers for a given rate and drain time |

### 93.2.2 Distributed key-value store

#### Goal and learning outcomes

Build a Dynamo-style key-value store: five or more node processes that partition keys with consistent hashing, replicate each key to three nodes, and serve reads and writes with tunable quorums. Section 52.8 designs this system in full and Chapters 14 and 27 explain each mechanism. In this project you will watch the mechanisms interact: a write that succeeds with one replica down, a stale replica that comes back, a read that repairs it, a node that joins and pulls its share of keys, and the cases where "eventually consistent" means a user briefly sees an old value.

After this project you should be able to:

- Implement a consistent-hash ring with virtual nodes and measure load balance and key movement when nodes join or leave (§14.8).
- Implement quorum reads and writes with configurable $N$, $R$ and $W$, and demonstrate both what $R + W > N$ guarantees and what it does not (§27.8).
- Implement read repair, hinted handoff and Merkle-tree anti-entropy, and measure how quickly replicas converge after a failure (§27.9, §27.13, §17.8).
- Detect concurrent writes with version vectors and return siblings, and compare with last-writer-wins (§27.14).

#### Prerequisites

- Consistent hashing, virtual nodes and replication on the ring — §14.8; rebalancing — §14.9.
- Leaderless replication, quorums, sloppy quorums and hinted handoff — §27.7–27.9; anti-entropy and read repair — §27.13; conflict resolution — §27.14.
- Failure detection with heartbeats and gossip — §27.10.
- Vector clocks and version vectors — §24.11; consistency models and Jepsen-style testing — §25.3, §25.7, §25.11.
- The case study — §52.8; and the message-queue project's storage lessons (§93.2.1), since each node needs a durable local store.

#### Specification

**Functional requirements.**

1. Each node is a process with an HTTP API: `GET /kv/{key}`, `PUT /kv/{key}` with an optional version context, `DELETE /kv/{key}` (a tombstone). Any node can act as **coordinator** for any key and forwards to the key's replicas.
2. Configurable $N$, $R$, $W$ per request or per cluster; defaults $N = 3$, $R = W = 2$.
3. Membership from a static seed list plus heartbeats; a node that misses heartbeats for 3 s is considered down by the coordinator.
4. Hinted handoff: when a replica is down, the coordinator writes to the next healthy node on the ring with a hint naming the intended owner, and that node delivers the write when the owner returns.
5. Anti-entropy: each pair of replicas compares Merkle trees of their key ranges every 30 s and exchanges only differing keys.
6. Node join and decommission with background data movement, rate-limited.
7. Each node persists data locally (SQLite, or an append-only log with an in-memory index, reusing §93.2.1).

**Non-functional requirements.**

**Table 93.14 — Distributed key-value store: targets (five to six node processes on one machine).**

| Property | Target | How you verify it |
|---|---|---|
| Latency | `GET` and `PUT` p99 ≤ 20 ms at 1,000 operations/s across the cluster, loopback | Load test |
| Load balance | Largest node holds ≤ 1.15 × the mean number of keys with 128 virtual nodes each | Key-count report |
| Availability | Reads and writes at $R = W = 2$ keep succeeding with any one node down | Kill a node during a load test |
| Read-your-writes | With $R + W > N$ and no sloppy-quorum substitutes, a read after an acknowledged write returns it in 100% of 10,000 trials | Linearizability-style checker on single-key histories |
| Convergence | After a node is down for 60 s under writes and then returns, all replicas agree within 2 anti-entropy rounds | Replica comparison |
| Join | Adding a sixth node moves ≈ 1/6 of the data, and foreground p99 stays ≤ 40 ms during movement | Movement counter and load test |
| Conflict detection | Concurrent writes from two clients produce siblings, never silent loss, in version-vector mode | Concurrency test |

#### Architecture

**Figure 93.7 — Distributed key-value store: coordinator, ring and replicas.**

```mermaid
flowchart LR
  CL([Client]) -->|PUT /kv/cart:7| N1["Node A<br/>coordinator for this request"]
  N1 -->|replicate| N2["Node B<br/>replica 1"]
  N1 -->|replicate| N3["Node E<br/>replica 2"]
  N1 -->|replicate| N4["Node A local<br/>replica 3"]
  N1 -.->|hinted write if a replica is down| N5["Node C<br/>holds hint"]
  N2 --- S2[(Local store B)]
  N3 --- S3[(Local store E)]
  N4 --- S4[(Local store A)]
  N2 -.->|Merkle tree exchange| N3
  N1 -.->|heartbeats| N2
```

**Reading the diagram.** The client sends a request to any node, which becomes the coordinator for that request. The coordinator computes the key's preference list on the hash ring: the first three distinct nodes clockwise from the key's hash (here B, E and A itself). It sends the write to all three in parallel over HTTP and replies after $W$ acknowledgments. Reads work the same way with $R$ responses, and if the responses disagree, the coordinator returns the newest and writes it back to the stale replicas (read repair). If a replica is down, the coordinator writes to the next node on the ring (C) with a hint (dotted), and C forwards the write when the owner recovers. In the background, replicas compare Merkle trees and exchange only differences, and nodes exchange heartbeats (both dotted). Each node's storage boundary is its local store; there is no shared storage. Failure points: any node (tolerated up to $N - W$ for writes and $N - R$ for reads), the coordinator crashing after a partial write (the write may be present on fewer than $W$ nodes and still surface later), lost hints, and network partitions that make each side believe the other is down. Scaling: add nodes; each joins the ring at its virtual-node positions and takes over about $1/n$ of the keys.

#### Milestones

1. **Single-process prototype.** Extend the starter with tombstones, version vectors (instead of a global counter, which a real cluster does not have) and siblings, and a deterministic fault schedule. *Done when:* unit tests reproduce every scenario in the starter plus a concurrent-write test that returns two siblings.
2. **Real nodes.** Move each node into its own process with an HTTP API and local persistence; the coordinator sends replica requests in parallel with a 200 ms timeout. *Done when:* the latency and availability targets hold with five processes, including a kill of one node mid-test.
3. **Hinted handoff and anti-entropy.** Implement hints with durable storage on the substitute node and a Merkle tree over each node's key range (hash leaves by key-range bucket, as §17.8 describes). *Done when:* the convergence target holds, and you can show the number of keys exchanged by anti-entropy compared with a full comparison.
4. **Membership changes.** Implement join and decommission with rate-limited streaming of the affected ranges, and switch reads to the new owner only after its copy is complete. *Done when:* the join target holds, and no acknowledged key is unreadable at any time during the move.
5. **Consistency testing.** Write a test harness that runs concurrent clients, records every operation's invocation and completion time and result, injects faults (kills, pauses with SIGSTOP, and network delays through a small proxy), and checks single-key histories for stale reads. *Done when:* the checker finds stale reads with $R = W = 1$, finds none with $R = W = 2$ when sloppy quorums are disabled, and finds some again with sloppy quorums enabled, and you can explain each result (§27.8.2).

#### Starter code

The starter keeps all nodes in one process, so failure is just a flag. It builds a ring with 64 virtual nodes per node, writes 1,000 keys with $N = 3$, $R = W = 2$, takes a replica down during a write, brings it back stale, repairs it on read, and finally measures key movement when a sixth node joins, compared with naive `hash mod N` placement.

```python
"""Distributed KV core: consistent hashing with virtual nodes, N=3 replication,
quorum reads and writes (R=W=2), last-writer-wins versions and read repair.
Nodes are in-process objects so that failures are one flag away (starter)."""
import bisect, hashlib

def h(s):
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")

class Ring:
    def __init__(self, nodes, vnodes=64):
        self.vnodes, self.points = vnodes, []          # sorted (hash, node) pairs
        for n in nodes:
            self.add(n)

    def add(self, node):
        for v in range(self.vnodes):
            bisect.insort(self.points, (h(f"{node}#{v}"), node))

    def preference_list(self, key, n=3):
        """First n distinct nodes clockwise from the key's position."""
        i, out = bisect.bisect(self.points, (h(key), "")), []
        while len(out) < n:
            node = self.points[i % len(self.points)][1]
            if node not in out:
                out.append(node)
            i += 1
        return out

class Node:
    def __init__(self, name):
        self.name, self.data, self.up = name, {}, True  # key -> (version, value)

class Cluster:
    def __init__(self, names, n=3, r=2, w=2):
        self.nodes = {x: Node(x) for x in names}
        self.ring, self.n, self.r, self.w, self.clock = Ring(names), n, r, w, 0

    def put(self, key, value):
        self.clock += 1                                 # stand-in for a hybrid clock
        acks = 0
        for name in self.ring.preference_list(key, self.n):
            node = self.nodes[name]
            if node.up:
                node.data[key] = (self.clock, value)
                acks += 1
        return acks >= self.w                           # success only with W acks

    def get(self, key):
        replies = [(name, self.nodes[name].data.get(key, (0, None)))
                   for name in self.ring.preference_list(key, self.n) if self.nodes[name].up]
        if len(replies) < self.r:
            raise RuntimeError("read quorum not met")
        newest = max(v for _, v in replies)             # last-writer-wins by version
        for name, v in replies:                         # read repair of stale replicas
            if v < newest:
                self.nodes[name].data[key] = newest
        return newest[1]

if __name__ == "__main__":
    names = ["A", "B", "C", "D", "E"]
    c = Cluster(names)
    print("preference list for 'user:42':", c.ring.preference_list("user:42"))
    for i in range(1000):
        c.put(f"k{i}", f"v{i}")
    print("keys per node:", {x: len(c.nodes[x].data) for x in names})

    a, b, _ = c.ring.preference_list("cart:7")
    c.put("cart:7", "1 item")
    c.nodes[a].up = False                               # one replica down
    print("put with one replica down ->", c.put("cart:7", "2 items"))
    c.nodes[a].up = True                                # it returns with a stale value
    print("stale replica holds:", c.nodes[a].data["cart:7"][1])
    print("quorum read ->", c.get("cart:7"), "| after read repair:", c.nodes[a].data["cart:7"][1])
    c.nodes[a].up = c.nodes[b].up = False
    print("put with two replicas down ->", c.put("cart:7", "3 items"))

    keys = [f"k{i}" for i in range(10_000)]
    before = {k: c.ring.preference_list(k, 1)[0] for k in keys}
    c.ring.add("F")
    moved = sum(before[k] != c.ring.preference_list(k, 1)[0] for k in keys)
    print(f"add node F: {moved / len(keys):.1%} of keys change primary (ideal 1/6 = 16.7%)")
    naive = sum(h(k) % 5 != h(k) % 6 for k in keys)
    print(f"hash mod N, 5 -> 6 nodes: {naive / len(keys):.1%} of keys move")
```

Output:

```text
preference list for 'user:42': ['B', 'E', 'A']
keys per node: {'A': 535, 'B': 607, 'C': 634, 'D': 604, 'E': 620}
put with one replica down -> True
stale replica holds: 1 item
quorum read -> 2 items | after read repair: 2 items
put with two replicas down -> False
add node F: 14.2% of keys change primary (ideal 1/6 = 16.7%)
hash mod N, 5 -> 6 nodes: 83.5% of keys move
```

What to notice:

- Five nodes with three replicas each should hold 600 keys on average; the actual range is 535–634, about ±10%, with 64 virtual nodes per node. More virtual nodes narrow the spread (§14.8.4); measure it with 16, 64, 128 and 256.
- The write with one replica down succeeds because two acknowledgments meet $W = 2$. The returning replica still holds `1 item`, and the quorum read returns `2 items` because any two of the three replicas include at least one with the new value. Read repair then fixes the stale copy as a side effect.
- The write with two replicas down returns `False`, but the one live replica *did* store `3 items`, and nothing undoes it. A later read that reaches that replica will return the "failed" value. A failed quorum write means "not guaranteed", not "did not happen"; clients must retry until success or treat the outcome as unknown.
- Adding a sixth node moved 14.2% of keys' primary owner, close to the ideal 1/6, whereas `hash mod N` moved 83.5%. The difference between those two numbers is the reason consistent hashing exists (§14.8.1).
- The global `self.clock` gives every write a total order, which no real cluster has. Replace it with version vectors in Milestone 1 and you will discover concurrent writes that last-writer-wins silently discards.

::: example
**Worked example — How available is a quorum write?**

*Assumptions.* $N = 3$ replicas; each replica is independently reachable with probability $p = 0.99$ at any moment (§4.14 for the arithmetic; real failures are often correlated, which makes the true numbers worse).

1. $W = 3$ (all replicas): $p^3 = 0.99^3 = 0.9703$, so about 3% of writes fail.
2. $W = 2$: success when all three are up or exactly two are: $p^3 + 3p^2(1 - p) = 0.9703 + 3 \times 0.9801 \times 0.01 = 0.9703 + 0.0294 = 0.9997$.
3. $W = 1$: success unless all three are down: $1 - (1 - p)^3 = 1 - 10^{-6} = 0.999999$.

*Interpretation.* Moving from $W = 3$ to $W = 2$ cuts the write failure rate a hundredfold, from about 3% to 0.03%, while keeping $R + W > N$ possible with $R = 2$. *Engineering implication.* $N = 3$, $R = W = 2$ is the common default because it tolerates one replica failure for both reads and writes; sloppy quorums push availability further at the cost of the overlap guarantee (§27.9). Place replicas in different zones so that the independence assumption is closer to the truth (§39.4.2).
:::

#### Test plan and load-test targets

Unit tests check the ring (preference lists have $N$ distinct nodes, wrap around correctly, and change minimally on join), version-vector comparison (equal, descends, concurrent), sibling merging and Merkle-tree diffing on ranges that differ by one key. Integration tests start five processes on different ports and run scripted fault scenarios.

The consistency harness is the centerpiece of the test plan. Run 10 clients for 60 s against 100 keys, each performing random reads and writes of unique values, while a nemesis thread kills and restarts a random node every 10 s. Record histories and check, per key, that no read returns a value older than one whose write completed before the read began (when $R + W > N$ without substitutes). Load-test at 1,000 operations/s with 90% reads and a Zipf key distribution, and record p99 overall and during a node kill.

#### Failure-injection exercises

1. **Coordinator crash mid-write.** Kill the coordinator after it has sent the write to one replica. Show the value surfacing later through read repair or anti-entropy, and decide whether your client should treat a timed-out write as failed or unknown.
2. **Network partition.** Put a forwarding proxy between nodes and drop traffic between {A, B} and {C, D, E}. With strict quorums, which keys can each side write? With sloppy quorums, both sides accept writes for every key; heal the partition and observe siblings or last-writer-wins losses (§25.8).
3. **Lost hints.** Kill the node holding hints before it delivers them. Show that anti-entropy eventually repairs the owner, and measure how long it takes.
4. **Clock skew with last-writer-wins.** Switch to wall-clock timestamps and skew one coordinator's clock by −5 s. Writes coordinated by it lose to older writes from other coordinators. Count the silently lost updates (§27.14.1).

#### Extensions

- Add multi-datacenter replication with per-datacenter quorums (local quorum in each of two "datacenters" on different ports with added delay).
- Replace last-writer-wins for a shopping-cart value with a CRDT (an observed-remove set) and show that concurrent adds and removes merge without loss (§27.14.3).
- Use gossip (SWIM-style) for membership instead of a static list (§27.10.3).
- Compare your store with a single-leader design built on the Raft simulator of §26.7.7 for the same workload: what do you gain and lose?

#### Self-assessment rubric

**Table 93.15 — Distributed key-value store: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Partitioning | Ring with virtual nodes | Balance and movement measured; join and decommission online | You can derive the movement fraction and the effect of virtual-node count |
| Replication and quorums | Quorum reads and writes | Availability under a node failure; parallel requests with timeouts | You can explain what $R + W > N$ does and does not guarantee, with your checker's results |
| Repair | Read repair | Hinted handoff and Merkle anti-entropy; convergence measured | You can compare the repair mechanisms by cost and by what they miss |
| Conflicts | Last-writer-wins | Version vectors and siblings; lost updates demonstrated under clock skew | You can choose LWW, siblings or CRDTs for a given data type and defend it |
| Testing | Unit tests | History checker with a nemesis | You can describe a bug your checker found and how you fixed it |

### 93.2.3 Replicated database simulation

#### Goal and learning outcomes

Build a primary–replica database out of a simple key-value state machine and a write-ahead log (WAL): the primary appends every change to its log and ships the log to two replicas, which apply it in order. Then break it. Make replicas lag, read from them, crash the primary, promote a replica, and bring the old primary back. Chapter 14 introduced replication modes and lag, Chapter 27 failover and recovery, and Chapter 26 fencing; this project lets you produce each anomaly on purpose and measure what each mode costs.

After this project you should be able to:

- Implement WAL shipping with log sequence numbers (LSNs), in-order apply and catch-up after a disconnection (§14.4.5, §27.12).
- Compare asynchronous, semi-synchronous and synchronous acknowledgment by latency and by acknowledged writes lost at failover (§14.4.1).
- Reproduce the replication-lag anomalies (stale reads, non-monotonic reads) and fix them with session guarantees (§14.4.3–14.4.4, §25.6).
- Run a failover: detect the dead primary, pick the most up-to-date replica, redirect clients, and fence the old primary with an epoch (§27.11, §26.13).

#### Prerequisites

- Primary–replica architecture, replication modes, lag and its anomalies — §14.3–14.4.
- Primary–backup replication — §27.4; failure detection — §27.10; failover and recovery — §27.11–27.12.
- Session guarantees — §25.6; split brain, leases and fencing tokens — §26.11–26.13.
- Write-ahead logging — §13.5; the Raft simulator — §26.7.7 (for the extension).
- The message-queue log format (§93.2.1) can be reused as the WAL.

#### Specification

**Functional requirements.**

1. Three node processes: one primary and two replicas. Clients send `PUT`/`GET` over HTTP; writes go to the primary, and reads go to the primary or a replica according to a client-side policy.
2. The primary assigns each write an LSN, appends it to its WAL, applies it to its state, and streams WAL records to each replica over a long-lived TCP connection. Replicas acknowledge the highest LSN they have durably written.
3. Replication mode per cluster: `async` (acknowledge the client after the local write), `semi-sync` (after at least one replica acknowledges) or `sync` (after all replicas acknowledge).
4. A replica that reconnects requests records from its last LSN; if the primary no longer has them, it requests a snapshot.
5. A failover controller monitors heartbeats, declares the primary dead after a timeout, promotes the replica with the highest LSN, increments the **epoch**, and publishes the new primary's address. Every replicated record and every write carries the epoch; nodes reject records from a lower epoch.
6. Client sessions carry the LSN of their last write, so that a read can be served by a replica only if it has applied at least that LSN (read-your-writes).

**Non-functional requirements.**

**Table 93.16 — Replicated database simulation: targets (three processes, 2 ms and 6 ms injected one-way delays to the two replicas).**

| Property | Target | How you verify it |
|---|---|---|
| Write latency by mode | Measured p50/p99 for each mode; semi-sync p50 ≈ async p50 + the faster replica's round trip | Load test at 500 writes/s |
| Lost writes at failover | Semi-sync and sync: 0 acknowledged writes lost over 50 crash trials; async: measured and explained | Crash harness with an acknowledgment log |
| Read-your-writes | 0 violations in 10,000 session reads served by replicas | Session checker |
| Failover time | New primary accepting writes within heartbeat timeout + 1 s | Timeline from logs |
| Fencing | 0 writes from a deposed primary accepted by any node | Old-primary return test |
| Catch-up | A replica disconnected for 60 s at 500 writes/s catches up within 10 s of reconnecting | Lag metric |

#### Architecture

**Figure 93.8 — Semi-synchronous write, primary crash and failover with fencing.**

```mermaid
sequenceDiagram
  participant C as Client
  participant P as Primary (epoch 1)
  participant R1 as Replica 1 (2 ms)
  participant R2 as Replica 2 (6 ms)
  participant FC as Failover controller
  C->>P: PUT k=v
  P->>P: append LSN 9 to WAL
  P->>R1: WAL record LSN 9, epoch 1
  P->>R2: WAL record LSN 9, epoch 1
  R1-->>P: ack LSN 9
  P-->>C: OK (one replica has it)
  Note over P: primary crashes
  FC->>R1: heartbeats missed, promote, epoch 2
  FC->>R2: follow Replica 1, epoch 2
  R1->>R2: catch-up records, epoch 2
  P->>R2: late record, epoch 1
  R2-->>P: rejected, epoch 1 is fenced
```

**Reading the diagram.** Time runs downward. The client's write is synchronous: it waits for the primary's `OK`. The primary appends the record to its WAL, sends it to both replicas over their streaming connections, and in semi-synchronous mode replies to the client as soon as the faster replica acknowledges (dashed arrows are replies). The slower replica's copy is still in flight, which is replication lag. When the primary crashes, the failover controller notices missing heartbeats, promotes Replica 1 (it has the highest LSN), increments the epoch to 2 and tells Replica 2 to follow it. Replica 1 then sends Replica 2 the records it is missing. If the old primary was not really dead (a long pause, or a network partition that only hid it from the controller), its late record carries epoch 1 and is rejected: that rejection is the fence. Storage boundaries are each node's WAL and state. Failure points: the primary (acknowledged writes that reached no replica are lost in async mode), the controller (it must not promote two replicas, which is why production systems run it on a consensus service), and the network (a partition can make a live primary look dead). Scaling: add read replicas for read throughput, at the cost of more lag to manage; write throughput stays bounded by one primary.

#### Milestones

1. **WAL shipping.** Turn the starter into three processes with a streaming TCP connection per replica, LSN-ordered apply, acknowledgments and a lag metric (primary LSN minus replica LSN). Inject delay in the sender. *Done when:* replicas converge to an identical state hash after a 100,000-write run, and lag is visible on a per-second graph.
2. **Modes and their costs.** Implement the three acknowledgment modes and run the latency load test and the crash harness for each. *Done when:* your results log has a table of mode × (p50, p99, lost acknowledged writes), and each number is explained.
3. **Session guarantees.** Reproduce a stale read (write to the primary, read immediately from the slow replica) and a non-monotonic read (two reads from different replicas going back in time); then implement LSN-based read-your-writes and monotonic reads. *Done when:* the checker finds violations without the session LSN and none with it.
4. **Failover and fencing.** Build the controller and the epoch checks; make clients rediscover the primary. *Done when:* failover and fencing targets hold, including a test that pauses the primary with SIGSTOP (so that it is alive but silent) and resumes it after promotion.
5. **Catch-up and snapshots.** Truncate the WAL after a checkpoint, so that a replica that has been away too long needs a snapshot followed by the log tail. *Done when:* the catch-up target holds for both paths.

#### Starter code

The starter simulates log shipping in 1 ms ticks. One write per millisecond goes to the primary, which ships it to replicas with one-way delays of 2 ms and 6 ms (the code calls them followers). The primary crashes at $t$ = 10 ms; the most up-to-date replica is promoted; the old primary then tries to keep shipping.

```python
"""Replicated database core: a primary ships its write-ahead log to two followers
with different network delays. Compares asynchronous and semi-synchronous
acknowledgment across a primary crash and failover, then fences the old primary.
Time advances in 1 ms ticks; everything is deterministic (starter)."""

DELAY = {"F1": 2, "F2": 6}                       # one-way log-shipping delay, ms

class Follower:
    def __init__(self, name):
        self.name, self.log, self.epoch = name, [], 1

    def apply(self, epoch, lsn, record):
        if epoch < self.epoch:                   # fencing: reject a deposed primary
            return False
        self.epoch = epoch
        if lsn == len(self.log) + 1:             # apply strictly in log order
            self.log.append(record)
        return True

def run(mode, writes=10, crash_at=10):
    followers = {n: Follower(n) for n in DELAY}
    in_flight, acked = [], []                    # (deliver_at, follower, lsn, record)
    for t in range(1, writes + 1):               # one client write per ms
        record = f"w{t}"
        for name, d in DELAY.items():
            in_flight.append((t + d, name, t, record))
        ack_at = t if mode == "async" else t + min(DELAY.values())   # semi-sync: wait for 1
        if ack_at <= crash_at:
            acked.append(record)
        if t == 6:                               # a read served by the slower follower
            seen = [x for x in in_flight if x[1] == "F2" and x[0] <= t]
            print(f"  [{mode}] t=6 ms: primary has w1..w6, follower F2 has {len(seen)} record(s)")
    for deliver_at, name, lsn, record in sorted(in_flight):
        if deliver_at <= crash_at:               # only what arrived before the crash
            followers[name].apply(1, lsn, record)
    new = max(followers.values(), key=lambda f: len(f.log))   # promote the most up to date
    lost = [r for r in acked if r not in new.log]
    print(f"  [{mode}] crash at t={crash_at} ms: acked {len(acked)}, promoted {new.name} "
          f"with {len(new.log)} records, lost acknowledged writes: {lost or 'none'}")
    return followers, new

if __name__ == "__main__":
    for mode in ("async", "semi-sync"):
        followers, new = run(mode)
    for f in followers.values():                 # failover bumps the epoch everywhere
        f.epoch = 2
    other = [f for f in followers.values() if f is not new][0]
    print("old primary (epoch 1) returns and ships w11 ->",
          "accepted" if other.apply(1, len(other.log) + 1, "w11") else "rejected (fenced)")
    nxt = new.log[len(other.log)]                # catch-up record from the new primary
    print(f"new primary (epoch 2) ships {nxt} to {other.name} ->",
          "accepted" if other.apply(2, len(other.log) + 1, nxt) else "rejected")
```

Output:

```text
  [async] t=6 ms: primary has w1..w6, follower F2 has 0 record(s)
  [async] crash at t=10 ms: acked 10, promoted F1 with 8 records, lost acknowledged writes: ['w9', 'w10']
  [semi-sync] t=6 ms: primary has w1..w6, follower F2 has 0 record(s)
  [semi-sync] crash at t=10 ms: acked 8, promoted F1 with 8 records, lost acknowledged writes: none
old primary (epoch 1) returns and ships w11 -> rejected (fenced)
new primary (epoch 2) ships w5 to F2 -> accepted
```

What to notice:

- At $t$ = 6 ms the primary has six writes and the slow replica none, because its first record arrives at 7 ms. A client that writes to the primary and reads from that replica sees nothing: the stale read of §14.4.3.
- In asynchronous mode all ten writes were acknowledged, but only eight had reached the faster replica by the crash, so promoting it loses `w9` and `w10`, writes the client was told had succeeded.
- In semi-synchronous mode the primary acknowledged only after the faster replica had a record, so writes 9 and 10 were never acknowledged (their acknowledgments were due at 11 and 12 ms), and nothing acknowledged is lost. The cost is that each write waits for a replica.
- After failover, the replicas are at epoch 2. The old primary's record carries epoch 1 and is rejected, while the new primary's catch-up record `w5` is accepted. The epoch is a fencing token (§26.13): it makes a deposed primary harmless even if it does not know it has been deposed.
- The starter promotes "the replica with the longest log" by looking at all replicas at once, which a real controller cannot do if a replica is unreachable. Choosing safely with partial information is exactly what consensus solves (§26.5.2).

::: example
**Worked example — Translating replication lag into a recovery point objective.**

*Assumptions.* The primary accepts 2,000 writes/s; asynchronous replication runs with a typical lag of 50 ms and spikes to 2 s during a bulk import; the replica with the least lag is promoted.

1. Typical loss on failover: $2{,}000 \times 0.050 = 100$ acknowledged writes.
2. Loss during a lag spike: $2{,}000 \times 2 = 4{,}000$ acknowledged writes.
3. Semi-synchronous mode with the nearest replica in another zone 1 ms away adds about one round trip, 1 ms, to every write's latency, and reduces the loss to zero for any single-node failure.

*Interpretation.* With asynchronous replication, the recovery point objective (§39.8.1) is not a fixed number; it is whatever the lag happens to be at the moment of failure. *Engineering implication.* Monitor lag in seconds and alert on it, and if the business requires RPO = 0, pay the round trip for semi-synchronous replication or use a consensus-replicated log.
:::

#### Test plan and load-test targets

Unit tests check in-order apply (out-of-order and duplicate records are handled), epoch rejection, LSN bookkeeping across reconnection and snapshot installation. The **crash harness** runs a client that logs every acknowledged write, kills the primary at a random moment, waits for failover and then reads every logged key from the new primary; any missing acknowledged write is a loss and is counted per mode. The **session checker** runs clients that write and immediately read, randomly routed to replicas, and counts reads that do not reflect the client's own last write. Load-test writes at 500 per second in each mode for 60 s and report p50 and p99.

#### Failure-injection exercises

1. **Network partition around the primary.** Block the controller's heartbeats from the primary while clients can still reach it. The controller promotes a replica; for a while two nodes believe they are primary. Count the writes the old primary accepts and then loses, and show that a primary lease (stop accepting writes when the lease expires, §26.11) closes the window.
2. **Slow disk on a replica.** Delay `fsync` on Replica 2. In sync mode every write slows down; in semi-sync mode nothing changes until Replica 1 also fails. Measure both.
3. **Double failure.** Kill the primary and the fastest replica together in semi-sync mode. The remaining replica may lack acknowledged writes; quantify how often, and explain why "semi-synchronous" protects against one failure only.
4. **Replica falls behind retention.** Pause a replica until the primary has truncated the WAL it needs. Verify that it falls back to a snapshot and does not silently skip records.
5. **Promotion of a lagging replica.** Force the controller to promote the slower replica. Measure the lost writes, and then make the controller refuse to promote a replica more than a configured lag behind (and explain the availability cost).

#### Extensions

- Replace the controller with Raft: run the §26.7.7 simulator's election and log rules over your WAL so that commit requires a majority and failover needs no external controller.
- Add logical replication: stream row-level change events to a fourth process that builds a read-optimized view (§14.4.5, §32.6).
- Implement chain replication with reads at the tail and compare latency and consistency (§27.5).
- Add point-in-time recovery from WAL archives (§39.9.3).

#### Self-assessment rubric

**Table 93.17 — Replicated database simulation: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Log shipping | Replicas apply the log | Streaming, acknowledgments, lag metric, catch-up and snapshots | You can explain LSNs, ordering and idempotent apply |
| Modes | Async works | Three modes measured for latency and loss | You can pick a mode for a given RPO and latency budget with your numbers |
| Read consistency | Reads from replicas | Stale and non-monotonic reads reproduced and fixed | You can explain session guarantees and their implementation cost |
| Failover | Manual promotion | Automatic failover with epochs; paused-primary test passes | You can explain split brain and why fencing is needed even with leases |
| Rigor | Happy path | Crash harness and session checker run in CI | You can argue when to replace the controller with consensus |

### 93.2.4 Notification service

#### Goal and learning outcomes

Build a service that accepts "notify this user" requests from other services and delivers them over e-mail, SMS and push through fake providers, respecting user preferences, provider quotas and priorities. Section 52.7 designs this system at the scale of 50 million recipients per campaign. The hard parts survive the scaling down: a one-time password must not wait behind a marketing campaign, a retried API call must not send two text messages, a provider outage must not lose messages, and an opt-out must take effect before the next send.

After this project you should be able to:

- Accept requests durably and idempotently, then deliver asynchronously through queues (§52.7.8, §22.15).
- Isolate priorities so that critical traffic meets its latency target during a large campaign (§52.7.3).
- Retry transient provider failures with exponential backoff and jitter, and route permanent failures to a dead-letter queue (§22.12, §30.10–30.11).
- Respect per-provider rate limits with the limiter of §93.1.4, and per-user preferences and quiet hours.

#### Prerequisites

- The case study — §52.7; mobile push and its delivery limits — §9.8.
- Queues, retries, poison messages and dead letters — §30.4, §30.10–30.11; idempotent consumers — §32.10.
- Retries with backoff and jitter, circuit breakers and idempotency keys — §22.12–22.13, §22.15.
- The message queue (§93.2.1) as the transport and the rate limiter (§93.1.4) for provider quotas.

#### Specification

**Functional requirements.**

1. `POST /notifications` with an `Idempotency-Key`, a user ID, a template ID, parameters, a kind (`otp`, `transactional` or `marketing`) and optional channels. The API returns `202 Accepted` with a notification ID after the request is durably stored.
2. A preference service: per user and channel opt-outs, quiet hours in the user's time zone (marketing is deferred, OTPs are not), and a frequency cap for marketing (at most 3 per day).
3. Per-channel worker pools reading from per-priority queues; critical queues are always served first, and marketing has its own quota so that it can never consume all provider capacity.
4. Fake providers for e-mail, SMS and push with configurable latency, transient error rate, permanent errors (invalid number) and a per-second quota that returns `429`.
5. Retries with exponential backoff and full jitter up to 4 attempts, then a dead-letter queue with the last error; a circuit breaker per provider.
6. `GET /notifications/{id}` returns the state history (accepted, queued, attempt *n*, sent, delivered, failed, suppressed) with timestamps and reasons.

**Non-functional requirements.**

**Table 93.18 — Notification service: targets (one machine, fake providers).**

| Property | Target | How you verify it |
|---|---|---|
| Acceptance | `POST` p99 ≤ 50 ms at 200 requests/s; 0 accepted requests lost on `kill -9` | Load test and crash test |
| OTP latency during a campaign | p99 ≤ 5 s from acceptance to provider acceptance while a 100,000-recipient campaign runs | Mixed load test |
| Campaign throughput | 100,000 marketing sends within 10 min with the SMS provider capped at 200/s | Campaign test |
| Duplicates | ≤ 1 duplicate provider send per 100,000 under retries and worker crashes | Provider-side counter keyed by notification ID |
| Opt-out freshness | An opt-out stops all not-yet-sent notifications within 60 s | Opt-out during a campaign |
| Accounting | Every accepted notification ends in exactly one terminal state with a reason | Reconciliation query |

#### Architecture

**Figure 93.9 — Notification service: acceptance, prioritized delivery and retries.**

```mermaid
flowchart LR
  SVC([Calling service]) -->|POST /notifications| API[Notification API]
  API -->|insert with idempotency key| DB[(Notification store)]
  API -.->|enqueue by priority| QH[[Critical queue]]
  API -.->|enqueue by priority| QL[[Marketing queue]]
  QH -.-> W[Channel workers]
  QL -.-> W
  W -->|check| PREF[(Preferences)]
  W -->|send, quota-limited| PRV{{Fake SMS, e-mail, push}}
  W -.->|retry with backoff| RQ[[Delayed retry queue]]
  RQ -.-> W
  W -.->|after 4 attempts| DLQ[[Dead-letter queue]]
  W -->|state transitions| DB
  PRV -.->|delivery callback| API
```

**Reading the diagram.** The calling service makes one synchronous request; the API stores the notification with its idempotency key and returns `202`, so a retry of the same request finds the stored row and enqueues nothing new. Everything after acceptance is asynchronous (dotted). The API enqueues the notification on a queue chosen by priority; channel workers drain the critical queue before the marketing queue and hold a separate quota for marketing. For each notification, a worker re-checks preferences at send time (an opt-out that arrived after acceptance must still win), renders the template and calls the fake provider through a rate limiter. Transient failures go to a delayed retry queue with exponential backoff and jitter; after four attempts the notification moves to the dead-letter queue. Every transition is recorded in the notification store, which is the storage boundary and the source of truth for accounting; provider delivery callbacks update it later. Failure points: the provider (outage, throttling, slow responses), workers crashing between a successful send and recording it (the source of duplicates), and a campaign filling the queues. Scaling: more workers per channel up to the provider's quota, partitioned queues, and per-tenant quotas so that one sender cannot starve others (§52.7.12).

#### Milestones

1. **Accept durably.** Build the API on the §93.1.1 scaffolding with the notification store in SQLite and the queues from §93.2.1. *Done when:* the acceptance target holds and a retried `POST` with the same key returns the same notification ID.
2. **Deliver with priorities and quotas.** Build workers, fake providers and per-channel limiters; implement priority queues and a marketing quota. *Done when:* the OTP-latency and campaign-throughput targets hold simultaneously.
3. **Retries, circuit breakers and dead letters.** *Done when:* with a provider error rate of 20%, every notification ends in a terminal state; with a 60 s provider outage, the circuit breaker opens, nothing is lost, and the backlog drains after recovery.
4. **Preferences and deduplication.** Implement opt-outs, quiet hours, frequency caps and send-time preference checks; make workers record "sending" before calling the provider and pass the notification ID to the provider as an idempotency key (your fake provider honors it; check whether a real provider offers one before relying on it). *Done when:* the opt-out and duplicate targets hold with workers killed at random.
5. **Tracking and reconciliation.** Add the state history endpoint, provider callbacks and a reconciliation job that finds notifications stuck in a non-terminal state for more than 10 minutes. *Done when:* the accounting target holds after a run with crashes and outages.

#### Starter code

The starter compresses the pipeline into one function with simulated time: it deduplicates by idempotency key, applies opt-outs (OTPs bypass marketing opt-outs because they are security messages), schedules by priority under a provider quota of 20 sends per second, retries failures with exponential backoff and full jitter, and dead-letters after four attempts. A 400-recipient campaign arrives first; 20 OTPs arrive 2–4 s later, plus one duplicate client retry.

```python
"""Notification service core: deduplication by idempotency key, preference checks,
priority scheduling, a flaky fake provider, retries with exponential backoff and
jitter, and a dead-letter list. Simulated time; fixed seed (starter)."""
import heapq, random
from collections import Counter

rng = random.Random(5)
OPTED_OUT = {("u3", "sms")}                         # (user, channel) preferences
PRIORITY = {"otp": 0, "order": 1, "marketing": 2}  # lower number = served first
MAX_ATTEMPTS, SENDS_PER_SECOND = 4, 20             # provider quota per channel

def provider_send(note):                            # fake SMS provider: 20% transient errors
    return rng.random() > 0.20

def run(requests):
    seen, status, queue = set(), Counter(), []      # queue: (ready_at, priority, seq, note)
    first_seen, done_at, seq = {}, {}, 0
    for t, note in requests:                        # 1) accept: dedupe and check preferences
        if note["key"] in seen:
            status["duplicate suppressed"] += 1; continue
        seen.add(note["key"])
        if (note["user"], note["channel"]) in OPTED_OUT and note["kind"] != "otp":
            status["suppressed (opted out)"] += 1; continue
        note["attempts"] = 0
        first_seen[note["key"]] = t
        heapq.heappush(queue, (t, PRIORITY[note["kind"]], seq := seq + 1, note))
    now = 0.0
    while queue:                                    # 2) dispatch, one tick per second
        now = max(now, queue[0][0])
        batch = []
        while queue and queue[0][0] <= now:         # everything that is due now
            batch.append(heapq.heappop(queue))
        batch.sort(key=lambda item: (item[1], item[0]))   # priority first, then age
        for item in batch[SENDS_PER_SECOND:]:       # over the provider quota: next second
            heapq.heappush(queue, (now + 1.0,) + item[1:])
        for _, prio, s, note in batch[:SENDS_PER_SECOND]:
            note["attempts"] += 1
            if provider_send(note):
                status["sent"] += 1; done_at[note["key"]] = now
            elif note["attempts"] >= MAX_ATTEMPTS:
                status["dead-lettered"] += 1
            else:                                   # exponential backoff with full jitter
                delay = rng.uniform(0, 0.5 * 2 ** note["attempts"])
                heapq.heappush(queue, (now + delay, prio, s, note))
        now += 1.0
    return status, first_seen, done_at

if __name__ == "__main__":
    reqs = [(0.0, {"key": f"mkt-{i}", "user": f"u{i % 50}", "channel": "sms", "kind": "marketing"})
            for i in range(400)]                    # a campaign of 400 arrives first
    reqs += [(2.0 + i * 0.1, {"key": f"otp-{i}", "user": f"u{i}", "channel": "sms", "kind": "otp"})
             for i in range(20)]                    # then 20 one-time passwords
    reqs += [(3.0, dict(reqs[-1][1]))]              # a client retry of the last OTP request
    status, first, done = run(reqs)
    for k, v in sorted(status.items()):
        print(f"{k:<24}{v}")
    for kind in ("otp", "mkt"):
        lat = sorted(done[k] - first[k] for k in done if k.startswith(kind))
        print(f"{kind}: delivered {len(lat)}, median {lat[len(lat) // 2]:.1f} s, max {lat[-1]:.1f} s")
```

Output:

```text
dead-lettered           1
duplicate suppressed    1
sent                    411
suppressed (opted out)  8
otp: delivered 20, median 0.7 s, max 3.0 s
mkt: delivered 391, median 13.0 s, max 26.0 s
```

What to notice:

- Even though the campaign arrived first and fills the queue, OTPs are delivered with a median of 0.7 s: each second, due items are sorted by priority before the quota is applied. Without that sort, an OTP arriving at $t$ = 2 s would wait behind about 360 marketing messages, 18 s at 20 per second.
- The slowest OTP took 3.0 s because a 20% transient error rate forces some to retry, and each retry waits a random backoff. The p99 target of 5 s therefore depends on the retry policy as much as on the queue; compute the worst case for four attempts before accepting it.
- The duplicate OTP request was suppressed at acceptance. This protects against client retries only. A worker that crashes after the provider accepted a message but before recording it will send again on redelivery; Milestone 4's provider-side idempotency key is what closes that gap.
- Eight marketing messages to user `u3` were suppressed because of the SMS opt-out, and the outcome is counted, not silently dropped: every request ends in one of four terminal states (sent, suppressed, duplicate, dead-lettered), which is the accounting property in Table 93.18.
- Marketing messages took up to 26 s. At the quota of 20 per second, 392 campaign messages need at least $392 / 20 = 19.6$ s; OTPs, retries and backoff explain the rest.

::: example
**Worked example — Can the campaign finish on time without hurting OTPs?**

*Assumptions.* The milestone's campaign: 100,000 SMS within 10 minutes; SMS provider quota 200 sends/s; transient error rate 5% with up to 4 attempts; OTP traffic at most 10/s.

1. Required campaign rate: $100{,}000 / 600 = 167$ sends/s.
2. Retries add about 5% more attempts: $167 \times 1.05 = 175$ attempts/s (second retries add $167 \times 0.05^2 \approx 0.4$/s more, negligible).
3. Reserve OTP capacity: $200 - 10 = 190$ attempts/s are left for the campaign, enough for 175 with 15/s of headroom (8% of the quota).
4. If the error rate jumps to 30% during a provider incident, attempts grow to about $167 \times (1 + 0.3 + 0.09 + 0.027) = 237$/s, over the 190 available, and the campaign falls behind while OTPs, served first, are unaffected.

*Interpretation.* The campaign target is feasible with little headroom; a provider incident delays marketing, which is the correct casualty. *Engineering implication.* Give marketing a quota below the provider limit and reserve the rest for critical traffic, and let the circuit breaker slow the campaign rather than spend quota on retries.
:::

#### Test plan and load-test targets

Unit tests cover idempotent acceptance (same key and body → same ID; same key, different body → `422`), preference evaluation with time zones and daylight-saving transitions, frequency caps, backoff bounds and terminal-state transitions. The mixed load test runs a 100,000-recipient campaign and 10 OTPs per second simultaneously for 10 minutes, recording OTP latency per second; the fake provider counts sends per notification ID to detect duplicates. A reconciliation query after every test checks that the count of accepted notifications equals the sum of terminal states.

#### Failure-injection exercises

1. **Provider outage.** Make the SMS provider return `503` for 60 s. Verify that the circuit breaker opens, OTPs are failed over to a second fake provider (or to push), and marketing waits.
2. **Throttling.** Lower the provider quota below the campaign's needs and make the provider return `429` with `Retry-After`. Your workers must slow down, not retry harder.
3. **Worker crash after send.** Kill a worker right after the provider accepts a message. Count duplicates with and without the provider-side idempotency key.
4. **Opt-out mid-campaign.** Opt out 1,000 campaign recipients halfway through and verify that none of their remaining messages is sent after 60 s.
5. **Poison template.** Add a template that fails to render for one user's data. It must be dead-lettered with the rendering error, not retried four times against the provider.

#### Extensions

- Add digesting: group several low-priority notifications to the same user within 15 minutes into one message.
- Add per-tenant fairness so that one calling service's campaign cannot delay another's transactional mail (§47).
- Add delivery-status webhooks back to calling services with signed payloads and retries (§10.4.6).
- Add a send-time optimization model (Ch 92, Q21 frames it as an ML problem) behind a simple interface.

#### Self-assessment rubric

**Table 93.19 — Notification service: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Acceptance | Requests accepted | Durable, idempotent `202`; crash test passes | You can explain why acceptance is synchronous and delivery is not |
| Priorities and quotas | One queue | Priority isolation and marketing quota; OTP target met during a campaign | You can size quotas from provider limits and error rates |
| Reliability | Retries | Backoff with jitter, circuit breaker, dead letters, reconciliation | You can explain where duplicates come from and how each is prevented |
| Preferences | Opt-outs checked once | Send-time checks, quiet hours, frequency caps; opt-out freshness met | You can discuss the consistency requirement of preferences |
| Observability | Logs | State history per notification; lag and dead-letter metrics | You can debug a "user never got the code" report from your data |

### 93.2.5 Real-time chat

#### Goal and learning outcomes

Build a chat service with one-to-one and group conversations, live delivery over persistent connections, per-message states (sent, delivered, read) and gap-free history sync when a device reconnects. Chapter 9 teaches the real-time techniques and §53.4 designs a chat system for hundreds of millions of users. Your version runs two or three gateway processes on one machine, which is enough to meet every core problem: who orders messages, how a message finds a user connected to another gateway, what happens to messages sent while a user is offline, and how a client knows it has missed nothing.

After this project you should be able to:

- Serve thousands of persistent connections from an `asyncio` gateway and measure memory per connection (§9.9.1–9.9.2).
- Assign a total order per conversation on the server and use it for deduplication, gap detection and sync (§53.4).
- Route messages between gateways through a registry and a publish/subscribe backplane (§9.9.3).
- Implement presence with heartbeats, and survive a reconnect storm with jittered backoff (§9.9.5–9.9.6).
- Upgrade the transport to WebSockets and explain the handshake, framing and heartbeat (§9.6).

#### Prerequisites

- Polling, long polling, Server-Sent Events and WebSockets — §9.3–9.6; connection management at scale — §9.9; mobile push for offline users — §9.8.
- The chat case study — §53.4, especially its ordering and sync requirements.
- Delivery guarantees and idempotent receivers — §30.8, §32.10.
- The message queue (§93.2.1) as the backplane, or Redis publish/subscribe in Docker.

#### Specification

**Functional requirements.**

1. Clients connect, authenticate with a token, and send `hello` with the last sequence number they hold for each conversation; the server replays everything after it.
2. `send(conversation, text, client_msg_id)`: the server assigns the next sequence number in that conversation, stores the message durably, acknowledges with the sequence number, and delivers it to every online member device. Retries with the same `client_msg_id` return the original sequence number.
3. Delivered and read receipts flow back to the sender; unread counts per conversation are maintained.
4. Several gateway processes: a registry maps users to gateways, and a backplane carries messages between gateways.
5. Presence: online, or last seen; heartbeats every 30 s; offline after 2 missed heartbeats. Typing indicators are sent but never stored.
6. Offline members get a (fake) push notification instead of live delivery.
7. Milestone 5 moves the transport to WebSockets (the `websockets` package, or your own RFC 6455 handshake and framing).

**Non-functional requirements.**

**Table 93.20 — Real-time chat: targets (two gateways, one store, one machine).**

| Property | Target | How you verify it |
|---|---|---|
| End-to-end latency | p99 ≤ 100 ms from send to recipient delivery across gateways, at 500 messages/s | Timestamps in messages |
| Connections | 10,000 concurrent idle connections per gateway; memory per connection measured | Connection test with a load client |
| Ordering | Every device sees each conversation in the same order with no gaps, over 1 million messages | Per-device sequence check |
| No loss | 0 acknowledged messages missing after gateway or store restarts | Sender log versus history |
| Sync | 1,000 missed messages synced in ≤ 2 s after reconnect | Reconnect test |
| Reconnect storm | After a gateway restart, 10,000 clients reconnect within 60 s without overloading the survivor | Jittered reconnect test |

#### Architecture

**Figure 93.10 — Real-time chat: gateways, registry, backplane and message store.**

```mermaid
flowchart LR
  A([Alice device]) <-->|WebSocket| G1[Gateway 1]
  B([Bob device]) <-->|WebSocket| G2[Gateway 2]
  G1 -->|send: assign seq, store| MS["Message service"]
  MS --> ST[(Message store<br/>by conversation, seq)]
  MS -->|look up members| REG[(Registry: user to gateway)]
  MS -.->|publish to gateway 2| BP[[Backplane pub/sub]]
  BP -.-> G2
  MS -.->|offline member| PUSH{{Fake push provider}}
  G1 -.->|heartbeats| PRES[(Presence)]
```

**Reading the diagram.** Each device holds one long-lived, bidirectional connection to a gateway (WebSocket in the final version). When Alice sends a message, gateway 1 passes it synchronously to the message service, which assigns the next sequence number for the conversation, stores the message in the message store keyed by (conversation, sequence) and returns the acknowledgment through gateway 1. The service then looks up the other members in the registry: for members on another gateway, it publishes the message to that gateway's channel on the backplane (dotted, asynchronous); gateway 2 pushes it down Bob's connection. Members with no live connection get a push notification and will sync on reconnect. Gateways also record heartbeats in the presence store. Storage boundaries are the message store (durable, the source of truth), the registry and presence (soft state, rebuilt from connections) and the backplane (transient). Failure points: a gateway crash drops all its connections at once (reconnect storm); a backplane message can be lost, which the sequence numbers expose as a gap that the client repairs by syncing; and the message service is the ordering point per conversation, so it must be partitioned by conversation, not replicated without coordination. Scaling: more gateways for connections, message service partitioned by conversation ID, and fan-out work proportional to group size (§53.4).

#### Milestones

1. **Single gateway with durable history.** Extend the starter with authentication, SQLite storage keyed by (conversation, seq), receipts and unread counts. *Done when:* the ordering and no-loss checks pass across server restarts, with a client simulator of 100 users.
2. **Multiple gateways.** Run two gateways, a registry and a backplane (your §93.2.1 broker or Redis pub/sub). *Done when:* cross-gateway latency meets the target, and dropping 1% of backplane messages produces gaps that clients detect and repair by syncing, with zero missing messages at the end.
3. **Presence and offline delivery.** Add heartbeats, last-seen, typing indicators and fake push for offline members. *Done when:* presence changes within 60 s of a client vanishing without closing its connection, and offline members receive one push per conversation burst, not one per message.
4. **Scale and storms.** Use a load client to open 10,000 connections per gateway and measure memory; kill a gateway and have its clients reconnect with exponential backoff and full jitter. *Done when:* the connection and reconnect-storm targets hold, and your results log shows the reconnect rate per second with and without jitter.
5. **WebSockets.** Replace newline-delimited JSON with WebSockets, including ping/pong heartbeats and close frames (§9.6.2–9.6.5); optionally add a browser client. *Done when:* every earlier test passes over WebSockets, and you can explain each field of the handshake.

#### Starter code

The starter runs a server and two clients in one `asyncio` process over TCP with newline-delimited JSON. It assigns sequence numbers per conversation, fans out to online members, deduplicates a retried send, and syncs a client that reconnects with its last seen sequence number.

```python
"""Real-time chat core: an asyncio server with persistent connections, per-conversation
sequence numbers, fan-out to online members, deduplication of client retries, and
gap-free sync on reconnect. Newline-delimited JSON over TCP (starter)."""
import asyncio, json

MEMBERS = {"c1": {"alice", "bob"}}
history = {"c1": []}                       # conversation -> list of messages (seq = index + 1)
online, seen_ids = {}, {}                  # user -> writer; client_msg_id -> seq

async def handle(reader, writer):
    hello = json.loads(await reader.readline())
    user = hello["user"]
    online[user] = writer
    for conv, last in hello["last_seq"].items():          # sync: everything after last seen
        for m in history[conv][last:]:
            writer.write((json.dumps({"op": "msg", **m}) + "\n").encode())
    while line := await reader.readline():
        req = json.loads(line)
        conv = req["conv"]
        if req["client_msg_id"] in seen_ids:               # retry: ack again, store nothing
            seq = seen_ids[req["client_msg_id"]]
        else:
            seq = len(history[conv]) + 1                   # the server orders the conversation
            m = {"conv": conv, "seq": seq, "from": user, "text": req["text"]}
            history[conv].append(m)
            seen_ids[req["client_msg_id"]] = seq
            for member in MEMBERS[conv] - {user}:          # fan out to online members
                if member in online:
                    online[member].write((json.dumps({"op": "msg", **m}) + "\n").encode())
        writer.write((json.dumps({"op": "ack", "client_msg_id": req["client_msg_id"],
                                  "seq": seq}) + "\n").encode())
    del online[user]

class Client:
    def __init__(self, user):
        self.user, self.last_seq = user, {"c1": 0}

    async def connect(self, port):
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", port)
        self.writer.write((json.dumps({"user": self.user, "last_seq": self.last_seq}) + "\n").encode())
        self.task = asyncio.create_task(self.listen())

    async def listen(self):
        while line := await self.reader.readline():
            ev = json.loads(line)
            if ev["op"] == "msg" and ev["seq"] > self.last_seq[ev["conv"]]:
                self.last_seq[ev["conv"]] = ev["seq"]
                print(f"  {self.user} <- #{ev['seq']} {ev['from']}: {ev['text']}")
            elif ev["op"] == "ack":
                print(f"  {self.user} ack {ev['client_msg_id']} -> seq {ev['seq']}")

    async def send(self, text, msg_id):
        self.writer.write((json.dumps({"conv": "c1", "text": text, "client_msg_id": msg_id}) + "\n").encode())
        await asyncio.sleep(0.05)

    async def close(self):
        self.writer.close(); await asyncio.sleep(0.05)

async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    alice, bob = Client("alice"), Client("bob")
    await alice.connect(port); await bob.connect(port); await asyncio.sleep(0.05)
    await alice.send("lunch?", "a-1")
    await bob.send("sure, 12:30", "b-1")
    print("bob goes offline")
    await bob.close()
    await alice.send("see you there", "a-2")
    await alice.send("see you there", "a-2")             # retry after a lost ack
    print("bob reconnects with last_seq", bob.last_seq)
    await bob.connect(port); await asyncio.sleep(0.05)
    print("history length:", len(history["c1"]))
    await alice.close(); await bob.close()
    server.close()

asyncio.run(main())
```

Output:

```text
  bob <- #1 alice: lunch?
  alice ack a-1 -> seq 1
  alice <- #2 bob: sure, 12:30
  bob ack b-1 -> seq 2
bob goes offline
  alice ack a-2 -> seq 3
  alice ack a-2 -> seq 3
bob reconnects with last_seq {'c1': 1}
  bob <- #2 bob: sure, 12:30
  bob <- #3 alice: see you there
history length: 3
```

What to notice:

- The server, not the client, assigns `seq`, so both devices agree on the conversation's order even if two members send at the same instant. Client timestamps would disagree across devices with skewed clocks (§24.9).
- Alice's retry of `a-2` was acknowledged with the same `seq` 3 and stored once. A client that retries after a lost acknowledgment must reuse the same `client_msg_id`; generating a new one creates a duplicate message that the server cannot recognize.
- Bob reconnected with `last_seq` 1 and received everything after it in order: one indexed range read per conversation, which is the sync requirement of §53.4. A client that sees `seq` jump from 3 to 5 knows that it missed 4 and asks for it.
- Bob also received his own message `#2` again, because his cursor advances only on incoming messages, not on acknowledgments. That is harmless (he discards anything at or below his cursor), but it wastes bandwidth; advance the cursor on acknowledgment when no gap precedes it.
- Assigning `seq` as `len(history) + 1` works only because one process owns the conversation. With several gateways, the message service partition that owns the conversation must assign it, or two gateways will hand out the same number.

::: example
**Worked example — Fan-out load from group chats.**

*Assumptions.* 2,000 active groups of 50 members each; each group sends 1 message every 10 s on average; 60% of members are online.

1. Messages sent: $2{,}000 / 10 = 200$ per second.
2. Deliveries attempted: $200 \times 49 = 9{,}800$ per second (every member except the sender).
3. Live deliveries: $9{,}800 \times 0.6 = 5{,}880$ per second over connections; the remaining $3{,}920$ per second are offline, collapsed into far fewer push notifications by batching per conversation.
4. With members spread evenly over two gateways, about half of the live deliveries, $2{,}940$ per second, cross the backplane.

*Interpretation.* A modest 200 messages per second becomes almost 10,000 delivery operations per second: fan-out, not message intake, sizes the gateways and the backplane. *Engineering implication.* Load-test with realistic group sizes, and publish one backplane message per destination gateway rather than one per recipient.
:::

#### Test plan and load-test targets

Unit tests cover sequence assignment, deduplication, sync ranges (empty, partial, beyond the end), receipts and unread-count arithmetic. A client simulator runs hundreds of users with scripted conversations, random disconnects and retries; every device checks that each conversation it holds has contiguous sequence numbers and identical content to the store. Load tests open 10,000 connections per gateway (raise the process's file-descriptor limit with `ulimit -n`) and send 500 messages per second across 1,000 conversations with a mix of one-to-one and 50-member groups.

#### Failure-injection exercises

1. **Gateway crash.** Kill a gateway with 5,000 connected clients. Measure how long until all are reconnected, with and without jitter, and verify that no acknowledged message is lost.
2. **Backplane loss.** Drop 1% of backplane messages. Clients must detect gaps and sync; count gap repairs.
3. **Half-open connections.** Make clients disappear without closing their sockets (suspend the process). Only heartbeats reveal this; measure detection time and its effect on presence.
4. **Slow consumer.** A client that reads slowly makes the gateway's send buffer grow. Bound it, and disconnect the client when the bound is reached so that one slow phone cannot exhaust gateway memory (§9.6.7).
5. **Store slowdown.** Delay the message store by 200 ms. Senders' acknowledgments slow down; decide whether to deliver to recipients before the store confirms (faster, but a message could appear and then vanish) and defend the choice.

#### Extensions

- End-to-end encryption with per-device keys, so that the server stores only ciphertext (§53.5 discusses the design).
- Message search over each user's history with an inverted index (§16).
- Attachments through presigned upload URLs to a local object store such as MinIO in Docker (§15).
- Rolling deploys with graceful connection draining (§9.9.7).

#### Self-assessment rubric

**Table 93.21 — Real-time chat: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Ordering and sync | Messages delivered live | Per-conversation `seq`, dedup, gap detection and sync; checks pass over 1 million messages | You can explain why the order is per conversation and who assigns it |
| Multi-gateway routing | One gateway | Registry and backplane; cross-gateway latency target met | You can explain the routing path and what happens when the backplane loses a message |
| Connections | A few clients | 10,000 connections, memory measured, storms survived with jitter | You can size a gateway fleet from your memory-per-connection figure |
| Presence and offline | Online flag | Heartbeats, last seen, push batching | You can explain why presence is approximate by design |
| Transport | Line-delimited JSON | WebSockets with heartbeats and close handling | You can compare WebSockets, SSE and long polling for this product (§9.10) |

