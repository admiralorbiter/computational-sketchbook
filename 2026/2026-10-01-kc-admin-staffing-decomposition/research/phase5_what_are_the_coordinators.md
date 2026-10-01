# Phase 5: "What Are the Coordinators?" — Functional and Institutional Decomposition

## 1. Research Context and Methodological Shift

In Phases 1 through 4, this initiative conducted a rigorous econometric and fiscal decomposition of administrative staffing intensity across 55 balanced regular public school districts in the 9-county bi-state Kansas City metropolitan area (2014–15 to 2023–24). The central empirical finding of that work was certified and frozen:
- **Central line administration (`LEAADM`) remained inelastic:** Growing by only +12.5% (+22.0 FTE) across 55 districts, functioning as rigid organizational overhead.
- **School building administration (`SCHADM`) scaled with physical plant:** Adding +23.7% (+249.8 FTE), or roughly ~1.91 administrators per school facility.
- **The primary locus of non-classroom workforce expansion was Instructional Coordinators and Supervisors (`CORSUP`):** Expanding by **+51.0% (+255.5 FTE)** pre-break, accounting for **48.45% of net supervisory growth**.

Phase 5 marks a deliberate methodological shift: **transitioning from econometric measurement to descriptive and institutional analysis**. The question is no longer *whether* the coordinator expansion occurred, but *what these professionals actually do*, *how authority and responsibilities are structured*, *how districts financed the positions*, and *which portions of this infrastructure survived the post-ESSER fiscal cliff*.

---

## 2. Four Guiding Research Questions

1. **Role-Level Crosswalk:** What specific job titles, functional responsibilities, and administrative loci comprise the aggregate NCES CCD `CORSUP` reporting line?
2. **Reconstructed Staffing Architectures:** How do school systems organize the supervisory layer between classroom teachers and central executives across distinct institutional archetypes?
3. **Funding Provenance:** What combinations of local operating tax receipts, federal categorical grants (Title I, Title II, Title III, IDEA), and emergency relief funds (ESSER I, II, III) enabled districts to create these positions?
4. **Post-ESSER Survival (2024–25 to 2026–27):** Which parts of the instructional-support infrastructure became permanent features of district organization, and which were genuinely temporary grant-funded expansions that were eliminated or restructured when COVID-19 relief expired?

---

## 3. Primary Evidence Sources & State Reporting Regimes

### 3.1 State Administrative Data Systems
- **Kansas State Department of Education (KSDE) — Superintendent’s Organization Report (SO66):**
  - KSDE collects licensed and non-licensed personnel assignments annually via the SO66 system.
  - Job classifications corresponding to NCES CCD `CORSUP` include: *Instructional Coach*, *Curriculum Specialist / Supervisor*, *Reading / Math Intervention Specialist*, *Bilingual / ELL Specialist*, *Technology Coordinator*, and *Assessment / Test Coordinator*.
  - KSDE distinguishes building-level instructional coaches from central curriculum directors, though both roll up into federal line `CORSUP`.
- **Missouri Department of Elementary and Secondary Education (DESE) — Core Data / MOSIS Screen 18:**
  - Missouri reports personnel using standardized position codes:
    - `Position Code 10`: Superintendent and Assistant Superintendent (rolls up to NCES `LEAADM`).
    - `Position Code 20`: Principals and Assistant Principals (rolls up to NCES `SCHADM`).
    - `Position Code 30`: Supervisor of Instruction (rolls up to NCES `CORSUP`). Designated for licensed personnel employed in the supervision of instruction or both teaching and supervision.
    - `Position Code 40`: Classroom Teachers.
    - `Position Code 60`: Instructional and Student Support Specialists.

### 3.2 District Primary Filings & Board Documents
- **Shawnee Mission USD 512:**
  - *2019–2024 Strategic Plan:* Established personalized learning and coaching framework.
  - *ESSER Allocation Plan (August 2021):* Authorized ~$10M in ESSER funding to hire ~50 instructional coaches, social workers, and building substitutes.
  - *March 2026 Board of Education Budget Workshop:* Superintendent Dr. Michael Schumacher announced the denial of all 113.3 FTE staffing requests (freezing instructional coaching, interventionist, and IT expansions).
- **Kansas City USD 500 (KCKPS):**
  - *Leadership & Learning Department Organizational Framework:* Directs curriculum, Diploma+ initiatives, and professional learning.
  - *Title I Schoolwide Plans & At-Risk Expenditure Filings:* Documents 36+ school-based Title I reading/math coaches and 22+ MTSS academic intervention specialists.
  - *2023–2024 Performance Accountability & Better Every Day Reports:* Establishes rationale for adding assistant principals and deans of students to address acute chronic absenteeism and post-pandemic climate disruptions.
- **Olathe USD 233:**
  - *Board of Education Budget Profiles (FY 2024 to FY 2027):* Documents post-ESSER budget realignment, including the reduction of ~23.6 coordinator FTE in 2024–25 (from 85.55 to 61.95 FTE) and reassignment back to classroom vacancies.
  - *Kansas Through-Year Curriculum-Directed (TYCD) Assessment Implementation Plans:* Maps instructional learning facilitators supporting state-aligned assessment modules.
- **North Kansas City 74:**
  - *Comprehensive School Improvement Plan (CSIP) & Finance Reports:* Details the absorption of discipline-specific content coordinators and 10 instructional tech coaches into local property tax funds (59% local revenue share).
  - *FY 2027 Budget Outlook:* Outlines emerging $16M structural gap driven by state funding shortfalls.
- **Raytown C-2:**
  - *2017–2022 CSIP Goal 1:* Formally codified dual Assistant Superintendents (Instructional Leadership - Elementary and Secondary), 5 central directors, and 7 discipline-specific K–12 coordinators.
- **Lee's Summit R-VII:**
  - *Board Organization & Salary Schedules:* Demonstrates reliance on classroom Department Chairs (stipend/release structure) and building assistant principals rather than standing non-evaluative instructional coaching cadres.

---

## 4. Organizational Archetypes & The KCKPS–SMSD Centerpiece

Our analysis reconstructs the non-classroom supervisory architecture across six distinct institutional archetypes:

```mermaid
graph TD
    subgraph Kansas City USD 500 (KCKPS)
        KCK_HQ[Lean Central Line: 6.0 FTE] --> KCK_SCH[Dense Building Admins: 141.0 FTE<br>3.28 per school - Direct Authority]
        KCK_SCH --> KCK_CO[106.8 FTE Coordinators & Interventionists<br>Title I, At-Risk, Bilingual Categoricals]
    end

    subgraph Shawnee Mission USD 512 (SMSD)
        SMSD_HQ[Central Line: 13.0 FTE] --> SMSD_SCH[Building Admins: 95.5 FTE<br>2.12 per school]
        SMSD_HQ --> SMSD_DEP[Curriculum Department]
        SMSD_DEP --> SMSD_CO[123.7 FTE Coaching Overlay<br>~50 Non-Evaluative Building Coaches<br>ESSER III + Local Tax Transition]
    end
```

### 4.1 Shawnee Mission USD 512 — The Specialized Coaching Overlay
- **Structural Philosophy:** The district layered a dense instructional coaching and technology integration overlay on top of classroom teachers without altering traditional administrative command structures.
- **Authority Dynamics:** Instructional coaches operate outside the administrative evaluation hierarchy. They do not evaluate teachers or issue disciplinary reprimands; their role is strictly collegial and pedagogic (planning, model teaching, data analysis).
- **Vulnerability:** Because ~50 coaching positions were scaled using temporary federal ESSER III grants, the district faced a severe local absorption hurdle upon grant expiration in 2024. Although initially absorbed, it triggered a complete hiring and expansion freeze by March 2026.

### 4.2 Kansas City USD 500 (KCKPS) — Distributed School Supervision
- **Structural Philosophy:** Rather than keeping authority at headquarters or creating an advisory coaching layer, KCKPS pushed administrative authority directly into school buildings. It created the densest building-level supervisory architecture in the region (141.0 FTE / 3.28 admins per school across 43 schools).
- **Authority Dynamics:** Assistant Principals and Deans of Students exercise direct evaluative, disciplinary, and operational authority to address urgent attendance, behavioral, and student trauma challenges on-site.
- **Vulnerability:** Because KCKPS financed its 100+ coordinator footprint through permanent federal Title I, Title III, IDEA, and Kansas State At-Risk headcount weightings, it experienced zero post-ESSER contraction. Coordinator FTE held at 120.96 FTE in 2024–25.

### 4.3 Summary Matrix of the Six Archetypes
1. **Shawnee Mission USD 512 (KS):** *Specialized Coaching Overlay* (Peak 123.7 FTE CORSUP; absorbed with budget freeze).
2. **Kansas City USD 500 (KS):** *Distributed School Supervision* (106.8 FTE CORSUP + 141.0 FTE SCHADM; permanent formula funding).
3. **Olathe USD 233 (KS):** *Suburban Scaling & Retrenchment* (Peak 85.6 FTE $\to$ cut to 62.0 FTE post-ESSER; coaches returned to classrooms).
4. **North Kansas City 74 (MO):** *Rapid Growth Departmental Hierarchy* (36.6 FTE $\to$ 37.9 FTE; absorbed locally via enrollment and property tax growth).
5. **Raytown C-2 (MO):** *Layered Curriculum Leadership* (16.8 FTE; inelastic central hierarchy retained despite enrollment loss).
6. **Lee's Summit R-VII (MO):** *Lean Comparator / Department Chair Model* (11.0 FTE; resisted coaching expansion, zero post-ESSER disruption).

---

## 5. Canonical Data Artifacts Generated in Phase 5

1. [`data/processed/coordinator_role_crosswalk.csv`](../data/processed/coordinator_role_crosswalk.csv): Detailed mapping of 29 discrete job titles across the 6 focal districts, specifying estimated FTE, function, locus, and funding stream.
2. [`data/processed/district_staffing_architectures_6archetypes.csv`](../data/processed/district_staffing_architectures_6archetypes.csv): Comparative institutional matrix detailing student scale, school counts, supervisory ratios, authority models, and post-ESSER trajectories.
3. [`data/processed/post_esser_coordinator_survival.csv`](../data/processed/post_esser_coordinator_survival.csv): Longitudinal tracking of coordinator headcount from 2023–24 peak into 2024–25, classifying disposition into Retrenched, Absorbed, or Formula Permanent.
4. [`outputs/tables/coordinator_functional_decomposition_report.md`](../outputs/tables/coordinator_functional_decomposition_report.md): Final research synthesis and institutional report.
