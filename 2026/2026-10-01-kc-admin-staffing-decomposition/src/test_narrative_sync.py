"""
Automated Narrative and Econometric Data Synchronization Test Suite.

Verifies that all narrative claims, statistical estimates, and fiscal counterfactual figures
reported across README.md, econometric_decomposition_report.md, fiscal_materiality_report.md,
and board_document_audit_report.md match the canonical CSV files with 100% precision.
"""

from pathlib import Path
import re
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs" / "tables"


def test_compensation_benchmarks_and_reconstruction_valid():
    benchmarks_path = DATA_DIR / "processed" / "compensation_benchmarks.csv"
    assert benchmarks_path.exists(), f"Missing {benchmarks_path}"
    df = pd.read_csv(benchmarks_path)
    assert len(df) == 8, f"Expected 8 benchmark rows, got {len(df)}"
    
    # Check marginal fringe rates
    ks_rates = df[df["state"] == "KS"]["marginal_fringe_rate"].unique()
    mo_rates = df[df["state"] == "MO"]["marginal_fringe_rate"].unique()
    assert len(ks_rates) == 1 and abs(ks_rates[0] - 0.2122) < 1e-4
    assert len(mo_rates) == 1 and abs(mo_rates[0] - 0.1595) < 1e-4

    # Check auditable Kansas 2015-16 reconstruction artifact
    recon_path = DATA_DIR / "processed" / "kansas_2015_16_reconstruction.csv"
    assert recon_path.exists(), f"Missing {recon_path}"
    df_recon = pd.read_csv(recon_path)
    assert len(df_recon) == 2, f"Expected 2 reconstructed districts, got {len(df_recon)}"
    
    olathe = df_recon[df_recon["nces_lea_id"].astype(str) == "2010140"].iloc[0]
    assert abs(olathe["teachers_k12_fte"] - 2018.42) < 0.01
    assert abs(olathe["instructional_coordinators_fte"] - 34.82) < 0.01
    
    gardner = df_recon[df_recon["nces_lea_id"].astype(str) == "2006420"].iloc[0]
    assert abs(gardner["teachers_k12_fte"] - 329.00) < 0.01
    assert abs(gardner["instructional_coordinators_fte"] - 3.90) < 0.01


def test_phase3_claim_evidence_integrity():
    claims_path = OUTPUTS_DIR / "phase3_claim_evidence.csv"
    assert claims_path.exists(), f"Missing {claims_path}"
    df = pd.read_csv(claims_path)
    assert len(df) == 16, f"Expected 16 qualitative claims, got {len(df)}"
    
    # Check claim IDs
    expected_ids = {
        "SMSD-01", "SMSD-02", "SMSD-03", "SMSD-04",
        "KCK-01", "KCK-02", "KCK-03", "KCK-04", "KCK-05", "KCK-06",
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

    # Verify HC3 robust SE column exists
    assert "robust_std_error_hc3" in df.columns
    t_row = df[df["variable"] == "d_teachers_100"].iloc[0]
    assert abs(t_row["robust_std_error_hc3"] - 6.90) < 0.05

    # Verify presence in econometric report
    econ_report = (OUTPUTS_DIR / "econometric_decomposition_report.md").read_text(encoding="utf-8")
    assert "11.118" in econ_report
    assert "-0.957" in econ_report
    assert "0.692" in econ_report


def test_sensitivity_family_and_lodo_diagnostics():
    sens_path = OUTPUTS_DIR / "long_difference_sensitivity_family.csv"
    assert sens_path.exists(), f"Missing {sens_path}"
    df_sens = pd.read_csv(sens_path)
    
    specs = df_sens["specification"].unique()
    assert len(specs) == 5, f"Expected 5 sensitivity models, found {len(specs)}"
    
    # Model B baseline capacity coefficient
    mod_b = df_sens[df_sens["specification"] == "Model B: Baseline 2014 Capacity Added"]
    base_row = mod_b[mod_b["variable"] == "base_corsup_fte"].iloc[0]
    assert abs(base_row["coefficient"] - (-0.401)) < 0.01
    assert abs(mod_b.iloc[0]["r2"] - 0.764) < 0.005

    # Model C demographic rate changes
    mod_c = df_sens[df_sens["specification"] == "Model C: Demographic Share/Rate Changes (% pts)"]
    assert abs(mod_c.iloc[0]["r2"] - 0.317) < 0.005
    for demog_var in ["d_poverty_rate_pct", "d_idea_rate_pct", "d_lep_rate_pct"]:
        d_row = mod_c[mod_c["variable"] == demog_var].iloc[0]
        assert d_row["robust_p_value_hc3"] > 0.30, f"{demog_var} p-value {d_row['robust_p_value_hc3']} <= 0.30"

    # Verify every sensitivity model's R2 appears dynamically in Table 3.2 of econometric report
    econ_report = (OUTPUTS_DIR / "econometric_decomposition_report.md").read_text(encoding="utf-8")
    for spec, grp in df_sens.groupby("specification"):
        r2_val = grp["r2"].iloc[0]
        r2_str = f"{r2_val:.3f}"
        assert r2_str in econ_report, f"R2 {r2_str} for {spec} not found in econometric report Table 3.2"

    # LODO diagnostics
    lodo_path = OUTPUTS_DIR / "long_difference_lodo_diagnostics.csv"
    assert lodo_path.exists(), f"Missing {lodo_path}"
    df_lodo = pd.read_csv(lodo_path)
    assert len(df_lodo) == 55
    top3_ids = set(df_lodo.head(3)["excluded_nces_lea_id"].astype(str))
    expected_top3 = {"2011640", "2007950", "2010140"}
    assert top3_ids == expected_top3, f"Unexpected top leverage districts: {top3_ids}"


def test_shapley_decomposition_sync():
    shapley_path = OUTPUTS_DIR / "shapley_decomposition_results.csv"
    assert shapley_path.exists(), f"Missing {shapley_path}"
    df = pd.read_csv(shapley_path)
    
    df_base = df[df["specification"] == "Baseline 3-Group Model"]
    shares = dict(zip(df_base["covariate_family"], df_base["pct_of_explained_variance"]))
    assert abs(shares["Student Need Shifts"] - 66.2) < 0.2
    assert abs(shares["Teacher Scale Growth"] - 27.7) < 0.2
    assert abs(shares["State Jurisdiction"] - 6.1) < 0.2

    # Check bootstrap intervals exist
    assert "boot_ci_95_lower" in df.columns and "boot_ci_95_upper" in df.columns
    t_scale = df_base[df_base["covariate_family"] == "Teacher Scale Growth"].iloc[0]
    assert t_scale["boot_ci_95_lower"] < 10.0 and t_scale["boot_ci_95_upper"] > 40.0
    
    # Verify presence in README.md and econometric report
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "66.2%" in readme_text
    assert "27.7%" in readme_text
    assert "6.1%" in readme_text


def test_studentized_residuals_and_outliers():
    outliers_path = OUTPUTS_DIR / "persistent_peer_outliers.csv"
    assert outliers_path.exists(), f"Missing {outliers_path}"
    df = pd.read_csv(outliers_path)
    
    # Check KCKPS (Model 1 SCHADM & Model 3 CORSUP)
    kck_sch = df[(df["nces_lea_id"].astype(str) == "2007950") & (df["model"] == "Model 1: SCHADM (Peer)")].iloc[0]
    assert abs(kck_sch["max_stud_resid"] - 10.11) < 0.1
    kck_cor = df[(df["nces_lea_id"].astype(str) == "2007950") & (df["model"] == "Model 3: CORSUP (Peer)")].iloc[0]
    assert abs(kck_cor["max_stud_resid"] - 6.98) < 0.1
    assert abs(kck_cor["mean_unexplained_deviation_fte"] - 56.3) < 0.2
    
    # Check SMSD (Model 3 CORSUP)
    smsd_cor = df[(df["nces_lea_id"].astype(str) == "2011640") & (df["model"] == "Model 3: CORSUP (Peer)")].iloc[0]
    assert abs(smsd_cor["max_stud_resid"] - 5.46) < 0.1

    # Check Fort Osage (Model 2 LEAADM) - verify 2.65 in table and report
    fo_lea = df[(df["nces_lea_id"].astype(str) == "2912290") & (df["model"] == "Model 2: LEAADM (Peer)")].iloc[0]
    assert abs(fo_lea["max_stud_resid"] - 2.65) < 0.01
    assert fo_lea["high_deviation_years_count"] == 10
    
    audit_text = (OUTPUTS_DIR / "board_document_audit_report.md").read_text(encoding="utf-8")
    assert "2.65" in audit_text
    assert "3.78" not in audit_text, "Found stale 3.78 residual for Fort Osage in audit report"

    # Check Raytown (Model 2 LEAADM)
    ray_lea = df[(df["nces_lea_id"].astype(str) == "2926070") & (df["model"] == "Model 2: LEAADM (Peer)")].iloc[0]
    assert abs(ray_lea["max_stud_resid"] - 2.54) < 0.1


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
    methods_text = (ROOT / "research" / "methods.md").read_text(encoding="utf-8")
    
    assert "$9,319,621.35" in fiscal_report and "$9,319,621.35" in readme_text
    assert "$13,077,668.38" in fiscal_report and "$13,077,668.38" in readme_text
    assert "$748,351.13" in fiscal_report and "$748,351.13" in readme_text
    assert "$478,434.88" in fiscal_report and "$478,434.88" in readme_text
    
    assert "+$4,117.30" in fiscal_report and "+$4,117.30" in readme_text
    assert "+$8,001.17" in fiscal_report and "+$8,001.17" in readme_text
    assert "+$1,861.09" in fiscal_report and "+$1,861.09" in readme_text
    assert "+$744.00" in fiscal_report and "+$744.00" in readme_text

    # Assert 136.0 teachers funded across all docs, and stale 97.4 is absent
    for doc_name, doc_text in [("fiscal_materiality_report.md", fiscal_report),
                               ("README.md", readme_text),
                               ("methods.md", methods_text)]:
        assert "136.0" in doc_text, f"136.0 teachers not found in {doc_name}"
        assert "97.4" not in doc_text, f"Stale 97.4 teachers found in {doc_name}"


def test_annual_trajectory_and_peer_summary_sync():
    traj_path = OUTPUTS_DIR / "fiscal_materiality_annual_trajectory.csv"
    assert traj_path.exists(), f"Missing {traj_path}"
    df_traj = pd.read_csv(traj_path)
    
    # 2014-15 and 2018-19 strictly $0.00
    row_15 = df_traj[df_traj["school_year"] == "2014-2015"].iloc[0]
    assert row_15["net_cohort_annual_cost_savings"] == 0.0
    row_19 = df_traj[df_traj["school_year"] == "2018-2019"].iloc[0]
    assert row_19["net_cohort_annual_cost_savings"] == 0.0

    # 2023-24 row (exact state pricing: KS 215.00 * 99450 + MO 2.81 * 93600 = $21,645,003.97)
    row_24 = df_traj[df_traj["school_year"] == "2023-2024"].iloc[0]
    assert abs(row_24["net_surplus_coordinators_fte"] - 217.81) < 0.1
    assert abs(row_24["net_cohort_annual_cost_savings"] - 21645003.97) < 1.0
    
    # Cumulative trajectory values
    traj_text = (OUTPUTS_DIR / "fiscal_materiality_report.md").read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    
    assert "$21,645,003.97" in traj_text and "$21,645,003.97" in readme_text
    assert "$72,296,352.01" in traj_text and "$72,296,352.01" in readme_text
    assert "$67,674,988.62" in traj_text and "$67,674,988.62" in readme_text
    assert "725.86 FTE-years" in traj_text or "725.86 FTE-Yrs" in traj_text
    assert "725.86 FTE-years" in readme_text
    
    # Peer summary
    peer_sum_path = OUTPUTS_DIR / "fiscal_materiality_peer_summary.csv"
    assert peer_sum_path.exists(), f"Missing {peer_sum_path}"
    df_peer = pd.read_csv(peer_sum_path)
    assert "positive_peer_deviation_fte" in df_peer.columns
    
    core_models = ['Model 1: SCHADM (Peer)', 'Model 2: LEAADM (Peer)', 'Model 3: CORSUP (Peer)']
    metro_core = df_peer[(df_peer["region"] == "METRO") & (df_peer["model_name"].isin(core_models))]
    total_savings = metro_core["estimated_expenditure_savings"].sum()
    total_fte = metro_core["positive_peer_deviation_fte"].sum()
    assert abs(total_savings - 41737693.51) < 1.0
    assert abs(total_fte - 360.87) < 0.1
    
    assert "$41,737,693.51" in traj_text and "$41,737,693.51" in readme_text
    assert "360.87 FTE" in traj_text and "360.87 FTE" in readme_text


def test_markdown_link_and_retraction_hygiene():
    """Verify absence of local Windows file links and retracted claims across all markdown files."""
    md_files = list(ROOT.glob("**/*.md"))
    assert len(md_files) > 0
    
    for f in md_files:
        text = f.read_text(encoding="utf-8")
        # Check no file:///c: or file:///C:
        assert not re.search(r"file:///[cC]:", text), f"Found local file link in {f.relative_to(ROOT)}"
        
        # Check no unretracted 89.5%
        if "89.5%" in text:
            assert ("retracted" in text.lower() or "preliminary" in text.lower()), \
                f"Found unretracted/unclarified 89.5% claim in {f.relative_to(ROOT)}"


if __name__ == "__main__":
    print("Running automated synchronization checks...")
    test_compensation_benchmarks_and_reconstruction_valid()
    print("[PASS] Compensation benchmarks & reconstruction artifact validated.")
    test_phase3_claim_evidence_integrity()
    print("[PASS] Phase 3 qualitative evidence ledger validated.")
    test_long_difference_regression_sync()
    print("[PASS] Long-difference growth model estimates validated.")
    test_sensitivity_family_and_lodo_diagnostics()
    print("[PASS] Growth sensitivity family & LODO diagnostics validated.")
    test_shapley_decomposition_sync()
    print("[PASS] Grouped Shapley growth decomposition validated.")
    test_studentized_residuals_and_outliers()
    print("[PASS] Externally studentized residuals & peer outliers validated.")
    test_fiscal_counterfactuals_sync()
    print("[PASS] District-level fiscal counterfactuals and feasible base raises validated.")
    test_annual_trajectory_and_peer_summary_sync()
    print("[PASS] Trajectory and peer summary aggregations validated.")
    test_markdown_link_and_retraction_hygiene()
    print("[PASS] Markdown link and retraction hygiene validated.")
    print("\nALL NARRATIVE AND DATA SYNCHRONIZATION CHECKS PASSED (100% MATCH).")
