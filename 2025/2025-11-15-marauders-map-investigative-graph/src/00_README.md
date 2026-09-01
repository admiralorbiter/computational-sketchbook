# Marauder's Map — Documentation Set (v1.2)
**Date:** November 16, 2025

This package is a complete, implementation-ready documentation set for the Marauder's Map Flask application. It is designed to be **KC‑first** (quick center on Kansas City) while remaining **data‑type‑agnostic** and scalable. The content focuses on **systems, decisions, flows, and acceptance**. The Slice 0 implementation in this repository provides a minimal but runnable skeleton that follows these docs.

## How to use this repo

- To run the app (Slice 0–2):
  - `pip install -r requirements.txt`
  - `python run.py`
- Then open `http://localhost:5000` in your browser:
  - Slice 0: minimal skeleton (health + entities).
  - Slice 1: entities CRUD + live search.
  - Slice 2 (planned): map canvas for entities + relationships; see `planning.md`.
- Use `commands.md` for common dev commands.

## How to use this doc set
- Start with **01_Product_Brief.md** and **02_System_Architecture.md** to understand the scope and system shape.
- Use **03_Data_Governance_and_Schema.md** and **12_Import_Export_Dedupe.md** when shaping data and ingesting sources.
- Use **04_Search_and_Enrichment.md** and **05_Visualization_and_Analysis.md** when designing user flows and analysis behavior.
- Use **07_Runbook_Operations.md** for backups, restores, health checks, and environment notes.
- Use **08_Vertical_Slices_Playbooks.md** and **09_Acceptance_Criteria_Checklists.md** to plan and ship vertical slices.
- Use **10_Risks_ADRs.md** to track decisions, and **11_KC_Preset_and_Scalability.md** to keep KC defaults without hard‑coding.
- **15_Glossary.md** provides canonical terms.

## Decision log (v1.2)
- Startup view restores **last workspace view**; add a quick **Center on KC** action.
- Entities are **unique per workspace** by `(normalized_name, entity_type)`.
- Relationships use a **controlled vocabulary** with **alias mapping**.
- Enrichment providers: **Wikipedia + Wikidata**, review-first, cached 30 days.
- **Encryption optional** (DB off by default). **Encrypted backups on** by default.
- Attachments allowed (images, PDFs, CSVs) with size/content controls.
- Imports are **robust and idempotent** (staging + dry‑run + dedupe).
- Analysis runs **on demand** with cached results.
- Edge **strength vs. confidence** are distinct and visible.
- Command palette covers **navigation** and **admin/ops**.
- **Undo/redo** depth: ~100 actions per workspace.
- **Workspace isolation** by default; copy preserves provenance.
- KC default is a **preset**, not a schema constraint.

## File list
- 01_Product_Brief.md
- 02_System_Architecture.md
- 03_Data_Governance_and_Schema.md
- 04_Search_and_Enrichment.md
- 05_Visualization_and_Analysis.md
- 06_API_Contracts.md
- 07_Runbook_Operations.md
- 08_Vertical_Slices_Playbooks.md
- 09_Acceptance_Criteria_Checklists.md
- 10_Risks_ADRs.md
- 11_KC_Preset_and_Scalability.md
- 12_Import_Export_Dedupe.md
- 13_Security_Privacy.md
- 14_Performance_Testing.md
- 15_Glossary.md

## Printing to PDF
Open any Markdown file in a Markdown viewer and print as PDF, or copy-paste into your preferred editor. This set is also available as a single combined file: **Marauders_Map_Docs_v1.2_All-in-One.md**.

