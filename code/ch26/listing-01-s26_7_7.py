# Extracted from manuscript/book1-traditional/26-consensus-and-coordination.md §26.7.7 (listing 1). Edit the manuscript, not this file.
"""A simplified, deterministic Raft simulator: leader election + log replication.

Time advances in 1 ms ticks. Messages take 2-8 ms. Nodes can crash and restart
(persistent state survives a crash; volatile state does not). Not production code:
no snapshots, no membership changes, no client sessions.
"""
import random

HEARTBEAT_MS = 50
ELECTION_MIN_MS, ELECTION_MAX_MS = 150, 300


class Node:
    def __init__(self, nid, peers, rng):
        self.id, self.peers, self.rng = nid, peers, rng
        # Persistent state (survives crashes)
        self.term, self.voted_for, self.log = 0, None, []   # log entries: (term, command)
        self.up = True
        self.reset_volatile(now=0)

    def reset_volatile(self, now):
        self.role, self.commit, self.votes = "follower", 0, set()
        self.next_idx, self.match_idx = {}, {}
        self.reset_election_timer(now)

    def reset_election_timer(self, now):
        self.deadline = now + self.rng.randint(ELECTION_MIN_MS, ELECTION_MAX_MS)

    def last_index(self):
        return len(self.log)

    def term_at(self, index):          # log indices are 1-based; index 0 has term 0
        return self.log[index - 1][0] if index > 0 else 0


class Cluster:
    def __init__(self, n=5, seed=7):
        self.rng = random.Random(seed)
        ids = list(range(1, n + 1))
        self.nodes = {i: Node(i, [p for p in ids if p != i], self.rng) for i in ids}
        self.inbox, self.now = [], 0                      # (deliver_at, dst, msg)

    def log_event(self, text):
        print(f"t={self.now:5d} ms  {text}")

    def send(self, src, dst, msg):
        msg["src"] = src
        self.inbox.append((self.now + self.rng.randint(2, 8), dst, msg))

    # ---------------- message handlers ----------------
    def step_down_if_stale(self, n, term):
        if term > n.term:
            n.term, n.voted_for, n.role = term, None, "follower"

    def handle(self, n, m):
        self.step_down_if_stale(n, m["term"])
        kind = m["type"]
        if kind == "RequestVote":
            up_to_date = (m["last_term"], m["last_index"]) >= (n.term_at(n.last_index()), n.last_index())
            grant = (m["term"] == n.term and n.voted_for in (None, m["src"]) and up_to_date)
            if grant:
                n.voted_for = m["src"]
                n.reset_election_timer(self.now)
            self.send(n.id, m["src"], {"type": "Vote", "term": n.term, "granted": grant})
        elif kind == "Vote" and n.role == "candidate" and m["term"] == n.term and m["granted"]:
            n.votes.add(m["src"])
            if len(n.votes) > (len(n.peers) + 1) // 2:
                self.become_leader(n)
        elif kind == "AppendEntries":
            ok = False
            if m["term"] == n.term:
                n.role = "follower"
                n.reset_election_timer(self.now)
                prev = m["prev_index"]
                if prev <= n.last_index() and n.term_at(prev) == m["prev_term"]:
                    ok = True
                    for k, entry in enumerate(m["entries"]):       # log matching: fix conflicts
                        idx = prev + 1 + k
                        if idx <= n.last_index() and n.term_at(idx) != entry[0]:
                            del n.log[idx - 1:]
                        if idx > n.last_index():
                            n.log.append(entry)
                    n.commit = max(n.commit, min(m["commit"], prev + len(m["entries"])))
            self.send(n.id, m["src"], {"type": "AppendReply", "term": n.term, "ok": ok,
                                       "match": m["prev_index"] + len(m["entries"])})
        elif kind == "AppendReply" and n.role == "leader" and m["term"] == n.term:
            p = m["src"]
            if m["ok"]:
                n.match_idx[p] = max(n.match_idx[p], m["match"])
                n.next_idx[p] = n.match_idx[p] + 1
                self.advance_commit(n)
            else:
                n.next_idx[p] = max(1, n.next_idx[p] - 1)          # back up and retry

    # ---------------- leader logic ----------------
    def become_leader(self, n):
        n.role = "leader"
        n.next_idx = {p: n.last_index() + 1 for p in n.peers}
        n.match_idx = {p: 0 for p in n.peers}
        self.log_event(f"n{n.id} becomes LEADER for term {n.term} (votes from {sorted(n.votes)})")
        n.log.append((n.term, "no-op"))                            # commit something in our term
        n.hb_due = self.now

    def advance_commit(self, n):
        for idx in range(n.last_index(), n.commit, -1):
            replicas = 1 + sum(1 for p in n.peers if n.match_idx[p] >= idx)
            # Commit rule: majority AND entry from the current term (Raft paper, Figure 8)
            if replicas > (len(n.peers) + 1) // 2 and n.term_at(idx) == n.term:
                self.log_event(f"n{n.id} commits up to index {idx} (on {replicas} nodes)")
                n.commit = idx
                break

    def replicate(self, n):
        for p in n.peers:
            prev = n.next_idx[p] - 1
            self.send(n.id, p, {"type": "AppendEntries", "term": n.term, "prev_index": prev,
                                "prev_term": n.term_at(prev), "entries": n.log[prev:],
                                "commit": n.commit})

    def client_write(self, command):
        leader = next((n for n in self.nodes.values() if n.up and n.role == "leader"), None)
        if leader is None:
            self.log_event(f"client write {command!r} rejected: no leader")
            return
        leader.log.append((leader.term, command))
        self.log_event(f"client write {command!r} -> leader n{leader.id} at index {leader.last_index()}")

    # ---------------- main loop ----------------
    def tick(self):
        self.now += 1
        due = [x for x in self.inbox if x[0] <= self.now]
        self.inbox = [x for x in self.inbox if x[0] > self.now]
        for _, dst, msg in sorted(due, key=lambda x: (x[0], x[1])):
            if self.nodes[dst].up and self.nodes[msg["src"]].up:   # crashed nodes drop traffic
                self.handle(self.nodes[dst], msg)
        for n in self.nodes.values():
            if not n.up:
                continue
            if n.role == "leader" and self.now >= n.hb_due:
                self.replicate(n)
                n.hb_due = self.now + HEARTBEAT_MS
            elif n.role != "leader" and self.now >= n.deadline:
                n.role, n.term, n.voted_for, n.votes = "candidate", n.term + 1, n.id, {n.id}
                n.reset_election_timer(self.now)
                self.log_event(f"n{n.id} times out, starts election for term {n.term}")
                for p in n.peers:
                    self.send(n.id, p, {"type": "RequestVote", "term": n.term,
                                        "last_index": n.last_index(),
                                        "last_term": n.term_at(n.last_index())})

    def run_until(self, t):
        while self.now < t:
            self.tick()

    def crash(self, nid):
        self.nodes[nid].up = False
        self.log_event(f"n{nid} CRASHES")

    def restart(self, nid):
        n = self.nodes[nid]
        n.up = True
        n.reset_volatile(self.now)
        self.log_event(f"n{nid} restarts as follower (term {n.term}, log length {n.last_index()})")


def check_safety(cluster):
    """State machine safety: committed prefixes on all nodes must agree."""
    committed = [n.log[:n.commit] for n in cluster.nodes.values()]
    longest = max(committed, key=len)
    return all(c == longest[:len(c)] for c in committed)


def failover_experiment(runs=200):
    """Crash the leader in many seeded runs; measure failover time and check safety."""
    import contextlib, io
    times, violations = [], 0
    for seed in range(1, runs + 1):
        with contextlib.redirect_stdout(io.StringIO()):          # silence per-run events
            c = Cluster(n=5, seed=seed)
            c.run_until(400)
            for k in range(6):
                c.client_write(f"op{k}")
                c.run_until(c.now + 60)
            old = next(n for n in c.nodes.values() if n.role == "leader")
            crashed_at = c.now
            c.crash(old.id)
            while not any(n.up and n.role == "leader" for n in c.nodes.values()):
                c.tick()
            times.append(c.now - crashed_at)
            c.run_until(c.now + 300)
            c.restart(old.id)
            c.run_until(c.now + 400)
        violations += not check_safety(c)
    times.sort()
    print(f"{runs} seeded runs: safety violations={violations}, failover ms: "
          f"median={times[runs // 2]}, p95={times[int(runs * 0.95)]}, max={times[-1]}")


if __name__ == "__main__":
    c = Cluster(n=5, seed=7)
    c.run_until(400)
    for cmd in ["x=1", "y=2"]:
        c.client_write(cmd)
    c.run_until(500)
    old = next(n.id for n in c.nodes.values() if n.role == "leader")
    c.crash(old)
    c.run_until(900)
    c.client_write("x=3")
    c.run_until(1000)
    c.restart(old)
    c.run_until(1200)
    print()
    for n in c.nodes.values():
        print(f"n{n.id} {n.role:9s} term={n.term} commit={n.commit} "
              f"log={[f'{t}:{cmd}' for t, cmd in n.log]}")
    print("state machine safety holds:", check_safety(c))
    failover_experiment()
