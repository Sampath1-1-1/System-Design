# Wave 5 Integration Review — Chapters 30–38

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-10-31 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* Parts VI–VII, chapters 30–38 (messaging, Kafka, event-driven patterns, architecture patterns, microservices, OOD, SOLID, design patterns, UML/LLD), and their interfaces with chapters 1–29.

**Method.** This was targeted grep and reading, not a full read-through. It follows the wave 4 method.

1. **Ownership.** A scratch script split every chapter 18–38 at its `##`–`####` headings and counted words and keyword hits per block for these topics:
   - Kafka internals (ISR, KRaft, high watermark, leader epoch, `min.insync`, `linger.ms`)
   - sagas, outbox, CDC, CQRS and event sourcing
   - idempotency
   - DDD (aggregates, bounded contexts, ubiquitous language)
   - hexagonal architecture and ports
   - tracing (spans, context propagation)
   - circuit breakers and bulkheads
   - LRU
   - rate-limiter algorithms
   - Observer and pub/sub
   - SOLID names
   - shuffle sharding

   Every non-owner block with three or more hits was read against the brief's ownership list and 04 §4.5:
   - Kafka internals → Ch 31
   - sagas → §32.7 (preview §28.6)
   - outbox, CDC, CQRS and event sourcing → Ch 32
   - idempotency → §22.15
   - microservices deep treatment → Ch 34 (overview §33.7)
   - DDD → Ch 34
   - hexagonal → §33.10
   - OOD → Ch 35; SOLID → Ch 36; patterns → Ch 37
   - rate-limiter algorithm → §22.4
   - LRU policy → §20.9
   - circuit breakers and bulkheads → Ch 22
   - distributed tracing → Ch 40 (intro §34.9)
2. **Recurring facts.** Facts that appear in more than one chapter were extracted and compared:
   - Kafka version history (Ch 26, 27, 30, 31, 32): KRaft, ZooKeeper removal, KIP-848, KIP-932
   - Kafka defaults
   - delivery-semantics wording (Ch 22, 24, 29, 30, 31, 32)
   - the Prime Video and Segment stories (Ch 33, 34)
   - shuffle-sharding attribution (Ch 18, 33)
   - Spring/DI statements (Ch 36, 37)
   - event/command/message definitions (Ch 30, 33, 34, 37, terminology)
3. **Cross-references.** All 590 `§N.M[.K]` references in Ch 30–38 were resolved by script: 229 intra-chapter, 361 cross-chapter, 11 into Ch 39+. All 56 `§` references and 38 chapter-level references from Ch 1–29 into Ch 30–38 were resolved the same way. Targets in Ch 1–38 were checked against the actual headings and targets in Ch 39+ against `01-master-toc.md`, then every cross-chapter reference was read for topic fit. The 78 chapter-level "Chapter N"/"Ch N" references in Ch 30–38 were also checked. Every Figure, Table and Formula number cited in Ch 30–38 has a matching caption.
4. **Numbers.** About 120 numbers in 40 worked examples were recomputed with `python3` (list below). All 63 Python listings in Ch 30–38 were extracted and run (61 runnable, 2 marked illustrative), and their output was compared with the chapters' `text` output blocks and inline output comments.
5. **Concepts.** These statements were checked: Kafka EOS covers Kafka-to-Kafka only; the outbox requires idempotent consumers; the Liskov–Wing rules (preconditions not strengthened, postconditions not weakened, invariants and history kept); Singleton caveats; double-checked locking needs `volatile` (JSR-133); DI ≠ DIP ≠ IoC.
6. **Terminology.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 38 chapters.
- `python3 build/build.py --chapters 30-38 --name qa --formats html`: 493 diagrams across 38 chapters, 0 errors.
- `dist/qa.*` was deleted afterwards, and `manuscript/appendices` was restored with `git checkout`.
- The build left no changes in `diagrams/` or `code/`. The only modified files are chapters 30, 31, 32, 34, 36, 37 and 38.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 31 | §31.15.2 disk worked example, step 4 | S2 | **Internal inconsistency.** "44 brokers, far more than the 3 that throughput needed (§31.13.2)". The 3 brokers come from §31.13.2's **400 MB/s** example. This example is at **200 MB/s**, where the same formula gives ⌈max(1.2, 0.77)⌉ = 2. | Now reads "far more than the 2 that throughput needs at 200 MB/s by the formula of §31.13.2 (the 400 MB/s example there needed 3)". The rest was recomputed: 121 / 363 / 518 TB, 43.2 → 44 brokers, tiered 74 TB → 7 brokers. |
| 2 | 36 | §36.8.1, "Reading the diagram" after Figure 36.15 | S3 | "Timeouts, retries and circuit breakers belong (Chapter 39)". Chapter 39 (Reliability and Resilience) exists in the TOC, but these mechanisms are owned by §22.11–§22.13. | Changed to "(§22.11–§22.13)". |
| 3 | 34 | §34.10 "Meshing QuickBite", step 4 | S3 | The ambient CPU was computed as "40 × 0.06" (nodes × vCPU). The box's own formula is $C = (\Lambda x/1{,}000)\,c$, with the per-1,000-RPS figure, as used for sidecars in step 2. The result (2.4 vCPU) is the same only by coincidence (40 nodes = 40 thousand proxy-requests/s). | Now reads $(20{,}000 \times 2 / 1{,}000) \times 0.06 = 2.4$ vCPU "(two ztunnels per call)". The memory term (per node, $M = P m$) was correct and is unchanged. |
| 4 | 31 vs 26 | §31.4 "From ZooKeeper to KRaft" | S3 | "From 2011 until 2022, Kafka stored its metadata in ZooKeeper" suggests ZooKeeper ended in 2022. KRaft became production-ready in 3.3 (2022), ZooKeeper mode stayed supported until 4.0 (March 2025), and both Ch 26 (§26.8) and §31.4's own next paragraph say so. | Now reads "From 2011 until KRaft became production-ready in 2022 (and in many clusters until 4.0 removed the option)…". |
| 5 | 30 vs 37 | §30.5.1 pub/sub | S3 | **Observer vs pub/sub** linked one way only. §37.8 ("Observer and publish/subscribe", Table 37.1) cites §30.5, but Ch 30 never mentions Observer. | Added one sentence to §30.5.1: "Inside a single process the same idea is the Observer pattern (§37.8), which is synchronous and keeps no messages; Table 37.1 compares the two." |
| 6 | 36 vs 33 | §36.7.3 after Figure 36.13 | S3 | **Hexagonal ownership.** §36.7.3's port/adapter refactor (825-word code example) is DIP at class level and does not re-teach hexagonal architecture. However, it did not link to §33.10, which links back ("this is the dependency inversion principle (§36.7) applied to a whole application"). §36.8.1 already cites §33.10. | Added "Applied to a whole application, this arrangement is hexagonal architecture (ports and adapters, §33.10)." |
| 7 | 34 vs 33 | §34.3.3 Conway's law | S3 | Conway's law and the inverse Conway maneuver are stated in both §33.13.2 (with the communication-path formula) and §34.3.3 (≈100 words, with team-ownership rules). The overlap is short, but Ch 34 cited only §1.4. | Added "(§1.4; §33.13.2 counts the coordination paths)". |
| 8 | 34 vs 37 | §34.4 misconception "DDD means repositories and factories" | S3 | **DDD/Repository ownership.** §37.13 cites §34.4 for aggregates, but Ch 34 never pointed to the Repository and Factory patterns. | Added "(the Repository and Factory patterns themselves are in §37.13 and §37.3)". |
| 9 | 30, 31, 32, 34, 37, 38 | Prose (≈40 places) | S3 | **British spellings.** Examples: "acknowledgement(s)" ×34 in Ch 30–31 (Ch 1–29 use "acknowledgment" 52 times), "modelling" ×2 and "labelled" in Ch 34, "catalogued" in Ch 37, "cancelled" in Ch 37 and 38, and "Cancelling" in Ch 32. | Changed to the American forms. Kept unchanged: the cited RabbitMQ title *Consumer Acknowledgements and Publisher Confirms*, the provider status codes `AUTHORISED`, the `CANCELLED`/*Cancelled* identifiers and state names, and the quoted status value "cancelled" in Table 32.9 (same treatment as wave 2 #10). |
| 10 | 38 | §38.13 Q6 model answer | S3 | "Entries with optional expiry" uses "expiry" as a synonym for TTL (`terminology.md`). | Now reads "Entries with an optional TTL". "Lazy/active expiry", meaning the *mechanism*, is kept, as in §20.8. Lease-like uses are also kept: lease expiry (Ch 30), reservation and hold expiry (Ch 32, 38). |
| 11 | 31 | §31.7.4 share groups; §30.12 | S3 | KIP-932 maturity. Ch 31 says "early access in Kafka 4.0 and … still maturing through the 4.x line as of 2026", and Ch 30 says "introduced in the 4.x line". The two are consistent and both are hedged, but the current GA status was not verified. | **Deferred.** Already an open item in §30.19 and §31.22. |
| 12 | 33 vs 34 | Prime Video and Segment callouts | S3 | The facts are consistent: Step Functions + Lambda → single process; Segment's 100+ destination services consolidated into one. Ch 33 gives "over 90%" and Ch 34 "about 90%", and Ch 34 lists the author attribution as open while Ch 33 cites Kolny. The post's title says "by 90%" and the body says "over 90%" (from memory; not re-verified). | **Deferred.** Both chapters carry open items, so they should be unified once the post is checked. The difference does not change either lesson. |
| 13 | 37 | §37.16.5 citation `[Bacon et al.; Manson et al. 2005]` | S3 | The Bacon et al. "Double-Checked Locking is Broken" declaration is cited without a year, so it does not match the author–year format. | **Deferred.** Already an open item in §37.24 (full author list and date). |
| 14 | TOC vs 30–38 | `01-master-toc.md` Parts VI–VII | S3 | Drafted titles are reworded or extended. Examples: 30.12 "Kafka vs RabbitMQ (and SQS, Pulsar)", 31.4 "Brokers and clusters: ZooKeeper mode versus KRaft", 33.7/33.8 "(overview)", 34.9 "(introduction)", 37.15 "State, Template Method and Chain of Responsibility", 38.8 "Object relationships in depth", 38.9 "The LLD interview method". | **Deferred** (TOC owner). The section numbers 30.3–38.10 match the TOC exactly, so no reference breaks. |
| 15 | 30–38 | Ownership measurement | — | Non-owner passages measured:<br>• **Kafka internals:** none outside Ch 31 except §27.4's ISR callout (190 words, consistent with §31.9). §30.12 (786 words) compares brokers at summary level and points to Ch 31.<br>• **EOS:** §32.9.1 (437 words) summarizes the three EOS mechanisms in about 130 words, citing §31.11 and §28.4.8. The rest (Figure 32.13 boundary, Table 32.11, misconception) is unique to Ch 32.<br>• **Outbox, CDC, CQRS, ES:** the only hits outside Ch 32 are §31.14.2 (Debezium as a Connect source, 299 words, cites §32.5–§32.6) and the Ch 36 SRP example, where `outbox` is a list variable, not the pattern.<br>• **Sagas:** §28.6 is still 311 words; Ch 33, 34, 37 and 38 mention sagas in one sentence each, citing §32.7/§32.8.<br>• **Idempotency:** every use in Ch 30–38 cites §22.15 or §32.10, and §32.10 opens "Section 22.15 owns idempotency keys".<br>• **Microservices:** §33.7 (480 words) is an overview citing §34.6, §34.13 and §34.14.<br>• **DDD:** appears only in Ch 34; Ch 33 and 37 cite §34.4/§34.5.<br>• **Tracing:** §34.9.1 (452 words) is the designated intro and cites §40.6–§40.7.<br>• **Circuit breakers and bulkheads:** only one-line uses, all citing Ch 22.<br>• **Rate limiter and LRU:** §38.10.3 and §38.10.6 state that policy and algorithm are in §20.9 and §22.4/§22.8 and treat class design only. Ch 20 has the one-paragraph LRU description; Ch 38 has the data structure and the class.<br>• **Patterns in Ch 38:** the solutions name and cite patterns (§37.3, §37.7, §37.8, §37.10, §37.12, §37.15, §37.16) and principles (§36.4, §36.5, §36.7) rather than re-teaching them. | No action beyond #5–#8. No non-owner passage over about 400 words duplicates owner content. |
| 16 | 26, 27, 30, 31, 32 | Kafka facts | — | All consistent:<br>• KRaft is Raft-based for metadata only, and data partitions use ISR (Ch 26, 31).<br>• KRaft was production-ready in 3.3 (2022); ZooKeeper mode was deprecated in 3.5 and removed in 4.0 (March 2025) (Ch 26 ×3, Ch 31).<br>• KIP-848 is GA in 4.0.<br>• KIP-932 is early access in 4.0 (Ch 30, 31).<br>• The defaults agree wherever they appear: `acks=all` and idempotence since 3.0 (KIP-679), `min.insync.replicas` 1, unclean election false, `replica.lag.time.max.ms` 30 s, `delivery.timeout.ms` 120 s, `transaction.timeout.ms` 60 s, `retention.ms` and `segment.ms` 7 days, `segment.bytes` 1 GiB, 50 `__consumer_offsets` partitions, EOS commit interval 100 ms.<br>• `acks=all` waits for the current ISR (Ch 27 §27.4 and Ch 31 §31.6.2). | No action. |
| 17 | 22, 24, 29, 30, 31, 32 | Delivery semantics | — | Wording is consistent with `terminology.md`:<br>• Exactly-once *delivery* is impossible over a network (§24.3.3 two generals; §30.8; §31.11.1; §32.9).<br>• Effectively-once = at-least-once + idempotent or transactional effect (Table 30.6; §32.9 equation; §22 cites §32.9).<br>• Kafka EOS stops at Kafka's boundary (§30.8, §31.11.3 warning, §32.9.1 Figure 32.13 and mistake callout).<br>• The outbox needs idempotent consumers (§32.5 cites §32.10; §33.8 and §34.11.2 say the same).<br>• The Pub/Sub and SQS FIFO "exactly-once" features are described as broker-boundary features. | No action. |
| 18 | 30, 32, 33, 34, 37 | Event / command / message | — | §30.6.1 defines message (transport unit), command (request to one receiver, may be refused) and event (fact, past tense, cannot be refused), matching `terminology.md`. §33.8 (EDA), §34.4.4 (domain event), §34.4 ("a *command* asks for something and may be refused", citing §30.6) and §37.12 ("In this book's terminology a command is a request…") agree. | No action. |
| 19 | 18, 33 | Shuffle sharding | — | Both attribute the Builders' Library article to MacCárthaigh 2019 and agree on the mechanism. §33.12.2's open item records the brief's Brooker misattribution. | No action. |
| 20 | 36, 37 | DI and Spring | — | Consistent. §36.7.4 says DI is one form of IoC, that DI is possible without DIP, and that DIP is possible with a service locator. §37.14 says Spring and Guice build the graph, that Spring recommends constructor injection, and that a locator is not a fix for constructor bloat. §37.11 describes Spring's proxy-based `@Transactional` and self-invocation caveat, with the Boot CGLIB default flagged as an open item. | No action. |
| 21 | 35, 36, 37 | Conceptual statements | — | All correct:<br>• **Liskov–Wing rules:** §36.5.1 gives $\text{Pre}_T \Rightarrow \text{Pre}_S$, $\text{Post}_S \Rightarrow \text{Post}_T$ and invariants plus the history constraint. §35.9.1 states Meyer's rule as "weaken pre, strengthen post"; the §35 summary and checkpoint agree.<br>• **Singleton:** "one per process / class loader" (200 pools × 10 = 2,000 connections); leader election, not a pattern, for system-wide uniqueness.<br>• **Double-checked locking:** broken without `volatile` under JSR-133; holder idiom and enum preferred; the Python race demonstrated. | No action. |
| 22 | 30–38 | Terminology | — | No QPS, "uptime", "message bus" or "slave". "Master" does not appear. "Box" appears only for UML boxes (§38.5). "Hit rate" appears once in a table header ("Consumer dedup hit rate"), which is acceptable. | No action. |

**Counts:** S1 = 0 · S2 = 1 (fixed) · S3 = 13 (9 fixed, 4 deferred) · 8 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. **Ch 30 §30.3.1** availability:
   - $0.999^5 = 0.99501$ → 216 min/month
   - $0.999^{10} = 0.99004$ → 430 min
   - hybrid $0.999^2 \times 0.9999 = 0.99790$ → 91 min
   - front + broker 0.99890 → 48 min
2. **Ch 30 §30.4.2** visibility timeout: $10 \times 2.5 + 10 = 35$ s, rounded to 40 s.
3. **Ch 30 §30.4.3** consumers:
   - $L = 300$, 428.6 slots, 42.9 → 43 instances
   - $\mu = 2{,}867$/s
   - drain $3.6 \times 10^6 / 867 = 4{,}154$ s (69 min)
   - 100 instances: 771 s (13 min)
   - wait 20.9 min
4. **Ch 30 §30.5.2** fan-out:
   - 60,000 deliveries/s (5.18 billion/day)
   - 120 MB/s ≈ 0.96 Gb/s
   - 108 million messages, 216 GB
5. **Ch 30 §30.8** duplicates: 1.001 deliveries, 10.01/s, 864,865/day.
6. **Ch 30 §30.9** per-key ordering:
   - 20/s per key, 4,000/s for the queue
   - backlog 18,000, 900 s
7. **Ch 30 §30.10** DLQ:
   - 300 s
   - $5 \times 2 + (10 + 20 + 40 + 80 + 160) = 320$ s, consistent with the formula counting the delay after the fifth failure, as in the Figure 30.12 description
8. **Ch 31 §31.5.2** partitions:
   - 5 and 25
   - $1.5 \times 25 = 37.5$ → 38, rounded to 48
9. **Ch 31 §31.5.3** remap fractions:
   - $6 \to 8$: 0.75
   - $6 \to 12$: 0.50
   - $12 \to 13$: 0.923

   The murmur2 listing was run. All six Kafka test-vector asserts pass, and the output (75.1% / 49.9% / 92.3%; `customer-42` → 3 and 1) matches the chapter verbatim.
10. **Ch 31 §31.6.1** batching:
    - linger bound 5, size bound 32
    - 9,600 → 2,400 batches/s (4×)
11. **Ch 31 §31.7.3** lag:
    - 48 million records
    - 2,400 s (40 min)
    - 600 s with 24 members
12. **Ch 31 §31.9** ISR:
    - HW = 1,020, then 1,048 after the shrink
    - $U_w$: 0.000298 ($m = 2$), 0.0297 ($m = 3$), $10^{-6}$ ($m = 1$)
    - $q = 0.01$ ≈ 7.2 h/month
13. **Ch 31 §31.13.2** brokers at 400 MB/s: 2.4 (disk) vs 1.54 (egress) → 3. At 200 MB/s: 1.2 vs 0.77 → 2 (#1).
14. **Ch 31 §31.13.3** end-to-end latency: $5 + 1 + 1 + 10 + 2 + 10 = 29$ ms.
15. **Ch 31 §31.15.2** disk:
    - $1.2096 \times 10^{14}$ B = 121 TB; 363 TB; 518 TB
    - 43.2 → 44 brokers
    - tiered 74.1 TB → 7 brokers
16. **Ch 32 §32.3.2** replay:
    - 2.5 s
    - $0.002 + 0.0125 = 14.5$ ms
    - 20,000 s (5.6 h)
    - 20.8 min on 16 partitions
17. **Ch 32 §32.4.2** projection catch-up: 400 s, and 2,400 s (40 min) at $\lambda = 4{,}500$.
18. **Ch 32 §32.5.3** relay:
    - 16,667 events/s
    - 495 events/s (10.1× too slow)
    - 80 ms latency
19. **Ch 32 §32.10** dedup table: $3.024 \times 10^9$ rows × 60 B = 181 GB; 24 h = 26 GB.
20. **Ch 33 §33.4.2** release train:
    - $0.99^{48} = 0.617$ (38% held)
    - $0.99^4 = 0.961$
    - $0.99^{12} = 0.886$
21. **Ch 33 §33.9** serverless:
    - Little's Law: 20 environments
    - $8.33 \times 10^{-7}$ + $2 \times 10^{-7}$ → $R^* = 116.1$ M/month = **44.8 RPS**
    - with gateway: 59.0 M = 22.8 RPS
    - \$52.7 at 10 RPS; \$1,054 at 200 RPS (8.8×)
22. **Ch 33 §33.12.1** cells: 20 cells, $B = 5\%$, waves 1 + 2 + 4 + 8 + 5 = 20.
23. **Ch 33 §33.12.2** shuffle sharding:
    - $\binom{8}{2} = 28$: 3.6% / 53.6% / 42.9%
    - $\binom{100}{5} = 75{,}287{,}520$
    - $P(3) = 5.93 \times 10^{-4}$, $P(4) = 6.3 \times 10^{-6}$, $P(5) = 1.3 \times 10^{-8}$; sum $6.0 \times 10^{-4}$ (≈ 6 customers)
    - $P(0) = 0.770$
24. **Ch 33 §33.13.2** Conway paths: 3 / 66 / 12 (−82%).
25. **Ch 34 §34.3.2** Jaccard: 0.43 and 0.029.
26. **Ch 34 §34.4.3** aggregate conflicts:
    - $1 - e^{-0.2} = 0.181$
    - $1.67 \times 10^{-4}$ (1 in 6,000)
    - ratio 1,088 ("about 1,000-fold")
27. **Ch 34 §34.6.2** BFF: 960 / 360 / 268 / 163 ms.
28. **Ch 34 §34.7** stale endpoints:
    - 62 s → 6,200 failures
    - 32 s → 3,200
    - with $q = 0.99$: 62
29. **Ch 34 §34.8.2–§34.8.3** chatty calls and fan-out:
    - 375 / 37.5 / 5.5 ms; 68× faster, 150× less load
    - $0.99^6 = 0.9415$; $0.99^{100} = 0.366$
30. **Ch 34 §34.10** mesh: 1.0 ms, 8 vCPU, 24 GB, 2.4 vCPU, 480 MB, 0.8 ms.
31. **Ch 34 §34.14.3** call chain:
    - 3.59 / 7.17 / 2.16 h per month
    - 107.5 / 32.25 ms
32. **Ch 35 §35.8** class explosion: 6/6, 27/10, 36/11.
33. **Ch 35 §35.10.1** LCOM1: 15 pairs, $|Q| = 4$, $|P| = 11$, LCOM = 7, three components; listing output `(7, 11, 4)` and `(0, 0, 3)`.
34. **Ch 36 §36.3.2** SRP receipt: 3.19 / 47.19 and 2.90 / 46.90; 6.90 gap.
35. **Ch 36 §36.5.1** SMS segments: ⌈320/153⌉ = 3, ⌈1,600/153⌉ = 11, ⌈10,000/153⌉ = 66.
36. **Ch 36 §36.8.2** Martin metrics: 0.25 / 0.375 / 0.375, 0 / 0.5 / 0.5, adapters 1 / 0 / 0.
37. **Ch 37 §37.16.2** Goetz pool sizing:
    - $8 \times 0.75 \times 20 = 120$ threads
    - 1,200 tasks/s
    - 75% CPU
    - 8 threads → 80/s at 5% CPU (95% idle)
    - 50 threads for 500/s
38. **Ch 38 §38.10.1** parking fee: \$12, \$30, \$84; the cap binds from 421 min.
39. **Ch 38 §38.10.2** elevator ETA: 18 / 36 / 12 s; C chosen.
40. **Listings.** All 61 runnable Python listings in Ch 30–38 ran (exit 0). Every one with a `text` output block matches verbatim, with these exceptions, all expected:
    - three `unittest` timing lines in Ch 32
    - the timing line in the §37.10 decorator listing (0.004 vs 0.002 ms)
    - the §38.10.3 LRU stress run, whose output is quoted inline and whose `evictions` count the chapter says varies with scheduling (32,233 here vs 32,220 quoted; hit ratio 0.33 as stated)

    The inline output comments in Ch 35–36 also match. They include:
    - `PercentOff 634 / FixedOff 500 / BuyNGetOneFree 1299`
    - `5049`, `5849`
    - `True 5452`
    - the LSP contract-test table
    - the Martin metrics table

    Two listings were marked illustrative and not run (§32.11.1 Temporal, §35.4.3 tell-don't-ask).
41. **Cross-references.**
    - **Ch 30–38:** all 590 `§` references resolve to sections on the stated topic, apart from #2. The five "unresolved" hits in Ch 8, 16, 21 and 22 are RFC and book section numbers, not book references.
    - **Inbound:** all 56 `§` references and 38 chapter-level references from Ch 1–29 into Ch 30–38 resolve on topic. Examples:
      - §30.8, §30.11 (Ch 1, 9)
      - §31.3/§31.6/§31.8/§31.9/§31.13 (Ch 3, 5, 6, 23)
      - §32.4–§32.10 (Ch 2, 11–14, 18, 20, 22, 28, 29)
      - §33.5/§33.12 (Ch 1–3, 18, 22)
      - §34.3–§34.14 (Ch 1, 2, 7, 8, 10, 12, 19)
      - §38.10 (Ch 3)
    - **Ch 39+:** references into Ch 39+ match the TOC topics:
      - §40.6–§40.7 tracing and OpenTelemetry
      - §42.10 Gateway API
      - §43.4–§43.7 and §43.13 deployments, flags and migrations
      - Ch 44 multi-region, Ch 47 tenancy, Ch 48 Lambda internals, Ch 87 interviews

## Remaining risks

- **Kafka and cloud product facts are the most perishable content in Parts VI–VII.** They include:
  - the KIP-932 share-group maturity (#11)
  - the KIP-848 client opt-in
  - tiered-storage status
  - Lambda prices and the 15-minute limit
  - SQS fair queues (2025)
  - RabbitMQ 4.0's delivery-limit default
  - Pub/Sub retention limits
  - Istio's per-hop latency and per-proxy resource figures
  - Spring proxy defaults

  All carry "as of 2026" tags or open verification items, but none was re-verified against primary sources in this review.
- **Unverified narrative sources:**
  - the Prime Video post (title, "over 90%", author)
  - the Segment post (number of services)
  - the Slack job-queue post
  - Uber's retry-topic post
  - the Bacon et al. declaration's date

  All are listed in the chapters' open items.
- **Overlapping pairs to watch.** Several pairs are now linked both ways, but a future edit could re-create duplication:
  - Conway's law (§33.13.2 / §34.3.3)
  - hexagonal and DIP (§33.10 / §36.7.3 / §36.8.1)
  - Kafka EOS (§31.11 / §32.9.1)
  - Observer and pub/sub (§30.5.1 / §37.8)

  Chapter 40 (§40.6–§40.7) should build on §34.9 rather than re-introduce spans and context propagation. Chapter 52.3 (rate-limiter case study) should cite §22.4 and §38.10.6.
- **Reference drift.** About 690 references were checked by a scratch script. `qa_check.py` still has no `§`-reference resolver. Parts VI–VII add 11 references into Ch 40–43 that depend on TOC numbering not yet drafted.
