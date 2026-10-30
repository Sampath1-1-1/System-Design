# Extracted from manuscript/book1-traditional/20-caching.md §20.3.3 (listing 1). Edit the manuscript, not this file.
"""Why small caches work: the ideal hit ratio of a cache that holds the C most
popular of N keys under Zipf popularity, versus a simulated LRU cache."""
import itertools
import random
from collections import OrderedDict

def zipf_weights(n, s):
    """Unnormalized Zipf weights 1/i^s for ranks 1..n."""
    return [1.0 / i ** s for i in range(1, n + 1)]

def ideal_hit_ratio(weights, c):
    """Fraction of requests for the top-c keys: H(c, s) / H(n, s)."""
    return sum(weights[:c]) / sum(weights)

def zipf_trace(weights, length, seed=1):
    """Sample `length` requests; key i has probability weights[i] / sum."""
    cum = list(itertools.accumulate(weights))
    return random.Random(seed).choices(range(len(weights)), cum_weights=cum, k=length)

def lru_hit_ratio(trace, capacity, warmup):
    cache, hits = OrderedDict(), 0
    for t, key in enumerate(trace):
        if key in cache:
            cache.move_to_end(key)
            hits += t >= warmup
        else:
            cache[key] = None
            if len(cache) > capacity:
                cache.popitem(last=False)          # evict least recently used
    return hits / (len(trace) - warmup)

if __name__ == "__main__":
    N, LENGTH, WARMUP = 100_000, 1_000_000, 200_000
    sizes = [100, 1_000, 10_000]                    # 0.1%, 1%, 10% of the keys
    print(f"N = {N:,} keys, {LENGTH:,} requests; hit ratio by cache size")
    print("   s   policy        " + "".join(f"{c / N:>9.1%}" for c in sizes))
    for s in (0.7, 0.9, 1.0):
        w = zipf_weights(N, s)
        trace = zipf_trace(w, LENGTH)
        ideal = [ideal_hit_ratio(w, c) for c in sizes]
        lru = [lru_hit_ratio(trace, c, WARMUP) for c in sizes]
        print(f"{s:>4}   ideal top-C   " + "".join(f"{h:>9.1%}" for h in ideal))
        print(f"{s:>4}   LRU (sim)     " + "".join(f"{h:>9.1%}" for h in lru))
    w = zipf_weights(1_000_000, 1.0)
    print(f"worked example: N = 1e6, s = 1, C = 1e4 -> ideal "
          f"{ideal_hit_ratio(w, 10_000):.1%}")
