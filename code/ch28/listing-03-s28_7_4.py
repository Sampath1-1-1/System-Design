# Extracted from manuscript/book1-traditional/28-distributed-transactions.md §28.7.4 (listing 3). Edit the manuscript, not this file.
"""A Percolator-style transaction on a multi-version key-value store.

Each row has three columns, each a map timestamp -> value (as in Bigtable):
  data[ts]  = value written by the txn that started at ts
  lock[ts]  = name of the primary row, while the txn that started at ts is in flight
  write[cts] = start ts of the txn whose data became visible at commit ts cts
Assumes the holder of any lock a reader finds is dead (Percolator checks liveness first).
"""
import itertools


class Store:
    def __init__(self):
        self.rows = {}

    def row(self, key):
        return self.rows.setdefault(key, {"data": {}, "lock": {}, "write": {}})


class Oracle:                                     # the timestamp oracle
    def __init__(self):
        self._next = itertools.count(1)

    def ts(self):
        return next(self._next)


class Txn:
    def __init__(self, store, oracle):
        self.s, self.o = store, oracle
        self.start = oracle.ts()                  # snapshot timestamp
        self.writes = {}

    def get(self, key):
        r = self.s.row(key)
        for lts in [t for t in r["lock"] if t <= self.start]:
            self._cleanup(key, lts)               # stale lock below our snapshot
        visible = [c for c in r["write"] if c <= self.start]
        return r["data"][r["write"][max(visible)]] if visible else None

    def set(self, key, value):
        self.writes[key] = value

    def _prewrite(self, key, primary):
        r = self.s.row(key)
        if any(c >= self.start for c in r["write"]) or r["lock"]:
            return False                          # write-write conflict or locked
        r["data"][self.start] = self.writes[key]
        r["lock"][self.start] = primary
        return True

    def commit(self, crash=None):
        keys = sorted(self.writes)
        primary, secondaries = keys[0], keys[1:]
        for k in keys:                            # phase 1: prewrite, primary first
            if not self._prewrite(k, primary):
                self._rollback(keys)
                return False
        if crash == "before_primary":
            return None                           # client dies holding all locks
        commit_ts = self.o.ts()
        p = self.s.row(primary)                   # phase 2: single-row txn on primary
        if self.start not in p["lock"]:
            return False                          # someone rolled us back
        p["write"][commit_ts] = self.start
        del p["lock"][self.start]                 # <- the commit point
        if crash == "after_primary":
            return True                           # committed; secondaries still locked
        for k in secondaries:
            r = self.s.row(k)
            r["write"][commit_ts] = self.start
            r["lock"].pop(self.start, None)
        return True

    def _rollback(self, keys):
        for k in keys:
            r = self.s.row(k)
            if r["lock"].get(self.start) is not None:
                del r["lock"][self.start]
                del r["data"][self.start]

    def _cleanup(self, key, lts):
        """Roll a dead transaction forward or back, decided by its primary row."""
        r, primary = self.s.row(key), self.s.row(key)["lock"][lts]
        p = self.s.row(primary)
        if lts in p["lock"]:                      # primary never committed: roll back
            del p["lock"][lts]
            p["data"].pop(lts, None)
        committed = [c for c, st in p["write"].items() if st == lts]
        if committed and key != primary:          # roll forward this secondary
            r["write"][committed[0]] = lts
        elif not committed:
            r["data"].pop(lts, None)
        r["lock"].pop(lts, None)


def setup():
    s, o = Store(), Oracle()
    t = Txn(s, o)
    t.set("acct7", 500)
    t.set("acct9", 0)
    assert t.commit()
    return s, o


def transfer(s, o, amount, crash=None):
    t = Txn(s, o)
    t.set("acct7", t.get("acct7") - amount)
    t.set("acct9", t.get("acct9") + amount)
    return t.commit(crash)


def balances(s, o):
    t = Txn(s, o)
    return t.get("acct7"), t.get("acct9")


if __name__ == "__main__":
    # 1. Snapshot isolation: a reader that started earlier keeps its snapshot.
    s, o = setup()
    old_reader = Txn(s, o)
    assert transfer(s, o, 100)
    assert (old_reader.get("acct7"), old_reader.get("acct9")) == (500, 0)
    assert balances(s, o) == (400, 100)

    # 2. Write-write conflict: the second concurrent writer aborts.
    s, o = setup()
    t1, t2 = Txn(s, o), Txn(s, o)
    t1.set("acct7", 1)
    t2.set("acct7", 2)
    assert t1.commit() and not t2.commit()

    # 3. Client dies after committing the primary: a reader rolls the secondary forward.
    s, o = setup()
    assert transfer(s, o, 100, crash="after_primary")
    assert balances(s, o) == (400, 100)

    # 4. Client dies before the commit point: a reader rolls everything back.
    s, o = setup()
    transfer(s, o, 100, crash="before_primary")
    assert balances(s, o) == (500, 0)

    # 5. Write skew is allowed: invariant acct7 + acct9 >= 0 is violated.
    s, o = setup()
    a, b = Txn(s, o), Txn(s, o)
    if a.get("acct7") + a.get("acct9") >= 400:
        a.set("acct7", a.get("acct7") - 400)      # writes acct7 only
    if b.get("acct7") + b.get("acct9") >= 400:
        b.set("acct9", b.get("acct9") - 400)      # writes acct9 only
    assert a.commit() and b.commit()
    print("after write skew:", balances(s, o), "sum =", sum(balances(s, o)))
    print("all Percolator scenarios passed")
