# Case-Study Chapter Brief (Chapters 52–56)

Applies on top of `agent-brief.md`. Case-study chapters *apply* the concept chapters; they never re-teach them.

## Structure (headings are binding)

```
# Chapter N — Case Studies …
> **Level:** … · **Track:** A · **Estimated reading time:** …
## N.1 Learning objectives
## N.2 Prerequisites            (list the concept chapters each case leans on)
## N.3 How to use these case studies   (Ch 52: full method, ~600 words; Ch 53–56: one paragraph pointing to §52.3)
## N.4 <First case>
### N.4.1 Problem statement
### N.4.2 Functional requirements
### N.4.3 Non-functional requirements      (numeric targets: availability, p99 latency, durability, consistency)
### N.4.4 Capacity estimation              (full arithmetic in `example` callouts; DAU → RPS → peak, storage/yr, bandwidth, cache size, servers)
### N.4.5 API design                       (endpoints/RPCs with request/response shapes)
### N.4.6 Data model and database schema   (SQL DDL or key design; choice of store justified with cross-refs)
### N.4.7 High-level architecture          (Mermaid diagram + "Reading the diagram")
### N.4.8 Detailed component design        (the 2–3 hardest components in depth)
### N.4.9 Data flow                        (sequence diagrams for the main write and read paths)
### N.4.10 Bottlenecks
### N.4.11 Failure scenarios               (table: what fails · impact · detection · recovery · prevention)
### N.4.12 Scaling strategy                (10× and 100× growth: what breaks and what changes)
### N.4.13 Trade-offs
### N.4.14 Alternative designs
### N.4.15 Interview discussion            (45-minute pacing plan, likely follow-ups with short answers, what distinguishes senior/staff answers)
### N.4.16 Production considerations       (observability, security, cost, operations)
## N.5 <Second case> … (same 16 subsections)
…
## N.x Summary and revision notes
## N.x Knowledge checkpoint
## N.x Interview questions
## N.x Practical exercises
## N.x Design challenges
## N.x References
## N.x Open verification items
```

## Rules

- Each case: ≥ 3 Mermaid figures (high-level architecture, write-path sequence, read-path sequence; add others where they teach), each with `**Figure N.K — Title.**` and "Reading the diagram". Figures and tables are numbered sequentially across the whole chapter.
- Capacity estimates use decimal units and state every assumption; recompute every number with python3.
- Deep concepts get one or two sentences plus a cross-reference (e.g. "consistent hashing, §14.8"). Do not re-derive formulas owned by earlier chapters — cite them and apply them.
- Industry facts are only what companies have published (label *Evidence: Primary/Secondary*); the designs themselves are teaching designs (label *Evidence: Illustrative*) — never claim "this is how X works internally" unless published.
- Different cases must teach different things: emphasize the distinctive hard problem of each (e.g., ID generation for URL shortener, fan-out for news feed, transcoding pipeline for YouTube, geospatial matching for Uber, exactly-once money movement for payments).
- Code is optional; include only short, runnable Python where it clarifies a core algorithm (tested with python3).
- Length: ~4,000–5,000 words per case by qa_check.py count, plus ~2,000 for front and end matter.

## Book II additions (Chapters 81–86, ML and AI case studies)

The 16 subsection headings above stay binding (so every case in the book has the same shape). For ML/AI systems, fill them as follows:

- **N.x.1 Problem statement** — the business objective *and* the ML formulation (prediction target, label, task type) with why ML is warranted (§59.3).
- **N.x.3 Non-functional requirements** — add model-quality targets (offline metric thresholds, online guardrails), freshness of features and models, and inference latency budgets.
- **N.x.4 Capacity estimation** — inference QPS and peak; feature-store reads; training-data volume per day and retained; embedding/index sizes; training compute (GPU-hours) and serving fleet (CPU/GPU count) using formulas owned by earlier chapters (§60.11, §64, §65, §73) — cite, don't re-derive.
- **N.x.5 API design** — prediction/ranking/generation APIs plus feedback/logging APIs.
- **N.x.6 Data model and database schema** — features (with entity keys and freshness), labels and label delay (§63.4), training-example schema, feature-store/vector-index layout.
- **N.x.8 Detailed component design** — always cover: (a) features and training-data pipeline, (b) model choice and training (baseline first, then the production model), (c) serving path, (d) evaluation: offline metrics and the online experiment design (§57.14). Pick the 2–3 hardest pieces to go deepest.
- **N.x.11 Failure scenarios** — include ML-specific failures: training–serving skew, drift, feedback loops, label leakage, stale features/models, adversarial adaptation, safety failures for LLM systems.
- **N.x.16 Production considerations** — monitoring (§70), retraining cadence, responsible ML (§71), cost.
- Per-case length for Book II: **3,500–4,500 words** by qa_check.py, plus ~2,000 for front and end matter. N.3 is one paragraph pointing to §52.3 plus 2–4 sentences on what is different for ML cases.
- Use QuickBite only where a case explicitly says so; otherwise design for a generic company of the stated scale (*Evidence: Illustrative*) and cite published systems (YouTube, Netflix, Pinterest, Uber, Meta, etc.) only for what they have published.
- Different cases must teach different hard problems; the per-chapter briefing names each case's emphasis.
