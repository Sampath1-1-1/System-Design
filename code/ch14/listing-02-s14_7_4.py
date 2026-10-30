# Extracted from manuscript/book1-traditional/14-database-scaling.md §14.7.4 (listing 2). Edit the manuscript, not this file.
"""Shard-count calculator: the binding constraint among storage, writes and reads."""
import math


def shards_needed(data_tb, disk_tb, fill, writes, write_cap, reads,
                  read_nodes, read_cap, util):
    terms = {
        "storage": data_tb / (disk_tb * fill),
        "writes": writes / (write_cap * util),
        "reads": reads / (read_nodes * read_cap * util),
    }
    binding = max(terms, key=terms.get)
    return math.ceil(terms[binding]), binding, terms


def even_logical_counts(physical, candidates=(512, 720, 960, 1024, 4096)):
    """Logical-shard counts that divide evenly over `physical` shards."""
    return [c for c in candidates if c % physical == 0]


if __name__ == "__main__":
    s, binding, terms = shards_needed(
        data_tb=30 + 24 * 1.5, disk_tb=8, fill=0.6,
        writes=90_000 * 1.5, write_cap=10_000,
        reads=1_200_000 * (1 - 0.90), read_nodes=2, read_cap=20_000, util=0.6)
    print({k: round(v, 2) for k, v in terms.items()})
    print(f"minimum shards = {s} ({binding}-bound)")
    physical = 3 * math.ceil(s / 3)          # round up to a multiple of 3 zones
    print(f"physical shards = {physical}, nodes = {physical * 3}, "
          f"even logical counts = {even_logical_counts(physical)}")
