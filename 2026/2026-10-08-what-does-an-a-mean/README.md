# What Does an "A" Actually Mean? Grades, Learning, and the Incentives Behind Both (`2026-10-08-what-does-an-a-mean`)

An empirical computational observatory investigating grade inflation, institutional accountability incentives, and demonstrated learning in secondary mathematics across the United States, Missouri, and the Kansas City metropolitan area.

---

## 1. Project Overview

We desire schools to maximize student learning, but we evaluate and reward their success using proxy measures—grades, graduation rates, and standardized test scores—that can be systematically improved without necessarily increasing authentic learning.

This computational sketchbook investigates the central research question:
> **When schools are rewarded for better grades and test scores, how much of the resulting improvement represents actual learning, and how much reflects changes in behavior around the measures themselves?**

### Key Conceptual Contributions
1. **The Disconnect**: Identifies the national divergence between rising high school GPAs (3.00 → 3.11 in NAEP HSTS; 3.17 → 3.36 in ACT) and stagnant/declining standardized mathematics performance (NAEP Grade 12 Math 153 → 150; ACT Math 21.0 → 19.9). Documents the **rigorous curriculum paradox**, where advanced-track students saw math scores drop from 188 to 184 despite their GPAs rising from 3.61 to 3.69.
2. **The Chicago Tension**: Reconciles the Allensworth & Clark (2020) University of Chicago CCSR finding that high school GPA is 5x more predictive of college graduation than ACT scores. Grades capture multi-month behavioral habits, attendance, and work submission that tests miss, explaining how grades can be inflated while remaining profoundly predictive.
3. **The Missouri A–F Accountability Cascade**: Examines the Missouri State Board of Education's September 15, 2026 adoption of a new A–F school rating framework (Executive Order 26-01), tracking how accountability pressure cascades from the state board to district leaders, building principals, classroom teachers, and students.
4. **Kansas City High School Credential Compression**: Analyzes Missouri public high schools, demonstrating that suburban and inner-ring high schools cluster in an upper graduation band of 88%–98% across a massive mathematics achievement gradient (MPI 278 to 458).
5. **The Algebra I Signaling Gap**: Unpacks what passing Algebra I certifies across low-poverty suburban schools versus high-poverty urban schools facing intense failure-rate scrutiny.
6. **Incentive Duality**: Synthesizes the economics literature (Campbell 1979, Jacob 2005, Dee & Jacob 2011, McElroy 2023) showing that incentives generate authentic instructional focus and strategic gaming simultaneously.

---

## 2. Directory Architecture

```text
2026-10-08-what-does-an-a-mean/
├── README.md                           # Observatory overview and navigation
├── docs/
│   ├── research_design.md              # Research questions, theoretical model, and hypotheses
│   └── literature_review.md            # Synthesis of incentive economics, grading, and psychometrics
├── sources/
│   └── source_registry.csv             # Provenance registry of national and Missouri data
├── data/
│   ├── raw/                            # Raw data link documentation
│   └── processed/
│       ├── naep_hsts_trends.csv        # NAEP High School Transcript Study panel (2009–2019)
│       ├── act_gpa_score_trends.csv    # ACT grade inflation panel (2010–2021)
│       ├── uchicago_college_prediction.csv # University of Chicago CCSR empirical parameters
│       ├── mo_high_school_panel.parquet # Master Missouri high school accountability panel (2022–2025)
│       └── kc_high_school_panel.csv    # Kansas City metropolitan high school panel
├── src/
│   ├── acquire_national_benchmarks.py  # Generates cleaned national benchmark datasets
│   ├── build_kc_highschool_panel.py    # Merges DESE APR supporting graduation data & school panel
│   ├── generate_figures.py             # Generates publication-quality charts (Figures 1, 2, 3)
│   └── build_notebook.py               # Generates the Jupyter notebook via nbformat
├── notebooks/
│   └── 01_what_does_an_a_mean.ipynb    # Comprehensive interactive research notebook
└── artifacts/
    ├── essay_what_does_an_a_mean.md    # Complete long-form essay written in teacher-researcher voice
    ├── figures/
    │   ├── 01_national_gpa_vs_achievement.png # Figure 1: National transcript vs. test disconnect
    │   ├── 02_kc_graduation_vs_math_mpi.png   # Figure 2: KC high schools graduation vs. Math MPI
    │   └── 03_algebra1_grade_proficiency_gap.png # Figure 3: Algebra I classroom signaling gap
    └── tables/
        ├── table1_national_trends.csv         # Table 1: National transcript & test trends
        ├── table2_kc_high_schools_2022_2025.csv # Table 2: KC metro high schools benchmark table
        └── table3_literature_matrix.csv       # Table 3: Comparative incentive literature matrix
```

---

## 3. Core Figures

| Figure | Description | Key Insight |
| :--- | :--- | :--- |
| **Figure 1** | **National Transcript vs. Assessment Disconnect (2009–2021)** | High school GPAs rose substantially (+0.11 NAEP, +0.19 ACT) while 12th-grade NAEP and ACT math scores fell. Advanced-track students saw math scores drop from 188 to 184 despite GPAs rising from 3.61 to 3.69. |
| **Figure 2** | **Credential Compression in Greater Kansas City High Schools** | High school graduation rates cluster between 88% and 98% across suburban and inner-ring districts, while measured Algebra I performance spans an index from 278 to 458. Van Horn HS (94.6% grad, MPI 300.1) matches Park Hill HS (94.2% grad, MPI 428.4). |
| **Figure 3** | **The Algebra I Classroom Signaling Gap** | In suburban high schools, 90% of 'A' students and 74% of 'B' students score Proficient or Advanced on state EOCs. In high-poverty, high-stakes schools, 64% of 'B' students and 84%–94% of 'C'/'D' students score Below Basic or Basic. |

---

## 4. Execution Pipeline

To reproduce the entire analysis from scratch:

```bash
# Phase 1: Compile national benchmark datasets
python 2026/2026-10-08-what-does-an-a-mean/src/acquire_national_benchmarks.py

# Phase 2: Build the Missouri & Kansas City high school panel
python 2026/2026-10-08-what-does-an-a-mean/src/build_kc_highschool_panel.py

# Phase 3: Generate publication figures and literature tables
python 2026/2026-10-08-what-does-an-a-mean/src/generate_figures.py

# Phase 4: Construct and execute the interactive Jupyter Notebook
python 2026/2026-10-08-what-does-an-a-mean/src/build_notebook.py
jupyter nbconvert --to notebook --execute 2026/2026-10-08-what-does-an-a-mean/notebooks/01_what_does_an_a_mean.ipynb --output 01_what_does_an_a_mean.ipynb
```
