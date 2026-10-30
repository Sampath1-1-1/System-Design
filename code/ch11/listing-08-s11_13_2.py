# Extracted from manuscript/book1-traditional/11-relational-databases.md §11.13.2 (listing 8). Edit the manuscript, not this file.
# PostgreSQL-specific: needs a running PostgreSQL and `pip install psycopg2-binary`.
import psycopg2

DSN = "dbname=shop user=postgres host=localhost"   # adjust to your server

def session(level):
    conn = psycopg2.connect(DSN)
    conn.set_session(isolation_level=level)
    return conn, conn.cursor()

def reset():
    conn = psycopg2.connect(DSN); conn.autocommit = True
    conn.cursor().execute("""
        DROP TABLE IF EXISTS stock, doctors;
        CREATE TABLE stock (product_id int PRIMARY KEY, on_hand int NOT NULL);
        INSERT INTO stock VALUES (42, 10);
        CREATE TABLE doctors (name text PRIMARY KEY, on_call bool NOT NULL);
        INSERT INTO doctors VALUES ('alice', true), ('bob', true);""")
    conn.close()

def try_commit(conn):
    try:
        conn.commit(); return "commit"
    except psycopg2.Error as e:
        conn.rollback(); return "abort: " + e.pgerror.splitlines()[0]

def lost_update(level):           # read-modify-write computed in the application
    reset(); (a, ca), (b, cb) = session(level), session(level)
    ca.execute("SELECT on_hand FROM stock WHERE product_id = 42"); va = ca.fetchone()[0]
    cb.execute("SELECT on_hand FROM stock WHERE product_id = 42"); vb = cb.fetchone()[0]
    ca.execute("UPDATE stock SET on_hand = %s WHERE product_id = 42", (va - 1,)); a.commit()
    try:
        cb.execute("UPDATE stock SET on_hand = %s WHERE product_id = 42", (vb - 1,))
        result = try_commit(b)
    except psycopg2.Error as e:
        b.rollback(); result = "abort: " + e.pgerror.splitlines()[0]
    print(f"lost update, {level}: B {result}")

def write_skew(level):            # invariant: at least one doctor on call
    reset(); (a, ca), (b, cb) = session(level), session(level)
    for cur, me in ((ca, "alice"), (cb, "bob")):
        cur.execute("SELECT count(*) FROM doctors WHERE on_call")
        if cur.fetchone()[0] >= 2:
            cur.execute("UPDATE doctors SET on_call = false WHERE name = %s", (me,))
    print(f"write skew, {level}: A {try_commit(a)}; B {try_commit(b)}")

for level in ("READ COMMITTED", "REPEATABLE READ"):
    lost_update(level)
for level in ("REPEATABLE READ", "SERIALIZABLE"):
    write_skew(level)
