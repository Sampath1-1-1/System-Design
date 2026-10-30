# Extracted from manuscript/book1-traditional/19-load-balancing.md §19.4.1 (listing 1). Edit the manuscript, not this file.
"""Smooth weighted round robin, the algorithm NGINX uses for weighted upstreams."""
from collections import Counter


class SmoothWRR:
    def __init__(self, weights: dict):
        self.weights = dict(weights)              # server -> configured weight
        self.current = {s: 0 for s in weights}    # server -> current weight
        self.total = sum(weights.values())

    def pick(self) -> str:
        # 1. Every server earns its weight.
        for s, w in self.weights.items():
            self.current[s] += w
        # 2. The richest server wins (ties: first in insertion order).
        best = max(self.current, key=self.current.get)
        # 3. The winner pays the total, so it falls behind the others.
        self.current[best] -= self.total
        return best


def naive_wrr(weights: dict) -> list:
    """Repeat each server w times in a row: correct shares, bursty order."""
    return [s for s, w in weights.items() for _ in range(w)]


if __name__ == "__main__":
    w = {"a": 5, "b": 1, "c": 1}
    lb = SmoothWRR(w)
    seq = [lb.pick() for _ in range(7)]
    print("naive :", " ".join(naive_wrr(w)))
    print("smooth:", " ".join(seq))
    assert seq == ["a", "a", "b", "a", "c", "a", "a"]

    w2 = {"s1": 1, "s2": 2, "s3": 4}               # 8, 16 and 32 cores
    lb2 = SmoothWRR(w2)
    counts = Counter(lb2.pick() for _ in range(7_000))
    print("shares over 7,000 picks:", dict(counts))
    assert counts == {"s1": 1_000, "s2": 2_000, "s3": 4_000}
