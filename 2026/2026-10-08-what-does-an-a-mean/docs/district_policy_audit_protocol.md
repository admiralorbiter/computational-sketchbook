# District Policy Audit Protocol & Coding Manual

## 1. Purpose & Scope

This protocol establishes the standardized procedure for collecting, verifying, and coding secondary grading policies, graduation regulations, and credit recovery practices across public school districts and charter Local Educational Agencies (LEAs) in the Greater Kansas City metropolitan area.

The objective is to translate institutional documents into a structured, auditable dataset to evaluate how local policy decisions influence course credit assignment and graduation rates.

---

## 2. Target District Universe

The audit focuses on the major secondary education providers in the Kansas City metropolitan area (Jackson, Clay, Platte, and Cass Counties in Missouri):

1. **Kansas City Public Schools (KCPS - 048-078)**: Urban core district serving Kansas City.
2. **Independence School District (048-077)**: Mature inner-ring suburban district; operates on a 4-day school week.
3. **North Kansas City Schools (024-093)**: Large, high-growth suburban district north of the Missouri River.
4. **Lee's Summit R-VII (048-074)**: Affluent outer-ring suburban district in southeast Jackson County.
5. **Hickman Mills C-1 (048-072)**: High-poverty suburban district in south Kansas City.
6. **Blue Springs R-IV (048-068)**: Large eastern suburban district.
7. **Raytown C-2 (048-079)**: Inner-ring suburban district bordering KCPS.
8. **Grandview C-4 (048-071)**: Southern suburban district.
9. **Park Hill School District (083-005)**: High-performing northwest suburban district.
10. **Charter High Schools (LEAs)**: Crossroads Charter Schools, DeLaSalle Charter School, Hogan Preparatory Academy, University Academy, Frontier Schools, and Ewing Marion Kauffman School.

---

## 3. Policy Document Hierarchy

Researchers must audit primary policy artifacts in the following hierarchical order:

1. **Board of Education Policies (MSBA Indexing)**:
   - `Policy IK`: Academic Achievement
   - `Policy IKA`: Grading Systems
   - `Policy IKAB`: Student Progress Reports to Parents / Grading
   - `Policy IKE`: Promotion, Retention, and Acceleration
   - `Policy IKF`: Graduation Requirements
2. **District Secondary Grading Guidelines / Handbooks**:
   - District-wide secondary assessment manuals issued by curriculum and instruction departments.
3. **High School Student-Parent Handbooks**:
   - Building-level rules governing grading scales, retakes, make-up work, and credit recovery eligibility.
4. **Course Description Catalogs**:
   - Course listings, prerequisites, weighting systems (AP/IB/Dual Credit), and credit recovery options.

---

## 4. Standardized Coding Codebook

For each LEA, coders record the following twelve discrete variables:

| Variable Name | Field Type | Permitted Values | Definition / Coding Instructions |
| :--- | :--- | :--- | :--- |
| `district_code` | String | e.g. `048-078` | Missouri DESE 6-digit LEA identifier. |
| `district_name` | String | Text | Official legal name of school district or charter LEA. |
| `policy_code` | String | e.g. `IKA`, `IKF` | MSBA policy classification code or local document equivalent. |
| `grading_model` | Categorical | `TRADITIONAL_PCT`, `STANDARDS_BASED`, `HYBRID` | Overall grading framework: Traditional 100-point percentage scale, Standards-Based Learning (rubric 1–4), or Hybrid. |
| `grade_floor_policy` | Categorical | `FLOOR_50`, `FLOOR_40`, `NO_FLOOR_ZERO_ALLOWED`, `DISCRETIONARY` | Minimum score recorded on assignments or quarter marks. `FLOOR_50` = no mark below 50%; `FLOOR_40` = no mark below 40%; `NO_FLOOR` = zero permitted for unsubmitted work. |
| `retake_rule` | Categorical | `UNIVERSAL_MANDATORY`, `CAPPED_RETAKE`, `TEACHER_DISCRETION`, `PROHIBITED` | Rules governing reassessment. `UNIVERSAL_MANDATORY` = students permitted to retake any summative test for full credit; `CAPPED_RETAKE` = retake score capped (e.g. 70% or 80%); `TEACHER_DISCRETION` = individual teacher decides. |
| `homework_weight_cap` | Categorical | `CAPPED_10_PCT`, `CAPPED_20_PCT`, `PRACTICE_ONLY_0_PCT`, `UNCAPPED_TRADITIONAL` | Statutory limits placed on homework or formative assessments in final course grade calculation. |
| `eoc_grade_weight` | Categorical | `NONE_0_PCT`, `WEIGHT_5_10_PCT`, `WEIGHT_20_PCT`, `LOCAL_DISCRETION` | Percentage that state End-of-Course (EOC) exam score contributes to final semester course grade. |
| `credit_recovery_platform`| Categorical | `EDGENUITY`, `APEX_LEARNING`, `ACELLUS`, `EDMENTUM`, `IN_HOUSE`, `UNKNOWN` | Primary digital software platform deployed for student course credit recovery. |
| `credit_recovery_setting` | Categorical | `DEDICATED_LAB`, `SUMMER_ONLY`, `ASYNCHRONOUS_REMOTE`, `BLENDED` | Operational environment where credit recovery modules are completed. |
| `credit_recovery_cutoff`  | Numeric | e.g. `60.0`, `70.0` | Minimum score required in credit recovery course to convert failing mark into earned graduation credit (usually 60% = 'D'). |
| `source_url` | String | URL | Direct link to official board policy manual, student handbook, or district catalog. |

---

## 5. Audit Validation & Inter-Rater Reliability

1. **Independent Dual Coding**: Every LEA policy document must be independently coded by two researchers.
2. **Discrepancy Resolution**: Any divergence in categorical classification is resolved by reviewing the exact text of the Board Policy manual or Secondary Student Handbook.
3. **Provenance Hash**: The official URL, retrieval timestamp, and SHA-256 hash of downloaded PDF policy files must be recorded in `sources/source_registry.csv`.
