## 93.3 Advanced projects

The five advanced projects move from "one service that works" to "several processes that must agree while some of them fail." Each one is built around a single mechanism that interviewers probe again and again: leases and fencing tokens (job scheduler), the transactional outbox and sagas (event-driven microservices), event-time windows and watermarks (real-time analytics), two-tower retrieval with a sampling correction (recommendation engine) and dynamic batching with admission control (distributed ML inference). The starter code isolates that mechanism in under a hundred lines so you can see it work and break before you wrap it in HTTP servers, containers and dashboards.

All five assume the beginner and intermediate projects in §93.1–§93.2 or equivalent experience: you can build a REST service, run several processes locally, write a load generator and read a p99. Each project is sized for roughly 25–40 hours. Numbers attached to QuickBite are the Book II assumptions; laptop targets are deliberately modest so they can be met on a four-core machine without a GPU.

### 93.3.1 Distributed job scheduler

**Level:** 3 · **Effort:** about 25–35 hours · **Related:** leases §26.11, fencing tokens §26.13, workflow engines §32.11, cluster scheduling Ch 46, practice question Ch 91 Q40

#### Goal and learning outcomes

QuickBite runs thousands of jobs that must happen *at a time* rather than *in response to a request*: restaurant payout batches at 02:00, menu syncs every 15 minutes, "your order is late" checks five minutes after a promised time, nightly retraining triggers for the ETA model. A single cron daemon is a single point of failure; two cron daemons run every job twice. You will build a scheduler that runs every job **at least once, close to its due time, on a pool of workers that may crash or pause at any moment**, and that makes the duplicates harmless.

After this project you should be able to:

- **Implement** a job store with atomic claims, time-bounded leases, heartbeats and monotonically increasing fencing tokens.
- **Explain** why a lease alone cannot prevent two workers acting on the same job, and show with a test how a fencing token and an idempotent effect close the gap.
- **Design** retry with exponential backoff, a maximum attempt count and a dead-letter state, and choose the lease duration from the heartbeat interval.
- **Measure** firing delay (actual start minus due time) and takeover time after a worker crash, and state both as p99 targets.

#### Prerequisites

- Leases and the clock assumptions behind them — §26.11; fencing tokens — §26.13. This project is those two sections turned into code.
- Visibility timeouts and dead-letter queues — §30.4.2 and §30.11. A leased job is the same idea as an in-flight message.
- Idempotency keys — §22.15. The only reliable defense against the duplicates the scheduler will produce.
- Durable execution and workflow engines — §32.11, to see what you are *not* building (multi-step workflows with saved state).
- Scheduling vocabulary (jobs, tasks, priorities, quota) — §46.3 and §46.8.

#### Specification

**Functional requirements.**

1. `POST /jobs` creates a one-off job (`run_at`, `payload`, `max_attempts`, `idempotency_key`) or a recurring job (`cron` expression, time zone). Creating the same `idempotency_key` twice returns the first job.
2. Workers call `claim(worker_id, n)` to lease up to $n$ due jobs, `heartbeat(job_id, fence)` to extend a lease, and `complete(job_id, fence, result)` or `fail(job_id, fence, error)` to finish one.
3. A failed run is retried after $b \cdot 2^{a-1}$ seconds (attempt $a$, base $b$) until `max_attempts`, after which the job moves to `DEAD` and raises an alert.
4. A recurring job materializes its next occurrence only when the current one is claimed, so a backlog never multiplies.
5. `GET /jobs/{id}` shows state, attempts, current fence, lease holder and history; `POST /jobs/{id}/cancel` and `/retry` exist for operators.

**Non-functional requirements (laptop scale).**

- **No lost jobs:** every due job reaches `DONE` or `DEAD`; verified by a reconciliation query after each test.
- **Firing delay:** p99 below 2 s with 10,000 jobs due in the same minute and 8 workers.
- **Takeover after a crash:** a crashed worker's job restarts within lease + one claim interval (10 s + 1 s).
- **Throughput:** 500 claims/s sustained against PostgreSQL or SQLite in WAL mode.
- **Duplicates:** permitted at the job level (at-least-once) but **zero duplicate side effects** at the sink, because effects are keyed by `job_id`.

::: formula
**Lease duration from heartbeats**

$$L \;\ge\; k \cdot h + d_{\max}$$

| Symbol | Meaning | Units |
|---|---|---|
| $L$ | Lease duration granted on claim and on each heartbeat | s |
| $h$ | Heartbeat interval used by workers | s |
| $k$ | Number of consecutive heartbeats you are willing to lose before takeover | count |
| $d_{\max}$ | Worst-case delay between a heartbeat being sent and the store recording it | s |
:::

::: example
**Worked example — sizing the lease for QuickBite's scheduler.** Heartbeats every $h = 3$ s; tolerate $k = 3$ lost heartbeats (a short network blip or a slow database); $d_{\max} = 1$ s.

1. $k \cdot h = 3 \times 3 = 9$ s.
2. $L \ge 9 + 1 = 10$ s, the value used in the starter code.
3. Worst-case takeover after a real crash: the lease can have up to 10 s left, plus one claim poll of 1 s, so about 11 s.

**Interpretation.** Halving the lease to 5 s halves takeover time but turns a single 6 s database hiccup into a false takeover and a duplicate run. **Engineering implication.** Choose $L$ from the heartbeat budget, then make duplicates cheap with fencing and idempotent effects rather than trying to make them impossible. The clock-drift margin of §26.11 adds only milliseconds here; pauses dominate.
:::

#### Architecture

**Figure 93.101 — Distributed job scheduler with leases and fencing tokens.**

```mermaid
flowchart LR
  C([Operator or service]) -->|HTTPS create job| API[Scheduler API]
  API -->|SQL insert| DB[(Job store<br/>jobs, attempts)]
  T[Recurrence planner] -->|materialize next run| DB
  W1[Worker 1] -->|claim, heartbeat, finish| DB
  W2[Worker 2] -->|claim, heartbeat, finish| DB
  W1 -->|write with fence| S{{Downstream sink}}
  W2 -->|write with fence| S
  R[Reaper and DLQ alerter] -->|scan expired and dead| DB
  R -.->|alert| O([On-call])
```

**Reading the diagram.** Clients create jobs through the **Scheduler API**, which inserts rows into the **job store** (PostgreSQL in production, SQLite for the first milestone); the store is the only source of truth, and every state change is a single conditional `UPDATE`. The **recurrence planner** turns cron expressions into concrete `run_at` rows, one occurrence ahead. **Workers** pull: they claim due rows with `SELECT … FOR UPDATE SKIP LOCKED` (or an equivalent compare-and-set), receive a lease and a fencing token, heartbeat while working and finish with the token. All of these calls are synchronous request/response (solid arrows). Workers write their effect to the **downstream sink** (a payout API, a table) carrying the fence, and the sink rejects writes older than the newest fence it has seen. The **reaper** scans for expired leases and dead jobs; its alerts are asynchronous (dotted). Failure points: a worker can crash (lease expires, job is re-claimed), pause (it becomes a zombie holding a stale fence) or lose its connection; the store itself is the availability bottleneck and is made highly available with a replica and automatic failover (§27). Scaling: partition jobs by `hash(job_id)` across store shards and give each worker pool a shard set, or move to a log-based design (Kafka topics per delay bucket) once one database cannot sustain the claim rate.

#### Milestones

1. **Single-node store and claim loop.** Implement `submit`, `claim`, `finish` and backoff on SQLite with one worker process. *Done when* 1,000 jobs with random `run_at` all reach `DONE` and the firing delay histogram is printed.
2. **Leases, heartbeats and takeover.** Add leases and a heartbeat thread; kill a worker with `SIGKILL` mid-job. *Done when* the job is re-claimed by another worker within 11 s, measured by the test.
3. **Fencing and idempotent effects.** Add fencing tokens and a sink that checks them; make the effect an upsert keyed by `job_id`. *Done when* the pause test in the starter code produces zero duplicate effects after the idempotent upsert.
4. **Recurring jobs and operator API.** Cron parsing with time zones, cancel, retry and a DLQ view. *Done when* a job scheduled for 02:30 local time behaves correctly across a daylight-saving transition in a unit test.
5. **Scale-out and observability.** Move to PostgreSQL with `SKIP LOCKED`, 8 workers and metrics for due-but-unclaimed jobs, firing delay, attempts and dead jobs. *Done when* the load test in the test plan meets its targets.

#### Starter code

The core is a job table with atomic claims and a worker simulation in logical time. Five percent of claims are followed by a 15 s stop-the-world pause, longer than the 10 s lease, so some workers wake up as zombies holding stale fences.

```python
import random

class JobStore:
    """Authoritative job table (stands in for Postgres or etcd). All methods are atomic."""
    def __init__(self, lease_s=10, max_attempts=4, backoff_s=2):
        self.jobs, self.fence = {}, 0
        self.lease_s, self.max_attempts, self.backoff_s = lease_s, max_attempts, backoff_s

    def submit(self, jid, run_at):
        self.jobs[jid] = dict(state="PENDING", run_at=run_at, attempts=0, fence=0, until=0)

    def claim(self, now):
        ready = [(j["run_at"], jid) for jid, j in self.jobs.items()
                 if (j["state"] == "PENDING" and j["run_at"] <= now)
                 or (j["state"] == "LEASED" and j["until"] <= now)]       # expired lease
        for _, jid in sorted(ready):
            j = self.jobs[jid]
            if j["attempts"] >= self.max_attempts:
                j["state"] = "DEAD"; continue                              # dead-letter
            self.fence += 1                                                # monotonic token
            j.update(state="LEASED", until=now + self.lease_s, fence=self.fence)
            j["attempts"] += 1
            return jid, self.fence
        return None

    def heartbeat(self, jid, fence, now):
        j = self.jobs[jid]
        if j["state"] == "LEASED" and j["fence"] == fence:
            j["until"] = now + self.lease_s
            return True
        return False                                                       # lease lost

    def finish(self, jid, fence, now, ok):
        j = self.jobs[jid]
        if j["state"] != "LEASED" or j["fence"] != fence:
            return "STALE"
        if ok:
            j["state"] = "DONE"
        else:
            j.update(state="PENDING", run_at=now + self.backoff_s * 2 ** (j["attempts"] - 1))
        return "OK"

class Sink:
    """Downstream resource that checks fencing tokens (e.g. a conditional write)."""
    def __init__(self):
        self.highest, self.effects, self.rejected = {}, 0, 0
    def write(self, jid, fence):
        if fence < self.highest.get(jid, 0):
            self.rejected += 1; return False
        self.highest[jid] = fence; self.effects += 1; return True

def simulate(n_jobs=300, n_workers=6, seed=7):
    rng = random.Random(seed)
    store, sink = JobStore(), Sink()
    for i in range(n_jobs):
        store.submit(f"job-{i:03d}", run_at=rng.randrange(0, 120))
    workers = [dict(job=None, busy_until=0, paused_until=0) for _ in range(n_workers)]
    stale = 0
    for now in range(0, 400):
        for w in workers:
            if w["paused_until"] > now:                    # stop-the-world pause: no heartbeats
                continue
            if w["job"] is None:
                got = store.claim(now)
                if got:
                    w["job"], w["busy_until"] = got, now + rng.randint(2, 6)
                    if rng.random() < 0.05:                # 5%: long pause > lease
                        w["paused_until"] = now + 15
                continue
            jid, fence = w["job"]
            if now < w["busy_until"]:
                store.heartbeat(jid, fence, now); continue
            ok = rng.random() > 0.15                       # 15% of runs fail
            if ok:
                sink.write(jid, fence)                     # side effect guarded by fence
            if store.finish(jid, fence, now, ok) == "STALE":
                stale += 1
            w["job"] = None
    states = {}
    for j in store.jobs.values():
        states[j["state"]] = states.get(j["state"], 0) + 1
    print("final states:", dict(sorted(states.items())))
    print("fencing tokens issued:", store.fence, "| stale finishes rejected:", stale)
    print("side effects applied:", sink.effects, "| stale writes blocked at sink:", sink.rejected)
    print("jobs with >1 applied effect:", sink.effects - len(sink.highest))

simulate()
```

Output:

```text
final states: {'DEAD': 1, 'DONE': 299}
fencing tokens issued: 387 | stale finishes rejected: 24
side effects applied: 311 | stale writes blocked at sink: 8
jobs with >1 applied effect: 11
```

What to notice:

- `claim` treats an expired lease exactly like a pending job; this is the whole takeover mechanism, and it needs no failure detector beyond the clock.
- `fence` is a single counter for the whole store. Every claim gets a strictly larger number than any earlier claim, so "newer holder" is well defined even across jobs and workers.
- `finish` rejected 24 stale completions: zombies that woke after their lease had been reassigned. Without the fence check, those completions would have overwritten the new holder's state.
- The sink blocked 8 stale writes but **11 jobs still had two effects applied**. A fence only stops a stale write that arrives *after* a newer one; when the zombie writes first, both writes look legitimate. This is the central lesson: leases and fences give at-least-once with ordering protection, not exactly-once. Making the effect an upsert keyed by `job_id` (§22.15) turns those 11 into no-ops.
- 387 tokens for 300 jobs means about 29% extra claims came from retries and takeovers. Track this ratio in production; a sudden rise means slow workers or a lease that is too short.

#### Test plan and load-test targets

- **Unit tests:** claim never returns a job twice while its lease is valid; `finish` with an old fence returns `STALE`; backoff delays are 2, 4 and 8 s; a job reaches `DEAD` after `max_attempts`.
- **Property test:** with random crashes and pauses, the final state of every job is `DONE` or `DEAD` and the count of distinct `job_id`s with an effect equals the count of `DONE` jobs.
- **Concurrency test:** 8 worker processes against PostgreSQL; assert no two *unexpired* leases on one job by scanning an audit log of claims.
- **Load test:** 10,000 jobs due in one minute, 8 workers each processing jobs that sleep 50 ms. Targets: p99 firing delay below 2 s, claim rate at least 500/s, database CPU below 70%.
- **Soak test:** 24 hours of a recurring job every 10 s; assert exactly 8,640 occurrences and no growth in table size beyond retention.

#### Failure-injection exercises

**Table 93.101 — Failure injections for the job scheduler.**

| Inject | Expected behavior | How you verify |
|---|---|---|
| `SIGKILL` a worker mid-job | Job re-claimed within about 11 s with a higher fence | Takeover-time metric; attempts column increments |
| `SIGSTOP` a worker for 20 s, then `SIGCONT` | Its `finish` returns `STALE`; its sink write is rejected or deduplicated | Stale-finish counter; sink shows one effect per job |
| Database failover during claims | Claims fail fast and retry; no job lost; some duplicates | Reconciliation query after failover |
| Clock step of +30 s on one worker | Worker-local clock is not used for lease decisions | Leases computed from the database clock (`now()`) only |
| Poison job that always fails | Moves to `DEAD` after `max_attempts`; alert fires | DLQ view and alert log |
| 50,000 jobs due at once (thundering herd) | Claim batches of $n$ jobs keep up; firing delay degrades gracefully | Firing-delay p99 and backlog gauge |

#### Extensions

- Add **priorities and per-tenant quotas** so a bulk backfill cannot starve payout jobs (§46.8 and §47.8).
- Replace polling with **delay buckets** on a log: one topic per minute bucket, consumers that sleep until the bucket's time, and a compacted topic for cancellations.
- Add **DAG dependencies** (job B runs after job A succeeds) and compare your design with a workflow engine's durable execution (§32.11.1).
- Make the store **multi-region**: what happens to fencing tokens when two regions can each issue them? (Hint: partition token ranges by region or run consensus, §26.7.)

#### Self-assessment rubric

**Table 93.102 — Self-assessment rubric: distributed job scheduler.**

| Dimension | Working (meets the spec) | Strong | Exceptional |
|---|---|---|---|
| Correctness | No lost jobs in crash tests | Zero duplicate effects with pauses | Property test with random faults in CI |
| Lease design | Fixed lease and heartbeat | Lease derived from $k \cdot h + d_{\max}$ and justified | Database clock only; clock-step test |
| Throughput | 100 claims/s | 500 claims/s with `SKIP LOCKED` | Sharded store and measured scaling curve |
| Operations | Logs | Metrics for delay, backlog, DLQ | Runbook, cancel/retry API, DST tests |
| Explanation | Describes the flow | Explains lease versus fence | Explains why exactly-once needs idempotent effects |
