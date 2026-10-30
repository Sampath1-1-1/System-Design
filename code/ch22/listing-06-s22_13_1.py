# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.13.1 (listing 6). Edit the manuscript, not this file.
import time
from collections import deque


class CircuitOpenError(Exception):
    """Raised instead of calling the dependency while the breaker is open."""


class CircuitBreaker:
    def __init__(self, failure_rate=0.5, window=20, open_for=5.0, probes=3,
                 clock=time.monotonic):
        self.failure_rate, self.window = failure_rate, window
        self.open_for, self.probes, self.clock = open_for, probes, clock
        self.state, self.opened_at = "closed", 0.0
        self.results = deque(maxlen=window)          # outcomes of the last `window` calls
        self.probes_sent = self.probe_successes = 0
        self.transitions = []

    def _move(self, state):
        self.transitions.append((round(self.clock(), 1), state))
        self.state = state

    def _allow(self):
        if self.state == "open":
            if self.clock() - self.opened_at < self.open_for:
                return False                         # fail fast: do not touch the dependency
            self._move("half_open")
            self.probes_sent = self.probe_successes = 0
        if self.state == "half_open":
            if self.probes_sent >= self.probes:      # only a few trial calls at a time
                return False
            self.probes_sent += 1
        return True

    def _record(self, ok):
        now = self.clock()
        if self.state == "half_open":
            if not ok:                               # dependency still sick: reopen
                self.opened_at = now
                self._move("open")
            else:
                self.probe_successes += 1
                if self.probe_successes >= self.probes:
                    self.results.clear()
                    self._move("closed")
            return
        self.results.append(ok)
        failures = self.results.count(False)
        if len(self.results) == self.window and failures / self.window >= self.failure_rate:
            self.opened_at = now
            self._move("open")

    def call(self, fn, *args, **kwargs):
        if not self._allow():
            raise CircuitOpenError("circuit open")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._record(False)
            raise
        self._record(True)
        return result


if __name__ == "__main__":
    from itertools import count

    class Clock:
        t = 0.0
        def __call__(self):
            return self.t

    clock = Clock()
    breaker = CircuitBreaker(clock=clock)
    reached = short_circuited = failed = 0

    def dependency():
        global reached
        reached += 1
        if 10.0 <= clock.t < 28.0:                   # outage from t = 10 s to t = 28 s
            raise ConnectionError("upstream down")
        return "ok"

    for i in count():                                # 20 requests per second for 60 s
        clock.t = i * 0.05
        if clock.t >= 60.0:
            break
        try:
            breaker.call(dependency)
        except CircuitOpenError:
            short_circuited += 1
        except ConnectionError:
            failed += 1

    print(f"requests 1200, reached dependency {reached}, failed {failed}, "
          f"short-circuited {short_circuited}")
    print("transitions:", breaker.transitions)
    assert breaker.state == "closed" and short_circuited > 350 and failed < 20
