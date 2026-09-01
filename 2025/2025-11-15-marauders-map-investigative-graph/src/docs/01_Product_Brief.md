# 01 — Product Brief

## Vision
Marauder’s Map is a single‑user investigative mapping tool that lets you map **people, organizations, places, and events**, visualize how they interconnect on a **map** and a **network graph**, and perform **search, enrichment, and analysis** to discover influence pathways.

## Problems we solve
- Research is scattered across notes, spreadsheets, and bookmarks.
- It is hard to **see** geographic and network context together.
- Imports and enrichment often introduce duplicates and weak provenance.
- Graph analysis needs to be explainable and adjustable (not a black box).

## Target personas
- **Researcher/Investigator** — curates entities and relationships, validates facts, needs provenance and safe edits.
- **Analyst** — explores the graph, runs path/centrality/cluster analysis, exports findings for reports.
- **Curator** — imports external CSVs, cleans data quality, sets vocabularies and tags.

## Scope (v1)
- Entity & relationship authoring
- Map, graph, and hybrid views
- Smart search patterns and geo/temporal filters
- Wikipedia + Wikidata enrichment (review‑first)
- On‑demand analysis: shortest path, power path, centrality, clusters
- Workspaces with last‑view restore
- CSV/JSON import/export, idempotent
- Command palette and keyboard shortcuts

## Non‑goals (v1)
- Multi‑user roles/permissions
- Cloud sync or real‑time collaboration
- General web scraping beyond Wikipedia/Wikidata

## Success metrics & SLOs
- 90% of searches respond in < 200 ms.
- “Find path” (≤ 1K nodes) completes in < 1.5 s.
- ≥ 95% enrichment actions can be applied with one review pass.
- Daily backup age < 24 h; restore verified on each release.
- 0 critical data‑loss incidents in last 90 days.
