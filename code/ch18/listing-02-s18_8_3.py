"""Target-tracking autoscaler with startup delay and warm-up (Section 18.8).

A simplified model of the Kubernetes HPA rule
    desired = ceil(current * current_metric / target_metric)
applied every 15 s to CPU utilization. New pods serve nothing for STARTUP_S seconds,
then serve at half capacity for WARMUP_S seconds (cold caches, JIT compilation).
Load ramps linearly from 6,000 to 12,000 RPS over five minutes.
"""
import math

POD_RPS = 1_000        # requests/s one warm pod handles at 100% CPU
STARTUP_S = 60         # scheduling + image pull + process start + readiness probe
WARMUP_S = 60          # serving at half capacity while caches and JIT warm up
SYNC_S = 15            # autoscaler evaluation period
METRIC_LAG_S = 30      # age of the utilization sample the autoscaler sees
TOLERANCE = 0.10       # no action while |ratio - 1| <= 10%
RAMP_S = 300           # load doubles over five minutes, starting at t = 60 s


def load(t):
    return 6_000 + 6_000 * min(max(t - 60, 0), RAMP_S) / RAMP_S


def run(target):
    pods = [-10_000] * math.ceil(6_000 / (POD_RPS * target))   # start times; all warm
    worst, overloaded = 0.0, 0
    for t in range(0, 1_200):
        cap = 0.0
        for start in pods:
            age = t - start
            if age >= STARTUP_S + WARMUP_S:
                cap += POD_RPS
            elif age >= STARTUP_S:
                cap += POD_RPS / 2
        util = load(t) / cap
        worst = max(worst, util)
        overloaded += util > 1.0
        if t % SYNC_S == 0 and t >= METRIC_LAG_S:
            # Average CPU over all pods as the autoscaler sees it; pods that are
            # not ready count as idle, as the HPA assumes when scaling up.
            seen = load(t - METRIC_LAG_S) / (len(pods) * POD_RPS)
            ratio = seen / target
            if abs(ratio - 1) > TOLERANCE:
                desired = math.ceil(len(pods) * ratio)
                if desired > len(pods):
                    pods += [t] * (desired - len(pods))
    return worst, overloaded, len(pods)


print("target  peak util  seconds >100%  final pods")
for target in (0.5, 0.6, 0.7, 0.8):
    worst, over, final = run(target)
    print(f"{target:5.0%}   {worst:8.0%}   {over:12d}   {final:9d}")
