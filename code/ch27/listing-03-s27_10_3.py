# Extracted from manuscript/book1-traditional/27-replication-and-fault-tolerance.md §27.10.3 (listing 3). Edit the manuscript, not this file.
"""Rounds for a rumor to reach every node: push, pull and push-pull gossip,
plus SWIM's expected time to first detection of a crashed member."""
import math
import random
import statistics

def spread(n, mode, fanout=1, rng=random):
    """Synchronous rounds: every node contacts `fanout` random peers per round."""
    informed = [False] * n
    informed[0] = True
    count, rounds = 1, 0
    while count < n:
        rounds += 1
        new = informed[:]                        # updates take effect next round
        for node in range(n):
            for _ in range(fanout):
                peer = rng.randrange(n - 1)
                peer += peer >= node             # a random peer other than itself
                if mode in ("push", "push-pull") and informed[node]:
                    new[peer] = True             # push: informed node tells peer
                if mode in ("pull", "push-pull") and informed[peer]:
                    new[node] = True             # pull: node asks peer for news
        informed = new
        count = sum(informed)
    return rounds

def swim_first_detection(n, rng=random):
    """Protocol periods until some live member pings the one crashed member."""
    periods = 0
    while True:
        periods += 1
        # each of the n-1 live members pings one random other member
        if any(rng.randrange(n - 1) == 0 for _ in range(n - 1)):
            return periods

if __name__ == "__main__":
    rng = random.Random(2026)
    n, trials = 1000, 100
    print(f"n = {n}, fanout 1, {trials} trials each")
    for mode in ("push", "pull", "push-pull"):
        r = [spread(n, mode, 1, rng) for _ in range(trials)]
        print(f"  {mode:9s}: mean {statistics.fmean(r):5.2f} rounds, max {max(r)}")
    print(f"  model log2(n) + ln(n) = {math.log2(n) + math.log(n):.2f} rounds (push)")
    for f in (2, 3):
        r = [spread(n, "push", f, rng) for _ in range(trials)]
        model = math.log(n, 1 + f) + math.log(n) / f
        print(f"  push, fanout {f}: mean {statistics.fmean(r):5.2f}, model {model:5.2f}")
    for size in (100, 1000, 10000):
        print(f"  push, n = {size:>5}: mean "
              f"{statistics.fmean(spread(size, 'push', 1, rng) for _ in range(30)):5.2f} rounds")

    d = [swim_first_detection(n, rng) for _ in range(5000)]
    print(f"SWIM first detection: mean {statistics.fmean(d):.3f} periods, "
          f"e/(e-1) = {math.e / (math.e - 1):.3f}")
