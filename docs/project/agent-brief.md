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
- Code must be correct; run Python with `python3` before including it. Code lives only inside the chapter; do not create separate code files.
- Industry examples carry `*Evidence: Primary|Secondary|Illustrative*`. Never attribute a hypothetical design to a company.
- Cite only sources you are confident exist; use WebSearch/WebFetch sparingly to verify. Never fabricate titles, authors, URLs or numbers. Put anything uncertain under "Open verification items".
- Run `python3 build/qa_check.py` and fix every finding for your chapter.
- Build side effects: `build.py` regenerates `manuscript/appendices/A-glossary.md`. After any check build, run `rm -f dist/check.* && git checkout -- manuscript/appendices` so you leave only your chapter's changes.
- Length is measured by `qa_check.py` (counts everything outside code blocks, including tables and references). Stay within the stated target on that count.
- Write in chunks (create, then append) to avoid oversized writes. Do not commit or push. Do not create or edit any file other than your chapter.

**When finished, reply with:** word count, number of figures/tables/formulas, QA-check result, and the open verification items (≤ 150 words).

## Book II additions (Chapters 57–86)

- Output folder: `manuscript/book2-ml-ai/NN-slug.md` (slug from `build/book.yaml`).
- Running example for Book II: **QuickBite** (the food-delivery app from Ch 2, 18, 39–44) — use its ML problems (delivery-time/ETA prediction, restaurant and dish recommendations, fraud detection, demand forecasting, support chatbot) where an example is needed; keep numbers consistent across chapters and state them as assumptions.
- Available for runnable examples: Python 3 with NumPy, scikit-learn and PyTorch (CPU only). Run scikit-learn code with `OMP_NUM_THREADS=1` (threading can stall in this container). Keep examples small (seconds to run on CPU) and deterministic (fixed seeds).
- Book I chapters own systems concepts (caching, queues, Kafka, Kubernetes, observability, etc.); cross-reference them by section number rather than re-teaching.
- QuickBite shared assumptions (set in Ch 2/18 and Ch 57; reuse, don't change): 500,000 orders/day; ~60 orders/s peak; ~7,000 browse RPS at peak; ~4 million weekly active users; 0.5% fraud rate on orders; 35-minute median delivery time (ETA target); 10 million registered customers (for embedding-table sizing, set in Ch 58); 50,000 restaurants; 50,000 registered couriers; 4,000 delivery zones (Ch 62); 4% of orders get a written review (~20,000/day, Ch 63); support chatbot: continued pre-training of a 7B model on 50B tokens (Ch 65); recommendations: 2,500 requests/s at peak, ~1,200 deliverable restaurants (120,000 dishes) per address, 120 ms server-side p99 budget (Ch 68); fraud model flags 0.7% of orders at launch with 50% precision and 70% recall (Ch 70); support chatbot RAG: 75,000 queries/day, 8 QPS peak, 8.6M-token knowledge corpus (25,800 chunks), token prices $0.20/M input and $0.60/M output (Ch 75); chatbot model: Llama-2-7B shape (32 layers, 32 KV heads, 6.74B params, 13.5 GB BF16, KV 524 KB/token), 10,000 conversations/day, 200 concurrent at peak, ~9,063 input + 468 output tokens per conversation (Ch 72); ETA predictions: 2,000 search RPS × 20 restaurants = 40,000 predictions/s at peak, ~360 million/day, ~720 per order (Ch 2 §2.4, Ch 60).
