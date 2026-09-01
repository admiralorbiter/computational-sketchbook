Slice 1 notes
=============

- Stick with vanilla JS modules + Tailwind; no bundler yet.
- Use `type="module"` in `index.html` so we can import between JS files.
- Debounce search input at ~200 ms to feel responsive without spamming the API.
- Edit is prompt-based for now; can move to inline or modal editing in later slices.
- Map/graph modules exist only as stubs to preserve a clear structure for future work.

Slice 2 notes
=============

- Canvas is map-first (Leaflet) for Slice 2; graph view waits for Slice 3 but will reuse the same `selection` state model.
- Relationship creation UX is click-based: select source, select target, then confirm details in a lightweight editor.
- Location is optional; entities only appear on the map once `lat/lng` are set.
- Provenance for relationships is stored as JSON on the relationship row; a richer provenance editor can be added later.
- Map performance: keep behavior simple initially, add marker clustering and more advanced rendering when entity counts grow.

