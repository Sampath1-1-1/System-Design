# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.15.3 (listing 10). Edit the manuscript, not this file.
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE products (
  product_id  INTEGER PRIMARY KEY,
  description TEXT    NOT NULL,
  version     INTEGER NOT NULL DEFAULT 1
);
INSERT INTO products (product_id, description) VALUES (7, 'Blue mug');
""")

def save(product_id, new_description, version_read):
    """Optimistic concurrency control: the write succeeds only if nobody wrote since we read."""
    with db:
        cur = db.execute(
            "UPDATE products SET description = ?, version = version + 1 "
            "WHERE product_id = ? AND version = ?",
            (new_description, product_id, version_read))
    return cur.rowcount == 1          # 0 rows updated means a concurrent edit won

# Two editors load the same row (version 1), then both try to save.
_, _, v_alice = db.execute("SELECT * FROM products WHERE product_id = 7").fetchone()
_, _, v_bob = db.execute("SELECT * FROM products WHERE product_id = 7").fetchone()
print("alice saved:", save(7, "Blue ceramic mug", v_alice))
print("bob saved:  ", save(7, "Navy mug", v_bob))       # rejected: must re-read and retry
print(db.execute("SELECT * FROM products").fetchall())
