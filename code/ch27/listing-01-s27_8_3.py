# Extracted from manuscript/book1-traditional/27-replication-and-fault-tolerance.md §27.8.3 (listing 1). Edit the manuscript, not this file.
"""Quorum overlap and the latency of waiting for the k-th fastest of N replicas."""
from itertools import combinations
from math import comb
import random

def min_overlap(n, r, w):
    """Smallest possible intersection of any read set and any write set."""
    replicas = range(n)
    return min(len(set(rs) & set(ws))
               for rs in combinations(replicas, r)
               for ws in combinations(replicas, w))

def p_kth_slow(n, k, p_slow):
    """P(the k-th fastest reply is slow) = P(fewer than k replicas are fast)."""
    q = 1 - p_slow
    return sum(comb(n, j) * q**j * p_slow**(n - j) for j in range(k))

def mean_kth_exponential(n, k, mean):
    """E[k-th smallest of n i.i.d. exponential latencies with the given mean]."""
    return mean * sum(1 / i for i in range(n - k + 1, n + 1))

if __name__ == "__main__":
    n = 3
    print("R W  R+W>N  min overlap  read faults ok  write faults ok")
    for r in range(1, n + 1):
        for w in range(1, n + 1):
            print(f"{r} {w}  {str(r + w > n):5}  {min_overlap(n, r, w):^11}  "
                  f"{n - r:^14}  {n - w:^15}")

    print("\nP(k-th reply is slow), each replica slow with p = 0.01")
    for k in (1, 2, 3):
        print(f"  k = {k}: {p_kth_slow(n, k, 0.01):.3e}")

    random.seed(1)
    trials = 200_000
    print("\nk-th fastest of 3 exponential replies, mean 2 ms")
    for k in (1, 2, 3):
        sim = sum(sorted(random.expovariate(1 / 2.0) for _ in range(n))[k - 1]
                  for _ in range(trials)) / trials
        print(f"  k = {k}: formula {mean_kth_exponential(n, k, 2.0):.3f} ms, "
              f"simulated {sim:.3f} ms")
