# Extracted from manuscript/book1-traditional/27-replication-and-fault-tolerance.md §27.10.2 (listing 2). Edit the manuscript, not this file.
"""A phi-accrual failure detector (Hayashibara et al. 2004) with a normal model."""
from collections import deque
from math import erfc, log10, sqrt
import random
import statistics

class PhiAccrualDetector:
    def __init__(self, window=1000, min_std_ms=50.0):
        self.intervals = deque(maxlen=window)   # recent heartbeat inter-arrival times
        self.last = None
        self.min_std = min_std_ms              # floor so a very regular sender is not hair-trigger

    def heartbeat(self, now_ms):
        if self.last is not None:
            self.intervals.append(now_ms - self.last)
        self.last = now_ms

    def phi(self, now_ms):
        if len(self.intervals) < 2:
            return 0.0
        mu = statistics.fmean(self.intervals)
        sigma = max(statistics.stdev(self.intervals), self.min_std)
        z = (now_ms - self.last - mu) / sigma
        p_later = 0.5 * erfc(z / sqrt(2))       # P(next heartbeat arrives even later)
        return -log10(max(p_later, 1e-300))

if __name__ == "__main__":
    random.seed(42)
    d = PhiAccrualDetector()
    t = 0.0
    for _ in range(1000):                       # heartbeats every ~1,000 ms, sd ~100 ms
        t += random.gauss(1000, 100)
        d.heartbeat(t)
    mu = statistics.fmean(d.intervals)
    sd = statistics.stdev(d.intervals)
    print(f"learned mean {mu:.0f} ms, std {sd:.0f} ms")
    for silence in (1000, 1200, 1400, 1500, 1600, 2000):
        print(f"silent for {silence:>4} ms -> phi = {d.phi(t + silence):6.2f}")
    s = 1000
    while d.phi(t + s) < 8:                     # when does phi cross the threshold of 8?
        s += 1
    print(f"phi reaches 8 after {s} ms of silence")
