# The Complete System Design Knowledge Base

**From absolute beginner to expert — traditional system design, distributed systems, machine-learning system design and AI/LLM infrastructure.**

This repository is the single source of truth for one engineering textbook. Every chapter is written in Markdown with Mermaid diagrams, and a build script turns them into a formatted PDF and Word document.

## Start here

| If you want to… | Open |
|---|---|
| See what the books cover | [`docs/project/01-master-toc.md`](docs/project/01-master-toc.md) |
| Know what to learn first | [`docs/project/02-dependency-map.md`](docs/project/02-dependency-map.md) and [Appendix E — Learning roadmap](manuscript/appendices/E-learning-roadmap.md) |
| Read the textbook | [`dist/System-Design-Textbook.pdf`](dist/) (or the chapter sources in [`manuscript/`](manuscript/)) |
| Check progress | [`docs/project/progress-tracker.md`](docs/project/progress-tracker.md) |
| Contribute a chapter | [`docs/project/style-guide.md`](docs/project/style-guide.md) and [`docs/project/chapter-template.md`](docs/project/chapter-template.md) |

## Structure

- **Book I — Traditional System Design and Distributed Systems** (Chapters 1–56): foundations, data systems, scalability, distributed systems, messaging, architecture, production infrastructure, expert topics and 27 case studies.
- **Book II — Machine Learning and AI System Design** (Chapters 57–86): ML foundations, data infrastructure, GPUs and distributed training, serving and optimization, MLOps, LLMs, RAG, agents, AI infrastructure and 27 case studies.
- **Book III — Interviews and Practice** (Chapters 87–93): interview framework, capacity estimation handbook, company preparation, 100+ practice questions, 20 implementation projects.
- **Appendices**: learning roadmap and glossary.

## Output

One deliverable: **the main textbook**, built to `dist/System-Design-Textbook.pdf` and `dist/System-Design-Textbook.docx`. It contains every written chapter in order, followed by the learning roadmap and the glossary. Code examples and diagrams live inside the chapters; there are no separate code or diagram files.

## Building

Requirements: Python 3.10+ with `pyyaml` and `python-docx`, pandoc ≥ 3.1, Node 18+ with Playwright/Chromium.

```bash
cd build && npm install && cd ..
```

```bash
python3 build/build.py
```

```bash
python3 build/qa_check.py --tracker
```

The build renders every Mermaid diagram with headless Chromium, regenerates the glossary from the chapters, and writes the textbook to `dist/`.
