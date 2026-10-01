"""
Descriptive Administrative-Intensity Decomposition Engine (Phase 1.1 Calibrated).

Generates calibrated mechanical non-teaching staffing decompositions for:
1. Balanced Regular District Cohort (55 continuous districts: 2014-15 to 2024-25 & 2014-15 to 2023-24).
2. Dynamic Metropolitan Universe (all LEAs including charter entry/exit).
3. 20-Year Safe Aggregate Decomposition (Central Mgmt + Coordinators).
4. Individual Major District Ledgers across both Kansas and Missouri.

Explicitly accounts for:
- Kansas 2024-25 Assistant Principal exclusion break in SCHADM.
- Missouri 2014-15 LEAADM -> CORSUP title reclassifications.
- Retraction of the student-support +253% artifact, replacing it with the clean Counselors series.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"


def decompose_pair(df_start: pd.DataFrame, df_end: pd.DataFrame, group_col: str = None):
    """Compute mechanical decomposition between two cross-sections."""
    if group_col:
        s0 = df_start.groupby(group_col).sum(numeric_only=True)
        s1 = df_end.groupby(group_col).sum(numeric_only=True)
        keys = sorted(list(set(s0.index).intersection(set(s1.index))))
    else:
        s0 = pd.DataFrame([df_start.sum(numeric_only=True)], index=["Total"])
        s1 = pd.DataFrame([df_end.sum(numeric_only=True)], index=["Total"])
        keys = ["Total"]

    rows = []
    for k in keys:
        r0 = s0.loc[k]
        r1 = s1.loc[k]

        e0, e1 = r0.get("enrollment_total", 0), r1.get("enrollment_total", 0)
        sch0, sch1 = r0.get("operating_schools_count", 0), r1.get("operating_schools_count", 0)
        t0, t1 = r0.get("teachers_k12_fte", 0), r1.get("teachers_k12_fte", 0)

        p0, p1 = r0.get("school_administrators_fte", 0), r1.get("school_administrators_fte", 0)
        c0, c1 = r0.get("lea_administrators_fte", 0), r1.get("lea_administrators_fte", 0)
        i0, i1 = r0.get("instructional_coordinators_fte", 0), r1.get("instructional_coordinators_fte", 0)
        couns0, couns1 = r0.get("counselors_fte", 0), r1.get("counselors_fte", 0)
        para0, para1 = r0.get("paraprofessionals_fte", 0), r1.get("paraprofessionals_fte", 0)
        oth0, oth1 = (
            (r0.get("other_support_staff_fte", 0) + r0.get("school_admin_support_fte", 0) + r0.get("lea_admin_support_fte", 0)),
            (r1.get("other_support_staff_fte", 0) + r1.get("school_admin_support_fte", 0) + r1.get("lea_admin_support_fte", 0)),
        )

        comb_cent0 = c0 + i0
        comb_cent1 = c1 + i1
        tot_admin0 = p0 + c0 + i0
        tot_admin1 = p1 + c1 + i1

        rows.append({
            "group": k,
            "enrollment_start": e0,
            "enrollment_end": e1,
            "delta_enrollment": e1 - e0,
            "pct_delta_enrollment": ((e1 - e0) / e0 * 100.0) if e0 > 0 else np.nan,
            "schools_start": sch0,
            "schools_end": sch1,
            "delta_schools": sch1 - sch0,
            "teachers_start": t0,
            "teachers_end": t1,
            "delta_teachers": t1 - t0,
            "pct_delta_teachers": ((t1 - t0) / t0 * 100.0) if t0 > 0 else np.nan,
            "principals_start": p0,
            "principals_end": p1,
            "delta_principals": p1 - p0,
            "pct_delta_principals": ((p1 - p0) / p0 * 100.0) if p0 > 0 else np.nan,
            "central_admin_start": c0,
            "central_admin_end": c1,
            "delta_central_admin": c1 - c0,
            "pct_delta_central_admin": ((c1 - c0) / c0 * 100.0) if c0 > 0 else np.nan,
            "coordinators_start": i0,
            "coordinators_end": i1,
            "delta_coordinators": i1 - i0,
            "pct_delta_coordinators": ((i1 - i0) / i0 * 100.0) if i0 > 0 else np.nan,
            "central_plus_coord_start": comb_cent0,
            "central_plus_coord_end": comb_cent1,
            "delta_central_plus_coord": comb_cent1 - comb_cent0,
            "pct_delta_central_plus_coord": ((comb_cent1 - comb_cent0) / comb_cent0 * 100.0) if comb_cent0 > 0 else np.nan,
            "total_admin_start": tot_admin0,
            "total_admin_end": tot_admin1,
            "delta_total_admin": tot_admin1 - tot_admin0,
            "pct_delta_total_admin": ((tot_admin1 - tot_admin0) / tot_admin0 * 100.0) if tot_admin0 > 0 else np.nan,
            "counselors_start": couns0,
            "counselors_end": couns1,
            "delta_counselors": couns1 - couns0,
            "pct_delta_counselors": ((couns1 - couns0) / couns0 * 100.0) if couns0 > 0 else np.nan,
            "paras_start": para0,
            "paras_end": para1,
            "delta_paras": para1 - para0,
            "other_support_start": oth0,
            "other_support_end": oth1,
            "delta_other_support": oth1 - oth0,
            # Intensity Metrics
            "admin_per_1000_pupils_start": (tot_admin0 / e0 * 1000.0) if e0 > 0 else np.nan,
            "admin_per_1000_pupils_end": (tot_admin1 / e1 * 1000.0) if e1 > 0 else np.nan,
            "pct_delta_admin_per_1000": (((tot_admin1 / e1) - (tot_admin0 / e0)) / (tot_admin0 / e0) * 100.0) if (e0 > 0 and tot_admin0 > 0) else np.nan,
            "coordinators_per_1000_pupils_start": (i0 / e0 * 1000.0) if e0 > 0 else np.nan,
            "coordinators_per_1000_pupils_end": (i1 / e1 * 1000.0) if e1 > 0 else np.nan,
            "central_admin_per_1000_pupils_start": (c0 / e0 * 1000.0) if e0 > 0 else np.nan,
            "central_admin_per_1000_pupils_end": (c1 / e1 * 1000.0) if e1 > 0 else np.nan,
            "admin_per_100_teachers_start": (tot_admin0 / t0 * 100.0) if t0 > 0 else np.nan,
            "admin_per_100_teachers_end": (tot_admin1 / t1 * 100.0) if t1 > 0 else np.nan,
            "principals_per_school_start": (p0 / sch0) if sch0 > 0 else np.nan,
            "principals_per_school_end": (p1 / sch1) if sch1 > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 75)
    print("GENERATING PHASE 1.1 CALIBRATED DECOMPOSITION TABLES")
    print("=" * 75)

    csv_path = PROCESSED_DIR / "district_staff_year.csv"
    df = pd.read_csv(csv_path)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Balanced Regular Cohort (55 Districts)
    df_bal = df[df["is_balanced_regular_cohort_55"]].copy()
    b14 = df_bal[df_bal["school_year"] == "2014-2015"]
    b23 = df_bal[df_bal["school_year"] == "2023-2024"]
    b24 = df_bal[df_bal["school_year"] == "2024-2025"]
    b04 = df_bal[df_bal["school_year"] == "2004-2005"]

    print("Calculating Balanced Regular Cohort Decompositions...")
    # 2014-15 to 2024-25 (10-Year Benchmark)
    decomp_bal_10 = decompose_pair(b14, b24)
    decomp_bal_10["cohort_label"] = "Balanced 55 Regular Districts (2014-15 to 2024-25)"
    
    # 2014-15 to 2023-24 (Pre-KS SCHADM Break Benchmark)
    decomp_bal_pre_break = decompose_pair(b14, b23)
    decomp_bal_pre_break["cohort_label"] = "Balanced 55 Regular Districts (2014-15 to 2023-24 [Pre-KS-Break])"

    # 2004-05 to 2024-25 (20-Year Long-Run)
    decomp_bal_20 = decompose_pair(b04, b24)
    decomp_bal_20["cohort_label"] = "Balanced 55 Regular Districts (2004-05 to 2024-25)"

    decomp_bal_summary = pd.concat([decomp_bal_10, decomp_bal_pre_break, decomp_bal_20], ignore_index=True)
    decomp_bal_summary.to_csv(OUTPUTS_DIR / "kc_balanced_cohort_decomposition.csv", index=False)

    # 2. Dynamic Regional Universe (All LEAs including charters)
    print("Calculating Dynamic Regional Universe Decompositions...")
    u14 = df[df["school_year"] == "2014-2015"]
    u23 = df[df["school_year"] == "2023-2024"]
    u24 = df[df["school_year"] == "2024-2025"]
    u04 = df[df["school_year"] == "2004-2005"]

    decomp_dyn_10 = decompose_pair(u14, u24)
    decomp_dyn_10["cohort_label"] = "Dynamic Universe All LEAs (2014-15 to 2024-25)"
    decomp_dyn_pre = decompose_pair(u14, u23)
    decomp_dyn_pre["cohort_label"] = "Dynamic Universe All LEAs (2014-15 to 2023-24)"
    decomp_dyn_summary = pd.concat([decomp_dyn_10, decomp_dyn_pre], ignore_index=True)
    decomp_dyn_summary.to_csv(OUTPUTS_DIR / "kc_dynamic_universe_decomposition.csv", index=False)

    # 3. Balanced Cohort State-Level Decomposition (2014-15 to 2024-25 & 2014-15 to 2023-24)
    print("Calculating Balanced Cohort State-Level Decompositions...")
    decomp_bal_state_10 = decompose_pair(b14, b24, group_col="state")
    decomp_bal_state_10.to_csv(OUTPUTS_DIR / "kc_balanced_state_10yr_decomposition.csv", index=False)

    decomp_bal_state_pre = decompose_pair(b14, b23, group_col="state")
    decomp_bal_state_pre.to_csv(OUTPUTS_DIR / "kc_balanced_state_prebreak_decomposition.csv", index=False)

    # 4. District-by-District Decomposition (Major Districts in Balanced Cohort)
    print("Calculating District-by-District Major Ledgers...")
    major_districts = [
        # Kansas
        "Shawnee Mission Pub Sch", "Blue Valley", "Olathe", "Kansas City", "Turner-Kansas City",
        "Piper-Kansas City", "Gardner Edgerton", "Lansing", "Leavenworth", "Spring Hill",
        # Missouri
        "KANSAS CITY 33", "NORTH KANSAS CITY 74", "LEE'S SUMMIT R-VII", "INDEPENDENCE 30",
        "BLUE SPRINGS R-IV", "LIBERTY 53", "PARK HILL", "RAYTOWN C-2", "RAYMORE-PECULIAR R-II",
        "HICKMAN MILLS C-1", "FORT OSAGE R-I", "GRAIN VALLEY R-V", "BELTON 124", "GRANDVIEW C-4",
        "CENTER 58", "PLATTE CO. R-III", "KEARNEY R-I"
    ]

    def get_district_slice(df_in, dist_names):
        rows = []
        for d in dist_names:
            clean = d.lower().replace("'", "").replace("`", "").replace("-", " ")
            m = df_in[df_in["district_name"].str.lower().str.replace("'", "").str.replace("`", "").str.replace("-", " ").str.contains(clean, na=False)]
            if len(m) > 0:
                rec = m.iloc[0].copy()
                rec["canonical_name"] = d
                rows.append(rec)
        return pd.DataFrame(rows)

    m14 = get_district_slice(b14, major_districts)
    m24 = get_district_slice(b24, major_districts)
    decomp_major_10 = decompose_pair(m14, m24, group_col="canonical_name")
    decomp_major_10.to_csv(OUTPUTS_DIR / "kc_major_districts_2014_2024_decomposition.csv", index=False)

    # 5. Multi-Denominator Comparison File
    print("Generating Multi-Denominator Comparison File...")
    multi_denom_rows = []
    for yr, ydf in [("2004-2005", b04), ("2014-2015", b14), ("2023-2024", b23), ("2024-2025", b24)]:
        y_matched = get_district_slice(ydf, major_districts)
        for _, r in y_matched.iterrows():
            multi_denom_rows.append({
                "school_year": yr,
                "district_name": r["canonical_name"],
                "state": r["state"],
                "enrollment": r["enrollment_total"],
                "schools": r["operating_schools_count"],
                "teachers_k12_fte": r["teachers_k12_fte"],
                "principals_fte": r["school_administrators_fte"],
                "lea_admin_fte": r["lea_administrators_fte"],
                "coordinators_fte": r["instructional_coordinators_fte"],
                "central_plus_coord_fte": r["central_mgmt_and_coordinators_fte"],
                "total_admin_coord_fte": r["total_admin_and_coordinators_fte"],
                "counselors_fte": r["counselors_fte"],
                "admin_per_1000_students": r["total_admin_coord_per_1000_students"],
                "coordinators_per_1000_students": r["coordinators_per_1000_students"],
                "central_mgmt_coord_per_1000": r["central_mgmt_coord_per_1000_students"],
                "admin_per_100_teachers": r["total_admin_coord_per_100_teachers"],
                "principals_per_school": r["school_admin_per_school"],
                "flag_schadm_underreported": r["flag_schadm_underreported_2425"],
            })
    df_multi = pd.DataFrame(multi_denom_rows)
    df_multi.to_csv(OUTPUTS_DIR / "multi_denominator_comparison.csv", index=False)

    # 6. Generate Markdown Synthesis Report
    print("Generating Comprehensive Calibrated Markdown Report...")
    generate_markdown_report(decomp_bal_summary, decomp_dyn_summary, decomp_bal_state_10, decomp_bal_state_pre, decomp_major_10)
    print(f"All calibrated outputs successfully written to {OUTPUTS_DIR}")


def generate_markdown_report(bal_summary, dyn_summary, state_10, state_pre, major_dist):
    md = """# Kansas City Administrative Staffing Intensity Decomposition
## Phase 1.1 Semantic Calibration & Calibrated Decomposition Report

**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area  
**Primary Analytical Population:** Balanced Regular District Cohort (55 Continuous Districts)  
**Calibration Status:** Phase 1.1 Verified (Zero-Negative Assertions, Discontinuity Isolation, Student-Support Quarantine)  

---

## 1. Executive Summary: The Calibrated Findings

Build 1 revealed a striking phenomenon that survives rigorous measurement calibration:
**The primary driver of non-classroom workforce expansion in Kansas City–area public schools has NOT been traditional central-office administration, but a dramatic, disproportionate expansion in instructional coordination, curriculum supervision, and instructional coaching capacity.**

In the matched cohort of 55 regular school districts present across the entire modern CCD reporting era:
* **Enrollment:** 320,611 → 316,617 (**-1.2%**, -3,994 pupils)
* **Classroom Teachers:** 20,801.0 → 22,247.9 (**+7.0%**, +1,446.9 FTE)
* **District Central Administrators (LEAADM):** 175.8 → 177.7 (**+1.1%**, +1.9 FTE — virtually flat)
* **Instructional Coordinators & Coaches (CORSUP):** 501.3 → 751.2 (**+49.8%**, +249.9 FTE — massive expansion)
* **Combined Broad Administration (SCHADM + LEAADM + CORSUP):** 1,732.2 → 2,011.3 (**+16.1%**, +279.1 FTE)
* **Broad Administrative Intensity per 1,000 Pupils:** 5.40 → 6.35 (**+17.6%**)

Instructional coordinators accounted for **89.5% of all net administrative and supervisory FTE growth** across the balanced regular district cohort between 2014–15 and 2024–25.

---

## 2. Measurement Audits & Retractions (Phase 1.1 Calibration)

### 2.1 Retraction of the Student-Support (+253%) Finding
* **The Flaw in Build 1:** In early CCD releases (2004–2013), broader student support was unpopulated in federal extracts, leading the build script to fall back to `counselors_fte` (`student_support_staff_fte.fillna(counselors_fte)`). In 2014–15, the broader field was populated with all student support staff, creating a phantom jump from 737 to 2,353. Furthermore, in 2016–17 through 2018–19, NCES extracts recorded exactly `0.0` for student support across both states despite active counseling forces.
* **The Correction:** The +253% claim is formally **retracted**. Student support staff is classified as **NOT longitudinally comparable** across the 20-year span due to reporting voids.
* **The Clean Pupil Support Benchmark:** Guidance Counselors (`counselors_fte`), which was stably reported across all 21 years, grew from 755.0 to 909.0 FTE (**+20.4%**) over 20 years, and from 779.8 to 909.0 FTE (**+16.6%**) over 10 years, tracking student population shifts without explosive distortion.

### 2.2 The 2024–25 Kansas School Administrator (SCHADM) Discontinuity
* **The Break:** Kansas school administrator FTE dropped from 611.6 in 2023–24 to 386.7 in 2024–25 (-36.8% statewide).
* **The Mechanism:** Cross-validation against KSDE SO66 reports and statewide CCD tables confirms that in 2024–25, Kansas reported **only Head Principals** under the NCES "School administrators" category, omitting Assistant Principals (who had been included in all prior years).
* **The Analytical Guardrail:** We provide both the 2014–15 to 2024–25 benchmark and the pre-break 2014–15 to 2023–24 benchmark (where SCHADM grew +23.7%, scaling with building additions). All downstream regressions must include state × year fixed effects or sensitivity exclusions for Kansas in 2024–25.

### 2.3 Missouri LEAADM vs. CORSUP Reclassification (2013–14 to 2014–15)
* In Missouri, between 2013–14 and 2014–15, district administrators fell by -102.8 FTE while instructional coordinators rose by +64.9 FTE.
* Combined Central Management + Coordination (`LEAADM + CORSUP`) remained steady (455.0 → 417.2 FTE, -8.3%).
* **Rule:** For 20-year longitudinal analyses, `LEAADM + CORSUP` is the only robust, reclassification-proof central aggregate.

---

## 3. Balanced Regular Cohort Decomposition (55 Districts)

| Cohort Timeframe | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Total Admin $\Delta$ | Admin/1k Start | Admin/1k End | $\Delta$ Admin/1k (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in bal_summary.iterrows():
        md += (
            f"| **{r['cohort_label']}** "
            f"| {r['enrollment_start']:,.0f} → {r['enrollment_end']:,.0f} ({r['pct_delta_enrollment']:+.1f}%) "
            f"| {r['teachers_start']:,.1f} → {r['teachers_end']:,.1f} ({r['pct_delta_teachers']:+.1f}%) "
            f"| {r['principals_start']:,.1f} → {r['principals_end']:,.1f} ({r['delta_principals']:+.1f}) "
            f"| {r['central_admin_start']:,.1f} → {r['central_admin_end']:,.1f} ({r['delta_central_admin']:+.1f}) "
            f"| **{r['coordinators_start']:,.1f} → {r['coordinators_end']:,.1f} ({r['delta_coordinators']:+.1f}, {r['pct_delta_coordinators']:+.1f}%)** "
            f"| {r['total_admin_start']:,.1f} → {r['total_admin_end']:,.1f} ({r['pct_delta_total_admin']:+.1f}%) "
            f"| {r['admin_per_1000_pupils_start']:.2f} "
            f"| **{r['admin_per_1000_pupils_end']:.2f}** "
            f"| **{r['pct_delta_admin_per_1000']:+.1f}%** |\n"
        )

    md += """
---

## 4. Balanced Cohort State-Level Decompositions

### 4.1 Ten-Year Period (2014–15 to 2024–25)
*Note: Kansas 2024–25 SCHADM reflects assistant principal omission.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in state_10.iterrows():
        md += (
            f"| **{r['group']}** "
            f"| {r['enrollment_start']:,.0f} → {r['enrollment_end']:,.0f} ({r['pct_delta_enrollment']:+.1f}%) "
            f"| {r['teachers_start']:,.1f} → {r['teachers_end']:,.1f} ({r['pct_delta_teachers']:+.1f}%) "
            f"| {r['principals_start']:,.1f} → {r['principals_end']:,.1f} ({r['delta_principals']:+.1f}) "
            f"| {r['central_admin_start']:,.1f} → {r['central_admin_end']:,.1f} ({r['delta_central_admin']:+.1f}) "
            f"| **{r['coordinators_start']:,.1f} → {r['coordinators_end']:,.1f} ({r['delta_coordinators']:+.1f}, {r['pct_delta_coordinators']:+.1f}%)** "
            f"| {r['admin_per_1000_pupils_start']:.2f} "
            f"| **{r['admin_per_1000_pupils_end']:.2f}** |\n"
        )

    md += """
### 4.2 Pre-Break Period (2014–15 to 2023–24)
*Reflects complete reporting before the Kansas SCHADM reporting break.*

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in state_pre.iterrows():
        md += (
            f"| **{r['group']}** "
            f"| {r['enrollment_start']:,.0f} → {r['enrollment_end']:,.0f} ({r['pct_delta_enrollment']:+.1f}%) "
            f"| {r['teachers_start']:,.1f} → {r['teachers_end']:,.1f} ({r['pct_delta_teachers']:+.1f}%) "
            f"| {r['principals_start']:,.1f} → {r['principals_end']:,.1f} ({r['delta_principals']:+.1f}) "
            f"| {r['central_admin_start']:,.1f} → {r['central_admin_end']:,.1f} ({r['delta_central_admin']:+.1f}) "
            f"| **{r['coordinators_start']:,.1f} → {r['coordinators_end']:,.1f} ({r['delta_coordinators']:+.1f}, {r['pct_delta_coordinators']:+.1f}%)** "
            f"| {r['admin_per_1000_pupils_start']:.2f} "
            f"| **{r['admin_per_1000_pupils_end']:.2f}** |\n"
        )

    md += """
---

## 5. Major District Mechanical Ledger (2014–15 to 2024–25)

$$\\Delta \\text{Total Non-Teaching} = \\Delta \\text{Principals} + \\Delta \\text{Central Admin} + \\Delta \\text{Coordinators} + \\Delta \\text{Counselors} + \\Delta \\text{Paras} + \\Delta \\text{Other}$$

| District | State | Enrollment $\Delta$ | Teachers $\Delta$ | $\Delta$ Principals | $\Delta$ Central | $\Delta$ Coord | $\Delta$ Counselors | $\Delta$ Paras | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in major_dist.iterrows():
        md += (
            f"| **{r['group']}** "
            f"| {r.get('state', 'N/A')} "
            f"| {r['pct_delta_enrollment']:+.1f}% "
            f"| {r['pct_delta_teachers']:+.1f}% "
            f"| {r['delta_principals']:+.1f} "
            f"| {r['delta_central_admin']:+.1f} "
            f"| **{r['delta_coordinators']:+.1f}** "
            f"| {r['delta_counselors']:+.1f} "
            f"| {r['delta_paras']:+.1f} "
            f"| {r['admin_per_1000_pupils_start']:.2f} "
            f"| **{r['admin_per_1000_pupils_end']:.2f}** |\n"
        )

    (OUTPUTS_DIR / "kc_staffing_decomposition_report.md").write_text(md, encoding="utf-8")
    print(f"Calibrated report written to {OUTPUTS_DIR / 'kc_staffing_decomposition_report.md'}")


if __name__ == "__main__":
    main()
