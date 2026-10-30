# Extracted from manuscript/book1-traditional/19-load-balancing.md §19.4.4 (listing 2). Edit the manuscript, not this file.
"""Balls into bins: maximum load with d = 1, 2, 3 random choices."""
import math
import random


def max_load(n: int, d: int, rng: random.Random) -> int:
    """Throw n balls into n bins; each ball goes to the least loaded of d random bins."""
    bins = [0] * n
    for _ in range(n):
        if d == 1:
            i = rng.randrange(n)
        else:
            i = min((rng.randrange(n) for _ in range(d)), key=bins.__getitem__)
        bins[i] += 1
    return max(bins)


if __name__ == "__main__":
    rng = random.Random(42)
    trials = 5
    print(f"{'n':>9} | {'d=1':>5} {'d=2':>5} {'d=3':>5} | "
          f"{'ln n/ln ln n':>12} {'ln ln n/ln 2':>12} {'ln ln n/ln 3':>12}")
    for n in (1_000, 10_000, 100_000, 1_000_000):
        t = trials if n < 1_000_000 else 2
        row = [sum(max_load(n, d, rng) for _ in range(t)) / t for d in (1, 2, 3)]
        lnln = math.log(math.log(n))
        print(f"{n:>9,} | {row[0]:5.1f} {row[1]:5.1f} {row[2]:5.1f} | "
              f"{math.log(n) / lnln:12.2f} {lnln / math.log(2):12.2f} {lnln / math.log(3):12.2f}")
