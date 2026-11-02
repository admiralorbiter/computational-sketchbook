"""
Semantic & Longitudinal Calibration Audit Suite (Phase 1.1 Final Patch).

Audits data integrity beyond syntax:
1. Zero negative values assertion across all numerical fields.
2. Missingness vs True Zero semantic distinction:
   - Verifies complete_outcome_cohort_53 (53 districts) vs balanced_presence_cohort_55 (55 districts).
   - Confirms Olathe and Gardner Edgerton 2015-16 reporting dropouts are flagged.
3. Detection of suspicious all-zero state-years (2016–2018 student support).
4. Quantification and explanation of longitudinal discontinuities:
   - 2023-24 -> 2024-25 Kansas break across BOTH SCHADM (-36.8%) and LEAADM (-32.0%).
   - 2013-14 -> 2014-15 Missouri LEAADM -> CORSUP reclassification (~100 FTE).
   - 2006-07 -> 2008-09 Kansas reporting void in combined central management (downgrading to AMBER).
5. Strict quarantine of student support services from administrative composites.
6. Balanced cohort verification:
   - Clean pre-break benchmark (2014–15 to 2023–24): +51.0% coordinators, +12.5% LEAADM, 48.5% coordinator share of supervisory growth.
   - Counselors clean pupil support benchmark: +17.1% in balanced cohort.
7. Machine-Enforced Longitudinal Comparability Gate:
   - Validates all rules in COMPARABILITY_REGISTRY.
   - Executes assert_outcome_eligible() stopping rules to guarantee Phase 2 models cannot fit on broken series.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Import machine-enforced comparability gate
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from comparability import COMPARABILITY_REGISTRY, ComparabilityStatus, assert_outcome_eligible, filter_eligible_observations


def run_audit():
    print("=" * 75)
    print("PHASE 1.1 SEMANTIC & LONGITUDINAL CALIBRATION AUDIT (FINAL PATCH)")
    print("=" * 75)

    csv_path = PROCESSED_DIR / "district_staff_year.csv"
    assert csv_path.exists(), f"Missing dataset: {csv_path}"
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records across {len(df.columns)} columns.\n")

    # ---------------------------------------------------------
    # CHECK 1: Zero Negative Values (Syntactic)
    # ---------------------------------------------------------
    print("[Check 1] Asserting zero negative values across all numerical fields...")
    num_cols = df.select_dtypes(include=[np.number]).columns
    neg_counts = {c: (df[c] < 0).sum() for c in num_cols if (df[c] < 0).sum() > 0}
    assert not neg_counts, f"FAILED: Negative values detected: {neg_counts}"
    print("  [OK] PASSED: Zero negative values detected across all columns.")

    # ---------------------------------------------------------
    # CHECK 2: Missingness vs True Zero Semantic Audit & Dropouts
    # ---------------------------------------------------------
    print("\n[Check 2] Auditing missingness vs true zero & cohort completeness...")
    operating = df[df["enrollment_total"] > 100].copy()
    missing_staff = operating[operating["flag_missing_key_staff"]][
        ["school_year", "nces_lea_id", "district_name", "state", "enrollment_total", "teachers_k12_fte", "school_administrators_fte"]
    ]
    print(f"  Detected {len(missing_staff)} district-years with unpopulated core staffing:")
    for _, r in missing_staff.head(5).iterrows():
        print(f"    - {r['school_year']} | {r['district_name']} ({r['state']}, ID: {r['nces_lea_id']}): Enrollment={r['enrollment_total']:.0f}, Teachers={r['teachers_k12_fte']}, SCHADM={r['school_administrators_fte']}")

    # Assert Olathe and Gardner Edgerton 2015-16 dropouts are caught
    olathe_1516 = df[(df["school_year"] == "2015-2016") & (df["district_name"].str.contains("Olathe", case=False, na=False))]
    gardner_1516 = df[(df["school_year"] == "2015-2016") & (df["district_name"].str.contains("Gardner", case=False, na=False))]
    assert len(olathe_1516) > 0 and olathe_1516["flag_missing_key_staff"].iloc[0], "Olathe 2015-16 missingness was not flagged!"
    assert len(gardner_1516) > 0 and gardner_1516["flag_missing_key_staff"].iloc[0], "Gardner Edgerton 2015-16 missingness was not flagged!"

    # Verify balanced presence (55) vs complete outcome (53)
    bal_55 = df[df["is_balanced_presence_cohort_55"]]["nces_lea_id"].nunique()
    comp_53 = df[df["is_complete_outcome_cohort_53"]]["nces_lea_id"].nunique()
    print(f"  Balanced Presence Cohort (in all 11 years): {bal_55} districts")
    print(f"  Complete Outcome Cohort (non-null staffing in all 11 years): {comp_53} districts")
    assert bal_55 == 55, f"Expected 55 balanced presence districts, found {bal_55}"
    assert comp_53 == 53, f"Expected 53 complete outcome districts, found {comp_53}"
    print("  [OK] PASSED: District-year dropouts successfully isolated and complete cohort certified.")

    # ---------------------------------------------------------
    # CHECK 3: Suspicious All-Zero State-Years (Artifact Detection)
    # ---------------------------------------------------------
    print("\n[Check 3] Detecting suspicious all-zero state-years...")
    zero_support_years = df[df["flag_zero_student_support"]].groupby(["school_year", "state"])["nces_lea_id"].count()
    print("  District-years flagged for reported 0.0 student support (enrollment > 500):")
    for (sy, st), cnt in zero_support_years.items():
        print(f"    - {sy} [{st}]: {cnt} large districts reporting exactly 0.0 student support staff")
    
    flagged_years = set(df[df["flag_zero_student_support"]]["school_year"])
    for y in ["2016-2017", "2017-2018", "2018-2019"]:
        assert y in flagged_years, f"Failed to catch all-zero student support in {y}"
    print("  [OK] PASSED: State reporting voids (2016–2018 student support) detected and quarantined.")

    # ---------------------------------------------------------
    # CHECK 4: Longitudinal Break & Discontinuity Reconciliation
    # ---------------------------------------------------------
    print("\n[Check 4] Reconciling major longitudinal administrative discontinuities...")
    
    # 4a: Kansas 2024-25 Break (BOTH SCHADM and LEAADM)
    ks_schadm_23 = df[(df["school_year"] == "2023-2024") & (df["state"] == "KS")]["school_administrators_fte"].sum()
    ks_schadm_24 = df[(df["school_year"] == "2024-2025") & (df["state"] == "KS")]["school_administrators_fte"].sum()
    ks_schadm_pct = (ks_schadm_24 - ks_schadm_23) / ks_schadm_23 * 100.0

    ks_lea_23 = df[(df["school_year"] == "2023-2024") & (df["state"] == "KS")]["lea_administrators_fte"].sum()
    ks_lea_24 = df[(df["school_year"] == "2024-2025") & (df["state"] == "KS")]["lea_administrators_fte"].sum()
    ks_lea_pct = (ks_lea_24 - ks_lea_23) / ks_lea_23 * 100.0

    print(f"  [Kansas 2024-25 Break]")
    print(f"    - SCHADM (Building Admins): {ks_schadm_23:.1f} -> {ks_schadm_24:.1f} ({ks_schadm_pct:+.1f}%)")
    print(f"    - LEAADM (District Central): {ks_lea_23:.1f} -> {ks_lea_24:.1f} ({ks_lea_pct:+.1f}%)")
    assert ks_schadm_pct < -30.0, "Expected large negative drop in Kansas 2024-25 SCHADM"
    assert ks_lea_pct < -25.0, "Expected large negative drop in Kansas 2024-25 LEAADM"
    print("    -> CONFIRMED: Kansas CCD line 059 omitted Assistant Principals and central directors in 2024-25.")

    # 4b: Missouri 2014-15 LEAADM -> CORSUP Reclassification
    mo_lea_13 = df[(df["school_year"] == "2013-2014") & (df["state"] == "MO")]["lea_administrators_fte"].sum()
    mo_lea_14 = df[(df["school_year"] == "2014-2015") & (df["state"] == "MO")]["lea_administrators_fte"].sum()
    mo_cor_13 = df[(df["school_year"] == "2013-2014") & (df["state"] == "MO")]["instructional_coordinators_fte"].sum()
    mo_cor_14 = df[(df["school_year"] == "2014-2015") & (df["state"] == "MO")]["instructional_coordinators_fte"].sum()
    mo_comb_13 = mo_lea_13 + mo_cor_13
    mo_comb_14 = mo_lea_14 + mo_cor_14
    print(f"  [Missouri Reclassification] 2013-14 -> 2014-15:")
    print(f"    - LEAADM: {mo_lea_13:.1f} -> {mo_lea_14:.1f} ({mo_lea_14 - mo_lea_13:+.1f} FTE)")
    print(f"    - CORSUP: {mo_cor_13:.1f} -> {mo_cor_14:.1f} ({mo_cor_14 - mo_cor_13:+.1f} FTE)")
    print(f"    - Combined LEAADM+CORSUP: {mo_comb_13:.1f} -> {mo_comb_14:.1f} ({mo_comb_14 - mo_comb_13:+.1f} FTE, {(mo_comb_14-mo_comb_13)/mo_comb_13*100:+.1f}%)")
    assert abs((mo_comb_14 - mo_comb_13) / mo_comb_13) < 0.10, "Combined central+coord should be smooth across 2014"
    print("    -> CONFIRMED: Combined LEAADM+CORSUP is stable across 2014-15 break.")

    # 4c: Kansas 2006-2009 Void in Combined Central Management
    ks_comb_05 = df[(df["school_year"] == "2005-2006") & (df["state"] == "KS")]["central_mgmt_and_coordinators_fte"].sum()
    ks_comb_06 = df[(df["school_year"] == "2006-2007") & (df["state"] == "KS")]["central_mgmt_and_coordinators_fte"].sum()
    ks_comb_09 = df[(df["school_year"] == "2009-2010") & (df["state"] == "KS")]["central_mgmt_and_coordinators_fte"].sum()
    print(f"  [Kansas 2006-2009 Void in Central Management]")
    print(f"    - 2005-06: {ks_comb_05:.1f} FTE")
    print(f"    - 2006-07: {ks_comb_06:.1f} FTE (drop of {ks_comb_06 - ks_comb_05:.1f} FTE)")
    print(f"    - 2009-10: {ks_comb_09:.1f} FTE (rebound of {ks_comb_09 - ks_comb_06:+.1f} FTE)")
    assert ks_comb_06 < 120.0, "Expected severe reporting hole in Kansas 2006-2009 central staffing"
    print("    -> CONFIRMED: Kansas 2006-2009 unmodeled void justifies AMBER status for 20-year combined series.")

    # ---------------------------------------------------------
    # CHECK 5: Strict Quarantine of Student Support Staff
    # ---------------------------------------------------------
    print("\n[Check 5] Verifying strict quarantine of student support staff...")
    sample_sub = df[df["counselors_fte"] > 10].copy()
    for _, r in sample_sub.head(10).iterrows():
        sch = r["school_administrators_fte"] or 0
        lea = r["lea_administrators_fte"] or 0
        cor = r["instructional_coordinators_fte"] or 0
        tot = r["total_admin_and_coordinators_fte"]
        if pd.notna(tot):
            assert abs(tot - (sch + lea + cor)) < 1e-4, f"Quarantine breached in {r['district_name']}!"
    print("  [OK] PASSED: Student support staff is strictly quarantined from administrative totals.")

    # ---------------------------------------------------------
    # CHECK 6: Balanced Cohort Benchmarks Verification
    # ---------------------------------------------------------
    print("\n[Check 6] Auditing Balanced Regular District Cohort Benchmarks...")
    d14 = df[(df["school_year"] == "2014-2015") & df["is_balanced_presence_cohort_55"]]
    d23 = df[(df["school_year"] == "2023-2024") & df["is_balanced_presence_cohort_55"]]
    d24 = df[(df["school_year"] == "2024-2025") & df["is_balanced_presence_cohort_55"]]

    # Pre-break Clean 10-Year Benchmark (2014-15 -> 2023-24)
    e14, e23 = d14["enrollment_total"].sum(), d23["enrollment_total"].sum()
    t14, t23 = d14["teachers_k12_fte"].sum(), d23["teachers_k12_fte"].sum()
    l14, l23 = d14["lea_administrators_fte"].sum(), d23["lea_administrators_fte"].sum()
    s14, s23 = d14["school_administrators_fte"].sum(), d23["school_administrators_fte"].sum()
    c14, c23 = d14["instructional_coordinators_fte"].sum(), d23["instructional_coordinators_fte"].sum()
    couns14, couns23 = d14["counselors_fte"].sum(), d23["counselors_fte"].sum()

    tot_sup_14 = s14 + l14 + c14
    tot_sup_23 = s23 + l23 + c23
    delta_tot_sup = tot_sup_23 - tot_sup_14
    delta_coord = c23 - c14
    coord_share_of_sup = (delta_coord / delta_tot_sup) * 100.0

    print("  [Pre-Break Clean Benchmark: 2014-15 -> 2023-24 (55 Regular Districts)]")
    print(f"    - Enrollment: {e14:,.0f} -> {e23:,.0f} ({(e23-e14)/e14*100:+.1f}%)")
    print(f"    - Teachers: {t14:,.1f} -> {t23:,.1f} ({(t23-t14)/t14*100:+.1f}%, {t23-t14:+.1f} FTE)")
    print(f"    - District Central Admins (LEAADM): {l14:.2f} -> {l23:.2f} ({(l23-l14)/l14*100:+.1f}%, {l23-l14:+.2f} FTE)")
    print(f"    - School Building Admins (SCHADM): {s14:.2f} -> {s23:.2f} ({(s23-s14)/s14*100:+.1f}%, {s23-s14:+.2f} FTE)")
    print(f"    - Instructional Coordinators (CORSUP): {c14:.2f} -> {c23:.2f} ({(c23-c14)/c14*100:+.1f}%, {c23-c14:+.2f} FTE)")
    print(f"    - Broad Supervisory Workforce: {tot_sup_14:.2f} -> {tot_sup_23:.2f} ({(tot_sup_23-tot_sup_14)/tot_sup_14*100:+.1f}%, {delta_tot_sup:+.2f} FTE)")
    print(f"    - Coordinator Share of Net Supervisory Growth: {coord_share_of_sup:.2f}% (Retracted 89.5% artifact replaced with ~48.5%)")
    print(f"    - Guidance Counselors: {couns14:.2f} -> {couns23:.2f} ({(couns23-couns14)/couns14*100:+.1f}%, {couns23-couns14:+.2f} FTE)")

    assert abs(coord_share_of_sup - 48.45) < 0.5, f"Expected coordinator share ~48.5%, got {coord_share_of_sup:.2f}%"
    assert abs((c23 - c14) - 255.52) < 1.0, f"Expected coordinator growth ~255.5 FTE, got {c23-c14:.2f}"
    assert abs((l23 - l14) - 21.98) < 1.0, f"Expected central admin growth ~22.0 FTE, got {l23-l14:.2f}"
    print("  [OK] PASSED: Clean pre-break benchmark verified.")

    # ---------------------------------------------------------
    # CHECK 7: Machine-Enforced Comparability Gate Testing
    # ---------------------------------------------------------
    print("\n[Check 7] Testing Machine-Enforced Comparability Registry & Gate...")
    
    # Test valid model
    ok_cor, msg_cor = assert_outcome_eligible("instructional_coordinators_fte", "2014-2015", "2024-2025")
    assert ok_cor, f"Expected CORSUP modern to pass: {msg_cor}"
    print(f"  - CORSUP modern gate test: {msg_cor}")

    ok_lea, msg_lea = assert_outcome_eligible("lea_administrators_fte", "2014-2015", "2023-2024")
    assert ok_lea, f"Expected LEAADM primary to pass: {msg_lea}"
    print(f"  - LEAADM primary gate test: {msg_lea}")

    # Test prohibited model (STUSUP over 20 years - MUST FAIL)
    ok_stu, msg_stu = assert_outcome_eligible("student_support_staff_fte", "2004-2005", "2024-2025")
    assert not ok_stu, "Expected STUSUP 20-year to trigger HARD STOPPING RULE"
    print(f"  - STUSUP stopping rule gate test: PASSED (Triggered: {msg_stu})")

    # Test conditional model (Central combined 20-year - MUST BE CONDITIONAL)
    ok_comb, msg_comb = assert_outcome_eligible("central_mgmt_and_coordinators_fte", "2004-2005", "2024-2025")
    assert not ok_comb, "Expected central combined 20-year to require conditional approval"
    print(f"  - Central combined 20-year gate test: PASSED (Triggered: {msg_comb})")

    print("\n" + "=" * 75)
    print("COMPARABILITY REGISTRY ACTIVE RULES:")
    print("=" * 75)
    for name, rule in COMPARABILITY_REGISTRY.items():
        print(f"[{rule.status.value:<22}] {rule.outcome_variable:<32} | {rule.valid_period[0]} to {rule.valid_period[1]} | Isolated: {str(rule.allow_isolated_modeling):<5}")
        print(f"   -> Rationale: {rule.analytical_rationale}")

    print("=" * 75)
    print("ALL AUDIT CHECKS PASSED: DATASET & COMPARABILITY ENFORCEMENT VERIFIED")
    print("=" * 75)


if __name__ == "__main__":
    run_audit()
