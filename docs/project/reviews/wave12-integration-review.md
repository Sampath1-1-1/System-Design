# Wave 12 Integration Review — Chapters 71–75 (Part XV close, Part XVI: Responsible ML, LLM Fundamentals, LLM Inference, Vector Search, RAG)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-11 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* five chapters drafted in parallel:

- 71 responsible ML: fairness, privacy and explainability
- 72 LLM fundamentals
- 73 LLM inference infrastructure
- 74 embeddings, vector search and vector databases
- 75 RAG architecture

The review also covered their interfaces with Book I (Ch 1–56), Parts XI–XV (Ch 57–70) and the Ch 76+ plan in `01-master-toc.md`. The reference standard is `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md`, and `04-agent-allocation.md` §4.5. Ch 76–80 were being drafted in parallel by other agents during this review; they were not edited, and their QA findings are out of scope. Where they already reuse Ch 75 numbers, the fixes below were chosen so that those numbers stay valid (see #3, #4 and #6). The ownership split for this wave:

| Owner | Topics |
|---|---|
| Book I | Queueing (§4.10), Server-Sent Events (§9.5), inverted indexes and BM25 (§16.3–§16.5), search indexing pipeline (§16.10.2), caching (§20.3, §20.7, §20.10), rate limiting and shedding (§22.3, §22.9), multi-tenancy and row-level security (§47.4, §47.5.2), differential privacy introduced (§50.11), GDPR deletion (§50.9.3) |
| Parts XI–XIII | Classification and ranking metrics (§57.10, §57.12); embeddings (§58.6); slices and model cards (§59.10); data documentation (§63.13); roofline, precision formats, FlashAttention tiling (§64.9–§64.13); training FLOPs, TP/PP/EP for training (§65.4, §65.10–§65.12) |
| Ch 66–70 | General serving and dynamic batching (§66.6); quantization in general and LLM *weight* quantization (Ch 67, §67.6); governance (§69.11); drift statistics (§70.5–§70.7) |
| Ch 71 | Fairness metrics and mitigation, explainability, privacy attacks, DP-SGD, federated learning, documentation, regulation |
| Ch 72 | Tokenization, attention, MHA/MQA/GQA, parameter counts, RoPE, prefill vs decode, **KV-cache mechanics and size**, sampling, MoE, FLOPs per token |
| Ch 73 | LLM serving: memory budget, continuous batching, PagedAttention, prefix caching, attention kernels, speculative decoding, inference parallelism, disaggregation, **LLM-specific (KV and serving) quantization**, scheduling, capacity, engines |
| Ch 74 | Embedding models, similarity, exact vs ANN search, HNSW, IVF, PQ/SQ/BQ, ScaNN, DiskANN, filtering, updates, **vector databases (deep)**, capacity |
| Ch 75 | Ingestion, chunking, embedding at scale, hybrid retrieval and RRF, reranking, query transformation, context construction, grounded generation, **retrieval metrics (§75.13)**, RAG in production; *previews only* of RAG vs fine-tuning (Ch 76), LLM evaluation and prompt-injection defenses (Ch 78), agents (Ch 77) |

**Method.** Targeted grep, scripted checks and reading, following the wave 11 method.

1. **Ownership.** A scratch script word-counted every `##`/`###` block in Ch 71–75 (code excluded) and counted keyword hits for eleven owned topics (quantization, KV cache, batching and engines, vector databases, fine-tuning, LLM evaluation, prompt injection, fairness and privacy, BM25, tokenization, agents). Every block over 300 words with four or more hits for a topic it does not own was read against its owner, together with the sections named in the brief (§72.11.1, §73.5.1, §73.13.1, §75.3.2–§75.3.3, §75.11.4, §75.12, §75.13.4, §75.16.2). Results are in #14.
2. **Recurring facts.** Extracted and compared across Ch 2, 4, 5, 58, 60, 61, 64, 65, 67 and 71–75, against the agent brief:
   - **Chatbot model:** Llama-2-7B shape, parameters, weight bytes, KV bytes per token, context window
   - **Chatbot traffic:** conversations per day, concurrency, tokens per conversation and per call, calls per day, RAG queries per day, peak rate, peak-to-average ratio
   - **Knowledge corpus:** documents, tokens, chunks, vector bytes
   - **Prices:** token prices, GPU-hour, node-hour
   - **GPU constants** against Table 64.4, §64.5.2 and §65's achieved bandwidths
3. **Cross-references.** All `§N.M[.K]` references in Ch 71–75 (44, 43, 55, 36 and 60 distinct targets after edits) were resolved by script against the actual headings of all 80 chapter files, and every target was printed with its title for a topic check. Chapter-level references to Ch 76+ were checked against `01-master-toc.md`. All 82 inbound references from Ch 1–70 to Ch 71–75 were read on topic; the inbound files touched were re-resolved afterwards (the only unresolved targets are the forward references §81.7 and §85.4, which match the TOC, as in wave 11).
4. **Numbers.** About 330 numbers in the 63 `example` callouts of Ch 71–75, their formulas and in their assumption notes were recomputed with `python3` (list below). All 24 Python listings were extracted and run with `OMP_NUM_THREADS=1 python3 -I` (NumPy, SciPy, scikit-learn, PyTorch CPU). Every output matches the chapter verbatim. The second Ch 74 listing (IVF) continues the session of the first, as the text says, and was run concatenated with it.
5. **Terminology and spelling.** Grepped against `terminology.md` and for British spellings and unit spellings (kB/KB, FLOP/FLOPs per byte).

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in Ch 1–75. Word counts after edits: Ch 71 13,933; Ch 72 14,942; Ch 73 15,936 (cap 16,000; additions offset by removing a resolved open-verification item); Ch 74 13,936; Ch 75 14,982. The in-progress Ch 76, 77, 79 and 80 report missing end matter and a heading skip, which is expected while they are drafted.
- `python3 build/build.py --chapters 71-75 --name qa --formats html`: 1,121 diagrams across 80 chapters rendered with **0 errors**. The wave 11 render error in Ch 73's `sequenceDiagram` has been fixed by its author. The `qa` volume contains all 78 Ch 71–75 diagrams as inline SVG, and the edited text (#1–#6, #9, #12) appears as intended in the rendered HTML.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices` was restored with `git checkout`.
- Modified files: chapters 4, 9, 12, 56, 57, 58, 59, 62, 63, 64, 65, 66, 67, 69, 70, 71–75, plus this report. No figure or table was renumbered. This review committed nothing. Coordinator WIP snapshots taken during the review (`4f9aaed`, `86a6b5e`) already contain all the chapter edits; this report is uncommitted.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 75 | §75.7.1 worked example "Embedding QuickBite's two corpora", assumptions | S1 | **Wrong FLOP count.** "$2 \times 3 \times 10^8 = 6 \times 10^{11}$ FLOPs per token, so this is 12% of 989 TFLOP/s". The product is $6 \times 10^8$. At $6 \times 10^{11}$, 200,000 tokens/s would need 121 times the H100's peak. The 12% figure is right for $6 \times 10^8$. | Now $6 \times 10^{8}$. No other number changes. |
| 2 | 74 vs 75 | Opening assumptions note; §74.5.2 "Support chatbot retrieval"; §74.14 worked example step 7 | S2 | **Chatbot corpus and traffic contradict Ch 75 and the agent brief.** Ch 74 said "8,000 articles split into about 60,000 chunks", "15 retrieval queries per second" and "184 MB". Ch 75 (and the brief) use 8,400 documents, 25,800 chunks and 8 queries/s at peak. | The note now says the support knowledge corpus is about 25,800 chunks at 8 queries/s peak ("both from Chapter 75"). §74.5.2: $25{,}800 \times 768 \times 4 = 79$ MB; one query reads it in about 4 ms at 20 GB/s, or about 1 ms across a few cores. §74.14 step 7: "(79 MB, 8 QPS)". The conclusion (exact search, no ANN infrastructure) is unchanged. |
| 3 | 75 vs 61, 72, 73 | Opening assumptions note ("New in this chapter") | S2 | **Conversations per day contradict Table 61.1 and Ch 72–73.** Ch 75 had "6% of orders open a support chat, so 30,000 conversations a day with 2.5 user messages each". Table 61.1, §72.4.5 and Ch 73 use 10,000 chatbot conversations a day (2% of orders) of six turns, 60,000 LLM calls. The note also tied 8 queries/s to "200 concurrent conversations of Chapter 64 sending a message every 25 s". Both 10,000 conversations and 75,000 RAG queries are in the brief, and Ch 75's 30,000/day also generates the 21.9-million-case corpus (30,000 × 730 days), so neither number could simply change. | The note now says 6% of orders open a support conversation, 30,000 a day: the 10,000 chatbot conversations of Chapters 72–73 (2%, Table 61.1) plus 20,000 handled by human agents with a retrieval assistant. At 2.5 retrieval queries per conversation on average (six per chatbot conversation, fewer for agents; 60,000 + 15,000), the total is about 75,000 queries a day, peaking at 8/s. The Chapter 64 concurrency clause was removed. Every downstream Ch 75 number (21.9 M cases, \$0.0047 per conversation, \$141/day) and Ch 76's "75,000 queries a day from 30,000 conversations" stay valid. |
| 4 | 75 vs 73 | Ch 75 opening note (token prices); §73.15.1 worked example step 6 and interpretation | S2 | **The two chapters describe the token prices differently.** Ch 75 called \$0.20/\$0.60 per million "an illustrative internal transfer price for the self-hosted 7B model (Chapter 73 derives such prices from GPU-hours)". Ch 73 called them "the API prices assumed in Chapter 75" and concluded "a hosted API at the assumed prices would cost a sixth as much". Ch 73 actually derives \$1.26 per million tokens for QuickBite's dedicated fleet, so the prices are not what it derives. The in-progress Ch 78 treats them as an in-house transfer price. | Ch 75 now says §73.15.1 derives per-token costs from GPU-hours, that a dedicated 7B fleet at QuickBite's volume costs about \$1.26 per million tokens, and that these prices assume a shared, well-utilized platform (Chapter 79). Ch 73 step 6 now says "per-token prices assumed in Chapter 75". The interpretation now says billing the same traffic at those prices, "which assume a shared, well-utilized fleet, would recover only a sixth of it". Arithmetic unchanged (\$20.9 vs \$120 a day). |
| 5 | 75 vs 74 | §75.13.1 Metrics, before the formula | S2 | **One term, two definitions.** §74.6 defines recall@$k$ as overlap with the *exact-search* top $k$, divided by $k$. §75.13.1 defines it as *labeled relevant* chunks found, divided by the number of relevant chunks. Neither chapter pointed out the difference. | Added: "Unlike the ANN recall@$k$ of §74.6, which measures agreement with exact search, recall@$k$ here counts labeled relevant chunks found." |
| 6 | 75 vs 73 | §75.15.1 worked example "QuickBite's p50 path" (prefill) | S3 | **Unstated throughput assumption differs from the owner chapter.** The 4,050-token prefill used $2.47 \times 10^{14}$ FLOP/s (the reranker's $u = 0.25$ from §75.9.2) and gave 230 ms. Ch 73 assumes 50% MFU, 494.5 TFLOP/s, for the same model on the same GPU, which gives 115 ms. Both are defensible, but the reuse was silent. Recomputing would change 575 ms, Figure 75.15, §75.16.3 and the summary, and Ch 76 (in progress) already cites "575 ms TTFT from §75.15". | The assumption is now explicit: "at the reranker's 25% utilization, $2.47 \times 10^{14}$ FLOP/s, $= 230$ ms (conservative for a busy shared GPU; Chapter 73's 50% MFU would give 115 ms)". Numbers unchanged. |
| 7 | 73 → 72 | §73.5.1, after Table 73.3 | S3 | Wrong cross-reference: "Some newer architectures cache a compressed latent instead (Chapter 72)". Ch 72 does not discuss latent KV compression. | Now "Some newer architectures, such as DeepSeek-V2's multi-head latent attention, cache a compressed latent instead." |
| 8 | 72 | §72.5 worked example "Three vocabularies", step 3 | S3 | Llama-3-8B output head "about 7.5% of the model's matrix-multiply FLOPs". $1.05 / (2 \times (8.03 - 0.525)) = 7.0\%$. | Now "about 7%". |
| 9 | 72, 75 | Ch 72 opening note; Ch 75 opening note, §75.4, §75.7, §75.13, Figure 75.15 reading | S3 | **Chapter-level references written as sections:**<br>• Ch 72: "(§67)"<br>• Ch 75: "(§64)", "(§22)", "(§69)", "(§63)", "(§4)"<br>Ch 75 also cited "(Chapter 67)" for the H100's 989 TFLOP/s, which is a Table 64.4 constant. | Now:<br>• Ch 72: §67.6<br>• Ch 75: §64.13 (the 8,192-token chatbot example), §22.3, §69.8.3, "Chapter 63", §4.10 and Table 64.4 |
| 10 | 71, 72, 73 | Ch 71 Figures 71.2, 71.5, 71.6 and 71.8 readings; Ch 73 opening note, §73.9, §73.11; Ch 72 §72.8 | S3 | **Terminology and units:**<br>• Ch 71: "scoring path" and "Scoring hands…" where `terminology.md` prefers "inference" (×4)<br>• Ch 73: "kB" in prose (×4) where the book uses KB; "FLOP/byte" (×5) where Ch 64 and Ch 72 use "FLOPs/byte"<br>• Ch 72: British "travelling" | Now:<br>• Ch 71: "inference path" and "Inference…"<br>• Ch 73: KB in prose (the listing prints "kB" and was left verbatim); FLOPs/byte<br>• Ch 72: "traveling"<br>Kept: "social scoring" (an EU AI Act term), ANN "rescoring" and "harmonised" (in the EU regulation's title). |
| 11 | 73 | §73.24 Open verification items | S3 | The item "Chapter 72 cross-references (§72.4.5, §72.7, §72.8.2, §72.10–§72.15) were checked … re-check if it is renumbered" is resolved: Ch 72 is final, and all Ch 73 → Ch 72 references resolve on topic. It is not in `unresolved-questions.md`. | Removed. This also offsets the words added by #4 and #7 under Ch 73's 16,000-word cap. |
| 12 | 72–75 siblings | Chapter-level references between the five chapters | S3 | Ch 72 was drafted before Ch 73 and pointed to "Chapter 73" eleven times. Ch 74 and Ch 75 cited each other and Ch 73 by chapter number for specific mechanisms. | Made precise:<br>• **Ch 72 → 73:** batching and sharding → §73.6, §73.11; shared prefix → §73.8; output-head sharding and KV-head splitting → §73.11; batch/chunk/disaggregate (×2) → §73.6, §73.14, §73.12; GQA, FP8 KV, TP, offloading → §73.5, §73.13, §73.11; paged allocation → §73.7; chunked prefill → §73.14<br>• **Ch 73 → 75:** retrieved documents as shared prefixes → §75.11<br>• **Ch 74 → 75:** chunking → §75.6; hybrid retrieval (×2) → §75.8.3<br>• **Ch 75 → 73/74:** prefix caching and cost → §73.8, §73.15; prefix cache (×3) → §73.8; ANN index → §74.7–§74.10; HNSW build → §74.7; quantization and partitioning → §74.9, §74.14<br>Overview references ("Chapter 73 builds its serving architecture…", "Chapter 74 owns these topics") were kept at chapter level. |
| 13 | 4, 9, 12, 56–70 → 71–75 | Inbound chapter-level references | S3 | All 82 inbound references resolve on topic, with two imprecisions:<br>• §58.9 and §67.6 credited the KV cache and its 327,680-byte formula to Chapter 73, which §4.5's split assigns to §72.11<br>• Ch 65 credited the $2N$ inference FLOPs to Chapter 73 (they are §72.15)<br>The other topic-specific references said only "Chapter 71–75". | 23 references made precise (by source chapter):<br>• **Ch 4:** recall–latency → §74.6<br>• **Ch 9:** TTFT → §73.4<br>• **Ch 12:** vector database design → §74.13<br>• **Ch 56:** incremental insertion plus rebuild → §74.12<br>• **Ch 57:** approximate explanations → §71.7<br>• **Ch 58:** KV cache → §72.11; FlashAttention → §73.9; attention's $n^2$ cost → §72.6<br>• **Ch 59:** fairness metrics → §71.4, mitigation → §71.6<br>• **Ch 62:** privacy techniques → §71.9–§71.11<br>• **Ch 63:** differential privacy → §71.10<br>• **Ch 64:** KV reads growing with batch → §73.3; continuous batching and disaggregation → §73.6, §73.12; FlashAttention FP8 → §73.9<br>• **Ch 65:** $2N$ FLOPs per token → §72.15<br>• **Ch 66:** LLM batching mechanisms → §73.6–§73.7; LLM parallelism → §73.11<br>• **Ch 67:** 327,680 B/token → §72.11; KV bottleneck → §73.5; paging, sharing, KV quantization → §73.7, §73.8, §73.13<br>• **Ch 69:** model-card content → §71.12; high-risk obligations → §71.13.1<br>• **Ch 70:** query drift for RAG → §75.15.4<br>List and overview references were kept at chapter level, among them Ch 3's roadmap, Ch 59's chapter map, Ch 66–67's ownership notes and Ch 16's bridge. |
| 14 | 71–75 | Ownership measurement | — | Non-owner passages flagged by the script, plus the sections named in the brief, were read:<br>• **§72.10.1 (1,067 words, 4 quantization hits).** Mentions INT8/INT4 weight bytes and FP8 KV in passing and cites §67.6; Ch 73 owns the serving trade-offs.<br>• **§72.11.1 (824) and §73.5.1 (1,156) KV cache.** Ch 72 derives $M_\text{KV}$ and per-token sizes (Table 72.6 calculator); §73.5 cites §72.11 for $k$ and adds the memory budget, $S_\text{max}$ and the 70B TP split. Complementary, not duplicated.<br>• **§73.13.1 (635).** States "Chapter 67 owns GPTQ, AWQ, SmoothQuant and FP8 recipes" and adds only serving plans (Table 73.6) and KV quantization, per §4.5.<br>• **§75.6.3 (426, 4 vector-database hits).** Sizes the index with $g$ for HNSW links and defers to Chapter 74 (now §74.9, §74.14). §75.8.1 dense retrieval is 105 words. Ch 75 nowhere re-teaches HNSW, IVF or PQ.<br>• **§75.3.2 (279) and §75.3.3 (309).** One comparison table and "Chapter 76 develops the decision between the two; the short rule is fine-tune for behavior, retrieve for knowledge": a preview, as allowed.<br>• **§75.11.4 (232).** Indirect prompt injection with four defense layers; "Chapter 78 treats them in depth".<br>• **§75.12 (416, 4 evaluation hits).** Citation verification and refusal design; the judge is cited to Chapter 78. §75.13.4 (112) is titled "preview of Chapter 78".<br>• **§75.16.2 (112).** Agentic retrieval; defers to Chapter 77.<br>• **Ch 71.** Uses §50.11's Laplace mechanism and composition "used, not redefined"; model cards cite §59.10.3 and datasheets §63.13. | No non-owner passage re-teaches an owned concept; no condensation needed. |
| 15 | 2, 58, 60, 61, 64, 65, 67, 71–75 | Recurring facts | — | Consistent across chapters (after #2–#4):<br>• **Chatbot model:** Llama-2-7B shape: $L = 32$, $d = 4{,}096$, 32 heads and 32 KV heads of 128, $d_\text{ff} = 11{,}008$, $V = 32{,}000$; 6,738,415,616 parameters (Ch 72 table = listing); 13.5 GB BF16, rounded to 14 GB in Ch 64, 67 and 73 (stated); KV 524,288 B/token = 524 KB (Ch 72, 73); 70B shape $L = 80$, 8 KV heads, 327,680 B/token (Ch 67, 72, 73)<br>• **Context:** 8,192-token window (§64.13, Ch 75); Ch 73 reserves a 4,096-token maximum per request in its paging example (see Remaining risks)<br>• **Chatbot traffic:** 10,000 conversations/day (Table 61.1, Ch 72, 73, 75); 200 concurrent at peak (Ch 64, 72, 73); 9,063 input + 468 output tokens per conversation, 1,510 + 78 per call, 1,866 final context, 60,000 calls/day, 95.3 M tokens/day, 6.9 req/s peak (Ch 72, 73); 75,000 RAG queries/day, 8/s peak, 0.87/s average (Ch 75; the brief)<br>• **Corpus:** 8,400 documents, 8.6 M tokens, 25,800 chunks, 87.7 MB with graph and metadata, 79 MB of FP32 vectors (Ch 74 after #2, Ch 75); 21.9 M resolved cases<br>• **Prices:** \$0.20/M input and \$0.60/M output (Ch 73, 75); \$2.50/GPU-h and \$0.77 per 16-vCPU node-hour (§60.11, Ch 73, 75)<br>• **GPU constants:** H100 SXM 80 GB, 3.35 TB/s, 989 TFLOP/s dense BF16 (Ch 72, 73, 74, 75 = Table 64.4); ridge 295 FLOPs/byte; H200 141 GB, 4.8 TB/s (§64.5.2, Ch 74); NVLink 360 GB/s and InfiniBand 40 GB/s achieved, 400 Gb/s = 50 GB/s NIC (§65, Ch 73); DDR5 socket ~300 GB/s (§5.5, Ch 74); 4.2 ms BF16 7B decode bound (§64.9.2) reconciled in §72.10 (4.3 ms with 13.5 GB + KV)<br>• **Book I and Part XI numbers reused:** 2,000 search RPS, 300 ms p99 (§2.4, Ch 74); 5 M dishes, 120,000 per address (§58.6, §68.3, Ch 74); 3,500 fraud holds/day at 50% precision and 70% recall (Ch 70; Table 71.1 totals) | No action beyond #2–#4. |
| 16 | 71–75 | Terminology | — | **Terms:** "master" only in a GitHub URL; "hit rate" for prefix-cache reuse in Ch 73 (acceptable synonym); "QPS" in Ch 74, defined in §74.6, plus one earlier use in a §74.5.2 inequality; "ground truth" in Ch 74 means exact-search results (an ANN benchmarking term), not labels; no "slave", "uptime", "message bus". **Spelling:** no other British spellings (the grep hits were "raise", "noise", "supervised", "enterprise", "elementwise", "pairwise", "listwise"). | #10 only. |

**Counts:** S1 = 1 (fixed) · S2 = 4 (fixed) · S3 = 8 (fixed) · 3 checked with no action needed (#14–#16).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 24 Python listings were run with `OMP_NUM_THREADS=1 python3 -I`. All matched verbatim; none is timing-dependent.
   - **Ch 71 (5):** fairness metrics on synthetic data; group thresholds (thresholds 0.111/0.230, \$57,496); SHAP; DP-SGD accountant ($\varepsilon = 1.26$); FedAvg
   - **Ch 72 (8):** BPE; UTF-8 bytes; attention by NumPy; parameter counts (6,738,415,616; 8,030,261,248; 70,553,706,496; RoPE scores); incremental KV cache; KV calculator; sampling; MoE routing
   - **Ch 73 (3):** step-time and batching simulator; scheduler; capacity planner (60,000 calls, 6.9 req/s, 95 M tokens)
   - **Ch 74 (4):** HNSW-style graph; IVF sweep (continues the graph session); PQ; filtering
   - **Ch 75 (4):** structural chunking; BM25 + dense + RRF; context builder; retrieval metrics
2. **§71.4–§71.5 fairness.**
   - **Table 71.1:** selection 0.525% vs 1.40%; DP ratio 0.375; TPR 68.8/72.2%; FPR 0.251/0.757%, ratio 3.0; PPV 52.4/46.4%.
   - **Chouldechova:** 0.757% reproduced; 0.281% vs 0.636%, ratio 2.26 = odds ratio.
   - **Wilson interval:** $\tilde p = 0.6825$, $h = 0.1368$, [0.546, 0.819]; $n_\text{req} = 19{,}112$, about 150 days at 125 orders/zone/day.
3. **§71.6–§71.11 mitigation, explanation, privacy.**
   - **Reweighing:** 1.250 / 0.556 / 0.999 / 1.004; 0.5% after weighting.
   - **Group thresholds:** \$57,496 vs \$55,520 (+3.6%), \$0.72 M/year.
   - **Shapley:** 3.5 / 1.0 / 1.5.
   - **TreeSHAP:** 384×; $6.9 \times 10^7$ and $4.6 \times 10^{10}$ ops/s; 204,800 calls.
   - **Membership inference:** 0.166%, 0.74%, $e^8 = 2{,}981$.
   - **RDP:** minimum 15.13 at $\alpha = 3$.
   - **FedAvg:** 0.35; 1.6 GB/round, 800 GB, 10 rounds and 16 MB per courier; masks sum to 14.
4. **§72.3–§72.5 tokens.** Perplexity: 5.116 nats, 1.279/token, 1.85 bits, 3.59. BPE pair counts and merge order. Chatbot budget: 9,063 input, 468 output, 1,866 final context, 90.6 M/4.7 M per day; 10,926 (+21%) at $r = 2.6$; 79% prompt share. Vocabularies: 38.6 M (31%), 262 M (3.9%), 1.05 B (13%).
5. **§72.6–§72.9 attention and shapes.**
   - **Attention:** weights 0.446/0.108/0.446, output 18.8; $2.75 \times 10^{11}$ FLOPs per layer at 4K.
   - **GQA:** 67.1 / 41.9 / 34.6 M; 524/131/16 KB per token; 0.98 GB per conversation; 196/49/6 GB at 200 concurrent.
   - **Parameter table:** sums exactly; $12Ld^2$ within 4.4%; 67% MLP; $d_\text{ff} = 11{,}008 = 43 \times 256$.
   - **RoPE:** $\lambda_{63}$ = 54,400 and 2.56 M tokens.
6. **§72.10–§72.15 inference arithmetic.**
   - **Prefill:** $2.82 \times 10^{13}$ FLOPs, $I$ = 1,930, 28.5 / 47.5 / 4.4 ms.
   - **Decode:** 4.3 ms (230 tok/s); 9.2 ms (1,740); 19.4 ms (2,470, $I$ = 10.6, KV 79%); GQA-8 8.6 ms (5,550, 2.2×).
   - **KV calculator:** 2.15 / 68.7 GB; 0.54 / 17.2; 1.34 / 42.9; 10.7 / 344; concurrency 27/0, 104/3, 109/3.
   - **Table 72.7:** all five rows, including 96 ms at 4K and 8.5 min at 1M; crossovers 24,576 and 49,152.
   - **Sampling:** 0.512, 0.761, nucleus 0.896 → four tokens, 0.530.
   - **Mixtral shape:** 176.2 M per expert, 46.7 B / 12.9 B, 7.2 and 7.9 experts.
   - **FLOPs conventions:** +16% / +130% / +520%; 14% PaLM term; 43,000 tokens/s.
7. **§73.3–§73.5 serving basics.**
   - **Batch 1 / 64:** 7.53 ms, 133 tok/s; 26.6 ms, 2,404 tok/s (18×, 3.5× slower); prefill 42.8 ms, attention +2.8%.
   - **Latency:** TTFT 94.8 ms, end-to-end 2.14 s (96% decode).
   - **Goodput:** 12.3 req/s at 14 (12% miss); 1 + 1 replicas.
   - **Memory:** 102,997 tokens, 64 / 55 / 25 sequences (−61%); 70B 402,832 tokens, 253 calls, 97 vs 63 per GPU, 3.9×.
8. **§73.6–§73.10 batching, paging, prefix, kernels, speculation.**
   - **Static batching:** $\eta$ = 36%.
   - **Paging:** 61% vs 0.47% waste; 25 vs 64 sequences, 14.8 ms, 1,689 vs 2,404 tok/s (+42%); parallel sampling 3.33 vs 0.96 GB (−71%), 94 blocks + 6.
   - **Prefix cache:** $h$ = 0.66, 14.5 ms, 0.047 GPU-s (−38%); $h$ = 0.956, 1.9 ms; swap 20 ms vs 53 ms; $S'$ = 173; 59.6 ms vs 26.0 ms and 6,650 tok/s; \$1.18/day.
   - **FlashAttention:** ~6× fewer HBM accesses, 134 MB per head; $I_\text{dec}$ 1 and 8; 24% of SMs, 3.9 blocks/SM.
   - **Speculation:** $E$ = 3.36, $S$ = 2.80 (9.5 ms); 2.31/1.92; 1.43/0.79. 70B at batch 253: 89.5 / 91.5 / 96.9 ms, 0.94×; 7B 9.1 ms.
9. **§73.11–§73.17 parallelism, disaggregation, quantization, capacity.**
   - **TP:** 3.93 MB/token/GPU; 994 MB, 2.8 + 1.3 ms; prefill 5.94 GB, 16.5 vs 106.9 ms, 148 ms across nodes; PP 16 KB, 0.1 ms; EP 32.8 KB/layer, 1.05 MB.
   - **Disaggregation:** 15.8 ms, $R$ = 0.37; 2.5 ms, $R$ = 0.023; 42.8 vs 32.4 ms.
   - **Table 73.6:** 64 / 129 / 77 / 154 sequences, 26.6–26.8 ms, 2,404 / 4,819 / 2,886 / 5,772 tok/s (2.0×, 1.2×, 2.4×).
   - **Preemption:** swap 39 vs 53 ms; 70B 6.1 vs 132 ms (22×); $C^*$ = 805; 46.5 ms spike (1.7×).
   - **Capacity:** 6.9 req/s, 0.075 GPU-s, 0.52 busy GPUs, 2 replicas, \$120/day, \$1.26/M; \$0.29 / \$0.020 per M (14×); \$20.9 at Chapter 75's prices; 70B 0.461 GPU-s, 3 × 4 GPUs, 216 GPU-h, \$540, \$5.67/M (4.5×); busy floors \$0.033 and \$0.202, routed \$0.067 (−67%).
   - **TPOT constraint:** $B_\text{SLO}$ = 141 and 308.
10. **§74.4–§74.6 similarity and exact search.**
    - **Metrics:** cos 0.96 / 0.8; L2 0.08 / 0.40; MIPS 1.33 vs 0.85.
    - **Brute force at $10^8$:** 307 GB, $1.54 \times 10^{11}$ FLOPs, 1.0 s per query, 614 TB/s; H200 16 ms, $7.7 \times 10^{13}$ FLOPs, 0.16 s, 6,400 q/s, $B^*$ = 206.
    - **Dish filter:** 369 MB and 737 GB/s; recall@10 0.867.
11. **§74.7–§74.11 ANN.**
    - **HNSW:** layers 312,500 / 19,531 / 1,221 / 76 / 5, $\log_{16} N$ = 5.6; 132 B links, 16.0 GB (4%), SQ 4.5 GB (15%), $M = 32$ 260 B.
    - **IVF:** $\sqrt{N}$ = 2,236 → 2,048, 2,441 per list, $C$ = 41,111 (0.82%, 122×); $nlist^*$ = 8,944, $C$ = 17,888 (0.36%), 27 MB centroids.
    - **PQ:** 96 B (32×), 9.6 GB, 786 KB codebooks, 98 KB table; toy ADC 0 and 3.
    - **Post-filtering:** $s$ = 0.024, $E$ = 0.96; $P(\ge 10)$ = 0.0002 at 100; $k'$ = 778 / 183 / 1,874 (binomial tail); city index $k'$ = 34.
12. **§74.14 capacity.** 334 GB → 2 shards and 6 nodes; SQ 104 GB; IVF-PQ 10.4 GB; dishes 4.5 GB + 15.4 GB; 4 and 20 cores (encoder 5× the search).
13. **§75.6–§75.7 chunking and embedding.**
    - **Chunk counts:** 3 / 17 / 2 per document → 9,000 + 6,800 + 10,000 = 25,800; 3,400 B → 87.7 MB; text 41.3 MB.
    - **Case corpus:** 74.5 GB FP32, 24.0 GB INT8, 849×.
    - **Chunk-size table:** 49,143 / 24,571 / 12,286 (167 / 83.5 / 41.8 MB; 24,571 is 4.8% below 25,800).
    - **Embedding:** 10.6 M tokens, 53 s, \$0.04 vs \$0.53; 6.13 B tokens, 64 min, \$21 vs \$307; 8.4 M/day, 42 GPU-s; 12% utilization (after #1).
14. **§75.8–§75.11 retrieval and context.**
    - **RRF:** 0.032522, 0.031778, 0.016129, 0.015873 (tie), 0.015625; $2/90$ = 0.0222 > $1/61$.
    - **Reranking:** 54.4 / 59 / 223 ms; cascade 23.9 + 32.6 + 10 = 66.5 ms; 0.47 GPU-s/s; \$0.000094 and \$7/day; LLM reranker 0.68 s.
    - **Token budget:** $B$ = 5,882, $k_\text{max}$ = 13, prompt 4,050 (65% retrieved).
    - **Retrieval metrics:** recall 1.0 / 0.5, RR 1.0, nDCG@5 = 3.387/3.631 = 0.933.
15. **§75.15–§75.16 production.**
    - **TTFT:** 230 ms prefill at the stated 25% (115 ms at Chapter 73's 50%), 575 ms, 5.6 s, first message 425 ms; retrieval 21 ms (3.7%), model calls 83%.
    - **Cost:** \$1,686/month; \$0.000930 + 0.000108 + 0.000094 + 0.000749 = \$0.00188; \$0.0047 per conversation; \$141/day; context 28%; cache saving 7%; fixed share 40% → 6% at 10× traffic.
    - **Long context:** \$0.0256 (32×), 7.3 s.
    - **Peak rate:** $75{,}000/86{,}400 \times 9.6 = 8.3$/s.
16. **Concepts checked against the text.**
    - PagedAttention waste is internal fragmentation of at most one block per sequence; copy-on-write shares prompt blocks across parallel samples (§73.7) [Kwon et al. 2023].
    - GQA shrinks KV bytes by $h/g$ but attention parameters by less (§72.7).
    - Speculative sampling preserves the target distribution; $\alpha = \sum \min(p, q)$ (§73.10) [Leviathan et al. 2023].
    - RRF $k = 60$ from the original paper; pgvector's `ef_search = 40` filter example (4 of 40 rows at 10% selectivity) and its $\sqrt{N}$ lists rule above 1 M rows (§74.8, §74.11).
    - DPR's 9–19-point top-20 gain over BM25 (§75.8.1) [Karpukhin et al. 2020].
    - DP-SGD clips per example, then adds Gaussian noise scaled to $C$; subsampling amplifies privacy (§71.10) [Abadi et al. 2016].
    - The four-fifths rule is a screening heuristic from US employment selection, not a legal definition of fairness (§71.4).
17. **Cross-references.**
    - **Outbound:** every `§` reference in Ch 71–75 resolves to an existing section on its topic. Forward references are Chapters 76 (adaptation, RAG vs fine-tuning), 77 (agents, tool permissions), 78 (evaluation, prompt injection, routing), 79 (multi-model platforms, token rate limits) and 80; all match the TOC.
    - **Book I targets checked:** §4.8–§4.11, §4.9.2–§4.9.3; §5.5; §6.6.2, §6.6.5; §9.5; §12.10; §13.8–§13.9; §14.3, §14.6, §14.8; §16.3–§16.11, §16.6.2, §16.7.3, §16.10.2; §20.3, §20.7, §20.10, §20.10.2; §22.3, §22.9; §39.6; §40.4; §47.4, §47.5.2, §47.12; §50.8–§50.11.3.

## Remaining risks

- **RAG-era call profile versus Chapter 73's sizing.** Ch 73 sizes the chatbot for pre-RAG calls of 1,510 input and 78 output tokens: a 1,000-token system prompt, a 4,096-token maximum per request, 64 sequences per GPU and 6.9 req/s. Ch 75's RAG call is 4,050 input and 200 output tokens (a 700-token system prompt plus 2,640 retrieved), in an 8,192-token window. That roughly doubles KV per call, prefill and output time, so Ch 73's two-GPU plan does not carry over unchanged. Each chapter is internally consistent; Ch 79 or the chatbot case study (Ch 85) should re-size the fleet for the RAG profile.
- **Two prefill-throughput assumptions.** Ch 75's 575 ms TTFT uses 25% utilization; Ch 73 uses 50% MFU. #6 makes this explicit rather than recomputing, because Ch 76 (in progress) already cites 575 ms. If Ch 75 is ever recomputed at 50%: TTFT 460 ms, first message 310 ms, model calls 79%.
- **Peak-to-average ratio.** Ch 73 uses 10 (as for orders); Ch 60 and Ch 75 use 9.6. The resulting rates, 6.9/s and 8/s, are stated per chapter.
- **In-progress Ch 76–80.** Their drafts reuse Ch 75's 30,000 conversations, 75,000 queries, 575 ms and "in-house transfer price"; all remain valid after this review. Ch 78 (line 12) and Ch 79 should cite §75.15 rather than "§75", and should describe the 30,000 as chatbot plus human-agent conversations (#3).
- **Unverified hardware details.** The H100's ~228 KB shared memory per SM and 132 SMs (Ch 73), and DeepSeek-V2 as the example of latent KV caching (#7), were not re-verified against primary sources here.
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–11.
- **Perishable facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 71:** EU AI Act timeline after the Digital Omnibus; Abadi et al. accuracies; Carlini et al. extraction count; SCHUFA and CFPB scope
  - **Ch 72:** Llama 3 tokenizer compression and 128K extension; Chinchilla constants; Pope et al. and Ainslie et al. figures; DeepSeek-V3 parameter counts
  - **Ch 73:** TGI maintenance-mode date; engine defaults (`gpu_memory_utilization`, preemption mode); speed-ups reported by Orca, vLLM, SGLang, DistServe, Splitwise, Sarathi-Serve, FlashAttention-3, Flash-Decoding, Medusa and EAGLE
  - **Ch 74:** Qdrant, Weaviate (ACORN default), Elasticsearch and OpenSearch defaults and URLs (§74.13.2); Matryoshka "up to 14×" wording
  - **Ch 75:** DoorDash reported reductions; Liu et al. position effect; OWASP LLM Top 10 ordering (2025); author lists of Xu et al. and Edge et al.
