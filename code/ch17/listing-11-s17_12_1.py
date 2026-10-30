# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.12.1 (listing 11). Edit the manuscript, not this file.
import math
import random
from collections import Counter

def reservoir_sample(stream, k, rng=random):
    """Algorithm R: a uniform sample of k items from a stream of unknown length, in O(k) memory."""
    reservoir = []
    for n, item in enumerate(stream, start=1):
        if n <= k:
            reservoir.append(item)                     # fill the reservoir first
        else:
            j = rng.randrange(n)                       # uniform in [0, n)
            if j < k:                                  # happens with probability k / n
                reservoir[j] = item                    # evict a uniformly chosen resident
    return reservoir

def reservoir_sample_skip(stream, k, rng=random):
    """Algorithm L (Li 1994): same distribution, but jumps over items, so it draws
    O(k log(n/k)) random numbers instead of n."""
    it = iter(stream)
    reservoir = [x for _, x in zip(range(k), it)]
    w = math.exp(math.log(rng.random()) / k)
    while True:
        skip = math.floor(math.log(rng.random()) / math.log(1 - w))
        for _ in range(skip):                          # discard without drawing randomness
            if next(it, None) is None:
                return reservoir
        item = next(it, None)
        if item is None:
            return reservoir
        reservoir[rng.randrange(k)] = item
        w *= math.exp(math.log(rng.random()) / k)

# Validate uniformity: every one of n = 1,000 items should be chosen with probability k/n = 0.01
n, k, trials = 1_000, 10, 50_000
rng = random.Random(5)
for name, fn in (("Algorithm R", reservoir_sample), ("Algorithm L", reservoir_sample_skip)):
    counts = Counter()
    for _ in range(trials):
        counts.update(fn(range(n), k, rng))
    freqs = [counts[i] / trials for i in range(n)]
    expected = k * trials / n                          # 500 selections per item
    chi2 = sum((counts[i] - expected) ** 2 / expected for i in range(n))
    print(f"{name}: inclusion prob. min {min(freqs):.4f}  max {max(freqs):.4f}  "
          f"(target {k / n:.4f}); first decile {sum(freqs[:100]) / 100:.4f}, "
          f"last decile {sum(freqs[-100:]) / 100:.4f}; chi-square {chi2:.0f} on {n - 1} dof")
