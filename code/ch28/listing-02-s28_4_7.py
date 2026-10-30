# Extracted from manuscript/book1-traditional/28-distributed-transactions.md §28.4.7 (listing 2). Edit the manuscript, not this file.
"""Two-phase commit with presumed abort: coordinator crash and recovery from its log.

Each node has a durable log (a list that survives crash()) and volatile state
(locks, pending writes) that is lost on a crash and rebuilt from the log.
Run it directly with python3 to execute the scenario tests.
"""
import unittest


class Crash(Exception):
    """Raised when a node is killed at an injected crash point."""


class Participant:
    def __init__(self, name, balances):
        self.name, self.up = name, True
        self.data = dict(balances)        # committed state (durable)
        self.log = []                     # durable log: (record, txid, payload)
        self.locks, self.pending = {}, {}  # volatile: key -> txid, txid -> new values

    def prepare(self, txid, deltas):
        if not self.up:
            raise Crash(self.name)        # the coordinator sees a timeout
        new = {}
        for key, delta in deltas.items():
            if self.locks.get(key, txid) != txid:
                return "NO"               # row locked by an in-doubt or active txn
            new[key] = self.data[key] + delta
            if new[key] < 0:
                return "NO"               # invariant: no overdraft
        for key in new:
            self.locks[key] = txid
        self.pending[txid] = new
        self.log.append(("PREPARED", txid, new))   # forced before voting YES
        return "YES"

    def finish(self, txid, decision):
        """Apply COMMIT or ABORT. Idempotent: duplicates are harmless."""
        if not self.up:
            raise Crash(self.name)
        new = self.pending.pop(txid, None)
        if new is None:
            return "ACK"                  # already finished, or never prepared
        if decision == "COMMIT":
            self.data.update(new)
            self.log.append(("COMMIT", txid, None))   # forced, then ACK
        else:
            self.log.append(("ABORT", txid, None))    # not forced under presumed abort
        for key in new:
            del self.locks[key]
        return "ACK"

    def crash(self):
        self.up, self.locks, self.pending = False, {}, {}

    def recover(self):
        """Redo from the log: a PREPARED txn with no outcome is in doubt and relocked."""
        self.up = True
        done = {txid for rec, txid, _ in self.log if rec in ("COMMIT", "ABORT")}
        for rec, txid, new in self.log:
            if rec == "PREPARED" and txid not in done:
                self.pending[txid] = new
                for key in new:
                    self.locks[key] = txid

    def in_doubt(self):
        return sorted(self.pending)

    def resolve(self, coordinator):
        """Termination protocol: ask the coordinator about each in-doubt txn."""
        for txid in self.in_doubt():
            if not coordinator.up:
                return False              # blocked: cannot decide alone
            self.finish(txid, coordinator.outcome(txid))
        return True


class Coordinator:
    def __init__(self, participants):
        self.parts = {p.name: p for p in participants}
        self.log = []                     # durable
        self.up, self.crash_at = True, None

    def _point(self, where):
        if self.crash_at == where:
            self.up = False
            raise Crash("coordinator at " + where)

    def run(self, txid, plan):
        """plan: {participant name: {key: delta}}. Returns COMMIT or ABORT."""
        votes = {}
        for name, deltas in plan.items():          # phase 1: prepare
            try:
                votes[name] = self.parts[name].prepare(txid, deltas)
            except Crash:
                votes[name] = "NO"                 # timeout counts as NO
        self._point("after_votes")
        if all(v == "YES" for v in votes.values()):
            self.log.append(("COMMIT", txid, sorted(plan)))   # forced: commit point
            self._point("after_decision")
            self._send(txid, "COMMIT", sorted(plan))
            return "COMMIT"
        # presumed abort: no forced log record, no ACKs needed
        yes = [n for n, v in votes.items() if v == "YES"]
        for name in yes:
            try:
                self.parts[name].finish(txid, "ABORT")
            except Crash:
                pass                               # it will ask later; answer is ABORT
        return "ABORT"

    def _send(self, txid, decision, names):
        acked = 0
        for i, name in enumerate(names):
            try:
                self.parts[name].finish(txid, decision)
                acked += 1
            except Crash:
                pass
            if i == 0:
                self._point("mid_phase2")
        if acked == len(names):
            self.log.append(("END", txid, None))   # not forced; allows log truncation

    def outcome(self, txid):
        """Answer an inquiry. No COMMIT record means ABORT (presumed abort)."""
        return "COMMIT" if any(r == "COMMIT" and t == txid for r, t, _ in self.log) else "ABORT"

    def recover(self):
        """Re-drive phase 2 for every COMMIT without END; everything else is aborted."""
        self.up, self.crash_at = True, None
        ended = {t for r, t, _ in self.log if r == "END"}
        for rec, txid, names in list(self.log):
            if rec == "COMMIT" and txid not in ended:
                self._send(txid, "COMMIT", names)


def bank():
    a, b = Participant("A", {"acct7": 50_000}), Participant("B", {"acct9": 0})
    return a, b, Coordinator([a, b])


TRANSFER = {"A": {"acct7": -10_000}, "B": {"acct9": +10_000}}


class TwoPhaseCommitTests(unittest.TestCase):
    def total(self, a, b):
        return a.data["acct7"] + b.data["acct9"]

    def test_happy_path(self):
        a, b, c = bank()
        self.assertEqual(c.run("t1", TRANSFER), "COMMIT")
        self.assertEqual((a.data["acct7"], b.data["acct9"]), (40_000, 10_000))
        self.assertEqual([r for r, _, _ in c.log], ["COMMIT", "END"])
        self.assertEqual(a.locks, {})

    def test_no_vote_aborts_without_coordinator_log(self):
        a, b, c = bank()
        plan = {"A": {"acct7": -60_000}, "B": {"acct9": +60_000}}   # overdraft
        self.assertEqual(c.run("t1", plan), "ABORT")
        self.assertEqual(c.log, [])                # presumed abort: nothing logged
        self.assertEqual((a.data["acct7"], b.data["acct9"]), (50_000, 0))
        self.assertEqual((a.locks, b.locks), ({}, {}))

    def test_crash_before_decision_blocks_then_aborts(self):
        a, b, c = bank()
        c.crash_at = "after_votes"
        with self.assertRaises(Crash):
            c.run("t1", TRANSFER)
        self.assertEqual((a.in_doubt(), b.in_doubt()), (["t1"], ["t1"]))
        self.assertFalse(a.resolve(c))             # blocked while coordinator is down
        self.assertEqual(a.prepare("t2", {"acct7": -1}), "NO")   # row is locked
        c.recover()
        self.assertTrue(a.resolve(c) and b.resolve(c))
        self.assertEqual((a.data["acct7"], b.data["acct9"]), (50_000, 0))
        self.assertEqual((a.locks, b.locks), ({}, {}))

    def test_crash_after_decision_commits_on_recovery(self):
        a, b, c = bank()
        c.crash_at = "after_decision"
        with self.assertRaises(Crash):
            c.run("t1", TRANSFER)
        self.assertEqual(self.total(a, b), 50_000)
        self.assertEqual(a.data["acct7"], 50_000)  # nothing applied yet
        c.recover()                                # finds COMMIT without END
        self.assertEqual((a.data["acct7"], b.data["acct9"]), (40_000, 10_000))
        self.assertEqual(c.log[-1][0], "END")

    def test_crash_mid_phase2_is_completed(self):
        a, b, c = bank()
        c.crash_at = "mid_phase2"
        with self.assertRaises(Crash):
            c.run("t1", TRANSFER)
        self.assertEqual((a.data["acct7"], b.in_doubt()), (40_000, ["t1"]))
        self.assertFalse(b.resolve(c))             # still down
        c.recover()
        self.assertEqual(b.data["acct9"], 10_000)
        self.assertEqual(self.total(a, b), 50_000)  # money conserved

    def test_participant_crash_after_prepare_recovers_from_its_log(self):
        a, b, c = bank()
        c.crash_at = "after_decision"
        with self.assertRaises(Crash):
            c.run("t1", TRANSFER)
        b.crash()                                  # loses locks and pending writes
        b.recover()                                # rebuilds them from PREPARED
        self.assertEqual((b.in_doubt(), b.locks), (["t1"], {"acct9": "t1"}))
        c.recover()
        self.assertEqual(b.data["acct9"], 10_000)

    def test_unreachable_participant_means_abort(self):
        a, b, c = bank()
        b.crash()
        self.assertEqual(c.run("t1", TRANSFER), "ABORT")
        self.assertEqual((a.data["acct7"], a.locks), (50_000, {}))

    def test_duplicate_commit_is_idempotent(self):
        a, b, c = bank()
        c.run("t1", TRANSFER)
        a.finish("t1", "COMMIT")
        c.recover()
        self.assertEqual(a.data["acct7"], 40_000)


if __name__ == "__main__":
    unittest.main(verbosity=1)
