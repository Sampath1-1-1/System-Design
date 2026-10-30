# Extracted from manuscript/book1-traditional/23-performance-engineering.md §23.7.2 (listing 3). Edit the manuscript, not this file.
import heapq
import math
import random

SERVERS = 20
N_REQ = 400_000

def service_time(rng):
    """~1 ms of work; 0.1% of requests hit a 50 ms hiccup (GC, compaction...)."""
    t = 0.0005 + rng.expovariate(1 / 0.0005)
    if rng.random() < 0.001:
        t += 0.050
    return t

def simulate(rho, hedge_after=None, cancel=False, seed=3):
    """FIFO replicas; Poisson arrivals; optional hedge to a second replica.
    Returns (latencies in ms, extra work as a fraction of original work)."""
    rng = random.Random(seed)
    lam = rho * SERVERS / 0.00105            # mean service time is 1.05 ms
    free_at = [0.0] * SERVERS
    events, t = [], 0.0                      # (submit_time, seq, req_id, is_hedge, avoid)
    for i in range(N_REQ):
        t += rng.expovariate(lam)
        heapq.heappush(events, (t, i, i, False, -1))
    done = [0.0] * N_REQ
    sent = [0.0] * N_REQ
    seq, base_work, extra_work = N_REQ, 0.0, 0.0
    while events:
        now, _, rid, is_hedge, avoid = heapq.heappop(events)
        server = rng.randrange(SERVERS)
        while server == avoid:
            server = rng.randrange(SERVERS)
        start = max(now, free_at[server])
        if is_hedge:
            if cancel and done[rid] <= start:  # original already answered: drop copy
                continue
            work = service_time(rng)
            free_at[server] = start + work
            extra_work += work
            done[rid] = min(done[rid], free_at[server])
        else:
            work = service_time(rng)
            free_at[server] = start + work
            base_work += work
            sent[rid], done[rid] = now, free_at[server]
            if hedge_after is not None and done[rid] > now + hedge_after:
                seq += 1
                heapq.heappush(events, (now + hedge_after, seq, rid, True, server))
    lat = sorted((d - s) * 1000 for d, s in zip(done, sent))
    return lat, extra_work / base_work

def pct(xs, q):
    return xs[max(math.ceil(q / 100 * len(xs)), 1) - 1]

for rho in (0.5, 0.8):
    base, _ = simulate(rho)
    d = pct(base, 95) / 1000                 # hedge after the unhedged p95
    print(f"utilization {rho:.0%}: hedge delay = p95 = {d*1000:.2f} ms")
    print(f"  {'policy':<16}{'p50':>8}{'p95':>8}{'p99':>8}{'p99.9':>8}{'extra work':>12}")
    for name, kw in (("no hedging", {}),
                     ("hedge at p95", {"hedge_after": d}),
                     ("hedge + cancel", {"hedge_after": d, "cancel": True}),
                     ("hedge at p50", {"hedge_after": pct(base, 50) / 1000})):
        lat, extra = simulate(rho, **kw)
        print(f"  {name:<16}" + "".join(f"{pct(lat, q):>8.1f}" for q in (50, 95, 99, 99.9))
              + f"{extra:>12.1%}")
