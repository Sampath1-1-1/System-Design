# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.4.4 (listing 2). Edit the manuscript, not this file.
import hashlib
import math

class BloomFilter:
    """Standard Bloom filter using Kirsch-Mitzenmacher double hashing."""

    def __init__(self, n_expected: int, fp_target: float):
        # m = -n ln p / (ln 2)^2 ; k = (m / n) ln 2
        self.m = math.ceil(-n_expected * math.log(fp_target) / math.log(2) ** 2)
        self.k = max(1, round(self.m / n_expected * math.log(2)))
        self.bits = bytearray((self.m + 7) // 8)

    def _positions(self, item: str):
        digest = hashlib.blake2b(item.encode(), digest_size=16).digest()
        h1 = int.from_bytes(digest[:8], "little")
        h2 = int.from_bytes(digest[8:], "little") | 1     # odd, so it never sticks at h1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str) -> None:
        for pos in self._positions(item):
            self.bits[pos >> 3] |= 1 << (pos & 7)

    def __contains__(self, item: str) -> bool:
        return all(self.bits[pos >> 3] & (1 << (pos & 7)) for pos in self._positions(item))

def predicted_fp(m: int, n: int, k: int) -> float:
    return (1 - math.exp(-k * n / m)) ** k

n, probes = 100_000, 1_000_000
print(f"{'target p':>9} {'m (bits)':>10} {'bits/item':>9} {'k':>3} {'predicted':>10} {'measured':>10}")
for target in (0.05, 0.01, 0.001):
    bf = BloomFilter(n, target)
    for i in range(n):
        bf.add(f"member-{i}")
    assert all(f"member-{i}" in bf for i in range(n))    # no false negatives, ever
    fps = sum(f"stranger-{i}" in bf for i in range(probes))
    print(f"{target:9.3f} {bf.m:10d} {bf.m / n:9.2f} {bf.k:3d} "
          f"{predicted_fp(bf.m, n, bf.k):10.5f} {fps / probes:10.5f}")

# What happens if you insert 3x more items than the filter was sized for?
bf = BloomFilter(n, 0.01)
for i in range(3 * n):
    bf.add(f"member-{i}")
fps = sum(f"stranger-{i}" in bf for i in range(probes))
print(f"overfilled 3x: predicted {predicted_fp(bf.m, 3 * n, bf.k):.4f}, measured {fps / probes:.4f}")
