# Extracted from manuscript/book1-traditional/12-nosql-databases.md §12.4.4 (listing 1). Edit the manuscript, not this file.
"""A toy single-table store that mimics DynamoDB's key model:
hash(partition key) -> partition; items sorted by sort key inside it;
global secondary indexes maintained from attributes on each item."""
import bisect
import hashlib
from collections import defaultdict

class Table:
    def __init__(self, partitions=4, gsis=()):
        self.partitions = [defaultdict(list) for _ in range(partitions)]
        self.gsis = {name: Table(partitions) for name in gsis}   # name -> index table

    def _part(self, pk):
        h = int(hashlib.md5(pk.encode()).hexdigest(), 16)
        return self.partitions[h % len(self.partitions)]

    def put(self, item):
        rows = self._part(item["PK"])[item["PK"]]          # the item collection
        keys = [r["SK"] for r in rows]
        i = bisect.bisect_left(keys, item["SK"])
        if i < len(rows) and rows[i]["SK"] == item["SK"]:
            rows[i] = item                                   # overwrite same key
        else:
            rows.insert(i, item)                             # keep sorted by SK
        for name, index in self.gsis.items():                # sparse: only if keys present
            if f"{name}PK" in item:
                index.put({**item, "PK": item[f"{name}PK"], "SK": item[f"{name}SK"]})

    def query(self, pk, sk_prefix="", newest_first=False):
        rows = [r for r in self._part(pk).get(pk, []) if r["SK"].startswith(sk_prefix)]
        return rows[::-1] if newest_first else rows

t = Table(gsis=("GSI1", "GSI2"))
t.put({"PK": "CUST#c42", "SK": "PROFILE", "name": "Ana", "email": "ana@example.com"})
t.put({"PK": "EMAIL#ana@example.com", "SK": "EMAIL", "customer": "c42"})
for oid, ts, wh in [("o900", "2026-10-21T08:02", None), ("o901", "2026-10-28T09:15", "WH#w7")]:
    header = {"PK": f"ORDER#{oid}", "SK": "#HEADER", "total": 59.0,
              "GSI1PK": "CUST#c42", "GSI1SK": f"ORDER#{ts}#{oid}"}
    if wh:                                   # only unshipped orders enter GSI2
        header |= {"GSI2PK": wh, "GSI2SK": f"{ts}#{oid}"}
    t.put(header)
    for n in (1, 2):
        t.put({"PK": f"ORDER#{oid}", "SK": f"ITEM#{n:03d}", "sku": f"SKU-{n}", "qty": n})

print("AP1 profile:  ", t.query("CUST#c42", "PROFILE")[0]["name"])
print("AP2 orders:   ", [r["SK"] for r in t.gsis["GSI1"].query("CUST#c42", "ORDER#", newest_first=True)])
print("AP3 order:    ", [r["SK"] for r in t.query("ORDER#o901")])
print("AP4 by email: ", t.query("EMAIL#ana@example.com")[0]["customer"])
print("AP5 to ship:  ", [r["SK"] for r in t.gsis["GSI2"].query("WH#w7")])
