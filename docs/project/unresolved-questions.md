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
