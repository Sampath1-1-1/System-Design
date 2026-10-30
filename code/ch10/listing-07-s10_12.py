# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.12 (listing 7). Edit the manuscript, not this file.
"""Tamper-evident audit log: each entry commits to the previous one (hash chain)."""
import hashlib
import hmac
import json

GENESIS = "0" * 64

def entry_hash(prev_hash: str, event: dict) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(prev_hash.encode() + payload).hexdigest()

class AuditLog:
    def __init__(self):
        self.entries: list[dict] = []

    def append(self, event: dict) -> str:
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        h = entry_hash(prev, event)
        self.entries.append({"event": event, "prev": prev, "hash": h})
        return h                       # publish/anchor this "head" externally

    def verify(self, anchored_head: str | None = None) -> int | None:
        """Return index of first bad entry, or None if the chain is intact."""
        prev = GENESIS
        for i, e in enumerate(self.entries):
            if e["prev"] != prev or not hmac.compare_digest(e["hash"], entry_hash(prev, e["event"])):
                return i
            prev = e["hash"]
        if anchored_head is not None and prev != anchored_head:
            return len(self.entries)   # tail truncated or rewritten
        return None
