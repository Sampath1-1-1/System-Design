# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.17.3 (listing 13). Edit the manuscript, not this file.
"""E-commerce order schema and queries (Section 11.17), runnable with Python's sqlite3.
The PostgreSQL DDL in the chapter differs only in types (bigint identity, timestamptz)."""
import sqlite3

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  full_name   TEXT NOT NULL,
  city        TEXT NOT NULL,
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE products (
  product_id  INTEGER PRIMARY KEY,
  sku         TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);
CREATE TABLE inventory (
  product_id INTEGER PRIMARY KEY REFERENCES products,
  on_hand    INTEGER NOT NULL CHECK (on_hand >= 0)
);
CREATE TABLE orders (
  order_id        INTEGER PRIMARY KEY,
  customer_id     INTEGER NOT NULL REFERENCES customers,
  status          TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','paid','shipped','cancelled')),
  ship_to         TEXT NOT NULL,
  total_cents     INTEGER NOT NULL DEFAULT 0 CHECK (total_cents >= 0),
  idempotency_key TEXT NOT NULL UNIQUE,
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE order_items (
  order_id         INTEGER NOT NULL REFERENCES orders ON DELETE CASCADE,
  line_no          INTEGER NOT NULL,
  product_id       INTEGER NOT NULL REFERENCES products,
  quantity         INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
  PRIMARY KEY (order_id, line_no)
);
CREATE TABLE payments (
  payment_id   INTEGER PRIMARY KEY,
  order_id     INTEGER NOT NULL REFERENCES orders,
  amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
  provider_ref TEXT UNIQUE,
  status       TEXT NOT NULL CHECK (status IN ('authorized','captured','failed','refunded')),
  created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX orders_customer_created ON orders (customer_id, created_at DESC, order_id DESC);
CREATE INDEX order_items_product     ON order_items (product_id);
CREATE INDEX payments_order          ON payments (order_id);
CREATE INDEX orders_pending_created  ON orders (created_at) WHERE status = 'pending';
"""

class OutOfStock(Exception):
    pass

def place_order(db, customer_id, ship_to, items, idempotency_key):
    """items: list of (product_id, quantity). Returns order_id. All-or-nothing."""
    with db:  # BEGIN ... COMMIT, or ROLLBACK if an exception escapes
        row = db.execute(
            "INSERT INTO orders (customer_id, ship_to, idempotency_key) VALUES (?, ?, ?) "
            "ON CONFLICT (idempotency_key) DO NOTHING RETURNING order_id",
            (customer_id, ship_to, idempotency_key)).fetchone()
        if row is None:  # a retry of a request we already processed
            return db.execute("SELECT order_id FROM orders WHERE idempotency_key = ?",
                              (idempotency_key,)).fetchone()[0]
        order_id, total = row[0], 0
        for line_no, (product_id, qty) in enumerate(sorted(items), start=1):  # fixed lock order
            cur = db.execute(
                "UPDATE inventory SET on_hand = on_hand - ? WHERE product_id = ? AND on_hand >= ?",
                (qty, product_id, qty))
            if cur.rowcount != 1:
                raise OutOfStock(product_id)  # aborts the whole transaction
            price = db.execute("SELECT price_cents FROM products WHERE product_id = ?",
                               (product_id,)).fetchone()[0]
            db.execute("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)",
                       (order_id, line_no, product_id, qty, price))
            total += qty * price
        db.execute("UPDATE orders SET total_cents = ? WHERE order_id = ?", (total, order_id))
        return order_id

ORDER_HISTORY = """
SELECT order_id, status, total_cents, created_at
FROM orders
WHERE customer_id = :cid
  AND (created_at, order_id) < (:after_created, :after_id)   -- keyset cursor
ORDER BY created_at DESC, order_id DESC
LIMIT 20"""

TOP_PRODUCTS = """
SELECT p.sku, SUM(i.quantity) AS units, SUM(i.quantity * i.unit_price_cents) AS revenue_cents
FROM order_items i
JOIN orders   o ON o.order_id   = i.order_id
JOIN products p ON p.product_id = i.product_id
WHERE o.status <> 'cancelled'
GROUP BY p.sku
ORDER BY revenue_cents DESC
LIMIT 3"""

NO_ORDERS = """
SELECT c.email FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)"""

db = sqlite3.connect(":memory:")  # default mode: BEGIN issued implicitly before DML
db.executescript(SCHEMA)
db.executemany("INSERT INTO customers (email, full_name, city) VALUES (?, ?, ?)",
               [("ana@example.com", "Ana", "Pune"), ("bo@example.com", "Bo", "Lima")])
db.executemany("INSERT INTO products (sku, name, price_cents) VALUES (?, ?, ?)",
               [("MUG-1", "Mug", 1200), ("TEE-1", "T-shirt", 2500), ("CAP-1", "Cap", 1800)])
db.execute("INSERT INTO inventory SELECT product_id, 5 FROM products")

o1 = place_order(db, 1, "1 Main St", [(2, 1), (1, 2)], "key-001")
o1_retry = place_order(db, 1, "1 Main St", [(2, 1), (1, 2)], "key-001")
print("order", o1, "retry returns", o1_retry)
try:
    place_order(db, 1, "1 Main St", [(3, 99), (1, 1)], "key-002")
except OutOfStock as e:
    print("out of stock: product", e.args[0])
print("inventory:", db.execute("SELECT product_id, on_hand FROM inventory").fetchall())
print("orders:", db.execute("SELECT order_id, total_cents FROM orders").fetchall())
print("history:", db.execute(ORDER_HISTORY, {"cid": 1, "after_created": "9999", "after_id": 0}).fetchall())
print("top products:", db.execute(TOP_PRODUCTS).fetchall())
print("no orders:", db.execute(NO_ORDERS).fetchall())
print("plan:", db.execute("EXPLAIN QUERY PLAN " + ORDER_HISTORY,
                          {"cid": 1, "after_created": "9999", "after_id": 0}).fetchall()[0][3])
try:
    db.execute("INSERT INTO orders (customer_id, ship_to, idempotency_key) VALUES (99, 'x', 'k')")
except sqlite3.IntegrityError as e:
    print("foreign key enforced:", e)
