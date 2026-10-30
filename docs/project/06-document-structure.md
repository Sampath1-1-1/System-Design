# 6. Estimated Document Structure and Deliverable Mapping

## 6.1 How the deliverable is assembled

> **Scope change (2026-10-30):** at the reader's request only the main textbook is produced: `dist/System-Design-Textbook.pdf` and `.docx`, containing all written chapters plus the learning roadmap and glossary as appendices. The table below records the original plan for reference.

All deliverables are generated from one source of truth — the Markdown manuscript — so content is written once and reused. `build/book.yaml` lists which files go into each deliverable.

**Table P.4 — Deliverables.**

| # | Deliverable | Composed from | Formats | Est. pages |
|---|---|---|---|---|
| D1 | Master System Design Textbook | Front matter + Book I (Ch 1–56) + App. A, B, C | PDF, DOCX, HTML | ~1,350 |
| D2 | ML and AI System Design Textbook | Front matter + Ch 4 (maths) + Book II (Ch 57–86) + App. A, B, C | PDF, DOCX, HTML | ~1,000 |
| D3 | Learning Roadmap | Appendix E + Ch 3 §3.8–3.10 + dependency map | PDF, DOCX, HTML | ~30 |
| D4 | Architecture Diagram Collection | All Mermaid blocks extracted with captions (App. D) | PDF, HTML, `.mmd` sources | ~200 |
| D5 | Formula & Estimation Handbook | All `formula` + `example` callouts (App. C) + Ch 89 | PDF, DOCX, HTML | ~80 |
| D6 | Implementation Project Handbook | Ch 93 + `code/` | PDF, DOCX, HTML | ~100 |
| D7 | Traditional Interview Handbook | Ch 87–89, 90, 91 | PDF, DOCX, HTML | ~220 |
| D8 | ML & AI Interview Handbook | Ch 87–90 (ML sections), 92 | PDF, DOCX, HTML | ~180 |
| D9 | Glossary | App. A (generated from bold defining terms + `terminology.md`) | PDF, DOCX, HTML | ~40 |
| D10 | Bibliography & Reference Library | App. B (merged chapter reference lists, de-duplicated) | PDF, DOCX, HTML | ~50 |

## 6.2 Page anatomy of a chapter

1. Chapter opener: title, level/track/reading-time line, learning objectives, prerequisites.
2. Numbered sections, each following the concept template (definition → first principles → why → internals → diagram → maths → code → industry → pros/cons → alternatives → failures → misconceptions).
3. End matter: summary, knowledge checkpoint, interview questions, exercises, design challenges, references, open verification items.

## 6.3 Numbering conventions

| Element | Format | Example |
|---|---|---|
| Chapter | `Chapter N` | Chapter 20 |
| Section | `N.M` | 20.11 Cache stampede |
| Figure | `Figure N.K` | Figure 20.4 |
| Table | `Table N.K` | Table 20.2 |
| Case study | `N.M` with 16 sub-sections `N.M.1–N.M.16` | 52.1.4 Capacity estimation |
| Practice question | `Q-T-NN` (traditional), `Q-ML-NN` (ML/AI) | Q-ML-17 |
| Project | `P-NN` | P-07 Distributed KV store |
| Planning documents | `Figure P.K`, `Table P.K` | Table P.3 |

## 6.4 Visual design (applied by the build)

| Element | Treatment |
|---|---|
| Body text | Serif (Source Serif / Georgia fallback), 10.5 pt print, line-height 1.55, max line ≈ 75 characters |
| Headings | Sans (Inter), dark navy `#1B2A4A`; chapter titles 26 pt with rule |
| Technical concepts / definitions | Blue `#1F5FA8` left border on pale blue `#EEF4FB` |
| Architecture insights / industry | Teal `#127A7A` border on `#ECF6F6` |
| Recommendations / interview tips | Muted green `#3C7A4A` border on `#EEF5EF` |
| Warnings / trade-offs / mistakes | Amber `#B7791F` border on `#FBF4E6` |
| Background notes / worked examples | Light grey `#F4F5F7` with grey border |
| Summary | Navy border on pale navy |
| Code | Monospace (DejaVu Sans Mono), 9 pt, grey background, syntax highlighted (pandoc `tango`) |
| Tables | Header row navy-tinted, repeated on each printed page (`thead { display: table-header-group }`), zebra rows |
| Diagrams | Rendered from Mermaid to SVG (HTML/PDF) and PNG (DOCX), centered, never clipped (max-width 100%) |
| Page | A4/Letter-compatible margins 22 mm; running page numbers; chapters start on a new page |
