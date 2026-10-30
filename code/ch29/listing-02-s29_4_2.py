# Extracted from manuscript/book1-traditional/29-distributed-data-processing.md §29.4.2 (listing 2). Edit the manuscript, not this file.
"""A mini MapReduce engine: splits -> map -> (combine) -> partition -> sort -> shuffle -> reduce.
Map tasks are pure functions of their split, so a failed task is simply re-executed."""
import heapq
import itertools
import zlib
from collections import Counter, defaultdict


def hash_partition(key, num_reducers):
    # Deterministic across processes (Python's built-in hash() is salted per process).
    return zlib.crc32(repr(key).encode()) % num_reducers


class TaskFailure(Exception):
    pass


class MiniMapReduce:
    def __init__(self, mapper, reducer, num_reducers=4, combiner=None,
                 partitioner=hash_partition, max_attempts=4):
        self.mapper, self.reducer, self.combiner = mapper, reducer, combiner
        self.R, self.partitioner, self.max_attempts = num_reducers, partitioner, max_attempts
        self.stats = Counter()

    def _map_task(self, split, crash):
        if crash:                               # simulate a worker dying mid-task
            raise TaskFailure("worker lost")
        buckets = [defaultdict(list) for _ in range(self.R)]
        for record in split:
            for key, value in self.mapper(record):
                self.stats["map_output_records"] += 1
                buckets[self.partitioner(key, self.R)][key].append(value)
        runs = []                               # one sorted run per reducer partition
        for bucket in buckets:
            run = []
            for key in sorted(bucket):
                values = bucket[key]
                if self.combiner:               # local pre-aggregation before the shuffle
                    values = list(self.combiner(key, values))
                run.extend((key, v) for v in values)
            runs.append(run)
        return runs

    def run(self, splits, crash_first_attempt=()):
        map_outputs = []                        # map_outputs[m][r] = sorted run
        for m, split in enumerate(splits):
            for attempt in range(1, self.max_attempts + 1):
                try:
                    crash = m in crash_first_attempt and attempt == 1
                    map_outputs.append(self._map_task(split, crash))
                    break
                except TaskFailure:
                    self.stats["map_reexecutions"] += 1
            else:
                raise RuntimeError(f"map task {m} failed {self.max_attempts} times")
        result, reducer_input = {}, []
        for r in range(self.R):                 # shuffle: reducer r fetches run r from every mapper
            runs = [map_outputs[m][r] for m in range(len(map_outputs))]
            self.stats["shuffled_records"] += sum(len(run) for run in runs)
            reducer_input.append(sum(len(run) for run in runs))
            merged = heapq.merge(*runs, key=lambda kv: kv[0])   # k-way merge of sorted runs
            for key, group in itertools.groupby(merged, key=lambda kv: kv[0]):
                for out in self.reducer(key, (v for _, v in group)):
                    result[key] = out
        self.stats["max_reducer_input"] = max(reducer_input)
        return result


# ---- Job 1: word count ------------------------------------------------------
def wc_map(line):
    for word in line.lower().split():
        yield word.strip(".,;:!?\"'"), 1


def wc_sum(key, values):
    yield sum(values)


# ---- Job 2: reduce-side (sort-merge) join of users and orders ----------------
def join_map(record):
    table, row = record
    if table == "users":                        # ("users", (user_id, country))
        yield row[0], ("U", row[1])
    else:                                       # ("orders", (order_id, user_id, amount))
        yield row[1], ("O", (row[0], row[2]))


def join_reduce(user_id, tagged):
    country, orders = None, []
    for tag, payload in tagged:
        if tag == "U":
            country = payload
        else:
            orders.append(payload)
    yield sorted((oid, amt, country) for oid, amt in orders)   # orders enriched; None = no profile


if __name__ == "__main__":
    text = ["the quick brown fox", "jumps over the lazy dog", "the dog barks",
            "The fox runs. The dog sleeps!", "a quick test of the engine"] * 200
    splits = [text[i:i + 100] for i in range(0, len(text), 100)]        # 10 input splits
    expected = Counter(w.strip(".,;:!?\"'") for line in text for w in line.lower().split())

    plain = MiniMapReduce(wc_map, wc_sum, num_reducers=4)
    out_plain = plain.run(splits)
    combined = MiniMapReduce(wc_map, wc_sum, num_reducers=4, combiner=wc_sum)
    out_comb = combined.run(splits, crash_first_attempt={2, 7})
    assert out_plain == dict(expected) == out_comb
    print("distinct words:", len(out_comb), " 'the' =", out_comb["the"])
    print("map output records:", plain.stats["map_output_records"])
    print("shuffled without combiner:", plain.stats["shuffled_records"])
    print("shuffled with combiner:   ", combined.stats["shuffled_records"])
    print("re-executed map tasks:", combined.stats["map_reexecutions"])

    users = [("users", (u, c)) for u, c in [(1, "IN"), (2, "US"), (3, "DE")]]
    orders = [("orders", (100 + i, 1 + i % 4, 10 * i)) for i in range(8)]   # user 4 has no profile
    joined = MiniMapReduce(join_map, join_reduce, num_reducers=2).run([users, orders[:4], orders[4:]])
    assert joined[1] == [(100, 0, "IN"), (104, 40, "IN")]
    assert joined[4] == [(103, 30, None), (107, 70, None)]   # orphan orders keep country None
    print("join, user 2:", joined[2])
    print("all tests passed")
