# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.11.1 (listing 7). Edit the manuscript, not this file.
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE accounts (
  account_id    INTEGER PRIMARY KEY,
  balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0)   -- invariant: no overdraft
);
INSERT INTO accounts VALUES (1, 10000), (2, 0);
""")

def transfer(src, dst, cents):
    try:
        with db:                                   # BEGIN; ... COMMIT (or ROLLBACK on error)
            db.execute("UPDATE accounts SET balance_cents = balance_cents + ? "
                       "WHERE account_id = ?", (cents, dst))          # credit first, on purpose
            db.execute("UPDATE accounts SET balance_cents = balance_cents - ? "
                       "WHERE account_id = ?", (cents, src))          # may violate the CHECK
        return "committed"
    except sqlite3.IntegrityError as e:
        return f"rolled back ({e})"

print(transfer(1, 2, 7000), db.execute("SELECT * FROM accounts").fetchall())
print(transfer(1, 2, 7000), db.execute("SELECT * FROM accounts").fetchall())
