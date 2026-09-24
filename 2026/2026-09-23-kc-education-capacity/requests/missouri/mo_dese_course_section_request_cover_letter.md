# Research Data Request: Course Assignment, Student Assignment & Section Microdata

**To:**  
Office of Data System Management  
Missouri Department of Elementary and Secondary Education (MO DESE)  
PO Box 480, Jefferson City, MO 65102  

**From:**  
Kansas City Metropolitan Education Capacity Study Research Team  

**Date:** September 24, 2026  
**Subject:** Formal Research Data Request: De-identified Longitudinal Course Section and Roster Microdata (MARC Region LEAs, SY 2014–15 to 2024–25)

---

### 1. Executive Summary & Research Justification

The Kansas City Metropolitan Education Capacity Study is an independent quantitative research initiative investigating adult instructional capacity, teacher scheduling, and class-size distributions across the 9-county Kansas City metropolitan region. 

Over the 2014–15 through 2024–25 decade, federal Common Core of Data (CCD) and state Core Data filings demonstrate a significant regional capacity expansion: regional enrollment remained essentially flat (-0.73%), while reported certified teacher FTE expanded by +8.88% across fully regional LEAs. Consequently, regional pupil/teacher ratios declined from 14.85 to 13.54 students per teacher FTE.

However, headline pupil/teacher ratios aggregate all certified instructional personnel (special education case managers, reading interventionists, instructional coaches) and do not reflect classroom section sizes experienced by students or daily roster loads carried by teachers. While administrative ratios trended downward, classroom educators frequently report secondary core academic class sizes of 25–30+ students. 

To evaluate whether added instructional capacity was absorbed by specialized roles, elective course proliferation, co-teaching models, or teacher planning periods, the research team formally requests de-identified section-level course and roster data.

---

### 2. Statutory Authority & FERPA Compliance

This request is submitted pursuant to the research and audit exceptions under the **Family Educational Rights and Privacy Act (FERPA), 34 CFR § 99.31(a)(6)**, which permits the disclosure of education records to organizations conducting studies for or on behalf of educational agencies to improve instruction.

**Strict Privacy Commitments:**
1. **Zero Direct Student PII:** The researchers request **no student names, Social Security numbers, state student IDs (MOSIS IDs), birthdates, or street addresses**.
2. **De-identification via Surrogate IDs:** We request that MO DESE replace all educator and student identifiers with cryptographically salted, one-way hashed surrogate IDs (or sequential integers) that remain stable across files within a school year.
3. **FERPA Data Protection Agreement:** The research team is prepared to execute MO DESE's standard Data Use Agreement (DUA) and adhere to all data security, encryption, and destruction protocols upon study completion.
4. **Public Small-Cell Suppression:** Any public-facing reports, tables, or academic publications will strictly adhere to MO DESE suppression guidelines ($n < 5$).

---

### 3. Requested Scope & Data Elements

#### 3.1 Geographic & Temporal Scope
- **Geographic Universe:** All public school districts and public charter LEAs in the five Missouri counties of the MARC region: **Jackson, Clay, Platte, Cass, and Ray**.
- **School Years Requested:** 
  - Priority Anchor Years: **2014–15**, **2019–20**, and **2024–25**.
  - Preferred (if standard extraction pipeline allows): Annual panel (2014–15 through 2024–25).

#### 3.2 Target Collections & Two-Tier Architecture
We request linkage across October Core Data collections:
1. **Course Assignment (MOSIS Screen 20)**
2. **Student Assignment (MOSIS)**
3. **Educator Core / Educator School (MOSIS Screen 18)**

To accommodate agency administrative bandwidth and privacy policies, we propose a **two-tier structure**:

- **Tier 1 (Preferred — De-identified Microdata Extract):**
  - Section records linked to stable surrogate educator IDs and surrogate student IDs.
  - Fields: `school_year`, `district_code`, `school_code`, `course_code` (6-digit MOSIS), `course_title`, `subject_area`, `section_id`, `period_number`, `term_code`, `educator_surrogate_id`, `duty_code` (001–099), `teacher_fte_assigned`, `co_teacher_flag`, `student_surrogate_id`, `student_grade_level`, `student_iep_status` (Y/N), `student_ell_status` (Y/N), `delivery_mode`.
- **Tier 2 (Fallback — Agency-Aggregated Section & Teacher Summary):**
  - If student-level surrogate IDs cannot be released, MO DESE provides aggregated section and teacher summaries with **zero student-level records**:
    - Section-level: `section_id`, `course_code`, `section_enrollment` (headcount), `section_iep_count`, `section_ell_count`, `delivery_mode`.
    - Educator-level: `educator_surrogate_id`, `assigned_sections_count`, `teacher_student_seat_load` (sum of seats across sections), `unique_students_per_educator_school_year` (state-computed unduplicated count).

Full technical variable specifications and mathematical definitions are detailed in the attached technical document: `research/phase4a_data_request_specifications.md`.

---

### 4. Agency Contact & Inquiries

Please direct all questions, technical inquiries, or Data Use Agreement paperwork to the study research team. We welcome an initial technical consultation with MO DESE's data system team to discuss extraction parameters and ensure minimal burden on agency staff.

Thank you for your partnership in advancing empirical research on Missouri public education capacity.
