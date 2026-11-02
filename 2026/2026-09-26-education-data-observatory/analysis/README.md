# Analysis Directory Index

This directory houses the empirical scripts, data pipelines, visual generators, and research monographs of the Education Data Observatory.

In accordance with Observatory standards:
- **Analyses consume measures and operationalizations; they do not redefine them.**
- **All scripts use relative paths and environment-aware artifact routing.**
- **Historical exploratory scripts are clearly distinguished from canonical frozen generators.**

---

## 1. Canonical Visual Generators
These scripts produce the visual evidence packets stored in [`../dashboard/`](../dashboard/) and linked directly within measure dossiers.

| Script | Target Figures | Associated Measure | Status |
| :--- | :--- | :--- | :--- |
| [`cross-measure/generate_observatory_visuals.py`](cross-measure/generate_observatory_visuals.py) | **Figures 1–3**: Macro PTR vs Class Size, KC 10-Yr Capacity Paradox, Schedule Waterfall Decomposition | `EDU-001` | Active / Frozen |
| [`cross-measure/generate_edu002_visuals.py`](cross-measure/generate_edu002_visuals.py) | **Figures 4–6**: School Size Distribution, Campus vs LEA Gap, 11-Yr Trajectory | `EDU-002` | Active / Frozen |
| [`cross-measure/generate_national_enrollment_visuals.py`](cross-measure/generate_national_enrollment_visuals.py) | **Figures 7–8**: KC vs US Enrollment Indexed, School Size in National Context | `EDU-002` | Active / Frozen |
| [`cross-measure/generate_task003d_visuals.py`](cross-measure/generate_task003d_visuals.py) | **Figures 9–11**: Post-2020 Recovery Typology, Kindergarten Pipeline Indicator, School Scale vs Curricular Breadth | `EDU-002` | Active / Frozen |
| [`cross-measure/generate_edu003_visuals.py`](cross-measure/generate_edu003_visuals.py) | **Figures 12–14**: Longitudinal Teacher Trajectory (KC vs US), Fixed-Plant Staffing Stickiness, Secondary Staffing Wedge | `EDU-003` | Active / Frozen |

---

## 2. Authoritative Machine-Readable Claims Ledger
All headline empirical findings across frozen measures are formally owned by the claims ledger:

- **[`results/claims.csv`](results/claims.csv):** Authoritative machine-readable ledger containing 20 cryptographically audited empirical claims spanning `EDU-001`, `EDU-002`, and `EDU-003`. Every claim specifies its measure ID, claim class, producing analysis script, source artifact IDs, universe ID, temporal reference window, estimand description, start value, end value, absolute change, percent change, percent basis, support N, and epistemic status (`audited_fact`, `descriptive_fact`, `descriptive_association`, `empirical_wedge`).
- **Generator Script:** [`../scripts/generate_claims_ledger.py`](../scripts/generate_claims_ledger.py) computes and populates `results/claims.csv` directly from authoritative upstream data panels.

---

## 3. Active Canonical Audit Scripts
Scripts used to mathematically audit, calculate sensitivity specifications, and verify claims across administrative files.

| Script | Focus Area | Key Outputs | Status |
| :--- | :--- | :--- | :--- |
| [`cross-measure/explore_edu001_ptr.py`](cross-measure/explore_edu001_ptr.py) | `EDU-001` Empirical Audit | Canonical audit script computing balanced 75 PTR compression ($14.85 \to 13.55$), dynamic regional trajectory ($14.85 \to 13.54$), 28-LEA staffing stickiness ($14.02 \to 13.34$), campus vs LEA allocation gap ($-0.24$, $-1.74\%$), and regular school campus distribution ($N=616$). | Active / Frozen |
| [`cross-measure/task004a_empirical_audit.py`](cross-measure/task004a_empirical_audit.py) | `EDU-003` Mathematical Audit | Verifies declining district sensitivity specifications (Spec 1, 2, 3), audits staff-category historical coverage matrix, calculates matched high school calculus offerings ($67.9\% \to 35.7\%$), and evaluates charter net expansion ratios. | Active / Frozen |

---

## 4. Historical Exploratory & Step Scripts
These scripts document the step-by-step epistemic progression of earlier tasks. Their findings have been superseded or formalized into canonical dossiers and memos.

| Script | Originating Task | Epistemic Role | Current Status |
| :--- | :--- | :--- | :--- |
| [`cross-measure/explore_edu002_enrollment.py`](cross-measure/explore_edu002_enrollment.py) | Task 002 | Initial exploration of CCD school and LEA enrollment fields. | Superseded by Task 003C/003E. |
| [`cross-measure/explore_task003c.py`](cross-measure/explore_task003c.py) | Task 003C | Uncovered the LEA-school reconciliation gap and separated dynamic from balanced universes. | Formalized in `EDU-002` dossier. |
| [`cross-measure/task003d_investigation.py`](cross-measure/task003d_investigation.py) | Task 003D | Explored suburban growth, kindergarten drops, and course offering distributions. | Audited in Task 003E / Task 004A. |
| [`cross-measure/task003e_audit.py`](cross-measure/task003e_audit.py) | Task 003E | Audited great-circle centroid shift ($0.32$ miles), facility continuity ($25$ of $28$ identical), and complexity tables. | Formalized in frozen `EDU-002` dossier. |
| [`cross-measure/explore_edu003_teachers.py`](cross-measure/explore_edu003_teachers.py) | Task 004 | Initial exploratory run on teacher FTE, fixed plant stickiness, and secondary staffing wedge. | Audited and corrected in Task 004A. |

---

## 5. Comprehensive Research Monographs & Memos

- **[`cross-measure/enrollment_exploratory_memo.md`](cross-measure/enrollment_exploratory_memo.md):** 11-Year Empirical Analysis of Student Enrollment, Geographic Sorting, and Institutional Demography in the Kansas City Metropolitan Area (`EDU-002`). *Status: Audited & Frozen.*
- **[`cross-measure/teacher_capacity_exploratory_memo.md`](cross-measure/teacher_capacity_exploratory_memo.md):** Instructional Labor Stock, Fixed-Plant Stickiness, and the Secondary Staffing Wedge (`EDU-003`). *Status: Audited & Reconciled (Task 004A).*
