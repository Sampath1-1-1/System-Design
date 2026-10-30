# Extracted from manuscript/book1-traditional/13-storage-engine-internals.md §13.13.2 (listing 3). Edit the manuscript, not this file.
"""Dictionary encoding, run-length encoding and bit-packing for one column."""
import math
import random


def dictionary_encode(values):
    dictionary = sorted(set(values))
    code = {v: i for i, v in enumerate(dictionary)}
    return dictionary, [code[v] for v in values]


def run_length_encode(codes):
    runs = []                                   # list of [value, run_length]
    for c in codes:
        if runs and runs[-1][0] == c:
            runs[-1][1] += 1
        else:
            runs.append([c, 1])
    return runs


def bit_pack(codes, width):
    packed = 0
    for i, c in enumerate(codes):
        packed |= c << (i * width)              # width bits per value, no byte padding
    return packed.to_bytes(math.ceil(len(codes) * width / 8), "little")


def bit_unpack(data, width, n):
    packed, mask = int.from_bytes(data, "little"), (1 << width) - 1
    return [(packed >> (i * width)) & mask for i in range(n)]


if __name__ == "__main__":
    rng = random.Random(7)
    countries = ["BR", "DE", "FR", "IN", "JP", "US"]
    # 100,000 rows sorted by country, as a column store would often keep them
    column = sorted(rng.choice(countries) for _ in range(100_000))
    raw = sum(len(v.encode()) for v in column)

    dictionary, codes = dictionary_encode(column)
    width = max(1, math.ceil(math.log2(len(dictionary))))
    packed = bit_pack(codes, width)
    runs = run_length_encode(codes)
    assert bit_unpack(packed, width, len(codes)) == codes

    print("raw bytes:", raw)
    print("dictionary:", dictionary, "-> width", width, "bits per value")
    print("bit-packed bytes:", len(packed), " ratio %.1fx" % (raw / len(packed)))
    print("RLE runs:", len(runs), "-> about", len(runs) * 5, "bytes (1-byte code + 4-byte length)")
    # a filter can run on codes: count rows WHERE country = 'IN' without decoding strings
    target = dictionary.index("IN")
    print("rows with IN:", sum(length for c, length in runs if c == target))
