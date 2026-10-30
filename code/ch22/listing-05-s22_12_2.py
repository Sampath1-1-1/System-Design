# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.12.2 (listing 5). Edit the manuscript, not this file.
"""N clients each need one successful write to a contended resource (optimistic
concurrency: if another write started less than WORK ms earlier, this one conflicts).
Compare backoff strategies by total calls (work) and time until every client succeeds."""
import heapq
import random

BASE, CAP, WORK = 5.0, 2000.0, 1.0               # milliseconds


def no_jitter(attempt, prev, rng):
    return min(CAP, BASE * 2 ** attempt)

def full_jitter(attempt, prev, rng):
    return rng.uniform(0, min(CAP, BASE * 2 ** attempt))

def equal_jitter(attempt, prev, rng):
    v = min(CAP, BASE * 2 ** attempt)
    return v / 2 + rng.uniform(0, v / 2)

def decorrelated_jitter(attempt, prev, rng):
    return min(CAP, rng.uniform(BASE, prev * 3))


def simulate(strategy, clients, seed, max_attempts=200):
    rng = random.Random(seed)
    # every client makes its first call within the same 1 ms (a synchronized wave)
    queue = [(rng.uniform(0, 1.0), c, 0, BASE) for c in range(clients)]
    heapq.heapify(queue)
    busy_until, calls, finish = -1.0, 0, 0.0
    while queue:
        t, c, attempt, prev = heapq.heappop(queue)
        calls += 1
        if t >= busy_until:                      # no conflicting write in flight: success
            busy_until, finish = t + WORK, t
        elif attempt + 1 < max_attempts:         # conflict: back off and try again
            sleep = strategy(attempt + 1, prev, rng)
            heapq.heappush(queue, (t + WORK + sleep, c, attempt + 1, sleep))
    return calls, finish


if __name__ == "__main__":
    strategies = [("exponential, no jitter", no_jitter), ("full jitter", full_jitter),
                  ("equal jitter", equal_jitter), ("decorrelated jitter", decorrelated_jitter)]
    seeds = range(20)
    for n in (25, 100):
        print(f"{n} clients (mean of {len(seeds)} runs)     calls   calls/client   time to finish")
        results = {}
        for name, fn in strategies:
            runs = [simulate(fn, n, s) for s in seeds]
            calls = sum(r[0] for r in runs) / len(runs)
            finish = sum(r[1] for r in runs) / len(runs)
            results[name] = calls
            print(f"  {name:24s} {calls:8.0f}   {calls / n:10.1f}   {finish:10.0f} ms")
        print()
        assert results["full jitter"] < results["exponential, no jitter"] / 3
