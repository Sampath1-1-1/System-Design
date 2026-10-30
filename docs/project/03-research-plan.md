# 3. Research Plan

## 3.1 Objectives

1. Every concept is explained from first principles and cross-checked against at least one authoritative source (original paper, RFC/specification, official documentation, or a recognised textbook).
2. Every industry example is traceable to a primary public source, or explicitly labelled *Illustrative*.
3. Fast-moving topics (LLM inference, AI infrastructure, ML serving, cloud products) carry an "as of" date and are re-verified at each release.

## 3.2 Research phases

| Phase | Output | Exit criterion |
|---|---|---|
| R0 — Scoping | Master TOC, dependency map, chapter scope (this folder) | Approved structure; every brief topic mapped (crosswalk §1.5) |
| R1 — Source collection | Per-chapter reading list in the chapter's References | ≥ 1 primary source per major concept; papers/RFCs preferred |
| R2 — Drafting | Chapter draft following the template | All template elements present; diagrams captioned; maths worked |
| R3 — Verification | Corrections; "Open verification items" list | Formulas recomputed; code executed; URLs checked |
| R4 — Integration | Cross-references, terminology unification, de-duplication | QA reviews 1–7 passed (see 08-qa-plan.md) |
| R5 — Publication | HTML/PDF/DOCX builds; diagram collection; glossary; bibliography | Review 8 passed |

## 3.3 Research waves (execution order)

Chapters are researched in waves that respect the dependency map, so later chapters can cross-reference finished ones.

| Wave | Chapters | Theme | Parallel agents |
|---|---|---|---|
| 1 | 1–10 | Foundations: thinking, maths, architecture, OS, networking, web, real-time, security | 10 |
| 2 | 11–17 | Data systems | 7 |
| 3 | 18–23 | Scalability and performance | 6 |
| 4 | 24–29 | Distributed systems | 6 |
| 5 | 30–38 | Messaging, architecture, OOD | 9 |
| 6 | 39–43 | Production infrastructure | 5 |
| 7 | 44–51 | Advanced and expert topics | 8 |
| 8 | 52–56 | Traditional case studies (27 problems) | 5 (one per case chapter) |
| 9 | 57–63 | ML foundations and data infrastructure | 7 |
| 10 | 64–71 | Training, serving, MLOps | 8 |
| 11 | 72–80 | LLM and AI systems | 9 |
| 12 | 81–86 | ML/AI case studies (27 problems) | 6 |
| 13 | 87–93 | Interviews, practice library, projects | 7 |
| 14 | Appendices A–I + front matter | Glossary, bibliography, formula handbook, diagram collection, roadmap | 4 + integration |

Each wave ends with an integration and review pass before the next wave's agents start, so that terminology and cross-references stay consistent.

## 3.4 Per-chapter research protocol

1. Read the chapter's TOC entry, prerequisites (02-dependency-map.md) and neighbouring chapters that already exist.
2. Collect sources in this priority order (see 07-source-strategy.md): original papers/specs → official docs → company engineering blogs → textbooks → reputable educational material.
3. Draft following `chapter-template.md` and `style-guide.md`.
4. Verify: re-derive formulas, recompute numerical examples, execute code, re-check every URL that is cited.
5. Record anything not verifiable in "Open verification items" (aggregated into Appendix H).
6. Return a summary to the integration lead: word count, figures, tables, open items.

## 3.5 Research directions requiring primary sources

| Topic | Primary sources to use |
|---|---|
| Google Spanner | Corbett et al., OSDI 2012; Brewer, "Spanner, TrueTime and the CAP Theorem" (2017) |
| Dynamo / DynamoDB | DeCandia et al., SOSP 2007; Elhemali et al., USENIX ATC 2022 |
| Bigtable | Chang et al., OSDI 2006 |
| GFS / MapReduce | Ghemawat et al., SOSP 2003; Dean & Ghemawat, OSDI 2004 |
| Facebook TAO | Bronson et al., USENIX ATC 2013 |
| Memcache at Facebook | Nishtala et al., NSDI 2013 |
| Borg / Omega / Kubernetes | Verma et al., EuroSys 2015; Schwarzkopf et al., EuroSys 2013; Burns et al., ACM Queue 2016 |
| Raft / Paxos | Ongaro & Ousterhout, USENIX ATC 2014; Lamport 1998, 2001 |
| ZooKeeper / Chubby | Hunt et al., USENIX ATC 2010; Burrows, OSDI 2006 |
| Kafka | Kreps et al., NetDB 2011; Apache Kafka documentation; KIP-500 (KRaft) |
| Netflix | Netflix Tech Blog (Open Connect, Zuul, Hystrix, chaos engineering) |
| Uber | Uber Engineering blog (Michelangelo 2017; H3; Schemaless) |
| YouTube recommendations | Covington et al., RecSys 2016; Zhao et al., RecSys 2019 |
| Meta recommendation | Naumov et al., DLRM 2019; Meta engineering blog |
| LLM inference | Kwon et al., SOSP 2023 (PagedAttention/vLLM); Leviathan et al., ICML 2023 (speculative decoding); Dao et al., NeurIPS 2022 (FlashAttention); Yu et al., OSDI 2022 (Orca) |
| Distributed training | Shoeybi et al. 2019 (Megatron-LM); Rajbhandari et al., SC 2020 (ZeRO); Huang et al. 2019 (GPipe); Narayanan et al., SC 2021 |
| Large-scale AI infra | Meta engineering blog on 24k-GPU clusters (2024); Llama 3 paper (Dubey et al. 2024) on training reliability; Google TPU papers (Jouppi et al. ISCA 2017, 2023) |
| OpenAI / Anthropic | Only publicly published engineering posts, papers and documentation; no inference beyond them |

## 3.6 Handling fast-moving topics

- Each claim about a product, hardware generation, price or model capability includes "as of <year>".
- A **freshness register** (column in the progress tracker) records chapters with time-sensitive content and their last verification date.
- Re-verification cadence: LLM/AI chapters (72–80, 86) every 6 months; cloud/Kubernetes chapters (41–43) every 12 months; foundational chapters on edition changes.

## 3.7 Handling insufficient evidence

When evidence is missing or contradictory:

1. State the uncertainty in the text ("Public sources do not document X; the following is an illustrative design").
2. Add the item to the chapter's "Open verification items".
3. The integration lead aggregates these into `unresolved-questions.md` (Appendix H).
