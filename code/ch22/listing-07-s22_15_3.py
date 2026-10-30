# Extracted from manuscript/book1-traditional/22-api-traffic-management.md §22.15.3 (listing 7). Edit the manuscript, not this file.
import hashlib
import json
import sqlite3
import uuid

SCHEMA = """
CREATE TABLE idempotency_keys (
    account_id    TEXT    NOT NULL,
    idem_key      TEXT    NOT NULL,
    fingerprint   TEXT    NOT NULL,          -- hash of method + path + canonical body
    status        TEXT    NOT NULL,          -- 'in_progress' or 'completed'
    locked_until  REAL,                      -- lease for the worker executing the request
    response_code INTEGER,
    response_body TEXT,
    created_at    REAL    NOT NULL,
    PRIMARY KEY (account_id, idem_key)       -- keys are scoped to the caller
);
CREATE TABLE charges (id TEXT PRIMARY KEY, account_id TEXT, amount INTEGER, currency TEXT);
"""


def fingerprint(method, path, body):
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{method} {path}\n{canonical}".encode()).hexdigest()


class LeaseLost(Exception):
    """Another worker took over this key; our business writes must roll back."""


class IdempotencyLayer:
    def __init__(self, db, clock, lease=30.0, ttl=24 * 3600.0):
        self.db, self.clock, self.lease, self.ttl = db, clock, lease, ttl

    def claim(self, account, key, method, path, body):
        """Phase 1. Returns ('proceed', lease) or ('respond', (status, body))."""
        fp, now = fingerprint(method, path, body), self.clock()
        with self.db:                                    # one transaction
            self.db.execute("DELETE FROM idempotency_keys WHERE account_id=? AND idem_key=? "
                            "AND created_at < ?", (account, key, now - self.ttl))
            inserted = self.db.execute(
                "INSERT INTO idempotency_keys VALUES (?,?,?,'in_progress',?,NULL,NULL,?) "
                "ON CONFLICT DO NOTHING", (account, key, fp, now + self.lease, now)).rowcount
            if inserted:
                return "proceed", now + self.lease       # first time we see this key
            fp0, status, locked_until, code, resp = self.db.execute(
                "SELECT fingerprint, status, locked_until, response_code, response_body "
                "FROM idempotency_keys WHERE account_id=? AND idem_key=?", (account, key)).fetchone()
            if fp0 != fp:
                return "respond", (422, {"error": "idempotency key reused with different request"})
            if status == "completed":
                return "respond", (code, json.loads(resp))   # replay the stored response
            if locked_until > now:
                return "respond", (409, {"error": "request with this key is in progress"})
            self.db.execute("UPDATE idempotency_keys SET locked_until=? WHERE account_id=? "
                            "AND idem_key=?", (now + self.lease, account, key))
            return "proceed", now + self.lease           # previous worker died: take over

    def execute(self, account, key, lease, handler, body):
        """Phase 2. Business writes and the stored response commit atomically, and only
        if we still hold the lease we were given (the lease value acts as a fencing token)."""
        with self.db:
            code, resp = handler(self.db, account, body)
            done = self.db.execute(
                "UPDATE idempotency_keys SET status='completed', locked_until=NULL, "
                "response_code=?, response_body=? WHERE account_id=? AND idem_key=? "
                "AND status='in_progress' AND locked_until=?",
                (code, json.dumps(resp), account, key, lease)).rowcount
            if not done:
                raise LeaseLost(key)                     # exception => transaction rolls back
        return code, resp

    def handle(self, account, key, method, path, body, handler):
        action, value = self.claim(account, key, method, path, body)
        return value if action == "respond" else self.execute(account, key, value, handler, body)


def create_charge(db, account, body):
    charge_id = "ch_" + uuid.uuid4().hex[:12]
    db.execute("INSERT INTO charges VALUES (?,?,?,?)",
               (charge_id, account, body["amount"], body["currency"]))
    return 201, {"id": charge_id, "amount": body["amount"], "status": "succeeded"}


if __name__ == "__main__":
    class Clock:
        t = 1_000.0
        def __call__(self):
            return self.t

    clock, db = Clock(), sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    api = IdempotencyLayer(db, clock)
    charges = lambda: db.execute("SELECT COUNT(*) FROM charges").fetchone()[0]
    body, key = {"amount": 2000, "currency": "usd"}, str(uuid.uuid4())

    first = api.handle("acct_1", key, "POST", "/v1/charges", body, create_charge)
    retry = api.handle("acct_1", key, "POST", "/v1/charges", dict(body), create_charge)
    print("1. first call:", first)
    print("2. retry     :", retry, "| charges in DB:", charges())
    assert first == retry and charges() == 1

    other = api.handle("acct_1", key, "POST", "/v1/charges", {"amount": 9999, "currency": "usd"},
                       create_charge)
    print("3. same key, different body:", other[0])
    assert other[0] == 422

    k2 = str(uuid.uuid4())                               # two concurrent duplicates
    a = api.claim("acct_1", k2, "POST", "/v1/charges", body)
    b = api.claim("acct_1", k2, "POST", "/v1/charges", body)
    print("4. concurrent duplicate while first in progress:", b[1][0])
    assert a[0] == "proceed" and b[1][0] == 409

    clock.t += 31                                        # first worker stalls past its lease
    c = api.claim("acct_1", k2, "POST", "/v1/charges", body)
    api.execute("acct_1", k2, c[1], create_charge, body)  # the retry takes over and finishes
    try:
        api.execute("acct_1", k2, a[1], create_charge, body)  # the stalled worker wakes up
    except LeaseLost:
        print("5. stalled worker's late write rejected and rolled back")
    print("   retry took over:", c[0], "| charges in DB:", charges())
    assert c[0] == "proceed" and charges() == 2          # one charge per logical operation

    clock.t += 25 * 3600                                 # beyond the 24 h retention window
    late = api.handle("acct_1", key, "POST", "/v1/charges", body, create_charge)
    print("6. same key after TTL expired:", late[0], "| charges in DB:", charges())
    assert late[0] == 201 and charges() == 3             # the duplicate is no longer caught
