# 05 — Visualization & Analysis

## Views
- **Map (Leaflet)**: KC quick center button; markers per type; clustering when zoomed out; relationship lines (solid=current, dashed=past); edge thickness suggests strength; tooltips show role/dates/confidence.
- **Graph (D3)**: SVG up to ~500 nodes; Canvas beyond; progressive neighbor expansion past ~1K; node size by degree; focus mode (ego network up to 2 hops); Fit/Reset; legend and color keys.
- **Hybrid**: split view; synchronized selection; one detail panel.

## Accessibility
- Keyboard navigable controls; ARIA labels; Escape closes modals; status announcements (“3 entities selected”).

## Analysis behaviors
- **Shortest path**: breadth‑first search; depth limit default 5; “No path” state is explicit.
- **Power Path**: influence‑aware path that minimizes edge cost with parameters:
  - Edge cost decreases with higher **confidence** and **strength**.
  - Optional recency boost to prefer recent ties.
  - Node influence from betweenness centrality penalizes weak intermediaries.
- **Centrality**: degree, betweenness, closeness; top‑N table; node badges.
- **Clusters**: on‑demand community detection; cluster colors and isolate mode; export cluster membership.

## Explainability
- Each analysis action has an **Explain** panel:
  - For paths: show costs, which edges/nodes dominated, and alternatives considered.
  - For centrality: definitions and why top entities rank highly.
  - For clusters: algorithm summary and confidence statements.

## Performance expectations
- 60 fps interactions up to ~500 nodes (SVG); Canvas after threshold; hide labels while zoomed out; debounce search 300 ms; virtualize lists > 100 rows.
