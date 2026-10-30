# Extracted from manuscript/book1-traditional/14-database-scaling.md §14.8.4 (listing 4). Edit the manuscript, not this file.
"""How load imbalance on a hash ring shrinks as virtual nodes V grow.

For each V, build many independent rings of N nodes, compute every node's
exact share of the key space (the total length of the arcs it owns) and
compare the spread with the closed form sqrt((N-1)/(N*V+1)).
"""
import hashlib
import math
import statistics

RING = 2 ** 64
N = 10            # physical nodes
TRIALS = 200      # independent rings per value of V

def h(key: str) -> int:
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")

def node_shares(n: int, v: int, trial: int) -> list:
    """Fraction of the ring owned by each node in one random ring."""
    points = sorted((h(f"t{trial}/node-{i}#vn{j}"), i)
                    for i in range(n) for j in range(v))
    share = [0] * n
    prev = points[-1][0] - RING          # wrap: arc ending at the first point
    for pos, owner in points:
        share[owner] += pos - prev       # a vnode owns the arc that ends at it
        prev = pos
    return [s / RING for s in share]

def expected_max_std_normal(n: int, samples: int = 4000) -> float:
    """E[max of n standard normals], by a quick deterministic quadrature."""
    nd = statistics.NormalDist()
    total = 0.0
    for k in range(samples):                  # E[max] = integral of x d(F^n)
        u = (k + 0.5) / samples               # u = F(x)^n  =>  x = F^-1(u^(1/n))
        total += nd.inv_cdf(u ** (1.0 / n))
    return total / samples

if __name__ == "__main__":
    z = expected_max_std_normal(N)
    print(f"N = {N} nodes, {TRIALS} rings per row, E[max of {N} normals] = {z:.3f}")
    print(f"{'V':>5} {'CV sim':>8} {'CV theory':>10} {'max/mean sim':>13} "
          f"{'max/mean approx':>16}")
    rows = []
    for v in (1, 4, 16, 64, 256, 1024):
        trials = TRIALS if v <= 256 else TRIALS // 4
        cvs, maxes = [], []
        for t in range(trials):
            s = node_shares(N, v, t)
            cvs.append(statistics.pstdev(s) * N)      # std / mean, mean = 1/N
            maxes.append(max(s) * N)
        # shares sum to exactly 1, so pstdev about the mean 1/N is unbiased
        cv_sim = math.sqrt(statistics.fmean(c * c for c in cvs))
        cv_th = math.sqrt((N - 1) / (N * v + 1))
        rows.append((v, cv_sim))
        print(f"{v:>5} {cv_sim:>8.4f} {cv_th:>10.4f} "
              f"{statistics.fmean(maxes):>13.3f} {1 + z * cv_th:>16.3f}")
    harmonic = sum(1 / k for k in range(1, N + 1))
    print(f"V=1 exact: E[max/mean] = H_N = {harmonic:.3f}")
    (v1, c1), (v2, c2) = rows[1], rows[-1]
    slope = math.log(c2 / c1) / math.log(v2 / v1)
    print(f"log-log slope of CV vs V between V={v1} and V={v2}: {slope:.3f}")
