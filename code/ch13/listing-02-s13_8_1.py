# Extracted from manuscript/book1-traditional/13-storage-engine-internals.md §13.8.1 (listing 2). Edit the manuscript, not this file.
"""A toy LSM tree: write-ahead log, memtable, SSTable flush, merge compaction,
manifest and WAL replay. Teaching code: single-threaded, JSON-lines files."""
import bisect
import hashlib
import heapq
import json
import os

TOMBSTONE = None          # a deleted key is stored as key -> None


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class BloomFilter:
    """m bits and k hash positions per key, derived from one SHA-256 digest."""

    def __init__(self, n_keys, bits_per_key=10, k=7, bits=0):
        self.m = max(64, n_keys * bits_per_key)
        self.k = k
        self.bits = bits

    def _positions(self, key):
        d = hashlib.sha256(key.encode()).digest()
        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:16], "big")
        return [(h1 + i * h2) % self.m for i in range(self.k)]   # double hashing

    def add(self, key):
        for p in self._positions(key):
            self.bits |= 1 << p

    def may_contain(self, key):
        return all(self.bits >> p & 1 for p in self._positions(key))


class SSTable:
    """Immutable sorted file: one JSON record per line, then a footer line holding
    a sparse index (every INDEX_EVERY-th key -> byte offset) and a Bloom filter."""
    INDEX_EVERY = 16

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            f.seek(max(0, end - 8))
            footer_len = int(f.read(8))           # last 8 bytes: footer length
            f.seek(end - 8 - footer_len)
            footer = json.loads(f.read(footer_len))
        self.index_keys = [k for k, _ in footer["index"]]
        self.index_offsets = [o for _, o in footer["index"]]
        self.data_end = footer["data_end"]
        self.bloom = BloomFilter(0, bits=int(footer["bloom"], 16))
        self.bloom.m, self.bloom.k = footer["m"], footer["k"]
        self.size = end

    @staticmethod
    def write(path, items, sync=True):
        """items: iterable of (key, value) in ascending key order. Returns bytes written."""
        items = list(items)
        bloom = BloomFilter(len(items))
        index, tmp = [], path + ".tmp"
        with open(tmp, "wb") as f:
            for i, (k, v) in enumerate(items):
                if i % SSTable.INDEX_EVERY == 0:
                    index.append((k, f.tell()))
                bloom.add(k)
                f.write((json.dumps([k, v]) + "\n").encode())
            footer = json.dumps({"index": index, "data_end": f.tell(), "m": bloom.m,
                                 "k": bloom.k, "bloom": format(bloom.bits, "x")}).encode()
            f.write(footer + b"%08d" % len(footer))
            if sync:
                f.flush()
                os.fsync(f.fileno())
            size = f.tell()
        os.replace(tmp, path)                     # appears atomically, complete or not at all
        return size

    def get(self, key):
        """Returns (found, value). Reads at most INDEX_EVERY records from disk."""
        if not self.bloom.may_contain(key):
            return False, None                    # definitely absent: no disk read
        i = bisect.bisect_right(self.index_keys, key) - 1
        if i < 0:
            return False, None
        with open(self.path, "rb") as f:
            f.seek(self.index_offsets[i])
            for _ in range(self.INDEX_EVERY):
                if f.tell() >= self.data_end:
                    break
                k, v = json.loads(f.readline())
                if k == key:
                    return True, v
                if k > key:
                    break
        return False, None

    def scan(self):
        with open(self.path, "rb") as f:
            while f.tell() < self.data_end:
                k, v = json.loads(f.readline())
                yield k, v


class LSMTree:
    def __init__(self, directory, memtable_limit=256, compact_at=4, sync=True):
        self.dir, self.limit, self.compact_at, self.sync = directory, memtable_limit, compact_at, sync
        os.makedirs(directory, exist_ok=True)
        self.stats = {"user": 0, "wal": 0, "flush": 0, "compaction": 0}
        self.memtable = {}
        manifest = os.path.join(directory, "MANIFEST")
        names = json.load(open(manifest)) if os.path.exists(manifest) else []
        self.tables = [SSTable(os.path.join(directory, n)) for n in names]  # oldest first
        self.next_id = 1 + max([int(n[4:10]) for n in names], default=0)
        for n in os.listdir(directory):           # delete orphans left by a crash
            if n.startswith("sst-") and n not in names:
                os.remove(os.path.join(directory, n))
        self.wal_path = os.path.join(directory, "wal.log")
        self._replay_wal()
        self.wal = open(self.wal_path, "ab")

    # ---------- durability ----------
    def _replay_wal(self):
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "rb") as f:
            for line in f:
                try:
                    k, v = json.loads(line)
                except ValueError:
                    break                         # torn final record from a crash: stop
                self.memtable[k] = v

    def _save_manifest(self):
        tmp = os.path.join(self.dir, "MANIFEST.tmp")
        with open(tmp, "w") as f:
            json.dump([os.path.basename(t.path) for t in self.tables], f)
            if self.sync:
                f.flush()
                os.fsync(f.fileno())
        os.replace(tmp, os.path.join(self.dir, "MANIFEST"))
        if self.sync:
            _fsync_dir(self.dir)

    # ---------- write path ----------
    def put(self, key, value):
        record = (json.dumps([key, value]) + "\n").encode()
        self.wal.write(record)                    # 1. log first (write-ahead)
        self.wal.flush()
        if self.sync:
            os.fsync(self.wal.fileno())           #    durable before we acknowledge
        self.stats["user"] += len(key) + len(value or "")
        self.stats["wal"] += len(record)
        self.memtable[key] = value                # 2. then apply to the memtable
        if len(self.memtable) >= self.limit:
            self.flush()

    def delete(self, key):
        self.put(key, TOMBSTONE)

    def _new_path(self):
        path = os.path.join(self.dir, "sst-%06d.jsonl" % self.next_id)
        self.next_id += 1
        return path

    def flush(self):
        if not self.memtable:
            return
        path = self._new_path()
        self.stats["flush"] += SSTable.write(path, sorted(self.memtable.items()), self.sync)
        self.tables.append(SSTable(path))
        self._save_manifest()                     # the new table is now part of the tree
        self.memtable = {}
        self.wal.close()
        self.wal = open(self.wal_path, "wb")      # its records are in the SSTable: truncate
        if len(self.tables) >= self.compact_at:
            self.compact()

    def compact(self):
        """Full merge of every SSTable into one. Newest version of each key wins;
        tombstones are dropped because no older table remains below the output."""
        def tagged(age, table):                   # age 0 = newest
            for k, v in table.scan():
                yield k, age, v
        streams = [tagged(age, t) for age, t in enumerate(reversed(self.tables))]
        merged, last = [], object()
        for k, _, v in heapq.merge(*streams):     # sorted by key, then newest first
            if k != last:
                last = k
                if v is not TOMBSTONE:
                    merged.append((k, v))
        path = self._new_path()
        self.stats["compaction"] += SSTable.write(path, merged, self.sync)
        old, self.tables = self.tables, [SSTable(path)]
        self._save_manifest()                     # switch atomically, then delete inputs
        for t in old:
            os.remove(t.path)

    # ---------- read path ----------
    def get(self, key):
        if key in self.memtable:
            return self.memtable[key]             # may be TOMBSTONE -> None
        for table in reversed(self.tables):       # newest to oldest
            found, value = table.get(key)
            if found:
                return value
        return None

    def write_amplification(self):
        disk = self.stats["wal"] + self.stats["flush"] + self.stats["compaction"]
        return disk / max(1, self.stats["user"])


if __name__ == "__main__":
    import random
    import tempfile

    rng = random.Random(13)
    with tempfile.TemporaryDirectory() as d:
        db, model = LSMTree(d, sync=False), {}
        for i in range(20_000):
            key = "user:%04d" % rng.randrange(2_000)
            if rng.random() < 0.1:
                db.delete(key)
                model.pop(key, None)
            else:
                value = "v%d-%s" % (i, "x" * rng.randrange(20, 60))
                db.put(key, value)
                model[key] = value
        stats, wa = dict(db.stats), db.write_amplification()
        unflushed = len(db.memtable)

        db.wal.close()                            # simulate a crash: memtable is lost
        db = LSMTree(d, sync=False)               # reopen: manifest + WAL replay
        assert len(db.memtable) == unflushed, "WAL replay lost records"
        for k in ("user:%04d" % n for n in range(2_000)):
            assert db.get(k) == model.get(k), k
        print("all 2000 keys match after crash and WAL replay")
        print("live keys:", len(model), " SSTables:", len(db.tables),
              " memtable entries replayed:", unflushed)
        print("bytes by user=%(user)d wal=%(wal)d flush=%(flush)d compaction=%(compaction)d" % stats)
        print("write amplification = %.1f" % wa)
