# Wave 10 Integration Review — Chapters 61–65 (Parts XII–XIII, ML Data and Training Infrastructure)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-09 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* five chapters drafted in parallel:

- 61 data engineering for ML
- 62 feature engineering and feature stores
- 63 data labeling, quality and data-centric AI
- 64 GPU architecture and performance
- 65 distributed ML training

The review also covered their interfaces with Book I (Ch 1–56), Part XI (Ch 57–60) and the Ch 66+ plan in `01-master-toc.md`. The reference standard is `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md`, and `04-agent-allocation.md` §4.5. The ownership split for this wave:

| Owner | Topics |
|---|---|
| Book I | Spark, Flink, watermarks (Ch 29); Kafka (Ch 31); CDC (Ch 32); columnar/Parquet basics (§13.13); Dremel/Snowflake (Ch 49); MPI collectives and α–β (§49.9); gang scheduling and Slurm (Ch 46); CPU caches and SIMD (Ch 5) |
| Part XI | Labels and leakage basics (Ch 57); training memory and FLOPs (§58.11–§58.12); data validation intro and PSI (§59.7) |
| Ch 61 | Lakehouse table formats, ML data pipelines, validation at platform scale, lineage, versioning |
| Ch 62 | Feature stores, point-in-time joins, training–serving skew, freshness |
| Ch 64 | GPU internals, roofline, precision formats, MFU, interconnect bandwidths |
| Ch 65 | Parallelism strategies, ZeRO/FSDP, training fault tolerance |

**Method.** Targeted grep, scripted checks and reading, following the wave 9 method.

1. **Ownership.** A scratch script word-counted every `##`/`###` block in Ch 61–65 and counted keywords for each owned topic. Every block over ~300 words with three or more hits for a topic it does not own was read against its owner: §61.6.1 (streaming features vs Ch 29), §61.9.2 (Parquet vs §13.13.2), §61.11 (validation vs §59.7), §62.9.2 (PSI vs §59.7.2), §62.10 (freshness vs §60.7 and §61.6.1), §64.3.1 and §64.5.1 (vs Ch 5), §64.13 (vs §58.11), §64.14.1 (vs §49.10), §65.3–§65.4 (vs §58.11–§58.12), §65.7 (vs §49.9), §65.18 (vs Ch 46).
2. **Recurring facts.** Extracted and compared across Ch 2, 57–65:
   - **QuickBite assumptions:** orders/day, DAU, couriers, restaurants, zones, customers, ETA predictions/s, reviews/day, the 7B chatbot run
   - **GPU constants:** H100/H200/B200/A100 HBM, bandwidth, dense BF16/FP8 peaks; NVLink, PCIe and NIC bandwidths; the "H100-class" round numbers of Ch 58 and Ch 65
   - **Training rules:** $6ND$, 16 bytes per parameter, ZeRO formulas, MFU definitions, PaLM and Llama 3 statistics
   - **Table formats:** Delta/Iceberg/Hudi facts against Ch 29 and Ch 49
3. **Cross-references.** All 365 `§N.M[.K]` references in Ch 61–65 were resolved by script against the actual headings, and every target was printed with its title for a topic check. Chapter-level references to Ch 66+ were checked against `01-master-toc.md`. All 83 chapter-level references from Ch 1–60 into Ch 61–65 were read (there were no inbound `§6x` references).
4. **Numbers.** About 230 numbers were recomputed with `python3` (list below). All 14 runnable Python listings in Ch 61–65 were extracted and run with `python3 -I` (NumPy, scikit-learn, PyTorch CPU); every quoted output matches verbatim. The Feast listing (§62.12) is marked `# illustrative` and was not run (Feast is not installed).
5. **Terminology and spelling.** Grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 65 chapters.
- `python3 build/build.py --chapters 61-65 --name qa --formats html`: 896 diagrams across 65 chapters, 0 errors. The edited arithmetic (#1, #2) appears as intended in the rendered HTML.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored with `git restore`.
- Modified files: chapters 13, 15, 46, 49, 58, 59, 60, 62, 64 and 65, plus this report. No figure or table was renumbered. Nothing was committed.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 64 | §64.10.2 worked example "Choosing $S$", step 3 | S1 | **Self-contradictory loss-scaling arithmetic.** After an overflow at $S = 65{,}536$ with a gradient of 2.0, the text said halving to 32,768 "fits", then in parentheses that 65,536 "would still overflow". $2 \times 32{,}768 = 65{,}536 > 65{,}504$, so 32,768 does not fit. | Step 3 now says the gradient would still overflow at 32,768 and the scaler halves again to 16,384 (giving 32,768, which fits). |
| 2 | 64 vs 65 | §64.14 worked example "Moving 7B gradients", step 4 | S2 | **Cross-node all-reduce time contradicts §65.6.2.** With "one 400 Gb/s NIC per GPU", Ch 64 gave $2 \times 14 / 50 = 560$ ms, the single-ring figure. §65.6.2 shows that in exactly this rail-optimized topology NCCL runs one ring per NIC, so $B_\text{eff} \approx 8 \times B_\text{NIC}$ and the time is about 8× lower. | Step 4 now gives both: 560 ms for a single ring through one NIC per server, about 70 ms with one ring per NIC ($2 \times \frac{127}{128} \times 14 / 400 = 69.5$ ms), with a pointer to §65.6.2. |
| 3 | 64 vs 65, brief | §64 opening note; §64.11 MFU worked example | S2 | **QuickBite chatbot run contradicts the shared assumption.** `agent-brief.md` and §65.9.1 set continued pre-training of a 7B model on 50B tokens. Ch 64 called it a "fine-tuning run" and costed "a run of $10^{12}$ tokens" (463 h, 29,600 GPU-hours, \$74,000). | Heading and opening note now say continued pre-training on 50 billion tokens (§65.9.1). Step 5 recomputed: $5 \times 10^{10}/600{,}000 = 83{,}300$ s = 23.1 h, 1,480 GPU-hours, \$3,700; about \$8,500 at 20% MFU. This agrees with §65.9.1 (22.8 h, 1,458 GPU-hours, \$3,650 at 40% MFU with $R = 10^{15}$). |
| 4 | 65 vs 64 | §65.4.1, "Two refinements matter" | S2 | **MFU defined two ways.** §65.4.1 said "MFU counts only the $6N$ model FLOPs"; §64.11 defines MFU with PaLM's attention term, $X(6N + 12Lhs)/(nF_\text{peak})$, and its example reports 46% (40% without attention). §65.4.1 also quotes Kaplan's $2Lsh$ forward attention count, a different convention. | §65.4.1 now says MFU counts only model FLOPs, that this chapter uses the $6N$ shortcut, that §64.11 adds PaLM's $12Lhs$ term, and that a quoted MFU must state its convention. §65.17's formula ($6NX/GR$) is now consistent with that statement. |
| 5 | 65 | §65.14.1 | S1 | **Misattributed citation.** "**BF16 mixed precision** [Micikevicius et al. 2018] … no loss scaling". Micikevicius et al. 2018 is the FP16 recipe, which *requires* loss scaling; it does not cover BF16. | Rephrased: BF16 mixed precision is the default, with none of the loss scaling that the original FP16 recipe needs [Micikevicius et al. 2018] (§64.10.2). |
| 6 | 64 | §64.4.5 worked example, step 3 | S3 | Unit error: "$4{,}096/256 = 16$ FLOPs per clock" is a ratio, not a rate. | Now "$16\times$ per clock". |
| 7 | 62 → 59 | §62.9.2 reading of Figure 62.8 | S3 | Ch 62 restates the PSI formula and a worked example without pointing to its owner, §59.7.2. The thresholds (0.1/0.2) and arithmetic agree with §59.7.2. | Added "(shift, §59.7.2)". The Ch 62 formula and example are kept: under ~150 words, and the example is new. |
| 8 | 13, 15, 46, 49, 58, 59, 60 → 61, 62, 65 | Inbound chapter-level references | S3 | Inbound references said only "Chapter 61/62/65" now that the targets exist. Ch 15's design challenge sent readers to Ch 61 for "pack samples into shards" of 50 billion images; Ch 61 covers per-file overhead (§61.9.3) but not training-image storage, which the TOC gives to Ch 80. | Made precise:<br>• §13.13 → §61.8–§61.9<br>• Ch 15 → §61.9.3 and Chapter 80<br>• §46 preemption → §65.15<br>• §49.5 lakehouse → §61.8; §49.9 bucketing → §65.5.2<br>• §58.12 → §65.4<br>• §59.8 → §62.8–§62.9<br>• §60.6.2 log-and-wait → §62.9.4 |
| 9 | 61–65 | Ownership measurement | — | Non-owner passages over ~300 words were read:<br>• **§61.6.1 streaming features (692 words).** Cites §29.8.1, §29.8.3 and §29.9.2 for event time, watermarks and checkpoints in one clause each; teaches only the two-sink ML pattern and a freshness formula specialized from §60.7.<br>• **§61.9.2 inside Parquet (385).** Cites §13.13.2 for encoding; adds pushdown and a runnable row-group simulation.<br>• **§61.11 validation (≈600).** Opens "§59.7 introduced expectations, mean-shift z-scores and PSI on a single batch" and adds only platform concerns (Deequ, TFDV, anomaly detection on metrics, quarantine, circuit breaking, data contracts). No duplication with §59.7.<br>• **§61.8 lakehouses.** Owned by Ch 61 (§49.5 says so). Delta/Iceberg/Hudi facts match Ch 29 and Ch 49.<br>• **§62.10 freshness.** Cites §60.7's formula; §61.6.1 and §62.10 each add a distinct, non-conflicting specialization.<br>• **§64.3.1 and §64.5.1.** Cite §5.3, §5.5, §5.9 and §5.11 and give CPU figures only as contrast.<br>• **§64.13 memory optimization.** A bulleted survey pointing to §58.11, Ch 65, 67 and 73.<br>• **§64.14.1 interconnects (669).** Owned by Ch 64 per the TOC; RDMA and topologies are cited to §49.10.<br>• **§65.3–§65.4.** Reuse §58.11–§58.12 numbers (112 GB, 30.6 GB, $4.2 \times 10^{22}$) with pointers, and add the cluster-sizing and compute-optimal layer.<br>• **§65.7 (≈350).** A table plus figure recap of §49.9; ring optimality and α–β are cited, not re-derived.<br>• **§65.18 (402).** Opens "Chapter 46 owns cluster scheduling" and gives only a comparison table and a figure. | No non-owner passage over ~400 words re-teaches an owned concept; no condensation needed. |
| 10 | 57–65 | Recurring facts | — | Consistent across chapters (after #3):<br>• **QuickBite:** 500,000 orders/day, 2 M DAU, 20,000 couriers at peak (Ch 2, 61, 62); 50,000 restaurants and 50,000 registered couriers, 4,000 zones (Ch 62); 2,000 search RPS × 20 = 40,000 ETA predictions/s (Ch 62 §62.11); 10 M customers (Ch 62, 65); 0.5% fraud and 35-min median (Ch 63); 20,000 reviews/day (Ch 63); 7B on 50B tokens (Ch 64 after #3, Ch 65)<br>• **GPU constants:** H100 SXM 80 GB, 3.35 TB/s, 989 TFLOP/s dense BF16, 1,979 FP8 (Tables 64.1–64.4); Ch 58 and Ch 65 use a stated round $10^{15}$ FLOP/s "H100-class" device; NVLink 4 450 GB/s per direction, PCIe Gen5 x16 64 GB/s, 400 Gb/s = 50 GB/s NICs in Ch 64 and Ch 65<br>• **Training rules:** $6ND = 4.2 \times 10^{22}$ for 7B × 1T and 57 h on 512 GPUs at 40% MFU in Ch 58 (§58.12) and Ch 65 (§65.4, calculator); 16 bytes/param and ZeRO-3 over 8 GPUs = 14 GB in Ch 58 and Table 65.2<br>• **PaLM:** 46.2% MFU (Ch 64, 65), 57.8% HFU (Ch 64) [Chowdhery et al. 2022]<br>• **Llama 3:** cited only in Ch 65 (405B, 15.6T tokens, $3.8 \times 10^{25}$ FLOPs, 16,384 H100s, 38–43% MFU; 466/419 interruptions in 54 days)<br>• **PSI thresholds:** 0.1/0.2 in §59.7.2 and §62.9.2 | No action. |
| 11 | 61–65 | Terminology | — | **Terms:** "master" appears only in "FP32 master weights"; "ground truth" only in Ch 63's annotation context (allowed); no "slave", "uptime", "QPS", "hit rate" or "message bus". **Spelling:** no British spellings. The grep hits were "optimistic", "programmer" and the paper title "Synthetic Data – Anonymisation Groundhog Day". | No action. |

**Counts:** S1 = 2 (fixed) · S2 = 3 (fixed) · S3 = 3 (fixed) · 3 checked with no action needed (#9–#11).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 14 runnable Python listings were run with `python3 -I`; every quoted output matches verbatim.
   - **Ch 61 (3):** idempotent partitions and backfill; table-format commit log; row-group pushdown
   - **Ch 62 (2):** naive vs point-in-time join; skew detector
   - **Ch 63 (4):** agreement statistics; Dawid–Skene; active learning; confident learning
   - **Ch 64 (3):** memory-coalescing sector counter; roofline calculator; precision demonstration (range, underflow, accumulation)
   - **Ch 65 (2):** ring all-reduce and DDP; planning calculator (memory, bubble, $6ND$, Young/Daly)
2. **§61.3–§61.5 storage and backfill.**
   - **Table 61.1:** total 79.75 ≈ 80 GB/day; app + GPS 79% of bytes; orders 5%.
   - **Lake growth:** 48 GB/day; 17.5 TB/yr; \$350/month at year end; \$2,100 for the first year; 35 TB, \$700/month for two years.
   - **Backfill:** naive 448 s per partition, 20,608 s (5.7 h), 2,907 core-h, \$145; sketches 167 s, 7,682 s (2.1 h), 1,084 core-h, \$54.
3. **§61.6.1 freshness.** 95 s online; 395 s (6.6 min) lake.
4. **§61.8.4 upserts.** $u = 41.7$ MB; CoW WA 24, 96 GB/day; MoR WA 4.0, 16 GB/day; 6× ratio; 33% read overhead.
5. **§61.9.3 small files.** 46,080 files of 56 KB; 22.0 s (98% overhead); 21 files, 0.42 s or 1.3 s; 33 min vs 2 min over 90 days; 4.1 M file entries.
6. **§61.16 size check.** 90 × 500,000 × 60 × 4 B = 10.8 GB.
7. **§62.3 encodings.** Smoothed target encoding 37.2 and 50.9 min; hashing collisions 17.4% ($2^{18}$) and 4.7% ($2^{20}$).
8. **§62.5 materialization.** \$10.54/day daily; \$252.96/day (\$92,000/yr) hourly; \$24.00/day incremental + daily (2.3×).
9. **§62.8 as-of join.** Order A age 25.5 h, $x_A = 13.0$; order D age 60 h > 48 h TTL; $\delta = 0$ gives 14.0. Semantics checked: $t + \delta \le t_i$ and $t_i - t \le$ TTL, joining on availability.
10. **§62.9 PSI.** 0.137 + 0.011 + 0.009 + 0.071 = 0.228.
11. **§62.10 freshness cost.** 5,160 s and \$4.61/day hourly; 375 s and \$5.53/day micro-batch; 63 s and \$13.82/day streaming (3×, ≈ \$3,000–3,400/yr difference).
12. **§62.11 online store.**
    - **Read load:** 46 keys and 326 values per request; 92,000 keys/s; 652,000 values/s; 52,000 keys/s and 6,000 calls/s after row merging; $0.99^3 = 0.970$ vs $0.99^{46} = 0.630$.
    - **Table 62.9:** 4.00 + 3.36 + 8.96 + 1.20 + 0.064 + 0.016 + 0.001 = 17.60 GB; × 3 / 0.6 = 88.0 GB; 6 nodes; ≈ 15,300 keys/s per node; affinity is 51%.
13. **§63.4.2 label delay.** $C(0,30) = 0.3875$ (agrees with §57.6.2's 38.75%); 0.194% observed; 61% missing; $C(60,240) = 0.9958$; 448,125 positives; 0.0021% residual noise; 74-day blind spot.
14. **§63.5.2 labeling cost.** 550 h → 687.5 h; 40 h → 50 h; \$12,312.50 = \$0.41/label; 9 annotators; 130.9 judgments/h; ≈ 3,140 labels/day.
15. **§63.6 agreement.**
    - **Cohen's κ:** $p_o = 0.850$, $p_e = 0.6508$, κ = 0.570; prevalence paradox κ = −0.026.
    - **Fleiss' κ:** $\bar P = 0.5333$, $\sum p_j^2 = 0.3689$, κ = 0.261.
    - **Krippendorff's α:** 1 − 14 × 7/142 = 0.310.
16. **§63.7 aggregation.** Majority of 3 at 0.8: 0.896; of 5: 0.942; Dawid–Skene odds 0.0414, P(remove) = 0.040.
17. **§63.8–§63.10.**
    - **LF:** 15% conflicts; 33/40 = 0.825 ± 0.12; odds 0.0126.
    - **Uncertainty:** entropy 1.030 vs 0.857 nats.
    - **Active learning:** $S = 0.75$; \$16,400 vs \$4,100; net \$7,300.
    - **Confident learning:** off-diagonal sum 395; 48% of lost accuracy recovered.
18. **§63.11 downsampling.** 4,477,500 negatives kept; 4,927,500 rows (18×); 9.13% prevalence; $p_s = 0.30 \to p = 0.021$ by both forms of the correction.
19. **§63.14 hybrid labeling.** $c_h = \$0.115$; $c = \$0.0405$ (65% cheaper, ≈ \$745/day); $A = 0.958$; audit ±0.018.
20. **§64.4 SMs.**
    - **Occupancy:** 100% / 25% / 50%; checkpoint 21 warps (33%).
    - **Divergence:** 2×.
    - **Peaks:** 66.9 TFLOP/s FP32; 989 TFLOP/s implies 1.83 GHz; 93% of 16-bit arithmetic in tensor cores.
21. **§64.5–§64.7.**
    - **Little's law:** 1.68 MB in flight.
    - **Fusion:** 537 MB; 0.96 vs 0.32 ms; 1.25 µs.
    - **Wave quantization:** 1,089 tiles; 8.25 → 9 waves (92%) vs 97%; ≈ 12% slower.
22. **§64.8–§64.9 roofline.**
    - **Ridge points:** H100 295 (BF16), 591 (FP8); A100 153; H200 206; B200 ≈ 280; V100 139.
    - **GEMM:** $2MNK$ intensity 1,365 for $4{,}096^3$ (139 µs); thin GEMM 15.9 (53 TFLOP/s, 5%).
    - **Other operations:** elementwise 0.17 (0.56 TFLOP/s); attention naive 62 vs fused 2,048.
    - **Decode:** 4.2 ms and 239 tok/s at batch 1; batch 512 7.25 ms.
    - **Checkpoint:** ridge 200; $I = 341$; 32% MFU (13B).
23. **§64.10 precision.** 70B weights 140 / 70 / 37.2 GB (MXFP4 at 4.25 bits); loss-scale window $6.6 \times 10^{-5}$ to 655 at $S = 2^{16}$; FP16 smallest subnormal $6 \times 10^{-8}$.
24. **§64.11 MFU.** $6N + 12Lhs = 4.84 \times 10^{10}$; MFU 46% (40% with $6N$ only); HFU 61%.
25. **§64.13 attention memory.** 4.3 GB per layer naive (275 GB over 32 layers with softmax output); 2.1 MB of statistics.
26. **§64.14 transfers.** 15.6 vs 2.2 ms per GB (7×); 54 ms (NVLink) and 383 ms (PCIe) for 14 GB all-reduce; 70 ms cross-node after #2; checkpoint 7.8 ms.
27. **§65.3–§65.4 walls and FLOPs.**
    - **Memory wall:** 143 GB → 3 GPUs; 70B 6.5 GB/layer, 521 GB activations, 1,641 GB → 25 GPUs.
    - **Compute wall:** 1,215 days and 46.6 years on one GPU; 41 and 568 GPUs for 30 days.
    - **7B × 1T:** 205,078 s = 57.0 h; 29,167 GPU-h; \$72,900; 91 h and \$116,700 at 25%; \$1,800 and \$25,000 per MFU point.
    - **Chinchilla:** $N_\text{opt} = 1.87 \times 10^{10}$, $D_\text{opt} = 3.74 \times 10^{11}$; 2.7× serving cost.
    - **Attention share:** 4% at $s = 2{,}048$, 61% at 32,768.
28. **§65.6 data parallelism.**
    - **All-reduce volume $2(p-1)/p\,S$:** 3.5 GB / 9.7 ms on NVLink; 3.94 GB / 98 ms with one NIC per node; 12.3 ms rail-optimized; 29% utilization at a small batch.
    - **Linear scaling:** η = 3.2; 5,000 → 156 steps/epoch.
29. **§65.8 parameter servers.** 512 GB table; 210 MB sparse traffic (≈ 5,000× less); 0.02% rows per update; QuickBite 2.56 GB.
30. **§65.9 ZeRO (Table 65.2).**
    - **$p = 8$:** 38.5 / 26.3 / 14.0 GB.
    - **$p = 64$:** 29.3 / 15.5 / 1.75 GB.
    - **QuickBite run:** $2.1 \times 10^{21}$ FLOPs, 22.8 h, 1,458 GPU-h, \$3,650.
    - **Traffic:** $V_3 = 41.3$ GB (129 ms, 7.5% of 1.72 s); $V_2 = 27.6$ GB (86 ms).
    - **Stage definitions** match Rajbhandari et al. 2020 (stage 1 optimizer, stage 2 + gradients, stage 3 + parameters; 1.5× traffic for stage 3).
31. **§65.10 tensor parallelism.** 67.1 MB activation; 470 MB per layer; 6.2 ms compute; 1.3 ms NVLink (21%) vs 11.7 ms cross-node; 0.9 s per micro-batch over 80 layers. This supports "TP within node".
32. **§65.11 pipeline.** Bubble $(p-1)/(m+p-1)$: 9/21 in Figure 65.12; 46.7% / 17.9% / 9.9%; interleaved 5.2%; 1.7 ms point-to-point.
33. **§65.13 70B plan.**
    - **Memory:** 140 GB with TP only; $2.19 \times 10^9$ params/GPU; 10.4 GB with ZeRO-1; 143 MB/layer and 11.4 GB activations; ≈ 22 GB in total. Alternative PP 2 × DP 32 ≈ 31 GB.
    - **Batch and traffic:** DP 16, $m = 64$, bubble 4.5%; 8.2 GB DP traffic, 205 ms vs 8.6 s step (2.4%); 33.2 days.
34. **§65.14 memory techniques.** $k^* = 0.75$; 1.49 GB (20×); MFU 30% / HFU 40%; selective 9.1 GB (3.4×); offload 0.28 s.
35. **§65.15–§65.16 checkpoints and failures.**
    - **Checkpoint size:** 980 GB (14 B/param); 490 s and 70 GPU-h with gather; 9.8 s sharded; 0.08 s async stall; 39 checkpoints, 38 TB.
    - **Young/Daly:** MTBF 3.1 h = 11,160 s and ≈ 50,700 GPU-h per interruption; Young 668 s, Daly 655 s, waste 11.4%; 512 GPUs 3,776 / 3,762 s, 1.2%; async 47 s.
    - **Goodput:** 8 failures, 5.3 h + 4.4 h, 98.8%; 88.6% at 16K; 1.5% waste with async + hot spares.
    - **Llama 3:** 54 days / 419 = 3.1 h.
36. **§65.17 bottlenecks.** MFU 37.8% and 21%; $1 - 0.999^{512} = 40\%$, +20% step time; 18 MB/s text vs 113 GB/s images.
37. **Concepts checked against the text.**
    - Point-in-time join on availability time with TTL (§62.8), and the "naive same-date" leak in Table 62.6.
    - Target-encoding leakage and its out-of-fold/ordered/time-window defenses (§62.3.3).
    - ZeRO stage definitions; ZeRO does not shard activations (§65.9).
    - TP inside the NVLink domain (§65.10).
    - Ring all-reduce bandwidth optimality and all-reduce = reduce-scatter + all-gather (§65.7).
    - FP16 needs loss scaling; BF16 does not (§64.10.2, after #1 and #5).
    - Downsampling correction by Bayes' rule (§63.11).
    - Fleiss reduces to Scott's π for two raters (§63.6.3).
38. **Cross-references.**
    - **Outbound:** all 365 `§` references in Ch 61–65 resolve and are on topic. The one non-match, §85.4 in Ch 62's introduction, is the TOC's Feature Store case study in the unwritten Ch 85, which is correct.
    - **Book I targets checked:**
      - **Data and storage:** §2.11, §12.4, §13.11, §13.13/§13.13.2, §14.6/§14.8/§14.10, §15.4/§15.9, §18.4/§18.11
      - **Reliability and caching:** §20.7/§20.8/§20.15, §22.12/§22.15, §23.7, §27.10, §39.4
      - **Processing and messaging:** §29.3–§29.11, §30.8/§30.11, §31.3–§31.11, §32.3.5–§32.10
      - **Scheduling, HPC and governance:** §46.8–§46.12, §49.5–§49.11, §50.8.2–§50.10
      - **Foundations:** §4.6/§4.8/§4.11/§4.18.5, §5.3/§5.5/§5.9/§5.11
    - **Chapter level:** references to Ch 66–80 match the TOC (serving, compilation, recommenders, MLOps, monitoring, LLM fundamentals and inference, adaptation, large-scale infrastructure).

## Remaining risks

- **Two attention-FLOP conventions remain** in the text: Kaplan's forward $2Lsh$ (§65.4.1) and PaLM's $12Lhs$ for forward and backward (§64.11). They differ by about 2× for attention. They are now labeled (#4), but Ch 73 and Ch 89 should pick one, preferably PaLM's for MFU, and say so.
- **QuickBite training numbers are now pinned.** Ch 64 and Ch 65 agree on 7B continued pre-training on 50B tokens on 64 GPUs, about 23 h and about 1,460–1,480 GPU-hours, at \$2.50/GPU-hour. Ch 76 (fine-tuning), Ch 79, Ch 85.5 and Ch 86.7 should reuse them. Ch 64's design challenge 2 also mentions "nightly fine-tuning jobs", which is consistent only if those are separate, smaller jobs.
- **The rail-optimized all-reduce model** ($B_\text{eff} \approx g \cdot B_\text{NIC}$, §65.6.2) is now used in Ch 64 too. Ch 80 (10k+ GPU clusters) should build on it rather than on single-ring estimates.
- **Ch 15's design challenge** now points to §61.9.3 and Chapter 80 for training-image storage. Ch 80's author should cover sample sharding (WebDataset/TFRecord-style packing), or the pointer will be thin.
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–9.
- **Perishable and unverified facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 62:** Uber Michelangelo's "≈ 10,000 features"
  - **Ch 64:** PaLM 46.2% MFU / 57.8% HFU and the Gholami et al. volume; B200 figures marked "~"
  - **Ch 65:** PaLM's JMLR venue; DDP "near-linear to 256 GPUs"
  - **All chapters:** the vendor specs flagged "as of 2026"
