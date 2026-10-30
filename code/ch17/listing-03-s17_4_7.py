# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.4.7 (listing 3). Edit the manuscript, not this file.
import hashlib
import random

class CuckooFilter:
    """Cuckoo filter (Fan et al. 2014): b slots per bucket, f-bit fingerprints,
    partial-key cuckoo hashing. Supports delete. num_buckets must be a power of two."""

    def __init__(self, num_buckets: int, bucket_size: int = 4, fp_bits: int = 8, max_kicks: int = 500):
        assert num_buckets & (num_buckets - 1) == 0
        self.nb, self.b, self.f, self.max_kicks = num_buckets, bucket_size, fp_bits, max_kicks
        self.buckets = [[] for _ in range(num_buckets)]
        self.count = 0
        self.victim = None          # (bucket, fp) left homeless by a failed insert
        self.rng = random.Random(7)

    def _hash(self, data: bytes) -> int:
        return int.from_bytes(hashlib.blake2b(data, digest_size=8).digest(), "little")

    def _fingerprint_and_index(self, item: str):
        h = self._hash(item.encode())
        fp = (h >> 32) & ((1 << self.f) - 1) or 1       # fingerprint 0 is reserved for "empty"
        return fp, (h & 0xFFFFFFFF) % self.nb

    def _alt_index(self, index: int, fp: int) -> int:
        # i2 = i1 XOR hash(fp): applying it twice returns the original bucket
        return (index ^ self._hash(fp.to_bytes(4, "little"))) % self.nb

    def add(self, item: str) -> bool:
        if self.victim is not None:
            return False                                 # full: refuse further inserts
        fp, i1 = self._fingerprint_and_index(item)
        i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if len(self.buckets[i]) < self.b:
                self.buckets[i].append(fp)
                self.count += 1
                return True
        i = self.rng.choice((i1, i2))                    # both full: evict ("kick") a victim
        for _ in range(self.max_kicks):
            j = self.rng.randrange(self.b)
            fp, self.buckets[i][j] = self.buckets[i][j], fp
            i = self._alt_index(i, fp)
            if len(self.buckets[i]) < self.b:
                self.buckets[i].append(fp)
                self.count += 1
                return True
        self.victim = (i, fp)                            # keep the homeless fingerprint
        self.count += 1                                  # so nothing is ever lost
        return False

    def __contains__(self, item: str) -> bool:
        fp, i1 = self._fingerprint_and_index(item)
        i2 = self._alt_index(i1, fp)
        if self.victim is not None and self.victim[1] == fp and self.victim[0] in (i1, i2):
            return True
        return fp in self.buckets[i1] or fp in self.buckets[i2]

    def delete(self, item: str) -> bool:
        fp, i1 = self._fingerprint_and_index(item)
        i2 = self._alt_index(i1, fp)
        if self.victim is not None and self.victim[1] == fp and self.victim[0] in (i1, i2):
            self.victim = None
            self.count -= 1
            return True
        for i in (i1, i2):
            if fp in self.buckets[i]:
                self.buckets[i].remove(fp)
                self.count -= 1
                return True
        return False

cf = CuckooFilter(num_buckets=2 ** 15, bucket_size=4, fp_bits=8)   # 131,072 slots
capacity = cf.nb * cf.b
inserted = 0
while cf.add(f"member-{inserted}"):
    inserted += 1
inserted += 1                                            # the failed item is held as the victim
print(f"filter full at load factor {inserted / capacity:.3f}")
assert all(f"member-{i}" in cf for i in range(inserted))  # no false negatives

probes = 500_000
fps = sum(f"stranger-{i}" in cf for i in range(probes))
bound = 2 * cf.b / 2 ** cf.f
print(f"false-positive rate: measured {fps / probes:.4f}, bound 2b/2^f = {bound:.4f}")
print(f"bits per stored item: {cf.f * capacity / inserted:.2f}")

for i in range(0, inserted, 2):                          # delete every second member
    assert cf.delete(f"member-{i}")
still_there = all(f"member-{i}" in cf for i in range(1, inserted, 2))
print(f"after deleting half: count = {cf.count}, all survivors found = {still_there}")
