# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.14.2 (listing 6). Edit the manuscript, not this file.
from math import comb, prod

def series(*avail):
    """All components must be up (assumes independent failures)."""
    return prod(avail)

def parallel(*avail):
    """At least one component must be up (independent failures)."""
    return 1 - prod(1 - a for a in avail)

def k_of_n(k, n, a):
    """At least k of n identical, independent components must be up."""
    return sum(comb(n, i) * a**i * (1 - a)**(n - i) for i in range(k, n + 1))

def downtime_per_year(a, hours_per_year=365 * 24):
    return (1 - a) * hours_per_year

web_tier = parallel(0.99, 0.99)          # two app nodes behind a load balancer
db_quorum = k_of_n(2, 3, 0.99)           # 2-of-3 replicated database
system = series(0.9999, web_tier, db_quorum)   # LB -> web tier -> DB

for name, a in [("web tier", web_tier), ("db 2-of-3", db_quorum), ("system", system)]:
    print(f"{name:10s} A = {a:.6f}  downtime = {downtime_per_year(a):6.2f} h/year")
