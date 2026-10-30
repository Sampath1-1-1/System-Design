# Extracted from manuscript/book1-traditional/18-scalability.md §18.11.5 (listing 2). Edit the manuscript, not this file.
"""QuickBite capacity plan from 1k to 10M daily active users (Section 18.11).

All inputs are teaching assumptions carried over from Chapter 2 (Table 2.10, Section 2.11).
"""
import math

BROWSE_PER_DAU = 30      # browse requests per DAU per day
ORDERS_PER_DAU = 0.25    # orders per DAU per day
BUSY_HOUR_SHARE = 0.20   # share of daily traffic in the busiest hour
BURST = 2.0              # burst factor above the busiest-hour average
COURIERS_PER_DAU = 0.01  # couriers active at peak per DAU (20,000 at 2M DAU)
UPDATE_INTERVAL_S = 4    # courier location update interval
NODE_RPS = 1_000         # sustained RPS per API node (measured, Section 2.11)
U_TARGET = 0.6           # target utilization per node


def peak(daily):
    return daily * BUSY_HOUR_SHARE / 3_600 * BURST


def api_nodes(rps, zones):
    work = max(1, math.ceil(rps / (NODE_RPS * U_TARGET)))
    if zones == 1:
        return work, work + 1                     # N+1 on one zone
    return work, math.ceil(work * zones / (zones - 1))  # survive one zone loss


stages = [  # (name, DAU, zones)
    ("S1 pilot", 1_000, 2),
    ("S2 city", 20_000, 2),
    ("S3 region", 200_000, 3),
    ("S4 country", 2_000_000, 3),
    ("S5 multi-country", 10_000_000, 3),
]

print(f"{'stage':17} {'DAU':>10} {'browse/s':>9} {'avg/s':>7} {'PAR':>4} "
      f"{'orders/s':>8} {'loc w/s':>8} {'work':>5} {'total':>5} {'avg util':>8}")
for name, dau, zones in stages:
    browse_peak = peak(dau * BROWSE_PER_DAU)
    browse_avg = dau * BROWSE_PER_DAU / 86_400
    orders_peak = peak(dau * ORDERS_PER_DAU)
    loc_writes = dau * COURIERS_PER_DAU / UPDATE_INTERVAL_S
    work, total = api_nodes(browse_peak, zones)
    total = max(total, 2)                         # never fewer than two nodes
    avg_util = browse_avg / (total * NODE_RPS)
    print(f"{name:17} {dau:>10,} {browse_peak:>9,.0f} {browse_avg:>7,.0f} "
          f"{browse_peak / browse_avg:>4.1f} {orders_peak:>8.2f} {loc_writes:>8,.0f} "
          f"{work:>5} {total:>5} {avg_util:>8.1%}")
