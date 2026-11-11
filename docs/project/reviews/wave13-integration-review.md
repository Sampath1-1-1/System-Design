# Wave 13 Integration Review — Chapters 76–80 (Part XVI close: LLM Adaptation, AI Agents, LLM Evaluation, Production AI Infrastructure, Large-Scale AI Infrastructure)

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-11 · **Scope:** QA Reviews 2 (technical accuracy), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* five chapters drafted in parallel:

- 76 LLM adaptation: prompting, fine-tuning and alignment pipelines
- 77 AI agents and agentic systems
- 78 LLM evaluation and reliability
- 79 production AI infrastructure
- 80 large-scale AI infrastructure

The review also covered their interfaces with Book I (Ch 1–56), Parts XI–XV (Ch 57–70) and Ch 71–75, and the Ch 81–86 plan in `01-master-toc.md`. The reference standard is `style-guide.md`, `terminology.md`, the Book II additions and QuickBite shared assumptions in `agent-brief.md` (including the Ch 77–79 assumptions), and `04-agent-allocation.md` §4.5. Ch 81–86 were being drafted in parallel by other agents during this review; they were not touched, and their QA findings are out of scope. The ownership split for this wave:

| Owner | Topics |
|---|---|
| Book I | Queueing and Erlang C (§4.10.4), Little's law (§4.6), object storage (§15.4), retries, budgets, breakers, idempotency (§22.11–§22.15), workflow engines and sagas (§32.7, §32.11), SLOs and error budgets (§39.6–§39.7), tracing (§40.6–§40.7), multi-region and residency (§44.4–§44.9), gang scheduling and Slurm (§46.10–§46.12), tenancy, quotas, isolation (§47.4–§47.12), RDMA, fabrics, parallel file systems (§49.9–§49.11), authorization and privacy engineering (§50.5, §50.8–§50.10), FinOps, build versus buy, PUE and carbon (§51.4–§51.11) |
| Parts XI–XIII | A/B statistics (§57.14); learning-rate schedules (§58.5.3); cascades (§60.13.2); annotation quality and synthetic data (§63.5–§63.12); GPU hardware and MIG (Table 64.4, §64.14–§64.15); training FLOPs, ZeRO/FSDP, checkpointing, Young/Daly, Llama 3 failure statistics (§65.4, §65.9, §65.15–§65.16) |
| Ch 66–75 | Model serving and safe deployment (§66.8–§66.12); general quantization and distillation (§67.6, §67.8); registry (§69.8); KV cache (§72.11); single-model LLM serving, prefix caching, capacity (§73.5, §73.8, §73.15, §73.17); RAG, grounded generation, retrieval metrics (§75.11–§75.15) |
| Ch 76 | Adaptation ladder, prompts as artifacts, **structured output and function-calling formats (§76.5)**, ICL limits, SFT, LoRA/QLoRA, multi-LoRA serving, RLHF/DPO, adaptation data pipelines, **RAG versus fine-tuning (§76.14)** |
| Ch 77 | **Agent architecture, tool calling, MCP**, planning patterns, memory, durable execution, multi-agent systems, guardrails, human-in-the-loop, **agent security**, agent cost and latency |
| Ch 78 | **Evaluation methodology, LLM-as-a-judge, hallucination**, RAG evaluation, online evaluation, safety, **prompt injection (deep)**, **model routing policy and fallbacks**, cost–quality frontier |
| Ch 79 | **Platform implementation**: gateways, inference routers, multi-model serving, GPU pools, token quotas, tenant isolation, multi-region, caching, observability, privacy, chargeback, build versus buy |
| Ch 80 | **Training-cluster facilities, networking and reliability**: fabrics, storage bursts, power and cooling, job MTBF, SDC, goodput, spares, stragglers, scheduling, published infrastructure, economics, sustainability |

**Method.** Targeted grep, scripted checks and reading, following the wave 12 method.

1. **Ownership.** A scratch script word-counted every `##`/`###` block in Ch 76–80 (code excluded) and counted keyword hits for ten owned topics (injection, judging and evaluation, routing and fallbacks, gateways and quotas, prefix caching and batching, LoRA, MCP and tool calls, checkpointing and MTBF, quantization, RDMA fabrics). Every block over 300 words with four or more hits for a topic it does not own was read against its owner, together with the overlaps named in the brief: 77/78 (agent evaluation, injection), 78/79 (routing, fallbacks, caching), 73/79 (serving, prefix caching), 65/80 (failure statistics), 76/79 (multi-LoRA). Results are in #9, #10 and #15.
2. **Recurring facts.** Extracted and compared across Ch 44, 60, 63, 64, 65, 72, 73, 75 and 76–80, against the agent brief:
   - **Chatbot model and traffic:** Llama-2-7B shape and bytes; 10,000 chatbot + 20,000 human-agent conversations; 75,000 RAG queries/day, 8/s peak; tokens per query
   - **Prices:** \$0.20/\$0.60 internal; hosted \$2.50/\$10/\$0.25 cached; small-model API \$0.15/\$0.60; \$2.50 per GPU-hour
   - **Support economics:** human contact \$3.00, 20% escalation, annotator and reviewer rates
   - **QuickBite support policy:** late-delivery credit and refund rules
   - **Training-cluster constants:** 50,700 GPU-hours per failure, 3.1 h job MTBF, $\delta$ = 20 s, $R$ = 600 s, 668 s Young interval, 88.6% goodput; H100 constants against Table 64.4 and Ch 65's round numbers
   - **Fleet sizing:** Ch 73's 1,510-token plan, Ch 75's RAG profile and Ch 79's capacity plan (the wave 12 remaining risk; see #1)
3. **Cross-references.** All `§N.M[.K]` references in Ch 76–80 (50, 58, 47, 66 and 46 distinct targets after edits) were resolved by script against the actual headings of all chapter files, and every target was printed with its title for a topic check. Before edits, eight did not resolve or were chapter-level references written as sections (#11). Chapter-level references to Ch 81–86 were checked against `01-master-toc.md`. All 47 inbound references from Ch 1–75 to Ch 76–80 were read on topic: all are correct, so no Ch 1–75 file was edited.
4. **Numbers.** About 400 numbers in the `example` callouts, formulas, tables and assumption notes of Ch 76–80 were recomputed with `python3` (list below), including an independent Monte Carlo of the ECMP collision example, Poisson quantiles for the spare pool and Erlang C for the review queue. All 13 Python listings (Ch 76: 4, Ch 77: 3, Ch 78: 3, Ch 79: 2, Ch 80: 1) were extracted and run with `OMP_NUM_THREADS=1 python3 -I`. Every output matches the chapter verbatim; the edited Ch 77 and Ch 78 listings were re-run after edits and still match.
5. **Terminology and spelling.** Grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in Ch 1–80. Word counts after edits (cap 15,000): Ch 76 14,971; Ch 77 14,924; Ch 78 14,889; Ch 79 14,982; Ch 80 14,945. Additions in Ch 77 and Ch 78 were offset by removing duplicated material (#9, #10). The in-progress Ch 81–86 report missing end matter, which is expected while they are drafted.
- `python3 build/build.py --chapters 76-80 --name qa --formats html`: 1,154 diagrams across 86 chapters rendered with **0 errors**. The `qa` volume embeds all 78 Ch 76–80 diagrams as SVG, and the edited text (#1–#14) appears as intended in the rendered HTML.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices` was restored with `git checkout`.
- Modified files: chapters 76, 77, 78, 79 and 80, plus this report. No figure or table was renumbered (one figure caption reworded, #13). This review committed nothing.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 79 vs 73, 75 | Opening assumptions note; used in §79.6.2, §79.8, §79.10, §79.15, §79.16 | S2 | **Output-token cost misattributed, and optimistic for the RAG profile (wave 12 remaining risk).** The note gave "0.567 ms per output token at its memory-limited batch of 46 (decode step 26.1 ms)" as "From Chapter 73 (§73.15)". Ch 73 sizes batch 64 at 26.6 ms (0.42 ms/token) for 1,588-token calls. Ch 79's step model ($T_0$ = 7.2 ms, $T_B$ = 0.41 ms) implies about 2,100 tokens of context per sequence (102,997/46 = 2,239). Ch 75's RAG generation call is 4,050 + 200 tokens. In the 102,997-token pool of §73.5 that caps the batch at 24 (28 with the 700-token system prompt stored once). The step is then 26.7–30.0 ms, about 1.1 ms per output token, so $g_\text{req}$ = 0.36 GPU-s rather than 0.238, 2.9 busy GPUs at peak and 6 replicas rather than 5. Ch 79's 4,500/230 tokens per query are correct as generation plus condensation (§75.15.3), but the note did not say so. | The note now presents batch 46 as this chapter's assumption ("averaging about 2,100 tokens of context"). It says that full-length 4,250-token RAG contexts would cap the batch near 24 and roughly double the output-token cost, so the plans are optimistic, and that Chapter 86 re-sizes the fleet. The tokens per query are now attributed to "its generation and condensation calls (§75.15.3)". The numbers are unchanged, per the brief: re-sizing would cascade through §79.8, §79.10, §79.15, Table 79.6, §79.16 and the summary (see Remaining risks). |
| 2 | 76 vs 73, 79 | §76.6.1 worked example "Three demonstrations", step 5 | S2 | **Unsupported number with a wrong reference.** "with 46 concurrent sequences on a GPU (§73.8) that is 25 GB of KV cache". §73.8 has no 46 (its concurrency figures are 64 and 173). The 46 is Ch 79's assumption (#1), and it does not fit 4,050-token RAG prompts. | Now "with the roughly 24 RAG-length sequences that fill a 103,000-token KV pool (§73.5), 13 GB of KV cache" ($24 \times 550$ MB). The interpretation is unchanged. |
| 3 | 76 vs 73, 79 | §76.9.1 worked example "Twelve chatbot variants", step 2 | S2 | "Three replicas serve every variant (§73.15)." §73.15 sizes two replicas for the chatbot; Ch 79's shared RAG pool has 5 at peak and 2 off-peak. | Now "The shared pool of §79.8 serves every variant." |
| 4 | 78 vs 73, 79 | §78.16 worked example "Choosing between the in-house 7B and the hosted model", step 3 | S2 | "about \$135 a day mostly fixed (§73.15)". §73.15 gives \$120 a day (two GPUs for the pre-RAG profile); Ch 79's RAG-profile pool is 72 GPU-hours a day, \$180. | Now "about \$180 a day, mostly fixed (§79.8)". The conclusion (the marginal in-house cost is below its transfer price) is unchanged. |
| 5 | 78 vs 73 | §78.14.1, before Figure 78.14 | S2 | **Misquoted number.** "routing 80% of calls to the 7B model would cut the blended serving floor by 60% (§73.17)". §73.17 computes \$0.067 against \$0.202, 67% less. | Now 67%. |
| 6 | 78 vs 75 | Opening assumptions note; §78.11 worked example "Sizing an A/B test on handoff rate", steps 3–4 | S2 | **Conversation mix contradicts Ch 75 after wave 12 #3.** The note had "30,000 conversations (2.5 user messages each)" and "20% of conversations are handed off". The A/B test split "about 30,000 conversations a day" 50/50 on the chatbot's handoff rate, reaching the sample "in under 2 days" with "210,000 per arm" over 14 days. Ch 75 (and the brief) define the 30,000 as 10,000 chatbot plus 20,000 human-agent conversations, so only 10,000 a day are in a chatbot A/B test. The note also cited "§72" and "§75" as sections (wave 12 remaining risk). | Note: "30,000 support conversations (10,000 with the chatbot and 20,000 handled by human agents with a retrieval assistant; 2.5 queries each on average)" and "20% of chatbot conversations are handed off". References are now "Chapter 72", "§75.6.3" (the 25,800-chunk count) and "Chapter 75". A/B test: 10,000 chatbot conversations, 5,000 per arm per day, the sample of 24,638 reached in 5 days, about 70,000 per arm over 14 days. The required $n$ and the interpretation ("volume is not the constraint") are unchanged. The availability SLO base (2.25 M messages a month = 75,000 × 30) was already consistent. |
| 7 | 77 vs 75, 78 | §77.11 refund policy, item 3; §77.7.2 semantic-memory example | S2 | **Two QuickBite late-delivery policies.** Ch 75's policy text (also Ch 78's golden answers and examples): more than 20 minutes late gives a **credit of 20% of the food total**. Ch 77's policy engine: late-delivery **refunds** of 50% at 30–59 minutes late and 100% at 60+. The definition example called the latter "the late-delivery policy". The two contradicted each other for the same order. | Item 3 is now scoped: "at most the refund entitlement for late orders with a food complaint, which Chapter 75's automatic 20% late credit does not settle (50% … 100% …)". The memory example now says "the late-order refund policy". Ch 77's opening case (38 minutes late, soup cold), \$12.25, the \$11 average and the \$56,100 fleet cap are all consistent with the scoped rule; no number changes. |
| 8 | 78 vs 77 | Opening assumptions note | S3 | Ch 78's agent has four tools (look up an order, propose a credit, request a redelivery, hand off), cited as "Chapter 77". Ch 77's agent has `lookup_order`, `get_refund_history`, `issue_refund`, `handoff_to_human`. | Now "a credit-and-redelivery variant of Chapter 77's refund agent". |
| 9 | 77 vs 78 | §77.14 formula "pass^k from repeated trials" and worked example "Consistency hidden by the average" | S3 | **Duplicated owned content.** Ch 77 repeated Ch 78's pass^k estimator ($\binom{c}{k}/\binom{n}{k}$) with a near-identical worked example: 6 of 8 trials, pass^4 = 15/70 = 0.214, the same numbers as §78.6.3. Evaluation methodology is Ch 78's. | Ch 77's formula and example callouts were replaced by a short paragraph. It gives the estimator with a pointer to §78.6.3, keeps the 6-of-8 illustration (pass^1 0.75, pass^4 0.21) and the 6,000-refunds-a-day consequence, and keeps the gating recommendation. Table 77.7, knowledge checkpoint 10 and the §77.21 exercises still work. This saved about 150 words, which offsets #7, #12 and #13. |
| 10 | 78 vs 75 | §78.17 industry callout "DoorDash's quality pipeline" | S3 | **Duplicated industry example.** The same DoorDash post and the same figures (hallucinations −90%, severe compliance issues −99%) are told in full in §75.12 and again in §78.17. | Condensed to the evaluation angle: the guardrail, judge and quality-pipeline loop of Figure 78.1, with a pointer to "the courier-support assistant summarized in §75.12". The reported figures are kept and labeled as the company's own; the evidence label is unchanged. This offsets the additions in #6 and #8. |
| 11 | 76, 77, 78, 80 | Outbound references | S3 | **Unresolved or imprecise section references:**<br>• Ch 76: "(§58)" for learning-rate warmup; "(object storage, §15)"<br>• Ch 77: "(§77.7.4)" in Figure 77.3's reading (no such section); "M/M/c (§4)"<br>• Ch 78: "(§72, …)" and "(§75)" ×2 (#6); "rollout ladder of §66"<br>• Ch 80: QuickBite's continued pre-training cited as "§65.4" (the run is worked in §65.9.1, as Ch 76 and Ch 72 cite it) | Now:<br>• Ch 76: §58.5.3; §15.4<br>• Ch 77: §77.7.3 (memory write policies and privacy); §4.10.4 (M/M/c, Erlang C)<br>• Ch 78: Chapter 72, §75.6.3, Chapter 75; §66.12 (safe deployment)<br>• Ch 80: §65.9.1 |
| 12 | 77, 79, 80 | §77.6.4 example; §79.3.1; §80.4.1, §80.9.3, §80.14 | S3 | **Number wording:**<br>• Ch 77: "A twenty-step agent at 95% per step is a coin flip without retries": $0.95^{20} = 0.358$<br>• Ch 79: "QuickBite's chatbot alone needs three GPUs to do about one GPU's work (§73.15)": §73.15 has two GPUs for 0.52 busy at peak<br>• Ch 80 §80.4.1: "more cables than the cluster has GPUs times three": 49,152 = exactly 3 × 16,384<br>• Ch 80 §80.9.3: halving repair to 1.5 days gives "about 19 nodes": the 99.9% Poisson quantile at $L$ = 9.08 is 20<br>• Ch 80 §80.14: CPT "about \$3,600": 1,458 × \$2.50 = \$3,645, given as \$3,650 in Ch 65 and Ch 76 | Now:<br>• Ch 77: "fails almost two tasks in three without retries"<br>• Ch 79: "keeps two GPUs (N+1) for about half a GPU of peak work (§73.15)"<br>• Ch 80: "three cables for every GPU"; "about 20 nodes"; "\$3,650" |
| 13 | 77 | Figure 77.19 caption vs Figure 77.18 | S3 | **Diagram–prose mismatch.** Both figures claim to show task T-501. Figure 77.18's trace shows 12.0 s and a 2,010 ms, two-attempt refund; Figure 77.19's p50 critical path shows 15.1 s and a 150 ms refund. | Figure 77.19 is now "Critical path of a p50 refund task, in milliseconds" (number unchanged); the reading text did not name T-501. |
| 14 | 78 | §78.4.3 listing, `wilson()` | S3 | British `centre` as a variable name (×3). | Now `center`; the listing was re-run and its output is unchanged. |
| 15 | 76–80 | Ownership measurement | — | Non-owner passages flagged by the script, plus the overlaps named in the brief, were read:<br>• **§77.13.1 (340 words, injection).** Agent-specific: lethal trifecta, CaMeL and the confused deputy; it says "§78.13 covers testing them". §78.13 treats injection in depth (threat model, instruction hierarchy, dual-LLM pattern, residual-risk formula) and cites CaMeL in one sentence. Complementary.<br>• **§77.14 (after #9, ~480).** Systems-level metrics table and trajectory checks; defers methodology to Chapter 78 and the end-state harness to §78.6.4.<br>• **§79.4–§79.6 and §79.11 (routing and fallback hits).** Implementation: gateway retries only before the first byte, endpoint selection, bounded affinity, regional spillover. §79.6.1 rule 5 states that quality-aware model selection "is evaluated in Chapter 78; the router implements it". §78.14–§78.15 own the policy (router vs cascade, break-even $\Delta p^*$, fallback chain and availability). No duplicated formula.<br>• **Caching (78/79/75).** §79.12 owns platform cache economics ($f^\star$); §78.15 uses a policy-version-keyed FAQ cache from §75.15.2; the two agree (semantic answers only for non-personal FAQ content).<br>• **§79.6.1, §79.10.1 (prefix-cache hits).** Cite §73.8 and add only routing (bounded affinity) and tenant isolation (cache salting).<br>• **§79.7.1 (754, LoRA).** Restates the adapter-size product of §76.8.1 for placement; a pointer "as in §76.8.1" was added to step 2 of its example. Multi-LoRA mechanisms are summarized in two sentences with S-LoRA and Punica, as in §76.9.<br>• **§76.8.2 (QLoRA, quantization hits).** NF4 and double quantization are QLoRA-specific; dequantization cites §67.6.1.<br>• **§76.5.2 (fallback hits).** The handoff fallback of a validation retry loop, not model routing.<br>• **Ch 80 vs Ch 65.** Ch 80 reuses 50,700 GPU-hours, 3.1 h, $\delta$ = 20 s, $R$ = 600 s, 668 s and 88.6% unchanged, and adds Daly's exact goodput, a Monte Carlo of it, and spares. It does not re-derive parallelism or Young/Daly. Ch 80 cites RDMA, PFC and fat trees to §49.9–§49.10 and does not re-teach them. | Pointer added in §79.7.1 (4 words). No other condensation needed beyond #9 and #10. |
| 16 | 44, 60, 63–65, 72–80 | Recurring facts | — | Consistent across chapters (after #1–#7):<br>• **Chatbot model:** Llama-2-7B shape, 6,738,415,616 parameters, 13.5 GB BF16, 524,288 B/token KV (Ch 76, 79 = Ch 72); LoRA $r$ = 16 attention adapter 16,777,216 parameters = 33.6 MB (Ch 76 = Ch 79)<br>• **Traffic:** 30,000 support conversations = 10,000 chatbot + 20,000 human-agent (Ch 75, 76, 78 after #6; Ch 77 uses the 30,000 for its 40% account-action share, 12,000 tasks); 75,000 queries/day, 8/s peak (Ch 76, 77, 78, 79); RAG generation call 4,050 + 200 tokens, plus condensation 450 + 30 (Ch 75, 76, 78; Ch 79's 4,500/230 is the sum)<br>• **Prices:** \$0.20/\$0.60 internal transfer price (Ch 73, 75, 76, 77, 78, 79); hosted \$2.50/\$10, cached \$0.25 (Ch 77, 78, 79 = brief); small-model API \$0.15/\$0.60 (Ch 79 = brief); \$0.00093 per query in-house and \$0.0121 hosted (Ch 78 = §75.15.3 arithmetic); \$2.50 per GPU-hour (§60.11, Ch 76, 79, 80; Ch 80 derives \$2.49 from capex)<br>• **Support economics:** human contact \$3.00 = \$30/h × 6 min, 20% escalation (Ch 77, 78, 79 = brief)<br>• **Ch 79 tenants:** 100,000 dish updates, 4,000 tasks × 8 steps, 20,000 reviews (Ch 63) = brief; regional incidents 2 per region-year of 180 min (Ch 44 = Ch 79)<br>• **Training constants:** 50,700 GPU-h/failure, 3.09–3.1 h at 16,384 GPUs, $\delta$ = 20 s, $R$ = 600 s, Young 668 s, goodput 88.6% first-order (Ch 65 listing = Ch 80 text and listing); Llama 3 root-cause shares (Ch 65 = Table 80.6); $3.8 \times 10^{25}$ FLOPs, 26.4 M ideal GPU-hours; 1,458 GPU-hours for the 50B-token CPT (Ch 65, 76, 80 after #12)<br>• **GPU constants:** H100 989 TFLOP/s dense BF16 (Ch 76 = Table 64.4); Ch 80 uses Ch 65's stated round numbers ($10^{15}$ FLOP/s, 360/40 GB/s achieved), 700 W TDP (Table 64.4) | No action beyond #1–#7 and #12. |
| 17 | 76–80 | Terminology | — | **Terms:** "master" only as "FP32 master weights" (a training term, not primary/replica); "QPS" not used (rates are "queries per second" or "/s"); "hit ratio" and "hit rate" both appear (acceptable synonym); no "slave", "uptime" (only the Uptime Institute's name), "message bus". **Spelling:** apart from #14, no British spellings (the grep hits were "raising", "rising", "devising", "Compromising"). | #14 only. |

**Counts:** S1 = 0 · S2 = 7 (fixed or, for #1, made explicit) · S3 = 7 (fixed) · 3 checked with no action needed (#15–#17).

## Technical spot-checks that passed (recomputed with `python3`)

1. **Running all listings.** The 13 Python listings were run with `OMP_NUM_THREADS=1 python3 -I`. All matched verbatim; none is timing-dependent.
   - **Ch 76 (4):** validator and retry loop (7,024/2,564/347/65, 1.339 calls); masked SFT labels (2.9590 vs 2.9347); LoRA layer, merge and 7B counts (16,777,216; 39,976,960); Bradley–Terry and DPO (0.5544, 0.3711, KL 1.650/0.770/0.105)
   - **Ch 77 (3):** mini agent loop (idempotent replay, injection denied, loop and budget stops); compounding-error Monte Carlo (0.359/0.785/0.810 at 20 steps); durable-execution replay (one LLM call, one refund)
   - **Ch 78 (3):** bootstrap intervals and sample sizes (1,356; 2,401; 1,039; 2,281); judge–human agreement and position bias (0.740/0.332, swap-corrected 0.536); router and cascade simulation (cascade 0.7: 38.9%, 0.936, \$5.83, \$37.8)
   - **Ch 79 (2):** routing-policy simulator (67/67/92/91% hits; affinity TTFT p99 4.22 s); token-bucket accounting modes (80/72/64/71% admitted)
   - **Ch 80 (1):** goodput Monte Carlo against Daly's exact and the first-order formula (89.2/89.2/88.6% at 16,384 GPUs; 54.6% vs 40.0% at 131K)
2. **§76.3–§76.6 prompting, structured output, ICL.**
   - **Break-even:** \$24.00/day, \$60,800, 2,533 days; 25,333 days with caching; 25 days at 100× volume.
   - **Retries:** $P_\text{fallback}$ 0.00675 (506/day) and 0.0012 (90/day); $E$[calls] 1.345 and 1.036 (−23%); 5.8 s per call (575 ms + 200 × 26 ms).
   - **ICL:** \$15.75/day (\$5,749/year), 29.7 ms; \$2.28 and 1.5 ms cached; 10 chunks instead of 13; 550 MB per sequence.
   - **Other:** 750 failures/day at 1%; 400 golden cases \$0.34; 29,167 GPU-hours for 7B on 1T tokens (§65.3 listing).
3. **§76.7–§76.9 SFT, LoRA, serving.**
   - **Masked loss:** 0.70 vs 1.6 nats, 43% of loss mass on prompts.
   - **Full fine-tuning:** 107.8 GB state; 22.6 GB per GPU on 8 with ZeRO-3; $7.28 \times 10^{18}$ FLOPs, 5.06 GPU-hours, 38 min, \$12.60.
   - **LoRA:** 131,072 per matrix; 16.8 M (0.249%), 40.0 M (0.593%); 33.6/80.0 MB (400×/170×); 0.27/0.64 GB of state; 0.78% and 3.1% per matrix; checkpoint question 4,194,304 (0.062%).
   - **QLoRA:** NF4 overhead 0.5 → 0.127 bits; 202,375,168 linear parameters per layer; 3.34 + 0.52 + 0.64 + 1.5 = 6.0 GB; 15.6 GB BF16 LoRA; Table 76.3 batches 2/12/26 and 7/17/31; 0.26 GB of logits per sequence.
   - **Multi-LoRA:** 162 GB merged and 24 GPUs; 0.40 GB, 769 KV tokens (0.75%); +0.25% FLOPs.
4. **§76.10–§76.14 alignment and data.**
   - **Bradley–Terry:** 0.690, 0.371 / 1.171 nats; $\sigma(1.5)$ = 0.818.
   - **KL penalty:** 1.70 vs 1.70 at $\beta$ = 0.05; 1.40 vs 1.00 at 0.1; clip 2.4.
   - **DPO:** margin 0.3, loss 0.554, weight 0.426; $6.4 \times 10^7$ tokens, $3.45 \times 10^{18}$ FLOPs, 2.4 GPU-hours, \$6.
   - **Labeling costs:** preference labels \$5,500; review \$55,000.
   - **Data funnel:** 2.7 M → 945,000 → 567,000 → 23,900; 48 + 12 = 60 M tokens per epoch, 180 M; 45 M in the loss; 0.89% survives; CPT 278× the SFT budget.
   - **Distillation storage:** 11.5 TB full logits vs 21.6 GB top-20 (0.19%).
5. **§77.5–§77.10 agents.**
   - **Assumptions and tool budget:** 1.33 tasks/s peak; 900 approvals; \$0.05 for 20,000 schema tokens.
   - **Compounding errors:** 0.774/0.599/0.358; 0.988 → 0.886/0.785; ceiling 0.98958 → 0.811; 0.818 silent-only; checkpoint answers 0.663 and 0.9896.
   - **Memory:** 30.7 GB of FP16 episodic vectors.
   - **Multi-agent:** 64,900 tokens (1.35×); 19.2 vs 12.0 s; 6 vs 3 channels.
   - **Retry storm:** 64 and 192 calls per task, 125 calls/s (192×); 0.72 calls/s budgeted; 27 in the checkpoint.
6. **§77.11–§77.17 guardrails, humans, cost.**
   - **Fleet cap:** 5,100 × \$11 = \$56,100; cap 1.34× that.
   - **Erlang C:** $C(4, 3)$ = 0.509, mean wait 1.02 min, $P(W > 5)$ = 0.042; $C(5, 3)$ = 0.236, 0.24 min, 0.16%; 30 reviewer-hours, \$1.00 per approval; checkpoint answer 8 reviewers.
   - **Cost per task:** 24,000 input tokens; \$0.0665 uncached, \$0.0328 cached; \$0.0006 aux; \$0.218 agent-side, \$0.82 blended (\$9,816 vs \$36,000/day); \$0.27 per agent-resolved ticket; tokens 4%, escalations 73%; 7B alternative \$0.0052.
   - **Latency:** 2.45 s per step (82% decode), 10.1/15.1 s, 7.65 s with parallel reads, 4.9% tail; Gantt 94% model time.
   - **pass^2 checkpoint:** 10/28 = 0.357.
7. **§78.4–§78.8 offline evaluation and judges.**
   - **Intervals and sample sizes:** 0.8175 ± 0.0379; 1,355.1 → 1,356; 2,401; paired 1,038.7 → 1,039; unpaired 2,281; ±16.5 at $n$ = 20; ±2.1 at 1,200; slices ±4–8.
   - **Overlap metrics:** F1 0.706 vs 0.588.
   - **pass@k:** pass@1 0.75, pass@4 1.0, pass^4 0.214; checkpoint pass@3 0.833, pass^3 0.5.
   - **Judge calibration:** κ = 0.659; Se 0.923, Sp 0.714; Rogan–Gladen 0.650; checkpoint 0.786.
   - **Position bias:** consistency 0.60, first-position share 0.60, naive 0.650, corrected 0.550.
   - **Human review:** 90 h, \$3,600, 3.75 days vs \$11.10 judged (324×).
8. **§78.9–§78.13 hallucination, RAG, online, safety.**
   - **SelfCheckGPT:** 0.05/0.10/0.80, 0.317.
   - **RAG metrics:** CP@6 0.722, CR 0.75, AR 0.860.
   - **A/B test:** 24,638 per arm (after #6: 5 days, 70,000 per arm).
   - **Refusal policy:** \$199.1 vs \$124.8 per 1,000 conversations.
   - **Injection layers:** 30 vs 144 successful attacks a day.
9. **§78.14–§78.17 routing, fallbacks, frontier, platform.**
   - **Cascade:** \$0.00584, $Q$ 0.936; \$438/\$908/\$70 a day; $\Delta p^*$ = 0.0223.
   - **Availability:** 0.9935 (4.7 h/month) and 0.9985 (1.1 h); 4.4 s worst-case TTFT; error budget 11,250 messages.
   - **Frontier:** \$70 and \$8,453; \$766 and \$3,276; −\$5,177; $V$ > \$0.072.
   - **Evaluation run:** \$12.22 and 337.5 s per run; \$489 a day (64% of \$766).
10. **§79.5–§79.8 gateway, router, pools.**
    - **Gateway budget:** 90 ms with 9.0 ms used; +25 ms NER = 34 ms; 108 ms prefill of 3,800 tokens.
    - **Bounded affinity:** bound 40,000; 14 ms refused-hit cost.
    - **Adapters:** 33.6 MB, 101 MB, 40.5 GB, 119 in 4 GB; checkpoint 16.8 MB.
    - **Shared pool:** $g_\text{req}$ 0.238; 1.90 busy, 5 replicas; 72 GPU-h/day, \$5,400/month; menu 10,203 GPU-s, 0.52 GPUs; reviews 907 GPU-s; headroom $H$ = 1; utilization 241/2,160 = 11%.
11. **§79.9–§79.16 quotas, isolation, regions, caching, cost.**
    - **Quotas:** 2.27 M TPM, 3.4 M limit, 720 RPM; $e$ 8,596 (1.82×); $U$ 236,600 tokens (4.2 s); 10,400 at $\hat o$ = 400.
    - **Fair share:** 4.0/1.0, 3.10 GPU-s/s, 30 menu requests/s, 2.3× and 20×.
    - **Failover:** \$3,650 standby vs \$3.51 spillover (\$0.000813/query, \$7.02/h).
    - **Semantic cache:** −\$0.0071/query (−\$531/day), $f^\star$ 0.00069; exact cache saves 4,081 GPU-s.
    - **Ops-agent tasks:** \$0.144 vs \$0.0576 per task, \$17,280 vs \$6,912/month, output 42% of cached cost.
    - **Chargeback:** rates \$0.0197/\$0.394 and \$0.176/\$3.52; shares 61.6/35.2/3.1%; cost-driver \$5,169/\$213/\$19; overhead \$859/\$1,145/\$229/\$367; Table 79.6 totals; \$0.0027 per query.
    - **Build versus buy:** $p$ \$0.172, $c$ \$0.0582, $F$ \$11,650, $V^\star$ ≈ 102,500 M tokens; 10.6 B tokens/month, \$1,830 API.
    - **Re-sizing check for #1:** batch 24 (28 with a shared prefix), 26.7–30.0 ms step, 1.07–1.11 ms per output token, $g_\text{req}$ 0.35–0.36, 2.8–2.9 busy GPUs, 6 replicas.
12. **§80.3–§80.6 coupling, fabric, storage.**
    - **Jitter:** $\mu$ = 5.93 s; $\sqrt{2\ln N}$ = 2.04/3.72/4.41/4.85; 1.3 M GPU-hours, \$3.2 M.
    - **Parts count:** 512 + 512 + 256 = 1,280 switches, 49,152 cables, 98,304 transceivers.
    - **Bisection:** 3,277 Tb/s; 4.9 Pb/s; 702 Tb/s with 1:7 oversubscription.
    - **Cross-pod all-reduce:** 6.33 GB shard, 12.6 GB ring volume; 1,075 vs 176 Tb/s, 8.2 GB/s, 1.5 s; 51 Tb/s and 0.31 s topology-aware.
    - **Hierarchical all-reduce:** 0.43 s flat; 9.7 + 12.5 + 0.2 ≈ 22 ms hierarchical.
    - **ECMP:** 0.24%; 5.25 uplinks; independent Monte Carlo 2.60 and 21.9 busiest-uplink flows, $\eta$ 39% and 73%.
    - **Storage:** 11 MB/s dataset stream; 5.67 TB, 346 MB/GPU; 94.5/567/846 GB/s; 2.8 s at 2 TB/s; 8.5 GB/s average; 104 TB and 52 s amplified restart reads.
13. **§80.7–§80.9 facilities, reliability, goodput.**
    - **Cooling:** 2.87 kg/s, 172 L/min; 6.6 m³/s, 14,000 CFM, 2,300×; checkpoint 86 L/min.
    - **Power:** 20.9 + 1.5 + 1.3 = 23.7 MW, 28.5 MW at PUE 1.2, 1.74 kW/GPU, 212 GWh/year, 170 MW at 100K GPUs; 17,000 GPUs at 30 MW.
    - **Job MTBF:** 3.09 h, 0.04%; GPU-only 86,300 h and 5.3 h; 0.507 h and 49.5 h; checkpoint 1.55 h.
    - **Goodput:** 3.0 + 3.0 + 5.4% → 88.6%; 0.7 + 0.7 + 1.1% → 97.6%; 85.7% and 93.7%; 2.6 M GPU-hours, \$6.6 M.
    - **Spares:** 6.05 nodes/day, $L$ 18.2, Poisson 29/33 (20 at $L$ = 9.08, #12).
    - **Recovery timeline:** Figure 80.11's 37 = 20 + 17 minutes.
14. **§80.10–§80.15 stragglers, economics, sustainability.**
    - **Stragglers:** $s^*$ 5.6%, 1.1%, 0.35%; checkpoint 1.4%; draining 49,152 GPU-hours.
    - **Cost per GPU-hour:** \$1.43 + 0.14 + 0.36 + 0.57 = \$2.49, \$3.12 at $u$ = 0.8.
    - **Reference run:** 26.4 M ideal, 29.3 M GPU-hours, 74.5 days, \$73 M; 1 goodput point ≈ \$0.8 M; CPT 1,458 GPU-h (20,000× smaller).
    - **Footprint:** 21.6 and 43.3 GWh; 17,300 t; 71 M L.
15. **Concepts checked against the text.**
    - LoRA's $B = 0$ initialization and exact merge; QLoRA's NF4 with double quantization to 0.127 bits [Dettmers et al. 2023].
    - DPO's closed-form policy and implicit reward [Rafailov et al. 2023]; PPO clipping [Schulman et al. 2017]; InstructGPT's 1.3B-over-175B result and about 73% inter-labeler agreement [Ouyang et al. 2022].
    - MCP roles (host, client, server), primitives, stdio and Streamable HTTP transports, and `isError` tool results (2025 revisions).
    - Durable execution replays recorded activity results [Temporal Docs]; τ-bench's pass^k and end-state grading [Yao et al. 2024].
    - The Rogan–Gladen estimator; McNemar pairing; Wilson interval.
    - Daly's exact goodput expression reduces to the first-order waste of §65.15 when $\tau + R \ll M$.
    - Llama 3 Table 5 shares (30.1/17.2/12.9/8.4/7.6%, 58.7% GPU, 1.4% SDC, ~78% hardware) [Dubey et al. 2024].
    - TPU v4 OCS cost and power (<5%, <3%) [Jouppi et al. 2023]; MegaScale 55.2% MFU [Jiang et al. 2024]; Gemini goodput 85% → 97% [Gemini Team 2023].
16. **Cross-references.**
    - **Outbound:** every `§` reference in Ch 76–80 resolves to an existing section on its topic after #11. Forward references are to Chapter 86 (Ch 79's re-sizing note, #1), which matches the TOC (86.4 Enterprise RAG Assistant, 86.5 LLM Inference Platform, 86.7 Customer-Support Agent).
    - **Book I targets checked:** §4.6, §4.10.4; §9.5, §9.6; §14.8; §15.4; §18.4; §19.4, §19.6; §20.3; §22.3–§22.15, §22.12.3–§22.12.4; §32.7, §32.11, §32.11.1; §34.10; §39.4, §39.6, §39.7, §39.11; §40.3–§40.7, §40.4.5, §40.6.3; §42.10–§42.13; §44.4–§44.9; §46.10–§46.12, §46.12.2; §47.4–§47.12, §47.12.2; §49.4.2, §49.9.2, §49.10–§49.11; §50.3, §50.5, §50.5.4, §50.8–§50.10, §50.9.3; §51.4–§51.11.

## Remaining risks

- **Ch 79's fleet size for the RAG profile (carried from wave 12).** #1 makes the assumption explicit but keeps Ch 79's numbers. With 4,050 + 200-token RAG calls, the 7B pool needs about 6 replicas at peak rather than 5. Output-token cost is about 1.1 ms rather than 0.567 ms, and the derived figures shift: 72 GPU-hours a day, \$5,400 a month, 11% utilization, Table 79.6, the \$0.0027 per query and $V^\star$ ≈ 102.5 B tokens. The chatbot case study in Chapter 86 should re-size the fleet once, consistently with §73.5's 102,997-token pool. Ch 79's note now promises that it does. The 30 condensation output tokens run on Ch 75's 1B condenser, which Ch 79 bills at 7B rates; that is minor.
- **Transfer price versus Ch 79's loaded rates.** At Ch 79's 11% utilization the loaded self-hosted rates are \$0.18 input and \$3.52 output per million tokens, against the \$0.20/\$0.60 transfer price used in Ch 75–78. This is consistent with §73.15's "would recover only a sixth" and with Ch 75's "assume a shared, well-utilized platform". Readers comparing Ch 78's \$0.00093 per query with Ch 79's \$0.0027 chargeback may still need the bridge sentence that Chapter 86 can supply.
- **Three people-cost rates.** Ch 76 uses \$22/h at 80% productive time for trained support leads (§63.5.2). Ch 77 uses \$30/h for human support agents (giving \$3.00 per contact). Ch 78 uses \$40/h for annotators and experts. Each is stated in its chapter's assumptions and applies to a different role, but support leads costing less than support agents is odd. Ch 86 should pick one rate per role.
- **Policy scope (#7).** QuickBite now has an automatic 20% late credit (Ch 75, 78) and a separate refund entitlement for late orders with a food complaint (Ch 77). Case studies should keep both rules distinct.
- **Prefill-throughput assumptions.** Ch 76, 78 and 79 use 28.3 µs per prompt token (Ch 73's 50% MFU), while Ch 75's 575 ms TTFT uses 25% (wave 12 #6). Both are stated.
- **Perishable facts** stay in the chapters' open-verification lists and were not re-verified here:
  - **Ch 76:** LoRA, InstructGPT, LIMA, Lee et al. and Structured Outputs figures; Llama 2 license clauses; Ovadia et al. venue
  - **Ch 77:** MCP revisions (2025-06-18, 2025-11-25); OpenTelemetry GenAI names; τ-bench figures; ReAct and Reflexion numbers; the first author of "Building Effective Agents"
  - **Ch 78:** Zheng et al. agreement wording; Perez et al. count; FrugalGPT and RouteLLM savings; RAGAS formulas; OWASP 2025 ordering; DoorDash figures
  - **Ch 79:** Gateway API Inference Extension resource names; OpenTelemetry GenAI attributes; provider retention terms; the Vertex AI URL; Preble, DynamoLLM and GPTCache venues
  - **Ch 80:** Llama 3 Table 5 count inconsistency (148 at 30.1%); Gemini wording; DGX SuperPOD switch counts; GB200 rack power; Llama 3.1 model-card figures; Li et al. water estimate
- **No `§`-reference resolver in `qa_check.py`.** This review again used a scratch script, as in waves 8–12. Eight unresolved or chapter-level references were found this wave (#11).
