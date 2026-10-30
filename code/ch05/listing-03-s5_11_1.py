# Extracted from manuscript/book1-traditional/05-computer-architecture.md §5.11.1 (listing 3). Edit the manuscript, not this file.
"""simd.py — interpreted loop vs vectorized (SIMD-backed) numpy."""
import time
import numpy as np

n = 10_000_000
a = np.random.rand(n).astype(np.float32)
b = np.random.rand(n).astype(np.float32)

t0 = time.perf_counter()
out = [0.0] * n
for i in range(n):                 # one element at a time, interpreted
    out[i] = a[i] * b[i] + 1.0
t1 = time.perf_counter()
c = a * b + 1.0                    # whole-array ops in compiled, SIMD loops
t2 = time.perf_counter()

print(f"python loop: {t1 - t0:.2f} s")
print(f"numpy:       {t2 - t1:.4f} s  ({(t1 - t0) / (t2 - t1):.0f}x faster)")
