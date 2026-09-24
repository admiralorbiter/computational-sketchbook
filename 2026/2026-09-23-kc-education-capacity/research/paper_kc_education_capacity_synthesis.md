# The Capacity Paradox: Why Hiring More Teachers Didn’t Shrink the Classroom
## A Four-Decade Investigation into Institutional Staffing, Bell Schedules, and Effective Teacher Workload Across Metropolitan Kansas City

**Author:** Computational Sketchbook Project  
**Date:** September 2026  
**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Kansas City Metropolitan Area (56 School Districts, 691 Public Campuses)  
**Methodological Decisions:** Decisions 001–033 Adopted  

---

## Abstract

Across the bi-state Kansas City metropolitan area, school districts employ substantially more certified teachers per pupil than they did a decade ago. Between 2014–15 and 2024–25, certified teacher FTE expanded by +8.86% while total student enrollment remained essentially flat (-0.73%), driving regional pupil/teacher ratios down from 14.85:1 to 13.54:1. Yet secondary classroom teachers continue to report classes in the mid-20s and unprecedented workload distress. 

This study resolves this institutional capacity paradox through an exhaustive synthesis of administrative personnel censuses, Civil Rights Data Collection (CRDC) course offerings, district collective bargaining agreements, state accountability regulations, and federal desegregation trial records from *Jenkins v. Missouri*. We show that the paradox is resolved not by administrative data distortion or a secular explosion in classroom headcount, but by a **Four-Layer Explanatory Architecture**:

1. **Institutional Staffing:** Public school districts actively added certified personnel, but headline pupil/teacher ratios measure system-wide staffing rather than classroom group sizes.
2. **Instructional Allocation:** Specialized instructional personnel (special education, reading specialists, interventionists) create a persistent **+2.7 ratio point wedge** between general classroom staffing and building-level ratios. In Kansas, state data confirm that 88.9% of net instructional additions were general classroom teachers, proving that specialist expansion alone cannot explain why core classes remain large.
3. **Teacher Assignment Load:** Under secondary departmentalization, average section sizes are governed by bell-schedule multipliers ($\phi = P_{\text{student}} / P_{\text{teacher}}$). Shifting from a traditional 6-of-7 schedule ($\phi \approx 1.167$) to a contractual 5-of-7 schedule ($\phi = 1.400$) structurally requires **+20.0% teacher FTE just to hold section sizes constant**. In demonstrated cases like Shawnee Mission USD 512, adding +10.4% high school teacher FTE was absorbed by buying protected planning periods rather than shrinking core sections.
4. **Effective Workload:** Available public evidence does not indicate a dramatic increase in secondary roster headcount over the past four decades; modern schedule-based loads (87–147 students/day) fall in a similar or lower range compared to audited KCMSD loads from 1985 (149–154 students/day). Rather, operational complexity per seat has exploded: Section 504 accommodations surged **+93.5% in student volume**, total legally mandated accommodations reached **16.41%**, and chronic absenteeism settled into a persistent post-pandemic plateau at **24.69% (+11.8 percentage points above baseline)**.

Finally, we identify a critical **Public Data Transparency Boundary**: While public agencies publish extensive data on building-level ratios and course averages, public state releases do not expose the primary operational metric that governs secondary teacher workload—individual teacher active roster load—a metric that federal courts audited directly forty years ago.

---

## 1. Introduction: The Wrong Number

In 1985, a federal judge studying Kansas City schools decided pupil/teacher ratio was the wrong number.

Presiding over the landmark desegregation case *Jenkins v. Missouri*, U.S. District Judge Russell G. Clark was confronted with official state reports showing that the Kansas City Missouri School District (KCMSD) operated with an elementary pupil/teacher ratio of 22.14:1 and a high school ratio of 24.8:1. State officials pointed to those ratios as evidence of adequate instructional staffing. 

Judge Clark ordered an independent audit of the district's actual master schedules. The audited trial exhibits (Trial Exhibits K-58 and K-59) revealed a completely different reality:
* At the junior high level, 243 full-time teachers were assigned 37,457 "student-classes" across 1,376 sections. The average class size was **27.22 students**, teachers taught an average of 5.66 periods per day, and the average teacher was responsible for **154.14 students per day**.
* At the senior high level, approximately 352 teachers taught 52,362 student-classes across 1,824 sections. The average class size was **28.71 students**, teachers taught 5.18 periods per day, and the average teacher carried **148.76 students per day** (*Jenkins v. Missouri*, 639 F. Supp. 19, 33–34 (W.D. Mo. 1985)).

The headline pupil/teacher ratio had obscured reality through two mechanisms: it included federally funded Chapter I remedial specialists who taught small pull-out groups, and it treated a secondary teacher seeing six distinct groups of adolescents as mathematically equivalent to a self-contained elementary teacher spending the entire day with a single cohort. 

Recognizing that daily student contact load—not building staffing ratios—was the operative constraint on instructional quality, Judge Clark established a binding remedial ceiling: KCMSD was ordered to staff secondary schools to achieve a maximum of **$\le 125$ students per teacher per day**. Four years later, the Eighth Circuit explicitly affirmed the remedial use of **maximum class sizes rather than district averages** to determine staffing requirements (*Jenkins v. Missouri*, 890 F.2d 65, 68 (8th Cir. 1989)), establishing historical precedent that the upper tail of teacher workload is the policy-relevant constraint.

Forty years later, metropolitan Kansas City finds itself confronting the exact same paradox in reverse. 

Over the past decade, public school districts across the nine-county Kansas City area added thousands of certified teachers, driving headline pupil/teacher ratios down to historic lows of 13:1 to 15:1. Yet when secondary core teachers describe their working conditions, they describe classrooms packed with 24 to 28 students and unprecedented workload distress.

This study was designed to investigate that paradox. Is the teacher workload crisis an illusion driven by selective memory? Are official administrative databases distorted? Did secondary class sizes balloon despite falling ratios? Or are our public metrics still measuring the wrong construct?

---

## 2. The Four-Layer Explanatory Architecture

The empirical findings of this project reject both simplistic explanations: the staffing increase is not an administrative reporting scam, but neither is teacher workload distress an imaginary artifact. 

Instead, the evidence demonstrates that adult instructional capacity is filtered through four distinct, nested organizational layers before reaching the classroom:

```
                            THE FOUR-LAYER WORKLOAD ARCHITECTURE
   ========================================================================================
   LAYER 1: Institutional Staffing (Pupil/Teacher Ratio)
   --> Ratio of total enrolled students to total teacher FTE (CCD / State Personnel Reports).
   --> Explains macro hiring: Regional teacher FTE expanded +8.86% while enrollment was
       essentially flat (-0.73%, from 321,228 to 318,883 across the 56-district metro panel).
   ----------------------------------------------------------------------------------------
   LAYER 2: Instructional Allocation (Classroom vs. Specialized Personnel)
   --> Allocation of teacher FTE between regular general education classrooms and specialist
       roles (Special Education, Title I/ELL reading specialists, interventionists, coaches).
   --> Explains the specialist denominator wedge: ~2.7 ratio points lower than classroom reality.
       88.9% of net instructional-teacher additions across the 19 Kansas USD panel were in
       KSDE's Classroom Teachers category, proving staffing growth was real.
   ----------------------------------------------------------------------------------------
   LAYER 3: Teacher Assignment Load (Sections Taught x Students per Section)
   --> The Jenkins "more revealing figure": Total student-class enrollments / teachers.
   --> Governed by bell-schedule regimes: phi_regime = P_student / P_teacher.
   --> Explains staffing absorption: Shifting from 6-of-7 (phi = 1.17) to 5-of-7 (phi = 1.40)
       structurally requires +20.0% teacher FTE just to hold section sizes constant!
       In demonstrated cases like Shawnee Mission USD 512, staffing additions specifically
       funded the contractual transition to 5-of-7, buying protected planning time rather
       than reducing section size.
   ----------------------------------------------------------------------------------------
   LAYER 4: Effective Workload (Instructional Friction & Complexity Drag)
   --> Effective Workload = sum_j [ n_j * (1 + w_acc * AccShare + w_abs * AbsDrag) ] + Compliance - Prep
   --> The lived constraint: Roster headcounts are flat to lower (122–147), but 16.4% of students
       require legal accommodations and 24.7% are chronically absent, requiring perpetual
       asynchronous re-teaching, individualized documentation, and parent coordination.
   ========================================================================================
```

---

## 3. Layer 1: Institutional Staffing (The Macro Capacity Expansion)

The baseline phase of this research constructed an 11-year longitudinal panel (2014–15 through 2024–25) harmonizing all public elementary, middle, and high schools across the official 9-county Mid-America Regional Council (MARC) region (Jackson, Clay, Platte, Cass, and Ray in Missouri; Johnson, Wyandotte, Leavenworth, and Miami in Kansas).

Across the balanced panel of 56 operating public school districts, the administrative data demonstrate an unambiguous structural expansion in certified staffing:
* **Student Enrollment:** Regional K–12 enrollment was essentially flat, contracting by **-0.73%** (-2,345 students, moving from 321,228 to 318,883).
* **Teacher Staffing:** Certified K–12 teacher FTE expanded by **+8.86%** (+1,783.1 FTE, moving from 20,131.7 to 21,914.8).
* **Pupil/Teacher Ratio:** The regional student-weighted pupil/teacher ratio contracted from **14.85:1 to 13.54:1** (-1.31 students per teacher FTE, an -8.82% reduction). The median regular campus ratio fell from **15.23:1 to 13.53:1**.

To verify whether this expansion was a federal processing artifact or reporting reclassification, Phase 3C audited state-level administrative personnel files directly against the Common Core of Data (CCD). In Missouri, DESE Core Data Screen 18 certified payroll registers corroborated the staffing numbers within 1.5% across benchmark districts. In Kansas, KSDE Certified Personnel reports confirmed an identical expansion. The capacity expansion is real within the administrative data ecosystem: Kansas City public schools employ substantially more certified educators per pupil today than they did a decade ago.

---

## 4. Layer 2: Instructional Allocation (The Specialist Denominator Wedge)

If school systems employ more teachers per pupil, why are classrooms not smaller? The first structural filter is **Instructional Allocation**: how certified FTE is divided between general classroom teachers and specialized support roles.

A school's reported pupil/teacher ratio divides all enrolled students by all certified teachers. But not all certified teachers stand in front of standard classrooms. In a modern comprehensive high school, the certified teacher denominator includes:
* Self-contained and resource-room Special Education (SPED) teachers carrying legal caseloads of 8–15 students;
* Title I and English Language Learner (ELL) interventionists working with small pull-out groups of 3–8 students;
* Instructional coaches, department chairs, and curriculum specialists who carry reduced teaching loads or no classroom rosters at all;
* Low-enrollment specialized electives, such as AP Physics C or upper-level music ensembles.

In Phase 3C, we utilized the Kansas State Department of Education's (KSDE) statutory reporting taxonomy, which uniquely separates certified instructional staff into **Classroom Teachers** (standard general-education teachers) and **Other Teachers** (special education teachers, Title I reading specialists, and certified interventionists).

Analyzing all 19 metropolitan Kansas USDs over the decade revealed the **Specialist Denominator Wedge**:
* Across the 19 Kansas districts, building-level pupil/total teacher ratios contracted from **14.05:1 to 13.60:1**.
* But the ratio of students to regular *Classroom Teachers* was **16.86:1 in 2014–15 and 16.26:1 in 2023–24**.
* Specialized instructional personnel account for a structural denominator wedge of **+2.66 to +2.81 students per teacher**.

Crucially, Kansas data allowed an exact decomposition of decade-long hiring:
* Net student enrollment growth: **+2.5%** (+3,799 students)
* Net Classroom Teacher growth: **+6.2%** (+549.9 FTE)
* Net Specialist Teacher growth: **+3.9%** (+69.1 FTE)
* Net Total Instructional Teacher growth: **+5.8%** (+619.0 FTE)

At the 19-USD aggregate, **88.9% of net instructional additions were general Classroom Teachers**. While the specialist denominator effect is real and accounts for roughly 2.7 ratio points of the baseline gap, specialist hiring did *not* drive the decade-long staffing expansion in Kansas. Districts were hiring general classroom teachers. The puzzle shifted to how those classroom teachers were scheduled.

---

## 5. Layer 3: Teacher Assignment Load (Bell Schedules and Staffing Absorption)

The second structural filter is **Teacher Assignment Load**: the translation of classroom teacher FTE into daily student sections through bell-schedule architecture.

In elementary schools, teachers operate primarily in self-contained classrooms: one teacher instructs the same cohort of students for most of the day. In secondary schools (grades 6–12), instruction is departmentalized: students move between multiple specialized teachers across periods.

Under secondary departmentalization, the mathematical relationship between the classroom staffing ratio and average section size is defined by the **Schedule Capacity Identity**:

$$\overline{\text{Section Size}} \approx \text{PTR}_{\text{class}} \times \left(\frac{P_{\text{student}}}{P_{\text{teacher}}}\right) = \text{PTR}_{\text{class}} \times \phi_{\text{regime}}$$

Where:
* $P_{\text{student}}$ is the number of instructional periods a student attends per day/cycle;
* $P_{\text{teacher}}$ is the number of instructional periods a teacher teaches per day/cycle;
* $\phi_{\text{regime}} = P_{\text{student}} / P_{\text{teacher}}$ is the structural schedule multiplier.

Task 004B.1 compiled a grounded panel of bell schedules, negotiated agreements, and state accountability regulations across 10 representative Kansas City metropolitan districts, identifying three distinct schedule regimes:
1. **Traditional 6-of-7 Schedule ($\phi \approx 1.167$):** Students attend 7 periods; teachers teach 6 periods and receive 1 planning period (e.g., Basehor-Linwood, Richmond, pre-2020 Shawnee Mission). A classroom PTR of 16.0:1 mathematically translates to an average section size of $16.0 \times 1.167 = \mathbf{18.7\text{ students}}$.
2. **Alternating 8-Block Schedule ($\phi \approx 1.333$):** Students take 8 courses across alternating 4-block days (A/B); teachers instruct 6 blocks and receive 2 planning/duty blocks (e.g., North Kansas City 74, Lee's Summit R-VII, Olathe). A classroom PTR of 16.0:1 translates to an average section size of $16.0 \times 1.333 = \mathbf{21.3\text{ students}}$.
3. **Contractual 5-of-7 Schedule ($\phi = 1.400$):** Students attend 7 periods; teachers teach 5 periods and receive 2 non-instructional periods (one individual planning period and one professional learning community/duty period, as mandated by Missouri MSIP 6 prep rules or collective bargaining agreements) (e.g., modern Shawnee Mission, KCPS secondary). A classroom PTR of 16.0:1 translates to an average section size of $16.0 \times 1.400 = \mathbf{22.4\text{ students}}$.

### The Shawnee Mission Quasi-Case Study: The Mechanics of Staffing Absorption
The profound implication of the schedule multiplier is that **moving from a 6-of-7 schedule to a 5-of-7 schedule structurally requires an exact +20.0% increase in teacher FTE just to hold class sizes constant**:

$$\frac{\phi_{\text{5-of-7}}}{\phi_{\text{6-of-7}}} = \frac{1.400}{1.1667} = 1.200 \quad (+20.0\%)$$

In January 2020, following years of teacher advocacy regarding secondary workload, the Shawnee Mission USD 512 Board of Education formally approved a phased transition for high schools from a 6-of-7 teaching schedule to a contractual 5-of-7 schedule, fully implemented by 2021–22.

Task 004B.1 tracked Shawnee Mission's high school staffing, enrollment, and CRDC section sizes across this transition:
* High school enrollment held steady (-1.0%, 8,187 to 8,103 students).
* The district added **+48.8 high school teacher FTE (+10.4%)**, expanding from 471.1 to 519.9 FTE.
* Building-level high school PTR contracted from **17.38:1 down to 15.59:1**.
* Yet Civil Rights Data Collection (CRDC) course reporting confirmed that core mathematics section sizes remained virtually flat: Algebra I averaged 23.8 in 2017–18 and 23.2 in 2023–24; Geometry averaged 24.8 in 2017–18 and 24.6 in 2023–24.

Shawnee Mission provides the demonstrated mechanism case: the district added dozens of high school teachers and drove its staffing ratio down to 15.6:1, yet core classes remained at 23–25 because the added instructional capacity was absorbed by **buying protected teacher planning time**. 

By reducing secondary teaching loads from 6 sections to 5 sections, the district reduced a teacher's total daily student load from **147.0 students/day** ($6 \times 24.5$) down to **122.5 students/day** ($5 \times 24.5$)—bringing secondary teachers under Judge Clark's historical *Jenkins* remedial ceiling of $\le 125$ students per day.

---

### Course-Level Load Asymmetry & The Public Course-Load Boundary (Task 006.1)

While suburban case studies illustrate how schedule reform absorbed staffing additions, a critical empirical question remained: **Does administrative building PTR systematically understate the classroom load represented by core academic gateway courses, and can this be investigated strictly from public records without private Student Information System (SIS) microdata?**

Task 006.1 evaluated this boundary across six selected urban-core high schools (Lincoln College Prep and East High in KCPS; Grandview Senior High; Ruskin High in Hickman Mills; Center Senior High; and Wyandotte High in KCKPS). 

Methodologically, this requires adhering to a strict **Five-Step Reconstruction Ladder**:

```
                          THE FIVE-STEP RECONSTRUCTION LADDER
========================================================================================
[1. OBSERVED]            School-course enrollment and class counts (CRDC: E_c, S_c)
                         --> Objective public empirical fact from federal collection.
----------------------------------------------------------------------------------------
[2. DERIVED]             Course-average class load (s_bar_c = E_c / S_c)
                         --> Exact mathematical average per reported course section.
----------------------------------------------------------------------------------------
[3. MODELED SCENARIOS]   Schedule scenario loads (R_5 = 5 * s_bar_c; R_6 = 6 * s_bar_c)
                         --> Modeled seat burden for a teacher assigned D sections of course c.
----------------------------------------------------------------------------------------
[4. DEPARTMENT LOAD]     Enrollment per teacher (E_math / T_math)
                         --> Average covered student-course enrollments per subject teacher.
----------------------------------------------------------------------------------------
[5. STILL UNOBSERVED]    Individual teacher roster distribution (P(R > 140), section variance)
                         --> Requires student-level SIS microdata or section schedule tables.
========================================================================================
```

The right conclusion is narrower and methodologically rigorous: **We do not need private data to show that building PTR materially understates the load represented by many core courses. But public CRDC aggregates alone still do not reveal the actual roster of an individual teacher.**

When an average section size $\bar{s}_c$ is multiplied by an assumed teaching load ($D = 5$ or $D = 6$), the result is a **derived scenario load**, not an observed teacher roster. We do not know whether any specific teacher teaches five pure core sections, whether their sections average $\bar{s}_c$, or how students are distributed across classes.

Under this calibrated framework, the difference between a modeled scenario load and the naive administrative baseline is decomposed into two arithmetic components:

$$\Delta_{\text{total}} = R_{\text{modeled}} - R_{\text{naive}} = \underbrace{D \cdot (\bar{s}_{\text{dept}} - PTR_{\text{bldg}})}_{\text{Course-vs-PTR Residual}} + \underbrace{D \cdot (\bar{s}_{\text{core}} - \bar{s}_{\text{dept}})}_{\text{Core-vs-Advanced Mix Difference}}$$

Where:
* $R_{\text{naive}} = D \cdot PTR_{\text{bldg}}$ is the baseline load implied by building staffing;
* The **Course-vs-PTR Residual** reflects the mathematical gap between departmental course averages and the building teacher ratio (driven in part by teacher planning periods under $\mu = P/D$ and specialist teachers coded in the teacher denominator who instruct small specialized caseloads rather than full general sections);
* The **Core-vs-Advanced Mix Difference** reflects arithmetic variation within the department: gateway and broadly enrolled foundation courses (e.g., Algebra I, Geometry) concentrate heavy student enrollment, while upper-level electives (e.g., Calculus, Advanced Math) operate with small enrollments (3 to 15 students) that pull down building averages.

#### Table 2: Course-Level Averages & Modeled Scenario Loads for Selected Urban High Schools (SY 2023–24)
| School Campus | District | Schedule Architecture | Building PTR | Alg I Mean | Geom Mean | Core Math Mean | Adv Math Mean | Modeled R5 (5 × Core) | Modeled R6 (6 × Core) | Naive R5 (5 × PTR) | R5 Residual (Δtotal) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lincoln College Prep** | KANSAS CITY 33 | 7-period / hybrid | 17.25:1 | 26.3 | 31.0 | 29.5 | 14.8 | **147.4** | 176.9 | 86.3 | **+61.1** |
| **Grandview Senior High** | GRANDVIEW C-4 | 7-period day | 16.99:1 | 25.8 | 25.9 | 24.0 | 6.8 | **120.1** | 144.2 | 85.0 | **+35.2** |
| **Ruskin High School** | HICKMAN MILLS C-1 | 7-period day | 12.94:1 | 20.2 | 21.8 | 21.0 | 4.2 | **104.8** | 125.7 | 64.7 | **+40.1** |
| **Center Senior High** | CENTER 58 | 7-period day | 12.10:1 | 19.0 | 17.0 | 16.7 | N/A | **83.4** | 100.1 | 60.5 | **+22.9** |
| **East High School** | KANSAS CITY 33 | 7-period / hybrid | 13.85:1 | 19.0 | 12.3 | 17.1 | 10.0 | **85.5** | 102.7 | 69.3 | **+16.3** |
| **Wyandotte High School** | Kansas City USD 500 | 8-period Red/White block | 20.10:1 | 28.5 | 14.3 | 20.2 | 11.8 | **101.0** | **121.1** | 100.5 | **+0.5** |

As illustrated in **Figure 15**, reporting these campuses individually highlights both structural loading patterns and critical counterexamples:

1. **Course-Level Mismatch at Selected Campuses:** At Lincoln Prep, reported Geometry sections average 31.0 and Algebra II sections average 30.6 students. A hypothetical teacher assigned 5 sections at the core mean would carry approximately **147.4 students**—a **+61.1 student residual** over the 86.3 naive PTR expectation, surpassing the 1985 Jenkins ceiling (125 students). Similarly, at Grandview High (core mean 24.0 vs. PTR 17.0) and Ruskin High (core mean 21.0 vs. PTR 12.9), core course averages substantially exceed building staffing ratios.
2. **The Wyandotte Counterexample & Gateway Bottleneck:** Wyandotte High demonstrates that core wedges are **not automatic**. Its aggregate core-math section mean is **20.19**, virtually identical to its building PTR of **20.10** (an aggregate residual of essentially zero, +0.09). However, disaggregating specific courses reveals an acute **gateway bottleneck in Algebra I**: **46 classes enrolling 1,313 students (average 28.54 students/class)**. Under Wyandotte's public 8-period Red/White alternating-block schedule (where full-time teachers typically instruct 6 blocks across the two-day cycle), an Algebra I instructor teaching 6 sections manages a modeled active grading roster of **171.2 students** (+50.6 students above naive 6-period PTR). This demonstrates that allocation wedges exist not merely between "core teachers" and electives, but between specific high-demand gateway courses within the same department.
3. **Staffing Denominator & Policy Guardrails:** The Common Core of Data (CCD) pupil/teacher ratio divides enrollment by full-time equivalent classroom teachers. Guidance counselors are categorized separately and do not depress the teacher denominator; the specialist denominator gap is driven by instructional personnel coded as teachers (e.g. special education resource teachers or Title I interventionists). Furthermore, while Missouri requires 3 math and 3 science credits with EOC exams in Algebra I and Biology, and Kansas requires 3 units incorporating algebraic and geometric concepts, state law does not mandate a universal 9th/10th grade sequence. Gateway courses absorb large volumes because they are foundational requirements, not because of a rigid statutory lockstep.

![Figure 15: Public Course-Load Modeling for Selected Urban Kansas City High Schools](../figures/fig15_urban_core_teacher_load_wedge.png)

---

## 6. Layer 4: Effective Workload (The Headcount vs. Complexity Divergence)

The final structural layer addresses the lived experience of the classroom: **Effective Workload**. 

To determine whether secondary teachers are carrying more students than in previous generations, Task 005C.2 constructed a 40-year cross-era benchmark panel evaluating teacher capacity across four distinct eras, structured strictly into three evidence classes:
* **Class 1: Measured / Court-Reported:** Audited master schedule exhibits K-58/K-59 from *Jenkins v. Missouri* (1985); official published NCES NTPS/SASS survey statistics.
* **Class 2: Court Observation (Not Finding):** Judicial hearing observations from *Jenkins* unitary status hearings (1997).
* **Class 3: Derived Schedule Benchmarks:** Published section means $\times$ contract teaching periods under documented schedule regimes.

> [!IMPORTANT]
> **Comparability Guardrail:** The historical and modern observations synthesized in Table 1 differ in geography, school population, measurement system, and evidentiary status; they establish operational scale and historical continuity, not a single longitudinal estimate.

### Table 1: Cross-Era Capacity Benchmarks (1985–2024)

| Metric / Dimension | Era 1: 1985 Jenkins Remedial Order (Class 1) | Era 2: 1997 Desegregation Review (Class 2) | Era 3: 2017–18 Pre-Pandemic Baseline (Class 1/3) | Era 4: 2023–24 Modern Reality (Class 1/3) | Operational Synthesis Across Eras |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Headline Building PTR** | 22.1:1 (Elem) / 24.8:1 (HS) | 8.6–18.4:1 | 14.5–16.2:1 | 13.5–15.6:1 | **Modern benchmarks generally lower** |
| **Specialist Denominator Wedge** | +4.41 students (Ch. I) | +4.0 to +8.0 students | +2.7 ratio points | +2.7 ratio points | **Structural Institutional Feature** |
| **Secondary Section Size** | 27.2 (Jr) / 28.7 (Sr) | 22–25 (Middle) | 24.0 (Suburban Core) | 24.5 (Suburban Core) | **Similar 20s range** |
| **Secondary Daily Student Load** | 148.8–154.1 std/day | 135–140 std/day | 144.0 std/day (6-of-7) | 122.5 (5-of-7) / 147 (6-of-7) | **Same broad order of magnitude; modern modeled loads overlap or fall below historical KCMSD** |
| **Section 504 Accommodations** | *Not comparable / no equiv.* | *Not comparable / no equiv.* | 2.87% | 4.79% (5–10% in HS) | **Surged +93.5% in Student Volume** |
| **Total Mandated Accommodations** | *Not comparable / no equiv.* | *Not comparable / no equiv.* | 13.50% | 16.41% | **Accelerated Modern Expansion (+2.91 pp)** |
| **Chronic Absenteeism Rate** | *Not comparable / no equiv.* | *Not comparable / no equiv.* | 12.90% | 24.69% | **Persistent Plateau (+11.8 pp above baseline)** |

### The Historical Headcount Continuity
Table 1 demonstrates a foundational empirical result: **available public evidence does not indicate a dramatic increase in secondary roster headcount over the past four decades**.

In 1985, audited master schedules proved that KCMSD secondary teachers were carrying **149 to 154 students per day** across sections averaging 27 to 29 students. In 1997, Judge Clark observed that middle school teachers routinely taught six periods of 22–25 students (**135–140 students/day**). In 2024, derived schedule contact loads in modern suburban high schools range from **122.5 students/day** (under 5-of-7 schedules) to **147.0 students/day** (under 6-of-7 schedules). In official NCES surveys, statewide departmentalized averages in Kansas (17.4) and Missouri (19.2) produce derived 6-period loads of **104.4 and 115.2 students/day**.

The simple narrative that teachers are overwhelmed today because class sizes or student headcounts have exploded is difficult to reconcile with historical public evidence.

### The Modern Complexity Surge
If secondary teachers are carrying similar or fewer total students than their predecessors, why is operational distress at an all-time high? 

The answer lies in the **Compound Workload Framework**: while raw student volume has remained stable, the operational friction per student seat has escalated dramatically.

Task 004C.1 harmonized CRDC school-level complexity tables and EDFacts FS195 attendance files across 3,744 school-years (2015–16 through 2023–24). The data document an unprecedented surge in student support requirements within the modern era where standardized federal reporting exists:
1. **The Section 504 Accommodation Surge:** Between 2015–16 and 2023–24, the number of students receiving formal accommodation plans under Section 504 of the Rehabilitation Act expanded from 6,552 to 12,676 across the metro—a **+93.5% increase in student volume**. In large comprehensive suburban high schools (e.g., Blue Valley North, Shawnee Mission East, Lee's Summit West), Section 504 accommodation shares regularly exceed **5% to 10% of total enrollment**. Unlike specialized pull-out programs, Section 504 plans are executed almost entirely by general classroom teachers, requiring differentiated testing environments, modified assignments, behavioral accommodations, and extensive legal compliance logging.
2. **Total Legally Mandated Accommodations:** Combining federal IDEA Special Education (12.46% of regional enrollment) and Section 504 (3.95%), **16.41% of all students** across metropolitan Kansas City now carry legally binding individualized instructional accommodations. In a standard secondary section of 25 students, a teacher is legally responsible for executing individualized modifications for 4 to 6 students in every period.
3. **The Chronic Absenteeism Plateau:** Prior to the pandemic, regional chronic absenteeism (defined as missing $\ge 10\%$ of school days) stood at **12.90%**. During the 2020–21 pandemic disruption, chronic absenteeism spiked to **35.14%**. Rather than receding to pre-pandemic baselines, absenteeism settled into a persistent post-pandemic plateau at **24.68% in 2021–22, 24.69% in 2022–23, and 24.7% in 2023–24**—an increase of **+11.8 percentage points above baseline**. 

While average daily attendance remains around 90–92%, chronic absenteeism means that on any given day, 2 to 4 students are absent from each classroom, only to return on subsequent days requiring individual remediation. A teacher managing 125 to 147 students across a cycle is now managing perpetual asynchronous re-teaching, continuous digital gradebook maintenance, makeup testing, and parent coordination for 30 to 35 chronically absent students.

**The Qualitative Paradox Resolution:**
> *The number of students on a secondary teacher's roster did not explode. The number of individualized instructional problems, legal compliance accommodations, and asynchronous re-teaching burdens a teacher must solve for those students did.*

---

## 7. The Public Data Transparency Boundary

A central contribution of this investigation is documenting precisely **where public administrative data end and where restricted microdata begin**.

```
                       THE PUBLIC DATA TRANSPARENCY BOUNDARY
========================================================================================
LEVEL 1: Institutional Staffing  --> CCD / State Personnel Reports
                                     (FTE, Enrollment, Building Pupil/Teacher Ratio)
                                     STATUS: FULLY PUBLIC & AUDITED (Phases 1–3C)
----------------------------------------------------------------------------------------
LEVEL 2: Instructional Allocation --> State Role Codes / Special Education Densities
                                     (Classroom vs. Specialist Teachers, SPED FTE)
                                     STATUS: FULLY PUBLIC & RECONCILED (Task 003C)
----------------------------------------------------------------------------------------
LEVEL 3: Course-Level Capacity   --> CRDC Course Catalogs / NTPS State Tables
                                     (Average class size in Algebra II, Chemistry, etc.)
                                     STATUS: FULLY PUBLIC & AUDITED (Task 004A.1)
----------------------------------------------------------------------------------------
LEVEL 4: Teacher Roster Load     --> Sum of sections for individual teachers
                                     (R_i = sum_j n_{ij}, percentile tails, distribution)
                                     STATUS: RESTRICTED-USE / CUSTOM DATALAB ONLY
                                     NOT AVAILABLE IN PUBLIC AGGREGATE TABLES
========================================================================================
```

Public administrative records allow researchers and citizens to establish system-level staffing (+8.86% teacher FTE against -0.73% enrollment), specialist allocations (+2.7 ratio point wedge), regional course averages (high teens) alongside mid-20s averages at selected comprehensive suburban campuses, bell-schedule regimes (5-of-7 vs. 6-of-7), Section 504 growth (+93.5%), and chronic absenteeism (24.7%).

What public data **cannot** reveal today is the empirical distribution of individual teacher active roster loads or the precise percentage of teachers carrying $>140$ students. While the federal National Teacher and Principal Survey (NTPS) collects section-by-section counts from teachers (questionnaire items T0260–T0269), public NCES tables publish only average section size $\bar{n}$, not the joint distribution of total student assignments $E[\sum_j n_{ij}]$. Calculating actual roster percentiles requires custom DataLab extraction or restricted-use microdata licenses.

Herein lies the institutional irony: **Forty years ago, a federal court was able to inspect audited master schedules and calculate the exact daily roster load of every secondary teacher in Kansas City. Today, in an era of massive digital state databases, public state releases do not expose the primary metric that governs secondary teacher workload.**

Policymakers and school boards debate building-level pupil/teacher ratios that obscure classroom reality, while the actual administrative data systems published by states fail to report teacher active roster load.

---

## 8. Conclusion: Reframing Adult Instructional Capacity

When this project began, the central hypothesis was that physical classroom size had ballooned and that headline staffing ratios were hiding massive classrooms. 

The empirical evidence points toward a more profound conclusion: **Adult instructional capacity is the root construct, but building-level class size is an incomplete measure of it.**

The findings of this study converge on five grounded principles:
1. **Pupil/Teacher Ratio is Not Classroom Size:** Ratios measure institutional employment, not student exposure. Conflating the two distorts public policy and misleads community stakeholders.
2. **Staffing Additions Bought Planning Time:** In demonstrated cases like Shawnee Mission, staffing growth was real and absorbed by reducing daily teaching periods (buying protected planning time) rather than shrinking class headcounts. This succeeded in reducing daily contact loads below historical crisis levels (from 147 to 122.5 students/day).
3. **The Problem is Compound Instructional Friction:** Managing 125 students in 2024 is fundamentally more demanding than managing 125 students in 1985. The explosive growth of formal accommodations, legal compliance logging, and chronic absenteeism has dramatically increased the non-instructional drag on every teaching minute.
4. **Tail Protection Matters More Than Averages:** As the Eighth Circuit affirmed in 1989, averages conceal the overloaded tail. A contractual schedule change that caps teaching loads at 5 periods protects teachers from catastrophic 150+ student rosters even if the campus average class size remains 24.
5. **Close the Public Transparency Gap:** Educational governance cannot manage what it does not publish. State departments of education in Missouri and Kansas already collect section assignment data; releasing de-identified teacher roster load distributions is the single most important transparency reform needed to align education policy with the lived realities of the classroom.

Forty years after Judge Russell G. Clark looked past pupil/teacher ratios to count student-classes and daily teaching assignments, his insight remains the definitive guide: if we want to understand the capacity of our schools, we must measure the actual work assigned to the teacher.

---

### Key Project Artifacts & Repository Ledgers
- **Historical Analysis:** `outputs/tables/task005a_jenkins_historical_capacity_report.md` & `outputs/figures/fig13_jenkins_capacity_framework.png`
- **NTPS Survey Audit:** `outputs/tables/task005b2_ntps_roster_load_audit_report.md`, `task005b2_ntps_published_benchmarks.csv` & `task005b2_ntps_schedule_derived_benchmarks.csv`
- **Cross-Era Synthesis:** `outputs/tables/task005c_historical_roster_load_synthesis_report.md` & `outputs/figures/fig14_historical_roster_load_synthesis.png`
- **Schedule Decomposition:** `outputs/tables/task004b_schedule_capacity_report.md` & `outputs/figures/fig11_schedule_capacity_decomposition.png`
- **Student Complexity Panel:** `outputs/tables/task004c_complexity_analysis_report.md` & `outputs/figures/fig12_student_complexity_trends.png`
- **Urban Roster Reconstruction Pilot:** `outputs/tables/task006_urban_roster_reconstruction_report.md`, `task006_urban_roster_reconstruction.csv` & `outputs/figures/fig15_urban_core_teacher_load_wedge.png`
- **CRDC Course Capacity Audit:** `outputs/tables/task004a1_crdc_estimand_audit.md` & `outputs/tables/task004a1_crdc_sensitivity_analysis.csv`
- **Governance & Decisions:** `research/decisions.md` (Decisions 001–033) & `research/hypotheses.md` (H1–H4)
