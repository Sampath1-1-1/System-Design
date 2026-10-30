# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.7.2 (listing 4). Edit the manuscript, not this file.
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, email TEXT)")
db.execute("INSERT INTO users VALUES ('alice', 'a@example.com')")
attacker_input = "x' OR '1'='1"
# Vulnerable (illustrative, never do this): f"... WHERE name = '{attacker_input}'"
rows = db.execute("SELECT email FROM users WHERE name = ?", (attacker_input,)).fetchall()
print(rows)   # [] -- the input is treated purely as a value
