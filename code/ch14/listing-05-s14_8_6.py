# Extracted from manuscript/book1-traditional/14-database-scaling.md §14.8.6 (listing 5). Edit the manuscript, not this file.
"""Jump consistent hash and rendezvous (HRW) hashing, compared on movement and balance."""
import hashlib
import statistics

MASK64 = (1 << 64) - 1


def h64(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode("utf-8")).digest()[:8], "big")


def jump_hash(key: int, num_buckets: int) -> int:
    """Lamping & Veach (2014): 64-bit key -> bucket in [0, num_buckets)."""
    b, j = -1, 0
    while j < num_buckets:
        b = j
        key = (key * 2862933555777941757 + 1) & MASK64   # 64-bit LCG step
        j = int((b + 1) * (float(1 << 31) / float((key >> 33) + 1)))
    return b


def rendezvous(key: str, nodes: list) -> str:
    """Highest random weight: every node scores the key; the top score wins."""
    return max(nodes, key=lambda node: h64(f"{node}|{key}"))


def report(name, assign_before, assign_after, keys, n_after):
    moved = sum(assign_before(k) != assign_after(k) for k in keys) / len(keys)
    counts = {}
    for k in keys:
        b = assign_after(k)
        counts[b] = counts.get(b, 0) + 1
    mean = len(keys) / n_after
    cv = statistics.pstdev(counts.values()) / mean
    print(f"{name:<11} moved {moved:6.2%} (ideal {1 / n_after:.2%})  "
          f"key-count CV {cv:.4f}  max/mean {max(counts.values()) / mean:.3f}")


if __name__ == "__main__":
    keys = [f"order:{i}" for i in range(100_000)]
    hashed = {k: h64(k) for k in keys}
    n = 10
    names = [f"db-{i}" for i in range(n + 1)]
    report("jump", lambda k: jump_hash(hashed[k], n),
           lambda k: jump_hash(hashed[k], n + 1), keys, n + 1)
    report("rendezvous", lambda k: rendezvous(k, names[:n]),
           lambda k: rendezvous(k, names), keys, n + 1)
    # Binomial noise alone (perfectly fair assignment of 100,000 random keys)
    p = 1 / (n + 1)
    print(f"{'noise floor':<11} key-count CV of a perfect hash = "
          f"{((1 - p) / (len(keys) * p)) ** 0.5:.4f}")
