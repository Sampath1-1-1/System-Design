# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.4.1 (listing 1). Edit the manuscript, not this file.
import random
import time


class FakeClock:
    """A controllable clock so tests are deterministic (time in seconds)."""
    def __init__(self, t=0.0):
        self.t = t
    def __call__(self):
        return self.t
    def advance(self, dt):
        self.t += dt


class TokenBucket:
    """Refill at `rate` tokens/s up to `capacity`; each request spends `cost` tokens."""
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate, self.capacity, self.clock = float(rate), float(capacity), clock
        self.tokens = float(capacity)          # start full: a new client may burst at once
        self.last = clock()

    def _refill(self):
        now = self.clock()
        elapsed = max(0.0, now - self.last)    # ignore a clock that steps backwards
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last = now

    def try_acquire(self, cost=1.0):
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def retry_after(self, cost=1.0):
        """Seconds until `cost` tokens are available: the value for a Retry-After header."""
        self._refill()
        return max(0.0, (cost - self.tokens) / self.rate)


if __name__ == "__main__":
    clock = FakeClock()
    tb = TokenBucket(rate=10, capacity=20, clock=clock)

    # 1. A burst of 50 requests at t = 0
    admitted = sum(tb.try_acquire() for _ in range(50))
    print(f"t=0.0 s burst of 50: admitted {admitted}, retry after {tb.retry_after():.2f} s")
    assert admitted == 20

    # 2. One second later the bucket has refilled 10 tokens
    clock.advance(1.0)
    admitted = sum(tb.try_acquire() for _ in range(50))
    print(f"t=1.0 s burst of 50: admitted {admitted}")
    assert admitted == 10

    # 3. Sustained 15 RPS for 10 s against a fresh (full) bucket
    clock, n_ok = FakeClock(), 0
    tb = TokenBucket(rate=10, capacity=20, clock=clock)
    for k in range(150):
        clock.t = k / 15
        n_ok += tb.try_acquire()
    bound = 20 + 10 * (149 / 15)               # b + r*T over the 9.93 s span
    print(f"15 RPS for 10 s: admitted {n_ok} of 150 (bound b + rT = {bound:.1f})")
    assert n_ok <= bound
