# Requirements Workbench (Interactive SWEBOK Labs)

**Date:** July 31, 2026  
**Original Path:** pilot/software-engineering/site/labs/ (in Big-Brain-Time)  
**Final Status:** Consolidated to Sketchbook. *Educational content extracted; browser application retired.*

---

## 1. The Original Question

> **Can an interactive browser workbench improve requirements engineering education by combining live heuristic text critique, combinatorial logic-space exploration, and visual change-impact traceability around a single shared scenario?**

When studying or teaching software requirements (IEEE SWEBOK v4.0 Knowledge Area 01), learners struggle with three common gaps:
1. **Critique gap:** Recognizing vague modals ("should"), undefined actors ("staff"), unmeasured speed ("quickly"), and solution statements masquerading as requirements.
2. **Logic-space gap:** Overlooking boundary combinations when business rules involve multiple boolean or categorical conditions.
3. **Traceability gap:** Visualizing how a localized policy change (e.g. changing an attendance lock window) ripples through upstream needs, downstream components, test suites, and metrics.

The Requirements Workbench was built as an interactive companion to explore whether client-side browser tools could bridge these three gaps through an integrated case study.

---

## 2. What Was Built

The prototype implemented three browser-based labs and a shared project engine:

- **Shared Project Engine (labs.js, labs.css, labs/index.html):** Managed workspaces using browser localStorage (bt_lab_projects), provisioned a starter project (*Pathways Community Programs Hub*), and exported project bundles as JSON.
- **Lab 1: Requirement Clinic (labs/clinic/):** A 5-step wizard that ran 20 deterministic regex rules against user input, highlighted flagged anti-patterns in real time, guided structured rewrites in EARS syntax (Easy Approach to Requirements Syntax), and assigned maturity levels.
- **Lab 2: Decision Table Studio (labs/decision-table/):** Computed the full Cartesian product across condition variables (e.g., 3 roles × 3 session states × 2 period states = 18 rules), allowed learners to cycle cell states (unresolved, Yes, No, N/A, Impossible), tracked coverage, and generated Given-When-Then Gherkin scenarios.
- **Lab 3: Evidence Map (labs/evidence-map/):** Rendered a 30-node directed graph via Cytoscape.js modeling relationships across 9 artifact types (goal, 
eed, equirement, ssumption, decision, component, 	est, metric, incident), and ran Breadth-First Search (BFS) traversals to simulate downstream change impact.
- **Capstone Curriculum (ttendance-correction.json):** A 4-stage narrative scenario following an attendance-correction policy change from stakeholder complaint through clinic critique, decision table, and trace graph impact.

---

## 3. Useful Example: Requirement Transformation

The core value of the experiment is demonstrated in how a raw, ambiguous stakeholder complaint transforms into an auditable specification.

### Input: Raw Stakeholder Request
> *"The system should allow staff to quickly update a completed session."*

### Heuristic Rule Flags Identified
1. weak-modal — *"should"* conveys ambiguity about whether attendance correction is mandatory or optional.
2. undefined-actor — *"staff"* fails to distinguish between authorized Program Administrators, temporary volunteers, and school coordinators.
3. ague-speed — *"quickly"* lacks an SLA or latency threshold.
4. undefined-term — *"completed session"* does not define whether locked or closed reporting periods can be reopened.

### Guided Critique Questions
- Does "should" mean mandatory or optional?
- Which specific staff roles qualify to make updates?
- What measurable response time does "quickly" imply?
- Can all completed sessions be changed, or only open reporting periods?

### Transformed EARS Statement
`	ext
WHEN an authorized Program Administrator discovers an attendance error,
THE session-management system SHALL permit the administrator to amend student or volunteer attendance
WHILE the reporting period remains open,
AND record previous and revised values in the audit history.
`

### Generated Given-When-Then Acceptance Scenario
`gherkin
Scenario: Amend session attendance within open reporting period
  Given a completed session in an open reporting period
  And the user has the Program Administrator role
  When the user amends volunteer attendance
  Then the updated attendance shall be saved
  And an audit trail entry shall record previous and revised values.
`

---

## 4. Preserved Content Files

The educational datasets have been preserved directly in their native JSON format:

| File | Description |
| :--- | :--- |
| [exercises.json](exercises.json) | 8 graded requirement-quality exercises with raw text, detected issues, guided critique questions, and improved EARS statements across volunteer platforms, e-commerce, banking, and public services. |
| [ules.json](rules.json) | 20 heuristic regex rules detecting requirement smells (vague modals, missing triggers, unmeasured bounds, hidden conjunctions, premature tech solutions). |
| [ttendance-correction.json](attendance-correction.json) | 4-part capstone journey connecting critique, combinatorial rule expansion, graph tracing, and policy change simulation. |
| [decision-table-cases.json](decision-table-cases.json) | 3 multi-variable condition/action rule sets (Pathways attendance, ATM withdrawal, course registration) for combinatorial expansion. |
| [evidence-map-graph.json](evidence-map-graph.json) | Complete 30-node directed traceability graph connecting goals, needs, requirements, design decisions, tests, and metrics. |

---

## 5. What Was Learned & Why It Stopped

1. **The curriculum is durable; the browser application is disposable.** The intellectual value of the experiment was in the pedagogical examples, the 20 heuristic rules, and the multi-step transformation model. The custom client-side JavaScript wizard added maintenance friction without adding insight.
2. **Local storage silos break the primary workflow.** Storing exercise results in browser localStorage disconnected the learner's work from the actual substrate (plain Markdown documents). Exporting JSON files without seamless bidirectional markdown sync meant work created in the tool was effectively trapped.
3. **Application bugs in the discarded code:**
   - The clinic's acceptance-criteria generator supplied a hardcoded Pathways attendance scenario regardless of what requirement was entered.
   - The evidence map's sidebar button passed a PointerEvent object where a string ID was expected, silently failing the BFS traversal.
   - The site search inputs were unfunctional placeholders.
4. **Conclusion:** An experiment can be finished even when its software is unfinished. Retiring the browser UI removes ~55 KB of fragile client code while keeping 100% of the educational content ready for reference in Markdown-based workflows.
