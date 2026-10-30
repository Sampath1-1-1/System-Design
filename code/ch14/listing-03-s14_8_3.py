# Extracted from manuscript/book1-traditional/14-database-scaling.md §14.8.3 (listing 3). Edit the manuscript, not this file.
"""Consistent-hash ring with virtual nodes, weights and replica placement."""
import bisect
import hashlib
from collections import Counter


def h(key: str) -> int:
    """Map a string to a 64-bit ring position (MD5 used only for mixing)."""
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")


class HashRing:
    def __init__(self, vnodes_per_weight: int = 100):
        self.vpw = vnodes_per_weight
        self.weights = {}          # physical node -> weight
        self._positions = []       # sorted vnode positions
        self._owners = []          # owner of _positions[i]

    def _rebuild(self) -> None:
        points = sorted(
            (h(f"{node}#vn{i}"), node)
            for node, w in self.weights.items()
            for i in range(self.vpw * w)
        )
        self._positions = [p for p, _ in points]
        self._owners = [n for _, n in points]

    def add_node(self, node: str, weight: int = 1) -> None:
        self.weights[node] = weight
        self._rebuild()            # one sort per membership change

    def remove_node(self, node: str) -> None:
        del self.weights[node]
        self._rebuild()

    def _index(self, key: str) -> int:
        i = bisect.bisect_right(self._positions, h(key))
        return 0 if i == len(self._positions) else i   # wrap around

    def owner(self, key: str) -> str:
        return self._owners[self._index(key)]

    def preference_list(self, key: str, r: int) -> list:
        """First r *distinct physical* nodes clockwise from the key."""
        r = min(r, len(self.weights))
        result, i = [], self._index(key)
        while len(result) < r:
            node = self._owners[i]
            if node not in result:
                result.append(node)
            i = (i + 1) % len(self._owners)
        return result


if __name__ == "__main__":
    keys = [f"user:{i}" for i in range(200_000)]
    ring = HashRing(vnodes_per_weight=128)
    for n in range(8):
        ring.add_node(f"db-{n}")

    before = {k: ring.owner(k) for k in keys}
    ring.add_node("db-8")
    after = {k: ring.owner(k) for k in keys}
    moved = [k for k in keys if before[k] != after[k]]
    print(f"add 9th node : {len(moved) / len(keys):.2%} of keys moved "
          f"(theory 1/9 = {1 / 9:.2%}); all moved keys went to "
          f"{set(after[k] for k in moved)}")

    share = sum(1 for k in keys if after[k] == "db-3") / len(keys)
    ring.remove_node("db-3")
    gone = {k: ring.owner(k) for k in keys}
    moved = [k for k in keys if after[k] != gone[k]]
    receivers = Counter(gone[k] for k in moved)
    print(f"remove db-3  : {len(moved) / len(keys):.2%} moved, exactly db-3's "
          f"share ({share:.2%}); spread over {len(receivers)} survivors, "
          f"largest receiver took {max(receivers.values()) / len(moved):.0%}")

    ring.add_node("db-big", weight=2)        # twice the vnodes
    load = Counter(ring.owner(k) for k in keys)
    mean = len(keys) / (len(ring.weights) + 1)   # db-big counts as two
    print(f"weighted node: db-big holds {load['db-big'] / mean:.2f}x a "
          f"weight-1 share")
    print("replicas of user:42 ->", ring.preference_list("user:42", 3))
