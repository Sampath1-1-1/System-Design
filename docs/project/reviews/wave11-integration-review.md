# Wave 11 Integration Review — Chapters 66–70 (Parts XIV–XV, Serving, Optimization, Recommenders, MLOps, Monitoring)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-10 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* five chapters drafted in parallel:

- 66 model serving
- 67 ML model optimization
- 68 recommendation and ranking systems architecture
- 69 MLOps and ML platforms
- 70 ML monitoring

The review also covered their interfaces with Book I (Ch 1–56), Parts XI–XIII (Ch 57–65) and the Ch 71+ plan in `01-master-toc.md`. The reference standard is `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md`, and `04-agent-allocation.md` §4.5. Ch 71–75 were being drafted in parallel by other agents during this review; they were not edited and their QA findings are out of scope. The ownership split for this wave:

| Owner | Topics |
|---|---|
| Book I | Canary releases and canary statistics (§43.6, §43.6.4), GitOps (§43.10), CI/CD (§43.3); observability, metrics, alerting (Ch 40); burn-rate alerting (§39.7.3); timeouts, breakers, shedding (Ch 22); hedging (§23.7); recommender serving plumbing (§56.5) |
| Part XI | Lifecycle and maturity levels (§59.15); validation and PSI introduced (§59.7.2); label-delay detection time (§59.12.2); retraining cadence (§59.13.1); fleet sizing and cost per 1,000 predictions (§60.11), with a batching preview (§60.11.2); embeddings (§58.6) |
| Parts XII–XIII | Training–serving skew (§62.9); label delay $F(a)$ (§63.4); precision formats and roofline (§64.9–§64.10); parameter servers (§65.8) |
| Ch 66 | General (non-LLM) serving, dynamic batching, CPU vs GPU, autoscaling, cold start, versioning, safe deployment (§66.12) |
| Ch 67 | Quantization (general), pruning, distillation, compilation, fusion; LLM *weight* quantization |
| Ch 68 | Recommender models: funnel, retrieval, ranking, embedding tables at scale, exploration, feedback loops |
| Ch 69 | CI/CD/CT for ML, tracking, registry, orchestration, governance, rollback |
| Ch 70 | Drift statistics (PSI, KS, chi-square, KL/JS, Wasserstein, MMD), delayed-label performance, ML alerting, retraining triggers |

**Method.** Targeted grep, scripted checks and reading, following the wave 10 method.

1. **Ownership.** A scratch script word-counted every `##`/`###` block in Ch 66–70 and counted keywords for each owned topic. Every block over ~300 words with hits for a topic it does not own was read against its owner (list in #20).
2. **Recurring facts.** Extracted and compared across Ch 2, 5, 43, 56–70:
   - **QuickBite assumptions:** orders/day, search and browse RPS, ETA predictions/s, rec requests/s and budget, restaurants, dishes, customers, zones, fraud rate and flag rate, chargeback curve, node and GPU prices, retraining cost
   - **Serving fleets:** §60.11 vs §66.6, §66.7, §66.9, §66.16, §67.3
   - **GPU constants and prices** against Table 64.4 and §60.11
   - **Server and tool status:** Triton/Dynamo-Triton, TorchServe, KServe, BentoML, MLflow stages vs aliases
   - **Statistics:** canary and gate sample sizes (Ch 43, 57, 66, 69); PSI notation and bands (Ch 59, 62, 70)
3. **Cross-references.** All `§N.M[.K]` references in Ch 66–70 (62, 45, 46, 58 and 61 distinct targets after edits) were resolved by script against the actual headings, and every target was printed with its title for a topic check. Chapter-level references to Ch 71+ were checked against `01-master-toc.md`. All inbound references from Ch 1–65 were read: there were no `§66`–`§70` references, and 77 chapter-level ones.
4. **Numbers.** About 260 numbers were recomputed with `python3` (list below). All 16 Python listings in Ch 66–70 were extracted and run with `OMP_NUM_THREADS=1 python3 -I` (NumPy, SciPy, scikit-learn, PyTorch CPU). Every deterministic output matches verbatim. Three timing-dependent outputs differ, as the chapters say they will: the CPU batch curve (§66.6), INT8 latency (§67.5.2) and pruned matmul time (§67.7).
5. **Terminology and spelling.** Grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in Ch 1–70. The in-progress Ch 71–75 report missing end matter, which is expected while they are drafted.
- `python3 build/build.py --chapters 66-70 --name qa --formats html`: every Ch 66–70 diagram rendered. The build renders all chapters' diagrams, and it reported one error, in the in-progress Ch 73 (a `sequenceDiagram` with two statements on one line, "…accept d1, d2; reject d3 S->>S: sample rep…"). It is left to the Ch 73 author (see Remaining risks). The edited text (#1, #2, #8, #12) appears as intended in the rendered HTML.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored with `git restore`.
- Modified files: chapters 5, 57–70, plus this report. No figure or table was renumbered. Nothing was committed.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 69 vs 59, 70 | §69.5.2 worked example "Nightly ETA retraining versus weekly fraud retraining" | S2 | **Retraining cost contradicts §59.13.1.** §59.13.1 (and Ch 70's simulation) cost one ETA retraining cycle at \$1,000 and derive a twice-weekly cadence. §69.5.2 costs the same run at \$48 and justifies nightly retraining, with no link between the two. | §69.5.2's interpretation now reconciles them: §59.13.1's \$1,000 assumed an engineer reviewing every report; at $C = \$48$, $T^* = \sqrt{2 \times 48/(2{,}000 \times 0.05)} = 0.98$ days, so automation turns twice-weekly into nightly. §70.14.2 step 3 now cites §69.5.2's \$48 beside its \$100 scenario. |
| 2 | 66 vs 60 | §66.16 worked example "Sizing the ETA pods", step 4 | S2 | **Serving fleet cost contradicts §60.11 and Table 66.9.** Step 4 gave \$1.15/h (6 pods × 4 vCPU), but Table 66.9's "about \$0.0001 per order (§60.11)" assumes §60.11's three-node floor of 48 vCPU at \$2.31/h. | Step 4 now says \$1.15/h is pod capacity on shared nodes, and that dedicated 16-vCPU nodes set §60.11's three-node floor (\$2.31/h), which the table's per-order cost assumes. |
| 3 | 62 vs 59, 70 | §62.9.2 formula "Skew and shift statistics per feature" | S3 | **PSI notation differs.** §59.7.2 and §70.5 use $p_i$ (reference) and $q_i$ (current); §62.9.2 used $e_b$, $a_b$. Thresholds (0.1/0.2) and arithmetic (0.228) agree in all three chapters. | Ch 62's formula and variable table now use $p_b$, $q_b$, "as in §59.7.2". |
| 4 | 66 | §66.8.1, first paragraph | S3 | Wrong cross-reference: "10⁹ × 128 × 4 bytes = 512 GB, §58.6". The 512 GB example is in §65.8. | Now §65.8. |
| 5 | 66 vs 69 | §66.11.1 definition of alias | S3 | Alias names differ: Ch 66 gave `production`/`challenger`; Ch 69 uses `champion`/`challenger`/`previous` for QuickBite (§69.6.2). | Now `champion` or `challenger` "(the QuickBite names of §69.6.2)". |
| 6 | 66 vs 60 | §66.9.1 worked example, step 3 | S3 | 10 deep-model CPU nodes (at $u = 0.55$, no redundancy node) vs 11 in §60.11 and §67.3, with no pointer. Both are correct under their own assumptions. | Added "(§60.11, at $u = 0.5$ with one redundancy node, sized 11)". |
| 7 | 66 | §66.6.1, "What to notice" after the CPU batch curve | S3 | "Cost per row falls about tenfold from batch 1 to 64"; the quoted output gives 44.92 → 5.72 µs, 7.9×. | Now "about eightfold … in this run". |
| 8 | 66 vs 60 | §66.7.1, before the formula | S3 | The cost-per-1,000 formula was restated without pointing to §60.11's fleet form. | Added "The formula below is the per-device form of §60.11's fleet cost." |
| 9 | 66 | §66.1 objective; §66.13 formula and Figure 66.11 titles | S3 | Terminology: "batch scoring" where `terminology.md` prefers "inference". | Now "batch inference" in the objective, the formula title and the Figure 66.11 caption (number unchanged). The Michelangelo sentence ("Batch scoring ran as Spark jobs") reports the source's wording and was kept. |
| 10 | 67 | Chapter opening note | S3 | Chapter-level reference written as a section: "(Llama-2-like, §65)". | Now "(Llama-2-like; the shape of §65.3 and §65.10)". |
| 11 | 67 vs 66 | §67.12.1 TorchInductor bullet | S3 | "Inductor generates Triton kernels" right after Ch 66 taught the Triton Inference Server. Readers can confuse the two. | Now "GPU kernels in Triton (OpenAI's Python-embedded kernel language, unrelated to the Triton Inference Server of §66.5)". |
| 12 | 68 | Figure 68.2; Figure 68.4 | S3 | **Funnel inconsistency.** Figure 68.2 said "4 sources" and Figure 68.4 drew five. Figure 68.4's quotas summed to 900 (400 + 200 + 150 + 100 + 50), but its merge output and §68.4.1 say ~1,000 candidates; the cost model filters 1,000. | Figure 68.2 now says "5 sources"; the two-tower quota is 500, so the quotas sum to 1,000. No other number changes. |
| 13 | 68 | §68.8 worked example, step 4 | S3 | "at 50 GB/s per GPU (Chapter 65 assumptions)" is vague. | Now "(one 400 Gb/s NIC per GPU, §65.6.2)". |
| 14 | 69 | §69.15 worked example, interpretation | S3 | "Four engineers' salaries equal a 30% premium on \$3 million." The salaries are \$1.0M and the premium is \$0.9M; the break-even also nets the \$100,000 fixed-fee difference. | Now "Four engineers' salaries, less the \$100,000 difference in fixed fees, equal…". |
| 15 | 69 | Figure 69.3 (CI pipeline) node L5 | S3 | Hyphen in "Training-serving parity"; the canonical term uses an en dash. | Now "Training–serving parity". |
| 16 | 70 | Table 70.6, row "Cost per 1,000 predictions" | S3 | Unit mismatch: the metric is per 1,000 predictions, but the cell gave "\$0.0001 per order (§60.15)". | Now "About \$0.00015 per 1,000, \$0.0001 per order (§60.11)". |
| 17 | 70 → 69 | Opening (line 9); §70.14.1; Figure 70.11 reading | S3 | Ch 70 cited Ch 69 by chapter number only (as briefed). | Now precise:<br>• opening → §69.5 (CT pipeline), §69.5.3 (promotion gate), §69.13 (rollback)<br>• §70.14.1 → §69.5 and §69.12 (monitoring hooks)<br>• Figure 70.11 gate → §69.5.3, canary → §43.6 and §66.12 |
| 18 | 66–70 siblings | Chapter-level references between the five chapters | S3 | Several sibling references said only "Chapter 69/70/66". | Made precise:<br>• **Ch 66:** registry → §69.8; PSI canary guardrail → §70.5.1<br>• **Ch 67:** release contract → §69.5.3<br>• **Ch 68:** two-tower versioning → §69.8<br>• **Ch 69:** drift trigger (Table 69.3) → §70.5, §70.14<br>• **Ch 70:** serving details → §66.15; batching row → §66.6<br>Overview references ("Chapter 66 owns model servers…") were kept at chapter level. |
| 19 | 5, 57–65 → 66–70 | Inbound chapter-level references | S3 | All 77 inbound references resolve on topic. Topic-specific ones said only "Chapter 66–70" now that the targets exist. | 33 references made precise (by source chapter):<br>• **Ch 5:** dynamic batching (×2) → §66.6<br>• **Ch 57:** proxy-label monitoring → §70.8; shadow deployment → §66.12<br>• **Ch 58:** batching → §66.6; embedding serving → §68.8; versioned embedding artifact → §69.8; experiment tracker → §69.7; ONNX Runtime/TensorRT → §67.10–§67.11; pinned framework versions → §69.4.5<br>• **Ch 59:** PSI alongside KS/JS → §70.5; MLflow tracking → §69.7; exploration share → §68.11; metadata store → §69.8, §69.10<br>• **Ch 60:** shadow/canary → §66.12; recommender feedback loops → §68.12; registry → §69.8; orchestrators → §69.9; autoscaling → §66.9; dynamic batching → §66.6; per-city indicators → §70.9.2<br>• **Ch 61:** logging policy → §68.12; ML orchestration → §69.9<br>• **Ch 62:** feature crosses → §68.9; drift detection → §70.4–§70.7<br>• **Ch 63:** registry lineage → §69.8.3; label-free drift monitoring → §70.8.2<br>• **Ch 64:** compiler fusion → §67.12; quantization → §67.4–§67.6; GPU monitoring → §70.12; dynamic batching → §66.6<br>• **Ch 65:** DLRM hybrid → §68.8; DLRM descendants → §68.7.3, §68.8<br>List and overview references (Ch 59's chapter map, Table 59.2, Ch 57's lifecycle list, Ch 53 and 56 scope notes) were kept at chapter level. |
| 20 | 66–70 | Ownership measurement | — | Non-owner passages over ~300 words were read:<br>• **§66.6.1 dynamic batching (≈1,200 words).** Ch 66 owns it; §60.11.2 is a short preview that points here.<br>• **§66.7.1 CPU vs GPU.** Builds on §60.11's numbers (\$0.000154, three nodes) and adds the break-even speedup $S^*$; formula now cross-linked (#8).<br>• **§66.12.1 safe deployment.** Adds a continuous-metric (MAE) sample-size formula and the paired shadow comparison; proportion tests are cited to §43.6.4, mechanics of canaries to §43.6.<br>• **§66.14 reliability.** One line per Chapter 22 pattern, with §22.11, §22.13 and §23.7 cited; the new content is the queue-limit formula.<br>• **§67.4–§67.6 quantization.** Owned; cites §64.10 and §64.10.4 for formats rather than restating them. Ch 64's INT8 paragraph is a pointer to Ch 67.<br>• **§68.4.1 funnel (1,260).** Follows §56.5.4's latency-budget method by citation; the dish-funnel CPU model and Table 68.3 are new. §68.5.5 cites §56.5.8 for the merge code; §68.8 cites §58.6 and §65.8 and adds the 100M-row example, hashing collisions and all-to-all volume.<br>• **§69.3.3 (362).** Points to §59.15 for maturity levels in one sentence.<br>• **§69.6.4.** Explicitly defers to §66.12 and §43.6 (one paragraph).<br>• **§69.12 hooks (342).** Opens "Chapter 70 owns what to monitor"; logging schema only.<br>• **§70.5.1 PSI (389).** "The formula is defined in §59.7.2"; adds bins, empty-bin floors and the 0.1/0.2 (or 0.25) provenance.<br>• **§70.8.1 (416).** Reuses §63.4.2's $F(a)$ and §59.12.2's detection times; adds observed precision and recall.<br>• **§70.13.2 (473).** Takes $b$ and $b_\text{alert}$ from §39.7.3; adds the quality-SLO differences.<br>• **§70.12.** Cites Chapter 40 and §40.5.2; adds only the ML rows of Table 70.6. | No non-owner passage over ~400 words re-teaches an owned concept; no condensation needed. |
| 21 | 2, 5, 43, 56–70 | Recurring facts | — | Consistent across chapters (after #1, #2):<br>• **QuickBite:** 500,000 orders/day; 2,000 search RPS × 20 = 40,000 ETA predictions/s, 360 M/day, 4,167/s average, peak/average 9.6, 720 per order (Ch 60, 66, 67, 69, 70); 7,000 browse RPS and 300 ms browse p99 (§2.5, Ch 68); 2,500 rec requests/s, ~1,200 restaurants / 120,000 dishes per address, 120 ms rec p99 (Ch 68; Table 68.3 sums to 120 ms); 50,000 restaurants, 5 M dishes, 10 M customers, 4 M weekly users (Ch 58, 66, 68); 4,000 zones = 20 × 200 (Ch 62, 70); 0.5% fraud = 2,500/day; 0.7% flagged = 3,500/day at 50% precision and 70% recall (Ch 70); chargebacks 40/75/95/100% at 15/30/60/90 days (Ch 57, 63, 70); \$0.77 per 16-vCPU node-hour = \$0.048/vCPU-h; \$2.50/GPU-h; \$2,000 per minute-day of MAE; \$450,000/month fraud losses (§60.13, Ch 69)<br>• **Fleets:** trees 3 nodes / \$2.31/h / \$0.000154 per 1,000; deep model 11 CPU nodes or 3 + 1 GPUs at batch 64 (Ch 60, §66.16, §67.3); §66.6 uses three GPUs sharing the peak, i.e. the same 3 + 1<br>• **GPU constants:** H100 SXM 80 GB, 3.35 TB/s, 989 TFLOP/s BF16, 1,979 FP8/INT8 (Ch 67 = Table 64.4); 4.2 ms BF16 7B decode (§64.9.2, §67.3); NIC 50 GB/s (§65.6.2, Ch 68 after #13)<br>• **Server status (as of 2026):** Triton renamed Dynamo-Triton in March 2025 and still supported; TorchServe archived 7 August 2025 (§66.5.2, Table 66.4, checkpoint Q3); no other chapter makes a status claim. MLflow stages deprecated in 2.9 in favor of aliases (§69.8.2, Q7), consistent with Ch 66's alias definition after #5<br>• **Sample sizes:** Ch 43 (two proportions, one-sided $\alpha = 0.01$), Ch 57 (two-sided, $\approx 16\sigma^2/\delta^2$), §66.12 (two-group $2(z_\alpha + z_\beta)^2\sigma^2/\delta^2$ and paired), §69.5.3 (paired non-inferiority). Each states its $\alpha$ and sidedness; §66.12's two-group form reduces to Ch 57's rule at two-sided 0.05<br>• **PSI:** $\sum (q_i - p_i)\ln(q_i/p_i)$ and bands < 0.1 / 0.1–0.2 / > 0.2 in §59.7.2, §62.9.2 (after #3) and §70.5.1; Ch 70 adds the 0.25 variant with provenance | No action. |
| 22 | 66–70 | Terminology | — | **Terms:** "master" only in "BF16 master weights"; "scoring" in "credit scoring", "inverse propensity scoring", the scikit-learn `scoring=` argument and a cited source; no "slave", "uptime", "QPS", "hit rate", "message bus" or "ground truth". **Spelling:** no British spellings (the grep hits were "raising", "promising", "surprising", "advertising"). | #9 and #15 only. |

**Counts:** S1 = 0 · S2 = 2 (fixed) · S3 = 17 (fixed) · 3 checked with no action needed (#20–#22).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 16 Python listings were run with `OMP_NUM_THREADS=1 python3 -I`.
   - **Matched verbatim:**
     - **Ch 66 (1):** dynamic batching simulator (11 rows)
     - **Ch 67 (2):** INT8 from scratch (17 lines); QAT/STE
     - **Ch 68 (3):** implicit ALS; two-tower with logQ; Thompson sampling
     - **Ch 69 (3):** behavioral tests; promotion gate (16 lines); mini tracker
     - **Ch 70 (4):** every statistic on synthetic drift; noise floor and KS at large $n$; domain classifier; retraining policies
   - **Timing-dependent, as stated in the text:** Ch 66 CPU batch curve; Ch 67 INT8 dynamic latency (size, MAE and gap lines match); Ch 67 pruning (error figures match, matmul times differ).
2. **§66.6 batching.**
   - **Table 66.5:** $X(B)$ 976 / 6,667 / 17,778 / 24,615 / 30,476 / 34,595; rows/s per ms 952 … 4,675; 25× from 1 to 64.
   - **$B_{\max}$ choice:** need 19,048 rows/s; $L_\text{worst}$ 7.2 ms and 16.8 ms; utilization 0.54; ceiling 40,000.
3. **§66.7 CPU vs GPU.**
   - **Break-even:** $S^* = 52.1 \times 0.833 = 43.4$.
   - **Dish classifier:** \$0.00133 vs \$0.000193 (6.9×).
   - **Trees:** 13% saving at 0.6; 2.7% of capacity; \$0.000500 vs \$0.000154 (3.2×).
   - **Photos:** 2.8 vCPU-h and \$0.13/day.
4. **§66.8–§66.10 multi-model, autoscaling, cold start.**
   - **Packing:** 46 models of 1.5 GB.
   - **Autoscaling:** $g = 0.30$, $u_\text{target} = 0.577$; 10 nodes; step 0.65; 7 nodes and 0.93 without headroom; 1 → 3 off-peak.
   - **Cold start:** 166 s, 196 s, 18 s; provisioning 72%; Q11 34 s.
5. **§66.12 canary.** $(1.645 + 0.842)^2 = 6.185$; 11,133 per group, about 11 h at 25,000/day; paired 348 (32×).
6. **§66.13–§66.16.**
   - **Batch job:** $8 \times 10^8$ rows; 2,500 s + 300 s = 47 min; \$15.6; \$0.00002 per 1,000 (≈ 1/8 of \$0.000154); 14 GPUs for 30 min.
   - **Admission:** $Q_{\max} = 428$ rows = 21 requests.
   - **Pods:** 6 vCPU busy; 3 pods; 0.75 after zone loss; 0.25 and 0.33 at 6 pods; \$1.15/h.
   - **Checkpoint:** Q4 30,476/s; Q7 $S^* = 50$; Q10 0.64; Q13 250 rows.
7. **§67.3 bounds.** INT4 7B 3.61 GB, 1.08 ms, $S_\text{max} = 3.88$, $S$ = 2.46 / 3.01; INT8 ETA fleet 1.25 ms, 8 vs 11 nodes, \$6.16 vs \$8.47/h, \$20,200/yr, 27% fewer nodes.
8. **§67.4 quantization.**
   - **Scale and zero-point:** $s = 0.017255$, $z = 104$; $\hat{x}$ 1.20784, 0.29333, −1.79451; symmetric $s = 0.020472$, −0.49134, 15% of grid unused; half-steps 0.0086/0.0102.
   - **SQNR:** 40.9 / 26.6 / 19.3 dB, 2.4 bits lost to one outlier; MSE $5.17 \times 10^{-6}$.
   - **Calibration:** 0.0083 vs 0.0028 (3×).
   - **Requantization:** $M = 0.64 \times 2^{-7}$, $M_0 = 1{,}374{,}389{,}535$, $q_y = 62$; $6.6 \times 10^7$ accumulator bound.
9. **§67.5–§67.6.** Size ratio 3.97×; 70B weights 140 / 70 / 36.1 / 36.4 / 27.3 GB; KV 327,680 B/token, 134,000 and 30,500 tokens; embeddings +0.8 GB.
10. **§67.7–§67.8.**
    - **Sparsity break-even:** 50% (FP16 CSR), 2/3 (INT8); 2:4 = 0.5625.
    - **Distillation:** softmaxes at $T = 1, 4$; KL 0.0375, $T^2$KL 0.601, CE 0.524, $\mathcal{L} = 0.578$.
    - **Re-ranker:** $1.41 \times 10^{10}$ FLOPs/candidate, 12.4 / 2.5 / 0.6 GPUs; low-rank 4× and $r < 512$.
11. **§67.12–§67.14.** Fusion 0.40 vs 0.16 ms, 25.6 vs 10.3 ms, 232 ms GEMM, 6%; decode 36.6 vs 5.6 µs (6.5×), 2.3 vs 0.36 ms, 30%; launch-bound 3.2 ms, 310 vs ~800 tok/s.
12. **§68.4 funnel.** 40.5 ms CPU/request; 203 cores, \$9.70/h; 60,000 cores without a funnel (296×); 500 CPU-s on the full catalog; heavy ranker 74% of CPU on 0.25% of items; +74% for 600 items; Table 68.3 = 120 ms.
13. **§68.6 logQ.** Uncorrected 0.509/0.309/0.114/0.069, loss 0.675; corrected logits 8.908/5.412/6.715/7.601, probabilities 0.708/0.022/0.079/0.192, loss 0.345; popular negative pushed 14× less.
14. **§68.8 embeddings.** 51.2 / 25.6 / 12.8 GB; Adam 153.6 GB; collisions 33% and 9.5%; all-to-all 41.9 MB, 0.84 ms; Table 68.8 sizes 2.56 GB + 12.8 MB, 3 GB, 1.28 GB.
15. **§68.10 MMR.** Picks Napoli (0.665), Sushi (0.565 vs 0.374/0.470), Burger (0.470); relevance 2.72 vs 2.60 (−4.4%); 6,000 similarity evaluations.
16. **§68.12 IPS.** Naive 0.056; IPS 0.077 = truth; clipped 0.053; position-corrected 0.10 vs 0.15.
17. **§69.5 retraining and gate.**
    - **Retraining break-even:** \$47.67 ≈ \$48, $\Delta E^* = 0.024$, $B = \$112$ (2.3×); fraud \$1,100, $\Delta E^* = 0.0105$.
    - **Paired gate:** SE 0.00657, $z$ = 23.7 (8.5 at $m = 0$); candidate B $z = -3.11$.
    - **Pairing:** unpaired SE 0.050 (7.6×) with implied correlation 0.98.
    - **Sample size:** $n_\text{req} = 251$; city slice 1,400.
18. **§69.7.3 winner's curse.** $c_8 = 1.424$ (bound 2.04); $\sigma_v = 0.037$; optimism 0.052 min; top-four range 0.013, runs 3/5/7 within 0.010.
19. **§69.9.3 caching and §69.15 TCO.**
    - **Caching:** \$1,200 vs \$359/day (70%), 95 → 20 min (4.75×), \$841/day saved, \$0.22/month storage.
    - **TCO:** \$2.35M vs \$1.69M (\$660,000); $C^* = \$3.0$M.
20. **§70.5 statistics.**
    - **PSI empty bin:** 0.0105 + 0.690 / 1.151 = 0.70 / 1.16.
    - **KS:** $c(0.05) = 1.358$, $D_\text{crit} = 0.0429$, $\lambda = 1.581$, $p = 0.0135$; 0.0019 at $10^6$.
    - **Chi-square:** $\chi^2 = 43.3$, $p = 3.9 \times 10^{-10}$, PSI 0.020, $w = 0.147$.
    - **KL/JS:** KL 0.1064 / 0.1218, sum 0.2282 = PSI; JS 0.0279 nats = 0.040 bits, distance 0.167.
    - **Wasserstein:** $W_1 = 1.2$ km, KS $D = 0.2$.
21. **§70.6 practical detection.**
    - **Noise floor:** $9/n$ = 0.09, 0.018; $n \ge 900$; 417 orders per city-hour, 1,250 per 3 h, 20,800 platform-hour.
    - **Large-$n$ KS:** gamma(2) CDF shift $\le 0.54 \times 0.01$; $D_\text{crit} = 0.0019$; $\lambda = 3.8$, $p \approx 6 \times 10^{-13}$; 5 s of ETA.
22. **§70.8–§70.9 delayed labels and calibration.**
    - **Delayed labels:** 700/3,500 = 20% observed precision, corrected 50%, recall 70% unbiased; detection 63 min and 3.7 h (§59.12.2).
    - **Calibration:** ECE 0.35% with 30-point gap in the flagged bin; implied frauds 2,501/day; zone SE 3.4 points/day and 1.3/week.
23. **§70.13–§70.14.**
    - **Burn rates:** 0.9; max 5; 14.4× impossible (288%); $b_\text{alert} = 3.4$ (68%); ticket 0.7; 41 + 35 ≈ 75 min.
    - **Retraining policies:** perf+gate \$69k, weekly \$77k, daily+gate \$156k; at \$100 per retrain \$62k vs \$64.5k; retrain-day lists match counts (20, 16 after day 90, 5).
24. **Concepts checked against the text.**
    - Dynamic quantization measures activation ranges per call and keeps FP32 activations between layers; static fixes scales by calibration (§67.5.1, Figure 67.5, Table 67.2).
    - Per-channel = one scale per output row; it folds into integer GEMMs, whereas per-group needs dedicated kernels (§67.4.2).
    - Symmetric weights avoid the input-dependent cross term (§67.4.4).
    - The logQ correction *subtracts* $\log q_j$, shrinking popular negatives' gradients (§68.6.1) [Yi et al. 2019].
    - IPS is unbiased only when $\pi_0 > 0$ wherever $\pi > 0$ and logged propensities are correct; clipping trades bias for variance (§68.12.2).
    - KS is most sensitive mid-distribution and over-powered at large $n$ (§70.5.2, §70.6.2–§70.6.3).
    - JS is symmetric, finite and bounded by $\ln 2$ (1 bit), and $\sqrt{\mathrm{JS}}$ is a metric; PSI = Jeffreys divergence (§70.5.4).
    - STE passes gradients inside the clamp range and zeroes them outside (§67.5.3).
25. **Cross-references.**
    - **Outbound:** every `§` reference in Ch 66–70 resolves to an existing section on its topic. Forward references are Chapter 71 (fairness, model cards, EU AI Act), 73 (LLM batching, KV cache, LLM parallelism), 74 (ANN internals), 75, 76 (LLM distillation and adapters), 79 (cost allocation) and 81 (§81.7 Search Ranking); all match the TOC.
    - **Book I targets checked:**
      - **Foundations and HPC:** §4.10–§4.12, §4.18.6; §18.8, §18.11; §19.4
      - **Reliability and performance:** §22.9–§22.15; §23.3.3, §23.4, §23.5, §23.7, §23.8.1
      - **Data and messaging:** §29.5, §29.8; §30.3; §31.5, §31.12
      - **Operations:** §39.6, §39.7.3; §40.4–§40.10.4; §42.5, §42.7.3, §42.12; §43.3–§43.13.2; §51.6.2
      - **Case studies:** §56.5, §56.5.4, §56.5.8, §56.5.16

## Remaining risks

- **Ch 73 diagram error.** The book-wide diagram render fails on one `sequenceDiagram` in the in-progress `73-llm-inference.md` (two statements on one line around "reject d3 S->>S: sample rep…"). It was not edited because Ch 73 is being drafted; its author or wave 12 must fix it before a full build reports 0 errors.
- **Re-ranker traffic in Ch 67.** §67.8.1 sizes a distilled cross-encoder re-ranking the top 50 dishes of every browse request at 7,000 RPS, while Ch 68 serves 2,500 recommendation requests/s and re-ranks with MMR. Both are stated as assumptions and do not conflict, but Ch 81 (search and recommendation case studies) should say which surfaces run a cross-encoder.
- **Retraining-cost anchors.** Three values now coexist, reconciled by #1: \$1,000 (manual review, §59.13.1 and Ch 70's simulation), about \$48 (automated, §69.5.2) and \$100 (Ch 70's sensitivity case). Ch 83.5 (ETA case study) should reuse \$48 for automated nightly runs.
- **Bridge-closure detection.** Ch 70 (Figure 70.13) says "about three hours" for a city-level quality ticket; §59.12.2 gives 3.7 h for a 2%-of-orders city. They are consistent only for a larger city; left as is.
- **Unverified hardware details.** The MIG layout in Figure 66.6 (3g + 2g + 2g on one H100) was not verified against NVIDIA's supported profile combinations.
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–10.
- **Perishable facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 66:** BentoML's reported acquisition (February 2026); KServe's CNCF incubation date; Triton backend and warm-up field names; Ray Serve API names
  - **Ch 67:** PyTorch 2 headline speed-ups; GPTQ timings; `torch.ao.quantization` deprecation
  - **Ch 69:** FBLearner Flow figures; MLflow alias URI syntax
  - **Ch 70:** Siddiqi's exact PSI bands; Evidently default thresholds; WhyLabs status
