# 9. File and Folder Organization

```text
System-Design/
├── README.md                         Project overview, how to read, how to build
├── docs/
│   └── project/                      Master project specification (planning set)
│       ├── 00-master-spec.md         Project charter and invariants (read first in every session)
│       ├── 01-master-toc.md          Canonical table of contents + crosswalk
│       ├── 02-dependency-map.md      Concept dependency graph and reading paths
│       ├── 03-research-plan.md       Research phases and waves
│       ├── 04-agent-allocation.md    Agent ownership, coordination, dedup ownership
│       ├── 05-chapter-scope.md       Per-chapter level, pages, diagrams, sources
│       ├── 06-document-structure.md  Deliverable composition and visual design
│       ├── 07-source-strategy.md     Source tiers and citation rules
│       ├── 08-qa-plan.md             Eight review passes and checks
│       ├── 09-folder-organization.md This file
│       ├── progress-tracker.md       Chapter status tracker (updated every session)
│       ├── style-guide.md            Binding authoring conventions
│       ├── chapter-template.md       Mandatory chapter/case/question/project templates
│       ├── terminology.md            Canonical terms
│       └── unresolved-questions.md   Open research questions (feeds Appendix H)
├── manuscript/                       Single source of truth (Markdown)
│   ├── front-matter/                 Preface, how to use, notation
│   ├── book1-traditional/            Ch 01–56  (NN-slug.md)
│   ├── book2-ml-ai/                  Ch 57–86
│   ├── book3-interviews/             Ch 87–93
│   └── appendices/                   Learning roadmap (E) and generated glossary (A)
├── build/
│   ├── build.py                      Build pipeline: Markdown → PDF and DOCX
│   ├── qa_check.py                   Automated QA checks (Review 1/4/5/7 helpers)
│   ├── book.yaml                     Deliverable composition (which files go into which volume)
│   ├── styles/book.css               Print/screen stylesheet (palette, callouts, tables)
│   ├── render_mermaid.js             Headless-Chromium Mermaid → SVG/PNG renderer
│   └── package.json                  Node dependencies (mermaid); node_modules is git-ignored
└── dist/                             The textbook: System-Design-Textbook.pdf and .docx
```

## Naming rules

- Chapter files: `NN-kebab-slug.md` (two-digit zero-padded chapter number).
- Split chapters: `NNa-…`, `NNb-…`.
- Never rename a chapter file without updating `build/book.yaml` and the progress tracker.
