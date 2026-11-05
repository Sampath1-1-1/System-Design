# Wave 8 Integration Review — Chapters 52–56

**Reviewer:** Agent 16 (Quality and Integration) · **Date:** 2026-11-05 · **Scope:** QA Reviews 2 (technical accuracy, spot-check), 3 (pedagogy: cross-references), 4 (architecture: diagram/prose cross-links) and 7 (duplication and consistency) from `08-qa-plan.md`. They were applied *across* Part X, the five case-study chapters 52–56 (27 system designs), and their interfaces with chapters 1–51 and the Book II/III plan in `01-master-toc.md`. The reference standard is `case-study-brief.md` (16 subsections per case, ≥ 3 figures per case, application not re-teaching) together with `style-guide.md`, `terminology.md` and `04-agent-allocation.md` §4.5.

**Method.** This was targeted grep, scripted checks and reading, not a full read-through. It follows the wave 7 method.

1. **Structure.** A scratch script parsed every `##`/`###` heading outside code blocks. For each case `N.k` (k ≥ 4) it checked:
   - that subsections `N.k.1`–`N.k.16` exist in order with the brief's exact titles (Problem statement … Production considerations)
   - that each `### N.k.m` sits under its own `## N.k` heading
   - the number of figure captions per case
   - that `**Figure N.K**` and `**Table N.K**` captions run 1, 2, 3 … per chapter with no gaps or repeats
2. **Ownership and distinctiveness.**
   - **Concept blocks.** Every `###`/`####` block in Ch 52–56 was split out and keyword-counted for these owned concepts:
     - consistent hashing; Bloom filters; geohash/S2/H3
     - token bucket and windows; idempotency keys; leases and fencing; quorums, hinted handoff and Merkle trees
     - watermarks; sagas; Snowflake IDs; inverted indexes and BM25; Count-Min and HyperLogLog
     - WebSockets; APNs/FCM; Open Connect; outbox and CDC; Signal protocol; OT/CRDT; LSM; tail latency and hedging
   - **Reading.** Every block over ~350 words with four or more hits was read against its owner section (§14.8, §17.4, §17.9, §22.4–§22.8, §22.15, §26.10–§26.13, §27.7–§27.13, §29.8, §32.7, Ch 40).
   - **Copied text.** A 10-word-shingle comparison was run between every case and every other section of Ch 1–56.
   - **Overlapping pairs.** The pairs named in the brief were read side by side: 53.4/53.5; 55.4/55.5; 53.6/53.7/53.8; 56.4/52.10/Ch 16; 56.5/Ch 68; 52.7/§9.8; 52.8/Ch 27.
3. **Recurring facts.** These facts appear in more than one chapter and were extracted and compared:
   - the Instagram ID layout; the Snowflake layout and epoch
   - Netflix Open Connect; Dropbox blocks and Magic Pocket; Discord message storage
   - Twitter timeline figures; Earlybird; Uber H3 areas and k-ring counts
   - Stripe idempotency; S3 limits and prices; Gorilla 1.37 B/sample; APNs/FCM payload limits and token errors
   - Table 9.12 connection memory
4. **Cross-references.**
   - **Outbound `§`.** All 930 `§N.M[.K]` references in Ch 52–56 (196 intra-chapter, 734 cross-chapter) were resolved by script against the actual headings. Every cross-chapter target was printed with its title and context, and all 262 distinct targets were read for topic fit.
   - **Chapter level.** The chapter-level references to Ch 57+ (on 43 lines) were checked against `01-master-toc.md`.
   - **Inbound.** Every `§5[2-6].*` and `Ch 5[2-6]` reference in Ch 1–51 was read.
   - **Figures and tables.** Every Figure/Table number cited in Ch 52–56 has a matching caption, including six cross-chapter citations: Table 10.2, Figure 22.5, Table 9.12 (×2), Figure 32.10 and Table 40.3.
5. **Numbers.** About 300 numbers in the capacity-estimation sections of all 27 cases were recomputed with `python3` (list below). So were the special checks the brief names:
   - base62 length vs keyspace; timing-wheel span; politeness bound
   - Hungarian vs greedy; Dijkstra vs A*; ledger invariants
   - fan-out cost; Count-Min sizing

   All 17 Python listings in Ch 52–56 were extracted and run with `python3 -I`. Their output was compared with the `text` output blocks (11) or the inline `# prints:` comments (6).
6. **Terminology.** The text was grepped against `terminology.md` and for British spellings.

**Post-edit checks.**
- `python3 build/qa_check.py`: 0 findings in all 56 chapters.
- `python3 build/build.py --chapters 52-56 --name qa --formats html`: 774 diagrams across 56 chapters, 0 errors.
- The rendered HTML was checked for stray inline maths. None of its 1,007 TeX annotations contains prose, and "\$20 per day … \$0.005 per 1,000 PUTs" renders as text.
- `dist/qa.html` was deleted afterwards, and `manuscript/appendices/A-glossary.md` was restored with `git checkout`.
- The only modified files are chapters 03, 52, 54, 55 and 56, plus `docs/project/01-master-toc.md` and `docs/project/04-agent-allocation.md`. Nothing was committed.

## Issues found

| # | Chapter | Location | Severity | Issue | Fix applied |
|---|---|---|---|---|---|
| 1 | 56 | Between §56.4.16 and §56.5.1 | S2 | **Missing case heading.** `## 56.5 Recommendation …` was absent, so the recommendation case's 16 subsections sat under §56.4. Effects:<br>• the build TOC showed no §56.5<br>• three `§56.5` references (Table 56.1, Table 56.2, design challenge 2) did not resolve<br>• §56.4 appeared to have 7 figures and §56.5 none | Inserted `## 56.5 Recommendation System (systems view)`, the TOC title. Re-check: 56.4 has 4 figures, 56.5 has 3. |
| 2 | 55 → 56, 81, 83 | §55.7.1 out-of-scope list; §55.7.8 product-page component; §55.4.8 pricing hand-off; §55.6.1 problem statement | S3 | Old or wrong case numbers:<br>• "§56.2" (×2) is Prerequisites; the recommender is now §56.5<br>• "§81.5" is Instagram Recommendations; Product Recommendation is §81.8<br>• "§83.3" for dynamic pricing should be §83.6<br>• "§83.2" for the ETA model should be §83.5 (the TOC now starts Book II cases at N.4) | All five references corrected. |
| 3 | 55 | §55.7.10 Bottlenecks, item 5 | S3 | "use multiple providers (§55.9.14)". §55.9.14 is the ledger-design comparison. Multi-PSP routing and failover are in §55.9.8. | Changed to (§55.9.8). |
| 4 | 55 → 9 | §55.4.4 storage example, step 6 | S3 | Two problems:<br>• "§9.6 sizes memory per connection": §9.6 is the WebSocket protocol; sizing is §9.9.2<br>• the zone-loss count $35 \times 3/2 = 52.5 \approx 53$ does not follow §9.9.2's formula $S = Z \lceil C/((Z-1)n) \rceil$, which Ch 53 applies correctly | Now cites §9.9.2 and gives $3 \times \lceil 7 \times 10^6 / (2 \times 200{,}000) \rceil = 54$. |
| 5 | 3 → 52 | Table 3.9, month 6 | S3 | **Old numbering.** The chapter column reads "52.1–52.3", which are now objectives, prerequisites and method; the URL shortener, Pastebin and rate limiter are §52.4–§52.6. The same row already cites §52.6 (fixed in the previous commit). | Changed to "52.4–52.6". |
| 6 | 52, 54, 56 | §52.17, §54.15, §56.14 open verification items | S3 | **Stale items.** Each chapter carries an item asking for its old-numbering inbound references to be fixed at integration. These are now resolved:<br>• §9.8 → §52.7, §3.8/§10 → §52.4 and §52.6 (fixed in the previous commit, plus #5)<br>• Ch 21 → §54.5<br>• Ch 56 → §52.3, §52.10, Search Ranking §81.7 | Removed the three items. |
| 7 | 56 → 81 | §56.4.1, scope paragraph | S3 | "Chapter 81 (Search Ranking case study)". The TOC now numbers this case §81.7. | Now "§81.7 (Search Ranking case study)". |
| 8 | 52 | §52.10.4 politeness formula, variable table, example step 3 | S3 | The symbol $d_{\min,host}$ is defined as "Largest delay that still crawls the host within the cycle", which is a maximum. The subscript contradicts the definition. | Renamed $d_{\max,host}$ (×3). |
| 9 | 56 | §56.6.4 metrics example, Interpretation | S3 | "Metrics are a hundred times cheaper than logs per day on disk." The example's own figures give 395 GB/day of metrics against 6.91 TB/day of compressed logs, which is 17×. The 175× ratio holds only against raw logs. | Now "need about 17 times less disk per day than compressed logs (395 GB versus 6.91 TB)". |
| 10 | 56 vs 52 | §56.4.4 crawl example, Interpretation | S3 | **Scale mismatch.** §56.4 says its crawler is "designed in §52.10". But its 4 billion fetches/day (46,296 pages/s) is 23× the §52.10 design point of 2,000 pages/s, and nothing reconciles the two. | Added one sentence: the §52.10 fleet scales out by about 23×. |
| 11 | 56 | §56.7.8 Druid industry callout | S3 | "Message bus" is a term `terminology.md` says to avoid (the Druid paper uses it). | Changed to "message broker". |
| 12 | docs | `01-master-toc.md` Part X; `04-agent-allocation.md` §4.5 | S3 | **Planning docs on old numbering.**<br>• The TOC listed Part X cases as 52.1–56.4, while Book II already starts at N.4 and the drafted chapters start at N.4<br>• §4.5 names "55.6" (now Google Maps) as the idempotency summary site and "85.1" as the feature-store case | TOC Part X renumbered to 52.4–52.10, 53.4–53.8, 54.4–54.8, 55.4–55.9 and 56.4–56.7. §4.5 now reads 55.9 and 85.4. |
| 13 | 54 | §54.8.4, §54.8.5, §54.8.8, §54.8.13, Q16, exercise 4 | S3 | **Units mixed.** Dropbox's block size is "4 MB" in prose and the trade-offs table but "4 MiB" in the `PUT /2/blocks` contract, Q16 and the CDC exercise. The estimates are decimal by convention (§52.3), and the published measurement [Drago et al.] says "4 MB". | **Deferred.** No numeric conclusion changes. The chapter owner should choose one form and state it once. |
| 14 | 52 | §52.8.4 rebuild example, step 3 | S3 | The assumption line gives 100 MB/s per streaming peer. The single-peer comparison uses 200 MB/s. Both conclusions (3.6 h vs 9 min) hold under either reading. | **Deferred** (cosmetic). |
| 15 | 52–56 | Perishable product facts | S3 | These carry "as of" tags or open verification items, but none was re-verified against primary sources here:<br>• S3 PUT price \$0.005/1,000; Google 2024 bulk-sender rules; RFC 9309 details<br>• Netflix 300 M memberships (Q4 2024); YouTube 500 h/min; Drive "over a billion users"<br>• Twitter Redis 800-entry cap and 2023 "For You" figures; WhatsApp 1,024 group limit; Discord 177 → 72 nodes<br>• Geisberger CH timings; Ticketmaster 2022 statement; Stripe 2024 Ledger date | **Deferred.** Already open items in §52.17, §53.15, §54.15, §55.16 and §56.14. |
| 16 | 52–56 | Structure | — | **Structure is correct** (after #1). All 27 cases have exactly the 16 brief subsections with the brief's exact titles, in order. Every case has ≥ 3 figures: 52.4 has 4, 52.10 has 4, 54.4 has 5, 55.9 has 5, the rest 3–4. Figure and table captions run without gaps: Ch 52 24/33, Ch 53 20/27, Ch 54 21/16, Ch 55 25/21, Ch 56 15/26. Case lengths are 3,590–6,116 prose words; §56.4 (5,605) and §56.5 (4,901) split correctly once #1 is fixed. | No action beyond #1. |
| 17 | 52–56 | Ownership measurement | — | Non-owner passages over ~350 words were read:<br>• **§52.4.8 Component 1 (1,384 words, short-code generation).** This is the case's distinctive problem. It defers ID generators to §17.10, the birthday bound to §17.10.2 and the layout to §17.10.3, and adds the keyed Feistel permutation with cycle-walking.<br>• **§52.6.8 Component 1 (356).** Opens "Algorithm choice is settled in Chapter 22" and cites §22.4–§22.8.3 per algorithm; new content is *where* each rule is counted.<br>• **§52.8.8 Component 2 (388).** Cites §27.7–§27.13, §24.11 and §27.14.2 per mechanism; no quorum or Merkle derivation is repeated.<br>• **§55.5.8 Component 4 (500).** Cites §26.10, §26.11 and §26.13 and adds the dispatch-specific CAS plus driver lease.<br>• **§55.9.8 Component 2 (423).** Cites §22.15.1 and §22.15.3 and adds PSP attempt keys, webhooks and payouts.<br>• **§56.4.8 serving tree (559).** Cites §4.8.4, §16.7.3 and §23.7 and adds the 300-shard mixer tree.<br>• **§56.7.8 watermarks (621).** Cites §29.8.2–§29.8.3 and adds a runnable allowed-lateness and deduplication listing.<br>• **New algorithms.** OT (§54.7.8), SimHash, timing wheels, contraction hierarchies and the Hungarian method are taught nowhere in Ch 1–51.<br>• **Copied text.** The shingle check found no shared 10-word run longer than 13 shingles with any other section. | No action. No passage over ~400 words re-derives an owned concept. |
| 18 | 53, 55, 56, 52 | Distinctiveness of overlapping pairs | — | Each overlapping pair splits the work cleanly:<br>• **53.4 vs 53.5.** Chat owns sequencing, watermark receipts and offline sync. WhatsApp's components are all E2EE-specific (X3DH, Double Ratchet, per-device fan-out formula, media keys) and point back to §53.4 for the rest.<br>• **55.4 vs 55.5.** Uber covers the trip state machine, ingestion, supply index and regions, and defers matching to §55.5. §55.5 owns ring expansion, ETA scoring, batching and fencing.<br>• **53.6, 53.7, 53.8.** Instagram's feed component is 167 words and says "§53.7 analyzes them". Twitter's home-timeline component (337) opens "The design applies §53.7.8". §53.7.8 (877) owns the fan-out economics.<br>• **56.4 vs 52.10 vs Ch 16.** §56.4 defers crawling to §52.10 and index internals to Ch 16, and owns serving-tree fan-out and the freshness tiers.<br>• **56.5 vs Ch 68.** §56.5 states the systems-view scope and names no model internals beyond Chapter 68 pointers.<br>• **52.7 vs §9.8.** The push limits and 410/`UNREGISTERED` token handling agree with §9.8 and cite it; §52.7 owns campaigns, priorities and provider failover.<br>• **52.8 vs Ch 27.** See #17. | No action. |
| 19 | 12, 14, 15, 17, 21, 22, 51 vs 52–56 | Recurring facts | — | Consistent across chapters:<br>• **Instagram IDs:** 41/13/10 bits, PostgreSQL-generated, ~69 years (Ch 14 callout, §17.10.3, §53.6.6). The listing's millisecond offset (1,387,263,000) and sequence (5001 mod 1024 = 905) match the 2012 post's worked example as recalled; the shard ID differs by choice.<br>• **Snowflake:** 41/10/12 bits, 2010 (§17.10.3, §52.4.8, §53.4).<br>• **Open Connect:** embedded and IXP appliances, AWS control plane, off-peak tiered fill (§21.10, §54.5).<br>• **Dropbox:** blocks of up to 4 MB [Drago et al.]; Magic Pocket in 2016; "tens of millions" of annual savings, matching Ch 51's \$39.5 M + \$35.1 M.<br>• **Discord:** `((channel_id, bucket), message_id)` and the 2023 ScyllaDB move (§12.6.4, §14.10.1, §53.4.6).<br>• **Twitter:** 4.6k/12k tweets/s, 300k reads/s, 75 followers and 345k writes/s [Kleppmann]; 143,199 tweets/s record; Earlybird ~10 s (§16.7.5 callout, §53.8.8).<br>• **H3:** resolution 7/8/9 = 5.16/0.737/0.105 km²; k-ring $1 + 3k(k+1)$ (§17.9.5, §55.4, §55.5).<br>• **Stripe:** `Idempotency-Key`, stored first response, 409 for concurrent duplicates and 422 for a changed body (§22.15, §55.9).<br>• **Gorilla:** 1.37 B/sample (§12.8, §40.5.5, §56.6.4).<br>• **Connections:** 40 KB per connection (Table 9.12, §53.5). | No action. |
| 20 | 52–56 | Terminology | — | Terms:<br>• No "slave", "uptime", "micro-app", "hit rate" or "ground truth".<br>• "QPS" appears only in a reference title; "master" only for Dynamo's "no master node" and studio video masters.<br>• **"Expiry"** is used as a Pastebin product feature (a paste's expiration time); §52.5 explicitly contrasts it with database TTLs, so it is not a TTL synonym.<br>Spelling:<br>• No British spellings ("-ise", "behaviour", "labelled", "catalogue", "defence").<br>• "Cancellation" (6×) is correct in American English. | No action beyond #11. |

**Counts:** S1 = 0 · S2 = 1 (fixed) · S3 = 14 (11 fixed, 3 deferred) · 5 checked with no action needed.

## Technical spot-checks that passed (recomputed with `python3`)

1. **§52.4.4 URL shortener**
   - **Request rates:** creates 579 / 2,778 per second; redirects 57,870 / 277,778 RPS
   - **Storage and egress:** 9.125 TB/yr, 274 TB for 10 years × 3; 139 MB/s = 1.11 Gbps; click events 1 TB/day and 56 MB/s
   - **Keyspace:** $62^7 = 3.52 \times 10^{12}$; fill 5.2% (1 retry in 19); birthday collisions $4.73 \times 10^7$; $62^{10} < 2^{63} < 62^{11}$
   - **Cache and fleet:** 200 GB working set; 13,889 misses/s (55,556 at 80%); 50 nodes
   - **Code length:** $\log_{62}$ = 6.84 / 7.96 / 6.28 → L = 7 / 8 / 7; $2^{42}/62^7 = 1.25$; allocator one call per 3.6 s; 36 s per block
   - **Feistel listing:** output matches verbatim.
2. **§52.5.4 Pastebin**
   - 556 creates/s and 2,778 reads/s; 444 Mbps
   - **Little's Law:** 3,472 / 62,500 / 2.0 M / 10.5 M / 45 M = 57.6 M pastes, 1.15 TB
   - 21.9 TB/yr permanent; 1.46 TB/yr metadata (0.44 TB retained); deletes 81/s average, 389/s peak; 95% share
   - S3 PUT cost \$20/day for 4 M PUTs
3. **§52.6 rate limiter**
   - 3 M decisions/s; 100 shards and 4.8 Gbps if every decision were central; 20 shards at 20%; 3 GB of keys
   - lease batches 1,000 calls/s; 20,000 outstanding tokens = 0.2 s of quota
   - allocation 3,440 / 1,820 / 740; overshoot 167 (2.8%) and 833 (14%)
4. **§52.7 notification system**
   - 5,787/s average; 8,333 transactional peak; 27,778 campaign; ≈ 36,000 → 50,000 design rate
   - 45 TB log; 150 GB events; 270 GB preferences and tokens; \$100,000/day SMS
   - **Drain:** 1,200 s; 4,286 s at a 20,000/s provider cap
5. **§52.8 key-value store**
   - 390 TB raw; 69.6 → 70 nodes for capacity; 9 M replica operations/s → 150 nodes; 2.6 TB per node (46%)
   - Bloom filters 375 GB (2.5 GB per node)
   - 23.8 GB per partition, 328 per node; 72 GB of hints; rebuild 13,000 s vs 520 s
6. **§52.9 job scheduler**
   - $1.999 \times 10^8$ recurring + $5 \times 10^7$ one-off = 2,892/s
   - burst $1.03 \times 10^6$ → 103,000/s (36×); 125 GB/day, 3.75 TB for 30 days; $1.04 \times 10^7$ timers in the next hour
   - **Timing wheel:** span 3,600 s with 600 + 60 slots, 86,400 s with 684 slots vs 864,000 flat; listing span $60^3$ = 216,000 s (60 h); 1.7 M timers per 10-minute window; 52,000 and 5,200/s per node of 20
   - **Hierarchical timing-wheel listing:** output matches verbatim.
7. **§52.10 web crawler**
   - 1,157 pages/s; 1.6 / 0.93 Gbps; 75 / 225 TB; 2,000 in flight (Little's Law)
   - **Bloom filter:** 9.59 bits → 36 GB and 14.38 bits → 54 GB (1.08 GB per node)
   - **SimHash:** 24 / 96 GB; pigeonhole on four 16-bit blocks for distance ≤ 3
   - **Politeness:** $H \ge 10{,}000$; 579 days at d = 5 s; $d_{\max} = 0.26$ s (3.9 req/s)
   - **SimHash listing:** output matches verbatim.
8. **§53.4 chat**
   - 46,296 / 138,889 messages/s; 6.4 recipients; 888,889 deliveries/s at peak
   - receipts 592,593/s naive vs 69,444/s with watermarks (8.5×)
   - 438 TB/yr, 1.31 PB at RF 3; media 100 TB/day, 51.1 PB erasure-coded (39× text); 7.1 Gbit/s; 1.8 TB cache
   - 81 gateways at 308,642 each; 1.03 M writes → 124 nodes; 329 storage nodes
   - **Sequencer listing:** prints `[1, 2, 3] last_seq = 3`.
9. **§53.5 WhatsApp**
   - **Per-device ciphertexts:** $C_{1:1} = 2.2$; group delivery 15; 1.96 uploads and 4.76 deliveries per message; 1.16 M / 2.27 M / 5.51 M per second
   - large groups: 1,637 pairwise encryptions; re-key $1.67 \times 10^6$
   - pending queue $2.38 \times 10^{10}$ envelopes, 11.9 TB; 750 chat servers
   - **Media:** 2.1 PB/day up; 10 PB/day and 0.93 Tbit/s down; 88 PB over 30 days
10. **§53.6 Instagram**
    - 1,157 / 3,472 posts/s; 339 TB/day, 124 PB/yr, 173 PB erasure-coded
    - 115,741 / 347,222 feed requests/s; 1.16 M image fetches/s; 15 PB/day = 1.39 / 4.17 Tbit/s; origin 57,870/s and 0.75 PB/day
    - hot counter 3,333 likes/s; push 173,611 inserts/s at 150 followers
    - **Instagram ID listing:** output matches the inline `# prints:`.
11. **§53.7 News Feed fan-out**
    - push 4.63 M/s (ordinary) vs 23.1 M/s (100,000 large accounts, 5×, 0.005% of DAU); $T_{\text{fan}}$ = 100 s
    - 36 TB of lists; pull 694,444 loads/s, 278 M lookups, 27.8 M index requests; 1 TB index; 694 M scorings/s
    - **Fan-out simulation:** output matches verbatim.
12. **§53.8 Twitter/X**
    - 5,787 tweets/s; 579,000 inserts/s; 450 M burst backlog drained in 225 s
    - 86,806 / 260,000 reads/s; timeline cache 5.12 / 15.4 TB; search index 210 GB
    - **Count-Min:** $N = 8.67 \times 10^6$, $\varepsilon N = 87$, $w = 271{,}829$, $d = 7$, 7.6 MB per window, 274 MB for 36 sketches
    - **Trends listing:** prints z = 180.0 / 9.6 / 1.4 as commented.
13. **§54.4 YouTube**
    - 30,000 video-s/s; 300 / 600 Gb/s; 7.2 M uploads/day (83/s); 3.24 PB/day, 1.18 EB/yr, 1.77 EB raw
    - H.264 ladder 5.25 PB/day; 120,000 cores = 1,875 → 6,250 servers; VP9 600,000 cores (6× total), 3.15 PB/day
    - 104 / 208 Tb/s; 115,741 views/s; 1.39 M heartbeats/s; metadata 5.3 TB/yr, 52.6 TB, 526 GB cache
    - **VP9 break-even:** \$0.04 + \$0.0525 over \$0.0000984 = 940 views; \$98 per million views
    - **Transcoding DAG simulation:** output matches verbatim.
14. **§54.5 Netflix**
    - 50 / 125 Tb/s; 1,563 appliances
    - 4.5 × 10⁸ play starts (5,208 / 15,625 per second); 104,167 / 312,500 RPS; 156,000 RPS per region after evacuating one of three
    - catalog 900 TB; 1.8 TB/day of new content
15. **§54.6 Spotify**
    - 8.23 × 10⁹ plays (95,238/s); 3.2 / 6.4 Tb/s; 476,190 events/s, 20.6 TB/day
    - catalog 2.52 PB; 4.2 MB per track; 8.8 TB of playlists; 476 cached tracks
    - **Stream-counting listing:** prints `{('T1', '2026-10'): 1, ('T2', '2026-10'): 1}` as commented.
16. **§54.7 Google Drive**
    - 1 PB of metadata; 5 EB stored; 3 PB/day (1.1 EB/yr, 278 Gb/s)
    - 347,222 / 34,722 metadata operations/s; $2 \times 10^6$ OT commits/s on 200 servers
    - **OT listing:** prints "converged in 10,000 random concurrent pairs" and `cha`.
17. **§54.8 Dropbox**
    - $10^8$ connections, 400 servers; 11,574 / 34,722 commits/s; 1 PB/day (93 Gb/s); 104,000 wake-ups/s
    - block index $5 \times 10^{11}$ blocks, 32 TB
    - **Three-way sync listing:** output matches the comment.
18. **§55.4 Uber**
    - 347 / 1,042 trips/s; 5,208 estimates/s; $U$ = 500,000/s (0.8 Gb/s); 1 M reads/s; 480 and 720 updates per trip
    - 788 TB/yr of history; 54.75 and 164 TB/yr; 400 MB supply index; 25 → 50 ingestion nodes
    - 54 gateways (see #4)
19. **§55.5 ride matching**
    - **k-ring:** 7 / 19 / 127 / 169 / 37 cells; $C$ = 5.9 / 16.0 / 4.0 / 5.3; radii 2.38 and 0.48 km; resolution 8 = 7.0× resolution 9; Q5 15.5 drivers
    - 20,000 ETAs/s; Hungarian $200^2 \times 300 = 1.2 \times 10^7$
    - **Re-offers:** $E[N] = 1.43$; $0.3^3 = 2.7\%$; 8.33 s and 25 s
    - **Greedy vs Hungarian:** toy 7.5 vs 3.5 min (2.0 + 5.5 vs 2.5 + 1.0); 3 × 3 block expectation 9; the 14% batch gain matches the listing output verbatim
20. **§55.6 Google Maps**
    - **Tile pyramid:** $T_{\le 14}$ = 357,913,941 → $1.07 \times 10^8$ land tiles = 2.15 TB; $T_{\le 18} = 9.16 \times 10^{10}$ → 412 TB raster
    - **Ground resolution:** $C/256$ = 156,543 m; cos 37.77° = 0.7905; 3.78 and 0.47 m/pixel
    - 694,444 tiles/s, 111 Gb/s; 15,625 routes/s; 20,833 searches/s; 104,167 autocomplete requests/s; 200 MB/s of probes; 46.4 GB road graph
    - **Dijkstra vs A*:** 16.24 min both; 13,132 vs 9,582 settled (27% fewer); the listing matches verbatim
21. **§55.7 Amazon**
    - 23,148 / 115,741 page views/s; 28,935 searches/s; 11,574 cart writes/s; 1,157 orders/s
    - 5 TB catalog; 18.25 TB/yr of orders; 5.8 M internal calls
    - **Hot-item partitioning:** $N$ = 15 (48 without the gate); one row = 500/s; 16,667 page views/s
22. **§55.8 ticket booking**
    - 328,767 orders/day (3.8/s); 50 GB seats; 360 GB/yr
    - **Waiting room:** $q^* = 25{,}000$ (98.75% miss); $a = 83.3$/s; $T^* = 300$ s; 208 holds/s, sold out in 240 s; 75,000 concurrent holds; 66,667 polls/s
23. **§55.9 payments**
    - 579 / 2,894 payments/s; 60 GB/day, 21.9 TB/yr, 153 TB over 7 years; 1,157 webhooks/s; 50 GB/day of keys
    - **Duplicate charges:** $D = 25{,}000$/day
    - **Ledger invariants:** 9,680 + 320 − 8,500 − 1,500 = 0; refund 2,125 + 375 − 2,500 = 0; seller owed 6,375; trial balance 0. The listing matches verbatim.
24. **§56.4 search engine**
    - 57,870 / 115,741 queries/s; 347,222 autocomplete/s; 81,019 after the cache; 55.6 Gbit/s; cold-cache 1.43×
    - **Index:** 36 / 30 / 120 TB; 300 shards of 120 GB postings and 100 GB forward index
    - **Fleet:** 194,444 cores, 3,038 leaves, $R = 11$, 8,000 QPS per replica, 5,400 leaves
    - **Crawl and distribution:** 46,296 pages/s; 18.5 Gbit/s; 50 TB/day; 375 / 562.5 TB; 648 TB/week at 1.07 GB/s
    - **Tail latency:** $0.99^{300} = 4.9\%$
25. **§56.5 recommendation (systems view)**
    - 34,722 / 104,167 requests/s; $1.56 \times 10^8$ light and $4.17 \times 10^7$ heavy scorings/s; 8,333 cores (131 servers) and 1,563 cores
    - 50 GB / 5 GB of item features; 521 MB/s of user features
    - 1.44 TB precomputed; $7.5 \times 10^{10}$ impressions (868,056/s); 75 + 15 + 2 = 92 TB/day
    - **Latency budget:** 160 ms + 40 ms slack; $0.99^4 = 96\%$
    - **Candidate-merge listing:** output matches verbatim.
26. **§56.6 logging and monitoring**
    - 69.12 TB/day; hot 96.8 TB; warm 159 TB; archive 232 TB; full-text 484 TB (5×)
    - **Metrics:** 3.33 M samples/s; 395 GB/day; 5.9 TB; 7.8 TB downsampled; 600 GB ingester memory
    - **Kafka:** 51.8 TB; drain 6 h and 24 h
    - **Series-limiter listing:** output matches verbatim.
27. **§56.7 real-time analytics**
    - 1 / 2.5 GB/s; 86.4 TB/day; 453.6 TB of Kafka
    - rollup 30×; 345.6 GB/day, 273 TB; raw 151 TB
    - 6,667 dashboard queries/s; 7-day panel $2.02 \times 10^7$ vs $5.04 \times 10^5$ rows (40×)
    - **Freshness:** $F_{\text{live}}$ 7.6 s (32.6 s with a 30 s checkpoint); $F_{\text{final}}$ 77.6 s
    - **Watermark listing:** output matches verbatim.
28. **Cross-references.**
    - **Ch 52–56:** after the fixes, all 930 `§` references resolve. Every cross-chapter target is on topic apart from #2–#4.
    - **Out to Ch 57+:** chapter-level references match the TOC: Ch 57 statistics, 62 feature stores, 64/66/67 serving and optimization, 68 recommendation models, 69 rollout, 74–75 ANN and dense retrieval, 81 product recommenders, 82 fraud, 83 pricing and ETA, 89 estimation handbook, 91 practice library.
    - **Inbound:** all `§5x` references from Ch 1, 3, 9, 10, 17 and 21 resolve to the right case (§52.4, §52.6, §52.7, §53.7, §54.5, §55.4, §55.5). #5 fixes the one bare old-numbering range.

## Remaining risks

- **Book II case numbering.** Ch 55 and 56 now cite §81.7, §81.8, §83.5 and §83.6 from the TOC. These are plans, not drafted sections. If Ch 81–86 change the N.4 start or reorder cases, these four references and the Ch 68/74/81 pointers in §56.5 must be re-resolved. `qa_check.py` still has no `§`-reference resolver; this review used a scratch script, as in waves 6 and 7.
- **Recommender split across three places.** §56.5 owns the serving funnel, the latency budget and served-feature logging. Ch 68 must own the models; Ch 81 must not re-derive the 200 ms budget or the logging-for-training argument; Ch 62 must own point-in-time correctness. Ch 68 should cite §56.5.4 and §56.5.8 for the systems numbers.
- **Teaching scales diverge between cases by design.** Several systems appear at different design points:
  - **Crawler:** §52.10 at 2,000 pages/s; §56.4 at 46,296 (now reconciled in text)
  - **Feeds:** Instagram 500 M DAU; News Feed 2 B; Twitter 250 M
  - **Connection gateways:** 500,000 (§53.4), 1 M (§53.5) and 200,000 (§55.4) per server

  Each states its assumptions. Ch 89 and Ch 91 should cite one case's numbers per question rather than mixing them.
- **QuickBite and PhotoShare do not appear in Ch 52–56.** No running-example contradictions are possible here. The case studies do not say which earlier teaching scale they would map to, which is acceptable because they use their own assumptions throughout.
- **Perishable facts** (#15) are concentrated in the industry callouts of Ch 53–55: Twitter 2012–2023 figures, WhatsApp limits, Netflix memberships and Ticketmaster. They carry open items but were not re-verified here.
- **Units and spelling.** "4 MB" vs "4 MiB" for Dropbox blocks (#13) is the only unit mix found. `terminology.md` now rules "canceled", and Ch 52–56 use only "cancellation", which is unaffected.
