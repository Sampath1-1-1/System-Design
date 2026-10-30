# Extracted from manuscript/book1-traditional/23-performance-engineering.md §23.5.3 (listing 2). Edit the manuscript, not this file.
import math
import random

RATE = 500                    # intended request rate, requests/second
INTERVAL = 1 / RATE           # 2 ms between scheduled sends
DURATION = 60.0               # seconds of test
STALL = (30.0, 31.5)          # server freezes for 1.5 s (GC pause, failover...)

class Server:
    """Single-threaded FIFO server; service time ~1 ms; one 1.5 s stall."""
    def __init__(self, seed=1):
        self.rng = random.Random(seed)
        self.free_at = 0.0
    def submit(self, t):
        start = max(t, self.free_at)
        if STALL[0] <= start < STALL[1]:          # frozen: wait for the stall to end
            start = STALL[1]
        service = 0.0008 + self.rng.expovariate(1 / 0.0002)
        if start < STALL[0] < start + service:    # stall hits mid-request
            service += STALL[1] - STALL[0]
        self.free_at = start + service
        return self.free_at                       # completion time

def closed_loop():
    """Naive tester: one connection; waits for each reply before sending the
    next; measures from the actual send time (like wrk or a simple script)."""
    server, t, lat = Server(), 0.0, []
    while t < DURATION:
        done = server.submit(t)
        lat.append(done - t)
        t = max(t + INTERVAL, done)               # late? just carry on from now
    return lat

def corrected(lat):
    """HdrHistogram-style correction: a reply that took v > INTERVAL implies
    missed sends that would have seen v - INTERVAL, v - 2*INTERVAL, ..."""
    out = []
    for v in lat:
        out.append(v)
        missing = v - INTERVAL
        while missing > INTERVAL:
            out.append(missing)
            missing -= INTERVAL
    return out

def open_loop():
    """Correct tester: sends on a fixed schedule whatever happens and measures
    from the *intended* send time (like wrk2, or k6 constant-arrival-rate)."""
    server, lat = Server(), []
    for i in range(int(DURATION * RATE)):
        t = i * INTERVAL
        lat.append(server.submit(t) - t)
    return lat

def pct(sorted_ms, q):
    return sorted_ms[max(math.ceil(q / 100 * len(sorted_ms)), 1) - 1]

print(f"{'tester':<22}{'count':>7}{'p50':>8}{'p90':>8}{'p99':>8}"
      f"{'p99.9':>8}{'max':>8}   (ms)")
for name, lat in (("closed loop (naive)", closed_loop()),
                  ("closed + correction", corrected(closed_loop())),
                  ("open loop (truth)", open_loop())):
    ms = sorted(v * 1000 for v in lat)
    print(f"{name:<22}{len(ms):>7}" +
          "".join(f"{pct(ms, q):>8.1f}" for q in (50, 90, 99, 99.9)) +
          f"{ms[-1]:>8.0f}")
