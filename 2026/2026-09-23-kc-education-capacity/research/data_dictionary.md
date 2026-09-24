# Data Dictionary: Kansas City School Universe

| Variable | Type | Source | Description / Valid Values |
| :--- | :--- | :--- | :--- |
| `nces_school_id` | String(12) | NCES CCD / EDGE | Unique 12-digit NCES school identifier (`NCESSCH`). Primary key. |
| `nces_lea_id` | String(7) | NCES CCD / EDGE | Unique 7-digit NCES Local Education Agency identifier (`LEAID`). |
| `school_name` | String | NCES CCD / EDGE | Official name of the school building. |
| `district_name` | String | NCES CCD | Name of the local education agency / district. |
| `state` | String(2) | NCES CCD / EDGE | State abbreviation (`MO` or `KS`). |
| `county_name` | String | NCES EDGE | County name where the school is physically located. |
| `county_fips` | String(5) | NCES EDGE | 5-digit FIPS code of the physical county (`29095`, `20091`, etc.). |
| `street_address` | String | NCES CCD / EDGE | Reported physical street address. |
| `city` | String | NCES CCD / EDGE | Reported physical city. |
| `zip_code` | String(5) | NCES CCD / EDGE | Reported 5-digit ZIP code. |
| `latitude` | Float | NCES EDGE | Geocoded latitude coordinate of the school location. |
| `longitude` | Float | NCES EDGE | Geocoded longitude coordinate of the school location. |
| `distance_downtown_kc_miles` | Float | Derived | Haversine distance in statute miles from Kansas City Hall ($39.1027^\circ \text{N}, -94.5779^\circ \text{W}$). |
| `lowest_grade` | String | NCES CCD | Lowest grade offered (e.g., `PK`, `KG`, `01`, `09`). |
| `highest_grade` | String | NCES CCD | Highest grade offered (e.g., `05`, `08`, `12`). |
| `school_level` | String | NCES CCD | NCES assigned level: `Primary`, `Middle`, `High`, `Other`. |
| `school_type` | Integer | NCES CCD | 1=Regular, 2=Special Education, 3=Vocational, 4=Alternative/Other. |
| `school_type_desc`| String | NCES CCD | Text description of `school_type`. |
| `charter_status` | String | NCES CCD | Charter indicator (`Yes`, `No`). |
| `operational_status` | Integer | NCES CCD | Operational status code: 1=Open, 2=Closed, 3=New, 4=Added, 5=Changed Agency, 6=Inactive, 7=Future, 8=Reopened. |
| `operational_status_desc` | String | NCES CCD | Text description of operational status. |
| `virtual_status` | String | NCES CCD Char. | Virtual instruction flag: `NOTVIRT` (No virtual instruction), `FULLVIRT` (Exclusively virtual), `FACEVIRT` (Primarily virtual), `SUPPVIRT` (Supplemental). |
| `virtual_status_desc` | String | NCES CCD Char. | Full descriptive text of virtual status. |
| `locale_code` | String(2) | NCES EDGE | Official NCES 2-digit locale code (11-43). |
| `locale_desc` | String | NCES EDGE / Standard | Text description of locale (e.g., `City: Large`, `Suburb: Large`, `Rural: Fringe`). |
| `locale_group` | String | Derived | Standard 4-category classification: `City`, `Suburb`, `Town`, or `Rural`. |
| `cbsa_code` | String(5) | NCES EDGE | Core Based Statistical Area code (e.g., `28140` for Kansas City, MO-KS). |
| `cbsa_name` | String | NCES EDGE | Core Based Statistical Area name. |
| `csa_code` | String(3) | NCES EDGE | Combined Statistical Area code (e.g., `312` for Kansas City-Overland Park-Kansas City, MO-KS). |
| `csa_name` | String | NCES EDGE | Combined Statistical Area name. |
| `is_charter` | Boolean | Derived | `True` if `charter_status == 'Yes'`. |
| `is_virtual` | Boolean | Derived | `True` if school offers exclusively or primarily virtual instruction. |
| `is_regular` | Boolean | Derived | `True` if `school_type == '1'` (Regular School). |
| `is_special_ed` | Boolean | Derived | `True` if `school_type == '2'` (Special Education School). |
| `is_vocational` | Boolean | Derived | `True` if `school_type == '3'` (Career and Technical School). |
| `is_alternative` | Boolean | Derived | `True` if `school_type == '4'` (Alternative School). |
| `is_operating` | Boolean | Derived | `True` for schools actively operating in the survey year (status 1=Open, 3=New, 4=Added, 5=Changed Agency, 8=Reopened). `False` for status 2=Closed, 6=Inactive, 7=Future. |
| `is_continuing_school` | Boolean | Derived | `True` strictly for continuing open schools (`operational_status == '1'`). |
| `school_year` | String | NCES CCD | School year of the record (e.g., `2024-2025`). |

## School-Level Baseline Capacity Metrics (`kc_school_capacity_2024_2025.csv`)

| Variable | Type | Source | Description / Valid Values |
| :--- | :--- | :--- | :--- |
| `enrollment_total` | Integer | NCES CCD FS052 | Total student membership count (Education Unit Total). |
| `enrollment_pk` | Integer | NCES CCD FS052 | Pre-Kindergarten student enrollment count. |
| `enrollment_k12` | Integer | Derived | Total K–12 enrollment (`enrollment_total - enrollment_pk`). |
| `enrollment_kg` | Integer | NCES CCD FS052 | Kindergarten student enrollment count. |
| `has_pre_k` | Boolean | Derived | `True` if `enrollment_pk > 0`. |
| `is_standalone_pk` | Boolean | Derived | `True` if school serves exclusively Pre-K (`lowest_grade == 'PK'` and `highest_grade == 'PK'`). |
| `classroom_teacher_fte` | Float | NCES CCD FS059 | Full-time equivalent classroom teachers reported for the school building (`TEACHERS`). |
| `students_per_classroom_teacher_fte_allgrades` | Float | Derived | Structural capacity ratio: $\frac{\text{enrollment\_total}}{\text{classroom\_teacher\_fte}}$. **Strict Guardrail:** Represents structural staffing ratio, NOT observed class size. Set to `NaN` if `classroom_teacher_fte == 0`. |
| `free_lunch_eligible` | Float | NCES CCD FS033 | Number of students eligible for free lunch under NSLP. |
| `reduced_lunch_eligible` | Float | NCES CCD FS033 | Number of students eligible for reduced-price lunch under NSLP. |
| `frl_eligible` | Float | NCES CCD FS033 | Total Free and Reduced-Price Lunch eligible students. |
| `frl_rate` | Float | Derived | Free/reduced lunch rate: $\frac{\text{frl\_eligible}}{\text{enrollment\_total}}$. |
| `direct_certification` | Float | NCES CCD FS033 | Number of students directly certified for free lunch through SNAP/TANF. |
| `frl_observed` | Boolean | Derived | `True` if free/reduced lunch eligibility count is reported in CCD FS033; `False` if unobserved/missing. |
| `analytical_stratum` | String | Derived | Mutually exclusive analytical category: `Operating Regular (NCES)`, `Standalone Early Childhood`, `Exclusively Virtual`, `Special Education`, `Alternative`, `Career and Technical`, `Non-Operating`. **Note:** `Operating Regular (NCES)` indicates NCES `school_type == 1`, but is not synonymous with traditional neighborhood schools as it includes several specialized, custody, and day-treatment programs. |

## LEA-Level Baseline Capacity Metrics (`kc_lea_capacity_2024_2025.csv`)

| Variable | Type | Source | Description / Valid Values |
| :--- | :--- | :--- | :--- |
| `nces_lea_id` | String(7) | NCES CCD | Unique 7-digit NCES Local Education Agency identifier (`LEAID`). |
| `district_name` | String | NCES CCD | Name of the local education agency / district. |
| `state` | String(2) | NCES CCD | State postal abbreviation (`MO` or `KS`). |
| `county_primary` | String | Derived | Primary modal county of operating schools in the district. |
| `operating_schools_count` | Integer | Derived | Number of operating schools in the district located within the 9 MARC counties. |
| `regular_schools_count` | Integer | Derived | Number of operating regular schools in the district located within the 9 MARC counties. |
| `enrollment_total` | Integer | NCES CCD FS052 | District total student membership (Education Unit Total). |
| `enrollment_pk` | Integer | NCES CCD FS052 | District Pre-Kindergarten student enrollment. |
| `enrollment_k12` | Integer | Derived | District K–12 student enrollment (`enrollment_total - enrollment_pk`). |
| `enrollment_kg` | Integer | NCES CCD FS052 | District Kindergarten enrollment. |
| `enrollment_elem` | Integer | NCES CCD FS052 | District Elementary enrollment (Grades 1–5 sum). |
| `enrollment_middle` | Integer | NCES CCD FS052 | District Middle School enrollment (Grades 6–8 sum). |
| `enrollment_high` | Integer | NCES CCD FS052 | District High School enrollment (Grades 9–12 sum). |
| `enrollment_ungraded` | Integer | NCES CCD FS052 | District Ungraded student count. |
| `teachers_prek_fte` | Float | NCES CCD FS059 | Pre-kindergarten teachers FTE. |
| `teachers_kindergarten_fte` | Float | NCES CCD FS059 | Kindergarten teachers FTE. |
| `teachers_elementary_fte` | Float | NCES CCD FS059 | Elementary teachers FTE. |
| `teachers_secondary_fte` | Float | NCES CCD FS059 | Secondary teachers FTE. |
| `teachers_ungraded_fte` | Float | NCES CCD FS059 | Ungraded teachers FTE. |
| `teachers_total_reported_fte`| Float | NCES CCD FS059 | Total reported classroom teachers FTE in CCD LEA staff file. |
| `teachers_k12_fte` | Float | Derived | K–12 teachers FTE: Kindergarten + Elementary + Secondary + Ungraded teachers (excludes Pre-K). |
| `teachers_sum_diff_reported` | Float | Derived | Internal consistency check: $\text{teachers\_total\_reported} - (\text{teachers\_k12} + \text{teachers\_prek})$. Equals $0.00$ across all 79 LEAs. |
| `paraprofessionals_fte` | Float | NCES CCD FS059 | Paraprofessionals / instructional aides FTE. |
| `instructional_coordinators_fte`| Float | NCES CCD FS059 | Instructional coordinators and supervisors FTE. |
| `counselors_fte` | Float | NCES CCD FS059 | Total guidance counselors FTE (elementary, secondary, and unassigned). |
| `psychologists_fte` | Float | NCES CCD FS059 | School psychologists FTE. |
| `student_support_staff_fte` | Float | NCES CCD FS059 | Student support services staff FTE (without psychology). |
| `librarians_fte` | Float | NCES CCD FS059 | Librarians / media specialists FTE. |
| `school_administrators_fte` | Float | NCES CCD FS059 | School building administrators (principals, assistant principals) FTE. |
| `school_admin_support_fte` | Float | NCES CCD FS059 | School administrative support staff FTE. |
| `lea_administrators_fte` | Float | NCES CCD FS059 | District / central office administrators (superintendents, directors) FTE. |
| `lea_admin_support_fte` | Float | NCES CCD FS059 | District administrative support staff FTE. |
| `other_support_staff_fte` | Float | NCES CCD FS059 | All other district support staff FTE. |
| `total_staff_fte` | Float | NCES CCD FS059 | Total district staff FTE (Education Unit Total). |
| `idea_students` | Float | EDFacts FS002 | Special education students with IEPs under IDEA. *Pending federal 2024–25 release (`NaN`).* |
| `sped_teacher_fte` | Float | EDFacts FS070 | Special education teachers FTE. *Pending federal 2024–25 release (`NaN`).* |
| `sped_paraprofessional_fte` | Float | EDFacts FS112 | Special education paraprofessionals FTE. *Pending federal 2024–25 release (`NaN`).* |
| `english_learner_students` | Float | EDFacts FS141 | English Learner (EL) student count. *Pending federal 2024–25 release (`NaN`).* |
| `title3_teacher_count` | Float | EDFacts FS067 | Title III English Learner teachers. *Pending federal 2024–25 release (`NaN`).* |
| `idea_students_per_sped_teacher_fte` | Float | Derived | Caseload ratio of IDEA students to SPED teachers. *Pending federal 2024–25 release (`NaN`).* |
| `students_per_teacher_fte_k12` | Float | Derived | Matched K–12 structural capacity ratio: $\frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte}}$. |
| `students_per_teacher_para_fte_k12` | Float | Derived | Adult instructional capacity ratio: $\frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte} + \text{paraprofessionals\_fte}}$. |
| `teachers_k12_per_1000` | Float | Derived | K–12 classroom teachers per 1,000 K–12 students. |
| `paraprofessionals_per_1000` | Float | Derived | Paraprofessionals per 1,000 K–12 students. |
| `counselors_per_1000` | Float | Derived | Counselors per 1,000 K–12 students. |
| `psychologists_per_1000` | Float | Derived | Psychologists per 1,000 K–12 students. |
| `student_support_per_1000` | Float | Derived | Student support staff per 1,000 K–12 students. |
| `coordinators_per_1000` | Float | Derived | Instructional coordinators per 1,000 K–12 students. |
| `school_administrators_per_1000`| Float | Derived | School administrators per 1,000 K–12 students. |
| `lea_total_operating_schools_national` | Integer | NCES CCD FS029 | Total operating schools operated by the LEA nationally. |
| `lea_operating_schools_in_region` | Integer | Derived | Operating schools operated by the LEA located physically within the 9 MARC counties. |
| `lea_operating_schools_outside_region` | Integer | Derived | Operating schools operated by the LEA located outside the 9 MARC counties (`national - in_region`). |
| `lea_geographic_coverage_share` | Float | Derived | Regional school coverage share: $\frac{\text{lea\_operating\_schools\_in\_region}}{\text{lea\_total\_operating\_schools\_national}}$. |
| `lea_fully_within_region` | Boolean | Derived | `True` if `lea_operating_schools_outside_region == 0`. `False` if LEA operates schools outside the 9-county region (e.g. MO DYS, MSSD). Staffing/enrollment for `False` LEAs reflect statewide totals. |
| `school_year` | String | NCES CCD | School year of the record (`2024-2025`). |

---

### 3. Longitudinal Panel & Transition Variables

These attributes appear in the primary repeated cross-sections panel (`kc_school_capacity_long_2014_15_2024_25.csv`) and the secondary balanced panel (`kc_school_balanced_panel_2014_15_2024_25.csv`):

| Field Name | Type | Source | Description |
| :--- | :--- | :--- | :--- |
| `locale_code_year` | String | NCES EDGE | 2-digit NCES locale code (11–43) active in the observed school year. Preserves historical classification without retroactive backfilling. |
| `locale_desc_year` | String | Derived | Standard text description of active annual locale code (e.g. `City: Large`, `Suburb: Midsize`). |
| `locale_group_year` | String | Derived | 4-category broad locale grouping in observed year (`City`, `Suburb`, `Town`, `Rural`). |
| `years_observed_count` | Integer | Derived | Total number of annual cross-sections (out of 11) in which the NCES school ID is observed in the regional universe. |
| `years_operating_count` | Integer | Derived | Total number of annual cross-sections (out of 11) in which the school was observed with an active operating status (`is_operating == True`). |
| `first_observed_school_year` | String | Derived | First school year in which the school ID appeared in the regional frame (e.g. `2014-2015`). |
| `last_observed_school_year` | String | Derived | Most recent school year in which the school ID appeared in the regional frame (e.g. `2024-2025`). |
| `balanced_panel_eligible` | Boolean | Derived | `True` iff school is observed in all 11 school years and is operating in all 11 school years (`years_observed_count == 11 and years_operating_count == 11`). 620 schools meet this criterion. |
| `grade_span_changed_any` | Boolean | Derived | `True` if school reported different grade span configurations (`lowest_grade` to `highest_grade`) across observed years. |
| `lea_changed_any` | Boolean | Derived | `True` if school was reassigned to a different `nces_lea_id` across observed years. |
| `school_type_changed_any` | Boolean | Derived | `True` if school's NCES school type classification changed over the decade. |
| `locale_changed_any` | Boolean | Derived | `True` if school's 2-digit NCES locale code changed across observed years. |
| `locale_code_fixed_2024_2025` | String | NCES EDGE (24–25) | Fixed 2024–25 NCES locale code attached to balanced panel schools for sensitivity controls against census boundary shifts. |
| `locale_group_fixed_2024_2025`| String | Derived (24–25) | Fixed 2024–25 broad locale group (`City`, `Suburb`, `Town`, `Rural`) attached to balanced panel schools. |
| `teacher_fte_valid` | Boolean | Derived | `True` iff `classroom_teacher_fte` is non-missing and $\ge 0$. `False` if teacher FTE was suppressed, missing, or negative in raw files. |
| `teachers_k12_fte_components` | Float | Derived | Secondary K–12 teacher FTE derived via grade-level component sum: $\text{KG} + \text{Elem} + \text{Sec} + \text{Ungraded}$. Retained for automated QA audit against the primary $\text{Total} - \text{PreK}$ formula. |
| `teacher_k12_valid` | Boolean | Derived | `True` iff `teachers_k12_fte` is non-missing and $\ge 0$. `False` if total teachers or Pre-K teachers were suppressed (`-9.0`) or missing (`-1.0`). |

---

### 3.4 Historical CCD Exception-Code Handling & Reporting Quality Tiers

#### NCES Administrative Exception Codes
In historical wide-format CCD files (SY 2014–15 and 2015–16), NCES utilized negative numeric exception codes to denote administrative data states:
- `-1` / `-1.0`: **Missing / Not Reported** (data were expected from the agency but omitted).
- `-2` / `-2.0`: **Not Applicable** (the educational unit does not offer this grade, program, or staff category).
- `-9` / `-9.0`: **Suppressed / Data Withheld** (data withheld by NCES to protect confidentiality or due to state reporting withholding).

#### Cleaning and Remediation Protocol:
1. **Zero Arithmetic on Negative Codes:** Negative values are systematically identified and converted to `NaN` or explicit NA representations prior to arithmetic. Negative codes never participate in sums, subtractions, aggregations, or ratio denominators.
2. **Distinction of Zeros:** A true reported count of 0 is preserved as `0.0`. Administrative non-reporting or suppression is represented strictly as `NaN`.
3. **Pre-K Non-Applicability:** Where an LEA or school does not offer Pre-K (`-2.0` Not Applicable), Pre-K enrollment and teacher FTE are treated as 0 for K–12 derivations, preserving total reported teachers as K–12 teachers. Where Pre-K is suppressed (`-9.0`) or missing (`-1.0`), derived K–12 measures are set to `NaN`.
4. **Integrity Assertions:** Automated assertions in `src/clean/build_longitudinal_panel.py` enforce that 0 negative values exist across all 38 numeric school and LEA analytical variables in all 11 school years.

#### Reporting Coverage Quality Tiers
To prevent distorted longitudinal aggregations (such as the 2015–16 Kansas suppression artifact), every annual aggregate is audited for reporting coverage across both entity counts and represented student enrollment:
- **`complete`:** 100.0% of regional enrollment represented by valid entities.
- **`high_coverage`:** 95.0% to < 100.0% of regional enrollment represented.
- **`partial_coverage`:** 80.0% to < 95.0% of regional enrollment represented.
- **`insufficient_coverage`:** < 80.0% of regional enrollment represented. Series in this tier must NOT be used for unadjusted trend regressions.



