# Extracted from manuscript/book1-traditional/15-object-block-file-storage.md §15.8.3 (listing 2). Edit the manuscript, not this file.
# Content-defined chunking (CDC) versus fixed-size chunking, LBFS-style parameters.
# A Rabin-Karp polynomial rolling hash stands in for a true Rabin fingerprint
# (which uses polynomial arithmetic over GF(2)); the boundary logic is the same.
import hashlib
import random

WINDOW = 48                      # bytes in the rolling window (as in LBFS)
MASK = (1 << 13) - 1             # 13 low bits -> expected chunk ~ 2^13 = 8 KiB
MAGIC = 0x78                     # boundary when (hash & MASK) == MAGIC
MIN_CHUNK, MAX_CHUNK = 2 * 1024, 64 * 1024
BASE, MOD = 257, (1 << 61) - 1
BASE_OUT = pow(BASE, WINDOW, MOD)  # weight of the byte leaving the window


def cdc_chunks(data):
    chunks, start, h = [], 0, 0
    for i, byte in enumerate(data):
        h = (h * BASE + byte) % MOD
        if i >= WINDOW:
            h = (h - data[i - WINDOW] * BASE_OUT) % MOD   # roll the oldest byte out
        size = i - start + 1
        if (size >= MIN_CHUNK and (h & MASK) == MAGIC) or size >= MAX_CHUNK:
            chunks.append(data[start:i + 1])
            start = i + 1
    if start < len(data):
        chunks.append(data[start:])
    return chunks


def fixed_chunks(data, size=8 * 1024):
    return [data[i:i + size] for i in range(0, len(data), size)]


def shared_fraction(old, new):
    """Fraction of the new version's bytes found in chunks already stored."""
    stored = {hashlib.sha256(c).digest() for c in old}
    reused = sum(len(c) for c in new if hashlib.sha256(c).digest() in stored)
    return reused / sum(len(c) for c in new)


if __name__ == "__main__":
    rng = random.Random(42)
    v1 = bytes(rng.randrange(256) for _ in range(2_000_000))   # 2 MB "file"
    v2 = b"inserted header!" + v1[:900_000] + b"edit" + v1[900_000:]

    for name, chunker in (("fixed 8 KiB", fixed_chunks), ("content-defined", cdc_chunks)):
        a, b = chunker(v1), chunker(v2)
        avg = sum(map(len, a)) / len(a)
        print(f"{name:16s} chunks={len(a):4d} avg={avg:8.0f} B "
              f"reused after edit={shared_fraction(a, b):6.1%}")
