# 8. Quality Assurance Plan

Eight review passes are applied to every chapter before it is marked *Final* in the progress tracker. Reviews 1–7 run per chapter after drafting; Review 8 runs per deliverable build.

**Table P.6 — Review passes.**

| # | Review | Questions asked | Method | Pass criterion |
|---|---|---|---|---|
| 1 | Completeness | Are all TOC sections present? All 20 template elements (where applicable)? All brief topics covered? | Automated section check (`build/qa_check.py`) + manual TOC diff | 100% of TOC sections; template elements present or justified |
| 2 | Technical accuracy | Are formulas, numbers, algorithms, protocol details and code correct? | Recompute every worked example; run all code; compare to primary sources | Zero known errors; disputed items listed |
| 3 | Pedagogical quality | Can a beginner follow without unexplained prerequisites? Analogy before jargon? | Read as a beginner; check every term is defined before use or cross-referenced | No undefined terms; prerequisites listed |
| 4 | Architectural quality | Do diagrams match prose? Are components, protocols, sync/async, storage boundaries and failure points explained? | Diagram-by-diagram audit against "Reading the diagram" | Every figure has caption + explanation; diagrams render |
| 5 | Industry relevance | Are company examples sourced and labelled? Any invented internals? | Check each `industry` callout's evidence label and citation | 100% labelled; no unlabelled company claims |
| 6 | Interview readiness | Does the chapter teach reasoning (trade-offs, failure, estimation), not memorization? | Check interview questions have model answers with trade-offs; design challenges are open-ended | ≥ 3 basic, 3 intermediate, 3 advanced questions with answers |
| 7 | Duplication and consistency | Same term, same meaning? Repeated deep explanations? | Terminology grep against `terminology.md`; dedup ownership table (04 §4.5) | No conflicting definitions; duplicates replaced by cross-references |
| 8 | Final document quality | Layout, typography, tables, diagram clipping, references, page numbers, navigation | Build PDF/DOCX/HTML; visual inspection of rendered pages; link check | Clean build; no clipped diagrams; TOC and numbering correct |

## 8.1 Automated checks (`build/qa_check.py`)

- Exactly one `#` heading per chapter file; heading levels never skip.
- Required end-matter sections present (Summary, Knowledge checkpoint, Interview questions, Practical exercises, Design challenges, References, Open verification items).
- Every ` ```mermaid ` block is preceded by a `**Figure N.K` caption and followed (within 3 paragraphs) by "Reading the diagram".
- Figure and table numbers are sequential and prefixed with the correct chapter number.
- Every `industry` callout contains `*Evidence:`.
- Every `formula` callout contains a table.
- Mermaid blocks render without error (checked during build).
- Word count, figure count and table count reported for the tracker.

## 8.2 Manual review checklist (per chapter)

- [ ] Learning objectives are measurable and met by the content.
- [ ] Every formula: variables, units, worked example, interpretation, implication.
- [ ] Every code sample executed (or marked illustrative).
- [ ] Failure scenarios cover detection, recovery and prevention.
- [ ] At least one comparison table where alternatives exist.
- [ ] Cross-references point to the correct chapter/section numbers.
- [ ] Time-sensitive claims carry "as of".
- [ ] Open verification items are copied to `unresolved-questions.md`.

## 8.3 Defect severity

| Severity | Definition | Action |
|---|---|---|
| S1 | Technically wrong statement, wrong formula/calculation, fabricated source | Block release; fix immediately |
| S2 | Missing required element, unexplained prerequisite, unlabelled industry claim | Fix before *Final* |
| S3 | Style, formatting, minor duplication | Fix during integration |
