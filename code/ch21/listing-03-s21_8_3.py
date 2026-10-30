# Extracted from manuscript/book1-traditional/21-content-delivery-networks.md §21.8.3 (listing 3). Edit the manuscript, not this file.
# Throughput-based versus buffer-based (BBA-style) bitrate selection on the
# same synthetic bandwidth trace. Rates in Mb/s, times in seconds.
LADDER = [0.4, 0.8, 1.5, 3.0, 4.5, 6.0]   # bitrate ladder, Mb/s
SEG = 4.0                                  # segment duration, s
B_MAX = 60.0                               # player buffer limit, s
DT = 0.05                                  # simulation step, s


def bandwidth(t):
    """6 Mb/s, except a 60 s collapse to 0.6 Mb/s starting at t = 30 s."""
    return 0.6 if 30 <= t < 90 else 6.0


def throughput_rule(history, buffer):
    if not history:
        return LADDER[0]
    recent = history[-5:]
    estimate = len(recent) / sum(1 / x for x in recent)   # harmonic mean
    fits = [r for r in LADDER if r <= 0.8 * estimate]     # 20% safety margin
    return fits[-1] if fits else LADDER[0]


def buffer_rule(history, buffer, reservoir=10.0, cushion=30.0):
    if buffer <= reservoir:
        return LADDER[0]
    if buffer >= reservoir + cushion:
        return LADDER[-1]
    target = LADDER[0] + (buffer - reservoir) / cushion * (LADDER[-1] - LADDER[0])
    return max(r for r in LADDER if r <= target)


def play(rule, duration=200.0):
    t = buffer = stall = 0.0
    history, chosen, started = [], [], False
    while t < duration:
        rate = rule(history, buffer)
        bits, start = rate * SEG, t
        while bits > 0:                   # download one segment
            bits -= bandwidth(t) * DT
            t += DT
            if started:
                if buffer > 0:
                    buffer = max(0.0, buffer - DT)
                else:
                    stall += DT           # empty buffer: the video freezes
        history.append(rate * SEG / (t - start))
        buffer += SEG
        started = True
        chosen.append(rate)
        if buffer > B_MAX - SEG:          # buffer full: idle until room
            t += buffer - (B_MAX - SEG)
            buffer = B_MAX - SEG
    switches = sum(a != b for a, b in zip(chosen, chosen[1:]))
    return sum(chosen) / len(chosen), stall, switches


if __name__ == "__main__":
    for name, rule in [("throughput-based", throughput_rule), ("buffer-based", buffer_rule)]:
        avg, stall, switches = play(rule)
        print(f"{name:<17} mean bitrate {avg:4.2f} Mb/s  stalled {stall:4.1f} s  "
              f"switches {switches}")
