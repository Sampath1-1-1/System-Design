# The Complete System Design Knowledge Base

**From absolute beginner to expert — traditional system design, distributed systems, machine-learning system design and AI/LLM infrastructure.**

This repository is the single source of truth for a multi-volume engineering textbook. Every chapter is written in Markdown with Mermaid diagrams. A build pipeline turns it into professionally formatted PDF, DOCX and HTML deliverables.

## Start here

| If you want to… | Open |
|---|---|
| See what the books cover | [`docs/project/01-master-toc.md`](docs/project/01-master-toc.md) |
| Know what to learn first | [`docs/project/02-dependency-map.md`](docs/project/02-dependency-map.md) and [Appendix E — Learning roadmap](manuscript/appendices/E-learning-roadmap.md) |
| Read the chapters | [`manuscript/`](manuscript/) or the built files in [`dist/`](dist/) |
| Check progress | [`docs/project/progress-tracker.md`](docs/project/progress-tracker.md) |
| Contribute a chapter | [`docs/project/style-guide.md`](docs/project/style-guide.md) and [`docs/project/chapter-template.md`](docs/project/chapter-template.md) |

## Structure

- **Book I — Traditional System Design and Distributed Systems** (Chapters 1–56): foundations, data systems, scalability, distributed systems, messaging, architecture, production infrastructure, expert topics and 27 case studies.
- **Book II — Machine Learning and AI System Design** (Chapters 57–86): ML foundations, data infrastructure, GPUs and distributed training, serving and optimization, MLOps, LLMs, RAG, agents, AI infrastructure and 27 case studies.
- **Book III — Interviews and Practice** (Chapters 87–93): interview framework, capacity estimation handbook, company preparation, 100+ practice questions, 20 implementation projects.
- **Appendices A–I**: glossary, bibliography, formula handbook, diagram collection, learning roadmap, reference numbers, comparison index, open questions, index.

## Deliverables

| # | Deliverable | Output file(s) in `dist/` |
|---|---|---|
| D1 | Master System Design Textbook | `D1-system-design-textbook.{pdf,docx,html}` |
| D2 | ML and AI System Design Textbook | `D2-ml-ai-system-design-textbook.*` |
| D3 | Learning Roadmap | `manuscript/appendices/E-learning-roadmap.md` (+ built with D1) |
| D4 | Architecture Diagram Collection | `D4-architecture-diagram-collection.{pdf,html}` + `diagrams/**/*.mmd` |
| D5 | Formula and Estimation Handbook | `D5-formula-handbook.*` |
| D6 | Project Handbook | `D6-project-handbook.*` |
| D7 | Traditional Interview Handbook | `D7-traditional-interview-handbook.*` |
| D8 | ML/AI Interview Handbook | `D8-ml-ai-interview-handbook.*` |
| D9 | Glossary | Appendix A |
| D10 | Bibliography | Appendix B / `references/bibliography.md` |

Volumes whose chapters are not written yet are skipped by the build; see the progress tracker.

## Building

Requirements: Python 3.10+ with `pyyaml` and `python-docx`, pandoc ≥ 3.1, Node 18+ with Playwright/Chromium.

```bash
cd build && npm install && cd ..
```

```bash
python3 build/build.py
```

```bash
python3 build/build.py --chapters 1-10 --name preview --formats html,pdf
```

```bash
python3 build/qa_check.py --tracker
```

The build extracts every Mermaid diagram to `diagrams/chNN/*.mmd`, renders SVG/PNG with headless Chromium, regenerates Appendix C (formulas) and Appendix D (diagrams), and writes the volumes to `dist/`.
