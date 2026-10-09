# CRDC Survey Documentation & Variable Mechanics (2021–22)

Reference: [U.S. Department of Education, Office for Civil Rights: 2021–22 Civil Rights Data Collection School Form](https://www.ed.gov/sites/ed/files/about/offices/list/ocr/docs/2021-22-crdc-school-form.pdf)

---

## 1. Critical Definitional Distinction: Offering vs. Participation

In earlier informal policy proposals and casual analyses, the AP indicator is frequently described as:
> *"Does the school offer Advanced Placement courses?"*

A close reading of the official CRDC School Form corrected this assumption:
> **Item 10 (Advanced Placement):**
> *"Are students enrolled in Advanced Placement (AP) courses?"* (`SCH_APENR_IND`)
> 
> **Item 11 (Dual Enrollment / Dual Credit):**
> *"Are students enrolled in dual enrollment or dual credit programs?"* (`SCH_DUAL_IND`)

### Methodological Consequence
Both items measure **reported student participation / enrollment**, not simply institutional course availability in a course catalog:
- If a high school lists AP Calculus in its curriculum guide, but zero students enrolled during the 2021–22 school year, the survey instruction requires reporting `"No"`.
- Conversely, a `"Yes"` confirms that at least one student was actively taking an AP course during the collection window.

This changes which questions we can answer:
- We cannot claim that a school completely forbids or fails to schedule an AP course.
- We **can** claim that an AP-only participation indicator misses schools where students access advanced coursework exclusively through dual enrollment or college credit partnerships.

---

## 2. Variable Dictionary & Clean Coding Crosswalk

| Variable Name | Table / Form Section | Raw Encoding | Clean Python Encoding | Survey Instruction & Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SCH_APENR_IND` | `Advanced Placement.csv` | `"Yes"`, `"No"` | `bool` (`True` if Yes) | Reported student enrollment in at least one AP course during 2021–22. |
| `SCH_APCOURSES` | `Advanced Placement.csv` | Positive integer, or `-9` | `float` (NaN if negative) | Count of different AP courses in which students were enrolled. |
| `SCH_DUAL_IND` | `Dual Enrollment.csv` | `"Yes"`, `"No"` | `bool` (`True` if Yes) | Reported student enrollment in dual enrollment or dual credit courses. |
| `SCH_APCOMPENR_IND` | `Advanced Placement.csv` | `"Yes"`, `"No"`, `"-9"` | `bool` (`True` if Yes, `False` if No) | Reported student enrollment in AP Computer Science (Computer Science A or Computer Science Principles). |
| `SCH_COMPCLASSES_CSCI` | `Computer Science.csv` | Positive integer, or `-9` | `float` (0 if zero/negative) | Count of class sections in computer science offered at the school. |
| `SCH_SCICLASSES_PHYS` | `Physics.csv` | Positive integer, or `-9` | `float` (0 if zero/negative) | Count of class sections in physics offered at the school. |
| `TOT_ENR_M`, `TOT_ENR_F`, `TOT_ENR_X` | `Enrollment.csv` | Non-negative integers | Summed to `crdc_total_enrollment` | School-wide student enrollment by sex (Male, Female, Nonbinary). |

---

## 3. The Negative Exception Code Structure

The CRDC uses negative integer codes to indicate specific non-response or structural skip conditions:
- `-9`: Data not applicable / skipped due to skip logic (e.g., if `SCH_APENR_IND == "No"`, then `SCH_APCOMPENR_IND` is coded `-9`).
- `-5`: Action plan / data missing under approved compliance agreement.
- `-3`: Data omitted by state agency or LEA submission failure.

In `build_panel.py`, skip codes are harmonized:
- For subject-specific participation among non-participating umbrella schools, `-9` correctly represents zero participation in that subcategory.
- In section counts (`SCH_SCICLASSES_PHYS`), missing/skip values are checked against school open status and verified against zero provisions.
