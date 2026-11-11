# Book III Brief — Practice Libraries (Ch 91–92) and Project Handbook (Ch 93)

Applies on top of `agent-brief.md` (incl. "Book III additions"). Each of these chapters is written by **two agents in parallel**: part A writes `NN-slug.md` (front matter + first half), part B writes `NNb-slug.md` (second half + end matter). The build concatenates them.

## Numbering across the two parts

- Part A numbers figures `N.1, N.2, …` and tables `N.1, N.2, …` sequentially.
- Part B numbers figures from `N.101` and tables from `N.101` (sequentially). The integration lead renumbers part B afterwards to follow part A; always refer to figures/tables by their number, so the script can rewrite them.
- Part A has exactly one H1 (`# Chapter N — …`). Part B has **no H1**; it starts with its first `##` section.
- Section numbers are fixed below; do not renumber them.

## Per-question format (Ch 91–92)

```
### N.s.k Qk. <Title>
**Difficulty:** Easy | Medium | Hard | Expert · **Time:** 45 or 60 min · **Related:** §… (case study or owner chapter)
#### Prompt                      (as an interviewer would say it, 1–3 sentences)
#### Clarifying questions and assumptions
#### Requirements                (functional / non-functional with numbers)
#### Estimation                  (`example` callout; cite §89.x formulas, don't re-derive)
#### API and data model          (compact)
#### High-level design           (one Mermaid figure + "Reading the diagram")
#### Deep dives                  (the 2–3 points that decide the interview)
#### Trade-offs and alternatives
#### Follow-up questions         (4–6, each with a short model answer)
#### What distinguishes levels   (mid / senior / staff signals, 3–5 bullets)
```

- If the book already has a full case study for the question (Ch 52–56, 81–86) or a worked design (e.g., §60 QuickBite ETA), keep the solution **compact (~450–650 words)**: give the interview-length answer and cross-reference the case study for depth. Otherwise write a **full solution (~900–1,200 words)**.
- ML questions (Ch 92) replace "API and data model" with "Data, labels and features" and add "#### Model and evaluation" (baseline → production model; offline metrics; online test) and "#### Serving and monitoring". Follow Ch 88's ML extension.
- All numbers recomputed with python3. Designs are *Evidence: Illustrative*; company facts only as published.

## Ch 91 — Interview Practice Library I: Traditional System Design (56 questions)

Sections: 91.1 Learning objectives · 91.2 Prerequisites · 91.3 How to use this library (incl. an index table of **all 56** questions: number, title, difficulty, related sections) · 91.4 Easy (Q1–Q12) · 91.5 Medium (Q13–Q28) | **part B:** 91.6 Hard (Q29–Q44) · 91.7 Expert (Q45–Q56) · 91.8 Summary and revision notes · 91.9 Knowledge checkpoint · 91.10 Interview questions (meta: how to approach unseen prompts) · 91.11 Practical exercises · 91.12 Design challenges · 91.13 References · 91.14 Open verification items.

- Easy: Q1 URL shortener · Q2 Pastebin · Q3 Rate limiter · Q4 Distributed LRU cache · Q5 Unique ID generator · Q6 Like/view counter · Q7 Parking-lot reservation system · Q8 Real-time leaderboard · Q9 Notification service · Q10 File upload service (presigned URLs) · Q11 Feature-flag service · Q12 API gateway
- Medium: Q13 News feed · Q14 Chat/messaging app · Q15 Photo-sharing app · Q16 Typeahead/autocomplete · Q17 Web crawler · Q18 E-commerce catalog search · Q19 Ticket booking (seat reservation) · Q20 Ride-hailing dispatch · Q21 Food delivery · Q22 File sync (Dropbox-like) · Q23 Video upload and streaming · Q24 Metrics monitoring system · Q25 Distributed logging pipeline · Q26 Email service · Q27 Calendar and scheduling · Q28 Collaborative document editing
- Hard: Q29 Payment system · Q30 Stock-exchange matching engine · Q31 Distributed key-value store · Q32 Distributed message queue · Q33 Resharding a live SQL database · Q34 Global CDN · Q35 Distributed cache at very large scale · Q36 Real-time search over posts · Q37 Ad-click aggregation · Q38 Top-K heavy hitters · Q39 Multi-region active-active social app · Q40 Distributed cron/job scheduler · Q41 Live streaming platform · Q42 Proximity service · Q43 Maps and routing · Q44 Multiplayer game backend
- Expert: Q45 Globally consistent database · Q46 Distributed file system · Q47 Object storage service · Q48 Durable workflow engine · Q49 Multi-tenant SaaS platform with tenant isolation · Q50 Tracing/observability platform at exabyte scale · Q51 Zero-downtime monolith-to-microservices migration · Q52 Coordination/configuration service (consensus) · Q53 Digital wallet with double-entry ledger and reconciliation · Q54 Global edge rate limiting and DDoS protection · Q55 Lakehouse/data warehouse · Q56 Bank-grade disaster recovery (RPO 0 across regions)

Length: part A 23,000–27,000 words; part B 24,000–28,000 words (by qa_check.py, part counted alone).

## Ch 92 — Interview Practice Library II: ML and AI System Design (52 questions)

Sections: 92.1 Learning objectives · 92.2 Prerequisites · 92.3 How to use this library (index table of **all 52**) · 92.4 Easy (Q1–Q10) · 92.5 Medium (Q11–Q26) | **part B:** 92.6 Hard (Q27–Q40) · 92.7 Expert (Q41–Q52) · 92.8 Summary and revision notes · 92.9 Knowledge checkpoint · 92.10 Interview questions · 92.11 Practical exercises · 92.12 Design challenges · 92.13 References · 92.14 Open verification items.

- Easy: Q1 Email spam classifier · Q2 Movie rating prediction · Q3 Image tagging service · Q4 Sentiment analysis API · Q5 Churn prediction · Q6 Duplicate-question detection · Q7 Product categorization · Q8 Store-level demand forecasting · Q9 Language identification service · Q10 Click-through-rate prediction basics
- Medium: Q11 News feed ranking · Q12 Video recommendations · Q13 Search ranking · Q14 People You May Know · Q15 Payment fraud detection · Q16 ETA prediction · Q17 Ad CTR prediction at scale · Q18 Content moderation · Q19 Visual search · Q20 Playlist generation · Q21 Notification ranking and send-time optimization · Q22 ML query autocomplete · Q23 Dynamic pricing · Q24 Credit scoring · Q25 Metrics anomaly detection · Q26 Document OCR and extraction pipeline
- Hard: Q27 Feature store · Q28 ML training platform · Q29 Model serving platform · Q30 Real-time personalization with streaming features · Q31 Billion-scale embedding retrieval · Q32 Enterprise RAG assistant · Q33 LLM customer-support agent · Q34 Speech recognition · Q35 Machine translation · Q36 Perception data engine for autonomous driving · Q37 Experimentation platform · Q38 ML monitoring platform · Q39 Federated learning for a mobile keyboard · Q40 Two-sided marketplace matching
- Expert: Q41 LLM inference platform · Q42 LLM pre-training infrastructure · Q43 Multi-tenant fine-tuning service (LoRA) · Q44 AI coding assistant · Q45 Multi-agent orchestration platform · Q46 LLM evaluation platform · Q47 AI answer engine · Q48 GPU cluster scheduler · Q49 Billion-scale vector database · Q50 Guardrails and safety system for an LLM product · Q51 Image-generation (diffusion) service at scale · Q52 Cold-start marketplace recommendations with bandits

Length: part A 22,000–26,000 words; part B 24,000–28,000 words.

## Ch 93 — Project Handbook (20 projects)

Sections: 93.1 Beginner · 93.2 Intermediate | **part B:** 93.3 Advanced · 93.4 Expert · then end matter 93.5 Summary and revision notes · 93.6 Knowledge checkpoint · 93.7 Interview questions (talking about your projects) · 93.8 Practical exercises · 93.9 Design challenges · 93.10 References · 93.11 Open verification items. Part A starts with a short unnumbered introduction under the H1 (how to use the projects, tooling assumptions: Python 3, Docker optional, local-only), then `## 93.1`. *(Exception to the template: this chapter's learning objectives and prerequisites are given per project.)*

- 93.1 Beginner: REST API service · URL shortener · Redis-style cache · Rate limiter · Load-balancer simulation
- 93.2 Intermediate: Message queue · Distributed key-value store · Replicated database simulation · Notification service · Real-time chat
- 93.3 Advanced: Distributed job scheduler · Event-driven microservices · Real-time analytics pipeline · Recommendation engine · Distributed ML inference service
- 93.4 Expert: Distributed training platform (simulated) · Multi-tenant feature store · Production RAG system · Scalable LLM inference platform (simulated where GPUs are needed) · Multi-agent orchestration platform

Per-project format (`### 93.s.k <Project>`): Goal and learning outcomes · Prerequisites (chapter refs) · Specification (FR, NFR with measurable targets) · Architecture (Mermaid figure + "Reading the diagram") · Milestones (3–5, each with "done when") · Starter code (short, runnable Python core — run it, quote output; fixed seeds) · Test plan and load-test targets · Failure-injection exercises · Extensions · Self-assessment rubric. ~1,800–2,300 words each.

Length: part A 19,000–23,000 words; part B 21,000–25,000 words.

## Measuring your part alone

`qa_check.py` reports the two parts combined. To count one file:

```
python3 -c 'import sys,pathlib;sys.path.insert(0,"build");import qa_check;print(qa_check.check_chapter(int(sys.argv[1]),[pathlib.Path(sys.argv[2])])[0]["words"])' 91 manuscript/book3-interviews/91b-practice-library-traditional.md
```

Until both parts exist, qa_check will report missing end matter (part A) or a missing H1 (part B) and non-sequential figure/table numbers — those findings are expected; fix every other finding. Check builds: `python3 build/build.py --chapters N --name checkNN<a|b> --formats html`, then remove `dist/checkNN*` and `git checkout -- manuscript/appendices`.
