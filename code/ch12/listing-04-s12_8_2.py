# Extracted from manuscript/book1-traditional/12-nosql-databases.md §12.8.2 (listing 4). Edit the manuscript, not this file.
"""Gorilla-style compression (Pelkonen et al., VLDB 2015): delta-of-delta
timestamps and XOR-encoded float values. Counts bits; returns bits per point."""
import random
import struct

def float_bits(x: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", x))[0]

def encode(points):
    """points: list of (unix_seconds, float). Returns total bits used."""
    t0, v0 = points[0]
    bits = 64 + 64                          # first timestamp and value stored raw
    prev_t, prev_delta, prev_v = t0, 0, float_bits(v0)
    prev_lead, prev_trail = None, None
    for t, v in points[1:]:
        delta = t - prev_t
        dod = delta - prev_delta            # delta of delta
        if dod == 0:
            bits += 1                                   # '0'
        elif -63 <= dod <= 64:
            bits += 2 + 7                               # '10' + 7 bits
        elif -255 <= dod <= 256:
            bits += 3 + 9                               # '110' + 9 bits
        elif -2047 <= dod <= 2048:
            bits += 4 + 12                              # '1110' + 12 bits
        else:
            bits += 4 + 32                              # '1111' + 32 bits
        prev_t, prev_delta = t, delta

        x = float_bits(v) ^ prev_v
        if x == 0:
            bits += 1                                   # '0': value repeated
        else:
            lead = min(64 - x.bit_length(), 31)         # 5-bit field caps at 31
            trail = (x & -x).bit_length() - 1
            if prev_lead is not None and lead >= prev_lead and trail >= prev_trail:
                bits += 2 + (64 - prev_lead - prev_trail)   # '10' + reuse window
            else:
                bits += 2 + 5 + 6 + (64 - lead - trail)     # '11' + new window
                prev_lead, prev_trail = lead, trail
        prev_v = float_bits(v)
    return bits

random.seed(7)
start = 1_793_318_400                       # 2026-10-30 00:00:00 UTC
series = {
    "constant gauge":   [(start + 15 * i, 42.0) for i in range(120)],
    "counter (+1/scr)": [(start + 15 * i, float(1000 + i)) for i in range(120)],
    "noisy CPU %":      [(start + 15 * i + random.choice([0, 0, 0, 1]),
                          round(random.uniform(20, 80), 1)) for i in range(120)],
}
for name, pts in series.items():
    b = encode(pts)
    print(f"{name:18s} {b / len(pts) / 8:5.2f} bytes/point  ({128 / (b / len(pts)):4.1f}x vs 16 B)")
