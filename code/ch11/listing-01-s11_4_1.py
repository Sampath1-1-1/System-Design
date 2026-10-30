# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.4.1 (listing 1). Edit the manuscript, not this file.
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
PRAGMA foreign_keys = ON;            -- SQLite enforces FKs only when this is set
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers (customer_id)
);
INSERT INTO customers VALUES (1, 'ana@example.com');
INSERT INTO orders VALUES (100, 1);
""")
for sql in ["INSERT INTO orders VALUES (101, 99)",                    # no customer 99
            "INSERT INTO customers VALUES (2, 'ana@example.com')",   # duplicate candidate key
            "DELETE FROM customers WHERE customer_id = 1"]:          # still has an order
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as e:
        print(f"{sql[:40]:<42} -> {e}")
