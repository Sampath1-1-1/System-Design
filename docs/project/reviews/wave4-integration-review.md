# Wave 4 Integration Review — Chapters 24–29

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-10-30 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* the Part V chapters 24–29 (Distributed Systems) and their interfaces with chapters 1–23.

**Method.** This was targeted grep and reading, not a full read-through.

1. **Ownership.** A scratch script split every Part V chapter at its `##`–`####` headings and counted words and keyword hits for each block. The topics were clocks, consistency models and CAP, quorums, leases and fencing, R + W > N and the topics around it, version vectors, 2PC/Spanner, FLP, Merkle trees, consistent hashing, idempotency and Spark/Flink. Every block that is not the owner's and has three or more hits was then read against the ownership list in the brief and 04 §4.5. That list is: clocks → Ch 24; consistency models, CAP, PACELC and session guarantees → Ch 25; quorums, consensus, leases, fencing and split brain → Ch 26; R + W > N, sloppy quorums, failure detection, anti-entropy, CRDTs and siblings → Ch 27; 2PC, 3PC, Percolator and Spanner → Ch 28; FLP → Ch 24; Merkle trees → §17.8; consistent hashing → §14.8; idempotency → §22.15; sagas → §32.7; Spark → Ch 29.
2. **Recurring facts.** Facts that appear in more than one chapter were extracted and compared:
   - CockroachDB maximum offset
   - TrueTime ε and commit wait
   - NTP accuracy
   - the GitHub 2018 incident
   - Raft election timing against the failover budgets
   - the three quorum-latency formulas
   - the Jepsen findings
   - KRaft and ZooKeeper statements
   - Dynamo details (Ch 12, 14, 24, 25, 27)
3. **Cross-references.** All 337 `§N.M[.K]` references in Ch 24–29 (229 cross-chapter, 108 intra-chapter) and all 76 forward references from Ch 1–23 into Ch 24–29 were resolved by script. Targets in Ch 1–29 were checked against the actual headings, and targets in Ch 30+ against `01-master-toc.md`. Each reference was then read for topic fit. The same was done for chapter-level "Chapter N"/"Ch N" references in both directions and for cross-chapter Figure/Table references (Figure 11.8, Figure 14.3), and for every intra-chapter Figure/Table number.
4. **Numbers.** About 90 numbers in about 40 worked examples were recomputed with `python3`. All 18 runnable Python listings in `code/ch24`–`code/ch29` were re-run and their output was compared line by line with the chapters (see the list at the end).
5. **Concepts.** The five statements most often gotten wrong were checked: CAP "C" means linearizability; R + W > N alone does not give linearizability; Raft commits only current-term entries by counting replicas; 3PC is unsafe under partitions; snapshot isolation allows write skew.
6. **Terminology.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 29 chapters.
- `python3 build/build.py --chapters 24-29 --name qa --formats html`: 349 diagrams across 29 chapters, 0 errors.
- `dist/qa.*` was deleted afterwards, and `manuscript/appendices` was restored with `git checkout`.
- The build left no changes in `diagrams/` or `code/`. The only modified files are chapters 14 and 24–29.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 25 vs 28 | §25.10.3 "External consistency in Spanner" | S2 | **Contradiction.** Ch 25 says the commit cost is "a wait proportional to clock uncertainty (single-digit milliseconds) **plus** Paxos round trips". Ch 28 §28.8.2 (the owner) says commit wait runs *in parallel* with the Paxos write of the commit record: $T_{\text{commit}} \approx \max(T_{\text{Paxos}}, 2\bar\varepsilon)$. With the paper's ε sawtooth of 1–7 ms (mean about 4 ms), the wait is about 8 ms. Ch 24 §24.9.2 (1–7 ms, 200 ppm, 30 s polls) and Ch 28 §28.8.1 (200 µs/s, mean about 4 ms) agree with each other. | Now reads "a commit wait of about twice the clock uncertainty (about 8 ms at the paper's typical uncertainty of 4 ms), which overlaps the Paxos round trip that logs the commit, so a commit takes roughly the larger of the two", pointing to §28.8.2. The matching open-verification item in §25.18 was updated. |
| 2 | 25 | §25.7.2 PBS formula callout | S2 | **Internal inconsistency.** The formula was labeled $P(\text{more than } k \text{ versions stale}) = p_s^k$, and the variable table defined $k$ as "versions the read is allowed to miss". Item 5 of the worked example uses $k = 3$ to mean "may miss the last two but not three", which is $p_s^k$ under Bailis et al.'s definition (fresh if within the $k$ most recent versions). Under the table's definition, the exponent would have to be $k + 1$. | The label is now $P(\text{older than all } k \text{ most recent versions})$, and $k$ is "Number of most recent versions, any one of which counts as fresh enough (the read may miss $k-1$ of them)". The numbers (2/3, 1/3, 0, 0.3, 8/27 ≈ 0.30) are unchanged and were recomputed. |
| 3 | 26 | §26.11.1 lease worked example, step 4 | S2 | "Renew at about $T/3$ to $T/2$ (3.3–5 s), so two consecutive renewals can fail before the lease lapses." This holds for $T/3$ (renewals at 3.3 and 6.7 s can fail before the holder stops at 9.5 s) but not for $T/2$, where only the 5 s renewal can fail. | Now reads "renew about every $T/3$ (3.3 s), so two consecutive renewals can fail before the lease lapses at 9.5 s; renewing every $T/2$ (5 s) tolerates only one." Steps 1–3 were recomputed: holder 9.499 s, grantor 10.001 s, worst-case real-time end of the holder's action 9.99995 s, which is before the grantor's 10.0 s. |
| 4 | 25 | §25.3.3, "Reading the diagram" after Figure 25.2 | S2 | Points to §25.3.5, which does not exist. The leaderless new–old inversion and its fix (ABD write-back) are in §25.3.4. | Changed to §25.3.4. |
| 5 | 28 (and 14) | §28.4.3 variable table for $N_{\text{doubt}}$; Ch 14 §14.2 prerequisites | S2 | "Little's Law, §4.10". §4.10 is Queueing theory, and Little's Law is §4.11. Ch 14's prerequisite line had the same slip. | Both changed to §4.11. Ch 18/19/22/23 cite §4.10 for queueing and utilization, which is correct. |
| 6 | 29 | §29.2 prerequisites | S2 | "Clocks and logical time — §24.9–§24.10 (event time; Chandy–Lamport snapshots)". Ch 24 never mentions Chandy–Lamport. The algorithm appears only in §29.9.2. | Now reads "(event time; the happens-before reasoning behind the Chandy–Lamport snapshots of §29.9.2)". |
| 7 | 28 vs 24 | §28.8.2 commit-wait example, implication | S3 | "Commodity NTP with tens to hundreds of milliseconds of worst-case error (§24.9)" does not match §24.9.3 and Table 24.8. They give milliseconds over the Internet and sub-millisecond to a few ms in a datacenter, with *no guaranteed bound* (occasionally seconds). | Now reads "Commodity NTP is usually accurate to milliseconds but gives no guaranteed bound (§24.9), so a safe configured bound must be hundreds of milliseconds (CockroachDB's default maximum offset is 500 ms, §28.10.1), which would make commit wait unacceptable". The 500 ms default is stated the same way in §24.12.4, §24.17 Q6 and §28.10.1, with matching open items. |
| 8 | 24 vs 27 | §24.11.2–§24.11.5 (version vectors, sibling code and dotted version vectors, about 1,070 words with the listing) vs §27.14.2 (owner of siblings, 602 words) | S3 | **Overlap.** Both chapters walk through a shopping-cart sibling example. Both mention Dynamo's truncation at about 10 entries and Riak 2.0's dotted version vectors, and neither linked to the other. The Ch 24 material is mechanism-level and partly unique: a runnable `VersionedStore`, the same-replica lost-update flaw and DVVs, none of which Ch 27 has. Condensing it would delete unique content and change the `code/ch24` listing. | The overlap is kept, and the two sections are now linked both ways. §24.11.2 now says it introduces the mechanism only and points to §27.14.2 for store-level use (Dynamo cart, Riak contexts, merge functions). §27.14.2 cites §24.11.2, the §24.11.3 example and §24.11.5. The Riak callout cites §24.11.5 and adds "and lost updates". |
| 9 | 27 vs 26 | §27.11.1 failover worked example | S3 | The failover budget (6 s detection, 1 s election, 3 s reconfiguration, 30 s DNS → 40 s) is a primary–backup example and is correct. It did not connect to Raft's measured detection-plus-election time in §26.7.2 (156.5 ms in one datacenter, 1,221 ms across regions), so a reader could take 7 s as the norm for consensus systems. | One sentence added to the interpretation: consensus-replicated systems shrink detection and election to about 0.16–1.2 s (§26.7.2), which leaves redirection even more dominant. |
| 10 | 14 vs 27 | §14.8.5 "Replication on the ring" | S3 | **Notation clash.** It writes "the first $R$ distinct physical nodes" for the replication factor, but §27.8 (cited in the same paragraph) uses $N$ for the replication factor and $R$ for the read quorum. Ch 14 cannot use $N$ because it already means the node count there. | Added "($R$ here is the replication factor, which §27.8 calls $N$ because there $R$ is the read quorum)". |
| 11 | 25, 26, 27 | §25.3.4 quorum latency, §26.4.2 commit latency, §27.8.3 k-th fastest | S3 | Three formulas for quorum latency. They are consistent: $\text{RTT}_{(q)}$ counting the coordinator at 0 is the same as $\text{RTT}_{(q-1)}$ over followers, and both are special cases of the order statistic $T_{(k)}$. None of them mentioned the others. | Ch 25's interpretation now names the same order statistic in §26.4.2 and §27.8.3. All three examples were recomputed (66/131/13/25 ms; 13/26/71 ms and the 5.5× ratio; $2.98 \times 10^{-4}$, 0.0297, 0.67/1.67/3.67 ms). |
| 12 | 27 vs 24 | §27.14.1 LWW | S3 | The "Losing a later write to clock skew" example repeats the idea of §24.9.6, the danger window $x < \varepsilon$, with different numbers. It is about 200 words, under the threshold. | Added "§24.9.6 derives the danger window" to the existing §24.9 citation. Both examples were recomputed: Ch 27 5% at 10 writes/s with ε = 5 ms; Ch 24 window 150 ms. |
| 13 | 29 | §29.6.2 shuffle example, interpretation | S3 | "Tens of millions of 64 KB random reads". The example's own step 5 gives $78{,}125 \times 2{,}000 = 1.56 \times 10^8$ blocks. | Changed to "over a hundred million". The rest of the example checks out: NIC 45.3 s, uplinks 102.4 s, disk 100 s, so the ≈102 s claim holds; 64 KB per block. |
| 14 | 29 | §29.7 | S3 | Table formats (Iceberg, Delta, Hudi) were cited to "Chapters 61–62". The TOC puts lakehouses in Ch 61; Ch 62 is feature stores. The §29.10 citation of "Chapters 61–62" (streaming into tables that batch jobs and feature pipelines read) fits and was left. | Changed to "Chapter 61". |
| 15 | 27 | §27.5.2 chain-replication example | S3 | Style guide §5: the example mixed "4 KB" computed as 4,096 B (16,384 B per write) with decimal 1.25 GB/s. | Relabeled as 4 KiB and 16 KiB. The numbers (76,000 and 305,000 writes/s) are unchanged and correct. |
| 16 | 26 vs 27 | GitHub October 2018 incident callouts (§26.12, §27.11) and their reference URLs | S3 | The figures are consistent: 43 s loss of connectivity, about 24 h (Ch 26) and 24 h 11 min (Ch 27) degraded. The reference URLs differ: `github.blog/news-insights/company-news/oct21-post-incident-analysis/` vs `github.blog/2018-10-30-oct21-post-incident-analysis/`. Each callout is about 110 words, with a different lesson (controller consensus vs failover policy). | **Deferred.** Both chapters already list the figures and URL as open verification items, and github.blog was unreachable. Unify the URL once one is verified. |
| 17 | TOC vs 24–29 | `01-master-toc.md` Part V | S3 | Drafted titles are reworded or extended. Examples: 24.5 "The eight fallacies…", 24.8 adds "gray failures and timeouts", 27.14 adds "version vectors", 28.6 "Sagas: a preview", 29.11 "Batch versus stream; Spark versus Flink". | **Deferred** (TOC owner). Section numbers 24.3–29.11 match the TOC exactly, so no reference breaks. |
| 18 | 24–29 | Ownership measurement | — | Non-owner passages measured:<br>• **Consensus quorums:** §24.6.3 (2f+1/3f+1, 328 words) cites §26.4.<br>• **FLP:** §26.3.1 (215 words) opens "Section 24.13 introduced…".<br>• **Clocks and HLC:** §24.12.4 (316 words, CockroachDB uncertainty) and §28.10.1 item 5 agree (500 ms, restart in $(t, t+\varepsilon_{\max}]$, self-shutdown). §28.8 cites §24.9; §24.9.7 (462 words) only previews TrueTime and cites §28.8.<br>• **Sagas:** §28.6 is 311 words and cites §32.7–§32.8 and §32.5.<br>• **Spanner previews:** §25.10.3 is 238 words.<br>• **Merkle trees:** §27.13 cites §17.8 twice, and its "about 80 hashes" matches §17.8's $1 + 2kh = 81$.<br>• **Consistent hashing:** §27.7 cites §14.8.<br>• **Idempotency:** 14 uses across Ch 24–29, all citing §22.15.<br>• **Spark/Flink:** appear only in Ch 29.<br>• **CAP/PACELC:** outside Ch 25, only §24.7.3 (one sentence citing §25.8–§25.9) and §28.8.5 (Spanner and CAP, citing §25.8).<br>• **Session guarantees:** Ch 14 §14.4.3–§14.4.4 keeps its applied lag treatment and cites §25.6; §25.6.2 cites §14.4.4. | No action beyond #8. No non-owner passage over about 400 words duplicates owner content. |
| 19 | 24–29 vs 1–23 | Recurring facts | — | All consistent:<br>• **CockroachDB max offset:** 500 ms in Ch 24 and 28.<br>• **NTP:** Ch 7 gives no accuracy figure (it mentions NTP only for UDP amplification); Ch 17 §17.10 agrees with Ch 24 ("slew rather than step").<br>• **Jepsen:** findings appear only in §25.11.3 (etcd 3.4.3, MongoDB 4.2.6, PostgreSQL 12.3); Ch 26 cites §25.11 once.<br>• **KRaft:** Ch 26 says three times that it is Raft-based and that Kafka 4.0 (2025) removed ZooKeeper mode, with no conflicting statement elsewhere.<br>• **Dynamo:** Ch 12 §12.2, §12.6, Ch 14 §14.8.5, Ch 24 §24.11.4 and Ch 27 §27.7–§27.14 agree on the shopping cart, vector clocks truncated at about 10 entries, union merge resurrecting deletes, sloppy quorums with hinted handoff, Merkle anti-entropy and N = 3 with R = W = 2.<br>• **Failover arithmetic:** 52.6 min a year and 4.32 min a month at 99.99%, matching Ch 4 §4.14 (4 min 19 s).<br>• **Spanner:** 200 ppm and 30 s polls in Ch 24 and Ch 28. | No action. |
| 20 | 24–29 | Conceptual statements | — | All five are stated correctly:<br>• CAP "C" is atomic/linearizable (§25.8.1, plus misreadings in §25.8.2).<br>• R + W > N is not linearizable (§25.3 mistake, §27.8.2 five reasons, Figure 27.7, the Cassandra mistake callout).<br>• Raft commits only current-term entries by counting (§26.7.5; Figure 26.10 matches Figure 8 of the Raft paper).<br>• 3PC is unsafe under partitions (§28.5.2, Figure 28.8, Table 28.4).<br>• SI permits write skew (§28.3.3, reproduced in §28.7.4; TiDB defaults to SI). | No action. |
| 21 | 24–29 | Terminology and spelling | — | No British spellings. No QPS, "box" (node sense), "uptime" or "message bus". "Master" appears only as a proper or protocol name: GFS, Bigtable and Chubby masters, Spanner time masters, the chain-replication master service of van Renesse and Schneider, Google MapReduce's "master" introduced as "coordinator", and Spark's `.master(...)` API. "Expiry" appears only for leases and locks, not as a synonym for TTL. | No action (same treatment as wave 3 #11). |

**Counts:** S1 = 0 · S2 = 6 (all fixed) · S3 = 11 (9 fixed, 2 deferred) · 4 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. Ch 24 §24.4: $A_3 = 1 - 10^{-9}$; $0.999^{1000} = 0.368$, so $P_{\text{any}} = 0.632$; 0.999 ≈ 8.8 h/yr.
2. Ch 24 §24.9.2 drift: 50 ppm → 4.32 s/day; 100 µs/s pairwise; $T_{\text{sync}} = 10$ s for 1 ms; Spanner $200 \times 10^{-6} \times 30 = 6$ ms sawtooth.
3. Ch 24 §24.9.3 NTP: $\delta = 60$ ms, $\theta = 90$ ms, asymmetric true offset 70 ms (error 20 ms ≤ 30 ms). Checkpoint Q9: $\delta = 20$, $\theta = 40$, ±10 ms. §24.9.5 smear 11.6 ppm.
4. Ch 24 §24.8.3 timeout 224 → 250 ms; §24.14 fleet corruption $1 - e^{-0.1} = 0.095$.
5. Ch 24 §24.11.4 vector-clock size: 48 B per key → 48 GB for $10^9$ keys; 160 KB for 10,000 client entries; 16 KB for 1,000 processes.
6. Ch 24 §24.6.3: $2f+1 = 3$ / 5; $3f+1 = 4$ with 3-vote quorums.
7. Ch 25 §25.3.4 quorum latency: $q = 3$, $\text{RTT}_{(3)} = 65$ → 66 / 131 ms; relocated 13 / 25 ms; lower bound 10 < 35 ms.
8. Ch 25 §25.7.2 PBS closed form: 2/3, 1/3, 0, 3/10, $(2/3)^3 = 0.296$. §25.9.2 RCU: 20,000 / 40,000 / 21,000 (+5%).
9. Ch 26 §26.4.1 quorum sizes for $N = 3, 4, 5, 7$; cluster availability 0.999702 / 0.999408 / 0.9999901 / 0.99999966 (157 min, 5.2 min, 11 s per year); Table 26.1 unavailabilities.
10. Ch 26 §26.4.2 commit latency 13 / 26 / 71 ms (5.5×); §26.4.3 flexible quorums $3 + 5 > 7$.
11. Ch 26 §26.7.2 Raft failover 156.5 ms and 1,221 ms; collision probability 0.241 / 0.039 / 0.052.
12. Ch 26 §26.11.1 lease: 9.499 s / 10.001 s; non-overlap verified (see #3).
13. Ch 27 §27.4 async loss 100 / 1,000 writes; §27.5 chain 1.15 / 1.75 / 1.1 ms, 76,294 / 305,176 writes/s, CRAQ 150,000 reads/s.
14. Ch 27 §27.6 conflicts 0.004/s (14.4/h); $4 \times 10^{-7}$/s per key → 0.4/s → 34,560/day.
15. Ch 27 §27.8 overlap table (the listing brute-forces all 9 $(R, W)$ pairs); k-th fastest $10^{-6}$ / $2.98 \times 10^{-4}$ / 0.0297; exponential means 0.667 / 1.667 / 3.667 ms.
16. Ch 27 §27.9 hints: 15,000 writes/s per node, 54 GB, 4.9 GB per survivor, 540 s replay.
17. Ch 27 §27.10.2 phi: $z = 2/4/5/6$ → 1.64 / 4.50 / 6.54 / 9.01; threshold 8 at $z = 5.612$ → 1,561 ms ($\sigma = 100$) and 3,245 ms ($\sigma = 400$).
18. Ch 27 §27.10.3 gossip: 16.9 rounds ($f = 1$), 7.3 ($f = 3$), +5.6 per 10× nodes; SWIM $(1 - 1/999)^{999} = 0.3677$ → 1.58 s, $e/(e-1) = 1.582$; 999,000 vs 2,000 messages/s.
19. Ch 27 §27.11 failover 40 / 11 s; 240 / 66 s per year = 7.6% / 2.1% of 3,156 s; 15% of the 4.32 min monthly budget.
20. Ch 27 §27.12 recovery: 8,000 + 13,333 s (5.9 h); 1,600 + 2,667 s (71 min); $(21{,}333/4{,}267)^2 = 25$.
21. Ch 27 §27.13 Merkle: $1 + 2 \cdot 2 \cdot 20 = 81$ ≈ 80 hashes, matching §17.8's formula.
22. Ch 27 §27.14.1 LWW 5%; §27.14.2 Dynamo D1–D5 vectors and dominance.
23. Ch 28 §28.4.3 in-doubt: $\lambda = 3.86 \times 10^{-7}$/s, $P = 5.8 \times 10^{-10}$ (1 in 1.7 billion), $N_{\text{doubt}} = 3$, 30,000 queued transfers.
24. Ch 28 §28.4.4 2PC: 3 ms / 2.5 ms hold in one datacenter; 142 / 72 ms across regions; 400/s vs 14/s hot row. $A^k$: $0.999^{10} = 0.990045$ (430 min/month); $0.99999^{10}$ → 4.3 min/month.
25. Ch 28 §28.5 3PC 3.5 ms vs 3 ms; §28.7.3 Percolator 6 / 3 / 125 ms.
26. Ch 28 §28.8.2 commit wait $2\bar\varepsilon = 8$ ms; max(2, 8) = 8 and max(50, 8) = 50 ms; ε = 100 ms → 200 ms, 5 commits/s. External-consistency proof chain checked against [Corbett et al. 2012].
27. Ch 28 §28.9 Calvin 77 / 9 ms vs 2PC ≈ 140 / ≈ 5 ms; §28.10.1 parallel commits 80 → 40 ms.
28. Ch 29 §29.3 scan 20,000 s / 200 s / 20 s; §29.4.2 job model: $M = 7{,}813$, 10 waves (last 613 tasks, 77% full), 128 + 6 + 37.5 + 20 ≈ 192 s; combiner 2 TB → 18.75 GB (≈105×).
29. Ch 29 §29.4.3 stragglers: $1 - e^{-7.8} = 0.9996$; last wave $1 - e^{-0.613} = 0.46$; +51 s (+27%).
30. Ch 29 §29.4.4 joins: 1.985 TB vs 495 GB (4×); 4.95 vs 2.03 TB; break-even 20 GB. §29.5.3 caching 660 / 120 s, 5.5× (limit 11×).
31. Ch 29 §29.6.2 shuffle: NIC 45.3 s, uplinks 102.4 s, disk 100 s → **≈102 s confirmed**; 78,125 × 2,000 = $1.56 \times 10^8$ blocks of 64 KB.
32. Ch 29 §29.6.3 skew: 40.8 (1,224 s), 5.8 (174 s), 1.43 theoretical with $s = 64$; formula $fP + (1 - f)$ re-derived.
33. Ch 29 §29.7 locality 500 / 4,000 s (8×), 17 / 33 s (2×).
34. Ch 29 §29.8.3 late events: formula re-derived by integrating $e^{-(\delta+u)/\mu}$ over $u \in [0, W)$; 3.33% / 0.27% / 0.022%.
35. Ch 29 §29.9.2 Young: $\sqrt{345{,}600} = 588$ s; catch-up 240 s (stale 300 s), 60 s (stale 120 s); overhead 0.33% → 3.3%.
36. Listings: all 18 Python listings in `code/ch24`–`code/ch29` were run. 17 ran (exit 0), and every output line appears verbatim in the chapters, with three expected exceptions:
    - §27.8.3 prints six off-diagonal overlap rows, which the chapter deliberately abridges.
    - §28.4.7 prints a `unittest` timing line, which is nondeterministic.
    - §29.5.4 needs `pyspark`, which is not installed in the review environment, so it was not run.

    Every Monte Carlo figure quoted in prose was checked against these outputs:
    - Raft median failover of 155 ms
    - PBS 0.9600 / 0.9792 / 0.9989
    - phi 6.36 at 1,500 ms and a crossing at 1,571 ms
    - gossip 17.99 / 13.66 / 9.13 rounds
    - SWIM 1.597 periods
37. Cross-references:
    - **Ch 24–29:** all 337 `§` references in Ch 24–29 resolve to sections on the stated topic, apart from #4–#6.
    - **Inbound:** all 76 inbound references from Ch 1–23 also resolve on topic. Examples are §24.5 fallacies from Ch 2 and 8; §24.9 clocks from Ch 12, 14, 17 and 22; §26.8–§26.13 from Ch 3, 6, 14, 15, 17, 19, 20 and 22; §27.7–§27.14 from Ch 3, 4, 12, 14 and 17; §28.4/§28.8/§28.10 from Ch 12; §29.4/§29.7/§29.8 from Ch 3, 5 and 17.
    - **Chapter-level and Ch 30+:** chapter-level references into Ch 30+ match the TOC topics: Ch 31 Kafka/KRaft, Ch 32 sagas, outbox and exactly-once (§32.5, §32.7–§32.9), §31.11 Kafka transactions, Ch 34 microservices, Ch 44 multi-region, Ch 45 BFT, Ch 61 lakehouses and Beam, Ch 62 streaming features.
    - **Figures and tables:** cross-chapter Figure 11.8 (write skew) and Figure 14.3 (lag anomalies) match their captions, and every intra-chapter Figure/Table number in Ch 24–29 has a caption.

## Remaining risks

- **Clock and product constants are the most perishable facts in Part V.** They include:
  - CockroachDB's 500 ms maximum offset and 512 MiB range size
  - Cassandra's 3 h hint window, `phi_convict_threshold` 8 and 10-day `gc_grace_seconds`
  - etcd's 100 ms / 1,000 ms defaults
  - Chubby's 12 s session lease
  - DynamoDB MRSC (June 2025)
  - Kafka 4.0
  - S3 per-prefix rates
  - Spark's 10 MB broadcast threshold
  - Riak 2.0 DVVs

  All carry "as of" tags or open verification items, but none was re-verified against primary sources in this review.
- **Unverified primary figures that Part V leans on**: Dynamo's 99.94% single-version figure and the 10-entry truncation threshold, the GitHub 2018 timings and URL (#16), Brewer 2017's network-incident share, and the Attiya–Welch bound attribution. All are listed in the chapters' open items, and github.blog and jepsen.io were unreachable from the drafting sessions.
- **Version-vector material is split across two chapters (#8).** Ch 24 holds the mechanism and code, and Ch 27 holds the store-level use. They are now linked, but a future edit to either (for example, adding DVV code to Ch 27) would re-create the duplication. Chapter 45 (CRDT theory and the consistency hierarchy) should cite §24.11, §25.7.5 and §27.14 rather than re-derive them.
- **Reference drift.** About 410 references were checked by a scratch script, again. `qa_check.py` still has no §-reference resolver. Part V adds many inbound links: 76 from Ch 1–23, plus Ch 24–29 references into §31–§34, §44–§45 and §61–§62 that depend on TOC numbering not yet drafted.
