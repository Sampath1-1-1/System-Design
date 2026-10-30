# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.6.2 (listing 5). Edit the manuscript, not this file.
import hashlib
import heapq
import math
import random
from collections import Counter

class CountMinSketch:
    """Count-Min sketch (Cormode & Muthukrishnan 2005): d rows x w counters."""

    def __init__(self, epsilon: float, delta: float):
        self.w = math.ceil(math.e / epsilon)               # width from accuracy
        self.d = math.ceil(math.log(1 / delta))            # depth from confidence
        self.table = [[0] * self.w for _ in range(self.d)]
        self.total = 0

    def _columns(self, item: str):
        digest = hashlib.blake2b(item.encode(), digest_size=16).digest()
        h1 = int.from_bytes(digest[:8], "little")
        h2 = int.from_bytes(digest[8:], "little")
        return [(h1 + r * h2) % self.w for r in range(self.d)]

    def add(self, item: str, count: int = 1) -> None:
        self.total += count
        for row, col in enumerate(self._columns(item)):
            self.table[row][col] += count

    def estimate(self, item: str) -> int:
        return min(self.table[row][col] for row, col in enumerate(self._columns(item)))

class TopK:
    """Heavy hitters: a Count-Min sketch plus a min-heap of the k largest estimates."""

    def __init__(self, k: int, epsilon: float, delta: float):
        self.k, self.cms = k, CountMinSketch(epsilon, delta)
        self.heap, self.members = [], {}                   # heap of (estimate, item)

    def add(self, item: str) -> None:
        self.cms.add(item)
        est = self.cms.estimate(item)
        if item in self.members:
            self.members[item] = est                       # lazily refreshed below
        elif len(self.heap) < self.k:
            self.members[item] = est
            heapq.heappush(self.heap, (est, item))
        elif est > self.heap[0][0]:
            # refresh stale heap entries before deciding whom to evict
            self.heap = [(self.members[i], i) for _, i in self.heap]
            heapq.heapify(self.heap)
            if est > self.heap[0][0]:
                _, evicted = heapq.heapreplace(self.heap, (est, item))
                del self.members[evicted]
                self.members[item] = est

    def top(self):
        return sorted(((c, i) for i, c in self.members.items()), reverse=True)

def space_saving(stream, k):
    """Metwally et al. 2005: k counters; the newcomer replaces the minimum and inherits its count."""
    counters = {}
    for item in stream:
        if item in counters:
            counters[item] += 1
        elif len(counters) < k:
            counters[item] = 1
        else:
            victim = min(counters, key=counters.get)      # O(k); production uses a stream-summary list
            counters[item] = counters.pop(victim) + 1
    return sorted(((c, i) for i, c in counters.items()), reverse=True)

# A Zipf-like stream: 1,000,000 events over 100,000 distinct URLs (exponent 1.1)
rng = random.Random(1)
universe = 100_000
weights = [1 / (r ** 1.1) for r in range(1, universe + 1)]
stream = [f"/page/{r}" for r in rng.choices(range(1, universe + 1), weights=weights, k=1_000_000)]
truth = Counter(stream)

eps, delta = 0.001, 0.01
cms = CountMinSketch(eps, delta)
for item in stream:
    cms.add(item)
N = cms.total
errors = [cms.estimate(x) - c for x, c in truth.items()]
assert min(errors) >= 0                                     # never underestimates
print(f"w = {cms.w}, d = {cms.d}, counters = {cms.w * cms.d:,} vs distinct items = {len(truth):,}")
print(f"error bound eps*N = {eps * N:,.0f}; max error = {max(errors)}; "
      f"mean error = {sum(errors) / len(errors):.1f}; "
      f"items over bound = {sum(e > eps * N for e in errors)} of {len(errors):,} (delta allows {delta:.0%})")

tk = TopK(10, eps, delta)
for item in stream:
    tk.add(item)
true_top = [i for i, _ in truth.most_common(10)]
print("CMS+heap top-10 recall:", len(set(i for _, i in tk.top()) & set(true_top)) / 10)
ss = space_saving(stream, 100)
print("Space-Saving (100 counters) top-10 recall:", len(set(i for _, i in ss[:10]) & set(true_top)) / 10)
print("true top-3:", truth.most_common(3))
print("Space-Saving top-3:", [(i, c) for c, i in ss[:3]])
