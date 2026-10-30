# Extracted from manuscript/book1-traditional/24-distributed-systems-fundamentals.md §24.12.3 (listing 4). Edit the manuscript, not this file.
"""Hybrid logical clock (Kulkarni et al. 2014) on two nodes whose clocks disagree by 100 ms."""


class HLC:
    def __init__(self, physical_clock):
        self.pt = physical_clock      # function returning this node's wall clock, in ms
        self.l, self.c = 0, 0         # l: largest physical time seen; c: logical counter

    def now(self):
        """Timestamp a local or send event."""
        old_l = self.l
        self.l = max(old_l, self.pt())
        self.c = self.c + 1 if self.l == old_l else 0
        return (self.l, self.c)

    def update(self, msg):
        """Timestamp a receive event for a message stamped msg = (l_m, c_m)."""
        l_m, c_m = msg
        old_l = self.l
        self.l = max(old_l, l_m, self.pt())
        if self.l == old_l == l_m:
            self.c = max(self.c, c_m) + 1
        elif self.l == old_l:
            self.c += 1
        elif self.l == l_m:
            self.c = c_m + 1
        else:
            self.c = 0
        return (self.l, self.c)


def pack(ts):
    """48 bits of milliseconds plus a 16-bit counter fit in one 64-bit integer."""
    l, c = ts
    assert c < 2**16
    return (l << 16) | c


if __name__ == "__main__":
    true_ms = 1000
    a = HLC(lambda: true_ms + 100)    # node A's clock runs 100 ms fast
    b = HLC(lambda: true_ms)          # node B's clock is correct

    def show(event, node, ts, wall):
        print(f"true={true_ms} {event:<15} {node}: wall={wall}  hlc={ts}")

    ts = a.now()
    show("A sends m", "A", ts, true_ms + 100)
    true_ms += 1
    ts = b.update(ts)
    show("B receives m", "B", ts, true_ms)
    true_ms += 1
    ts = b.now()
    show("B local write", "B", ts, true_ms)
    true_ms += 1
    ts = b.now()
    show("B sends m2", "B", ts, true_ms)
    true_ms += 1
    ts = a.update(ts)
    show("A receives m2", "A", ts, true_ms + 100)
    true_ms = 1150
    ts = b.now()
    show("B local", "B", ts, true_ms)
    print("packed:", hex(pack(ts)), "->", ts == (pack(ts) >> 16, pack(ts) & 0xFFFF))
