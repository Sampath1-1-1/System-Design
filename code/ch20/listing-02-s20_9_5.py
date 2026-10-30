# Extracted from manuscript/book1-traditional/20-caching.md §20.9.5 (listing 2). Edit the manuscript, not this file.
"""Hit ratios of LRU, LFU, ARC and a simplified W-TinyLFU on three synthetic traces."""
import itertools
import random
from collections import OrderedDict, defaultdict

class LRU:
    def __init__(self, capacity):
        self.c, self.d = capacity, OrderedDict()
    def access(self, key):                       # returns True on a hit
        if key in self.d:
            self.d.move_to_end(key)
            return True
        self.d[key] = None
        if len(self.d) > self.c:
            self.d.popitem(last=False)
        return False

class LFU:
    """O(1) in-cache LFU: evict the lowest count, least recent among ties."""
    def __init__(self, capacity):
        self.c, self.freq = capacity, {}
        self.buckets, self.min_f = defaultdict(OrderedDict), 0
    def access(self, key):
        if key in self.freq:
            f = self.freq[key]
            del self.buckets[f][key]
            if not self.buckets[f] and self.min_f == f:
                self.min_f = f + 1
            self.freq[key] = f + 1
            self.buckets[f + 1][key] = None
            return True
        if len(self.freq) >= self.c:
            victim, _ = self.buckets[self.min_f].popitem(last=False)
            del self.freq[victim]
        self.freq[key], self.min_f = 1, 1
        self.buckets[1][key] = None
        return False

class ARC:
    """Adaptive Replacement Cache [Megiddo & Modha 2003]: T1/T2 hold data,
    B1/B2 are ghost lists of recently evicted keys, p is T1's target size."""
    def __init__(self, capacity):
        self.c, self.p = capacity, 0
        self.t1, self.t2, self.b1, self.b2 = (OrderedDict() for _ in range(4))
    def _replace(self, in_b2):
        if self.t1 and (not self.t2 or len(self.t1) > self.p
                        or (in_b2 and len(self.t1) == self.p)):
            k, _ = self.t1.popitem(last=False)
            self.b1[k] = None
        else:
            k, _ = self.t2.popitem(last=False)
            self.b2[k] = None
    def access(self, x):
        if x in self.t1:                         # second hit: recency -> frequency
            del self.t1[x]
            self.t2[x] = None
            return True
        if x in self.t2:
            self.t2.move_to_end(x)
            return True
        if x in self.b1:                         # T1 was too small: grow p
            self.p = min(self.c, self.p + max(len(self.b2) // len(self.b1), 1))
            self._replace(False)
            del self.b1[x]
            self.t2[x] = None
            return False
        if x in self.b2:                         # T2 was too small: shrink p
            self.p = max(0, self.p - max(len(self.b1) // len(self.b2), 1))
            self._replace(True)
            del self.b2[x]
            self.t2[x] = None
            return False
        l1 = len(self.t1) + len(self.b1)
        if l1 == self.c:
            if len(self.t1) < self.c:
                self.b1.popitem(last=False)
                self._replace(False)
            else:
                self.t1.popitem(last=False)
        else:
            total = l1 + len(self.t2) + len(self.b2)
            if total >= self.c:
                if total == 2 * self.c:
                    self.b2.popitem(last=False)
                self._replace(False)
        self.t1[x] = None
        return False

SEEDS = (0x9E3779B97F4A7C15, 0xC2B2AE3D27D4EB4F, 0x165667B19E3779F9, 0xD6E8FEB86659FD93)

class CountMin4:
    """Count-Min sketch (4 rows) with 4-bit counters (cap 15) and periodic halving."""
    def __init__(self, capacity):
        self.bits = max(4, (capacity * 4 - 1).bit_length())   # width >= 4 x capacity
        self.rows = [[0] * (1 << self.bits) for _ in SEEDS]
        self.samples, self.reset_at = 0, 10 * capacity
    def _cols(self, key):                        # multiplicative hashing of int keys
        return [(((key + 1) * s) & 0xFFFFFFFFFFFFFFFF) >> (64 - self.bits) for s in SEEDS]
    def add(self, key):
        for row, col in zip(self.rows, self._cols(key)):
            if row[col] < 15:
                row[col] += 1
        self.samples += 1
        if self.samples >= self.reset_at:        # aging: halve every counter
            self.rows = [[v >> 1 for v in row] for row in self.rows]
            self.samples //= 2
    def estimate(self, key):
        return min(row[col] for row, col in zip(self.rows, self._cols(key)))

class WTinyLFU:
    """1% window LRU, then a TinyLFU admission filter guarding a segmented LRU
    main area (20% probation, 80% protected), as in Caffeine (simplified)."""
    def __init__(self, capacity):
        self.wcap = max(1, capacity // 100)
        main = capacity - self.wcap
        self.prot_cap = int(main * 0.8)
        self.main_cap = main
        self.window, self.prob, self.prot = OrderedDict(), OrderedDict(), OrderedDict()
        self.sketch = CountMin4(capacity)
    def access(self, key):
        self.sketch.add(key)
        if key in self.window:
            self.window.move_to_end(key)
            return True
        if key in self.prot:
            self.prot.move_to_end(key)
            return True
        if key in self.prob:                     # promote on second hit
            del self.prob[key]
            self.prot[key] = None
            if len(self.prot) > self.prot_cap:
                k, _ = self.prot.popitem(last=False)
                self.prob[k] = None              # demote to probation MRU
            return True
        self.window[key] = None
        if len(self.window) > self.wcap:
            cand, _ = self.window.popitem(last=False)
            if len(self.prob) + len(self.prot) < self.main_cap:
                self.prob[cand] = None
            elif self.prob or self.prot:
                seg = self.prob if self.prob else self.prot
                victim = next(iter(seg))
                if self.sketch.estimate(cand) > self.sketch.estimate(victim):
                    del seg[victim]              # admit candidate, evict victim
                    self.prob[cand] = None       # else: candidate is dropped
        return False

def zipf_cum(n, s):
    return list(itertools.accumulate(1.0 / i ** s for i in range(1, n + 1)))

def stationary(n, length, rng, s=0.9):
    return rng.choices(range(n), cum_weights=zipf_cum(n, s), k=length)

def with_scans(n, length, rng, s=0.9, burst=8_000, scan=2_000):
    """Zipf bursts interleaved with scans of keys that are never seen again."""
    cum, out, fresh = zipf_cum(n, s), [], n
    while len(out) < length:
        out += rng.choices(range(n), cum_weights=cum, k=burst)
        out += range(fresh, fresh + scan)
        fresh += scan
    return out[:length]

def shifting(n, length, rng, s=0.9, phases=4):
    """Popularity ranks are reshuffled at the start of every phase."""
    cum, out = zipf_cum(n, s), []
    for _ in range(phases):
        perm = list(range(n))
        rng.shuffle(perm)
        out += [perm[r] for r in rng.choices(range(n), cum_weights=cum,
                                             k=length // phases)]
    return out

def hit_ratio(policy, trace, warmup):
    hits = 0
    for t, key in enumerate(trace):
        if policy.access(key) and t >= warmup:
            hits += 1
    return hits / (len(trace) - warmup)

if __name__ == "__main__":
    N, LENGTH = 50_000, 400_000
    rng = random.Random(7)
    traces = {"stationary Zipf": stationary(N, LENGTH, rng),
              "Zipf + scans": with_scans(N, LENGTH, rng),
              "shifting Zipf": shifting(N, LENGTH, rng)}
    policies = [("LRU", LRU), ("LFU", LFU), ("ARC", ARC), ("W-TinyLFU", WTinyLFU)]
    for cap in (500, 2_500):
        print(f"cache = {cap:,} entries ({cap / N:.0%} of {N:,} keys)")
        print(f"  {'trace':<17}" + "".join(f"{name:>11}" for name, _ in policies))
        for tname, trace in traces.items():
            row = [hit_ratio(cls(cap), trace, LENGTH // 10) for _, cls in policies]
            print(f"  {tname:<17}" + "".join(f"{h:>11.1%}" for h in row))
