# Track C: Elementary School Yearbook Photography Sampling Protocol
## Independent Non-Administrative Triangulation of Classroom Capacity

---

## 1. Research Justification & Theoretical Objective

Throughout Phases 1 through 3C and Task 004A, all capacity analyses have relied on administrative data submitted by school districts to state agencies (KSDE, MO DESE) or federal authorities (NCES CCD, OCR CRDC). While Task 004A validated that headline pupil/teacher ratios conceal large secondary class sizes via the **Allocation Wedge** (+3.5 to +11.5 students), administrative collections remain subject to institutional reporting rules, course taxonomy aggregation, and potential reporting artifacts.

**Track C** establishes an **independent, physical, non-administrative measurement protocol** using published school yearbooks.

### Why Elementary Homerooms?
1. **The Purest Test of Class Size:** In grades K–5, students spend the vast majority of the instructional day in a single, self-contained homeroom classroom under the care of one certified teacher. There is no departmentalized period rotation, no elective schedule dilution, and no honors/remedial section stratification.
2. **Photographic Ground Truth:** Elementary yearbooks publish annual composite classroom portraits (grids of individual student photos grouped by teacher and grade) or panoramic whole-class photos. Every child assigned to that classroom is photographed or cataloged on the "Not Pictured" roster.
3. **Historical Permanence:** Yearbooks are physical documents printed and distributed to hundreds of families in May of each school year. They are impervious to retroactive administrative adjustments, metric redefinitions, or electronic data system migrations.

---

## 2. Stratified Sampling Matrix

To ensure regional representativeness across the 9-county metropolitan area, **12 elementary schools** are selected via a stratified purposive design balancing **State (MO vs. KS)**, **NCES Urbanization Locale (City, Suburb, Town/Rural)**, and **Socioeconomic / Title I Status**:

| School Name | NCES School ID | District (LEA) | State | County | NCES Locale | Title I Status | Target Profile |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **McKinley Elementary** | 200001000494 | Kansas City (USD 500) | KS | Wyandotte | City: Large | Schoolwide | Urban Core Kansas; High FRL/Bilingual |
| **Banneker Elementary** | 200001000474 | Kansas City (USD 500) | KS | Wyandotte | City: Large | Schoolwide | Urban Core Kansas; Historic neighborhood |
| **Corinth Elementary** | 201083001509 | Shawnee Mission (USD 512) | KS | Johnson | Suburb: Large | Non-Title I | High-wealth established Johnson Co suburb |
| **Tomahawk Elementary** | 200870001099 | Olathe (USD 233) | KS | Johnson | Suburb: Large | Schoolwide | Diverse Johnson County suburban campus |
| **Basehor Elementary** | 200153000085 | Basehor-Linwood (USD 458) | KS | Leavenworth | Town: Fringe | Non-Title I | Rapidly developing exurban growth corridor |
| **Broadmoor Elementary** | 200801001037 | Louisburg (USD 416) | KS | Miami | Rural: Fringe | Non-Title I | Southern agricultural peripheral community |
| **Hale Cook Elementary** | 291689002509 | Kansas City Public Schools | MO | Jackson | City: Large | Targeted | Reopened urban neighborhood school; diverse |
| **Border Star Montessori** | 291689000407 | Kansas City Public Schools | MO | Jackson | City: Large | Schoolwide | Signature magnet urban elementary |
| **Lakewood Elementary** | 292352001358 | North Kansas City (74) | MO | Clay | Suburb: Large | Non-Title I | Major Northland suburban neighborhood school |
| **Highland Park Elementary** | 291854000757 | Lee's Summit R-VII | MO | Jackson | Suburb: Large | Non-Title I | Established eastern suburban campus |
| **Dear Elementary** | 292631001633 | Richmond R-XVI | MO | Ray | Town: Distant | Schoolwide | Outlying rural/town seat in Ray County |
| **Butcher-Greene Elementary** | 291395000438 | Grandview C-4 | MO | Jackson | Suburb: Large | Schoolwide | High-diversity southern suburban ring |

---

## 3. Longitudinal Temporal Anchors

To directly test **Hypothesis H1a (Ratio Concealment)** and **Hypothesis H1b (Longitudinal Ballooning)** without processing thousands of intermediary books, the protocol targets three 5-year anchor intervals:

1. **SY 2024–2025** (Contemporary Baseline)
2. **SY 2019–2020** (Pre-Pandemic Benchmark)
3. **SY 2014–2015** (Decade Baseline)

### Sample Size Calculation:
- **Schools:** 12 campuses
- **Years:** 3 anchor years
- **Grades per school:** 6 grade levels (Kindergarten through Grade 5)
- **Sections per grade level:** Mean 3.0 sections per grade
- **Expected Observations:** 
  $$N = 12 \times 3 \times 6 \times 3.0 \approx 648 \text{ classroom homeroom observations}$$

---

## 4. Classroom Enumeration & Photometric Protocol

### 4.1 Unit of Observation
The fundamental unit of observation is a **single homeroom classroom section**:
- Identified by the **Teacher Name** (e.g., "Mrs. Miller’s 3rd Grade") and **Grade Level** (K, 1, 2, 3, 4, or 5).

### 4.2 Counting Rules:
1. **Individual Composite Grid Pages:**
   - Count every student portrait thumbnail within the designated homeroom box.
   - **Exclusion:** The teacher portrait (usually larger or top-left) and any designated paraprofessional / student teacher portrait are **excluded** from the student headcount.
   - **Inclusion of "Not Pictured":** If the page includes an explicit textual list of enrolled students who were absent on picture day (e.g., *"Not Pictured: Marcus Davis, Chloe Smith"*), add these names directly to the portrait count.
2. **Panoramic / Whole-Class Photo Pages:**
   - In yearbooks featuring whole-group class photos, enumerate individual student faces left-to-right, row-by-row.
   - Cross-check against the printed name caption below the photo to ensure exact 1:1 match.
3. **Specialized Homerooms / Focus Programs:**
   - Classrooms explicitly designated as "Self-Contained Special Education", "Life Skills", or "Intensive Resource" are cataloged with an explicit program flag (`is_specialized = 1`) and analyzed separately from general education homerooms.

### 4.3 Data Ledger Schema (`data/raw/yearbooks/yearbook_homeroom_ledger.csv`):
```text
record_id               # Unique observation ID: YBK_{NCES_ID}_{YEAR}_{GRADE}_{TEACHER}
nces_school_id          # 12-digit NCES school code
school_name             # School name
school_year             # Academic year (e.g. 2024-25)
grade_level             # K, 1, 2, 3, 4, 5
teacher_name            # Last name of classroom teacher
photo_type              # composite_grid | group_photo
portrait_student_count  # Count of photographed student faces
not_pictured_count      # Count of students listed in text caption but not pictured
total_homeroom_students # portrait_student_count + not_pictured_count
is_specialized          # 0 = General Education Homeroom, 1 = Self-contained SPED
coder_initials          # Initials of researcher extracting data
source_citation         # Library archive, call number, or physical book donor
```

---

## 5. Quality Control & Inter-Rater Reliability (IRR)

To eliminate counting errors or ambiguity in photographic enumeration:
1. **Dual-Blind Coding:** A random **15% subsample** (~100 classrooms) will be independently enumerated by two separate researchers without knowledge of the other's count.
2. **Inter-Rater Reliability Metric:**
   - Compute Pearson's correlation ($r$) and Cohen’s weighted kappa ($\kappa$) across the dual-coded sample.
   - **Pre-set Acceptance Standard:** $r \ge 0.98$ and $\kappa \ge 0.95$.
   - Any discrepant classroom count ($\Delta \ge 1$) must be adjudicated by high-resolution optical re-examination.
3. **Internal Consistency Check:**
   - For each school and year, compute:
     $$\text{Estimated Total School Enrollment} = \sum_{c} \text{Homeroom Students}_c$$
   - Cross-reference with the school's official **NCES CCD October Fall Enrollment**.
   - If the yearbook total differs from NCES CCD by more than **$\pm 8\%$**, investigate the discrepancy (e.g., missing pre-K pages, mid-year attrition, or excluded classrooms).

---

## 6. Analytical Estimands & Hypothesis Tests

Using the compiled homeroom panel, we compute:

1. **Elementary Allocation Wedge:**
   $$\text{Elementary Wedge}_{s, t} = \text{Mean Homeroom Class Size}_{s, t} - \text{School Pupil/Teacher Ratio (CCD PTR)}_{s, t}$$
2. **Comparison with Secondary Wedge:**
   - Compare the Elementary Wedge against the Secondary High School Wedge (+3.5 to +4.4 regional mean from Task 004A).
   - If elementary homerooms average **21 to 24 students** while elementary building PTR is **13.5 to 15.0:1**, this confirms that the Allocation Wedge is an institutional property of K–12 public schooling that manifests across all grade spans.
3. **Decade Trend Test (H1b):**
   - Estimate within-school change:
     $$\Delta \text{Homeroom Size} = \text{Homeroom Size}_{2024-25} - \text{Homeroom Size}_{2014-15}$$
   - Direct test of whether elementary classrooms got smaller, larger, or remained flat while macro teacher FTE grew +8.9%.

---

## 7. Archive Sourcing & Acquisition Strategy

Yearbooks will be accessed through the following physical and digital repositories:
1. **Public Library Local History Collections:**
   - **Kansas City Public Library:** Missouri Valley Special Collections (Central Library, 14 W. 10th St, KCMO).
   - **Johnson County Library:** Local History Collection (Central Resource Library, 9875 W. 87th St, Overland Park, KS).
   - **Mid-Continent Public Library:** Midwest Genealogy Center / Local History Collection (Independence, MO).
2. **School District Archives & Public Inquiries:**
   - District communications offices routinely archive copies of all published annuals.
   - School PTA / PTO parent organizations and school library media centers.
3. **Digital Repositories:**
   - Classmates.com / Ancestry.com digital school yearbook databases.
   - Internet Archive community collections.
