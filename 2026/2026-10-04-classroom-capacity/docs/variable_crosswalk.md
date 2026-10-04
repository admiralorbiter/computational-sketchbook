# Civil Rights Data Collection (CRDC) Longitudinal Variable Crosswalk

This dossier documents the variable-level harmonization protocol connecting course section counts and student enrollments across six waves of the U.S. Department of Education Office for Civil Rights (OCR) Civil Rights Data Collection:
- **2013–14**
- **2015–16**
- **2017–18**
- **2020–21**
- **2021–22**
- **2023–24** (Released August 31, 2026)

---

## 1. Core Estimand & Definition

For any school $s$, secondary course $c$, and academic wave $t$:

$$\widehat{\text{ClassSize}}_{s,c,t} = \frac{\text{CourseEnrollment}_{s,c,t}}{\text{NumberOfClasses}_{s,c,t}}$$

### Epistemic Classification: **School-Course Mean Class Size**
This metric is **never** referred to as "section size." CRDC reports the total aggregated enrollment in a course and the total count of classes/sections of that course taught at that school. It cannot observe within-school variance among sections. If a school reports 90 students across 3 sections, the school-course mean is 30.0, which could reflect three sections of $(30, 30, 30)$ or $(20, 30, 40)$.

---

## 2. Harmonization Architecture by Course

| Course Code | Canonical Course Name | Academic Domain | Stratum | Classes Variable (`NumberOfClasses`) | Enrollment Variables (`CourseEnrollment`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `alg1` | **Algebra I** | Mathematics | Foundation Core | `SCH_MATHCLASSES_ALG` (2015–16 to 2023–24; grades 9–12)<br/>*2013–14:* `SCH_ALGCLASSES_GS0712` | `TOT_ALGENR_GS0910_*` + `TOT_ALGENR_GS1112_*`<br/>*2013–14:* `TOT_ALGENR_GS0708_*` + `TOT_ALGENR_GS0910_*` + `TOT_ALGENR_GS1112_*` |
| `geom` | **Geometry** | Mathematics | Foundation Core | `SCH_MATHCLASSES_GEOM` (2015–16 to 2023–24)<br/>*2013–14:* `SCH_GEOMCLASSES_GS0712` | `TOT_MATHENR_GEOM_*`<br/>*2015–16:* `TOT_GEOM_M` + `TOT_GEOM_F`<br/>*2013–14:* `TOT_GEOMENR_GS0712_*` |
| `alg2` | **Algebra II** | Mathematics | Foundation Core | `SCH_MATHCLASSES_ALG2` (all waves) | `TOT_MATHENR_ALG2_M` + `TOT_MATHENR_ALG2_F` (+ `_X` in 2023–24) |
| `advm` | **Advanced Mathematics** | Mathematics | Advanced / Specialized | `SCH_MATHCLASSES_ADVM` (all waves) | `TOT_MATHENR_ADVM_M` + `TOT_MATHENR_ADVM_F` (+ `_X` in 2023–24) |
| `calc` | **Calculus** | Mathematics | Advanced / Specialized | `SCH_MATHCLASSES_CALC` (all waves) | `TOT_MATHENR_CALC_M` + `TOT_MATHENR_CALC_F` (+ `_X` in 2023–24) |
| `bio` | **Biology** | Natural Science | Foundation Core | `SCH_SCICLASSES_BIOL` (all waves) | `TOT_SCIENR_BIOL_M` + `TOT_SCIENR_BIOL_F` (+ `_X` in 2023–24) |
| `chem` | **Chemistry** | Natural Science | Foundation Core | `SCH_SCICLASSES_CHEM` (all waves) | `TOT_SCIENR_CHEM_M` + `TOT_SCIENR_CHEM_F` (+ `_X` in 2023–24) |
| `phys` | **Physics** | Natural Science | Advanced / Specialized | `SCH_SCICLASSES_PHYS` (all waves) | `TOT_SCIENR_PHYS_M` + `TOT_SCIENR_PHYS_F` (+ `_X` in 2023–24) |

---

## 3. Wave-Specific Technical Nuances and Pitfalls

### 3.1 2013–14 Wave (Modular Excel Spreadsheets)
- **File Structure:** Stored across multiple `.xlsx` workbooks (`05-1 Algebra I`, `05-2 Geometry`, `05-3 Other Math`, `05-4 Biology`, `05-5 Chemistry`, `05-6 Physics`).
- **Algebra I Universe Shift:** In 2013–14, OCR collected class counts for grades 7–12 combined (`SCH_ALGCLASSES_GS0712`). In subsequent waves, grades 7–8 Algebra I was disaggregated into `SCH_ALGCLASSES_GS0708` while `SCH_MATHCLASSES_ALG` became restricted to grades 9–12. To maintain demographic and numerator/denominator congruence in 2013–14, the numerator must sum grades 7–8, 9–10, and 11–12. In 2015–16 through 2023–24, high school Algebra I uses `SCH_MATHCLASSES_ALG` matched to grades 9–12 enrollments.
- **Geometry Universe:** In 2013–14, `SCH_GEOMCLASSES_GS0712` matched `TOT_GEOMENR_GS0712_M` and `TOT_GEOMENR_GS0712_F`.

### 3.2 2015–16 Wave (Single Flat CSV)
- **Geometry Naming Bug:** In raw CRDC 2015–16, the total geometry enrollment variables were named `TOT_GEOM_M` and `TOT_GEOM_F` (dropping the `MATHENR` infix). Failing to capture this results in false zero/missing enrollments.
- **Identifier Handling:** `COMBOKEY` in Excel exports often suffers from floating-point scientific notation corruption (e.g. `2.90001E+11`). The 12-digit NCES ID must be reconstructed by padding `LEAID` to 7 digits and `SCHID` to 5 digits: `str(LEAID).zfill(7) + str(SCHID).zfill(5)`.

### 3.3 2017–18, 2020–21, 2021–22 Waves (Modular CSVs)
- **Course-Level Modularity:** Each subject is packaged as an independent CSV file (`Algebra I.csv`, `Geometry.csv`, etc.).
- **Variable Stability:** Field names are highly stable across these three waves.
- **Pandemic Discontinuity:** The 2020–21 collection occurred during widespread school closures, hybrid instruction, and remote scheduling. It must be treated as an institutional discontinuity rather than an ordinary point on a secular trend.

### 3.4 2023–24 Wave (Released August 31, 2026)
- **Nonbinary Demographic Category:** OCR introduced a third sex reporting category `_X` (Nonbinary). Total course enrollment formulas must incorporate `TOT_*_M + TOT_*_F + TOT_*_X`.

---

## 4. Missing Value and Anomaly Rules

1. **Negative Reserve Codes:** CRDC utilizes negative integers for missing and suppression states:
   - `-9`: Missing / Not reported
   - `-5`: Not applicable / Course not offered
   - `-7`: Not certified
   - `-1`, `-2`, `-3`, `-11`, `-12`: Additional suppression and skip-pattern codes.
   **Strict Rule:** All negative values are converted to `NaN` prior to any aggregation. Under no circumstances may a negative reserve code enter arithmetic.
2. **Zero Denominator:** If `NumberOfClasses == 0` or is missing, `mean_class_size` is mapped to `NaN`.
3. **Plausibility Bounds:** Any calculated school-course mean exceeding 60 students per class is flagged as an anomaly (`flag_extreme_size = TRUE`) for auditing and sensitivity testing.
