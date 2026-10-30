# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.8.2 (listing 5). Edit the manuscript, not this file.
import math

def bplus_tree(n_rows, page_bytes=16 * 1024, fill=0.8, internal_entry=16, leaf_entry=200):
    """Return (fan-out, entries per leaf, pages per level from root to leaves)."""
    usable = page_bytes * fill
    fanout = int(usable // internal_entry)          # child pointers per internal page
    per_leaf = int(usable // leaf_entry)            # entries per leaf page
    levels = [math.ceil(n_rows / per_leaf)]         # leaf level first
    while levels[-1] > 1:
        levels.append(math.ceil(levels[-1] / fanout))
    return fanout, per_leaf, levels[::-1]

for label, leaf_entry in [("clustered, 200-byte rows", 200), ("secondary, 8-byte key + 8-byte PK", 16)]:
    f, L, pages = bplus_tree(10**9, leaf_entry=leaf_entry)
    internal_mib = sum(pages[:-1]) * 16 / 1024
    leaf_gib = pages[-1] * 16 / 1024**2
    print(f"{label}: fan-out={f}, entries/leaf={L}, height={len(pages)}")
    print(f"  pages per level (root..leaf) = {pages}")
    print(f"  internal levels = {internal_mib:,.0f} MiB, leaf level = {leaf_gib:,.1f} GiB")
