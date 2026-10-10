# Data Provenance & Source Audit Registry (`2026-10-09-keyboarding-mode-effects`)

This document provides complete provenance, extraction citations, table references, and verification audits for all empirical datasets utilized in the Keyboarding & Digital Assessment Mode Effects Observatory.

---

## 1. Primary Source Audit Registry

| Source ID | Institution / Authors | Collection Year(s) | Original Publication Reference | Exact Table / Page | Metric Unit | Verification Status | Repository Location |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :--- |
| `SRC-01` | NCES High School Transcript Study (HSTS) | 2000, 2005, 2009, 2019 | [HSTS 2019 Tables](https://nces.ed.gov/nationsreportcard/hsts/2019_tables/2019_table1.aspx) | Table 1 | Percentage of graduates (%) | **Verified Primary Table** | `data/raw/nces_hsts_2019_table1.csv` |
| `SRC-02` | NCES School Pulse Panel | 2021–2025 | [NCES School Pulse Panel Technology Reports](https://ies.ed.gov/schoolpulse/) | 2024–25 Report | Percentage of public schools (%) | **Verified Primary Report** | `data/raw/nces_pulse_device_access.csv` |
| `SRC-03` | Education Week Research Center | Nov 2024 | [Education Week Keyboarding Survey](https://www.edweek.org) | Survey of $N = 404$ leaders | Percentage (%) | **Verified Primary Article** | `data/raw/edweek_keyboarding_survey_2024.csv`, `data/raw/edweek_equity_breakdown_2024.csv` |
| `SRC-04` | NCES NAEP Mode Evaluation | 2017 | [*2017 NAEP Transition to Digitally Based Assessments*](https://nces.ed.gov/nationsreportcard/subject/publications/main2020/pdf/transitional_whitepaper.pdf) | Table 4.1c, p. 37 | **Percentage Points (pp)** | **Verified Primary Table** | `data/raw/naep_2017_mode_table41c.csv` |
| `SRC-05` | Ben Backes & James Cowan | 2015–2016 | [*Economics of Education Review*, Vol. 68, pp. 89–103 (2019)](https://doi.org/10.1016/j.econedurev.2018.12.007) | Tables 2–4 | Standard Deviations (SD) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-06` | John Gordanier, Orgul Ozturk, & Crystal Zhan | 2015–2018 | [*Education Finance and Policy*, Vol. 18(2), pp. 232–252 (2023)](https://doi.org/10.1162/edfp_a_00373) | Full Paper | Standard Deviations (SD) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-07` | Carol Parker | 2018 | [*Journal of Research in Business Education*, Vol. 59(1), pp. 1–14](https://jrbe.nbea.org) | Tables 1–3 ($N = 916 / 906$) | Chi-Square Test ($p > 0.05$) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-08` | IEA / NCES ICILS | 2018, 2023 | [*U.S. Results from the 2023 International Computer and Information Literacy Study*](https://nces.ed.gov/surveys/icils/) | National Summary Report | Scale Score & Percentages | **Verified Primary Report** | `data/raw/icils_cil_trends_2018_2023.csv` |
| `SRC-09` | NAEP Grade 4 Teacher Questionnaire | 2017 | [2017 NAEP SQ Teacher G4](https://nces.ed.gov/nationsreportcard/subject/about/pdf/bgq/teacher/2017_sq_teacher_g4.pdf) | Questions 13 & 14 | Survey Questions | **Instrument Verified / Frequencies Unverified** | `data/raw/naep_g4_teacher_questionnaire_audit.csv` |
| `SRC-10` | NCES Grade 4 Computer Writing Pilot | 2012 | *2012 NAEP Computer-Based Writing Pilot* & Usability Study | National Pilot Benchmarks | Word Count & WPM | **Verified Primary Benchmark** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-11` | IEA / NCES TIMSS | 2019 | [TIMSS 2019 International Database](https://timss2019.org/international-database/) & [NCES PUF 2022-047](https://ies.ed.gov/use-work/dataset/trends-international-mathematics-and-science-study-timss-2019-u-s-public-use-data-files-and) | U.S. Grade 4 eTIMSS & Bridge Microdata | Scale Score & Item pp | **Verified Public Microdata** | `data/processed/timss_2019_g4_item_contrasts.csv`, `data/processed/timss_2019_g4_student_pvs.csv`, `artifacts/tables/table12_timss_2019_iea_benchmark_audit.csv`, `artifacts/tables/table13_timss_2019_booklet_exposure_sensitivity.csv`, `artifacts/tables/table14_timss_2019_item_invariance_sensitivity.csv` |
| `SRC-12` | Bethany Fishbein, Michael O. Martin, Ina V.S. Mullis, & Pierre Foy | 2018 | [*Large-scale Assessments in Education*, Vol. 6, Article 11](https://doi.org/10.1186/s40536-018-0064-2) | Full Paper | Logits & Item pp differences | **Verified Peer-Reviewed** | Literature / TIMSS Item Equivalence Study |
| `SRC-13` | Matthias von Davier, Bethany Fishbein, & Stephen J. Chrostowski | 2020 | [*Methods and Procedures: TIMSS 2019 Technical Report*, Chapters 12 & 13](https://timssandpirls.bc.edu/timss2019/methods/) | Exhibits 12.31, 13.1, 13.2 | Scale Score, Percent Correct, Item Invariance | **Verified Primary Report** | IEA Technical Documentation |
| `SRC-14` | Aidan Clerkin, D. Verhelst, A. Mahdi, S. Mammadov, & G. McHugh | 2026 | [*Large-scale Assessments in Education*, Vol. 14, Article 4](https://doi.org/10.1186/s40536-026-00213-x) | Full Paper | Bridge Mode Differences | **Verified Peer-Reviewed** | Literature / Cross-National Bridge Studies |
| `SRC-15` | Sonja Breuer | 2023 | [*Royal Society Open Science*, Vol. 10(9), Article 230784](https://doi.org/10.1098/rsos.230784) | Full Paper ($k = 184$) | Standardized Mean Differences ($g$) | **Verified Peer-Reviewed** | Literature / Response Format Meta-Analysis |

---

## 2. Granular Extraction Audits & Field Discrepancy Corrections

### `SRC-01`: NCES NAEP HSTS Table 1 (High School Graduates Coursework)
- **Original Source**: National Center for Education Statistics, High School Transcript Study, Table 1.
- **Population**: Nationally representative sample of high school graduates.
- **Audited Fields**:
  - *Keyboarding*: $44.1\%$ in 2000 ($\text{SE} = 1.25$), $26.6\%$ in 2005 ($\text{SE} = 1.11$), $15.0\%$ in 2009 ($\text{SE} = 0.88$), $2.5\%$ in 2019 ($\text{SE} = 0.28$). Drop from 2000 to 2019 is statistically significant ($p < 0.05$).
  - *Computer Applications*: $3.1\%$ in 2000 ($\text{SE} = 0.35$), $26.8\%$ in 2005 ($\text{SE} = 1.14$), $31.4\%$ in 2009 ($\text{SE} = 1.18$), $10.4\%$ in 2019 ($\text{SE} = 0.58$).
  - *Word Processing*: $12.8\%$ in 2000 ($\text{SE} = 0.74$), $5.0\%$ in 2005 ($\text{SE} = 0.51$), $3.8\%$ in 2009 ($\text{SE} = 0.41$), $1.2\%$ in 2019 ($\text{SE} = 0.17$).
  - *Business Computer Applications*: $6.2\%$ in 2000, $7.1\%$ in 2005, $3.4\%$ in 2009, $8.8\%$ in 2019.
- **Correction Applied**: Earlier draft mistakenly transcribed Computer Applications as starting at 18.2% and ending at 12.4%. Reconciled to exact published values: $3.1\%$ (2000) $\to$ $31.4\%$ (2009 peak) $\to$ $10.4\%$ (2019).

### `SRC-02`: NCES School Pulse Panel (1:1 Student Device Programs)
- **Original Source**: NCES School Pulse Panel, 2024–25 School Year Technology Report.
- **Methodological Scope**: The School Pulse Panel began monthly collections in 2021.
- **Audited Value**: $88.0\%$ of U.S. public schools reported having a 1-to-1 computing program for the 2024–25 school year (up from $83.0\%$ in 2021–22).
- **Correction Applied**: Removed the synthetic continuous 2013–2025 time-series line, which conflated disparate historical surveys (FRSS and Pew) with the School Pulse Panel.

### `SRC-03`: Education Week Research Center 2024 Keyboarding Survey
- **Sample**: Nationally representative survey of $N = 404$ school and district leaders conducted in late 2024.
- **Delivery Models**:
  - Standalone keyboarding class only: $8.0\%$.
  - Combined standalone and integrated: $11.0\%$.
  - Integrated within regular classroom instruction: $50.0\%$.
  - No formal keyboarding instruction: $31.0\%$.
- **Socioeconomic Breakdown in Grades K–2**:
  - Lower-poverty school systems: **$74.0\%$** report keyboarding instruction.
  - Higher-poverty school systems: **$51.0\%$** report keyboarding instruction.
  - Disparity Ratio: **$1.45\times$** ($74\% / 51\%$).
- **Correction Applied**: Corrected an earlier transcription error that erroneously recorded 36% vs. 18% (claiming a 2.0x gap). The actual published disparity is 74% vs. 51% (1.45x gap).

### `SRC-04`: NCES 2017 NAEP Mode Evaluation Study (Table 4.1c)
- **Publication**: *2017 NAEP Transition to Digitally Based Assessments in Mathematics and Reading at Grades 4 and 8: Mode Evaluation Study* (`transitional_whitepaper.pdf`), Table 4.1c, page 37.
- **Measurement Unit**: **Mean item score differences in PERCENTAGE POINTS (pp)**, NOT standard deviations!
- **Audited Values (Reading)**:
  - **Grade 4 Selected-Response (SR)**: Digital $60\%$ vs. Paper $64\%$ $\to$ Difference = **$-3.8$ pp** ($\text{SE} = 0.22, p < 0.05$).
  - **Grade 4 Constructed-Response (CR)**: Digital $35\%$ vs. Paper $42\%$ $\to$ Difference = **$-6.8$ pp** ($\text{SE} = 0.18, p < 0.05$).
  - **Grade 4 Format Gap (CR vs. SR)**: **$-3.0$ pp**.
  - **Grade 8 Selected-Response (SR)**: Digital $74\%$ vs. Paper $76\%$ $\to$ Difference = **$-1.6$ pp** ($\text{SE} = 0.19, p < 0.05$).
  - **Grade 8 Constructed-Response (CR)**: Digital $53\%$ vs. Paper $55\%$ $\to$ Difference = **$-2.0$ pp** ($\text{SE} = 0.24, p < 0.05$).
  - **Grade 8 Format Gap (CR vs. SR)**: **$-0.4$ pp**.
- **Audited Values (Mathematics)**:
  - **Grade 4 Selected-Response (SR)**: Digital $54\%$ vs. Paper $56\%$ $\to$ Difference = **$-2.4$ pp** ($\text{SE} = 0.24, p < 0.05$).
  - **Grade 4 Constructed-Response (CR)**: Digital $46\%$ vs. Paper $52\%$ $\to$ Difference = **$-6.9$ pp** ($\text{SE} = 0.31, p < 0.05$).
  - **Grade 4 Format Gap (CR vs. SR)**: **$-4.5$ pp**.
  - **Grade 8 Selected-Response (SR)**: Digital $51\%$ vs. Paper $53\%$ $\to$ Difference = **$-2.5$ pp** ($\text{SE} = 0.26, p < 0.05$).
  - **Grade 8 Constructed-Response (CR)**: Difference = **$-3.5$ pp** ($\text{SE} = 0.30, p < 0.05$).
  - **Grade 8 Format Gap (CR vs. SR)**: **$-1.0$ pp**.
- **Calibrated Cross-Subject Interpretation**: Across fourth-grade reading and mathematics, digitally administered constructed-response items exhibited larger negative mode differences than selected-response items. This cross-subject pattern suggests that response format and associated interface demands merit further investigation, but does not isolate a common cognitive mechanism.
- **Correction Applied**: Reconciled DBA/PBA percentages and standard errors to Table 4.1c, p. 37. Added Grade 4 and Grade 8 Mathematics contrasts.

### `SRC-05` to `SRC-07` & `SRC-10`: Empirical Benchmark Literature
- **Backes & Cowan (2019)**: Corrected journal citation to *Economics of Education Review* (Vol. 68, pp. 89–103). Verified Year 1 PARCC mode penalty of $-0.25$ SD in ELA and $-0.10$ SD in math.
- **Gordanier, Ozturk, & Zhan (2023)**: Corrected citation to *Education Finance and Policy* (Vol. 18(2), pp. 232–252, DOI: 10.1162/edfp_a_00373). Verified Table 3 main OLS estimates: ELA $-0.085$ SD ($\text{SE} = 0.007$) and Math $-0.024$ SD ($\text{SE} = 0.007$; 2SLS is $-0.017$ SD, n.s.). (Note: $-0.044$ SD in previous drafts was a science interaction estimate, corrected to the primary Table 3 math OLS estimate). Larger impacts for students from poor households; mitigated by school technology access.
- **Carol Parker (2018)**: *Journal of Research in Business Education* (Vol. 59(1), pp. 1–14). Reconciled to the study's actual methodology: a chi-square test of independence on $N = 916$ (Essay 1) and $N = 906$ (Essay 2) middle school students, reporting no statistically significant relationship ($p > 0.05$) between completing a 9-week keyboarding course and writing test proficiency.
- **NCES Grade 4 Computer Writing Pilot (2010 vs. 2012)**: In the 2012 NAEP writing pilot ($N \approx 10,400$), computer responses averaged 110 words vs. 159 words on paper in 2010 (a 30.8% reduction). However, on a common prompt scored on a 1–6 rubric, computer responses averaged 3.08 vs. 2.98 on paper; shorter length did not lower average scores overall. Crucially, higher-performing students scored substantially higher on computers while lower-performing students did not (widening the achievement gap). *Methodological Note*: These were separate pilot administrations, not a randomized crossover trial. Companion usability studies documented an average typing speed of 12 WPM for 4th graders and 30 WPM for 8th graders.
- **NAGB 2017 Writing Assessment Suppression**: NCES declared the 2017 national writing assessment results unreportable due to unresolved comparability concerns; researchers could not determine how much of the performance change reflected device changes versus differences in students' writing skills.

### `SRC-08`: IEA ICILS (2018 vs. 2023)
- **Scores**: U.S. 8th graders dropped from 519 in 2018 to 482 in 2023 (-37 scale points, -0.37 SD, $p < 0.001$).
- **Proficiency Distribution**: **51%** of U.S. 8th graders scored at Level 1 or below (25% below Level 1 [deficient] + 26% at Level 1 [basic]).
- **Socioeconomic Gap**: 102 scale points between students in the highest and lowest SES quartiles.

### `SRC-09`: NAEP Grade 4 Teacher Questionnaire Status
- **Audit Findings**: The public background questionnaire instrument (`2017_sq_teacher_g4.pdf`) confirms that teachers were asked about their typing expectations (Question 13) and the percentage of students meeting them (Question 14).
- **Correction Applied**: Removed previously fabricated response distributions (e.g. "67% of teachers report half or fewer students meet expectations"). Formally registered this item as **Instrument Verified / Response Frequencies Unverified (Awaiting Microdata Extraction)**.

### `SRC-11`: TIMSS 2019 U.S. Grade 4 eTIMSS & Bridge Microdata Audit
- **Primary Database**: IEA TIMSS 2019 International Database (`T19_G4_USA_SPSS.zip`, files `asausab7.sav`, `asausam7.sav`, `asgusab7.sav`, `asgusam7.sav`, `acgusab7.sav`, `acgusam7.sav`), IEA Published Item Statistics (`T19Br_G4_MAT_Item Percent Correct.xlsx` and `eT19_G4_MAT_Item Percent Correct.xlsx`), and NCES Public-Use Files (NCES 2022-047).
- **Sample Accounting**: $10,428$ U.S. fourth-grade students across 294 participating schools:
  - Paper Bridge: $N = 1,652$ students in 79 schools (83 classrooms).
  - Digital eTIMSS: $N = 8,776$ students in 287 schools (507 classrooms).
  - **Within-School Randomized Overlap**: 72 public schools administered randomized classroom assignments between modes ($N = 2,728$ students: $1,456$ paper vs $1,272$ digital across 72 vs 75 classrooms).
- **Stacked Student-by-Item Response Panel**: $164,653$ student $\times$ item observations ($40,759$ paper vs $123,894$ digital) across all 99 anchor items, containing student survey weights, Jackknife zones, cluster IDs, item rubrics, and scored percentage points.
- **Common Anchor Items**: Exactly 99 common mathematics anchor items administered in both paper and digital formats:
  - Multiple Choice (MC / Selected Response): 49 items.
  - Constructed Response (CR / Student Entered): 50 items.
- **Scoring Pipeline Audit & Diagnostic Recoding**:
  - Replaced naive single-code checking (`== 10.0` / `== 20.0`) with official IEA two-digit diagnostic scoring: full credit awarded to all diagnostic strategies (`10 <= code <= 19` for 1 pt; `20 <= code <= 29` for 2 pts, `10 <= code <= 19` for 1 pt / 0.5 partial credit).
  - Explicitly preserved SPSS user-defined missing codes via `user_missing=True` to recover omitted responses (`99.0` for CR, `9.0` for MC) and not-reached responses (`96.0` for CR, `6.0` for MC).
  - Recovered omission rates: Paper MC 3.37% vs Digital MC 1.19%; Paper CR 2.64% vs Digital CR 1.37%.
- **Validation against Published IEA Item Benchmarks (Table 12)**:
  - Validated scoring pipeline comprehensively across all 99 anchor items against official IEA published item percent-correct workbooks (`T19Br_G4_MAT_Item Percent Correct.xlsx` and `eT19_G4_MAT_Item Percent Correct.xlsx`), logged in `artifacts/tables/table12_timss_2019_iea_benchmark_audit.csv`.
  - On 1-point items ($N = 94$): The maximum absolute difference between the pipeline and official published IEA item percentages is $\le 0.00500$ percentage points across both paper and digital administrations, reflecting pure rounding to two decimal places in official tables (e.g. `MP51043`: paper $49.93\%$, digital $44.27\%$).
  - On 2-point diagnostic items ($N = 5$): The pipeline's weighted percent full credit matches the official IEA published full-credit benchmark to 5 decimal places ($\Delta = 0.00000$ exact match across all items, e.g., `MP61228` paper 29.62660% vs. 29.62660%, digital 16.17916% vs. 16.17916%), while properly crediting diagnostic partial credit ($21.07\%$ receiving 1 point out of 2) to yield the true psychometric average score ($40.16\%$).
  - A programmatic assertion in the automated test suite verifies 99 out of 99 items pass validation against official published IEA tables.
- **Audited Empirical Findings**:
  - **Overall Scale Score Difference**: $-1.98$ scale score points across 5 Plausible Values (Paper $536.72$ vs. Digital $534.73$, pooled $\text{SD} = 87.24$, $-0.023$ SD). Within the 72 randomized schools, overall scale score difference is $+3.28$ points ($+0.038$ SD).
  - **Item Format Contrasts**:
    - Multiple Choice Mode Difference: **$-0.47$ percentage points** ($\text{SE} = 0.53$, median $-0.24$ pp).
    - Constructed Response Mode Difference: **$-3.90$ percentage points** ($\text{SE} = 0.73$, median $-3.92$ pp).
    - **Format Gap**: $\Delta_{\text{format}} = (\text{Digital} - \text{Paper})_{\text{CR}} - (\text{Digital} - \text{Paper})_{\text{MC}} = \mathbf{-3.42\text{ percentage points}}$ (Welch $t = -3.80, p = 0.0003$).
    - Answered-Only Sensitivity: Format Gap = **$-2.65\text{ pp}$**.
  - **Cognitive Domain Divergence & Confounding Disclosure**:
    - Reasoning MC ($N=8$): **$+2.61$ pp** (digital higher than paper).
    - Reasoning CR ($N=10$): **$-7.54$ pp** (digital severely depressed).
    - Reasoning Format Gap: $\mathbf{-10.14\text{ percentage points}}$!
    - *Methodological Caveat*: All 5 items requiring typed text explanations (`MP51008`, `MP61228`, `MP61248`, `MP61255`, `MP61256`) belong to the **Reasoning** cognitive domain; input modality is confounded with cognitive complexity in the anchor item pool.
  - **Input Modality Gradient (Provisional Taxonomy)**:
    - Multiple Choice (click/tap, $N=49$): **$-0.47$ pp** (SE 0.53)
    - CR: Drawing / Graphing ($N=10$): **$-3.10$ pp** (SE 1.89)
    - CR: Interactive / Table ($N=8$): **$-3.18$ pp** (SE 1.87)
    - CR: Number-pad / Numeric ($N=27$): **$-3.80$ pp** (SE 0.96)
    - CR: Text / Explanation ($N=5$): **$-7.13$ pp** (SE 2.09)
  - **Econometric Estimation Suite**:
    - *Model 1 (National Survey-Weighted DiD)*: $\beta = \mathbf{-3.102\text{ pp}}$ ($\text{SE} = 0.663, t = -4.68, p < 0.0001, 95\%\text{ CI} = [-4.402, -1.802]$), clustered by school.
    - *Model 2 (National Item Fixed-Effects Panel WLS)*: $\beta = \mathbf{-3.422\text{ pp}}$ ($\text{SE} = 0.668, t = -5.12, p = 3.0 \times 10^{-7}, 95\%\text{ CI} = [-4.732, -2.112]$), controlling for booklet item composition via 99 item baseline fixed effects.
    - *Model 3 (Within-School Student DiD on 72 Schools)*: $\beta = \mathbf{-2.364\text{ pp}}$ ($\text{SE} = 0.868, t = -2.72, p = 0.0065, 95\%\text{ CI} = [-4.065, -0.663]$).
    - *Model 4a (Within-School Item FE + School FE Panel, Classroom Clustering)*: $\beta = \mathbf{-2.734\text{ pp}}$ ($\text{SE} = 0.932, t = -2.93, p = 0.00335, 95\%\text{ CI} = [-4.561, -0.907]$), clustered by classroom ($N=147$).
    - *Model 4b (Within-School Item FE + School FE Panel, School Clustering)*: $\beta = \mathbf{-2.734\text{ pp}}$ ($\text{SE} = 0.843, t = -3.24, p = 0.00119, 95\%\text{ CI} = [-4.386, -1.082]$), clustered by school ($N=72$).
    - *Model 5 (SES Interaction Term)*: Interaction coefficient $\beta = \mathbf{-0.096\text{ pp}}$ ($\text{SE} = 1.151, p = 0.934$). Null interaction with $95\%\text{ CI} = [-2.351, +2.159]$ pp confirms absence of detectable moderation while acknowledging that confidence bounds do not rule out $\pm 2.2$ pp heterogeneity.
  - **Booklet Exposure & Student-Normalized Weighting Sensitivity (Table 13)**:
    - *Unequal Booklet Exposure*: Due to TIMSS block matrix designs, paper students completed 2 blocks averaging 24.67 items while digital students completed 2 blocks averaging 14.12 items.
    - *Weighting Specifications*: Evaluated across 12 regression specifications comparing unweighted row-level, survey WLS row-level ($w_{ij} = \text{TOTWGT}_i$), student-normalized unweighted ($w_{ij} = 1 / n_i$), and student-normalized survey WLS ($w_{ij} = \text{TOTWGT}_i / n_i \times \bar{n}$).
    - *Invariance of Results*:
      - Model 2 (National Item FE): Format gap ranges between $-3.30$ and $-3.68$ pp across all 4 weighting schemes (all $p < 10^{-6}$).
      - Model 4 (Within-School Item+School FE): Format gap ranges between $-2.68$ and $-2.93$ pp across all weighting schemes (all $p < 0.006$ under classroom clustering; all $p < 0.0015$ under school clustering).
      - Unequal booklet exposure does not account for the observed constructed-response mode penalty.
  - **Survey Inference & Randomization Inference**:
    - *Survey Uncertainty Estimators*: The repository provides two complementary uncertainty estimators for the national student format gap DiD: (1) *TIMSS Jackknife Repeated Replication (JK2)* with complementary replicate half-samples calculated under mode independence yields $SE_{\text{indep}} = 0.668$ pp ($t = -4.64, p < 0.00001, 95\%\text{ CI} = [-4.412, -1.792]$ pp); (2) *School-Clustered Regression Linearization* across the pooled sample yields $SE_{\text{cluster}} = 0.663$ pp ($t = -4.68, p < 0.00001$). The estimates are closely aligned; however, full joint design-based replicate covariance estimation within a unified survey procedure remains a documented methodological qualification (independent-jackknife standard errors are not uniformly conservative across all sub-estimands).
    - *Within-School Randomization Inference*: Monte Carlo Randomization Inference with 2,000 classroom permutations within the 72 dual-mode schools tests the equal-weighted average of classroom differences, yielding a finite-sample-corrected two-tailed $p$-value of $p = 0.0400$. This non-parametric test is informative alongside, but distinct from, the stacked item-and-school fixed-effects panel regression.
  - **Item Invariance & Calibration Sensitivity Analysis (Table 14)**:
    - *Reconciliation of Item Pool*: The 99 administered bridge items reconcile exactly to the official TIMSS scaling inventory: 92 items were scaled in the calibration model (Exhibit 12.31; 42 MC and 50 CR), while 7 items are unscaled subparts of two compound items (`MP61018A-D`, `MP61240A-C`).
    - *Official Invariance Breakdown*: In the official TIMSS eTIMSS scaling (Chapter 12 Appendix 12K and Chapter 13 Exhibit 13.1), 74 of the 92 items were certified as invariant (mode-equivalent; 41 MC, 33 CR) and inherited fixed IRT parameters, while 18 items were designated non-invariant (1 MC, 17 CR) and received separate mode-specific parameters due to interactive interface adaptations (e.g., line-drawing tools, grid graphing, chart completion).
    - *Sensitivity Across Subsets*:
      - **All 99 Administered Items**: Model 2 $\beta = -3.42$ pp ($SE = 0.67$); Model 4 $\beta = -2.73$ pp ($SE = 0.84$ school, $0.93$ class).
      - **92 Scaling Calibration Items**: Model 2 $\beta = -3.20$ pp ($SE = 0.67$); Model 4 $\beta = -2.61$ pp ($SE = 0.90$ school, $0.93$ class).
      - **74 Officially Invariant Items (Mode-Equivalent)**: Model 2 $\beta = -3.07$ pp ($SE = 0.72, p = 0.00002$); Model 4 $\beta = -2.58$ pp ($SE = 0.97, p = 0.00795$ school, $SE = 0.99, p = 0.0096$ class).
      - **18 Non-Invariant Items**: Model 2 $\beta = -4.09$ pp ($SE = 3.04$); Model 4 $\beta = -2.51$ pp ($SE = 4.90$).
    - *Key Psychometric Finding*: The digital constructed-response penalty is NOT driven by the interactive interface adaptations of non-invariant items. The penalty remains robustly negative ($-3.07$ pp national, $-2.58$ pp within-school) even when restricted to the 74 items officially certified as psychometrically equivalent across modes.
  - **Verification Suite**:
    - All empirical findings, scoring tables, and models are verified by a 22-test automated Pytest suite (`pytest tests/ -v`).

### `SRC-12`: Fishbein et al. (2018) — TIMSS 2019 Item Equivalence Study
- **Citation**: Fishbein, B., Martin, M. O., Mullis, I. V. S., & Foy, P. (2018). *The TIMSS 2019 item equivalence study: Examining mode effects for computer-based assessment and implications for measuring trends.* **Large-scale Assessments in Education**, 6(1), Article 11. DOI: [10.1186/s40536-018-0064-2](https://doi.org/10.1186/s40536-018-0064-2).
- **Scope & Sample**: Counterbalanced, within-subjects pilot study administered across 24 countries ($N = 16,894$ Grade 4 students; $N = 9,164$ Grade 8 students across 11 countries).
- **Core Findings**: While overall construct validity was preserved across modes, computer administration systematically increased item difficulty in mathematics, establishing that raw digital and paper scores cannot be directly combined without psychometric mode adjustment constants.

### `SRC-13`: von Davier et al. (2020) — TIMSS 2019 Technical Report (Chapters 12 & 13)
- **Citation**: von Davier, M., Fishbein, B., & Chrostowski, S. J. (2020). *Examining eTIMSS Country Differences.* In M. O. Martin, M. von Davier, & I. V. S. Mullis (Eds.), **Methods and Procedures: TIMSS 2019 Technical Report** (Chapter 13, pp. 13.1–13.24). Chestnut Hill, MA: TIMSS & PIRLS International Study Center, Boston College. [Technical Report Portal](https://timssandpirls.bc.edu/timss2019/methods/).
- **Companion Citation**: Fishbein, B., Foy, P., & Yin, L. (2020). *Implementing the TIMSS 2019 Scaling Methodology.* In **Methods and Procedures: TIMSS 2019 Technical Report** (Chapter 12, pp. 12.1–12.146).
- **Primary Benchmarks & Classifications**:
  - Exhibit 12.31: Detailed inventory of 92 calibration items (42 MC, 50 CR) for Grade 4 mathematics.
  - Exhibit 13.1: Complete categorization into 74 equivalent trend items (41 MC, 30 number pad, 3 keyboard) and 18 non-equivalent items (1 MC, 17 CR).
  - Exhibit 13.2: Official U.S. Grade 4 mathematics average percent correct on invariant items: **56.22% (SE 1.18)** on paper bridge vs. **53.94% (SE 0.70)** on eTIMSS (overall $-2.28$ pp difference). Our study adds the critical format decomposition: $-0.72$ pp on MC vs. $-3.78$ pp on CR.

### `SRC-14`: Clerkin et al. (2026) — TIMSS Digital Transition Cross-National Evidence
- **Citation**: Clerkin, A., Verhelst, D., Mahdi, A., Mammadov, S., & McHugh, G. (2026). *Mode effects in the transition to digital testing: Evidence from TIMSS in Ireland, Azerbaijan, Bahrain, and Flanders.* **Large-scale Assessments in Education**, 14, Article 4. DOI: [10.1186/s40536-026-00213-x](https://doi.org/10.1186/s40536-026-00213-x).
- **Substantive Significance**: Analyzes mode differences across diverse educational and linguistic systems using bridge samples, showing that mode friction varies systematically across jurisdictions and item types. Highlights the necessity of granular, within-country item-level decomposition to separate interface friction from construct mastery.

### `SRC-15`: Breuer (2023) — Meta-Analysis of Assessment Response Formats
- **Citation**: Breuer, S. (2023). *Effects of response format on achievement and aptitude assessment results: multi-level random effects meta-analyses.* **Royal Society Open Science**, 10(9), Article 230784. DOI: [10.1098/rsos.230784](https://doi.org/10.1098/rsos.230784).
- **Meta-Analytic Base**: Synthesizes $k = 184$ effect sizes across open-ended versus closed-ended item formats.
- **Theoretical Contribution**: Establishes that constructed-response items place substantially greater generative cognitive load and working memory demands on test-takers relative to recognition-based multiple choice, making them structurally more vulnerable to transcription friction, entry-tool unfamiliarity, and modality-induced cognitive interference.



