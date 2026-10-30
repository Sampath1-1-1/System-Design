# Extracted from manuscript/book1-traditional/29-distributed-data-processing.md §29.8.3 (listing 5). Edit the manuscript, not this file.
"""Event-time windowing with a bounded-out-of-orderness watermark, allowed lateness,
on-time and late firings, and a side output for events that arrive too late."""
import math
import random


class EventTimeWindower:
    def __init__(self, size, slide=None, max_out_of_orderness=0.0, allowed_lateness=0.0):
        self.size, self.slide = size, slide or size        # slide == size -> tumbling windows
        self.delta, self.lateness = max_out_of_orderness, allowed_lateness
        self.max_ts = -math.inf
        self.state = {}             # keyed window state: (key, window_start) -> count
        self.fired = set()          # windows that already emitted their on-time result
        self.output = []            # (kind, key, start, end, count, emitted_at)
        self.dropped = []           # side output: (event_time, key, window_start)

    @property
    def watermark(self):            # "no more events older than this are expected"
        return self.max_ts - self.delta

    def window_starts(self, ts):
        start = math.floor(ts / self.slide) * self.slide
        starts = []
        while start > ts - self.size:                       # every window [s, s+size) holding ts
            starts.append(start)
            start -= self.slide
        return starts

    def on_event(self, ts, key, now):
        for start in self.window_starts(ts):
            w = (key, start)
            if self.watermark >= start + self.size + self.lateness:
                self.dropped.append((ts, key, start))       # state already purged: too late
                continue
            self.state[w] = self.state.get(w, 0) + 1
            if w in self.fired:                             # late, but within allowed lateness
                self.output.append(("LATE", key, start, start + self.size, self.state[w], now))
        self.max_ts = max(self.max_ts, ts)
        self._on_watermark(now)

    def _on_watermark(self, now):
        wm = self.watermark
        for w in sorted(self.state):
            key, start = w
            end = start + self.size
            if wm >= end and w not in self.fired:           # event-time trigger
                self.fired.add(w)
                self.output.append(("ON_TIME", key, start, end, self.state[w], now))
            if wm >= end + self.lateness:                   # garbage-collect window state
                del self.state[w]
                self.fired.discard(w)

    def end_of_input(self, now):
        self.max_ts = math.inf                              # final watermark flushes everything
        self._on_watermark(now)


def run(events, **cfg):
    """events: (event_time, key, arrival_time); processed in arrival order."""
    op = EventTimeWindower(**cfg)
    for ts, key, arrival in sorted(events, key=lambda e: e[2]):
        op.on_event(ts, key, arrival)
    op.end_of_input(max(e[2] for e in events))
    return op


def late_fraction_model(mean_delay, delta, size):
    """P(event misses its tumbling window) for exponential delays, uniform position in window."""
    return (mean_delay / size) * math.exp(-delta / mean_delay) * (1 - math.exp(-size / mean_delay))


if __name__ == "__main__":
    # Scenario: 10 s tumbling windows, watermark 2 s behind max event time, 5 s allowed lateness.
    ev = [(1, "a", 1.2), (4, "a", 4.1), (8, "a", 8.3), (13, "a", 13.0),   # wm reaches 11 -> fire [0,10)
          (9, "a", 13.5),                                                 # late, within lateness
          (23, "a", 23.0),                                                # wm 21 -> fire [10,20)
          (7, "a", 23.4),                                                 # wm 21 >= 10+5 -> dropped
          (15, "a", 23.6)]                                                # late update for [10,20)
    op = run(ev, size=10, max_out_of_orderness=2, allowed_lateness=5)
    for row in op.output:
        print(row)
    print("dropped:", op.dropped)
    assert op.output[0] == ("ON_TIME", "a", 0, 10, 3, 13.0)
    assert op.output[1] == ("LATE", "a", 0, 10, 4, 13.5)
    assert ("ON_TIME", "a", 10, 20, 1, 23.0) in op.output
    assert ("LATE", "a", 10, 20, 2, 23.6) in op.output
    assert op.dropped == [(7, "a", 0)]

    # Sliding windows: size 10, slide 5 -> each event lands in two windows.
    sl = run([(7, "k", 7), (12, "k", 12), (40, "k", 40)], size=10, slide=5)
    assert [(r[2], r[4]) for r in sl.output if r[0] == "ON_TIME"][:3] == [(0, 1), (5, 2), (10, 1)]

    # Simulation: 50 events/s for 2 h, exponential network delay (mean 2 s), 60 s windows.
    rng = random.Random(42)
    events, t = [], 0.0
    while t < 7200:
        t += rng.expovariate(50)
        events.append((t, "clicks", t + rng.expovariate(1 / 2.0)))
    print(f"{'delta s':>7} {'late model':>10} {'late sim':>9} {'emit delay s':>12}")
    for delta in (0, 2, 5, 10):
        op = run(events, size=60, max_out_of_orderness=delta, allowed_lateness=0)
        sim = len(op.dropped) / len(events)
        counted = sum(r[4] for r in op.output if r[0] == "ON_TIME")
        assert counted + len(op.dropped) == len(events)            # nothing lost silently
        on_time = [r for r in op.output if r[0] == "ON_TIME" and r[3] < 7200]
        lag = sum(r[5] - r[3] for r in on_time) / len(on_time)      # emission time - window end
        print(f"{delta:>7} {late_fraction_model(2.0, delta, 60):>10.4%} {sim:>9.4%} {lag:>12.2f}")
    print("all tests passed")
