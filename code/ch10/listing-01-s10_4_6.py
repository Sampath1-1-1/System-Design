# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.4.6 (listing 1). Edit the manuscript, not this file.
"""HMAC-SHA256 request signing and verification with replay protection."""
import hashlib
import hmac
import secrets
import time

MAX_SKEW_SECONDS = 300          # accept requests at most 5 minutes old/new

def canonical_request(method: str, path: str, timestamp: str,
                      nonce: str, body: bytes) -> bytes:
    body_hash = hashlib.sha256(body).hexdigest()
    # Every field the server relies on must be covered by the signature.
    return "\n".join([method.upper(), path, timestamp, nonce, body_hash]).encode()

def sign(key: bytes, method: str, path: str, body: bytes) -> dict:
    ts = str(int(time.time()))
    nonce = secrets.token_hex(16)
    mac = hmac.new(key, canonical_request(method, path, ts, nonce, body),
                   hashlib.sha256).hexdigest()
    return {"X-Key-Id": "client-42", "X-Timestamp": ts,
            "X-Nonce": nonce, "X-Signature": mac}

class Verifier:
    def __init__(self, keys: dict[str, bytes]):
        self.keys = keys
        self.seen_nonces: dict[str, int] = {}    # production: shared store with TTL

    def verify(self, method: str, path: str, body: bytes, headers: dict) -> bool:
        key = self.keys.get(headers.get("X-Key-Id", ""))
        if key is None:
            return False
        ts = int(headers["X-Timestamp"])
        now = int(time.time())
        if abs(now - ts) > MAX_SKEW_SECONDS:
            return False                                    # stale or future
        expected = hmac.new(key, canonical_request(method, path, headers["X-Timestamp"],
                                                   headers["X-Nonce"], body),
                            hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, headers["X-Signature"]):
            return False                                    # forged or tampered
        # Expire old nonces, then reject a nonce we have already seen (replay).
        self.seen_nonces = {n: t for n, t in self.seen_nonces.items()
                            if now - t <= 2 * MAX_SKEW_SECONDS}
        if headers["X-Nonce"] in self.seen_nonces:
            return False
        self.seen_nonces[headers["X-Nonce"]] = ts
        return True
