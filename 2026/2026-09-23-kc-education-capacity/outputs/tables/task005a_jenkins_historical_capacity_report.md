# Task 005A: Jenkins v. Missouri Historical Capacity Benchmark Reconstruction
## The 1985 Remedial Order, Appellate Affirmance of Maximums, and the Blueprint for Modern Teacher Roster Load

---

## 1. Executive Summary: The 40-Year Continuity of the Capacity Problem

A critical breakthrough in this project is the discovery that the measurement paradox we are addressing—why low reported pupil/teacher ratios coexist with large classroom sections and teacher overload—was **formally confronted and empirically decomposed forty years ago by the federal judiciary in Kansas City**.

In *Jenkins v. Missouri*, 639 F. Supp. 19 (W.D. Mo. 1985), the U.S. District Court (Judge Russell G. Clark) did not rely on simple pupil/teacher ratios. Instead, the court constructed almost exactly the multi-level capacity measurement architecture we are building today:
1. **Separated Specialized Staff:** Removed Chapter I and special education teachers from the denominator, uncovering an immediate **+4.4-student denominator wedge** in elementary grades.
2. **Identified the Planning-Time Capacity Mechanism:** Ordered the hiring of 54 art, music, and physical education specialists, plus 31 certified teachers and 31 aides, explicitly to purchase elementary teacher planning time (180 minutes weekly) rather than reducing homeroom headcounts.
3. **Counted Student Seats and Teaching Assignments:** In junior and senior high schools, the court counted total student-class enrollments (seats) and divided by teaching assignments (sections) to reveal ordinary course sections of 27.2 to 28.7 students.
4. **Pioneered Teacher Daily Roster Load as the Primary Metric:** The court declared that the most revealing measure of secondary instructional load was total students taught per teacher per day (149–154 students/day), establishing a binding remedial ceiling of **125 students per teacher per day**.
5. **Legal Primacy of the Maximum Over the Average (Hypothesis H3):** When the State of Missouri appealed Judge Clark's methodology, the Eighth Circuit explicitly held that the court was fully justified in using **maximum class sizes rather than averages** to determine teacher staffing requirements (*Jenkins v. Missouri*, 890 F.2d 65 (8th Cir. 1989)).

---

## 2. Structured Historical Benchmark Panel

From `data/processed/jenkins_historical_capacity_benchmarks.csv`:

| Year | Grade Band | Evidentiary Status | Headline PTR | Adjusted Classroom Load | Section Size | Daily Roster Load | Court Remedial Ceiling | Key Legal / Structural Finding |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1985** | Grades 1–3 | `formal_remedial_finding` | 22.14:1 | 26.6 | — | — | Class maximum 22 | Chapter I classes had 2 teachers per class (58 classes, 116 teachers). Removing special classes revealed ordinary load was 26.55, not 22.14. |
| **1985** | Grades 4–6 | `formal_remedial_finding` | 24.1:1 | 27.6 | — | — | Class maximum 27 | Adjusted for special two-teacher classes. State argued for average class size; Eighth Circuit affirmed use of maximums in 1989. |
| **1985** | Junior High (Grades 7–8) | `formal_remedial_finding` | 22.02:1 | — | 27.2 | 154.1 | Max 125 daily student roster | Court explicitly counted 37,457 student-classes across 1,376 teaching assignments for 243 teachers. 154 students/teacher/day. |
| **1985** | Senior High (Grades 9–12) | `formal_remedial_finding` | 24.8:1 | — | 28.7 | 148.8 | Max 125 daily student roster | Counted 52,362 student-classes across 1,824 teaching assignments for ~352 teachers. 148.76 students/teacher/day. |
| **1985** | District-Wide Remedial Order | `formal_remedial_finding` | — | — | — | — | K-3 <= 22; 4-6 <= 27; Sec <= 125/day | Eighth Circuit affirmed Judge Clark's use of maximum class sizes rather than averages to determine required staffing in 1989 (890 F.2d 65). |
| **1997** | Elementary Overall | `court_observation_not_finding` | 8.62–18.43:1 | — | 22–28 commonly (outliers >30) | — | MSIP Desirable Standards | Judge Clark explicitly stated these were observations, not findings of fact for unitary status. Elementary classes commonly 22-28. |
| **1997** | Middle School Overall | `court_observation_not_finding` | 10.30–14.83:1 | — | ~22–25 | 135–140 | MSIP Desirable Standards | Eighth Circuit noted observations were instructive regarding management and resource deployment, but not formal factual findings. |
| **1997** | High School Overall | `court_observation_not_finding` | 12.59–17.30:1 | — | Varies by school | Varies widely by campus | MSIP Desirable Standards | Proves that low teacher roster load is a resource condition, not a mechanical guarantee of student academic achievement. |


---

## 3. Deep-Dive: The 1985 Remedial Order (639 F. Supp. 19)

### A. Elementary Specialist Denominator Effect (The 4.4-Student Wedge)
In grades 1–3, the headline district statistic reported **8,603 students and 388.5 teachers**, producing an apparent pupil/teacher ratio of **22.14:1**.

However, the court inspected actual classroom organization (KCMSD Exhibit K-56). It discovered that **1,369 students were enrolled in 58 specialized Chapter I classes**, staffed by **116 teachers (2 teachers per class)**. When the court segregated these specialized classes from the general population:
$$\text{General Education Enrollment} = 8,603 - 1,369 = 7,234$$
$$\text{General Education Teachers} = 388.5 - 116.0 = 272.5$$
$$\text{Actual Classroom Ratio} = \frac{7,234}{272.5} = \mathbf{26.55:1}$$

Accounting for specialized instructional personnel immediately expanded the classroom load by **+4.41 students per teacher**! Furthermore, the court examined the distribution: **71.0% of the 338 elementary classrooms (240 rooms) exceeded the district's 22-student goal**, proving that 56 additional classroom teachers were required.

### B. Secondary Student Seats, Teaching Assignments, and Daily Roster Load
In secondary schools, the court recognized that dividing total students by total certified staff produced a completely misleading figure (22.0:1 in junior high, 24.8:1 in senior high). It examined master schedule exhibits (K-58 and K-59) to construct the true operational metrics:

1. **Junior High Schools (Grades 7–8):**
   - **Student-Class Enrollments (Seats):** 37,457
   - **Teaching Assignments (Sections):** 1,376
   - **Average Section Size:** $\frac{37,457}{1,376} = \mathbf{27.22}$ students per section
   - **Total Full-Time Teachers:** 243
   - **Average Sections Taught:** $\frac{1,376}{243} = 5.66$ sections
   - **Average Daily Roster Load:** $\frac{37,457}{243} = \mathbf{154.14}$ students per teacher per day!
   - **Overload Tail:** 7 of the 9 junior high schools exceeded the district's 125-student daily roster ceiling.

2. **Senior High Schools (Grades 9–12):**
   - **Student-Class Enrollments (Seats):** 52,362
   - **Teaching Assignments (Sections):** 1,824
   - **Average Section Size:** $\frac{52,362}{1,824} = \mathbf{28.71}$ students per section
   - **Total Full-Time Teachers:** ~352
   - **Average Daily Roster Load:** $\mathbf{148.76}$ students per teacher per day
   - **Overload Tail:** 8 of the 9 senior high schools exceeded the 125-student ceiling.

### C. The Planning-Time Capacity Mechanism
In 1985, Missouri AAA accreditation standards required elementary planning time during the school day and limited teachers to an average of 310 instructional minutes in a 6-hour day. KCMSD was out of compliance.

To remedy this, the court did not order smaller homerooms; it ordered the addition of **54 specialist teachers (art, music, PE)** to take students out of homerooms, providing classroom teachers with 180 minutes of weekly planning time, plus **31 certified teachers and 31 aides** for duty relief. This historical finding provides primary-source proof that **teacher staffing FTE can expand substantially without shrinking classroom rosters, because the added capacity purchases planning time, specialist instruction, and statutory compliance**.

---

## 4. Appellate Affirmance: The Legal Primacy of Maximum Class Size (890 F.2d 65)

In 1989, the State of Missouri appealed Judge Clark's remedial orders, arguing that teacher staffing requirements should be determined by **average class size** rather than **maximum class sizes**.

The appellate court affirmed the remedial use of maximum class sizes, providing historical precedent for treating the upper tail—not merely averages—as policy-relevant. This provides judicial precedent for taking the overloaded tail seriously, though empirical validation of our modern distribution hypothesis (Hypothesis H3) depends on classroom section distributions (*Jenkins v. Missouri*, 890 F.2d 65, 67 (8th Cir. 1989)).

---

## 5. The 1997 Unitary Status Decision (959 F. Supp. 1151) & Legal Caveat

Twelve years later, following roughly **$1.8 billion** in desegregation expenditures ($1.2B State, $600M KCMSD), Judge Clark re-examined KCMSD staffing:
- **Reported Staffing Ratios Were Exceptionally Low:** Elementary 8.6–18.4:1; Middle 10.3–14.8:1; High 12.6–17.3:1.
- **Judicial Observations:** The court noted that these ratios were artificially lowered by counting itinerant, special education, resource, and content teachers. In actual practice, elementary classes were commonly in the 22–28 range, and middle school teachers routinely carried 6 classes per day with 135–140 students/day.
- **Important Legal Caveat:** Judge Clark explicitly stated that these 1997 matters were **not intended to be findings of fact** and played no role in his unitary status decision; they were judicial observations on district management. The Eighth Circuit affirmed (122 F.3d 588), noting the observations were 'instructive.' In this research, we classify 1985 as `formal_remedial_finding` and 1997 as `court_observation_not_finding`.

---

## 6. Conceptual Reorientation: From 'Class Size' to 'Teacher Roster Load'

The Jenkins historical record reframes our entire analytical objective. Rather than searching for class size as the single missing variable, we adopt the court's multi-layered capacity hierarchy:

| Capacity Dimension | Historical Concept (Jenkins 1985) | Modern Public Equivalent (2026 Repo) |
| :--- | :--- | :--- |
| **1. Structural Staffing** | Enrollment ÷ Certified Teachers | CCD Reported Pupil/Teacher Ratio (PTR) |
| **2. Specialist-Adjusted Staffing** | General Enrollment ÷ General Teachers (excl Chapter I) | KSDE Classroom Teachers vs. Other Specialist Teachers |
| **3. Section Load** | Student-Class Seats ÷ Teaching Assignments | CRDC Course Average Class Size (Classes & Enrollment) |
| **4. Teacher Roster Load** | Student-Class Seats ÷ Full-Time Teachers | $\sum_{j=1}^{K} n_j$ (Total Daily Students Responsible For) |
| **5. Overloaded Tail Risk** | % Classrooms Exceeding Binding Ceiling | Roster Tail ($\% \ge 25, 30, 33$) & Maximum Standard |

### The Historical Continuity Hypothesis:
Comparing 1985 secondary daily loads (149–154 students/day) and 1997 middle school loads (135–140 students/day) to modern modeled loads (~125–145 students/day under 5-of-7 or 6-of-7 regimes) suggests that **raw secondary student headcounts per teacher may not have increased over 40 years—and may have slightly declined under expanded planning schedules**.

This strengthens the pivot toward **Hypothesis H2 (The Complexity Hypothesis)**: secondary teachers are carrying similar or slightly fewer students across the day, but each individual student represents dramatically higher instructional, legal, and operational complexity.

### Visual Reference:
See [`fig13_jenkins_capacity_framework.png`](../figures/fig13_jenkins_capacity_framework.png) for visual representations of the 1985 capacity wedges and the four-decade teacher daily roster load trajectory.
