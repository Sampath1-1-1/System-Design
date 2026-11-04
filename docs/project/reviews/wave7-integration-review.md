# Wave 7 Integration Review — Chapters 44–51

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-04 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* Part IX, chapters 44–51 (multi-region, advanced consistency and BFT, distributed scheduling, multi-tenancy, edge and serverless, large-scale data and HPC, security architecture and privacy, cost and sustainability), and their interfaces with chapters 1–43.

**Method.** This was targeted grep and reading, not a full read-through. It follows the wave 6 method.

1. **Ownership.** A scratch script split every chapter 44–51 at its `##`–`####` headings and counted words and keyword hits per block for these topics:
   - consistency models (linearizability, sequential, causal, session guarantees)
   - isolation (SI, write skew, serializability, phantoms)
   - CRDTs and LWW; Spanner/TrueTime
   - cells and shuffle sharding; DR tiers, RTO and RPO
   - Kubernetes scheduling (filter/score, taints, affinity, preemption)
   - Firecracker, gVisor and microVMs; Lambda, serverless and break-even
   - Colossus, Tectonic, GFS/HDFS, erasure coding, S3; MPI and all-reduce
   - TLS/mTLS, KMS, threat modeling; OAuth/OIDC, JWT, Zanzibar
   - data residency and GDPR; commitments, spot and rightsizing; showback and chargeback

   Every non-owner block with four or more hits was read against the brief's ownership list and 04 §4.5:
   - consistency-model basics → Ch 25; isolation basics → §11.13 (Ch 45 deeper)
   - CRDT practice → §27.14 (Ch 45 theory; Ch 44 cross-references)
   - Spanner/TrueTime → Ch 28; DR tiers → Ch 39; cells and shuffle sharding → §33.12
   - Kubernetes scheduling basics → §42.13 (Ch 46 deeper)
   - Firecracker/gVisor isolation → §47.9 (Ch 41, 42, 48 cross-reference)
   - serverless basics and break-even → §33.9 (§48.11 and Ch 51 cross-reference)
   - storage → Ch 15 (Ch 49 exabyte material only); MPI/all-reduce → Ch 49
   - security fundamentals → Ch 10; OAuth/Zanzibar → Ch 8; data residency → §44.9
   - cost basics → §41.13; per-tenant cost → §47.11
2. **Recurring facts.** Facts that appear in more than one chapter were extracted and compared:
   - Firecracker figures (Ch 33, 41, 42, 47, 48)
   - Lambda limits and prices (Ch 33, 41, 48, 51)
   - inter-region RTTs (Ch 7, 24, 44)
   - fairness: water-filling and DRF (Ch 46, 47)
   - Borg (Ch 41, 42, 46)
   - Prime Video (Ch 33, 34, 48, 51)
   - PUE and energy (Ch 51 only)
   - differential privacy (Ch 50 only; Ch 71 not yet drafted)
   - QuickBite (Ch 2, 18, 39, 44, 46, 50, 51) and PhotoShare (Ch 1, 48)
   - S3, Colossus, Tectonic and Azure Storage scale (Ch 15, 49)
3. **Cross-references.** All 609 `§N.M[.K]` references in Ch 44–51 were resolved by script against the actual headings: 251 intra-chapter, 358 cross-chapter, none unresolved. Every cross-chapter target was read for topic fit (contexts read where the fit was not obvious). The 32 chapter-level references from Ch 44–51 to Ch 52+ were checked against `01-master-toc.md`; there are no `§` references to Ch 52+. Inbound: Ch 1–43 contain no `§` references into Ch 44–51 and 46 chapter-level references, all read for fit. Every Figure and Table number cited in Ch 44–51 has a matching caption (including the four cross-chapter citations: Figure 25.10, Figure 11.8, Table 11.9, Table 10.13), and the captions in each chapter run in sequence.
4. **Numbers.** About 230 numbers in 60 worked examples and the eight checkpoint blocks were recomputed with `python3` (list below). All 17 Python listings in Ch 44–51 were extracted and run with Python 3.13. Their output was compared with the chapters' `text` output blocks.
5. **Concepts.** These statements were checked:
   - SI permits write skew (G2-item, two rw edges) and forbids G-single
   - SI and PL-2.99 are incomparable
   - SSI detects dangerous structures (two consecutive rw edges), including the commit-ordering and read-only refinements
   - BFT needs $n \ge 3f + 1$ under partial synchrony, even with signatures
   - DRF's four properties (sharing incentive, strategy-proofness, envy-freeness, Pareto efficiency)
   - ε-DP basic composition is additive; parallel composition takes the maximum
   - k-anonymity bounds row re-identification, not attribute disclosure
   - the commitment optimum is the $d$-quantile of hourly usage
6. **Terminology.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 51 chapters.
- `python3 build/build.py --chapters 44-51 --name qa --formats html`: 669 diagrams across 51 chapters, 0 errors. The rendered HTML was checked for stray inline maths from unescaped `$`. None of the 1,975 TeX annotations contains prose, and "\$74.6 million" and "\$22 million" render as text.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored with `git checkout`.
- The only modified files are chapters 01, 44, 46, 47 and 51.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 46 → 26 | §46.5.2 Figure 46.5 "Reading the diagram" | S3 | "Election uses Paxos and a Chubby lock (§26.8)". §26.8 is ZooKeeper and ZAB. Chubby is defined in §26.14.1. | Changed to (§26.14.1). |
| 2 | 47 vs 46 | §47.8.2 formula "Weighted max–min fair share (water-filling)"; DRF sentence after the example | S3 | **Duplicated formula.** The water-filling formula and its variable table are repeated almost verbatim from §46.9.1 (about 150 words). The tenant example is new, and fairness theory belongs to Ch 46. The DRF pointer said only "Chapter 46 covers it". | Formula title now reads "(water-filling, as in §46.9.1)". The DRF pointer now reads "§46.9.3 covers it". The example is kept, because it is unique tenant content. |
| 3 | 46 → 49 | §46.10.1 opening paragraph | S3 | "runs collectives (all-reduce, Chapter 65)". Ch 49 §49.9.2 now owns all-reduce and its cost models, and Ch 65 will build on it. | Now reads "(all-reduce, §49.9.2 and Chapter 65)". |
| 4 | 51 | §51.8 forecast listing, output block | S3 | The program ends with `print("all tests passed")`, but the printed output omits that line. Every other line matches. | Line added. Re-run: output matches verbatim. |
| 5 | 51 | §51.11.2 "Shifting QuickBite's nightly analytics job", steps 2–3 | S3 | "$\Delta C = 40$ kg per run (44%); 18.3 t a year" reads as an annual saving. 18.3 t is the *new* annual total ($50 \times 365$); the saving is 14.6 t. Step 3's "7.8 t a year" has the same ambiguity. | Both now end "… t a year instead of 32.9 t". The numbers are unchanged. |
| 6 | 44, 47, 51 | §44.6.4 Figure 44.9 reading; §47.5.1, §47.11.1 (×2), §47.20; §51.3.3 Figure 51.2 reading | S3 | **Spelling.** British forms "travelling", "labelled" (×4) and "travelled". Ch 1–43 use "labeled" (31×) and "traveled". | Changed to "traveling", "labeled" and "traveled". |
| 7 | 1 → 44 | Table 1.8, Compliance row | S3 | The example "EU users' data stored in the EU" points only to Ch 50. Data residency is owned by §44.9; Ch 50 cross-references it (§50.2, §50.9.3). | Now "Ch 44, Ch 50". |
| 8 | 47 | §47.8.4 noisy-tenant simulation, output block | S3 | The program's first `print(f"\n{policy}")` emits a leading blank line, and the printed output starts at "fifo". This is cosmetic only; all values match. | **Deferred.** No action: changing either side adds noise for no reader benefit. |
| 9 | 46 vs 1–43 | §46.4.4 (×2), §46.15 Q6 | S3 | "cancelled" (British) appears here, but Ch 1–43 already mix "canceled" (4×) and "cancelled" (6×). `terminology.md` does not rule on it. | **Deferred** to the terminology owner: choose one form book-wide. |
| 10 | 44–51 | Perishable product facts | S3 | These facts carry "as of 2026" tags or open verification items, but none was re-verified against primary sources here:<br>• Lambda account concurrency 1,000 and scaling 1,000 per 10 s; provisioned price \$0.0000041667/GB-s; 1,769 MB per vCPU<br>• DynamoDB MRSC (three Regions, GA 2025); Spanner base configurations; CockroachDB survival goals<br>• SPIRE 1 h default SVID TTL; Slurm `bf_window` 1,440 min and `bf_interval` 30 s<br>• Cloud Run 80/1,000 concurrency; Mandiant 2025 median dwell time of 11 days<br>• El Capitan Rmax/Rpeak; Census 2020 ε = 19.61<br>• Google 1.09 PUE (2024); Uptime 1.56–1.58 | **Deferred.** Already open items in §44.19, §46.20, §48.20, §49.20, §50.20 and §51.20. |
| 11 | 44–51 | Ownership measurement | — | Non-owner passages measured:<br>• **Ch 44 (residency owner):**<br>  – **CRDT/LWW:** §44.8.2 (441 words) cites §27.14.1–§27.14.3 for each strategy and adds only the cross-region conflict-rate model and Figure 44.11.<br>  – **Spanner:** one Table 44.7 row and one bullet citing §28.8.<br>  – **Cells:** §44.10.1 (408 words) opens "Cells (§33.12) bound the blast radius …" and covers only regional independence and static stability.<br>  – **DR:** §44.6.1 defers tiers to §39.8.<br>• **Ch 45:**<br>  – **Consistency:** §45.3 cites Figure 25.10 and adds Adya's portable levels and HAT classes, which appear nowhere else.<br>  – **Isolation:** §45.4 cites Figure 11.8 and §11.13 and formalizes them (DSG, dangerous-structure theorem, PostgreSQL SSI internals).<br>  – **CRDTs:** §45.6 opens "§27.14.3 built CRDTs …" and gives only theory (semilattices, convergence proof, CALM).<br>• **Ch 46:** §46.6 opens "§42.13 introduced filtering, scoring and binding" and adds framework extension points, `percentageOfNodesToScore`, profiles and the descheduler.<br>• **Ch 47:** §47.4.3 (682 words) cites §33.12 and adds revenue-weighted blast radius. Shuffle sharding appears in one sentence citing §33.12.2. §47.9 owns the isolation spectrum.<br>• **Ch 48:**<br>  – §48.3.2 (273 words) states the billing model.<br>  – §48.11 (846 words) opens "§33.9.3 derived the break-even …" and adds front-door, provisioning-factor and egress terms.<br>  – Firecracker appears in one industry callout citing §47.9.<br>• **Ch 49:** §49.4 says "§15.5.3 introduced Colossus and Tectonic, and §15.4 the S3-style object store". The Colossus callout (180 words) repeats §15.5.3's component list but adds the 2025 flash/HDD placement and the >10 EB figures.<br>• **Ch 50:** identity (§50.5) cites §8.12.2, §8.13.4, §8.14.3 and §8.14.6 and adds brokered federation, token-lifetime load and policy engines. Residency is cited to §44.9 three times. Controls cite §10.9 and §10.10.<br>• **Ch 51:**<br>  – §51.6.1 cites §41.13.1 for $u^* = 1 - d$ and adds the portfolio quantile rule.<br>  – §51.5.2 (164 words) cites §47.11.2 for allocation.<br>  – The serverless curve is cited to §33.9.3 and §48.11. | No action beyond #2. No non-owner passage over about 400 words duplicates owner content. |
| 12 | 33, 41, 42, 47, 48 | Firecracker | — | Every chapter that gives numbers agrees with Agache et al. 2020: ~125 ms boot, < 5 MiB VMM overhead, 150 microVMs/s/host (§41.8.4, Table 42.3, §47.9.2, Table 47.8, §48.4.1). The minimal device model (virtio net and block, serial, keyboard controller for reset, no PCI or BIOS) is identical in Ch 41 and Ch 47. Ch 48 adds placement under 20 ms. | No action. |
| 13 | 33, 41, 48, 51 | Lambda | — | Consistent:<br>• \$0.0000166667/GB-s and \$0.20 per million (Ch 33, 48)<br>• 15-minute maximum (Ch 33, 41, Table 48.3)<br>• concurrency 1,000 per account (Ch 48 only)<br>• Ch 51 gives no Lambda prices<br>• Ch 48's break-even of about 52 million requests per month (≈ 20 RPS) is explicitly reconciled with §33.9.3's 23–45 RPS | No action. |
| 14 | 7, 24, 44 | Inter-region RTTs | — | Table 44.2 floors match $2d/v$ for recomputed great-circle distances. Examples: Virginia–Singapore 15,526 km → 155 ms; Virginia–Tokyo 10,873 km → 109 ms. Observed ranges include Virginia–Oregon 60–70 ms (Ch 7 §7.15 example: ~70 ms) and Virginia–London floor 59 ms (Ch 7: New York–London ≥ 56 ms over 5,570 km). | No action. Two rows round loosely (Virginia–Frankfurt "~6,500 km, ~66 ms"; 2d/v = 65), within the stated "~". |
| 15 | 41, 42, 46 | Borg | — | Ch 42 (cells of about 10,000 machines, five-replica Borgmaster, feasibility then scoring) agrees with §46.5. Against Verma et al. 2015, as recalled, §46.5 is right on:<br>• failover about 10 s (up to a minute)<br>• 99.99% availability<br>• 3–5% better packing than best fit<br>• a few hundred seconds vs > 3 days without optimizations<br>• 20–30% more machines if prod and non-prod were segregated<br>• 30–50% for power-of-two buckets | No action (#1 fixed the reference only). |
| 16 | 33, 34, 48, 51 | Prime Video | — | All four say: Step Functions plus Lambda passing frames through object storage, consolidated into one process on containers (ECS), about 90% cost reduction [Kolny 2023]. Ch 51 cites §33.9.3, which is where Ch 33's callout sits. | No action. |
| 17 | 1, 2, 18, 39, 44, 46, 48, 50, 51 | QuickBite and PhotoShare | — | Consistent:<br>• **Ch 51:** 2 million DAU, 500,000 orders/day and 15 million per month (§2.11). 0.25 orders and 30 browse reads per user (120 reads per order). Routing call \$0.005 (§2.4). PAR 9.6 and 6–18 nodes averaging about 8 (§18.11.3). Log bill \$11,664 → \$2,528 (§40.4.4).<br>• **Ch 44:** a three-market expansion with its own teaching figures. The 30,000 RPS global peak sits between Ch 18's S4 (6,667) and S5 (33,333). EU DR stays within the EU.<br>• **Ch 50:** 40 million customers and 2 million peak sessions, explicitly a post-Ch 44 state.<br>• **Ch 48 (PhotoShare):** 70 uploads/s and 17,400 views/s at 10 million DAU, recomputed from §1.9's assumptions (69.4 and 17,361). Feed API 1,700 RPS (§1.9).<br>• RTO/RPO usage in Ch 44 agrees with §39.8's tiers. | No action. |
| 18 | 15, 49 | Storage scale | — | Consistent:<br>• Colossus (curators over Bigtable, D servers, custodians) and Tectonic (Name/File/Block layers in ZippyDB) match §15.5.3.<br>• S3 strong read-after-write since December 2020 matches §15.4.<br>• Warfield 2023: > 280 trillion objects, > 100 million requests/s.<br>• WAS stamps: 10–20 racks × 18 nodes, ~2 PB raw (2011).<br>• Object-storage prices of about \$21,000/PB-month and \$1,000/PB-month agree with Ch 15's \$0.023/GB first tier. | No action. |
| 19 | 50 | Differential privacy | — | The ε-DP definition (neighbors differ in one person; bound for all output sets), Laplace $b = \Delta f/\varepsilon$, additive sequential and max parallel composition, and the $(\varepsilon, \delta)$ relaxation are all correct. Ch 71 must reuse this definition and notation ($\varepsilon$, $\Delta f$, $b$). | No action (see Remaining risks). |
| 20 | 44–51 | Terminology | — | No QPS, "message bus", "slave", "micro-app" or "uptime".<br>• **"Expiry":** used only for certificate and backup lifecycles (§47.13, §50.15), not as a TTL synonym.<br>• **"Centres":** appears only in the ISO/IEC 30134-2 title.<br>• **"Defense":** spelled American throughout. | No action beyond #6, #9. |

**Counts:** S1 = 0 · S2 = 0 · S3 = 10 (7 fixed, 3 deferred) · 10 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. **Ch 44 §44.4.1** fiber floor:
   - Virginia–Singapore 155 ms; with $k = 1.4$ + 2 ms, 219 ms; vacuum 103 ms; 71% propagation
   - inflation factors for all 11 rows of Table 44.2
2. **Ch 44 §44.4.2** Berlin checkout: 340 / 445 / 89 ms.
3. **Ch 44 §44.4.3** quorum placement:
   - A 92/181/241 ms, mean 148.5
   - B 67/156/216 ms, mean 123.5
   - C 14/103/163 ms, mean 70.5
   - Ohio-down sensitivity 92 ms; Figure 44.2 total 215 ms
4. **Ch 44 §44.5.2** DNS failover: 170 s worst, 140 s mean, 410 s at TTL 300, 110 s anycast; Q5 350 s.
5. **Ch 44 §44.6.5** topology downtime:
   - 390 / 120 / 174 / 36 / 6 min
   - 99.926% / 99.977% / 99.967% / 99.993% / 99.9989%
   - 83% global share; 54 of 270 min
6. **Ch 44 §44.7.2** lag budget: 40 changes; 120,000 backlog; 300.1 s lag; 3,000×.
7. **Ch 44 §44.8.1** conflicts: 0.04/s, 12 per group order; Q10 0.02/s.
8. **Ch 44 §44.11.2** N + 1 regions:
   - 37,500 / 18,750 / 12,500 / 9,375 per region
   - normal 40/53/60/64%; overhead 100/50/33/25%
   - uneven EU 26,250 (+40%)
9. **Ch 44 listing** (geo-replication simulator): output matches verbatim.
10. **Ch 45 §45.4** SI anomalies:
    - write skew $x + y = -80$; read-only anomaly $x = -11$
    - overlap $2.31 \times 10^{-5}$ (1 in 43,000); 231 pairs/day; 12 overdrafts; Q8 doubles to 24
11. **Ch 45 §45.8.2** BFT sizing:
    - $n = 4, 5, 7, 10$ → $f = 1, 1, 2, 3$; $q = 3, 4, 5, 7$; overlaps 2, 3, 3, 4
    - liveness $q \le n - f$ in each case
12. **Ch 45 §45.9.3** PBFT messages:
    - **24 / 84 / 180** replica messages ($2n(n-1)$); 29 / 92 / 191 with client
    - 180,000 → 1,800 per second with batching; ratio 7.5
13. **Ch 45 §45.10.2** HotStuff: basic 24 / 72 / 792; chained 6 / 18 / 198; PBFT 19,800 at $n = 100$ (100×).
14. **Ch 45 §45.11.1** Nakamoto probabilities:
    - $q = 0.1$: 0.2045873, 0.0509779, 0.0131722, 0.0002428, 0.0000012
    - $q = 0.3$: 0.1773523 … 0.0001522
    - $z$ for $P < 0.1\%$: 5, 8, 11, 15, 24, 41, 89, 340 (whitepaper values)
15. **Ch 45 listings** (DSG cycle detector, lattice-law checker, Nakamoto): all three match verbatim.
16. **Ch 46 §46.3.2** slack: 80% / 48%; 3,200 slack; 2,000 reclaimable; 4,000 for batch; Q2 520 cores.
17. **Ch 46 §46.4.4** Sparrow:
    - random 0.098%, per-task 5.6%
    - batch $P(\text{Bin}(20, 0.5) \ge 10) = 58.8\%$; $d = 3$: 97.9%
    - Q5 0.316
18. **Ch 46 §46.7** bin packing:
    - fragmentation $F = 100\%$ and 57% (6 copies, 12 vCPU)
    - alignment $A_X = 0.0664$, $A_Y = 0.1328$
    - FFD 11/9 bound
19. **Ch 46 §46.9** fairness:
    - water-filling 10/40/50 and weighted 10/30/60
    - **DRF 3 and 2 tasks**, ⟨3 CPU, 12 GB⟩ / ⟨6 CPU, 2 GB⟩, both 2/3, 4 GB idle; sharing incentive 2.25 / 1.5
    - weighted 18/24 tasks, shares 2/5 and 4/5
    - Q11 6 and 4
20. **Ch 46 §46.10.1** gang deadlock: 32 GPU·h, \$96; 24 GPU·h useful with gang admission.
21. **Ch 46 §46.12.2** backfill:
    - strict starts 4/4/6/6 (**mean 5 h**, end 12 h)
    - backfill 4/0/0/6 (**mean 2.5 h**, end 11 h)
    - $G = 14$ of 16 node·h (88%); 78 node·h; utilization 65% → 71%
22. **Ch 46 §46.5.6** Borg compaction: 240,000–260,000 machines; 40,000–60,000 extra; \$400–600 million.
23. **Ch 46 listings** (DRF, bin-packing simulation, backfill planner): all three match verbatim.
24. **Ch 47 §47.3.2** pooling:
    - silo 21,650; pool 11,165 (**48.4%** saving)
    - correlated $\rho = 0.3$: variance 7,675,000, σ 2,770, 16,455 (**24.0%**)
25. **Ch 47 §47.4.3** blast radius:
    - 99% / 79.8%; 16.5% / 13.3%; 0.05% / 1.0%
    - expected impact 1.60 + 0.40 = 2.0
26. **Ch 47 §47.8** per-tenant limits:
    - 260,000 RPS of limits, 13× oversubscription; 16,000-request burst = 2 s of headroom
    - weighted fair share $\theta = 400$; 3:1 → 750/250; Q10 500/200/200
    - shuffle sharding $\binom{100}{5} = 75.3$ million
27. **Ch 47 §47.9.3** isolation cost:
    - $H$ = 5 / 7 / 7 / 25; \$1.10 / \$1.53 / \$1.53 / \$5.48
    - +40%, 5×, 2,000×
28. **Ch 47 listing** (noisy-tenant simulation): values match; see #8.
29. **Ch 48 §48.5.2** cold-start percentiles:
    - $p = 0.5\%$ → warm p99.5 (+12%)
    - $p = 2\%$ → cold median 580 ms (3.6×); mean 84 → 94 ms
30. **Ch 48 §48.5.2** keep-alive, **$P_{\text{cold}} = e^{-\lambda K}$**:
    - 13.5% / 1.8% / 71.7%
    - idle 259 / 295 / 1,020 s
    - Q6 36.8%
31. **Ch 48 §48.5.3** provisioned concurrency: 32.4 million GB-s = \$135 vs \$14.4 on demand (9.4×); 535,680 invocations/day.
32. **Ch 48 §48.6** **Little's Law concurrency**:
    - 833 photos/s at 1,000; 96 interactive environments
    - 333 photos/s, 600,000 s (6.9 days); scale-up 10 s / 50 s
    - $N_{\text{pool}} = 1$; Q8 150
33. **Ch 48 §48.11 cost curves at 1M / 100M / 10B**:
    - per request $\$2.033 \times 10^{-6}$; container \$36.04, VM \$43.80 per month
    - 97 tasks; 107 VMs
    - totals \$2.93 / \$93.23 / \$108.75; \$293.33 / \$207.08 / \$222.60; \$29,333 / \$15,016 / \$16,207
    - break-even 51.6 million per month (19.9 RPS)
34. **Ch 48 listing** (keep-alive and provisioned simulation): output matches verbatim; the idempotent-handler listing runs.
35. **Ch 49 §49.3.1** **drive failures at EB scale**:
    - 75,000 drives (2,083 servers); 3.1 per day (6.2 at 3%; 150,000 drives at 3×)
    - 96 TB per repair, 296 TB/day, 3.4 GB/s; \$22.5 million
    - Q1 116,700 drives, 6.4 per day
36. **Ch 49 §49.3.2** metadata: 12.9 TB; 12 PB; 1.25 million lookups/s.
37. **Ch 49 §49.7** migration: 579 / 57.9 days; shipment 12.3 days (≈ 378 Gb/s effective); \$1 million.
38. **Ch 49 §49.8** scaling:
    - stencil 21.05 ms (99.6%) and 401.7 µs (81.6%), 52.4× speed-up
    - El Capitan HPL 63.4%; hypothetical Rmax 127 PFlop/s
39. **Ch 49 §49.9.2** **ring vs tree all-reduce**:
    - 79.4 vs 480 ms (6×); 0.631 ms vs 64 µs (10×)
    - **crossover 1.42 MB at 64 ranks**; Rabenseifner 78.8 ms
    - Q9 18.8 / 80 ms
40. **Ch 49 §49.10–§49.11** networks and checkpoints:
    - DCQCN 50 → 25 → 37.5 … 49.2 Gb/s; 12.5% cut at $\alpha = 0.25$
    - fat tree 65,536 hosts, 5,120 switches, 13.1 Pb/s
    - dragonfly 16,512 hosts, 832 Tb/s, ≈ 102 Gb/s per host
    - Young 4,290 s (9.6% waste) vs 1,200 s (2.7%); Q12 27,648; Q13 1,860 s
41. **Ch 49 listings:** the ring all-reduce simulation matches verbatim. The Dremel-levels listing runs. The mpi4py listing is marked illustrative and its comment (`10 [6. 6. 6. 6.]`) is correct.
42. **Ch 50 §50.3** defense in depth: 0.0015 (1 in 670) → 0.005 (3.3×).
43. **Ch 50 §50.4.3–§50.6** identity and supply chain:
    - SPIRE 11.1 + 1.39 ≈ 12.5 signatures/s; 30 min outage budget
    - token refresh 556 / 6,667 / 2,222 per second
    - dependencies 13.9% and 7.2%
44. **Ch 50 §50.7** detection:
    - precision 0.98% (101 false per true)
    - MTTD 30 h, MTTR 3 h, $E$ = 66,000 / 63,000 / 36,000 / 6,600 records
    - Q7 0.1%
45. **Ch 50 §50.10.2** **k-anonymity**: classes 3/3/2/2 → $k = 2$; 6/4 → $k = 4$ with $l = 1$. The listing matches verbatim.
46. **Ch 50 §50.11** **Laplace noise $b = \Delta f/\varepsilon$**:
    - $b = 2$, $e^{-2.5} = 0.082$, $t_{95} = 2 \ln 20 = 5.99$ (0.48%)
    - $\varepsilon = 0.1$: $t_{95} = 30$
    - $e^{0.1} = 1.105$, $e^{10} \approx 22{,}026$
    - the composition example 1.0/day, 365/year, 20.8/year
    - Census 19.61 = 17.14 + 2.47; Q10 0.135
    - The Laplace listing matches verbatim.
47. **Ch 51 §51.3–§51.4** unit economics:
    - crossover 444 million messages
    - Table 51.2: \$95,000 + \$390,000 = \$485,000, \$0.03233 per order; third-party share 80%
    - unit cost \$0.0551 / \$0.0323 / \$0.0304
    - margin \$1.858 (21.9%) vs −\$10.12 with 2,400 routing calls; break-even 1.08 million orders
48. **Ch 51 §51.6** **commitment optimum (discount quantile)**:
    - $c^* = Q_x(d)$ derivation checked
    - table check \$1,175 + \$3,436 = \$4,611; 26.6% (\$1,433) at 60.1
    - spot \$0.0345, 65.5%; Q8 70%
    - The listing matches verbatim (grid optimum 60.0, quantile 60.1).
49. **Ch 51 §51.7–§51.9** levers and build vs buy:
    - cross-zone 86.4 million requests, 2,304 GB/day, \$1,382 → \$207
    - Kafka TCO \$39,628 vs \$29,871 (24.6%); \$222,280 vs \$253,712 (12%); $k^* = 2.7$
    - forecast routing saving \$162,000 in month 1, \$3.07 million per year
50. **Ch 51 §51.10–§51.11** **PUE and SCI**:
    - PUE 1.30, 3.0 GWh, \$300,000, 1,200 t; 1.58 vs 1.10 → 4.8 GWh, \$480,000, 1,920 t; Q9 1.20
    - carbon shift 90 → 50 kg (44%), 21.25 kg (76%); 32.9 / 18.3 / 7.8 t a year
    - **SCI** 1,192.3 kWh, 453 kg operational, 116 kg embodied, 0.0379 g per order (embodied 20%)
51. **Cross-references.**
    - **Ch 44–51:** all 609 `§` references resolve. All cross-chapter targets are on topic apart from #1 (and #3, imprecise rather than wrong).
    - **Out to Ch 52+:** chapter-level references match the TOC (Ch 61 data engineering, 62 feature stores, 64 GPUs/roofline, 65 distributed training, 71 DP for ML, 77 agents, 79 production AI and tenant isolation, 80 large AI clusters).
    - **Inbound:** all 46 chapter-level references from Ch 1–43 into Ch 44–51 match the drafted chapters (Ch 44 multi-region and residency; Ch 45 $3f+1$; Ch 46 Borg and scheduling theory; Ch 47 noisy neighbors and isolation levels; Ch 48 Lambda and Firecracker internals; Ch 49 RDMA; Ch 50 supply chain and privacy; Ch 51 FinOps and carbon). #7 adds one.

## Remaining risks

- **Differential privacy across books.** Ch 50 now defines ε-DP, sensitivity, the Laplace scale and basic composition. Ch 71 (DP-SGD, accounting) should cite §50.11.1–§50.11.3 instead of redefining them. It should also keep the notation ($\varepsilon$, $\delta$, $\Delta f$, $b$) and state clearly when it switches from basic to advanced or Rényi composition, which §50.11.3 mentions only qualitatively.
- **All-reduce ownership.** §49.9.2 now owns the α–β model, ring, tree and Rabenseifner costs and the 1.42 MB crossover. Ch 65 (collectives, NCCL) and Ch 80 should build on §49.9.2 with the same symbols ($p$, $n$, $\alpha$, $\beta$) and not re-derive the ring bound.
- **Fairness in three places.** Water-filling appears in §46.9.1 and §47.8.2 (now cross-linked), and DRF in §46.9.3. Ch 79 (token-based rate limiting, tenant isolation) and the Ch 52.3 rate-limiter case study should cite these and §22.4 rather than restate them.
- **Teaching scales diverge by design.** QuickBite appears at its 2 million DAU design point (Ch 2, 18, 39, 51), at a three-market 30,000 RPS scale (Ch 44) and at 40 million customers (Ch 50). Each chapter labels its numbers as teaching assumptions. Case studies (Ch 52–56) should say which scale they use.
- **Perishable facts** (#10) are concentrated in Ch 44, 48 and 51. They include managed-database modes, Lambda quotas and prices, Slurm defaults, PUE survey figures and vendor energy claims (Graviton). They carry open items, but none was re-verified here.
- **Reference drift.** About 655 references were checked by a scratch script. `qa_check.py` still has no `§`-reference resolver. Part IX adds 32 chapter-level references into Ch 61–80, which depend on TOC numbering not yet drafted.
