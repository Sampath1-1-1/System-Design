# Wave 6 Integration Review — Chapters 39–43

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-10-31 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* Part VIII, chapters 39–43 (reliability, observability, cloud computing, containers and Kubernetes, deployment and infrastructure), and their interfaces with chapters 1–38.

**Method.** This was targeted grep and reading, not a full read-through. It follows the wave 5 method.

1. **Ownership.** A scratch script split every chapter 39–43 at its `##`–`####` headings and counted words and keyword hits per block for these topics:
   - availability, reliability and durability arithmetic (MTBF, MTTR, series/parallel, nines)
   - N+k and zone sizing (N+1, N+2, $Z/(Z-f)$, static stability)
   - timeouts, retries, backoff, circuit breakers, load shedding, bulkheads
   - SLOs, error budgets and burn rates
   - tracing (spans, context propagation, sampling)
   - USE, RED and golden signals; profiling
   - HPA and target tracking; rolling-update parameters
   - etcd and Raft; service mesh and sidecars; Firecracker, Lambda and serverless
   - object and block storage; KMS and secrets

   Every non-owner block with four or more hits was read against the brief's ownership list and 04 §4.5:
   - availability, reliability and durability math → §4.14–§4.16 (Ch 39 applies)
   - N+k and zone sizing → §18.11 (Ch 39 and 41 cross-reference)
   - timeouts, retries, breakers, shedding → Ch 22 (Ch 39 cross-references)
   - SLOs and burn-rate alerts → §39.6–§39.7; Prometheus rules in §40.10
   - distributed tracing → Ch 40 (intro §34.9)
   - USE/RED/golden signals → §23.3; profiling → §23.4 (Ch 40 cross-references)
   - HPA formula → §18.8 (Ch 42 cross-references)
   - rolling-update formula → §42.8.1 (Ch 43 cross-references)
   - etcd → §26.9; service mesh → §34.10
   - Firecracker and serverless → §33.9 and Ch 48 (preview)
   - object and block storage → Ch 15; KMS and secrets → Ch 10
2. **Recurring facts.** Facts that appear in more than one chapter were extracted and compared:
   - QuickBite figures in Ch 2, 18, 39, 40, 42 and 43 (SLOs, fleet sizes, order rates, latency thresholds)
   - SLO and burn-rate parameters in §39.7.3 and §40.10 (thresholds, windows, budget fractions)
   - Kubernetes version and feature claims in Ch 18, 42 and 43
   - Firecracker figures in Ch 33, 41 and 42
   - cloud prices in Ch 12, 15, 18, 21, 33, 40, 41 and 42
   - DORA definitions (Ch 1, 33, 43)
   - Knight Capital (Ch 1, 43); Google Cloud 12 June 2025 (Ch 39); Aurora quorums (Ch 41)
   - security groups vs NACLs (Ch 7, 41); liveness vs readiness (Ch 19, 42)
3. **Cross-references.** All 291 `§N.M[.K]` references in Ch 39–43 were resolved by script against the actual headings: 111 intra-chapter, 180 cross-chapter, none unresolved. Every cross-chapter reference was then read for topic fit. The 64 chapter-level "Chapter N"/"Ch N" references in Ch 39–43 were checked (targets in Ch 44+ against `01-master-toc.md`). All 44 `§` references and 20 chapter-level references from Ch 1–38 into Ch 39–43 were resolved and read the same way. Every Figure and Table number cited in Ch 39–43 has a matching caption, and the captions in each chapter run in sequence.
4. **Numbers.** About 150 numbers in 40 worked examples and five checkpoint blocks were recomputed with `python3` (list below). All nine Python listings in Ch 39–43 were extracted and run, and their output was compared with the chapters' `text` output blocks and inline output comments.
5. **Concepts.** These statements were checked:
   - percentiles cannot be averaged
   - liveness vs readiness (and startup) probe semantics
   - requests vs limits, CFS throttling and the three QoS classes
   - security groups stateful vs NACLs stateless
   - expand–contract ordering
   - the two-window burn-rate logic
6. **Terminology.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 43 chapters.
- `python3 build/build.py --chapters 39-43 --name qa --formats html`: 559 diagrams across 43 chapters, 0 errors. The rendered HTML was checked for stray inline maths from unescaped `$` (none; the Knight Capital "$460 million" renders as text).
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored with `git checkout`.
- The only modified files are chapters 06, 39, 40, 41, 42 and 43.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 40 vs 2, 39 | §40.11.3 "What the incident cost" | S2 | **Wrong rate and wrong budget base.** "Checkout serves 300 orders/s" is 5× QuickBite's design peak of 60 orders/s (§2.11; §2.10 puts the WAL limit at about 500 orders/s). The monthly budget was then computed as that peak rate over the whole month: $300 \times 2{,}592{,}000 \times 0.001 = 777{,}600$ allowed failures. QuickBite's 500,000 orders/day (Ch 2, §39.3.2, Table 39.4) give 15 million orders and 15,000 allowed failures at 99.9%. As a result "4.4% of the budget" understated the cost about tenfold. | Rate set to 60 orders/s (§2.11) with 15 million orders per month (§39.3.2). Recomputed: 75,600 requests; 6,728 excess failures; $75{,}600 \times 0.09 / 15{,}000 = 45\%$ of the budget. A sentence now reconciles this with the time-based figure ($21 \times 0.09 = 1.89$ of 43.2 min = 4.4%): peak traffic is about 10.4× the average, so a peak incident costs about ten times its share of the clock (§18.11.3). Step 5 is now $60 \times 2{,}400 \times 0.089 = 12{,}816$, and the interpretation reads "45% … and thousands of orders". |
| 2 | 40 vs 2, 39 | §40.10.2–§40.11.3, checkpoint Q14 | S2 | **Checkout SLO.** Ch 40 uses 99.9% for checkout throughout: the 14.4× example, the Prometheus rule `14.4 * 0.001`, the incident and Q14. Ch 2 ("checkout at 99.95%", N1) and Ch 39 (Table 39.4, place-order 99.95%) use 99.95%. Converting Ch 40 to 99.95% would also change its 0.1% baseline (burn rate 2) and the timeline in Figure 40.14. | The 14.4× worked example now says that 99.9% is a round figure used in all of the chapter's alerting examples. It adds that at QuickBite's negotiated 99.95% (Table 39.4) every error-ratio threshold halves while the burn rates stay the same. The other numbers are unchanged. |
| 3 | 40 vs 39 | §40.5.2 worked example step 3 and the listing comment | S3 | "Custom buckets … around the 300 ms SLO" conflicts with the place-order latency SLO of 800 ms in Table 39.4. The listing's `SLO_BUCKETS` already contain both 0.3 and 0.8. | Now reads "around the latency thresholds (a 300 ms target, and the 800 ms place-order SLO of Table 39.4)". The code comment now reads "around 300 ms and 800 ms latency thresholds" (comment only; the output is unchanged and was re-verified). |
| 4 | 40 vs 39 | §40.10.3 alert rule, "What to notice" | S3 | The rule has `for: 2m`, which delays paging beyond the detection times in Table 39.6 (52 s for a total outage). §40.11.3 accounts for it, but neither table nor rule says so. The thresholds (14.4 × 0.001), windows (1 h / 5 min), budget fraction (2%) and period (30 days) agree exactly with §39.7.3. | Added a bullet: "`for: 2m` adds up to two minutes to the detection times of Table 39.6 (52 s … becomes about 3 minutes); the short window already filters blips, so keep `for` short or omit it." |
| 5 | 43 | §43.3.3 "Is deploying more often riskier?" | S3 | $60 \times 30/7 \times 0.1 = 25.71$ min of 43.2 is 59.5%, printed as "59%"; Team A's 95% is correct. The same example has a typo: "2 changes per deploy,, CFR 5%". | "60%"; double comma removed. |
| 6 | 43 | §43.6.3 "Against the error budget" | S3 | The monthly volume $2{,}000 \times 2{,}592{,}000$ treats the *midday* rate as the monthly average, the same pattern as #1 but smaller in effect. | Added "(taking the midday rate as the monthly average, which understates both shares below)". The 13.5% and 0.068% are unchanged. |
| 7 | 6 → 43 | §6 IPC list, Signals bullet | S3 | "services must handle `SIGTERM` to drain gracefully (§43.4)". §43.4 (Rolling deployments) does not cover termination; §42.7.4 (Graceful termination) covers `preStop`, `SIGTERM`, grace period and draining. | Changed to (§42.7.4). |
| 8 | 42 vs 18 | §42.13.4 "QuickBite's production cluster", implication | S3 | "Surviving the loss of one of three zones requires about 50% more nodes (Chapter 44 discusses zone and region capacity)". Zone-level sizing ($Z/(Z-f)$, static stability) is owned by §18.11.2; Ch 44 is about regions. | Now reads "(§18.11.2 derives zone-level sizing; Chapter 44 extends it to regions)". |
| 9 | 41 vs 42 | §41.8.4 | S3 | "Containers … start in milliseconds" conflicts with Table 42.3 ("~0.1–1 s") and Table 42.3's ~125 ms microVM boot. Read literally, containers would boot faster than Firecracker. | Now reads "start in well under a second". |
| 10 | 39, 42 | §39.12.1 Figure 39.13 description; §42.6.1 Borg callout | S3 | **Terminology.** "acknowledgement" (British; Ch 1–38 use "acknowledgment"). "a Paxos-replicated master" (`terminology.md` avoids master/slave; Verma et al. call the component the Borgmaster). | "acknowledgment"; "a Paxos-replicated controller, the Borgmaster (five replicas per cell)". |
| 11 | 42 | §42.3.3, §42.7.2, §42.9.3, §42.12 | S3 | **Kubernetes versions.** Native sidecars and nftables kube-proxy stable in 1.33, in-place pod resize stable and IPVS deprecated in 1.35, dockershim removed in 1.24, Go 1.25 cgroup-aware `GOMAXPROCS`. All are consistent within Ch 42, and Ch 18 and Ch 43 make no conflicting version claims. Not re-verified against release notes in this review. | **Deferred.** Already an open item in §42.23. |
| 12 | 39 | §39.12.2 Google Cloud 12 June 2025 callout | S3 | The description matches the incident report as recalled: Service Control quota-policy code path from 29 May with no feature flag; blank-field policy replicated globally by Spanner; null pointer; red button; us-central1 herd effect without randomized backoff; fail-open remediation. This is the only chapter that tells the story. Exact timings were not re-fetched. | **Deferred.** Already an open item in §39.19. |
| 13 | 41 | §41.8.3 citation `[AWS Nitro System docs; AWS Nitro security whitepaper 2022]` | S3 | The inline year (2022) does not appear in reference 8 (*The Security Design of the AWS Nitro System*), which has no date, so the author–year key does not match its entry. | **Deferred.** The publication year was not verified, so no date was added. |
| 14 | TOC vs 39–43 | `01-master-toc.md` Part VIII | S3 | Drafted titles are reworded or extended. Examples: 39.10 "Multi-region architecture (introduction)", 41.4 "Regions, availability zones, edge locations and the shared responsibility model", 41.6 "Google Cloud core services", 42.8 "Workload controllers", 42.9 "Networking: CNI and Services". | **Deferred** (TOC owner). The section numbers 39.3–43.13 match the TOC exactly, so no reference breaks. |
| 15 | 39–43 | Ownership measurement | — | Non-owner passages measured:<br>• **Availability math:** Ch 39 states (opening, §39.4.1) that §4.14–§4.16 are not re-derived. Its formulas are new applications: beta-factor common cause, fallback $A_{\text{eff}}$, composite SLO citing §4.14.2, DR expected cost and restore duration. §41.4.1's zone formula (≈ 460 words with its example) applies §4.14 to zones and cites it.<br>• **N+k:** §39.4.1 lists the schemes in five bullets and defers the arithmetic to §18.11.2 ("We do not repeat that arithmetic here"). Figure 39.2's "three groups of six" matches §18.11.2's 18 nodes.<br>• **Timeouts and retries:** only one-line mentions, citing §22.9, §22.11–§22.15.<br>• **SLO and burn rate:** deep in §39.6–§39.7. §40.10.2 (327 words) is a short recap citing §39.7.3 twice, and §40.10.3 adds only the Prometheus/Alertmanager rules.<br>• **Tracing:** owned by §40.6 (1,422 words in §40.6.3), which builds on §34.9 (cited twice). The W3C `traceparent` byte layout and sampling maths appear only in Ch 40.<br>• **USE/RED:** §40.9 uses the terms in dashboard guidance and cites §23.3.<br>• **Profiling:** §40.12 opens "Section 23.4 explained…" and covers only continuous/eBPF profiling.<br>• **HPA:** §42.12 gives the formula in one line and cites §18.8.3–§18.8.4.<br>• **Rolling update:** §43.4 (253 words) cites §42.8.1 for the formula and adds only the release-risk reading.<br>• **etcd:** one bullet in §42.6.2 citing §26.9 and §26.9.2.<br>• **Mesh:** §42.7.2, §42.9.3 and Ch 43 cite §34.10.<br>• **Firecracker:** ≈ 120 words in §41.8.4 and one table column in §42.3.4, both citing Ch 47/48; §42.16 cites §33.9 and Ch 48.<br>• **Storage:** §41.9 opens "Chapter 15 explains…" and gives only cloud names and classes.<br>• **KMS and secrets:** §41.12.3 (83 words) and §42.11 cite §10.8/§10.9.2. | No action beyond #8. No non-owner passage over about 400 words duplicates owner content. |
| 16 | 2, 18, 39, 42, 43 | QuickBite figures | — | Consistent, apart from #1–#3:<br>• Place order 99.95% and browse 99.9% per 30 days (Ch 2 N1, §39 opening, Table 39.4); 500,000 orders/day (Ch 2, §39.3.2, §39.6.3, Table 39.4).<br>• N+2 = 14 and zone-safe = 18 API nodes (§18.11.2, §39.4.1, Figure 39.2).<br>• The ordering service's 10 pods at 550 RPS and 4,800 RPS evening peak (§42.8.1) and 2,000 RPS midday (§43.6.3) are request rates across all endpoints, not order rates, and are labeled as such.<br>• §43.4's "four 45-second waves, about three minutes" matches §42.8.1's $\lceil 10/3 \rceil \times 45 = 180$ s. | No action. |
| 17 | 39, 40 | Burn-rate parameters | — | Identical in §39.7.3 (formula, Table 39.6, Figure 39.8, listing) and §40.10 (example, rule):<br>• 14.4× / 6× / 1×<br>• long windows 1 h / 6 h / 3 d; short windows 5 min / 30 min / 6 h<br>• budget fractions 2% / 5% / 10% of a 30-day (720 h) period<br>• error ratios 1.44% / 0.6% / 0.1% at 99.9%<br><br>§40.10.2 uses $\beta$ and $T$ where §39.7.3 uses $b$ and $P$. Both are defined locally. | No action (see #4). |
| 18 | 1, 33, 43 | DORA | — | §43.3.3 defines the four metrics with the 2023 rename ("failed deployment recovery time", formerly time to restore service). Ch 1 Table 1.8 ("change-failure rate", deploy frequency) and Ch 33 Q3 use the names only, and they agree. | No action. |
| 19 | 1, 43 | Knight Capital | — | Both say: 2012 (Ch 1: 1 August), one of eight servers not updated, a repurposed flag activating dead code ("Power Peg" in Ch 43), about 45 minutes, more than \$460 million, [SEC 2013]. Both carry open items for the SEC wording. | No action. |
| 20 | 41 | Aurora | — | $V = 6$, $V_w = 4$, $V_r = 3$; both quorum conditions; survives a zone loss for writes and zone + 1 for reads. No other chapter states Aurora quorums. | No action. |
| 21 | 33, 41, 42 | Firecracker | — | Ch 41 and Ch 42 agree with Agache et al. 2020 as cited: ~125 ms boot, < 5 MiB overhead, 150 microVMs/s/host (Ch 41). Ch 33 and 21 only name Firecracker and defer to Ch 48. Lambda's 15-minute limit (Ch 41) matches Ch 33. | No action. |
| 22 | 12, 15, 18, 21, 33, 40, 41, 42 | Cloud prices | — | All are labeled illustrative and "as of 2026", and they do not conflict:<br>• S3 Standard \$0.023/GB-month (Ch 15, 40, 41)<br>• internet egress \$0.09 → \$0.085 → \$0.07/GB tiers (Ch 41) and "on the order of \$0.05/GB" at PB tiers (Ch 21)<br>• cross-zone \$0.01/GB per direction, NAT \$0.045/h + \$0.045/GB, IPv4 \$0.005/h (Ch 41)<br>• Lambda \$0.0000166667/GB-s, \$0.20/M (Ch 33)<br>• 16 vCPU node \$0.77/h, control plane \$0.10/h (Ch 42) | No action. |
| 23 | 7, 19, 22, 41, 42, 43 | Concepts | — | All correct:<br>• **Percentiles:** cannot be averaged (§40.5.2 listing: mean of p99s 453 ms vs fleet 585 ms; §39.6.3 counts).<br>• **Probes:** liveness restarts, readiness removes from endpoints with no restart, startup gates both; no dependencies in liveness (Table 42.5, §19.5.2; Ch 19 agrees).<br>• **Scheduling:** places by requests; limits are enforced by the kernel; CPU utilization for the HPA is relative to the request.<br>• **QoS:** Guaranteed −997, Burstable 2–999, BestEffort 1,000 and evicted first.<br>• **Security groups:** stateful and allow-only; NACLs stateless and ordered (Ch 7 §7.14 and Ch 41 agree).<br>• **Expand–contract:** expand → dual-write → backfill → switch reads → stop old writes → contract, with rollback safety stated at each step and the Gantt chart in the same order.<br>• **Two windows:** the short window speeds reset, the long window gives significance. | No action. |
| 24 | 39–43 | Terminology | — | No QPS, "message bus", "slave" or "micro-app".<br>• **Uptime:** appears only in quoted product terms (AWS "monthly uptime percentage", Google's "user-uptime").<br>• **Expiry:** appears only as flag expiry dates (lifecycle, not TTL).<br>• **Box:** appears only for diagram boxes or checklists. | No action beyond #10. |

**Counts:** S1 = 0 · S2 = 2 (fixed) · S3 = 12 (8 fixed, 4 deferred) · 10 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. **Ch 39 §39.3.2** time- vs request-based availability:
   - $1 - 130/43{,}200 = 99.699\%$
   - 3,333 + 15,000 failed, $99.878\%$
   - shares 31% vs 18%
2. **Ch 39 §39.4.2** beta-factor: $10^{-6}$ (2.6 s/30 d); $1.008 \times 10^{-4}$ (4.4 min); ≈ 100× worse.
3. **Ch 39 §39.5** fallback: $A_{\text{eff}} = 0.9999995$; $Q = 0.9985$.
4. **Ch 39 §39.6.3** latency SLI: 0.99157; 84% of the half-window allowance; 42% of the full window.
5. **Ch 39 §39.6.5** SLA vs SLO: 43.2 vs 20.2 min; credits \$4,000 / \$10,000.
6. **Ch 39 §39.6.6** composite SLO:
   - 0.99890 (47.5 min/30 d)
   - 0.99940
   - 0.999499 → 0.99950
   - 0.99960 (≈ 20% margin)
7. **Ch 39 §39.7.1 and Table 39.5** budgets:
   - 43.2 / 40.3 / 21.6 / 20.2 min
   - 7,000 failed orders
   - 13.5 min = 67%
   - every cell of Table 39.5
8. **Ch 39 §39.7.3** burn rates:
   - 14.4 / 6 / 1; 1.44% / 0.6% / 0.1%
   - exhaustion 50 / 120 / 720 h; total outage 43.2 min
   - detection 0.864 min (52 s), 17.3 min at 5% (2.0% spent)
   - 28-day 13.44 / 5.6 / 0.93; 2.14%
   - Table 39.6 detection 52 s / 2.2 min / 4.3 min
9. **Ch 39 §39.8** DR expected cost: \$78k / \$48.5k / \$121.45k (printed 121.5) / ≈ \$350.1k; one event \$700k.
10. **Ch 39 §39.9.1** backups: 5.2 vs 8.2 TB (+58%); 7 vs 2 pieces.
11. **Ch 39 §39.9.3** restore:
    - 10,000 s = 2.78 h; 5,400 s = 1.5 h; 5.03 h
    - fixed: 0.5 h + 1.11 h → 2.36 h
12. **Ch 39 §39.11** chaos budget: 0.3 min = 1.5%; 0.02 min = 0.1%.
13. **Ch 40 §40.4.4** logs:
    - 9 MB/s, 777.6 GB/day (23.3 TB/month)
    - \$11,664 hot, 6,998 GB and \$161 cold
    - 1.3 lines (21.7%) = 168.5 GB/day, \$2,528, saving ≈ \$9,100
    - hot share 98.6%
    - $0.1^5 = 10^{-5}$
14. **Ch 40 §40.5.2** bucket error: 100%, 150%, 25%; native histogram $2^{0.125} = 1.0905$.
15. **Ch 40 §40.5.3** cardinality:
    - 48,000; 201,600 series; 806 MB
    - 3.5 million series = 14 GB
    - 24,000; 134,400; 538 MB
16. **Ch 40 §40.6.3** sampling:
    - 12.5 MB/s = 1.08 TB/day; 54 GB
    - $1 - 0.99^{20} = 18.2\%$, $1 - 0.95^{20} = 64.2\%$
    - $p_{\text{eff}} = 0.0219$ → 23.6 GB/day
    - buffer 375 MB
17. **Ch 40 §40.8.3** recording rule: $5.81 \times 10^9$ vs 432,000 samples (≈ 13,400×); 300 series.
18. **Ch 40 §40.10.2 / §40.11.3** paging:
    - $\beta = 14.4$; 2%; 50 h
    - $t = 9.03$ min + 2 min `for` = page at 19:51
    - incident: see #1 (75,600; 6,728; 45%; 4.4% time-based; 12,816; burn rate 90 → 8 h)
19. **Ch 41 §41.4.1** zones:
    - 0.9989 (9.6 h/yr); 0.9999 (53 min/yr)
    - over-provisioning 2.0× vs 1.5×
20. **Ch 41 §41.8.5** spot:
    - $\tau^* = 1.41$ h; overheads 0.035 + 0.040; $T_{\text{wall}} = 107.6$ h; \$75.30 (−62%)
    - sensitivity: 121.1 h (\$84.79), 116.3 h (\$81.43)
    - no checkpoints: 2,963 h, \$2,074
21. **Ch 41 §41.10.3** network bill:
    - \$7,800 egress, \$4,000 cross-zone, \$200 cross-region
    - NAT \$98.55 + \$1,800
    - ≈ \$13,900
22. **Ch 41 §41.11.2** Aurora:
    - $P_{\text{unavail}}(4) = 1.96 \times 10^{-5}$, $P_{\text{unavail}}(3) = 1.48 \times 10^{-7}$
    - 3-copy majority $2.98 \times 10^{-4}$ (15.2×)
23. **Ch 41 §41.13** commitments:
    - break-even 65% / 40% (15.6 / 9.6 h/day)
    - \$292 vs \$189.80
    - \$30.66 vs \$47.45 (−\$16.79); \$29.20
    - idle test environment 70%
24. **Ch 41 §41.13.3** Table 41.12: the listing reproduces every line (total \$2,035.88 / \$1,597.20). The database share is 31%, network lines 35%, and the saving 22%.
25. **Ch 42 §42.3.2** CFS throttling:
    - $Q = 200$ CPU-ms; $t_{\text{run}} = 25$ ms; throttled 75 ms; ≈ 85 ms latency
    - $k = 2$ → 0 ms
    - Q2: 25 / 75 ms
26. **Ch 42 §42.4.2** image pull: 11.7 s vs 0.33 s; 9 GB vs 270 MB.
27. **Ch 42 §42.8.1** rolling update:
    - defaults: $s = 3$, $u = 2$, $A_{\min} = 8$ (4,400 < 4,800 RPS), 90 s
    - surge-only: 10 / 13 pods, 5,500 RPS, 180 s
    - Figure 42.9 bounds 13 / 8
    - Q9: 15 / 25
28. **Ch 42 §42.13.4** pods per node and cluster:
    - 7.51 CPU / 26.85 GiB → 15 pods (CPU-bound); 11.85 GiB stranded (44%)
    - LeastAllocated 75/25; MostAllocated 25/75; 2/2/2 vs 4/2/0
    - cluster: 9.7 → 10 nodes vs 8.04 → 9; \$5,621 + \$73 = \$5,694; 30% real utilization
    - rightsized: 6.9 → 7 CPU, memory 9 → \$5,132 (−9.9%)
    - Q12: 7 pods, CPU-bound
29. **Ch 43 §43.3.3** DORA: 0.4 vs 2.0 failed deploys; 96 vs 60 min/week; 411 vs 257 min/month; 95% vs 60% (#5).
30. **Ch 43 §43.5.4** blue–green: \$3,288 (11%); canary \$82; Q6 \$2,466.
31. **Ch 43 §43.6.3** blast radius:
    - 351,000 vs 1,755 (**200×** = 20 × 10)
    - $5.18 \times 10^9$, $2.59 \times 10^6$ allowed; 13.5% vs 0.068%
    - 17,550 for a human-watched canary
    - Q7: 900
32. **Ch 43 §43.6.4** z-test:
    - SE $7.723 \times 10^{-4}$, **$z = 2.59$, p = 0.0048**
    - 104 errors → $z = 0.28$, p = 0.39
    - 2,000 per group → $z = 0.82$
    - Q8: $z = 2.64$, p = 0.004
33. **Ch 43 §43.6.4** sample size:
    - **19,945.3 → 19,946 per group** (with the rounded $z$ values; 19,945.3 with exact quantiles too)
    - 199 s / 997 s / 9,973 s
    - doubling ≈ 5,975 (≈ 6,000); 0.5% → 20% ≈ 47.2 (48); 20% relative ≈ 109,790 (≈ 110,000)
    - sample-limited $B \approx 50$
34. **Ch 43 §43.7.3** flags: $2^{12} = 4{,}096$ → 8,192 min (5.7 days); $2^4 = 16$ → 32 min.
35. **Ch 43 §43.12** change correlation: $1 - e^{-2.5} = 0.92$; $1 - e^{-0.0625} = 0.061$.
36. **Ch 43 §43.13.2** backfill: $3 \times 10^8 / 20{,}000 = 15{,}000$ s ≈ 4.2 h.
37. **Checkpoint answers.** All numeric answers in §39.14, §40.14, §41.16, §42.18 and §43.15 were recomputed, for example:
    - §39 Q2 $1.0 \times 10^{-4}$; Q9 0.99840; Q12 1.86 h
    - §40 Q3 276 GB/day; Q7 1,500 / 21,000 series; Q9 18.3%; Q10 2.49%
    - §41 Q7 1,225 peerings; Q13 3.2 h
38. **Listings.** All nine Python listings ran (exit 0):
    - **Match their `text` output verbatim:** §39.7.3 burn-rate calculator; §40.5.2 histogram quantile; §40.6.3 sampling simulation; §41.12.2 policy evaluator; §42.6.3 toy reconcilers; §43.6.4 canary judge.
    - **§41.13.3 cost model:** its printed table matches Table 41.12.
    - **§43.6.4 canary tests:** the test file passes with the judge saved as `canary.py` ("false-positive rate 0.015, power 0.843").
    - **§43.7.2 flag bucketing:** prints the inline-commented `5034 25212 True`.
39. **Cross-references.**
    - **Ch 39–43:** all 291 `§` references resolve to sections on the stated topic, apart from #7 and #8.
    - **Inbound:** all 44 `§` references and 20 chapter-level references from Ch 1–38 into Ch 39–43 resolve on topic (apart from #7). Examples:
      - §39.3–§39.12 (Ch 1, 2, 3, 4, 8, 10, 13, 14)
      - §40.6–§40.7 (Ch 23, 30, 32, 33, 34)
      - §42.3/§42.7/§42.9–§42.13 (Ch 1, 6, 9, 10, 19, 34)
      - §43.3–§43.13 (Ch 1, 3, 33, 34)
    - **Ch 44+:** references into Ch 44+ match the TOC topics:
      - Ch 44 multi-region
      - Ch 46 scheduling (Borg)
      - Ch 47 isolation levels
      - Ch 48 Lambda/Firecracker
      - Ch 50 supply chain
      - Ch 51 FinOps
      - Ch 57 A/B testing statistics

## Remaining risks

- **QuickBite's alerting SLO.** Ch 40 keeps 99.9% for checkout as an explicitly labeled teaching figure (#2), while the book's negotiated target is 99.95%. A later edit that quotes Ch 40's thresholds (1.44%, `14.4 * 0.001`) as QuickBite's real alert levels would be wrong by 2×. Case studies (Ch 52–56) should take QuickBite's targets from Table 39.4.
- **Peak-rate-as-average.** Two examples (#1, #6) computed monthly request budgets from a peak or midday rate. Future worked examples should take monthly volume from the 500,000 orders/day assumption (§2.11, §39.3.2), or say so when they approximate.
- **Perishable product facts in Part VIII.** They include:
  - Kubernetes feature status (1.33/1.35)
  - Go 1.25 `GOMAXPROCS`
  - Cluster Autoscaler defaults
  - Karpenter and KEDA behavior
  - AWS/GCP/Azure prices and service names (Aurora DSQL, DynamoDB MRSC, Cloud Run functions)
  - DORA 2024 cluster thresholds
  - OpenTelemetry signal maturity (Table 40.9)
  - Prometheus native-histogram schema
  - the Google Cloud June 2025 timings

  All carry "as of 2026" tags or open verification items, but none was re-verified against primary sources in this review.
- **Overlapping pairs to watch.**
  - SLO/burn rate (§39.7.3 / §40.10.2)
  - rolling update (§42.8.1 / §43.4)
  - zone sizing (§18.11.2 / §39.4.1 / §41.4.1 / §42.13.4)
  - tracing (§34.9 / §40.6)
  - CFS throttling (§6.5 / §42.3.2)
  - Firecracker (§41.8.4 / §42.3.4 / Ch 47–48)

  Each is now cross-linked; Ch 44 (multi-region), Ch 47 (isolation) and Ch 48 (serverless) should cite these rather than re-derive them.
- **Reference drift.** About 400 references were checked by a scratch script. `qa_check.py` still has no `§`-reference resolver. Part VIII adds 18 chapter-level references into Ch 44–57 that depend on TOC numbering not yet drafted.
