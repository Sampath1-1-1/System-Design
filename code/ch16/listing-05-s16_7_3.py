# Extracted from manuscript/book1-traditional/16-search-systems.md §16.7.3 (listing 5). Edit the manuscript, not this file.
"""Scatter-gather tail latency: a query waits for the slowest of S shards.
Monte Carlo check of P(all fast) = p**S, and the latency percentiles of max(S shard latencies)."""
import math
import random

def shard_latency_ms(rng):
    # Log-normal per-shard latency: median 8 ms, a heavy-ish right tail (p99 ~ 25.6 ms).
    return 8.0 * math.exp(rng.gauss(0.0, 0.5))

def percentile(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, int(q * len(sorted_vals)))]

if __name__ == "__main__":
    rng = random.Random(42)
    trials = 20_000
    single = sorted(shard_latency_ms(rng) for _ in range(200_000))
    t99 = percentile(single, 0.99)
    print(f"one shard: p50={percentile(single, 0.50):.1f} ms  p99={t99:.1f} ms")
    print(" S   P(all<shard p99) sim  0.99**S   query p50   query p99")
    for S in (1, 10, 50, 100, 200):
        maxes = sorted(max(shard_latency_ms(rng) for _ in range(S)) for _ in range(trials))
        fast = sum(m <= t99 for m in maxes) / trials
        print(f"{S:>3}   {fast:>18.3f}  {0.99 ** S:>7.3f}   {percentile(maxes, 0.5):>6.1f} ms"
              f"   {percentile(maxes, 0.99):>6.1f} ms")
