# Extracted from manuscript/book1-traditional/04-quantitative-foundations.md §4.10.3 (listing 3). Edit the manuscript, not this file.
import random

def simulate_mm1(lam, mu, n_customers=200_000, seed=1):
    """Simulate a FIFO single-server queue with Poisson arrivals and
    exponential service times. Returns mean time in system (seconds)."""
    rng = random.Random(seed)
    arrival = 0.0          # arrival time of current customer
    server_free_at = 0.0   # time at which the server finishes its current job
    total_time = 0.0
    for _ in range(n_customers):
        arrival += rng.expovariate(lam)            # next arrival
        start = max(arrival, server_free_at)       # wait if server busy
        server_free_at = start + rng.expovariate(mu)
        total_time += server_free_at - arrival     # queueing + service
    return total_time / n_customers

mu = 100.0  # server completes 100 requests/s on average (10 ms each)
print(" rho   formula W (ms)   simulated W (ms)")
for lam in (50, 80, 90, 95, 99):
    formula = 1 / (mu - lam)
    sim = simulate_mm1(lam, mu)
    print(f"{lam/mu:4.2f}   {formula*1000:12.1f}   {sim*1000:14.1f}")
