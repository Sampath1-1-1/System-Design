# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.6.3 (listing 3). Edit the manuscript, not this file.
from collections import defaultdict

customers = [(1, "Berlin"), (2, "Austin"), (3, "Pune")]           # (customer_id, city)
orders = [(10, 1, 2500), (11, 3, 900), (12, 1, 4100), (13, 4, 50)]  # (order_id, customer_id, total)

def nested_loop_join(outer, inner, okey, ikey):
    for o in outer:                      # for every outer row ...
        for i in inner:                  # ... scan the whole inner input
            if o[okey] == i[ikey]:
                yield o + i

def hash_join(build, probe, bkey, pkey):
    table = defaultdict(list)
    for b in build:                      # build phase: hash the smaller input
        table[b[bkey]].append(b)
    for p in probe:                      # probe phase: one lookup per probe row
        for b in table.get(p[pkey], ()):
            yield b + p

def sort_merge_join(left, right, lkey, rkey):
    left, right = sorted(left, key=lambda r: r[lkey]), sorted(right, key=lambda r: r[rkey])
    i = j = 0
    while i < len(left) and j < len(right):
        lv, rv = left[i][lkey], right[j][rkey]
        if lv < rv:
            i += 1
        elif lv > rv:
            j += 1
        else:                            # emit every pair in the matching groups
            j_end = j
            while j_end < len(right) and right[j_end][rkey] == lv:
                j_end += 1
            while i < len(left) and left[i][lkey] == lv:
                for r in right[j:j_end]:
                    yield left[i] + r
                i += 1
            j = j_end

for name, rows in [("nested loop", nested_loop_join(customers, orders, 0, 1)),
                   ("hash", hash_join(customers, orders, 0, 1)),
                   ("sort-merge", sort_merge_join(customers, orders, 0, 1))]:
    print(f"{name:<12}", sorted(rows, key=lambda r: r[2]))
