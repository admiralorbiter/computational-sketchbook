# Epistemic Boundaries and Measurement Limitations

Strict empirical discipline requires explicitly defining what the available federal datasets can and cannot measure.

---

## 1. School-Course Aggregates vs. True Classroom Section Counts

1. **Aggregation Over Sections:** CRDC collects only total course enrollment ($E$) and total number of class sections ($K$) per school. The derived measure $\bar C = E / K$ is the **school-course mean class size**.
2. **Unobservable Section Dispersion:** CRDC cannot observe within-school variation among sections. A reported 6 sections averaging 30 students could represent:
   - Six perfectly uniform sections: $(30, 30, 30, 30, 30, 30)$;
   - Or wide variance across honors, remedial, and co-taught sections: $(20, 25, 28, 32, 35, 40)$.
3. **Implication for Tail Shares:** Statements such as "X% of students are in classes $\ge 30$" are strictly inadmissible from CRDC data alone. The correct phrasing is:
   > *"X% of student enrollment is concentrated in school-course cells averaging $\ge 30$ students."*

---

## 2. Pupil-Teacher Ratio (PTR) is NOT Class Size

1. **Accounting vs. Classroom Reality:** Pupil-teacher ratio (from CCD or state registries) divides total school membership by total classroom teacher FTE ($FTE_{\text{teacher}}$).
2. **Scheduling Wedge:** In secondary schools, teachers typically instruct 4 or 5 periods out of a 6- or 7-period schedule, reserving 1 to 2 periods for planning, collaboration, and duty assignments. This mechanical schedule factor inflates true classroom size by 20% to 40% above PTR.
3. **Classification Drift:** CCD teacher FTE counts include instructional specialists, reading coaches, interventionists, and department chairs who do not manage standalone rostered classrooms.
4. **Discipline Rule:** Never substitute PTR for class size. CCD PTR is used exclusively as a baseline to quantify the **staffing-to-classroom wedge**.

---

## 3. Survey Wave Discontinuities and Comparability

1. **2013–14 Grade Spans:** In 2013–14, Algebra I and Geometry class counts spanned grades 7–12, whereas subsequent waves split middle school (7–8) and high school (9–12).
2. **2020–21 COVID-19 Discontinuity:** The 2020–21 CRDC was collected during peak COVID disruptions, featuring hybrid cohorts, simultaneous remote streaming, and atypical master schedules. It must not be treated as a smooth secular trend point.
3. **2023–24 Nonbinary Gender Classification:** The release of 2023–24 public data introduced the `_X` reporting category, expanding enrollment summations.

---

## 4. State Administrative Data Boundaries

1. **Collection vs. Public Download:** While Missouri (MOSIS) and Kansas (SO66/PBR) collect student-course-teacher section assignment rosters, these files contain protected FERPA records and are restricted.
2. **Public Data Scope:** All empirical findings in Phases 0–3 rely exclusively on audited public federal microdata and state aggregate releases.
