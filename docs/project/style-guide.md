# Manuscript Style Guide

This guide is binding for every author (human or agent) who writes a chapter. The build pipeline (`build/build.py`) depends on these conventions, so deviations break the PDF/DOCX output.

## 1. File naming and front matter

- One chapter per file: `manuscript/<book>/<NN>-<slug>.md`, where `NN` is the two-digit chapter number from `docs/project/01-master-toc.md`.
- Very large chapters may be split into `NN a`, `NN b` files only with an entry in the progress tracker: `<NN>a-<slug>.md`, `<NN>b-<slug>.md`.
- Each file starts with a single level-1 heading: `# Chapter N — Title`.
- Directly under it, a status line: `> **Level:** 1–5 · **Track:** A (Traditional) | B (ML/AI) | Shared · **Estimated reading time:** X h`.

## 2. Heading hierarchy

| Level | Use | Example |
|---|---|---|
| `#` | Chapter title (exactly one per file) | `# Chapter 7 — Networking Fundamentals` |
| `##` | Numbered section | `## 7.4 TCP and UDP` |
| `###` | Numbered subsection | `### 7.4.2 The three-way handshake` |
| `####` | Template element inside a subsection (unnumbered) | `#### How it works internally` |

Sections are numbered manually (`N.M`, `N.M.K`). Never skip a level.

## 3. Mandatory chapter template

Every chapter follows `docs/project/chapter-template.md`. Chapter-level elements (learning objectives, prerequisites, summary, checkpoint, references) appear once per chapter. Substantial subtopics repeat the concept-level elements (definition → first principles → why → internals → diagram → maths → code → industry → pros/cons → alternatives → failures → misconceptions). Omit an element only when it genuinely does not apply; never omit an explanation to save space.

## 4. Callout blocks (pandoc fenced divs)

Use exactly these classes. The first line inside should be a bold title.

```markdown
::: definition
**Definition — Latency.** The time between a request being issued and its response being received, measured in units of time (ms, µs).
:::
```

| Class | Purpose | Color (rendered) |
|---|---|---|
| `definition` | Precise technical definitions | Blue |
| `concept` | Important concepts and key insights | Teal |
| `example` | Worked examples and step-by-step calculations | Light grey |
| `formula` | A formula with variable table and units | Blue (boxed) |
| `tip` | Interview tips | Muted green |
| `recommendation` | Practical engineering recommendations | Muted green |
| `mistake` | Common mistakes and misconceptions | Amber |
| `warning` | Warnings, trade-offs, pitfalls | Amber |
| `industry` | Real-world industry examples (with evidence label) | Teal |
| `note` | Background notes and asides | Light grey |
| `summary` | Summary and revision notes | Navy |

Do not nest callouts. Code blocks, lists, tables and maths are allowed inside callouts.

## 5. Mathematics

- Inline maths: `$L = \lambda W$`. Display maths: `$$ ... $$` on its own lines.
- Every formula must be followed by a variable table:

```markdown
::: formula
**Little's Law**

$$L = \lambda \times W$$

| Symbol | Meaning | Units |
|---|---|---|
| $L$ | Average number of items in the system | items |
| $\lambda$ | Average arrival rate | items/second |
| $W$ | Average time an item spends in the system | seconds |
:::
```

- Every formula needs at least one numerical worked example inside an `example` callout with step-by-step arithmetic, an interpretation, and the engineering implication.
- Use SI and binary prefixes deliberately: KB/MB/GB = 10³/10⁶/10⁹ bytes for estimation; KiB/MiB/GiB when power-of-two precision matters. State which one you use.

## 6. Diagrams

- Use fenced ```` ```mermaid ```` blocks. Supported: `flowchart`, `sequenceDiagram`, `classDiagram`, `stateDiagram-v2`, `erDiagram`, `gantt`. Avoid experimental diagram types (`architecture-beta`, `block-beta`, `C4`).
- Keep labels short (≤ 40 characters per node); use `<br/>` for line breaks inside node labels. Quote labels containing punctuation: `A["API Gateway (L7)"]`.
- Do not use parentheses, `#`, `;` or unescaped quotes in edge labels; prefer `-->|HTTPS|`.
- Precede every diagram with a caption line: `**Figure N.K — Title.**` (N = chapter, K = sequence within chapter).
- Follow every diagram with a "Reading the diagram" explanation covering: each component; protocol on each edge; direction of data flow; synchronous vs asynchronous paths (solid arrows `-->` = synchronous request/response, dotted arrows `-.->` = asynchronous/eventual); storage boundaries; failure points; scaling options.
- Standard node shapes across the book:
  - Clients/users: `C([Client])` (stadium)
  - Services: `S[Service]` (rectangle)
  - Data stores: `DB[(Database)]` (cylinder)
  - Queues/logs/streams: `Q[[Queue]]` (subroutine)
  - External systems: `E{{External}}` (hexagon)
  - Decision points: `D{Decision}`
- Group deployment boundaries with `subgraph Name ... end`.

## 7. Tables

- Precede with `**Table N.K — Title.**`.
- Comparison tables use a consistent row set where possible: What it is · How it works · Advantages · Disadvantages · Performance · Operational complexity · Cost · Use cases · Choose when.
- Keep cells short; move long explanations to prose below the table.

## 8. Code

- Fenced blocks with a language tag (`python`, `sql`, `java`, `go`, `bash`, `yaml`, `json`, `protobuf`, `text`).
- Code must be correct and runnable where presented as runnable. Mark illustrative pseudo-code with the `text` tag or a comment `# illustrative`.
- Follow each non-trivial block with "What to notice" bullets explaining the important lines.
- Longer runnable programmes also go in `code/chNN/` with the same content.

## 9. Citations and evidence

- Inline citation format: author–year in square brackets, e.g. `[DeCandia et al. 2007]`, `[Kleppmann 2017]`, `[AWS Docs: DynamoDB]`.
- Every chapter ends with `## N.X References`, a numbered list: `Authors. *Title*. Venue/Publisher, Year. URL`.
- Only cite sources you are confident exist. Never fabricate titles, authors, URLs, dates or benchmark numbers. If unsure of an exact URL, cite the title/venue/year without a URL and add the item to `docs/project/unresolved-questions.md` (via the chapter's "Open verification items" list).
- Industry examples carry an evidence label as the last line of the `industry` callout:
  - `*Evidence: Primary* — company engineering blog, paper or official docs (cite it).`
  - `*Evidence: Secondary* — reputable third-party reporting/conference summary (cite it).`
  - `*Evidence: Illustrative* — a hypothetical architecture used for teaching; not a claim about any company.`
- Never attribute an unpublished or hypothetical design to a named company.
- Flag time-sensitive facts (product features, hardware specs, prices, model capabilities) with "as of <year>".

## 10. Voice and pedagogy

- Second person, direct and calm. Assume zero prior knowledge on first introduction of any term; bold the term at its defining use.
- Analogy first, then mechanism, then precise terminology, then numbers.
- Explain *why* before *how*. Every technology is presented as an answer to an engineering problem.
- Prefer concrete numbers over adjectives ("~0.5 ms within a datacenter" rather than "fast").
- Cross-reference with explicit chapter/section numbers: "see §14.3 (Consistent hashing)".
- Use the glossary's canonical terms (see `docs/project/terminology.md`).

## 11. Chapter end matter (in this order)

1. `## N.X Summary and revision notes` (with a `summary` callout of key bullet points)
2. `## N.X Knowledge checkpoint` (10–20 questions; answers in a collapsible `<details>` block)
3. `## N.X Interview questions` (basic / intermediate / advanced, each with a model answer)
4. `## N.X Practical exercises`
5. `## N.X Design challenges`
6. `## N.X References`
7. `## N.X Open verification items` (may be "None")
