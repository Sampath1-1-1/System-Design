# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.8.2 (listing 1). Edit the manuscript, not this file.
import math
import random
import statistics

def percentile_nearest_rank(samples, p):
    """Return the p-th percentile (0 < p <= 100) using the nearest-rank method."""
    if not samples:
        raise ValueError("no samples")
    ordered = sorted(samples)
    rank = math.ceil(p / 100 * len(ordered))   # 1-based rank
    return ordered[max(rank, 1) - 1]

random.seed(42)
# Log-normal latencies: median ~20 ms, heavy right tail (sigma = 1.0)
latencies_ms = [random.lognormvariate(math.log(20), 1.0) for _ in range(100_000)]

print(f"mean   = {statistics.fmean(latencies_ms):7.1f} ms")
for p in (50, 90, 99, 99.9):
    print(f"p{p:<5} = {percentile_nearest_rank(latencies_ms, p):7.1f} ms")

# Fan-out: a request waits for the slowest of N parallel calls
p99 = percentile_nearest_rank(latencies_ms, 99)
for n in (1, 10, 100):
    trials = 20_000
    slow = sum(
        max(random.choice(latencies_ms) for _ in range(n)) > p99
        for _ in range(trials)
    )
    print(f"N={n:>3}: simulated P(slow) = {slow/trials:.3f}, "
          f"formula 1 - 0.99^N = {1 - 0.99**n:.3f}")
