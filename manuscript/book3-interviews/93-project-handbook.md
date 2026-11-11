# Chapter 93 — Project Handbook

> **Level:** 1–5 · **Track:** Shared · **Estimated reading time:** 8 h (building the projects: 10–100 h each)

Reading about a write-ahead log and writing one are different experiences. When you write it, you discover that a torn record at the end of the file is a normal event, that `fsync` costs milliseconds, and that "the follower is a little behind" means something very specific when the primary dies. This chapter turns the book into twenty build projects, arranged in four levels, so that you can have those discoveries on your own laptop rather than in production or in an interview.

Each project is a scaled-down version of a system that the book designs at full size. The URL shortener of §52.4 handles 280,000 redirects per second across a fleet; your version handles a few thousand per second on one machine. The mechanisms are the same: a code generator that never collides, a cache in front of a store, an asynchronous click path. What you lose in scale you gain in visibility. You can kill any process, delay any message and read every byte on disk, and you can measure what happens.

**How to use the projects.** Pick a level that matches what you already know, read the project's prerequisites, and skim the owning chapter sections before you start. Then work through the milestones in order. Each milestone ends with a **done when** statement: a check you can run, not a feeling. Do not move on until it passes. Keep two files next to your code from the first day: a one-page design document (requirements, the architecture figure redrawn in your own words, the decisions you made and why), and a results log in which every measurement is recorded with the hardware, Python version, command line and date. The results log is what turns a toy into evidence. When an interviewer asks "how do you know?", you will have an answer (§93.7 shows how to talk about a project in an interview).

The starter code in each project is deliberately small: a runnable core of 60–120 lines that demonstrates the central mechanism and prints its result. It is not a solution. The milestones ask you to replace almost all of it. Every starter was run with Python 3.13 on Linux, and its printed output is quoted below it. Where a starter uses randomness, it fixes the seed, so you should see exactly the same output.

::: note
**Tooling assumptions for every project in this chapter.**

- **Language.** Python 3.11 or later, standard library first (`http.server`, `asyncio`, `socket`, `sqlite3`, `threading`, `heapq`, `hashlib`, `unittest`). Where a third-party package makes a milestone much easier (an HTTP client for load tests, a WebSocket library, a Prometheus client), the milestone says so and the package is optional. You may port any project to Go, Java or Rust once the Python version works; the measurements then change, and that comparison is itself instructive (§23.9).
- **Containers.** Docker is optional. It is useful for running a real Redis, PostgreSQL or Kafka next to your own implementation for comparison, and for running several copies of a node with separate network namespaces (§42.3). Nothing in Part A requires it.
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

Beginner projects take roughly 10–20 hours each and Intermediate projects 20–40 hours. They build on each other: the rate limiter reuses the cache's TTL logic, the notification service sits on top of the message queue, and the chat server reuses the REST service's operational scaffolding. If you only have time for four projects in Part A, build the REST API service, the Redis-style cache, the message queue and the distributed key-value store; together they exercise almost every Book I chapter that interviews probe.

## 93.1 Beginner

The five Beginner projects are single-process or single-machine systems. Each one isolates one idea that every larger design depends on: a well-behaved API, a collision-free identifier, a cache with expiry and eviction, admission control, and traffic distribution under failure. None needs consensus or replication, which keeps your attention on getting the mechanism right and measuring it.

### 93.1.1 REST API service

#### Goal and learning outcomes

Build a small task-tracking API (`/tasks`) that behaves like a production service: correct status codes, validated input, stable pagination, safe retries, durable writes, structured logs and metrics, and a measured capacity. The domain is deliberately boring so that every hour goes into the properties that make an API trustworthy. Almost every later project in this chapter exposes an HTTP interface, and they all reuse what you build here.

After this project you should be able to:

- Design resource URIs, methods and status codes that follow HTTP semantics, and explain which methods are safe and idempotent (§8.6.3).
- Implement cursor pagination that stays correct while rows are being inserted, and explain why offset pagination does not (§8.6.5).
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

**Reading the diagram.** Clients (your load generator and ad-hoc `curl` calls) send synchronous HTTP/1.1 requests to a single API process. Inside it, every request first passes through middleware that assigns a request ID, rejects oversized bodies, starts a deadline timer and records a latency observation; the router then dispatches to a handler. Handlers never touch SQL directly: they call a repository, which keeps storage concerns in one place and lets you swap SQLite for PostgreSQL later. The idempotency store lives in the same SQLite file and, crucially, is written in the **same transaction** as the task it protects, so a crash can never leave a task without its idempotency record or vice versa. The storage boundary is the SQLite file in write-ahead-log mode (§13.5); everything above it is stateless and could be replicated behind a load balancer. The dotted arrow to the log file is asynchronous from the request's point of view: logging must never fail a request. Prometheus, if you run it in Docker, pulls metrics (§40.8.1). Failure points to study: the database (locked, slow or full disk), the process (killed mid-request) and the client (retrying after a timeout). Scaling: run several API processes behind the load balancer of §93.1.5; the single SQLite writer then becomes the bottleneck, which is the motivation for a client–server database.

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
- `id = len(TASKS) + 1` is a bug waiting for `DELETE`: after a deletion it reissues an existing ID. SQLite's `INTEGER PRIMARY KEY` fixes this in Milestone 2.

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
5. **Malicious input.** Send a 10 MB body, a body that claims `Content-Length: 1000000` but sends 10 bytes, deeply nested JSON and a title containing SQL metacharacters. None should crash the process or leak a stack trace.

#### Extensions

- Add bearer-token authentication with signed JSON Web Tokens and per-user task ownership (§8.11, §8.13); return `404`, not `403`, for other users' tasks so that IDs cannot be probed.
- Replace SQLite with PostgreSQL in Docker, add a connection pool, and repeat the capacity report; explain the change in the knee (§14.13.1).
- Add `ETag`-based conditional `GET` (`If-None-Match` → `304`) and measure bandwidth saved.
- Run three instances behind the load balancer of §93.1.5 and confirm that idempotency still holds when a retry lands on a different instance.
- Add OpenTelemetry tracing and follow one slow request from middleware to SQL (§40.6–40.7).

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
- Defend the design in an interview with your own measured numbers.

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
5. **Hot link.** Replay a trace in which one link receives 50% of all traffic. Confirm it stays cached, and measure whether the single lock around your LRU structure becomes a bottleneck with many threads (§20.15).

#### Extensions

- Add a shared Redis (Docker) between the in-process cache and SQLite, and measure the latency of each tier.
- Replace LRU with a W-TinyLFU admission filter and compare hit ratios on the same trace (§20.9.3).
- Record approximate unique visitors per link with HyperLogLog (§17.5) and compare its error with exact counting.
- Add a negative cache or a Bloom filter for unknown codes and measure store reads under a scan of random codes (§17.4).
- Re-check stored destinations against an updated blocklist in a background job and disable matches, as §52.4.11 describes.

#### Self-assessment rubric

**Table 93.5 — URL shortener: self-assessment rubric.**

| Dimension | 1 — Working | 2 — Solid | 3 — Interview-ready |
|---|---|---|---|
| Code generation | Random codes with retry | Leased blocks + keyed permutation; 10 million unique codes; parallel processes never collide | You can compare all five schemes of Table 52.3 with your collision and enumeration measurements |
| Redirect path | Redirect works | Cache-aside with eviction; hit-ratio target met; store outage degrades gracefully | You can explain `301` versus `302` for caching and analytics, and cache penetration with a fix |
| Invalidation | Delete removes the row | Disabled links stop within 5 s on every instance | You can state the staleness bound of your approach and its cost |
| Analytics | Counts update | File-backed log, offset in the same transaction, exact counts after crashes | You can explain why redirect latency is unaffected by aggregator failure, with data |
| Capacity | One load test | Hits and misses measured separately at target rates | You scale your numbers to §52.4.4 and identify what changes at 280,000 RPS |

