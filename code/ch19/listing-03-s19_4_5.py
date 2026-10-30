# Extracted from manuscript/book1-traditional/19-load-balancing.md §19.4.5 (listing 3). Edit the manuscript, not this file.
"""Compare load-balancing policies on heterogeneous servers.

Ten FIFO servers: five 'slow' (1 request/s each) and five 'fast' (2 requests/s each).
Poisson arrivals, exponential service times. For each policy we record, for every
request, the queue length it finds at its chosen server (requests already there)
and its latency (waiting + service). Times are in units of the slow server's mean
service time.
"""
import random
from collections import deque

SPEEDS = [1.0] * 5 + [2.0] * 5          # service rate of each server, requests/s


def percentile(sorted_xs, p):
    """Nearest-rank percentile of an already sorted list."""
    k = max(0, min(len(sorted_xs) - 1, int(round(p / 100 * len(sorted_xs) + 0.5)) - 1))
    return sorted_xs[k]


class Policy:
    def __init__(self, n, rng):
        self.n, self.rng, self.i = n, rng, -1

    def pick(self, qlen):              # qlen[i] = requests at server i now
        raise NotImplementedError


class Random(Policy):
    def pick(self, qlen):
        return self.rng.randrange(self.n)


class RoundRobin(Policy):
    def pick(self, qlen):
        self.i = (self.i + 1) % self.n
        return self.i


class WeightedRR(Policy):              # smooth WRR, weights = server speeds
    def __init__(self, n, rng):
        super().__init__(n, rng)
        self.cur = [0.0] * n

    def pick(self, qlen):
        for s in range(self.n):
            self.cur[s] += SPEEDS[s]
        best = max(range(self.n), key=self.cur.__getitem__)
        self.cur[best] -= sum(SPEEDS)
        return best


class LeastConnections(Policy):        # global view, random tie-break
    def pick(self, qlen):
        m = min(qlen)
        return self.rng.choice([s for s in range(self.n) if qlen[s] == m])


class PowerOfTwo(Policy):              # sample two distinct servers, keep the shorter queue
    def pick(self, qlen):
        a, b = self.rng.sample(range(self.n), 2)
        if qlen[a] == qlen[b]:
            return self.rng.choice((a, b))
        return a if qlen[a] < qlen[b] else b


def simulate(policy_cls, load, refresh=0.0, requests=200_000, seed=1):
    """refresh > 0: the policy sees queue lengths that are refreshed only every
    `refresh` time units, as when many balancers share load reports."""
    rng = random.Random(seed)
    n = len(SPEEDS)
    lam = load * sum(SPEEDS)                       # arrival rate for target utilization
    policy = policy_cls(n, random.Random(seed + 1))
    departures = [deque() for _ in range(n)]       # FIFO departure times per server
    t, found, latency = 0.0, [], []
    view, next_refresh = [0] * n, 0.0
    for _ in range(requests):
        t += rng.expovariate(lam)
        for dq in departures:                      # drop requests that finished
            while dq and dq[0] <= t:
                dq.popleft()
        qlen = [len(dq) for dq in departures]
        if t >= next_refresh:                      # refresh = 0 means a live view
            view, next_refresh = qlen, t + refresh
        s = policy.pick(view)
        start = departures[s][-1] if departures[s] else t
        done = start + rng.expovariate(SPEEDS[s])
        departures[s].append(done)
        found.append(qlen[s])
        latency.append(done - t)
    warm = requests // 10                          # discard warm-up
    found, latency = sorted(found[warm:]), sorted(latency[warm:])
    return {
        "q_mean": sum(found) / len(found), "q_p99": percentile(found, 99),
        "q_max": found[-1], "lat_mean": sum(latency) / len(latency),
        "lat_p99": percentile(latency, 99),
    }


POLICIES = [Random, RoundRobin, WeightedRR, LeastConnections, PowerOfTwo]

if __name__ == "__main__":
    for load, refresh in ((0.6, 0.0), (0.85, 0.0), (0.85, 2.0)):
        print(f"\nLoad {load:.0%} of capacity, arrival rate {load * sum(SPEEDS):.2f}/s, "
              + ("live load view" if refresh == 0 else f"load view refreshed every {refresh:g} s"))
        print(f"{'policy':<17}{'queue mean':>11}{'queue p99':>10}{'queue max':>10}"
              f"{'lat mean':>10}{'lat p99':>9}")
        for cls in (POLICIES if refresh == 0 else POLICIES[2:]):   # load-aware only
            r = simulate(cls, load, refresh)
            print(f"{cls.__name__:<17}{r['q_mean']:>11.2f}{r['q_p99']:>10d}{r['q_max']:>10d}"
                  f"{r['lat_mean']:>10.2f}{r['lat_p99']:>9.2f}")
