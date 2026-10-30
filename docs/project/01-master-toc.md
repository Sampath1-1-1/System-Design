# 1. Master Table of Contents

The knowledge base is organized as **three books, nineteen parts, 93 chapters and nine appendices**. Book I is Deliverable 1 (Traditional System Design), Book II is Deliverable 2 (ML & AI System Design), Book III holds the interview handbooks (Deliverables 7–8) and the project handbook (Deliverable 6). Appendices supply Deliverables 3, 4, 5, 9 and 10.

The chapter numbering below is canonical. A crosswalk from the numbering in the original project brief is in §1.5.

Levels: **L1** Absolute beginner · **L2** Intermediate · **L3** Advanced · **L4** Senior/Staff · **L5** Principal. Track: **A** traditional, **B** ML/AI, **S** shared.

---

## Front matter

- Preface — who this book is for and how it was built
- How to use this knowledge base (reading paths per level and per goal)
- The five proficiency levels (summary; full detail in Appendix E)
- Notation, units and conventions (diagram legend, callout legend, SI vs binary prefixes)

---

# BOOK I — TRADITIONAL SYSTEM DESIGN AND DISTRIBUTED SYSTEMS

## Part I — Foundations of System Design Thinking

**Ch 1 — What Is System Design?** (L1, S)
1.3 Definition of system design · 1.4 Software architecture · 1.5 High-level vs low-level design · 1.6 Functional requirements · 1.7 Non-functional requirements (the "-ilities" catalog) · 1.8 Architectural decision-making and ADRs · 1.9 Why system design matters (cost of wrong decisions) · 1.10 How system design is practiced in industry (design docs, reviews, RFCs) · 1.11 How system design interviews work · 1.12 Common beginner mistakes

**Ch 2 — How to Think Like a System Designer** (L1–L2, S)
2.3 Decomposition into components · 2.4 System boundaries and context diagrams · 2.5 Understanding and negotiating requirements · 2.6 Identifying bottlenecks (the resource model: CPU, memory, disk, network, locks) · 2.7 Making and stating assumptions · 2.8 Evaluating trade-offs (decision matrices, reversibility, "one-way vs two-way doors") · 2.9 Designing for failure · 2.10 Reasoning about scale (orders of magnitude) · 2.11 Back-of-the-envelope capacity estimation (intro; full treatment Ch 89) · 2.12 Architecture documentation (C4 model, design docs, ADRs)

**Ch 3 — The System Design Learning Method** (L1, S)
3.3 The ten-step concept-mastery loop · 3.4 Active recall, spaced repetition and the Feynman technique applied to architecture · 3.5 Reading papers and engineering blogs · 3.6 Drawing architecture from memory · 3.7 Building simplified implementations · 3.8 Beginner methodology (12-month path) · 3.9 Advanced methodology for experienced engineers (gap analysis, design reviews, postmortem study) · 3.10 Tracking progress

**Ch 4 — Quantitative Foundations for System Design** (L1–L3, S)
4.3 Exponents, powers of two and powers of ten · 4.4 Logarithms (why B-trees and binary search are fast) · 4.5 Units: bits, bytes, rates, SI vs binary prefixes · 4.6 Probability essentials (independence, union/intersection, expected value) · 4.7 Statistics: mean, median, variance, distributions, heavy tails · 4.8 Percentiles and tail latency (p50/p99/p999, fan-out amplification) · 4.9 Basic linear algebra (vectors, dot products, matrices — preparation for ML) · 4.10 Queueing theory (M/M/1, utilization vs latency) · 4.11 Little's Law · 4.12 Amdahl's Law and Gustafson's Law · 4.13 Universal Scalability Law · 4.14 Availability arithmetic (series, parallel, nines) · 4.15 Reliability: MTBF, MTTR, failure rates · 4.16 Durability and replication probability · 4.17 Latency numbers every engineer should know (with dated values) · 4.18 Relationships: latency↔throughput, availability↔reliability, replication↔durability, accuracy↔latency, GPU utilization↔throughput, batch size↔latency

## Part II — Computer Science Foundations

**Ch 5 — Computer Architecture** (L1, S)
5.3 CPU, cores, registers, instruction pipeline · 5.4 CPU caches (L1/L2/L3, cache lines, false sharing) · 5.5 RAM and the memory hierarchy · 5.6 Storage devices (HDD, SATA/NVMe SSD, persistent memory) · 5.7 I/O operations (blocking, DMA, interrupts, polling) · 5.8 CPU-bound vs I/O-bound workloads · 5.9 Memory latency and bandwidth · 5.10 NUMA · 5.11 SIMD and accelerators (preview of GPUs) · 5.12 Throughput vs latency at the hardware level

**Ch 6 — Operating Systems** (L1–L2, S)
6.3 Processes and threads · 6.4 Context switching and its cost · 6.5 CPU scheduling · 6.6 Virtual memory and paging, page cache, mmap · 6.7 System calls and the kernel/user boundary · 6.8 Concurrency vs parallelism · 6.9 Race conditions and critical sections · 6.10 Mutexes, semaphores, condition variables, atomics, lock-free structures · 6.11 Deadlock, livelock, starvation · 6.12 Inter-process communication · 6.13 I/O models: blocking, non-blocking, epoll/kqueue/io_uring, event loops · 6.14 File systems and fsync · 6.15 Concurrency models in practice (thread-per-request, event loop, actors, green threads/goroutines, async/await)

**Ch 7 — Networking Fundamentals** (L1–L2, S)
7.3 OSI and TCP/IP models · 7.4 IP addressing, IPv4/IPv6, subnets and CIDR · 7.5 Routing basics, BGP, anycast · 7.6 DNS (resolution, record types, TTL, DNS-based load balancing) · 7.7 TCP (handshake, flow control, congestion control, head-of-line blocking) · 7.8 UDP · 7.9 HTTP/1.1, HTTP/2, HTTP/3 and QUIC · 7.10 TLS 1.3 and HTTPS · 7.11 WebSockets (intro; deep dive Ch 9) · 7.12 Proxies and reverse proxies · 7.13 NAT · 7.14 Firewalls and security groups · 7.15 Latency, bandwidth, BDP, packet loss · 7.16 Connection pooling and keep-alive · 7.17 Datacenter networking (leaf-spine, east-west traffic)

**Ch 8 — Web Application Fundamentals** (L1–L2, A)
8.3 Client–server architecture · 8.4 Frontend and backend; SPA, SSR, mobile clients · 8.5 The request–response lifecycle end to end · 8.6 REST API design (resources, verbs, status codes, pagination, filtering) · 8.7 GraphQL · 8.8 gRPC and RPC · 8.9 Serialization: JSON, Protocol Buffers, Avro, Thrift; schema evolution · 8.10 Cookies and sessions · 8.11 Authentication (passwords, MFA, sessions vs tokens) · 8.12 Authorization (RBAC, ABAC, ReBAC/Zanzibar) · 8.13 JWT · 8.14 OAuth 2.0 and OpenID Connect · 8.15 API versioning and compatibility · 8.16 API documentation (OpenAPI)

**Ch 9 — Real-Time Communication** (L2, A)
9.3 Short polling · 9.4 Long polling · 9.5 Server-Sent Events · 9.6 WebSockets in depth · 9.7 WebRTC basics · 9.8 Mobile push (APNs, FCM) · 9.9 Connection management at scale (gateways, sticky routing, presence) · 9.10 Choosing a real-time technique

**Ch 10 — Security Fundamentals for System Designers** (L2, S)
10.3 Threat modeling (STRIDE) · 10.4 Cryptography essentials (hashing, symmetric/asymmetric encryption, signatures, MACs) · 10.5 PKI and certificates · 10.6 Password storage · 10.7 OWASP Top 10 in architectural terms · 10.8 Secrets management · 10.9 Encryption at rest and in transit, KMS, envelope encryption · 10.10 Network security, zero trust, mTLS · 10.11 DDoS basics · 10.12 Audit logging

## Part III — Data Systems

**Ch 11 — Relational Databases** (L1–L2, A)
11.3 Relational model: tables, rows, columns · 11.4 Keys: primary, foreign, natural vs surrogate · 11.5 Normalization (1NF–BCNF) and denormalization · 11.6 SQL and joins (nested-loop, hash, merge) · 11.7 Indexes (clustered, secondary, composite, covering, partial) · 11.8 B-trees and B+ trees · 11.9 Query execution and plans · 11.10 Query optimization (cost-based optimizer, statistics, EXPLAIN) · 11.11 Transactions · 11.12 ACID · 11.13 Isolation levels and anomalies · 11.14 MVCC · 11.15 Locking (2PL, row/table locks, deadlocks) · 11.16 PostgreSQL vs MySQL · 11.17 Data modeling for real applications

**Ch 12 — NoSQL Databases** (L2, A)
12.3 Why NoSQL emerged · 12.4 Key-value stores · 12.5 Document databases · 12.6 Wide-column stores · 12.7 Graph databases · 12.8 Time-series databases · 12.9 Search engines as databases (preview of Ch 16) · 12.10 Vector databases (preview of Ch 74) · 12.11 NewSQL · 12.12 Selection framework and SQL vs NoSQL comparison · 12.13 Polyglot persistence

**Ch 13 — Storage Engine Internals** (L3, A)
13.3 Pages and blocks · 13.4 Buffer pools · 13.5 Write-ahead logging and recovery (ARIES overview) · 13.6 B-tree storage engines · 13.7 Log-structured storage · 13.8 LSM trees: memtables, SSTables · 13.9 Compaction strategies (size-tiered, levelled) · 13.10 Bloom filters in storage · 13.11 Read, write and space amplification · 13.12 Durability: fsync, checksums, torn writes · 13.13 Columnar storage · 13.14 Case studies: InnoDB, RocksDB, PostgreSQL heap

**Ch 14 — Database Scaling: Replication, Partitioning and Sharding** (L2–L3, A)
14.3 Read replicas and primary–replica architecture · 14.4 Synchronous vs asynchronous replication, replication lag · 14.5 Multi-primary replication · 14.6 Partitioning (range, hash, list, directory) · 14.7 Sharding strategies and shard keys · 14.8 Consistent hashing and virtual nodes · 14.9 Rebalancing · 14.10 Hot partitions and skew mitigation · 14.11 Secondary indexes in partitioned databases · 14.12 Cross-shard queries and distributed transactions (preview of Ch 28) · 14.13 Connection pooling and proxies (PgBouncer, Vitess, ProxySQL)

**Ch 15 — Object, Block and File Storage** (L2–L3, A)
15.3 Block, file and object storage compared · 15.4 Object storage architecture (S3 model) · 15.5 Distributed file systems (GFS, HDFS, Colossus as published) · 15.6 Replication vs erasure coding · 15.7 Metadata services · 15.8 Multipart upload, chunking, deduplication · 15.9 Storage tiers and lifecycle policies

**Ch 16 — Search Systems** (L3, A)
16.3 Inverted indexes · 16.4 Tokenization and analysis · 16.5 Ranking: TF-IDF and BM25 · 16.6 Index construction and segment merging · 16.7 Distributed search (sharding, replication, scatter-gather) · 16.8 Elasticsearch/OpenSearch architecture · 16.9 Typeahead and autocomplete (tries) · 16.10 Near-real-time indexing

**Ch 17 — Data Structures and Algorithms for Scale** (L2–L3, A)
17.3 Hash functions and hashing at scale · 17.4 Bloom filters and cuckoo filters · 17.5 HyperLogLog · 17.6 Count-Min sketch and heavy hitters · 17.7 Skip lists · 17.8 Merkle trees · 17.9 Geospatial indexing (geohash, quadtrees, S2, H3) · 17.10 Unique ID generation (UUID, Snowflake, ULID) · 17.11 Tries · 17.12 Reservoir sampling and streaming algorithms

## Part IV — Scalability and Performance

**Ch 18 — Scalability** (L2, A)
18.3 Vertical scaling · 18.4 Horizontal scaling · 18.5 Stateless vs stateful services · 18.6 Load distribution · 18.7 Bottleneck identification · 18.8 Scaling application servers · 18.9 Scaling databases (overview) · 18.10 Scale cube (X/Y/Z axes) · 18.11 Capacity planning

**Ch 19 — Load Balancing** (L2, A)
19.3 Layer 4 vs Layer 7 · 19.4 Algorithms: round robin, weighted RR, least connections, least response time, power of two choices, consistent hashing, Maglev · 19.5 Health checks · 19.6 Session affinity · 19.7 Active–passive and active–active · 19.8 Load balancer failure and redundancy (VRRP, anycast, ECMP) · 19.9 DNS and global server load balancing · 19.10 Client-side load balancing

**Ch 20 — Caching** (L2, A)
20.3 Cache fundamentals and hit ratio · 20.4 CPU cache vs application cache · 20.5 Where to cache (client, CDN, gateway, application, database) · 20.6 Redis and Memcached internals · 20.7 Cache-aside, read-through, write-through, write-back, write-around · 20.8 TTL · 20.9 Eviction: LRU, LFU, ARC, TinyLFU · 20.10 Cache invalidation · 20.11 Cache stampede · 20.12 Cache penetration · 20.13 Cache avalanche · 20.14 Distributed caching and consistent hashing · 20.15 Hot keys · 20.16 Redis vs Memcached

**Ch 21 — Content Delivery Networks** (L2, A)
21.3 CDN architecture · 21.4 Edge, mid-tier and origin · 21.5 Cache hierarchy and origin shielding · 21.6 Cache keys and invalidation/purge · 21.7 Static vs dynamic content · 21.8 Video delivery (HLS/DASH, adaptive bitrate) · 21.9 Edge computing on CDNs · 21.10 Netflix Open Connect (public material)

**Ch 22 — API and Traffic Management** (L2–L3, A)
22.3 Rate limiting · 22.4 Token bucket · 22.5 Leaky bucket · 22.6 Fixed window · 22.7 Sliding window log and sliding window counter · 22.8 Distributed rate limiting · 22.9 Throttling and load shedding · 22.10 Backpressure · 22.11 Timeouts and deadlines · 22.12 Retries with exponential backoff and jitter; retry budgets · 22.13 Circuit breakers · 22.14 Bulkheads · 22.15 Idempotency and idempotency keys

**Ch 23 — Performance Engineering** (L3, A)
23.3 Performance methodology (USE, RED, golden signals) · 23.4 Profiling CPU and memory · 23.5 Load testing and benchmarking pitfalls (coordinated omission) · 23.6 Tail latency at scale · 23.7 Hedged and tied requests · 23.8 Batching, pipelining and compression · 23.9 Garbage collection and runtime effects · 23.10 Capacity models from measurements

## Part V — Distributed Systems

**Ch 24 — Distributed Systems Fundamentals** (L2–L3, A)
24.3 What is a distributed system? · 24.4 Why distributed systems exist · 24.5 The fallacies of distributed computing · 24.6 System models: synchrony, failure models (crash-stop, crash-recovery, omission, Byzantine) · 24.7 Network partitions · 24.8 Partial failures · 24.9 Physical clocks, NTP, PTP, clock skew · 24.10 Logical clocks: Lamport clocks · 24.11 Vector clocks and version vectors · 24.12 Hybrid logical clocks · 24.13 FLP impossibility (intuition) · 24.14 End-to-end argument

**Ch 25 — Consistency and Availability** (L3, A)
25.3 Linearizability (strong consistency) · 25.4 Sequential consistency · 25.5 Causal consistency · 25.6 Session guarantees: read-your-writes, monotonic reads, monotonic writes, writes-follow-reads · 25.7 Eventual consistency · 25.8 CAP theorem (precise statement and misreadings) · 25.9 PACELC · 25.10 Consistency trade-offs in real databases · 25.11 Jepsen-style testing

**Ch 26 — Consensus and Coordination** (L3–L4, A)
26.3 The consensus problem · 26.4 Quorums · 26.5 Leader election · 26.6 Paxos (single-decree and Multi-Paxos) · 26.7 Raft (election, log replication, safety, membership changes) · 26.8 ZooKeeper and ZAB · 26.9 etcd · 26.10 Distributed locks · 26.11 Leases · 26.12 Split brain · 26.13 Fencing tokens · 26.14 Coordination services in practice (Chubby)

**Ch 27 — Replication and Fault Tolerance** (L3, A)
27.3 Replication strategies overview · 27.4 Primary–backup · 27.5 Chain replication · 27.6 Multi-leader · 27.7 Leaderless replication (Dynamo-style) · 27.8 Read and write quorums (R + W > N) · 27.9 Sloppy quorums and hinted handoff · 27.10 Failure detection (heartbeats, phi-accrual, gossip/SWIM) · 27.11 Failover · 27.12 Recovery · 27.13 Anti-entropy and read repair · 27.14 Conflict resolution: LWW, vector clocks, CRDTs

**Ch 28 — Distributed Transactions** (L4, A)
28.3 Why distributed transactions are hard · 28.4 Two-phase commit · 28.5 Three-phase commit · 28.6 Sagas (preview; deep dive Ch 32) · 28.7 Percolator-style transactions · 28.8 Spanner and TrueTime · 28.9 Calvin and deterministic databases · 28.10 Distributed SQL (CockroachDB, YugabyteDB, TiDB) · 28.11 Choosing a transaction strategy

**Ch 29 — Distributed Data Processing** (L3, A/B)
29.3 Batch processing concepts · 29.4 MapReduce · 29.5 Apache Spark (RDDs, DataFrames, DAG scheduler, Catalyst) · 29.6 Partitioning and shuffle · 29.7 Data locality · 29.8 Stream processing concepts (event time, watermarks, windows) · 29.9 Apache Flink · 29.10 Lambda and Kappa architectures · 29.11 Batch vs stream; Spark vs Flink

## Part VI — Messaging and Event-Driven Systems

**Ch 30 — Messaging Fundamentals** (L2, A)
30.3 Synchronous vs asynchronous communication · 30.4 Message queues · 30.5 Publish/subscribe · 30.6 Event-driven architecture · 30.7 Event brokers (RabbitMQ, SQS/SNS, Pub/Sub, Pulsar) · 30.8 Delivery guarantees · 30.9 Ordering · 30.10 Retries and poison messages · 30.11 Dead-letter queues · 30.12 Kafka vs RabbitMQ

**Ch 31 — Kafka Deep Dive** (L3, A)
31.3 The log abstraction · 31.4 Brokers and clusters (ZooKeeper vs KRaft) · 31.5 Topics and partitions · 31.6 Producers (batching, acks, idempotence) · 31.7 Consumers and consumer groups · 31.8 Offsets · 31.9 Replication, ISR and leader election · 31.10 Retention and log compaction · 31.11 Delivery semantics and transactions · 31.12 Rebalancing protocols · 31.13 Performance (zero-copy, page cache, sequential I/O) · 31.14 Kafka Streams and Connect · 31.15 Operating Kafka

**Ch 32 — Event-Driven Architecture Patterns** (L3–L4, A)
32.3 Event sourcing · 32.4 CQRS · 32.5 Transactional outbox · 32.6 Change data capture · 32.7 Saga pattern · 32.8 Choreography vs orchestration · 32.9 Exactly-once processing and its limits · 32.10 Idempotent consumers · 32.11 Workflow engines (Temporal, Step Functions)

## Part VII — Software Architecture and Design

**Ch 33 — Architecture Patterns** (L2, A)
33.3 Layered · 33.4 Monolithic · 33.5 Modular monolith · 33.6 Service-oriented architecture · 33.7 Microservices (overview) · 33.8 Event-driven · 33.9 Serverless · 33.10 Hexagonal (ports and adapters) · 33.11 Clean architecture · 33.12 Cell-based architecture · 33.13 Monolith vs microservices

**Ch 34 — Microservices** (L3, A)
34.3 Service boundaries · 34.4 Domain-driven design · 34.5 Bounded contexts and context maps · 34.6 API gateways and BFF · 34.7 Service discovery · 34.8 Inter-service communication · 34.9 Distributed tracing (intro) · 34.10 Service mesh · 34.11 Data ownership, database-per-service · 34.12 Deployment strategies · 34.13 Migration from monolith (strangler fig) · 34.14 Anti-patterns (distributed monolith)

**Ch 35 — Object-Oriented Design** (L1–L2, A)
35.3 Classes and objects · 35.4 Encapsulation · 35.5 Inheritance · 35.6 Polymorphism · 35.7 Abstraction · 35.8 Composition over inheritance · 35.9 Interfaces and contracts · 35.10 Cohesion and coupling

**Ch 36 — SOLID Principles** (L2, A)
36.3 Single Responsibility · 36.4 Open/Closed · 36.5 Liskov Substitution · 36.6 Interface Segregation · 36.7 Dependency Inversion · 36.8 SOLID at the architecture level

**Ch 37 — Design Patterns** (L2, A)
37.3 Factory · 37.4 Abstract factory · 37.5 Builder · 37.6 Singleton · 37.7 Strategy · 37.8 Observer · 37.9 Adapter · 37.10 Decorator · 37.11 Proxy · 37.12 Command · 37.13 Repository · 37.14 Dependency injection · 37.15 State, Template Method, Chain of Responsibility · 37.16 Concurrency patterns

**Ch 38 — UML and Low-Level Design** (L2–L3, A)
38.3 Class diagrams · 38.4 Sequence diagrams · 38.5 Component diagrams · 38.6 State diagrams · 38.7 Activity diagrams · 38.8 Object relationships · 38.9 LLD method · 38.10 LLD exercises: parking lot, elevator system, LRU cache, vending machine, library system, rate limiter class design, in-memory KV store, chess

## Part VIII — Production Infrastructure and Operations

**Ch 39 — Reliability and Resilience** (L3, A)
39.3 Availability vs reliability · 39.4 Fault tolerance and redundancy · 39.5 Graceful degradation · 39.6 SLI, SLO, SLA · 39.7 Error budgets · 39.8 Disaster recovery, RTO, RPO · 39.9 Backup strategies · 39.10 Multi-region architecture (intro; deep dive Ch 44) · 39.11 Chaos engineering · 39.12 Incident management and blameless postmortems

**Ch 40 — Observability** (L3, A)
40.3 Monitoring vs observability · 40.4 Logs · 40.5 Metrics (counters, gauges, histograms; cardinality) · 40.6 Traces and distributed tracing · 40.7 OpenTelemetry · 40.8 Prometheus · 40.9 Grafana · 40.10 Alerting (symptom-based, burn-rate alerts) · 40.11 Root cause analysis · 40.12 Profiling in production

**Ch 41 — Cloud Computing** (L2, A)
41.3 IaaS, PaaS, SaaS, FaaS · 41.4 Regions, zones and the shared responsibility model · 41.5 AWS core services · 41.6 GCP core services · 41.7 Azure core services · 41.8 Compute · 41.9 Storage · 41.10 Networking (VPC, subnets, peering, private link) · 41.11 Managed databases · 41.12 Cloud security (IAM) · 41.13 Cost optimization · 41.14 Cross-cloud service mapping table

**Ch 42 — Containers and Kubernetes** (L3, A)
42.3 Containers (namespaces, cgroups) · 42.4 Docker, images, layers · 42.5 Registries · 42.6 Kubernetes architecture (control plane, etcd, kubelet) · 42.7 Pods · 42.8 Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs · 42.9 Services and kube-proxy · 42.10 Ingress and Gateway API · 42.11 ConfigMaps and Secrets · 42.12 Autoscaling (HPA, VPA, cluster autoscaler) · 42.13 Scheduling · 42.14 Persistent volumes · 42.15 Operators and CRDs · 42.16 Kubernetes vs serverless

**Ch 43 — Deployment and Infrastructure** (L3, A)
43.3 CI/CD · 43.4 Rolling deployments · 43.5 Blue–green deployments · 43.6 Canary releases · 43.7 Feature flags · 43.8 Infrastructure as code · 43.9 Terraform · 43.10 GitOps · 43.11 Secrets management in pipelines · 43.12 Infrastructure monitoring · 43.13 Database migrations

## Part IX — Advanced and Expert Topics

**Ch 44 — Multi-Region and Global Systems** (L4, A) — global traffic management, geo-DNS, anycast, geo-replication, active–active vs active–passive, data residency, conflict handling, cell architecture
**Ch 45 — Advanced Consistency and Byzantine Fault Tolerance** (L5, A) — consistency hierarchy (Jepsen map), snapshot isolation vs serializability, CRDT theory, BFT, PBFT, HotStuff, blockchain consensus overview
**Ch 46 — Distributed Scheduling and Cluster Management** (L4, S) — Borg, Omega, Mesos, Kubernetes scheduler, bin-packing, preemption, gang scheduling, fairness (DRF)
**Ch 47 — Multi-Tenant Architecture and Isolation** (L4, S) — tenancy models, noisy neighbours, quotas, isolation levels (process, VM, microVM/Firecracker, gVisor), tenant-aware sharding
**Ch 48 — Edge Computing and Serverless at Scale** (L4, A) — edge runtimes, cold starts, Lambda internals (Firecracker), serverless data patterns, limits
**Ch 49 — Large-Scale Data Infrastructure and High-Performance Computing** (L4–L5, S) — exabyte storage, data platform architecture, HPC (MPI, RDMA, InfiniBand), batch schedulers
**Ch 50 — Security Architecture and Privacy Engineering** (L4, S) — defense in depth, zero trust (BeyondCorp), identity architecture, supply-chain security, privacy by design, GDPR/CCPA engineering, data minimization, differential privacy intro
**Ch 51 — Cost-Aware and Sustainable Architecture** (L4, S) — unit economics, FinOps, reserved/spot capacity, cost modeling, carbon-aware computing, efficiency metrics (PUE)

## Part X — Traditional System Design Case Studies (16-section format)

**Ch 52 — Case Studies I: Foundational Services** — 52.1 URL Shortener · 52.2 Pastebin · 52.3 Rate Limiter · 52.4 Notification System · 52.5 Distributed Key-Value Store · 52.6 Distributed Job Scheduler · 52.7 Web Crawler
**Ch 53 — Case Studies II: Social and Communication** — 53.1 Chat Application · 53.2 WhatsApp · 53.3 Instagram · 53.4 Facebook News Feed · 53.5 Twitter/X
**Ch 54 — Case Studies III: Media and Files** — 54.1 YouTube · 54.2 Netflix · 54.3 Spotify · 54.4 Google Drive · 54.5 Dropbox
**Ch 55 — Case Studies IV: Location, Commerce and Payments** — 55.1 Uber · 55.2 Ride Matching System · 55.3 Google Maps · 55.4 Amazon E-commerce · 55.5 Ticket Booking System · 55.6 Payment System
**Ch 56 — Case Studies V: Data Platforms** — 56.1 Search Engine · 56.2 Recommendation System (systems view) · 56.3 Logging and Monitoring Platform · 56.4 Real-time Analytics Platform

---

# BOOK II — MACHINE LEARNING AND AI SYSTEM DESIGN

## Part XI — ML Foundations

**Ch 57 — Machine Learning Fundamentals for System Designers** (L2, B) — what ML is; supervised, unsupervised, self-supervised, reinforcement learning; training vs inference; features and labels; train/validation/test splits; overfitting/underfitting; bias–variance; loss functions and gradient descent; classification metrics (precision, recall, F1, ROC-AUC, PR-AUC, log loss, calibration); regression metrics (MAE, RMSE, MAPE); ranking metrics (NDCG, MAP, MRR); offline vs online evaluation; A/B testing statistics
**Ch 58 — Deep Learning Essentials for System Designers** (L2–L3, B) — neurons, MLPs, backpropagation, optimizers, embeddings, CNNs, RNNs, transformers (preview), training dynamics, memory footprint of training; traditional ML vs deep learning
**Ch 59 — The ML Lifecycle** (L2, B) — data collection, ingestion, validation, feature engineering, training, evaluation, deployment, monitoring, retraining, versioning, reproducibility; maturity levels
**Ch 60 — ML System Architecture** (L3, B) — ML vs traditional systems; data-centric vs model-centric; training and inference pipelines; offline/online/nearline; batch vs real-time ML; requirements; latency, throughput and quality; cost vs accuracy; hidden technical debt

## Part XII — ML Data Infrastructure

**Ch 61 — Data Engineering for ML** (L3, B) — ingestion, batch and streaming pipelines, ETL vs ELT, data lakes, warehouses, lakehouses (Delta, Iceberg, Hudi), Spark, Flink, Beam, file formats (Parquet, ORC, Avro), validation, quality, lineage, versioning (DVC, lakeFS), governance, orchestration
**Ch 62 — Feature Engineering and Feature Stores** (L3, B) — feature engineering, transformations, pipelines, offline and online stores, point-in-time correctness, training–serving skew, freshness, Feast and other architectures (Uber Michelangelo, Airbnb Zipline, Tecton), feature computation patterns; feature store vs data warehouse
**Ch 63 — Data Labeling, Quality and Data-Centric AI** (L3, B) — labeling pipelines, human annotation, weak supervision, active learning, label noise, synthetic data, dataset documentation (datasheets)

## Part XIII — Training Infrastructure

**Ch 64 — GPU Architecture and Performance** (L3–L4, B) — CPU vs GPU, SMs, warps, memory hierarchy (HBM, SRAM), CUDA model, tensor cores, memory bandwidth, FLOPS, roofline model, precision formats (FP32, TF32, FP16, BF16, FP8, INT8, FP4), utilization and MFU, compute- vs memory-bound, NVLink/NVSwitch/PCIe/InfiniBand, GPU scheduling (MIG, MPS, time-slicing)
**Ch 65 — Distributed ML Training** (L4, B) — single-machine → multi-GPU → multi-node; data parallelism (DDP), ZeRO/FSDP, tensor, pipeline, sequence/context and expert parallelism; 3D/4D parallelism; collectives (all-reduce, ring, tree, all-gather, reduce-scatter); NCCL; parameter servers; gradient synchronization; mixed precision; activation checkpointing; checkpointing and fault recovery; elastic training; bottlenecks; training FLOPs estimation; Ray, Slurm and Kubernetes for training

## Part XIV — Model Serving and Optimization

**Ch 66 — Model Serving** (L3, B) — online, offline, batch, real-time, sync, async and streaming inference; model servers (Triton, TorchServe, TensorFlow Serving, KServe, Ray Serve, BentoML); dynamic batching; model-parallel serving; autoscaling; model loading; versioning; shadow, canary and A/B deployment; online vs offline inference
**Ch 67 — ML Model Optimization** (L4, B) — quantization (dynamic, static, QAT, PTQ for LLMs: GPTQ, AWQ), pruning, distillation, ONNX, ONNX Runtime, TensorRT, compilation (XLA, TorchInductor, TVM), operator fusion, memory optimization, latency/throughput optimization; TensorRT vs ONNX Runtime
**Ch 68 — Recommendation and Ranking Systems Architecture** (L4, B) — multi-stage funnel (candidate generation, filtering, ranking, re-ranking), two-tower models, embedding retrieval with ANN, DLRM and embedding tables, feature crossing, exploration/exploitation, feedback loops, real-time personalization

## Part XV — MLOps and Responsible ML

**Ch 69 — MLOps and ML Platforms** (L3–L4, B) — CI/CD/CT for ML, experiment tracking, MLflow, model registry, pipeline orchestration (Kubeflow, Airflow, Metaflow, Flyte), governance, reproducibility, model monitoring hooks, drift detection, rollback; platform case studies (Michelangelo, TFX, FBLearner as published)
**Ch 70 — ML Monitoring** (L3, B) — data, concept, feature and prediction drift; statistical tests (PSI, KS, KL/JS divergence); performance degradation with delayed labels; prediction quality; freshness; latency; GPU utilization; cost; retraining triggers
**Ch 71 — Responsible ML: Fairness, Privacy and Explainability** (L4, B) — fairness metrics, bias mitigation, explainability (SHAP, LIME), differential privacy, federated learning, model cards, regulation (EU AI Act overview)

## Part XVI — LLM and AI Systems

**Ch 72 — LLM Fundamentals** (L3, B) — transformer architecture, tokenization (BPE, SentencePiece), embeddings, attention, self-attention, multi-head/MQA/GQA, positional encoding (sinusoidal, RoPE), prefill and decode, KV cache, context windows, autoregressive generation, sampling, mixture of experts
**Ch 73 — LLM Inference Infrastructure** (L4, B) — serving architecture, GPU memory requirements, KV cache management, static/dynamic/continuous batching, PagedAttention, prefix caching, FlashAttention, speculative decoding, tensor/pipeline/expert parallelism for inference, disaggregated prefill/decode, quantization, TTFT, TPOT/ITL, tokens/s, goodput, utilization, cost optimization; engines compared (vLLM, TensorRT-LLM, SGLang, TGI, llama.cpp)
**Ch 74 — Embeddings, Vector Search and Vector Databases** (L3–L4, B) — embedding models, similarity metrics, exact vs approximate search, HNSW, IVF, PQ, ScaNN, DiskANN, filtering, vector database architecture, recall/latency trade-offs
**Ch 75 — RAG Architecture** (L4, B) — document ingestion, parsing, chunking, embedding generation, indexing, similarity search, hybrid search with BM25, reciprocal rank fusion, reranking (cross-encoders), query rewriting, context construction, grounded generation and citations, retrieval evaluation, RAG monitoring, GraphRAG and agentic RAG
**Ch 76 — LLM Adaptation: Prompting, Fine-Tuning and Alignment Pipelines** (L4, B) — prompting, in-context learning, structured output; SFT, LoRA/QLoRA, RLHF, DPO; RAG vs fine-tuning; training data pipelines for LLMs
**Ch 77 — AI Agents and Agentic Systems** (L4, B) — agent architecture, tool calling, planning (ReAct, plan-and-execute), memory, orchestration, multi-agent systems, workflow engines, state management, retries, guardrails, human-in-the-loop, evaluation, observability, failure handling, security and sandboxing, Model Context Protocol
**Ch 78 — LLM Evaluation and Reliability** (L4, B) — offline/online evaluation, benchmarks and their limits, LLM-as-a-judge, human evaluation, hallucination detection, groundedness, retrieval quality, safety, prompt injection, model routing, fallback models, cost–quality trade-offs
**Ch 79 — Production AI Infrastructure** (L4–L5, B) — model gateways, inference routers, multi-model serving, model registries, GPU clusters, distributed inference, autoscaling, multi-region AI, rate limiting by tokens, tenant isolation, AI observability, data privacy, cost allocation
**Ch 80 — Large-Scale AI Infrastructure** (L5, B) — building and operating 10k+ GPU clusters (networking topologies, storage for training, power and cooling, failure rates and goodput), publicly documented infrastructure from Meta, Google (TPU), NVIDIA, OpenAI, Anthropic

## Part XVII — ML and AI Case Studies

**Ch 81 — Case Studies VI: Recommendation, Search and Ads** — 81.1 YouTube Recommendations · 81.2 Instagram Recommendations · 81.3 Netflix Recommendations · 81.4 Search Ranking · 81.5 Product Recommendation · 81.6 Personalized Advertising · 81.7 Large-scale Recommendation Platform
**Ch 82 — Case Studies VII: Risk and Trust** — 82.1 Real-time Fraud Detection · 82.2 Credit Risk Prediction · 82.3 Spam Detection · 82.4 Content Moderation
**Ch 83 — Case Studies VIII: Marketplace Forecasting and Optimization** — 83.1 Ride Demand Prediction · 83.2 ETA Prediction · 83.3 Dynamic Pricing
**Ch 84 — Case Studies IX: Perception and Language** — 84.1 Face Recognition · 84.2 Image Classification Service · 84.3 Speech Recognition · 84.4 Real-time Translation
**Ch 85 — Case Studies X: ML Platforms** — 85.1 Feature Store · 85.2 Distributed Model Training Platform · 85.3 Multi-tenant ML Serving Platform · 85.4 Real-time ML Inference Platform
**Ch 86 — Case Studies XI: LLM and Agent Systems** — 86.1 Enterprise RAG Assistant · 86.2 LLM Inference Platform · 86.3 AI Coding Assistant · 86.4 Customer-Support Agent · 86.5 AI-powered Search

---

# BOOK III — INTERVIEWS AND PRACTICE

## Part XVIII — Interview Preparation

**Ch 87 — Interview Fundamentals** — what interviewers evaluate; requirements gathering; FR/NFR; estimation; API design; data modeling; diagrams; bottlenecks; trade-offs; communication; pacing a 45/60-minute interview
**Ch 88 — The Interview Readiness Framework** — the 14-step traditional sequence; the ML extension (problem formulation → retraining); rubrics by level (L3–L7 equivalents: junior, mid, senior, staff, principal)
**Ch 89 — Capacity Estimation Handbook** — RPS, DAU, peak traffic, storage, bandwidth, read/write ratio, replication overhead, cache hit ratio, database sizing, memory, GPU memory, training FLOPs, inference throughput, cost (all with worked examples)
**Ch 90 — Company-Level Interview Preparation** — Google, Amazon, Meta, Microsoft, Apple, Netflix, Uber, Airbnb, LinkedIn, Stripe, Databricks, Snowflake, OpenAI, Anthropic, NVIDIA (verified public information separated from general advice)
**Ch 91 — Interview Practice Library I: Traditional System Design** (≥ 55 questions, easy → expert)
**Ch 92 — Interview Practice Library II: ML and AI System Design** (≥ 50 questions, easy → expert)

## Part XIX — Practical Projects

**Ch 93 — Project Handbook** — 93.1 Beginner (REST API, URL shortener, Redis cache, rate limiter, load balancer simulation) · 93.2 Intermediate (message queue, distributed KV store, replicated DB simulation, notification service, real-time chat) · 93.3 Advanced (distributed job scheduler, event-driven microservices, real-time analytics pipeline, recommendation engine, distributed ML inference) · 93.4 Expert (distributed training platform, multi-tenant feature store, production RAG, scalable LLM inference platform, multi-agent orchestration platform)

---

# APPENDICES

- **A — Glossary** (Deliverable 9)
- **B — Bibliography and Research Reference Library** (Deliverable 10)
- **C — Formula and Quantitative Estimation Handbook** (Deliverable 5)
- **D — Architecture Diagram Collection** (Deliverable 4; generated from all chapters)
- **E — Learning Roadmap and Proficiency Levels** (Deliverable 3)
- **F — Latency, Throughput and Hardware Reference Numbers** (dated)
- **G — Technology Comparison Tables Index**
- **H — Unresolved Research Questions and Evidence Gaps**
- **I — Index**

---

## 1.5 Crosswalk from the original brief

| Brief chapter | Canonical chapter | Brief chapter | Canonical chapter |
|---|---|---|---|
| 1 What Is System Design | 1 | 29 Cloud Computing | 41 |
| 2 How to Think | 2 | 30 Containers & Kubernetes | 42 |
| 3 Learning Method | 3 | 31 Deployment | 43 |
| — (Maths, §6 of brief) | 4 | 32 OOD | 35 |
| 4 Computer Architecture | 5 | 33 SOLID | 36 |
| 5 Operating Systems | 6 | 34 Design Patterns | 37 |
| 6 Networking | 7 | 35 UML & LLD | 38 |
| 7 Web Fundamentals | 8 | Design problems (after 35) | 52–56 |
| 8 Relational DBs | 11 | 36 ML Fundamentals | 57 |
| 9 NoSQL | 12 | 37 ML Lifecycle | 59 |
| 10 Storage Engines | 13 | 38 ML System Architecture | 60 |
| 11 DB Scaling | 14 | 39 Data Engineering for ML | 61 |
| 12 Scalability | 18 | 40 Feature Stores | 62 |
| 13 Load Balancing | 19 | 41 Distributed Training | 65 |
| 14 Caching | 20 | 42 GPU Architecture | 64 |
| 15 CDNs | 21 | 43 Model Serving | 66 |
| 16 API & Traffic Mgmt | 22 | 44 Model Optimization | 67 |
| 17 Distributed Fundamentals | 24 | 45 MLOps | 69 |
| 18 Consistency & Availability | 25 | 46 ML Monitoring | 70 |
| 19 Consensus | 26 | ML case studies (after 46) | 81–85 |
| 20 Replication | 27 | 47 LLM Fundamentals | 72 |
| 21 Distributed Processing | 29 | 48 LLM Inference | 73 |
| 22 Messaging | 30 | 49 RAG | 74–75 |
| 23 Kafka | 31 | 50 Agents | 77 |
| 24 EDA Patterns | 32 | 51 LLM Evaluation | 78 |
| 25 Architecture Patterns | 33 | 52 Production AI Infra | 79 |
| 26 Microservices | 34 | Advanced list (after 52) | 28, 44–51, 80 |
| 27 Reliability | 39 | 53 Interview Fundamentals | 87–88 |
| 28 Observability | 40 | 54 Capacity Estimation | 89 |
| | | 55 Company Prep | 90 |
| | | 56 Practice Library | 91–92 |

**Chapters added beyond the brief** (gaps identified during planning): 4 Quantitative Foundations, 9 Real-Time Communication, 10 Security Fundamentals, 15 Object/Block/File Storage, 16 Search Systems, 17 Data Structures for Scale, 23 Performance Engineering, 28 Distributed Transactions, 58 Deep Learning Essentials, 63 Data Labeling, 68 Recommendation Architecture, 71 Responsible ML, 74 Vector Search, 76 LLM Adaptation, 80 Large-Scale AI Infrastructure, 86 LLM/Agent case studies.
