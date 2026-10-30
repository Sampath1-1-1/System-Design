# Extracted from manuscript/book1-traditional/27-replication-and-fault-tolerance.md §27.14.3 (listing 4). Edit the manuscript, not this file.
"""State-based CRDTs: G-Counter, PN-Counter, LWW-Register and OR-Set,
with randomized tests that merge is commutative, associative and idempotent."""
import copy
import itertools
import random

class GCounter:
    """Grow-only counter: one slot per replica; merge takes the per-slot max."""
    def __init__(self, replica):
        self.replica, self.slots = replica, {}
    def increment(self, n=1):
        assert n >= 0, "a G-Counter only grows"
        self.slots[self.replica] = self.slots.get(self.replica, 0) + n
    def value(self):
        return sum(self.slots.values())
    def merge(self, other):
        for r, v in other.slots.items():
            self.slots[r] = max(self.slots.get(r, 0), v)
    def state(self):
        return dict(sorted(self.slots.items()))

class PNCounter:
    """Counter with decrements: one G-Counter for increments, one for decrements."""
    def __init__(self, replica):
        self.p, self.n = GCounter(replica), GCounter(replica)
    def increment(self, k=1):
        self.p.increment(k)
    def decrement(self, k=1):
        self.n.increment(k)
    def value(self):
        return self.p.value() - self.n.value()
    def merge(self, other):
        self.p.merge(other.p)
        self.n.merge(other.n)
    def state(self):
        return (self.p.state(), self.n.state())

class LWWRegister:
    """Last-writer-wins register; ties on timestamp broken by replica ID."""
    def __init__(self, replica):
        self.replica, self.value_, self.stamp = replica, None, (0, "")
    def assign(self, value, timestamp):
        stamp = (timestamp, self.replica)
        if stamp > self.stamp:
            self.value_, self.stamp = value, stamp
    def value(self):
        return self.value_
    def merge(self, other):
        if other.stamp > self.stamp:
            self.value_, self.stamp = other.value_, other.stamp
    def state(self):
        return (self.value_, self.stamp)

class ORSet:
    """Observed-remove set: each add creates a unique tag; remove deletes only
    the tags it has observed, so a concurrent add survives (add wins)."""
    def __init__(self, replica):
        self.replica, self.adds, self.removes, self.seq = replica, set(), set(), 0
    def add(self, element):
        self.seq += 1                            # tag = (replica, sequence): globally unique
        self.adds.add((element, (self.replica, self.seq)))
    def remove(self, element):
        self.removes |= {t for t in self.adds if t[0] == element}
    def value(self):
        return {e for (e, tag) in self.adds - self.removes}
    def merge(self, other):
        self.adds |= other.adds
        self.removes |= other.removes
    def state(self):
        return (sorted(self.adds), sorted(self.removes))

def merged(a, b):
    """Return a copy of a merged with b, leaving both inputs unchanged."""
    out = copy.deepcopy(a)
    out.merge(b)
    return out

def random_replicas(cls, rng, ops=30):
    replicas = [cls(name) for name in "ABC"]
    for step in range(ops):
        r = rng.choice(replicas)
        if cls is GCounter:
            r.increment(rng.randint(1, 5))
        elif cls is PNCounter:
            (r.increment if rng.random() < 0.6 else r.decrement)(rng.randint(1, 5))
        elif cls is LWWRegister:
            r.assign(rng.choice("xyz"), timestamp=rng.randint(1, 20))
        else:
            (r.add if rng.random() < 0.6 else r.remove)(rng.choice("abcd"))
        if rng.random() < 0.3:                   # occasional partial gossip
            r.merge(rng.choice(replicas))
    return replicas

def check_laws(cls, trials=200, seed=7):
    rng = random.Random(seed)
    for _ in range(trials):
        a, b, c = random_replicas(cls, rng)
        assert merged(a, b).state() == merged(b, a).state(), "commutativity"
        assert merged(merged(a, b), c).state() == merged(a, merged(b, c)).state(), "associativity"
        assert merged(a, a).state() == a.state(), "idempotence"
        finals = [merged(merged(x, y), z).state() for x, y, z in itertools.permutations((a, b, c))]
        assert all(s == finals[0] for s in finals), "convergence in every merge order"
    return f"{cls.__name__:11s}: {trials} random histories, all laws hold"

class SumCounter(GCounter):
    """A broken design: merge adds slots instead of taking the maximum."""
    def merge(self, other):
        for r, v in other.slots.items():
            self.slots[r] = self.slots.get(r, 0) + v

if __name__ == "__main__":
    for cls in (GCounter, PNCounter, LWWRegister, ORSet):
        print(check_laws(cls))

    bad = SumCounter("A"); bad.increment(5)
    print("SumCounter: value 5, after merging a duplicate delivery:", merged(bad, bad).value())

    # Add-wins: A removes "milk" while B concurrently re-adds it.
    a, b = ORSet("A"), ORSet("B")
    a.add("milk"); b.merge(a)                    # both replicas see milk
    a.remove("milk")                             # A removes the tag it observed
    b.add("milk")                                # B adds again with a fresh tag
    a.merge(b); b.merge(a)
    print("OR-Set after concurrent remove and add:", a.value(), b.value())

    # The same story with LWW on timestamps loses B's add if A's clock is ahead.
    ra, rb = LWWRegister("A"), LWWRegister("B")
    ra.assign("<removed>", timestamp=103)        # A removes at real time 98; its clock is 5 ms fast
    rb.assign("milk", timestamp=100)             # B re-adds later, at real time 100
    ra.merge(rb); rb.merge(ra)
    print("LWW register after the same history:", ra.value(), rb.value())
