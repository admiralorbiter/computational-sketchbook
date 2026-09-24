# Task 003B — Longitudinal Structural Capacity Analysis Report
**Kansas City Metropolitan Education Capacity Study (2014–15 through 2024–25)**  
**Date of Audit & Analysis:** September 24, 2026 (Task 003B.1 Report-Integrity Pass)  
**Pipeline Script:** `src/analysis/longitudinal_capacity_analysis.py`  
**Data Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area across 11 School Years  
**Primary Panels Analyzed:**
- School Panel (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 school-years, 730 unique schools)
- LEA Panel (`kc_lea_capacity_long_2014_15_2024_25.csv`, 881 LEA-years, 77 fully regional LEAs per year)
- Balanced Panel Sensitivity (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 rows across 620 continuously operating schools)

---

## Executive Summary & Core Headline Finding

Over the 10-year interval from 2014–15 to 2024–25, **structural staffing capacity expanded significantly** across the Kansas City metropolitan region:

1. **Regional LEA Pupil/Teacher Ratio (K–12):** Fell from **14.85 to 13.54 students per teacher FTE** ($-1.31$ students per FTE, a **$-8.82\%$** structural reduction).
2. **Typical School-Level Staffing Ratio (Regular Operating Schools):** Median ratio fell from **15.23 to 13.53 students per teacher FTE** ($-1.70$ students per FTE, a **$-11.16\%$** reduction; IQR contracted from $[13.84, 16.63]$ down to $[12.14, 14.93]$).
3. **Driver Decomposition:** Regional K–12 student enrollment was **virtually flat** over the decade (321,228 in 2014–15 vs. 318,883 in 2024–25, changing less than 1%: $-2,345$ students, or $-0.73\%$). Meanwhile, reported regional K–12 teacher FTE rose by nearly 9% (**$+1,921.91\text{ FTE}$**, or **$+8.88\%$**), rising from 21,633.26 to 23,555.17 FTE. Paraprofessionals expanded even faster ($+11.85\%$, adding $+565.91\text{ FTE}$).
4. **Conclusion on Capacity:** The regional decline in structural pupil/teacher staffing ratios is **not** an artifact of student enrollment collapse. Rather, it is overwhelmingly driven by **net expansion of employed professional instructional staff**.
5. **Within-School Robustness:** The trend changes very little when analysis is restricted to continuously operating schools, suggesting that school openings, closures, and other compositional turnover are not the primary explanation for the observed decline in staffing ratios. School fixed-effects regressions on the 620-school balanced panel confirm a within-school trajectory of $\beta = -0.1750\text{ students/FTE per year}$ ($p < 0.0001$; implied 10-year within-school decline of $−1.75$ students per FTE).

> [!IMPORTANT]
> **Core Methodological Boundary**: These findings measure **macro structural staffing capacity** (the aggregate ratio of students to employed professional FTE). They do **NOT** measure observable classroom section sizes and do **NOT** adjudicate Hypotheses H1a, H1b, H2, or H3.


---

## 1. Research Question and Methodological Boundaries

### Core Research Question
*How has structural staffing capacity changed across the Kansas City metropolitan region over the past decade (2014–15 to 2024–25)?*

### Methodological Guardrails & Boundary Rules
1. **Structural Capacity vs. Classroom Section Size:**
   - Common Core of Data (CCD) pupil/teacher ratios divide total student headcount by total full-time equivalent (FTE) classroom teachers reported by administrative units.
   - Pupil/teacher staffing ratios are **never described as class sizes**. Staffing ratios obscure class size whenever teachers are assigned to non-rostered instructional roles or whenever daily schedules distribute students across fewer active classroom periods.
2. **No Hypothesis Testing:**
   - Task 003B/003B.1 does **not** declare support or rejection for Hypotheses H1a, H1b, H2, or H3.
   - H1a (ratios obscure section sizes) and H1b (actual section sizes increased) require student course roster and schedule data that CCD cannot provide.
   - H2 (student complexity escalation) requires longitudinal IEP, ELL, and chronic absenteeism microdata.
   - H3 (instructional role specialization) requires detailed course and program assignment classifications beyond broad CCD teacher FTE categories.
   - H4 (joint interaction of size and complexity) remains completely unresolved.
3. **Non-Causal Estimations:**
   - Observed changes, percentage decompositions, and fixed-effects coefficients describe factual historical trajectories. No causal claims are made regarding policy interventions, tax levies, or pandemic impacts.


---

## 2. Coverage and Missing-Data Rules

### Standardized Reporting Coverage Quality Tiers
Reporting coverage is audited across entity counts and student enrollment prior to calculating any aggregate:
- **`complete`** ($100\%$ enrollment coverage)
- **`high_coverage`** ($95.0\%\text{--}99.9\%$)
- **`partial_coverage`** ($80.0\%\text{--}94.9\%$)
- **`insufficient_coverage`** ($< 80.0\%$)

### Treatment of 2015–16 Federal Suppression
- In the 2015–16 NCES CCD LEA staff release, two major Kansas districts—**Olathe School District (2010140)** (28,567 K–12 students) and **Gardner Edgerton (2006420)** (5,611 K–12 students)—had their entire staff data withheld/suppressed (`-9.0`).
- **Zero Imputation:** In accordance with Decision 022, suppressed values remain `NaN`. No imputation or interpolation is permitted.
- **Reporting Tiers Enforced:**
  - Kansas LEA 2015–16 valid enrollment coverage is **$75.92\%$** (`insufficient_coverage`). Kansas 2015–16 is **excluded from primary temporal trend regressions and slope fits**. On reporting Kansas LEAs (20 districts), the calculated ratio is 15.03.
  - Metro LEA 2015–16 enrollment coverage is **$89.45\%$** (`partial_coverage`). Metro 2015–16 is **excluded from primary temporal slope fits** and presented descriptively with explicit data warnings.
  - Missouri LEA 2015–16 enrollment coverage is **$100.0\%$** (`complete`, 56 valid LEAs, 181,900 students, ratio 14.80) and enters trend fits normally.
- In all visualizations, 2015–16 data points are plotted with hollow markers and dashed bridge lines to make data limitations visually obvious.


---

## 3. Region-Wide Structural Staffing Trajectory

Primary regional staffing estimands are reported under two distinct statistical perspectives:
1. **Student-Weighted Structural Staffing Ratio:** $\frac{\sum \text{Enrollment}}{\sum \text{Teacher FTE}}$. Answers: *What did the regional student population experience structurally?*
2. **Typical-School Distribution:** Median, 25th percentile, 75th percentile (IQR), 10th percentile, and 90th percentile across individual schools. Answers: *What did the typical school campus look like?*

### Table 1: Regional Staffing Trajectory Across 11 School Years (2014–15 to 2024–25)
*Source: `outputs/tables/task003b_regional_trends.csv`*

| School Year | Coverage Tier | Reg. LEA K–12 Enrollment | Reg. LEA Teacher FTE | Student-Weighted LEA PTR | Typical LEA Median PTR | School Regular Enrollment | School Classroom Teacher FTE | Student-Weighted School PTR | Typical School Median PTR [IQR] | 10th–90th Percentile Range |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014–2015** | Complete | 321,228 | 21,633.26 | **14.85** | 14.06 | 326,021 | 21,191.15 | **15.38** | 15.23 [13.84, 16.63] | [11.73, 17.82] |
| **2015–2016** | partial_coverage (89.5%)\* | 289,666\* | 19,458.42\* | **14.89**\* | 14.26\* | 294,128\* | 19,316.49\* | **15.23**\* | 15.07 [13.70, 16.45]\* | [11.90, 17.73]\* |
| **2016–2017** | Complete | 325,274 | 22,065.54 | **14.74** | 13.92 | 329,875 | 21,641.83 | **15.24** | 14.93 [13.40, 16.44] | [11.94, 17.77] |
| **2017–2018** | Complete | 327,585 | 22,670.66 | **14.45** | 13.85 | 332,234 | 22,115.58 | **15.02** | 14.70 [13.24, 16.12] | [11.75, 17.42] |
| **2018–2019** | Complete | 328,578 | 22,828.39 | **14.39** | 13.77 | 330,157 | 22,140.55 | **14.91** | 14.62 [13.00, 16.17] | [11.55, 17.21] |
| **2019–2020** | Complete | 329,357 | 23,136.48 | **14.24** | 13.70 | 332,190 | 22,342.11 | **14.87** | 14.53 [13.05, 15.97] | [11.75, 17.26] |
| **2020–2021** | Complete | 321,732 | 23,310.69 | **13.80** | 13.18 | 323,656 | 22,293.20 | **14.52** | 14.04 [12.11, 15.69] | [10.93, 17.24] |
| **2021–2022** | Complete | 320,149 | 23,508.76 | **13.62** | 12.86 | 323,047 | 22,659.59 | **14.26** | 13.78 [12.28, 15.36] | [10.60, 16.69] |
| **2022–2023** | Complete | 321,595 | 23,886.08 | **13.46** | 12.79 | 326,348 | 22,950.10 | **14.22** | 13.63 [12.26, 15.11] | [10.73, 16.44] |
| **2023–2024** | Complete | 319,559 | 23,620.08 | **13.53** | 12.92 | 324,324 | 22,942.12 | **14.14** | 13.64 [12.16, 15.10] | [10.68, 16.48] |
| **2024–2025** | Complete | 318,883 | 23,555.17 | **13.54** | 12.73 | 323,188 | 23,178.23 | **13.94** | 13.53 [12.14, 14.93] | [10.62, 16.13] |
| **10-Year Change** | — | **-2,345** | **+1,921.91** | **-1.31** | **-1.33** | **-2,833** | **+1,987.08** | **-1.44** | **-1.70** | **[-1.11, -1.69]** |
| **% Change** | — | **-0.73%** | **+8.88%** | **-8.82%** | **-9.46%** | **-0.87%** | **+9.38%** | **-9.36%** | **-11.16%** | — |

*\*Note: 2015–16 figures reflect reporting entities only due to federal suppression in Olathe and Gardner Edgerton; excluded from primary trend estimation.*

See Figure 1 (`outputs/figures/regional_teacher_capacity_trend.png`) and Figure 7 (`outputs/figures/school_ratio_distribution.png`).


---

## 4. Enrollment vs. Staffing Decomposition

To establish whether ratio changes reflect shrinking student bodies or expanding instructional staff, we decompose endpoint and subperiod shifts into accounting components.

### Table 2: Non-Causal Accounting Decomposition Across Subperiods
*Source: `outputs/tables/task003b_endpoint_decomposition.csv`*

| Analytical Dimension | Period | Start Year | End Year | Enrollment Change (%) | Teacher FTE Change (%) | Ratio Change (Pts) | Primary Accounting Driver |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Metro_LEA_K12 | Full_Decade_2014_to_2024 | 2014-2015 | 2024-2025 | -0.73% | +8.88% | -1.31 | Staffing Expansion |
| Metro_LEA_K12 | Pre_Pandemic_2014_to_2019 | 2014-2015 | 2019-2020 | +2.53% | +6.95% | -0.61 | Staffing Expansion |
| Metro_LEA_K12 | Pandemic_Shock_2019_to_2020 | 2019-2020 | 2020-2021 | -2.32% | +0.75% | -0.43 | Enrollment Contraction |
| Metro_LEA_K12 | Post_Pandemic_2020_to_2024 | 2020-2021 | 2024-2025 | -0.89% | +1.05% | -0.26 | Joint Staffing Expansion & Enrollment Contraction |
| Metro_School_Regular | Full_Decade_2014_to_2024 | 2014-2015 | 2024-2025 | -0.87% | +9.38% | -1.44 | Staffing Expansion |
| Metro_School_Regular | Pre_Pandemic_2014_to_2019 | 2014-2015 | 2019-2020 | +1.89% | +5.43% | -0.52 | Staffing Expansion |
| Metro_School_Regular | Pandemic_Shock_2019_to_2020 | 2019-2020 | 2020-2021 | -2.57% | -0.22% | -0.35 | Enrollment Contraction |
| Metro_School_Regular | Post_Pandemic_2020_to_2024 | 2020-2021 | 2024-2025 | -0.14% | +3.97% | -0.57 | Staffing Expansion |

### Findings from Decomposition
1. **Pre-Pandemic Period (2014–15 to 2019–20):** Regional enrollment grew by $+8,129$ students ($+2.53\%$), yet teacher FTE grew even faster by $+1,503.22$ FTE ($+6.95\%$), lowering the staffing ratio by $−0.61$.
2. **Pandemic Shock (2019–20 to 2020–21):** Student enrollment dropped abruptly by $−7,625$ ($−2.32\%$), while staffing remained resilient ($+174.21$ LEA teacher FTE, $+0.75\%$), driving a ratio drop of $−0.43$.
3. **Post-Pandemic Period (2020–21 to 2024–25):** Enrollment plateaued (down $−2,849$), while schools added another $+885.03$ classroom teacher FTE ($+3.97\%$).
4. **Summary Fact:** Regional K–12 enrollment was essentially flat over the full decade (changed by less than 1%, $-0.73\%$, $-2,345$ students), while teacher FTE expanded by nearly 9% ($+8.88\%$, $+1,921.91$ FTE). (See Figure 5: `outputs/figures/capacity_change_decomposition.png`).


---

## 5. Missouri vs. Kansas Comparison

Both sides of the state line experienced substantial structural staffing expansions, with striking parity in both starting levels and ultimate outcomes.

### Table 3: State-Level Trajectory Comparison (Regional LEAs)
*Source: `outputs/tables/task003b_state_trends.csv`*

| School Year | MO K–12 Enrollment | MO Teacher FTE | MO Weighted PTR | MO Typical Median PTR | KS K–12 Enrollment | KS Teacher FTE | KS Weighted PTR | KS Typical Median PTR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014–2015** | 180,423 | 12,171.86 | **14.82** | 13.90 | 140,805 | 9,461.40 | **14.88** | 14.66 |
| **2015–2016** | 181,900 | 12,290.42 | **14.80** | 13.73 | 107,766\* | 7,168.00\* | **15.03**\* | 14.51\* |
| **2016–2017** | 183,086 | 12,441.24 | **14.72** | 13.60 | 142,188 | 9,624.30 | **14.77** | 14.43 |
| **2017–2018** | 183,816 | 12,706.28 | **14.47** | 13.58 | 143,769 | 9,964.38 | **14.43** | 14.24 |
| **2018–2019** | 184,491 | 12,775.61 | **14.44** | 13.15 | 144,087 | 10,052.78 | **14.33** | 14.14 |
| **2019–2020** | 184,382 | 12,899.81 | **14.29** | 13.54 | 144,975 | 10,236.67 | **14.16** | 14.00 |
| **2020–2021** | 180,743 | 13,003.52 | **13.90** | 13.16 | 140,989 | 10,307.17 | **13.68** | 13.58 |
| **2021–2022** | 179,330 | 12,990.01 | **13.81** | 12.82 | 140,819 | 10,518.75 | **13.39** | 13.62 |
| **2022–2023** | 180,389 | 13,296.40 | **13.57** | 12.59 | 141,206 | 10,589.68 | **13.33** | 13.22 |
| **2023–2024** | 180,015 | 13,322.38 | **13.51** | 12.66 | 139,544 | 10,297.70 | **13.55** | 13.42 |
| **2024–2025** | 179,402 | 13,350.66 | **13.44** | 12.34 | 139,481 | 10,204.51 | **13.67** | 13.40 |
| **10-Year Change** | **-1,021** | **+1,178.80** | **-1.38** | **-1.56** | **-1,324** | **+743.11** | **-1.21** | **-1.26** |
| **% Change** | **-0.57%** | **+9.68%** | **-9.31%** | **-11.22%** | **-0.94%** | **+7.85%** | **-8.13%** | **-8.59%** |

*\*Note: KS 2015–16 is insufficient coverage due to federal suppression of Olathe and Gardner Edgerton.*

### State Comparison Insights
1. **Level Alignment:** Both states began in 2014–15 with nearly identical student-weighted structural ratios: Missouri at **14.82** and Kansas at **14.88**.
2. **Ending Concordance:** By 2024–25, Missouri reached **13.44** and Kansas reached **13.67**.
3. **Staffing Growth:** Missouri added $+1,178.80\text{ FTE}$ ($+9.68\%$) while Kansas added $+743.11\text{ FTE}$ ($+7.85\%$). Both states experienced flat enrollment (MO: $−0.57\%$; KS: $−0.94\%$).
4. **Trajectory Parallelism:** Linear slope fits across complete reporting years are virtually identical: Missouri at **$-0.1581\text{ students/FTE/yr}$** ($R^2 = 0.969$) and Kansas at **$-0.1623\text{ students/FTE/yr}$** ($R^2 = 0.832$). (See Figure 2: `outputs/figures/teacher_capacity_by_state.png`).


---

## 6. City / Suburb / Town / Rural Comparison

Analyzing NCES locale groups reveals distinct structural dynamics across the metropolitan geography, as well as an important classification nuance.

### Table 4A: Dynamic Annual Repeated Cross-Section by Locale (Operating Regular Schools)
*Source: `outputs/tables/task003b_locale_trends.csv` (dynamic_annual_cross_section)*

| NCES Locale Family | 2014–15 Weighted PTR | 2024–25 Weighted PTR | 10-Yr Ratio Change | 10-Yr Ratio Change (%) | 10-Yr Enrollment Change (%) | 10-Yr Teacher FTE Change (%) | Dynamic Cross-Section Driver |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **City** | **15.06** | **13.75** | **-1.31** | **-8.70%** | +10.94% | +21.46% | Staffing Outpaced Growth |
| **Suburb** | **15.81** | **14.16** | **-1.65** | **-10.44%** | -8.11% | +2.61% | Enrollment Contraction |
| **Town** | **15.06** | **13.97** | **-1.09** | **-7.24%** | -7.26% | -0.06% | Staffing Expansion |
| **Rural** | **15.18** | **13.86** | **-1.32** | **-8.70%** | -3.91% | +5.22% | Enrollment Contraction |

### Table 4B: Fixed 2024–25 Locale Classification on Balanced Panel (620 Continuous Schools)
*Source: `outputs/tables/task003b_locale_trends.csv` (fixed_2024_2025_balanced_panel)*

| NCES Locale Family (Fixed 2024–25) | 2014–15 Weighted PTR | 2024–25 Weighted PTR | 10-Yr Ratio Change | 10-Yr Ratio Change (%) | 2014–15 Enrollment | 2024–25 Enrollment | 10-Yr Enrollment Change (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **City** | **15.26** | **13.84** | **-1.42** | **-9.31%** | 116,761 | 116,566 | **-0.17%** |
| **Suburb** | **15.86** | **14.17** | **-1.69** | **-10.66%** | 132,576 | 124,354 | **-6.20%** |
| **Town** | **15.47** | **13.99** | **-1.48** | **-9.57%** | 31,068 | 26,752 | **-13.89%** |
| **Rural** | **14.81** | **13.84** | **-0.97** | **-6.55%** | 36,689 | 36,764 | **+0.20%** |

### Geographical & Classification Insights
1. **The City/Suburb Classification Effect:**
   - Under the dynamic annual cross-section (Table 4A), City enrollment appears to surge $+10.94\%$ while Suburban enrollment drops $−8.11\%$.
   - However, under fixed 2024–25 geography on continuously observed schools (Table 4B), City enrollment is **essentially flat** ($116,761 \rightarrow 116,566$, $-0.17\%$).
   - This divergence occurs because **90 continuously observed schools changed NCES locale codes over the decade** (reflecting census reclassifications, suburban densification, and campus updates), alongside new school openings in urban core charters. The apparent enrollment surge in 'City' schools is largely a classification and compositional transition, not massive depopulation of suburbs into the urban core.
2. **Universal Capacity Expansion Across All Locales:**
   - Regardless of whether dynamic annual locales or fixed classifications are used, **structural staffing ratios improved across all four geographic categories**:
     - Fixed City: $15.26 \rightarrow 13.84$ ($-1.42$, $-9.31\%$)
     - Fixed Suburb: $15.86 \rightarrow 14.17$ ($-1.69$, $-10.66\%$)
     - Fixed Town: $15.47 \rightarrow 13.99$ ($-1.48$, $-9.57\%$)
     - Fixed Rural: $14.81 \rightarrow 13.84$ ($-0.97$, $-6.55\%$)
3. **Distance Rings from Downtown KC:**
   - Inner core ($< 5\text{ mi}$): $14.96 \rightarrow 13.66$ ($-1.30$, $-8.7\%$)
   - Inner ring ($5\text{--}10\text{ mi}$): $15.44 \rightarrow 14.09$ ($-1.35$, $-8.8\%$)
   - Suburban belt ($10\text{--}20\text{ mi}$): $15.75 \rightarrow 14.22$ ($-1.53$, $-9.7\%$)
   - Outer fringe ($20+\text{ mi}$): $14.85 \rightarrow 13.49$ ($-1.36$, $-9.2\%$)
   (See Figure 3: `outputs/figures/teacher_capacity_by_locale.png`).


---

## 7. Primary / Middle / High School Comparison

Disaggregating by official NCES `school_level` reveals that structural capacity expansion was **heavily concentrated in primary/elementary grades**, while high schools experienced much milder change.

### Table 5: Grade Band Trajectories (Official NCES `school_level`, Operating Regular Schools)
*Source: `outputs/tables/task003b_gradeband_trends.csv`*

| NCES School Level | 2014–15 Weighted PTR | 2024–25 Weighted PTR | 10-Yr Ratio Change | 10-Yr Ratio Change (%) | 10-Yr Enrollment Change (%) | 10-Yr Teacher FTE Change (%) | Primary Accounting Driver |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Primary** | **15.39** | **13.51** | **-1.88** | **-12.22%** | -5.86% | +7.24% | Joint Staffing Expansion & Enrollment Contraction |
| **Middle** | **14.78** | **13.35** | **-1.43** | **-9.68%** | -0.22% | +10.50% | Joint Staffing Expansion & Enrollment Contraction |
| **High** | **16.22** | **15.28** | **-0.94** | **-5.80%** | +11.85% | +18.76% | Staffing Outpaced Growth |
| **Other** | **10.41** | **2.39** | **-8.02** | **-77.04%** | -95.09% | -78.63% | Staffing Expansion |

### Grade-Band Insights
1. **Elementary Front-Loading:** Primary schools saw the steepest reduction in student-to-teacher ratio ($15.39 \rightarrow 13.51$, a drop of **$-1.88$ students/FTE, $-12.22\%$**). Enrollment shrank by $-5.86\%$ while teacher staffing expanded $+7.24\%$.
2. **Middle Schools:** Ratios dropped from **14.78 to 13.35** ($-1.43$ students/FTE, $-9.68\%$). Enrollment was flat ($-0.22\%$) while teacher FTE expanded by $+10.50\%$.
3. **High School Resistance:** In contrast, high schools consistently maintained the highest ratios in the region throughout the decade ($16.22$ in 2014 down to $15.28$ in 2024). High school enrollment grew by $+11.85\%$ ($+10,817$ students) while teacher FTE grew $+18.76\%$ ($+1,055.45$ FTE). Because student enrollment expanded so strongly, the ratio fell by only **$-0.94$ students/FTE ($-5.80\%$)**.
4. **Fixed-Effects Validation:** Within-school fixed effects models on the balanced panel confirm this pronounced divergence: the annual within-school trend was **$-0.2152\text{ students/FTE/yr}$** in Primary schools ($p < 0.0001$), **$-0.1422$** in Middle schools ($p < 0.0001$), and only **$-0.0531$** in High schools ($p = 0.0151$).
5. **Methodological Note on Classification:** Using the alternative custom grade-span classifier produces essentially identical qualitative findings (Primary $-1.88$, Middle $-1.44$, High $-0.73$). The official NCES `school_level` is adopted as canonical.


---

## 8. Teacher vs. Paraprofessional Staffing Composition

A critical structural question is whether schools substituted paraprofessionals for certified teachers or expanded both categories concurrently.

### Table 6: Teacher and Paraprofessional Staffing Intensity (Regional LEAs)
*Source: `outputs/tables/task003b_regional_trends.csv`*

| School Year | K–12 Enrollment | Teachers K–12 FTE | Paraprofessionals FTE | Teachers per 1,000 Students | Paras per 1,000 Students | Combined Staffing Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014–2015** | 321,228 | 21,633.26 | 4,774.11 | **67.35** | **14.86** | **12.16** |
| **2015–2016** | 289,666\* | 19,458.42\* | 4,038.03\* | **67.18**\* | **13.94**\* | **12.33**\* |
| **2016–2017** | 325,274 | 22,065.54 | 4,856.21 | **67.84** | **14.93** | **12.08** |
| **2017–2018** | 327,585 | 22,670.66 | 4,886.68 | **69.21** | **14.92** | **11.89** |
| **2018–2019** | 328,578 | 22,828.39 | 5,147.01 | **69.48** | **15.66** | **11.75** |
| **2019–2020** | 329,357 | 23,136.48 | 5,273.11 | **70.25** | **16.01** | **11.59** |
| **2020–2021** | 321,732 | 23,310.69 | 4,871.59 | **72.45** | **15.14** | **11.42** |
| **2021–2022** | 320,149 | 23,508.76 | 4,774.43 | **73.43** | **14.91** | **11.32** |
| **2022–2023** | 321,595 | 23,886.08 | 4,933.75 | **74.27** | **15.34** | **11.16** |
| **2023–2024** | 319,559 | 23,620.08 | 5,225.16 | **73.91** | **16.35** | **11.08** |
| **2024–2025** | 318,883 | 23,555.17 | 5,340.02 | **73.87** | **16.75** | **11.04** |
| **10-Year Change** | **-2,345** | **+1,921.91** | **+565.91** | **+6.52** | **+1.89** | **-1.12** |
| **% Change** | **-0.73%** | **+8.88%** | **+11.85%** | **+9.68%** | **+12.72%** | **-9.21%** |

*\*Note: 2015–16 figures reflect reporting entities only due to suppression in Olathe and Gardner Edgerton.*

### Staffing Composition Findings
1. **Narrow Aggregate Statement on Substitution:** There is no aggregate evidence that increased paraprofessional staffing simply replaced teacher FTE. Both categories increased relative to enrollment.
   - Certified teachers per 1,000 K–12 students rose from **67.35 to 73.87** ($+9.68\%$).
   - Paraprofessionals per 1,000 K–12 students rose from **14.86 to 16.75** ($+12.67\%$).
   - *Caveat:* Substitution could still occur in specific districts, particular programs, or individual specialized schools even while both categories expand regionally.
2. **Combined Adult Ratio:** The combined student-to-adult ratio ($\frac{\text{Enrollment}}{\text{Teachers} + \text{Paras}}$) dropped from **12.16 down to 11.04**, an overall adult capacity expansion of $−9.28\%$. (See Figure 4: `outputs/figures/teacher_and_para_intensity.png`).
3. **Terminology Guardrail:** This combined metric is strictly designated the *teacher-plus-paraprofessional staffing measure* and is **never** termed 'all instructional adults.'


---

## 9. Repeated Cross-Section vs. Balanced Panel Sensitivity

To test whether observed secular trends are artifacts of school openings, closures, or reconfigurations, we compare the full annual repeated cross-section against the 620-school continuously operating balanced panel.

### Table 7: Panel Sensitivity Audit Across 11 School Years (Operating Regular Schools)
*Source: `outputs/tables/task003b_balanced_panel_sensitivity.csv`*

| School Year | Cross-Sec Schools | Balanced Schools | Cross-Sec Weighted PTR | Balanced Weighted PTR | Weighted Diff | Cross-Sec Median PTR | Balanced Median PTR | Median Diff |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2014-2015 | 601 | 574 | 15.38 | 15.47 | +0.08 | 15.23 | 15.26 | +0.04 |
| 2015-2016 | 544 | 518 | 15.23 | 15.32 | +0.09 | 15.07 | 15.12 | +0.05 |
| 2016-2017 | 595 | 570 | 15.24 | 15.35 | +0.11 | 14.93 | 15.05 | +0.12 |
| 2017-2018 | 601 | 571 | 15.02 | 15.09 | +0.07 | 14.70 | 14.74 | +0.03 |
| 2018-2019 | 601 | 570 | 14.91 | 15.01 | +0.10 | 14.62 | 14.73 | +0.11 |
| 2019-2020 | 604 | 572 | 14.87 | 14.93 | +0.06 | 14.53 | 14.59 | +0.06 |
| 2020-2021 | 610 | 572 | 14.52 | 14.58 | +0.06 | 14.04 | 14.02 | -0.02 |
| 2021-2022 | 612 | 571 | 14.26 | 14.33 | +0.08 | 13.78 | 13.80 | +0.02 |
| 2022-2023 | 618 | 571 | 14.22 | 14.28 | +0.06 | 13.63 | 13.68 | +0.05 |
| 2023-2024 | 626 | 576 | 14.14 | 14.16 | +0.03 | 13.64 | 13.64 | +0.00 |
| 2024-2025 | 623 | 576 | 13.94 | 13.99 | +0.04 | 13.53 | 13.59 | +0.06 |

### Sensitivity Assessment
1. **Near-Perfect Concordance:** Across all 11 years, the discrepancy between the repeated cross-section and the balanced panel is **under $0.11$ ratio points** for student-weighted ratios and **under $0.12$ ratio points** for medians.
2. **Endpoint Parity:** The 10-year change in student-weighted ratio is $−1.44$ in the repeated cross-section and $−1.48$ in the balanced panel. The median school change is $−1.70$ vs. $−1.68$.
3. **Substantive Conclusion:** The trend changes very little when analysis is restricted to continuously operating schools, suggesting that school openings, closures, and other compositional turnover are not the primary explanation for the observed decline in staffing ratios. (See Figure 6: `outputs/figures/repeated_vs_balanced.png`).


---

## 10. Statistical Trend Summaries

Standardized quantitative slope summaries with clustered uncertainty describe aggregate series and school fixed-effects models on the balanced panel.

### Table 8: Econometric & Descriptive Model Results
*Source: `outputs/tables/task003b_model_results.csv`*

| Model ID | Model Family | Dependent Variable | Sample / Specification | N Obs | Annual Slope (beta) | Robust SE | p-value | Implied 10-Yr Change |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M01 | Descriptive_Aggregate_OLS | Metro_LEA_PTR_K12 | Annual aggregate series (10 valid years) | 10 | -0.16 | 0.02 | 0.00 | -1.60 |
| M02 | Descriptive_Aggregate_OLS | Metro_LEA_Combined_Ratio | Annual aggregate series (10 valid years) | 10 | -0.13 | 0.01 | 0.00 | -1.27 |
| M03 | Descriptive_Aggregate_OLS | Metro_LEA_Teachers_Per_1000 | Annual aggregate series (10 valid years) | 10 | 0.80 | 0.08 | 0.00 | 8.03 |
| M04 | Descriptive_Aggregate_OLS | Metro_LEA_Paras_Per_1000 | Annual aggregate series (10 valid years) | 10 | 0.15 | 0.05 | 0.03 | 1.47 |
| M05 | Descriptive_Aggregate_OLS | State_KS_LEA_PTR_K12 | Annual aggregate series (10 valid years) | 10 | -0.16 | 0.03 | 0.00 | -1.62 |
| M06 | Descriptive_Aggregate_OLS | State_MO_LEA_PTR_K12 | Annual aggregate series (11 valid years) | 11 | -0.16 | 0.01 | 0.00 | -1.58 |
| M07 | Descriptive_Aggregate_OLS | Metro_School_Weighted_PTR | Annual aggregate series (10 valid years) | 10 | -0.15 | 0.01 | 0.00 | -1.54 |
| M08 | Descriptive_Aggregate_OLS | Metro_School_Median_PTR | Annual aggregate series (10 valid years) | 10 | -0.19 | 0.01 | 0.00 | -1.87 |
| M09 | School_Fixed_Effects_Panel | students_per_classroom_teacher_fte_allgrades | Balanced Panel: All Regular Operating Schools (Within-School Estimator) | 6,182 | -0.17 | 0.01 | 0.00 | -1.75 |
| M10 | School_Fixed_Effects_Panel | students_per_classroom_teacher_fte_allgrades | Balanced Panel Sensitivity: Excluding Schools with Any Grade-Span Change | 3,922 | -0.16 | 0.01 | 0.00 | -1.63 |
| M11 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Locale Interaction: City (Fixed 2024-25 Classification) | 6,182 | -0.19 | 0.02 | 0.00 | -1.90 |
| M12 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Locale Interaction: Suburb (Fixed 2024-25 Classification) | 6,182 | -0.19 | 0.01 | 0.00 | -1.87 |
| M13 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Locale Interaction: Town (Fixed 2024-25 Classification) | 6,182 | -0.16 | 0.03 | 0.00 | -1.58 |
| M14 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Locale Interaction: Rural (Fixed 2024-25 Classification) | 6,182 | -0.12 | 0.02 | 0.00 | -1.18 |
| M15 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel State Interaction: MO | 6,182 | -0.17 | 0.01 | 0.00 | -1.75 |
| M16 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel State Interaction: KS | 6,182 | -0.18 | 0.02 | 0.00 | -1.76 |
| M17 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Grade Band Interaction: Primary (Official NCES school_level) | 6,182 | -0.22 | 0.01 | 0.00 | -2.15 |
| M18 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Grade Band Interaction: Middle (Official NCES school_level) | 6,182 | -0.14 | 0.02 | 0.00 | -1.42 |
| M19 | Interaction_Fixed_Effects | students_per_classroom_teacher_fte_allgrades | Balanced Panel Grade Band Interaction: High (Official NCES school_level) | 6,182 | -0.05 | 0.02 | 0.02 | -0.53 |

*Note: All school fixed-effects models absorb school indicator fixed effects and cluster standard errors at the NCES school level ($572$ clusters).*

### Modeling Interpretations
1. **Descriptive Aggregate OLS:** Aggregate linear trends show an annual slope of approximately $−0.16$ students per FTE per year across LEA ($R^2 = 0.926$) and school ($R^2 = 0.971$) levels.
2. **Within-School Magnitude:** The primary fixed-effects estimate (Model M09) shows that within the average continuously operating school, the staffing ratio fell by **$-0.1750$ students/FTE per year** ($SE = 0.0098$, $t = -17.8$).
3. **Structural Robustness:** Excluding schools with grade-span changes (Model M10) yields an almost identical within-school slope of **$-0.1634$** ($SE = 0.0120$).
4. **State Symmetry:** Within-school slopes in Missouri ($-0.1745$) and Kansas ($-0.1757$) are identical to two decimal places.


---

## 11. What the Data Establish

The empirical findings from Task 003B establish the following facts regarding the 2014–15 to 2024–25 decade in the Kansas City metropolitan area:
1. **Structural Capacity Expanded Metro-Wide:** Macro staffing ratios improved substantially. The regional pupil/teacher ratio fell by $−1.31$ students per teacher FTE ($-8.8\%$) at the LEA level and by $−1.44$ students per teacher FTE ($-9.4\%$) at the school level.
2. **Expansion Was Driven by Active Staffing Additions:** Regional K–12 enrollment was essentially flat (changed by less than 1%, $-0.73\%$, $-2,345$ students), while teacher FTE expanded by nearly 9% ($+8.88\%$, $+1,921.91$ LEA FTE). The ratio reduction was **not** caused by student loss.
3. **Staffing Intensity Rose Across Both Teachers and Paras:** Teachers per 1,000 students rose from 67.35 to 73.87 ($+9.7\%$), while paraprofessionals per 1,000 students rose from 14.86 to 16.75 ($+12.7\%$). Both categories increased relative to enrollment.
4. **The Trend Occurred Within Schools:** Continuous balanced panel models confirm a within-school contraction of $-1.75$ students per FTE ($p < 0.0001$). Compositional turnover had negligible impact.
5. **Elementary Concentration:** The expansion was heavily tilted toward Primary/Elementary schools (within-school $\beta = -0.2152$), whereas High schools saw minimal change (within-school $\beta = -0.0531$).


---

## 12. What the Data Do NOT Establish

It is equally essential to state what these data **cannot** establish:
1. **Does NOT Establish That Classroom Section Sizes Got Smaller:**
   - A lower pupil/teacher ratio does **not** prove that actual class sections shrank.
   - If added teacher FTE were allocated to non-classroom instructional roles, intervention, co-teaching, or electives, ordinary general-education sections could remain large or grow even as overall building staffing capacity rises.
2. **Does NOT Establish That Teacher Workloads Became Easier:**
   - Staffing ratios say nothing about student behavioral complexity, IEP caseloads, ELL language needs, or chronic absenteeism—all of which could intensify teacher workload independently of staffing headcounts.
3. **Does NOT Test H1a, H1b, H2, or H3:**
   - These hypotheses remain unadjudicated. Section rosters (H1a/H1b), student complexity microdata (H2), and detailed staffing role assignments (H3) are strictly required.
4. **Does NOT Establish Causal Explanations:**
   - These data do not establish whether specific tax levies, state funding formulas (e.g., Kansas *Gannon* settlement or Missouri foundation formula), or federal ESSER funds caused the staffing expansions.


---

## 13. Implications for Phase 4 Section-Level Research

These structural findings fundamentally reshape the empirical puzzle for subsequent phases of the project:

### The Emerging Paradox: "Macro Capacity Expansion vs. Micro Classroom Experience"
Prior to this analysis, a common hypothesis was that classrooms feel overcrowded and overwhelming because school districts suffered a decade of teacher attrition and deteriorating staffing ratios.

**The data decisively reject that simple narrative.** The Kansas City region employs substantially more teachers and paraprofessionals per student today than it did ten years ago.

This counterintuitive finding makes Phase 4 research substantially more important and sharply focused:
1. **The Allocation Question (Testing H1a & H3):**
   - *How are additional teacher FTE distributed among general-education sections, special education, intervention/small-group instruction, co-teaching, electives, alternative programs, and other instructional assignments?*
   - NCES defines a classroom teacher as professional staff who instruct students and maintain attendance records. Administrative staff and instructional coordinators/supervisors are separate CCD categories.
   - Phase 4 must analyze section-level master schedules and course rosters to measure the gap between **reported pupil/teacher ratios** and **median classroom section sizes**.
   - Separately examine growth in non-teacher categories: instructional coordinators, counselors, administrators, and student-support staff.
2. **The Student Complexity Question (Testing H2):**
   - If structural adult capacity expanded by $9\%\text{--}12\%$, why might teachers feel more constrained than ever?
   - Phase 4 must incorporate SPED/IEP rates, ELL density, student mental health referrals, and chronic absenteeism to evaluate whether rising student needs eclipsed the real growth in instructional capacity.
3. **High School vs. Elementary Divergence:**
   - Because structural capacity barely expanded at the high school level ($-0.53$ within-school change over 10 years) compared to primary schools ($-2.15$), section-level inquiries should test whether secondary academic courses experienced acute section-size inflation.


---

## 14. Artifact and Verification Inventory

### Output Tables (`outputs/tables/`)
1. `task003b_regional_trends.csv` (22 rows: annual regional LEA and school series with coverage tiers)
2. `task003b_state_trends.csv` (44 rows: annual Missouri and Kansas LEA and school series)
3. `task003b_locale_trends.csv` (88 rows: dynamic cross-section and fixed 2024–25 balanced panel by locale)
4. `task003b_gradeband_trends.csv` (44 rows: annual series across Primary, Middle, High, and Other using official NCES `school_level`)
5. `task003b_endpoint_decomposition.csv` (84 rows: full decade and subperiod accounting decompositions)
6. `task003b_balanced_panel_sensitivity.csv` (11 rows: annual cross-section vs. balanced panel comparisons)
7. `task003b_model_results.csv` (19 rows: descriptive OLS trends and fixed-effects panel models)

### Output Figures (`outputs/figures/`)
1. `regional_teacher_capacity_trend.png` (LEA and School student-weighted trends with 2015–16 marked)
2. `teacher_capacity_by_state.png` (Missouri vs. Kansas trajectories with suppression annotation)
3. `teacher_capacity_by_locale.png` (City, Suburb, Town, Rural trajectories)
4. `teacher_and_para_intensity.png` (Staff per 1,000 students and combined adult staffing ratio)
5. `capacity_change_decomposition.png` (Enrollment change % vs. Teacher FTE change % across subgroups)
6. `repeated_vs_balanced.png` (Cross-section vs. balanced panel weighted and median comparisons)
7. `school_ratio_distribution.png` (School-level median, IQR, and 10th–90th percentile bands)

*All figures carry the mandatory subtitle: "Structural staffing ratio; not classroom size."*