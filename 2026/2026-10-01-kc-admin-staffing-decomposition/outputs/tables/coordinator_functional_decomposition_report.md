# Phase 5: "What Are the Coordinators?" — Institutional and Functional Decomposition

## Executive Summary: Looking Through the Telescope

Phases 1 through 4 established that the central locus of supervisory workforce expansion in the Kansas City metropolitan area was not traditional central-office line administration (`LEAADM` grew by only +12.5% / +22.0 FTE), but **Instructional Coordinators and Supervisors (`CORSUP`)**, which expanded by **+51.0% (+255.5 FTE)** from 2014–15 to 2023–24 across the balanced 55-district cohort, accounting for **48.45% of net supervisory growth**.

Having certified and frozen that econometric and fiscal architecture, this inquiry turns from *measuring* the expansion to conducting a disciplined **institutional and descriptive reconstruction** answering four concrete questions:
1. **What are the documented job titles and functional families inside `CORSUP`?**
2. **How does supervisory architecture differ across institutional archetypes?**
3. **What funding streams enabled districts to support these positions?**
4. **What happened to these roles after temporary COVID relief (ESSER) expired?**

At the heart of the regional story is a sharp structural contrast between two large urban-suburban neighbors: **Shawnee Mission USD 512** and **Kansas City USD 500 (KCKPS)**. Both systems maintain extraordinary non-classroom supervisory capacity (+59.0 FTE and +56.3 FTE above peer expectations, respectively), but they organized and funded that capacity under fundamentally different organizational models:
- **Shawnee Mission (Specialized Coaching Overlay):** Retained standard building administration (2.12 admins/school, 95.5 FTE) and lean central line management (13.0 FTE), while layering an unprecedented cadre of ~50 building instructional coaches on top of classroom teachers—funded largely via federal ESSER III and facing an acute local operating absorption challenge.
- **Kansas City USD 500 (Distributed School Supervision):** Built an exceptionally dense building administrative architecture (3.28 admins/school, 141.0 FTE) alongside a permanent 100+ coordinator layer—funded primarily by formulaic federal (Title I/III) and state at-risk compensatory funding to address acute post-pandemic student attendance, behavior, and language needs directly at the school site.

---

## 1. Role-Level Reconstruction & Epistemic Basis

Across state reporting regimes—**Kansas KSDE SO66** licensed personnel reports and **Missouri DESE Core Data MOSIS Position Code 30 (Supervisor of Instruction)**—school districts aggregate highly heterogeneous roles into the federal NCES CCD `CORSUP` reporting line. Because state data systems do not publish individual employee payroll microdata linking specific people to specific funding codes, our 29-role crosswalk ([`data/processed/coordinator_role_reconstruction.csv`](../../data/processed/coordinator_role_reconstruction.csv)) represents an **evidence-aware institutional reconstruction**.

Every row explicitly registers its epistemic basis (`documented_count`, `inferred_allocation`, or `residual_allocation`), along with its primary source document, URL, evidence type, and confidence score. Fractional 'last buckets' (e.g., 8.71 FTE in SMSD, 10.55 FTE in Olathe, 6.55 FTE in North KC) represent residual balancing allocations calibrated to match exact federal CCD CORSUP totals.

### Table 1.1: Functional Distribution of Reconstructed Coordinator Workforce (2023–24)

Across the six focal districts, the reconstructed coordinator workforce totals **380.36 FTE**:

| Functional Category | Estimated Sample FTE | Share of Sample | Primary Operational Role | Administrative Locus |
| :--- | :--- | :--- | :--- | :--- |
| **Instructional Coaching** | 135.75 FTE | **35.7%** | Building-level coaches guiding teacher pedagogy, peer observation, and literacy/math tier-1 instruction. | School Building (Decentralized) |
| **SPED/EL Program Management** | 93.10 FTE | **24.5%** | Specialists and process coordinators managing IEP compliance, language acquisition, and specialized instruction. | Central & School Hybrid |
| **Curriculum/Content** | 73.80 FTE | **19.4%** | Central discipline specialists (ELA, Math, Science, CTE) designing curriculum scope, sequence, and pacing. | Central Office |
| **Instructional Technology** | 35.00 FTE | **9.2%** | Coaches supporting 1:1 hardware/software devices, learning management systems (Canvas), and digital tools. | School & Central Hybrid |
| **Intervention/MTSS** | 22.00 FTE | **5.8%** | Specialists coordinating multi-tiered systems of support, behavioral interventions, and student remediation. | School Building (Decentralized) |
| **Data/Assessment** | 14.71 FTE | **3.9%** | Analysts and psychometricians managing state standardized testing (KAP/MAP), screening diagnostics, and analytics. | Central Office |
| **Federal Programs** | 6.00 FTE | **1.6%** | Compliance officers overseeing Title I/II/III grant budgeting, equitable non-public services, and state audits. | Central Office |

### Exact Locus & Functional Accounting
- **Functional Instructional Coaching:** Accounts for **135.75 FTE (35.7%)** of the sample.
- **Intervention & MTSS:** Accounts for **22.00 FTE (5.8%)** of the sample.
- **Combined Coaching + MTSS:** Accounts for **157.75 FTE (41.5%)** of the sample.
- **School-Sited Locus:** Roles located strictly inside school buildings total **175.75 FTE (46.2%)**. Roles with a hybrid school/central locus add another **51.00 FTE (13.4%)**.
- **Hybrid Locus Allocation:** If hybrid school/central roles are allocated evenly (50/50) between loci, approximately **201.25 FTE (52.9%)** of the coordinator workforce is estimated to be school-sited, while **179.11 FTE (47.1%)** is central-office sited.

> [!NOTE]
> **Epistemic Clarity:** The finding that approximately ~53% of coordinators operate in schools derives from **administrative locus** under an explicit 50/50 hybrid allocation ($175.75 + 0.5 \times 51.0 = 201.25$ FTE, or $52.9\%$). Under a strict functional definition, building instructional coaching and MTSS intervention account for **41.5%** of the workforce, with the remainder dedicated to specialized program management (24.5%), central curriculum (19.4%), technology (9.2%), testing (3.9%), and federal compliance (1.6%).

---

## 2. Reconstructed Staffing Architectures Across Six Archetypes

Rather than treating districts as statistical outliers along a single dimension, Table 2.1 reconstructs the organizational staffing models of six representative systems representing distinct institutional archetypes. To maintain comparability with Phases 1 through 4, teacher counts report **K–12 classroom teacher FTE (`teachers_k12_fte`)**:

### Table 2.1: Institutional Staffing Architecture & Supervisory Footprint (2023–24)

| District | Archetype | Students | Schools | K–12 Teachers | Total Teachers (w/ PK) | CORSUP FTE | 10-Yr $\Delta$ | Building Admins (`SCHADM`) | Admins/School | Central Admins (`LEAADM`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Shawnee Mission USD 512** | Specialized Coaching Overlay | 26,464 | 45 | 1867.29 | 1900.29 | **123.71** | +348.2% | 95.50 | **2.12** | 13.00 |
| **Kansas City USD 500** | Distributed School Supervision | 21,132 | 43 | 1348.35 | 1411.95 | **106.80** | -0.1% | 141.00 | **3.28** | 6.00 |
| **Olathe USD 233** | Suburban Scaling & Retrenchment | 28,590 | 52 | 2136.60 | 2223.60 | **85.55** | +168.2% | 99.00 | **1.90** | 12.00 |
| **North Kansas City 74** | Rapid Growth Departmental Hierarchy | 21,015 | 34 | 1454.54 | 1518.54 | **36.55** | +143.7% | 76.00 | **2.24** | 8.00 |
| **Raytown C-2** | Layered Curriculum Leadership | 7,953 | 20 | 554.60 | 578.54 | **16.75** | -28.0% | 33.00 | **1.65** | 7.00 |
| **Lee's Summit R-VII** | Lean Comparator / Dept Chair Model | 17,797 | 29 | 1190.17 | 1214.92 | **11.00** | -48.8% | 66.50 | **2.29** | 8.00 |

### Detailed Archetype Profiles

#### Shawnee Mission USD 512 — *Specialized Coaching Overlay*
- **Supervisory Strategy:** Specialized coaching overlay: layered ~50 non-evaluative instructional coaches across buildings on top of teachers.
- **Locus of Authority:** Coaches sit outside administrative evaluation hierarchy; support building teachers while reporting functionally to curriculum department.
- **Funding Bridge:** Surge funded substantially through ESSER III and 2019 Strategic Plan; absorbed locally for 2024-25 before broad fiscal pressures forced staffing freezes.
- **Post-ESSER Trajectory:** Frozen: absorbed locally in 2024-25 (116.04 FTE, -6.2%), but March 2026 budget denied all 113.3 FTE staffing requests amid broader fiscal strains.

#### Kansas City USD 500 — *Distributed School Supervision*
- **Supervisory Strategy:** Decentralized building supervision: dense building admin density (3.28/school) paired with permanent 100+ coordinator layer.
- **Locus of Authority:** Authority pushed to building level (Assistant Principals & Deans) to directly manage discipline, attendance, and student climate.
- **Funding Bridge:** Coordinators supported primarily by permanent federal/state compensatory streams (Title I, Title III, At-Risk); building admin funded via state foundation.
- **Post-ESSER Trajectory:** Permanent: expanded post-ESSER (120.96 FTE in 2024-25, +13.3%); sustained by continuing federal Title I and state at-risk categoricals.

#### Olathe USD 233 — *Suburban Scaling & Retrenchment*
- **Supervisory Strategy:** Suburban scaling with pandemic coaching surge: expanded learning facilitators and curriculum specialists across rapidly growing system.
- **Locus of Authority:** Instructional facilitators deployed at school sites to support teacher induction and state TYCD assessment alignment.
- **Funding Bridge:** Coaching surge funded substantially via ESSER II/III and local operating growth; exposed when COVID relief expired.
- **Post-ESSER Trajectory:** Retrenched: cut 23.6 FTE in 2024-25 (falling from 85.55 to 61.95 FTE, -27.6%) amid general operating deficits and enrollment decline.

#### North Kansas City 74 — *Rapid Growth Departmental Hierarchy*
- **Supervisory Strategy:** Departmental curriculum expansion: added discipline-specific coordinators and tech coaches to manage rapid enrollment growth (+1,390 pupils).
- **Locus of Authority:** Centralized curriculum directors overseeing discipline coordinators who deploy across elementary and secondary feeder pathways.
- **Funding Bridge:** Robust local tax base (59% local property tax funding) successfully absorbed positions into general operating budget.
- **Post-ESSER Trajectory:** Retained: coordinator counts rose to 37.93 FTE in 2024-25 (+3.8%); absorbed permanently through local revenue growth, though facing state aid gaps for 2027.

#### Raytown C-2 — *Layered Curriculum Leadership*
- **Supervisory Strategy:** Layered central curriculum hierarchy: maintained dual Assistant Superintendents and 7 K-12 subject coordinators despite enrollment decline.
- **Locus of Authority:** Centralized curriculum authority; coordinators manage districtwide subject curricula, pacing, and diagnostic assessments.
- **Funding Bridge:** Funded primarily via Local Teachers Fund and Title I/II allocations; inelastic central hierarchy resistant to enrollment downsizing.
- **Post-ESSER Trajectory:** Inelastic: remained stable at 17.95 FTE in 2024-25 (+7.2%); structure preserved despite pupil contraction (-12.7% enrollment over decade).

#### Lee's Summit R-VII — *Lean Comparator / Dept Chair Model*
- **Supervisory Strategy:** Lean administrative model: resisted building coach surge; relies on classroom Department Chairs and building APs for instructional leadership.
- **Locus of Authority:** Instructional leadership anchored in classroom teachers (with stipends/release periods) and school building administrators.
- **Funding Bridge:** Funded strictly via local general operations; zero reliance on temporary federal relief to expand non-classroom supervisory layers.
- **Post-ESSER Trajectory:** Zero Cliff: held completely steady at 9.75 FTE in 2024-25 (-11.4%); no post-ESSER fiscal dislocation because no bubble was created.

---

## 3. Funding Provenance: How Districts Paid for the Expansion

A central question in education policy is: *Why could districts afford to create this supervisory layer?* Table 3.1 maps the observable revenue sources that financed these positions, distinguishing direct grant authorizations from inferred budget mechanisms:

### Table 3.1: Observable Funding Streams Supporting Non-Classroom Supervisory Roles

| Funding Stream | Stability / Horizon | Eligible Roles | Governing Regulations & Constraints | District Deployment Pattern | Evidence Basis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Federal ESSER I/II/III** | Temporary (Expired Sep 2024 / Liquidation 2025–26) | Instructional coaches, interventionists, summer coordinators, learning loss specialists | American Rescue Plan Section 2001; 20% minimum learning recovery set-aside | Heavily utilized by Shawnee Mission (~$10M) and Olathe to create temporary coaching surge. | Direct board resolutions and grant filings |
| **Federal Title I, Part A** | Permanent Annual Formula | Schoolwide instructional coaches, reading/math specialists, data coordinators | ESEA / ESSA Section 1114; schoolwide poverty threshold ($\ge 40\%$) | Core funding engine for KCKPS (36+ coaches) and urban core compensatory programs. | Direct schoolwide plans & building rosters |
| **Federal Title II, Part A** | Permanent Annual Formula | Professional development coordinators, instructional coaches, mentor teachers | ESEA Section 2101; restricted to educator quality and professional growth | Universally used to co-fund 2–5 central professional development coordinators. | Inferred categorical allocation |
| **Federal Title III, Part A** | Permanent Annual Formula | English language acquisition coaches, sheltered instruction specialists | ESEA Section 3111; supplemental to state bilingual mandates | Significant in KCKPS and North KC; vulnerable to federal grant reductions ($255k cut in SMSD). | Inferred categorical allocation & budget reporting |
| **Federal IDEA, Part B** | Permanent Annual Formula | Special education process coordinators, instructional facilitators | 34 CFR §300.203; Maintenance of Effort (MOE) non-supplanting | Protected core in all 6 districts (2 to 14 FTE); aggregate spending constrained by MOE. | Inferred categorical allocation |
| **State At-Risk Categorical** | Permanent (Kansas Formula) | MTSS interventionists, reading specialists, graduation coaches | K.S.A. 72-5151; requires approved at-risk practices list | Critical in Kansas (KCKPS absorbed ESSER interventionists directly into At-Risk aid). | Inferred categorical weighting |
| **Local Operating Funds** | Permanent / Discretionary | Central curriculum directors, technology coaches, content coordinators | Local property tax levies and state foundation formula aid | North Kansas City absorbed full expansion via 59% local tax share; Lee's Summit stays strictly within this. | Budget line items & board adoption |

> [!NOTE]
> **Regulatory Precision on IDEA MOE:** IDEA Maintenance of Effort (MOE) regulations constrain a school district's ability to reduce its *aggregate* state and local special-education expenditures from year to year. MOE makes special-education operations less fiscally discretionary than purely local operating expenditures, but it does *not* mandate the retention of any specific individual coordinator, facilitator, or administrative position.

---

## 4. Post-ESSER Staffing Survival: 2023–24 → 2024–25 Observed Trajectory, with 2025–2027 Institutional Follow-Up

By tracking these six districts from peak ESSER (2023–24) into the post-relief period (**2024–25 CCD counts**), alongside **2025–2027 board actions and budget filings**, we resolve whether the coordinator expansion was a temporary grant bubble or a permanent transformation of school system organization.

### Table 4.1: Observed Staffing Trajectory (2023–24 $\to$ 2024–25) and Subsequent Institutional Follow-Up

| District | Archetype | Observed CORSUP (2023–24) | Observed CORSUP (2024–25) | Observed Net Change | Observed $\Delta \%$ | Trajectory Classification | Disposition Classification | 2025–2027 Documented Institutional Context |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Shawnee Mission USD 512** | Specialized Coaching Overlay | 123.71 FTE | 116.04 FTE | **-7.67 FTE** | **-6.2%** | Local Absorption -> Budget Freeze | **Absorbed with Restructuring** | Operating reserves absorbed initial payroll; March 2026 board action declined 113.3 FTE in staffing requests citing broader fiscal pressures (enrollment decline, SPED gaps, formula shifts). |
| **Kansas City USD 500** | Distributed School Supervision | 106.80 FTE | 120.96 FTE | **+14.16 FTE** | **+13.3%** | Permanent Formula Categoricals | **Retained Intact** | Supported by substantial ongoing federal Title I and state at-risk weightings; coordinator capacity expanded post-ESSER (+14.16 FTE). |
| **Olathe USD 233** | Suburban Scaling & Retrenchment | 85.55 FTE | 61.95 FTE | **-23.60 FTE** | **-27.6%** | Sharp Retrenchment (-27.6%) | **Eliminated / Reassigned to Classrooms** | Cut 23.60 FTE upon ESSER expiration; public district explanations emphasize right-sizing amid enrollment loss and special education shortfalls. |
| **North Kansas City 74** | Rapid Growth Departmental Hierarchy | 36.55 FTE | 37.93 FTE | **+1.38 FTE** | **+3.8%** | Local Absorption via Growth (+3.8%) | **Retained Intact** | Strong property tax revenue growth (59% local share) and enrollment expansion (+1,390 students) absorbed curriculum team. |
| **Raytown C-2** | Layered Curriculum Leadership | 16.75 FTE | 17.95 FTE | **+1.20 FTE** | **+7.2%** | Inelastic Preservation (+7.2%) | **Retained Intact** | Central curriculum hierarchy maintained intact despite ongoing student enrollment contraction (-12.7% over decade). |
| **Lee's Summit R-VII** | Lean Comparator / Dept Chair Model | 11.00 FTE | 9.75 FTE | **-1.25 FTE** | **-11.4%** | Stable Baseline (-11.4%) | **Retained Intact** | Maintained lean staffing without disruption; no temporary relief bubble was created. |

### Three Post-ESSER Institutional Patterns

1. **The Retrenchment Pattern (Olathe USD 233):**
   - **Observed Change:** Coordinator FTE dropped from **85.55 to 61.95 FTE (-23.60 FTE / -27.6%)** between 2023–24 and 2024–25.
   - **Documented Context:** Olathe publicly documented severe structural budget pressure, attributing deficits to declining student enrollment, state special education funding shortfalls, and the expiration of pandemic relief. While public reporting suggests coaches returned to classrooms, that mechanism is classified as *inferred with medium confidence*.

2. **The Absorption-with-Freeze Pattern (Shawnee Mission USD 512):**
   - **Observed Change:** Coordinator FTE held relatively stable immediately post-ESSER, moving from **123.71 to 116.04 FTE (-7.67 FTE / -6.2%)** in 2024–25.
   - **Documented Context:** SMSD initially absorbed its coaching layer into local operating reserves. However, in **March 2026**, Superintendent Dr. Schumacher announced that the district would **deny all 113.3 FTE staffing requests** submitted by building leaders (including 79.3 FTE general staffing requests and a 34 FTE counselor proposal). The district cited multiple converging fiscal pressures—declining enrollment, reduced at-risk funding, special education shortfalls, and formula uncertainty—placing a de facto freeze on further coaching additions.

3. **The Entrenched Formula Pattern (KCKPS USD 500 & North Kansas City 74):**
   - **Observed Change:** In KCKPS, coordinator capacity actually **expanded** post-ESSER, rising from **106.80 to 120.96 FTE (+14.16 FTE / +13.3%)**.
   - **Documented Context:** Because KCKPS has maintained 90–120 coordinator FTE across the entire 10-year panel, funded through ongoing Title I, Title III, IDEA, and State At-Risk categoricals, the expiration of temporary ESSER funds caused zero contraction.
   - In North Kansas City, coordinator counts rose slightly from **36.55 to 37.93 FTE (+1.38 FTE / +3.8%)**, absorbed permanently by rapid student enrollment growth (+1,390 students) and a expanding property tax base (59% local funding share).

---

## 5. The Centerpiece: Shawnee Mission vs. KCKPS

The structural divergence between Shawnee Mission USD 512 and Kansas City USD 500 demonstrates that there is no single 'administrative growth' story in urban-suburban education.

### Table 5.1: Comparative Institutional Matrix — SMSD vs. KCKPS

| Organizational Dimension | Shawnee Mission USD 512 | Kansas City USD 500 (KCKPS) |
| :--- | :--- | :--- |
| **Metropolitan Context** | Affluent, fully developed first-ring Johnson County suburb | High-poverty, linguistically diverse Wyandotte County urban core |
| **Enrollment (2023–24)** | 26,464 students (45 operating schools) | 21,132 students (43 operating schools) |
| **K–12 Classroom Teachers** | **1,867.29 FTE** (14.2 students / teacher) | **1,348.35 FTE** (15.7 students / teacher) |
| **Total Reported Teachers (w/ PK)** | 1,900.29 FTE (includes 33.0 FTE Pre-K) | 1,411.95 FTE (includes 63.6 FTE Pre-K) |
| **Instructional Coordinators (`CORSUP`)** | **123.71 FTE** (+59.0 FTE above peer mean, $t = +5.46$) | **106.80 FTE** (+56.3 FTE above peer mean, $t = +6.98$) |
| **Building Administrators (`SCHADM`)** | **95.50 FTE** (**2.12 admins / school**) | **141.00 FTE** (**3.28 admins / school**, +55.2 FTE above peers) |
| **Central Line Administration (`LEAADM`)** | **13.00 FTE** (roughly peer expected) | **6.00 FTE** (**$-3.0$ FTE below peer expected**) |
| **Primary Operational Philosophy** | **Specialized Instructional Coaching Overlay** | **Decentralized School-Level Supervisory Dispersion** |
| **Locus of Non-Classroom Authority** | Central Curriculum Department & non-evaluative coaches | School Building Principals, Assistant Principals, and Deans |
| **Problem Being Solved** | Differentiated instruction, personalized learning, technology integration, curriculum pacing | Chronic absenteeism, student behavioral crisis, trauma-informed climate, tiered interventions |
| **Evaluation Authority** | Coaches do **not** evaluate teachers; strictly collegial support | Assistant Principals and Deans hold **formal supervisory and evaluative authority** |
| **Primary Funding Bridge** | ESSER III ($10M) + local capital/operating levies | Federal Title I Schoolwide + State At-Risk + Bilingual Categoricals |
| **Post-ESSER Observed Staffing** | 123.71 $\to$ 116.04 FTE (-6.2%) in 2024–25; March 2026 hiring freeze | 106.80 $\to$ 120.96 FTE (+13.3%) in 2024–25; formula permanent |

### Institutional Implications
1. **Authority vs. Support:** In Shawnee Mission, supervisory growth was built as an *advisory support service* without administrative evaluation authority. In KCKPS, supervisory growth was built as *direct line authority* (assistant principals and deans) to manage behavior, disciplinary hearings, and parent contacts directly on the ground.
2. **Fiscal Resilience:** Programs built on formulaic categorical aid (Title I, IDEA, At-Risk) exhibit extreme institutional permanence. Programs built on emergency federal relief (ESSER) inevitably trigger budget freezes, classroom reassignments, or local structural deficits once the grant window closes.

---

## 6. Conclusion

When we 'stop debugging the telescope and look through it,' the 51% surge in instructional coordinators ceases to be an econometric abstraction. It represents two distinct movements in contemporary public school governance:
1. **The Professionalization of Instructional Support:** Suburban districts invested heavily in non-evaluative coaching, technology integration, and curriculum standardization, creating a new professional tier between teachers and principals.
2. **Compensatory Supervisory Densification:** Urban core districts layered school-based interventionists, compliance specialists, and assistant principals to manage acute post-pandemic student needs through federal and state compensatory grants.

Understanding this functional anatomy provides the essential institutional foundation for evaluating educational productivity, teacher satisfaction, and student achievement in the post-pandemic era.