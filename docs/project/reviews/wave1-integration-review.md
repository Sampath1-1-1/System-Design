# Wave 1 Integration Review — Chapters 1–10

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-10-30 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`, applied *across* chapters 1–10.

**Method.** Targeted grep and reading, not a full read-through. (1) The latency, RTT, handshake, password-hashing and availability claims were extracted from every chapter and compared. (2) All 740 `§N.M[.K]` references and all 174 `Ch N`/`Chapter N` references were checked by script: Ch 1–10 targets against the actual headings, Ch 11–93 targets against `01-master-toc.md`. Then each cross-chapter reference was read for topic fit. (3) The ownership rows in 04 §4.5 were checked: WebSockets (9.6 vs 7.11), password storage (10.6 vs 8.11) and the latency table (4.17 vs 5.9.4). (4) 38 worked examples and protocol facts were recomputed or checked with `python3`; see the list at the end. (5) The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.** `python3 build/qa_check.py`: 0 findings in all 10 chapters. `python3 build/build.py --chapters 1-10 --name qa --formats html`: 100 diagrams, 0 errors. `dist/qa.html` was deleted afterwards. The build regenerated `manuscript/appendices/A-glossary.md` and `C-formula-handbook.md` from the current manuscript; most of that diff comes from other authors' uncommitted chapter changes.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 4 | §4.10.2, "Reading the diagram" for Figure 4.3 (M/M/1) | S2 | Points to "M/M/c, §4.10.5", but §4.10.5 does not exist; M/M/c is §4.10.4. | Changed to §4.10.4. |
| 2 | 10 | §10.3.5, Step 3 "Rank" | S2 | "(see §10.3.6)", but §10.3.6 does not exist. The risk score is in the "Mathematical foundations" block of §10.3.5. | Changed to "(see the risk-score formula below)". |
| 3 | 10 | Table 10.2, row T5 (payment webhook) | S2 | HMAC verification cross-referenced to §10.4.7 (Randomness). | Changed to §10.4.6 (MACs and HMAC). |
| 4 | 10 | Table 10.4 (primitive summary), key-exchange row | S2 | The "mixing paint" analogy for Diffie–Hellman cross-referenced to §10.4.5 (Digital signatures). | Changed to §10.4.4 (Key exchange). |
| 5 | 7 | §7.12, definition of API gateway | S2 | "API gateway (§22)": wrong target, and a chapter-only § reference. API gateways are §34.6 in the master TOC. | Changed to §34.6. |
| 6 | 7 | §7.6 (GeoDNS paragraph) | S3 | Chapter-only reference "§44". | Changed to "Ch 44". |
| 7 | 7 | §7.15.1 worked-example interpretation | S3 | "(CDNs, §21; multi-region, §44)": chapter-only § references. | Changed to "Ch 21", "Ch 44". |
| 8 | 7 | §7.4 CIDR worked example | S3 | Pod IP exhaustion pointed to §42.9 (Services and kube-proxy), which does not match the topic. | Changed to "Ch 42". |
| 9 | 9 | §9.8 mobile push | S3 | "Chapter 52.4" mixes chapter and section notation. | Changed to §52.4. |
| 10 | 10 | §10.17 exercise 6 | S3 | "Ch 52.1" mixes chapter and section notation. | Changed to §52.1. |
| 11 | 4 vs 5 | Table 4.9, three rows | S2 | Modern values disagreed with Ch 5's derivations. Memory 1 MB sequential: 25–100 µs in Ch 4 vs 50–100 µs in Ch 5; 25 µs would need about 40 GB/s per thread, but Ch 5 uses about 10 GB/s. NVMe random 4 KB: 20–100 vs 50–100 µs. NVMe 1 MB sequential: 0.15–0.5 vs 0.15–0.3 ms. | Ch 4 rows aligned to Ch 5 (hardware-detail owner). The memory row is now labeled "One thread". |
| 12 | 5 vs 4 | Table 5.11, two SSD rows | S3 | Ch 5 says SSD rows are "Not in 2009 list", while Ch 4 shows classic SSD values (150 µs and 1 ms) from the later, widely circulated version of the list. | Ch 5 cells now read "Not in 2009 list (150 µs / 1 ms in later versions)". |
| 13 | 2 vs 4/7 | Table 2.17 row 1; §2.3 (L155) | S3 | Datacenter RTT given as "~0.5 ms". Ch 4 (summary) and Ch 7 (§7.7 RTO example) use 0.1–0.5 ms. | Changed to "~0.1–0.5 ms" in both places. |
| 14 | 8 vs 10 | §8.11 password code and "What to notice" | S2 | The Ch 8 example used scrypt N = 2¹⁵ (32 MiB). That is below the OWASP minimum N = 2¹⁷ that Ch 10 Table 10.8 states and uses. The "~100 ms" cost also disagreed with Ch 10's measured ~0.4 s at N = 2¹⁷. | Code changed to N = 2¹⁷, `maxmem` 256 MiB, comment "~128 MiB". Text now cites Table 10.8 and "a few hundred milliseconds" (re-measured: 0.43 s). Code re-run and passes. `code/ch08/listing-13-s8_11.py` regenerated. Open verification item updated. |
| 15 | 8 vs 10 | §8.11 citation; Reference 18; open items | S3 | Ch 8 cited NIST SP 800-63B (2017), while Ch 10 cites SP 800-63B-4 (2025) for the same guidance. | Ch 8 inline citation, reference entry and open item aligned with Ch 10's reference. |
| 16 | 7 / 10 | §7.10.3; Figure 10.2 "Reading the diagram" | S3 | Overlapping TLS/PKI material (§7.10 owns round trips, §10.4–10.5 own the cryptography and PKI) had no cross-reference from Ch 7 to §10.5, or from Ch 10's handshake to §7.10. | Added "PKI design … is covered in §10.5" to §7.10.3. Added "(round-trip costs and 0-RTT resumption are covered in §7.10)" to Ch 10. |
| 17 | 7 / 8 | §7.18.1 step 7; §8.5.1 | S3 | Two end-to-end "type a URL" walkthroughs (network view and server view) with no reference to each other. | §7.18 now cites §8.5. §8.5.1 now says §7.18 covers the packet-level view. |
| 18 | 2, 3, 4, 5, 6, 7, 8, 9, 10 | Prose (12 places) | S3 | British spellings: theatre, catalogued, acknowledgement(s) ×2, signalled, programme ×2, colour, analogue ×2, travelled, cancelled (prose). | Changed to the American forms. The cited title "The C4 model for visualising…" and the JSON value `"cancelled"` were left unchanged. |
| 19 | 10 | §10.3 asset list | S3 | "database master credentials": legacy term that `terminology.md` asks authors to avoid. | Changed to "database administrator credentials". |
| 20 | 3 | §3.5 and §3.6 (L579, L590) | S3 | Readers are pointed to "§9 / §6 of the style guide", an internal project document that is not part of the book. | **Deferred.** Should point to the front-matter "Notation, units and conventions" once it is written. |
| 21 | 4, 7, 9 | Open verification items | S3 | Items say runnable code "should be copied to `code/chNN/`". This is stale: `build/extract_code.py` now does it automatically. | **Deferred** (owner chapters' end matter). |
| 22 | 7 | §7.10.3 | S3 | "Maximum lifetime of 398 days as of 2025" is accurate for 2025 but probably out of date for a 2026 book (CA/B Forum SC-081 schedule). Ch 10 already lists the schedule as an open item. | **Deferred** until the schedule is verified from the primary source. |
| 23 | 5 | Table 5.11, "Dean 2009" column | S3 | Different versions of Dean's 2009 talk give 20 ms or 30 ms for "read 1 MB sequentially from disk". The table already says that versions differ. | **Deferred** (verify against the LADIS 2009 slides). |
| 24 | 1 vs 4 | Table 1.9 vs Table 4.7 | — | The nines table appears twice. The values are identical and verified, and Ch 1 cross-references §4.14. | No action (an introductory subset is acceptable). |
| 25 | 7, 8, 5 | Ownership rows of 04 §4.5 | — | §7.11 WebSockets is 319 words with a deferral to Ch 9. §8.11 password storage is about 150 words plus a short code block, with a cross-reference to §10.6. Table 5.11 cross-references §4.17. | No action. Ownership is respected and no non-owner duplication is over about 400 words. |

**Counts:** S1 = 0 · S2 = 8 (all fixed) · S3 = 15 (11 fixed, 4 deferred) · 2 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. Little's Law: thread pool (Ch 4 §4.11, 250 RPS × 80 ms = 20); connection pool (Ch 4: 6 / 0.2 / 600 connections); Ch 6 thread sizing (200 threads, 224 by the Goetz formula); Ch 7 database pool (10 / 50); Ch 2 orders in flight (27.8 × 900 ≈ 25,000).
2. The M/M/1 table (Table 4.5) at all six utilizations, including p99 = W·ln 100.
3. Erlang C: M/M/2 example (P_wait 0.711, W 55.6 ms) and pool sizing c = 25/30/35 (20.9% / 2.5% / 0.16% wait; 83.4 / 80.2 ms).
4. Amdahl, Gustafson and USL comparison table (eight rows) and N* = 30.8.
5. Availability in series: Ch 1 (99.89%, 99.79%), Ch 2 (99.70% → 130 min; 99.80% → 86 min), Ch 4 (99.84% → 14.0 h/yr).
6. Parallel and k-of-n availability (0.9999; 0.999702; system 0.999502 → 4.4 h/yr); 0.999¹⁰ = 99.0%.
7. Nines downtime tables (Tables 1.9 and 4.7, including the week and six-nines columns).
8. Binomial spare-server example (0.3677 / 0.3681 / 0.1840 / 8.0% → 29 days/yr) and 1 − 0.999¹⁰⁰⁰ = 0.632.
9. Fan-out tail amplification (0.99¹⁰⁰ = 0.366; 0.99^(1/100); 0.99⁵⁰ = 0.605).
10. HDD access time: 7,200 RPM → 4.17 ms rotation, 12.69 ms access, 79 IOPS, ~620× sequential/random gap; 5,400 RPM answer of 64 IOPS.
11. Ch 5 "read 1 GB" table (DRAM, NVMe, SATA, HDD, network, random 64 B / 4 KiB / HDD ≈ 51.6 min).
12. Ch 5 AMAT (1.62 vs 16.24 ns) and memory-level parallelism (307.2 GB/s × 110 ns = 528 lines).
13. Ch 6 effective access time with page faults (110 ns; p < 10⁻⁶ for HDD) and TLB reach (6 MiB vs 3 GiB).
14. Fiber propagation: NY–London 55.7 ms floor and 37.2 ms vacuum; CA–NL 88 ms floor.
15. BDP: 10 Gbps × 80 ms = 100 MB; 64 KiB window → 6.55 Mbps.
16. Mathis formula (17.8 Mbps at p = 10⁻⁴; 178 Mbps at 10⁻⁶; p ≈ 3.2 × 10⁻¹⁰ for 10 Gbps).
17. TCP slow start for 1 MB (685 segments, 7 RTTs + 2 handshake RTTs = 720 ms).
18. RTO computation per RFC 6298 (175 ms → 1 s RFC / 200 ms Linux).
19. TIME_WAIT ephemeral-port exhaustion (28,232 ports / 60 s ≈ 470/s).
20. Round trips before first byte (Table 7.15): TLS 1.2 = 2 RTT, TLS 1.3 = 1 RTT, QUIC = 1 RTT (0 on resumption), consistent with Ch 8 §8.5 (eq. and Table 8.3), Ch 8 exercises and Ch 10 Figure 10.2.
21. Ch 8 cold vs warm request (163 ms vs 53 ms).
22. HTTP/2 head-of-line statements in Ch 7, 8 and 9: consistent (HTTP-layer HOL removed, TCP-layer HOL remains, QUIC removes it).
23. WebSocket `Sec-WebSocket-Accept` for the RFC 6455 sample key = `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=` (Ch 7 Figure 7.9 and Ch 9 §9.6.2); 2–14 byte frame headers.
24. Ch 9 short-polling cost table (requests/s, e^(−λT) empty fraction, delay, header bandwidth) and the 99.2% / ~1,700 useful requests per second example.
25. Ch 9 gateway sizing (800k memory limit, 500k blast limit, 36 servers, 278k connections per server, 11.1 / 16.7 GB) and reconnect storm (7,900 vs 265 per gateway).
26. Ch 9 per-connection memory table totals (14–94 KB, 40 KB), consistent with Ch 6's ~20 KB socket and TLS assumption.
27. Brute-force and entropy (Ch 10): 95⁸ = 6.63 × 10¹⁵, 52.6 bits, 9 h vs 1,050 years, 95¹² → 8.6 × 10¹⁰ years.
28. AES-GCM random-nonce bound (2⁻³³ ≈ 1.2 × 10⁻¹⁰ at 2³² messages; ≈ 1 day at 50k messages/s).
29. 64-bit truncated-hash birthday example (P approximation 2.7, so a collision is near certain; 4 × 10⁻⁵⁸ at 256 bits) and 128-bit security ≈ 10¹³ years.
30. Password-hash capacity planning (200 logins/s × 0.1 s = 20 cores; 1.3 GiB); scrypt memory 128·N·r; OWASP and RFC 9106 parameters.
31. Protobuf varint hand-encoding (1337 → `b9 0a`; 33 vs 81 bytes).
32. CIDR answers (172.20.14.200/22 → .12.0–.15.255, 1,022 hosts; longest-prefix match /14).
33. Ch 2 QuickBite capacity estimate (orders, browse RPS, storage 5.5 TB, 390 GB locations, 1.12 Gbps, 14 nodes).
34. Ch 1 PhotoShare launch-day estimate (0.58 / 1.7 RPS).
35. Durability replica comparison (2.2 × 10⁻⁶ vs 3.6 × 10⁻¹⁰ ≈ 6,000×) and 2-of-3 quorum latency (0.9997).
36. Ch 4 short answers (2⁴⁰, log₅₀₀ 10⁹ = 3.33, 50 TB over 25 Gbps = 4.4 h, 0.995²⁰, 0.9995⁵ → 108 min).
37. Cross-chapter Table/Figure references: all resolve; the only cross-chapter one is Ch 8 → Table 10.8, which was added in this review.
38. Terminology: there is no master/slave usage; QPS is introduced once as a synonym (Ch 1); "message bus" does not appear; "uptime" appears only inside the availability formula.

## Remaining risks

- **Dated hardware and network numbers** still appear in five places: Ch 2 Table 2.17, Ch 4 Table 4.9, Ch 5 Tables 5.3/5.5/5.6/5.10/5.11, Ch 7 Table 7.15 and Ch 8 Table 8.3. They are now consistent with each other, but all of them defer to an Appendix F that does not exist yet. When Appendix F is written, it should take Ch 4 Table 4.9 (as amended) as its source, and the other tables should be re-checked against it.
- **Ch 11–93 references** were checked only against section titles in the master TOC. If later authors renumber sections, about 150 forward references from Ch 1–10 will break silently. A script check in `qa_check.py` (§-references resolved against headings and the TOC) would catch this; it is not implemented here.
- **Time-sensitive security facts** are tracked as open items but not resolved: the certificate-lifetime schedule (#22), the NIST 800-63B-4 wording, and the OWASP parameters "as of 2026".
- **Code drift:** `code/ch08/listing-13` was regenerated by hand for this one change. If other uncommitted chapter edits changed code blocks, run `build/extract_code.py` before committing.
- Internal same-chapter references were all checked for existence and scanned for topic fit only against the target's heading title. Mismatches that fall within a subsection (right section, wrong paragraph) would not be caught.
