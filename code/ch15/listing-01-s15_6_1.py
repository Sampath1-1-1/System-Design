# Extracted from manuscript/book1-traditional/15-object-block-file-storage.md §15.6.1 (listing 1). Edit the manuscript, not this file.
# A toy erasure code: XOR parity (m = 1) and a Reed-Solomon-style (k, m) code.
# The RS code works over the prime field GF(257) so the arithmetic is plain
# modular integer maths; production systems use GF(2^8) so every symbol is a byte.
import itertools
import random

P = 257  # prime modulus; symbols are integers 0..256


def xor_parity(blocks):
    """RAID-5 style parity: byte-wise XOR of all data blocks."""
    parity = bytearray(len(blocks[0]))
    for b in blocks:
        for i, byte in enumerate(b):
            parity[i] ^= byte
    return bytes(parity)


def lagrange_at(points, x):
    """Evaluate, at x, the unique polynomial of degree < len(points)
    passing through points [(xi, yi)], all arithmetic mod P."""
    total = 0
    for i, (xi, yi) in enumerate(points):
        num, den = 1, 1
        for j, (xj, _) in enumerate(points):
            if j != i:
                num = num * (x - xj) % P
                den = den * (xi - xj) % P
        total = (total + yi * num * pow(den, P - 2, P)) % P  # pow(.., P-2) = inverse
    return total


def rs_encode(data, k, m):
    """Systematic encoding of one stripe column: fragment i (i = 1..k) holds
    data[i-1]; parity fragments k+1..k+m hold the polynomial's values there."""
    pts = list(zip(range(1, k + 1), data))
    return data + [lagrange_at(pts, x) for x in range(k + 1, k + m + 1)]


def rs_decode(survivors, k):
    """Rebuild the k data symbols from ANY k surviving (index, value) pairs."""
    pts = survivors[:k]
    return [lagrange_at(pts, x) for x in range(1, k + 1)]


if __name__ == "__main__":
    # 1. XOR parity: lose any one block, rebuild it from the others.
    d = [b"GFS!", b"HDFS", b"S3ok"]
    p = xor_parity(d)
    rebuilt = xor_parity([d[0], d[2], p])  # pretend d[1] was lost
    print("XOR rebuilt block 1:", rebuilt, rebuilt == d[1])

    # 2. RS(4, 2): 4 data symbols, 2 parity symbols, survives ANY 2 losses.
    k, m = 4, 2
    data = [ord(c) for c in "EC4u"]
    stripe = rs_encode(data, k, m)
    print("stripe (data + parity):", stripe)
    ok = 0
    for lost in itertools.combinations(range(k + m), m):
        survivors = [(i + 1, v) for i, v in enumerate(stripe) if i not in lost]
        ok += rs_decode(survivors, k) == data
    print(f"RS({k},{m}) recovered data in {ok} of "
          f"{len(list(itertools.combinations(range(k + m), m)))} two-loss patterns")

    # 3. RS(10, 4) on random bytes: lose 4 random fragments, decode, compare.
    rng = random.Random(7)
    k, m = 10, 4
    data = [rng.randrange(256) for _ in range(k)]
    stripe = rs_encode(data, k, m)
    lost = set(rng.sample(range(k + m), m))
    survivors = [(i + 1, v) for i, v in enumerate(stripe) if i not in lost]
    print("RS(10,4) lost fragments", sorted(lost), "-> recovered:",
          rs_decode(survivors, k) == data, "| symbols read for repair:", k)
