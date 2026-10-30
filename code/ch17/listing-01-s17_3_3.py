# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.3.3 (listing 1). Edit the manuscript, not this file.

def murmur3_32(data: bytes, seed: int = 0) -> int:
    """MurmurHash3 x86_32 (Appleby), pure Python. Returns an unsigned 32-bit int."""
    c1, c2, mask = 0xCC9E2D51, 0x1B873593, 0xFFFFFFFF
    h = seed & mask
    n_blocks = len(data) // 4
    for i in range(n_blocks):                      # body: 4-byte little-endian blocks
        k = int.from_bytes(data[4 * i:4 * i + 4], "little")
        k = (k * c1) & mask
        k = ((k << 15) | (k >> 17)) & mask         # rotl32(k, 15)
        k = (k * c2) & mask
        h ^= k
        h = ((h << 13) | (h >> 19)) & mask         # rotl32(h, 13)
        h = (h * 5 + 0xE6546B64) & mask
    tail, k = data[4 * n_blocks:], 0               # tail: remaining 1-3 bytes
    for i, byte in enumerate(tail):
        k |= byte << (8 * i)
    if tail:
        k = (k * c1) & mask
        k = ((k << 15) | (k >> 17)) & mask
        k = (k * c2) & mask
        h ^= k
    h ^= len(data)                                 # finalization ("fmix32")
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & mask
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & mask
    h ^= h >> 16
    return h

def additive_hash(data: bytes) -> int:
    """A deliberately bad hash: sum of byte values."""
    return sum(data)

def bucket_stats(hash_fn, keys, buckets):
    counts = [0] * buckets
    for key in keys:
        counts[hash_fn(key) % buckets] += 1
    expected = len(keys) / buckets
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    return max(counts), sum(1 for c in counts if c == 0), chi2

print(f"murmur3_32('hello') = {murmur3_32(b'hello'):#010x}")   # reference: 0x248bfa47

# 100,000 realistic, highly structured keys: "user:0" ... "user:99999"
keys = [f"user:{i}".encode() for i in range(100_000)]
B = 1024                                           # expected ~97.7 keys per bucket
for name, fn in [("additive", additive_hash), ("murmur3", murmur3_32)]:
    mx, empty, chi2 = bucket_stats(fn, keys, B)
    print(f"{name:9s} max bucket = {mx:6d}  empty buckets = {empty:4d}  chi-square = {chi2:12.0f}")
