# Chapter 66 — Model Serving

> **Level:** 3 · **Track:** B (ML/AI) · **Estimated reading time:** 5 h

A trained model is a file. On QuickBite's laptop-sized test bench the ETA model answers in a tenth of a millisecond, the dish-photo classifier in 40 milliseconds, and both look finished. In production the same files must answer 40,000 times a second at dinner and 4,000 times a second at 3 a.m.; survive a node failure, a bad release and a feature store that slows down; change version every night without a single failed request; and cost a fraction of a cent per order. **Model serving** is the engineering that turns the file into that service.

This chapter owns general model serving: everything between "the model is in the registry" and "a prediction reached the client", for models that are not large language models. You will learn the four inference modes (online, asynchronous, streaming and batch), the anatomy of a model server, and what each widely used server (NVIDIA Triton, TorchServe, TensorFlow Serving, KServe, Ray Serve and BentoML) is for. The quantitative core is **dynamic batching**: you will derive its latency and throughput, simulate it, and measure a real batch curve with PyTorch. You will then decide between CPUs and GPUs by cost per 1,000 predictions, share GPUs among models, autoscale with headroom, load and warm models quickly, route traffic between versions, and roll out safely with shadow traffic, canaries, A/B tests and interleaving. The chapter ends with batch inference at scale, reliability and observability for serving, and a reference architecture for QuickBite's ETA service at 40,000 predictions per second.

Chapter 60 placed the model runtime inside the inference pipeline (§60.6), set its latency budget (§60.10) and fleet-sizing formula (§60.11). Chapter 64 explained why GPUs need batches. Chapter 67 makes each model cheaper (quantization, distillation, compilation), Chapter 68 serves recommenders, and Chapter 73 owns large language model (LLM) serving: key–value (KV) cache management and continuous batching are previewed here only.

::: note
**QuickBite assumptions used in this chapter.** These reuse the Book II design point; they are teaching assumptions, not measurements of a real company. Search peaks at 2,000 requests per second (RPS), each scoring 20 restaurants: **40,000 ETA predictions/s at peak**, about 360 million a day, an average of 4,167/s (peak-to-average ratio 9.6, §18.11), about 720 ETA predictions per order (§60.6.2). The primary ETA model is gradient-boosted trees costing 0.1 ms of CPU per prediction; a deep challenger costs 2 ms per prediction on CPU or runs at 25,000 predictions/s per GPU at batch 64 (§60.11). The ETA service's p99 budget is 100 ms, of which the model stage gets 20 ms (Table 60.12). Prices: \$0.77 per hour for a 16-vCPU node (\$0.048 per vCPU-hour) and \$2.50 per GPU-hour (§60.11, §64.1). QuickBite receives 200,000 new dish photos per day (§58.19). Sizes use SI units (1 GB = 10⁹ bytes).
:::

## 66.1 Learning objectives

After this chapter you should be able to:

- Choose among online, asynchronous, streaming and batch inference for a product requirement, and justify the choice with latency, freshness and cost.
- Draw the components of a model server and explain what each does on the request path and the control path.
- Compare Triton, TorchServe, TensorFlow Serving, KServe, Ray Serve and BentoML by purpose and architecture, and state their status as of 2026.
- Derive the latency and throughput of dynamic batching, pick a maximum batch size and maximum queue delay from a latency budget, and verify the choice by simulation.
- Compute cost per 1,000 predictions on CPUs and GPUs and decide when GPUs pay off.
- Explain model sharding, multi-model serving, model multiplexing and GPU sharing with MIG and MPS.
- Size an autoscaled inference fleet with headroom for reaction time, and estimate cold-start time from model size and storage bandwidth.
- Design version routing and a safe rollout (shadow, canary, A/B, interleaving) with automated analysis and rollback.
- Size a batch-scoring job and make its output writes idempotent.
- Apply timeouts, fallbacks, circuit breakers, load shedding and hedging to an inference service, and instrument it for observability.

## 66.2 Prerequisites

- The inference pipeline, latency budgets and fleet sizing — §60.6, §60.10, §60.11 (this chapter implements the model-runtime box of those sections).
- Fallbacks and cascades — §60.12.2, §60.13.2 (serving reliability builds on the fallback ladder).
- Online feature fetch — §62.7.2, §62.11 (most of an online prediction's latency is often feature retrieval, not the model).
- GPU utilization, the roofline and GPU sharing — §64.9, §64.11, §64.12, §64.15 (why batching helps and why "100% utilized" can mean idle).
- Batching model $T(B) = t_0 + B t_1$ — §4.18.6, §23.8.1 (the formulas this chapter extends).
- Queueing and Little's Law — §4.10, §4.11 (queue delay near saturation).
- Load balancing — §19.4 (least-loaded routing to replicas with queues).
- Autoscaling and Kubernetes — §18.8, §42.12 (HPA, KEDA, node autoscalers, reaction time).
- Canary statistics — §43.6 (two-proportion tests and sample size).
- Timeouts, backpressure, load shedding and circuit breakers — §22.9–§22.13; hedged requests — §23.7.

## 66.3 Inference modes

### 66.3.1 Four ways to run a model

::: definition
**Definition — Inference modes.** **Online (synchronous) inference** computes a prediction inside a client's request and returns it in the response, within a latency budget of milliseconds. **Asynchronous inference** accepts a request, places it on a queue, and delivers the result later by callback, polling or a result store, within seconds to minutes. **Streaming inference** is triggered by events on a log such as Kafka, scores each event (or a micro-batch) as it arrives, and writes results to another stream or store, with no client waiting. **Batch (offline) inference** scores a large, bounded dataset on a schedule and writes the predictions to storage, where online services look them up.
:::

#### First-principles explanation

Think of a bakery. A customer at the counter who wants a coffee waits while it is made: that is online inference, and the barista must be quick because a person is standing there. A wedding cake ordered today for Saturday is asynchronous: the order goes into a queue, the work takes hours, and the customer is called when it is ready. The baker who takes a fresh tray out whenever the oven timer rings, without anyone asking, is streaming: an event (the timer) triggers work whose result goes onto a shelf. And the bread baked at 4 a.m. for the whole day is batch: compute everything ahead, then serve from the shelf instantly.

The choice is driven by two questions: **does someone wait for the answer?** and **can the answer be computed before the question is asked?** If the input space is small and known in advance (every restaurant's prep time tomorrow), precompute it in batch. If the input is only known at request time (this customer, this basket, this traffic, now), compute it online. If the input arrives as events and the consumer can tolerate seconds of delay, stream it. If the computation is too slow for a request but someone needs the answer (an image-moderation verdict, a document summary), make it asynchronous.

#### Why does this exist?

Latency, freshness and cost pull in different directions. Online inference gives the freshest answer but pays for peak capacity and every millisecond of the budget. Batch inference is the cheapest per prediction, because it runs at full utilization on cheap capacity, but its answers are hours old and it must compute predictions for inputs nobody asks about. Asynchronous and streaming modes sit between: they absorb bursts in a queue (§30.3), so capacity can be sized for the average rather than the peak. Section 60.8 introduced the batch-versus-online decision; this section adds the two queue-based modes and their mechanics.

#### How it works internally

1. **Online.** The client opens an RPC (HTTP/JSON or gRPC) to a load balancer, which routes to a replica of the model server. The server fetches or receives features, runs the model, and responds. Every stage spends part of a deadline propagated from the client (§22.11).
2. **Asynchronous.** The client posts a job to an API, which writes it to a queue (SQS, Kafka, Redis streams) and returns a job ID immediately (HTTP 202 Accepted). Workers pull jobs at their own pace, run the model and write the result to a store keyed by job ID; the client polls or receives a webhook. Queue depth is the natural autoscaling signal.
3. **Streaming.** A stream processor (Kafka consumer, Flink job) reads events from partitions, gathers features, calls the model in-process or through a model server, and produces predictions to an output topic or writes them to a key-value store. Ordering and parallelism follow the topic's partitions (§31.5); consumer lag is the health signal.
4. **Batch.** A scheduler (Airflow, §61.15) launches a Spark or Ray job that reads a partition of input rows, scores them in large batches on many workers, and writes an output partition atomically. Online services read the results from a key-value store or warehouse.

**Figure 66.1 — The four inference modes.**

```mermaid
flowchart LR
  subgraph Online["Online: client waits, ms"]
    C1([Client]) -->|gRPC| LB1[Load balancer]
    LB1 --> MS1[Model server]
  end
  subgraph Async["Asynchronous: s to min"]
    C2([Client]) -->|POST, 202 + job ID| API[Job API]
    API -.-> Q2[[Job queue]]
    Q2 -.-> W2[Workers + model]
    W2 --> R2[(Result store)]
    C2 -.->|poll or webhook| R2
  end
  subgraph Stream["Streaming: event-driven, s"]
    K1[[Kafka: events]] -.-> SP[Stream job + model]
    SP -.-> K2[[Kafka: predictions]]
    SP --> KV3[(Key-value store)]
  end
  subgraph Batch["Batch: scheduled, hours"]
    LAKE[(Lake partition)] --> BJ[Spark or Ray job]
    BJ --> OUT[(Prediction table)]
    OUT -.->|bulk load| KV4[(Serving KV store)]
  end
```

**Reading the diagram.** *Online* (solid arrows, synchronous): the client's RPC passes a load balancer to a model-server replica and waits for the answer; the only storage on the path is whatever the server reads for features. Failure point: any slow stage breaks the client's deadline; scale by adding replicas. *Asynchronous*: the job API returns immediately and the queue (dotted, asynchronous) decouples arrival from processing; workers write to a result store, the storage boundary the client polls. Failure point: a growing queue; scale workers on queue depth. *Streaming*: a stream job consumes events from Kafka, scores them and produces predictions to another topic or a key-value store; no client waits. Failure point: consumer lag; scale by partitions and consumers. *Batch*: a scheduled job reads a bounded lake partition and writes a prediction table, which is bulk-loaded into a serving store. Failure point: a failed or late run leaves stale predictions; scale with more workers.

#### QuickBite's inference modes

**Table 66.1 — QuickBite's models and the mode each uses.**

| Model | Input known in advance? | Who waits | Mode | Freshness |
|---|---|---|---|---|
| Search-page ETA (20 restaurants) | No: customer location, live backlog | Customer, 100 ms | Online | Request time |
| Restaurant prep-time baseline | Yes: 50,000 restaurants × 96 quarter-hours | Nobody | Batch, nightly | ≤ 24 h |
| In-flight order ETA refresh | No: courier status events | Nobody; app reads latest | Streaming | ~seconds |
| Fraud score at checkout | No: basket, payment, device | Checkout, 150 ms | Online | Request time |
| Dish-photo tagging | Photo uploaded | Restaurant, minutes | Asynchronous | Minutes |
| Home-page candidate list | Mostly: 4 million weekly active users | Nobody | Batch, then online re-rank | Hours + request |

The prep-time baseline shows why batch wins when the input space is enumerable: 50,000 × 96 = 4.8 million predictions a night, versus 360 million online ETA calls a day that each need it as a feature. The home-page list is the common hybrid: precompute candidates in batch, re-rank online (Chapter 68).

#### Alternatives and trade-offs

**Table 66.2 — Inference modes compared.**

| Aspect | Online | Asynchronous | Streaming | Batch |
|---|---|---|---|---|
| What it is | Prediction inside a request | Queued job, result later | Prediction per event on a log | Scheduled scoring of a dataset |
| How it works | RPC → server → model → response | API → queue → workers → result store | Consumer → model → topic or store | Scheduler → Spark/Ray → table |
| Advantages | Freshest inputs; any input | Absorbs bursts; long models fit | Fresh without a waiting client; decoupled | Cheapest per prediction; easy retries |
| Disadvantages | Peak-sized capacity; tight budget | Client must poll or accept callback | Ordering, lag and replay to manage | Stale; scores inputs never requested |
| Performance | ms p99; batches small | s–min; large batches | Seconds of lag; micro-batches | Hours; maximal batches |
| Operational complexity | High: SLOs, autoscaling, fallbacks | Medium: queue, retries, idempotency | Medium–high: offsets, rebalances | Low–medium: job orchestration |
| Cost | Highest (peak, headroom) | Medium (sized near average) | Medium | Lowest (spot, full utilization) |
| Use cases | ETA, fraud, ranking | Image or document processing | Re-prediction on status change, alerts | Prep-time baselines, candidate lists |
| Choose when | Input known only at request time and a user waits | Work too slow for a request, someone needs it | Inputs are events, seconds of delay OK | Input space enumerable, staleness OK |

#### Failure scenarios

**Table 66.3 — Inference-mode failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Online p99 breach at peak | Replicas saturated; queues grow | Latency SLI, queue time metric | Shed load to fallback; scale out | Headroom (§66.9), load shedding |
| Async queue grows for hours | Workers fewer than arrivals; poison job retried forever | Queue age, oldest-message metric | Scale workers; dead-letter the poison job | Queue-depth autoscaling; retry limits |
| Streaming lag after a rebalance | Consumers restart and reload the model | Consumer lag per partition | Wait, or add consumers | Keep model loaded across rebalances; cooperative rebalancing (§31.12) |
| Batch run fails at 05:00 | Bad input partition, spot preemption | Job status, freshness of output table | Re-run the idempotent job; serve yesterday's table | Data validation gates; checkpointed jobs |
| Online and batch disagree | Different feature code in each path | Skew monitor (§62.9) | Fix the path that diverged | One feature definition for both paths |

::: mistake
**Mistake — "Real-time" means online inference.** Product managers say "real-time" for anything that looks fresh. A courier-status ETA refreshed by a streaming job within 3 seconds is real-time to the customer, yet no request waits on the model. Ask who waits and how stale the answer may be; the mode follows from those two numbers, not from the word.
:::

## 66.4 Anatomy of a model server

### 66.4.1 Components

::: definition
**Definition — Model server.** A **model server** is a long-running process that loads one or more trained models into memory and exposes them as a network service. It accepts inference requests over HTTP or gRPC, applies pre- and post-processing, schedules requests (usually through a batching queue) onto a **model runtime** (an execution engine such as ONNX Runtime, TensorRT, LibTorch or XGBoost), and returns predictions. A **model repository** is the storage location and layout from which the server loads models and versions; **health** and **metrics** endpoints let orchestrators and monitoring observe it.
:::

#### First-principles explanation

A model server is a restaurant kitchen. The front-of-house (the request handler) takes orders in several languages and checks them. Prep cooks (pre-processing) chop the inputs into the shape the chef needs. The pass (the batching queue) holds tickets for a moment so that the chef can cook four steaks in one pan. The chef (the runtime) does the heavy work, the plating station (post-processing) makes the output presentable, and the pantry (the model repository) holds the recipes, of which the kitchen keeps one or a few in active use. A manager walks around with a clipboard: the health checks and metrics.

#### Why does this exist?

You can call `model.predict()` inside your web service, and for small models that is often right (§66.16). A dedicated server earns its place when: the model needs a GPU and its process must batch requests from many clients; several models or versions must share one machine's memory; the runtime is in a different language from the service; or the platform team wants one way to deploy, observe and roll back every model. Clipper [Crankshaw et al. 2017] and TensorFlow-Serving [Olston et al. 2017] were early, influential designs that separated a model-agnostic serving layer (batching, caching, versioning) from model-specific execution; today's servers follow the same split.

#### How it works internally

1. **Request handling.** A network front end (HTTP/REST and gRPC) parses the request, validates shapes and types against the model's signature, and checks the deadline. Most servers speak the **Open Inference Protocol** (also called the KServe V2 protocol): `POST /v2/models/{name}[/versions/{v}]/infer` with named input tensors [KServe Docs].
2. **Pre-processing.** Converts the request into tensors: tokenizing text, decoding and resizing images, normalizing features, mapping categorical values to indices. It must match training exactly, or you create training–serving skew (§62.9). It runs on CPU and can be the bottleneck for GPU models.
3. **Scheduling and batching.** A per-model queue groups requests into batches under a size limit and a delay limit (§66.6), and assigns them to one of several **model instances** (copies of the model, possibly on different GPUs or CUDA streams).
4. **Model runtime.** Executes the forward pass. The runtime is chosen per model format: TensorRT or ONNX Runtime for compiled graphs, LibTorch or TorchScript for PyTorch, the TensorFlow runtime for SavedModels, a forest-inference library for trees.
5. **Post-processing.** Turns raw outputs into answers: softmax and top-k, calibration, clipping an ETA into a range, attaching the model version and explanation fields.
6. **Model repository and lifecycle manager.** Watches a directory or object-store prefix, loads new versions, unloads old ones according to a version policy, and reports which versions are ready.
7. **Health and metrics.** Liveness (`/v2/health/live`: is the process up?) and readiness (`/v2/health/ready`: are the models loaded and warmed?), and Prometheus metrics such as request counts, queue time, compute time and batch sizes.

**Figure 66.2 — Anatomy of a model server.**

```mermaid
flowchart LR
  C([Clients]) -->|HTTP or gRPC| FE[Request handler<br/>validate, deadline]
  FE --> PRE[Pre-processing<br/>CPU workers]
  PRE --> BQ[[Per-model<br/>batching queue]]
  BQ --> I1[Model instance 1<br/>GPU 0]
  BQ --> I2[Model instance 2<br/>GPU 1]
  I1 --> POST[Post-processing]
  I2 --> POST
  POST --> FE
  REPO[(Model repository<br/>object storage)] -.->|load, unload versions| LM[Lifecycle manager]
  LM -.-> I1
  LM -.-> I2
  FE -.->|metrics| PROM[(Prometheus)]
  K8S{{Orchestrator}} -->|liveness, readiness| FE
```

**Reading the diagram.** The request path (solid arrows) is synchronous: clients call the request handler over HTTP or gRPC; requests are validated, pre-processed on CPU workers, queued per model, batched and executed on one of two model instances, post-processed and returned. The batching queue is the heart of the server and its main failure point: when arrivals exceed instance capacity it grows and latency rises without any error. The control path (dotted, asynchronous) runs beside it: the lifecycle manager loads and unloads versions from the model repository, the storage boundary, and metrics are scraped into Prometheus. The orchestrator probes liveness and readiness; a replica that is not ready receives no traffic. Scaling: add instances inside a server (more GPUs or streams), or add server replicas behind a load balancer.

#### Where pre-processing runs

Pre-processing placement is a design decision with real cost. Decoding and resizing a JPEG costs a few milliseconds of CPU, which can exceed the GPU time of the classification itself. Three placements exist: in the client service (simple, but every client reimplements it), in the server's CPU workers (one implementation, but the server's CPU-to-GPU ratio must cover it), or as a separate **transformer** stage in a pipeline (KServe's transformer component, Triton's ensembles). For QuickBite's dish classifier, decoding on CPU workers in the same pod keeps one implementation and avoids sending raw images over the network twice.

::: recommendation
**Recommendation — Make the model signature a contract.** Store the input and output names, shapes, types and the pre-processing version with each model in the registry, validate requests against it in the request handler, and fail loudly on mismatch. A silently reordered feature vector is the most expensive bug in serving because nothing crashes.
:::

#### Common misconceptions

::: mistake
**Mistake — A model server is just a web server around `predict()`.** The difference is the scheduler. A plain web framework runs one request per worker thread, so a GPU receives batches of 1 and runs at a few percent of its capability while requests queue in the framework. A model server's batching queue and instance scheduler are what turn many small requests into the large matrix multiplications GPUs need (§64.12).
:::

## 66.5 Model servers compared

### 66.5.1 Runtimes, servers and platforms

The products are easier to compare once you separate three layers. An **inference runtime** executes a model graph (TensorRT, ONNX Runtime, LibTorch). An **inference server** wraps runtimes with the machinery of §66.4: protocols, batching, model repository, metrics. A **serving platform** deploys servers onto a cluster and adds autoscaling, traffic splitting and a declarative API. Some products are frameworks in which you write the serving logic in Python and the framework provides replicas, batching and composition.

**Figure 66.3 — Where each product sits.**

```mermaid
flowchart TB
  subgraph Platform["Serving platform on Kubernetes"]
    KS["KServe<br/>InferenceService CRD"]
  end
  subgraph Frameworks["Python serving frameworks"]
    RS["Ray Serve<br/>deployments on Ray"]
    BM["BentoML<br/>services, Bentos"]
  end
  subgraph Servers["Inference servers"]
    TR["Triton<br/>multi-framework, C++"]
    TFS["TensorFlow Serving"]
    TS["TorchServe<br/>archived 2025"]
  end
  subgraph Runtimes["Runtimes"]
    RT["TensorRT, ONNX Runtime,<br/>LibTorch, TF, XGBoost"]
  end
  KS -->|runs as ServingRuntime| TR
  KS --> TFS
  KS --> TS
  RS --> RT
  BM --> RT
  TR --> RT
  TFS --> RT
  TS --> RT
```

**Reading the diagram.** Arrows mean "deploys or calls"; all are in-process or local except KServe's, which creates Kubernetes resources that run a server image. KServe is a control plane: it does not execute models itself but launches a server (Triton, TensorFlow Serving, TorchServe or others) as a **serving runtime**. Ray Serve and BentoML are Python frameworks that call runtimes directly from user code. The three inference servers wrap runtimes with batching and model management. No storage is drawn; all load models from a repository or object store. Failure points differ by layer: a runtime crash takes down one server; a platform misconfiguration can affect every model. Scaling happens at the platform or framework layer (replicas) and at the server layer (instances per GPU).

### 66.5.2 The six servers

**NVIDIA Triton Inference Server.** An open-source C++ server that runs many frameworks through **backends**: TensorRT, ONNX Runtime, PyTorch (LibTorch), TensorFlow, OpenVINO, a Python backend for custom code and a forest-inference backend for tree models [NVIDIA Triton Docs]. Each model has a directory in the model repository with numbered version subdirectories and a `config.pbtxt` declaring inputs, outputs, `max_batch_size`, an **instance group** (how many copies on which devices) and a **dynamic batcher** (preferred batch sizes and `max_queue_delay_microseconds`). Triton runs several models and several instances concurrently on one GPU, supports **ensembles** (a pipeline of models and pre-processing steps executed inside the server), a sequence batcher for stateful models, and serves HTTP and gRPC with the Open Inference Protocol and Prometheus metrics. Companion tools (Perf Analyzer, Model Analyzer) sweep batch and concurrency settings. *As of 2026*: in March 2025 NVIDIA renamed it **NVIDIA Dynamo-Triton** as part of its Dynamo inference platform, whose separate Dynamo framework targets distributed LLM serving (Chapter 73); NVIDIA states that Triton continues to be supported under the new name [NVIDIA Dynamo-Triton].

**TorchServe.** A PyTorch server developed by AWS and Meta: models are packaged as model archives (`.mar`) with a Python **handler** for pre- and post-processing, served with separate inference, management and metrics APIs, and batched with `batchSize` and `maxBatchDelay` settings. *As of 2026*: the project's README carries a "Limited Maintenance" notice stating that it is no longer actively maintained, and the GitHub repository was archived (read-only) on 7 August 2025 [TorchServe GitHub]. Do not start new deployments on it; existing ones should plan a migration (Triton's PyTorch backend, Ray Serve or a KServe runtime are the usual targets).

**TensorFlow Serving.** Google's C++ server for TensorFlow SavedModels, described by Olston et al. [Olston et al. 2017]. Its abstractions are worth learning even if you never use it: a **servable** is any object clients query (a model version, a lookup table); **loaders** know how to load and unload one; **sources** discover new versions on storage and emit *aspired versions*; and a **manager** loads and unloads them under a **version policy**, either availability-preserving (load the new version before unloading the old) or resource-preserving (unload first to save memory). It includes a request batcher (`max_batch_size`, `batch_timeout_micros`). *As of 2026* it remains maintained for TensorFlow users, with a smaller share of new projects as PyTorch dominates.

**KServe.** A Kubernetes-native serving platform. You declare an `InferenceService` custom resource with a `predictor` (and optionally a `transformer` for pre/post-processing and an `explainer`); a controller creates the deployment using a **ServingRuntime** (Triton, TensorFlow Serving, an MLServer runtime for scikit-learn and XGBoost, a Hugging Face runtime, or your own image). An init container (the storage initializer) downloads the model from `storageUri`. Deployment modes include a serverless mode on Knative (request-based autoscaling, scale to zero), a raw Kubernetes Deployment mode (HPA or KEDA), and ModelMesh for dense multi-model serving. Canary rollout is a field (`canaryTrafficPercent`) [KServe Docs]. *As of 2026*: KServe was accepted as a Cloud Native Computing Foundation (CNCF) incubating project in 2025, after starting as KFServing in Kubeflow, and recent releases add LLM-oriented features [CNCF 2025].

**Ray Serve.** A Python serving library on the Ray distributed runtime. A **deployment** is a Python class whose replicas are Ray actors; deployments call each other through handles, which makes **model composition** (pipelines, ensembles, business logic between models) ordinary Python. It provides request batching through a `@serve.batch` decorator (maximum batch size and a wait timeout), autoscaling on ongoing requests per replica, fractional GPU allocation, and **model multiplexing**: routing requests for one of many models to replicas that already have it loaded [Ray Serve Docs]. On Kubernetes it runs through KubeRay. Choose it when serving logic is Python-heavy or spans many models.

**BentoML.** A Python framework for packaging and serving models. You define a service class with API methods; marking an API `batchable` enables **adaptive batching** with a maximum batch size and maximum latency; `bentoml build` produces a **Bento**, a versioned bundle of code, model references and dependencies that becomes a container image [BentoML Docs]. A managed platform (BentoCloud) deploys Bentos. *As of 2026*: the open-source project remains Apache-2.0 licensed; Modular was reported in February 2026 to have acquired BentoML (see Open verification items).

#### Alternatives and trade-offs

**Table 66.4 — Model servers compared (as of 2026).**

| Aspect | Triton (Dynamo-Triton) | TorchServe | TF Serving | KServe | Ray Serve | BentoML |
|---|---|---|---|---|---|---|
| What it is | Multi-framework inference server | PyTorch server | TensorFlow server | Kubernetes serving platform | Python serving library on Ray | Python packaging and serving framework |
| How it works | C++ core, backends, model repo, dynamic batcher | Java front end, Python handlers, `.mar` | Servables, loaders, managers | CRD → controller → runtime pods | Deployments as Ray actors, handles | Service classes → Bento → image |
| Advantages | Throughput, GPU features, many formats | Simple for PyTorch | Mature version management | Declarative, canary, scale to zero | Composition, multiplexing, Python | Fast path from notebook to image |
| Disadvantages | Config-heavy; custom logic in Python backend is slower | Archived, no fixes | TensorFlow only | Needs Kubernetes expertise; layers to debug | Ray cluster to operate | Less control of low-level GPU scheduling |
| Performance | Highest for GPU models | Moderate | High for TF | Inherits from runtime | Good; Python overhead per call | Good; inherits from runtime |
| Operational complexity | Medium | Low (but unmaintained) | Medium | High | Medium–high | Low–medium |
| Cost | Free; GPU efficiency lowers cost | Free | Free | Free; cluster overhead | Free; Ray overhead | Free; managed option paid |
| Use cases | GPU vision, ranking, ensembles | Legacy PyTorch | Legacy TF | Platform for many teams | Multi-model pipelines | Small teams, many services |
| Choose when | You need maximum GPU throughput | Only to keep an existing system running | Your models are TensorFlow | You run Kubernetes and want one API for all models | Logic between models is complex | You want packaging conventions fast |

::: industry
**Uber — Michelangelo's online prediction service.** Uber's ML platform deploys trained models into prediction-service containers that load models from storage and serve them over RPC; several models can be deployed to the same container at once, which supports safe transitions and side-by-side A/B tests, and clients address a model by an identifier or tag. The platform also offered batch scoring through Spark jobs. The design matches this chapter's split between a model-agnostic serving layer and model artifacts managed by a registry.
*Evidence: Primary* — [Hermann and Del Balso 2017]
:::

::: warning
**Warning — Product names and maintenance status change quickly.** Within two years one major server was archived and another renamed. Wrap the server behind the Open Inference Protocol and your own client library, keep model artifacts in standard formats (ONNX, TorchScript or exported programs, SavedModel), and treat the server as a replaceable component.
:::

## 66.6 Dynamic batching

### 66.6.1 Why batching pays and what it costs

::: definition
**Definition — Dynamic batching.** **Dynamic batching** is a server-side scheduling policy that combines individual inference requests arriving within a short window into one batch for a single model execution. A batch is dispatched when it reaches a **maximum batch size** $B_{\max}$ or when the oldest request has waited a **maximum queue delay** $D_{\max}$, whichever comes first (and, in most servers, as soon as an execution instance is free if the queue is non-empty and delay is zero). **Adaptive batching** adjusts $B_{\max}$ online to keep latency within an objective.
:::

#### First-principles explanation

An elevator could leave with each passenger who arrives, or it could wait a few seconds for more. Waiting costs the first passenger a little time but moves many more people per trip. If the lobby is crowded, the elevator fills instantly and waiting costs nothing; if the lobby is empty, waiting a long time is pointless. Dynamic batching is an elevator with two rules: leave when full, or leave when the first passenger has waited $D_{\max}$.

The reason it pays on accelerators is the roofline (§64.9). At batch 1 a dense layer reads each weight once for one multiply–add, so the GPU is memory-bound and its arithmetic units idle. At batch 64 the same weight read serves 64 rows. Time per batch therefore grows much more slowly than batch size until the layer becomes compute-bound (§64.12): $T(B) = t_0 + B t_1$ with a large $t_0$ (weight reads, kernel launches, framework overhead) and a small $t_1$.

#### Why does this exist?

Without a batcher, a GPU serving one request at a time spends most of each execution on fixed cost. Clipper introduced adaptive batching for online serving, increasing batch size additively and cutting it multiplicatively (AIMD) when latency exceeded the objective [Crankshaw et al. 2017]; TensorFlow-Serving's batcher used a size and a timeout [Olston et al. 2017]. Every server in §66.5 now implements the pattern.

#### How it works internally

1. A request arrives and is appended to the model's queue with its arrival time (and, in some servers, a priority and deadline).
2. When an instance is free, the scheduler looks at the queue. If it holds $B_{\max}$ rows, it dispatches a full batch at once.
3. Otherwise it waits until either $B_{\max}$ rows have arrived or the oldest has waited $D_{\max}$; then it dispatches whatever is queued (up to $B_{\max}$). Triton can also prefer certain batch sizes (for example multiples of 8 that suit tensor cores).
4. The batch is padded or concatenated into one tensor, executed, and the outputs are split and returned to each request.
5. If all instances are busy, requests keep accumulating; batches then fill without waiting, so **under heavy load the queue itself does the batching**.

**Figure 66.4 — Two batches formed by size and by delay.**

```mermaid
sequenceDiagram
  participant R as Requests
  participant Q as Batching queue
  participant G as GPU instance
  R->>Q: r1 at 0.0 ms
  R->>Q: r2 at 0.4 ms
  R->>Q: r3 at 1.1 ms
  Note over Q: oldest waited D_max = 2 ms
  Q->>G: batch of 3 at 2.0 ms
  R->>Q: r4 .. r67 arrive during execution
  G-->>Q: batch done at 3.1 ms
  Q->>G: batch of 64 at 3.1 ms, B_max reached
  G-->>R: responses split per request
```

**Reading the diagram.** Time runs downward. Three requests arrive into the queue (synchronous appends inside the server); none fills the batch, so the delay rule fires when the oldest has waited 2 ms and the GPU runs a batch of 3. While that batch executes, 64 or more requests arrive; when the instance becomes free, the size rule fires immediately with a full batch of 64, without waiting. Responses are split and returned (dashed reply arrows). The queue is in memory, so a crash loses queued requests: clients must retry. The failure point is the queue growing faster than batches drain; scale with more instances or replicas.

#### Mathematical foundations

A request's latency has three parts: waiting for the instance to finish earlier work, waiting for its own batch to close, and the batch's execution time.

::: formula
**Dynamic batching latency and throughput**

$$L = W_{\text{busy}} + W_{\text{fill}} + T(B) \qquad T(B) = t_0 + B\,t_1 \qquad X(B) = \frac{B}{t_0 + B\,t_1}$$

$$L_{\text{worst}} \approx D_{\max} + 2\,T(B_{\max}) \quad (\text{one batch in flight}) \qquad \text{stable only if } \lambda < X(B_{\max})$$

| Symbol | Meaning | Units |
|---|---|---|
| $L$ | Latency of one request inside the server | ms |
| $W_{\text{busy}}$ | Wait for the batch already executing to finish, $\le T(B_{\max})$ | ms |
| $W_{\text{fill}}$ | Wait for the request's own batch to close, $\le D_{\max}$ | ms |
| $T(B)$ | Execution time of a batch of $B$ rows | ms |
| $t_0$, $t_1$ | Fixed time per batch; marginal time per row | ms, ms/row |
| $X(B)$ | Throughput of one instance at batch size $B$ | rows/s |
| $B_{\max}$, $D_{\max}$ | Maximum batch size and maximum queue delay | rows, ms |
| $\lambda$ | Arrival rate of rows at the instance | rows/s |
| $L_{\text{worst}}$ | Approximate worst case when the queue holds no backlog | ms |
:::

Note the asymmetry: $D_{\max}$ only adds latency when the lobby is empty, while $B_{\max}$ sets the throughput ceiling $X(B_{\max})$ when it is full. Beyond the ceiling no delay setting helps; the queue grows without bound (§4.10.3).

::: example
**Worked example — Choosing $B_{\max}$ and $D_{\max}$ for the deep ETA model on a GPU.** A load test of the deep ETA model on one GPU gives the batch curve below, which fits $t_0 = 1.0$ ms and $t_1 = 0.025$ ms per row (assumed, illustrative values consistent with §60.11). The model stage's p99 budget is 20 ms (Table 60.12). Three GPUs share the 40,000 rows/s peak, so each receives $\lambda = 13{,}333$ rows/s; we want peak utilization at most 0.7.

**Table 66.5 — Assumed GPU batch curve for the deep ETA model.**

| $B$ (rows) | $T(B)$ (ms) | $X(B)$ (rows/s) | Rows/s per ms of latency |
|---|---|---|---|
| 1 | 1.025 | 976 | 952 |
| 8 | 1.200 | 6,667 | 5,556 |
| 32 | 1.800 | 17,778 | 9,877 |
| 64 | 2.600 | 24,615 | 9,467 |
| 128 | 4.200 | 30,476 | 7,256 |
| 256 | 7.400 | 34,595 | 4,675 |

1. Capacity: we need $X(B_{\max}) \ge 13{,}333 / 0.7 = 19{,}048$ rows/s. $B_{\max} = 32$ gives 17,778, too little; $B_{\max} = 64$ gives 24,615, enough (peak utilization $13{,}333 / 24{,}615 = 0.54$).
2. Latency with $B_{\max} = 64$, $D_{\max} = 2$ ms: $L_{\text{worst}} \approx 2 + 2 \times 2.6 = 7.2$ ms, well inside 20 ms.
3. The alternative $B_{\max} = 256$ has more throughput (34,595) but $L_{\text{worst}} \approx 2 + 2 \times 7.4 = 16.8$ ms leaves only 3 ms for variance and queueing; reject.
4. Ceiling: $1/t_1 = 40{,}000$ rows/s per GPU, never reachable because $t_0$ is paid per batch.

**Interpretation.** Throughput per GPU rises 25-fold from batch 1 to 64, while the worst-case model latency stays under 8 ms. The last column shows diminishing returns: past 64 rows each extra millisecond of latency buys fewer rows per second. **Engineering implication.** Pick the smallest $B_{\max}$ that meets peak demand with headroom, then the largest $D_{\max}$ that keeps $L_{\text{worst}}$ within the budget; re-measure the curve whenever the model, runtime or GPU changes, because $t_0$ and $t_1$ come from a load test, not from the formula.
:::

#### Code example: a dynamic batching simulator

The simulator below runs one GPU instance with the batch curve of Table 66.5 under Poisson arrivals of single-row requests. It applies the size and delay rules of §66.6.1 and reports latency percentiles, mean batch size, throughput and the fraction of time the GPU is executing.

```python
"""Dynamic batching simulator: one GPU, Poisson arrivals, size and delay limits."""
import numpy as np

T0, T1 = 1.0e-3, 0.025e-3        # batch time T(B) = t0 + B*t1 (s), from a load test
N = 200_000                      # requests per run, one row each

def simulate(rate, max_batch, max_delay, seed=1):
    rng = np.random.default_rng(seed)
    arr = np.cumsum(rng.exponential(1.0 / rate, N))   # Poisson arrivals
    lat = np.empty(N)
    sizes = []
    t_free, i = 0.0, 0
    while i < N:
        ready = max(t_free, arr[i])             # instance free and a request waiting
        j = i + max_batch - 1                   # request that would fill the batch
        t_full = arr[j] if j < N else np.inf
        close = max(ready, min(arr[i] + max_delay, t_full))
        k = np.searchsorted(arr, close, side="right")
        n = min(k - i, max_batch)
        done = close + T0 + T1 * n
        lat[i:i + n] = done - arr[i:i + n]
        sizes.append(n)
        t_free, i = done, i + n
    busy = sum(T0 + T1 * b for b in sizes) / (t_free - arr[0])
    return (np.percentile(lat, 50) * 1e3, np.percentile(lat, 99) * 1e3,
            np.mean(sizes), N / (t_free - arr[0]), busy)

print(f"{'rate/s':>7}{'B_max':>6}{'delay ms':>9}{'p50 ms':>10}{'p99 ms':>10}"
      f"{'mean B':>8}{'served/s':>10}{'busy':>6}")
runs = [(2_000, 1, 0.0), (2_000, 64, 0.0), (2_000, 64, 1.0), (2_000, 64, 2.0), (2_000, 64, 4.0),
        (15_000, 64, 0.0), (15_000, 64, 2.0), (15_000, 64, 4.0),
        (30_000, 64, 0.0), (30_000, 128, 0.0), (30_000, 128, 2.0)]
for rate, max_batch, delay_ms in runs:
    p50, p99, mean_b, served, busy = simulate(rate, max_batch, delay_ms / 1e3)
    print(f"{rate:>7,}{max_batch:>6}{delay_ms:>9.1f}{p50:>10.2f}{p99:>10.2f}"
          f"{mean_b:>8.1f}{served:>10,.0f}{busy:>6.0%}")
```

Output (about 3 seconds on one CPU core; deterministic for the fixed seed):

```text
 rate/s B_max delay ms    p50 ms    p99 ms  mean B  served/s  busy
  2,000     1      0.0  52701.84 104388.30     1.0       976  100%
  2,000    64      0.0      1.58      2.16     2.2     2,009   95%
  2,000    64      1.0      1.85      2.18     3.0     2,009   72%
  2,000    64      2.0      2.40      3.23     5.0     2,009   45%
  2,000    64      4.0      3.50      5.33     9.0     2,008   27%
 15,000    64      0.0      2.43      3.48    24.2    15,061  100%
 15,000    64      2.0      2.84      3.95    31.2    15,061   86%
 15,000    64      4.0      4.44      6.47    59.3    15,059   63%
 30,000    64      0.0    745.81   1476.24    64.0    24,609  100%
 30,000   128      0.0      6.84     11.26   121.7    30,107  100%
 30,000   128      2.0      6.84     11.26   121.9    30,107  100%
```

What to notice:

- **No batching collapses at 2,000 rows/s.** With $B_{\max} = 1$ the instance serves 976 rows/s, so the queue grows for the whole run and latencies reach tens of seconds. Any batching at all fixes this.
- **The queue batches for you.** With $D_{\max} = 0$ (dispatch whenever the instance is free) the mean batch grows from 2.2 at 2,000/s to 24 at 15,000/s automatically, because requests accumulate while the GPU is busy. With one instance, a zero delay gives the lowest latency at every load below saturation.
- **Delay buys GPU time, not latency.** At 2,000 rows/s a 2 ms delay raises p50 by 0.8 ms but cuts busy time from 95% to 45%. That freed time is what a second model on the same GPU (§66.8) or fewer GPUs can use. The 95% "busy" GPU at batch 2.2 is the nvidia-smi trap of §64.11: always running, mostly wasted.
- **$B_{\max}$ sets the ceiling.** At 30,000 rows/s, $B_{\max} = 64$ caps throughput at 24,609 rows/s and latency explodes to seconds; $B_{\max} = 128$ serves the load at 11 ms p99. Near saturation the delay setting is irrelevant because batches are always full.
- **Limitations.** Real servers have several instances, execution-time variance, multi-row requests (an ETA request carries 20 rows, so batches fill in coarser steps) and Python overhead; use the simulator for intuition and confirm with a load test (§23.5).

#### Code example: measuring a real batch curve on CPU

The curve in Table 66.5 is assumed. The program below measures one on your machine for a small multilayer perceptron with about 300,000 parameters, roughly the size of a deep ETA model over 64 features.

```python
"""Time a small MLP on CPU at several batch sizes; fit T(B) = t0 + B*t1."""
import time
import numpy as np
import torch

torch.manual_seed(0)
torch.set_num_threads(1)                     # one core: steadier numbers
model = torch.nn.Sequential(                 # ETA-sized deep model: 64 features in
    torch.nn.Linear(64, 512), torch.nn.ReLU(),
    torch.nn.Linear(512, 512), torch.nn.ReLU(),
    torch.nn.Linear(512, 1)).eval()

def batch_ms(b, reps=50):
    x = torch.randn(b, 64)
    with torch.inference_mode():
        for _ in range(10):                  # warm-up: allocator, kernel selection
            model(x)
        times = []
        for _ in range(reps):
            t = time.perf_counter()
            model(x)
            times.append(time.perf_counter() - t)
    return 1e3 * float(np.median(times))

sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
ms = [batch_ms(b) for b in sizes]
print(f"{'batch':>6}{'ms/batch':>10}{'us/row':>9}{'rows/s':>10}")
for b, t in zip(sizes, ms):
    print(f"{b:>6}{t:>10.3f}{1e3 * t / b:>9.2f}{1e3 * b / t:>10,.0f}")
t1, t0 = np.polyfit(sizes, ms, 1)            # least-squares line through the points
print(f"fit: t0 = {t0:.3f} ms per batch, t1 = {1e3 * t1:.2f} us per row, "
      f"ceiling 1/t1 = {1e3 / t1:,.0f} rows/s")
```

Output from one run (about 3 seconds on a 4-core cloud VM; your numbers will differ, and a second run on the same VM differed by up to 30%):

```text
 batch  ms/batch   us/row    rows/s
     1     0.045    44.92    22,264
     2     0.039    19.57    51,111
     4     0.053    13.35    74,915
     8     0.072     9.01   111,036
    16     0.143     8.95   111,738
    32     0.215     6.71   149,128
    64     0.366     5.72   174,876
   128     0.670     5.23   191,080
   256     1.235     4.83   207,240
   512     2.431     4.75   210,611
  1024     4.818     4.70   212,552
fit: t0 = 0.051 ms per batch, t1 = 4.66 us per row, ceiling 1/t1 = 214,761 rows/s
```

What to notice:

- **The shape, not the numbers.** Cost per row falls about tenfold from batch 1 to 64 and then flattens: fixed overhead (Python dispatch, operator launch, weight reads) is amortized, and beyond a few hundred rows the matrix multiplications are compute-bound. Expect the same shape on any machine, with the knee in a different place.
- **CPU batching helps too.** Even with no GPU, scoring 20 restaurants as one batch of 20 rather than 20 calls of 1 is several times cheaper. This is why the ETA service scores a search page as one batch.
- **Warm-up and medians.** The first calls are slower (memory allocation, kernel selection), so the program discards them and reports the median; benchmarking without warm-up overstates $t_0$ (§23.5.4, §66.10).
- **A straight line is an approximation.** Small batches sit above the fitted line and some sizes (16 here) show steps from how the library tiles the matrix; GPUs show stronger steps (wave quantization, §64.4). Always use measured points for decisions.

#### Failure scenarios

**Table 66.6 — Dynamic batching failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| p99 rises with no error | $D_{\max}$ or $B_{\max}$ too large for budget | Queue-time and compute-time histograms | Lower $D_{\max}$, then $B_{\max}$ | Derive both from $L_{\text{worst}}$ |
| Latency explodes at peak | $\lambda > X(B_{\max})$ | Queue depth growing; batch size pinned at $B_{\max}$ | Shed or scale out | Capacity test at $1.3\times$ peak |
| Out-of-memory at large batches | Activation memory grows with $B$ | GPU OOM errors on big requests | Cap rows per request | Test $B_{\max}$ with the largest input shapes |
| Padding waste | Variable-length inputs padded to the longest | Low useful-token fraction | Bucket by length | Sequence bucketing; ragged batching |
| One slow client starves others | Large requests fill batches | Per-client latency | Priority levels or separate queues | Per-tenant queues and limits |

::: mistake
**Mistake — Tuning $D_{\max}$ to "improve throughput".** With one instance per GPU, a work-conserving batcher already fills batches under load; a delay raises latency at low load and changes nothing at high load. Its real benefits are freeing GPU time for co-located models and avoiding many tiny concurrent batches when several instances share a GPU. Increase $B_{\max}$ (or add instances) to raise the ceiling.
:::

::: note
**Preview — LLM batching is different.** A transformer generating text runs hundreds of decode steps per request with different output lengths, so request-level batching leaves slots idle when short requests finish. **Continuous (iteration-level) batching** admits and retires requests at every decode step, and the KV cache, not compute, limits the batch. Chapter 73 owns these mechanisms.
:::

## 66.7 CPU versus GPU serving

### 66.7.1 When GPUs pay off

::: definition
**Definition — Cost per 1,000 predictions.** The fully loaded hourly price of the serving hardware divided by the predictions it serves per hour, times 1,000. It depends on the device's throughput at a batch size that meets the latency objective *and* on the utilization the fleet actually achieves, including idle redundancy.
:::

A GPU is a bus and a CPU core is a taxi. The bus costs far more per hour, but if it is full, each passenger pays less. If it carries three people, the taxi was cheaper. Whether GPUs pay off depends on three things: how much arithmetic each prediction needs (a tree walk barely uses a GPU; a convolutional network fills it), whether enough traffic arrives to fill batches within the latency budget (§66.6), and whether the fleet's minimum size, set by redundancy rather than load, leaves GPUs idle.

::: formula
**Cost per 1,000 predictions and the GPU break-even speedup**

$$C_{1k} = \frac{1{,}000 \; p}{3{,}600 \; X \; u} \qquad S^{*} = \frac{p_{\text{gpu}}}{p_{\text{cpu}}} \cdot \frac{u_{\text{cpu}}}{u_{\text{gpu}}}$$

| Symbol | Meaning | Units |
|---|---|---|
| $p$ | Price of one device (one vCPU or one GPU with its share of host) | \$/h |
| $X$ | Predictions per second one device sustains within the latency budget | predictions/s |
| $u$ | Average utilization the fleet achieves | dimensionless |
| $C_{1k}$ | Cost per 1,000 predictions | \$ |
| $S^{*}$ | Throughput ratio $X_{\text{gpu}}/X_{\text{cpu}}$ above which the GPU is cheaper | dimensionless |
:::

::: example
**Worked example — QuickBite's ETA trees versus a dish-photo classifier.** Prices: \$0.048 per vCPU-hour, \$2.50 per GPU-hour. Planned utilization: CPU 0.5, GPU 0.6. Then $S^{*} = (2.50 / 0.048) \times (0.5 / 0.6) = 52.1 \times 0.833 = 43.4$: a GPU must do the work of 43 vCPUs to be cheaper.

**Dish classifier** (a ResNet-50-class CNN, about 8 GFLOP per image; assumed load tests): one vCPU classifies 20 images/s (50 ms each); one GPU 6,000 images/s at batch 64 in FP16.

1. CPU: $C_{1k} = 1{,}000 \times 0.048 / (3{,}600 \times 20 \times 0.5) = 48 / 36{,}000 = \$0.00133$.
2. GPU: $C_{1k} = 1{,}000 \times 2.50 / (3{,}600 \times 6{,}000 \times 0.6) = 2{,}500 / 12{,}960{,}000 = \$0.000193$.
3. Speedup $6{,}000 / 20 = 300 > 43.4$: the GPU is $0.00133 / 0.000193 = 6.9$ times cheaper, and 50 ms per image on CPU would also miss a tight latency budget.

**ETA trees** (0.1 ms per prediction): one vCPU does 10,000/s; assume a GPU forest-inference backend does 500,000/s in large batches.

4. Per device the GPU is 50 times faster, barely above $S^{*} = 43.4$, so even at 0.6 utilization it would save only $1 - 43.4/50 = 13\%$.
5. But utilization is not 0.6. Zone redundancy requires at least three GPUs (\$7.50/h) for a peak of 40,000/s, which is 2.7% of their capacity. At the average 4,167/s: $C_{1k} = 1{,}000 \times 7.50 / (3{,}600 \times 4{,}167) = \$0.000500$, versus \$0.000154 for the three-node CPU fleet of §60.11: the GPUs cost 3.2 times more.

**Interpretation.** Arithmetic per prediction decides whether a GPU *can* win; traffic and the redundancy floor decide whether it *does*. **Engineering implication.** Serve tree models and small MLPs on CPUs inside the calling service; serve convolutional networks, transformers and large ranking models on GPUs once traffic fills at least a few GPUs; for low volume, as with 200,000 dish photos a day (200,000 × 50 ms = 2.8 vCPU-hours, about \$0.13 a day on CPU), keep the CPU and spend engineering elsewhere.
:::

**Figure 66.5 — Choosing CPU or GPU for a model.**

```mermaid
flowchart TB
  A{"Model is trees, linear<br/>or small MLP?"} -->|yes| CPU["CPU, in-process or<br/>CPU model server"]
  A -->|no| B{"CPU meets the latency<br/>budget at batch 1?"}
  B -->|no| GPU["GPU with dynamic batching"]
  B -->|yes| C{"Peak traffic fills<br/>≥ 2-3 GPUs at batch B?"}
  C -->|no| SH{"GPU sharing available?<br/>MIG, MPS, multi-model"}
  SH -->|yes| GPU2["GPU slice shared<br/>with other models"]
  SH -->|no| CPU
  C -->|yes| D{"C_1k on GPU<br/>lower than CPU?"}
  D -->|yes| GPU
  D -->|no| CPU
```

**Reading the diagram.** Decisions flow top to bottom; there is no runtime traffic in this figure. The first test removes models whose arithmetic is too small to use a GPU. The second sends models that cannot meet the budget on CPU straight to GPUs, whatever the price. The third asks whether traffic can fill GPUs; if not, sharing a GPU with other models (§66.8) can recover utilization. The last compares $C_{1k}$ with the formula above. Failure point: answering with benchmark throughput at a batch size the latency budget does not allow. Scaling: re-run the decision when traffic grows, because a model that is cheaper on CPU at 1,000/s may be cheaper on GPU at 100,000/s.

::: mistake
**Mistake — Comparing a GPU at batch 256 with a CPU at batch 1.** Benchmarks quote GPU throughput at the batch size that maximizes it. Use the throughput at the batch size your latency budget and traffic actually produce (§66.6), and compare the CPU at its best batch size too; the CPU also gains several times from batching (§66.6.1).
:::

## 66.8 Model-parallel and multi-model serving

### 66.8.1 One model too big, many models too small

::: definition
**Definition — Model-parallel serving, multi-model serving and multiplexing.** **Model-parallel serving** splits one model's weights across several devices because they do not fit on one: **tensor parallelism** splits each layer's matrices, **pipeline parallelism** places consecutive layers on different devices, and **embedding sharding** places rows of large embedding tables on different hosts. **Multi-model serving** hosts many models in one server process or GPU. **Model multiplexing** routes each request for one of many models to a replica that already has that model loaded, loading it on demand and evicting the least recently used model when memory is full.
:::

Two opposite problems share a solution space. A recommendation model with a billion-user embedding table (10⁹ × 128 dimensions × 4 bytes = 512 GB, §58.6) cannot fit on an 80 GB GPU, so it must be split. QuickBite's 20 per-city ETA models or 300 per-restaurant-chain demand models are each small and mostly idle, so giving each its own replica wastes the floor of §66.7 twenty or three hundred times. Model parallelism serves the first; packing serves the second.

**How the large-model case works.** Tensor parallelism inside one server keeps the per-layer exchange on NVLink (§64.14) and cuts per-request latency; pipeline parallelism across servers sends activations only between stages but adds a hop per stage and needs several requests in flight to keep every stage busy. For recommenders, the dense layers are replicated and embedding lookups go to sharded embedding servers or to host memory; Chapter 68 owns that design, and Chapter 73 owns tensor and pipeline parallelism for LLMs.

**How the many-models case works.** A memory budget decides how many models fit: an 80 GB GPU with 10 GB reserved for activations and runtime workspace holds $\lfloor 70 / 1.5 \rfloor = 46$ models of 1.5 GB each. Compute must also fit: the sum of the models' busy fractions must stay below the target utilization. When the working set exceeds memory, the server loads models on demand from a node-local cache and evicts the least recently used; a request for an evicted model pays the load time of §66.10, so the router should send requests for a model to the replicas that already hold it (Ray Serve multiplexing, KServe ModelMesh) [Ray Serve Docs; KServe Docs]. INFaaS went further: clients state a latency and accuracy requirement, and the system picks among *variants* of a model (different hardware, batch size, precision) and scales them, so users need not choose [Romero et al. 2021].

**GPU sharing** gives each model a slice of one GPU (§64.15). **MIG** partitions an A100/H100-class GPU into up to seven isolated instances with dedicated memory and compute, which gives predictable latency for tenants that must not disturb each other. **MPS** lets processes run kernels concurrently on one GPU without hardware isolation, which suits cooperating models of one team. Nexus showed how a cluster scheduler can pack DNN models onto shared GPUs with batch-aware "squishy" bin packing that accounts for how each model's latency grows with batch size [Shen et al. 2019].

**Figure 66.6 — Three ways to map models to GPUs.**

```mermaid
flowchart LR
  subgraph Shard["One large model, sharded"]
    R1([Request]) --> G1[GPU 0: layers 1-12]
    G1 -->|activations, NVLink| G2[GPU 1: layers 13-24]
  end
  subgraph Pack["Many models, multiplexed"]
    RT[Router: model ID] --> S1["Replica A<br/>holds m1, m7, m9"]
    RT --> S2["Replica B<br/>holds m2, m7"]
    S1 -.->|miss: load| CACHE[(Node cache)]
  end
  subgraph Slice["One GPU, partitioned"]
    MIG["H100 MIG"] --> M1["3g slice:<br/>deep ETA"]
    MIG --> M2["2g slice:<br/>dish classifier"]
    MIG --> M3["2g slice:<br/>fraud model"]
  end
```

**Reading the diagram.** *Sharded*: a request enters GPU 0, which computes the first layers and sends activations synchronously over NVLink to GPU 1; a failure of either GPU fails the model, so replicate whole shard groups to scale. *Multiplexed*: a router reads the model ID and sends the request to a replica that already holds the model; on a miss, the replica loads it from the node cache (dotted, asynchronous with respect to other requests), the storage boundary, which is the latency failure point. Scale by adding replicas and letting popular models occupy several. *Partitioned*: one H100 split by MIG into isolated slices, each serving one model with its own memory and compute; a fault or overload in one slice does not affect the others, but slice sizes are fixed until the GPU is reconfigured.

::: warning
**Warning — Co-location trades isolation for cost.** Packing models onto one GPU with MPS or time-slicing means a burst for one model raises the others' latency, and one process crash can affect all MPS clients (§64.15). Use MIG or separate GPUs for models with strict latency objectives; pack the rest.
:::

## 66.9 Autoscaling inference

### 66.9.1 Signals, reaction time and headroom

::: definition
**Definition — Inference autoscaling.** Automatically changing the number of model-server replicas (and the nodes or GPUs beneath them) to track load, using a signal proportional to load, a target value for it, and limits on how fast and how far to scale. **Scale to zero** removes all replicas when there is no traffic and starts one on the next request, paying a **cold start**.
:::

A web service's autoscaler (§18.8, §42.12) usually tracks CPU utilization. For inference, choose the signal carefully:

**Table 66.7 — Autoscaling signals for model serving.**

| Signal | Good for | Problem |
|---|---|---|
| Request or prediction rate (RPS) | Stateless CPU models; predictable cost per prediction | Ignores request size (20 rows vs 1) |
| CPU utilization | In-process CPU models | Pre-processing or GC can dominate |
| GPU utilization (nvidia-smi) | Rarely | Reads near 100% at batch 2 (§64.11, §66.6) |
| Queue depth or ongoing requests per replica | GPU servers with batching; async workers | Needs a server metric; target from load test |
| Latency (p95, p99) | Alerting, a guardrail | Lags; rises only after saturation, so scaling starts late |

For a batching GPU server the best signal is **in-flight requests (or queued rows) per replica**, with its target taken from the load test as the concurrency at which latency still meets the objective. Ray Serve scales on ongoing requests per replica for this reason [Ray Serve Docs], and KEDA can scale on any Prometheus query such as queue depth, including to and from zero [KEDA Docs].

**Reaction time** is the sum of metric collection, the autoscaler's decision, scheduling, node provisioning if no spare node exists (one to several minutes for GPU nodes), image pull, model download and load, and warm-up (§66.10). Load that arrives during that time must be absorbed by replicas that already exist, so the target utilization must leave room for it.

::: formula
**Target utilization and replicas with headroom for reaction time**

$$u_{\text{target}} = \frac{u_{\max}}{1 + g} \qquad g = \max\!\left(r\,T_{\text{react}},\; s\right) \qquad N = \left\lceil \frac{\lambda \, c}{k \, u_{\text{target}}} \right\rceil$$

| Symbol | Meaning | Units |
|---|---|---|
| $u_{\max}$ | Highest utilization at which the load test still meets the latency objective | dimensionless |
| $r$ | Fractional growth rate of load during a ramp | 1/min |
| $T_{\text{react}}$ | Time from load change to a new replica serving | min |
| $s$ | Largest sudden step in load, as a fraction | dimensionless |
| $g$ | Growth the existing fleet must absorb | dimensionless |
| $u_{\text{target}}$ | Utilization the autoscaler should hold | dimensionless |
| $\lambda$, $c$, $k$ | Load, CPU time per prediction, vCPUs per node | predictions/s, vCPU-s, vCPU |
| $N$ | Nodes (or replicas) to run | count |
:::

::: example
**Worked example — Autoscaling the deep ETA model on CPU.** Option B of §60.11: $c = 2$ ms per prediction, 16-vCPU nodes. A load test shows p99 within budget up to $u_{\max} = 0.75$. Reaction time: 30 s metrics, 15 s decision, 120 s node provisioning, 60 s image pull, model load and warm-up: $T_{\text{react}} = 3.75$ min. The dinner ramp rises at most 2% per minute; a marketing push can add 30% within two minutes.

1. Ramp: $r T_{\text{react}} = 0.02 \times 3.75 = 0.075$. Step: $s = 0.30$. So $g = 0.30$.
2. $u_{\text{target}} = 0.75 / 1.30 = 0.577$; use 0.55.
3. Peak: $N = \lceil 40{,}000 \times 0.002 / (16 \times 0.55) \rceil = \lceil 80 / 8.8 \rceil = \lceil 9.09 \rceil = 10$ nodes.
4. Check the step: 30% more load on 10 nodes is $52{,}000 \times 0.002 / 160 = 0.65 < 0.75$. Holds.
5. Off-peak at 4,167/s: $\lceil 8.33 / 8.8 \rceil = 1$, but the floor of one node per zone keeps 3.
6. Without the step allowance ($u_{\text{target}} = 0.75$): 7 nodes at peak, and the push would drive them to $104 / 112 = 0.93$, where p99 explodes (§4.10.3).

**Interpretation.** The step, not the ramp, sets headroom, because a 4-minute reaction time is long compared with a 2-minute surge. **Engineering implication.** Shorten $T_{\text{react}}$ before buying headroom: keep warm spare nodes (placeholder pods, §42.12), pre-pull images and cache models on nodes (§66.10). Each minute removed lets $u_{\text{target}}$ rise. Predictive scaling on the known dinner curve helps the ramp; only headroom helps the surprise.
:::

**Figure 66.7 — The inference autoscaling loop.**

```mermaid
flowchart LR
  MS[Model server replicas] -.->|queue depth, in-flight| PROM[(Prometheus)]
  PROM -.->|query every 15 s| KEDA[KEDA or HPA]
  KEDA -->|set replicas| DEP[Deployment]
  DEP -->|new pod| SCH[Scheduler]
  SCH -->|no GPU free| NA[Node autoscaler]
  NA -->|launch GPU node, minutes| CLOUD{{Cloud}}
  SCH -->|placed| POD[New replica]
  POD -->|pull model| REPO[(Model store)]
  POD -->|ready after warm-up| LB[Load balancer]
  LB --> MS
```

**Reading the diagram.** Replicas export queue depth and in-flight requests (dotted, asynchronous) to Prometheus; KEDA or the HPA queries it and sets the replica count. New pods go to the scheduler; if no GPU is free, the node autoscaler launches a node through the cloud API, the slowest step. A placed pod pulls its model from the model store (the storage boundary) and joins the load balancer only after warm-up, when its readiness probe passes. Failure points: a stale metrics pipeline freezes scaling; GPU capacity shortages leave pods Pending; a readiness probe that passes before warm-up sends traffic to a cold replica. Scaling limits: cloud GPU quota and the model-store bandwidth when many replicas start at once.

**Scale to zero.** Removing all replicas saves money for models that are idle most of the day: development endpoints, per-tenant models, asynchronous workers. The first request then waits for the full cold start, tens of seconds to minutes for a GPU model (§66.10), so scale to zero only where a client can wait or where an asynchronous queue absorbs the delay. QuickBite's dish-photo workers scale to zero on queue depth overnight; the ETA service never does. MArk combined predictive autoscaling of instances with serverless functions to absorb bursts while new instances started [Zhang et al. 2019].

::: mistake
**Mistake — Scaling a GPU server on GPU utilization.** At low load a work-conserving batcher keeps the GPU "busy" with tiny batches (95% in the §66.6 simulation at 7% of capacity), so the autoscaler sees a hot GPU and adds replicas that are not needed; at high load the signal saturates at 100% and cannot show how far over capacity you are. Scale on queue depth or in-flight requests per replica.
:::
