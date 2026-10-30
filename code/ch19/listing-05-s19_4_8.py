# Extracted from manuscript/book1-traditional/19-load-balancing.md §19.4.8 (listing 5). Edit the manuscript, not this file.
"""Maglev lookup-table population (Eisenbud et al., NSDI 2016) and its disruption."""
import hashlib
from collections import Counter


def _h(s: str, salt: str) -> int:
    return int.from_bytes(hashlib.md5((salt + s).encode()).digest()[:8], "big")


def offset_skip(name: str, m: int):
    return _h(name, "offset") % m, _h(name, "skip") % (m - 1) + 1


def populate(backends, m, params=None):
    """Return a lookup table of size m (m prime). params optionally maps a
    backend name to a fixed (offset, skip) pair, for hand-checkable examples."""
    perms = []
    for b in backends:
        off, skip = params[b] if params else offset_skip(b, m)
        perms.append((off, skip))
    nxt = [0] * len(backends)        # next preference index for each backend
    table = [None] * m
    filled = 0
    while True:
        for i, (off, skip) in enumerate(perms):     # one turn per backend
            c = (off + nxt[i] * skip) % m
            while table[c] is not None:              # preferred slot taken: try next
                nxt[i] += 1
                c = (off + nxt[i] * skip) % m
            table[c] = backends[i]
            nxt[i] += 1
            filled += 1
            if filled == m:
                return table


if __name__ == "__main__":
    # Small example: M = 7, three backends with hand-picked offset and skip.
    p = {"B0": (3, 4), "B1": (0, 2), "B2": (3, 1)}
    print("B0..B2 table:", populate(["B0", "B1", "B2"], 7, p))
    print("B1 removed  :", populate(["B0", "B2"], 7, p))

    # Realistic size: M = 65,537 (prime), 100 backends; then backend-42 fails.
    M = 65_537
    names = [f"backend-{i}" for i in range(100)]
    before = populate(names, M)
    counts = Counter(before)
    print(f"entries per backend: min {min(counts.values())}, max {max(counts.values())}, "
          f"ideal {M / len(names):.1f}")
    after = populate([n for n in names if n != "backend-42"], M)
    changed = sum(1 for a, b in zip(before, after) if a != b)
    collateral = sum(1 for a, b in zip(before, after) if a != b and a != "backend-42")
    print(f"backend-42 removed: {changed / M:.2%} of entries changed "
          f"(minimum {counts['backend-42'] / M:.2%}); "
          f"{collateral / M:.2%} moved between surviving backends")
