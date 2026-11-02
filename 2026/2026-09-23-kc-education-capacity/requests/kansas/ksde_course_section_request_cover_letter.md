# Research Data Request: Course Section, Educator Assignment & Roster Microdata

**To:**  
Data & Information Systems / Research & Evaluation  
Kansas State Department of Education (KSDE)  
900 S.W. Jackson Street, Suite 102, Topeka, KS 66612  

**From:**  
Kansas City Metropolitan Education Capacity Study Research Team  

**Date:** September 24, 2026  
**Subject:** Formal Research Data Request: De-identified Longitudinal KEDX Course Section and Staff Assignment Microdata (Kansas Metropolitan USDs, SY 2014–15 to 2024–25)

---

### 1. Executive Summary & Research Justification

The Kansas City Metropolitan Education Capacity Study is an independent empirical research project examining educator capacity, staffing allocation, and classroom distributions across the 9-county metropolitan area.

Our preliminary analysis of KSDE personnel records across the 19 metropolitan Unified School Districts in Johnson, Wyandotte, Leavenworth, and Miami counties revealed a vital pattern over the past decade (2014–15 to 2024–25):
- Total enrollment in the 19 USDs grew modestly (+2.46%).
- Total instructional teacher FTE grew by +5.85% (from 9,747.6 to 10,317.9 FTE).
- Certified **Classroom Teachers** expanded by **+6.24%** (+506.9 FTE), while specialized teachers (Special Education and Reading Specialists) grew by +3.90% (+63.4 FTE). In suburban Johnson County, classroom teachers grew by +8.70%.
- Consequently, while specialized roles create a ~2.7 student per teacher difference in headline ratios (the *Specialist Denominator Wedge*), roughly 89% of net instructional additions occurred in conventional classroom-teacher positions.

Despite this demonstrated growth in classroom-teacher capacity, high school and middle school educators widely report that core academic sections (Algebra, Biology, English 9–12) regularly enroll 25 to 30+ students. 

To determine how classroom capacity was utilized—whether absorbed into expanded elective offerings, advanced/remedial courses, co-teaching models, or teacher preparation periods—the research team requests de-identified course section microdata.

---

### 2. Statutory Authority & FERPA Compliance

This request is submitted under the research provisions of the **Family Educational Rights and Privacy Act (FERPA), 34 CFR § 99.31(a)(6)**, which authorizes disclosure of de-identified student and educator data for studies aimed at improving instruction.

**Strict Privacy Commitments:**
1. **Zero Direct Student PII:** The researchers request **no student names, Kansas State Student Identifiers (KIDS IDs), birthdates, or physical addresses**.
2. **De-identification via Surrogate IDs:** KSDE is requested to replace all educator and student identifiers with stable, cryptographically salted surrogate IDs (or sequential integers).
3. **FERPA Data Use Agreement:** The research team will execute KSDE's standard Data Use Agreement and enforce strict encryption, restricted server access, and data destruction upon study conclusion.
4. **Small-Cell Masking:** All public reporting will apply standard KSDE privacy suppression rules ($n < 5$).

---

### 3. Requested Scope & Data Elements

#### 3.1 Geographic & Temporal Scope
- **Geographic Universe:** All 19 Unified School Districts located in the four Kansas MARC counties: **Johnson, Wyandotte, Leavenworth, and Miami** (USDs 202, 203, 204, 207, 229, 230, 231, 232, 233, 416, 458, 464, 469, 491, 500, 512, etc.).
- **School Years Requested:** 
  - Priority Anchor Years: **2014–15**, **2019–20**, and **2024–25**.
  - Preferred: Continuous annual panel (2014–15 through 2024–25).

#### 3.2 Target Collections & Two-Tier Architecture
We request linkage between:
1. **Primary Collection (Course & Section Structure):** KEDX / Ed-Fi `Section`, `StaffSectionAssociation`, and `StudentSectionAssociation`.
2. **Supplemental Source (Educator Assignment Context):** EDCS / Licensed Personnel Report (LPR) for educator classification, assignment codes, FTE percentage, and co-teacher flags.

To accommodate agency resources and privacy governance, we propose a **two-tier structure**:

- **Tier 1 (Preferred — De-identified Section & Roster Extract):**
  - Section records linked to stable surrogate educator IDs and surrogate student IDs.
  - Fields: `school_year`, `usd_number`, `district_name`, `building_number`, `course_code` (5-digit KCCMS), `course_title`, `subject_cluster`, `section_identifier`, `term_descriptor`, `period_descriptor`, `staff_surrogate_id`, `assignment_code`, `assigned_fte`, `classroom_position_type`, `student_surrogate_id`, `student_grade_level`, `special_education_status`, `english_learner_status`, `virtual_status`.
- **Tier 2 (Fallback — Agency-Aggregated Section & Teacher Summary):**
  - If student surrogate IDs cannot be provided, KSDE aggregates section totals and computes unduplicated student counts prior to export:
    - Section-level: `section_identifier`, `course_code`, `section_enrollment` (headcount), `section_iep_count`, `section_ell_count`, `virtual_status`.
    - Educator-level: `staff_surrogate_id`, `assigned_sections_count`, `teacher_student_seat_load` (sum of seats across sections), `unique_students_per_educator_school_year` (state-computed unduplicated count).

Complete technical specifications and methodological definitions are detailed in `research/phase4a_data_request_specifications.md`.

---

### 4. Agency Contact & Inquiries

We welcome an initial technical conversation with KSDE's data management team to refine table mappings and minimize administrative effort. Thank you for your consideration and support of empirical research on Kansas public school capacity.
