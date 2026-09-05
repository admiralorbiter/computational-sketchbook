# Origin: Requirements Workbench (pilot/software-engineering/site/labs/)

- **Original Repository:** https://github.com/admiralorbiter/Big-Brain-Time
- **Original Path:** pilot/software-engineering/site/labs/
- **Date Created / Tested:** July 31, 2026 (Commit: 1696920)
- **Consolidated into Sketchbook:** 2026-09-05
- **Tech Stack:** Vanilla JavaScript (ES6), HTML5, CSS3, Cytoscape.js (CDN), JSON datasets

---

## 1. Concept & Scope

Explored an interactive, browser-based requirements engineering workbench accompanying the IEEE SWEBOK v4.0 pilot. Implemented three interconnected tools:
1. **Requirement Clinic:** Live heuristic text analysis against 20 regex-based anti-pattern rules, EARS syntax restructuring, and maturity classification.
2. **Decision Table Studio:** Cartesian product logic-space generator, state-cycling matrix, and Gherkin Given-When-Then acceptance scenario exporter.
3. **Evidence Map:** 30-node directed graph visualizing traceability from goals to tests/metrics, featuring BFS change-impact simulation.

---

## 2. Preserved Curricular Artifacts

Rather than retaining the client-side JavaScript application, the educational data files are preserved intact:
- exercises.json: 8 graded requirement critique exercises.
- ules.json: 20 heuristic analysis regex rules.
- ttendance-correction.json: 4-part capstone scenario.
- decision-table-cases.json: Combinatorial decision rule sets.
- evidence-map-graph.json: 30-node full traceability graph.

---

## 3. Why It Stopped

- The browser application lived in a disjoint silo (localStorage), failing to integrate into the primary Antigravity $\to$ Markdown workflow.
- Critical interaction bugs (click-event target in graph simulation, hardcoded acceptance criteria in clinic, broken import) proved that maintaining client-side state wizards distracted from the durable curriculum itself.
