# The Undertow — News Narrative Intelligence & Relationship Explorer (November 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / NLP & NARRATIVE KNOWLEDGE GRAPHS]`  
> **Date:** November 2, 2025  
> **Stack:** Python 3, Flask, SQLite (FTS5), Sentence-Transformers (`all-MiniLM-L6-v2`), UMAP, HDBSCAN, spaCy, Chart.js  
> **Original Origin:** `admiralorbiter/the_undertow` (HEAD: `4fc0a88`)  

---

## 1. Project Purpose & The Automation of Narrative Epistemics

*The Undertow* is a local-first NLP intelligence platform designed to ingest raw news articles and automatically discover latent narrative relationships—semantic similarity, named entity co-occurrence, evolving storylines, and surge anomalies.

### The Evolutionary Leap from SKIEN:
```text
1. GOOGLE SHEET (Summer 2025) ──► Flat, frictionless capture ledger ("What did I read?").
2. SKIEN (Sep 2025)           ──► Hand-annotated ontology (Story ≠ Claim, typed edges). High cognitive friction.
3. THE UNDERTOW (Nov 2025)    ──► Automated narrative extraction (Embeddings + NER + HDBSCAN + UMAP + Storylines).
```

---

## 2. Implemented Intelligence Tiers

1. **P0 - Foundations & Search:** CSV ingestion, content deduplication, and SQLite FTS5 full-text indexing.
2. **P1 - Semantic Geometry:** MiniLM-L6-v2 embeddings, cosine similarity threshold graph, 2D UMAP scatter projection ("Galaxy View"), and HDBSCAN cluster auto-labeling.
3. **P2 - Narrative Intelligence:** spaCy Named Entity Recognition (PERSON, ORG, GPE), multi-tier storyline resolution (near-duplicates vs. continuations vs. related coverage), and storyline momentum scoring (*active*, *dormant*, *concluded*).
4. **P3 - State-of-the-World Monitoring:** Anomaly detection for topic surges, story reactivations, new actor emergence, and severity-ranked alert dashboards.

---

## 3. Preserved Architecture & Pipeline

- **Backend (`backend/`):** Clean separation of API blueprints, database models, and service workers (embeddings, clustering, NER, storylines, anomaly detection).
- **Frontend (`static/`):** Vanilla JavaScript visualizations including UMAP scatter galaxy, storyline timelines, and state-of-the-world alert feeds.
- **Harness (`test_pipeline.py` & `tests/`):** End-to-end pipeline verification asserting entity extraction and storyline clustering.
