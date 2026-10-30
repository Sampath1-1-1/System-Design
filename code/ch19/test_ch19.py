"""Tests for the Chapter 19 listings. Run: python3 -m pytest code/ch19 (or python3 test_ch19.py)."""
import importlib.util
import math
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wrr = load("listing-01-s19_4_1")
bins = load("listing-02-s19_4_4")
sim = load("listing-03-s19_4_5")
bounded = load("listing-04-s19_4_7")
maglev = load("listing-05-s19_4_8")


def test_smooth_wrr_matches_nginx_sequence_and_shares():
    lb = wrr.SmoothWRR({"a": 5, "b": 1, "c": 1})
    assert [lb.pick() for _ in range(7)] == list("aabacaa")
    lb = wrr.SmoothWRR({"x": 3, "y": 2})
    assert Counter(lb.pick() for _ in range(500)) == {"x": 300, "y": 200}


def test_two_choices_beats_one_choice():
    rng = random.Random(3)
    one = bins.max_load(20_000, 1, rng)
    two = bins.max_load(20_000, 2, rng)
    assert two < one and two <= 4


def test_simulation_ranks_policies_on_heterogeneous_servers():
    r = {c.__name__: sim.simulate(c, 0.6, requests=40_000) for c in sim.POLICIES}
    for good in ("WeightedRR", "LeastConnections", "PowerOfTwo"):
        assert r[good]["q_p99"] < r["RoundRobin"]["q_p99"] < r["Random"]["q_p99"]
    stale_lc = sim.simulate(sim.LeastConnections, 0.85, refresh=2.0, requests=40_000)
    stale_p2c = sim.simulate(sim.PowerOfTwo, 0.85, refresh=2.0, requests=40_000)
    assert stale_p2c["q_p99"] < stale_lc["q_p99"]          # herd behavior


def test_bounded_load_cap_is_respected():
    servers = [f"s{i}" for i in range(10)]
    keys = ["hot"] * 300 + [f"k{i}" for i in range(700)]
    ring = bounded.Ring(servers, vnodes=20)
    load, _ = ring.assign(keys, eps=0.25)
    assert max(load.values()) <= math.ceil(1.25 * len(keys) / len(servers))
    plain, _ = ring.assign(keys)
    assert max(plain.values()) >= 300


def test_maglev_balance_and_small_example():
    p = {"B0": (3, 4), "B1": (0, 2), "B2": (3, 1)}
    assert maglev.populate(["B0", "B1", "B2"], 7, p) == ["B1", "B0", "B1", "B0", "B2", "B2", "B0"]
    names = [f"b{i}" for i in range(13)]
    counts = Counter(maglev.populate(names, 251))
    assert max(counts.values()) - min(counts.values()) <= 1
    assert sum(counts.values()) == 251


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
