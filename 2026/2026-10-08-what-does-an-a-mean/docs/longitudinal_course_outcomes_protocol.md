# Longitudinal Course Outcomes & Policy Transition Protocol
**Kansas City Public Schools (KCPS) & Secondary Institutional Case Studies**
*Computational Sketchbook Research Series (`2026-10-08-what-does-an-a-mean`)*

---

## 1. Research Objective & Central Hypothesis

This protocol establishes the empirical framework for analyzing the effects of secondary grading policy reforms on:
1. **Recorded academic performance**: Term-level letter grades (A–F), course failure rates (% F), and credit completion rates.
2. **Actual student learning**: Performance on state End-of-Course (EOC) standardized assessments (Algebra I and Biology).
3. **Signaling fidelity & institutional decoupling**: Whether reductions in course failure rates and increases in credit acquisition reflect true improvements in academic proficiency or administrative artifacts of grading floor policies.

### Central Empirical Question
> *When an urban school district institutes an artificial grading floor (e.g., establishing a 40% minimum score for attempted work) and subsequently revises missing-work penalties and track exemptions, does the resulting improvement in course pass rates signal real academic learning, or does it decouple course credit accumulation from verified mastery?*

---

## 2. Policy Chronology & Empirical Regimes (KCPS Case Study A)

The Kansas City Public Schools (KCPS) policy sequence provides a natural quasi-experimental progression across four consecutive academic years:

| Academic Year | Policy Era | Institutional Rule Description | General Education Track | Honors / AP / IB / MYP Track |
| :--- | :--- | :--- | :--- | :--- |
| **2021–2022** | Pre-Reform Baseline | Board Policy IKA (Traditional 0–100%). Zeroes awarded for missing work; no minimum floor (F = 0–59%). | Traditional (0% floor, zeroes for missing) | Traditional (0% floor, zeroes for missing) |
| **2022–2023** | Pre-Reform Baseline Trend | Continuation of Policy IKA. Identical grading scales and failure ranges. | Traditional (0% floor, zeroes for missing) | Traditional (0% floor, zeroes for missing) |
| **2023–2024** | Initial 40% Floor Rollout | Administrative adoption of 40% floor across secondary schools. As reported by KCUR (Fortino 2024), missing assignments in practice frequently received 40% rather than 0%. | 40% Floor Applied (Attempted & Missing) | 40% Floor Applied (Attempted & Missing) |
| **2024–2025** | Revised Missing-Work & Exemption | Official Secondary Grading Policy Manual (August 2024). Establishes 3-tier category weighting (10% Engagement, 40% Progress, 50% Proficiency). Missing work strictly receives 0%. Attempted work floor remains 40%. **Advanced courses (Honors, AP, IB, MYP) explicitly EXEMPTED (retaining 0–59% F scale).** | 40% Attempted Floor; 0% Missing; 10/40/50 Weights | **EXEMPT**: 0% Floor (0–59% F retained); 10/40/50 Weights |

---

## 3. Data Dictionary: `kcps_longitudinal_course_outcomes.csv`

The harmonized dataset (`data/processed/kcps_longitudinal_course_outcomes.csv`) contains 384 term-level course observations across 6 KCPS secondary campuses:
- **Campuses**: Central High School, East High School, Lincoln College Preparatory Academy, Northeast High School, Southeast High School, Paseo Academy of Children's & Performing Arts.
- **Academic Years**: 2021–2022, 2022–2023, 2023–2024, 2024–2025.
- **Terms**: Fall (Semester 1), Spring (Semester 2).
- **Core Subjects**: Algebra I (MATH101), Geometry (MATH201), English I (ENG101), Biology (SCI101).
- **Tracks**: General Education, Honors / AP / IB.

### Variable Definitions

| Variable Name | Data Type | Description & Verification Standard |
| :--- | :--- | :--- |
| `district_code` | string | Missouri DESE 6-digit district identifier (`048-078` for KCPS). |
| `district_name` | string | Official district name (`Kansas City 33`). |
| `school_name` | string | Building name matching Missouri DESE APR Directory. |
| `academic_year` | string | Academic school year (`YYYY-YYYY`). |
| `policy_era` | string | Analytical regime (`Pre-Reform`, `Initial 40% Floor`, `Revised Missing-Work & Exemption`). |
| `term` | string | Academic semester (`Fall`, `Spring`). |
| `course_code` | string | Department course identifier (`MATH101`, `MATH201`, `ENG101`, `SCI101`). |
| `course_title` | string | Course name. |
| `course_track` | string | Curricular track (`General Education`, `Honors / AP / IB`). |
| `students_enrolled` | integer | Total student count completing the term course section. |
| `count_A`–`count_F` | integer | Absolute count of final semester grades awarded in each letter tier. |
| `pct_A`–`pct_F` | float | Percentage of enrolled students receiving each letter grade (sum to 100%). |
| `failure_rate_pct` | float | Primary outcome metric: percentage of students receiving an 'F' (`count_F / students_enrolled * 100`). |
| `credits_attempted` | float | Total Carnegie units attempted (0.5 credit per semester course per student). |
| `credits_earned` | float | Total Carnegie units awarded for passing marks (A, B, C, D). |
| `credit_completion_pct` | float | Ratio of credits earned to credits attempted (`credits_earned / credits_attempted * 100`). |
| `eoc_proficient_or_advanced_pct`| float | Percentage of students scoring Proficient or Advanced on state EOC assessment (Spring term). |
| `eoc_below_basic_pct` | float | Percentage of students scoring Below Basic on state EOC assessment. |
| `policy_exposure_role` | string | Dynamic classification from evidence register (e.g. `Case_A_General_Track_Floor_2024_25`). |
| `grading_model` | string | Institutional grading structure (`TRADITIONAL_PCT`, `STANDARDS_BASED_SBL`). |
| `attempted_work_floor` | string | Minimum allowable score for attempted student work (`0_NO_FLOOR`, `40_PCT_MINIMUM`). |
| `missing_work_rule` | string | Formal penalty for unsubmitted work (`TRUE_ZERO_ALLOWED`, `FLOOR_40_UNSUBMITTED`). |
| `reassessment_rule` | string | Retake policy (`TEACHER_DISCRETION`, `UNIVERSAL_MANDATORY`, `NOT_YET_VERIFIED`). |
| `engagement_weight_pct` | float | Formal category weight for attendance/participation (10.0% in 24–25). |
| `progress_weight_pct` | float | Formal category weight for quizzes/formative progress (40.0% in 24–25). |
| `proficiency_weight_pct` | float | Formal category weight for summative assessments (50.0% in 24–25). |
| `audit_status` | string | Evidence classification from evidence register (`PRIMARY_POLICY_DOCUMENT`, etc.). |

---

## 4. Empirical Methodology & Econometric Framework

### A. Within-School Difference-in-Differences (DiD)
The August 2024 policy revision creates an ideal within-school identification strategy. Because Honors, AP, IB, and MYP courses were explicitly exempted from the 40% grading floor while General Education courses remained subject to it:
$$\text{Outcome}_{ist} = \alpha_s + \lambda_t + \beta_1 (\text{GeneralTrack}_i \times \text{PostFloor}_{t}) + \beta_2 (\text{GeneralTrack}_i \times \text{PostRevision}_t) + \mathbf{X}'_{st}\boldsymbol{\gamma} + \varepsilon_{ist}$$
Where:
- $\alpha_s$ are school fixed effects (absorbing constant campus differences like Lincoln's magnet selectivity vs Central's neighborhood intake).
- $\lambda_t$ are semester-year fixed effects.
- $\beta_1$ estimates the initial effect of introducing the 40% floor in 2023–24.
- $\beta_2$ estimates the subsequent adjustment when missing-work zeroes were restored and the honors exemption formalized in 2024–25.

### B. Empirical Decoupling Test
To distinguish genuine learning gains from artificial measurement compression, we estimate the relationship between course pass rates ($\text{PassRate} = 100 - \text{FailureRate}$) and standardized EOC proficiency:
$$\Delta \text{Decoupling Gap}_{st} = \Delta \text{CoursePassRate}_{st} - \Delta \text{EOCProficiencyRate}_{st}$$
Under the null hypothesis that grading floor policies promote real learning by maintaining student motivation and engagement, $\Delta \text{Decoupling Gap} \approx 0$ (both metrics rise in tandem). Under the Goodhart-Campbell hypothesis, $\Delta \text{Decoupling Gap} > 0$ (course passing surges while EOC proficiency remains flat or declines).

---

## 5. North Kansas City SBL Extension (Case Study B)

For Phase 3 expansion, North Kansas City High's Standards-Based Learning (SBL) pilot (scheduled for Fall 2025) will be incorporated as Case Study B:
1. **Pilot designated courses**: English I, Algebra I, Biology at North Kansas City High School.
2. **Within-district non-pilot controls**: Identical courses at Oak Park High, Staley High, and Winnetonka High (operating under traditional 0–100% percentage grading until full rollout in 2026–27).
3. **Key outcome difference**: In SBL, grades communicate demonstrated mastery on specific learning standards rather than accumulated mathematical points or attendance. The research question is whether SBL grade distributions demonstrate higher concordance with state EOC performance than traditional point-based grading systems.
