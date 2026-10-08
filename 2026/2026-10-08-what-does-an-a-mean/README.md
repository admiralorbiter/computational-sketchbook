# What Does an "A" Actually Mean? Grades, Learning, and the Incentives Behind Both (`2026-10-08-what-does-an-a-mean`)

An empirical computational observatory investigating grade inflation, institutional accountability incentives, and demonstrated learning in secondary mathematics across the United States, Missouri, and the Kansas City metropolitan area.

---

## 1. Project Overview

We desire schools to maximize student learning, but we evaluate and reward their success using proxy measures—grades, graduation rates, and standardized test scores—that can be systematically improved without necessarily increasing authentic learning.

This computational sketchbook investigates the central research question:
> **When schools are rewarded for better grades and test scores, how much of the resulting improvement represents actual learning, and how much reflects changes in behavior around the measures themselves?**

### Key Conceptual Contributions
1. **The Disconnect**: Identifies the national divergence between rising high school GPAs (3.00 → 3.11 in NAEP HSTS; 3.17 → 3.36 in ACT) and stagnant/declining standardized mathematics performance (NAEP Grade 12 Math 153 → 150; ACT Math 21.0 → 19.9). Documents the **rigorous curriculum paradox**, where advanced-track students saw math scores drop from 188 to 184 despite their GPAs rising from 3.61 to 3.69.
2. **The Chicago Tension**: Reconciles the Allensworth & Clark (2020) University of Chicago CCSR finding that high school GPA is vastly more predictive of six-year college graduation than ACT scores (analyzing 17,753 four-year college entrants from a cohort of 55,084). Degree completion rates ranged from ~20% below 1.5 GPA to ~80% at 3.75+ GPA. Grades capture multi-month behavioral habits, attendance, and work submission that tests miss, explaining how grades can be inflated while remaining profoundly predictive.
3. **The Missouri A–F Accountability Cascade**: Examines the Missouri State Board of Education's September 15, 2026 adoption of a new A–F school rating framework (Executive Order 26-01), tracking how accountability pressure cascades from the state board to district leaders, building principals, classroom teachers, and students.
4. **Kansas City High School Accountability Landscape**: Analyzes 45 Kansas City metropolitan public high schools in the complete 2022 cross-sectional baseline (drawn from a 51-school, 188-record panel across 2022–2025). Finds a positive overall metro correlation between graduation and math achievement ($r = +0.68$) driven by suburban/urban divides, while graduation rates are polarized: 25 of 45 schools (56%) exceed 90%, while 11 schools (24%) fall below 80%. Within schools graduating $\ge 90\%$, Math MPI spans from 300.1 to 457.8 (across the full sample, 277.8 to 457.8). Documents powerful poverty links ($r = -0.73$ to $-0.83$) and qualifies Community Eligibility Provision status alongside USDA Direct Certification.
5. **The Algebra I Signaling Benchmark**: Incorporates Seth Gershenson's (*Grade Inflation in High Schools (2005–2016)*, Fordham Institute, 2018, Figure 2, p. 16; Tyner & Gershenson 2020) statewide North Carolina empirical benchmark (~250,000 students from 2014–2016) showing that 92% of 'A', 64% of 'B' (36% non-proficient), 29% of 'C' (71% non-proficient), and 10% of 'D/F' combined students (90% non-proficient) reach proficiency on the external state end-of-course exam—even though the state exam counted for at least 20% of the final course grade. Contrasted with Gershenson's (2020) *Great Expectations* study examining the positive effects of rigorous grading standards on subsequent learning.
6. **Incentive Duality**: Synthesizes the economics literature (Campbell 1979, Jacob 2005, Dee & Jacob 2011, Allensworth & Clark 2020, Gershenson 2018, 2020, Sanchez & Moore 2022, McElroy 2023) showing that incentives generate authentic instructional focus and strategic gaming simultaneously. Clarifies that McElroy (2023) evaluates educational attainment (high school graduation, college attendance, BA receipt) rather than adult earnings.

---

## 2. Directory Architecture

```text
2026-10-08-what-does-an-a-mean/
├── README.md                           # Observatory overview and navigation
├── docs/
│   ├── research_design.md              # Phase 1: Research questions, model, and hypotheses
│   ├── literature_review.md            # Synthesis of incentive economics, grading, and psychometrics
│   ├── kc_institutional_incentives_design.md # Phase 2: KC institutional incentive research design
│   └── district_policy_audit_protocol.md # Standardized coding protocol for district grading policies
├── sources/
│   ├── source_registry.csv             # Provenance registry of national and Missouri data
│   ├── source_extraction_audit.csv     # Granular audit linking published figures/pages to data fields
│   └── kc_district_policy_registry.csv # Coded policy database for 10 KC LEAs (grading & credit recovery)
├── data/
│   ├── raw/                            # Raw data link documentation
│   └── processed/
│       ├── naep_hsts_trends.csv        # NAEP High School Transcript Study panel (2009–2019)
│       ├── act_gpa_score_trends.csv    # ACT grade inflation panel (2010–2021)
│       ├── uchicago_college_prediction.csv # University of Chicago CCSR empirical parameters
│       ├── gershenson_nc_algebra1_benchmark.csv # NC Algebra I grade vs. EOC proficiency benchmark
│       ├── mo_high_school_panel.parquet # Master Missouri high school accountability panel (2022–2025)
│       └── kc_high_school_panel.csv    # Kansas City metropolitan high school panel
├── src/
│   ├── acquire_national_benchmarks.py  # Generates cleaned national benchmark datasets & audit
│   ├── build_kc_highschool_panel.py    # Merges DESE APR supporting graduation data & school panel
│   ├── generate_figures.py             # Generates publication-quality charts (Figures 1, 2, 3)
│   ├── build_notebook.py               # Generates the Jupyter notebook via nbformat
│   └── analyze_institutional_incentives.py # Phase 2: Decoupling gap analysis and policy matrix
├── notebooks/
│   └── 01_what_does_an_a-mean.ipynb    # Comprehensive interactive research notebook
├── tests/
│   ├── test_data_integrity.py          # Phase 1: Automated verification test suite for data fidelity
│   └── test_institutional_incentives.py # Phase 2: Automated verification of policy & decoupling metrics
└── artifacts/
    ├── essay_what_does_an_a_mean.md    # Phase 1: Long-form essay in teacher-researcher voice
    ├── kc_institutional_incentive_analysis.md # Phase 2: Working paper on KC institutional mechanisms
    ├── figures/
    │   ├── 01_national_gpa_vs_achievement.png # Figure 1: National transcript vs. test disconnect
    │   ├── 02_kc_graduation_vs_math_mpi.png   # Figure 2: KC high schools graduation vs. Math MPI
    │   ├── 03_algebra1_grade_proficiency_gap.png # Figure 3: Algebra I classroom signaling benchmark
    │   └── 04_kc_signaling_decoupling_gap.png # Figure 4: KC Signaling Decoupling landscape & top schools
    └── tables/
        ├── table1_national_trends.csv         # Table 1: National transcript & test trends
        ├── table2_kc_high_schools_2022_2025.csv # Table 2: KC metro high schools benchmark table
        ├── table3_literature_matrix.csv       # Table 3: Comparative incentive literature matrix
        ├── table4_kc_institutional_decoupling_summary.csv # Table 4: School-level decoupling summary (N=45)
        └── table5_district_policy_matrix.csv  # Table 5: District policy & decoupling summary matrix
```

---

## 3. Core Figures

| Figure | Description | Key Insight |
| :--- | :--- | :--- |
| **Figure 1** | **National Transcript vs. Assessment Disconnect (2009–2021)** | High school GPAs rose substantially (+0.11 NAEP, +0.19 ACT adjusted) while 12th-grade NAEP and ACT math scores fell. Advanced-track students saw math scores drop from 188 to 184 despite GPAs rising from 3.61 to 3.69. |
| **Figure 2** | **Graduation vs. Mathematics Achievement in Kansas City High Schools** | 2022 cross-sectional baseline (45 complete schools): positive overall metro correlation ($r = +0.68$), strong correlation with direct certification ($r = -0.83$), and high upper-tier graduation rates alongside large MPI spreads (Van Horn 94.6% grad, MPI 300.1 vs. Park Hill 94.2% grad, MPI 428.4; MPI range in $\ge 90\%$ schools is 300.1 to 457.8). |
| **Figure 3** | **The Algebra I Classroom Signaling Benchmark** | Statewide North Carolina empirical distribution (Gershenson, 2018, Figure 2, p. 16; Tyner & Gershenson, 2020; N ≈ 250,000 from 2014–2016): 92% of 'A' students, 64% of 'B' students (36% non-proficient), 29% of 'C' students (71% non-proficient), and 10% of 'D/F' combined students (90% non-proficient) reach proficiency on external state EOC, despite the EOC counting for $\ge 20\%$ of final course grades. Framed alongside the Missouri open research agenda. |
| **Figure 4** | **The Signaling Decoupling Landscape & Top Decoupled Kansas City High Schools** | Quantifies the school-level gap between graduation rate rank and mathematics MPI rank ($\Delta = \text{Percentile}(\text{Grad}) - \text{Percentile}(\text{Math MPI})$) across 45 high schools. Highlights large positive decoupling outliers (North Kansas City High +63.3 pts, Van Horn +48.9 pts, Ruskin +22.2 pts) alongside district policy regimes (grading floors, Standards-Based Learning, and Edgenuity credit recovery). |

---

## 4. Execution Pipeline

To reproduce the entire analysis from scratch:

```bash
# Phase 1: Compile national benchmark datasets & source extraction audit
python 2026/2026-10-08-what-does-an-a-mean/src/acquire_national_benchmarks.py

# Phase 2: Build the Missouri & Kansas City high school panel
python 2026/2026-10-08-what-does-an-a-mean/src/build_kc_highschool_panel.py

# Phase 3: Generate publication figures and literature tables
python 2026/2026-10-08-what-does-an-a-mean/src/generate_figures.py

# Phase 4: Construct and execute the interactive Jupyter Notebook
python 2026/2026-10-08-what-does-an-a-mean/src/build_notebook.py
jupyter nbconvert --to notebook --execute 2026/2026-10-08-what-does-an-a-mean/notebooks/01_what_does_an_a_mean.ipynb --output 01_what_does_an_a_mean.ipynb

# Phase 5: Execute Kansas City Institutional Incentive Analysis (Phase 2)
python 2026/2026-10-08-what-does-an-a-mean/src/analyze_institutional_incentives.py

# Phase 6: Run full automated test suite (Data Integrity + Institutional Incentives)
pytest 2026/2026-10-08-what-does-an-a-mean/tests/ -v
```

---

## 5. Phase 2: Kansas City Institutional Incentive Study

Phase 2 advances beyond describing the disconnect to evaluating *why* high school course marks and graduation rates decouple from external exam achievement across Greater Kansas City:

1. **Theoretical Mechanism (Campbell's Law)**: High school graduation rate is a high-stakes, heavily weighted component of Missouri MSIP 6 APR scoring. While external standardized test scores (MAP / EOC) cannot be manipulated by school staff, the awarding of course credits is entirely endogenous. High schools rationally optimize on the margin they control: course passing and graduation credit accrual.
2. **The Missouri Regulatory Void**: Unlike North Carolina (which mandated that state EOC exams count for $\ge 20\%$ of final course marks), Missouri statutes mandate administering the Algebra I EOC but **do not require passing the EOC for graduation**, nor do they mandate a minimum weighting of the EOC in course grades. Local boards retain complete statutory authority over course grading.
3. **District Policy Levers**:
   - **Minimum Grading Floors**: Policies establishing 40% or 50% floors (e.g. KCPS 2023–24 40% floor; Hickman Mills 50% quarter floor) compress the failure range from 60 points to 10 points.
   - **Standards-Based Learning (SBL)**: Models (e.g., North Kansas City Schools) that decouple homework and compliance from grades and mandate uncapped reassessments.
   - **Digital Credit Recovery**: Universal adoption of modular platforms (Edgenuity, Apex Learning) with unit pre-testing and 60% mastery cutoffs, compressing semester coursework into 15–30 lab hours.
4. **Key Phase 2 Deliverables**:
   - **Research Design**: [`docs/kc_institutional_incentives_design.md`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-08-what-does-an-a-mean/docs/kc_institutional_incentives_design.md)
   - **Coding Protocol**: [`docs/district_policy_audit_protocol.md`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-08-what-does-an-a-mean/docs/district_policy_audit_protocol.md)
   - **Policy Registry**: [`sources/kc_district_policy_registry.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-08-what-does-an-a-mean/sources/kc_district_policy_registry.csv)
   - **Working Paper**: [`artifacts/kc_institutional_incentive_analysis.md`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-08-what-does-an-a-mean/artifacts/kc_institutional_incentive_analysis.md)
   - **Empirical Visualizations & Matrices**: Figure 4, Table 4, and Table 5.

---

## 6. Forward Research Agenda (Phase 3: Student-Level Microdata)

Phase 3 will pursue FERPA-compliant student-level data matching between Kansas City LEA student information systems, DESE longitudinal testing files, and Missouri DHEWD / community college postsecondary remedial enrollment records to quantify:
1. The exact student-level concordance between Missouri Algebra I teacher grades and EOC scale scores within specific grading policy regimes.
2. The postsecondary remedial placement rate of graduates who earned course credits through online credit recovery versus standard classroom seats.
