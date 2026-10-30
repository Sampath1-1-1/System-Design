# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.11.1 (listing 5). Edit the manuscript, not this file.
"""Two threads take two locks in opposite order -> deadlock (detected via timeout)."""
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()


def worker(name: str, first: threading.Lock, second: threading.Lock) -> None:
    with first:
        time.sleep(0.1)                       # make the bad interleaving very likely
        if second.acquire(timeout=1.0):       # a real program would block forever
            second.release()
            print(f"{name}: finished")
        else:
            print(f"{name}: gave up after 1 s -- probable deadlock")


t1 = threading.Thread(target=worker, args=("T1", lock_a, lock_b))
t2 = threading.Thread(target=worker, args=("T2", lock_b, lock_a))  # opposite order!
t1.start(); t2.start(); t1.join(); t2.join()

# Fix: impose a global lock order (always A before B) and the cycle cannot form.
t1 = threading.Thread(target=worker, args=("T1", lock_a, lock_b))
t2 = threading.Thread(target=worker, args=("T2", lock_a, lock_b))
t1.start(); t2.start(); t1.join(); t2.join()
