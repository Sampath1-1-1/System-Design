# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.10.3 (listing 3). Edit the manuscript, not this file.
"""A bounded buffer (producer/consumer) built from one mutex and two condition variables."""
import threading
from collections import deque


class BoundedBuffer:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items = deque()
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)   # producers wait here
        self.not_empty = threading.Condition(self.lock)  # consumers wait here

    def put(self, item) -> None:
        with self.lock:
            while len(self.items) == self.capacity:      # while, not if
                self.not_full.wait()                     # releases lock while asleep
            self.items.append(item)
            self.not_empty.notify()                      # wake one consumer

    def get(self):
        with self.lock:
            while not self.items:
                self.not_empty.wait()
            item = self.items.popleft()
            self.not_full.notify()                       # wake one producer
            return item


if __name__ == "__main__":
    buf = BoundedBuffer(capacity=8)
    N_PRODUCERS, PER_PRODUCER = 3, 10_000
    results = []

    def producer(pid: int) -> None:
        for i in range(PER_PRODUCER):
            buf.put((pid, i))

    def consumer() -> None:
        for _ in range(N_PRODUCERS * PER_PRODUCER):
            results.append(buf.get())

    threads = [threading.Thread(target=producer, args=(p,)) for p in range(N_PRODUCERS)]
    threads.append(threading.Thread(target=consumer))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("consumed:", len(results), "unique:", len(set(results)))
