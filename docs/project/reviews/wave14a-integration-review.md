# Wave 14a Integration Review — Chapters 81–83 (Case Studies VI–VIII: Recommendation, Search and Ads; Risk and Trust; Marketplace Forecasting and Optimization)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-11 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied across three case-study chapters:

- 81 Case Studies VI: Recommendation, Search and Ads (7 cases, §81.4–§81.10)
- 82 Case Studies VII: Risk and Trust (4 cases, §82.4–§82.7)
- 83 Case Studies VIII: Marketplace Forecasting and Optimization (3 cases, §83.4–§83.6)

The review also covered their interfaces with Ch 1–80. The reference standard is `case-study-brief.md` (16 subsections per case, ≥ 3 figures per case, failure-scenario tables, application not re-teaching, and the Book II additions), `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md`, and `04-agent-allocation.md` §4.5. A second reviewer handled Ch 84–86 in parallel (wave 14b). Those files were not edited here. The ownership split for this wave:

| Owner | Topics the cases apply |
|---|---|
| Book I | Erlang C (§4.10.4); Little's Law (§4.11); inverted indexes and BM25 (§16.3–§16.5); hybrid search (§16.11); H3 (§17.9.5); HyperLogLog and Count-Min (§17.5–§17.6); rate limiting, deadlines, breakers and idempotency (§22.3–§22.15); stream processing and Flink (§29.8–§29.9); Kafka (Chapter 31); kill switches (§43.7.2); privacy engineering (§50.8–§50.10); the YouTube, Netflix, Instagram, Uber, Maps, Amazon, payments and search platform cases (§53.6, §53.7.8, §54.4, §54.5, §55.4–§55.9, §56.4–§56.5) |
| Parts XI–XIII | Classification, regression and ranking metrics, pinball loss, A/B statistics (§57.10–§57.14); problem framing and asymmetric costs (§59.4); fleet sizing, latency budgets, fallbacks and cascades (§60.10–§60.13); **QuickBite ETA (§60.15)**; feature stores, point-in-time joins and skew (Chapter 62); label delay, downsampling and label noise (§63.4, §63.10–§63.11) |
| Ch 66–75 | Serving and safe deployment (§66.6–§66.14); quantization (§67.4); **recommender funnel, two-tower, MMoE fusion, calibration, IPS, interleaving, cold start (Chapter 68)**; registry and model risk (§69.8, §69.11.2); **monitoring and drift, including QuickBite fraud monitoring (§70.8)**; **fairness, explanations and regulation (Chapter 71)**; ANN and PQ (§74.9–§74.12); MinHash dedup and RRF (§75.5.3, §75.8.3) |
| Ch 76–80 | LLM-as-a-judge, safety evaluation and prompt injection (§78.7, §78.12–§78.13); AI platform tenancy and small-model API prices (Chapter 79) |
| Ch 81–83 (new here) | Watch-time-weighted logistic regression applied; integrity-before-ranking and prevalence; page-value construction and artwork replay; LambdaMART lambdas and swap-based propensities; association-rule lift; GSP auction, PI pacing and delayed conversions; layered experiment capacity; amount-dependent fraud thresholds; EL/PD break-even; LSH banding; reviewer staffing with an occupancy cap; forecast reconciliation; asymmetric Huber; split conformal by slice; market-clearing multiplier; switchback sizing |

**Method.** Targeted grep, scripted checks and reading, following the wave 8 (Book I cases) and wave 13 methods. All three chapters were read in full.

1. **Structure.** A scratch script parsed every heading outside code blocks. For each case it checked four things:
   - `N.k.1`–`N.k.16` exist in order with the brief's titles: all 14 cases pass.
   - The figures per case: Ch 81 has 3 for each of its 7 cases, Ch 82 has 3 for each of 4, and Ch 83 has 4 for each of 3.
   - Figure and table captions are sequential per chapter, with no gaps or repeats.
   - Every case has an N.x.11 failure table with the five columns (what fails, impact, detection, recovery, prevention). Each table includes the ML-specific failures the Book II addition asks for: skew, drift, feedback loops, label leakage, stale models and adversaries.
2. **Ownership and distinctiveness.**
   - **Overlaps named in the brief.** These pairs were read side by side: 81.4/68.6–68.8; 81.5/53.7.8 and 68.13; 81.6/54.5.8 and 68.11–68.14; 81.7/§16 and 56.4; 81.8/68.5.3, 68.15 and 55.7.8; 81.9/68.7.5; 81.10/62, 69.14 and 47; 82.4/70.8 (QuickBite fraud) and 63.4/63.11; 82.5/71.4–71.13; 82.6/75.5.3 and 52.10.8; 82.7/4.10.4 and 63.5–63.14; 83.5/60.15 (QuickBite ETA) and 55.6; 83.4/18.11.4; 83.6/57.14.
   - **Formula ownership.** The book was grepped for every formula introduced in Ch 81–83 (LSH banding, lift, GSP, delayed-conversion $F(\tau)$, MinT/OLS reconciliation, asymmetric Huber, conformal, switchback size, wild goose chase, interference) to confirm none re-derives an owned formula. Results are in #10.
3. **Recurring facts.** Every platform number the cases inherit was compared with its source: §53.6, §54.4.4, §54.5, §55.4.4, §55.7.4, §56.4.4 and Table 56.5, §60.15, §68.3.2 and the agent brief (#11).
4. **Cross-references.**
   - **Outbound.** All `§N.M[.K]` references in Ch 81–83 were resolved by script against the headings of every chapter file, using absolute paths: 108, 99 and 66 distinct targets. Every cross-chapter target was printed with its title and read for topic fit. All resolve; the only non-heading hit is the legal citation "§1002.9" (12 CFR 1002.9) in Ch 82's references. Two Ch 82 targets were on the wrong topic (#4, #5).
   - **Figures and tables cited across chapters.** Figure 68.8, Table 56.5 and Table 63.3 exist and match their use.
   - **Inbound.** All 30 inbound references from Ch 1–80 to Ch 81–83 were read on topic: Ch 16, 54, 55, 56, 59 and 68. Two in Ch 55 promised material Ch 83 does not contain (#7).
   - **Ch 84+ and Book III.** The only reference into Ch 81–83 from these chapters is Ch 86's "§81.7", which is correct.
5. **Numbers.** About 450 numbers were recomputed with `python3`: every capacity example, formula example, checkpoint answer and summary figure in the three chapters (list below). Independent checks included the Erlang C staffing loop, which exposed #1, the §57.14.2 sample sizes, the LSH curve, the NDCG swaps and the market-clearing cap.
   - **Listings.** All 9 Python listings (3 per chapter) were extracted and run with `OMP_NUM_THREADS=1 python3 -I`. Every output matches the chapter's `text` block verbatim. The slowest, the Ch 83 switchback simulation, takes 18 s. None of the edits touched a listing.
6. **Terminology and spelling.** The chapters were grepped against `terminology.md` and for British spellings (#12).

**Post-edit checks.**
- **`qa_check`.** `python3 build/qa_check.py` reports 0 findings for Ch 1–83; Ch 84–86 also report 0. The only findings are in the in-progress Book III Ch 88–90 (missing end matter while being drafted), which are out of scope. Word counts after edits: Ch 81 30,837 (target 28,000–33,000); Ch 82 19,068 (17,000–20,000); Ch 83 15,665 (14,000–16,000, unchanged); Ch 55 29,712.
- **Build.** `python3 build/build.py --chapters 81-83 --name qa14a --formats html` rendered 1,242 diagrams across 90 chapters with **0 errors**. The edited text (#1–#6) appears as intended in `dist/qa14a.html`.
- **Cleanup.** `dist/qa14a.*` was deleted and `manuscript/appendices` was restored with `git checkout`.
- **Files this review modified:** chapters 55, 81, 82 and 83, plus this report. No figure or table was renumbered, and no listing changed. This review committed nothing. The working tree also holds wave-14b edits to Ch 79 and Book III drafts (Ch 87, 89) by other agents; this review did not touch them.
- **Resumption after the usage-limit interruption.** The coordinator's snapshot commit 2e1d630 contains no Ch 81–83 changes. None had been lost, because all of this review's edits were applied after the resumption.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 82 | §82.7.8, "What to notice" after the reviewer-staffing listing | S2 | **Wrong number.** "For the largest queue the occupancy cap, not the service level, decides: 54 reviewers instead of the 41 that Erlang C alone would allow." The listing's own SLA loop, run without the occupancy cap, gives **44** for 1,200 items/h (load 40, 2-minute handle time, 99% picked up within 2 minutes; $C(44, 40)\,e^{-(44/120 - 1/3)\cdot 120} \le 0.01$). The listing and its output (5/14/54) are correct. | Now "instead of the 44 that Erlang C alone would allow". The point (the cap decides for large queues) is unchanged. |
| 2 | 81 | §81.4.4 worked example "Request rate and serving fleet", step 5 | S3 | Arithmetic slip: "$515/2 = 257.2$". 257.2 is the unrounded 514.4/2; 515/2 = 257.5. The result (258 per region, 774 GPUs) is right. | Now "$515/2 = 257.5$". |
| 3 | 83 | Table 83.9 (ETA non-functional requirements), throughput row | S3 | "Five consumers, see estimate". The §83.5.4 estimate and the API's `caller` field have four: fare estimates, dispatch, active-leg refresh and app-open display. | Now "Four consumers". |
| 4 | 82 | §82.7.9, Figure 82.11 reading | S3 | "Post-publish classification is asynchronous and event-driven (Chapter 30)". Chapter 30 is Messaging Fundamentals; event-driven architecture is Chapter 32. | Now "(Chapter 32)". |
| 5 | 82 | §82.5.6, first sentence | S3 | "immutable object storage, referenced by hash (§15.9)". §15.9 is storage tiers and lifecycle policies and says nothing about immutability. §15.4 (object storage architecture) is the immutable-object model. | Now "(§15.4)". |
| 6 | 82 | §82.4.9, Figure 82.2 reading | S3 | **Diagram/prose mismatch.** The reading says every hop is asynchronous except the stream processor's write into the online store. The diagram also draws the label joiner's append to the lakehouse (`LJ->>L`) as a synchronous call. | The reading now names both writes as "retried until acknowledged". The diagram is unchanged. |
| 7 | 55 → 83 | §55.5.8 (two-stage funnel paragraph) and Table 55.8 (§55.5.14), row "Batched with future value" | S3 | **Inbound references to material Ch 83 does not contain.**<br>• "the learned acceptance probability and ETA corrections are Chapter 83 material": Ch 83 has the ETA residual (§83.5) but no driver-acceptance model.<br>• "Mature marketplaces (Chapter 83)" for assignment with learned future driver value: Ch 83 has no dispatch-value model; its nearest content is demand forecasting for positioning (§83.4). | Now:<br>• "the learned ETA corrections are Chapter 83 material (§83.5), and an acceptance-probability model is an ordinary classifier (§57.10)"<br>• "Mature marketplaces (demand forecasts, §83.4)"<br>Both resolve. |
| 8 | 81–83 | Structure and brief compliance | — | All 14 cases have the 16 binding subsections in order and ≥ 3 figures each: write, read and architecture diagrams, plus extras in Ch 83. Every N.x.8 covers the four Book II pieces: (a) features and training data, (b) a baseline then a production model, (c) the serving path, (d) offline metrics and an online experiment design. Each chapter's N.3 is one paragraph pointing to §52.3 plus what differs for ML. Every N.x.11 table has five columns and includes ML-specific failures. | None. |
| 9 | 81–83 | Evidence labels and company claims | — | **Labels.** Each chapter states that its designs are teaching designs (*Evidence: Illustrative*): §81.3, and per case in Ch 82 and Ch 83. Ch 81 case titles say "YouTube-scale", "Instagram-style" and "Netflix-style", not the company names in the TOC. Every `industry` callout carries *Evidence: Primary* with a citation.<br>**Prose claims checked against their cited sources:** Covington, Yi, Zhao and Wilhelm (YouTube); Medvedev, Vorotilov and Mosseri (Instagram); Gomez-Uribe and Hunt, Chandrashekar, and Parks (Netflix); Linden and Smith (Amazon); He and McMahan (ads); Drapeau (Stripe); Zuo (PayPal); Kumaran, Bursztein and Taylor (Gmail); Facebook PDQ and Meta prevalence; Hu, Laptev, Hall and Cohen (Uber); Chamandy (Lyft); Derrow-Pinion (Google Maps). None claims unpublished internals.<br>**Uncertain points** are in each chapter's open-verification list and already logged as UQ-358, UQ-360 and UQ-361; Ch 81's items are listed in §81.17. They include Stripe's post year and wording, PDQ's threshold of 30–32 bits, DeepETA's asymmetric Huber loss, and the Hall et al. descriptions. | None. |
| 10 | 81–83 vs owners | Ownership and duplication | — | **Read against owners; no re-teaching found.**<br>• **§81.4 vs Ch 68.** The MMoE architecture and fusion arithmetic are deferred to §68.7.4 and Figure 68.8, and the sampling-bias correction to §68.6.1. The watch-time-weighted logistic regression is one sentence in §68; §81.4 applies it with a worked example (application, not duplication).<br>• **§81.7 vs §68.12.2.** IPS is cited; §81.7 adds swap-based propensity *estimation* and a simulation. LambdaMART's lambda is new; §68.7.1 only names the method.<br>• **§81.6 vs §68.14.2.** Interleaving is cited, not re-derived; replay evaluation (Li et al.) is new.<br>• **§81.8 vs §68.5.3.** Item-to-item CF is cited; association-rule lift is new.<br>• **§82.4 vs Ch 70.** §82.4 says explicitly that QuickBite's order-fraud model and its monitoring (§70.8) are "a different, smaller problem and are not repeated". It applies §59.4.2's newsvendor reasoning to an amount-dependent threshold. Table 82.4's immature-label row deliberately mirrors Table 63.3 and cites §63.4.2.<br>• **§82.6.** The LSH banding formula appears nowhere else (§75.5.3 only names MinHash for dedup).<br>• **§82.7.** Erlang C is applied, not re-derived (§4.10.4).<br>• **§83.5 vs §60.15.** §83.5.1 contrasts the two problems (restaurant prep and hand-offs at 40,000/s versus road-network driving time at 230,000/s). §60.15 contains no residual-over-router model, map matching, asymmetric Huber loss or conformal intervals.<br>• **§83.4 and §83.6.** Pinball loss is cited to §57.11.2 and A/B power to §57.14.2. Reconciliation, switchbacks and interference appear in no other chapter. | None. |
| 11 | 81–83 vs Book I, Ch 60, Ch 68 and the brief | Recurring facts | — | **Consistent:**<br>• **YouTube platform:** 1 B watch-hours/day, 6-minute views, 7.2 M uploads/day (§81.4 = §54.4.4)<br>• **Instagram platform:** 500 M DAU, 100 M posts and 250 M stories/day, 20 feed loads (§81.5 = §53.6)<br>• **Netflix:** 150 M daily viewers (§81.6 = §54.5)<br>• **Web search:** 5 B queries/day, 115,741/s peak, 81,019/s after a 30% results cache, 300 shards, 120 GB postings per shard, 3,000 merged candidates at L2 (§81.7 = §56.4.4, Table 56.5)<br>• **E-commerce:** 100 M DAC, 20 product views, 500 M products, 10 M orders/day, 5× sales peak, 115,741 product pages/s (§81.8 = §55.7.4)<br>• **Ride-hailing:** 30 M trips/day, 1,042 requests/s and 5,208 fare estimates/s at peak, 2 M drivers online, 500,000 location updates/s, H3 res-5/7/8 areas 252.9/5.16/0.737 km² (§83 = §55.4.4, §17.9.5)<br>• **QuickBite:** ETA 40,000 predictions/s (§83.5.1 = §60.15 and the brief); search 2,000 requests/s (§81.15 challenge 2 = brief); QuickBite fraud deferred to §70.8<br>• **Prices:** small-model API \$0.15/\$0.60 per M tokens (§82.7.4 = Ch 79 and the brief)<br>• **GPU throughput:** 150 TFLOP/s effective is used consistently across all Ch 81 GPU sizings<br>One internal tension is listed under Remaining risks. | None (see Remaining risks). |
| 12 | 81–83 | Terminology and spelling | — | **Terminology.** No "master", "slave", "uptime" or "message bus". "QPS" appears once, in Uber's own phrase "highest-QPS model". "Attributes" appears only in domain senses (credit-bureau attributes, protected attributes, targeting attributes). Hit ratio and freshness terms follow `terminology.md`.<br>**Spelling.** No British spellings; the grep hits were "promising", "spelling", "supervised", "cancellations" (correct in American English) and the cited title "Towards Backward-Compatible…". | None. |

**Counts:** S1 = 0 · S2 = 1 (fixed) · S3 = 6 (fixed; one in Ch 55, with two edits) · 5 checked with no action needed (#8–#12).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 9 Python listings were run with `OMP_NUM_THREADS=1 python3 -I`. All matched verbatim:
   - **Ch 81 (3):** greedy page construction (0.6095 vs 0.704, +15.5%); swap propensities and IPS NDCG (0.495/0.334/0.254/0.2; 0.8947/0.9571/0.9983); PI pacing (14:56 vs 23:58, 42.3% vs planned 42.4%)
   - **Ch 82 (3):** downsampled fraud model and policies (\$388k/\$459k/\$212k/\$212k; declines 11,860/2,062/1,684); monotonic credit GBDT (AUC 0.728/0.739, violations 20.7%/0.0%); Erlang C staffing with an occupancy cap (5/14/54)
   - **Ch 83 (3):** negative-binomial backtest and quantile aggregation (0.704/0.360, 0.880, 7.616/2.900, 1.000/0.775); residual ETA and per-slice conformal (118.2/84.3 s, 0.852/0.525 → 0.796/0.800, 14.6/12.9/26.4%); switchback simulation (22,330; 1,686/2,199/1,698/1,714)
2. **§81.4 video.**
   - **Traffic and fleets:** 231,481/462,963 requests/s; light ranker 6,944 cores; retrieval 5,556; heavy ranker $4.63 \times 10^{16}$ FLOP/s, 309 busy, 515 GPUs, 258 per region, 774 in total (#2).
   - **Memory and training data:** index 256/64/16 GB; 83 inserts/s; ID tables 512 + 128 GB, Adagrad state 10 GB; $2.76 \times 10^{10}$ examples/day, 27.6 TB/day, 1.66 PB over 60 days, $1.66 \times 10^{19}$ FLOPs (31 GPU-hours).
   - **Ranking objective:** weighted-LR odds 0.667/0.250 (2.7×); latency budget 135 ms used, 65 ms slack; $10^{11}$ pending join keys.
3. **§81.5 feed.**
   - **Traffic and fleet:** 347,222/69,444 requests/s; $8.85 \times 10^{15}$ FLOP/s, 59/98.4/150 GPUs; $1.84 \times 10^{8}$ lookups/s.
   - **Events and integrity:** 3.47 M impressions/s; 140 GB of counters; 4,051 uploads/s, $3.5 \times 10^{19}$ FLOPs (65 GPU-hours); prevalence $2 \times 10^8$ / $2 \times 10^7$ / $6 \times 10^6$; checkpoint answer $1.5 \times 10^7$ (0.015%).
4. **§81.6 homepage.**
   - **Traffic and batch:** 6,944/17,361 pages/s; $1.8 \times 10^{12}$ pairs, 5,000 core-hours, 833 cores; 15 TB, 0.87 GB/s; 833,333 artwork decisions/s, $1.5 \times 10^{11}$ per night.
   - **Page value:** 0.2175/0.1375; 0.2794 vs 0.2354 (+0.044, 19%).
   - **Replay:** 125,000 matches, 2.2% ± 0.04 pp.
5. **§81.7 search.**
   - **Compute:** query encoder $7.0 \times 10^8$ FLOPs, $5.7 \times 10^{13}$ FLOP/s; L2 4,861 cores; L3 $1.69 \times 10^{11}$ FLOPs per query, $1.37 \times 10^{16}$ FLOP/s, 91/152 GPUs (760 at BERT-base).
   - **Labels and index:** 600,000 judgments; $3 \times 10^9$ clicks; 320 GB dense index (1.07 GB/shard); ≈ 455,000:1.
   - **LambdaMART:** IDCG 9.393, DCG 6.347, NDCG 0.676 → 0.951/0.736; |Δ| 0.275/0.061; logistic 0.622; λ 0.171/0.038 (4.5×).
6. **§81.8 e-commerce.**
   - **Traffic:** 23,148/115,741 and 3,472/17,361 per second; 347 + 116 cores.
   - **Sparsity:** $2.25 \times 10^9$ purchases, density $4.5 \times 10^{-8}$; $1.9 \times 10^{10}$ pairs (304 GB); 60 GB table; exploration 0.83%.
   - **Lift:** 60 vs 8; support 0.06%.
7. **§81.9 ads.**
   - **Traffic and fleet:** 347,222/694,444 requests/s; 13,889 cores; $6.94 \times 10^{15}$ FLOP/s, 46/77/117 GPUs; $3.47 \times 10^8$ lookups/s; \$150 M/day.
   - **Training data:** $1.785 \times 10^9$ examples (0.89 TB/day); downsampling correction 0.0087.
   - **Auction:** eCPM \$20/\$25/\$16, price \$0.80, revenue \$20 → \$19.23 at \$1.92 (+140%, 60% lower CTR); checkpoint \$24/\$30, \$1.20.
   - **Delayed conversions:** $F(1)$ = 0.393 (−61%), $F(7)$ = 0.970; checkpoint 2.5×.
8. **§81.10 platform.** $7.5 \times 10^8$ scorings/s, $3.75 \times 10^{16}$ FLOP/s, 250/417 GPUs; 1.02 + 2.56 TB, 7.2 TB for two versions; GPU pooling 50,000 GPU-hours, 2,083 busy, 6,250 vs 2,708 (−57%). Experiment sizes: $n$ = 356,331 and 5,663,744 (§57.14.2 formula), giving $E$ = 701 and 44, and 440 across 10 layers; checkpoint 50.
9. **§82.4 fraud.**
   - **Traffic and features:** 1,157/5,787 authorizations/s; 28,935 reads/s; 173,611 counter updates/s; 1.21 B entities, 605 GB (1.8 TB with replicas).
   - **Data and fleet:** 110 TB decision log; $3.78 \times 10^8$ training rows (756 GB, 4.8% prevalence); 5.6 nodes, then 3 per region and 9 in total.
   - **Thresholds:** $t^*$ 0.344/0.231/0.146; 18% fewer declines; checkpoint answers 0.0085 and 0.194.
10. **§82.5 credit.**
    - **Volume:** 0.32/6.3 applications/s; prequalification 6.3/63/s; 160,000 bads/year; 7 TB.
    - **Explanations:** TreeSHAP $500 \cdot 32 \cdot 25$ = 400,000 operations, $1.2 \times 10^{13}$ in total, 3.3 core-hours; bureau cost \$15 M/year.
    - **Expected loss:** EL \$102, profit \$186, $PD^*$ 10.5%; exploration cell \$850,000/year; checkpoint 11.1%.
11. **§82.6 spam.**
    - **Traffic and fleet:** 231,481/462,963 messages/s; 694 busy vCPU, 44 nodes, 60 with one region lost; heavy model 9.6 GPUs; false positives 3 M vs 600,000/day.
    - **State:** reputation 200 GB; MinHash 1.02 TB/day; reports 174/s.
    - **LSH curve:** threshold 0.707; $P$(0.9/0.8/0.7/0.5/0.3) = 0.9999/0.947/0.613/0.061/0.001; $(b, r) = (32, 4)$: 0.42 and 0.873; checkpoint 0.549.
12. **§82.7 moderation.**
    - **Items and GPUs:** $3.82 \times 10^9$ items/day; text 81,019/s (27 GPUs); images 6,944/s (5.8); video 27,778 frames/s (23.1).
    - **LLM classifier:** \$2,520/day (\$0.92 M/year); 1.15 TB/day (418 TB/year) of decision logs.
    - **Reviewers:** 37,500 h/day, 9,918 reviewers, 990 per 10% automated; Erlang C 5/14/44 without the cap, 5/14/54 with it (#1); checkpoint 14.
13. **§83.4 demand.**
    - **Series and outputs:** 2.5 requests per hexagon-bucket; $6 \times 10^6$ values (24 MB, 20,000/s); 3,711 aggregates (2.5%); 504 MB day-ahead; 33,333 heat-map reads/s.
    - **Data and compute:** $2.17 \times 10^8$ events (2,510/7,530 per second, 65 GB); 11.5/2.9 GB/day, 2.1 TB over two years; 120 core-seconds (0.4 cores); 640 core-hours.
    - **Reconciliation:** 52.67/49.67/102.33, ±2.33; checkpoint answer 3.
14. **§83.5 ETA.**
    - **Prediction rate:** 10,417 + 41,667 + 78,125 + 100,000 = 230,208/s (5.8× QuickBite), 76,736/s average, $6.6 \times 10^9$/day.
    - **Fleets:** model 69 busy vCPU, 9 then 15 nodes (\$11.55/h, \$0.000042 per 1,000); router 190,625 queries/s, 193 cores, 11/8/6/5 = 30 nodes; map matching 25/50 cores; total \$35/h, \$0.00003 per trip.
    - **Data:** labels 60 GB/day, 21.9 TB/year; 96 GB of traversals; 7.5/22.5 GPU-hours; log 1.13 TB/day.
    - **Asymmetric Huber:** 315/135/11,340/4,860; 100× vs 36×; checkpoint 1,620.
15. **§83.6 pricing.**
    - **Capacity:** 6,667 hexagons/s; 28.8 MB table; 57.6 GB/day decisions; 75 GB/day quotes (27.4 TB/year).
    - **Market clearing:** $m^*$ = 1.66 (93.1 = 93.1); at cap 1.5, 98.0 vs 90.3, gap 7.6.
    - **Switchback:** $n$ = 6,720; SE 0.00293, MDE 0.82 pp; with burn-in ×1.22, MDE 1.00 pp; listing true effect +7.6%, naive overstatement 30%.
16. **Cross-references.**
    - **Outbound.** Every `§` reference in Ch 81–83 resolves to a section on its topic after #4–#5.
    - **Book I targets checked:** §4.8.4, §4.10.4, §4.11; §14.7; §15.4; §16.3, §16.5, §16.11; §17.5–§17.6, §17.9.5; §18.11, §18.11.4; §22.3, §22.7.2, §22.11, §22.13, §22.15; §23.7; §29.6, §29.6.3, §29.8–§29.9; §31.5.3, §31.7.3, §31.11; §43.7, §43.7.2; §50.8–§50.10; §52.3, §52.10.8; §53.6, §53.6.9, §53.7.8; §54.4, §54.4.4, §54.4.8, §54.5, §54.5.8; §55.4–§55.9 and subsections; §56.4–§56.5 and subsections.
    - **Forward references** go to Ch 82 (policy classifiers) from Ch 81 and to Chapter 86/79 (platform scale). They match `01-master-toc.md`.

## Remaining risks

- **Ride-hailing request rate (§83.4 vs §83.5 and §55.4.4).**
  - **The tension.** §55.4.4 derives "1,042 trip requests/s" from 30 M *completed* trips/day, and §83.5.4 uses 1,042 both as the request rate (dispatch) and as the leg arrival rate (Little's Law). §83.4.4 instead assumes 36 M requests/day at 83% fulfillment, which implies about 1,255 requests/s at peak.
  - **Effect.** Each case is internally consistent and the effect is under 20% on §83.5's dispatch and refresh terms. It was not edited because harmonizing it would cascade through Table 83.10, the fleet sizes and Ch 55.
  - **Fix.** Book III Ch 89, or a later Ch 83 revision, should state that peak requests and completed trips differ by the fulfillment rate.
- **Search funnel widths.** §81.7 uses L2 → top 30 → L3 cross-encoder → final re-rank. Table 56.5 has L2 keeping 100 for the final re-rank and does not name an L3. The two are compatible (Ch 81 adds a stage), but a reader comparing them may want one sentence. Table 56.5 was not edited, because it says what the systems view needs.
- **Case titles versus the TOC.** Ch 81 uses "Video recommendations (YouTube-scale)" and similar where `01-master-toc.md` lists "YouTube Recommendations", and Ch 83 uses "Ride Demand Forecasting" where the TOC says "Ride Demand Prediction". The chapter titles are deliberate (they avoid implying company internals). The TOC can be aligned at the final build if wanted.
- **Ch 55 location spoofing → Chapter 82.** §55.5.16's pointer to Chapter 82 for driver location-spoofing and fraud systems is generic: Ch 82 covers payment fraud and abuse in general, not GPS spoofing. It was left as a chapter-level pointer.
- **Perishable facts** stay in the chapters' open-verification lists (UQ-358, UQ-360, UQ-361 and §81.17) and were not re-verified here:
  - **Ch 81:** Instagram Explore funnel and authors; Netflix's 80% figure and interleaving wording; the Twitter 2023 pipeline; ItemSage and Airbnb claims
  - **Ch 82:** Stripe Radar's year and latency wording; PayPal post metadata; RETVec authors; the PDQ threshold; Regulation B retention; chargeback windows
  - **Ch 83:** the DeepETA author list and asymmetric Huber; Bell and Smyl; the Chamandy title; Hall et al.'s outage descriptions; Cohen et al.'s elasticity wording
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–13. Every reference resolved this wave, but two were on the wrong topic (#4, #5) and two inbound references over-promised (#7). A resolver plus a printed target-title report would catch the first kind automatically.
