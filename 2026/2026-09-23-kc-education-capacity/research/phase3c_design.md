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
| Workstream 1: State Replication    | Workstream 2: Role Decomposition | Workstream 3: External QA |
+------------------------------------+----------------------------------+---------------------------+
| * KSDE SO66 / LPR Reports          | * SPED Teacher & Para FTE        | * CRDC 6-Wave Panel       |
| * MO DESE Core Data / MOSIS        | * IDEA & EL Student Populations  | * NTPS Benchmark Registry |
| * Anchor Years: 2014, 2019, 2024   | * Coordinators, Counselors, Psych| * Non-Teacher Growth Rates|
| * District-by-District Audit       | * Estimated General-Ed Residual  | * Allocation Wedge Models |
+------------------------------------+----------------------------------+---------------------------+
```

### Workstream 1: Independent State-Source Replication
* **Objective:** Compare NCES CCD reported teacher FTE against state administrative records district by district for fully regional LEAs across three anchor years:
  - **SY 2014–15:** Baseline anchor.
  - **SY 2019–20:** Pre-pandemic peak anchor.
  - **SY 2024–25:** Current post-pandemic endline anchor.
* **Kansas Source Pipeline:**
  - KSDE Data Central $\rightarrow$ School Finance *Superintendent's Organization Report (SO66)*: Unaudited FTE of Licensed Personnel by position.
  - KSDE Licensed Personnel Reports (LPR): District-level licensed teacher FTE, special education teacher FTE, and pupil/teacher ratios.
  - Test Case: Reconcile major Kansas districts (e.g. Olathe USD 233, Shawnee Mission USD 512, Blue Valley USD 229, Kansas City USD 500) between NCES and KSDE.
* **Missouri Source Pipeline:**
  - MO DESE Missouri Comprehensive Data System (MCDS) $\rightarrow$ District & Building Staffing files.
  - MO DESE Core Data / MOSIS Educator Workforce and Vacancy Reports.
  - Test Case: Reconcile major Missouri districts (e.g. Kansas City Public Schools, North Kansas City, Lee's Summit, Independence).
* **Audit Thresholds:**
  - **Parity ($\Delta \le \pm 2\%$):** State payroll/licensure confirms NCES counts.
  - **Discrepancy ($\Delta > \pm 5\%$):** Trigger forensic review of position definitions (e.g., Pre-K inclusion, shared-service cooperatives, regional vocational center attribution).

### Workstream 2: Staffing Role & Student Need Decomposition
* **Objective:** Determine the operational destination of the $+1,921.91$ regional teacher FTE increase and evaluate concurrent growth in specialized support roles.
* **Target Staffing Measures:**
  1. **Special Education Teachers (FTE):** Federal EDFacts FS070 / FS099 and state SPED personnel files.
  2. **Special Education Paraprofessionals (FTE):** EDFacts FS112 and state personnel files.
  3. **English Learner / Bilingual Teachers (FTE):** Title III / ESL teacher reports.
  4. **Instructional Coordinators & Supervisors (FTE):** CCD LEA Staff (already observed rising $+49.7\%$, $+266.89$ FTE).
  5. **Student Support Professionals (FTE):**
     - Guidance Counselors (already observed rising $+18.9\%$, $+144.62$ FTE).
     - School Psychologists (reported separately from 2020 onward; $+231.05$ FTE).
     - Social Workers and Student Support Staff ($+15.4\%$, $+355.45$ FTE).
* **Target Student Need Measures:**
  1. **IDEA / Special Education Student Enrollment:** EDFacts FS002 (Children with Disabilities).
  2. **English Learner (EL) Student Enrollment:** EDFacts FS141 (LEP / EL headcount).
  3. **High-Need Intensity Ratios:** Students with IEPs per SPED Teacher FTE; EL students per ESL Teacher FTE.
* **The General-Education Residual Calculation:**
  $$\text{Teachers}_{\text{GenEd\_Residual}} = \text{Teachers}_{\text{Total\_K12}} - \text{Teachers}_{\text{SpecialEd}} - \text{Teachers}_{\text{Bilingual/ESL}}$$
  - If $\text{Teachers}_{\text{GenEd\_Residual}}$ grew at a substantially lower rate than total FTE, the Allocation Wedge hypothesis is strongly corroborated prior to Phase 4.

### Workstream 3: Federal Triangulation & External Benchmarks
* **Civil Rights Data Collection (CRDC):**
  - Mandatory OCR biennial collection covering all public schools.
  - Ingest public-use data files for 6 survey waves: **2013–14, 2015–16, 2017–18, 2020–21, 2021–22, 2023–24**.
  - Extract school-level certified teacher FTE, uncertified teacher counts, student enrollment by disability (IDEA/504) and EL status, school counselor FTE, and security staff.
* **NTPS Survey Integration:**
  - Compile published state-level departmentalized and self-contained average class sizes for Missouri and Kansas from the 2015–16, 2017–18, and 2020–21 NTPS waves as external reference points.

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

## 5. Deliverables and Execution Plan for Phase 3C

1. **State Ingestion Scripts:**
   - `src/download/download_ksde_personnel.py`: Download KSDE SO66 / LPR personnel tables.
   - `src/download/download_dese_workforce.py`: Download MO DESE staffing and educator workforce files.
2. **Replication & Reconciliation Audit:**
   - `outputs/tables/task003c_state_replication_audit.csv`: District-by-district comparison table (NCES vs. KSDE/DESE for 2014, 2019, 2024).
   - Anomaly ledger for any discrepancies $> \pm 3\%$.
3. **Staffing Role Decomposition Table & Figures:**
   - `outputs/tables/task003c_staffing_role_decomposition.csv`: SPED, EL, coordinator, counselor, and general-ed residual trajectories across 11 years.
   - `outputs/figures/staffing_category_growth_rates.png`: Comparative growth rates of teachers vs. specialized roles.
   - `outputs/figures/allocation_wedge_schematic.png`: Visualizing the gap between structural PTR and estimated general-ed classroom load.
4. **Phase 3C Synthesis Report:**
   - `outputs/tables/task003c_synthesis_report.md`: Formal findings on staffing integrity, role allocations, and the empirical magnitude of the allocation wedge.
