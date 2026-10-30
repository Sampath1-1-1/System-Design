# Extracted from manuscript/book1-traditional/14-database-scaling.md §14.4.4 (listing 1). Edit the manuscript, not this file.
"""Read-your-writes and monotonic reads with log-position tokens (simulation)."""
import random

class Replica:
    def __init__(self, name):
        self.name, self.applied = name, 0       # applied log position (LSN)

class Router:
    """Routes reads to any replica that has applied the session's watermark."""

    def __init__(self, replicas):
        self.primary_lsn = 0
        self.replicas = replicas
        self.watermark = {}                      # session -> minimum LSN to read

    def write(self, session):
        self.primary_lsn += 1                    # commit on the primary
        self.watermark[session] = self.primary_lsn
        return self.primary_lsn

    def read(self, session):
        need = self.watermark.get(session, 0)
        fresh = [r for r in self.replicas if r.applied >= need]
        if not fresh:
            return "primary"                     # nobody is fresh enough yet
        chosen = random.choice(fresh)
        # monotonic reads: later reads must be at least as fresh as this one
        self.watermark[session] = max(need, chosen.applied)
        return chosen.name

if __name__ == "__main__":
    random.seed(7)
    r1, r2 = Replica("replica-1"), Replica("replica-2")
    router = Router([r1, r2])
    lsn = router.write("alice")                  # alice writes; LSN 1
    print("right after write  ->", router.read("alice"))   # nobody has LSN 1
    r1.applied = lsn                             # replica-1 catches up
    print("replica-1 caught up ->", router.read("alice"))
    print("bob (no writes)     ->", router.read("bob"))    # any replica is fine
