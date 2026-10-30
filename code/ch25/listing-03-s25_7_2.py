# Extracted from manuscript/book1-traditional/25-consistency-and-availability.md §25.7.2 (listing 3). Edit the manuscript, not this file.
"""PBS-style Monte Carlo (WARS model, after Bailis et al. 2012): probability
that a read issued t ms after a write commits returns that write (or newer)."""
import random
from math import comb

def one_trial(n, r, w, t, lat):
    W = [lat("W") for _ in range(n)]           # write reaches replica i
    A = [lat("A") for _ in range(n)]           # replica i's ack returns
    commit = sorted(W[i] + A[i] for i in range(n))[w - 1]   # w-th ack
    R = [lat("R") for _ in range(n)]           # read request reaches replica i
    S = [lat("S") for _ in range(n)]           # replica i's response returns
    first_r = sorted(range(n), key=lambda i: R[i] + S[i])[:r]
    # consistent if some responder already had the write when the read arrived
    return any(W[i] <= commit + t + R[i] for i in first_r)

def lat(kind, rng=random.Random(7)):
    if kind == "W":                            # propagate + apply: slow tail
        return 1.0 + rng.expovariate(1 / 4.0)  # mean 5 ms
    return 0.25 + rng.expovariate(1 / 0.5)     # A, R, S: mean 0.75 ms

def p_consistent(n, r, w, t, trials=100_000):
    return sum(one_trial(n, r, w, t, lat) for _ in range(trials)) / trials

if __name__ == "__main__":
    n = 3
    print("closed form, no propagation after commit: P(stale) = C(N-W,R)/C(N,R)")
    for r, w in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        print(f"  N={n} R={r} W={w}: {comb(n - w, r) / comb(n, r):.3f}")
    ts = [0, 1, 2, 5, 10, 20]
    print("\nMonte Carlo P(consistent read) by delay t after commit (ms)")
    print("R W  " + "".join(f"{t:>8}" for t in ts))
    for r, w in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        row = [p_consistent(n, r, w, t) for t in ts]
        print(f"{r} {w}  " + "".join(f"{p:8.4f}" for p in row))
