# Extracted from manuscript/book1-traditional/24-distributed-systems-fundamentals.md §24.9.6 (listing 1). Edit the manuscript, not this file.
"""Clock arithmetic: NTP offset/delay, drift-based resync interval,
and how last-writer-wins (LWW) loses a write when clocks are skewed."""


def ntp_offset_delay(t1, t2, t3, t4):
    """RFC 5905 on-wire calculation (all values in seconds).
    t1, t4 are read from the client clock; t2, t3 from the server clock."""
    offset = ((t2 - t1) + (t3 - t4)) / 2   # theta: server clock minus client clock
    delay = (t4 - t1) - (t3 - t2)          # delta: round trip minus server hold time
    return offset, delay


def resync_interval(max_skew_s, drift_ppm):
    """Longest interval between syncs that keeps two clocks within max_skew_s
    when each may drift up to drift_ppm in opposite directions."""
    return max_skew_s / (2 * drift_ppm * 1e-6)


class LWWRegister:
    """A replica that keeps the value with the highest wall-clock timestamp."""

    def __init__(self):
        self.value, self.ts = None, float("-inf")

    def apply(self, value, ts):
        if ts > self.ts:
            self.value, self.ts = value, ts
            return "applied"
        return "discarded"


if __name__ == "__main__":
    theta, delta = ntp_offset_delay(0.000, 0.120, 0.121, 0.061)
    print(f"NTP: offset {theta * 1000:.1f} ms, delay {delta * 1000:.1f} ms, "
          f"error bound +/-{delta / 2 * 1000:.1f} ms")

    print(f"Resync every {resync_interval(0.001, 50):.0f} s to stay within 1 ms at 50 ppm")

    # Node A's clock runs 150 ms fast; node B's clock is correct.
    skew = {"A": 0.150, "B": 0.000}
    writes = [  # (true time in s, node, value): the second write happens 50 ms later
        (10.000, "A", "caption v1"),
        (10.050, "B", "caption v2"),
    ]
    replica = LWWRegister()
    for true_t, node, value in writes:
        stamp = true_t + skew[node]                      # what the node's clock says
        print(f"t={true_t:.3f} node {node} writes {value!r:13} stamp={stamp:.3f}"
              f" -> {replica.apply(value, stamp)}")
    print(f"Final value: {replica.value!r} (the later write was lost)")
