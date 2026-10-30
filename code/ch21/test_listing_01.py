# Tests for listing-01-s21_5_5.py (two-tier CDN simulation). Run: python3 -m unittest -v test_listing_01.py
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "cdn_sim", Path(__file__).with_name("listing-01-s21_5_5.py"))
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)


class LRUCacheTest(unittest.TestCase):
    def test_evicts_least_recently_used(self):
        c = sim.LRUCache(300)
        c.put("a", 100); c.put("b", 100); c.put("c", 100)
        self.assertTrue(c.get("a"))          # a becomes most recent
        c.put("d", 100)                      # must evict b, the LRU
        self.assertFalse(c.get("b"))
        self.assertTrue(c.get("a") and c.get("c") and c.get("d"))
        self.assertLessEqual(c.used, c.capacity)

    def test_oversized_object_not_cached(self):
        c = sim.LRUCache(100)
        c.put("big", 101)
        self.assertFalse(c.get("big"))
        self.assertEqual(c.used, 0)

    def test_reinsert_updates_size(self):
        c = sim.LRUCache(300)
        c.put("a", 100); c.put("a", 250)
        self.assertEqual(c.used, 250)


class SimulationTest(unittest.TestCase):
    def setUp(self):
        self.pops = 5
        self.sizes, self.trace = sim.make_workload(2_000, 30_000, self.pops, 0.9, seed=1)
        self.catalog = sum(self.sizes)

    def test_request_conservation(self):
        r = sim.simulate(self.sizes, self.trace, self.pops, int(0.05 * self.catalog),
                         int(0.2 * self.catalog))
        misses = r["requests"] - r["edge_hits"]
        self.assertEqual(r["requests"], len(self.trace))
        self.assertEqual(r["shield_hits"] + r["origin_fetches"], misses)

    def test_shield_never_increases_origin_load(self):
        edge = int(0.05 * self.catalog)
        base = sim.simulate(self.sizes, self.trace, self.pops, edge, None)
        for frac in (0.01, 0.1, 0.5):
            shielded = sim.simulate(self.sizes, self.trace, self.pops, edge,
                                    int(frac * self.catalog))
            self.assertEqual(shielded["edge_hits"], base["edge_hits"])
            self.assertLessEqual(shielded["origin_fetches"], base["origin_fetches"])

    def test_infinite_caches_fetch_each_object_once_with_shield(self):
        big = 10 * self.catalog
        distinct_objects = len({o for _, o in self.trace})
        distinct_pairs = len(set(self.trace))
        no_shield = sim.simulate(self.sizes, self.trace, self.pops, big, None)
        shield = sim.simulate(self.sizes, self.trace, self.pops, big, big)
        self.assertEqual(no_shield["origin_fetches"], distinct_pairs)   # one per PoP
        self.assertEqual(shield["origin_fetches"], distinct_objects)    # one in total

    def test_offload_ratios_in_range(self):
        r = sim.simulate(self.sizes, self.trace, self.pops, int(0.05 * self.catalog))
        self.assertGreaterEqual(r["request_offload"], 0.0)
        self.assertLessEqual(r["request_offload"], 1.0)
        self.assertAlmostEqual(r["request_offload"],
                               r["edge_hits"] / r["requests"])


if __name__ == "__main__":
    unittest.main()
