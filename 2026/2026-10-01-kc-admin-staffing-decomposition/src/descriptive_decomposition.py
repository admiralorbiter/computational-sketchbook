"""
Descriptive Administrative-Intensity Decomposition Engine.

Generates the mechanical non-teaching staffing decomposition and
multi-denominator intensity comparison across Kansas City public school districts
over 10-year (2014–2024) and 20-year (2004–2024) spans.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"


def format_change(v0, v1):
    diff = v1 - v0
    pct = (diff / v0 * 100.0) if (v0 is not None and v0 > 0) else np.nan
    pct_str = f"{pct:+.1f}%" if pd.notna(pct) else "N/A"
    return diff, pct, f"{v0:.1f} → {v1:.1f} ({diff:+.1f}, {pct_str})"


def decompose_pair(df_start: pd.DataFrame, df_end: pd.DataFrame, group_col: str = None):
    """Compute mechanical decomposition between two cross-sections."""
    if group_col:
        s0 = df_start.groupby(group_col).sum(numeric_only=True)
        s1 = df_end.groupby(group_col).sum(numeric_only=True)
        keys = sorted(list(set(s0.index).intersection(set(s1.index))))
    else:
        s0 = pd.DataFrame([df_start.sum(numeric_only=True)], index=["Region"])
        s1 = pd.DataFrame([df_end.sum(numeric_only=True)], index=["Region"])
        keys = ["Region"]

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
        ss0, ss1 = r0.get("student_support_staff_fte", 0), r1.get("student_support_staff_fte", 0)
        para0, para1 = r0.get("paraprofessionals_fte", 0), r1.get("paraprofessionals_fte", 0)
        oth0, oth1 = (
            (r0.get("other_support_staff_fte", 0) + r0.get("school_admin_support_fte", 0) + r0.get("lea_admin_support_fte", 0)),
            (r1.get("other_support_staff_fte", 0) + r1.get("school_admin_support_fte", 0) + r1.get("lea_admin_support_fte", 0)),
        )

        tot_admin0 = p0 + c0 + i0
        tot_admin1 = p1 + c1 + i1
        tot_nonteach0 = p0 + c0 + i0 + ss0 + para0 + oth0
        tot_nonteach1 = p1 + c1 + i1 + ss1 + para1 + oth1

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
            "central_admin_start": c0,
            "central_admin_end": c1,
            "delta_central_admin": c1 - c0,
            "coordinators_start": i0,
            "coordinators_end": i1,
            "delta_coordinators": i1 - i0,
            "student_support_start": ss0,
            "student_support_end": ss1,
            "delta_student_support": ss1 - ss0,
            "paras_start": para0,
            "paras_end": para1,
            "delta_paras": para1 - para0,
            "other_support_start": oth0,
            "other_support_end": oth1,
            "delta_other_support": oth1 - oth0,
            "total_admin_start": tot_admin0,
            "total_admin_end": tot_admin1,
            "delta_total_admin": tot_admin1 - tot_admin0,
            "pct_delta_total_admin": ((tot_admin1 - tot_admin0) / tot_admin0 * 100.0) if tot_admin0 > 0 else np.nan,
            "delta_total_nonteaching": tot_nonteach1 - tot_nonteach0,
            # Intensity Ratios
            "admin_per_1000_pupils_start": (tot_admin0 / e0 * 1000.0) if e0 > 0 else np.nan,
            "admin_per_1000_pupils_end": (tot_admin1 / e1 * 1000.0) if e1 > 0 else np.nan,
            "coordinators_per_1000_pupils_start": (i0 / e0 * 1000.0) if e0 > 0 else np.nan,
            "coordinators_per_1000_pupils_end": (i1 / e1 * 1000.0) if e1 > 0 else np.nan,
            "admin_per_100_teachers_start": (tot_admin0 / t0 * 100.0) if t0 > 0 else np.nan,
            "admin_per_100_teachers_end": (tot_admin1 / t1 * 100.0) if t1 > 0 else np.nan,
            "principals_per_school_start": (p0 / sch0) if sch0 > 0 else np.nan,
            "principals_per_school_end": (p1 / sch1) if sch1 > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 70)
    print("GENERATING DESCRIPTIVE ADMINISTRATIVE-INTENSITY DECOMPOSITION")
    print("=" * 70)

    csv_path = PROCESSED_DIR / "district_staff_year.csv"
    df = pd.read_csv(csv_path)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Filter slices
    df_2004 = df[df["school_year"] == "2004-2005"].copy()
    df_2014 = df[df["school_year"] == "2014-2015"].copy()
    df_2024 = df[df["school_year"] == "2024-2025"].copy()

    # 1. Metropolitan Aggregate (10-Year and 20-Year)
    print("\nCalculating Metropolitan Aggregates...")
    decomp_10yr_reg = decompose_pair(df_2014, df_2024)
    decomp_10yr_reg["timeframe"] = "2014-15 to 2024-25"
    decomp_20yr_reg = decompose_pair(df_2004, df_2024)
    decomp_20yr_reg["timeframe"] = "2004-05 to 2024-25"

    decomp_summary = pd.concat([decomp_10yr_reg, decomp_20yr_reg], ignore_index=True)
    decomp_summary.to_csv(OUTPUTS_DIR / "kc_metro_staffing_decomposition_summary.csv", index=False)

    # 2. State & Typology Aggregates (10-Year)
    print("Calculating State & Typology Aggregates...")
    decomp_state = decompose_pair(df_2014, df_2024, group_col="state")
    decomp_state.to_csv(OUTPUTS_DIR / "kc_state_10yr_decomposition.csv", index=False)

    decomp_typo = decompose_pair(df_2014, df_2024, group_col="typology")
    decomp_typo.to_csv(OUTPUTS_DIR / "kc_typology_10yr_decomposition.csv", index=False)

    # 3. District-by-District Decomposition (Major Districts)
    print("Calculating District-by-District Decomposition...")
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

    # Subset matched major districts
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

    m14 = get_district_slice(df_2014, major_districts)
    m24 = get_district_slice(df_2024, major_districts)
    decomp_dist_10 = decompose_pair(m14, m24, group_col="canonical_name")
    decomp_dist_10.to_csv(OUTPUTS_DIR / "kc_major_districts_2014_2024_decomposition.csv", index=False)

    # 20-Year Major Districts
    m04 = get_district_slice(df_2004, major_districts)
    m24_matched = get_district_slice(df_2024, m04["canonical_name"].unique())
    decomp_dist_20 = decompose_pair(m04, m24_matched, group_col="canonical_name")
    decomp_dist_20.to_csv(OUTPUTS_DIR / "kc_major_districts_2004_2024_decomposition.csv", index=False)

    # 4. Multi-Denominator Comparison Table
    print("Generating Multi-Denominator Comparison Ledger...")
    multi_denom_rows = []
    years_to_check = [("2004-2005", df_2004), ("2014-2015", df_2014), ("2024-2025", df_2024)]
    for yr, ydf in years_to_check:
        y_matched = get_district_slice(ydf, major_districts)
        for _, r in y_matched.iterrows():
            multi_denom_rows.append({
                "school_year": yr,
                "district_name": r["canonical_name"],
                "state": r["state"],
                "enrollment": r["enrollment_total"],
                "schools": r["operating_schools_count"],
                "teachers_k12_fte": r["teachers_k12_fte"],
                "core_admin_fte": r["core_admin_fte"],
                "coordinators_fte": r["instructional_coordinators_fte"],
                "total_admin_coord_fte": r["total_admin_and_coordinators_fte"],
                "student_support_fte": r["student_support_staff_fte"],
                "admin_per_1000_students": r["total_admin_coord_per_1000_students"],
                "core_admin_per_1000_students": r["core_admin_per_1000_students"],
                "coordinators_per_1000_students": r["coordinators_per_1000_students"],
                "admin_per_100_teachers": r["total_admin_coord_per_100_teachers"],
                "admin_share_of_staff_pct": r["admin_coord_share_of_total_staff_pct"],
                "principals_per_school": r["school_admin_per_school"],
                "students_per_principal": r["students_per_school_admin"],
            })
    df_multi = pd.DataFrame(multi_denom_rows)
    df_multi.to_csv(OUTPUTS_DIR / "multi_denominator_comparison.csv", index=False)

    # 5. Generate Markdown Summaries
    print("Generating Markdown Artifacts...")
    generate_markdown_tables(decomp_summary, decomp_state, decomp_typo, decomp_dist_10, df_multi)
    print(f"All decomposition artifacts written to {OUTPUTS_DIR}")


def generate_markdown_tables(decomp_summary, decomp_state, decomp_typo, decomp_dist, df_multi):
    # Summary Report Markdown
    md_content = f"""# Kansas City Administrative Staffing Intensity Decomposition
## Descriptive Ledger & Mechanical Decomposition (Build 1)

**Coverage:** Bi-State Kansas City Metropolitan Area (9 MARC Counties)  
**Time Horizons:** 10-Year (2014–15 to 2024–25) and 20-Year (2004–05 to 2024–25)  
**Data Sources:** Official NCES CCD LEA Releases, Urban Institute Harmonized Historical CCD API  

---

## 1. Metropolitan Aggregate Overview

| Timeframe | Enrollment $\Delta$ | Schools $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Student Support $\Delta$ | Total Admin $\Delta$ | Admin/1,000 Pupils | Admin/100 Teachers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in decomp_summary.iterrows():
        md_content += (
            f"| **{r['timeframe']}** | {r['enrollment_start']:,.0f} → {r['enrollment_end']:,.0f} ({r['pct_delta_enrollment']:+.1f}%) "
            f"| {r['schools_start']:,.0f} → {r['schools_end']:,.0f} ({r['delta_schools']:+.0f}) "
            f"| {r['teachers_start']:,.1f} → {r['teachers_end']:,.1f} ({r['pct_delta_teachers']:+.1f}%) "
            f"| {r['principals_start']:,.1f} → {r['principals_end']:,.1f} ({r['delta_principals']:+.1f}) "
            f"| {r['central_admin_start']:,.1f} → {r['central_admin_end']:,.1f} ({r['delta_central_admin']:+.1f}) "
            f"| **{r['coordinators_start']:,.1f} → {r['coordinators_end']:,.1f} ({r['delta_coordinators']:+.1f})** "
            f"| {r['student_support_start']:,.1f} → {r['student_support_end']:,.1f} ({r['delta_student_support']:+.1f}) "
            f"| {r['total_admin_start']:,.1f} → {r['total_admin_end']:,.1f} ({r['pct_delta_total_admin']:+.1f}%) "
            f"| {r['admin_per_1000_pupils_start']:.2f} → {r['admin_per_1000_pupils_end']:.2f} "
            f"| {r['admin_per_100_teachers_start']:.1f} → {r['admin_per_100_teachers_end']:.1f} |\n"
        )

    md_content += """
---

## 2. 10-Year Decomposition by State Sub-Region (2014–15 to 2024–25)

| State | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Student Support $\Delta$ | Admin/1,000 Pupils |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in decomp_state.iterrows():
        md_content += (
            f"| **{r['group']}** | {r['pct_delta_enrollment']:+.1f}% ({r['delta_enrollment']:+,.0f}) "
            f"| {r['pct_delta_teachers']:+.1f}% ({r['delta_teachers']:+,.1f}) "
            f"| {r['principals_start']:.1f} → {r['principals_end']:.1f} ({r['delta_principals']:+.1f}) "
            f"| {r['central_admin_start']:.1f} → {r['central_admin_end']:.1f} ({r['delta_central_admin']:+.1f}) "
            f"| **{r['coordinators_start']:.1f} → {r['coordinators_end']:.1f} ({r['delta_coordinators']:+.1f})** "
            f"| {r['student_support_start']:.1f} → {r['student_support_end']:.1f} ({r['delta_student_support']:+.1f}) "
            f"| {r['admin_per_1000_pupils_start']:.2f} → {r['admin_per_1000_pupils_end']:.2f} |\n"
        )

    md_content += """
---

## 3. 10-Year Decomposition by Typology (2014–15 to 2024–25)

| Typology | Enrollment $\Delta$ | Teachers $\Delta$ | Principals $\Delta$ | Central Admin $\Delta$ | Coordinators $\Delta$ | Total Admin $\Delta$ | Admin/1,000 Pupils |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in decomp_typo.iterrows():
        md_content += (
            f"| **{r['group']}** | {r['pct_delta_enrollment']:+.1f}% "
            f"| {r['pct_delta_teachers']:+.1f}% "
            f"| {r['delta_principals']:+.1f} "
            f"| {r['delta_central_admin']:+.1f} "
            f"| **{r['delta_coordinators']:+.1f}** "
            f"| {r['delta_total_admin']:+.1f} ({r['pct_delta_total_admin']:+.1f}%) "
            f"| {r['admin_per_1000_pupils_start']:.2f} → {r['admin_per_1000_pupils_end']:.2f} |\n"
        )

    md_content += """
---

## 4. Major District 10-Year Mechanical Decomposition (2014–15 to 2024–25)

$$\\Delta \\text{Total Non-Teaching} = \\Delta \\text{Principals} + \\Delta \\text{Central Admin} + \\Delta \\text{Coordinators} + \\Delta \\text{Student Support} + \\Delta \\text{Paraprofessionals} + \\Delta \\text{Operations/Other}$$

| District | Enrollment $\Delta$ | Teachers $\Delta$ | $\Delta$ Principals | $\Delta$ Central | $\Delta$ Coord | $\Delta$ Support | $\Delta$ Paras | Admin/1k Start | Admin/1k End |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, r in decomp_dist.iterrows():
        md_content += (
            f"| **{r['group']}** | {r['pct_delta_enrollment']:+.1f}% "
            f"| {r['pct_delta_teachers']:+.1f}% "
            f"| {r['delta_principals']:+.1f} "
            f"| {r['delta_central_admin']:+.1f} "
            f"| **{r['delta_coordinators']:+.1f}** "
            f"| {r['delta_student_support']:+.1f} "
            f"| {r['delta_paras']:+.1f} "
            f"| {r['admin_per_1000_pupils_start']:.2f} "
            f"| **{r['admin_per_1000_pupils_end']:.2f}** |\n"
        )

    (OUTPUTS_DIR / "kc_staffing_decomposition_report.md").write_text(md_content, encoding="utf-8")
    print(f"Generated Markdown report: {OUTPUTS_DIR / 'kc_staffing_decomposition_report.md'}")


if __name__ == "__main__":
    main()
