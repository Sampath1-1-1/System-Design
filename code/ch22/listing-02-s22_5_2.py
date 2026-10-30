# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.5.2 (listing 2). Edit the manuscript, not this file.
import random


class GCRA:
    """Generic Cell Rate Algorithm, virtual-scheduling form. State per key: one integer (TAT).
    Times are integer nanoseconds so that repeated additions do not drift."""
    def __init__(self, rate, burst):
        self.T = round(1e9 / rate)          # emission interval (ns): ideal gap between requests
        self.tau = (burst - 1) * self.T     # tolerance (ns): how far ahead of schedule we accept
        self.tat = None                     # theoretical arrival time of the next request

    def try_acquire(self, now_s):
        now = round(now_s * 1e9)
        tat = now if self.tat is None else max(self.tat, now)
        if tat - now > self.tau:            # arrived earlier than TAT - tau: non-conforming
            return False
        self.tat = tat + self.T             # conforming: push the schedule one interval out
        return True

    def retry_after(self, now_s):
        """Seconds until the next request would conform."""
        return max(0.0, (self.tat - self.tau) / 1e9 - now_s)


def token_bucket_decisions(rate, capacity, times):
    """Reference token bucket (starts full) for comparison."""
    tokens, last, out = float(capacity), times[0], []
    for t in times:
        tokens = min(capacity, tokens + (t - last) * rate)
        last = t
        ok = tokens >= 1.0
        tokens -= 1.0 if ok else 0.0
        out.append(ok)
    return out


if __name__ == "__main__":
    g = GCRA(rate=10, burst=20)
    burst = [g.try_acquire(0.0) for _ in range(50)]
    print(f"burst of 50 at t=0: admitted {sum(burst)}, retry after {g.retry_after(0.0):.2f} s")

    # Equivalence check on 100,000 random arrivals (Poisson, average 14 RPS)
    rng = random.Random(7)
    times, t = [], 0.0
    for _ in range(100_000):
        t += rng.expovariate(14.0)
        times.append(t)
    g = GCRA(rate=10, burst=20)
    gcra = [g.try_acquire(x) for x in times]
    tb = token_bucket_decisions(10, 20, times)
    mismatches = sum(a != b for a, b in zip(gcra, tb))
    print(f"admitted: GCRA {sum(gcra)}, token bucket {sum(tb)}; "
          f"decisions that differ: {mismatches}")
    assert sum(burst) == 20 and mismatches == 0
