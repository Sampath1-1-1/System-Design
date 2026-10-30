# Extracted from manuscript/book1-traditional/23-performance-engineering.md §23.4.5 (listing 1). Edit the manuscript, not this file.
import cProfile
import json
import linecache
import pstats
import random
import tracemalloc

def make_events(n, seed=7):
    """Synthetic request log: JSON lines with a user id and a latency."""
    rng = random.Random(seed)
    return [json.dumps({"user": f"u{rng.randrange(5_000)}",
                        "ms": round(rng.lognormvariate(3, 1), 2)})
            for _ in range(n)]

def distinct_users_slow(events):
    seen = []                          # list: membership test is O(n)
    for line in events:
        user = json.loads(line)["user"]
        if user not in seen:
            seen.append(user)
    return len(seen)

def distinct_users_fast(events):
    return len({json.loads(line)["user"] for line in events})  # set: O(1)

def report(events):
    return distinct_users_slow(events), distinct_users_fast(events)

events = make_events(50_000)

# 1. CPU: cProfile is a deterministic (instrumenting) profiler
profiler = cProfile.Profile()
profiler.enable()
print("distinct users (slow, fast):", report(events))
profiler.disable()
stats = pstats.Stats(profiler)
print(f"{'function':<22}{'calls':>8}{'self s':>9}{'total s':>9}")
rows = sorted(((k, v) for k, v in stats.stats.items() if not k[2].startswith("<")),
              key=lambda kv: kv[1][3], reverse=True)[:6]       # by total time
for (filename, line, name), (cc, nc, tottime, cumtime, _) in rows:
    print(f"{name[:21]:<22}{nc:>8}{tottime:>9.3f}{cumtime:>9.3f}")

# 2. Memory: tracemalloc attributes live allocations to source lines
tracemalloc.start()
more_events = make_events(50_000)
snapshot = tracemalloc.take_snapshot()
tracemalloc.stop()
for stat in snapshot.statistics("lineno")[:2]:
    frame = stat.traceback[0]
    code = linecache.getline(frame.filename, frame.lineno).strip()
    print(f"{stat.size / 1024:6.0f} KiB in {stat.count:6d} blocks: {code[:38]}")
