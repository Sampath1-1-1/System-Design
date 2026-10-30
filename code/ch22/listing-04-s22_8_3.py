# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.8.3 (listing 4). Edit the manuscript, not this file.
"""Simulate one tenant's global limit of 1,000 requests per 1-second window, enforced by
10 gateway nodes that receive skewed traffic. No Redis needed: the 'central store' is a dict."""
import random

LIMIT, NODES, SECONDS = 1000, 10, 20
WEIGHTS = [0.5] + [0.5 / 9] * 9                 # node 0 gets half the tenant's traffic


def arrivals(offered_rps, seed=1):
    rng, events = random.Random(seed), []
    for node, w in enumerate(WEIGHTS):
        t = 0.0
        while True:
            t += rng.expovariate(offered_rps * w)
            if t >= SECONDS:
                break
            events.append((t, node))
    return sorted(events)


def static_split(events):
    """Each node enforces LIMIT/N locally. Zero coordination."""
    counts = {}
    def allow(t, node):
        k = (int(t), node)
        if counts.get(k, 0) < LIMIT / NODES:
            counts[k] = counts.get(k, 0) + 1
            return True
        return False
    return allow, lambda: 0


def centralized(events):
    """Every decision is an atomic increment on one shared counter (Redis + Lua in production)."""
    counts, calls = {}, [0]
    def allow(t, node):
        calls[0] += 1                            # one network round trip per request
        k = int(t)
        if counts.get(k, 0) < LIMIT:
            counts[k] = counts.get(k, 0) + 1
            return True
        return False
    return allow, lambda: calls[0]


def local_with_sync(events, sync_interval):
    """Nodes count locally and exchange counts every sync_interval seconds."""
    local = [0] * NODES                          # this window's admits per node (true values)
    seen = [0] * NODES                           # each node's last snapshot of the others' total
    state = {"window": 0, "next_sync": sync_interval, "msgs": 0}
    def allow(t, node):
        while t >= state["next_sync"]:           # periodic all-to-all exchange of counters
            total = sum(local)
            for i in range(NODES):
                seen[i] = total - local[i]
            state["msgs"] += NODES * (NODES - 1)
            state["next_sync"] += sync_interval
        if int(t) != state["window"]:            # new window: everyone resets
            state["window"] = int(t)
            local[:] = [0] * NODES
            seen[:] = [0] * NODES
        if seen[node] + local[node] < LIMIT:     # decide on a possibly stale global view
            local[node] += 1
            return True
        return False
    return allow, lambda: state["msgs"]


def quota_leases(events):
    """A coordinator re-divides the limit once per window in proportion to each node's
    demand in the previous window; nodes then enforce their quota locally."""
    quota = [LIMIT / NODES] * NODES
    demand, used = [0] * NODES, [0] * NODES
    state = {"window": 0, "msgs": 0}
    def allow(t, node):
        if int(t) != state["window"]:            # window boundary: report demand, get quotas
            total = sum(demand) or 1
            for i in range(NODES):
                quota[i] = LIMIT * demand[i] / total
            state["msgs"] += 2 * NODES           # N reports in, N quota grants out
            state["window"] = int(t)
            demand[:], used[:] = [0] * NODES, [0] * NODES
        demand[node] += 1
        if used[node] + 1 <= quota[node]:
            used[node] += 1
            return True
        return False
    return allow, lambda: state["msgs"]


def run(name, factory, events):
    allow, cost = factory(events)
    per_window = [0] * SECONDS
    for t, node in events:
        if allow(t, node):
            per_window[int(t)] += 1
    steady = per_window[1:]                      # skip the first window (warm-up)
    print(f"{name:26s} mean {sum(steady)/len(steady):7.1f}/s  max {max(steady):5d}  "
          f"coordination msgs/s {cost()/SECONDS:9.0f}")
    return per_window


if __name__ == "__main__":
    for offered in (1500, 3000):
        events = arrivals(offered)
        print(f"Offered {offered} RPS, global limit {LIMIT}/s, {NODES} nodes, node 0 gets 50%")
        s = run("static split (L/N each)", static_split, events)
        c = run("centralized counter", centralized, events)
        y100 = run("local + sync every 100 ms", lambda e: local_with_sync(e, 0.1), events)
        y10 = run("local + sync every 10 ms", lambda e: local_with_sync(e, 0.01), events)
        q = run("demand-weighted quotas", quota_leases, events)
        print()
        assert max(c) <= LIMIT and max(s) <= LIMIT and max(q) <= LIMIT
        assert max(y100) > LIMIT >= max(c)       # stale views overshoot; exact counting does not
