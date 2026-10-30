# Extracted from manuscript/book1-traditional/02-thinking-like-a-system-designer.md §2.6.1 (listing 1). Edit the manuscript, not this file.
# Bottleneck finder using the utilization law (U = X * D / c).
resources = {
    # name: (demand per request in seconds, parallel units)
    "api_cpu":   (0.008, 32),
    "db_cpu":    (0.005, 8),
    "wal_disk":  (0.002, 1),
    "network":   (0.00002, 1),
    "db_pool":   (0.320, 20),
    "hot_row":   (0.320, 1),
}
arrival_rate = 60.0  # requests per second

for name, (demand, units) in sorted(
        resources.items(), key=lambda kv: kv[1][0] / kv[1][1], reverse=True):
    max_x = units / demand
    util = arrival_rate * demand / units
    flag = "SATURATED" if util >= 1 else ("HOT" if util >= 0.7 else "ok")
    print(f"{name:9s} max={max_x:9.1f}/s  util@{arrival_rate:.0f}/s={util:7.1%}  {flag}")
