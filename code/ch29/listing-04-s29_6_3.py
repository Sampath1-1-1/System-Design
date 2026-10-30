# Extracted from manuscript/book1-traditional/29-distributed-data-processing.md §29.6.3 (listing 4). Edit the manuscript, not this file.
"""Partition skew and key salting: per-partition load before and after a two-stage aggregation."""
import random
import zlib
from collections import Counter


def partition(key, n):
    return zlib.crc32(repr(key).encode()) % n


def stage_loads(keys, n):
    loads = Counter(partition(k, n) for k in keys)
    return [loads.get(p, 0) for p in range(n)]


def skew_ratio(loads):
    return max(loads) / (sum(loads) / len(loads))     # slowest task / average task


rng = random.Random(1)
P = 200                                              # shuffle partitions
records = [("hot" if rng.random() < 0.20 else f"user{rng.randrange(100_000)}", 1)
           for _ in range(1_000_000)]                # one key carries 20% of all rows
truth = Counter()
for k, v in records:
    truth[k] += v

# Plain aggregation: every row of a key goes to one partition.
plain = stage_loads((k for k, _ in records), P)
print(f"plain  : max={max(plain):>7,}  mean={sum(plain) / P:>7,.0f}  skew={skew_ratio(plain):5.1f}x")

sample = Counter(k for k, _ in rng.sample(records, 10_000))   # find hot keys from a 1% sample
hot = {k for k, c in sample.items() if c > 0.01 * 10_000}
print("hot keys found by sampling:", hot)

for salt in (8, 64):
    # Stage 1: append a random salt to hot keys only, spreading each over `salt` partitions.
    salted = [((k, rng.randrange(salt) if k in hot else 0), v) for k, v in records]
    s1 = stage_loads((sk for sk, _ in salted), P)
    partial = Counter()
    for (k, s), v in salted:
        partial[(k, s)] += v                         # partial sums per (key, salt)
    # Stage 2: strip the salt and combine at most `salt` partial sums per key.
    s2 = stage_loads((k for k, _ in partial), P)
    final = Counter()
    for (k, _), v in partial.items():
        final[k] += v
    assert final == truth                            # salting never changes the answer
    print(f"salt={salt:<3}: stage1 max={max(s1):>7,} skew={skew_ratio(s1):5.1f}x | "
          f"stage2 rows={len(partial):,} skew={skew_ratio(s2):4.1f}x")
