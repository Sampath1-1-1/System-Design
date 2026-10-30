# Extracted from manuscript/book1-traditional/24-distributed-systems-fundamentals.md §24.11.4 (listing 3). Edit the manuscript, not this file.
"""Vector clocks: comparison, the Figure 24.11 trace, and sibling detection with version vectors."""


def compare(v, w):
    """Return 'equal', 'before' (v happened before w), 'after' or 'concurrent'."""
    keys = set(v) | set(w)
    le = all(v.get(k, 0) <= w.get(k, 0) for k in keys)
    ge = all(v.get(k, 0) >= w.get(k, 0) for k in keys)
    if le and ge:
        return "equal"
    if le:
        return "before"
    if ge:
        return "after"
    return "concurrent"


def merge(v, w):
    return {k: max(v.get(k, 0), w.get(k, 0)) for k in sorted(set(v) | set(w))}


class VCProcess:
    def __init__(self, pid):
        self.pid, self.vc, self.events = pid, {}, {}

    def _tick(self, name):
        self.vc = dict(self.vc)
        self.vc[self.pid] = self.vc.get(self.pid, 0) + 1   # increment own entry
        self.events[name] = self.vc
        return self.vc

    def local(self, name):
        return self._tick(name)

    def send(self, name):
        return self._tick(name)                 # the message carries a copy of vc

    def receive(self, name, msg_vc):
        self.vc = merge(self.vc, msg_vc)        # element-wise maximum, then increment
        return self._tick(name)


class VersionedStore:
    """One key replicated with version vectors keyed by replica id. Concurrent
    writes are kept as siblings instead of being silently overwritten."""

    def __init__(self):
        self.siblings = []                      # list of (version_vector, value)

    def get(self):
        context = {}
        for vv, _ in self.siblings:
            context = merge(context, vv)
        return [val for _, val in self.siblings], context

    def put(self, replica, value, context):
        new_vv = dict(context)
        counter = max((vv.get(replica, 0) for vv, _ in self.siblings), default=0)
        new_vv[replica] = counter + 1           # replica issues its next counter value
        # Keep only siblings that the new write did not causally overwrite.
        self.siblings = [(vv, val) for vv, val in self.siblings
                         if compare(vv, new_vv) == "concurrent"]
        self.siblings.append((new_vv, value))


def fmt(v):
    return "[" + ",".join(str(v.get(p, 0)) for p in ("P1", "P2", "P3")) + "]"


if __name__ == "__main__":
    p1, p2, p3 = VCProcess("P1"), VCProcess("P2"), VCProcess("P3")
    p1.local("a"); m1 = p1.send("b")
    p2.local("c"); p2.receive("d", m1); m2 = p2.send("e")
    p3.local("f"); p3.receive("g", m2); m3 = p3.send("h")
    p1.receive("i", m3)
    ev = {**p1.events, **p2.events, **p3.events}
    for name in "abcdefghi":
        print(name, fmt(ev[name]))
    for x, y in [("b", "g"), ("c", "b"), ("f", "e"), ("a", "i")]:
        print(f"{x} vs {y}: {compare(ev[x], ev[y])}")

    store = VersionedStore()
    store.put("R1", "cart=[book]", {})
    _, ctx = store.get()                           # both clients read the same version
    store.put("R1", "cart=[book, pen]", ctx)       # client 1 writes via replica R1
    store.put("R2", "cart=[book, lamp]", ctx)      # client 2 writes via R2 concurrently
    values, ctx = store.get()
    print("siblings:", values, "context:", ctx)
    store.put("R1", "cart=[book, pen, lamp]", ctx) # client merges and writes back
    print("after merge:", store.get())

    # Pitfall: two clients write concurrently through the SAME replica.
    store = VersionedStore()
    store.put("R1", "v0", {})
    _, ctx = store.get()
    store.put("R1", "from client X", ctx)          # gets {R1: 2}
    store.put("R1", "from client Y", ctx)          # gets {R1: 3}, which dominates {R1: 2}
    print("same-replica concurrent writes:", store.get()[0])
