# Wave 9 Integration Review — Chapters 57–60 (Part XI, ML Foundations)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-09 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* the four chapters that open Book II, which were drafted in parallel:

- 57 ML fundamentals
- 58 deep learning essentials
- 59 the ML lifecycle
- 60 ML system architecture

The review also covered their interfaces with Book I (Ch 1–56) and the Ch 61+ plan in `01-master-toc.md`. The reference standard is `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md`, and `04-agent-allocation.md` §4.5. The Part XI ownership split from the wave brief also applies:

| Owner | Topics |
|---|---|
| Ch 57 | Metrics, splits, losses, gradient descent, A/B statistics |
| Ch 58 | Backpropagation, optimizers, embeddings, training memory and FLOPs |
| Ch 59 | Lifecycle stages, data validation, versioning and reproducibility, MLOps maturity |
| Ch 60 | Offline/nearline/online computation, latency budgets, cascades, hidden technical debt |

**Method.** This was targeted grep, scripted checks and reading, not a full read-through. It follows the wave 8 method.

1. **Structure and captions.** A scratch script listed every `##`/`###` heading outside code blocks, every `**Figure N.K**` and `**Table N.K**` caption, and every table without a caption. Formula variable tables are excluded from that last check.
2. **Ownership.** Every `##`–`####` block in Ch 58–60 was keyword-counted for owned concepts:
   - **Ch 57:** metrics; splits and leakage; loss and gradient descent; A/B statistics
   - **Ch 58:** backpropagation, optimizers and embeddings; memory and FLOPs
   - **Ch 59:** validation, PSI, versioning and maturity
   - **Ch 60:** nearline, budgets, cascades and debt
   - **Book I:** caching (Ch 20), Kafka (Ch 31), SLOs (Ch 39), skew and feature stores (Ch 62)

   Every block over ~300 words with three or more hits was read against its owner. These overlapping pairs were also read side by side:
   - 59.3.3 / 60.4.1; 59.5.3 / 60.6.2; 59.11.1 / 60.8; 59.13.2 / 60.3.4; 59.12 / 60.12
   - §57.14 / §43.6.4
3. **Recurring facts.** These were extracted from Ch 2, 18, 39, 42 and 57–60 and compared:
   - **QuickBite assumptions:** orders/day, peak orders/s, browse and search RPS, ETA predictions/s, weekly users, registered customers, fraud rate, delivery time, peak-to-average ratio, node price
   - **ETA quality:** the ETA MAE figures and the ETA latency budgets
   - **Metric definitions:** precision, recall, PR-AUC and NDCG
   - **Training cost rules:** the $6N$/$6ND$ rule, backward ≈ 2× forward, and 16 bytes per parameter
   - **Citations:** DeepETA [Hu et al. 2022] and Sculley et al. 2015
4. **Cross-references.**
   - **Outbound `§`.** All 217 `§N.M[.K]` references in Ch 57–60 were resolved by script against the actual headings, and every cross-chapter target was printed with its title for a topic check. Section numbers inside citations of external books (e.g. "[Hastie et al. 2009, §7.10]") are expected non-matches.
   - **Chapter level.** About 120 chapter-level references to Ch 61–86 were checked against `01-master-toc.md`.
   - **Inbound.** Every `§5[7-9].*`, `§60.*`, `Ch 5[7-9]` and `Ch 60` reference in Book I was read.
5. **Numbers.** About 150 numbers were recomputed with `python3` (list below). All 15 Python listings in Ch 57–60 were extracted and run with `python3 -I` (NumPy 2.5.3, scikit-learn 1.9.1, PyTorch CPU), and their output was compared with the quoted `text` blocks.
6. **Terminology and spelling.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 60 chapters.
- `python3 build/build.py --chapters 57-60 --name qa --formats html`: 824 diagrams across 60 chapters, 0 errors.
- The rendered HTML was checked: none of its 973 TeX annotations contains prose. The new captions (Tables 59.4, 59.6, 59.10, 59.15) and the edited arithmetic appear as intended.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored.
- The only modified files are chapters 43, 56, 57, 58, 59 and 60, plus this report. Nothing was committed.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 57, 58, 59 vs 60 and Ch 2 | §57.5.1 compute example and checkpoint Q3; §58.12.1 example step 4 and opening note; §59.5.3 logging example | S2 | **Peak ETA prediction rate contradicts Ch 60 and Ch 2.**<br>• Ch 60 uses the §2.4 search peak: 2,000 RPS × 20 restaurants = **40,000 ETAs/s**, with 4,167/s on average (peak-to-average ratio 9.6, §18.11), 360 M/day and 720 ETAs per order.<br>• Ch 57, 58 and 59 multiplied the §2.11 *browse* peak (7,000 RPS, all browse reads) by 20, giving **140,000/s** and 1.2 B/day. That figure is 3.3× too high, and it changed the derived numbers: 27× the training set, 28 cores, $4.4 \times 10^{11}$ FLOP/s, and 1.2 TB/day (438 TB/yr) of logs. | Rebased all three on the §2.4 search peak:<br>• **Ch 57:** 40,000/s; $3.6 \times 10^8$/day (8× the training set); 0.2 CPU-s/s and 8 cores; $1.3 \times 10^{11}$/yr; Q3 answer now 360 M. Added a note that 7,000 RPS counts all browse reads.<br>• **Ch 58:** $1.3 \times 10^{11}$ FLOP/s, about ⅛ of the step-5 CPU server; the opening note now cites §2.4.<br>• **Ch 59:** 360 GB/day, 131 TB/yr, 3.6 GB/day sampled, and a pointer to §60.6.2. |
| 2 | 57 | §57.6.3 worked example "A fraud model with 0.99 AUC" | S3 | "ROC-AUC 0.99 (§57.10.4)": there is no §57.10.4. ROC-AUC is §57.10.2. | Changed to §57.10.2. |
| 3 | 59 | §59.3.2, item 2 | S3 | "feedback loops are covered in §59.13.3": there is no §59.13.3. Feedback loops are §59.13.2. | Changed to §59.13.2. |
| 4 | 59, 60 vs 57 | Table 59.2 framing card; Ch 60 assumptions note | S3 | **Delivery-time statistic is inconsistent.**<br>• Ch 57 sets a 35-minute *median*.<br>• Ch 60 says "a *mean* delivery takes 35 minutes".<br>• The Ch 59 framing card says "mean ≈ 32 min", the synthetic simulator's mean. For a right-skewed distribution, a mean of 32 below a median of 35 is implausible. | Both now read "median ≈ 35 min" and cite Chapter 57. The single-order example in §59.4.2 (mean 32, sd 5) is unchanged; it is per order, not the population. |
| 5 | 59 | Uncaptioned tables: problem-framing failure scenarios (§59.4.3), data-validation failure scenarios (§59.7.3), city slices (§59.10.2) | S3 | **Missing captions.** Style guide §7 requires `**Table N.K**` before every table; Ch 60 captions its equivalent failure tables (60.3, 60.7, 60.8). | **Added captions:** Table 59.4 (problem-framing failure scenarios), Table 59.6 (data-validation failure scenarios), Table 59.10 (synthetic GBDT test error by city slice).<br>**Renumbered tables only**, so captions still run 59.1–59.15 without gaps: old 59.4 → 59.5, 59.5–59.7 → 59.7–59.9, 59.8–59.12 → 59.11–59.15. No figure was renumbered. No text in the manuscript or docs cites Table 59.4 or later, so nothing else changed. |
| 6 | 57 ↔ 43 | §57.14.1; §43.6.4 warning; §43.7 list; §56.5 interview prompt | S3 | **Canary test and model A/B test were not linked.** The two sections are consistent but did not reference each other:<br>• §43.6.4 runs a pooled two-proportion z-test, one-sided, on canary error rates.<br>• §57.14 runs the same pooled test two-sided, with an unpooled CI and unpooled sample size.<br>Inbound Book I references said only "Chapter 57". | **§57.14.1:** now states the relationship: the same test, one-sided for canaries because only a regression matters, two-sided for model launches.<br>**Inbound references made precise:**<br>• §43.6.4 peeking warning → §57.14.3<br>• §43.7 experiment toggles → §57.14<br>• Ch 56 ranker interview prompt → §57.14 |
| 7 | 59, 60 → 57, 59 | Several | S3 | **Sibling chapters barely cross-referenced each other.** Ch 59 and Ch 60 had no `§57`/`§59` references, only "Chapter 57/59". Ch 60's data-validation and reproducibility steps named Ch 61/63/65 as owners and left out Ch 59. | **Targeted references added in Ch 59:**<br>• §57.10–§57.14 (prerequisites)<br>• §57.7 (random-split mistake)<br>• §57.10–§57.12 (offline evaluation)<br>• §57.14.2 (monitoring sample size)<br>• §60.7–§60.8 (batch vs online)<br>• §60.3.4 (feedback loops)<br>**In Ch 60:**<br>• §59.13 (retraining) and §59.7 (validation step)<br>• §59.5.3 (logging as served) and §59.13.2 (hidden loops)<br>• Figure 59.2 beside Figure 60.3<br>• §57.14 (A/B) and §57.10.3 (calibration)<br>• Table 60.6 owner cells now "59, 61, 63" and "58, 59, 65" |
| 8 | 59 | §59.11.2 shadow-mode warning | S3 | "Those models need an A/B test (Chapter 68)". The A/B methodology, interleaving included, is §57.14; Ch 68 is recommender architecture. | Changed to (§57.14). |
| 9 | 60 vs 59 | §60.4.2 Table 60.4; Table 60.11 | S3 | **ETA MAE levels differ between chapters.**<br>• Ch 60's illustrative quarter runs from GBDT 6.0 to 4.2 min, against an SLO of MAE ≤ 4.5.<br>• Ch 59's synthetic pipeline gives rule 4.27 and GBDT 3.22.<br>Read together, Ch 59's *rule* would already meet Ch 60's SLO. Both chapters label their figures (illustrative or synthetic), so neither is wrong. | Added one sentence to §60.4.2: the absolute values are not comparable with §59.14.4's synthetic world; only the relative sizes of the changes matter. |
| 10 | 60 vs 59 | §60.5 model-age example | S3 | **Retraining cadence differs.** Ch 60 (and §57.5.1) retrains nightly; §59.13.1 derives "more often than weekly; twice a week satisfies both" bounds, and §59.15 calls the ETA model "retrained twice a week". The two are compatible but read as a contradiction. | §60.5 now says nightly is more often than the twice-weekly cadence §59.13.1 derives as sufficient. |
| 11 | 58 | §58.5.4 worked example, Engineering implication | S3 | "a 14 GB inference model may have a 100 GB+ training checkpoint". The example's own numbers give 28 GB (FP32 master) + 56 GB (moments) = 84 GB, or 98 GB with the BF16 copy. "100 GB+" overstates it. | Now "about 84 GB (28 GB of FP32 master weights plus 56 GB of moments) or more". |
| 12 | 57 | §57.16, answer 10 | S3 | "Brier 0.07: its probabilities are calibrated" overclaims. With the same ranking, lower Brier means *better* calibrated, not perfectly calibrated. | Now "with the same ranking, its probabilities are better calibrated". |
| 13 | 59 / 60 | Figure 59.2 vs Figure 60.3 (Sculley small-box); §59.13.2 vs §60.3.4 (feedback loops) | S3 | **Near-duplicate material.**<br>• Both chapters redraw the Sculley et al. "ML code is a small box" figure.<br>• Both define feedback loops with the same "long-ETA restaurants get fewer labels" mechanism.<br>Each passage is under ~300 words, below the ~400-word condensation threshold, and each adds something: §59.13.2 the ranking loop and the fraud label-destruction warning, §60.3.4 the dispatch loop and propensity logging. | Cross-references added both ways (#7). **Deferred:** removing either figure would renumber figures. The Ch 60 owner could replace Figure 60.3 with a pointer to Figure 59.2 in a later revision. |
| 14 | 58 | §58.11.1 worked example "1B and 7B models" | S3 | A table inside an `example` callout has no `**Table**` caption. Book I has one such case and 33 uncaptioned failure tables, and `qa_check.py` does not flag it. | **Deferred.** Captioning it would make it Table 58.6 and renumber Table 58.6 (GBDT vs DNN). Leave as a worked-example table. |
| 15 | 59 | Synthetic MAE vs rule assumption; node price | — | Recorded as consistent:<br>• **Node price.** §59.9.3 prices a training node at \$0.80/h, labeled "an assumption, not a quoted price"; Ch 60 uses \$0.77/h from §42.13. These are separate, explicitly stated assumptions.<br>• **Latency.** Checkout ETA p99 ≤ 50 ms (Table 59.2) and search ETA p99 ≤ 100 ms per 20-restaurant call (Table 60.11) are different endpoints. | No action. |
| 16 | 57–60 | Ownership measurement | — | Non-owner passages over ~300 words were read:<br>• **§58.10.1 learning rate and batch size (498 words).** Cites §57.9 for gradient descent and teaches only batch-size coupling, the linear scaling rule and the critical batch size, which are Ch 58's training dynamics.<br>• **§60.5.1 training-pipeline components (1,380).** Ch 60 owns the pipeline. Validation, reproducibility and skew each get one sentence plus a pointer (§59.7, Ch 62, Ch 65).<br>• **§60.7.1 three tiers (977) and §60.8.1 precomputation (910).** Owned by Ch 60. They cite §20.7/§20.8 for caching and §31.13 for Kafka, and add the freshness-lag and precompute-waste formulas, which are not in Ch 20.<br>• **§60.12 quality SLO and fallback ladder (647).** Cites §39.5–§39.7 and Table 39.2 and adds the blended-quality formula.<br>• **§59.11.1 batch vs online (218).** A summary pointing to Ch 60 and Ch 66.<br>• **§59.7.2 PSI (419).** Ch 59 owns data validation; Ch 70 owns drift tests, and §59.7.2 points to it.<br>• **Splits, metrics and the A/B formulas** appear only in Ch 57. Ch 58–60 cite them and define none of precision, recall, PR-AUC or NDCG again. | No action beyond #7 and #13. No non-owner passage over ~400 words re-teaches an owned concept. |
| 17 | 57–60, 2, 18, 39, 42 | Recurring facts | — | Consistent across chapters (after #1 and #4):<br>• **Orders and traffic:** 500,000 orders/day and 60 orders/s peak (§2.11); 7,000 browse RPS (§2.11); 2,000 search RPS × 20 (§2.4)<br>• **Users:** 4 M weekly active users (§57.14.2, §58.6); 10 M registered customers (§58.6)<br>• **Running-example rates:** 0.5% fraud (§57.3, §57.10, §59, §60); peak-to-average ratio 9.6 (§18.11: 6,667/694); \$0.77 per 16-vCPU node-hour = \$0.048/vCPU-h (§42.13)<br>• **ETA fallback:** listed as tier 2 with a static range (Table 39.2), matching Figure 60.9<br>• **ETA latency:** "p99 < 100 ms for a batch of 20" (§55.5), matching Table 60.11<br>• **Training rules:** $6N$/$6ND$ is used everywhere; backward = 2× forward (1.67× when the first layer needs no input gradient, measured); 16 bytes per parameter for mixed-precision Adam (2+2+4+4+4) and for pure FP32 Adam (4+4+8); Adam keeps two extra FP32 copies (56 GB for 7B)<br>• **Citations:** DeepETA is cited as [Hu et al. 2022] in Ch 57 and Ch 58 with the same reference entry and the same open item. Sculley et al. 2015 and Breck et al. 2017 have identical entries in Ch 59 and Ch 60, and the 28-test, minimum-of-four-sections description agrees. | No action. |
| 18 | 57–60 | Terminology | — | **Terms:**<br>• QPS is defined once as a synonym of RPS (§60.11.1).<br>• "Master" appears only in "FP32 master weights", the standard mixed-precision term (not a primary/replica synonym).<br>• "Shard" is used for embedding-table partitioning, an allowed synonym.<br>• No "slave", "uptime", "hit rate", "ground truth" or "message bus".<br>• **"Batch scoring"** (Ch 59 §59.11.1, Ch 60 Figures 60.6/60.7) is a defined compound term for scheduled batch inference, not a synonym of "inference"; Ch 60 also uses "batch prediction". Left as is.<br>**Spelling:** no British spellings ("-ise", "behaviour", "labelled", "modelling", "artefact"). | No action. |

**Counts:** S1 = 0 · S2 = 1 (fixed) · S3 = 13 (11 fixed, 2 deferred) · 4 checked with no action needed (#15–#18).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 15 Python listings were run with `python3 -I`; every quoted output matches verbatim:
   - **Ch 57 (9):** split leakage; polynomial and ridge; logistic SGD; imbalance; metrics; calibration; regression and quantile; ranking; A/B and peeking
   - **Ch 58 (3):** manual backpropagation with a gradient check; learning-rate sweep; FLOP counter
   - **Ch 59 (2):** batch validator; end-to-end pipeline, including the hashes `d5538a49044f` / `b7ae2fe05d17` / `ab53871e5176` under NumPy 2.5.3 and scikit-learn 1.9.1
   - **Ch 60 (1):** cascade simulation
2. **§57.10 classification (Table 57.6).**
   - **Threshold metrics:** TP 3, FP 2, FN 1, TN 4; accuracy 0.70, precision 0.60, recall 0.75, $F_1$ 0.667.
   - **ROC-AUC** 17/24 = 0.708; **AP** 2.767/4 = 0.692.
   - **Log loss and Brier:** log-loss term sums 1.989 + 4.538, giving 0.653; Brier 2.3175/10 = 0.232; order 2 is 29% of the total.
   - **Imbalanced 10,000-order case:** accuracy 99.50% for both models; precision 0.50, recall 0.80, $F_1$ 0.615.
   - **Base-rate log loss** at 4.77% = 0.192.
   - **Imbalance listing:** ROC-AUC stays ≈ 0.92 while PR-AUC falls 0.647 → 0.076, confirming that ROC-AUC is insensitive to class imbalance and PR-AUC is not.
   - **Calibration vs discrimination:** identical AUC 0.836, Brier 0.0706 vs 0.1064; the 0.702 vs 0.309 bin is 2.27×.
3. **§57.9 loss and gradient descent.**
   - **One step:** $p = 0.5$, $w = 0.5$, $b = 0.25$, $\sigma(1.25) = 0.777$, loss 0.693 → 0.252.
   - **Log-loss examples:** 0.105, 0.693, 2.303, 0.010 (22× ratio); MSE 36 with 93% from one miss.
   - **Ridge penalty:** 6.3 vs 309.0.
   - **Bias–variance:** reducible error 3.84 / 0.97 / 12.16; $\sqrt{4.97} = 2.23$.
4. **§57.11 regression.**
   - **Table 57.8:** MAE 5.00; RMSE $\sqrt{50.6} = 7.11$; MAPE 11.6%; RMSE/MAE = 1.42.
   - **Pinball loss:** 3.38 at $q = 0.9$; 2.50 at $q = 0.5$.
   - **Checkpoint:** MAE 6 and RMSE $\sqrt{68} = 8.25$.
5. **§57.12 ranking (Table 57.9).**
   - P@5 0.60, R@5 0.75, AP 0.442, RR 0.5; MRR 0.583.
   - **NDCG@5:** DCG 6.303, IDCG 10.823, NDCG 0.582 (exponential gain); swapped order 8.887 → 0.821; scikit-learn's linear gain gives 0.576.
   - **Checkpoint MRR:** 0.567.
6. **§57.14 A/B statistics.**
   - **Sample size:** $(1.95996 + 0.84162)^2 = 7.849$; $n = 356{,}331$ per arm (+2% relative); 1,419,070 at +1%; rule of thumb 360,000.
   - **Result:** pooled 0.101, SE 0.000674, $z = 2.97$, $p = 0.0030$, CI [+0.0007, +0.0033].
   - **Peeking:** 0.057 → 0.220 false-positive rate with 14 peeks (4.4×).
   - **Checkpoint:** $16 \times 0.16/0.0001 = 25{,}600$.
   - **§43.6.4 (consistency):** $z = 2.59$, $n = 19{,}946$.
7. **§57.6 label maturity.** Observed fraud rates 0.20% / 0.375% / 0.475%. Assuming linear arrival within each interval, the 0–30-day average is 38.75% of true, so "well under half" holds.
8. **§57.5.1 compute (after #1).**
   - 45 M rows per run; 40,000/s peak; $3.6 \times 10^8$/day (8×)
   - 0.2 CPU-s/s; 8 cores at 200 µs; $1.3 \times 10^{11}$/yr
9. **§58.3 parameters and memory.**
   - **ETA MLP:** 525,312 + 1,049,600 + 1,025 = 1,575,937 parameters (PyTorch agrees); 6.3 MB in FP32.
   - **Checkpoint:** 5,560 parameters.
10. **§58.4 backpropagation.**
    - **Forward:** $2 \times 256 \times 1{,}573{,}888 = 805{,}830{,}656$ FLOPs.
    - **Backward:** 1.34 GFLOPs (1.67× forward) without the layer-1 input gradient, 1.61 GFLOPs (2.00×) with it.
    - **Per parameter:** 5.33 and 5.99 FLOPs per parameter per sample, consistent with $6N$.
11. **§58.5 optimizers.**
    - **Adam first step:** $\sqrt{4 \times 10^{-9}} = 6.32 \times 10^{-5}$; uncorrected step 3.16×.
    - **Cosine schedule:** $1.5 \times 10^{-4}$, $2.60 \times 10^{-4}$, $1.65 \times 10^{-4}$, $3 \times 10^{-5}$ at steps 1,000 / 26,500 / 51,000 / 100,000.
    - **Adam state:** 56 GB for 7B; 8 GB for 1B (checkpoint).
12. **§58.6 embeddings.**
    - **100 M users:** 25.6 GB FP32, 12.8 GB FP16, 6.4 GB INT8; 102.4 GB with dense Adam; 0.4 GB row-wise Adagrad.
    - **QuickBite tables:** users 2.56 GB, restaurants 12.8 MB, dishes 1.28 GB.
    - **Checkpoint:** 5.12 GB FP16 table.
13. **§58.7 convolution.**
    - **Main example:** 73,856 parameters; 462,422,016 FLOPs (PyTorch agrees); dense equivalent $8.06 \times 10^{10}$ weights (322 GB), 1.09 M×; 6,261 FLOPs per parameter.
    - **Checkpoint:** 51,264 parameters and 80,281,600 FLOPs.
14. **§58.8 RNN.** 20 ms latency; $0.9^{100} = 2.66 \times 10^{-5}$; $1.1^{100} = 13{,}781$.
15. **§58.10 training dynamics.**
    - **Linear scaling:** $\eta = 3.2$ at 8,192.
    - **Clipping:** scale 0.02 and 0.25.
    - **Sweep:** 4.5× the noise floor; 83× between best and worst final loss.
16. **§58.11 memory, 1B and 7B.**
    - **Shapes:** $12Lh^2 = 1.0 \times 10^9$ and $6.44 \times 10^9$.
    - **Fixed part:** $16N$ = 16 GB and 112 GB.
    - **Activations:** $sh(34 + 5as/h)$ = 0.48 / 0.96 GB per layer; 9.6 / 30.6 GB in total; 26 / 143 GB at $b = 1$; 77 / 245 GB at $b = 8$.
    - **FlashAttention:** 34/114 = 30%, leaving 9.1 GB.
    - **ZeRO-3 over 8 GPUs:** 14 GB per GPU.
    - **Activation checkpointing:** +33% compute.
    - **Checkpoint:** 48 GB for 3B.
17. **§58.12 FLOPs.**
    - **7B run:** $6ND = 4.2 \times 10^{22}$ FLOPs; $1.05 \times 10^8$ GPU-s = 29,200 GPU-h; 57 h on 512 GPUs.
    - **ETA model:** $8.5 \times 10^{15}$ FLOPs = 2.4 h at $10^{12}$ FLOP/s; serving after #1 is $1.26 \times 10^{11}$ FLOP/s.
    - **Checkpoint:** $1.2 \times 10^{20}$ FLOPs.
18. **§59.4.2 quantile.** $q^* = 0.75$, $z_{0.75} = 0.674$, promise 35.37 min; $q^* = 0.60$, giving 33.27 min; checkpoint $q^* = 0.8$.
19. **§59.7.2 validation statistics.**
    - **Mean shift:** SE 0.032, $z = 3.13$.
    - **PSI:** 0.0402 + 0.1853 = 0.225, matching the validator's 0.22.
20. **§59.9.3 search budget.**
    - **Grid:** \$166.67 and 8.3 h.
    - **Random:** $N \ge 58.4$, so 60; $1 - 0.95^{60} = 0.954$; \$16 and 60 min.
    - **Yearly:** \$832 vs \$8,667.
    - **Checkpoint:** 28.4, so 29.
21. **§59.12.2 detection time.**
    - **Labels needed:** $n = 33.6^2 = 1{,}129$.
    - **Platform:** 5.79 orders/s, 195 s, 63 min in total.
    - **Small city:** 0.116/s, 2.7 h, 3.7 h in total.
    - **Checkpoint:** 4.2 h.
22. **§59.13.1 retraining cadence.**
    - $T_{\max} = 8$ days; $T^* = \sqrt{20} = 4.47$ days.
    - Halving $C$ gives 3.16 days.
    - **Checkpoint:** 7 days.
23. **§59.14.4 pipeline.**
    - GBDT vs rule: 4.27 → 3.22, a 24.6% gain.
    - Random-split optimism: 2.37 vs 3.22.
    - East slice: 3.1× worse.
24. **§60.5 model age.** 30 / 18 h nightly; 12 / 9 h at 6-hourly; checkpoint 15 / 9 h.
25. **§60.6.2 prediction logging.**
    - **Volume:** 4,167/s; 108 GB/day; 12 MB/s at peak.
    - **Label ratio:** $3.6 \times 10^8$ predictions/day, so 1 in 720 gets a label; $s = 0.101$, giving 10.9 GB/day.
26. **§60.7 feature freshness.**
    - **Nightly batch:** 99,000 s = 27.5 h, 330× over budget.
    - **Nearline:** 93 s worst case, 48 s average.
    - **Checkpoint:** 186 s.
27. **§60.8 precompute vs online.**
    - **Search ETAs:** $R_{\text{batch}} = 40{,}000$/s against 4,167/s online (9.6×).
    - **Daily recommendations:** 23/s.
    - **Checkpoint:** 1,389/s.
28. **§60.10 latency budget.**
    - **Budget:** 5 + 30 + 20 + 8 + 7 + 30 = 100 ms.
    - **Fan-out:** $0.99^{41} = 0.662$; $0.99^2 = 0.980$; $0.99^{1/2} = 0.995$.
    - **Checkpoint:** 0.904.
29. **§60.11 fleet sizing.**
    - **Tree model on CPU:** 4 busy vCPU, 3 nodes, \$2.31/h, $C_{1k}$ = \$0.000154.
    - **Deep model on CPU:** 80 vCPU, 11 nodes, \$8.47/h, \$0.000565.
    - **Deep model on GPU:** $\lceil 40{,}000/15{,}000 \rceil + 1 = 4$ GPUs, \$0.000667.
    - **Per order:** \$0.00011 and \$0.00041; 3.7× ratio.
    - **Checkpoint:** 0.75 → 1 node; \$0.00083.
30. **§60.12 blended quality.**
    - **Feature-store outage:** $Q$ = 0.8189 / 0.8109 / 0.7979.
    - **Checkpoint:** 0.8435.
31. **§60.13 cost vs accuracy.**
    - **Fraud:** \$750 → \$2,250; $\Delta V$ \$9,000, net +\$7,500.
    - **Ranking:** $N = 3.6 \times 10^{10}$; \$18,000 → \$54,000; $\Delta V$ \$15,000, net −\$21,000.
    - **Cascade:** 1.45×, \$8,100 → net +\$5,400.
    - **Cascade listing:** 85% / 97% of the gain at 33% / 49% of the cost; $0.002 + 0.263 \times 0.030 = \$0.0099$.
    - **Checkpoint:** \$0.005.
32. **Concepts checked against the text.**
    - ROC-AUC insensitive to class imbalance, PR-AUC baseline = positive rate (§57.10.2).
    - Calibration is distinct from discrimination: a monotone distortion leaves AUC unchanged (§57.10.3).
    - Backward ≈ 2× forward and $C_{\text{train}} \approx 6ND$ (§58.4.2, §58.12).
    - Adam state = two extra FP32 copies (§58.5.4).
    - Time-based splits with a label-maturity gap avoid leakage (§57.7, §59.8.3 mistake, §59.14.4).
    - Cascade p99 is set by the expensive path once $r > 1\%$ (§60.13.2).
33. **Cross-references.**
    - **Outbound:** after #2, #3 and #8, all 217 `§` references in Ch 57–60 resolve and are on topic.
    - **Book I targets:**
      - **Foundations:** §2.4/§2.11 (QuickBite), §4.6–§4.9, §4.8.4, §4.10.3, §4.18.4 (standard error), §4.18.6
      - **Data and scaling:** §14.6, §18.4/§18.11, §20.7/§20.8, §23.7, §23.8.1, §29.3/§29.8/§29.10, §31.3/§31.5/§31.13, §32.6
      - **Operations:** §39.5–§39.7, §40.4/§40.5/§40.10, §42.5, §42.13, §43.6/§43.7/§43.7.3
      - **Elsewhere:** §5.11, §1.6/§1.7/§2.5, §51.4, §55.5 (switchback; 100 ms/20 ETA), §56.5
    - **Ch 61+:** every chapter-level reference matches the TOC topic. Examples:
      - **Data and features:** 61 data engineering, 62 feature stores and skew, 63 labeling
      - **Training and serving:** 64 GPUs and MFU, 65 distributed training, 66 serving, 67 compilation, 68 recommenders and exploration
      - **MLOps and responsible ML:** 69 registry and orchestration, 70 drift and PSI, 71 fairness and explainability
      - **LLMs and vectors:** 72 transformers, 73 KV cache and FlashAttention, 74 ANN, 76 LoRA
      - **Case studies:** 82 fraud
    - **Inbound:** Book I has four references to Ch 57–60 (Ch 3 study plan; Ch 43 ×2; Ch 56). All resolve; three now name §57.14/§57.14.3 (#6).

## Remaining risks

- **QuickBite prediction rates are now pinned to the search page.** Ch 57–60 agree on 40,000 ETAs/s at peak, 4,167/s on average, 360 M/day and about 720 per order. Ch 62 (feature stores), Ch 66 (serving), Ch 70 (monitoring) and Ch 83.5 (ETA case study) should reuse them, together with the §60.10 100 ms budget and the §60.11 three-node tree fleet. Do not multiply the 7,000 RPS browse peak by 20 again. `agent-brief.md` could list "2,000 search RPS × 20 = 40,000 ETA predictions/s" explicitly.
- **Two figure duplications remain** (#13): Sculley's small-box figure and the ETA feedback loop. Both are cross-linked now, but a reader who goes straight from Ch 59 to Ch 60 will see each idea drawn twice.
- **Retraining cadence and MAE levels are illustrative in two different worlds** (#9, #10). They are now reconciled in text. Ch 70 and Ch 83 should pick one world (Ch 60's 6.0 → 4.2-minute quarter and nightly retraining are the more production-like) and state it.
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script. `qa_check.py` would not have caught the two dangling references (#2, #3).
- **Perishable and unverified facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 57, 58:** the DeepETA author list and URL; the section numbers of the external textbooks
  - **Ch 58:** the illustrative $10^{15}$ FLOP/s accelerator
  - **Ch 59:** the UberEATS feature examples; the Breck et al. scoring rule
  - **Ch 60:** the Bernardi et al. latency/conversion figure; Clipper details
- **Table renumbering in Ch 59** (#5) moved tables 59.4–59.12 to 59.5–59.15. No current text cites them, but any notes or drafts outside the manuscript that use the old numbers are now stale.
