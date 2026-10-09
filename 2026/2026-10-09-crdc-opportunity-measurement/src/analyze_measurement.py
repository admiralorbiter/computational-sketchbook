"""
Analysis: Replicate and compute exact findings for three bounded measurement studies
across Missouri high schools (2021-22 CRDC & NCES CCD).

Methodological Guardrails:
1. Distinguishes nonnegative enrollment counts from CRDC negative administrative codes (-9 = skipped, -12 = suppressed).
   Enrollment totals are provisional sums of released nonnegative counts, with suppressed components held unresolved.
2. In Study 1, presents both the conditional dual enrollment rate among non-AP schools (105/113 = 92.9%)
   and the miss rate among schools reporting either route (105/299 = 35.1%).
3. In Study 2, strictly reports lack of reported student participation in AP Computer Science,
   without asserting whether courses were offered in a school catalog.
4. In Study 3, treats school-weighted and student-weighted metrics as describing different populations,
   explaining the 14.70 pp divergence via institutional enrollment scale without unmodeled geographic claims.
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
    """Study 1 (Pilot): AP vs. Dual Enrollment Participation."""
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

    # Percentages of total 307
    ct_pct = (pd.crosstab(
        df_307["ap_indicator_raw"],
        df_307["dual_indicator_raw"],
        margins=True,
        margins_name="Total",
        normalize="all"
    ) * 100).round(2)
    print("\n[Baseline Table (% of Total 307 Schools)]")
    print(ct_pct)

    # Metric A: Conditional rate among schools with NO AP
    no_ap_307 = df_307[df_307["ap_indicator_raw"] == "No"]
    n_no_ap_307 = len(no_ap_307)
    n_dual_in_no_ap_307 = (no_ap_307["dual_indicator_raw"] == "Yes").sum()
    rate_no_ap_307 = (n_dual_in_no_ap_307 / n_no_ap_307) * 100

    # Metric B: Miss rate among schools reporting EITHER route (AP or Dual, N = 105 + 180 + 14 = 299)
    either_route_307 = df_307[(df_307["ap_participating"]) | (df_307["dual_participating"])]
    n_either_307 = len(either_route_307)
    miss_rate_either_307 = (n_dual_in_no_ap_307 / n_either_307) * 100

    print(f"\nMetric A (Among Schools Reporting NO AP Participation):")
    print(f"  No-AP High Schools: {n_no_ap_307} of 307 ({n_no_ap_307 / 307 * 100:.1f}%)")
    print(f"  Dual Enrollment reported: {n_dual_in_no_ap_307} of {n_no_ap_307} = {rate_no_ap_307:.1f}% ({rate_no_ap_307:.3f}%)")

    print(f"\nMetric B (Miss Rate Among Schools Reporting EITHER Advanced Route, N={n_either_307}):")
    print(f"  Dual-Only Schools Missed by AP Indicator: {n_dual_in_no_ap_307} of {n_either_307} = {miss_rate_either_307:.1f}% ({miss_rate_either_307:.3f}%)")

    # Sensitivity: 317 Matched Schools (includes 10 conflicting grade-span schools)
    no_ap_317 = df_317[df_317["ap_indicator_raw"] == "No"]
    n_no_ap_317 = len(no_ap_317)
    n_dual_in_no_ap_317 = (no_ap_317["dual_indicator_raw"] == "Yes").sum()
    rate_no_ap_317 = (n_dual_in_no_ap_317 / n_no_ap_317) * 100

    either_route_317 = df_317[(df_317["ap_participating"]) | (df_317["dual_participating"])]
    n_either_317 = len(either_route_317)
    miss_rate_either_317 = (n_dual_in_no_ap_317 / n_either_317) * 100

    print("\n[Sensitivity Check: 317 Matched High Schools (Broad Sample)]")
    print(f"  Metric A (Dual among No AP): {n_dual_in_no_ap_317} of {n_no_ap_317} = {rate_no_ap_317:.1f}% ({rate_no_ap_317:.3f}%)")
    print(f"  Metric B (Miss rate among either route, N={n_either_317}): {n_dual_in_no_ap_317} of {n_either_317} = {miss_rate_either_317:.1f}% ({miss_rate_either_317:.3f}%)")
    print(f"  Sensitivity delta (Metric A): {rate_no_ap_317 - rate_no_ap_307:+.2f} percentage points")

    # Save summary table
    res_df = pd.DataFrame([
        {
            "sample": "Consistent Grades 9-12 (Baseline)",
            "total_schools": 307,
            "no_ap_schools": n_no_ap_307,
            "dual_in_no_ap": n_dual_in_no_ap_307,
            "dual_pct_of_no_ap": round(rate_no_ap_307, 3),
            "either_route_schools": n_either_307,
            "miss_rate_among_either": round(miss_rate_either_307, 3),
            "neither_count": (no_ap_307["dual_indicator_raw"] == "No").sum()
        },
        {
            "sample": "All Matched (Sensitivity)",
            "total_schools": 317,
            "no_ap_schools": n_no_ap_317,
            "dual_in_no_ap": n_dual_in_no_ap_317,
            "dual_pct_of_no_ap": round(rate_no_ap_317, 3),
            "either_route_schools": n_either_317,
            "miss_rate_among_either": round(miss_rate_either_317, 3),
            "neither_count": (no_ap_317["dual_indicator_raw"] == "No").sum()
        }
    ])
    res_df.to_csv(DATA_PROCESSED / "study1_ap_dual_summary.csv", index=False)
    return res_df


def run_study_2(df_307, df_317):
    """Study 2: AP Computer Science Reported Participation Concealment."""
    print("\n" + "=" * 70)
    print("STUDY 2: AP COMPUTER SCIENCE REPORTED PARTICIPATION CONCEALMENT")
    print("=" * 70)

    # Baseline 307
    ap_schools_307 = df_307[df_307["ap_participating"]].copy()
    n_ap_307 = len(ap_schools_307)
    n_no_cs_307 = (ap_schools_307["ap_cs_indicator_raw"] == "No").sum()
    n_yes_cs_307 = (ap_schools_307["ap_cs_indicator_raw"] == "Yes").sum()
    pct_no_cs_307 = (n_no_cs_307 / n_ap_307) * 100

    print(f"[Baseline: 307 Consistent Sample]")
    print(f"AP-participating high schools: {n_ap_307} of 307 ({n_ap_307 / 307 * 100:.1f}%)")
    print(f"Schools reporting NO AP Computer Science participation: {n_no_cs_307} of {n_ap_307} = {pct_no_cs_307:.2f}%")
    print(f"Schools reporting YES AP Computer Science participation: {n_yes_cs_307} of {n_ap_307} = {n_yes_cs_307 / n_ap_307 * 100:.2f}%")
    print("Note: This measures reported student participation, not whether courses were scheduled in a school catalog.")

    # Sensitivity 317
    ap_schools_317 = df_317[df_317["ap_participating"]].copy()
    n_ap_317 = len(ap_schools_317)
    n_no_cs_317 = (ap_schools_317["ap_cs_indicator_raw"] == "No").sum()
    n_yes_cs_317 = (ap_schools_317["ap_cs_indicator_raw"] == "Yes").sum()
    pct_no_cs_317 = (n_no_cs_317 / n_ap_317) * 100

    print(f"\n[Sensitivity: 317 Broad Sample]")
    print(f"AP-participating high schools: {n_ap_317} of 317 ({n_ap_317 / 317 * 100:.1f}%)")
    print(f"Schools reporting NO AP Computer Science participation: {n_no_cs_317} of {n_ap_317} = {pct_no_cs_317:.2f}%")
    print(f"Sensitivity delta: {pct_no_cs_317 - pct_no_cs_307:+.2f} percentage points")

    res_df = pd.DataFrame([
        {"sample": "Consistent Grades 9-12 (Baseline)", "ap_schools": n_ap_307, "no_ap_cs_count": n_no_cs_307, "yes_ap_cs_count": n_yes_cs_307, "no_ap_cs_pct": round(pct_no_cs_307, 2)},
        {"sample": "All Matched (Sensitivity)", "ap_schools": n_ap_317, "no_ap_cs_count": n_no_cs_317, "yes_ap_cs_count": n_yes_cs_317, "no_ap_cs_pct": round(pct_no_cs_317, 2)}
    ])
    res_df.to_csv(DATA_PROCESSED / "study2_ap_cs_concealment.csv", index=False)
    return res_df


def run_study_3(df_307, df_317):
    """
    Study 3: Denominator Wedge in Physics Provision.
    Uses released nonnegative enrollment counts, with suppressed values held unresolved.
    """
    print("\n" + "=" * 70)
    print("STUDY 3: DENOMINATOR WEDGE (SCHOOL AVAILABILITY vs. STUDENT EXPOSURE IN PHYSICS)")
    print("=" * 70)

    # Audit and assert that course counts contain verified non-null, nonnegative values before calculating zero provision
    assert df_307["physics_classes"].notna().all(), "Strict 307 cohort contains unverified missing physics counts"
    assert (df_307["physics_classes"] >= 0).all(), "Strict 307 cohort contains negative physics counts"
    assert df_317["physics_classes"].notna().all(), "Broad sensitivity cohort contains unverified missing physics counts"
    assert (df_317["physics_classes"] >= 0).all(), "Broad sensitivity cohort contains negative physics counts"

    # Baseline 307
    zero_phys_307 = df_307["physics_classes"] == 0
    n_zero_schools_307 = zero_phys_307.sum()
    total_schools_307 = len(df_307)
    school_pct_307 = (n_zero_schools_307 / total_schools_307) * 100

    # Released nonnegative enrollment
    rel_enr_307 = df_307["crdc_released_enrollment"].sum()
    zero_rel_enr_307 = df_307.loc[zero_phys_307, "crdc_released_enrollment"].sum()
    student_pct_307 = (zero_rel_enr_307 / rel_enr_307) * 100
    wedge_307 = school_pct_307 - student_pct_307

    mean_enr_zero_307 = df_307.loc[zero_phys_307, "crdc_released_enrollment"].mean()
    mean_enr_has_307 = df_307.loc[~zero_phys_307, "crdc_released_enrollment"].mean()
    med_enr_zero_307 = df_307.loc[zero_phys_307, "crdc_released_enrollment"].median()
    med_enr_has_307 = df_307.loc[~zero_phys_307, "crdc_released_enrollment"].median()

    n_suppressed_307 = df_307["flag_enr_suppressed"].sum()

    print(f"[Baseline: 307 Consistent Sample]")
    print(f"Schools reporting 0 physics classes: {n_zero_schools_307} of {total_schools_307} = {school_pct_307:.2f}% ({school_pct_307:.4f}%)")
    print(f"Released student enrollment across 307 schools: {rel_enr_307:,.0f}")
    print(f"Released student enrollment at zero-physics schools: {zero_rel_enr_307:,.0f}")
    print(f"Student-weighted percentage (provisional from released counts): {student_pct_307:.2f}% ({student_pct_307:.4f}%)")
    print(f"Denominator Wedge (School % - Student %): {wedge_307:.2f} percentage points ({wedge_307:.4f} pp)")
    print(f"Suppressed nonbinary records held unresolved: {n_suppressed_307} school(s)")
    print(f"Enrollment Scale: Zero-Physics Mean = {mean_enr_zero_307:.1f} (med: {med_enr_zero_307:.0f}) vs Physics Mean = {mean_enr_has_307:.1f} (med: {med_enr_has_307:.0f})")

    # Sensitivity 317
    zero_phys_317 = df_317["physics_classes"] == 0
    n_zero_schools_317 = zero_phys_317.sum()
    total_schools_317 = len(df_317)
    school_pct_317 = (n_zero_schools_317 / total_schools_317) * 100

    rel_enr_317 = df_317["crdc_released_enrollment"].sum()
    zero_rel_enr_317 = df_317.loc[zero_phys_317, "crdc_released_enrollment"].sum()
    student_pct_317 = (zero_rel_enr_317 / rel_enr_317) * 100
    wedge_317 = school_pct_317 - student_pct_317

    print(f"\n[Sensitivity: 317 Broad Sample]")
    print(f"Schools reporting 0 physics classes: {n_zero_schools_317} of {total_schools_317} = {school_pct_317:.2f}%")
    print(f"Released student enrollment across 317 schools: {rel_enr_317:,.0f}")
    print(f"Released student enrollment at zero-physics schools: {zero_rel_enr_317:,.0f}")
    print(f"Student-weighted percentage (provisional from released counts): {student_pct_317:.2f}% ({student_pct_317:.4f}%)")
    print(f"Denominator Wedge: {wedge_317:.2f} percentage points ({wedge_317:.4f} pp)")

    res_df = pd.DataFrame([
        {
            "sample": "Consistent Grades 9-12 (Baseline)",
            "total_schools": total_schools_307,
            "zero_phys_schools": n_zero_schools_307,
            "school_pct_zero": round(school_pct_307, 2),
            "released_enrollment_total": int(rel_enr_307),
            "released_enrollment_zero_phys": int(zero_rel_enr_307),
            "student_pct_zero_released": round(student_pct_307, 2),
            "denominator_wedge_pp": round(wedge_307, 2),
            "suppressed_schools_count": int(n_suppressed_307)
        },
        {
            "sample": "All Matched (Sensitivity)",
            "total_schools": total_schools_317,
            "zero_phys_schools": n_zero_schools_317,
            "school_pct_zero": round(school_pct_317, 2),
            "released_enrollment_total": int(rel_enr_317),
            "released_enrollment_zero_phys": int(zero_rel_enr_317),
            "student_pct_zero_released": round(student_pct_317, 2),
            "denominator_wedge_pp": round(wedge_317, 2),
            "suppressed_schools_count": int(df_317["flag_enr_suppressed"].sum())
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
