# Extracted from manuscript/book1-traditional/25-consistency-and-availability.md §25.6.2 (listing 2). Edit the manuscript, not this file.
"""Bayou-style session guarantees with version vectors (after Terry et al. 1994).
A replica's vector counts how many writes from each origin it has applied.
The session remembers the vectors of what it wrote and what it read, and a
replica may serve the session only if its vector dominates the required one."""

def dominates(a, b):
    return all(a.get(k, 0) >= v for k, v in b.items())

def merge(a, b):
    return {k: max(a.get(k, 0), b.get(k, 0)) for k in a.keys() | b.keys()}

class Replica:
    def __init__(self, name):
        self.name, self.vv, self.log = name, {}, []
    def apply(self, origin, seq, item):        # anti-entropy delivers writes in order
        if self.vv.get(origin, 0) == seq - 1:
            self.vv[origin] = seq
            self.log.append(item)
    def local_write(self, item):
        seq = self.vv.get(self.name, 0) + 1
        self.apply(self.name, seq, item)
        return self.name, seq

class Session:
    def __init__(self, ryw=True, mr=True, mw=True, wfr=True):
        self.ryw, self.mr, self.mw, self.wfr = ryw, mr, mw, wfr
        self.read_vv, self.write_vv = {}, {}

    def can_read(self, rep):
        need = {}
        if self.ryw: need = merge(need, self.write_vv)   # see my own writes
        if self.mr:  need = merge(need, self.read_vv)    # never go backwards
        return dominates(rep.vv, need)

    def can_write(self, rep):
        need = {}
        if self.mw:  need = merge(need, self.write_vv)   # my writes stay in order
        if self.wfr: need = merge(need, self.read_vv)    # writes after what I read
        return dominates(rep.vv, need)

    def read(self, replicas):
        for rep in replicas:                             # try nearest first
            if self.can_read(rep):
                self.read_vv = merge(self.read_vv, rep.vv)
                return rep.name, list(rep.log)
        return None, "no replica is fresh enough: wait or go to another site"

    def write(self, replicas, item):
        for rep in replicas:
            if self.can_write(rep):
                origin, seq = rep.local_write(item)
                self.write_vv = merge(self.write_vv, {origin: seq})
                return rep.name
        return None

def own_write_then_read(**g):
    east, west = Replica("east"), Replica("west")
    s = Session(**g)
    s.write([east], "name=Ada")            # write lands in east
    return s.read([west, east])            # next request is routed to west first

def read_twice(**g):
    east, west = Replica("east"), Replica("west")
    east.local_write("comment 1")          # another user's write, not yet in west
    s = Session(**g)
    first = s.read([east])
    second = s.read([west, east])          # load balancer prefers west now
    return first, second

off = dict(ryw=False, mr=False, mw=False, wfr=False)
print("RYW off:", own_write_then_read(**off))
print("RYW on :", own_write_then_read())
print("MR off :", read_twice(**off))
print("MR on  :", read_twice())
