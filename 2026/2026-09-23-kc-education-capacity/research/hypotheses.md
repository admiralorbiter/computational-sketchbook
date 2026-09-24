# Research Hypotheses: Kansas City Education Capacity Study
## Status & Empirical Adjudication (Phases 1–3C & Tasks 004A.1–004C.1)

## Core Framing
**Central Research Question:**
*Is insufficient adult instructional capacity the common constraint behind many of the problems teachers experience—and is class size the best observable proxy for that constraint?*

Rather than cataloguing grievances or designing an analysis to validate prior recollections, this project tests competing hypotheses against empirical administrative data. Every hypothesis has defined observation criteria and explicit falsification conditions.

---

### H1a — Ratio / Measurement Illusion Hypothesis
* **Status:** **STRONGLY SUPPORTED (Tasks 004A.1 & 004B.1)**
* **Hypothesis:** Reported headline pupil/teacher ratios substantially obscure and understate actual class sizes experienced by students and teachers in standard classrooms.
* **Mechanism:** Staffing ratios divide total enrollment by total certified FTE (including interventionists, reading coaches, speech pathologists, and special education teachers with small caseloads). Consequently, an overall 14–16:1 ratio can easily coexist with general education core sections of 24–28+ students without any deliberate data distortion.
* **Empirical Adjudication:** Validated across all 6 CRDC waves and NTPS state benchmarks. Building-wide high school PTR averages 14.5 to 16.2:1, while observed core math and science sections average 24 to 28+ on large suburban comprehensive high school campuses.

---

### H1b — Longitudinal Growth (Ballooning-Class) Hypothesis
* **Status:** **NOT SUPPORTED BY AVAILABLE PUBLIC AGGREGATE EVIDENCE (Reserved for Section Microdata)**
* **Hypothesis:** Actual instructional classroom loads have increased over the past 10–15 years, even if reported headline staffing ratios have remained stable.
* **Mechanism:** Shifting resource allocations, expansion of non-classroom specialist positions, or budgetary constraints have expanded core section headcounts over time.
* **Empirical Adjudication:** Neither national teacher survey data (NTPS: 2011–12: 24.2; 2015–16: 26.0; 2017–18: 23.3; 2020–21: 21.0) nor Kansas City longitudinal CRDC course averages show a secular ballooning in average class sizes over the decade (regional class-weighted means remaining in the 17.5 to 19.5 range). However, because CRDC data represent school-course aggregated offerings rather than full classroom section distributions, **H1b cannot be formally falsified until true section microdata are evaluated** (to verify whether the variance or right-tail of core sections expanded).

---

### H1c — The Allocation Wedge & Schedule Arithmetic Hypothesis
* **Status:** **STRONGLY SUPPORTED AS PHENOMENON; STRUCTURAL DECOMPOSITION UNRESOLVED REGIONALLY (Task 004B.1)**
* **Hypothesis:** A substantial structural wedge exists between reported pupil/teacher ratios and typical general-education classroom section sizes because federal and state teacher FTE counts include instructional personnel who carry small caseloads, provide specialized services, or do not bear standard core classroom rosters, compounded by instructional bell schedules.
* **Mechanism & Schedule Arithmetic:**
  $$\overline{\text{Section Size}} \approx \text{PTR}_{class} \times \left(\frac{P_{\text{student}}}{P_{\text{teacher}}}\right) = \text{PTR}_{class} \times \phi$$
* **Empirical Adjudication:** On campuses with a documented 5-of-7 teaching load ($\phi = 1.400$), schedule mechanics account for a large portion of the gap between building PTR and observed core sections (as demonstrated in the Shawnee Mission USD 512 case study, where a +10.4% high school staffing expansion was absorbed by moving to 5-of-7 while class sizes remained flat at 23–25). However, regionally, schools operate under diverse structures (6-of-7 with $\phi \approx 1.167$, 8-block with $\phi \approx 1.333$, and 5-of-7 with $\phi = 1.400$). The relative weights of teacher role specialization, instructional scheduling, and curriculum tracking remain partially unseparated across the broader metropolitan area.

---

### H2 — Complexity Hypothesis (Heterogeneity and Support Demands)
* **Status:** **MEANINGFULLY SUPPORTED FOR FORMAL ACCOMMODATIONS; OVERALL WORKLOAD MECHANISM UNRESOLVED (Task 004C.1)**
* **Hypothesis:** Class sizes themselves have remained relatively stable, but the effective burden of a classroom has escalated because student support needs (IEP/SPED status, Section 504 accommodation plans, English language learners, chronic absenteeism, and coverage duties) have become significantly more heterogeneous and demanding.
* **Mechanism (The Compound Workload Conceptual Framework):**
  $$\text{Instructional Load}_i = \sum_{j=1}^{K_i} \left[ n_{ij} \cdot \left( 1 + \omega_{\text{acc}} \cdot \text{AccShare}_{ij} + \omega_{\text{abs}} \cdot \text{AbsDrag}_{ij} \right) \right] + \text{Compliance}_i + \text{Coverage}_i - \text{ProtectedPlanning}_i$$
* **Empirical Adjudication:** 
  1. **Section 504 Accommodations Surged +93.5% (+1.92 Percentage Points):** Grew from 6,552 students (2.03%) in 2015–16 to 12,676 students (3.95%) in 2023–24. On large suburban campuses, 504 plans alone reach 5% to 10% of total enrollment.
  2. **Total Mandated Accommodations Rose to 16.41%:** Combining IDEA (12.46%) and Section 504 (3.95%), roughly 1 in 6 students across the metro carries legally binding individual modifications that regular teachers must document and execute.
  3. **Chronic Absenteeism Trajectory:** Jumped from 12.90% pre-pandemic to 35.14% during the pandemic shock, and plateaued post-pandemic at 24.68% (2021–22) and 24.69% (2022–23) (+11.8 percentage points above baseline). While daily attendance remains ~90–93%, chronic absence creates severe asynchronous re-teaching, grading, and parent follow-up friction.
  4. **Workload Synthesis:** While individual accommodation parameters are documented, the compound workload formula is treated strictly as a conceptual model rather than an empirically fitted regression.

---

### H3 — Distribution Hypothesis (Averages Concealing the Overcrowded Tail)
* **Status:** **SUPPORTED BY HISTORICAL JUDICIAL PRECEDENT; UNRESOLVED WITHOUT SECTION MICRODATA (Tasks 004A.1, 005A, 005B.1)**
* **Hypothesis:** District and school-wide average class sizes appear moderate because low-enrollment specialized sections (small-group intervention, self-contained SPED, specialized electives, AP/IB courses) skew the mean downward, while ordinary core foundation courses (e.g., 9th-grade Algebra I, Geometry, Biology) absorb large, overcrowded rosters.
* **Mechanism:** Uneven staffing allocation concentrates unserved seat volume into mandatory core academic sections, creating an asymmetric right-tail of severely overloaded classrooms.
* **Empirical & Judicial Adjudication:** 
  1. **Appellate Judicial Precedent (*Jenkins v. Missouri*, 890 F.2d 65 (8th Cir. 1989)):** The appellate court affirmed the remedial use of maximum class sizes, providing historical precedent for treating the upper tail—not merely averages—as policy-relevant. This provides judicial precedent for taking the overloaded tail seriously, though empirical validation of our modern distribution hypothesis depends on classroom section distributions.
  2. **CRDC Course Hierarchy:** Supported by CRDC curriculum hierarchy (e.g. Calculus averaging 17.0 vs. Geometry and Algebra II averaging 24–28+ on large suburban campuses).
  3. **Illustrative Tail Modeling (Task 005B):** Under an illustrative IID normal section simulation ($X_j \sim N(24.5, 5.2^2)$), shifting from 6-of-7 to 5-of-7 cuts modeled $P(R > 140)$ from 70.9% to 6.6% and virtually eliminates $P(R > 150)$ (from 40.7% to 0.9%), illustrating how schedule relief compresses the upper tail even when section averages are unchanged. Direct teacher-level section distributions remain the key missing public measure to empirically confirm this tail.

---

### H4 — Null / Counter-Hypothesis
* **Status:** **PARTIALLY WEAKENED BY SHIFTS IN ACCOMMODATION COMPOSITION; PARTIALLY SUPPORTED ON RAW HEADCOUNT**
* **Hypothesis:** Neither classroom size nor measurable instructional complexity has deteriorated substantially across the Kansas City region over the last 10–15 years.
* **Mechanism:** Historical recollections of smaller or simpler classrooms represent cognitive availability biases, selective memory, or broader societal stress rather than empirical shifts in school staffing, class rosters, or demographic composition.
* **Adjudication:** The data confirm that raw classroom headcount has **not** exploded (countering H1b), but **instructional accommodations (Section 504 +93.5%) and chronic absenteeism (+11.8 pp post-pandemic plateau) have expanded substantially**, weakening the pure null hypothesis H4.
