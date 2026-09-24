# Kansas City Education Capacity Study (`kc_education_capacity`)

A quantitative investigation into adult instructional capacity, classroom load, and class-size distributions across the 9-county Kansas City bi-state metropolitan area (MARC region).

---

## Central Question

*What are the constraints on a good education, which ones can schools actually change, and which interventions relieve multiple constraints at once?*

Specifically, is insufficient adult instructional capacity the primary unmodeled constraint driving teacher overload—and are reported headline pupil/teacher ratios actively obscuring actual classroom distributions?

---

## Geographic Universe

The study encompasses the official **9-county Mid-America Regional Council (MARC)** Kansas City region:
* **Missouri (5 Counties):** Jackson, Clay, Platte, Cass, Ray
* **Kansas (4 Counties):** Johnson, Wyandotte, Leavenworth, Miami

Schools are classified by objective NCES standardized locale classifications:
* **City** (Urban Core: KCPS, KCKPS, Center, etc.)
* **Suburb** (Inner and Outer Ring Suburbs: Shawnee Mission, Blue Valley, Olathe, North Kansas City, Lee's Summit, Blue Springs, etc.)
* **Town** (Independent peripheral towns)
* **Rural** (Farmland and exurban communities)

---

## Directory Structure

```text
kc_education_capacity/
├── README.md                 # Project overview and instructions
├── research/                 # Theoretical framework, hypotheses, research questions, dictionary
│   ├── questions.md
│   ├── hypotheses.md
│   ├── methodology.md
│   ├── decisions.md
│   └── data_dictionary.md
├── data/
│   ├── raw/                  # Immutable original downloads
│   │   ├── nces/
│   │   ├── missouri/
│   │   └── kansas/
│   ├── interim/              # Intermediate transformations
│   ├── processed/            # Final analysis datasets
│   └── manifest.csv          # Audit ledger of all external downloads (URLs, dates, SHA256)
├── src/                      # Reproducible pipeline code
│   ├── download/             # Ingestion scripts
│   ├── clean/                # Harmonization and universe construction
│   ├── geography/            # Spatial distance and locale metrics
│   └── analysis/             # Statistical models and simulations
├── notebooks/                # Exploratory computational notebooks
│   ├── 01_geography.ipynb
│   ├── 02_baseline_capacity.ipynb
│   ├── 03_longitudinal.ipynb
│   └── 04_class_size.ipynb
├── outputs/                  # Exported artifacts
│   ├── figures/
│   └── tables/
└── requests/                 # Formal state data request documentation
    ├── missouri/
    └── kansas/
```

---

## Current Status: Complete Research Synthesis Available; Tasks 001–005C.2 Concluded

The complete empirical research paper synthesizing this 4-decade investigation is available at:
👉 **[
esearch/paper_kc_education_capacity_synthesis.md](research/paper_kc_education_capacity_synthesis.md)**: *The Capacity Paradox: Why Hiring More Teachers Didn’t Shrink the Classroom (A Four-Decade Investigation into Institutional Staffing, Bell Schedules, and Effective Teacher Workload Across Metropolitan Kansas City)*.

### Key Milestones & Completed Tasks:
- **Phase 1 & 2 (Universe & Baseline Capacity):** Geocoded 691 campuses across 9 MARC counties; audited 2024–25 baseline staffing.
- **Phase 3 (11-Year Longitudinal Panel):** Proved regional teacher FTE expanded **+8.86%** while enrollment was flat (**-0.73%**), reducing pupil/teacher ratio from 14.85:1 to 13.54:1.
- **Phase 3C (State Staffing Reconciliations):** Quantified the **+2.7 ratio point Specialist Denominator Wedge**; proved 88.9% of net Kansas additions were general classroom teachers.
- **Task 004A.1 (CRDC Course-Level Capacity):** Audited 6 biennial waves; documented positive Allocation Wedge (+3.5 to +5.1 in core courses) and suburban comprehensive high school sections of 24–28+.
- **Task 004B.1 (Schedule Regimes & SMSD Case Study):** Formulated Schedule Capacity Identity (phi = 1.17 to 1.40); demonstrated in Shawnee Mission how adding +10.4% teacher FTE bought protected planning periods rather than reducing section size.
- **Task 004C.1 (Student Complexity Panel):** Documented the modern complexity explosion: Section 504 accommodations surged **+93.5%**, total accommodations reached **16.41%**, and chronic absenteeism plateaued at **24.69%**.
- **Task 005A (Jenkins Historical Reconstruction):** Reconstructed Judge Russell G. Clark's 1985 capacity framework (audited exhibits K-58/K-59: 149–154 std/day load; 125 remedial ceiling; Eighth Circuit affirmance of maximums).
- **Task 005B.2 (NTPS Provenance Audit):** Retracted unverified survey distributions; preserved official NCES published state/national benchmarks; classified schedule loads as derived benchmarks.
- **Task 005C.2 (Cross-Era Capacity Benchmarks):** Synthesized 40-year benchmarks across three evidence classes; codified the **Four-Layer Explanatory Architecture** and documented the public transparency boundary.
- **Task 006.1 (Urban Course-Load Scenarios & Bottlenecks):** Reconstructed course-load proxies ($\bar{s}_c = E_c / S_c$) and schedule scenarios across 6 urban high schools; documented gateway bottlenecks (e.g. Wyandotte Algebra I averaging 28.5 across 46 classes vs. naive PTR 20.1:1).
- **Task 006.2 (Department Reconstruction Feasibility Audit):** Established the practical boundary in public artifacts audited; evaluated public personnel directories across 6 pilot campuses and codified the permanent data freeze.

- **Task 001 (Geographic Universe):** Complete. 691 schools across 9 MARC counties established, geocoded, and classified using NCES CCD/EDGE SY 2024–2025.
- **Task 002 & 002B (Baseline Staffing & Capacity):** Complete. School- and LEA-level baseline capacity panels constructed (`kc_school_capacity_2024_2025.csv`, `kc_lea_capacity_2024_2025.csv`), with programmatic LEA geographic coverage metadata, `Operating Regular (NCES)` terminology, FRL missingness analysis, independent Urban Institute ingestion replication, and audited anomalies in `outputs/tables/task002_qa_report.md`.
- **Task 003A & 003A.1 (11-Year Longitudinal Data Construction, Exception Remediation & Audit):** Complete.
  - Ingested and cataloged all 99 raw NCES archives spanning 11 school years (2014–15 through 2024–25).
  - Remediated all historical negative NCES exception codes (`-1` Missing, `-2` Not Applicable, `-9` Suppressed) to `NaN` or explicit Not Applicable representations prior to arithmetic.
  - Implemented dual K–12 teacher FTE derivations (`Total - PreK` audited against component summation), setting missing/suppressed measures to `NaN`.
  - Resolved 2015–16 Kansas discontinuity: identified NCES staff suppression in Olathe and Gardner Edgerton; confirmed reporting ratio of 15.03 on valid LEAs, while classifying Kansas 2015–16 as `insufficient_coverage (< 80%)`.
  - Automated integrity assertions verified **0 negative values** across all numeric analytical variables in all 11 years.
  - Automated baseline parity check confirmed **exact 100% parity (0 discrepancies)** with frozen Task 002B baseline for 2024–25.
  - Constructed primary repeated cross-section school panel (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 records across 730 unique schools), primary repeated cross-section LEA panel (`kc_lea_capacity_long_2014_15_2024_25.csv`, 881 records), secondary balanced panel (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 records across 620 schools), anomaly ledger (`task003a_anomalies.csv`, 409 entries), and reporting coverage table (`task003a1_reporting_coverage.csv`, 66 rows). Full audit documented in `outputs/tables/task003a_qa_report.md`.
- **Task 003B & 003B.1 (Longitudinal Structural Capacity Analysis & Report Integrity):** Complete (`outputs/tables/task003b_analysis_report.md`).
  - **Empirical Pipeline:** Executed `src/analysis/longitudinal_capacity_analysis.py`, generating 7 audited output CSV tables and 7 publication-quality figures in `outputs/figures/`.
  - **Core Findings:**
    - Regional LEA student-weighted pupil/teacher ratio contracted from **14.85 to 13.54** ($−1.31$ students per teacher FTE, $−8.82\%$). Typical regular school median ratio contracted from **15.23 to 13.53** ($−1.70$ students per teacher FTE, $−11.16\%$).
    - Non-causal decomposition establishes that regional K–12 enrollment was flat ($−0.73\%$, $−2,345$ students), while K–12 teacher FTE expanded $+8.88\%$ ($+1,921.91$ FTE) and paraprofessionals expanded $+11.85\%$ ($+565.91$ FTE), proving the capacity expansion was driven by active staff additions rather than enrollment decline.
    - School fixed-effects models on the 620-school balanced panel confirm a within-school trajectory of $\beta = -0.1750\text{ students/FTE per year}$ ($p < 0.0001$; implied 10-year within-school decline of $−1.75$ students/FTE).
    - Grade band divergence: Primary/Elementary schools expanded capacity significantly (within-school $\beta = -0.2152$), whereas High schools saw minimal change ($\beta = -0.0531$).
    - Missouri and Kansas exhibited near-identical starting levels (14.82 vs 14.88) and parallel decade slopes ($-0.1581$ vs $-0.1623$).
  - **Strict Methodological Guardrail:** Staffing ratios measure macro capacity and are never described as class sizes. Hypotheses H1a, H1b, H2, and H3 remain strictly unadjudicated.
- **Phase 3C (Staffing Metric & Allocation Audit):** Complete.
  - **Step 1A (State Staffing Reconciliation Pilot):** Complete (`outputs/tables/task003c_state_replication_pilot_report.md`). Audited 8 benchmark districts across anchor years (2014–15, 2019–20, 2024–25); 17/24 comparisons within 2%, 23/24 within 5% (median difference 1.47%). Confirmed state administrative systems reproduce the macro teacher expansion and identified Kansas's structural separation of Classroom Teachers vs. Other Teachers (SPED/Reading).
  - **Step 1B-KS (Kansas Role Decomposition across 19 Metropolitan USDs):** Complete (`outputs/tables/task003c_kansas_role_decomposition_report.md`). Quantified the **Specialist Denominator Wedge** at **2.66 to 2.81 students per teacher** between classroom ratios (16.86 -> 16.26) and total instructional ratios (14.05 -> 13.60). Proved that in major Johnson County suburbs, both classroom teachers (+8.7%) and specialized teachers (+21.3%) expanded faster than enrollment (+3.2%). At the 19-USD aggregate, 88.9% of net instructional additions were classroom teachers, demonstrating that specialist dilution alone does not explain why core classes remain large.
  - **Workstream 2 (Parallel Specialized Personnel & Non-Teaching Staff):** Complete across all 77 fully regional LEAs (`outputs/tables/task003c_workstream2_regional_staff_need_report.md`). Tracked parallel series showing paraprofessionals (+11.85%), instructional coordinators (+49.74%), counselors (+18.92%), and administrators (+16.62%) expanded faster than enrollment (-0.73%), separating non-teaching organizational support from the teacher denominator.
- **Task 004A & 004A.1 (CRDC Course Capacity Panel, Matched Allocation Wedge & Robustness Audit):** Complete (`outputs/tables/task004_crdc_analysis_report.md` and `outputs/tables/task004a1_crdc_estimand_audit.md`).
  - **Empirical Pipeline:** Executed `src/download/download_historical_crdc.py`, `src/clean/build_ccd_2013_14_capacity.py`, `src/clean/build_crdc_course_panel.py`, and `src/analysis/crdc_capacity_analysis.py` across all 6 public CRDC waves (2013–14 through 2023–24). Produced wide school panel (`kc_crdc_school_course_capacity_2013_14_2023_24.csv`, 3,914 school-years) and long school-course aggregates panel (`kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv`, 31,312 records).
  - **Estimand & Weighting Discipline (Decision 028):** Clarified unit of analysis as school-course average class size ($\frac{\text{Enrolled}}{\text{Classes}}$). Replaced student-weighted exposure terminology with class-weighted course mean. Enforced strict school-to-school matched PTR comparisons ($W_{s,c,t}$ calculated row by row; matched class-weighted PTR computed over contributing schools). Integrated contemporaneous 2013–14 CCD PTR via Urban Institute API.
  - **Four-Specification Sensitivity Testing (`outputs/tables/task004a1_crdc_sensitivity_analysis.csv`):** Proved the positive Allocation Wedge survives across all four specifications (All Valid -> Regular High Schools -> Excl Virtual/Specialized -> Diagnostic Outlier Filter): Core Math unweighted median wedge is consistently **+2.85 to +3.00** pooled across all waves, and in SY 2023–24, unweighted median wedges reach **+3.8 to +5.1 students** (Geometry +5.01, Algebra II +4.26, Chemistry +4.32, Algebra I +3.86) and class-weighted wedges reach **+1.5 to +2.8 students**.
  - **Coverage & Missingness Audit (`outputs/tables/task004a1_crdc_coverage_audit.csv`):** Regular high school class coverage reaches **88.5% to 92.0%** in core courses; demonstrated that missingness is non-random, consisting overwhelmingly of specialized, alternative, and virtual programs.
  - **Calibrated Substantive Findings:** Documented evidence consistent with a curriculum-allocation mechanism (Foundation Core class-weighted means 17.5–18.9 vs. Advanced/Calculus 15.0–17.0). Large suburban comprehensive campuses regularly report core course averages of **24 to 28+ students** (Shawnee Mission North, Shawnee Mission East, Olathe Northwest, Lincoln College Prep), while small-cell observations (Oak Park Calculus, Blue Valley North Algebra I) are flagged for public-use perturbation caveats.
- **Task 004B (The Schedule-Adjusted Capacity Model & Multi-Stage Decomposition):** Complete (`outputs/tables/task004b_schedule_capacity_report.md`, `fig11_schedule_capacity_decomposition.png`, and `outputs/tables/task004b_schedule_decomposition_benchmarks.csv`).
  - **The Schedule Arithmetic Identity:** Formulated the mathematical bridge: $\text{Expected Section Size} = \text{PTR}_{class} \times (P_{student} / P_{teacher}) = \text{PTR}_{class} \times \phi$. Under statutory and contractual planning mandates (Missouri MSIP 6 rule requiring $\ge 250$ min self-directed prep/week; Kansas negotiated agreements capping teaching loads at 5 of 7 periods daily), the schedule multiplier is $\phi = 7/5 = 1.400$ (+40% expansion over classroom ratio).
  - **Multi-Stage Decomposition:** Decomposed the gap between reported PTR and observed core class sizes into: $\Delta_1$ (Specialist Denominator, ~+2.7), $\Delta_2$ (Schedule Multiplier, $+6.5$ to $+8.0$), and $\Delta_3$ (Course Hierarchy Residual, $-1.5$ to $+3.5$).
  - **Empirical Resolution:** Proved that on large suburban high school campuses (Shawnee Mission North, Olathe Northwest, Lincoln Prep), **80% to 98% of the raw 10-to-13 student wedge is explained by specialist categorization ($\Delta_1$) and schedule planning mechanics ($\Delta_2$)**.
  - **Decade Expansion Explained ('5 of 7' Phasing):** Documented that shifting from 6 of 7 to 5 of 7 (e.g. Shawnee Mission Board approval in January 2020) structurally requires a +20% staffing expansion just to keep class sizes constant. Districts hired +8.9% more teachers to **buy back teacher planning time** and reduce daily section preps, not to shrink section rosters.
- **Task 004C (Public KC School Complexity Panel & Compound Workload Model):** Complete (`outputs/tables/task004c_complexity_analysis_report.md`, `fig12_student_complexity_trends.png`, and `data/processed/kc_school_complexity_panel_2015_2024.csv`).
  - **Hypothesis H1b Rejected; Hypothesis H2 Decisively Validated:** Refuted the theory that class headcounts secularly exploded by 5+ students. Proved that classroom headcounts remained anchored at 24–27 students while **instructional complexity per student escalated**:
    - **Section 504 Accommodations Surged +93.5%:** Grew from 6,552 students (2.03%) in 2015–16 to 12,676 students (3.95%) in 2023–24 (reaching 5% to 10% on large suburban campuses).
    - **Total Legally Mandated Accommodations Rose to 16.41%:** Combining IDEA (12.46%) and Section 504, roughly 1 in 6 students carries legally binding individual modifications.
    - **Chronic Absenteeism Tripled:** Surged from 12.90% to 35.14% in federal EDFacts files, introducing intense asynchronous instruction, make-up grading, and truancy documentation friction.
  - **The Compound Workload Formula:** Modeled total teacher load as a function of roster size, accommodation rates, absenteeism friction, administrative mandates, and substitute coverage burden.
- **Research Ladder Track Re-Alignment (Decision 029):**
  - **Track B (District KORA & Sunshine Requests):** **DE-PRIORITIZED / PARKED.** Research strategy prioritizes exhausting all public artifacts (state report cards, open-enrollment capacity filings, board agendas, NTPS surveys) before seeking non-public or internal records.
  - **Track C (Elementary Yearbook Photographic Sampling):** Preserved as an independent, non-administrative photographic validation protocol to be piloted if public elementary class-size report cards leave ambiguities.





