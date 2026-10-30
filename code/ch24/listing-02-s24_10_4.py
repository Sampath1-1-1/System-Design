# Extracted from manuscript/book1-traditional/24-distributed-systems-fundamentals.md §24.10.4 (listing 2). Edit the manuscript, not this file.
"""Lamport logical clocks: replay the trace of Figure 24.10 and derive a total order."""


class LamportProcess:
    def __init__(self, pid):
        self.pid, self.clock, self.log = pid, 0, []

    def _tick(self, name, kind):
        self.clock += 1                         # rule 1: increment before every event
        self.log.append((self.clock, self.pid, name, kind))
        return self.clock

    def local(self, name):
        return self._tick(name, "local")

    def send(self, name):
        return self._tick(name, "send")         # the message carries this timestamp

    def receive(self, name, msg_ts):
        self.clock = max(self.clock, msg_ts)    # rule 2: jump past the sender's time
        return self._tick(name, "receive")


if __name__ == "__main__":
    p1, p2, p3 = LamportProcess("P1"), LamportProcess("P2"), LamportProcess("P3")
    p1.local("a")
    m1 = p1.send("b")            # m1: P1 -> P2
    p2.local("c")
    p2.receive("d", m1)
    m2 = p2.send("e")            # m2: P2 -> P3
    p3.local("f")
    p3.receive("g", m2)
    m3 = p3.send("h")            # m3: P3 -> P1
    p1.receive("i", m3)

    events = p1.log + p2.log + p3.log
    for ts, pid, name, kind in sorted(events):  # total order: (timestamp, process id)
        print(f"{ts:>2} {pid} {name} ({kind})")
