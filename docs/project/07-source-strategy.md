# 7. Source Strategy

## 7.1 Source hierarchy

**Table P.5 — Source tiers.**

| Tier | Type | Examples | Use for |
|---|---|---|---|
| T1 | Original research papers | OSDI, SOSP, NSDI, EuroSys, USENIX ATC, VLDB, SIGMOD, SIGCOMM, NeurIPS, ICML, MLSys papers | Mechanisms, algorithms, original designs |
| T1 | Standards and specifications | IETF RFCs, W3C/WHATWG, OpenAPI, GraphQL spec, OpenTelemetry spec, MCP spec | Protocol behavior |
| T2 | Official documentation | PostgreSQL, Kafka, Kubernetes, Redis, AWS/GCP/Azure, NVIDIA CUDA, PyTorch, vLLM docs | Current behavior and configuration |
| T2 | Company engineering publications | Netflix Tech Blog, Uber Engineering, Meta Engineering, Google Research/Cloud blogs, AWS Builders' Library, Stripe, LinkedIn, Airbnb, Spotify, Discord, Cloudflare, OpenAI and Anthropic engineering/research posts | Industry examples (*Evidence: Primary*) |
| T3 | Established textbooks | Kleppmann *DDIA*; Hennessy & Patterson; OSTEP; Kurose & Ross; Google SRE books; Petrov *Database Internals*; Huyen *Designing ML Systems* | Pedagogical framing, cross-checks |
| T3 | Conference talks | QCon, Strange Loop, USENIX SREcon, re:Invent, KubeCon (official recordings) | Industry context (*Evidence: Primary* if by the company's engineers) |
| T4 | Reputable educational/secondary sources | University course notes (MIT 6.824/6.5840, CMU 15-445), Jepsen analyses, ACM Queue | Explanations; *Evidence: Secondary* for company claims |
| ✗ | Not acceptable as sole evidence | Anonymous posts, AI-generated summaries, content farms, unattributed "how X works" articles | — |

## 7.2 Citation rules

1. Every important technical claim cites the highest-tier source available.
2. Format: `Authors. *Title*. Venue/Publisher, Year. URL` (URL only when known with confidence).
3. Prefer stable URLs: DOIs, USENIX/ACM/arXiv landing pages, RFC Editor, official docs root pages.
4. Distinguish *original research* (T1) from *secondary explanation* (T3/T4) in the reference list with a tag `[original]` / `[secondary]` when both appear.
5. Industry callouts carry an evidence label: Primary / Secondary / Illustrative.
6. Benchmarks are reported with their conditions (hardware, version, date) and source; never invented.
7. Outdated information is flagged ("Superseded: Kafka ZooKeeper mode was removed in Kafka 4.0 (2025); KRaft is the only mode").

## 7.3 Verification checklist per citation

- [ ] Source exists and the title/authors/year match.
- [ ] The cited claim actually appears in the source.
- [ ] URL resolves (or is omitted and flagged).
- [ ] Time-sensitive claims carry "as of".
- [ ] Company claims are from the company's own publication or clearly labelled secondary.

## 7.4 Core reference library (seed list)

The full, de-duplicated bibliography is built in Appendix B. The seed list below anchors the most-cited works.

**Distributed systems and data**
- Kleppmann, M. *Designing Data-Intensive Applications*. O'Reilly, 2017.
- Petrov, A. *Database Internals*. O'Reilly, 2019.
- Lamport, L. "Time, Clocks, and the Ordering of Events in a Distributed System." CACM 21(7), 1978.
- Fischer, Lynch, Paterson. "Impossibility of Distributed Consensus with One Faulty Process." JACM, 1985.
- Ongaro, D., Ousterhout, J. "In Search of an Understandable Consensus Algorithm." USENIX ATC, 2014.
- DeCandia, G. et al. "Dynamo: Amazon's Highly Available Key-value Store." SOSP, 2007.
- Chang, F. et al. "Bigtable: A Distributed Storage System for Structured Data." OSDI, 2006.
- Corbett, J. et al. "Spanner: Google's Globally-Distributed Database." OSDI, 2012.
- Ghemawat, S., Gobioff, H., Leung, S. "The Google File System." SOSP, 2003.
- Dean, J., Ghemawat, S. "MapReduce: Simplified Data Processing on Large Clusters." OSDI, 2004.
- Zaharia, M. et al. "Resilient Distributed Datasets." NSDI, 2012.
- Kreps, J., Narkhede, N., Rao, J. "Kafka: a Distributed Messaging System for Log Processing." NetDB, 2011.
- Bronson, N. et al. "TAO: Facebook's Distributed Data Store for the Social Graph." USENIX ATC, 2013.
- Nishtala, R. et al. "Scaling Memcache at Facebook." NSDI, 2013.
- Verma, A. et al. "Large-scale cluster management at Google with Borg." EuroSys, 2015.
- Beyer, B. et al. (eds.) *Site Reliability Engineering*. O'Reilly, 2016.

**Performance and systems**
- Dean, J., Barroso, L. A. "The Tail at Scale." CACM 56(2), 2013.
- Barroso, L. A., Hölzle, U., Ranganathan, P. *The Datacenter as a Computer*, 3rd ed. Morgan & Claypool, 2018.
- Gregg, B. *Systems Performance*, 2nd ed. Addison-Wesley, 2020.
- Arpaci-Dusseau, R. & A. *Operating Systems: Three Easy Pieces*. ostep.org.

**ML systems**
- Sculley, D. et al. "Hidden Technical Debt in Machine Learning Systems." NeurIPS, 2015.
- Huyen, C. *Designing Machine Learning Systems*. O'Reilly, 2022.
- Covington, P., Adams, J., Sargin, E. "Deep Neural Networks for YouTube Recommendations." RecSys, 2016.
- Naumov, M. et al. "Deep Learning Recommendation Model for Personalization and Recommendation Systems." arXiv:1906.00091, 2019.
- Shoeybi, M. et al. "Megatron-LM." arXiv:1909.08053, 2019.
- Rajbhandari, S. et al. "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models." SC, 2020.

**LLM systems**
- Vaswani, A. et al. "Attention Is All You Need." NeurIPS, 2017.
- Kwon, W. et al. "Efficient Memory Management for Large Language Model Serving with PagedAttention." SOSP, 2023.
- Yu, G.-I. et al. "Orca: A Distributed Serving System for Transformer-Based Generative Models." OSDI, 2022.
- Leviathan, Y., Kalman, M., Matias, Y. "Fast Inference from Transformers via Speculative Decoding." ICML, 2023.
- Dao, T. et al. "FlashAttention." NeurIPS, 2022.
- Lewis, P. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS, 2020.
- Malkov, Y., Yashunin, D. "Efficient and robust approximate nearest neighbor search using HNSW graphs." IEEE TPAMI, 2018.
- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR, 2023.
