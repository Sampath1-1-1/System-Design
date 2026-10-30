# Extracted from manuscript/book1-traditional/05-computer-architecture.md §5.16 (listing 4). Edit the manuscript, not this file.
"""stride.py — how access stride affects time per element touched.

Run: python3 stride.py   (needs numpy)
"""
import time
import numpy as np

N_BYTES = 256 * 1024 * 1024            # 256 MiB buffer, far larger than any L3
data = np.ones(N_BYTES // 8, dtype=np.int64)   # 8-byte elements

def ns_per_element(stride_elems: int, repeats: int = 3) -> float:
    view = data[::stride_elems]          # strided view, no copy
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        view.sum()                       # touches every element of the view
        best = min(best, time.perf_counter() - t0)
    return best / view.size * 1e9

print(f"{'stride (B)':>10} {'elements':>12} {'ns/element':>11}")
for stride in [1, 2, 4, 8, 16, 32, 64, 128, 512]:
    n = data[::stride].size
    print(f"{stride * 8:>10} {n:>12,} {ns_per_element(stride):>11.2f}")
