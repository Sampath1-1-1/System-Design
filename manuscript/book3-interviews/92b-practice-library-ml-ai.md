## 92.6 Hard (Q27–Q40)

Hard questions change the unit of design. Easy and Medium prompts ask for one model behind one product surface; Hard prompts ask for a **platform** that many models share (feature store, training, serving, experimentation, monitoring), a **pipeline** whose data volume or freshness is the problem (streaming personalization, perception data, federated learning), or an **LLM system** whose quality must be measured before it can be designed (RAG, support agent). The ML extension of §88.6 still applies, but in a platform question the "model" of steps M4–M6 is often a statistical procedure or a scheduling policy rather than a predictor, and the deciding deep dive is usually a correctness property: point-in-time joins, score parity, permission fidelity, sample-ratio checks.

Eight of the fourteen questions have a full case study or an owning chapter elsewhere in the book. For those, the solution below is the interview-length answer with the case's numbers, and the cross-reference carries the depth. The other six are full solutions. All designs are *Evidence: Illustrative*: teaching designs with assumed numbers, not descriptions of any company's system.

**Table 92.101 — Hard questions at a glance.**

| Q | Title | Solution | Deciding deep dive | Owner |
|---|---|---|---|---|
| 27 | Feature store | Compact | Availability-time as-of join; partition fan-out | §85.4, Ch 62 |
| 28 | ML training platform | Compact | Quota borrowing, preemption cost, goodput | §85.5, Ch 46 |
| 29 | Model serving platform | Compact | Popularity tiers; scale models, not servers | §85.6, Ch 66 |
| 30 | Real-time personalization | Full | Freshness race between events and the next request | §68.13, §85.7 |
| 31 | Billion-scale embedding retrieval | Full | Memory versus throughput sizing; tower–index version lock | §68.6, Ch 74 |
| 32 | Enterprise RAG assistant | Compact | Permissions as index data; revocation window | §86.4, Ch 75 |
| 33 | LLM customer-support agent | Compact | Proposal versus decision; cost per resolution | §86.7, Ch 77 |
| 34 | Speech recognition | Compact | Concurrent streams; end-pointing dominates latency | §84.6 |
| 35 | Machine translation | Compact | Simultaneous policy is a capacity decision | §84.7 |
| 36 | Perception data engine | Full | Trigger mining and auto-labeling economics | Ch 63 |
| 37 | Experimentation platform | Full | Power, variance reduction, sample-ratio mismatch | §57.14 |
| 38 | ML monitoring platform | Full | Alert design under thousands of tests; delayed labels | Ch 70 |
| 39 | Federated keyboard model | Compact | Round economics, secure aggregation, client DP | §71.11 |
| 40 | Two-sided marketplace matching | Full | Batched assignment with learned costs; switchback tests | §55.5 |

### 92.6.1 Q27. Feature store

**Difficulty:** Hard · **Time:** 45 min · **Related:** §85.4 (full case study), Ch 62 (feature stores), §89.8–§89.9 (cache and database sizing)

#### Prompt

"Ninety teams each build their own feature pipelines, and two incidents last quarter came from models that saw different feature values online than in training. Design a company-wide feature store."

#### Clarifying questions and assumptions

Which consumers matter (fraud scoring with a few keys, ranking with hundreds of keys per request, batch forecasting)? How fresh must streaming features be? Is the training-set builder in scope? Assume the §85.4 marketplace: 100 million users, 40 million items, 400 models (150 online), 120,000 serving calls/s at peak.

#### Requirements

Functional: declare features once in reviewed code; materialize batch and streaming views to an offline history and an online store; build point-in-time-correct training sets; serve feature vectors with defaults; log served values; discover and govern. Non-functional (Table 85.3): online p99 ≤ 10 ms; 99.99% of reads return values or declared defaults; streaming p99 age ≤ 60 s; ≥ 99.5% of logged served values reproduced exactly by the builder; 500 million rows × 400 features built in under 2 hours.

#### Estimation

::: example
**Worked example — Fan-out, memory and the training join (numbers of §85.4.4).** Reads use the key-count and partition-touch arithmetic of §62.11.1; memory uses the stored-bytes and fleet formulas of §89.6 and §89.10.

1. Keys: $100{,}000 \times 4 + 20{,}000 \times 151 = 3.42$ million keys/s; ranking is 17% of calls but 88% of keys.
2. A ranking read of 150 random items over $S = 48$ partitions touches $48\,(1 - (1 - 1/48)^{150}) = 46.0$ partitions; at 0.999 per sub-request it meets its deadline with probability $0.999^{46} = 0.955$.
3. Online memory: one copy 221.4 GB; with $r = 3$ and 60% memory utilization, 1,107 GB, about 18 nodes.
4. One training build: 25 views × 180 days × 2 GB/day = **9 TB scanned**.

**Interpretation.** The online store is small; the expensive things are partition fan-out and the training-set join. **Engineering implication.** Replicate the 19 GB item view in full so a ranking read is one call, and invest in the offline builder (bucketing, tiles) rather than in more online nodes.
:::

#### Data, labels and features

Entities (user, item, merchant, card), sources (event streams, warehouse tables), and three view types: batch (daily aggregates), streaming (velocity counters, seconds fresh) and on-demand (computed from the request). Every stored value carries an **availability time**, when it could have been read in production, not only the event time; the as-of join uses availability time (§62.8). Labels belong to consumers; the platform supplies the spine join.

#### High-level design

**Figure 92.101 — Feature store: one definition, two engines, a tiered online store.**

```mermaid
flowchart LR
  REPO[Feature definitions<br/>in Git] --> REG[(Registry)]
  REG --> BJ[Batch jobs]
  REG --> SJ[Streaming jobs]
  WH[(Warehouse<br/>and lake)] --> BJ
  EV[[Event streams]] -.-> SJ
  BJ --> OFF[(Offline history<br/>object storage)]
  SJ --> OFF
  BJ --> ON[(Online store<br/>tiered)]
  SJ -.->|upserts| ON
  OFF --> TB[Training-set builder<br/>as-of join]
  SP([Spine: keys, label<br/>times, labels]) --> TB
  C([Model service]) -->|gRPC multi-get| API[Serving API]
  API --> ON
  API -.->|sampled served values| LOG[(Served-value log)]
  LOG -.-> PAR[Parity job]
  OFF --> PAR
```

**Reading the diagram.** One reviewed definition drives both batch and streaming engines, which write the same values to offline history (object storage) and the online store. The serving path is synchronous: model services call the serving API with batched keys over gRPC. Streaming upserts and served-value logging are asynchronous (dotted). The training-set builder joins a spine to offline history by availability time; the parity job recomputes logged served values and reports the match rate as an SLO. Failure points: a stalled streaming job (values age, so the API returns age with each value and defaults past a bound), hot partitions under ranking fan-out, and builder jobs that scan terabytes. Scaling: replicate small entity views in full, partition large ones, and tile windowed aggregates.

#### Model and evaluation

There is no single model; the platform's "evaluation" is correctness. Gate every definition change on a parity test (offline recompute equals online value on sampled keys), a backfill-versus-streaming comparison within 0.1%, and a leakage check (no value with availability time after the label time). Measure adoption: share of online models reading from the store, and reuse rate of features.

#### Serving and monitoring

Hedged reads after the p95, declared defaults on deadline, value age returned with every vector. Monitor per view: age at read, materialization lag, null and default rates, drift (Ch 70), parity match rate, builder bytes scanned.

#### Deep dives

1. **Availability-time as-of join.** A daily batch view computed at 04:00 for yesterday must not be visible to a label at 01:00; joining on event time leaks it (§62.8).
2. **Per-entity layout.** Partition fan-out, not key count, decides ranking latency; full item replicas collapse 46 sub-requests into one.
3. **Streaming correctness.** At-least-once delivery with deduplication and idempotent upserts, measured against a batch recompute rather than claimed as exactly-once.

#### Trade-offs and alternatives

Warehouse as-of joins are simpler and fine below about 100 million rows; managed feature stores trade control for speed of adoption (§62.13); logging served features and training on the logs ("log and wait") removes skew for new features at the price of a delay before they can be used.

#### Follow-up questions

1. *Why not just use the warehouse?* At 500 million rows it shuffles 9 TB and usually joins on event time, not availability time.
2. *How do you prove online equals offline?* Sampled served-value logs recomputed by the builder; the match rate is an SLO with an owner.
3. *A streaming job stalls for 20 minutes.* Values age; consumers see the age, fall back to defaults or to the batch value past their bound; alert on lag, not on errors.
4. *How do you stop duplicate features?* Catalog search by entity and usage, near-duplicate detection and review before activation.

#### What distinguishes levels

- **Mid:** offline and online stores, a registry, batch materialization.
- **Senior:** point-in-time joins, batched reads, streaming views, skew detection.
- **Staff:** quantifies partition fan-out and changes layout per entity, joins on availability time, makes streaming correctness and parity measurable SLOs, and treats backfill as part of the definition.

### 92.6.2 Q28. ML training platform

**Difficulty:** Hard · **Time:** 45 min · **Related:** §85.5 (full case study), §46.10–§46.12 (gang scheduling, GPUs, backfill), §65.15–§65.16 (checkpointing, fault tolerance)

#### Prompt

"Eighty teams share 4,096 GPUs, each owning a fixed slice. Some slices idle at night while others queue for days. Design a self-service training platform."

#### Clarifying questions and assumptions

Job mix (notebooks and sweeps versus multi-node pre-training)? Are GPUs homogeneous? Is billing in scope? Assume §85.5: 3,072 H100-class and 1,024 A100-class GPUs; 25,000 jobs a week, 80% small (≤ 8 GPUs), 18% medium (16–128), 0.1% large (256–1,024).

#### Requirements

Functional: submit jobs and sweeps; guaranteed quota per team with borrowing of idle capacity; gang admission and topology-aware placement; preemption with notice; automatic restart from checkpoints; experiment tracking; cost reports. Non-functional (Table 85.7): small-job median wait ≤ 10 min; quota returned within 15 min; large jobs start within 4 h; ≥ 85% allocation; ≥ 95% goodput for jobs of 256+ GPUs; running jobs survive a control-plane outage.

#### Estimation

::: example
**Worked example — Capacity, demand and the cost of reclaiming (numbers of §85.5.4).** Fleet arithmetic is the redundant-fleet form of §89.10; preemption loss uses the formula of §85.5.4.

1. Capacity $4{,}096 \times 168 = 688{,}128$ GPU-h/week; demand $120{,}000 + 216{,}000 + 256{,}000 = 592{,}000$, an allocation of **86%**.
2. Large jobs are 0.1% of jobs and **43%** of GPU-hours.
3. Reclaiming a borrowed 32-GPU job (30-minute checkpoints, 5-minute restart): without checkpoint-on-signal $32 \times (15 + 5)/60 = 10.7$ GPU-h lost; with a 1-minute save on signal, $32 \times 6/60 = 3.2$ GPU-h. At 200 reclaims a week: 2,133 versus 640 GPU-h.
4. A 30B-parameter checkpoint at 14 bytes/parameter is 420 GB; draining it in 30 s is a 14 GB/s burst per job.

**Interpretation.** Two populations share one fleet: many small latency-sensitive jobs and a few huge gangs that dominate GPU-hours. **Engineering implication.** Backfill small jobs fast, reserve rack-aligned blocks for large gangs, lend idle quota only as preemptible capacity, and make checkpoint-on-signal part of the training library.
:::

#### Data, labels and features

The platform's data are job specifications, queue events, node health signals and per-job utilization (allocation, SM activity, MFU), plus experiment metadata: parameters, metrics, code and data versions (§69.7). The "labels" a platform learns from are job runtimes and failures, used to predict durations for backfill.

#### High-level design

**Figure 92.102 — Training platform control plane.**

```mermaid
flowchart LR
  U([Engineer or SDK]) -->|submit job| API[Job API]
  API --> Q[(Job queue<br/>suspended jobs)]
  Q --> ADM[Admission:<br/>quota, borrowing]
  ADM --> PL[Placement:<br/>gangs, topology]
  PL --> K8S[Cluster manager]
  K8S --> N[GPU nodes]
  N -->|checkpoints| CK[(Object storage)]
  N -.->|metrics, events| TR[(Experiment tracker)]
  HM[Health monitor] -.->|cordon bad nodes| K8S
  N -.->|telemetry| HM
  ADM -.->|preempt borrowed| N
  TR -.-> BILL[Usage ledger<br/>and chargeback]
```

**Reading the diagram.** Jobs enter the queue suspended; admission checks quota and decides whether a job runs on guaranteed or borrowed capacity; placement admits whole gangs onto topology-aligned nodes (§46.10–§46.11). Nodes write checkpoints to object storage and stream metrics asynchronously to the tracker and the ledger. The health monitor cordons nodes that fail checks. Failure points: a node failure kills a gang (restart from the last complete checkpoint on spare nodes), a control-plane outage (running jobs continue; only admission stops), and checkpoint bursts saturating storage. Scaling: the scheduler handles bursts of sweep submissions, not the 0.04 jobs/s average.

#### Model and evaluation

The "model" is the scheduling policy. Evaluate a new policy by replaying recorded job traces in a simulator (queue wait percentiles per class, allocation, goodput, fairness deviation) before rollout, then canary it on one pool.

#### Serving and monitoring

Monitor queue wait by class and team, allocation versus effective utilization (SM activity, MFU), preemptions and restarts per job, checkpoint durations, node failure rates. Report allocation and utilization separately: a measured cluster trace found GPUs in use averaged about 52% hardware utilization [Jeon et al. 2019].

#### Deep dives

1. **Quota borrowing and reclaim.** Guarantees per team, idle capacity lent as preemptible, reclaimed within 15 minutes with checkpoint-on-SIGTERM.
2. **Large gangs.** Reservations on rack-aligned blocks, backfilled with jobs predicted to finish before the reservation starts (§46.12.2).
3. **Reliability.** Asynchronous checkpoints, staggered across large jobs; elastic restart on fewer nodes; node burn-in before joining the pool.

#### Trade-offs and alternatives

Slurm gives mature backfill and reservations; Kubernetes gives a shared platform with serving and data jobs (§46.12.3). Fixed slices are simple and predictable but waste idle capacity; full sharing is efficient but needs preemption that teams trust.

#### Follow-up questions

1. *Why is 90% allocation not 90% utilization?* Idle notebooks, input stalls and low MFU hide inside allocated GPUs.
2. *How do large jobs ever start?* A reservation drains a block while backfill uses the drain window.
3. *A node fails mid-run of a 512-GPU job.* Cordon it, restart from the last manifest on a spare; lost work is about half a checkpoint interval times 512 GPUs.
4. *How do you stop teams hoarding?* Bill reserved quota whether used or not, and lend it out when idle.

#### What distinguishes levels

- **Mid:** a job queue on Kubernetes with GPU requests.
- **Senior:** gang scheduling, quotas, checkpoints and restart.
- **Staff:** quantifies preemption cost and the value of a utilization point, separates allocation from utilization, uses billing as an incentive, and treats 8-GPU and 512-GPU jobs with different policies.

### 92.6.3 Q29. Model serving platform

**Difficulty:** Hard · **Time:** 45 min · **Related:** §85.6 (full case study), §66.6–§66.12 (batching, autoscaling, cold start, rollout), Ch 79 (LLM-specific serving)

#### Prompt

"Three hundred teams have 5,000 models deployed, each as its own service with two replicas. Design a shared serving platform that cuts cost while keeping each team's latency objective and isolation."

#### Clarifying questions and assumptions

Popularity distribution? Runtimes (trees, scikit-learn, ONNX, GPU models)? Latency objectives by class? Assume §85.6: 300,000 predictions/s at peak; 50 hot models carry 85% of traffic, 950 warm carry 14.9%, 4,000 cold share 0.1%; 200 models need GPUs.

#### Requirements

Functional: deploy a registry version with a runtime and SLO class; predict over REST and gRPC; load models on demand; scale per model, including to zero resident copies; alias-based rollout with shadow and canary; tenant quotas; sampled prediction logging. Non-functional (Table 85.11): ≤ 5 ms p99 platform overhead for warm models; cold first request ≤ 2 s on CPU; one tenant at 10× quota raises others' p99 by ≤ 10%; platform cost ≤ 25% of one-deployment-per-model.

#### Estimation

::: example
**Worked example — Dedicated versus shared (numbers of §85.6.4).** CPU fleet sizing is the CPU-bound form of §89.10; prices \$0.04 per vCPU-hour and \$0.005 per GB-hour.

1. Dedicated: 10,000 pods, 10,000 vCPU and 9,920 GB: **\$449.6/h**, \$3.94 million a year.
2. Real work at peak: $300{,}000 \times 2$ ms $= 600$ busy vCPU; the baseline reserves 17 times that.
3. Shared: hot models dedicated and autoscaled, \$51.0/h; warm and cold on 16 multi-model servers sized by memory, \$20.5/h; total **\$71.5/h**, 16% of the baseline.
4. Cold start of a 300 MB CPU model on a warm server: $0.75 + 0.3 + 0.2 + 0.3 = 1.55$ s from object storage.

**Interpretation.** In the baseline, cost is redundancy floors for models nobody calls; in the shared design the long tail costs only memory. **Engineering implication.** Scale models (resident copies), not servers; keep the multi-model fleet warm with memory headroom.
:::

#### Data, labels and features

The platform handles artifacts (verified by digest), per-model traffic statistics that drive placement, and sampled prediction logs with model version and features for tenants' monitoring and training (§60.6.2). Labels remain the tenants' responsibility.

#### High-level design

**Figure 92.103 — Multi-tenant serving: tiers, affinity router and controller.**

```mermaid
flowchart LR
  C([Client services]) -->|REST or gRPC| GW[Gateway:<br/>auth, quota]
  GW --> RT{Router:<br/>model affinity}
  RT -->|hot| HD[Dedicated autoscaled<br/>deployments]
  RT -->|warm, cold| MM[Multi-model<br/>server fleet]
  MM -.->|load on miss| AC[(Local artifact<br/>cache)]
  AC -.-> REG[(Registry and<br/>object storage)]
  CTL[Placement controller] -.->|copies per model| RT
  MM -.->|load, memory stats| CTL
  HD -.->|sampled predictions| LOG[[Prediction log]]
  MM -.-> LOG
```

**Reading the diagram.** The gateway authenticates and enforces per-tenant quotas; the router sends hot models to dedicated deployments and other models to a small set of home servers chosen by rendezvous hashing, so each model is resident on a few servers rather than all. On a miss, a server loads the artifact from a local cache or the registry. The controller adjusts copies per model from load statistics. Logging is asynchronous. Failure points: load storms after a restart (staged restarts preserve caches), cache thrash when memory is short, a slow or malicious model artifact (timeouts, sandboxes, safe formats). Scaling: add servers by memory; promote a warm model to the hot tier when its traffic warrants.

#### Model and evaluation

The platform's decision models are the placement and eviction policies. Evaluate them by replaying a week of request traces: cold-request rate, p99 by tier and isolation deviation. Affinity routing matters more than the eviction algorithm (§85.6.8).

#### Serving and monitoring

Per model and tenant: RED metrics, cold-request rate and latency, resident copies, evictions, version on every logged prediction; per server: memory, load queue, fair-share deviation. Cost per model from a ledger of memory-hours and CPU.

#### Deep dives

1. **Density.** Popularity tiers; affinity routing gives each model a few home servers; eviction by recency and size.
2. **Isolation.** Per-model concurrency limits, per-tenant fair queuing, timeouts, quarantine of slow models.
3. **Safe rollout.** Alias changes within 60 s, shadow and canary with automatic rollback (§66.12).

#### Trade-offs and alternatives

One deployment per model is simplest and isolates best but costs 6.3 times more here; serverless inference scales to zero but adds cold starts of minutes when nodes must be provisioned; GPU models pack on multi-model GPU servers or MIG slices (§66.8).

#### Follow-up questions

1. *Why not one Kubernetes deployment per model?* Redundancy floors cost \$3.9 million a year for 600 vCPU of real work.
2. *How do you avoid every server loading every model?* Rendezvous placement on a few home servers.
3. *How does one slow model not hurt others?* Concurrency caps, deadlines and fair queuing per tenant.
4. *How is an LLM gateway different?* Token-based quotas, KV-aware routing and adapters (Ch 79); same density and isolation principles.

#### What distinguishes levels

- **Mid:** a model server with autoscaling.
- **Senior:** multi-model servers with LRU eviction, canaries.
- **Staff:** quantifies popularity tiers, separates scaling models from scaling servers, shows affinity beats eviction policy, treats artifacts as untrusted code, and prices each tenant choice.

### 92.6.4 Q30. Real-time personalization with streaming features

**Difficulty:** Hard · **Time:** 45 min · **Related:** §68.13 (real-time personalization), §62.10 (freshness), §85.7 (low-latency inference), §31.5 (Kafka partitions)

#### Prompt

"Our shopping app's home feed is ranked once a day. Users browse a category and the feed still shows yesterday's interests. Design personalization that reacts to what the user does in the current session, within seconds."

#### Clarifying questions and assumptions

- Which surfaces? Home feed and "more like this" carousels; search is out of scope.
- How fast is "within seconds"? The next page load after a click should reflect it.
- Scale: assume 40 million daily active users, 25 interaction events and 15 feed requests per user per day, 3 sessions of 10 minutes each, peak-to-average 3.
- Existing stack: a daily batch recommender with two-tower retrieval and a ranker (§68.6–§68.7), and a feature store (Q27).

#### Requirements

Functional: rank about 500 candidates per feed request using long-term user features plus session features (items viewed, categories browsed, add-to-cart in the last minutes); retrieve candidates near the session's interests; log impressions and features for training.

Non-functional: feed p99 ≤ 150 ms server-side with a 40 ms ranking budget; session features reflect an event within 2 s at p99 when the client makes the next request; 99.95% availability, degrading to the daily ranking; online and offline feature values identical for at least 99.5% of logged requests.

#### Estimation

::: example
**Worked example — Events, requests, state and the freshness race.** Traffic uses the users-to-peak formula of §89.5; partitions use §89.11; concurrency uses Little's Law (§4.11).

1. Events: $4 \times 10^7 \times 25 = 10^9$ a day; average 11,574/s; **peak 34,722/s**. At 500 bytes each, 17.4 MB/s into the event log, comfortably served by 64 partitions with room for consumer parallelism.
2. Feed requests: $4 \times 10^7 \times 15 = 6 \times 10^8$ a day; **peak 20,833/s**; at 500 candidates each, **10.4 million scores/s**.
3. Ranker compute at 20 MFLOPs per candidate: $1.04 \times 10^7 \times 2 \times 10^7 = 2.1 \times 10^{14}$ FLOP/s; at an effective $10^{14}$ FLOP/s per GPU (10% of peak, typical for small ranking batches) about 2.1 busy GPUs, a few per region with headroom and redundancy.
4. Concurrent sessions: $4 \times 10^7 \times 3 / 86{,}400 \times 3 = 4{,}167$ starts/s at peak × 600 s = **2.5 million** open sessions; at 4 KB of session state each, 10 GB.
5. The race: if the gap between a click and the next feed request is exponential with mean 8 s and the streaming pipeline's lag is 5 s, then $1 - e^{-5/8} = 46\%$ of next requests arrive before the click is visible. Even a 1 s lag misses $1 - e^{-1/8} = 12\%$.

**Interpretation.** Volume and state are small; scoring is modest. The hard number is the race: a streaming pipeline cannot guarantee the *next* request sees the *last* event. **Engineering implication.** Carry the freshest signals in the request itself (the client sends its last few item IDs) and use the stream for everything older than a few seconds.
:::

#### Data, labels and features

- **Events:** views, clicks, add-to-cart, purchases, dwell time, with event time, session ID and device.
- **Labels:** click and add-to-cart on impressions (seconds to minutes), purchase within 24 hours (delayed). Positives are joined to impressions by impression ID.
- **Features:** long-term user embedding and affinities (daily batch); session features from the stream (category counts in the last 10 minutes with exponential decay, §68.13; last 20 item embeddings); request-time features sent by the client (last 5 item IDs, current category, time of day); item features (price, popularity in the last hour).
- **Skew hazard:** streaming aggregates are hard to reconstruct point-in-time offline. Log the exact feature vector used at each impression and train from the logs ("log and train"), so the training data contain what serving saw (§62.9.4).

#### High-level design

**Figure 92.104 — Session-aware personalization: request-time, streaming and batch features.**

```mermaid
flowchart LR
  APP([Mobile app]) -->|feed request plus<br/>last item IDs| FS[Feed service]
  APP -.->|events| EL[[Event log]]
  EL -.-> SP[Stream processor:<br/>session state]
  SP -.->|upsert| OS[(Online feature<br/>store)]
  FS --> RET[Retrieval: two-tower<br/>plus session ANN]
  RET --> RK[Ranker service]
  OS --> RK
  BF[(Batch user and<br/>item features)] --> OS
  RK --> RR[Re-rank: diversity,<br/>business rules]
  RR --> FS
  FS -.->|impressions with<br/>feature vectors| IL[[Impression log]]
  IL -.-> TR[Training pipeline]
  EL -.-> TR
  TR -.-> MR[(Model registry)]
  MR -.-> RK
```

**Reading the diagram.** The synchronous path (solid) runs from the app through retrieval, ranking and re-ranking; the request carries the client's last few item IDs so the freshest context has no pipeline lag. Events flow asynchronously (dotted) into the event log, where a stream processor keyed by user maintains session state and upserts it into the online store. Batch features are loaded daily. Impressions are logged with the exact feature vectors used, and the training pipeline joins them with later events for labels. Storage boundaries: event and impression logs (durable streams), online store, batch store, registry. Failure points: stream-processor lag (the request-time features still work; session features degrade to older values), online-store timeouts (defaults and the daily ranking), and a model trained on stale feature logic. Scaling: partition the event log and the stream processor by user ID; ranking scales horizontally per request.

#### Model and evaluation

- **Baseline:** the daily ranking plus a rule ("boost items in the last viewed category").
- **Production:** keep two-tower retrieval and add a session retrieval source (ANN on the mean of the last 5 item embeddings); rank with a multi-task model (click, add-to-cart, purchase) whose inputs include a short sequence encoder over the last 20 items (§68.7.4, §68.13).
- **Offline:** AUC and calibration per task, NDCG@10 on logged sessions, sliced by session depth (first request versus later requests), because the value of session features appears only after the first interaction.
- **Online:** A/B test randomized by user, primary metric purchases per user over 14 days; guardrails: latency, diversity, return rate. Watch for a novelty effect in the first week.

#### Serving and monitoring

Budget: retrieval 30 ms, feature fetch 20 ms (hedged), ranking 40 ms, re-ranking 10 ms, slack 50 ms (§60.10). Fallback ladder: full model → model without session features → daily ranking → popular items. Monitor stream lag (event time to state update) at p50 and p99, session-feature null rate, share of requests carrying request-time features, score distribution, CTR by session depth.

#### Deep dives

1. **The freshness race.** Streaming lag of seconds is enough to miss the last click on a fifth to a half of next requests. Request-time features from the client close the gap; the stream supplies the slightly older context; batch supplies the long term. Each layer has its own freshness budget (§62.10).
2. **Event time and session windows.** Late and out-of-order mobile events (offline phones) must be windowed by event time with a watermark; session windows close after inactivity. State is keyed by user, checkpointed, and rebuilt from the log after failure (§29.8).
3. **Training on what serving saw.** Because streaming features are expensive to recompute exactly offline, log the feature vector per impression and train from the logs; use point-in-time recomputation only for backfilling new features, with a parity check.

#### Trade-offs and alternatives

**Table 92.102 — Ways to react to a session, by freshness and cost.**

| Approach | Freshness | Cost and complexity | Choose when |
|---|---|---|---|
| Client-side re-ranking of a cached list | Instant | Low; limited model on device | Simple boosts, offline mode |
| Request-time features from the client | Instant | Low; trusts client input | Last few items, current category |
| Streaming session features | Seconds | Stream processor and state | Counts, decayed affinities, sequences |
| Micro-batch every few minutes | Minutes | Lowest infrastructure | Popularity and trend features |
| Online model updates | Minutes | High; stability risk | Fast-moving catalogs, news |

#### Follow-up questions

1. *The stream processor is down for 10 minutes.* Session features age; the request-time features still personalize; alert on lag, not on errors, and replay from the log on recovery.
2. *Can a malicious client forge request-time features?* It can bias its own feed only; validate IDs and cap their weight, and never use client-sent features for pricing or fraud.
3. *How do you avoid the feed collapsing onto one category after two clicks?* Diversity constraints in re-ranking (MMR, §68.10) and decay in session features.
4. *Why not update the model online?* Session features give most of the responsiveness with a stable model; online learning adds instability and harder rollbacks.
5. *How do you know session features help?* Slice the A/B result by session depth; the gain should rise after the first interaction.

#### What distinguishes levels

- **Mid:** adds streaming features to the existing ranker.
- **Senior:** designs the stream processor with event-time windows, defines the fallback ladder and logs features to avoid skew.
- **Staff:** quantifies the freshness race and moves the freshest signals into the request, assigns a freshness budget per feature layer, and evaluates by session depth so the benefit is measurable.

### 92.6.5 Q31. Billion-scale embedding retrieval

**Difficulty:** Hard · **Time:** 45 min · **Related:** §68.6 (two-tower models), Ch 74 (vector search; capacity §74.14), §81.4 (video recommendations), §81.10 (recommendation platform)

#### Prompt

"Our platform has 2 billion items (short videos and posts). Design the candidate-retrieval stage that returns the 1,000 most relevant items for a user in about 20 milliseconds, at 50,000 requests per second."

#### Clarifying questions and assumptions

- What happens after retrieval? A ranker scores the 1,000 candidates (out of scope, but it sets the recall target).
- How many new items a day? Assume 20 million; new items must be retrievable within 15 minutes.
- Embedding dimension? 256, learned by a two-tower model; assume nodes with 256 GB RAM and 64 cores.
- Filters? Language and safety eligibility, applied at retrieval time.

#### Requirements

Functional: compute a user embedding per request; search the item index for the top 1,000 by inner product with filters; add fresh items continuously; switch to new model versions without downtime.

Non-functional: retrieval p99 ≤ 20 ms; ANN recall@1,000 ≥ 0.90 against exact search with the same embeddings; 99.99% availability with fallback sources; new items searchable within 15 minutes; index rebuilt at least daily.

#### Estimation

::: example
**Worked example — Memory says one node, throughput says seven.** Apply the memory-bound and throughput-bound sizing of §74.14 (the vector form of §89.9–§89.10). Assume $N = 2 \times 10^9$, $d = 256$, 64 GB of usable RAM headroom aside, $u = 0.7$ (179 GB usable per 256 GB node), measured CPU per query $t_\text{cpu} = 4$ ms at the recall target, $\rho = 0.5$.

1. FP32 vectors: $2 \times 10^9 \times 1{,}024 = 2.05$ TB. INT8 with an HNSW graph ($256 + 260 + 8$ bytes): 1.05 TB, six shards per replica.
2. IVF-PQ with 64-byte codes and 8-byte IDs: $2 \times 10^9 \times 72 = 144$ GB: **one node holds a full replica**.
3. With 65,536 inverted lists, each holds about 30,500 items; probing 64 lists scans about 1.95 million codes per query, which is what the 4 ms measures.
4. Throughput: $50{,}000 \times 0.004 / 0.5 = 400$ cores, about **7 nodes** of 64 cores; with N+1, 8 full replicas per region.
5. Fresh items: 20 million a day in an HNSW delta index with FP32 vectors: $2 \times 10^7 \times (1{,}024 + 268) = 25.8$ GB.
6. Re-embedding the corpus after a model change at 50,000 items/s per GPU: $2 \times 10^9 / 5 \times 10^4 = 40{,}000$ GPU-s, **11 GPU-hours**, about \$28.

**Interpretation.** Compression turns a sharded 2 TB problem into a replicated 144 GB one, and replication is far simpler than scatter-gather. Re-embedding is cheap, so model upgrades are limited by index build and validation, not by compute. **Engineering implication.** Choose the compression first (it decides shard versus replicate), then size replicas by throughput, then add a small fresh index for new items.
:::

#### Data, labels and features

- **Training data:** (user, item) positive pairs from engagement (long watch, like, share) over the last 30 days, with event-time splits.
- **Negatives:** in-batch negatives with the logQ correction for popularity (§68.6.1) [Yi et al. 2019], plus sampled random negatives so rare items are pushed away from everything.
- **User tower features:** watch history (IDs and embeddings of the last 50 items), language, country, device, time; **item tower features:** content embedding (video and text encoders), creator, category, age, early engagement rates.
- **Hazard:** item-tower features that change after indexing (engagement counts) make the indexed vector stale; keep slowly changing features in the item tower and fast ones in the ranker.

#### High-level design

**Figure 92.105 — Two-tower retrieval with a main IVF-PQ index and a fresh delta index.**

```mermaid
flowchart LR
  C([Recommendation request]) --> QE[User tower<br/>on GPU or CPU]
  QE --> FAN{Search router}
  FAN --> MAIN[Main index replica<br/>IVF-PQ, 144 GB]
  FAN --> DELTA[Delta index<br/>HNSW, new items]
  MAIN --> MER[Merge, filter,<br/>dedupe top 1,000]
  DELTA --> MER
  MER --> RK([To ranker])
  NEW[[New item events]] -.-> IE[Item tower<br/>embedder]
  IE -.-> DELTA
  TP[Training pipeline] -.-> REG[(Model registry:<br/>paired towers)]
  REG -.-> BUILD[Daily index build<br/>on all items]
  BUILD -.->|blue-green swap| MAIN
  REG -.-> QE
```

**Reading the diagram.** A request computes the user embedding synchronously and searches one replica of the main index and the delta index in parallel; results are merged, filtered and deduplicated before the ranker. New items are embedded asynchronously and inserted into the delta index within minutes. A daily build re-embeds and re-indexes everything, then swaps replicas blue-green. The registry stores the user and item towers as one versioned pair. Failure points: a version mismatch between towers and index (vectors from different spaces give garbage silently), a slow replica (hedge to another), and a failed build (keep serving yesterday's index plus the delta). Scaling: add replicas for throughput; shard only if compression cannot keep a replica on one node.

#### Model and evaluation

- **Baseline:** popularity per country plus item-to-item co-engagement (§68.5.3).
- **Production:** two-tower model with sampled softmax and logQ correction; several retrieval sources merged (two-tower, co-engagement, followed creators, fresh items).
- **Offline:** recall@1,000 of held-out next engagements for the model with exact search, then ANN recall against exact search separately, so model quality and index quality are not confused. Slice by user activity and item age.
- **Online:** A/B on downstream watch time and engagement per user; guardrails on latency and creator diversity.

#### Serving and monitoring

Budget: user tower 5 ms, ANN 8 ms, merge and filter 3 ms, slack 4 ms. Fallbacks: if the user tower fails, use the cached daily user embedding; if the index fails, the co-engagement and popularity sources. Monitor ANN recall on a sampled exact-search shadow (nightly), per-source candidate counts, share of fresh items retrieved, embedding norm distributions (a broken tower shows as a shifted norm), and index build age.

#### Deep dives

1. **Shard or replicate.** Memory sizing decides whether a replica fits one node; throughput decides replicas. Scatter-gather over shards multiplies tail latency (the fan-out rule of §60.10), so compress until replication works.
2. **Version lock between towers and index.** Query and item embeddings are only comparable within one model version. Index builds carry the model version; the router queries an index only with the matching user tower; upgrades are blue-green on both together.
3. **Freshness and filtering.** New items enter a small HNSW delta index within minutes; filters for language and safety use per-list bitmaps or filtered graph search (§74.11) so that restrictive filters do not leave fewer than 1,000 results.

#### Trade-offs and alternatives

HNSW on INT8 vectors gives higher recall per millisecond but needs six shards per replica here; DiskANN keeps compressed codes in RAM and the graph on SSD (§74.10.2); GPU brute force over 2 billion vectors is exact but needs about 2 TB of GPU memory per replica [Johnson et al. 2021]. Generative retrieval and learned-index approaches exist but are harder to update and debug.

#### Follow-up questions

1. *Why not exact search?* At 2 billion × 256 dimensions, one query is 512 GFLOP of inner products; ANN at recall 0.90 costs a few milliseconds of one core.
2. *A new model version doubles offline recall but the A/B is flat.* The ranker was trained on the old candidate distribution; retrain or fine-tune the ranker on the new candidates before testing.
3. *How do you handle deleted or banned items?* Tombstones checked at merge time, then removal at the next build.
4. *Popular items dominate retrieval.* LogQ correction in training, per-source quotas at merge, and diversity in re-ranking.
5. *How do you detect index degradation?* Nightly shadow exact search on sampled queries; alert when ANN recall drops below target.

#### What distinguishes levels

- **Mid:** two-tower model plus an off-the-shelf ANN index.
- **Senior:** sizes memory and throughput, adds negatives with popularity correction, separates model recall from ANN recall.
- **Staff:** chooses compression to avoid sharding, versions towers and index as a pair with blue-green swaps, designs freshness through a delta index, and connects retrieval changes to ranker retraining.

### 92.6.6 Q32. Enterprise RAG assistant

**Difficulty:** Hard · **Time:** 45 min · **Related:** §86.4 (full case study), Ch 75 (RAG architecture; permissions §75.14), §78.9–§78.10 (groundedness, RAG evaluation)

#### Prompt

"Design an assistant that a company's employees use to ask questions across the company's documents (Drive, SharePoint, Confluence, tickets). Answers must cite sources and must only use documents the asking employee may open."

#### Clarifying questions and assumptions

Single company or a SaaS vendor serving many? Which sources and how do their permissions change? Is a revocation lag acceptable, and how long? Assume the §86.4 vendor: 2,000 tenants, 4 million seats, 30% daily active, 5 questions per active user per day.

#### Requirements

Functional: streamed answers with inline citations; connectors with initial crawl and incremental sync of content, deletions and permissions; search fallback when no grounded answer exists. Non-functional: permission fidelity within a stated sync lag (for example, revocations effective within 15 minutes at p99, verified again at query time); TTFT p95 ≤ 2 s; tenant isolation; no training on tenant data.

#### Estimation

::: example
**Worked example — Queries, corpus and cost per seat (numbers of §86.4.4).** Peak uses §89.5; the per-request cost uses the formula of §88.8; index memory uses §74.14.

1. Questions: $4 \times 10^6 \times 0.30 \times 5 = 6$ million a day; 69.4/s average, **208/s at peak**.
2. Routing 70% to a small model (\$0.00111 per answer) and 30% to a frontier model (\$0.0167): **\$0.00579 per answer**, \$34,700 a day, \$0.26 per seat per month.
3. Corpus: $5 \times 10^8$ documents, $10^{12}$ tokens, $3 \times 10^9$ chunks; index at 1,352 bytes per chunk (INT8 vector, graph links, metadata with ACL principals): **4.06 TB** per replica.
4. Initial embedding: 1,712 GPU-hours, about \$4,280; daily churn 8.6 GPU-hours.

**Interpretation.** Retrieved context is two-thirds of each prompt, so $k$ and chunk size drive the bill; embedding is cheap and the onboarding bottleneck is the source systems' rate limits. **Engineering implication.** Route by difficulty, keep $k$ small with a reranker, and schedule crawls under each source's API limits.
:::

#### Data, labels and features

Chunks with metadata: tenant, source, document ID, ACL principals (users and *unexpanded* group IDs), freshness timestamps. A separate group-membership mirror per tenant. Labels for retrieval come from graded judgments, citation clicks and calibrated LLM judges (§75.13); generation is judged on groundedness and correctness (§78.9).

#### High-level design

**Figure 92.106 — Permission-aware RAG: the index stores principals, the query expands the user.**

```mermaid
flowchart LR
  SRC{{Source systems}} -.->|crawl, webhooks| CON[Connectors]
  CON -.-> ING[Chunk, embed,<br/>attach ACL principals]
  ING -.-> IDX[(Per-tenant hybrid<br/>index)]
  CON -.->|group changes| GM[(Group-membership<br/>mirror)]
  U([Employee]) -->|question| ORCH[Orchestrator]
  ORCH --> GM
  ORCH -->|query plus user principals| IDX
  IDX --> RR[Reranker]
  RR --> LIVE[Live permission<br/>check on top chunks]
  LIVE --> GEN[LLM via gateway<br/>with routing]
  GEN -->|streamed answer<br/>with citations| U
```

**Reading the diagram.** Ingestion is asynchronous: connectors crawl content and permissions, chunks carry their ACL principals, and group changes update only the mirror. At query time the orchestrator expands the user into principals, retrieves with a permission filter inside the index, reranks, re-checks the top chunks against the source (the live check) and only then builds the prompt. Failure points: a missed revocation webhook (reconciliation sweeps bound the window; the live check catches the rest), cross-tenant leakage (per-tenant indexes and keys), and injection in retrieved documents. Scaling: index replicas by memory per tenant group; the LLM tier through the gateway.

#### Model and evaluation

Baseline: keyword search with snippets. Production: hybrid lexical and dense retrieval, cross-encoder reranker, routed generation with citation constraints. Offline: per-tenant synthetic and consented evaluation sets measuring retrieval recall, citation precision, groundedness and refusal on unanswerable questions; online: citation clicks, thumbs, reformulation rate.

#### Serving and monitoring

Monitor per tenant and source: freshness lag, revocation lag p99, reconciliation mismatches, empty-retrieval rate, groundedness on sampled answers, cost per answer. Fallback: ranked document list when generation fails or evidence is insufficient.

#### Deep dives

1. **Permissions as index data.** Filter inside retrieval; store group IDs, not expanded members, so renaming a 50,000-member group is one mirror update.
2. **Revocation window.** Per-source lag metrics, reconciliation, and a live check bounded to the top 10–20 chunks.
3. **Evaluation without reading customer data.** Synthetic questions generated inside the tenant boundary, judged automatically, with aggregates reported out.

#### Trade-offs and alternatives

Filtering after generation leaks paraphrases; a per-user index is exact but unaffordable; fine-tuning on tenant documents cannot enforce permissions and must be avoided for knowledge (§76.14).

#### Follow-up questions

1. *Why not filter the answer afterwards?* The model may paraphrase a forbidden document; enforcement must precede the prompt.
2. *How do you know a revocation has propagated?* Source-event-to-mirror lag per source, plus reconciliation and the live check.
3. *A tenant asks for proof you never trained on their data.* Contract, configuration (no retention at model providers) and audit logs.
4. *Answers are confidently wrong on old policies.* Freshness-aware ranking and showing document dates with citations.

#### What distinguishes levels

- **Mid:** chunk, embed, retrieve, generate with citations.
- **Senior:** filters inside retrieval and keys caches by permission, evaluates groundedness.
- **Staff:** quantifies the revocation window by source, explains unexpanded principals, bounds the live check's cost and designs per-tenant evaluation that never exports customer text.

### 92.6.7 Q33. LLM customer-support agent

**Difficulty:** Hard · **Time:** 45 min · **Related:** §86.7 (full case study), Ch 77 (agents: tools §77.5, state §77.10, human-in-the-loop §77.12, cost §77.17), Ch 78 (evaluation)

#### Prompt

"An e-commerce group with eight brands in 30 markets wants an AI agent that answers customers and, within policy, issues refunds, cancels orders and changes addresses. Design it."

#### Clarifying questions and assumptions

Which actions are in scope first? What does a human-handled contact cost? What is the refund limit without approval? Assume §86.7: 100,000 contacts a day (70% chat), \$4.50 per human contact, peak-to-average 3, conversations that can last days across channels.

#### Requirements

Functional: answer and act through tools; hand off to humans with a summary; agent-assist mode for human agents; per-brand, per-market policies. Non-functional: no duplicate or unauthorized money movements; first response p95 ≤ 3 s; wrong-action rate below 0.5% on QA samples; every action auditable; customers can always reach a human.

#### Estimation

::: example
**Worked example — Load is small; the business case is not (numbers of §86.7.4).** Concurrency uses Little's Law (§4.11); agent cost uses §77.17.1; the blended-cost formula is §86.7.4's.

1. Peak 3.47 contacts/s; concurrent chats $3.47 \times 0.7 \times 540$ s $= 1{,}313$; model calls 1.06 million a day, **36.7/s at peak**.
2. Agent-side cost per chat contact: tokens \$0.176, auxiliary calls \$0.0005, orchestration \$0.04, approvals \$0.06, wrong actions \$0.10: $C_a = \$0.377$.
3. With 65% of contacts covered and 30% of those escalated ($k = 0.9$): covered contact $0.377 + 0.30 \times 0.9 \times 4.50 = \$1.59$; blended $0.65 \times 1.59 + 0.35 \times 4.50 = \$2.61$ against \$4.50.

**Interpretation.** Tokens are under half of the agent's own cost, and escalations are three-quarters of a covered contact's cost. **Engineering implication.** Invest in resolution quality and safe coverage; optimize tokens last.
:::

#### Data, labels and features

Conversation history, order and customer facts from tools, policies as code per brand and market. Labels: resolution without repeat contact within 7 days (delayed), refund reversals and chargebacks (weeks), QA reviews of sampled conversations, human edits in assist mode.

#### High-level design

**Figure 92.107 — Support agent: the model proposes, the policy engine decides.**

```mermaid
flowchart LR
  CU([Customer chat or email]) --> CH[Channel service]
  CH --> WF[Durable workflow<br/>per conversation]
  WF --> LLM[LLM policy via gateway]
  LLM -->|proposed tool call| PE{Policy engine<br/>brand, market, limits}
  PE -->|allowed| TOOLS[Order, refund,<br/>address tools]
  PE -->|needs approval| HQ[[Human approval queue]]
  PE -->|deny or unsure| HO[Handoff with summary]
  TOOLS -->|idempotency key| OMS{{Commerce systems}}
  WF -.-> ST[(Conversation and<br/>action state)]
  WF -.->|traces| EVAL[QA sampling and<br/>offline replay]
```

**Reading the diagram.** Each conversation is a durable workflow (§77.8.2) that survives restarts and multi-day gaps. The LLM proposes replies and tool calls; a deterministic policy engine decides whether to execute, queue for human approval or hand off. Tools call commerce systems with idempotency keys persisted before the call. State and traces are written asynchronously for QA and replay. Failure points: a tool timeout with unknown outcome (reconcile before retrying), a promise in text without a succeeded action (output guardrail), injection through customer text or retrieved policy pages. Scaling: workflows scale horizontally; the gateway quota of about 37 calls/s is modest.

#### Model and evaluation

Baseline: intent classifier plus scripted flows. Production: LLM policy with tools and a small model for intent and risk. Offline: replay suites per intent with end-state checks (was the refund the right amount, exactly once?) and pass^k for reliability (§78.6.4); online: rollout by intent, resolution and repeat-contact rate, escalation rate, wrong-action rate from QA.

#### Serving and monitoring

Per intent, brand and market: resolution, repeat contact, handoff and approval rates, refund amounts per customer, guardrail triggers, cost per contact. Fallback: handoff to humans with summary; disable an intent's autonomy by configuration.

#### Deep dives

1. **Proposal versus decision.** The model never moves money directly; the policy engine and tool layer do.
2. **Idempotency and unknown outcomes.** Keys derived from the logical action; reconciliation before retry.
3. **Rollout by intent.** Assist mode first as evidence, then read-only intents, then low-limit refunds in one market.

#### Trade-offs and alternatives

Scripted flows are safe but brittle; full autonomy maximizes coverage but concentrates risk; multi-agent splits are unnecessary for short sequential tasks (§77.9.1).

#### Follow-up questions

1. *How do you prevent duplicate refunds?* Idempotency key persisted before the call; reconcile unknown states.
2. *The model says "your refund is approved" before the tool runs.* Output guardrail blocks promises without an action record.
3. *Why not measure deflection?* A customer who gives up and calls is a failure; measure resolution without repeat contact.
4. *Refund abuse rises after launch.* Per-customer refund velocity limits, risk scores in the policy engine and human review above thresholds.

#### What distinguishes levels

- **Mid:** an LLM with tools and a handoff.
- **Senior:** guardrails, approvals, durable state, intent-based evaluation.
- **Staff:** separates proposal from decision, quantifies cost per resolution with escalation as the dominant term, rolls out by intent with assist mode as evidence, and anticipates adversarial adaptation.

### 92.6.8 Q34. Speech recognition

**Difficulty:** Hard · **Time:** 45 min · **Related:** §84.6 (full case study), §9.9 (long-lived connections)

#### Prompt

"Design the speech recognition behind a phone assistant and dictation keyboard. Words should appear while the user speaks, and a contact name like 'Maya Chen' must be recognized."

#### Clarifying questions and assumptions

On-device, cloud or both? Languages? Privacy constraints on audio? Assume §84.6: 50 million daily users, 10 utterances of 4 s each per day, peak-to-average 3, 60% of audio recognized on device.

#### Requirements

Functional: streaming partial results every 100–200 ms; end-pointing; contextual biasing with per-request phrases; formatting; opt-in audio donation. Non-functional: first partial ≤ 300 ms (p90); final ≤ 500 ms after speech ends (p90); WER ≤ 6% on the voice-search set; contact-name recall ≥ 95%; every accent slice within 1.5× of overall WER; audio not stored without opt-in.

#### Estimation

::: example
**Worked example — Streams, not requests (numbers of §84.6.4).** Concurrency is Little's Law (§4.11); per-GPU capacity uses §84.6's real-time-factor formula.

1. Audio: $5 \times 10^8$ utterances × 4 s $= 2 \times 10^9$ s a day; average concurrent streams 23,148; peak 69,444; **27,778 in the cloud**.
2. A 160 ms chunk advanced for 120 streams in 32 ms: RTF 0.2, five steps per chunk period, 600 streams per GPU.
3. GPUs at 70% utilization: $27{,}778 / (600 \times 0.7) = 66$.
4. Final latency with a 600 ms silence timeout: $600 + 32 + 50 + 40 = 722$ ms, failing the target; with a learned end-of-query detector at 300 ms: 422 ms.

**Interpretation.** Speech is a concurrency problem, and end-pointing, not the model, dominates final latency. **Engineering implication.** Size gateways for long-lived streams, spend effort on the end-pointer, and move recognition on device for privacy and cost.
:::

#### Data, labels and features

Log-mel frames every 10 ms; transcribed audio from vendors and opted-in donations; pseudo-labels from large offline teacher models; per-request bias lists (contacts, app names) that stay on the device or in memory.

#### High-level design

**Figure 92.108 — Streaming recognition on device and in the cloud.**

```mermaid
flowchart LR
  MIC([Phone microphone]) --> DEC{Model installed<br/>and device capable?}
  DEC -->|yes| ODR[On-device<br/>streaming transducer]
  DEC -->|no| GW[Streaming gateway<br/>WebSocket or gRPC]
  GW -->|sticky stream| WK[GPU recognition<br/>workers, batched]
  WK --> EP[End-pointer and<br/>second pass]
  ODR --> FMT[Formatting]
  EP --> FMT
  FMT --> APP([Assistant or<br/>text field])
  WK -.->|opt-in audio only| DON[(Donation store)]
```

**Reading the diagram.** Each utterance runs on device when possible; otherwise audio streams over a long-lived connection to a GPU worker that batches many streams per step. Partials flow back continuously; the end-pointer finalizes, an optional second pass rescores, and formatting converts spoken to written forms. Only opted-in audio reaches the donation store, asynchronously. Failure points: a worker failure mid-stream (the client reconnects and resends the buffered audio), falling behind real time under load (admission control), and early cutoffs. Scaling: by concurrent streams per GPU; on-device share is the largest lever.

#### Model and evaluation

Baseline: a hosted batch recognizer on full utterances (fails partials). Production: streaming encoder–transducer with chunked attention, biasing via a prefix tree of phrases, learned end-of-query detection [Graves 2012; He et al. 2019]. Offline: WER after text normalization, entity accuracy for names, early-cutoff rate, slices by accent and device. Online: retry, edit and cancellation rates.

#### Serving and monitoring

Per worker: RTF and stream lag; per locale and device: first-partial and final latency, early-cutoff rate, bias false-trigger rate. Fallback: degrade to final-only results under overload rather than drop streams.

#### Deep dives

1. **Latency decomposition.** Chunk size sets partial latency and GPU efficiency; the end-pointer dominates final latency.
2. **Contextual biasing.** Contact names compiled into a biasing structure; evaluate recall and false triggers.
3. **Improvement without collecting audio.** Opt-in donations, teacher pseudo-labels, federated learning (Q39).

#### Trade-offs and alternatives

A large attention-based model on 30-second windows is accurate for batch transcription but not streaming; on-device models save cost and network delay but cost engineering per device class.

#### Follow-up questions

1. *Users say it cuts them off.* Plot early-cutoff rate against end-point latency by slice; slower speakers need a later decision.
2. *How do you recognize a name the model never saw?* Biasing from the device's contacts.
3. *How do you size the fleet?* Concurrent streams divided by streams per GPU at target utilization.
4. *Why not a single global model?* Per-language models or a multilingual model with language ID; measure per locale.

#### What distinguishes levels

- **Mid:** a streaming model and WER.
- **Senior:** sizes by concurrent streams, adds biasing and slices.
- **Staff:** decomposes final latency to show the end-pointer dominates, normalizes text before WER, treats on-device as a privacy and cost lever, and designs improvement around consent.

### 92.6.9 Q35. Machine translation

**Difficulty:** Hard · **Time:** 45 min · **Related:** §84.7 (full case study), §73.6 (continuous batching)

#### Prompt

"Design translation for a communications platform: chat messages and documents in 200 languages, and live captions in each listener's language during meetings. Enterprise customers have glossaries."

#### Clarifying questions and assumptions

Text, speech or both? Acceptable caption lag? How are glossaries enforced? Assume §84.7: 500 million text segments a day (25 source and 28 target tokens), a 20% segment-cache hit rate, peak-to-average 3, and 1 million meeting-hours a day with live translation.

#### Requirements

Functional: text and document translation with optional glossary and formality; live speech captions; tenant glossaries and do-not-translate lists; quality feedback; published quality tier per direction. Non-functional: 25-token segment p95 ≤ 400 ms; captions with average lagging ≤ 3 s; no COMET regression on the 40 high-volume directions; glossary term accuracy ≥ 98%; content not retained without opt-in.

#### Estimation

::: example
**Worked example — Output tokens, GPUs and the simultaneous policy (numbers of §84.7.4).** Peak uses §89.5; GPU throughput per second is the measured-rate form of §89.16.

1. Text output tokens: $5 \times 10^8 \times 0.8 \times 28 = 1.12 \times 10^{10}$ a day; **388,889/s at peak**; at 5,000 tokens/s per GPU and 60% utilization, **130 GPUs**.
2. Live speech: 83,333 concurrent meetings at peak; ASR $83{,}333 / 420 = 198$ GPUs.
3. MT for speech: $83{,}333 \times 1.5 \times 3.5 = 437{,}500$ tokens/s, 146 GPUs if each word is translated once; with re-translation on every partial (about 3×), 438 GPUs.

**Interpretation.** Live speech is the larger workload, and the latency policy changes its MT cost threefold. **Engineering implication.** Choose the simultaneous policy with both lag and GPU numbers in view, and cache and distill the highest-volume text directions.
:::

#### Data, labels and features

Human reference translations, mined and back-translated parallel data, post-edits from tenants who opt in; tenant glossaries as versioned data. Quality labels: COMET on frozen test sets, human MQM for top directions.

#### High-level design

**Figure 92.109 — Text and live translation with a direction router.**

```mermaid
flowchart LR
  C([Client]) -->|segments, target| API[Translate API]
  API --> CACHE[(Segment cache)]
  API --> GLO[Glossary masking<br/>and post-check]
  GLO --> DR{Direction router}
  DR -->|top directions| BI[Distilled bilingual<br/>models]
  DR -->|long tail| ML[Multilingual model]
  DR -->|low resource| PV[Pivot via English]
  MTG([Meeting audio]) --> ASR[Streaming ASR]
  ASR --> SIM[Simultaneous policy<br/>wait-k per direction]
  SIM --> DR
  BI --> OUT([Translations and captions])
  ML --> OUT
  PV --> OUT
```

**Reading the diagram.** Text requests check the segment cache, mask glossary terms, and go to a model chosen per direction by volume and measured quality. Live meetings run streaming ASR, then a simultaneous policy that decides when to emit, then the same router. Failure points: hallucinated or off-target output (language-ID check on output), caption flicker from re-translation, glossary violations (post-check). Scaling: GPUs by output tokens per second; distilled models for the highest-volume directions.

#### Model and evaluation

Baseline: a hosted general model for all directions. Production: a 1.3B multilingual encoder–decoder for coverage, distilled bilingual models for the top directions, pivot where it measures better [Johnson et al. 2017]. Offline: COMET per direction with no-regression gates, MQM for the top 10, glossary accuracy; online: flag rate and caption-off rate.

#### Serving and monitoring

Per direction: reference-free quality estimation on sampled traffic, off-target rate, flag rate; for speech: average lagging and flicker; per tenant: glossary accuracy. Fallback: multilingual model if a bilingual one fails; captions in the source language if MT fails.

#### Deep dives

1. **Simultaneous translation.** Wait-$k$ per direction, larger $k$ for verb-final sources; re-translation trades flicker and 3× compute for quality.
2. **Many-language serving.** 39,800 directed pairs cannot each have a model; route by volume and quality.
3. **Control.** Placeholder masking plus a post-check for do-not-translate terms.

#### Trade-offs and alternatives

End-to-end speech translation removes the ASR stage but loses transcripts and glossary control; a cascade is easier to debug and evaluate. BLEU is cheap but weakly correlated with quality; learned metrics plus human MQM gate releases.

#### Follow-up questions

1. *A verb-final source language?* Larger $k$ or an adaptive policy, and a published higher lag target.
2. *One model or 39,800?* Multilingual for coverage, distilled pairs for volume.
3. *How do you know a new model is better?* COMET on every routed direction, MQM on the top ones, then an online test.
4. *A brand name gets translated.* Masking plus post-check; add it to the tenant's glossary tests.

#### What distinguishes levels

- **Mid:** a multilingual model with BLEU.
- **Senior:** cascade for speech, glossary handling, COMET.
- **Staff:** quantifies lag with average lagging and sets $k$ per direction, shows the simultaneous policy is a capacity decision, and routes directions by volume and measured quality.

### 92.6.10 Q36. Perception data engine for autonomous driving

**Difficulty:** Hard · **Time:** 45 min · **Related:** §63.5 (labeling pipelines), §63.9 (active learning), §63.14.4 (hybrid labeling), §80.6 (storage for training), Ch 74 (vector search for scene retrieval)

#### Prompt

"A fleet of test vehicles records camera and lidar data every day. Our perception models fail on rare situations. Design the data engine that finds the right data, labels it and turns it into better models."

#### Clarifying questions and assumptions

- Scope: offline data engine (collection, mining, labeling, training, evaluation, release to vehicles), not the on-vehicle planning stack.
- Fleet: assume 500 vehicles driving 8 hours a day, each with 8 cameras (H.265 at 8 Mbit/s each) and one lidar (5 MB/s compressed).
- Uploads: at the depot over 10 Gb/s links; small trigger summaries over cellular.
- Labels: 3D boxes, tracks and lane geometry on keyframes at 2 Hz; assume \$3.00 per keyframe for full human labeling (illustrative; measure with vendors).

#### Requirements

Functional: ingest drives; on-vehicle and offline triggers that flag interesting moments; search over the fleet's data by metadata and by example (scene embeddings); select and label data; train and evaluate multi-task perception models; release models to vehicles in shadow mode first.

Non-functional: a new failure class goes from first report to a labeled training set within one week; every release passes scenario regression suites with no regression on safety-critical classes (pedestrians, cyclists) at any distance bin; full lineage from model to data and labels; raw data retained by policy (for example, 90 days hot, triggered snippets for years).

#### Estimation

::: example
**Worked example — Sensor volume, upload and labeling budget.** Storage uses §89.6; bandwidth uses §89.7; labeling cost uses the effort and hybrid-pipeline formulas of §63.5.2 and §63.14.4.

1. Per vehicle: cameras $8 \times 8$ Mbit/s $= 8$ MB/s plus lidar 5 MB/s $= 13$ MB/s; 8 hours is **374 GB a day**.
2. Fleet: $500 \times 374$ GB $= 187$ TB a day, **68 PB a year** if everything were kept.
3. Depot upload at 10 Gb/s (1.25 GB/s): $374 / 1.25 = 300$ s per vehicle, so the depot network, not cellular, carries raw data.
4. Selection: mining 1% of driving time gives $500 \times 8 \times 0.01 = 40$ hours a day, $40 \times 3{,}600 \times 2 = 288{,}000$ keyframes.
5. Fully human labeling: $288{,}000 \times \$3.00 = \$864{,}000$ a day.
6. Hybrid: an offline auto-labeler (large non-causal models that see past and future frames) labels everything at about 1 GPU-s per keyframe (80 GPU-hours a day); humans correct the 15% flagged as uncertain at full price and spot-check the rest at \$0.30: $288{,}000 \times (0.15 \times 3.00 + 0.85 \times 0.30) = \$203{,}040$, **23.5%** of the human-only cost.

**Interpretation.** Storage and labeling, not training compute, are the constraints, and both are governed by *selection*. **Engineering implication.** Keep raw data short-lived, keep triggered snippets long-lived, and make the auto-labeler plus targeted human review the default labeling path.
:::

#### Data, labels and features

- **Sources:** raw sensor logs, vehicle state (speed, braking, steering), disengagements and safety-driver annotations, map data.
- **Triggers:** hard braking, disengagement, disagreement between the shipped model and a shadow model, low detection confidence, tracker identity switches, and class-specific detectors for rare objects (strollers, animals, construction).
- **Labels:** 3D boxes and tracks, semantic attributes (occlusion, moving), lane geometry; quality measured by inter-annotator agreement and audit sampling (§63.6).
- **Search features:** per-scene embeddings from a vision encoder, indexed for "find more like this" queries (Ch 74), plus metadata (weather, time, city, speed).

#### High-level design

**Figure 92.110 — The perception data engine loop.**

```mermaid
flowchart LR
  V([Fleet vehicles]) -.->|depot upload| RAW[(Raw drive store<br/>90 days)]
  V -.->|trigger summaries| TRG[Trigger service]
  RAW --> IDX[Scene embedding<br/>and metadata index]
  TRG --> MINE[Mining: queries,<br/>similarity, uncertainty]
  IDX --> MINE
  MINE --> SNIP[(Curated snippets<br/>long-term)]
  SNIP --> AUTO[Offline auto-labeler]
  AUTO --> HUM[Human review of<br/>uncertain frames]
  HUM --> DS[(Versioned datasets)]
  DS --> TRAIN[Training on<br/>GPU cluster]
  TRAIN --> EVAL{Scenario regression<br/>and slice gates}
  EVAL -->|pass| SHADOW[Shadow deploy<br/>on vehicles]
  SHADOW -.->|disagreements| TRG
```

**Reading the diagram.** Raw drives arrive asynchronously at depots; trigger summaries arrive over cellular. A scene index (embeddings plus metadata) lets engineers and automated miners select snippets by query, similarity to a known failure, or model uncertainty. Snippets move to long-term storage, are auto-labeled, and uncertain frames go to human review; labeled data become versioned datasets. Training reads datasets; a release gate runs scenario suites and slice metrics; passing models run in shadow mode on vehicles, whose disagreements become new triggers, closing the loop. Storage boundaries: raw store (short retention), snippet store, dataset versions. Failure points: auto-labeler errors becoming training truth (human audit rates per class), triggers that flood the pipeline (per-trigger quotas), and dataset drift between training and evaluation versions. Scaling: storage by retention policy, labeling by selection rate, training by the GPU cluster (Ch 80).

#### Model and evaluation

- **Baseline:** train on uniformly sampled frames with human labels.
- **Production:** multi-task perception network (detection, tracking, lanes) trained on mined data; active learning by uncertainty and diversity (core-set) selection [Settles 2009; Sener and Savarese 2018].
- **Offline:** mAP and recall per class by distance bin, false negatives on safety-critical classes, tracking metrics; **scenario suites** (curated sets for each known failure) act as unit tests that must not regress.
- **Online:** shadow mode measures disagreement rate with the shipped model and the human-reviewed outcome of disagreements; no A/B test on public roads without the safety process.

#### Serving and monitoring

On-vehicle inference is out of scope but sets constraints: the model must meet its latency budget on vehicle compute after quantization (Ch 67), so evaluation runs on the compiled, quantized model. The engine monitors trigger rates by type, labeling throughput and backlog age, auditor disagreement with the auto-labeler per class, dataset growth per failure class, and time from report to labeled set.

#### Deep dives

1. **Selection is the product.** Uniform sampling labels millions of boring highway frames; triggers, similarity search and uncertainty concentrate labels on rare cases. Per-trigger quotas keep one noisy trigger from consuming the budget.
2. **Auto-labeling economics.** An offline labeler can be far larger than the vehicle model and can use future frames, so its labels are better than real-time predictions; humans correct the uncertain fraction. The audit rate per class is the safety valve.
3. **Regression gates as scenario tests.** Every resolved failure becomes a permanent scenario suite; a release cannot regress any of them, and aggregate mAP cannot hide a pedestrian-recall loss at 60 m.

#### Trade-offs and alternatives

Labeling everything is simpler but unaffordable; simulation and synthetic data cover rare events cheaply but have a domain gap (§63.12); self-supervised pretraining on unlabeled fleet video reduces label needs but still needs labeled evaluation sets.

#### Follow-up questions

1. *How do you find more examples of a rare failure?* Embed the failing scene and run similarity search over the scene index, then filter by metadata.
2. *The auto-labeler is wrong on a new object class.* Route that class to full human labeling until audit agreement recovers; retrain the auto-labeler on corrected labels.
3. *How long do you keep raw data?* Weeks to months by policy; triggered snippets and evaluation sets for years, with privacy controls (faces and plates blurred).
4. *How do you know the loop works?* Track per failure class: examples labeled, metric on its scenario suite and field disagreement rate over releases.

#### What distinguishes levels

- **Mid:** collect, label, train, evaluate on a test set.
- **Senior:** triggers, active learning, scenario regression suites, shadow mode.
- **Staff:** quantifies storage and labeling to show selection governs both, designs auto-labeling with per-class audit rates, and makes "report to labeled set in a week" a measured SLO.

### 92.6.11 Q37. Experimentation platform

**Difficulty:** Hard · **Time:** 45 min · **Related:** §57.14 (A/B statistics; sample size §57.14.2), §66.12 (shadow and canary), §68.14 (interleaving, holdouts) [Kohavi et al. 2020]

#### Prompt

"Hundreds of teams want to A/B test ranking models, UI changes and pricing at the same time. Design the experimentation platform."

#### Clarifying questions and assumptions

- Scale: assume 100 million daily active users, 1,000 concurrent experiments, 50 exposure events per user per day.
- Units: users by default; sessions, devices or markets for special cases.
- Who decides launches? Teams, using the platform's scorecard and guardrails.

#### Requirements

Functional: define experiments (unit, variants, allocation, metrics, duration); deterministic assignment with layers so independent experiments overlap; exposure logging; daily scorecards with confidence intervals; guardrail metrics and automatic alerts; sample-ratio-mismatch detection; holdouts.

Non-functional: assignment adds < 1 ms (no network call on the request path); scorecards by 09:00 daily; exposure loss < 0.1%; reproducible analyses from versioned metric definitions.

#### Estimation

::: example
**Worked example — How many users, and what does a scorecard cost?** Sample size uses the per-arm formula of §57.14.2 with $z_{0.975} = 1.96$ and $z_{0.80} = 0.84$; event volume uses §89.5–§89.6.

1. Detecting a 1% relative lift on a 5% conversion rate ($\delta = 0.0005$): $n = 2\,(1.96 + 0.84)^2 \times 0.05 \times 0.95 / 0.0005^2 \approx$ **2.98 million users per arm**.
2. With variance reduction using pre-experiment data (CUPED) and a correlation $\rho = 0.5$, variance falls by $1 - \rho^2 = 0.75$: about 2.24 million per arm [Deng et al. 2013].
3. Exposures: $10^8 \times 50 = 5 \times 10^9$ a day; average 57,870/s; peak 115,741/s at 2×; at 200 bytes, **1 TB a day**.
4. Sample-ratio check: a 50/50 test with 502,000 versus 498,000 users gives $\chi^2 = 16.0$, $p = 6 \times 10^{-5}$: flag it. 501,000 versus 499,000 gives $\chi^2 = 4.0$, $p = 0.046$: not alarming at the usual $p < 0.001$ threshold.

**Interpretation.** Small lifts need millions of users per arm, so traffic is the scarce resource and layering (overlapping experiments) is essential; variance reduction is worth a quarter of the traffic. **Engineering implication.** Compute power before launch, reserve traffic per layer, and treat SRM as a hard stop because it signals a broken assignment or logging path.
:::

#### Data, labels and features

Assignment records (unit, experiment, variant, layer, timestamp), exposure events from clients and services, metric events (orders, sessions, latency, errors), pre-experiment covariates for CUPED, metric definitions as versioned code. The "labels" are the metrics; their delays (purchases within 7 days, churn within 28) set test durations.

#### High-level design

**Figure 92.111 — Experimentation platform: deterministic assignment, logged exposure, batch analysis.**

```mermaid
flowchart LR
  UI([Experiment owner]) --> CFG[Config service:<br/>layers, allocation]
  CFG -.->|push config| SDK[Assignment SDK<br/>in services and apps]
  SDK -->|hash unit and layer| VAR[Variant in-process]
  SDK -.->|exposure events| EX[[Exposure log]]
  APPEV[[Metric events]] -.-> LAKE[(Data lake)]
  EX -.-> LAKE
  LAKE --> JOB[Daily metric jobs<br/>join, aggregate]
  JOB --> STATS[Stats engine:<br/>CUPED, intervals, SRM]
  STATS --> SC[(Scorecards)]
  SC --> UI
  STATS -.->|guardrail breach| ALERT[Alerts and<br/>auto-stop]
```

**Reading the diagram.** Configuration is pushed asynchronously to SDKs embedded in services and apps; assignment is a local hash of the unit ID, layer salt and allocation, so the request path never waits on the network. Exposures and metric events flow into the lake; daily jobs join them by unit, compute per-unit metrics and pass them to the statistics engine, which writes scorecards and raises alerts. Failure points: stale config on clients (versioned configs logged with exposures), lost exposures (SRM detects it), and metric definitions changing mid-test (versioned definitions). Scaling: assignment scales with services; analysis scales with exposures and metrics per day.

#### Model and evaluation

The platform's "model" is statistical: difference in means with delta-method variance for ratio metrics, CUPED adjustment, and either a fixed horizon or a sequential test that allows peeking without inflating false positives. Validate the platform itself with A/A tests: across many A/A experiments, about 5% should be significant at $p < 0.05$ and SRM should be rare. For ML rankers add interleaving as a fast, sensitive pre-test (§68.14.2) and long-term holdouts for cumulative effects [Hohnhold et al. 2015].

#### Serving and monitoring

Monitor assignment latency, config propagation age, exposure loss by platform, SRM rate across experiments, A/A false-positive rate, scorecard job completion time, and the number of experiments per layer against traffic capacity.

#### Deep dives

1. **Layers and overlap.** Experiments in different layers use independent hashes and overlap freely; experiments that interact (two rankers on one surface) share a layer and split traffic [Tang et al. 2010].
2. **Trustworthiness checks.** SRM, A/A tests, novelty and primacy effects (plot lift by day), and guardrails (latency, errors, revenue) evaluated with the same rigor as the primary metric.
3. **Interference.** When treatment affects control (marketplaces, social graphs), user randomization is biased; randomize by market, cluster or time (switchback, Q40).

#### Trade-offs and alternatives

**Table 92.103 — Choosing the randomization unit.**

| Unit | Use when | Cost |
|---|---|---|
| User | Most product and ranking changes | Needs a stable ID; logged-out users vary |
| Session or request | Short-lived effects, no learning across visits | Inconsistent experience; carryover |
| Device | Logged-out apps | Users with several devices see both |
| Cluster (graph community) | Social or network effects | Fewer units, wider intervals |
| Market or time slot (switchback) | Two-sided marketplaces, pricing | Few units; carryover between slots |

#### Follow-up questions

1. *A team peeks daily and stops when $p < 0.05$.* False-positive rate inflates; use sequential tests or a fixed horizon.
2. *The scorecard shows SRM.* Stop reading results; find the assignment or logging bug first.
3. *Twenty metrics, one is significant.* Pre-register the primary metric; correct or treat others as exploratory.
4. *Offline AUC improved, online flat.* The offline metric does not track the business metric, or the ranker is miscalibrated in the new candidate distribution; trust the online test.

#### What distinguishes levels

- **Mid:** random split, t-test, dashboards.
- **Senior:** power analysis, deterministic hashing, guardrails, SRM.
- **Staff:** layers for overlapping experiments, variance reduction quantified, trustworthiness checks as platform features, and the right unit under interference.

### 92.6.12 Q38. ML monitoring platform

**Difficulty:** Hard · **Time:** 45 min · **Related:** Ch 70 (ML monitoring; architecture §70.15, delayed labels §70.8, alerting §70.13), §69.12 (retraining loop)

#### Prompt

"We run 2,000 models. Most failures are silent: a feature pipeline breaks or user behavior shifts and nobody notices for weeks. Design a monitoring platform that every model team uses."

#### Clarifying questions and assumptions

Online, batch or both? Do labels arrive, and when? Who gets paged? Assume 2,000 models (500 online) producing 1 million predictions/s in total at peak; 100 monitored features per model on average; feature vectors logged for 2% of predictions at 2 KB each; label delays from minutes (clicks) to 90 days (chargebacks).

#### Requirements

Functional: SDK to log predictions with IDs, model version and sampled features; label ingestion and joining; data-quality checks; drift on features and predictions; performance metrics by slice when labels mature; alerting with routing to owners; dashboards; retraining triggers. Non-functional: drift and data-quality signals within 1 hour; at most a few actionable alerts per model per month; no impact on serving latency (asynchronous logging); 13 months of aggregates.

#### Estimation

::: example
**Worked example — Log volume and the multiple-testing trap.** Volume uses §89.6 and §89.11; false alarms use the formula of §70.6.4.

1. Feature logs: $10^6 \times 0.02 \times 2$ KB $= 40$ MB/s, **3.5 TB a day**; prediction records without features are small enough to keep for every prediction.
2. Drift tests: $2{,}000 \times 100 \times 24 = 4.8$ million per day if every feature is tested hourly.
3. At $\alpha = 0.01$ with no real drift: **48,000 false alarms a day**. Per model: $1 - 0.99^{2{,}400} \approx 1$, so every model alerts every day.
4. Even at $\alpha = 10^{-4}$, 480 false alarms a day remain.

**Interpretation.** Data volume is easy; alert volume is the design problem. Testing everything with a fixed threshold guarantees an ignored pager. **Engineering implication.** Page on a few outcome-linked signals (prediction distribution, volume, nulls, delayed-label performance), file tickets for feature drift ranked by importance and effect size, and require minimum effect sizes rather than p-values on huge samples (§70.6.3).
:::

#### Data, labels and features

Prediction records (prediction ID, model and version, timestamp, entity, score, decision, fallback level), sampled feature vectors, reference windows (training data or a stable production period), and labels joined by prediction ID or entity and time (§70.8). Proxies when labels are delayed: score distribution, decision rate, downstream engagement.

#### High-level design

**Figure 92.112 — Monitoring platform: log, aggregate, compare, alert.**

```mermaid
flowchart LR
  MS[Model services<br/>with SDK] -.->|predictions, sampled features| PL[[Prediction log]]
  LB{{Label sources}} -.-> LJ[Label joiner<br/>by prediction ID]
  PL -.-> AGG[Stream aggregation:<br/>sketches per window]
  PL -.-> LAKE[(Prediction lake)]
  LJ --> LAKE
  AGG --> TS[(Metric store)]
  LAKE --> BATCH[Batch jobs: slice<br/>performance, calibration]
  BATCH --> TS
  TS --> DET[Detectors: quality,<br/>drift, performance]
  REF[(Reference windows)] --> DET
  DET --> AL{Alert policy}
  AL -->|page| ONC([Model owner on-call])
  AL -->|ticket| TQ[[Ticket queue]]
  AL -.->|trigger| RT[Retraining pipeline]
```

**Reading the diagram.** Services log asynchronously through an SDK, so serving latency is untouched. A stream job keeps per-window sketches (counts, null rates, quantile sketches, category frequencies) per model and feature; the lake keeps raw records for batch jobs that compute slice performance once labels join. Detectors compare current windows to reference windows; an alert policy decides page, ticket or retraining trigger. Failure points: the logging path itself (alert on missing data per model, since silence looks healthy), label joins that silently drop rows (monitor join rate), and reference windows that include an incident. Scaling: sketches keep metric storage independent of traffic; batch jobs scale with labeled volume.

#### Model and evaluation

Detectors are the models: PSI or Jensen–Shannon distance with effect-size thresholds per feature, KS tests on numeric scores, a domain classifier or MMD for multivariate and embedding drift (§70.7), calibration error with confidence intervals per slice (§70.9). Evaluate detectors on replayed historical incidents (did they fire, how early) and on calm periods (false alarms per model-month).

#### Serving and monitoring

The platform monitors itself: log ingestion lag and loss per model, sketch job lag, label join rates, detector run completeness. Alert quality is tracked: pages per model per month and the share of pages that led to action.

#### Deep dives

1. **Alert design.** Few pages, tied to outcomes; feature drift ranked by importance-weighted effect size; seasonality-aware references (same hour last week); burn-rate alerts on quality SLOs (§70.13.2).
2. **Delayed labels.** Track label maturity; report performance only on matured cohorts; estimate precision and recall from scores in the meantime (§70.8.2).
3. **Bugs versus genuine change.** A step change at a deploy time with nulls or unit changes is a bug (roll back the pipeline); a gradual shift is drift (retrain or recalibrate).

#### Trade-offs and alternatives

Per-team dashboards are flexible but inconsistent; a vendor tool is fast to adopt but needs the same logging contract; logging all features gives fuller drift coverage at 50 times the storage.

#### Follow-up questions

1. *Every model alerts daily.* Fixed thresholds on huge samples; use effect sizes, importance weighting and fewer pages.
2. *Labels arrive after 60 days.* Proxies plus estimated metrics now, true metrics on matured cohorts later.
3. *How do you catch a broken upstream join?* Null and default rates per feature, and volume per entity, compared hour over hour.
4. *Should drift trigger automatic retraining?* Only with validation gates; a pipeline bug retrained into the model is worse.

#### What distinguishes levels

- **Mid:** dashboards of feature distributions and accuracy.
- **Senior:** drift tests, delayed-label handling, slice metrics.
- **Staff:** quantifies the multiple-testing problem and designs alert policy around it, separates bugs from drift, and makes logging completeness and alert quality platform SLOs.

### 92.6.13 Q39. Federated learning for a mobile keyboard

**Difficulty:** Hard · **Time:** 45 min · **Related:** §71.11 (federated learning, secure aggregation), §71.10 (differential privacy), Ch 67 (model optimization)

#### Prompt

"Improve next-word suggestions in our mobile keyboard without collecting what users type. Design the training and serving system."

#### Clarifying questions and assumptions

How many devices, and when may they train? Model size limits on phones? Privacy commitments (no raw text leaves the device; formal DP)? Assume 100 million devices with the keyboard, 10% eligible at a time (idle, charging, unmetered network), a 5-million-parameter language model, 3,000 training rounds of 1,000 completing clients.

#### Requirements

Functional: on-device next-word prediction; federated training rounds; federated evaluation; model release to devices. Non-functional: suggestion latency ≤ 20 ms per keystroke on low-end phones; model ≤ 10 MB on device; no raw text uploaded; secure aggregation with client-level DP; each device spends at most a few minutes and tens of megabytes per participation.

#### Estimation

::: example
**Worked example — Bytes and wall-clock per training run.** Apply the FedAvg communication formula of §71.11.1.

1. Per participant: download FP32 model $5 \times 10^6 \times 4 = 20$ MB; upload an 8-bit update, 5 MB; **25 MB** per participation.
2. Per round with 30% over-selection: $1{,}300 \times 20 + 1{,}000 \times 5 = 31$ GB at the server; 3,000 rounds, **93 TB**.
3. Wall clock at 7 minutes per round (deadline-bound by slow devices): $3{,}000 \times 7 / 1{,}440 = 14.6$ days.
4. Participation: $3{,}000 \times 1{,}000 / 10^7 = 0.3$ rounds per eligible device: most devices train once or never per run.

**Interpretation.** Per-device cost is small; the run is bounded by rounds and stragglers. **Engineering implication.** Spend local epochs to cut rounds, compress uploads, and keep the model small; parallel runs (hyperparameters) multiply server bandwidth, not device cost.
:::

#### Data, labels and features

Self-supervised: the next word the user actually typed is the label, available only on the device. Non-IID data (each user's vocabulary and language mix) and biased participation (newer, well-connected phones) are the main data hazards. A server-side proxy corpus (public text) is used for pre-training and sanity checks, never as the target distribution.

#### High-level design

**Figure 92.113 — Federated training with secure aggregation and on-device serving.**

```mermaid
flowchart LR
  SRV[FL coordinator:<br/>rounds, selection] -->|model and plan| DEV([Eligible phones])
  DEV -->|local training<br/>on own typing| DEV
  DEV -->|masked, clipped updates| SA[Secure aggregator]
  SA -->|sum only| SRV
  SRV --> DP[Add DP noise,<br/>update global model]
  DP --> FE[Federated evaluation<br/>on held-out devices]
  FE --> GATE{Release gate}
  GATE -->|pass| CDN[(Model CDN)]
  CDN -.->|staged rollout| KB([Keyboard on device])
```

**Reading the diagram.** The coordinator selects eligible devices and sends the model and a training plan; each device trains locally and uploads a clipped, masked update; the secure aggregator reveals only the sum; the server adds noise for client-level DP and forms the next model [Bonawitz et al. 2017; McMahan et al. 2018]. Federated evaluation on other devices measures quality; a gate releases the model through a CDN with staged rollout. Failure points: dropouts mid-round (over-selection, dropout-tolerant aggregation), poisoned updates (norm clipping, robust aggregation), and slow convergence on non-IID data. Scaling: clients per round bounded by aggregation cost; runs bounded by wall clock.

#### Model and evaluation

Baseline: n-gram model trained on public text. Production: small recurrent or transformer language model, pre-trained on a public corpus then federated-trained, quantized to INT8 for the device [Hard et al. 2018]. Offline: federated top-3 recall of the next word on held-out devices, sliced by language and device tier. Online: suggestion tap rate and characters saved, A/B by device.

#### Serving and monitoring

On-device inference within 20 ms; monitor crash and latency telemetry, suggestion tap rate by locale, round completion rates, dropout rates, update norm distributions (poisoning detection) and the cumulative privacy budget per run.

#### Deep dives

1. **Rounds dominate.** FedAvg's local epochs cut communication rounds relative to one-step FedSGD [McMahan et al. 2017].
2. **Privacy layering.** Data minimization (FL) + secure aggregation (server sees only sums) + client-level DP (sums do not reveal any one user).
3. **Systems heterogeneity.** Eligibility rules bias participation; track slices by device tier and region, and cap rounds per device.

#### Trade-offs and alternatives

Central training on donated or public text is faster but conflicts with the privacy promise; on-device personalization without federation adapts to one user but does not improve the global model.

#### Follow-up questions

1. *Is FL private by itself?* No; updates can leak, hence secure aggregation and DP.
2. *How do you debug a model you cannot see data for?* Federated analytics (aggregate statistics), synthetic test suites and the proxy corpus.
3. *A malicious client sends huge updates.* Clip update norms and use robust aggregation.
4. *Why is training slow?* Stragglers and non-IID data; over-select, use deadlines and more local work.

#### What distinguishes levels

- **Mid:** describes FedAvg.
- **Senior:** adds eligibility, secure aggregation, compression and federated evaluation.
- **Staff:** sizes rounds, bytes and wall clock, layers DP on secure aggregation with a budget, and treats participation bias as a fairness issue.

### 92.6.14 Q40. Two-sided marketplace matching

**Difficulty:** Hard · **Time:** 45 min · **Related:** §55.5 (ride matching: batched assignment, fencing), §83.5 (ETA at scale), §83.6 (dynamic pricing), §60.15 (QuickBite ETA)

#### Prompt

"QuickBite assigns each order to a courier as soon as it is placed. Food is often cold and couriers wait at restaurants. Design an ML-driven matching system."

#### Clarifying questions and assumptions

- Use the QuickBite shared assumptions: 500,000 orders a day, busiest-hour 27.8 orders/s and a 60 orders/s design peak, 20,000 couriers active at peak, 4,000 delivery zones, 35-minute median delivery.
- Objective? Minimize late and cold deliveries while keeping courier idle time and earnings fair.
- May one courier carry two orders (stacking)? Yes, within a lateness bound.
- Decision latency? Seconds are fine; food preparation takes 10 minutes or more.

#### Requirements

Functional: decide which courier gets each order and when to dispatch; consider stacking; send offers with accept or decline; reassign on decline or delay.

Non-functional: decisions within 5 s of a decision window closing; each order assigned to exactly one courier (leases and fencing, §55.5.8); p90 delivery-time error and lateness rate not worse than today at launch; courier earnings per hour fairness tracked by zone.

#### Estimation

::: example
**Worked example — Supply, problem size and prediction load.** Concurrency uses Little's Law (§4.11); prediction load uses §89.13.

1. Busiest hour: 27.8 orders/s × 20 minutes of courier time per order $= 33{,}360$ order-legs in flight against 20,000 couriers: an average of **1.67 orders per courier**, so stacking is not an optimization but a necessity at peak.
2. A 30 s decision window at the 60/s design peak holds 1,800 orders; a large city with 10% of volume gives about 180 orders against a few thousand nearby couriers, a sparse assignment problem solved in well under a second.
3. Predictions: 60 orders/s × 50 candidate couriers × 2 windows per order = **6,000 travel-time and acceptance predictions/s**, plus food-ready predictions per order: small next to search's 40,000 ETA predictions/s.

**Interpretation.** Compute is cheap; the value is in deciding *when* and *whom* jointly across many orders. **Engineering implication.** Batch decisions in short windows with learned costs (ready time, travel time, acceptance), and dispatch late enough that couriers do not wait at restaurants.
:::

#### Data, labels and features

- **Labels:** food-ready time (from courier arrival and pickup scans; censored when the courier arrives late), travel times per leg, offer acceptance, delivery lateness, customer ratings on cold food.
- **Features:** restaurant prep-time history by hour and item count, live kitchen load (open orders), courier location, vehicle, recent decline rate, traffic and weather, zone supply and demand.
- **Hazards:** selection bias (acceptance is only observed for offers made), and censoring of ready time when couriers arrive after the food is ready.

#### High-level design

**Figure 92.114 — Batched matching with learned costs.**

```mermaid
flowchart LR
  ORD[[New orders]] --> WIN[Decision window<br/>per city, 30 s]
  CL[(Courier locations<br/>and states)] --> CAND[Candidate generation:<br/>couriers within radius]
  WIN --> CAND
  CAND --> PRED[Prediction service:<br/>ready, travel, accept]
  PRED --> OPT[Assignment solver:<br/>min-cost with stacking]
  OPT --> DEC{Dispatch now<br/>or wait?}
  DEC -->|now| OFF[Offer service<br/>lease and fencing]
  DEC -->|wait| WIN
  OFF -->|push| CR([Courier app])
  CR -.->|accept, decline,<br/>scans| EVT[[Event log]]
  EVT -.-> TR[Training and<br/>simulator calibration]
```

**Reading the diagram.** Orders accumulate in per-city windows; candidate generation finds couriers within a radius; the prediction service scores each order–courier pair (and stacked pairs) for food-ready time, travel time and acceptance probability; the solver minimizes expected lateness, cold-food time and courier waiting. A dispatch decision may defer an order to a later window if its food will not be ready. Offers are leased with fencing tokens so one order has one courier (§55.5.8). Events flow back asynchronously for training and for calibrating a simulator. Failure points: prediction service outage (fallback to distance-based costs), a declined offer (re-enter the next window), and solver timeouts (greedy fallback). Scaling: cities are independent problems, solved in parallel.

#### Model and evaluation

- **Baseline:** greedy nearest available courier at order time.
- **Production:** gradient-boosted models for ready time (quantile loss, §57.11.2), travel time (reuse the ETA model) and acceptance; batched min-cost assignment with stacking [Kuhn 1955]; optionally a learned value of courier positions for future demand [Xu et al. 2018].
- **Offline:** prediction metrics (MAE and p90 error for ready time, calibration for acceptance) plus **simulation** of the full policy on replayed demand, because assignments change outcomes and logged data cannot score a new policy directly.
- **Online:** switchback experiments (alternate policies by city and time slot) because couriers are shared between arms; primary metric lateness and cold-food complaints; guardrails courier earnings per hour, wait time at restaurants, cancellations.

#### Serving and monitoring

Per city: window solve time, share of greedy fallbacks, offer acceptance rate, courier wait at pickup, lateness rate, stacked-order share and its lateness. Prediction monitoring per model as in Q38.

#### Deep dives

1. **When to dispatch.** Assigning at order time makes couriers wait while food cooks; dispatching so arrival matches predicted ready time cuts wait and frees supply. Quantile predictions bound the risk of being late.
2. **Joint assignment and stacking.** Batched matching beats greedy when orders compete for couriers (§55.5.8); stacking costs are evaluated on order pairs whose restaurants and destinations are close.
3. **Evaluation under interference.** User-level A/B tests are biased because arms share couriers; switchbacks with carryover buffers or city-level tests measure the policy.

#### Trade-offs and alternatives

Greedy is simple and immediate but myopic; reinforcement learning of the full policy can capture future value but is hard to validate safely; fixed zone-based dispatch is predictable for couriers but inefficient across zone boundaries.

#### Follow-up questions

1. *Why not assign immediately?* Couriers wait at restaurants and miss better matches; waiting a window costs seconds, not minutes.
2. *A courier declines repeatedly.* Acceptance predictions lower their cost-adjusted value; policy, not the model, sets any penalties.
3. *How do you test without a real A/B?* Switchbacks by city and time slot, with a simulator to pre-screen.
4. *Is stacking fair to customers?* Bound the extra minutes for the first order and measure lateness by stacked versus single.

#### What distinguishes levels

- **Mid:** predicts ETAs and assigns nearest courier.
- **Senior:** batched assignment with learned costs, exactly-one assignment with leases.
- **Staff:** uses Little's Law to show stacking is necessary, decides *when* to dispatch from ready-time quantiles, and evaluates with simulation and switchbacks because of interference.
