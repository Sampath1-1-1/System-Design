# 0. Master Project Specification

**Read this file first at the start of every working session.** It preserves context between generation stages.

## 0.1 Mission

Build a complete, technically accurate, professionally formatted system-design knowledge base that takes an absolute beginner to senior/staff-level competence in (A) traditional software system design and distributed systems and (B) machine-learning system design, ML infrastructure and AI/LLM infrastructure.

The learner must come to understand, for every technology: why it exists, what problem it solves, how it works internally, how it communicates with other components, how it is deployed, how it fails, how it scales, how to choose between alternatives, and how to design a complete production system with it.

## 0.2 Invariants (never violate)

1. **Teach from first principles.** Assume no prior knowledge; analogy → mechanism → terminology → numbers.
2. **Follow the template.** `chapter-template.md` and `style-guide.md` are binding.
3. **No fabrication.** No invented papers, authors, URLs, benchmarks or company internals. Uncertainty is stated and logged.
4. **Evidence labels.** Every industry example is Primary, Secondary or Illustrative.
5. **Every formula is explained** (variables, units, worked example, interpretation, implication).
6. **Every diagram teaches** (caption + "Reading the diagram").
7. **Integrate, don't concatenate.** One terminology, cross-references by chapter number, deep treatment in one owner chapter only.
8. **Never silently skip.** Chapters too large for one pass are split into numbered sub-files and tracked.
9. **Single source of truth.** All deliverables are built from `manuscript/`; never hand-edit outputs in `dist/`.

## 0.3 Scope summary

- 93 chapters in 3 books and 19 parts, plus 9 appendices (see `01-master-toc.md`).
- 27 traditional and 27 ML/AI case studies, each in the 16-section format.
- ≥ 105 practice interview questions with full reference solutions.
- 20 progressive implementation projects.
- 10 deliverables (see `06-document-structure.md`), built to PDF, DOCX and HTML.

## 0.4 Workflow per session

1. Read this file, `progress-tracker.md`, and `unresolved-questions.md`.
2. Pick the next research wave from `03-research-plan.md`.
3. Brief agents (one chapter each) with the owner specialty from `04-agent-allocation.md`.
4. Run QA reviews (`08-qa-plan.md`), integrate, update tracker and open questions.
5. Build (`python3 build/build.py`), inspect output, commit and push.

## 0.5 Decisions log

| Date | Decision | Rationale |
|---|---|---|
| 2026-10-30 | Canonical numbering of 93 chapters replaces the brief's 56; crosswalk kept in TOC §1.5 | 16 gap chapters added (maths, security, storage, search, data structures, performance, distributed transactions, DL essentials, labeling, recsys, responsible ML, vector search, LLM adaptation, large-scale AI infra, LLM case studies, real-time comms) |
| 2026-10-30 | Markdown + pandoc + Mermaid as the single source; PDF via headless Chromium, DOCX via pandoc with pre-rendered diagrams | Plain-text sources are diffable and updatable; meets "keep sources, diagrams and code separately" requirement |
| 2026-10-30 | American spelling throughout | Consistency (terminology.md) |
| 2026-10-30 | Decimal units (KB=10³) for estimation, binary (KiB) where precision matters, always stated | Matches common interview practice while staying precise |
| 2026-10-30 | Ten deliverables composed from shared chapters rather than duplicated text | Avoids divergence between volumes |
