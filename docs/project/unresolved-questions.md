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
