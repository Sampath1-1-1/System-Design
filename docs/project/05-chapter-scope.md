# 5. Chapter-by-Chapter Scope

Section-level content for each chapter is listed in `01-master-toc.md`. This file fixes, for each chapter: proficiency level, track, page budget, owning agent, the diagrams and quantitative content it must contain, and its anchor sources. Page estimates assume ~450 words per printed page including diagrams.

**Table P.3 — Chapter scope.**

| Ch | Title | Lvl | Trk | Pages | Owner | Required diagrams | Required quantitative content | Anchor sources |
|---|---|---|---|---|---|---|---|---|
| 1 | What Is System Design? | 1 | S | 20 | A15 | Evolving single-server → scaled app; HLD vs LLD | NFR targets as numbers | Bass et al.; Kleppmann 2017; Nygard 2011 |
| 2 | Thinking Like a Designer | 1–2 | S | 25 | A15 | Context diagram; decomposition; bottleneck flow; C4 levels | First envelope estimate | Brown (C4); Bezos 2015 letter |
| 3 | Learning Method | 1 | S | 18 | A15 | Mastery loop; 12-month path | — | Dunlosky 2013; Keshav 2007 |
| 4 | Quantitative Foundations | 1–3 | S | 32 | A1 | Queue model; availability series/parallel; fan-out | Little, Amdahl, USL, M/M/1, nines, durability | Kleinrock; Little 1961; Dean & Barroso 2013 |
| 5 | Computer Architecture | 1 | S | 25 | A1 | Memory hierarchy; cache coherence; NUMA | Access-time formulas, bandwidth | Hennessy & Patterson; Drepper 2007 |
| 6 | Operating Systems | 1–2 | S | 28 | A1 | Process states; event loop; syscall path | Thread memory, context-switch cost | OSTEP; Kegel C10K |
| 7 | Networking Fundamentals | 1–2 | S | 35 | A1 | Layers; DNS; TCP/TLS handshakes; leaf–spine | BDP, Mathis, RTT math | RFCs; Kurose & Ross; Grigorik |
| 8 | Web Application Fundamentals | 1–2 | A | 32 | A2 | Request lifecycle; OAuth PKCE; gRPC | Pagination cost | RFC 9110, 6749; Fielding 2000 |
| 9 | Real-Time Communication | 2 | A | 22 | A2 | Polling/SSE/WS sequences; gateway fleet | Connections per server, memory | RFC 6455; WHATWG SSE |
| 10 | Security Fundamentals | 2 | S | 28 | Sec | STRIDE DFD; envelope encryption; zero trust | Entropy, brute-force time | OWASP; NIST 800-63B; BeyondCorp |
| 11 | Relational Databases | 1–2 | A | 35 | A3 | B+ tree; query plan; MVCC versions | Index fan-out, I/O per lookup | Ramakrishnan; PostgreSQL docs; Berenson 1995 |
| 12 | NoSQL Databases | 2 | A | 25 | A3 | Data model per family; selection flowchart | — | DynamoDB/MongoDB/Cassandra docs |
| 13 | Storage Engine Internals | 3 | A | 28 | A3 | WAL; LSM levels; compaction | Read/write/space amplification | O'Neil 1996 (LSM); ARIES 1992; RocksDB wiki |
| 14 | Database Scaling | 2–3 | A | 30 | A3 | Replica topologies; hash ring; rebalancing | Shard count, keys moved on resize | Karger 1997; DDIA ch 5–6; Vitess docs |
| 15 | Object/Block/File Storage | 2–3 | A | 20 | A3 | S3-style architecture; GFS | Erasure-coding overhead and durability | GFS 2003; Reed–Solomon; S3 docs |
| 16 | Search Systems | 3 | A | 22 | A3 | Inverted index; scatter–gather | BM25, index size | Manning et al. IR book; Robertson & Zaragoza 2009 |
| 17 | Data Structures for Scale | 2–3 | A | 25 | A4 | Bloom filter; HLL; geohash grid; Snowflake ID layout | FP rate, HLL error, ID bit budget | Bloom 1970; Flajolet 2007; Cormode 2005 |
| 18 | Scalability | 2 | A | 18 | A4 | Scale cube; stateless tier | Capacity per node | Abbott & Fisher |
| 19 | Load Balancing | 2 | A | 22 | A4 | L4 vs L7; Maglev; GSLB | Power-of-two-choices load | Eisenbud 2016 (Maglev); Mitzenmacher 2001 |
| 20 | Caching | 2 | A | 30 | A4 | Five cache patterns; stampede | Hit ratio → latency, DB load | Nishtala 2013; Redis docs |
| 21 | CDNs | 2 | A | 18 | A4 | Edge/mid/origin; ABR video | Offload ratio, egress cost | Nygren 2010 (Akamai); Netflix Open Connect |
| 22 | API & Traffic Management | 2–3 | A | 28 | A4 | Token bucket; circuit breaker states | Bucket parameters, retry amplification | Stripe rate-limiter blog; AWS Builders' Library |
| 23 | Performance Engineering | 3 | A | 22 | A4 | USE method flow; hedged requests | Coordinated omission, tail math | Gregg *Systems Performance*; Dean & Barroso |
| 24 | Distributed Fundamentals | 2–3 | A | 26 | A5 | Partition scenarios; Lamport/vector clocks | Clock skew bounds | Lamport 1978; FLP 1985; Deutsch fallacies |
| 25 | Consistency & Availability | 3 | A | 24 | A5 | Consistency hierarchy; CAP/PACELC | — | Herlihy & Wing 1990; Gilbert & Lynch 2002; Abadi 2012 |
| 26 | Consensus & Coordination | 3–4 | A | 32 | A5 | Raft election/log; fencing tokens | Quorum sizes, fault tolerance f | Ongaro 2014; Lamport 2001; Burrows 2006 |
| 27 | Replication & Fault Tolerance | 3 | A | 26 | A5 | Leaderless quorum; Merkle anti-entropy | R+W>N; phi-accrual | DeCandia 2007; Shapiro 2011 (CRDTs) |
| 28 | Distributed Transactions | 4 | A | 24 | A5 | 2PC; Spanner commit-wait | Commit latency | Corbett 2012; Peng & Dabek 2010; Thomson 2012 |
| 29 | Distributed Data Processing | 3 | A/B | 28 | A9 | MapReduce; Spark DAG; watermarks | Shuffle volume | Dean & Ghemawat 2004; Zaharia 2012; Akidau 2015 |
| 30 | Messaging Fundamentals | 2 | A | 22 | A6 | Queue vs pub/sub; DLQ | Consumer count from throughput | RabbitMQ/SQS docs; Hohpe & Woolf |
| 31 | Kafka Deep Dive | 3 | A | 30 | A6 | Partitions/ISR; consumer group rebalance | Partition count sizing | Kreps 2011; Kafka docs; KIP-500 |
| 32 | Event-Driven Patterns | 3–4 | A | 26 | A6 | Outbox; saga orchestration | — | Garcia-Molina 1987 (Sagas); Richardson |
| 33 | Architecture Patterns | 2 | A | 20 | A2 | Each pattern's structure | — | Fowler; Cockburn (hexagonal); Martin |
| 34 | Microservices | 3 | A | 28 | A2 | Bounded contexts; mesh; strangler | — | Evans 2003; Newman 2021 |
| 35 | Object-Oriented Design | 1–2 | A | 18 | A2 | Class diagrams | — | GoF 1994; Meyer |
| 36 | SOLID | 2 | A | 16 | A2 | Before/after class diagrams | — | Martin 2017 |
| 37 | Design Patterns | 2 | A | 28 | A2 | One class diagram per pattern | — | GoF 1994 |
| 38 | UML & LLD | 2–3 | A | 30 | A2 | All UML types; 8 LLD solutions | — | OMG UML 2.5; Fowler *UML Distilled* |
| 39 | Reliability & Resilience | 3 | A | 26 | A7 | DR topologies; error-budget flow | SLO math, burn rates | Google SRE books |
| 40 | Observability | 3 | A | 24 | A7 | Telemetry pipeline; trace tree | Cardinality, sampling | Sigelman 2010 (Dapper); OpenTelemetry docs |
| 41 | Cloud Computing | 2 | A | 26 | A7 | VPC layout; service mapping | Cost estimates | AWS/GCP/Azure docs |
| 42 | Containers & Kubernetes | 3 | A | 32 | A7 | Control plane; pod networking | Resource requests, HPA formula | Kubernetes docs; Burns 2016 |
| 43 | Deployment & Infrastructure | 3 | A | 22 | A7 | Blue–green; canary; GitOps | Canary statistics | Humble & Farley; Terraform docs |
| 44 | Multi-Region Systems | 4 | A | 24 | A7 | Active–active; cell architecture | Cross-region latency budgets | AWS Builders' Library; Spanner |
| 45 | Advanced Consistency & BFT | 5 | A | 22 | A5 | PBFT phases | 3f+1 bound | Castro & Liskov 1999; Yin 2019 (HotStuff) |
| 46 | Distributed Scheduling | 4 | S | 22 | A10 | Borg architecture; gang scheduling | DRF allocation | Verma 2015; Ghodsi 2011 (DRF) |
| 47 | Multi-Tenancy | 4 | S | 20 | A7 | Tenancy models; isolation stack | Quota math | Agache 2020 (Firecracker) |
| 48 | Edge & Serverless | 4 | A | 20 | A7 | Lambda invoke path; edge runtime | Cold-start impact | Agache 2020; Jonas 2019 |
| 49 | Large-Scale Data & HPC | 4–5 | S | 22 | A9 | Data platform; RDMA | Exabyte storage cost | Colossus/Tectonic papers; MPI |
| 50 | Security Architecture & Privacy | 4 | S | 26 | Sec | Zero-trust; privacy pipeline | DP epsilon | BeyondCorp; Dwork & Roth 2014 |
| 51 | Cost & Sustainability | 4 | S | 18 | A7 | FinOps loop | Unit economics, PUE | FinOps Foundation; Barroso *Datacenter as a Computer* |
| 52 | Case Studies I (7) | 2–4 | A | 70 | A2/A4 | Full 16-section set per case | Full estimates | Per case |
| 53 | Case Studies II (5) | 3–4 | A | 55 | A2 | " | " | Per case |
| 54 | Case Studies III (5) | 3–4 | A | 55 | A4 | " | " | Per case |
| 55 | Case Studies IV (6) | 3–4 | A | 65 | A4/A5 | " | " | Per case |
| 56 | Case Studies V (4) | 3–4 | A | 45 | A3/A9 | " | " | Per case |
| 57 | ML Fundamentals | 2 | B | 32 | A8 | Train/infer loop; confusion matrix | All classification/regression/ranking metrics; A/B test sample size | Hastie et al.; Goodfellow et al. |
| 58 | Deep Learning Essentials | 2–3 | B | 24 | A8 | MLP; backprop graph | Parameter and activation memory | Goodfellow et al. 2016 |
| 59 | ML Lifecycle | 2 | B | 18 | A8 | Lifecycle loop | — | Google MLOps whitepaper; Sculley 2015 |
| 60 | ML System Architecture | 3 | B | 24 | A8 | Offline/nearline/online | Latency budget split | Huyen 2022; Sculley 2015 |
| 61 | Data Engineering for ML | 3 | B | 30 | A9 | Lakehouse; streaming pipeline | Storage/compute sizing | Armbrust 2021 (Lakehouse); Iceberg/Delta docs |
| 62 | Feature Stores | 3 | B | 24 | A9 | Online/offline store; PIT join | Freshness/latency | Feast docs; Uber Michelangelo blog |
| 63 | Data Labeling & Quality | 3 | B | 16 | A9 | Labeling pipeline; active learning | Label cost | Ratner 2017 (Snorkel); Gebru 2021 |
| 64 | GPU Architecture | 3–4 | B | 28 | A10 | SM layout; memory hierarchy; roofline | FLOPs, bandwidth, arithmetic intensity | NVIDIA docs; Williams 2009 (roofline) |
| 65 | Distributed Training | 4 | B | 36 | A10 | DP/TP/PP/EP; ring all-reduce | Comm volume, 6ND FLOPs, memory per GPU | Megatron; ZeRO; GPipe; Kaplan 2020 |
| 66 | Model Serving | 3 | B | 28 | A11 | Server architecture; batching | Batch size vs latency/throughput | Triton docs; Crankshaw 2017 (Clipper) |
| 67 | Model Optimization | 4 | B | 24 | A11 | Optimization pipeline | Quantization memory savings | Jacob 2018; Hinton 2015; TensorRT docs |
| 68 | Recommendation Architecture | 4 | B | 28 | A11 | Multi-stage funnel; two-tower | Candidate counts, embedding table size | Covington 2016; Naumov 2019 |
| 69 | MLOps | 3–4 | B | 28 | A12 | CI/CD/CT pipeline; registry | — | Google MLOps levels; MLflow docs |
| 70 | ML Monitoring | 3 | B | 22 | A12 | Monitoring pipeline | PSI, KS, KL/JS | Rabanser 2019; Gama 2014 |
| 71 | Responsible ML | 4 | B | 20 | A12 | Fairness pipeline; federated learning | Fairness metrics; DP-SGD | Mitchell 2019; McMahan 2017; Abadi 2016 |
| 72 | LLM Fundamentals | 3 | B | 30 | A13 | Transformer block; attention | Attention FLOPs, KV size | Vaswani 2017; Su 2021 (RoPE) |
| 73 | LLM Inference | 4 | B | 36 | A13 | Serving stack; paged KV; spec decoding | KV memory, TTFT/TPOT, tokens/s/GPU | Kwon 2023; Yu 2022; Leviathan 2023 |
| 74 | Vector Search | 3–4 | B | 24 | A13 | HNSW layers; IVF-PQ | Recall@k, memory per vector | Malkov 2018; Jégou 2011 |
| 75 | RAG | 4 | B | 30 | A13 | Ingestion + query pipelines | Context budget, retrieval metrics | Lewis 2020; Robertson 2009 |
| 76 | LLM Adaptation | 4 | B | 22 | A13 | SFT/RLHF/DPO pipelines | LoRA parameter count | Hu 2021; Ouyang 2022; Rafailov 2023 |
| 77 | Agents | 4 | B | 30 | A13 | Agent loop; orchestrator; sandbox | Cost/latency per step | Yao 2023 (ReAct); MCP spec; Anthropic "Building effective agents" 2024 |
| 78 | LLM Evaluation | 4 | B | 24 | A13 | Eval pipeline; router | Judge agreement | Zheng 2023 (LLM-as-judge); Greshake 2023 |
| 79 | Production AI Infrastructure | 4–5 | B | 26 | A13 | Gateway/router platform | Token-based quotas, cost allocation | Vendor docs; engineering blogs |
| 80 | Large-Scale AI Infrastructure | 5 | B | 24 | A13 | Cluster topology | Goodput, MTBF at scale | Llama 3 paper 2024; Meta infra blog; Jouppi 2023 |
| 81–86 | ML/AI case studies (27) | 3–5 | B | 270 | A8–A13 | Full case template + ML extension | Full estimates incl. GPU | Per case |
| 87 | Interview Fundamentals | 2 | S | 18 | A15 | Interview timeline | — | Public interview guides |
| 88 | Readiness Framework | 2–5 | S | 22 | A15 | 14-step flow; ML extension | — | — |
| 89 | Capacity Estimation | 2–4 | S | 32 | A4/A15 | Estimation trees | All formulas from brief §54 | Ch 4 sources |
| 90 | Company Preparation | 3–5 | S | 30 | A15 | — | — | Company career pages (verified only) |
| 91 | Practice Library I (≥55 Qs) | 2–5 | A | 120 | A15 | One per question | Per question | — |
| 92 | Practice Library II (≥50 Qs) | 3–5 | B | 110 | A15 | One per question | Per question | — |
| 93 | Project Handbook (20) | 1–5 | S | 100 | Proj | One per project | Load-test targets | — |
| App A–I | Glossary, bibliography, formulas, diagrams, roadmap, numbers, comparisons, open questions, index | — | S | 150 | A16 | Diagram collection (generated) | Formula handbook | — |

**Total estimated length:** ≈ 2,900 printed pages across all deliverables (Book I ≈ 1,350; Book II ≈ 1,000; Book III ≈ 400; appendices ≈ 150). This exceeds the brief's 600–1,000-page minimum because the brief requires 49 full case studies and ≥100 fully solved practice questions; the separate deliverable volumes keep each PDF at a manageable size.
