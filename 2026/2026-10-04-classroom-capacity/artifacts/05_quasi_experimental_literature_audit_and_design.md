# Causal Identification at the Secondary Margin: Literature Audit & Quasi-Experimental Research Design
**Phase 7 & Phase 8 Master Framework: Evaluating Class Size Non-Linearities (25–35 Margin) via Natural Experiments**

**Document Version:** 1.0 (Phase 7 Literature Audit & Research Protocol)  
**Status:** WORKING PROTOCOL & RESEARCH DESIGN  
**Target Scope:** Departmentalized Secondary Courses (Grades 9–12: Algebra I, Geometry, Biology, English II)  
**Focal Treatment Margin:** 25 vs. 30 vs. 35 students per section  
**Candidate Jurisdictions:** Florida ($C=25$ statutory mandate) & Missouri (MOSIS relational administrative warehouse)  

---

## 1. Executive Summary & Strategic Architecture

With **Study D (Project STAR Replication) frozen**, the empirical investigation transitions from early elementary foundational literacy to the central unaddressed question in modern education economics:

> **What is the causal effect of moving between 25, 30, and 35 students in modern, departmentalized secondary classrooms?**

Project STAR established gold-standard experimental proof that reducing kindergarten through 3rd-grade class size from 22–25 down to 13–17 improves test scores by $+0.20$ standard deviations ($+5$ to $+8$ percentile points). However, as certified in Studies A, B, and C, early elementary self-contained classrooms operate under completely different structural dynamics than secondary schools:
1. **Instructional Structure:** Elementary teachers instruct a single self-contained cohort all day ($\sim 15\text{--}23$ total students), whereas secondary teachers instruct departmentalized subjects across 5 to 6 daily periods, managing aggregate rosters of **87 to 147 unique students daily**.
2. **Pedagogical Margin:** STAR evaluated a cut from 23 down to 15. In secondary policy, school closures, staffing shortages, and budget caps operate along the **25 to 35 margin** (e.g. running 4 sections of 30 vs. 5 sections of 24).
3. **Student Need Intensity:** As established in Study B, modern high school classes serve sharply higher concentrations of IEP/504 plans ($19.0\%$), English Learners ($9.1\%$), and chronic absenteeism ($32.0\%$), compounding the cognitive load on secondary teachers grading across dozens of students.

### The Revised Five-Phase Research Roadmap

Rather than leaping prematurely to an operationally expensive, politically fraught randomized trial, we pursue an econometrically disciplined quasi-experimental design leveraging administrative scheduling rules:

```
========================================================================================================================
PHASE      NAME                                PURPOSE & OPERATIONAL OUTPUT
========================================================================================================================
Phase 7    Literature & Econometric Audit      Audit existing quasi-experimental class size literature; document why the 
                                               modern secondary 25–35 margin is completely blank.
------------------------------------------------------------------------------------------------------------------------
Phase 8    Empirical Coverage Mapping          Map the parameter space: grade level x baseline class size x instructional load;
                                               synthesize theoretical mechanisms for non-linear teacher capacity.
------------------------------------------------------------------------------------------------------------------------
Phase 9A   Public Natural-Experiment           Audit Florida's statutory 25-student cap and local KC/MO rules via Six Gates:
           Feasibility Audit                   - Gate 0: Temporal & definitional equivalence (CRDC vs October Survey 2).
                                               - Gate 1: Institutional scope (traditional public classroom C=25 vs charters/choice).
                                               - Gate 2: First-stage section responsiveness (pre vs post-2023 penalty removal).
                                               - Gate 3: Discrete running-variable manipulation & bunching audit (mass points/donuts).
                                               - Gate 4: Public outcome alignment (school-level EOC means vs course enrollment).
                                               - Gate 5: Empirical support & statistical power (effective N in threshold bandwidths).
------------------------------------------------------------------------------------------------------------------------
Phase 9B   Preregistered Restricted-Data       Provisional 14-variable minimal relational request for FL DOE, Missouri DESE,
           Protocol                            or KC metro districts, iteratively refined by Phase 9A feasibility findings.
------------------------------------------------------------------------------------------------------------------------
Phase 9C   Causal Estimation & Execution       Estimate structural section-size effects using administrative microdata.
========================================================================================================================
```

---

## 2. Systematic Literature Audit: Quasi-Experimental Class Size Research

Existing causal research on class size is concentrated almost exclusively in primary grades or relies on policy shifts that conflate class size with teacher labor market dilution.

```
=====================================================================================================================================
STUDY                      METHODOLOGY                SETTING / GRADES    MARGIN TESTED   ESTIMATED EFFECT   SECONDARY GENERALIZABILITY
=====================================================================================================================================
Krueger (1999)             Randomized Controlled      Tennessee STAR      15 vs. 23       +0.20 SD           ZERO. Elementary self-contained;
                           Trial (RCT)                (Grades K–3)        (13-17 v 22-25) (+5.4 to +7.4 pp)  non-departmentalized; 15-23 margin.
-------------------------------------------------------------------------------------------------------------------------------------
Angrist & Lavy (1999)      Regression Discontinuity   Israel Public       20 to 40        +0.10 to +0.15 SD  LOW. Elementary (grades 3–5);
                           (Maimonides' Rule, C=40)   (Grades 3–5)        (Cap = 40)      per 10 students    centralized curriculum; 1991 Israel.
-------------------------------------------------------------------------------------------------------------------------------------
Hoxby (2000)               Cohort Population Shocks   Connecticut Public  15 to 30        Zero / Null        LOW. Grades 4 and 6 only;
                           & District Rules           (Grades 4 & 6)      (Mean ~21)      (Beta ~ 0)         elementary/middle cohorts.
-------------------------------------------------------------------------------------------------------------------------------------
Jepsen & Rivkin (2009)     Statewide Mandate Panel    California CSR      20 vs. 30       Gross positive,    MODERATE. Highlights teacher hiring
                           with Teacher Controls      (Grades K–3)        (Cap = 20)      Net near zero      dilution; elementary only.
-------------------------------------------------------------------------------------------------------------------------------------
Chingos (2012)             Difference-in-Differences  Florida CSR         18 (K-3)        Small / Null       LOW. Evaluated broad mandate phase-in
                           across Mandate Burden      (Grades 3–8)        22 (4-8)        (Beta ~ 0)         (district/school averages), not high school.
-------------------------------------------------------------------------------------------------------------------------------------
Angrist et al. (2019)      Modern RD Donut-Hole       Israel 10-Yr Panel  20 to 40        Attenuated         LOW. Confirms sorting/manipulation
                           & Density Corrections      (Grades 4–5)        (Cap = 40)      +0.05 to +0.08 SD  concerns; elementary only.
=====================================================================================================================================
```

### Detailed Synthesis of Core Literature

#### 1. Angrist & Lavy (1999) & The Maimonides' Rule Precedent
- **Identification Logic:** 12th-century rabbinic scholar Maimonides proposed: *"Twenty-five children may be put in the charge of one teacher. If the number in each class exceeds twenty-five but is not more than forty, he shall have an assistant... If there are more than forty, two teachers must be appointed."* Modern Israeli law operationalized this as a strict maximum cap of 40 students per class.
- **Instrument Formulation:** If total cohort enrollment is $E$, the predicted number of classes is $\lceil E / 40 \rceil$, creating predicted class size:
  $$\widehat{CS} = \frac{E}{\lfloor (E-1)/40 \rfloor + 1}$$
- **Discontinuities:** Predicted class size drops abruptly from 40 to 20.5 at $E=41$, from 40 to 27.0 at $E=81$, and from 40 to 30.2 at $E=121$.
- **Relevance to Secondary Design:** Angrist & Lavy proved that administrative section-splitting rules generate massive exogenous variation in class size without requiring experimental randomization. However, their empirical application was restricted to elementary grades 3, 4, and 5.

#### 2. Angrist, Lavy, Leder-Luis, & Shany (2019) — "Maimonides' Rule Redux"
- **Methodological Warning:** Re-examining the Israeli data with modern regression discontinuity techniques revealed that enrollment near the threshold is subject to strategic sorting: parents in affluent communities avoid schools operating just below the cutoff (class sizes near 39–40) or lobby principals to open an unauthorized extra section.
- **Empirical Lesson for Us:** Any quasi-experimental design using class size caps **must** include:
  - Formal McCrary density tests to verify that enrollment is smooth around the threshold.
  - Donut-hole RD specifications excluding observations immediately adjacent to the threshold ($\pm 1$ student).
  - Predetermined student baseline covariate balance tests across the threshold.

#### 3. Chingos (2012) — The Florida Statewide CSR Mandate
- **Context:** Florida's 2002 constitutional amendment required school districts to phase in class size reductions:
  - Pre-K to Grade 3: Maximum 18 students.
  - Grades 4 to 8: Maximum 22 students.
  - Grades 9 to 12 (Core Courses): Maximum 25 students.
- **Findings:** Chingos examined the policy phase-in using district-by-grade variation, finding little to no effect on FCAT math and reading scores in grades 3 through 8.
- **Why Florida Remains Open for High School:**
  1. Chingos examined **grades 3 through 8**, completely omitting high school End-of-Course (EOC) performance.
  2. Chingos evaluated the **broad statewide policy intervention** during the 2003–2009 phase-in period when compliance was measured as *district-wide* or *school-wide averages*, which forced massive hiring surges and capital construction.
  3. Chingos did **not** estimate the sharp, local regression discontinuity generated by individual course section-formation thresholds ($25 \to 26$, $50 \to 51$) under modern classroom-level enforcement.

#### 4. The Complete Empirical Void in Modern High Schools
Across the entire empirical economics of education literature, there is a **complete void** regarding the causal effect of class size in modern departmentalized secondary schools:
- We do not know whether reducing Algebra I class size from 32 to 24 improves student mastery or algebra proficiency.
- We do not know whether the returns to class size reduction are non-linear (e.g. negligible from 35 to 30, but steep from 28 to 22).
- We do not know how class size interacts with modern secondary teacher roster burdens (managing 150 students across 5 periods vs. 110 students).

---

## 3. Econometric Framework: The Scheduling-Rule Discontinuity Design

### The Structural High School Scheduling Model

Let $s$ denote school, $c$ denote a specific core academic course (e.g., Algebra I, Geometry, Biology I, English II), and $t$ denote academic year.

Let $E_{sct}$ be the total verified student enrollment demanding course $c$ in school $s$ at time $t$. Under a maximum class size threshold $C$ (such as Florida's statutory cap of $C=25$), the institutional scheduling algorithm predicts that the school must create:
$$K_{sct}^* = \left\lceil \frac{E_{sct}}{C} \right\rceil$$
sections.

The predicted class size under mechanical rule adherence is:
$$\widehat{CS}_{sct} = \frac{E_{sct}}{\lceil E_{sct} / C \rceil} = \frac{E_{sct}}{K_{sct}^*}$$

```
========================================================================================================================
COURSE ENROLLMENT (E)    PREDICTED SECTIONS (K*)    PREDICTED CLASS SIZE (CS_hat)    THRESHOLD JUMP (DELTA CS_hat)
========================================================================================================================
23 students              1 section                  23.0 students                    -
24 students              1 section                  24.0 students                    -
25 students              1 section                  25.0 students (at cap)           -
------------------------------------------------------------------------------------------------------------------------
26 students [THRESHOLD]  2 sections                 13.0 students                    -12.0 students (SHARP DROP)
27 students              2 sections                 13.5 students                    -
...
49 students              2 sections                 24.5 students                    -
50 students              2 sections                 25.0 students (at cap)           -
------------------------------------------------------------------------------------------------------------------------
51 students [THRESHOLD]  3 sections                 17.0 students                    -8.0 students (SHARP DROP)
52 students              3 sections                 17.3 students                    -
...
75 students              3 sections                 25.0 students (at cap)           -
------------------------------------------------------------------------------------------------------------------------
76 students [THRESHOLD]  4 sections                 19.0 students                    -6.0 students (SHARP DROP)
========================================================================================================================
```

### Two-Stage Least Squares Formulation

#### Stage 1: First-Stage Response of Actual Class Size
$$\text{ActualCS}_{sct} = \alpha + \pi \widehat{CS}_{sct} + f(E_{sct}) + \mu_{sc} + \lambda_t + \mathbf{X}_{sct}' \mathbf{\Gamma} + \epsilon_{sct}$$
where:
- $\text{ActualCS}_{sct}$ is the observed average section size in school $s$, course $c$, year $t$.
- $\widehat{CS}_{sct}$ is the Maimonides-style predicted class size based strictly on total enrollment $E_{sct}$ and statutory cap $C$.
- $f(E_{sct})$ is a continuous control function for enrollment (e.g. linear spline, quadratic, or local linear polynomial) to ensure identification comes strictly from the discontinuous steps, not the smooth running variable.
- $\mu_{sc}$ is school $\times$ course fixed effects, absorbing time-invariant school-course unobservables.
- $\lambda_t$ is academic year fixed effects.
- $\mathbf{X}_{sct}$ is a vector of aggregated student baseline demographics (free/reduced lunch, special education, English Learner, race, prior achievement).
- $\pi$ captures the **first-stage compliance parameter**. If schools comply mechanically, $\pi \approx 1$. If schools ignore the rule or use administrative waivers, $\pi \to 0$.

#### Stage 2: Second-Stage Structural Outcome Equation
$$\text{Achievement}_{sct} = \alpha + \beta \widehat{\text{ActualCS}}_{sct} + f(E_{sct}) + \mu_{sc} + \lambda_t + \mathbf{X}_{sct}' \mathbf{\Gamma} + u_{sct}$$
where:
- $\text{Achievement}_{sct}$ is the standardized End-of-Course (EOC) scale score mean or pass rate.
- $\beta$ is the causal parameter of interest: the marginal effect on student achievement of a 1-student increase in secondary section size.

---

## 4. Candidate Natural Experiment 1: Florida's 25-Student High School Mandate

Florida provides an extraordinary institutional environment for testing secondary class size because the 25-student cap is **statutory, statewide, and applies specifically to core high school courses**.

### Statutory Framework: Florida Statute § 1003.03
1. **Core Academic Definition:** The 25-student maximum applies to all high school courses in:
   - Mathematics (Algebra I, Geometry, Algebra II, etc.)
   - Language Arts (English I, II, III, IV)
   - Science (Biology I, Chemistry, Physics, etc.)
   - Social Studies (World History, US History, Government, Economics)
2. **Measurement Level & Institutional Exclusions:** Under current law (s. 1003.03, F.S.), compliance for **traditional public schools** is calculated at the **individual classroom level** based on student membership in the October Full-Time Equivalent (FTE) Survey 2. Crucially, **charter schools and district-operated schools of choice are evaluated at the school-average level**, not the individual classroom level; they must be excluded or modeled separately in the first-stage discontinuity audit.
3. **Statutory Penalty Mechanism & The 2023 Regime Shift:** Historically, districts failing to meet class size caps faced statutory reductions in their Florida Education Finance Program (FEFP) state funding allocations. However, **the Florida Legislature eliminated the financial penalty in 2023**. For 2024–25 and 2025–26, noncompliant districts/schools submit **corrective compliance plans** rather than facing funding clawbacks. This creates an explicit empirical test: *Did removing the financial enforcement mechanism in 2023 weaken the first-stage discontinuity at 25?* Rather than pooling all years blindly, the empirical design explicitly models pre-2023 vs. post-2023 compliance behavior.

### Public Data Availability & The "Catch"
- **Publicly Available:**
  1. District-level and school-level class size compliance reports published annually by the Florida Department of Education (FDOE).
  2. School-level End-of-Course (EOC) assessment results: mean scale scores, percent Level 3+ (proficient), and test-taker counts for Algebra I, Geometry, Biology, and US History.
  3. School-level demographic files and total school enrollment.
- **The "Catch" (Access Restriction):**
  - While school-level summary reports are publicly downloadable, Florida's detailed **classroom-level class-size data file** is distributed directly to district Management Information Systems (MIS) contacts via secure file transfer, rather than posted as an open-access bulk CSV.
  - School-level EOC reports pool all students taking the exam (e.g. 9th, 10th, and middle-school accelerated students).
- **Implication:** Florida public data allow us to audit **feasibility, threshold mechanics, and aggregate first-stage plausibility (Phase 9A)**, but estimating clean structural parameters will require requesting the detailed course-section file (Phase 9B).

---

## 5. Candidate Natural Experiment 2: Missouri DESE & MOSIS Infrastructure

While Florida has the statutory cap, **Missouri possesses the ideal administrative data warehouse**.

### The Missouri Longitudinal Data System (MOSIS)
Under the Missouri Department of Elementary and Secondary Education (DESE), the state operates an integrated longitudinal data system that explicitly maintains the exact four-way relational link required for secondary causal identification:

$$\text{Student} \longleftrightarrow \text{Section} \longleftrightarrow \text{Teacher} \longleftrightarrow \text{Course} \longleftrightarrow \text{Assessment Outcome}$$

```
========================================================================================================================
MOSIS DATA COLLECTION FILE    DESE DESCRIPTION & RECORD CONTENTS
========================================================================================================================
Course Assignment File        Submitted in October & June. Contains educator's state ID, unique course code, section ID,
(Educator Level)              grade level, semester/term, instructional minutes per week, and verified section enrollment.
------------------------------------------------------------------------------------------------------------------------
Student Assignment File       Submitted in October & June. Establishes the exact student-to-course and student-to-section
(Student Level)               linkage for every student enrolled in a Missouri public high school.
------------------------------------------------------------------------------------------------------------------------
Student Demographic File      Tracks deidentified student ID, free/reduced lunch, IEP/special education, 504 plan,
(Core Data)                   English Learner (EL) status, race, ethnicity, gender, attendance rate, and enrollment mobility.
------------------------------------------------------------------------------------------------------------------------
End-of-Course (EOC) File      Mandatory statewide assessment results: Algebra I, English II, Biology, Government.
                              Contains student-level continuous scale scores, achievement levels, and test dates.
------------------------------------------------------------------------------------------------------------------------
MAP Prior Achievement File    Grades 3–8 Missouri Assessment Program (MAP) math and reading scale scores, providing
                              the essential lagged baseline control for student human capital.
========================================================================================================================
```

### Missouri Quasi-Experimental Levers
Even without a constitutional statewide cap like Florida's, Missouri high schools generate sharp quasi-experimental section cutoffs due to:
1. **District Staffing Formulas:** Large metro districts (e.g. Kansas City Public Schools, suburban Jackson/Clay/Platte districts, St. Louis County districts) operate with board-approved staffing ratios (e.g. staffing high school core classes at 1 FTE per 28 or 30 students).
2. **Collective Bargaining & Policy Caps:** District collective bargaining agreements (CBAs) or school board policies frequently establish contractual class size targets (e.g. class sizes shall not exceed 28 without overload pay).
3. **Physical Room Capacity Constraints:** Science lab stations (often capped at 24 or 28 stations for fire and safety codes) impose physical cutoffs on Biology and Chemistry sections.

---

## 6. Phase 9A: Public Natural-Experiment Feasibility Audit Protocol

Before requesting restricted administrative microdata, we execute a rigorous **Six-Gate Decision Tree** to determine whether Florida's public data can support a credible quasi-experimental design:

```
+---------------------------------------------------------------------------------------------------+
|                            PHASE 9A: SIX-GATE FEASIBILITY DECISION TREE                           |
+---------------------------------------------------------------------------------------------------+
|  [GATE 0: MEASUREMENT & TEMPORAL ALIGNMENT (STOPPING RULE)]                                       |
|  Verify temporal and definitional equivalence between public course enrollment E, section         |
|  counts K, and the operative Florida October Survey 2 compliance census.                          |
|  STOPPING RULE: If E and K represent different dates/universes, do not interpret discontinuity    |
|  as the statutory first stage.                                                                    |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 1: INSTITUTIONAL SCOPE & EXCLUSIONS]                                                       |
|  Filter strictly to traditional public schools evaluated at individual classroom C=25.            |
|  Exclude charter schools and district schools of choice (evaluated at school-average level).       |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 2: FIRST-STAGE SECTION RESPONSIVENESS & 2023 REGIME SPLIT]                                 |
|  Test whether section counts jump discontinuously around 25, 50, and 75, and class size falls.    |
|  Explicitly test pre-2023 (binding FEFP financial penalties) vs. post-2023 (corrective plans).    |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 3: DISCRETE RUNNING-VARIABLE MANIPULATION & BUNCHING AUDIT]                                |
|  Inspect mass points around integer enrollment thresholds (25, 50, 75).                           |
|  Test excess/deficient probability below/above cutoffs; estimate discrete-RD & donut models.      |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 4: PUBLIC OUTCOME ALIGNMENT]                                                               |
|  Evaluate whether Florida school-level EOC reports (Algebra I, Geometry, Biology I, US History)   |
|  align tightly enough with course enrollment to detect structural effects without microdata.      |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 5: EMPIRICAL SUPPORT & STATISTICAL POWER]                                                  |
|  Audit effective sample size in local bandwidths around thresholds (E in [20, 30], [45, 55]).      |
|  Confirm sufficient observation counts on both sides of each cutoff to support estimation.        |
+---------------------------------------------------------------------------------------------------+
```

### Detailed Gate Specifications

#### Gate 0 — Measurement & Temporal Alignment (The Foundational Stopping Rule)
- **The Timing Question:** Does the public course enrollment variable ($E_{sct}$) measure the student roster that existed when the section-count decision ($K_{sct}$) was made?
- **The CRDC vs. FDOE Roster Break:** Florida statutory compliance is calculated from student course records submitted during the **October Survey 2 membership census**. By contrast, CRDC course enrollment can reflect cumulative enrollment across the school year or combine terms in 4x4 block-scheduled schools.
- **Stopping Rule:** If the numerator (students) and denominator (sections) do not represent the same roster universe and census date, any observed discontinuity may be an artifact of schedule aggregation. If Gate 0 fails, public data cannot identify the statutory first stage, pointing directly to the necessity of administrative microdata.

#### Gate 1 — Institutional Scope & Legal Exclusions
- Under Florida Statute § 1003.03 and FDOE compliance guidelines:
  1. **Traditional Public Schools:** Evaluated at the **individual classroom level** for all core courses. This is our target estimation universe.
  2. **Charter Schools:** Evaluated at the **school-wide average** across all classrooms, exempt from classroom-level caps.
  3. **District-Operated Schools of Choice:** Evaluated at the **school-wide average**.
- **Action:** Exclude charter schools and schools of choice from the primary discontinuity sample, or analyze them as an explicit non-binding placebo group.

#### Gate 2 — First-Stage Section Responsiveness & The 2023 Penalty Removal
- **Primary Hypothesis:** $\Pr(K_{sct} = 2 \mid E_{sct} = 26) \gg \Pr(K_{sct} = 2 \mid E_{sct} = 24)$.
- **The 2023 Legislative Regime Break:** In 2023, the Florida Legislature eliminated the statutory financial penalty (withholding of FEFP state funding allocations) for non-compliance, replacing it with a requirement to submit a corrective compliance plan.
- **Empirical Strategy:** Split the panel into pre-2023 (binding financial penalties) and post-2023 (corrective compliance plan regime). Test whether the compliance parameter $\pi$ attenuated after the removal of monetary sanctions:
  $$\text{ActualCS}_{sct} = \alpha + \pi_1 \widehat{CS}_{sct} + \pi_2 (\widehat{CS}_{sct} \times \text{Post2023}_t) + f(E_{sct}) + \mu_{sc} + \lambda_t + \epsilon_{sct}$$

#### Gate 3 — Discrete Running-Variable Manipulation & Bunching Audit
- **Why Naive McCrary Fails:** Course enrollment $E_{sct}$ is an integer-valued running variable with discrete mass points (e.g. natural cohort sizes, multi-section multiples). Standard continuous-density McCrary tests assume a smooth continuous density and can generate spurious rejection.
- **Discrete Bunching Protocol:**
  1. Inspect the frequency distribution of integer enrollment $E$ for anomalous mass points immediately at or below $C=25$, $50$, and $75$.
  2. Test for excess probability mass at $E=25$ relative to $E=26$ using discrete bunching estimators (Chetty et al. 2011; Kleven 2016).
  3. Implement **donut-hole RD specifications** dropping $E \in \{24, 25, 26\}$ to verify that estimates are not driven by strategic student reallocation near the threshold.
  4. Test for predetermined student covariate balance (FRL share, minority share, baseline SWD) across cutoffs.

#### Gate 4 — Public Outcome Alignment
- Florida publishes annual school-level End-of-Course (EOC) reports containing mean scale scores, percent Level 3+ (proficient), and test-taker counts for **Algebra I, Geometry, Biology I, and US History** (including current 2024–2026 reports).
- **Feasibility Evaluation:** Test whether school-level EOC mean scale scores can be matched cleanly to school-course enrollment and sections, or whether within-school heterogeneity (e.g. middle-school accelerated students taking Algebra I vs. high-school repeaters) creates unresolvable aggregation bias.

#### Gate 5 — Empirical Support & Statistical Power
- A statistically valid discontinuity requires sufficient mass in the local bandwidths on both sides of each cutoff.
- **Empirical Audit:** In Florida CRDC course data, there are **2,318 school-course-year observations** with enrollment in $[20, 30]$, **1,294 observations** in $[45, 55]$, and **977 observations** in $[70, 80]$. We will evaluate whether statistical power is sufficient for a minimum detectable effect size of $0.05\text{--}0.08$ SD under school $\times$ course clustering.

---

## 7. Phase 9B: Preregistered Administrative Microdata Protocol (Provisional Draft)

If Phase 9A demonstrates that public data cannot resolve within-school sorting or exact October survey rosters, we submit a preregistered microdata request. Rather than locking a static specification prematurely, this **provisional minimal layout** incorporates the structural nuances identified by the Phase 9A design audit:

```
========================================================================================================================
#   VARIABLE NAME            TYPE          PURPOSE IN ECONOMETRIC SPECIFICATION & DESIGN AUDIT
========================================================================================================================
1   student_id_anon          String (Hash) Anonymous longitudinal student identifier for tracking across grades.
2   school_id_nces           String        NCES school identifier for school fixed effects (alpha_s).
3   academic_year            Integer       Academic school year for year fixed effects (lambda_t).
4   course_code_state        String        State course code (restricted to Algebra I, Geometry, Biology, English II).
5   section_id               String        Unique classroom section identifier within school-year-course.
6   teacher_id_anon          String (Hash) Anonymous teacher identifier for classroom clustering and teacher FE.
7   term_schedule_structure  String        Term start/end dates, minutes/week, and schedule type (4x4 block vs 7-period).
8   team_teaching_flag       Boolean       Identifies co-teaching / team-teaching classrooms (statutory exemption audit).
9   october_census_headcount Integer       Official verified section headcount at the October membership census date.
10  pre_assignment_demand    Integer       School-course pre-assignment demand count (ideal exogenous running variable).
11  eoc_scale_score          Float         Standardized End-of-Course continuous scale score (Primary Dependent Variable).
12  prior_achievement_score  Float         Standardized prior-year MAP (Grade 8) scale score (Baseline Human Capital).
13  prior_retention_flag     Boolean       Identifies course repeaters vs. first-time enrollees (critical for Algebra I).
14  student_demographics     Bitflags      Individual binary flags: FRL, IEP/Special Ed, Section 504, EL status, race, sex.
15  enrollment_duration_days Integer       Days enrolled in course section prior to assessment (exposure dose).
16  student_attendance_rate  Float         Course-specific or annual attendance rate during the enrolled academic term.
========================================================================================================================
```

### Critical Refinements Identified for Administrative Request
1. **Pre-Assignment Course Demand vs. Realized Section Enrollment:** Realized enrollment in a section is a post-scheduling outcome. Observing total pre-registration course requests before administrators split sections provides the purest exogenous running variable.
2. **Co-Teaching / Team-Teaching Exemption:** Under Florida law, a classroom with 48 students and two certified teachers complies with the 25-student cap (ratio of 24:1). Without a co-teaching indicator, apparent non-compliance is misclassified.
3. **Repeater / Acceleration Heterogeneity:** High school Algebra I pools advanced 8th graders, on-track 9th graders, and repeating 10th graders. Separating first-time test-takers is essential for internal validity.

---

## 8. Summary & Next Immediate Actions

1. **Phase 7 (Literature Audit):** Certified. The literature demonstrates that the **25–35 departmentalized secondary margin is an open empirical frontier**.
2. **Phase 8 (Coverage Mapping):** Certified. Parameter space mapped across elementary self-contained vs. secondary departmentalized structures.
3. **Next Operational Step (Phase 9A Execution):**
   - Execute **Gate 0** (Measurement & Temporal Alignment audit comparing CRDC course enrollment against Florida October Survey 2 documentation).
   - Execute **Gate 1 & Gate 2** (Extract traditional Florida public high schools; test section-count jumps at 26, 51, and 76 across pre-2023 vs. post-2023 penalty regimes).
   - Execute **Gate 3** (Discrete bunching test around 25, 50, and 75).
   - Report findings across the Six Gates to determine whether public data suffice or whether Phase 9B microdata must be requested immediately.
