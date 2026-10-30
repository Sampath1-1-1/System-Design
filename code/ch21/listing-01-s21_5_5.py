# Extracted from manuscript/book1-traditional/21-content-delivery-networks.md §21.5.5 (listing 1). Edit the manuscript, not this file.
# Two-tier CDN simulation: how much traffic reaches the origin with and
# without an origin shield. Edge PoPs and the shield are byte-capacity LRU caches;
# object popularity follows a Zipf distribution.
import random
from collections import OrderedDict


class LRUCache:
    """Least-recently-used cache whose capacity is measured in bytes."""

    def __init__(self, capacity_bytes):
        self.capacity = capacity_bytes
        self.used = 0
        self.items = OrderedDict()          # key -> size, oldest first

    def get(self, key):
        if key in self.items:
            self.items.move_to_end(key)     # mark as most recently used
            return True
        return False

    def put(self, key, size):
        if size > self.capacity:
            return                          # too big to cache at all
        if key in self.items:
            self.used -= self.items.pop(key)
        while self.used + size > self.capacity:
            _, old_size = self.items.popitem(last=False)   # evict LRU
            self.used -= old_size
        self.items[key] = size
        self.used += size


def make_workload(n_objects, n_requests, n_pops, alpha, seed):
    """Return object sizes and a trace of (pop, object) requests."""
    rng = random.Random(seed)
    sizes = [rng.choice([20_000, 50_000, 200_000, 1_000_000]) for _ in range(n_objects)]
    cum, total = [], 0.0
    for rank in range(1, n_objects + 1):    # Zipf: weight of rank k is 1/k^alpha
        total += 1.0 / rank ** alpha
        cum.append(total)
    objs = rng.choices(range(n_objects), cum_weights=cum, k=n_requests)
    pops = [rng.randrange(n_pops) for _ in range(n_requests)]
    return sizes, list(zip(pops, objs))


def simulate(sizes, trace, n_pops, edge_bytes, shield_bytes=None):
    """Replay the trace. shield_bytes=None means edges go straight to origin."""
    edges = [LRUCache(edge_bytes) for _ in range(n_pops)]
    shield = LRUCache(shield_bytes) if shield_bytes else None
    s = dict(requests=0, edge_hits=0, shield_hits=0, origin_fetches=0,
             bytes_served=0, origin_bytes=0)
    for pop, obj in trace:
        size = sizes[obj]
        s["requests"] += 1
        s["bytes_served"] += size
        if edges[pop].get(obj):
            s["edge_hits"] += 1
            continue
        if shield is not None and shield.get(obj):
            s["shield_hits"] += 1
        else:                               # fetch from origin
            s["origin_fetches"] += 1
            s["origin_bytes"] += size
            if shield is not None:
                shield.put(obj, size)
        edges[pop].put(obj, size)
    s["request_offload"] = 1 - s["origin_fetches"] / s["requests"]
    s["byte_offload"] = 1 - s["origin_bytes"] / s["bytes_served"]
    return s


if __name__ == "__main__":
    N_OBJ, N_REQ, N_POPS = 50_000, 1_000_000, 20
    sizes, trace = make_workload(N_OBJ, N_REQ, N_POPS, alpha=1.0, seed=21)
    catalog = sum(sizes)
    edge = int(0.03 * catalog)              # each PoP holds 3% of the catalog
    print(f"catalog {catalog / 1e9:.1f} GB, {N_POPS} PoPs x {edge / 1e9:.2f} GB each")
    for label, shield in [("no shield", None),
                          ("shield 10% of catalog", int(0.10 * catalog)),
                          ("shield 30% of catalog", int(0.30 * catalog))]:
        r = simulate(sizes, trace, N_POPS, edge, shield)
        print(f"{label:<22} edge hit {r['edge_hits'] / r['requests']:6.1%}  "
              f"origin fetches {r['origin_fetches']:>7,}  "
              f"request offload {r['request_offload']:6.1%}  "
              f"byte offload {r['byte_offload']:6.1%}  "
              f"origin egress {r['origin_bytes'] / 1e9:5.1f} GB")
