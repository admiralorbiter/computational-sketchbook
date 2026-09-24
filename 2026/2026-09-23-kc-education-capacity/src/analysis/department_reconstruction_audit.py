"""
src/analysis/department_reconstruction_audit.py
Task 006.2: Department Reconstruction Feasibility Audit for Selected Urban High Schools

Audits the feasibility of reconstructing department-level average student-course loads
(E_math / T_math) strictly from public records across six pilot high schools:
  1. Lincoln College Preparatory Academy (KCPS)
  2. Grandview Senior High (Grandview C-4)
  3. Ruskin High School (Hickman Mills C-1)
  4. Center Senior High (Center 58)
  5. East High School (KCPS)
  6. Wyandotte High School (Kansas City USD 500)

Evaluates whether publicly available faculty listings, district directories, and state
releases can establish an observed subject-specific teacher count (T_math) to compute:
    Covered Math Load per Teacher = (sum_c E_c) / T_math
analogous to the 1985 Jenkins remedial audit metric (student-classes per teacher).

Outputs:
  - outputs/tables/task006_2_department_reconstruction_audit.csv
  - outputs/tables/task006_2_department_reconstruction_audit_report.md
"""

import os
import pandas as pd
import numpy as np

def run_department_audit():
    print("=== Running Task 006.2: Department Reconstruction Feasibility Audit ===")
    
    # 1. Load 2023-24 CRDC Math Aggregates for the 6 Pilot Campuses
    df = pd.read_csv("data/processed/kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv")
    latest_year = df["school_year"].max()
    hs = df[(df["school_year"] == latest_year) & (df["school_level"] == "High")].copy()
    
    pilot_campuses = [
        {"name": "LINCOLN COLLEGE PREP.", "district": "KANSAS CITY 33", "short_name": "Lincoln Prep"},
        {"name": "GRANDVIEW SR. HIGH", "district": "GRANDVIEW C-4", "short_name": "Grandview High"},
        {"name": "RUSKIN HIGH SCHOOL", "district": "HICKMAN MILLS C-1", "short_name": "Ruskin High"},
        {"name": "CENTER SR. HIGH", "district": "CENTER 58", "short_name": "Center High"},
        {"name": "EAST HIGH SCHOOL", "district": "KANSAS CITY 33", "short_name": "East High"},
        {"name": "Wyandotte High", "district": "Kansas City", "short_name": "Wyandotte High"}
    ]
    
    math_codes = ["alg1", "geom", "alg2", "advm", "calc"]
    
    # Compile CRDC Math Data
    crdc_records = []
    for c in pilot_campuses:
        sdata = hs[(hs["school_name"] == c["name"]) & (hs["district_name"] == c["district"])]
        if len(sdata) == 0:
            continue
        row0 = sdata.iloc[0]
        mdata = sdata[sdata["course_code"].isin(math_codes)]
        tot_classes = mdata["num_classes"].sum()
        tot_enrolled = mdata["num_enrolled"].sum()
        mean_proxy = tot_enrolled / tot_classes if tot_classes > 0 else np.nan
        
        crdc_records.append({
            "school_name": c["name"],
            "district_name": c["district"],
            "short_name": c["short_name"],
            "building_ptr": row0["school_ptr"],
            "total_teacher_fte": row0["classroom_teacher_fte"],
            "enrollment_k12": row0["enrollment_k12"],
            "crdc_math_classes": tot_classes,
            "crdc_math_enrolled": tot_enrolled,
            "crdc_math_load_proxy": mean_proxy
        })
    crdc_df = pd.DataFrame(crdc_records)
    
    # 2. Public Personnel Directory Audit Findings
    # Audit criteria:
    # - observed_subject_teacher_count: number of distinct math instructors identified
    # - source_year: year represented by public directory
    # - source_type: medium/format of public record
    # - source_quality: High / Medium / Low / Unavailable
    # - mismatch_flags: structural, temporal, or taxonomic discrepancies
    
    audit_findings = [
        {
            "short_name": "Wyandotte High",
            "observed_subject_teacher_count": 8,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "School Website Departmental Listing (whs.kckschools.org)",
            "source_quality": "Medium (Disaggregated by Subject, but Non-Contemporaneous)",
            "source_notes": "Website explicitly segments faculty by department, listing 8 teachers under 'Math Teachers' (Brous, Cecil, L. Holst, M. Holst, Hornberger, O'Dell, et al.).",
            "mismatch_flags": "Severe Class-to-Teacher Disconnect: 121 CRDC classes / 8 teachers = 15.1 classes/teacher (293.9 enrollments/teacher). Indicates temporal lag, cumulative fall/spring snapshot aggregation, and/or missing itinerant, SPED, and long-term substitute instructors."
        },
        {
            "short_name": "Lincoln Prep",
            "observed_subject_teacher_count": np.nan,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "District Staff Portal (kcpublicschools.org)",
            "source_quality": "Unavailable (Bot-Protected / Undifferentiated)",
            "source_notes": "District Thrillshare/Apptegy portal is protected by F5/Cloudflare Client Challenge. Public staff directory entries do not categorize teachers by subject department (generic 'Teacher' title).",
            "mismatch_flags": "No Public Subject Disaggregation: Department-level teacher count cannot be observed without internal administrative schedules or private directory access."
        },
        {
            "short_name": "Grandview High",
            "observed_subject_teacher_count": np.nan,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "School Staff Directory (ghs.grandviewc4.net)",
            "source_quality": "Low (Staff Directory Present, Subject Unindexed)",
            "source_notes": "Public directory lists 71 classroom teachers, but does not index or filter by academic department. Teacher profile pages rely on self-reported biographical blurbs (only 3 teachers explicitly mention mathematics/algebra).",
            "mismatch_flags": "Unindexed Department Structure: Total faculty is known (71 FTE), but subject assignment is unobserved in public data."
        },
        {
            "short_name": "Ruskin High",
            "observed_subject_teacher_count": np.nan,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "District Staff Directory (ruskin.hickmanmills.org)",
            "source_quality": "Low (Staff Directory Present, Subject Unindexed)",
            "source_notes": "Directory lists 95 certified personnel names and email addresses, but provides no subject-area assignment or departmental classification.",
            "mismatch_flags": "Unindexed Department Structure: Department teacher count unobserved."
        },
        {
            "short_name": "Center High",
            "observed_subject_teacher_count": np.nan,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "District Staff Portal (center.k12.mo.us)",
            "source_quality": "Unavailable (Bot-Protected / Undifferentiated)",
            "source_notes": "District Thrillshare web platform operates under active bot protection (HTTP 200 Client Challenge). Subject departmental listings are not exposed publicly.",
            "mismatch_flags": "Platform Shielding & No Subject Classification."
        },
        {
            "short_name": "East High",
            "observed_subject_teacher_count": np.nan,
            "source_year": "2024–2026 (Current Web)",
            "source_type": "District Staff Portal (kcpublicschools.org)",
            "source_quality": "Unavailable (Bot-Protected / Undifferentiated)",
            "source_notes": "Same as Lincoln Prep: KCPS staff portals list personnel under undifferentiated 'Teacher' classifications behind automated bot challenges.",
            "mismatch_flags": "No Public Subject Disaggregation."
        }
    ]
    audit_df = pd.DataFrame(audit_findings)
    
    # 3. Merge CRDC Data with Audit Findings
    merged = pd.merge(crdc_df, audit_df, on="short_name")
    
    # Calculate Jenkins-style metrics where teacher count is observed
    merged["student_course_enrollments_per_observed_math_teacher"] = (
        merged["crdc_math_enrolled"] / merged["observed_subject_teacher_count"]
    )
    merged["classes_per_observed_math_teacher"] = (
        merged["crdc_math_classes"] / merged["observed_subject_teacher_count"]
    )
    
    # Implied full-time teacher equivalents under typical duty (5 or 6 periods)
    # Wyandotte: typical duty = 6 (8-block); others = 5 (7-period)
    typical_d = [5, 5, 5, 5, 5, 6]
    merged["typical_duty_periods"] = typical_d
    merged["implied_math_fte_from_crdc"] = merged["crdc_math_classes"] / merged["typical_duty_periods"]
    
    # Reorder columns for output
    cols_out = [
        "school_name", "district_name", "short_name", "building_ptr", "enrollment_k12",
        "total_teacher_fte", "crdc_math_classes", "crdc_math_enrolled", "crdc_math_load_proxy",
        "typical_duty_periods", "implied_math_fte_from_crdc", "observed_subject_teacher_count",
        "source_year", "source_type", "source_quality", "student_course_enrollments_per_observed_math_teacher",
        "classes_per_observed_math_teacher", "mismatch_flags", "source_notes"
    ]
    res_df = merged[cols_out]
    
    os.makedirs("outputs/tables", exist_ok=True)
    csv_path = "outputs/tables/task006_2_department_reconstruction_audit.csv"
    res_df.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")
    
    # 4. Generate Formal Audit Report
    report_path = "outputs/tables/task006_2_department_reconstruction_audit_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Task 006.2: Department Reconstruction Feasibility Audit\n\n")
        f.write("## 1. Executive Summary: The Feasibility Boundary of Department-Level Reconstruction\n\n")
        f.write("Task 006.2 executed an empirical feasibility audit across six selected urban high schools to determine whether public records allow the reconstruction of an **observed department-level teacher load**:\n\n")
        f.write("$$\\text{Covered Math Load per Teacher} = \\frac{\\sum_c E_c}{T_{\\text{math}}}$$\n\n")
        f.write("This metric was designed to replicate the historical *Jenkins v. Missouri* remedial audit metric ($\\text{student-classes} / \\text{teachers}$) at the department scale without requiring individual teacher-to-section roster linkage.\n\n")
        f.write("### The Core Audit Conclusion:\n")
        f.write("> **Department-level teacher load reconstruction is not reliably feasible from public records today.**\n")
        f.write(">\n")
        f.write("> Across the six pilot campuses, public personnel directories either (a) do not categorize faculty by subject department (Missouri urban districts), (b) shield staff rosters behind automated bot verification (KCPS, Center), or (c) exhibit severe temporal, taxonomic, and snapshot disconnects when department rosters are exposed (Wyandotte High in KCKPS).\n")
        f.write(">\n")
        f.write("> Consequently, **public data capability terminates at Step 3 (Modeled Course-Load Scenarios)**. Public records cannot observe $T_{\\text{math}}$ with sufficient fidelity to calculate an empirical department-level load.\n\n")
        
        f.write("## 2. Department Reconstruction Audit Matrix (SY 2023–24 vs. Public Personnel)\n\n")
        f.write("| Campus | District | CRDC Math Classes | CRDC Math Enr | CRDC Load Proxy | Implied FTE (Classes / Duty) | Observed Math Teachers | Source Type & Quality | Mismatch / Feasibility Finding |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |\n")
        for _, r in res_df.iterrows():
            obs_str = f"{r['observed_subject_teacher_count']:.0f}" if pd.notnull(r["observed_subject_teacher_count"]) else "*Unobserved*"
            f.write(f"| **{r['short_name']}** | {r['district_name']} | {r['crdc_math_classes']:.0f} | {r['crdc_math_enrolled']:.0f} | {r['crdc_math_load_proxy']:.1f} | {r['implied_math_fte_from_crdc']:.1f} FTE | {obs_str} | {r['source_type']} ({r['source_quality']}) | {r['mismatch_flags']} |\n")
            
        f.write("\n\n## 3. In-Depth Campus Case Audits\n\n")
        f.write("### 1. Wyandotte High School (KCKPS USD 500) — The Snapshot & Staffing Disconnect\n")
        f.write("- **The Public Listing:** Wyandotte's public staff directory is one of the few urban portals that explicitly disaggregates faculty by academic department, listing **8 Math Teachers** (Brous, Cecil, L. Holst, M. Holst, Hornberger, O'Dell, et al.).\n")
        f.write("- **The CRDC Reality:** In 2023–24, CRDC reported **121 math classes enrolling 2,351 students** across Algebra I, Geometry, Algebra II, and Advanced Math.\n")
        f.write("- **The Discrepancy:** Dividing CRDC quantities by the 8 listed teachers yields **15.1 classes per teacher and 293.9 student-course enrollments per teacher**. Under Wyandotte's 8-period Red/White alternating block, a full-time teacher typically instructs 6 blocks. Eight teachers could staff at most $8 \\times 6 = 48$ concurrent sections—fewer than half of the 121 classes reported!\n")
        f.write("- **The Mechanism Audit:**\n")
        f.write("  1. *Semester / Block Snapshot Aggregation:* Under OCR reporting rules, block-schedule schools may report the cumulative sum of fall and spring semester classes. If 121 represents a full-year cumulative count of semester courses, concurrent offerings were approximately ~60 sections per semester, requiring $\\approx 10$ full-time teachers.\n")
        f.write("  2. *Departmental Spillover:* Teachers who instruct math sections may be categorized under Special Education (co-teachers), ESOL/Bilingual education, or instructional coaching rather than 'Math Teachers'.\n")
        f.write("  3. *Temporal & Vacancy Lag:* Public school websites reflect current staffing (2024–2026) and routinely omit vacancies, long-term substitutes, or adjuncts that existed during the 2023–24 CRDC collection wave.\n")
        f.write("- **Audit Ruling:** Without internal master schedule tables, an analyst cannot determine whether $T_{\\text{math}} = 8$, $10$, $12$, or $20$. Computing $2,351 / 8 = 293.9$ produces a spurious artifact rather than a true teacher workload metric.\n\n")
        
        f.write("### 2. Missouri Urban Campuses (Lincoln Prep, East High, Grandview, Ruskin, Center)\n")
        f.write("- **Lincoln College Prep & East High (KCPS):** KCPS portals operate behind F5/Cloudflare automated challenges. Publicly visible staff directories list teachers with undifferentiated titles ('Teacher') without indexing academic subject assignments.\n")
        f.write("- **Grandview Senior High (Grandview C-4):** The public staff directory indexes 71 classroom teachers, but does not provide subject department tags. Teacher profile pages contain open-ended biographical text, with only 3 teachers mentioning math keywords.\n")
        f.write("- **Ruskin High School (Hickman Mills C-1):** Staff directories list 95 certified personnel with names and email addresses, but contain zero subject classifications.\n")
        f.write("- **Center Senior High (Center 58):** Web platform is bot-shielded; public directories do not classify teachers by department.\n")
        f.write("- **Audit Ruling:** Across all five Missouri urban campuses, $T_{\\text{math}}$ is **completely unobserved** in public personnel records. Any calculation of $E_{\\text{math}} / T_{\\text{math}}$ would require imputing $T_{\\text{math}} = S_{\\text{math}} / D$, which simply reduces to $D \\cdot \\bar{s}_{\\text{dept}}$ (Step 3 modeled load) rather than an independent empirical observation.\n\n")
        
        f.write("## 4. The Final Synthesis Boundary\n\n")
        f.write("This audit firmly establishes the public data boundary for the final synthesis paper:\n\n")
        f.write("1. **What Public Data Can Defensively Recover:**\n")
        f.write("   - School staffing ratios ($PTR_{\\text{bldg}}$) and macro personnel trends (CCD / State files).\n")
        f.write("   - Course enrollment pressure ($E_c$) and class counts ($S_c$) (CRDC).\n")
        f.write("   - Reported students per reported class (CRDC load proxy: $\\bar{s}_c = E_c / S_c$).\n")
        f.write("   - Derived schedule scenarios ($R_5 = 5\\bar{s}_c, R_6 = 6\\bar{s}_c$).\n")
        f.write("   - Gateway course bottlenecks (e.g. Wyandotte Algebra I averaging 28.5 across 46 classes).\n\n")
        f.write("2. **Where Public Reconstruction Breaks Down:**\n")
        f.write("   - **Department-Level Reconstruction ($E_{\\text{dept}} / T_{\\text{dept}}$):** Fails because public school directories are non-contemporaneous, unstandardized, subject-undifferentiated, and prone to semester-snapshot disconnects.\n")
        f.write("   - **Individual Teacher Rosters & Tail Distributions:** Strictly unobservable without private Student Information System (SIS) microdata or internal master schedules.\n")
        
    print(f"Generated {report_path}")
    print("=== Task 006.2 Complete ===")

if __name__ == "__main__":
    run_department_audit()
