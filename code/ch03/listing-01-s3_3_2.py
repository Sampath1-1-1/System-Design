# Extracted from manuscript/book1-traditional/03-learning-method.md §3.3.2 (listing 1). Edit the manuscript, not this file.
"""Simplified consistent-hashing ring with virtual nodes (teaching version)."""
import bisect
import hashlib
from collections import Counter


def h(key: str) -> int:
    """Map a string to a 64-bit integer position on the ring."""
    digest = hashlib.md5(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


class HashRing:
    def __init__(self, nodes=(), vnodes: int = 100):
        self.vnodes = vnodes
        self._positions = []   # sorted ring positions
        self._owner = {}       # position -> physical node name
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        for i in range(self.vnodes):
            pos = h(f"{node}#vn{i}")
            bisect.insort(self._positions, pos)
            self._owner[pos] = node

    def remove_node(self, node: str) -> None:
        for i in range(self.vnodes):
            pos = h(f"{node}#vn{i}")
            self._positions.remove(pos)
            del self._owner[pos]

    def get_node(self, key: str) -> str:
        """Return the first node clockwise from the key's position."""
        if not self._positions:
            raise LookupError("ring is empty")
        idx = bisect.bisect_right(self._positions, h(key))
        if idx == len(self._positions):  # wrap around past the top
            idx = 0
        return self._owner[self._positions[idx]]


def mod_n_node(key: str, nodes: list) -> str:
    """The naive scheme: hash(key) mod N."""
    return nodes[h(key) % len(nodes)]


if __name__ == "__main__":
    keys = [f"user:{i}" for i in range(100_000)]
    before = [f"cache-{i}" for i in range(4)]
    after = before + ["cache-4"]

    moved = sum(mod_n_node(k, before) != mod_n_node(k, after) for k in keys)
    print(f"mod-N : {moved / len(keys):.1%} of keys moved (4 -> 5 nodes)")

    for v in (1, 100):
        ring = HashRing(before, vnodes=v)
        old = {k: ring.get_node(k) for k in keys}
        ring.add_node("cache-4")
        moved = sum(old[k] != ring.get_node(k) for k in keys)
        load = Counter(ring.get_node(k) for k in keys)
        spread = max(load.values()) / (len(keys) / len(after))
        print(f"ring vnodes={v:<3}: {moved / len(keys):.1%} moved, "
              f"busiest node at {spread:.2f}x the mean load")
