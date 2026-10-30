# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.9.2 (listing 6). Edit the manuscript, not this file.
class Operator:
    """Volcano iterator: every operator exposes open(), next() and close()."""
    def open(self): pass
    def next(self): raise NotImplementedError   # returns one row, or None when exhausted
    def close(self): pass

class SeqScan(Operator):
    def __init__(self, rows): self.rows = rows
    def open(self): self.pos = 0
    def next(self):
        if self.pos == len(self.rows): return None
        self.pos += 1
        return self.rows[self.pos - 1]

class Filter(Operator):
    def __init__(self, child, pred): self.child, self.pred = child, pred
    def open(self): self.child.open()
    def next(self):
        while (row := self.child.next()) is not None:
            if self.pred(row): return row
        return None
    def close(self): self.child.close()

class HashJoin(Operator):
    def __init__(self, build, probe, bkey, pkey):
        self.build, self.probe, self.bkey, self.pkey = build, probe, bkey, pkey
    def open(self):                       # blocking: consumes the whole build side
        self.table, self.pending = {}, []
        self.build.open()
        while (b := self.build.next()) is not None:
            self.table.setdefault(b[self.bkey], []).append(b)
        self.build.close()
        self.probe.open()
    def next(self):                       # pipelined: one probe row at a time
        while not self.pending:
            p = self.probe.next()
            if p is None: return None
            self.pending = [b + p for b in self.table.get(p[self.pkey], [])]
        return self.pending.pop()
    def close(self): self.probe.close()

class Project(Operator):
    def __init__(self, child, cols): self.child, self.cols = child, cols
    def open(self): self.child.open()
    def next(self):
        row = self.child.next()
        return None if row is None else tuple(row[c] for c in self.cols)
    def close(self): self.child.close()

class Limit(Operator):
    def __init__(self, child, n): self.child, self.n = child, n
    def open(self): self.child.open(); self.seen = 0
    def next(self):
        if self.seen == self.n: return None   # stop pulling: the scan below never finishes
        self.seen += 1
        return self.child.next()
    def close(self): self.child.close()

# SELECT c.city, o.total FROM customers c JOIN orders o ON c.id = o.customer_id
# WHERE o.total > 1000 LIMIT 2
customers = [(1, "Berlin"), (2, "Austin"), (3, "Pune")]
orders = [(10, 1, 2500), (11, 3, 900), (12, 1, 4100), (13, 2, 1800)]
plan = Limit(Project(HashJoin(SeqScan(customers),
                              Filter(SeqScan(orders), lambda r: r[2] > 1000), 0, 1),
                     cols=[1, 4]), 2)
plan.open()
while (row := plan.next()) is not None:
    print(row)
plan.close()
