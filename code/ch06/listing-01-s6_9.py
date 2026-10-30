# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.9 (listing 1). Edit the manuscript, not this file.
"""Lost updates: a read-modify-write race, then the fix with a mutex."""
import threading
import time

N_THREADS = 4
N_INCREMENTS = 10_000

counter = 0
lock = threading.Lock()


def unsafe_increment() -> None:
    global counter
    for _ in range(N_INCREMENTS):
        current = counter      # 1. read
        time.sleep(0)          # widen the window: yield the CPU (see note)
        counter = current + 1  # 2. modify + 3. write


def safe_increment() -> None:
    global counter
    for _ in range(N_INCREMENTS):
        with lock:             # critical section starts
            current = counter
            time.sleep(0)
            counter = current + 1
                               # critical section ends (lock released)


def run(worker) -> int:
    global counter
    counter = 0
    threads = [threading.Thread(target=worker) for _ in range(N_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter


if __name__ == "__main__":
    expected = N_THREADS * N_INCREMENTS
    print(f"expected       = {expected}")
    print(f"without a lock = {run(unsafe_increment)}")
    print(f"with a lock    = {run(safe_increment)}")
