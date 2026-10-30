# Extracted from manuscript/book1-traditional/23-performance-engineering.md §23.10.2 (listing 4). Edit the manuscript, not this file.
import math
import random

def usl(n, gamma, alpha, beta):
    """USL throughput: gamma = throughput at N = 1."""
    return gamma * n / (1 + alpha * (n - 1) + beta * n * (n - 1))

def solve(a, b):
    """Solve the small linear system a x = b by Gaussian elimination."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            for k in range(c, n + 1):
                m[r][k] -= f * m[c][k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (m[r][n] - sum(m[r][k] * x[k] for k in range(r + 1, n))) / m[r][r]
    return x

def fit_linearized(ns, xs):
    """Step 1: N*gamma/X - 1 = alpha (N-1) + beta N (N-1), with gamma = X(1)."""
    gamma = xs[ns.index(1)]
    rows = [(n - 1, n * (n - 1)) for n in ns]
    ys = [n * gamma / x - 1 for n, x in zip(ns, xs)]
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(2)] for i in range(2)]
    aty = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(2)]
    alpha, beta = solve(ata, aty)
    return gamma, alpha, beta

def fit_nonlinear(ns, xs, p, iters=50):
    """Step 2: Gauss-Newton refinement of (gamma, alpha, beta) on throughput."""
    p = list(p)
    for _ in range(iters):
        r = [x - usl(n, *p) for n, x in zip(ns, xs)]
        jac = []
        for n in ns:
            row = []
            for k in range(3):
                h = 1e-6 * max(abs(p[k]), 1e-6)
                q = p[:]; q[k] += h
                row.append((usl(n, *q) - usl(n, *p)) / h)
            jac.append(row)
        jtj = [[sum(j[a] * j[b] for j in jac) for b in range(3)] for a in range(3)]
        jtr = [sum(j[a] * ri for j, ri in zip(jac, r)) for a in range(3)]
        step = solve(jtj, jtr)
        p = [pi + si for pi, si in zip(p, step)]
        if max(abs(s / pi) for s, pi in zip(step, p)) < 1e-10:
            break
    return p

# "Measured" throughput (req/s) at each client concurrency N. Synthetic:
# generated from gamma=950, alpha=0.03, beta=0.0004 with 3% noise.
rng = random.Random(11)
ns = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64]
xs = [round(usl(n, 950, 0.03, 0.0004) * rng.gauss(1, 0.03)) for n in ns]

g, a, b = fit_linearized(ns, xs)
print(f"linearized fit : gamma={g:7.1f}  alpha={a:.4f}  beta={b:.6f}")
g, a, b = fit_nonlinear(ns, xs, (g, a, b))
print(f"nonlinear fit  : gamma={g:7.1f}  alpha={a:.4f}  beta={b:.6f}")

mean = sum(xs) / len(xs)
ss_res = sum((x - usl(n, g, a, b)) ** 2 for n, x in zip(ns, xs))
ss_tot = sum((x - mean) ** 2 for x in xs)
n_star = math.sqrt((1 - a) / b)
x_max = usl(n_star, g, a, b)
print(f"R^2 = {1 - ss_res / ss_tot:.4f}   N* = {n_star:.1f}   X(N*) = {x_max:,.0f} req/s")

print(f"{'N':>4}{'measured':>10}{'model':>9}{'R=N/X ms':>10}{'efficiency':>12}")
for n in ns + [96, 128]:
    model = usl(n, g, a, b)
    meas = f"{xs[ns.index(n)]:>10,}" if n in ns else f"{'-':>10}"
    print(f"{n:>4}{meas}{model:>9,.0f}{1000 * n / model:>10.2f}{model / (n * g):>12.0%}")
