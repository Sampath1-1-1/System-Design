# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.8.1 (listing 7). Edit the manuscript, not this file.
import hashlib

def h(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def leaf_hash(record: bytes) -> bytes:
    return h(b"\x00" + record)          # domain separation: leaves and interior nodes
def node_hash(left: bytes, right: bytes) -> bytes:
    return h(b"\x01" + left + right)    # can never be confused (cf. RFC 6962)

def build(records):
    """Return all levels, leaves first. An odd node is promoted unchanged."""
    level = [leaf_hash(r) for r in records]
    levels = [level]
    while len(level) > 1:
        nxt = [node_hash(level[i], level[i + 1]) for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        levels.append(nxt)
        level = nxt
    return levels

def proof(levels, index):
    """Sibling hashes from leaf to root: the audit path for one record."""
    path = []
    for level in levels[:-1]:
        sibling = index ^ 1
        if sibling < len(level):
            path.append((sibling < index, level[sibling]))   # (sibling is on the left?, hash)
        index //= 2
    return path

def verify(record, path, root):
    acc = leaf_hash(record)
    for sibling_is_left, sib in path:
        acc = node_hash(sib, acc) if sibling_is_left else node_hash(acc, sib)
    return acc == root

def diff(a, b, level=None, index=0, found=None):
    """Anti-entropy: descend only into subtrees whose hashes differ. Returns (leaf indexes, hashes compared)."""
    if found is None:
        level, found = len(a) - 1, ([], [0])
    found[1][0] += 1
    if a[level][index] == b[level][index]:
        return found
    if level == 0:
        found[0].append(index)
        return found
    for child in (2 * index, 2 * index + 1):
        if child < len(a[level - 1]):
            diff(a, b, level - 1, child, found)
    return found

records = [f"key-{i}=value-{i}".encode() for i in range(1 << 20)]       # 1,048,576 records
replica_a = build(records)
records_b = list(records)
for i in (12_345, 777_777):                                               # two divergent records
    records_b[i] = b"stale"
replica_b = build(records_b)

root = replica_a[-1][0]
p = proof(replica_a, 424_242)
print(f"tree height = {len(replica_a) - 1}, proof length = {len(p)} hashes = {32 * len(p)} bytes")
print("valid record verifies:", verify(records[424_242], p, root))
print("tampered record verifies:", verify(b"key-424242=forged", p, root))
leaves, compared = diff(replica_a, replica_b)
print(f"roots equal: {replica_a[-1][0] == replica_b[-1][0]}; divergent leaves: {leaves}; "
      f"hashes compared: {compared[0]} of {sum(len(l) for l in replica_a):,}")
