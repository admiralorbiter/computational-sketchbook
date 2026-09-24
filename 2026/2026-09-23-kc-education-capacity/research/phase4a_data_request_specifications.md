# Phase 4A: State Data Request Specifications
**Course Section, Educator Assignment & Class Size Microdata**  
**Kansas City Metropolitan Education Capacity Study**  
**Date:** September 24, 2026  
**Status:** Drafted Specifications Ready for Agency Submission  
**Target Agencies:**
1. **Missouri Department of Elementary and Secondary Education (MO DESE)** — Office of Data System Management
2. **Kansas State Department of Education (KSDE)** — Data & Information Systems / Educator Data Collection

---

## 1. Research Background & Purpose

The Kansas City Metropolitan Education Capacity Study has documented a decade-long paradox across the 9-county metropolitan area (2014–15 through 2024–25):
- **K–12 Enrollment** remained essentially flat ($-0.73\%$, $321,228 \rightarrow 318,883$).
- **Reported Teacher FTE** expanded substantially ($+8.88\%$, $21,633 \rightarrow 23,555$ FTE across fully regional LEAs).
- **Macro Pupil/Teacher Ratios** dropped from $14.85 \rightarrow 13.54$.
- **Classroom Teachers** expanded by $+6.24\%$ across Kansas districts (and $+8.70\%$ in Johnson County suburbs).
- **Yet classroom teachers and school communities report that core classroom section sizes remain large (often 24–28+ students in secondary academic courses).**

To resolve this empirical paradox, aggregate district-level ratios are structurally insufficient. This data request seeks **deidentified, course-section-level microdata** to observe:
1. **True Student-Weighted Class Size Distributions:** Measuring the section size experienced by the median student (50th, 75th, 90th percentiles).
2. **Core vs. Elective Allocation:** Isolating core academic subjects (Mathematics, English Language Arts, Science, Social Studies) from elective, remedial, and specialized sections.
3. **Teacher Roster Load:** Calculating the total daily student burden per full-time teacher across assigned periods.
4. **Classroom Complexity Overlays:** Evaluating the section-level concentration of students with Individualized Education Programs (IEPs) and English Learners (ELs).

---

## 2. Missouri Request Specification (MO DESE)

### 2.1 Primary Target Collection
- **Core Data / MOSIS Screen 20 (Course Assignment):** Links certified educators to individual courses and sections.
- **Linked Source:** Core Data Screen 18 (Educator Core / Duty Codes).

### 2.2 Geographic & Temporal Scope
- **Geographic Scope:** All public school districts and public charter schools located within the five Missouri metropolitan counties: **Jackson, Clay, Platte, Cass, and Ray**.
- **School Years Requested:** 
  - Priority Anchor Years: **2014–15**, **2019–20**, and **2024–25**.
  - Preferred (if feasible within standard extraction): Continuous annual extracts for all 11 school years (2014–15 through 2024–25).

### 2.3 Requested Data Elements (Record Level: Course Section)

| Field Name | Variable Description | Justification / Analytical Use |
| :--- | :--- | :--- |
| `school_year` | Academic school year (e.g., 2024–25) | Longitudinal panel tracking |
| `district_code` | 6-digit DESE County-District Code (e.g., 048-078) | LEA linkage |
| `district_name` | Official district name | Verification |
| `school_code` | 4-digit DESE School Building Code (e.g., 1050) | School-level linkage |
| `school_name` | Official school building name | Verification |
| `course_code` | 6-digit State Course Code | Standardized curriculum subject classification |
| `course_title` | Local or state course title | Disaggregating core academic from electives |
| `subject_area` | State subject classification (e.g., ELA, Math) | Core subject grouping |
| `section_id` | Unique section identifier within school and term | Identifying distinct classroom cohorts |
| `educator_id_deidentified` | Anonymous, consistently hashed educator ID | Calculating educator section count & total student load |
| `duty_code` | Screen 18 Duty Code (e.g., 001–099) | Distinguishing classroom teachers from co-teachers |
| `teacher_fte_assigned` | FTE fraction dedicated to this section | Allocating teacher capacity accurately |
| `term_code` | Full Year, Fall Semester, Spring Semester, Quarter | Standardizing enrollment exposure |
| `period_number` | Scheduled period/block (e.g., 1, 2, 3...) | Analyzing teacher scheduling and duty releases |
| `section_enrollment` | Total student headcount rostered in section | Primary class-size measurement |
| `section_grade_level` | Predominant grade level of section (e.g., 9, 10, 11, 12) | Grade-band stratification |
| `section_iep_count` | Aggregate count of students with an active IEP | Testing H2 complexity at section level |
| `section_ell_count` | Aggregate count of English Learners (EL) | Testing H2 language complexity |
| `delivery_mode` | In-person, Blended, Virtual | Filtering virtual instruction |

---

## 3. Kansas Request Specification (KSDE)

### 3.1 Primary Target Collection
- **Educator Data Collection System (EDCS) / Kansas Course Code Management System (KCCMS):** Course Assignment records linking licensed educators to course codes and sections.
- **Linked Source:** Licensed Personnel Report (LPR) / OpenGov Assignment records.

### 3.2 Geographic & Temporal Scope
- **Geographic Scope:** All Unified School Districts (USDs) located within the four Kansas metropolitan counties: **Johnson, Wyandotte, Leavenworth, and Miami**.
- **School Years Requested:** 
  - Priority Anchor Years: **2014–15**, **2019–20**, and **2024–25**.
  - Preferred: Continuous annual extracts (2014–15 through 2024–25).

### 3.3 Requested Data Elements (Record Level: Course Section)

| Field Name | Variable Description | Justification / Analytical Use |
| :--- | :--- | :--- |
| `school_year` | Academic school year (e.g., 2024–25) | Longitudinal panel tracking |
| `usd_number` | State USD number (e.g., 229, 233, 500, 512) | District linkage |
| `district_name` | Official USD name | Verification |
| `building_number` | State 4-digit Building Number | Building-level linkage |
| `building_name` | Official building name | Verification |
| `course_code` | 5-digit KCCMS State Course Code | Standardized curriculum classification |
| `course_title` | Local or state course title | Core vs. elective identification |
| `subject_cluster` | State subject cluster (e.g., English, Math, CTE) | Core subject filtering |
| `section_number` | Local course section identifier | Identifying discrete classrooms |
| `educator_id_deidentified` | Anonymous, consistently hashed educator ID | Tracking teacher daily load and period assignments |
| `assignment_code` | State assignment code | Distinguishing classroom teachers from specialists |
| `assigned_fte` | FTE allocated to section | Precise staffing weighting |
| `term_code` | Term (Year, Semester, Trimester) | Exposure weighting |
| `period` | Scheduled period/block | Teacher prep load analysis |
| `section_enrollment` | Student headcount rostered in section | Primary class size measurement |
| `section_iep_count` | Aggregate count of students with an IEP | Testing H2 complexity at section level |
| `section_ell_count` | Aggregate count of English Learners | Testing H2 language complexity |
| `virtual_indicator` | In-person vs. Virtual section | Isolating physical classroom environments |

---

## 4. Privacy, Confidentiality & FERPA Compliance Protocols

To ensure compliance with the Family Educational Rights and Privacy Act (FERPA) and state privacy regulations:
1. **Zero Student PII:** **No student names, state student IDs, dates of birth, or individual demographic records are requested.** All student-level variables are strictly aggregated counts per section (`section_enrollment`, `section_iep_count`, `section_ell_count`).
2. **Deidentified Educator IDs:** Educator records will utilize a one-way cryptographically hashed or sequential surrogate ID generated by the state agency. This enables researchers to link multiple sections taught by the same teacher to compute daily student loads while preserving educator anonymity.
3. **Small-Cell Masking Protocols:** If required by state privacy policies for cell counts under 5 (e.g., sections with 1 to 4 IEP students), data may be provided using standard top/bottom coding (e.g. `< 5`) or blinded indicators.
4. **Data Security & Storage:** Data will be stored in an encrypted, access-controlled research environment dedicated solely to this academic study and will not be redistributed or utilized for commercial purposes.

---

## 5. Intended Analytical Outputs

Upon receipt, this microdata will directly generate the empirical foundation for **Phase 4A & Phase 4B**:
- **Output 4A.1:** Student-Weighted Class Size Distribution Curves (comparing the median student's exposure against the administrative pupil/teacher ratio).
- **Output 4A.2:** Core Academic Section Sizes vs. Elective / Specialized Section Sizes (quantifying the curriculum allocation wedge).
- **Output 4A.3:** Teacher Daily Roster Load Analysis (quantifying how planning periods, block scheduling, and duty assignments affect student load).
- **Output 4B.1:** Section Complexity Index (joint distribution of IEP and ELL students across general education classrooms).
