# Phase 5: "What Are the Coordinators?" — Functional and Institutional Decomposition

## 1. Research Context and Methodological Shift

In Phases 1 through 4, this initiative conducted a rigorous econometric and fiscal decomposition of administrative staffing intensity across 55 balanced regular public school districts in the 9-county bi-state Kansas City metropolitan area (2014–15 to 2023–24). The central empirical finding of that work was certified and frozen:
- **Central line administration (`LEAADM`) remained inelastic:** Growing by only +12.5% (+22.0 FTE) across 55 districts, functioning as rigid organizational overhead.
- **School building administration (`SCHADM`) scaled with physical plant:** Adding +23.7% (+249.8 FTE), or roughly ~1.91 administrators per school facility.
- **The primary locus of non-classroom workforce expansion was Instructional Coordinators and Supervisors (`CORSUP`):** Expanding by **+51.0% (+255.5 FTE)** pre-break, accounting for **48.45% of net supervisory growth**.

Phase 5 marks a deliberate methodological shift: **transitioning from econometric measurement to descriptive and institutional analysis**. The question is no longer *whether* the coordinator expansion occurred, but *what these professionals actually do*, *how authority and responsibilities are structured*, *how districts financed the positions*, and *which portions of this infrastructure survived the post-ESSER fiscal cliff*.

---

## 2. Four Guiding Research Questions

1. **Role-Level Reconstruction:** How can we plausibly allocate observed CCD `CORSUP` totals across institutionally documented job titles and functional families, and what is the epistemic basis for each allocation?
2. **Reconstructed Staffing Architectures:** How do school systems organize the supervisory layer between classroom teachers and central executives across distinct institutional archetypes?
3. **Funding Provenance:** What combinations of local operating tax receipts, federal categorical grants (Title I, Title II, Title III, IDEA), and emergency relief funds (ESSER I, II, III) enabled districts to support these positions?
4. **Post-ESSER Staffing Survival:** How did coordinator staffing change between 2023–24 and 2024–25 in observed federal counts, and what subsequent governance and budget signals emerge from 2025–2027 district follow-up?

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
  - *ESSER Allocation Plan (August 2021):* Authorized ~$10M in federal ESSER relief to hire ~50 new team members across instructional coaches, elementary classroom teachers (lowering class size), social workers, and building substitutes.
  - *March 2026 Board of Education Budget Workshop:* Superintendent Dr. Michael Schumacher announced the denial of all 113.3 FTE staffing requests submitted through building needs assessments (including 79.3 FTE general staffing requests and a 34 FTE counselor proposal). The district cited multiple converging fiscal pressures—declining enrollment, reduced at-risk funding, special education underfunding, formula uncertainty, and preserving fund balance—placing a de facto freeze on further instructional coaching additions.
- **Kansas City USD 500 (KCKPS):**
  - *Leadership & Learning Department Organizational Framework:* Directs curriculum, Diploma+ initiatives, and professional learning.
  - *Title I Schoolwide Plans & At-Risk Expenditure Filings:* Documents 36+ school-based Title I reading/math coaches and 22+ MTSS academic intervention specialists.
  - *2023–2024 Performance Accountability & Better Every Day Reports:* Establishes rationale for adding assistant principals and deans of students to address acute chronic absenteeism and post-pandemic climate disruptions.
- **Olathe USD 233:**
  - *Board of Education Budget Profiles (FY 2024 to FY 2027):* Documents post-ESSER budget realignment, including the reduction of ~23.6 coordinator FTE in 2024–25 (from 85.55 to 61.95 FTE). District explanations emphasize right-sizing amid enrollment loss and special education shortfalls, with public reporting indicating coaches returned to classroom vacancies.
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
        KCK_HQ["Lean Central Line: 6.0 FTE (-3.0 below peer exp)"] --> KCK_SCH["Dense Building Administration: 141.0 FTE<br>3.28 admins/school (+55.2 FTE above peers)<br>Formal Disciplinary & Evaluative Authority"]
        KCK_SCH --> KCK_CO["106.8 FTE Coordinators & Interventionists<br>(+57.9 FTE above peers in 2023–24; 10-yr mean +56.3 FTE)<br>Supported via Title I, III, & At-Risk Categoricals"]
    end

    subgraph Shawnee Mission USD 512 (SMSD)
        SMSD_HQ["Central Line: 13.0 FTE (peer expected)"] --> SMSD_SCH["Building Admins: 95.5 FTE (2.12/school)"]
        SMSD_HQ --> SMSD_DEP["Curriculum & Instruction Division"]
        SMSD_DEP --> SMSD_CO["123.7 FTE Coaching Overlay<br>(+59.0 FTE above peers in 2023–24; 10-yr mean +17.9 FTE)<br>~50 Non-Evaluative Building Coaches<br>Scaled via ESSER III -> Local Operating Freeze"]
    end
```

### 4.1 Shawnee Mission USD 512 — The Specialized Coaching Overlay
- **Structural Philosophy:** The district layered a dense instructional coaching and technology integration overlay on top of classroom teachers without altering traditional administrative command structures.
- **Authority Dynamics:** Instructional coaches operate outside the administrative evaluation hierarchy. They do not evaluate teachers or issue disciplinary reprimands; their role is strictly collegial and pedagogical (planning, model teaching, data analysis).
- **Vulnerability & Staffing Trajectory:** After scaling coaches with ESSER III relief, SMSD initially absorbed positions into local operating funds for 2024–25 (116.04 FTE). However, broader districtwide fiscal pressures (enrollment decline, special education shortfalls, and fund balance preservation) led the district in March 2026 to deny all proposed staffing additions, placing an attrition freeze on coaching.

### 4.2 Kansas City USD 500 (KCKPS) — Distributed School Supervision
- **Structural Philosophy:** Rather than keeping authority at headquarters or creating an advisory coaching layer, KCKPS pushed administrative authority directly into school buildings. It created the densest building-level supervisory architecture in the region (141.0 FTE / 3.28 admins per school across 43 schools).
- **Authority Dynamics:** Assistant Principals and Deans of Students exercise direct evaluative, disciplinary, and operational authority to address urgent attendance, behavioral, and student trauma challenges on-site.
- **Institutional Persistence:** In the focal cases, structures supported by ongoing categorical or local funding were more persistent after ESSER, while districts with larger temporary-relief-supported expansions showed greater retrenchment or fiscal constraint. Funding mechanism remains an institutional explanation rather than a causal estimate. In KCKPS, where 90–120 coordinator FTE had been maintained across the decade under Title I, Title III, IDEA, and State At-Risk categoricals, observed staffing rose from 106.80 to 120.96 FTE (+13.3%) in 2024–25.


### 4.3 Functional vs. Locus Breakdown
- **Functional Definition:**
  - Instructional Coaching: 135.75 FTE (35.7%)
  - Intervention / MTSS: 22.00 FTE (5.8%)
  - Combined Coaching + MTSS: **157.75 FTE (41.5%)**
  - SPED / EL Program Management: 93.10 FTE (24.5%)
  - Curriculum / Content: 73.80 FTE (19.4%)
  - Instructional Technology: 35.00 FTE (9.2%)
  - Data / Assessment: 14.71 FTE (3.9%)
  - Federal Programs: 6.00 FTE (1.6%)
- **Administrative Locus Definition:**
  - Pure School Building: **175.75 FTE (46.2%)**
  - Hybrid School / Central: **51.00 FTE (13.4%)**
  - Pure Central Office: **153.61 FTE (40.4%)**
  - Under a 50/50 hybrid allocation ($175.75 + 0.5 \times 51.0 = 201.25$ FTE), approximately **52.9%** of coordinator capacity is school-sited and **47.1%** is central-office sited.

---

## 5. Canonical Data Artifacts Generated in Phase 5

1. [`data/processed/coordinator_role_reconstruction.csv`](../data/processed/coordinator_role_reconstruction.csv): Canonical evidence-aware reconstruction of 29 discrete job titles across the 6 focal districts, specifying `fte_basis` (`documented_count`, `inferred_allocation`, `residual_allocation`), source document, URL, year, page/item, evidence type, and confidence score.
2. [`data/processed/coordinator_role_crosswalk.csv`](../data/processed/coordinator_role_crosswalk.csv): Exact mirror of the reconstruction file for backwards compatibility.
3. [`data/processed/district_staffing_architectures_6archetypes.csv`](../data/processed/district_staffing_architectures_6archetypes.csv): Comparative institutional matrix detailing student scale, school counts, supervisory ratios, canonical K–12 teacher FTE (`teachers_k12_fte`), authority models, and post-ESSER trajectories.
4. [`data/processed/post_esser_coordinator_survival.csv`](../data/processed/post_esser_coordinator_survival.csv): Longitudinal tracking of coordinator headcount comparing observed 2023–24 and 2024–25 CCD counts, alongside documented 2025–2027 institutional follow-up context and mechanism confidence scores.
5. [`outputs/tables/coordinator_functional_decomposition_report.md`](../outputs/tables/coordinator_functional_decomposition_report.md): Final research synthesis and institutional report.
