# Task 001 Audit — Grandview C-4 Public Evidence Inventory

## Status

**Task 001 is methodologically complete as a discovery/inventory phase, with explicit acquisition gates that must be resolved before post-grant or causal analysis.**

The first pass successfully identified the major public systems, built a governance census, created a source/evidence registry, and established a provisional chronology. This audit reviewed those artifacts against the repository tree and current public primary sources.

---

## What is solid

### 1. Governance census
The Simbli API extraction is real and useful.

- Raw artifact: `data/raw/grandview-c4/governance/simbli/simbli_meetings_raw.json`
- Returned meeting count: **788**
- Coverage in the current response: **February 2014 through September 2026**
- The raw response exposes meeting IDs, dates, meeting type, public status, minutes status, and encrypted meeting/site identifiers.

This is a strong backbone for Task 002 packet/minute acquisition.

### 2. Eight-layer architecture
The evidence-stack design is appropriate for the research question because it prevents a governance-language signal from being mistaken for operational persistence.

The project correctly separates:
- strategy,
- governance,
- finance,
- organization,
- operations,
- accountability,
- communication,
- outcomes.

### 3. Evidence/event registry
The use of discrete organizational behavior codes is preferable to sentiment scoring. The audit extends the taxonomy with explicit persistence/change-point codes:

- `PROGRAM_CONTINUED`
- `PARTNERSHIP_CONTINUED`
- `STAFF_RETAINED`
- `FUNDING_RENEWED`
- `LEADERSHIP_TRANSITION`

Persistence is the construct of interest, so the taxonomy must be able to observe maintenance rather than only creation and removal.

### 4. Strong verified Grandview anchors
The public record supports several high-value longitudinal anchors:

- Cohort 1 RWL membership.
- Honeywell/KCNSC advanced-manufacturing pathway evidence.
- Board approval of the current **2024–2027** strategic plan.
- December 2024 formal RWL program evaluation.
- January 2025 shared-pathway expansion.
- March 2026 superintendent succession.
- April 2026 continued RWL governance attention.
- June 2026 explicit continuation of T&L Welding plus a new healthcare training partnership.

These are enough to justify Grandview as the pilot district.

---

## Material corrections made

### A. Do not assume a Grandview post-grant period
The initial chronology used phrases such as **post-grant durability** without a district-specific grant-end record.

That is not currently justified.

The current RWL district page still lists Grandview in Cohort 1 and describes participating districts as receiving financial support. That language does not establish:
- award amount,
- award execution date,
- renewal history,
- final implementation year,
- closeout date,
- whether support changed form.

**Rule:** no Grandview observation may be labeled `post-grant` until award/budget/funder evidence resolves the lifecycle.

### B. Strategic-plan dates
The initial inventory labeled the current plan **2022–2027**.

A later district Board Brief states that the Board approved the current **2024–2027 Strategic Plan on June 20, 2024**.

The registries and case profile have been corrected. The legacy raw filename still contains `2022_2027`; rename it only after visual verification of the PDF itself.

### C. Regional MVA result was misdated and over-attributed
The initial timeline placed the regional 79% senior MVA attainment result in June 2024.

The cited RWL publication reports the **2024–25** result and was published in **2026**. It is also a **regional aggregate**, not a Grandview-specific outcome.

The corrected evidence registry keeps it as regional context only.

### D. Superintendent transition was over-interpreted
The initial evidence row stated that Dr. Stephanie Amaya explicitly identified RWL as a foundational priority.

The preserved district appointment announcement establishes the leadership transition, but not that exact RWL-priority claim.

The corrected event is `LEADERSHIP_TRANSITION` with `semantic_rwl=false`.

### E. June 2026 welding event was coded as creation
The Board Brief says the district is **continuing** its T&L Welding partnership.

That is stronger evidence for this study than a generic creation code because it directly measures persistence.

The corrected event is `PARTNERSHIP_CONTINUED`.

### F. Board Brief category contamination
`categoryId=5936` is not a clean governance corpus. The harvested index includes unrelated district news such as:
- teacher awards,
- registration help,
- summer meals,
- staffing announcements.

The original harvester also left `title` and `date_display` blank for many records.

The revised harvester:
1. treats the category page only as discovery,
2. preserves raw article HTML,
3. validates Board Brief membership from article content,
4. parses article titles/dates from the detail page,
5. emits a separate rejected-item index.

### G. Archive-status inflation
The initial registries marked several sources `archived=true` or `Harvested` even though the matching raw artifact was not present in the repository.

The audit reconciles source status with the actual Git tree.

Examples now treated as **identified, not archived** until acquired:
- full Issuu strategic plan,
- Simbli packets/agendas,
- current staff-directory corpus,
- GHS course guides,
- ASBR workbooks,
- APR/CTE state files,
- regional progress reports.

### H. Wayback coverage claims
The current raw CDX artifact contains targeted metadata, including:
- 53 returned staff-directory capture records,
- 500 returned news capture records.

Because 500 is also the old query limit, that count cannot be described as a complete archive census.

The revised Wayback collector:
- queries both apex and `www` hostnames,
- uses wildcard site queries,
- records query limits,
- deduplicates returned captures,
- explicitly flags possible truncation.

---

## Task 002 entry gates

Task 002 should begin with the following order.

### Gate 1 — Resolve the RWL funding lifecycle
Highest priority.

Search:
- district budgets and amendments,
- audit notes / grant schedules,
- board acceptance resolutions,
- Kauffman award announcements,
- grant agreements,
- funder tax filings or grant databases if needed,
- district financial ledgers available through DESE.

Desired output:

`grandview_rwl_funding_timeline.csv`

with:
- source date,
- award period,
- amount,
- fund/account code,
- restricted/unrestricted status,
- renewal,
- district match,
- closeout/end date,
- confidence.

### Gate 2 — Acquire exact governance artifacts
For priority meetings:
- 2024-12-19 RWL evaluation,
- 2025-01-16 shared pathways,
- 2025-03-20 strategic-plan review,
- 2026-04-16 RWL update,
- 2026-06-18 welding/healthcare continuation.

Archive:
- agenda,
- packet,
- presentation,
- approved minutes,
- Board Brief,
- video metadata/transcript when available.

### Gate 3 — Rebuild the Board Brief corpus
Run the revised `harvest_board_briefs.py`.

Acceptance criteria:
- every accepted record contains content-level Board Brief evidence,
- unrelated category articles appear only in the rejected index,
- title/date fields are populated where the article itself exposes them,
- corpus coverage is documented.

### Gate 4 — Staff genealogy
Re-run `wayback_archaeology.py`, choose reproducible annual/semester snapshots, then archive the actual snapshot content used for inference.

Do not infer a position disappeared simply because one Wayback snapshot is missing.

### Gate 5 — Operations and state outcomes
Acquire:
- annual GHS planning/course guides,
- pathway application materials,
- Herndon/shared-program documentation,
- DESE ASBR,
- MSIP 6 APR,
- CTE follow-up/placement data,
- district-level MVA data if publicly available.

---

## Recommended Task 002 stopping rule

Do **not** start embeddings, semantic trend scoring, event-time modeling, or institutionalization classification until:

1. grant lifecycle is resolved or explicitly declared unresolved after exhaustive search;
2. the priority Board artifacts are archived;
3. the Board Brief corpus is clean;
4. at least one operational series (course/pathway availability) and one resource series (budget/staffing) are longitudinally available.

At that point the project will have enough independent evidence streams to distinguish:

**language disappearance** from **organizational disappearance**.

That is the central measurement problem of the study.
