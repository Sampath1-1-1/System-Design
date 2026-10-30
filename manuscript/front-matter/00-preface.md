# Preface and How to Use This Book {.unnumbered}

## Who this book is for {.unnumbered}

This knowledge base is for anyone who wants to understand how large software systems, machine-learning platforms and AI infrastructure are actually designed — from a student who has never heard of a load balancer to a senior engineer preparing for staff-level architecture work. It assumes only that you can read simple code and do high-school algebra. Every other idea — networking, operating systems, databases, distributed systems, GPUs, transformers — is built from first principles.

It is not an interview cheat sheet. Interviews are covered thoroughly (Book III), but the aim is engineering judgment: knowing *why* a technology exists, *how* it works inside, *how* it fails, and *when* to choose it over the alternatives.

## How the book is organized {.unnumbered}

- **Book I — Traditional System Design and Distributed Systems** (Chapters 1–56).
- **Book II — Machine Learning and AI System Design** (Chapters 57–86).
- **Book III — Interviews and Practice** (Chapters 87–93).
- **Appendices** — glossary, bibliography, formula handbook, diagram collection, learning roadmap, reference numbers, comparison index and open research questions.

Every chapter follows the same teaching sequence: learning objectives and prerequisites; then, for each concept, a definition, a first-principles explanation, the motivating problem, the internal mechanism, an architecture diagram, the mathematics, code, real industry use, trade-offs, failure scenarios and common misconceptions; and finally a summary, a knowledge checkpoint, interview questions, exercises, design challenges and references.

## Reading paths {.unnumbered}

| Goal | Suggested path |
|---|---|
| Complete beginner | Chapters 1 → 3 → 4 → 5 → 6 → 7 → 8 → 11, then follow Appendix E, Track 1 |
| Interview in a few months | Appendix E, Track 2 |
| Moving into ML/AI infrastructure | Appendix E, Track 3 |
| Reference use | Jump to any chapter; its Prerequisites section lists what to read first |

## Conventions {.unnumbered}

**Callouts.** Colored boxes mark the role of a passage:

| Box | Meaning |
|---|---|
| Definition (blue) | A precise technical definition |
| Formula (blue, boxed) | A formula with every variable and unit explained |
| Key concept (teal) | An important idea or architectural insight |
| Industry example (teal) | A real-world system, with an evidence label |
| Interview tip / Recommendation (green) | Practical advice |
| Common mistake / Warning (amber) | Misconceptions, pitfalls and trade-offs |
| Worked example / Note (grey) | Step-by-step calculations and background |
| Summary (navy) | Revision notes |

**Evidence labels.** Every industry example ends with one of: *Evidence: Primary* (the company's own paper, blog or documentation), *Evidence: Secondary* (reputable third-party reporting), or *Evidence: Illustrative* (a teaching design that makes no claim about any company). This book never presents a hypothetical design as a company's internal architecture.

**Diagrams.** Shapes are consistent throughout: rounded "stadium" shapes are clients, rectangles are services, cylinders are data stores, double-bordered boxes are queues or logs, hexagons are external systems, and diamonds are decisions. Solid arrows are synchronous request/response; dotted arrows are asynchronous or eventual flows. Every diagram is followed by a "Reading the diagram" explanation.

**Units.** For estimation, KB, MB, GB and TB mean 10³, 10⁶, 10⁹ and 10¹² bytes. When power-of-two precision matters, KiB, MiB and GiB (2¹⁰, 2²⁰, 2³⁰) are used and stated explicitly. Rates are per second unless stated.

**Time-sensitive facts.** Hardware specifications, product features, prices and model capabilities change quickly. Such statements carry an "as of" year; Appendix H lists claims scheduled for re-verification.
