# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.7.4 (listing 4). Edit the manuscript, not this file.
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,          -- rowid alias: the table's clustered key
  customer_id INTEGER NOT NULL,
  status      TEXT    NOT NULL,
  total_cents INTEGER NOT NULL,
  created_at  TEXT    NOT NULL
);
CREATE INDEX orders_cust_created ON orders (customer_id, created_at);
CREATE INDEX orders_pending ON orders (created_at) WHERE status = 'pending';
""")
db.executemany(
    "INSERT INTO orders (customer_id, status, total_cents, created_at) VALUES (?,?,?,?)",
    [(i % 1000, "pending" if i % 100 == 0 else "shipped", i, f"2026-10-{1 + i % 28:02d}")
     for i in range(50_000)])

queries = {
    "both columns":        "SELECT * FROM orders WHERE customer_id = 7 AND created_at >= '2026-10-15'",
    "leftmost column only": "SELECT * FROM orders WHERE customer_id = 7",
    "second column only":  "SELECT * FROM orders WHERE created_at >= '2026-10-15'",
    "covering":            "SELECT created_at FROM orders WHERE customer_id = 7",
    "partial index":       "SELECT order_id FROM orders WHERE status = 'pending' AND created_at < '2026-10-03'",
}
for label, sql in queries.items():
    plan = db.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    print(f"{label:<21} -> {plan[0][3]}")
