# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.10.3 (listing 9). Edit the manuscript, not this file.
import datetime as dt
import os
import threading
import time
import uuid

TWITTER_EPOCH_MS = 1288834974657           # 2010-11-04 01:42:54.657 UTC, from Twitter's IdWorker
TIMESTAMP_BITS, MACHINE_BITS, SEQUENCE_BITS = 41, 10, 12
MAX_MACHINE = (1 << MACHINE_BITS) - 1      # 1023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1    # 4095

class ClockMovedBackwards(Exception):
    pass

class Snowflake:
    """64-bit IDs: 1 unused sign bit | 41-bit ms timestamp | 10-bit machine id | 12-bit sequence."""

    def __init__(self, machine_id: int, epoch_ms: int = TWITTER_EPOCH_MS, clock=lambda: time.time_ns() // 1_000_000):
        if not 0 <= machine_id <= MAX_MACHINE:
            raise ValueError("machine id must fit in 10 bits")
        self.machine_id, self.epoch_ms, self.clock = machine_id, epoch_ms, clock
        self.last_ms, self.sequence = -1, 0
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            now = self.clock()
            if now < self.last_ms:                      # NTP stepped the clock back
                raise ClockMovedBackwards(f"refusing to issue IDs for {self.last_ms - now} ms")
            if now == self.last_ms:
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE
                if self.sequence == 0:                  # 4,096 IDs used this ms: wait for the next
                    while now <= self.last_ms:
                        now = self.clock()
            else:
                self.sequence = 0
            self.last_ms = now
            return ((now - self.epoch_ms) << (MACHINE_BITS + SEQUENCE_BITS)) \
                | (self.machine_id << SEQUENCE_BITS) | self.sequence

def decode(snowflake_id: int, epoch_ms: int = TWITTER_EPOCH_MS):
    ms = (snowflake_id >> (MACHINE_BITS + SEQUENCE_BITS)) + epoch_ms
    machine = (snowflake_id >> SEQUENCE_BITS) & MAX_MACHINE
    seq = snowflake_id & MAX_SEQUENCE
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc), machine, seq

def uuid7() -> uuid.UUID:
    """RFC 9562 UUIDv7: 48-bit Unix ms | ver=7 | 12 random bits | var=10 | 62 random bits."""
    ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")      # 80 random bits, 74 of them used
    value = (ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76                                 # version
    value |= ((rand >> 62) & 0xFFF) << 64              # rand_a (12 bits)
    value |= 0b10 << 62                                # variant
    value |= rand & ((1 << 62) - 1)                    # rand_b (62 bits)
    return uuid.UUID(int=value)

gen = Snowflake(machine_id=37)
ids = [gen.next_id() for _ in range(200_000)]
assert len(set(ids)) == len(ids) and ids == sorted(ids)   # unique and strictly increasing
print("sample id:", ids[-1], "->", decode(ids[-1]))
start = time.perf_counter()
for _ in range(200_000):
    gen.next_id()
print(f"this Python generator: {200_000 / (time.perf_counter() - start):,.0f} IDs/s")

per_machine = (MAX_SEQUENCE + 1) * 1000
print(f"capacity: {per_machine:,} IDs/s per machine, {per_machine * (MAX_MACHINE + 1):,} IDs/s cluster")
lifetime_ms = 1 << TIMESTAMP_BITS
years = lifetime_ms / (1000 * 3600 * 24 * 365.25)
end = dt.datetime.fromtimestamp((TWITTER_EPOCH_MS + lifetime_ms) / 1000, dt.timezone.utc)
print(f"lifetime: 2^41 ms = {lifetime_ms:,} ms = {years:.1f} years; Twitter-epoch IDs run out {end:%Y-%m-%d}")

# A clock that jumps back 5 ms
fake = iter([1000, 1001, 996, 1002])
g = Snowflake(1, epoch_ms=0, clock=lambda: next(fake))
g.next_id(); g.next_id()
try:
    g.next_id()
except ClockMovedBackwards as e:
    print("clock step:", e)

u = [uuid7() for _ in range(3)]
print("uuid7:", u[0], "version", u[0].version, "| uuid4:", uuid.uuid4())
