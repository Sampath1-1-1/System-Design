# Wave 14b Integration Review — Chapters 84–86 (Case Studies IX–XI: Perception and Language, ML Platforms, LLM and Agent Systems)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-11 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* the last three Book II case-study chapters (13 system designs) and their interfaces with Ch 1–80:

- 84 Case Studies IX: perception and language (§84.4 face recognition, §84.5 image classification service, §84.6 speech recognition, §84.7 real-time translation)
- 85 Case Studies X: ML platforms (§85.4 feature store, §85.5 distributed training platform, §85.6 multi-tenant ML serving, §85.7 real-time inference platform)
- 86 Case Studies XI: LLM and agent systems (§86.4 enterprise RAG assistant, §86.5 LLM inference platform, §86.6 AI coding assistant, §86.7 customer-support agent, §86.8 AI-powered search)

The reference standard is `case-study-brief.md` (16 subsections per case, ≥ 3 figures per case, failure tables, apply rather than re-teach, Book II additions), `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md` (including the Ch 77–79 assumptions), and `04-agent-allocation.md` §4.5. A second reviewer covered Ch 81–83 in parallel; those files were not touched. The ownership split applied in this wave:

| Owner | Topics |
|---|---|
| Book I | Little's law (§4.11); Zanzibar (§8.12.2); WebSockets, WebRTC, connection sizing (§9.6–§9.9); object storage and presigned URLs (§15.6–§15.9); caching and popularity skew (§20.3.3, §20.9); rate limiting, token buckets, deadlines, idempotency (§22.3–§22.15); hedged requests (§23.7); sagas (§32.7); scheduling, fairness, gang scheduling, Slurm (§46.7–§46.12); tenancy, isolation, fair queuing, chargeback (§47.4–§47.13); multi-region (§44.4–§44.9); privacy engineering (§50.8–§50.9); web search engine (§56.4) |
| Ch 57–63 | A/B statistics (§57.14); problem framing (§59.4); latency budgets and cascades (§60.10, §60.13.2); **feature stores, point-in-time joins, skew, freshness, online read and memory formulas (§62.6–§62.15)**; label sources and delay (§63.4) |
| Ch 64–71 | GPU utilization and sharing (§64.11, §64.15); training checkpointing, Young/Daly, fault tolerance (§65.15–§65.18); **model serving: dynamic batching, CPU versus GPU, multi-model serving, autoscaling, cold start (§66.6–§66.14)**; quantization and distillation (§67.4–§67.8); MLOps registry and tracking (§69.7–§69.8); monitoring (Chapter 70); **responsible ML, fairness slices, biometric and AI-Act regulation (§71.4–§71.13)** |
| Ch 72–75 | KV cache (§72.11); **LLM serving: memory budget, speculative decoding, disaggregation, KV quantization, capacity plan (§73.5–§73.15)**; filtered ANN and vector index capacity (§74.9–§74.14); **RAG ingestion, ACL propagation, hybrid retrieval, citations, cost per query (§75.5–§75.15)** |
| Ch 76–80 | Structured output, distillation (§76.5, §76.13); **agents: tool calling, durable execution, idempotency, guardrails, human-in-the-loop, cost per task (§77.5–§77.17)**; evaluation, injection, routing, fallbacks (§78.4–§78.16); **AI platform: gateway, routers, GPU pools, quotas, isolation, chargeback, build versus buy (§79.5–§79.16)**; inference at very large scale (§80.13) |
| Ch 84–86 | Applied designs only: FPIR and gallery size, decode-stage pipeline costing, streaming ASR latency and RTF, average lagging and wait-k; partition fan-out, tiling reads, preemption loss, per-model cost on a shared fleet; revocation window, per-class LLM fleet sizing (QuickBite re-sizing), inline-completion latency, blended cost per contact |

**Method.** Targeted grep, scripted checks and reading, following the wave 8 (Book I case studies) and wave 13 methods. All three chapters were read in full.

1. **Structure.** A scratch script parsed every `##`/`###` heading outside code blocks and checked, per case, that `N.k.1`–`N.k.16` exist in order with the brief's exact titles, counted figures and tables per case, and checked that `**Figure N.K**`/`**Table N.K**` captions run without gaps. Every failure-scenarios subsection was checked for a table with the five brief columns and for the ML-specific rows the Book II additions require (training–serving skew, drift, feedback loops, leakage, stale models, adversarial adaptation, LLM safety).
2. **Ownership and distinctiveness.** The brief's named overlaps were read side by side with their owners:
   - §86.7 against Ch 77's QuickBite refund agent (§77.5–§77.17)
   - §85.4 against Ch 62 (§62.3.5, §62.7–§62.11, §62.15)
   - §85.6 and §85.7 against Ch 79 (LLM-specific deferral) and Ch 66
   - §86.4 against §75.5.4 and §75.14; §86.5 against §73.12–§73.15 and §79.5–§79.10; §84.5 against §66.6–§66.8 and §85.6
3. **The QuickBite LLM fleet (§86.5).** The re-sizing calculator was compared line by line with the §73.15 calculator and the Ch 79 assumptions note and §79.8 example; every Ch 76, 78 and 79 statement about the shared 7B pool was grepped and checked against §86.5's results.
4. **Cross-references.** All `§N.M[.K]` references in Ch 84–86 (88, 128 and 121 distinct targets) were resolved by script against the actual headings of all chapter files, and every cross-chapter target was printed with its title for a topic check. Cross-chapter Figure/Table citations (Figure 62.6) and chapter-level references (Chapters 81–84, 82–83) were checked. All inbound references from Ch 1–80 to Ch 84–86 were read: §62's pointer to §85.4 and Ch 79's pointer to Chapter 86.
5. **Numbers.** About 450 numbers in the capacity estimates, formulas, worked examples, tables, checkpoint answers and interview answers were recomputed with `python3` (list below), including independent re-implementations of the §86.5 generic-company fleet and the §86.8 answer-engine fleet with §73.15's step model. All nine runnable Python listings (Ch 84: 3; Ch 85: 3; Ch 86: 2; plus the Ch 85 Feast-style DSL block, which is labeled illustrative and was not run) were extracted and run with `OMP_NUM_THREADS=1 python3 -I`; every output matches the chapter verbatim, before and after edits.
6. **Evidence labels and company facts.** Every `industry` callout was checked for its label and citation; designs are presented as teaching designs; Klarna's figures were checked for the company-reported qualifier.
7. **Terminology and spelling.** Grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in Ch 1–86. Only the in-progress Book III chapters (87–90) report missing end matter, which is expected. Word counts after edits: Ch 84 19,917 (target 17,000–20,000); Ch 85 19,685 (17,000–20,000); Ch 86 23,272 (21,000–24,000); Ch 79 14,995 (cap 15,000).
- `python3 build/build.py --chapters 84-86 --name qa14b --formats html`: 1,242 diagrams across 90 chapters rendered with **0 errors**; the `qa14b` volume contains all 47 Ch 84–86 diagrams.
- `dist/qa14b.*` was deleted afterwards, and `manuscript/appendices` was restored with `git checkout`.
- Modified files: chapters 84, 85, 86 and 79, plus this report. No figure or table was renumbered. The Ch 84–86 edits were captured in the coordinator's WIP snapshot commit 2e1d630 when the session hit its usage limit; the Ch 79 edit (#13) and this report are uncommitted. This review itself committed nothing.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 86 | §86.5.4, batch paragraph; worked example "QuickBite's re-sized 7B pool", Interpretation | S2 | **Unsupported utilization claim.** The Interpretation says "the generic company above, at about 45%, is the case self-hosting was made for". The chapter's own numbers give: 618.9 busy 70B GPUs and 10.2 busy 8B GPUs at peak, an implied (unstated) peak-to-average of 2.5 (114 billion interactive tokens a day against 3.29 million tokens/s at peak), and $8.07 \times 10^6$ GPU-s of batch. That is about 8,300 busy GPU-hours a day of 21,960 provisioned (915 GPUs), **38%**, below the 45% target of Table 86.6. | The batch paragraph now states the 40%-of-peak average and adds "Busy time is about 8,300 of 21,960 GPU-hours, 38%; filling more of the trough with batch work is what lifts it to the 45% target of Table 86.6" (the night trough frees 600+ GPUs for 10 hours, so the target is reachable). The Interpretation now reads "at about 38% and rising toward 45%". |
| 2 | 86 | §86.7.4 worked example "Traffic, concurrency and model calls", Interpretation | S2 | **Wrong token rate.** "an LLM gateway quota of about 37 calls/s (2.5 million tokens per minute at the token counts below)". The next example's token counts give 8,100 input + 120 output tokens per chat call (105,300/13), about 7,950 per call averaged with email threads: $36.7 \times 7{,}950 \times 60 = 17.5$ million tokens per minute, seven times the stated figure. | Now "about 17 million tokens per minute". The conclusion (load is modest) is unchanged. |
| 3 | 86 | §86.7.4 worked example "The business case", Interpretation; §86.10 answer 13 | S2 | **Wrong comparison.** "Each point of escalation rate is worth \$0.026 per contact, \$2,600 a day, more than switching to a model with half the token price would save." Halving the \$0.176 token bill saves \$0.088 per covered contact, \$5,720 a day at 65,000 covered contacts, which equals about 2.2 points of escalation. Answer 13 repeated the claim ("more than the whole difference between two models' token prices"). | Interpretation: "…\$2,600 a day; a three-point cut saves more than halving the token price would (\$0.088 per covered contact, \$5,700 a day)". Answer 13 now gives the shares (escalations three-quarters of a covered contact's cost, tokens about 11%) and the three-point comparison. The engineering implication (optimize resolution first, tokens last) is unchanged and now correctly supported. |
| 4 | 86 | §86.6.4 worked example "The p50 path", step 2 | S2 | "Without the prefix cache, prefill is 24 ms more." Prefill of 2,000 uncached tokens on the 3B model is $2 \times 3 \times 10^9 \times 2{,}000 / 494.5 \times 10^{12} = 24.3$ ms, which is 17 ms more than the 7.3 ms cached case. | Now "prefill takes 24 ms, 17 ms more". |
| 5 | 86 | §86.5.4 batch paragraph | S3 | **Rounding.** A batch call at 2,500 + 250 tokens costs 0.807 GPU-s by the chapter's step model; the text truncated it to 0.80, giving $8.0 \times 10^6$ GPU-s and 247 GPUs instead of $8.1 \times 10^6$ and 249. | Now 0.81, $8.1 \times 10^6$ and 249 GPUs. No downstream figure changes (915 GPUs, \$54,900, \$0.32 per million). |
| 6 | 86 | §86.5.4 worked example "GPU time per call by class", step 4 | S3 | "$1{,}000 \times 0.010 = 10.2$ busy GPUs": the per-call cost is 0.0102 GPU-s. | Now $1{,}000 \times 0.0102 = 10.2$. |
| 7 | 86 vs 79 | §86.5.4 example step 4 | S3 | **Missing bridge (wave 13 remaining risk).** §86.5 reports 8.9% utilization for the whole QuickBite workload, while §79.8 reports 11% for a subset of it, which looks contradictory. The difference is that §79.8 priced every output token at 0.567 ms, while §86.5 uses each class's own batch, so short calls cost less. | Added "(§79.8's 11% priced every output token at 0.567 ms, overstating short calls)". The transfer-price bridge that wave 13 asked for is already in step 5 (\$121 a day of internal-price revenue against \$180–\$220 of cost). |
| 8 | 86 | §86.4.16, §86.5.16, §86.6.16, Table 86.15, §86.7.16, §86.8.16; §86.5.4 | S3 | **Chapter-level references written as sections**, which do not resolve: "(§71)" ×5, "(§70)" ×5 (two in combined parentheses), "(§79's figure)". | Now "Chapter 71", "Chapter 70", "(§77.15; Chapter 70)", "(Chapter 70; §79.13)" and "Chapter 79's figure". |
| 9 | 86 → 4 | §86.7.4 step 2 | S3 | "Little's law (§4.6)": §4.6 is Probability essentials; Little's Law is §4.11. | Now §4.11. |
| 10 | 84 | §84.3 | S3 | "rehearse each §84.x.15 pacing plan": a placeholder pattern, not a resolvable reference. | Now "each pacing plan (§84.4.15–§84.7.15)". |
| 11 | 84 | §84.5.8 Preprocessing, item 3, vs Figure 84.6 and its reading | S3 | **Prose–diagram mismatch.** The prose says GPU decode avoids sending "150 KB float tensors" over PCIe. Figure 84.6 and its reading give a 224×224×3 FP32 tensor of 602 KB (150 KB is the 8-bit size). | Now "602 KB FP32 tensors". |
| 12 | 85 | §85.4.4 tiling example step 2; §85.5.8 quota paragraph | S3 | (a) $50{,}000 / 121.4 = 411.9$, given as "411×". (b) "Admission has two phases" followed by three numbered items (guaranteed, borrowing, reclaim). | (a) Now 412×. (b) Now "two phases and a reclaim rule". |
| 13 | 79 → 86 | Ch 79 opening assumptions note | S3 | **Inbound pointer.** "(Chapter 86 re-sizes the fleet)" is correct but chapter-level, and a Ch 79 reader does not learn the outcome. | Now "(§86.5.4 re-sizes the fleet: six GPUs at peak with an FP16 KV cache, five with FP8)". This is the only Ch 1–80 edit (+12 words; Ch 79 at 14,995). |
| 14 | 84, 86 | §84.6.5 (`stable_prefix_len` paragraph); §86.6.1 | S3 | British "greyed" and "grey" (the book uses "gray" 48 times). | Now "grayed" and "gray". |
| 15 | 84 | §84.4.4 backfill (62 GPUs), §84.6.4 ASR (66 and 165 GPUs), §84.7.4 live ASR (198), and the derived 10× and cost figures | S3 | **Fleet sizes rounded down.** $49.7/0.8 = 62.1$, $27{,}778/420 = 66.1$, $69{,}444/420 = 165.3$, $83{,}333/420 = 198.4$, while the live photo fleet rounds 31.1 up to 32. | **No change.** Rounding down raises utilization from the 0.8/0.7 targets to at most 80.2%/70.2%, well within estimation precision; correcting would cascade through about ten figures (pacing tables, 10× sections, cost lines) for no change in any conclusion. |
| 16 | 84–86 | Structure | — | All 13 cases have exactly the 16 brief subsections with the brief's titles, in order. Figures per case: 84.4 4, 84.5 4, 84.6 4, 84.7 3; 85.4 4, 85.5 3, 85.6 3, 85.7 4; 86.4 4, 86.5 4, 86.6 3, 86.7 4, 86.8 3. Figure and table captions run without gaps: Ch 84 15/18, Ch 85 14/18, Ch 86 18/19. Every case has a five-column failure table with ML-specific rows: skew, drift and feedback loops in all 13; leakage (84.5, 85.4, 85.5); adversarial adaptation (84.4 presentation attacks, 84.5, 85.7, 86.7); LLM safety (injection in 86.4, 86.6, 86.7, 86.8; hallucinated citation 86.4, 86.8; off-target output 84.7). Each N.x.8 covers data pipeline, baseline then production model, serving and offline/online evaluation. | No action. |
| 17 | 84–86 | Ownership measurement | — | The named overlaps were read against their owners:<br>• **§86.7 vs Ch 77.** Different company (eight brands, 30 markets, email and multi-day conversations) and explicitly framed against Ch 77 in §86.7.1. Mechanisms are cited, not re-taught: tool contracts, durable execution (§77.8.2), idempotency keys (§77.10.1), compensation (§77.10.2), approval gates (§77.12.1), Erlang staffing (§77.12.2), sandboxing (§77.13). The agent-side cost applies the §77.17.1 formula; the new blended formula adds coverage $c$ and handoff factor $k$. Distinct emphases are policy-as-code per brand and market, rollout by intent, and cost per resolution.<br>• **§85.4 vs Ch 62.** The as-of join is "defined in §62.8"; read load and memory apply the §62.11.1 formulas by citation. New: partition fan-out $S(1-(1-1/S)^k)$, the two-level tiling read count (§62.3.5 describes tiles without a formula), bucketed merge at 500 M rows, and streaming exactly-once-ish composition (citing §29.8.4, §31.11.3, §61.4.5).<br>• **§85.6/§85.7 vs Ch 79.** LLM gateways, token quotas and multi-LoRA serving are deferred to Chapter 79 (§85.2, §85.6.1, §85.6.12 via §79.7, §85.6.15). §85.7 has no LLM content.<br>• **§86.4 vs §75.5.4/§75.14.** Builds on them: unexpanded principals with query-time expansion (Zanzibar, §8.12.2) and the revocation-window formula are the case's distinctive content.<br>• **§86.5 vs §73.15/§79.8.** The calculator re-implements §73.15's step model for per-class plans (class A reproduces §73.15 exactly); routing, quotas and isolation cite §79.5–§79.10.<br>• **§84.5 vs §85.6.** §84.5 defers the general platform to §85.6 and keeps image-specific content (decode stage, head bank, backbone upgrade). | No action. |
| 18 | 76, 78, 79 vs 86 | QuickBite LLM fleet | — | **§86.5 re-sizing verified** (see spot-checks). Statements in Ch 1–80 about the shared 7B pool, after #13:<br>• **Ch 79 note:** 0.567 ms at batch 46 flagged optimistic; batch near 24 at RAG length → consistent with §86.5 (FP16 batch 24, 1.11 ms; FP8 batch 48, 0.556 ms).<br>• **§79.8:** 5 GPUs, 72 GPU-hours, \$180 a day → §86.5 reproduces 5 GPUs and \$180 with an FP8 KV cache; FP16 needs 6 for this tenant.<br>• **§76.6.1:** "roughly 24 RAG-length sequences … 103,000-token KV pool (§73.5)" → matches.<br>• **§76.9.1:** "the shared pool of §79.8" → matches.<br>• **§78.16:** "about \$180 a day, mostly fixed (§79.8)" → matches the FP8 plan, which §86.5 names as "the figure §78.16 uses".<br>Ch 79's summary and Table 79.6 keep the 5-GPU, 11% plan; §86.5 states the FP8 condition and the parity gate. | #7, #13 only. |
| 19 | 84–86 | Evidence labels | — | All 10 `industry` callouts carry labels and citations. Company facts are limited to what was published: Microsoft 365 Copilot permissions; Character.AI KV-cache techniques; Copilot productivity studies; Facebook's BIPA settlement and Meta's 2021 shutdown; Apple on-device photos; Uber Michelangelo; Feast; DoorDash Sibyl; the Facebook ads paper. **Klarna** is labeled "*Evidence: Primary* — [Klarna 2024] (company-reported)", and the text says the figures are company-reported, not independently audited, with no published architecture. Zipline is labeled Secondary. All designs are teaching designs (§85.4 calls itself "a composite for teaching"). | No action. |
| 20 | 84–86 | Terminology | — | **Terms:** no "QPS", "master", "slave", "uptime", "message bus", "hit rate" or "ground truth". "Expiry" in §84.4 means retention expiry of a consent record, not a TTL synonym (as wave 8 accepted for Pastebin). "Cancellation" and "cancellable" are acceptable American forms. **Spelling:** "Localisation" appears only in the RetinaFace paper title, as published. | #14 only. |

**Counts:** S1 = 0 · S2 = 4 (fixed) · S3 = 11 (10 fixed, 1 no change) · 5 checked with no action needed (#16–#20).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 8 runnable Python listings were run with `OMP_NUM_THREADS=1 python3 -I`. All matched verbatim; none is timing-dependent.
   - **Ch 84 (3):** synthetic FMR/FNMR/FPIR (t = 0.326, FMR 1.5e-4 for group B, FPIR 0.0952/0.7851 at N = 10,000, FNMR 0.0351 at FMR 1e-8); WER alignment (5/18 = 0.278); average lagging (wait-k 1/3/5/9; 3.19–10.27 words at r = 1.3)
   - **Ch 85 (3):** tiling equivalence (0 mismatches, 2,797 vs 45.6 reads, 61×); weighted borrowing and reclaim; LRU vs GDSF (0.671/0.780/0.738)
   - **Ch 86 (2):** permission filtering (14.6% permitted, post-filter short 84%, recall 0.70; 4 leaked, 6 kept); QuickBite per-class fleet calculator (FP16 3.10 busy → 7 GPUs, 9.4 GPU-h/day; FP8 2.13 → 5 GPUs, 6.4 GPU-h/day)
2. **§84.4 face recognition**
   - **Traffic:** 2,894/8,681 photos/s; 3,472/10,417 faces/s; backfill 23,148 photos/s and 27,778 faces/s (8×)
   - **Fleet:** 14.5 + 4.2 GPUs → 32; backfill 49.7 busy (62, see #15); 149 and 1,193 GPU-h/day; \$1,100/day at \$0.80
   - **Storage and access:** templates 540 TB, +123 TB/year; galleries 614 KB and 61 TB; thumbnails 10.4 Gbit/s; 833 identifications/s; 4.1 ms exact search, 205 MB, 6.8 cores; 205 ms, 10.2 GB, 7.8 GB HNSW at 10 M
   - **Threshold:** FPIR 0.499% (N = 5,000, FMR 1e-6), 0.05%, 1.98% (N = 200,000, FMR 1e-7), FMR 5e-9 needed; 3e7 pairs; re-embed 2,222 GPU-days, detection 7,716; Q5 2e-8, 1.5e8 pairs, 2–5e-7
3. **§84.5 image classification**
   - **Traffic and pipeline cost:** 9,259/27,778/19,444 images/s; 88.9 Gbit/s; 19 GPUs (\$15.20/h); 1,065 and 231 decode cores; \$0.000148/\$0.000426/\$0.000093 per 1,000; totals \$0.000574 and \$0.000241; static fleet \$587/day, \$0.00073 per 1,000
   - **Models:** heads 164 KB and 4.1 GB; full models 51 MB, 102 GB, 390 per 20 GB; 26 ms load; backbone migration 14 GPU-hours
   - **Batching:** X(1) 513, X(8) 1,818, X(32) 2,500/s; 33.6 ms worst case; 1,462/s per GPU; 300 ms budget with 81 ms slack; 10× 190 GPUs, 2,300 cores, 41 GB of heads
4. **§84.6 speech recognition**
   - **Streams:** 23,148 average and 69,444 peak concurrent; 27,778 cloud; 444 Mbit/s; donated 4,444 h/day, 32 GB/day
   - **Latency and fleet:** RTF 0.2; 600 streams/GPU; 66/165 GPUs (see #15); 6 GFLOP/s per stream, 3.6 TFLOP/s per GPU; partial 264 ms; final 722 vs 422 ms; 2.5% per point moved on-device
   - **WER checkpoint:** S = D = I = 1, 60%
5. **§84.7 translation**
   - **Text:** 1.12e10 tokens/day; 129,630/388,889 tokens/s; 130 GPUs; 2.6 GB of weights
   - **Live:** 83,333 meetings; 198 ASR GPUs; 437,500 tokens/s, 146 GPUs, 438 with re-translation; 344–636 GPUs; 39,800 directions
   - **Wait-k:** 6.25-word budget; wait-5 2.0 s, wait-3 1.98 s, wait-5 at r = 1.3 2.69 s
6. **§85.4 feature store**
   - **Fan-out:** 3.42 M keys/s (17% of requests, 88% of keys); 340,000 calls/s; 45.96 partitions; 919,190 sub-requests/s; $0.999^{46}$ = 0.955
   - **Memory:** 128 + 19.2 + 2.16 + 72 = 221.4 GB; 1,107 GB, 18 nodes; item replicas 302,000 and 377,500 keys/s
   - **Volume:** 60.5 B events and 18.1 TB/day; 83,333 writes/s (2.4% of reads); 882 GB/day, 644 TB; spine 20 GB, output 800 GB, 9 TB join, 0.54 PB/day
   - **Tiling:** 52.3 (3.8×) and 121.4 (412×); 2.6e10 tile reads; listing 45.7 by formula; checkpoint 39 vs 1,680; backfill 1.8e12 events, 25,347 vCPU-h, \$1,270
7. **§85.5 training platform**
   - **Capacity:** 688,128 GPU-h/week; 592,000 demand (86.0%); shares 20.3/36.5/43.2%; 714/1,286/1,524 concurrent; 0.041 jobs/s
   - **Checkpoints:** 420 GB, 14/42 GB/s; 0.7 and 0.31 GB/s; rolling 5.5 TB; retained 273 and 270 TB
   - **Preemption and cost:** 10.7 vs 3.2 GPU-h (2,133 vs 640/week, 0.31% vs 0.09%); 171 GPU-h at 512 GPUs; \$1.53 M/week, \$15,300 per point; effective 0.37; 5,000 points/s, 13 GB/day; 410 GB/s; checkpoint 42.7/12.8 GPU-h
8. **§85.6 multi-tenant serving**
   - **Baseline vs shared:** \$449.6/h, \$3.94 M/year; 600 busy vCPU (17×); hot \$51.0/h; warm and cold 996 → 1,423 GB, 179 vCPU, \$20.5/h; \$71.5/h (6.3×, 16%)
   - **Cold start:** 1.55, 0.95 and 10.5 s; GPU 400 → 40 GPUs
   - **Per-model cost:** cold \$0.0068/day (\$2.48/year) vs \$2.18/day (321×); warm \$0.288/day, \$0.071 per million
9. **§85.7 real-time inference**
   - **Budget:** Gantt sums to 60 ms, a third slack
   - **Hedging:** 0.998 required per call; 0.927 unhedged; 0.999625 per call, 0.998 per stage, 39×; 2,000 extra calls/s
   - **Hardware:** S* 25 vs 125; \$0.0000111 vs \$0.00000222 per 1,000; 25 GPUs per region, 75, \$75/h vs \$375/h on CPU; ρ 0.4; risk 40 vCPU per region, \$4.80/h, \$0.42 per million
   - **Logging:** 12.8 MB/s, 0.44 TB/day; 6 GB/s, 60 MB/s, 2.1 TB/day; 10× 750 GPUs
10. **§86.4 enterprise RAG**
    - **Traffic and cost:** 6 M questions/day; 69.4/208 queries/s; 36 B/2.1 B tokens, 1.32 M tokens/s at peak; \$0.00111 and \$0.0167 per answer; routed \$0.00579, \$34,700/day, \$0.26 per seat per month (\$0.75 all-frontier, 2.9×)
    - **Index and ingestion:** 3e9 chunks, 4.06 TB (11 nodes), 12.3 TB FP32; 381 + 30 tokens; 1,712 GPU-h, \$4,280; churn 8.6 GPU-h/day, 250 GB; 1 M-document onboarding in 26 min on 8 GPUs
    - **Permissions:** $W_\text{rev}$ 60 s and 930 s; 1,500 live checks/s; 12 M chunks per group change; 1 permitted in top 50 at 2%
    - **Evaluation and scale:** 456 judged answers, \$0.0095 per call, \$4.33 per tenant, \$8,700/month; 10×: 40 TB, \$347,000/day
11. **§86.5 inference platform, generic company** (independent re-implementation with §73.15's step model, FP8 KV, TP = 4)
    - **Per call:** 283 µs per prefill token; RAG batch 128, 27.0 ms, 1.472 + 0.211 = 1.683; chat batch 256, 23.6 ms, 0.355; agent batch 78, 0.914; 8B 0.0102
    - **Fleet:** busy 420.9 + 106.6 + 91.4 = 618.9 (prefill 492.6, 80%); 8B 19 GPUs; RAG 38% of calls, 68% of GPU time; −142 GPUs at 4,000 tokens
    - **Disaggregation:** colocated 311 replicas (1,244 GPUs); disaggregated 177 + 47 = 224 (896 GPUs, 3.8:1); 348 saved (28%); 892 at ρ = 0.7; KV 0.98 GB, 4.9 ms, 508 GB/s, 1.3% of prefill
    - **Daily:** batch 0.807 GPU-s (#5); 915 GPUs, \$54,900/day; 114 + 27.5 + 28 = 169.5 B tokens; \$0.32 per million; 38% busy (#1)
12. **§86.5 QuickBite re-sizing** (checked against §73.5, §73.15, §75.15, §79.8 and wave 13 #1)
    - **Shapes:** Ch 73's 1,510 + 78 tokens (0.075 GPU-s, 0.52 busy, 2 GPUs); Ch 75's 4,050 + 200 generation (700 cached) and 450 + 30 condensation at 8/s; 35,000 plain turns at 4.0/s (peak-to-average 10, §73.15); 36,000 agent 7B calls at 3.9/s (1.3 tasks/s × 3, §77.17.1)
    - **FP16 KV:** RAG batch 24, step 26.7 ms, **1.11 ms per output token** (vs 0.42 at batch 64); prefill of 3,350 tokens 95 ms; support-chat tenant 2.54 + 0.13 = 2.67 busy → **6 GPUs** (lumped check: 3,800 × 28.3 µs + 230 × 1.11 ms = 0.363 GPU-s, 2.90 busy, 6); whole workload 3.10 busy (6× Ch 73) → **7 GPUs**, 7 × 8 + 2 × 16 = 88 GPU-h, **\$220/day**
    - **FP8 KV:** RAG batch 48, **0.556 ms**; 2.13 busy → **5 GPUs**, 72 GPU-h, **\$180/day**; 6.4 busy GPU-h, **8.9%** utilization
    - **Economics:** 494 M input + 37 M output tokens/day; \$0.34 per million; internal price **\$121/day** (67% of \$180, 55% of \$220); \$16 of busy GPU time; warm headroom 1; buying via the small-model API about \$96/day
13. **§86.6 coding assistant**
    - **Fleet:** 3 × 10⁸ requests/day; 3,472/8,681/5,208 per s; KV 57,344 B/token; prefill 7.3 ms; step 5.6 ms; decode 135 vs 52 ms; 0.0089 GPU-s; 59 busy → 118 GPUs; 177 → 354 without the prefix cache (3×); \$7,080/day, \$0.42 per developer-month
    - **Latency:** 184 ms p50; 267 ms without speculation; prefill 24.3 ms without the cache (#4); 294 ms cross-continent; 70B: 248 ms
    - **Chat and agents:** \$0.0205 per chat, \$82,000/day; 970,000 input tokens per task; \$0.63 (\$2.49 uncached), \$157,500/day; \$4.92 and \$9.45 per developer-month (agents 22× completion); 4,340 sandboxes
    - **Index:** 1.5e12 tokens, 5 B chunks, 5.5 TB, about 2,300 GPU-h
14. **§86.7 support agent**
    - **Traffic:** 1.16/3.47/5.79 contacts/s; 1,313 and 2,188 concurrent chats; 1.056 M calls/day, 36.7/s; 17 M tokens/min (#2)
    - **Agent-side cost:** 105,300 input tokens (45,500 cached); \$0.1765 (\$0.279 uncached); aux \$0.0005; \$0.377 (tokens 47%, approvals and errors 42%)
    - **Business case:** \$1.59 per covered contact; \$2.61 vs \$4.50; \$189,000/day, \$69 M/year; \$0.54 per resolution; 1,667 → 2,084 agents; 54,500 contacts, 908 → 1,136; escalation 76% of covered cost; \$0.026 per point (\$2,630/day) vs \$5,720/day for half-price tokens (#3)
15. **§86.8 answer engine** (independent re-implementation)
    - **Traffic:** 579/1,157 queries/s; 24 M generations/day, 556/s; 103 B tokens (61% of §86.5)
    - **Fleet and cost:** 70B: prefill 0.963 + decode (batch 187) 0.173 = 1.135 GPU-s; 8B: batch 184, 0.153; blended 0.448; 249 busy → 415 GPUs; \$18,675/day, \$0.37 per 1,000 queries; all-70B 1,052 GPUs, \$0.95; frontier \$0.0117 per answer, \$5.59 per 1,000
    - **Reranker and comparison:** 1.98e13 FLOPs, 0.080 GPU-s, 75 GPUs (\$0.07 per 1,000); classic search \$0.013 per 1,000 (1.2 core-s, §56.4.4); 28× and 420×
    - **Latency and index:** 430/561 ms TTFT; 8.1 s stream at 37 tokens/s; 12.8 TB passage index; 10× about 4,000 GPUs; routed 2.5× cheaper
16. **Concepts and company facts checked against the text:**
    - FPIR $= 1-(1-\text{FMR})^N$; rule of three; NIST FRVT Part 3 (189 algorithms, 10–100× false-positive differentials); Gender Shades 34.7% vs 0.8%; BIPA, GDPR Articles 9/17/25, AI Act Article 5 and Annex III; Facebook BIPA settlement \$650 M (2021) and the Meta 2021 shutdown
    - Average lagging and wait-k [Ma et al. 2019]; Whisper 680,000 hours; Koenecke et al. (nearly twice the WER); NLLB-200
    - Philly (Jeon et al. 2019) and PAI (Weng et al. 2022) trace findings as cited (open items in §85.14)
    - SWE-bench (2,294 tasks, 12 repositories, 1.96%); Peng et al. (55.8% faster); Liu et al. 2023 (51.5% and 74.5%)
    - Klarna's February 2024 figures, company-reported; *Moffatt v. Air Canada* 2024 BCCRT 149
17. **Cross-references.**
    - **Outbound:** every `§` reference in Ch 84–86 resolves to an existing section on its topic after #8–#10 (re-run after edits: 0 unresolved). Spot topic checks: §75.14 point 4 ("fetch structured data as the user"); §73.12's QuickBite disaggregation example; §56.4.4's 1.2 core-seconds per query; §62.11.1's formulas; §23.6.3, §46.10.2, §80.11.2.
    - **Inbound:** §62's pointer to §85.4 is correct; Ch 79's pointer to Chapter 86 is now §86.5.4 (#13). Ch 1–56 refer only to Ch 81–83 cases.

## Remaining risks

- **Ch 79 still plans with the FP16-optimistic 0.567 ms.** §79.8, Table 79.6, §79.15–§79.16 and the summary keep the 5-GPU, 11%, \$0.0027-per-query plan. Their note now states §86.5.4's outcome: 5 GPUs hold only with an FP8 KV cache, 6–7 with FP16. A full re-plan of Ch 79 was out of scope; if the FP8 KV cache fails QuickBite's parity gate, Ch 79's figures are about 20–25% low.
- **Little's law in Ch 80.** Ch 80 cites "Little's law — §4.6" (§80.2) and "(§4.6)" (in its hot-spares paragraph); the correct section is §4.11. The wave 13 report's ownership table repeats the error. This was not edited because it is outside this wave's inbound-reference scope.
- **Rounded-down fleet sizes in Ch 84** (#15) are left as they are; the chapter owner may round up consistently.
- **Generic-company utilization target.** After #1, §86.5 says the fleet runs at 38% and reaches its 45% target only by filling more of the trough with batch work. A future edit could size that extra batch load explicitly.
- **People-cost rates (carried from wave 13).** Ch 86 uses its own \$4.50 blended contact and \$1.20 approval for a non-QuickBite company, so it neither resolves nor worsens the QuickBite rate spread across Ch 76–78.
- **Perishable facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 84:** NISTIR 8280 wording; Meta and settlement details; Apple article titles; Whisper normalizer and hours; SeamlessM4T and NLLB sizes; dataset withdrawals; AI Act text; throughput assumptions
  - **Ch 85:** Philly and PAI figures; ModelMesh behavior; DoorDash post titles; scheduler-paper author lists; GDSF attribution
  - **Ch 86:** Character.AI figures and URL; Klarna title and figures; Liu et al. averages; Copilot privacy page; Ziegler et al. authors; Google-Extended scope
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–13. It found 13 unresolved or chapter-level references (#8–#10).
