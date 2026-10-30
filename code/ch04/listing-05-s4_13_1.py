# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.13.1 (listing 5). Edit the manuscript, not this file.
import math

def amdahl(p, n):
    """Speedup with n processors when fraction p of the work is parallel."""
    return 1 / ((1 - p) + p / n)

def gustafson(p, n):
    """Scaled speedup when the parallel part grows with n."""
    return (1 - p) + p * n

def usl(n, alpha, beta):
    """Relative capacity C(n) under the Universal Scalability Law."""
    return n / (1 + alpha * (n - 1) + beta * n * (n - 1))

p, alpha, beta = 0.95, 0.05, 0.001
print("   N  Amdahl  Gustafson   USL")
for n in (1, 2, 4, 8, 16, 32, 64, 128):
    print(f"{n:4d}  {amdahl(p, n):6.2f}  {gustafson(p, n):9.2f}  {usl(n, alpha, beta):5.2f}")
n_star = math.sqrt((1 - alpha) / beta)
print(f"USL peak at N* = {n_star:.1f}; Amdahl ceiling = {1/(1-p):.0f}")
