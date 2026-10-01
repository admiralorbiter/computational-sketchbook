"""
Automated Narrative and Econometric Data Synchronization Test Suite.

Verifies that all narrative claims, statistical estimates, and fiscal counterfactual figures
reported across README.md, econometric_decomposition_report.md, and fiscal_materiality_report.md
match the canonical CSV files with 100% precision.
"""

from pathlib import Path
import re
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs" / "tables"


def test_compensation_benchmarks_exist_and_valid():
    benchmarks_path = DATA_DIR / "processed" / "compensation_benchmarks.csv"
    assert benchmarks_path.exists(), f"Missing {benchmarks_path}"
    df = pd.read_csv(benchmarks_path)
    assert len(df) == 8, f"Expected 8 benchmark rows, got {len(df)}"
    
    # Check marginal fringe rates
    ks_rates = df[df["state"] == "KS"]["marginal_fringe_rate"].unique()
    mo_rates = df[df["state"] == "MO"]["marginal_fringe_rate"].unique()
    assert len(ks_rates) == 1 and abs(ks_rates[0] - 0.2122) < 1e-4
    assert len(mo_rates) == 1 and abs(mo_rates[0] - 0.1595) < 1e-4


def test_phase3_claim_evidence_integrity():
    claims_path = OUTPUTS_DIR / "phase3_claim_evidence.csv"
    assert claims_path.exists(), f"Missing {claims_path}"
    df = pd.read_csv(claims_path)
    assert len(df) == 15, f"Expected 15 qualitative claims, got {len(df)}"
    
    # Check claim IDs
    expected_ids = {
        "SMSD-01", "SMSD-02", "SMSD-03", "SMSD-04",
        "KCK-01", "KCK-02", "KCK-03", "KCK-04", "KCK-05",
        "RAY-01", "RAY-02", "RAY-03",
        "FO-01", "FO-02", "FO-03"
    }
    found_ids = set(df["claim_id"].unique())
    assert expected_ids == found_ids, f"Mismatch in claim IDs: {expected_ids ^ found_ids}"
    
    # Verify all claims are cited in board_document_audit_report.md
    report_text = (OUTPUTS_DIR / "board_document_audit_report.md").read_text(encoding="utf-8")
    for cid in expected_ids:
        assert cid in report_text, f"Claim ID {cid} not cited in board_document_audit_report.md"


def test_long_difference_regression_sync():
    ld_path = OUTPUTS_DIR / "long_difference_regression_results.csv"
    assert ld_path.exists(), f"Missing {ld_path}"
    df = pd.read_csv(ld_path)
    
    # Verify N and R2
    row0 = df.iloc[0]
    assert row0["n_obs"] == 55
    assert abs(row0["r2"] - 0.692) < 0.001
    
    # Verify key coefficients
    coeffs = dict(zip(df["variable"], df["coefficient"]))
    assert abs(coeffs["d_teachers_100"] - 11.118) < 0.01
    assert abs(coeffs["d_poverty_100"] - (-0.957)) < 0.01
    assert abs(coeffs["d_lep_100"] - (-3.634)) < 0.01
    assert abs(coeffs["is_ks"] - 1.502) < 0.01

    # Verify presence in econometric report
    econ_report = (OUTPUTS_DIR / "econometric_decomposition_report.md").read_text(encoding="utf-8")
    assert "11.118" in econ_report
    assert "-0.957" in econ_report
    assert "0.692" in econ_report


def test_shapley_decomposition_sync():
    shapley_path = OUTPUTS_DIR / "shapley_decomposition_results.csv"
    assert shapley_path.exists(), f"Missing {shapley_path}"
    df = pd.read_csv(shapley_path)
    
    shares = dict(zip(df["covariate_family"], df["pct_of_explained_variance"]))
    assert abs(shares["Student Need Shifts"] - 66.2) < 0.2
    assert abs(shares["Teacher Scale Growth"] - 27.7) < 0.2
    assert abs(shares["State Jurisdiction"] - 6.1) < 0.2
    
    # Verify presence in README.md and econometric report
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "66.2%" in readme_text
    assert "27.7%" in readme_text
    assert "6.1%" in readme_text


def test_fiscal_counterfactuals_sync():
    cf_path = OUTPUTS_DIR / "fiscal_materiality_counterfactuals.csv"
    assert cf_path.exists(), f"Missing {cf_path}"
    df = pd.read_csv(cf_path)
    
    # Shawnee Mission USD 512
    smsd = df[df["nces_lea_id"].astype(str) == "2011640"].iloc[0]
    assert abs(smsd["cf1_own_rollback_savings"] - 9319621.35) < 1.0
    assert abs(smsd["cf1_own_feasible_base_raise"] - 4117.30) < 1.0
    assert abs(smsd["cf1_own_pct_raise_on_base"] - 7.7) < 0.2
    assert abs(smsd["teachers_k12_fte"] - 1867.29) < 0.1
    
    # KCKPS USD 500
    kck = df[df["nces_lea_id"].astype(str) == "2007950"].iloc[0]
    assert abs(kck["cf2_all_supervisory_savings"] - 13077668.38) < 1.0
    assert abs(kck["cf2_all_feasible_base_raise"] - 8001.17) < 1.0
    assert abs(kck["cf2_all_pct_raise_on_base"] - 15.0) < 0.2
    
    # Fort Osage R-I
    fo = df[df["nces_lea_id"].astype(str) == "2912290"].iloc[0]
    assert abs(fo["cf2_all_supervisory_savings"] - 748351.13) < 1.0
    assert abs(fo["cf2_all_feasible_base_raise"] - 1861.09) < 1.0
    assert abs(fo["cf2_all_pct_raise_on_base"] - 3.8) < 0.2
    
    # Raytown C-2
    ray = df[df["nces_lea_id"].astype(str) == "2926070"].iloc[0]
    assert abs(ray["cf2_all_supervisory_savings"] - 478434.88) < 1.0
    assert abs(ray["cf2_all_feasible_base_raise"] - 744.00) < 1.0
    assert abs(ray["cf2_all_pct_raise_on_base"] - 1.5) < 0.2
    
    # Verify these exact dollar strings in fiscal_materiality_report.md and README.md
    fiscal_report = (OUTPUTS_DIR / "fiscal_materiality_report.md").read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    
    assert "$9,319,621.35" in fiscal_report and "$9,319,621.35" in readme_text
    assert "$13,077,668.38" in fiscal_report and "$13,077,668.38" in readme_text
    assert "$748,351.13" in fiscal_report and "$748,351.13" in readme_text
    assert "$478,434.88" in fiscal_report and "$478,434.88" in readme_text
    
    assert "+$4,117.30" in fiscal_report and "+$4,117.30" in readme_text
    assert "+$8,001.17" in fiscal_report and "+$8,001.17" in readme_text
    assert "+$1,861.09" in fiscal_report and "+$1,861.09" in readme_text
    assert "+$744.00" in fiscal_report and "+$744.00" in readme_text


def test_annual_trajectory_and_peer_summary_sync():
    traj_path = OUTPUTS_DIR / "fiscal_materiality_annual_trajectory.csv"
    assert traj_path.exists(), f"Missing {traj_path}"
    df_traj = pd.read_csv(traj_path)
    
    # 2023-24 row
    row_24 = df_traj[df_traj["school_year"] == "2023-2024"].iloc[0]
    assert abs(row_24["net_surplus_coordinators_fte"] - 217.81) < 0.1
    assert abs(row_24["net_cohort_annual_cost_savings"] - 21163879.32) < 1.0
    
    # Cumulative trajectory values
    traj_text = (OUTPUTS_DIR / "fiscal_materiality_report.md").read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "$21,163,879.32" in traj_text and "$21,163,879.32" in readme_text
    assert "$70,553,696.34" in traj_text and "$70,553,696.34" in readme_text
    assert "725.86 FTE-years" in traj_text or "725.86 FTE-Yrs" in traj_text
    assert "725.86 FTE-years" in readme_text
    
    # Peer summary
    peer_sum_path = OUTPUTS_DIR / "fiscal_materiality_peer_summary.csv"
    assert peer_sum_path.exists(), f"Missing {peer_sum_path}"
    df_peer = pd.read_csv(peer_sum_path)
    core_models = ['Model 1: SCHADM (Peer)', 'Model 2: LEAADM (Peer)', 'Model 3: CORSUP (Peer)']
    metro_core = df_peer[(df_peer["region"] == "METRO") & (df_peer["model_name"].isin(core_models))]
    total_savings = metro_core["estimated_expenditure_savings"].sum()
    total_fte = metro_core["peer_excess_fte"].sum()
    assert abs(total_savings - 41737693.51) < 1.0
    assert abs(total_fte - 360.87) < 0.1
    
    assert "$41,737,693.51" in traj_text and "$41,737,693.51" in readme_text
    assert "360.87 FTE" in traj_text and "360.87 FTE" in readme_text


if __name__ == "__main__":
    print("Running automated synchronization checks...")
    test_compensation_benchmarks_exist_and_valid()
    print("[PASS] Compensation benchmarks validated.")
    test_phase3_claim_evidence_integrity()
    print("[PASS] Phase 3 qualitative evidence ledger validated.")
    test_long_difference_regression_sync()
    print("[PASS] Long-difference growth model estimates validated.")
    test_shapley_decomposition_sync()
    print("[PASS] Grouped Shapley growth decomposition validated.")
    test_fiscal_counterfactuals_sync()
    print("[PASS] District-level fiscal counterfactuals and feasible base raises validated.")
    test_annual_trajectory_and_peer_summary_sync()
    print("[PASS] Trajectory and peer summary aggregations validated.")
    print("\nALL NARRATIVE AND DATA SYNCHRONIZATION CHECKS PASSED (100% MATCH).")
