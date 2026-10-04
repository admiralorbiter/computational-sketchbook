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
Phase 9A   Public Natural-Experiment           Audit Florida's statutory 25-student high school core cap and local KC rules:
           Feasibility Audit                   1. Verify scheduling rules & statutory thresholds.
                                               2. Test for first-stage section splitting using public course data.
                                               3. Audit manipulation / McCrary density around cutoffs.
                                               4. Evaluate public school-level EOC outcome alignment.
------------------------------------------------------------------------------------------------------------------------
Phase 9B   Preregistered Restricted-Data       If Phase 9A confirms a valid first stage, preregister the full IV/RD design
           Protocol                            and submit a precise 14-variable microdata request to FL DOE, Missouri DESE, 
                                               or Kansas City metro districts.
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
2. **Measurement Level:** Under current law (s. 1003.03, F.S.), compliance for traditional public schools is calculated at the **individual classroom level** based on student membership in the October Full-Time Equivalent (FTE) Survey 2.
3. **Financial Penalties:** Districts that fail to meet class size requirements face statutory reductions in their Florida Education Finance Program (FEFP) state funding allocations.

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

Before requesting restricted state files, we execute a rigorous four-stage public-data audit:

```
+---------------------------------------------------------------------------------------------------+
|                                 PHASE 9A: FOUR EMPIRICAL GATES                                    |
+---------------------------------------------------------------------------------------------------+
|  [GATE 1: RULE AUDIT]                                                                             |
|  Identify statutory and contractual caps (Florida C=25; KC metro board policies C=28/30).         |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 2: FIRST-STAGE RESPONSIVENESS]                                                             |
|  Test whether section counts jump discontinuously when course enrollment crosses thresholds:      |
|  Pr(Sections = 2 | E = 26) >> Pr(Sections = 2 | E = 24).                                          |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 3: DENSITY & MANIPULATION AUDIT]                                                           |
|  Run McCrary density test on enrollment E. Verify no clumping immediately below cutoff.           |
|  Verify baseline student covariates are balanced across the threshold.                           |
|                                    |                                                              |
|                                    v                                                              |
|  [GATE 4: OUTCOME ALIGNMENT]                                                                      |
|  Evaluate whether school-level EOC outcomes (Algebra I / Biology) align tightly enough with       |
|  course-level enrollment to detect structural effects without individual microdata.               |
+---------------------------------------------------------------------------------------------------+
```

### Empirical Gate Descriptions
1. **Gate 1 — Institutional Rule Verification:**
   - Review Florida Administrative Code Rule 6A-1.0943 and statutory exemptions (e.g. team teaching, schools of choice flexibility).
   - Review Missouri school board policy manuals and master agreements across Kansas City metro districts (KCPS, Independence, Lee's Summit, North Kansas City).
2. **Gate 2 — Section Formation Responsiveness (First Stage):**
   - Using available public course data (CRDC high school STEM files or Florida state course distributions), test whether observed section counts respond to enrollment.
   - If schools smooth section sizes by cross-scheduling or ignoring caps, the first stage fails ($\pi \approx 0$), terminating the design.
3. **Gate 3 — Manipulation & McCrary Density Audit:**
   - Estimate the McCrary (2008) density discontinuity:
     $$\theta = \ln \lim_{E \downarrow C} g(E) - \ln \lim_{E \uparrow C} g(E)$$
   - A statistically significant spike in enrollment density just below the threshold indicates systematic manipulation (counselors holding enrollment at 25 or 50 to avoid funding an additional section), violating the continuity assumption.
4. **Gate 4 — Public Outcome Alignment:**
   - Determine whether school-level EOC means have sufficient statistical power to detect reasonable effect sizes ($0.05\text{--}0.10$ SD per 5 students), or whether within-school student sorting across sections requires microdata.

---

## 7. Phase 9B: Preregistered Administrative Microdata Protocol

If Phase 9A validates the first-stage scheduling discontinuity, we submit a formal, preregistered microdata request to **Florida DOE**, **Missouri DESE**, or **individual Kansas City metro school districts**.

### The 14-Variable Minimal Relational Specification

To maximize approval probability and respect FERPA privacy boundaries, the request is restricted to the exact 14 variables required for causal identification:

```
========================================================================================================================
#   VARIABLE NAME            TYPE          PURPOSE IN ECONOMETRIC SPECIFICATION
========================================================================================================================
1   student_id_anon          String (Hash) Unique anonymous longitudinal student key for tracking across grades.
2   school_id_nces           String        NCES school identifier for school fixed effects (alpha_s).
3   academic_year            Integer       Academic school year (e.g. 2017 to 2024) for year fixed effects (lambda_t).
4   course_code_state        String        State course code (restricting to Algebra I, Geometry, Biology, English II).
5   section_id               String        Unique classroom section identifier within school-year-course.
6   teacher_id_anon          String (Hash) Anonymous teacher identifier for classroom clustering and teacher FE.
7   student_grade_level      Integer       Enrolled grade level of student (e.g. Grade 9 vs Grade 10).
8   section_enrollment_oct   Integer       Official verified section headcount at the October membership census.
9   course_schedule_type     String        Schedule structure (4x4 block, A/B block, traditional 7-period, minutes/week).
10  eoc_scale_score          Float         Standardized End-of-Course continuous scale score (Primary Dependent Variable).
11  prior_achievement_score  Float         Standardized prior-year MAP (Grade 8) or prior EOC scale score (Lagged Control).
12  student_demographics     Bitflags      Individual binary flags: FRL eligible, IEP/Special Ed, Section 504, EL status,
                                           race/ethnicity categories, and gender (for balance tests and covariate adjustment).
13  enrollment_duration_days Integer       Days enrolled in course section prior to assessment (exposure dose).
14  student_attendance_rate  Float         Course-specific or annual attendance rate during the enrolled academic term.
========================================================================================================================
```

### Why This Request Structure Succeeds
1. **Zero Personally Identifiable Information (PII):** No names, social security numbers, birth dates, or street addresses are requested. All student and teacher keys are irreversibly hashed.
2. **Methodologically Bounded:** Request is explicitly restricted to core state-tested subjects (Algebra I, Geometry, Biology, English II) with mandatory EOC exams.
3. **Preregistered Statistical Code:** The research protocol includes the exact Python/R estimation scripts, leaving zero ambiguity regarding data utilization.

---

## 8. Summary & Next Immediate Actions

1. **Phase 7 (Literature Audit):** Certified. The literature demonstrates that the **25–35 departmentalized secondary margin is an open empirical frontier**.
2. **Phase 8 (Coverage Mapping):** Underway. Parameter space defined across grade level, section size, and instructional load dimensions.
3. **Next Operational Step (Phase 9A):** Launch the Florida and Missouri public feasibility data pull to test the Maimonides-style scheduling discontinuity at $C=25$ and evaluate empirical Gates 1–4.
