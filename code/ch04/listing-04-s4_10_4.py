# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.10.4 (listing 4). Edit the manuscript, not this file.
import math

def erlang_c(c, lam, mu):
    """Probability that an arriving request must wait (M/M/c, Erlang C)."""
    a = lam / mu                 # offered load in "servers' worth" of work
    rho = a / c                  # per-server utilization
    if rho >= 1:
        return 1.0
    top = a**c / (math.factorial(c) * (1 - rho))
    bottom = sum(a**k / math.factorial(k) for k in range(c)) + top
    return top / bottom

def mmc_response_time(c, lam, mu):
    """Mean time in system W for an M/M/c queue (seconds)."""
    wait = erlang_c(c, lam, mu) / (c * mu - lam)
    return wait + 1 / mu

lam = 80.0
print(f"One fast server  (M/M/1, mu=100): W = {mmc_response_time(1, lam, 100)*1000:.1f} ms")
print(f"Two slow servers, shared queue (M/M/2, mu=50 each): "
      f"W = {mmc_response_time(2, lam, 50)*1000:.1f} ms")
print(f"Two slow servers, separate queues (2 x M/M/1, mu=50, lam=40 each): "
      f"W = {mmc_response_time(1, lam/2, 50)*1000:.1f} ms")
