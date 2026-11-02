# Phase 3C Research Design: Staffing Integrity & Allocation Audit
**Kansas City Metropolitan Education Capacity Study**  
**Date:** September 24, 2026  
**Status:** Approved Architecture (Decision 025)  
**Parent Tasks:** Phase 3 Macro Structural Panel (`outputs/tables/task003b_analysis_report.md`)  
**Subsequent Phases:** Phase 4A (Section & Roster Distributions) & Phase 4B (Classroom Complexity Overlay)  

---

## 1. Executive Motivation & The Allocation Wedge Framework

### 1.1 The Emerging Macro-Micro Paradox
Phase 3 established a definitive macro finding across the 9-county Kansas City metropolitan area between 2014–15 and 2024–25:
- **K–12 Student Enrollment:** Essentially flat ($-0.73\%$, $-2,345$ students).
- **Reported K–12 Classroom Teacher FTE:** Expanded by $+8.88\%$ ($+1,921.91$ FTE across fully regional LEAs).
- **Structural Pupil/Teacher Ratio:** Fell from **14.85 to 13.54** ($-1.31$ students per teacher FTE, $-8.82\%$).
- **Campus-Level Median Ratio:** Fell from **15.23 to 13.53** ($-1.70$ students per teacher FTE, $-11.16\%$).
- **Paraprofessional Staffing:** Rose by $+11.85\%$ ($+565.91$ FTE).

Despite this clear expansion of adult instructional headcounts, classroom teachers frequently report persistent or worsening instructional overload and high class headcounts.

### 1.2 The NCES Operational Reality
NCES explicitly documents that **pupil/teacher ratios do not measure class size**:
> *"The pupil/teacher ratio divides total student enrollment by total teacher FTE. It includes teachers for students with disabilities and other specialized teachers, while those teachers are generally excluded from class-size calculations."* (NCES CCD Documentation).

Furthermore, while the federal definition of a teacher is restrictive—a professional staff member who instructs students and maintains daily attendance records, distinguishing them from administrators and instructional coordinators—the "teacher FTE" umbrella encompasses diverse instructional assignments:
1. Standard general-education classroom teachers (who instruct large departmentalized or elementary rosters).
2. Special-education caseload and resource teachers (who instruct small caseloads of 5–12 students).
3. Targeted interventionists (reading/math specialists working with groups of 2–6 students).
4. Co-teachers and push-in/pull-out specialists (who share rosters with another lead teacher).
5. Alternative school and specialized program teachers.
6. Specialized electives with low student seat enrollments.

### 1.3 Formal Definition of the Allocation Wedge
The aggregate statistic answers a resource capacity question:
$$\text{Structural Staffing Ratio} = \frac{\sum \text{Students}}{\sum \text{Total Instructional Teacher FTE}}$$

Teachers and students in general classrooms experience an allocation reality:
$$\text{Classroom Exposure} = \frac{\sum \text{Student Seats in General Core Sections}}{\sum \text{Active General Classroom Period Teachers}}$$

We define the **Allocation Wedge** as:
$$\text{Allocation Wedge} = \text{Observable Median Core Section Size} - \text{Reported Pupil/Teacher Ratio}$$

### 1.4 External Survey Validation (NTPS Benchmarks)
External federal data from the National Teacher and Principal Survey (NTPS) confirm that this wedge is real, large, and structurally persistent across both Kansas and Missouri:
- **SY 2017–18 NTPS Departmentalized High School Class Sizes:**
  - Kansas: **19.8 students** (vs. structural LEA PTR of ~14.4) $\rightarrow$ **Wedge of $+5.4$ students**.
  - Missouri: **22.5 students** (vs. structural LEA PTR of ~14.5) $\rightarrow$ **Wedge of $+8.0$ students**.
- **SY 2020–21 NTPS Departmentalized High School Class Sizes:**
  - Kansas: **17.4 students** (vs. structural LEA PTR of ~13.7) $\rightarrow$ **Wedge of $+3.7$ students**.
  - Missouri: **19.2 students** (vs. structural LEA PTR of ~13.9) $\rightarrow$ **Wedge of $+5.3$ students**.

---

## 2. Phase 3C Scope and Objectives

Phase 3C bridges the gap between macro structural capacity (Phase 3) and micro course roster data (Phase 4) by answering two fundamental questions:
1. **Are the teacher counts real?** Does the $+1,922$ teacher FTE expansion replicate in independent state administrative and licensure databases (KSDE and MO DESE), or does it reflect federal reporting artifacts?
2. **What categories of instructional work actually grew?** Did the expansion occur in standard general-education classroom teachers, or was it concentrated in special education, English learner programs, interventionists, or non-teaching support staff?

---

## 3. The Three Empirical Workstreams

```
+---------------------------------------------------------------------------------------------------+
|                                     PHASE 3C RESEARCH WORKSTREAMS                                 |
+------------------------------------+----------------------------------+---------------------------+
| Workstream 1: State Reconciliation | Workstream 2: Role Decomposition | Workstream 3: External QA |
+------------------------------------+----------------------------------+---------------------------+
| * Upstream/Downstream Audit        | * Part A: Inside Teacher FTE     | * CRDC 6-Wave Panel       |
| * Pilot: 3-4 Districts/State       |   (SPED, Resource, Intervention) | * NTPS Benchmark Registry |
| * KSDE SO66 / LPR Reports          | * Part B: Non-Teacher Support    | * Non-Teacher Growth Rates|
| * MO DESE Core Data / MOSIS        |   (Coordinators, Counselors, etc)| * Mutual Exclusivity Audit|
| * Anchor Years: 2014, 2019, 2024   | * Residual Deferred              | * Allocation Wedge Models |
+------------------------------------+----------------------------------+---------------------------+
```

### Workstream 1: State-Source Staffing Reconciliation (Pilot First)
* **Epistemic Framing:** This is an upstream/downstream administrative source reconciliation exercise rather than an independent replication, as federal CCD data originate from state education agency submissions. The objective is to verify whether state-facing personnel records and the federal CCD transformation agree on the magnitude and direction of teacher staffing.
* **Step 1A: Pilot-First Protocol:**
  - Before any statewide bulk ingestion, execute a targeted pilot across 3–4 key districts per state across the three anchor years (**SY 2014–15**, **SY 2019–20**, **SY 2024–25**):
    - **Kansas:** Olathe (USD 233), Kansas City (USD 500), Blue Valley (USD 229), Shawnee Mission (USD 512).
    - **Missouri:** Kansas City 33 (KCPS), North Kansas City 74, Lee's Summit R-VII, Independence 30.
* **Kansas Source Pipeline:**
  - KSDE Data Central $\rightarrow$ School Finance *Superintendent's Organization Report (SO66)*: Unaudited FTE of Licensed Personnel by position.
  - KSDE Licensed Personnel Reports (LPR): District-level licensed teacher FTE, special education teacher FTE, and PK–12 teacher FTE.
  - *Strict Rule:* Explicitly distinguish between Licensed Personnel FTE, Special Education Teacher FTE, and PK–12 Teacher FTE. PK–12 Teachers is the primary comparable field; total Licensed Personnel is broader and must not be substituted.
* **Missouri Source Pipeline:**
  - MO DESE Missouri Comprehensive Data System (MCDS) $\rightarrow$ Building and District Staffing files.
  - MO DESE Core Data / MOSIS Educator Workforce and Vacancy Reports.
* **Reconciliation Classifications (Audit Flags):**
  - `close_match`: Absolute difference $\le \pm 2\%$.
  - `moderate_difference`: Difference $> 2\%$ and $\le 5\%$.
  - `material_difference`: Difference $> 5\%$ (triggers forensic review of PK, SPED attribution, cooperatives, timing snapshots, and audited/unaudited status).
  - `not_comparable`: Definitional mismatch.

### Workstream 2: Staffing Role & Student Need Decomposition
* **Epistemic Clarification:** Instructional coordinators, counselors, psychologists, and support staff do **not** explain the $+1,922$ classroom-teacher FTE because they are distinct CCD categories. Workstream 2 is strictly organized into two separate analytical components:
* **Part A: Decomposing Teacher FTE Itself (Inside the Denominator):**
  - Examine categories that legitimately sit inside teacher FTE:
    1. Special Education Teacher FTE (EDFacts FS070 / FS099 and state SPED personnel files).
    2. Special-education resource and caseload teachers.
    3. Targeted intervention instructors (reading/math specialists).
    4. Co-teachers and push-in/pull-out instructional specialists.
    5. Alternative program and low-enrollment specialized section teachers.
* **Part B: Separately Analyzing Non-Teacher Support Growth (Outside the Denominator):**
  - Track how auxiliary student support expanded alongside classroom teachers:
    1. Instructional Coordinators & Supervisors (already observed rising $+49.7\%$, $+266.89$ FTE).
    2. Guidance Counselors (already observed rising $+18.9\%$, $+144.62$ FTE).
    3. School Psychologists (reported separately from 2020 onward; $+231.05$ FTE).
    4. Social Workers and Student Support Staff ($+15.4\%$, $+355.45$ FTE).
    5. Special Education Paraprofessionals ($+11.85\%$, $+565.91$ FTE).
* **Part C: Student Need Trajectories (Parallel Series):**
  - IDEA / Special Education Student Enrollment (EDFacts FS002).
  - English Learner (EL) Student Headcount (EDFacts FS141).
  - Title III Language Instruction Program Teacher Headcounts (EDFacts FS067).
* **Methodological Guardrail on Residuals:**
  - **Do NOT calculate** an additive residual ($\text{Teachers}_{\text{Total}} - \text{Teachers}_{\text{SPED}} - \text{Teachers}_{\text{EL}}$) at this stage. Title III FS067 reports unduplicated teacher headcounts (not FTE) that can include general content teachers; subtracting it from total FTE mixes units and double-counts individuals.
  - The general-education residual is **strictly deferred** until mutually exclusive FTE categories are demonstrated from state assignment microdata. All specialized categories are retained as parallel series.

### Workstream 3: External Triangulation & Survey Benchmarks
* **Civil Rights Data Collection (CRDC):**
  - Mandatory OCR biennial collection covering all public schools.
  - Ingest public-use data files for 6 survey waves: **2013–14, 2015–16, 2017–18, 2020–21, 2021–22, 2023–24**.
  - Extract school-level certified teacher FTE, uncertified teacher counts, student enrollment by disability (IDEA/504) and EL status, school counselor FTE, and security staff.
* **NTPS Survey Integration:**
  - State-level NTPS estimates provide an external benchmark for plausible wedges (secondary departmentalized class sizes around $19.8\text{ KS} / 22.5\text{ MO}$ in 2017–18 and $17.4\text{ KS} / 19.2\text{ MO}$ in 2020–21). Phase 4 will directly estimate the KC-specific distribution.

---

## 4. Phase 4 Architecture: Two Focused Sub-Phases

By completing Phase 3C first, Phase 4 can be sharply split into two high-yield sub-phases:

### Phase 4A — Actual Section & Roster Distributions ("Where are students sitting?")
* **Unit of Analysis:** Individual course section records (`school_year`, `district`, `school`, `course_code`, `course_name`, `section_id`, `teacher_id`, `period`, `section_enrollment`).
* **Core Estimands:**
  1. **Actual Class Size Distributions:** Median, IQR, P90, maximum across core subjects (Algebra I, English I, Biology, 8th Grade Math).
  2. **Student-Weighted Exposure:** Percentage of student seats in classrooms of $\ge 25$, $\ge 30$, and $\ge 33$ students.
  3. **Teacher Roster Load:** Total unique students instructed per secondary teacher FTE.
  4. **Allocation Diagnostics ("Ghost Class" / Schedule Distributions):**
     - Sections per teacher FTE.
     - Total student seats per teacher FTE across assignment types (general-ed, resource, intervention, co-teaching).
     - Identification of any teacher FTE allocations unattached to student rosters.

### Phase 4B — Classroom Complexity Overlay ("What is inside the classroom?")
* **Unit of Analysis:** Section-level complexity characteristics.
* **Integrated Variables:**
  - Section-level IEP / SPED student count.
  - Section-level English Learner (EL) count.
  - Co-teacher and adult support presence.
  - Course-level chronic absenteeism rates and student mobility.
* **Hypothesis Evaluation:** Rigorous adjudication of **H2 (Complexity)** and **H4 (Joint Interaction)**.

---

## 5. Deliverables and Execution Plan for Step 1A Pilot

1. **Source Definition Matrix:**
   - `research/phase3c_state_source_definition_matrix.csv`: Detailed audit of report name, variable name, headcount vs FTE, reporting dates, PK inclusion, SPED inclusion, itinerant/shared staff, charters, cooperatives/interlocals, audited status, reporting unit, and comparability to CCD.
2. **Pilot Reconciliation Table:**
   - `outputs/tables/task003c_state_replication_pilot.csv`: District-year-source comparisons for the 8 pilot districts across 2014–15, 2019–20, and 2024–25 with percentage differences and audit classification flags (`close_match`, `moderate_difference`, `material_difference`, `not_comparable`).
3. **Pilot Anomaly Ledger:**
   - `outputs/tables/task003c_state_replication_anomalies.csv`: Detailed explanations for every comparison with difference $> 5\%$.
4. **Step 1A Pilot Report:**
   - `outputs/tables/task003c_state_replication_pilot_report.md`: Synthesis of source compatibility, pilot discrepancies, trend comparisons, and recommendation on scaling to the full 77 LEAs.

### Stop Condition
- **Strict Stop:** Stop immediately upon completion of the Step 1A Pilot.
- Do not proceed to statewide bulk ingestion across all 77 LEAs.
- Do not begin staffing-role decomposition until the pilot reconciliation has been reviewed and approved.
