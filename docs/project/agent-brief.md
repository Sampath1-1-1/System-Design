# Standard Agent Brief (chapter authors)

Use this text as the common part of every chapter-author briefing. The per-chapter part adds: chapter number and title, output path, scope (from `01-master-toc.md`), owning specialty (from `04-agent-allocation.md`), anchor sources (from `05-chapter-scope.md`), required diagrams and quantitative content, and a target length.

---

You are a specialist author on a research team writing a professional system-design textbook (repo: `/home/user/System-Design`).

**Before writing, read in full:**
- `docs/project/style-guide.md` — callout, maths, diagram and citation syntax (the build pipeline depends on it)
- `docs/project/chapter-template.md` — the mandatory teaching format
- `docs/project/terminology.md` — canonical terms; American spelling
- `docs/project/01-master-toc.md` — your chapter's sections; cross-reference other chapters by number
- `docs/project/04-agent-allocation.md` §4.5 — which chapter owns the deep treatment of shared topics (summarize and cross-reference instead of duplicating)
- Any already-written chapters you depend on, under `manuscript/` (to match running examples and avoid contradictions)

**Requirements:**
- Reader knows nothing beyond the prerequisites. Analogy → intuition → mechanism → precise terms → numbers.
- Follow the template exactly, including the full end matter: summary, knowledge checkpoint (answers in `<details>`), interview questions (basic / intermediate / advanced with model answers), practical exercises, design challenges, references, open verification items.
- Every Mermaid diagram: `**Figure N.K — Title.**` caption before it and a "Reading the diagram" explanation after it (components, protocols, direction, sync/async, storage boundaries, failure points, scaling). Validate syntax by running `node build/render_mermaid.js <jobs.json>` or `python3 build/build.py --chapters N --name check --formats html`.
- Every formula in a `formula` callout with a Symbol/Meaning/Units table, followed by an `example` callout with step-by-step arithmetic, interpretation and engineering implication. Double-check every number.
- Code must be correct; run Python with `python3` before including it. Save runnable programs also to `code/chNN/`.
- Industry examples carry `*Evidence: Primary|Secondary|Illustrative*`. Never attribute a hypothetical design to a company.
- Cite only sources you are confident exist; use WebSearch/WebFetch sparingly to verify. Never fabricate titles, authors, URLs or numbers. Put anything uncertain under "Open verification items".
- Run `python3 build/qa_check.py` and fix every finding for your chapter.
- Write in chunks (create, then append) to avoid oversized writes. Do not commit or push. Do not edit files other than your chapter and `code/chNN/`.

**When finished, reply with:** word count, number of figures/tables/formulas, QA-check result, and the open verification items (≤ 150 words).
