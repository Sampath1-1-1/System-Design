# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.5.1 (listing 4). Edit the manuscript, not this file.
import hashlib
import math

class HyperLogLog:
    """HyperLogLog (Flajolet et al. 2007) with 2^p registers and a 64-bit hash.
    Includes the linear-counting correction for small cardinalities."""

    def __init__(self, p: int = 14, salt: bytes = b""):
        self.p, self.m = p, 1 << p
        self.registers = bytearray(self.m)
        self.salt = salt
        self.alpha = 0.7213 / (1 + 1.079 / self.m)        # bias constant for m >= 128

    def add(self, item: str) -> None:
        x = int.from_bytes(hashlib.blake2b(item.encode(), digest_size=8, salt=self.salt).digest(), "big")
        j = x >> (64 - self.p)                            # first p bits choose the register
        w = x & ((1 << (64 - self.p)) - 1)                # remaining 64 - p bits
        rank = (64 - self.p) - w.bit_length() + 1         # position of the leftmost 1-bit
        if rank > self.registers[j]:
            self.registers[j] = rank

    def count(self) -> float:
        z = sum(2.0 ** -r for r in self.registers)
        estimate = self.alpha * self.m * self.m / z       # normalized harmonic mean
        zeros = self.registers.count(0)
        if estimate <= 2.5 * self.m and zeros:            # small range: linear counting
            estimate = self.m * math.log(self.m / zeros)
        return estimate

    def merge(self, other: "HyperLogLog") -> None:
        self.registers = bytearray(max(a, b) for a, b in zip(self.registers, other.registers))

n, trials = 100_000, 50
print(f"{'p':>3} {'registers':>9} {'memory':>9} {'predicted SE':>12} {'measured RMS err':>16}")
for p in (10, 12, 14):
    errors = []
    for t in range(trials):
        h = HyperLogLog(p, salt=t.to_bytes(4, "little"))
        for i in range(n):
            h.add(f"user-{i}")
        errors.append((h.count() - n) / n)
    rms = math.sqrt(sum(e * e for e in errors) / trials)
    mem = h.m * 6 / 8                                     # 6-bit registers, as in Redis
    print(f"{p:3d} {h.m:9d} {mem:7.0f} B {1.04 / math.sqrt(h.m):12.4f} {rms:16.4f}")

# Mergeability: two days of visitors with 50,000 in common
day1, day2 = HyperLogLog(14), HyperLogLog(14)
for i in range(0, 150_000):
    day1.add(f"user-{i}")
for i in range(100_000, 250_000):
    day2.add(f"user-{i}")
day1.merge(day2)
print(f"union estimate {day1.count():,.0f} (true 250,000)")
