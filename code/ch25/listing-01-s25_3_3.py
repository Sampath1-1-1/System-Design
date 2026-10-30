# Extracted from manuscript/book1-traditional/25-consistency-and-availability.md §25.3.3 (listing 1). Edit the manuscript, not this file.
"""Brute-force checker: is a history of register operations linearizable,
or at least sequentially consistent? Each operation is
    (process, kind, key, value, invoke_time, response_time)
kind is "w" (write value) or "r" (read that returned value).
response_time None means the client never heard back (the op may or may not
have taken effect). All registers start at 0."""
from functools import lru_cache

INF = float("inf")

def check(history, real_time=True):
    ops = [(p, k, key, v, inv, INF if resp is None else resp)
           for p, k, key, v, inv, resp in history]
    n = len(ops)
    done = frozenset(i for i in range(n) if ops[i][5] != INF)

    def must_precede(a, b):
        """True if op a has to be ordered before op b."""
        if real_time:                       # linearizability: real-time order
            return ops[a][5] < ops[b][4]
        # sequential consistency: only each process's own program order
        return ops[a][0] == ops[b][0] and ops[a][4] < ops[b][4]

    @lru_cache(maxsize=None)
    def search(placed, state):              # placed: bitmask; state: sorted (key, value) pairs
        if all(placed >> i & 1 for i in done):
            return ()                       # every completed op is placed
        regs = dict(state)
        for i in range(n):
            if placed >> i & 1:
                continue
            # i can go next only if no unplaced op must precede it
            if any(not placed >> j & 1 and j != i and must_precede(j, i)
                   for j in range(n)):
                continue
            p, kind, key, v, _, _ = ops[i]
            if kind == "r" and regs.get(key, 0) != v:
                continue                    # read would return the wrong value
            new = dict(regs)
            if kind == "w":
                new[key] = v
            rest = search(placed | 1 << i, tuple(sorted(new.items())))
            if rest is not None:
                return (i,) + rest
        return None

    order = search(0, ())
    return None if order is None else [ops[i][:4] for i in order]

def describe(name, h):
    lin, sc = check(h, real_time=True), check(h, real_time=False)
    print(f"{name}: linearizable={lin is not None}, sequential={sc is not None}")
    if lin:
        print("   linearization:", " -> ".join(f"{p}:{k}({key}={v})" for p, k, key, v in lin))
    elif sc:
        print("   sequential order:", " -> ".join(f"{p}:{k}({key}={v})" for p, k, key, v in sc))

H1 = [("A", "w", "x", 1, 0, 10),   # write overlaps both reads
      ("B", "r", "x", 0, 1, 4),
      ("C", "r", "x", 1, 5, 12)]
H2 = [("A", "w", "x", 1, 0, 5),    # write finished at t=5 ...
      ("B", "r", "x", 0, 7, 9)]    # ... yet a later read sees the old value
H3 = [("A", "w", "x", 1, 0, 10),   # new-then-old inversion during a write
      ("B", "r", "x", 1, 2, 4),
      ("C", "r", "x", 0, 6, 8)]
H4 = [("A", "w", "x", 1, 0, 2),    # a process misses its own write
      ("A", "r", "x", 0, 3, 4)]
H5 = [("A", "w", "x", 1, 0, 2), ("A", "r", "y", 0, 3, 4),   # store buffering
      ("B", "w", "y", 1, 0, 2), ("B", "r", "x", 0, 3, 4)]
H6 = [("A", "w", "x", 1, 0, None), # write timed out: outcome unknown
      ("B", "r", "x", 1, 5, 6),
      ("C", "r", "x", 1, 7, 8)]

for name, h in [("H1", H1), ("H2", H2), ("H3", H3), ("H4", H4), ("H5", H5), ("H6", H6)]:
    describe(name, h)
x_only = [op for op in H5 if op[2] == "x"]
y_only = [op for op in H5 if op[2] == "y"]
print("H5 per key sequential:", check(x_only, False) is not None, check(y_only, False) is not None)
