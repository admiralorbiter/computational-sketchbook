# CRDC Survey Documentation & Administrative Code Mechanics (2021–22)

References:
1. [U.S. Department of Education, Office for Civil Rights: 2021–22 Civil Rights Data Collection School Form](https://www.ed.gov/sites/ed/files/about/offices/list/ocr/docs/2021-22-crdc-school-form.pdf)
2. [CRDC 2021–22 Public-Use Data File User's Manual](https://topofire.dbs.umt.edu/public_data/federal_public_datasets/Civil%20Rights%20Data%20Collection/2021-2022/Data%20File%20Users%20Manual%202021-22.pdf)

---

## 1. Definitional Distinction: Course Offering vs. Student Participation

In policy discussions, AP survey indicators are frequently cited as measuring whether a school *"offers Advanced Placement courses"*.

A strict reading of the official CRDC School Form establishes that both AP and Dual Enrollment items measure **reported student participation / enrollment**:
> **Item 10 (Advanced Placement):**
> *"Are students enrolled in Advanced Placement (AP) courses?"* (`SCH_APENR_IND`)
> 
> **Item 11 (Dual Enrollment / Dual Credit):**
> *"Are students enrolled in dual enrollment or dual credit programs?"* (`SCH_DUAL_IND`)

### Methodological Consequence
- A `"No"` response indicates that zero students were reported enrolled during the 2021–22 school year. It does not establish that the course was prohibited, nor does it prove that the course was absent from the school's master curriculum catalog.
- Conversely, a `"Yes"` confirms active student participation in at least one course section during the collection window.
- In Study 2, `SCH_APCOMPENR_IND == 'No'` indicates that **zero students participated in AP Computer Science**; it does not prove the school lacked a course listing.
- Similarly, reporting neither AP nor Dual Enrollment (8 schools, 2.6%) does not establish an absence of all college-level coursework; schools may offer International Baccalaureate (IB), early college high school arrangements, career and technical education (CTE) articulation credits, or local college partnerships not captured under these survey items.

---

## 2. CRDC Administrative Code Structure & Nonnegative Summation

The CRDC public-use data files use negative integers to represent specific administrative skip patterns, non-collection, or data protections:

| Code | Official Definition | Mechanical Treatment in Analysis |
| :---: | :--- | :--- |
| **`-9`** | **Not Applicable / Skipped** | The question was skipped according to survey logic, or the data item was not collected / not applicable for the reporting entity. Treated as 0 when summing released counts. |
| **`-12`** | **Suppressed for Privacy Protections** | The true cell count was suppressed by OCR to prevent student re-identification. **Must remain unresolved**, not silently converted to zero. |
| **`-5`** | **Action Plan Missingness** | Data item missing under an approved state/LEA compliance agreement. |
| **`-3`** | **Agency Non-Response** | Data omitted due to state reporting failure. |

### The Nonbinary Enrollment Field (`TOT_ENR_X`)
In the 2021–22 collection, OCR introduced nonbinary student counts (`TOT_ENR_X` alongside `TOT_ENR_M` and `TOT_ENR_F`):
- Across the **307 baseline high schools**, the `TOT_ENR_X` field contains:
  - **304 instances of `-9`**: The reporting LEA did not collect or report nonbinary student counts.
  - **1 instance of `-12`**: Suppressed for privacy protection at *Central High School* in Kansas City Public Schools (`291640000840`).
  - **2 instances of positive counts**: 3 students at *Lincoln College Prep* (`291640000844`) and 4 students at *Perryville Sr. High* (`292453002387`).
- **Critical Accounting Fix**: Summing columns naively (`M + F + X`) subtracts 9 or 12 students from school headcounts. In `build_panel.py`, negative codes are audited and clipped at zero to produce `crdc_released_enrollment`.
- **Provisional Nature**: Because the single suppressed value remains unresolved in public data, total enrollment figures (228,637 across 307 schools; 41,616 at zero-physics schools) represent **provisional calculations from released counts**, not fully recovered population totals.

---

## 3. Variable Dictionary & Clean Coding Crosswalk

| Variable Name | Table / File | Raw Encoding | Clean Python Encoding | Survey Instruction & Audit Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SCH_APENR_IND` | `Advanced Placement.csv` | `"Yes"`, `"No"` | `bool` (`True` if Yes) | Reported student enrollment in at least one AP course during 2021–22. |
| `SCH_APCOURSES` | `Advanced Placement.csv` | Positive integer, or `-9` | `float` (NaN if negative) | Count of different AP courses with reported enrollment. |
| `SCH_DUAL_IND` | `Dual Enrollment.csv` | `"Yes"`, `"No"` | `bool` (`True` if Yes) | Reported student enrollment in dual enrollment or dual credit courses. |
| `SCH_APCOMPENR_IND` | `Advanced Placement.csv` | `"Yes"`, `"No"`, `"-9"` | `bool` (`True` if Yes, `False` if No) | Reported student enrollment in AP Computer Science (A or Principles). Coded `-9` if school reports no AP. |
| `SCH_COMPCLASSES_CSCI` | `Computer Science.csv` | Positive integer, or `-9` | `float` (0 if zero/negative) | Count of class sections in computer science offered at the school. |
| `SCH_SCICLASSES_PHYS` | `Physics.csv` | Positive integer, or `-9` | `float` (0 if zero/negative) | Count of class sections in physics offered at the school. |
| `TOT_ENR_M`, `TOT_ENR_F` | `Enrollment.csv` | Non-negative integers | Summed to released count | School student headcount by sex. |
| `TOT_ENR_X` | `Enrollment.csv` | Integers, `-9`, or `-12` | Nonnegative clipped; flagged | Nonbinary student headcount; 304 skipped (-9), 1 suppressed (-12). |
