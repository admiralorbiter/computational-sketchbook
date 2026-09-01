# SKIEN — Evolving News & Epistemic Graph Ontology (September 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / ONTOLOGY & KNOWLEDGE GRAPH PROTOTYPE]`  
> **Date:** September 29–30, 2025  
> **Stack:** Python 3, Flask, SQLAlchemy, SQLite, Jinja2, Bootstrap  
> **Original Origin:** `admiralorbiter/skien` (HEAD: `357becc`)  

---

## 1. The Core Intellectual Breakthrough: Story vs. Event/Claim

*SKIEN* was conceived to transition personal news and research consumption from flat spreadsheet rows into an evolving semantic graph:

> *"A log remembers what I consumed. Can I instead preserve how my understanding of an evolving situation was assembled over time?"*

### The Fundamental Epistemic Separation:
```text
           [ STORY ] (Raw Evidence Source)
         (URL, Publication Date, Capture Date, Text)
                             │
                             ▼ (Extracts / Supports)
        [ EVENT / CLAIM ] (Semantic Proposition)
   "X announced Y" / "Company filed Z" / "Study showed W"
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     [ TYPED RELATIONSHIPS ]        [ TEMPORAL THREADS ]
  ├── follow_up                  ├── Narrative progression
  ├── clarifies                  ├── Chronological synthesis
  ├── refutes                    └── Multi-topic aggregation
  ├── repeats
  └── action
```

- **Story $
e$ Event/Claim:** A news article is raw evidence, not the event itself. Multiple articles can support one claim; one article can generate multiple claims. Later articles can clarify or refute earlier claims.

---

## 2. Ingestion Pipeline & Friction Tradeoff

- **The Capture vs. Structuring Dilemma:** A Google Sheet has zero capture friction (*read $	o$ paste URL $	o$ add note*). SKIEN demanded high cognitive taxonomy overhead at capture time (choosing topic, thread, claim, edge types).
- **The Modern Inversion:** In 2025, ontology had to be hand-annotated; modern agentic systems invert this tradeoff by inferring the epistemic graph retroactively from raw immutable evidence traces.

---

## 3. Stopping Point & Architecture State

- **Implemented:** Full relational schema across `Story`, `EventClaim`, `Thread`, `Topic`, `Edge`, CSV ingestion mapper, and CRUD views.
- **Unfinished:** Graph visualization (Cytoscape), interactive timeline UI, and semantic search.
- **Preserved Artifacts:** Full SQLAlchemy models (`flask_app/models/`), comprehensive specifications (`docs/product_spec_v_0.md`), and database architecture (`docs/database_schema.md`).
