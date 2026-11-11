# Unresolved Research Questions and Evidence Gaps

This register feeds Appendix H. Each chapter's "Open verification items" are copied here during integration. Status: **Open** · **Resolved** (with resolution) · **Accepted** (documented as uncertain in text).

| ID | Chapter | Item | Status | Notes |
|---|---|---|---|---|
| UQ-000 | Global | Company-specific interview formats (Ch 90) change frequently; only official career-page content is treated as verified | Accepted | Re-verify each release |
| UQ-001 | 2 | Exact wording/URL of the "one-way vs two-way door" passage in Bezos's 2015 shareholder letter (paraphrased) | Open | sec.gov unreachable from build env |
| UQ-002 | 2 | Whether Jeff Dean's "design for ~10×, rewrite before ~100×" advice appears in the LADIS 2009 keynote | Open | Labeled Secondary |
| UQ-003 | 2 | Year/URL of Malte Ubl, "Design Docs at Google" (≈2020) | Open | |
| UQ-004 | 2 | Whether Vogels's 2006 ACM Queue interview contains the phrase "you build it, you run it" | Open | |
| UQ-005 | 2 | DeMarco *Structured Analysis and System Specification* edition year (1978 vs 1979) | Open | |
| UQ-006 | 2 | Authors/date of the Netflix "Simian Army" blog post | Open | |
| UQ-007 | 2 | Reconcile rough capacity figures (Table 2.17) and third-party SLA range with Appendix F | Open | Integration task |
| UQ-008 | 3 | AWS S3 us-east-1 2017 incident summary — URL and paraphrase to be checked against original | Open | |
| UQ-009 | 3 | Roediger & Karpicke (2006) one-week retention figures (~61% vs ~40%) confirmed only via secondary sources | Open | |
| UQ-010 | 3 | Macnamara et al. (2014): which domains showed lower variance explained (12% overall verified) | Open | |
| UQ-011 | 3 | Feynman "What I cannot create, I do not understand" — cite Caltech archives photo of the blackboard | Open | |
| UQ-012 | 3 / 14 | Load imbalance with V virtual nodes shrinks ~1/√V — needs derivation or citation in §14.8 | Resolved | §14.8.4 derives node share ~ Beta(V,(N−1)V), CV = √((N−1)/(NV+1)) → 1/√V; simulation slope −0.49 |
| UQ-013 | 1 | Exact URLs: Nygard "Documenting Architecture Decisions" (2011) and Ubl "Design Docs at Google" (2020); Ubl's statements on doc length | Open | Existence confirmed by search |
| UQ-014 | 1 | SEC 2013 Knight Capital order: release number, URL and quoted figures | Open | |
| UQ-015 | 1 | Primary source for YouTube's 2014 32-bit view-counter overflow ("Gangnam Style") | Open | |
| UQ-016 | 1 | Instagram 2011 stack details ("What Powers Instagram") | Open | |
| UQ-017 | 1 | Boehm & Basili (2001) "Software Defect Reduction Top 10 List" exact wording | Open | |
| UQ-018 | 1 | Current revision titles of ISO/IEC 25010 and ISO/IEC/IEEE 42010 | Open | Both revised 2022–2023 |
| UQ-019 | 1 | Barroso et al. (2018) passage on server failure frequency | Open | |
| UQ-020 | 1 | PEP 1 author list | Open | |
| UQ-021 | 5 | 2024 $/GB figures for DRAM and NAND (prices moved sharply 2025–26) | Open | Time-sensitive |
| UQ-022 | 5 | URLs: Dean 2009 LADIS slides; Cole 2010; Netflix 2022 post; choose one canonical variant of Dean's latency list | Open | Coordinate with Ch 4 §4.17 and Appendix F |
| UQ-023 | 5 | Hyper-Threading "up to ~30%" gain (Marr et al. 2002, Intel Technology Journal) | Open | |
| UQ-024 | 5 | MySQL release that added NUMA interleave option | Open | |
| UQ-025 | 5 | Primary source for Intel Optane wind-down announcement (2022) | Open | |
| UQ-026 | 5 | Branch-mispredict penalty (15–20 cycles) and outstanding misses per core (10–20) vs vendor optimization manuals | Open | |
| UQ-027 | 5 | TLC NAND 1,000–3,000 P/E cycles is a commonly cited range, not a vendor spec | Accepted | Stated as typical range |
| UQ-028 | 5 | Free-threaded CPython status (PEP 703) as of writing | Open | Time-sensitive |
| UQ-029 | 7 | RIPE NCC 2008 YouTube prefix-hijack case study: title, URL, "about two hours" duration | Open | |
| UQ-030 | 7 | AWS VPC docs URL; 5 reserved addresses per subnet (as of 2025) | Open | Time-sensitive |
| UQ-031 | 7 | CA/Browser Forum certificate-lifetime reduction schedule | Open | Left unquantified in text |
| UQ-032 | 7 | New York–London measured RTT "often around 70 ms" | Open | Coordinate with Appendix F |
| UQ-033 | 7 | Jacobson 1988 congestion-collapse figure (32 kbps → 40 bps) and BBR 2–25× gain on B4 vs primary papers | Open | |
| UQ-034 | 7 | Linux default values quoted (TIME_WAIT, min RTO, delayed ACK, ephemeral port range, keepalive) | Open | Kernel-version dependent |
| UQ-035 | 10 | OWASP Password Storage Cheat Sheet parameters; OWASP Top 10:2025 category names and release status (owasp.org unreachable; confirmed via search snippets) | Open | |
| UQ-036 | 10 | NIST SP 800-63B-4 rules (15-char minimum for single-factor passwords; pepper guidance) confirmed only via secondary sources | Open | |
| UQ-037 | 7 / 10 | CA/Browser Forum certificate-lifetime schedule (down to 47 days by 2029) | Open | Merge with UQ-031 |
| UQ-038 | 10 | GPU password-guessing rates are order-of-magnitude estimates | Accepted | Labeled as estimates |
| UQ-039 | 10 | AWS KMS quotas and pricing "as of 2026"; LinkedIn 2012 and Capital One 2019 breach figures from press reporting | Open | |
| UQ-040 | 10 | Exact URLs for BeyondCorp papers (;login:) and AWS KMS envelope-encryption docs | Open | |
| UQ-041 | 8 | Zanzibar request rate ("millions per second") — confirm exact figure in Pang et al. 2019 | Open | |
| UQ-042 | 8 | Browser default SameSite behavior and RFC 6265bis status | Open | Time-sensitive |
| UQ-043 | 8 | OAuth 2.1 draft revision at publication (-16 as of Sept 2026) | Open | Time-sensitive |
| UQ-044 | 8 / 10 | Whether NIST SP 800-63B-4 supersedes the 2017 revision cited in Ch 8; align with Ch 10 | Open | Merge with UQ-036 |
| UQ-045 | 8 | URLs: Byron 2015 GraphQL post; GitHub GraphQL rate-limit docs | Open | |
| UQ-046 | 8 | Table 8.3 latency ranges vs Appendix F; ~100 ms scrypt figure from a single measurement | Open | |
| UQ-047 | 4 | Dean & Barroso (2013) hedged-request figures (1,800 ms → 74 ms p99.9 with ~2% extra requests) | Open | |
| UQ-048 | 4 | Schroeder & Gibson (FAST 2007) annual disk replacement rates (2–4%) | Open | |
| UQ-049 | 4 / 5 | Canonical version of the "latency numbers" list (variants differ: 1 KB vs 2 KB send, 20 vs 30 ms disk read); "as of 2025" column is an author estimate | Open | Merge with UQ-022; resolve in Appendix F |
| UQ-050 | 4 | AWS S3 "11 nines" durability wording and URL | Open | |
| UQ-051 | 4 | Notation in Gunther's *Guerrilla Capacity Planning* (2007): α/β vs σ/κ | Open | |
| UQ-052 | 4 | Current edition year of IEC 80000-13 | Open | |
| UQ-053 | 9 | APNs details (latest-only coalescing, 64-byte apns-collapse-id, 5 KB VoIP payload, background-push guidance) and FCM 28-day max TTL / 4 KB payload (vendor docs unreachable) | Open | Time-sensitive |
| UQ-054 | 9 | WHATWG rule: non-200 response stops EventSource reconnection | Open | |
| UQ-055 | 9 | Default idle timeouts for AWS ALB, NGINX, Kubernetes ingress | Open | Version-dependent |
| UQ-056 | 9 | Author lists for RFC 8489 (STUN) and RFC 8656 (TURN) | Open | |
| UQ-057 | 9 | Per-connection memory figures are illustrative | Accepted | Labeled in text |
| UQ-058 | 6 | URL for Corbet (2023) LWN article on EEVDF | Open | EEVDF merged in Linux 6.6 (verified) |
| UQ-059 | 6 | Li et al. (2007) indirect context-switch cost; 1–5 µs direct-cost range | Open | |
| UQ-060 | 6 | Mars Pathfinder priority-inversion details and Reeves account URL (Cornell-hosted copy) | Open | |
| UQ-061 | 6 | Google 2023 io_uring vulnerability statistics | Open | |
| UQ-062 | 6 | WhatsApp 2012 "1 million is so 2011" blog post URL | Open | Also used in Ch 9 |
| UQ-063 | 6 | Erlang process initial size; Python 3.14 free-threading status | Open | Merge with UQ-028 |
| UQ-064 | 6 | Banker's algorithm source memo (EWD 108 vs EWD 123) | Open | |
| UQ-065 | 6 | MySQL docs page title cited; TLB entry counts per core | Open | |
| UQ-066 | 15 | S3 maximum object size (AWS pages say both "50 TB" and 48.8 TiB) | Open | Time-sensitive |
| UQ-067 | 15 | Dates S3 added conditional writes (If-None-Match, If-Match) | Open | |
| UQ-068 | 15 | S3 storage/transition/retrieval prices as of 2026 | Open | Time-sensitive |
| UQ-069 | 15 | Exact title/URL of the Google Cloud blog post on Colossus | Open | |
| UQ-070 | 15 | Primary source for ~150 bytes per HDFS NameNode object rule of thumb | Open | |
| UQ-071 | 15 | Recovery-traffic figure from Rashmi et al. (2013) | Open | |
| UQ-072 | 15 | Typical object-store first-byte latency range (Table 15.1) | Open | Coordinate with Appendix F |
| UQ-073 | 16 | Lucene postings block layout (128-value blocks in Lucene 5–9) — check against Lucene 10 | Open | Version-dependent |
| UQ-074 | 16 | TieredMergePolicy defaults (segmentsPerTier 10, max merged segment 5 GB) | Open | |
| UQ-075 | 16 | Lucene 8 removal of the (k1+1) factor in BM25; Elasticsearch boost 2.2 claim; BM25 default since Elasticsearch 5.0 | Open | |
| UQ-076 | 16 | Manning et al. Table 5.6 RCV1 figures (400 MB raw, 116 MB compressed), quoted from memory | Open | |
| UQ-077 | 16 | Twitter Earlybird latency figures (10 s indexing, 50 ms query); GitHub code search 25 TB / 115 TB index figures (search snippets only) | Open | |
| UQ-078 | 16 | Elastic Serverless "stateless" architecture claim | Open | Time-sensitive |
| UQ-079 | 12 | DynamoDB on-demand ($0.625/M WRU, $0.125/M RRU after Nov 2024 cut) and provisioned ($0.00065/WCU-h, $0.00013/RCU-h) prices — third-party confirmation only | Open | Time-sensitive; break-even ≈29% re-checked arithmetically |
| UQ-080 | 12 | DynamoDB limits and 89.2M requests/s Prime Day figure (Elhemali et al. 2022) | Open | |
| UQ-081 | 12 | Cassandra ~100 MB partition guideline (community practice); tombstone thresholds and gc_grace_seconds defaults by version | Accepted | Labeled as guideline |
| UQ-082 | 12 | Redis 8 AGPLv3 licensing option; InfluxDB 3 architecture (as of 2026) | Open | Time-sensitive |
| UQ-083 | 13 | PostgreSQL debug_io_direct (v16) and v18 asynchronous I/O details; PG18 data checksums on by default; MySQL 8.4 O_DIRECT default on Linux (secondary sources) | Open | Version-dependent |
| UQ-084 | 13 | PostgreSQL clock-sweep usage-count cap (5) and ring-buffer behavior | Open | |
| UQ-085 | 13 | Matsunobu et al. (VLDB 2020, MyRocks) storage savings — number intentionally not quoted | Accepted | |
| UQ-086 | 13 | Cassandra ~50% free-disk guidance for STCS; Cassandra 5.0 Unified Compaction Strategy | Open | |
| UQ-087 | 13 | Uber blog URL (Postgres→MySQL migration post) still live | Open | |
| UQ-088 | 13 | Compaction write-amplification formulas are a simplified average-case model by the author | Accepted | Labeled in text |
| UQ-089 | 14 | Cassandra 4.0 num_tokens default (16) and rationale | Open | |
| UQ-090 | 14 | PgBouncer 1.21 prepared-statement support in transaction mode | Open | |
| UQ-091 | 14 | DynamoDB per-partition limits (1,000 WCU / 3,000 RCU) as of 2026 | Open | Time-sensitive |
| UQ-092 | 14 | Vitess two-phase-commit (atomic distributed transaction) mode and default | Open | |
| UQ-093 | 14 | URLs/authors: Instagram ID/sharding post, Discord and Slack scaling posts; Lamping & Veach figures (arXiv blocked) | Open | |
| UQ-094 | 14 | Bigtable tablet split size | Open | |
| UQ-095 | 11 | PostgreSQL 18 B-tree skip scan; MySQL 8.4 still lacks partial indexes; MySQL 8.x has no sort-merge join | Open | Version-dependent |
| UQ-096 | 11 | Sentry 2015 transaction-ID wraparound postmortem — details and URL | Open | |
| UQ-097 | 11 / 13 | URLs for Uber 2016 (Postgres→MySQL) and Instagram 2012 (sharding & IDs) posts | Open | Merge with UQ-087, UQ-093 |
| UQ-098 | 11 | PostgreSQL 16 xid wraparound warning / write-refusal thresholds (stated qualitatively) | Accepted | |
| UQ-099 | 17 | Twitter 2010 "Announcing Snowflake" post — author, date, URL | Open | Bit layout verified from archived GitHub repo |
| UQ-100 | 17 | Flickr "Ticket Servers" post — author (believed Kay Kremerskothen) and date | Open | |
| UQ-101 | 17 | Akamai one-hit-wonder claim in Maggs & Sitaraman (2015) | Open | |
| UQ-102 | 17 | Counting Bloom filter counter-overflow bound in Fan et al. (2000) | Open | |
| UQ-103 | 17 | Redis sorted-set skip-list constants (p = 1/4, 32 levels); RedisBloom bundled in Redis 8 | Open | Version-dependent |
| UQ-104 | 17 | RocksDB ribbon filters; default skip-list memtable | Open | |
| UQ-105 | 17 | Citation form for Niemeyer (2008) geohash | Open | |
| UQ-106 | 17 | xxHash speed claims from author's own benchmarks only | Accepted | Labeled in text |
| UQ-107 | 18 | Kubernetes HPA defaults (tolerance 0.1, 15 s sync period, 300 s scale-down stabilization) and docs URL | Open | Version-dependent |
| UQ-108 | 18 | Largest cloud instance sizes as of 2026 | Open | Time-sensitive |
| UQ-109 | 18 | Stack Overflow server counts and URL of Craver (2016) architecture post | Open | |
| UQ-110 | 18 | Publication years of Weiss & Furr and Netflix Scryer posts; exact title of AWS cell-based architecture whitepaper | Open | |
| UQ-111 | 18 | Whether cited SRE book chapters contain the N+2 guidance and Auxon description | Open | |
| UQ-112 | 21 | Fastly ~150 ms global purge time; date of the Betts blog post | Open | fastly.com unreachable |
| UQ-113 | 21 | Netflix Open Connect facts (OCAs free to ISPs, control plane in AWS, fill order, 2012 launch) | Open | openconnect.netflix.com unreachable |
| UQ-114 | 21 | "10–20%" rebuffer reduction in Huang et al. (SIGCOMM 2014) | Open | |
| UQ-115 | 21 | Illustrative 2026 prices ($0.05/GB origin egress, $0.01/GB CDN delivery) | Accepted | Labeled illustrative |
| UQ-116 | 21 | CloudFront Functions / Lambda@Edge limits; Low-Latency HLS details; ESI 1.0 W3C note title and authors | Open | Time-sensitive |
| UQ-117 | 19 | Maglev paper (Eisenbud et al. 2016): GRE encapsulation wording, table size ≥100× backends guidance, author list (usenix.org unreachable) | Open | |
| UQ-118 | 19 | AWS ALB health-check defaults (30 s interval, 5/2 thresholds, 300 s deregistration delay); Envoy outlier-detection defaults | Open | Version-dependent |
| UQ-119 | 19 | HAProxy default number of draws for `balance random` | Open | |
| UQ-120 | 19 | Vimeo bounded-loads post (Rodland 2016) title/date/results; Google Cloud Pub/Sub use of bounded loads | Open | |
| UQ-121 | 19 | Facebook Katran blog post authors and date; subset sizes 20–100 in Google SRE book ch. 20 | Open | |
| UQ-122 | 23 | RED method origin: Wilkie's original venue/date (reportedly 2015; Grafana blog 2018) | Open | |
| UQ-123 | 23 | Dean & Barroso (2013): slowest 5% of leaves ≈ half of root p99; tied requests near idle-cluster latency with <1% disk overhead | Open | Merge with UQ-047 |
| UQ-124 | 23 | Netflix "Java in Flames" post — authors, date, URL | Open | |
| UQ-125 | 23 | Facebook Kraken (OSDI 2016) description; Discord two-minute forced GC (Go) | Open | |
| UQ-126 | 23 | Compression table values (zstd README, 2026); JVM collector version dates; Go GC 25% marking CPU target | Open | Time-sensitive |
| UQ-127 | 23 | Venue/year for Tene's "How NOT to Measure Latency" talk | Open | |
| UQ-128 | 20 | Nishtala et al. (NSDI 2013) figures: one lease token per 10 s per key; peak DB queries 17K/s → 1.3K/s; gutter pool ≈1% of servers (secondary summaries only) | Open | |
| UQ-129 | 20 | Zipf exponent range reported by Breslau et al. (1999) | Open | |
| UQ-130 | 20 | Valkey 8.0 1.2M req/s figure (vendor benchmark on AWS r7g); Redis license timeline (dual license from 7.4, AGPLv3 option from 8.0) | Open | Time-sensitive |
| UQ-131 | 20 | Whether Caffeine randomizes admission to resist hash flooding | Open | |
| UQ-132 | 20 | URLs: MySQL query-cache removal post; Linux Foundation Valkey press release; Redis licensing blog posts | Open | Merge with UQ-082 |
| UQ-133 | 22 | ITU-T I.371 edition year; ATM Forum TM 4.0 document number (GCRA) | Open | |
| UQ-134 | 22 | IETF RateLimit header fields draft: current revision/syntax (draft-10 Sept 2025, draft-11 May 2026 per search) | Open | Time-sensitive |
| UQ-135 | 22 | IETF Idempotency-Key header draft status after -07; 409/422 guidance | Open | Time-sensitive |
| UQ-136 | 22 | Cloudflare rate-limiting post URL and "0.003% of 400M requests" figure | Open | |
| UQ-137 | 22 | Stripe idempotency: key length limit, 24-hour pruning, replay of stored 500 responses (as of 2026) | Open | Time-sensitive |
| UQ-138 | 22 | Hystrix defaults; AWS SDK retry quota; ACM Queue URLs for Nichols & Jacobson 2012 (CoDel) and Maurer 2015 (Fail at Scale) | Open | |
| UQ-139 | 25 | Attiya–Welch and Lipton–Sandberg latency lower bounds as stated | Open | |
| UQ-140 | 25 | Mahajan et al. (2011) real-time causal consistency result | Open | |
| UQ-141 | 25 | Consistency-map edges and availability colors (Fig 25.10) vs jepsen.io (blocked); Jepsen findings for etcd 3.4.3, MongoDB 4.2.6, PostgreSQL 12.3 (fix believed in 12.4) checked via search only | Open | |
| UQ-142 | 25 | Cosmos DB bounded-staleness minimums; strong consistency unavailable with multiple write regions; DynamoDB multi-Region strong consistency release date | Open | Time-sensitive |
| UQ-143 | 25 / 28 | Spanner commit-wait duration figures; Brewer 2012 page numbers | Open | Coordinate with Ch 28 |
| UQ-144 | 28 | Mohan, Lindsay & Obermarck (1986) forced-write and message counts (Table 28.2) | Open | |
| UQ-145 | 28 | Percolator: timestamp oracle ~2M timestamps/s; ~50% reduction in document age | Open | |
| UQ-146 | 28 | Brewer (2017): share of Spanner incidents that were network-related (<8% per a secondary source) | Open | research.google unreachable |
| UQ-147 | 28 | Calvin near-linear scaling to 100 machines; FaunaDB being Calvin-inspired | Open | |
| UQ-148 | 28 | 2026 defaults: CockroachDB range size (512 MiB) and max clock offset (500 ms); YugabyteDB YSQL default isolation; TiDB async commit / 1PC status | Open | Version-dependent |
| UQ-149 | 26 | Ongaro (2015) report of the single-server membership-change bug and its fix | Open | |
| UQ-150 | 26 | GitHub October 2018 incident figures and blog URL | Open | |
| UQ-151 | 26 | URLs: antirez "Is Redlock safe?" reply; Redis Redlock documentation | Open | |
| UQ-152 | 26 | ZooKeeper 2010 paper throughput wording; persistent watches in 3.6 | Open | |
| UQ-153 | 26 | etcd defaults/tuning; Kubernetes leader-election defaults (15 s / 10 s / 2 s); Chubby defaults; Bigtable unavailability due to Chubby | Open | Version-dependent |
| UQ-154 | 26 / 31 | Kafka 4.0 removal of ZooKeeper mode | Open | Believed correct (Mar 2025); verify in Ch 31 |
| UQ-155 | 26 / 27 | GitHub Oct 2018 incident figures (43 s partition, 24 h 11 min degraded) from search summaries only | Open | Merge with UQ-150 |
| UQ-156 | 27 | Cassandra exponential phi model and 3-hour default hint window | Open | Version-dependent |
| UQ-157 | 27 | Dynamo (2007): 99.94% of requests see one version; ~10-entry vector-clock truncation threshold | Open | |
| UQ-158 | 27 | DynamoDB global tables LWW wording and strong-consistency mode (as of 2026); Akka/CouchDB/Redis/Riak doc URLs | Open | Time-sensitive |
| UQ-159 | 24 | URL of Lamport's 1987 "distributed system" email | Open | |
| UQ-160 | 24 | Gill et al. (SIGCOMM 2011) figures (5.2 device / 40.8 link failures per day, ~5 min median repair, ~43% redundancy effectiveness); Dean 2009 cluster-year failure counts (secondary summaries) | Open | |
| UQ-161 | 24 | Alquraan et al. (OSDI 2018): share of partition failures that were catastrophic / due to partial partitions; Gunawi et al. case count | Open | |
| UQ-162 | 24 | Attribution of fallacies 1–4 to Joy & Lyon and the year Gosling added the eighth | Open | |
| UQ-163 | 24 / 28 | CockroachDB 500 ms default max clock offset and node self-shutdown rule | Open | Merge with UQ-148 |
| UQ-164 | 24 | Meta PTP post details; AWS 2023 microsecond-accurate time announcement; Riak 2.0 dotted version vectors; AWS 2008/2011 post-mortem URLs | Open | |
| UQ-165 | 29 | MapReduce (OSDI 2004) sort figures: 891 s; 1,283 s without backup tasks; ~5% slower with 200 workers killed; ~1,800 machines | Open | |
| UQ-166 | 29 | Databricks 2014 100 TB sort (23 min on 206 machines vs 72 min on 2,100) — blog title and URL | Open | |
| UQ-167 | 29 | RDD paper (NSDI 2012): "up to 20×" speedup and 5–7 s interactive queries | Open | |
| UQ-168 | 29 | Magnet push-based shuffle shipped in Spark 3.2; author list | Open | |
| UQ-169 | 29 | Flink 2.0 ForSt state backend; unaligned checkpoints since Flink 1.11; Structured Streaming latency (~100 ms micro-batch, ~1 ms continuous) | Open | Version-dependent |
| UQ-170 | 15 / 29 | S3 per-prefix request rates | Open | Merge with Ch 15 items |
| UQ-171 | 30 | SQS FIFO quotas; SQS "fair queues" (2025); whether DLQ moves preserve enqueue timestamp | Open | Time-sensitive |
| UQ-172 | 30 | RabbitMQ 4.0: classic mirroring removed; default quorum-queue delivery limit 20; 30-min consumer timeout | Open | Version-dependent |
| UQ-173 | 30 | Google Pub/Sub limits: ack deadline 10–600 s; retention 7/31 days; 5–100 delivery attempts | Open | Time-sensitive |
| UQ-174 | 30 | Slack 2020 incident details/URL; Uber (Xia 2018) post URL | Open | |
| UQ-175 | 30 / 31 | KIP-932 share groups status in Kafka 4.x; Pulsar metadata-store alternatives by release | Open | Time-sensitive |
| UQ-176 | 33 | AWS Lambda prices, 15-min limit and INIT-phase billing (as of 2026); API Gateway ~$1 per million requests | Open | Time-sensitive |
| UQ-177 | 33 | Source book for Richards' 80–20 architecture-sinkhole heuristic | Open | |
| UQ-178 | 33 | Kolny (2023) Prime Video post: title, "90%" cost figure, URL; Noonan (2018) Segment post: title and service count | Open | |
| UQ-179 | 33 | Westeinde (2019) Shopify modular-monolith post title; current status of Packwerk | Open | Time-sensitive |
| UQ-180 | 18 / 33 | Route 53 use of shuffle sharding; title/year of AWS cell-based architecture whitepaper; Cockburn and Palermo URLs | Open | Merge with UQ-110 |
| UQ-181 | 32 | LMAX ~6M orders/s and nightly-snapshot recovery (Fowler 2011) | Open | |
| UQ-182 | 32 | Young (2017) title; URL of Young's 2010 *CQRS Documents* | Open | |
| UQ-183 | 32 | Frank & Zahle (1998) as source of Richardson's saga isolation countermeasures | Open | |
| UQ-184 | 32 | DBLog arXiv ID; Netflix Conductor blog URL; Debezium default delivery guarantee (as of 2026) | Open | |
| UQ-185 | 32 | Step Functions and Temporal limits (as of 2026); per-step latency figures in Table 32.13 | Open | Time-sensitive |
| UQ-186 | 32 | Whether crypto-shredding satisfies GDPR Art. 17 erasure | Accepted | Legal question; text presents it as commonly used, not as legal advice |
| UQ-187 | 37 | Norvig (1996) talk title/venue and "16 of 23 patterns invisible or simpler" figure | Open | |
| UQ-188 | 37 | Author list/date of "The 'Double-Checked Locking is Broken' Declaration"; PEP 318 author attribution | Open | |
| UQ-189 | 37 | Spring docs wording recommending constructor injection; default proxy type (JDK dynamic proxy in Spring Framework vs CGLIB in Spring Boot) | Open | Version-dependent |
| UQ-190 | 37 / 5 / 6 | PEP 703 free-threaded CPython still experimental as of 2026 | Open | Merge with UQ-028, UQ-063 |
| UQ-191 | 31 | Kafka milestones (as of 2026): KRaft production-ready 3.3; ZooKeeper deprecated 3.5, removed 4.0; KIP-848 GA in 4.0 (group.protocol=consumer); tiered storage production-ready 3.9 | Open | Merge with UQ-154; kafka.apache.org unreachable |
| UQ-192 | 31 | KIP-932 share-group maturity in current 4.x; defaults quoted (linger.ms 5 ms from 4.0; session.timeout.ms 45 s) | Open | Version-dependent; merge with UQ-175 |
| UQ-193 | 31 | Figures from Kreps (2014) benchmark post and Svingen (2017) NYT post; URLs for KIP-101, KIP-848 and the 4.0 release announcement | Open | |
| UQ-194 | 36 | Source of the Xerox Job-class story behind ISP (Martin 2002?); URL of Martin's 2014 SRP post | Open | |
| UQ-195 | 36 | Exact wording/page of Liskov's 1987 OOPSLA keynote quote; origin of the SOLID acronym (Feathers?) — chapter makes no claim | Open | |
| UQ-196 | 34 | BFF term origin (Calçado/SoundCloud); dates of Plotnicki and Newman 2015 posts; Netflix API redesign post (Jacobson 2012) title/date | Open | |
| UQ-197 | 34 / 40 | Dapper default sampling rate (1/1024) | Open | |
| UQ-198 | 34 | Istio 1.21/1.22/1.24 performance figures vs current release; ambient mode GA in 1.24 (Nov 2024, via search); Linkerd sidecar-only status as of 2026 | Open | Time-sensitive |
| UQ-199 | 34 | Eureka lease defaults and self-preservation behavior; author of 2023 Prime Video post | Open | Merge with UQ-178 |
| UQ-200 | 38 | UML 2.5.1 clause on shared-aggregation semantics varying by application; spec page count (~790) | Open | |
| UQ-201 | 38 | Page reference for Fowler quoting Rumbaugh's "modeling placebo" remark | Open | |
| UQ-202 | 38 | GitHub Mermaid support announcement date (believed 14 Feb 2022) and URL | Open | |
| UQ-203 | 38 | CPython lru_cache implementation details and ~100–200 bytes/entry estimate; Redis expiry and transaction behavior (2026 docs) | Open | Version-dependent |
| UQ-204 | 35 | Coupling kinds/order in Stevens, Myers & Constantine (1974) vs later works; venue of Hitz & Montazeri (1995, LCOM4) | Open | |
| UQ-205 | 35 | Years of Fowler bliki "TellDontAsk" (2013?) and "AnemicDomainModel" (2003?); *Effective Java* 3rd ed. item numbers cited (10–11, 17–20, 49–50) | Open | |
| UQ-206 | 42 | Kubernetes feature status as of 2026: native sidecars and nftables kube-proxy stable in 1.33; in-place pod resize stable and IPVS deprecated in 1.35; pod user namespaces and preStop sleep maturity | Open | Version-dependent |
| UQ-207 | 42 | Go 1.25 cgroup-aware GOMAXPROCS; JVM container support since JDK 10 / 8u191 | Open | |
| UQ-208 | 42 / 47 | Firecracker figures (~125 ms boot, <5 MiB overhead) from Agache et al. 2020 | Open | |
| UQ-209 | 42 | kube-scheduler percentageOfNodesToScore default (50% at 100 nodes, 5% floor); Borg figures quoted from Verma et al. 2015 | Open | |
| UQ-210 | 42 | Image sizes, node reservations and cloud prices in worked examples are illustrative | Accepted | Labeled |
| UQ-211 | 41 | Cloud prices used (NAT, egress tiers, cross-zone, Transit Gateway, PrivateLink, public IPv4, instance and RDS rates) | Accepted | Labeled "illustrative, as of 2026" |
| UQ-212 | 41 | Aurora figures (35× / 7.7×, 10 s segment repair) from Verbitski et al. 2017; Firecracker figures (125 ms, <5 MiB, 150/s) | Open | Merge with UQ-208 |
| UQ-213 | 41 | Commitment/spot discount ranges; spot notice periods on GCP and Azure | Open | Time-sensitive |
| UQ-214 | 41 | Existence and naming (as of 2026): Aurora DSQL, DynamoDB multi-Region strong consistency, Google Titanium, Azure Boost, GCP Managed Lustre, Managed Kafka services | Open | Time-sensitive |
| UQ-215 | 41 | S3 Block Public Access on by default for new buckets since April 2023 | Open | |
| UQ-216 | 39 | Google Cloud 12 June 2025 Service Control incident report: red-button and per-region recovery timings, remediation wording | Open | status.cloud.google.com unreachable |
| UQ-217 | 39 | AWS Compute SLA credit tiers below 99.0%; GitLab 2017 incident figures (~300 GB deleted, ~6 h data loss) | Open | |
| UQ-218 | 39 | Originator of the 3-2-1 backup rule; SRE Workbook error-budget policy wording (20% threshold, escalation path) | Open | |
| UQ-219 | 39 | DR cost percentages in Table 39.7 are illustrative planning figures | Accepted | Labeled in text |
| UQ-220 | 40 | OpenTelemetry per-language signal status; profiles signal maturity; reported 2026 CNCF graduation | Open | Time-sensitive |
| UQ-221 | 40 | Prometheus native histograms stable in 3.8 (Dec 2025); W3C Trace Context Level 2 status; OTel `ot=th:` sampling key | Open | Time-sensitive |
| UQ-222 | 40 | Honeycomb founders' use of Scuba via Parse; SRE book guidance of ~2 incidents per on-call shift | Open | |
| UQ-223 | 40 | ~4 KB memory per series and ~1% continuous-profiling overhead are planning assumptions | Accepted | Labeled in text |
| UQ-224 | 43 | DORA 2024 performance-cluster thresholds; whether later reports changed the four-metric set | Open | Time-sensitive |
| UQ-225 | 43 | Kayenta details ("critical" metric flag, marginal/pass semantics, effect-size settings); Google blog author/URL | Open | |
| UQ-226 | 43 | Terraform S3 backend use_lockfile GA version (believed 1.11) and DynamoDB-locking deprecation; HCL example not validated with terraform; OpenTofu governance home (2026); Argo CD default 3-min polling | Open | Version-dependent |
| UQ-227 | 1 / 43 | Knight Capital $460M loss wording in SEC order | Open | Merge with UQ-014 |
| UQ-228 | 44 | Observed inter-region RTT ranges in Table 44 region-pair table | Accepted | Labeled approximate, as of 2026 |
| UQ-229 | 44 | AWS Builders' Library "Minimizing correlated failures in distributed systems" author/year (title confirmed) | Open | |
| UQ-230 | 44 | Netflix 2013 active–active post author list; "Project Nimble" title, year and evacuation times | Open | |
| UQ-231 | 44 | DynamoDB global tables: "usually within a second" replication wording, regions with strong consistency, conflict rejection behavior; Aurora Global Database secondary-Region limit (5 vs 10) and typical lag | Open | Time-sensitive; merge with UQ-142, UQ-158 |
| UQ-232 | 44 | Pokémon GO launch details in SRE Workbook ch. 11 | Open | |
| UQ-233 | 47 | AWS *SaaS Architecture Fundamentals* whitepaper title/year/URL | Open | |
| UQ-234 | 47 | gVisor systrap default platform and Gofer details; Google production use of gVisor (cut from text — secondary sources only) | Open | |
| UQ-235 | 47 | Citus tenant-isolation function name/behavior; KMS key-deletion waiting period and quotas | Open | Version-dependent |
| UQ-236 | 47 | Isolation-overhead figures in §47.9.3 are planning assumptions | Accepted | Labeled in text |
| UQ-237 | 45 | Bailis et al. (VLDB 2014): 3 of 18 databases serializable by default, 8 not offering it; HAT availability classes (Table 45.2) | Open | |
| UQ-238 | 45 | Ports & Grittner (2012): "first production SSI", performance summary; predicate-lock support by index type/version | Open | |
| UQ-239 | 45 | "Cores That Don't Count" (Hochschild et al. HotOS 2021) failure rate quoted | Open | |
| UQ-240 | 45 | Hyperledger Fabric 3.0 SmartBFT orderer; Tendermint Core → CometBFT rename (2023); Ethereum finality ~12.8 min (as of 2026); Bitcoin transactions-per-block range | Open | Time-sensitive |
| UQ-241 | 45 | Daudjee & Salem (2006) as origin of strong session SI | Open | |
| UQ-242 | 46 | Borg (Verma et al. 2015) figures from memory: ~10 s Borgmaster failover; "a few hundred seconds" vs >3 days to schedule a cell without optimizations; 3–5% gain of hybrid scoring over best fit (baseline possibly E-PVM) | Open | Unverifiable numbers removed from text |
| UQ-243 | 46 | Sparrow default probe ratio d = 2 | Open | |
| UQ-244 | 46 | Kubernetes: preemption node-selection order; percentageOfNodesToScore default formula; native gang scheduling (v1.35 alpha Workload API); DRA core GA in v1.34; Kueue/Volcano feature names; Slurm backfill defaults; Slinky status | Open | Version-dependent; merge with UQ-206, UQ-209 |
| UQ-245 | 50 | SPIRE default SVID lifetime (1 h) confirmed only for v1.9.x docs; Fulcio ~10-min certificate validity | Open | Version-dependent |
| UQ-246 | 50 | US Census 2020 privacy-loss budget (ε = 19.61; 17.14 / 2.47 split) from June 2021 release as reported | Open | |
| UQ-247 | 50 | Mandiant M-Trends median dwell time (11 days) via secondary summaries | Open | Time-sensitive |
| UQ-248 | 50 | Author lists/issue numbers: Cittadini et al. 2016; Cedar (OOPSLA 2024); DELF (USENIX Security 2020) | Open | |
| UQ-249 | 50 | CCPA 45+45-day response periods; opt-out preference-signal (GPC) rules | Open | Legal; not advice |
| UQ-250 | 50 | MPC and FHE performance ranges (Table 50.6) are order-of-magnitude estimates | Accepted | Labeled in text |
| UQ-251 | 49 | Tectonic (FAST 2021): TrafficGroup/TrafficClass details, cluster sizes, per-tenant RS parameters (PDF unreachable) | Open | |
| UQ-252 | 49 | Colossus "two file systems above 10 EB" figure and Google post titles; Azure storage stamp sizes | Open | |
| UQ-253 | 49 | S3 scale figures (2023 vs reported 2026 ~500T objects, ~200M req/s); Snowflake micro-partition sizes; Snowmobile retirement date | Open | Time-sensitive |
| UQ-254 | 49 | El Capitan Nov 2024 Rmax/Rpeak and current Top500 leader (June 2026); MPI 5.0 release status | Open | Time-sensitive |
| UQ-255 | 49 | DCQCN parameters (50 µs notification interval, g = 1/256); titles of Gangidi et al. 2024 (Meta RoCE) and McCrory 2010 (data gravity) | Open | |
| UQ-256 | 51 | Radovanović et al. (IEEE Trans. Power Systems) volume/pages/year/authors; Google 2020 carbon-intelligent computing blog URL | Open | |
| UQ-257 | 51 | SCI spec: marginal vs average carbon intensity and exact symbols | Open | |
| UQ-258 | 51 | PUE figures: Uptime 1.58 (2023), 1.56 (2024); Google 1.09 TTM 2024; Green Grid WP#35 year | Open | Time-sensitive |
| UQ-259 | 51 | Dropbox S-1 infrastructure savings ($39.5M, $35.1M) via press reports; baseline for AWS Graviton3 "up to 60% less energy" claim | Open | Vendor claim labeled |
| UQ-260 | 51 | FinOps Foundation personas; FOCUS spec version/release date | Open | Time-sensitive |
| UQ-261 | 48 | Lambda limits/prices (1,000 account concurrency; scaling 1,000 per 10 s; provisioned-concurrency price; 1,769 MB per vCPU); 2025 INIT-phase billing change | Open | Time-sensitive; merge with UQ-176 |
| UQ-262 | 48 | Firecracker paper: placement <20 ms and pre-booted microVM pool; Lambda Worker Manager replacement (conference talks only); SnapStart runtimes and "up to 10×" | Open | |
| UQ-263 | 48 | Wang et al. 2018 figures (summarized qualitatively); Cloudflare Workers limits, KV ~60 s propagation, Varda/Partovi 2020 post titles; Lambda recursive-loop detection threshold (~16) | Open | |
| UQ-264 | 48 | Cloud Run and Azure Functions Flex Consumption details; Beswick 2021 post title | Open | Time-sensitive |
| UQ-265 | 56 | Percolator ~50% document-age reduction and its resource-cost comparison with MapReduce | Open | Merge with UQ-145 |
| UQ-266 | 56 | Druid/Pinot store Kafka offsets with segment metadata (exactly-once ingestion); Pinot paper's star-tree index and member-facing uses; Pixie full pruned graph in memory per server | Open | |
| UQ-267 | 56 | ClickHouse DDL details (tokenbf_v1 parameters; TTL … TO VOLUME with toDateTime(DateTime64); 8,192-row granule) untested on current release | Open | Version-dependent |
| UQ-268 | 56 | Illustrative ratios (3 B/posting, 4 KB/series, 1 GB/s/core scan, full-text index 0.5× raw, 10:1 log compression) | Accepted | Labeled illustrative |
| UQ-269 | 54 | YouTube "500 hours uploaded per minute" (no primary source); Goodrow 2017 "a billion hours a day" post title/author; Google Drive "over a billion users" (uncited) | Open | |
| UQ-270 | 54 | Netflix end-2024 membership; Izrailevsky 2016 venue; whether Basiri et al. 2016 describes whole-region failure exercises | Open | |
| UQ-271 | 54 | Spotify 30-second play rule wording; 2019 event-delivery post author; hourly partitions in 2016 vs 2019 post | Open | |
| UQ-272 | 54 | Dropbox Magic Pocket posts (Cowling 2016, Gupta 2016) titles/dates/details; Day-Richter authorship of all three 2010 Google Docs posts | Open | |
| UQ-273 | 53 | WhatsApp: 30-day undelivered-message limit, transport/media encryption details vs current privacy policy and security whitepaper; 1,024-member group limit (news reports); 2014 server counts (third-party summary) | Open | Time-sensitive |
| UQ-274 | 53 | Meta 2021 encrypted-backups and 2023 key-transparency post titles/URLs | Open | |
| UQ-275 | 53 | Twitter Redis timeline details (800-entry cap, 3 replicas) via secondary sources; Krikorian 2013 post title/URL; 2023 recommendation-algorithm figures (search snippets) | Open | |
| UQ-276 | 53 | Facebook Multifeed percentages; Lada et al. 2021 authors/URL; "~40 requests per query" (2012) | Open | |
| UQ-277 | 53 | Discord 177→72 nodes (2023 migration); Instagram 2015 like-count/lease details; 2016 ranked-feed post title | Open | Secondary sources |
| UQ-278 | 55 | Uber details (DISCO, S2 sharding, Ringpop, driver phones as backup store) from secondary summaries of Ranney 2015 / Hoff 2015; ringpop-node repo URL | Open | |
| UQ-279 | 55 | Geisberger et al. 2008 query/preprocessing times; Xu et al. 2018 (Didi order dispatch) author list and matching method | Open | |
| UQ-280 | 55 | Airbnb Orpheus (Chew 2019) library name; Stripe Ledger post date (~Feb 2024) and author; Ticketmaster 2022 statement (archived copy); Gray 2006 "100+ services per page" wording | Open | |
| UQ-281 | 52 | RFC 9309 (robots.txt) details: 24 h cache limit, 500 KiB parse minimum, 4xx/5xx handling (secondary sources; rfc-editor.org unreachable) | Open | |
| UQ-282 | 52 | Google email sender guidelines: 0.3% spam-rate threshold, one-click unsubscribe; help-page URL (from memory) | Open | Time-sensitive |
| UQ-283 | 52 | Google SRE book ch. 24 "?" crontab extension wording; S3 PUT price ($0.005/1,000) | Open | Time-sensitive |
| UQ-284 | 52 | Mercator "10× last fetch time" politeness delay is from Manning et al. ch. 20 as an example, not the Mercator paper | Accepted | Attributed accordingly |
| UQ-285 | 57 | Uber DeepETA post author list and URL (uber.com unreachable) | Open | |
| UQ-286 | 57 | Netflix 2017 interleaving post authors and "far smaller samples" claim | Open | |
| UQ-287 | 57 | Kohavi et al. (2020) Bing ad-title example (~12% revenue lift, >$100M/yr) | Open | |
| UQ-288 | 57 | Section numbers cited from Hastie et al., Bishop, Goodfellow et al., Murphy | Open | |
| UQ-289 | 58 | Grinsztajn et al. 2022: "45 datasets" and ~10,000-example medium-size regime | Open | |
| UQ-290 | 57 / 58 | DeepETA (Hu et al. 2022): prior GBDT model and Uber's stated reasons (scale, latency); author list/URL | Open | Merge with UQ-285 |
| UQ-291 | 58 | Haldar et al. 2019 (Airbnb): early neural models did not beat GBDT baseline | Open | |
| UQ-292 | 58 | 10^15 FLOP/s accelerator in §58.12 is a round illustrative number | Accepted | Labeled |
| UQ-293 | 60 | Netflix 2013 personalization-architecture post: technologies named per tier | Open | |
| UQ-294 | 60 | Michelangelo (2017): UberEATS delivery-time example wording; Hive/Cassandra as offline/online stores | Open | |
| UQ-295 | 60 | Booking.com: ~30% latency increase costing >0.5% conversion (Bernardi et al. KDD 2019) | Open | |
| UQ-296 | 60 | TFX Google Play continuous-training description; ML Test Score 28 tests in four sections of seven | Open | |
| UQ-297 | 59 | Google Cloud MLOps page current URL and trigger list; Microsoft MLOps maturity-level names/characteristics (from memory) | Open | |
| UQ-298 | 59 / 60 | UberEATS feature examples (Hermann & Del Balso 2017); Booking.com finding paraphrase (Bernardi et al. 2019); ML Test Score 28 tests and scoring rule | Open | Merge with UQ-294–296 |
| UQ-299 | 61 | Delta Lake (VLDB 2020) author list and "thousands of customers, exabyte scale" wording | Open | |
| UQ-300 | 61 | Uber Hudi blog post (Rajaperumal & Chandar 2017) title/authors/year; Beauchemin "Functional Data Engineering" essay title/year (2018) | Open | |
| UQ-301 | 61 | 2026 status: Iceberg format v3, Delta liquid clustering and UniForm; Delta default checkpoint interval (10 commits) and VACUUM retention (7 days) | Open | Version-dependent |
| UQ-302 | 61 | Engine latency ranges and file-size defaults are typical values, not benchmarks | Accepted | Labeled |
| UQ-303 | 62 | Airbnb Zipline talks (titles, speakers, years; Data Council 2019 vs 2020); Airbnb Chronon open-source post (2024) title/date; Orr et al. 2021 venue | Open | |
| UQ-304 | 62 | Uber Palette name/source talk; Michelangelo 2017 details (~10,000 features; Samza, Cassandra, Hive) | Open | Merge with UQ-294 |
| UQ-305 | 62 | Databricks–Tecton (reported Aug 2025) vs Databricks announcement; Feast API names (docs unreachable); Zinkevich Rules of ML numbers #29, #31, #32, #37 | Open | Time-sensitive |
| UQ-306 | 64 | H100 clock figures (1.98 GHz boost; ~1.83 GHz implied by tensor rate); "2× A100 FMA per clock per SM" claim; latency values in Table 64.2 | Open | |
| UQ-307 | 64 | B200 specs (vary across NVIDIA documents); Blackwell technical brief title; NVFP4 block size and scale format | Open | Time-sensitive |
| UQ-308 | 64 | PaLM 46.2% MFU / 57.8% HFU; Gholami et al. 2024 ("AI and Memory Wall") volume/issue; MI300X 5.3 TB/s; Trn1 chip count | Open | |
| UQ-309 | 63 | Ng 2021 data-centric AI talk title/date/venue; steel-defect figures (stated qualitatively) | Open | |
| UQ-310 | 63 | Sambasivan et al. CHI 2021: 53 participants and prevalence wording; Bach et al. 2019 (Snorkel DryBell) comparison wording | Open | |
| UQ-311 | 63 | Gilardi et al. 2023 (LLM vs crowd workers) task count and cost ratio; Northcutt et al. 2021b average test-set error rate; He et al. 2014 downsampling rates | Open | |
| UQ-312 | 63 | Data cards framework name; Steiger et al. 2021 full title; Label Studio/CVAT adoption (as of 2026) | Open | |
| UQ-313 | 65 | Llama 3 (Dubey et al. 2024) reliability stats (466/47/419 interruptions; 78% hardware; 58.7% GPU incl. 30.1% faulty GPU, 17.2% HBM3; 3 manual interventions; >90% effective time; 1–2% diurnal variation); 3.8×10^25 FLOPs; 38–43% MFU; 4D layouts | Open | |
| UQ-314 | 65 | Megatron throughput (15.1 PFLOP/s @ 76% in 2019; 502 PFLOP/s @ 52% in 2021); ZeRO >100B params on 400 GPUs, super-linear speedup, Turing-NLG | Open | |
| UQ-315 | 65 | Switch Transformer "up to 7×" speedup; GShard 2,048 TPU v3 cores ~4 days; PaLM 46.2% MFU and venue; DDP near-linear to 256 GPUs | Open | Merge with UQ-308 |
| UQ-316 | 65 | Jeaugey 2019 NCCL blog title; FSDP PVLDB volume; torchrun URL; achieved bandwidth figures (360/40/320 GB/s) are teaching approximations | Open | |
| UQ-317 | 66 | BentoML reported acquisition by Modular (Feb 2026, third-party sources); KServe CNCF incubation date (29 Sep vs 11 Nov 2025) | Open | Time-sensitive |
| UQ-318 | 66 | Triton details (backend list, model_warmup, queue-policy fields, Open Inference Protocol paths); Ray Serve batching/autoscaling/multiplexing parameter names — docs unreachable | Open | Version-dependent |
| UQ-319 | 66 | Netflix interleaving sample-size wording; Michelangelo multi-model container wording; TF Serving version-policy names; Olston et al. 2017 author list | Open | |
| UQ-320 | 69 | Kreuzberger et al. (2023) MLOps definition (paraphrased) | Open | |
| UQ-321 | 69 | FBLearner Flow figures (>25% of engineers, >1M models, >6M predictions/s) via secondary reports | Open | |
| UQ-322 | 69 | Michelangelo multi-model serving container (models addressed by ID/tag); MLflow alias URI syntax (stages deprecated in 2.9 — confirmed); Airbnb Bighead component names/status; Netflix Metaflow announcement URL/date; KServe canaryTrafficPercent | Open | Version-dependent; merge with UQ-319 |
| UQ-323 | 67 | PyTorch 2 headline speedups (2.27× inference, 1.41× training on A100, 180+ models) | Open | |
| UQ-324 | 67 | GPTQ speedups (3.25× A100, 4.5× A6000) and ~4 GPU-hours for 175B | Open | |
| UQ-325 | 67 | Release removing torch.ao.quantization in favor of torchao; TensorRT INT4 weight support and cross-GPU engine compatibility | Open | Version-dependent |
| UQ-326 | 67 | ~5 µs kernel launch overhead and ~20 kernels per decoder layer are assumptions | Accepted | Labeled |
| UQ-327 | 68 | Mudigere et al. ISCA 2022 "embedding tables up to terabytes"; Chapelle et al. 2012 interleaving agreement with A/B at lower traffic (qualitative); Hohnhold et al. KDD 2015 long-term holdout scope; DCN-V2 production deployment (Wang et al. 2021) | Open | |
| UQ-328 | 70 | Siddiqi (2006) PSI bands (0.1/0.25 vs 0.1/0.2) and page reference | Open | |
| UQ-329 | 70 | Evidently default drift methods/thresholds (2026); WhyLabs hosted platform status (2026); Vertex AI and SageMaker model-monitoring feature names | Open | Time-sensitive |
| UQ-330 | 70 | Shankar et al. 2022 alert-fatigue wording; Breck et al. 2017 seven monitoring tests phrasing; Zinkevich freshness rule number | Open | Merge with UQ-305 |
| UQ-331 | 74 | Qdrant query planner and filter-aware HNSW (secondary summaries); Weaviate flat-search cutoff default and ACORN default version; Elasticsearch default dense_vector index type by version; OpenSearch k-NN docs URL | Open | Version-dependent |
| UQ-332 | 74 | Kusupati et al. 2022 "up to 14×" claims wording | Open | |
| UQ-333 | 74 | DiskANN I/O budget example and QuickBite vector-search costs (1 ms CPU/query, 5 ms query encode, 2,000 texts/s re-embedding) are illustrative assumptions | Accepted | Labeled |
| UQ-334 | 75 | Nogueira & Cho 2019 MS MARCO gain (qualitative); Liu et al. 2024 U-shaped effect for long-context models as worded | Open | |
| UQ-335 | 75 | DoorDash 2024 RAG post: 90% hallucination / 99% compliance-issue reductions, authors, title; Xu et al. 2024 (LinkedIn) author list and ~6-month deployment | Open | |
| UQ-336 | 75 | Edge et al. 2024 (GraphRAG) author list for cited arXiv version; OWASP LLM Top 10 2025 ranking prompt injection first | Open | |
| UQ-337 | 71 | EU AI Act timeline after the July 2026 "Digital Omnibus on AI" (reported Regulation (EU) 2026/1744): Annex III → 2 Dec 2027, Annex I → 2 Aug 2028; Article 50 dates disputed — legal commentary only, not Official Journal | Open | Time-sensitive; not legal advice |
| UQ-338 | 71 | Abadi et al. 2016 ε 1.26 vs 9.34 and MNIST 90/95/97% accuracies; Carlini et al. 2021 extracted-sequence count; McMahan et al. "10–100× fewer rounds" | Open | |
| UQ-339 | 71 | Gboard FL eligibility rules and recall gains (Hard et al. 2018; Bonawitz et al. 2019); CJEU SCHUFA ruling (C-634/21); CFPB Circular 2022-03 scope | Open | |
| UQ-340 | 72 | Llama 3 tokenizer compression (3.17 → 3.94 chars/token); Llama 3.1 staged 128K context extension; "1.3 tokens per English word" rule; Petrov et al. 2023 language-disparity range | Open | |
| UQ-341 | 72 | Chinchilla fitted constants (§72.16); Pope et al. 2023 (29 ms/token, 76% MFU); Ainslie et al. ~5% uptraining compute for GQA; Mistral 7B 8× cache reduction at 32K; DeepSeek-V3 671B total / 37B active | Open | |
| UQ-342 | 73 | TGI maintenance-mode date (Dec 2025, secondary reports) and reported 2026 repository archival | Open | Time-sensitive |
| UQ-343 | 73 | Paper headline figures: Orca 36.9×; vLLM 20.4–38.2% / <4% waste / 2–4×; SGLang 6.4×; DistServe 7.4×/12.6×; Splitwise 1.4×/2.35×; Sarathi-Serve 2.6×/3.7×; Flash-Decoding 8×; FlashAttention-3, Medusa, EAGLE speedups | Open | |
| UQ-344 | 73 | vLLM `gpu_memory_utilization` default 0.9 and per-engine default preemption modes; H100 228 KB shared memory per SM and 132 SMs | Open | Efficiency figures (80% bandwidth, 50% MFU, 2 ms step overhead) are stated modeling assumptions |
| UQ-345 | 80 | Llama 3 Table 5: 148 faulty-GPU interruptions (30.1%) inconsistent with 419 total — chapter uses percentages only; Llama 3 storage (240 PB, 7,500 servers, 2 TB/s sustained, 7 TB/s peak) and 16M-token batch | Open | arXiv blocked during drafting |
| UQ-346 | 80 | Gemini report goodput (85%→97%) and "SDC every week or two" wording; Gangidi et al. SIGCOMM 2024 congestion-control details; DGX SuperPOD switch counts; GB200 NVL72 rack power 120–132 kW (vendor pages) | Open | |
| UQ-347 | 80 | Llama 3.1 model-card GPU-hours and emissions; Li et al. 700,000-liter water estimate; titles of cited AWS, Microsoft, OpenAI, Google engineering posts | Open | Capex, prices, device power are Illustrative |
| UQ-348 | 78 | Zheng et al. 2023 "over 80% agreement" wording; Perez et al. 2022 "tens of thousands of offensive replies" (280B chatbot); FrugalGPT and RouteLLM savings as author-reported | Open | |
| UQ-349 | 78 | τ-bench pass^k estimator C(c,k)/C(n,k); current RAGAS context precision/recall formulas; OWASP Top 10 for LLM Applications 2025 category names (prompt injection still #1) | Open | Time-sensitive |
| UQ-350 | 78 | CaMeL (Debenedetti et al. 2025) and Dubois et al. 2024 author lists and venues; DoorDash 2024 90%/99% reductions | Open | |
| UQ-351 | 77 | Anthropic "Building effective agents" (Dec 2024) second author full name (Erik Schluntz); MCP details from 2025-06-18 / 2025-11-25 spec revisions (site blocked; read from spec repo) | Open | |
| UQ-352 | 77 | OpenTelemetry GenAI semantic conventions moved repo, still Development status — attribute names may change; τ-bench figures from secondary summaries; ReAct, Reflexion, Toolformer headline figures quoted from memory | Open | Re-check against papers |
| UQ-353 | 76 | Hu et al. (LoRA) ~10,000× fewer trainable params and 3× less memory; InstructGPT ~73% labeler agreement; Christiano et al. "<1%" feedback; LIMA 43%; Lee et al. ~10× memorization reduction from dedup; GPT-3 13-gram decontamination | Open | arXiv blocked during drafting |
| UQ-354 | 76 | OpenAI Structured Outputs 100% vs <40%; Llama 2 license clauses (700M MAU, output-use restriction) and "more than a million" human comparisons; Alpaca terms; Ovadia et al. venue | Open | |
| UQ-355 | 79 | Gateway API Inference Extension resource names (InferencePool; InferenceModel in 2025 alpha, reportedly renamed) and endpoint-picker signals; OpenTelemetry GenAI attribute/metric names and stability (`gen_ai.system` → `gen_ai.provider.name`) | Open | Docs sites blocked; from search results |
| UQ-356 | 79 | Provider data retention as published: OpenAI 30-day abuse monitoring and ZDR eligibility; Anthropic default API retention (sources disagree); Google Vertex AI ZDR conditions and URL; provider prompt-caching terms (as of 2026) | Open | Time-sensitive |
| UQ-357 | 79 | Feature names for Envoy AI Gateway, LiteLLM, NVIDIA Dynamo, llm-d, Azure/Bedrock provisioned throughput; venues of Preble, DynamoLLM, GPTCache, RouteLLM | Open | |
| UQ-358 | 82 | Stripe Radar post year (2023 assumed); PayPal graph post date and authors; RETVec Google Security Blog authors; PDQ match threshold (30–32 bits) | Open | stripe.com unreachable during drafting |
| UQ-359 | 82 | Regulation B 25-month record retention and four-reason adverse-action guidance; card-network fraud-chargeback time limit (120 days assumed); Gmail spam-rate thresholds (omitted from text) | Open | Not legal advice |
| UQ-360 | 83 | Uber DeepETA blog (Hu et al. 2022b) author list and asymmetric Huber loss; Bell & Smyl 2018 title/year; Chamandy 2016 Lyft post title | Open | uber.com and arXiv blocked during drafting |
| UQ-361 | 83 | Hall, Kendrick & Nosko 2015 surge-outage descriptions (concert, New Year's Eve); Cohen et al. 2016 "inelastic demand" and rounding-discontinuity design; emergency surge-pricing rules are jurisdiction-specific and uncited | Open | |
| UQ-362 | 85 | Jeon et al. ATC 2019 (Philly) ~52% utilization of in-use GPUs and ~30% unsuccessful jobs (abstract only); Weng et al. NSDI 2022 "over 6,000" vs 6,742 GPUs; ModelMesh behavior vs current KServe docs | Open | usenix.org and arXiv blocked during drafting |
| UQ-363 | 85 | DoorDash Sibyl posts (2020, 2021) titles and authors; author lists for Gandiva, Tiresias, Themis, Gavel, Pollux; GDSF credit (Cherkasova 1998) | Open | Prices and throughputs Illustrative |
| UQ-364 | 86 | Character.AI 2024 blog URL and "20,000 queries per second"; Klarna Feb 2024 press release title and company-reported figures (and later qualifications); Liu et al. 2023 (lost in the middle) 51.5%/74.5% averages | Open | |
| UQ-365 | 86 | Microsoft Learn Copilot privacy page URL/wording; Ziegler et al. 2022/2024 author lists and acceptance-rate restatement; Google-Extended 2023 announcement title and scope | Open | Time-sensitive |
| UQ-366 | 84 | NISTIR 8280 "factors of 10–100" wording and 189-algorithm count; FRVT→FRTE renaming; Meta 2021 face-recognition shutdown announcement ("more than a billion" templates) and USD 650M BIPA settlement year; MS-Celeb-1M withdrawal (2019) | Open | |
| UQ-367 | 84 | Apple ML Research article titles/years; He et al. ICASSP 2019 on-device model details; Whisper normalizer and 680,000 hours; SeamlessM4T language counts; NLLB distilled sizes; EU AI Act biometric provisions vs Official Journal | Open | Per-GPU throughputs and JPEG decode times Illustrative |
| UQ-368 | 81 | Instagram Explore 2019 post (Medvedev et al.) authors, pre-ranking integrity filtering, 500→150→50→25 funnel (secondary only); Vorotilov & Shugaepov 2023 Explore post authors/date/stage names; Mosseri 2021 signal wording | Open | |
| UQ-369 | 81 | Parks et al. 2017 Netflix interleaving sample-size advantage; Gomez-Uribe & Hunt 2015 ~80% of hours from recommendations; Twitter 2023 Product Mixer/SimClusters roles; ItemSage (Baltescu et al. 2022) and Haldar et al. 2020 authors and summarized claims | Open | Capacity figures Illustrative |
