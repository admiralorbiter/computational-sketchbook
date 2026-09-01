# 11 — KC Preset & Scalability

## KC-first without hard‑coding
- **Quick action**: “Center on KC” map control sets viewport to a saved KC bounding box.
- **Workspace template**: initial workspace seeds KC viewport/zoom; can be overridden by last‑view restore.
- **Tag suggestions**: optional KC‑specific tags (e.g., neighborhood names) through a tag preset list.

## Data‑type agnosticism
- Core types remain: person, organization, place, event.
- Extend via a **type registry**: add new types with metadata schema and icon/color, plus allowed relationship pairs.
- Store unknown or emergent fields under `metadata.extra` to avoid schema churn; promote fields to top‑level when they stabilize.

## Scale considerations
- Keep FTS index slim (only necessary fields); store large text in metadata but avoid indexing everything.
- Enforce LOD policies (SVG/Canvas switch, label hiding) and debounced queries as the graph grows.
