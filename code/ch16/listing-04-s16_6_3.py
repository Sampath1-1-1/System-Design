# Extracted from manuscript/book1-traditional/16-search-systems.md §16.6.3 (listing 4). Edit the manuscript, not this file.
"""Simulate a simplified tiered merge policy and measure write amplification:
every refresh flushes one small segment; whenever `merge_factor` segments of the same tier
exist they are merged into one segment of the next tier, until the size cap is reached."""
import math

def simulate(flushes, merge_factor=10, max_tier=3):
    tiers = [0] * (max_tier + 1)      # number of live segments in each tier
    written = 0                       # units written: flushes + merge output
    for _ in range(flushes):
        tiers[0] += 1
        written += 1                  # the flush itself writes one unit
        t = 0
        while t < max_tier and tiers[t] == merge_factor:
            tiers[t] = 0
            tiers[t + 1] += 1
            written += merge_factor ** (t + 1)    # merged segment size in units
            t += 1
    return written / flushes, sum(tiers)

if __name__ == "__main__":
    for flushes in (1_000, 100_000):
        wa, live = simulate(flushes)
        print(f"flushes={flushes:>7,}  write amplification={wa:.2f}  live segments={live}")
    print("predicted 1 + log10(max/min) =", 1 + math.log10(10 ** 3))
