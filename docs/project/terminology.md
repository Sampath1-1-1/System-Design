# Canonical Terminology

Use these terms consistently across all chapters. Left column is canonical; right column lists variants to avoid (or to mention once as synonyms).

| Canonical term | Avoid / mention once as synonym |
|---|---|
| primary / replica | master / slave (mention once as legacy terms) |
| leader / follower (consensus and log replication contexts) | — |
| node (a machine or process in a cluster) | box, host (except in networking context) |
| service (a deployable unit with an API) | app, micro-app |
| client | caller (acceptable in RPC context) |
| request rate, in requests per second (RPS) | QPS (acceptable synonym; define once) |
| latency (time for one operation) | response time (only when including queueing explicitly) |
| throughput (operations completed per unit time) | bandwidth (reserve for network/memory capacity) |
| p50 / p95 / p99 / p99.9 | 50th percentile etc. (define once) |
| availability (fraction of time serving correctly) | uptime |
| durability (probability data is not lost) | — |
| partition (data subset) — in DB context; **network partition** for network splits | shard (acceptable synonym for DB partition; define once in Ch 14) |
| strong consistency = linearizability | "ACID consistency" (different concept — C in ACID) |
| eventual consistency | — |
| message broker | message bus |
| event (a fact that happened) vs command (a request to do something) vs message (transport unit) | — |
| at-most-once / at-least-once / exactly-once (effectively-once processing) | — |
| idempotency key | request ID (only when not used for deduplication) |
| cache hit ratio | hit rate (acceptable) |
| time to live (TTL) | expiry |
| feature (ML input variable) | attribute |
| label (ML target) | ground truth (acceptable when discussing annotation) |
| training–serving skew | — |
| inference (running a trained model) | prediction (acceptable for the output), scoring |
| time to first token (TTFT); time per output token (TPOT); inter-token latency (ITL) | — |
| model FLOPs utilisation (MFU) | — |
| retrieval-augmented generation (RAG) | — |
| approximate nearest neighbour (ANN) search | — |
| KB, MB, GB, TB = 10³, 10⁶, 10⁹, 10¹² bytes; KiB, MiB, GiB = 2¹⁰, 2²⁰, 2³⁰ bytes | mixing the two without stating |
| British/American spelling: American spelling in prose (optimize, behavior, utilization) | mixing spellings |
