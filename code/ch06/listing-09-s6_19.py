# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.19 (listing 9). Edit the manuscript, not this file.
"""Two processes bounce one byte over a pair of pipes (POSIX only: uses fork).

Each round trip forces at least two blocking reads and wake-ups, so the
time per round trip upper-bounds the cost of two context switches plus
four system calls and Python interpreter overhead.
"""
import os
import time

ROUNDS = 100_000

parent_to_child_r, parent_to_child_w = os.pipe()
child_to_parent_r, child_to_parent_w = os.pipe()

pid = os.fork()
if pid == 0:                                    # child process
    for _ in range(ROUNDS):
        os.read(parent_to_child_r, 1)           # block until parent writes
        os.write(child_to_parent_w, b"x")       # wake the parent
    os._exit(0)

start = time.perf_counter()
for _ in range(ROUNDS):
    os.write(parent_to_child_w, b"x")           # wake the child
    os.read(child_to_parent_r, 1)               # block until child answers
elapsed = time.perf_counter() - start
os.waitpid(pid, 0)
print(f"{elapsed / ROUNDS * 1e6:.1f} us per round trip")
