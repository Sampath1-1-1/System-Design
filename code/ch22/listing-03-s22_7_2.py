# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.7.2 (listing 3). Edit the manuscript, not this file.
import math
import random
from collections import deque


class FixedWindow:
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self.start, self.count = None, 0

    def try_acquire(self, now):
        start = math.floor(now / self.window) * self.window
        if start != self.start:                      # a new window: reset the counter
            self.start, self.count = start, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingLog:
    def __init__(self, limit, window):
        self.limit, self.window, self.log = limit, window, deque()

    def try_acquire(self, now):
        while self.log and self.log[0] <= now - self.window:
            self.log.popleft()                       # forget requests older than one window
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False


class SlidingWindowCounter:
    """Two counters per key; estimate = prev * (overlap fraction) + curr."""
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self.start, self.curr, self.prev = 0.0, 0, 0

    def estimate(self, now):
        start = math.floor(now / self.window) * self.window
        if start != self.start:                      # roll forward
            gap = round((start - self.start) / self.window)
            self.prev = self.curr if gap == 1 else 0  # an idle gap > 1 window empties both
            self.curr, self.start = 0, start
        overlap = 1.0 - (now - start) / self.window  # share of previous window still inside
        return self.prev * overlap + self.curr

    def try_acquire(self, now):
        if self.estimate(now) + 1 <= self.limit:     # never let the estimate exceed the limit
            self.curr += 1
            return True
        return False


def boundary_burst(limiter):
    """100 requests in the last second of a minute, 100 in the first second of the next."""
    times = [59 + i / 100 for i in range(100)] + [60 + i / 100 for i in range(100)]
    return sum(limiter.try_acquire(t) for t in times)


if __name__ == "__main__":
    L, W = 100, 60.0
    print("Boundary burst (limit 100 per 60 s, 200 requests within 2 s):")
    for name, cls in [("fixed window", FixedWindow), ("sliding log", SlidingLog),
                      ("sliding counter", SlidingWindowCounter)]:
        print(f"  {name:16s} admitted {boundary_burst(cls(L, W))}")

    # Worked example of section 22.7: prev = 84, curr = 36, 15 s into the window
    swc = SlidingWindowCounter(L, W)
    swc.start, swc.prev, swc.curr = 60.0, 84, 36
    print(f"\nestimate at t=75 s: {swc.estimate(75.0):.1f}; "
          f"next two requests: {swc.try_acquire(75.0)}, {swc.try_acquire(75.0)}")

    # Accuracy against the exact sliding log: 4 hours of random traffic
    def worst_window(ts):                            # most admitted requests in any 60 s span
        best, j = 0, 0
        for i, x in enumerate(ts):
            while ts[j] <= x - W:
                j += 1
            best = max(best, i - j + 1)
        return best

    print("\npattern  RPS  offered  | log: admitted worst60 | counter: admitted worst60 "
          "| fixed: admitted worst60")
    for pattern in ("steady", "on/off"):             # on/off: 40 s on, 20 s silent
        for rate in (1.5, 3.0):
            rng, times, t = random.Random(42), [], 0.0
            while t < 4 * 3600:
                t += rng.expovariate(rate)
                if pattern == "steady" or int(t // 20) % 3 != 2:
                    times.append(t)
            row = []
            for cls in (SlidingLog, SlidingWindowCounter, FixedWindow):
                lim = cls(L, W)
                ok = [x for x in times if lim.try_acquire(x)]
                row.append(f"{len(ok):>6} {worst_window(ok):>4}")
            print(f"{pattern:7s} {rate:4.1f} {len(times):>8}  |  " + "      |  ".join(row))

    assert boundary_burst(FixedWindow(L, W)) == 200
    assert boundary_burst(SlidingLog(L, W)) == 100
