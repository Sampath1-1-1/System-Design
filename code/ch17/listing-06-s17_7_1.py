# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.7.1 (listing 6). Edit the manuscript, not this file.
import math
import random

class Node:
    __slots__ = ("key", "forward")
    def __init__(self, key, level):
        self.key, self.forward = key, [None] * level

class SkipList:
    """Pugh's skip list with promotion probability p (Redis uses p = 0.25, max level 32)."""

    def __init__(self, p: float = 0.25, max_level: int = 32, seed: int = 0):
        self.p, self.max_level = p, max_level
        self.head = Node(None, max_level)
        self.level = 1
        self.pointers = 0                                # total forward pointers allocated
        self.rng = random.Random(seed)

    def _random_level(self) -> int:
        lvl = 1
        while self.rng.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def insert(self, key) -> None:
        update, x = [self.head] * self.max_level, self.head
        for i in reversed(range(self.level)):           # descend, remembering the last node per level
            while x.forward[i] and x.forward[i].key < key:
                x = x.forward[i]
            update[i] = x
        lvl = self._random_level()
        self.level = max(self.level, lvl)
        node = Node(key, lvl)
        self.pointers += lvl
        for i in range(lvl):                             # splice in at each of its levels
            node.forward[i], update[i].forward[i] = update[i].forward[i], node

    def search(self, key):
        """Return (found, number of key comparisons)."""
        x, steps = self.head, 0
        for i in reversed(range(self.level)):
            while x.forward[i] and x.forward[i].key < key:
                x, steps = x.forward[i], steps + 1
            steps += 1                                   # the comparison that stopped us
        x = x.forward[0]
        return (x is not None and x.key == key), steps

    def range(self, lo, hi):
        """All keys in [lo, hi]: find lo in O(log n), then walk level 0."""
        x = self.head
        for i in reversed(range(self.level)):
            while x.forward[i] and x.forward[i].key < lo:
                x = x.forward[i]
        x, out = x.forward[0], []
        while x and x.key <= hi:
            out.append(x.key)
            x = x.forward[0]
        return out

for p in (0.5, 0.25):
    for n in (10_000, 100_000, 1_000_000):
        sl = SkipList(p=p, seed=42)
        keys = list(range(n))
        random.Random(1).shuffle(keys)
        for k in keys:
            sl.insert(k)
        probe = random.Random(2).sample(range(n), 2_000)
        avg = sum(sl.search(k)[1] for k in probe) / len(probe)
        L = math.log(n, 1 / p)
        bound = L / p + 1 / (1 - p)                       # Pugh's expected-cost bound
        print(f"p={p:<4} n={n:>9,}  levels={sl.level:2d}  log_1/p(n)={L:5.1f}  "
              f"avg comparisons={avg:5.1f}  Pugh bound={bound:5.1f}  "
              f"pointers/node={sl.pointers / n:4.2f} (expect {1 / (1 - p):4.2f})")
print("range(500, 505):", sl.range(500, 505))
