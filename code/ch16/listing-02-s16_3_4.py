# Extracted from manuscript/book1-traditional/16-search-systems.md §16.3.4 (listing 2). Edit the manuscript, not this file.
"""Delta (gap) encoding + variable-byte (VByte) compression of a postings list,
and a measurement of bytes per posting on a synthetic Zipf-distributed collection."""
import random

def vbyte_encode(n):
    """Lucene-style VInt: 7 data bits per byte, low-order group first,
    high bit = 1 means 'more bytes follow'."""
    out = bytearray()
    while n >= 0x80:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)

def vbyte_decode_all(data):
    nums, n, shift = [], 0, 0
    for byte in data:
        n |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            nums.append(n)
            n, shift = 0, 0
    return nums

def compress_postings(doc_ids):
    gaps = [doc_ids[0]] + [b - a for a, b in zip(doc_ids, doc_ids[1:])]
    return b"".join(vbyte_encode(g) for g in gaps)

def decompress_postings(data):
    doc_ids, total = [], 0
    for gap in vbyte_decode_all(data):
        total += gap
        doc_ids.append(total)
    return doc_ids

if __name__ == "__main__":
    ids = [824, 829, 215406]            # the example used in Manning et al. (2008), ch. 5
    blob = compress_postings(ids)
    print("gaps:", [ids[0]] + [b - a for a, b in zip(ids, ids[1:])])
    print("bytes:", " ".join(f"{b:08b}" for b in blob), f"({len(blob)} bytes vs {4*len(ids)} raw)")
    assert decompress_postings(blob) == ids

    # Synthetic collection: N docs, vocabulary with Zipfian document frequencies.
    random.seed(16)
    N, M, total_postings_target = 200_000, 50_000, 10_000_000
    weights = [1 / r for r in range(1, M + 1)]                 # Zipf, exponent 1
    scale = total_postings_target / sum(weights)
    raw_bytes = vb_bytes = postings = 0
    for w in weights:
        df = max(1, min(N, int(w * scale)))
        doc_ids = sorted(random.sample(range(N), df))
        vb_bytes += len(compress_postings(doc_ids))
        raw_bytes += 4 * df
        postings += df
    print(f"postings={postings:,}  raw={raw_bytes/1e6:.1f} MB  vbyte={vb_bytes/1e6:.1f} MB  "
          f"bytes/posting={vb_bytes/postings:.2f}  ratio={vb_bytes/raw_bytes:.2f}")
