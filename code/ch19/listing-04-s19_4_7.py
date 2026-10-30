# Extracted from manuscript/book1-traditional/19-load-balancing.md §19.4.7 (listing 4). Edit the manuscript, not this file.
"""Consistent hashing with bounded loads (Mirrokni, Thorup & Zadimoghaddam)."""
import bisect
import hashlib
import math
import random
from collections import Counter


def h(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


class Ring:
    def __init__(self, servers, vnodes=100):
        pts = sorted((h(f"{s}#{v}"), s) for s in servers for v in range(vnodes))
        self.pos = [p for p, _ in pts]
        self.owner = [s for _, s in pts]
        self.servers = list(servers)

    def assign(self, keys, eps=None):
        """Place each key (a request or session) in order. eps=None: plain
        consistent hashing. Otherwise no server may exceed ceil((1+eps)*m/n)."""
        cap = math.inf if eps is None else math.ceil((1 + eps) * len(keys) / len(self.servers))
        load, where = Counter(), []
        for k in keys:
            i = bisect.bisect_right(self.pos, h(k)) % len(self.pos)
            while load[self.owner[i]] >= cap:         # full: keep walking clockwise
                i = (i + 1) % len(self.pos)
            load[self.owner[i]] += 1
            where.append(self.owner[i])
        return load, where


if __name__ == "__main__":
    rng = random.Random(7)
    servers = [f"cache-{i}" for i in range(40)]
    # 10,000 in-flight requests for 2,000 objects with Zipf(1.0) popularity:
    # every request for the same object hashes to the same point.
    objects = [f"video:{i}" for i in range(2_000)]
    zipf_w = [1 / (r + 1) for r in range(len(objects))]
    requests = rng.choices(objects, weights=zipf_w, k=10_000)
    avg = len(requests) / len(servers)
    ring = Ring(servers)
    for eps in (None, 1.0, 0.25):
        load, where = ring.assign(requests, eps)
        first = sum(1 for k, s in zip(requests, where)
                    if s == ring.owner[bisect.bisect_right(ring.pos, h(k)) % len(ring.pos)])
        label = "plain ring" if eps is None else f"bounded eps={eps}"
        print(f"{label:<18} max load {max(load.values()):5d} ({max(load.values()) / avg:4.2f}x avg)"
              f"  on first-choice server {first / len(requests):6.1%}")

    # Membership change: add a 41st server, count requests that change server.
    bigger = Ring(servers + ["cache-40"])
    for eps in (None, 1.0, 0.25):
        _, before = ring.assign(requests, eps)
        _, after = bigger.assign(requests, eps)
        moved = sum(1 for a, b in zip(before, after) if a != b) / len(requests)
        print(f"add 41st server, eps={eps}: {moved:5.1%} of requests change server")
