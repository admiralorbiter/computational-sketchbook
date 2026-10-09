"""
Analysis: Replicate and compute exact findings for three bounded measurement studies
across Missouri high schools (2021-22 CRDC & NCES CCD).

Outputs:
- Study 1: AP vs. Dual-Enrollment 4-cell table, conditional rates, and sensitivity.
- Study 2: AP Computer Science concealment rate among AP schools.
- Study 3: Physics provision denominator wedge (school-level vs student-level).
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"


def load_panel():
    parquet_path = DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing processed panel at {parquet_path}. Run build_panel.py first.")
    return pd.read_parquet(parquet_path)


def run_study_1(df_307, df_317):
    """Study 1: AP vs. Dual Enrollment Blind Spots."""
    print("\n" + "=" * 70)
    print("STUDY 1 (PILOT): AP vs. DUAL ENROLLMENT PARTICIPATION")
    print("=" * 70)

    # 4-Cell Contingency Table for 307 consistent schools
    ct_307 = pd.crosstab(
        df_307["ap_indicator_raw"],
        df_307["dual_indicator_raw"],
        margins=True,
        margins_name="Total"
    )
    print("\n[Baseline: 307 Consistent 9-12 High Schools]")
    print(ct_307)

    # Percentages of total
    ct_pct = (pd.crosstab(
        df_307["ap_indicator_raw"],
        df_307["dual_indicator_raw"],
        margins=True,
        margins_name="Total",
        normalize="all"
    ) * 100).round(2)
    print("\n[Baseline Table (% of Total 307 Schools)]")
    print(ct_pct)

    # Conditional rate: Dual Enrollment among No-AP schools
    no_ap_307 = df_307[df_307["ap_indicator_raw"] == "No"]
    n_no_ap_307 = len(no_ap_307)
    n_dual_in_no_ap_307 = (no_ap_307["dual_indicator_raw"] == "Yes").sum()
    rate_307 = (n_dual_in_no_ap_307 / n_no_ap_307) * 100

    print(f"\nNo-AP High Schools: {n_no_ap_307} of 307 ({n_no_ap_307 / 307 * 100:.1f}%)")
    print(f"Dual Enrollment among No-AP: {n_dual_in_no_ap_307} of {n_no_ap_307} = {rate_307:.1f}% ({rate_307:.3f}%)")

    # Sensitivity: 317 Matched Schools (includes 10 conflicting grade-span schools)
    no_ap_317 = df_317[df_317["ap_indicator_raw"] == "No"]
    n_no_ap_317 = len(no_ap_317)
    n_dual_in_no_ap_317 = (no_ap_317["dual_indicator_raw"] == "Yes").sum()
    rate_317 = (n_dual_in_no_ap_317 / n_no_ap_317) * 100

    print("\n[Sensitivity Check: 317 Matched High Schools (Broad Sample)]")
    print(f"No-AP High Schools: {n_no_ap_317} of 317 ({n_no_ap_317 / 317 * 100:.1f}%)")
    print(f"Dual Enrollment among No-AP: {n_dual_in_no_ap_317} of {n_no_ap_317} = {rate_317:.1f}% ({rate_317:.3f}%)")
    print(f"Sensitivity delta: {rate_317 - rate_307:+.2f} percentage points")

    # Save summary table
    res_df = pd.DataFrame([
        {"sample": "Consistent Grades 9-12 (Baseline)", "total_schools": 307, "no_ap_schools": n_no_ap_307, "dual_in_no_ap": n_dual_in_no_ap_307, "dual_pct_of_no_ap": round(rate_307, 3), "neither_count": (no_ap_307["dual_indicator_raw"] == "No").sum()},
        {"sample": "All Matched (Sensitivity)", "total_schools": 317, "no_ap_schools": n_no_ap_317, "dual_in_no_ap": n_dual_in_no_ap_317, "dual_pct_of_no_ap": round(rate_317, 3), "neither_count": (no_ap_317["dual_indicator_raw"] == "No").sum()}
    ])
    res_df.to_csv(DATA_PROCESSED / "study1_ap_dual_summary.csv", index=False)
    return res_df


def run_study_2(df_307, df_317):
    """Study 2: AP Computer Science Subject Concealment."""
    print("\n" + "=" * 70)
    print("STUDY 2: CURRICULAR CONCEALMENT (AP COMPUTER SCIENCE)")
    print("=" * 70)

    # Baseline 307
    ap_schools_307 = df_307[df_307["ap_participating"]].copy()
    n_ap_307 = len(ap_schools_307)
    n_no_cs_307 = (ap_schools_307["ap_cs_indicator_raw"] == "No").sum()
    n_yes_cs_307 = (ap_schools_307["ap_cs_indicator_raw"] == "Yes").sum()
    pct_no_cs_307 = (n_no_cs_307 / n_ap_307) * 100

    print(f"[Baseline: 307 Consistent Sample]")
    print(f"AP-participating high schools: {n_ap_307} of 307 ({n_ap_307 / 307 * 100:.1f}%)")
    print(f"Schools reporting NO AP Computer Science: {n_no_cs_307} of {n_ap_307} = {pct_no_cs_307:.2f}%")
    print(f"Schools reporting YES AP Computer Science: {n_yes_cs_307} of {n_ap_307} = {n_yes_cs_307 / n_ap_307 * 100:.2f}%")

    # Sensitivity 317
    ap_schools_317 = df_317[df_317["ap_participating"]].copy()
    n_ap_317 = len(ap_schools_317)
    n_no_cs_317 = (ap_schools_317["ap_cs_indicator_raw"] == "No").sum()
    n_yes_cs_317 = (ap_schools_317["ap_cs_indicator_raw"] == "Yes").sum()
    pct_no_cs_317 = (n_no_cs_317 / n_ap_317) * 100

    print(f"\n[Sensitivity: 317 Broad Sample]")
    print(f"AP-participating high schools: {n_ap_317} of 317 ({n_ap_317 / 317 * 100:.1f}%)")
    print(f"Schools reporting NO AP Computer Science: {n_no_cs_317} of {n_ap_317} = {pct_no_cs_317:.2f}%")
    print(f"Sensitivity delta: {pct_no_cs_317 - pct_no_cs_307:+.2f} percentage points")

    res_df = pd.DataFrame([
        {"sample": "Consistent Grades 9-12 (Baseline)", "ap_schools": n_ap_307, "no_ap_cs_count": n_no_cs_307, "yes_ap_cs_count": n_yes_cs_307, "no_ap_cs_pct": round(pct_no_cs_307, 2)},
        {"sample": "All Matched (Sensitivity)", "ap_schools": n_ap_317, "no_ap_cs_count": n_no_cs_317, "yes_ap_cs_count": n_yes_cs_317, "no_ap_cs_pct": round(pct_no_cs_317, 2)}
    ])
    res_df.to_csv(DATA_PROCESSED / "study2_ap_cs_concealment.csv", index=False)
    return res_df


def run_study_3(df_307, df_317):
    """Study 3: Denominator Wedge in Physics Provision."""
    print("\n" + "=" * 70)
    print("STUDY 3: DENOMINATOR WEDGE (SCHOOLS vs. STUDENTS IN PHYSICS PROVISION)")
    print("=" * 70)

    # Baseline 307
    zero_phys_307 = df_307["physics_classes"] == 0
    n_zero_schools_307 = zero_phys_307.sum()
    total_schools_307 = len(df_307)
    school_pct_307 = (n_zero_schools_307 / total_schools_307) * 100

    total_enr_307 = df_307["crdc_total_enrollment"].sum()
    zero_enr_307 = df_307.loc[zero_phys_307, "crdc_total_enrollment"].sum()
    student_pct_307 = (zero_enr_307 / total_enr_307) * 100
    wedge_307 = school_pct_307 - student_pct_307

    mean_enr_zero_307 = df_307.loc[zero_phys_307, "crdc_total_enrollment"].mean()
    mean_enr_has_307 = df_307.loc[~zero_phys_307, "crdc_total_enrollment"].mean()
    med_enr_zero_307 = df_307.loc[zero_phys_307, "crdc_total_enrollment"].median()
    med_enr_has_307 = df_307.loc[~zero_phys_307, "crdc_total_enrollment"].median()

    print(f"[Baseline: 307 Consistent Sample]")
    print(f"Schools reporting 0 physics classes: {n_zero_schools_307} of {total_schools_307} = {school_pct_307:.2f}%")
    print(f"Students in zero-physics schools: {zero_enr_307:,.0f} of {total_enr_307:,.0f} = {student_pct_307:.2f}%")
    print(f"Denominator Wedge: {wedge_307:.2f} percentage points")
    print(f"Mean enrollment: Zero-Physics = {mean_enr_zero_307:.1f} (med: {med_enr_zero_307:.0f}) vs Physics = {mean_enr_has_307:.1f} (med: {med_enr_has_307:.0f})")

    # Sensitivity 317
    zero_phys_317 = df_317["physics_classes"] == 0
    n_zero_schools_317 = zero_phys_317.sum()
    total_schools_317 = len(df_317)
    school_pct_317 = (n_zero_schools_317 / total_schools_317) * 100

    total_enr_317 = df_317["crdc_total_enrollment"].sum()
    zero_enr_317 = df_317.loc[zero_phys_317, "crdc_total_enrollment"].sum()
    student_pct_317 = (zero_enr_317 / total_enr_317) * 100
    wedge_317 = school_pct_317 - student_pct_317

    print(f"\n[Sensitivity: 317 Broad Sample]")
    print(f"Schools reporting 0 physics classes: {n_zero_schools_317} of {total_schools_317} = {school_pct_317:.2f}%")
    print(f"Students in zero-physics schools: {zero_enr_317:,.0f} of {total_enr_317:,.0f} = {student_pct_317:.2f}%")
    print(f"Denominator Wedge: {wedge_317:.2f} percentage points")

    res_df = pd.DataFrame([
        {
            "sample": "Consistent Grades 9-12 (Baseline)",
            "total_schools": total_schools_307,
            "zero_phys_schools": n_zero_schools_307,
            "school_pct_zero": round(school_pct_307, 2),
            "total_students": int(total_enr_307),
            "zero_phys_students": int(zero_enr_307),
            "student_pct_zero": round(student_pct_307, 2),
            "denominator_wedge_pp": round(wedge_307, 2)
        },
        {
            "sample": "All Matched (Sensitivity)",
            "total_schools": total_schools_317,
            "zero_phys_schools": n_zero_schools_317,
            "school_pct_zero": round(school_pct_317, 2),
            "total_students": int(total_enr_317),
            "zero_phys_students": int(zero_enr_317),
            "student_pct_zero": round(student_pct_317, 2),
            "denominator_wedge_pp": round(wedge_317, 2)
        }
    ])
    res_df.to_csv(DATA_PROCESSED / "study3_physics_denominator_wedge.csv", index=False)
    return res_df


def main():
    panel = load_panel()
    df_307 = panel[panel["flag_consistent_9_12"]].copy()
    df_317 = panel[panel["flag_matched_crdc"]].copy()

    run_study_1(df_307, df_317)
    run_study_2(df_307, df_317)
    run_study_3(df_307, df_317)


if __name__ == "__main__":
    main()
