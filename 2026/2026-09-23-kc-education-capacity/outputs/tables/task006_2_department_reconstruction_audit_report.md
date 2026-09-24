# Task 006.2: Department Reconstruction Feasibility Audit

## 1. Executive Summary: The Feasibility Boundary of Department-Level Reconstruction

Task 006.2 executed an empirical feasibility audit across six selected urban high schools to determine whether public records allow the reconstruction of an **observed department-level teacher load**:

$$\text{Covered Math Load per Teacher} = \frac{\sum_c E_c}{T_{\text{math}}}$$

This metric was designed to replicate the historical *Jenkins v. Missouri* remedial audit metric ($\text{student-classes} / \text{teachers}$) at the department scale without requiring individual teacher-to-section roster linkage.

### The Core Audit Conclusion:
> **Department-level teacher load reconstruction is not reliably feasible from public records today.**
>
> Across the six pilot campuses, public personnel directories either (a) do not categorize faculty by subject department (Missouri urban districts), (b) shield staff rosters behind automated bot verification (KCPS, Center), or (c) exhibit severe temporal, taxonomic, and snapshot disconnects when department rosters are exposed (Wyandotte High in KCKPS).
>
> Consequently, **public data capability terminates at Step 3 (Modeled Course-Load Scenarios)**. Public records cannot observe $T_{\text{math}}$ with sufficient fidelity to calculate an empirical department-level load.

## 2. Department Reconstruction Audit Matrix (SY 2023–24 vs. Public Personnel)

| Campus | District | CRDC Math Classes | CRDC Math Enr | CRDC Load Proxy | Implied FTE (Classes / Duty) | Observed Math Teachers | Source Type & Quality | Mismatch / Feasibility Finding |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Lincoln Prep** | KANSAS CITY 33 | 37 | 855 | 23.1 | 7.4 FTE | *Unobserved* | District Staff Portal (kcpublicschools.org) (Unavailable (Bot-Protected / Undifferentiated)) | No Public Subject Disaggregation: Department-level teacher count cannot be observed without internal administrative schedules or private directory access. |
| **Grandview High** | GRANDVIEW C-4 | 40 | 875 | 21.9 | 8.0 FTE | *Unobserved* | School Staff Directory (ghs.grandviewc4.net) (Low (Staff Directory Present, Subject Unindexed)) | Unindexed Department Structure: Total faculty is known (71 FTE), but subject assignment is unobserved in public data. |
| **Ruskin High** | HICKMAN MILLS C-1 | 49 | 960 | 19.6 | 9.8 FTE | *Unobserved* | District Staff Directory (ruskin.hickmanmills.org) (Low (Staff Directory Present, Subject Unindexed)) | Unindexed Department Structure: Department teacher count unobserved. |
| **Center High** | CENTER 58 | 25 | 417 | 16.7 | 5.0 FTE | *Unobserved* | District Staff Portal (center.k12.mo.us) (Unavailable (Bot-Protected / Undifferentiated)) | Platform Shielding & No Subject Classification. |
| **East High** | KANSAS CITY 33 | 48 | 807 | 16.8 | 9.6 FTE | *Unobserved* | District Staff Portal (kcpublicschools.org) (Unavailable (Bot-Protected / Undifferentiated)) | No Public Subject Disaggregation. |
| **Wyandotte High** | Kansas City | 121 | 2351 | 19.4 | 20.2 FTE | 8 | School Website Departmental Listing (whs.kckschools.org) (Medium (Disaggregated by Subject, but Non-Contemporaneous)) | Severe Class-to-Teacher Disconnect: 121 CRDC classes / 8 teachers = 15.1 classes/teacher (293.9 enrollments/teacher). Indicates temporal lag, cumulative fall/spring snapshot aggregation, and/or missing itinerant, SPED, and long-term substitute instructors. |


## 3. In-Depth Campus Case Audits

### 1. Wyandotte High School (KCKPS USD 500) — The Snapshot & Staffing Disconnect
- **The Public Listing:** Wyandotte's public staff directory is one of the few urban portals that explicitly disaggregates faculty by academic department, listing **8 Math Teachers** (Brous, Cecil, L. Holst, M. Holst, Hornberger, O'Dell, et al.).
- **The CRDC Reality:** In 2023–24, CRDC reported **121 math classes enrolling 2,351 students** across Algebra I, Geometry, Algebra II, and Advanced Math.
- **The Discrepancy:** Dividing CRDC quantities by the 8 listed teachers yields **15.1 classes per teacher and 293.9 student-course enrollments per teacher**. Under Wyandotte's 8-period Red/White alternating block, a full-time teacher typically instructs 6 blocks. Eight teachers could staff at most $8 \times 6 = 48$ concurrent sections—fewer than half of the 121 classes reported!
- **The Mechanism Audit:**
  1. *Semester / Block Snapshot Aggregation:* Under OCR reporting rules, block-schedule schools may report the cumulative sum of fall and spring semester classes. If 121 represents a full-year cumulative count of semester courses, concurrent offerings were approximately ~60 sections per semester, requiring $\approx 10$ full-time teachers.
  2. *Departmental Spillover:* Teachers who instruct math sections may be categorized under Special Education (co-teachers), ESOL/Bilingual education, or instructional coaching rather than 'Math Teachers'.
  3. *Temporal & Vacancy Lag:* Public school websites reflect current staffing (2024–2026) and routinely omit vacancies, long-term substitutes, or adjuncts that existed during the 2023–24 CRDC collection wave.
- **Audit Ruling:** Without internal master schedule tables, an analyst cannot determine whether $T_{\text{math}} = 8$, $10$, $12$, or $20$. Computing $2,351 / 8 = 293.9$ produces a spurious artifact rather than a true teacher workload metric.

### 2. Missouri Urban Campuses (Lincoln Prep, East High, Grandview, Ruskin, Center)
- **Lincoln College Prep & East High (KCPS):** KCPS portals operate behind F5/Cloudflare automated challenges. Publicly visible staff directories list teachers with undifferentiated titles ('Teacher') without indexing academic subject assignments.
- **Grandview Senior High (Grandview C-4):** The public staff directory indexes 71 classroom teachers, but does not provide subject department tags. Teacher profile pages contain open-ended biographical text, with only 3 teachers mentioning math keywords.
- **Ruskin High School (Hickman Mills C-1):** Staff directories list 95 certified personnel with names and email addresses, but contain zero subject classifications.
- **Center Senior High (Center 58):** Web platform is bot-shielded; public directories do not classify teachers by department.
- **Audit Ruling:** Across all five Missouri urban campuses, $T_{\text{math}}$ is **completely unobserved** in public personnel records. Any calculation of $E_{\text{math}} / T_{\text{math}}$ would require imputing $T_{\text{math}} = S_{\text{math}} / D$, which simply reduces to $D \cdot \bar{s}_{\text{dept}}$ (Step 3 modeled load) rather than an independent empirical observation.

## 4. The Final Synthesis Boundary

This audit firmly establishes the public data boundary for the final synthesis paper:

1. **What Public Data Can Defensively Recover:**
   - School staffing ratios ($PTR_{\text{bldg}}$) and macro personnel trends (CCD / State files).
   - Course enrollment pressure ($E_c$) and class counts ($S_c$) (CRDC).
   - Reported students per reported class (CRDC load proxy: $\bar{s}_c = E_c / S_c$).
   - Derived schedule scenarios ($R_5 = 5\bar{s}_c, R_6 = 6\bar{s}_c$).
   - Gateway course bottlenecks (e.g. Wyandotte Algebra I averaging 28.5 across 46 classes).

2. **Where Public Reconstruction Breaks Down:**
   - **Department-Level Reconstruction ($E_{\text{dept}} / T_{\text{dept}}$):** Fails because public school directories are non-contemporaneous, unstandardized, subject-undifferentiated, and prone to semester-snapshot disconnects.
   - **Individual Teacher Rosters & Tail Distributions:** Strictly unobservable without private Student Information System (SIS) microdata or internal master schedules.
