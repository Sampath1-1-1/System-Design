# Extracted from manuscript/book1-traditional/20-caching.md §20.11.2 (listing 3). Edit the manuscript, not this file.
"""One hot key under Poisson traffic: recomputations and misses per refresh for
no protection, a recompute lock, and XFetch [Vattani et al. 2015]."""
import math
import random

def simulate(policy, rate=100.0, ttl=60.0, delta=2.0, beta=1.0,
             hours=3.0, seed=42):
    rng = random.Random(seed)
    expiry = ttl                         # value computed at t = 0
    inflight = []                        # finish times of running recomputes
    t, end = 0.0, hours * 3600
    recomputes = misses = requests = episodes = 0
    last_episode, leads = -1e9, []

    def start(now):
        nonlocal recomputes, episodes, last_episode
        recomputes += 1
        inflight.append(now + delta)
        if now > last_episode + delta:   # first recompute of a new refresh
            episodes += 1
            last_episode = now
            leads.append(expiry - now)   # > 0 means refreshed before expiry

    while True:
        t += rng.expovariate(rate)       # next request (Poisson arrivals)
        if t >= end:
            break
        requests += 1
        for f in [f for f in inflight if f <= t]:
            inflight.remove(f)           # a recompute finished: store value
            expiry = f + ttl
        if t >= expiry:                  # value missing: the request misses
            misses += 1
            if policy == "none" or not inflight:
                start(t)                 # "lock" lets only one recompute run
        elif policy.startswith("xfetch"):
            early = t - delta * beta * math.log(rng.random()) >= expiry
            if early and (policy == "xfetch" or not inflight):
                start(t)                 # "xfetch+lock" also skips duplicates
    return dict(requests=requests, episodes=episodes,
                per_refresh=recomputes / episodes, miss_ratio=misses / requests,
                mean_lead=sum(leads) / len(leads))

if __name__ == "__main__":
    rate, delta = 100.0, 2.0
    print(f"rate {rate:.0f} req/s, TTL 60 s, recompute time {delta:.0f} s, 3 hours")
    print(f"{'policy':<14}{'beta':>5}{'recomputes/refresh':>20}{'miss ratio':>12}"
          f"{'mean lead (s)':>15}{'theory lead':>13}")
    runs = [("none", 1.0), ("lock", 1.0), ("xfetch", 0.5), ("xfetch", 1.0),
            ("xfetch", 2.0), ("xfetch+lock", 1.0)]
    for policy, beta in runs:
        r = simulate(policy, rate=rate, delta=delta, beta=beta)
        theory = (f"{delta * beta * (math.log(rate * delta * beta) + 0.5772):.2f}"
                  if policy.startswith("xfetch") else "-")
        print(f"{policy:<14}{beta:>5}{r['per_refresh']:>20.2f}{r['miss_ratio']:>12.4%}"
              f"{r['mean_lead']:>15.2f}{theory:>13}")
