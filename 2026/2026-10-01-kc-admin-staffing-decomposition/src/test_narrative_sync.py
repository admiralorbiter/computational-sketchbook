"""
Automated Narrative and Econometric Data Synchronization Test Suite.

Verifies that all narrative claims, statistical estimates, and fiscal counterfactual figures
reported across README.md, econometric_decomposition_report.md, fiscal_materiality_report.md,
and board_document_audit_report.md match the canonical CSV files with 100% precision.
"""

import hashlib
from pathlib import Path
import re
import pandas as pd
import numpy as np
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
    assert "727.31" in traj_text and "727.31" in readme_text
    assert "680.84" in traj_text and "680.84" in readme_text
    assert "725.86" in traj_text and "725.86" in readme_text
    assert "679.39" in traj_text and "679.39" in readme_text

    # Softened demographic composition narrative
    econ_report = (OUTPUTS_DIR / "econometric_decomposition_report.md").read_text(encoding="utf-8")
    assert "Changes in demographic composition show no detectable independent association" in econ_report
    assert "Changes in demographic composition show no detectable independent association" in readme_text
    
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


def test_phase5_coordinator_functional_decomposition():
    recon_path = DATA_DIR / "processed" / "coordinator_role_reconstruction.csv"
    crosswalk_path = DATA_DIR / "processed" / "coordinator_role_crosswalk.csv"
    arch_path = DATA_DIR / "processed" / "district_staffing_architectures_6archetypes.csv"
    post_path = DATA_DIR / "processed" / "post_esser_coordinator_survival.csv"
    report_path = OUTPUTS_DIR / "coordinator_functional_decomposition_report.md"

    assert recon_path.exists(), f"Missing {recon_path}"
    assert crosswalk_path.exists(), f"Missing {crosswalk_path}"
    assert arch_path.exists(), f"Missing {arch_path}"
    assert post_path.exists(), f"Missing {post_path}"
    assert report_path.exists(), f"Missing {report_path}"

    df_recon = pd.read_csv(recon_path)
    df_cross = pd.read_csv(crosswalk_path)
    df_arch = pd.read_csv(arch_path)
    df_post = pd.read_csv(post_path)
    report_text = report_path.read_text(encoding="utf-8")

    # Verify counts and parity between reconstruction and crosswalk mirror
    assert len(df_recon) == 29
    assert len(df_cross) == 29
    assert len(df_arch) == 6
    assert len(df_post) == 6
    assert (df_recon["estimated_fte_2023_24"] == df_cross["estimated_fte_2023_24"]).all()

    # Verify epistemic basis requirements across all 29 rows
    valid_basis = {"documented_count", "inferred_allocation", "residual_allocation"}
    assert set(df_recon["fte_basis"].unique()) == valid_basis

    basis_counts = df_recon["fte_basis"].value_counts().to_dict()
    basis_fte = df_recon.groupby("fte_basis")["estimated_fte_2023_24"].sum().round(2).to_dict()

    assert basis_counts["documented_count"] == 18
    assert basis_counts["inferred_allocation"] == 7
    assert basis_counts["residual_allocation"] == 4

    assert abs(basis_fte["documented_count"] - 244.80) < 0.01
    assert abs(basis_fte["inferred_allocation"] - 105.00) < 0.01
    assert abs(basis_fte["residual_allocation"] - 30.56) < 0.01

    tot_sample_fte = df_recon["estimated_fte_2023_24"].sum()
    assert abs(tot_sample_fte - 380.36) < 0.01
    assert abs(basis_fte["documented_count"] / tot_sample_fte - 0.6436) < 0.001
    assert abs(basis_fte["inferred_allocation"] / tot_sample_fte - 0.2761) < 0.001
    assert abs(basis_fte["residual_allocation"] / tot_sample_fte - 0.0803) < 0.001

    for col in ["source_document", "source_url", "source_year", "page_or_item", "evidence_type", "confidence"]:
        assert col in df_recon.columns
        assert df_recon[col].notna().all()

    # Verify functional category sums (Total sample: 380.36 FTE)
    func_sums = df_recon.groupby("functional_category")["estimated_fte_2023_24"].sum().round(2).to_dict()
    assert abs(func_sums["Instructional Coaching"] - 135.75) < 0.01
    assert abs(func_sums["SPED/EL Program Management"] - 93.10) < 0.01
    assert abs(func_sums["Curriculum/Content"] - 73.80) < 0.01
    assert abs(func_sums["Instructional Technology"] - 35.00) < 0.01
    assert abs(func_sums["Intervention/MTSS"] - 22.00) < 0.01
    assert abs(func_sums["Data/Assessment"] - 14.71) < 0.01
    assert abs(func_sums["Federal Programs"] - 6.00) < 0.01
    assert abs(sum(func_sums.values()) - 380.36) < 0.01

    # Combined Coaching + MTSS = 157.75 FTE (41.5%)
    coaching_mtss = func_sums["Instructional Coaching"] + func_sums["Intervention/MTSS"]
    assert abs(coaching_mtss - 157.75) < 0.01
    assert abs(coaching_mtss / 380.36 - 0.4147) < 0.001

    # Verify locus sums and 50/50 hybrid allocation (52.9% school-sited)
    tot = df_recon["estimated_fte_2023_24"].sum()
    pure_school = df_recon[df_recon["work_location"] == "School Building"]["estimated_fte_2023_24"].sum()
    hybrid = df_recon[df_recon["work_location"] == "School Building / Central"]["estimated_fte_2023_24"].sum()
    central = tot - pure_school - hybrid
    school_5050 = pure_school + 0.5 * hybrid

    assert abs(pure_school - 175.75) < 0.01
    assert abs(hybrid - 51.00) < 0.01
    assert abs(central - 153.61) < 0.01
    assert abs(school_5050 - 201.25) < 0.01
    assert abs(school_5050 / tot - 0.5291) < 0.001

    # Verify canonical K-12 teacher FTE scale (and total reported teachers w/ Pre-K)
    k12_teachers = dict(zip(df_arch["district_name"], df_arch["teachers_k12_fte_2023_24"]))
    assert abs(k12_teachers["Shawnee Mission USD 512"] - 1867.29) < 0.01
    assert abs(k12_teachers["Kansas City USD 500"] - 1348.35) < 0.01
    assert abs(k12_teachers["Olathe USD 233"] - 2136.60) < 0.01
    assert abs(k12_teachers["North Kansas City 74"] - 1454.54) < 0.01
    assert abs(k12_teachers["Raytown C-2"] - 554.60) < 0.01
    assert abs(k12_teachers["Lee's Summit R-VII"] - 1190.17) < 0.01

    tot_teachers = dict(zip(df_arch["district_name"], df_arch["teachers_total_reported_fte_2023_24"]))
    assert abs(tot_teachers["Shawnee Mission USD 512"] - 1900.29) < 0.01
    assert abs(tot_teachers["Kansas City USD 500"] - 1411.95) < 0.01

    # Verify exact crosswalk summation to reported CCD CORSUP
    corsup_by_dist = df_cross.groupby("district_name")["estimated_fte_2023_24"].sum().round(2).to_dict()
    assert abs(corsup_by_dist["Shawnee Mission USD 512"] - 123.71) < 0.01
    assert abs(corsup_by_dist["Kansas City USD 500"] - 106.80) < 0.01
    assert abs(corsup_by_dist["Olathe USD 233"] - 85.55) < 0.01
    assert abs(corsup_by_dist["North Kansas City 74"] - 36.55) < 0.01
    assert abs(corsup_by_dist["Raytown C-2"] - 16.75) < 0.01
    assert abs(corsup_by_dist["Lee's Summit R-VII"] - 11.00) < 0.01

    # Verify apples-to-apples Model 3 peer residuals (2023-24)
    res_path = OUTPUTS_DIR / "peer_expected_staffing_residuals.csv"
    assert res_path.exists(), f"Missing {res_path}"
    df_res = pd.read_csv(res_path)
    m3_24 = df_res[(df_res["school_year"] == "2023-2024") & (df_res["model_name"] == "Model 3: CORSUP (Peer)")]
    smsd_m3 = m3_24[m3_24["nces_lea_id"].astype(str) == "2011640"].iloc[0]
    kck_m3 = m3_24[m3_24["nces_lea_id"].astype(str) == "2007950"].iloc[0]

    assert abs(smsd_m3["residual_peer"] - 58.98) < 0.05
    assert abs(smsd_m3["stud_resid"] - 5.46) < 0.05
    assert abs(kck_m3["residual_peer"] - 57.86) < 0.05
    assert abs(kck_m3["stud_resid"] - 5.32) < 0.05

    # Verify 10-year longitudinal persistence (persistent_peer_outliers.csv)
    outliers_path = OUTPUTS_DIR / "persistent_peer_outliers.csv"
    df_out = pd.read_csv(outliers_path)
    smsd_out = df_out[(df_out["nces_lea_id"].astype(str) == "2011640") & (df_out["model"] == "Model 3: CORSUP (Peer)")].iloc[0]
    kck_out = df_out[(df_out["nces_lea_id"].astype(str) == "2007950") & (df_out["model"] == "Model 3: CORSUP (Peer)")].iloc[0]

    assert abs(smsd_out["mean_unexplained_deviation_fte"] - 17.9) < 0.1
    assert smsd_out["high_deviation_years_count"] == 5
    assert abs(smsd_out["max_stud_resid"] - 5.46) < 0.05

    assert abs(kck_out["mean_unexplained_deviation_fte"] - 56.3) < 0.1
    assert kck_out["high_deviation_years_count"] == 10
    assert abs(kck_out["max_stud_resid"] - 6.98) < 0.05

    # Verify key architectural metrics and nuanced institutional text in report
    assert "123.7" in report_text
    assert "106.8" in report_text
    assert "141.0" in report_text
    assert "3.28" in report_text
    assert "2.12" in report_text
    assert "Specialized Instructional Coaching Overlay" in report_text
    assert "Decentralized School-Level Supervisory Dispersion" in report_text
    assert "1,867.29" in report_text
    assert "1,348.35" in report_text
    assert "52.9%" in report_text
    assert "41.5%" in report_text
    assert "+58.98 FTE" in report_text
    assert "+57.86 FTE" in report_text
    assert "5.32" in report_text
    assert "17.9 FTE" in report_text
    assert "Funding mechanism remains an institutional explanation rather than a causal estimate" in report_text



def test_phase6_architecture_and_chronic_absenteeism():
    """Verify Phase 6 continuous architecture panel, repaired chronic absenteeism panel, and recovery models."""
    # 1. District Architecture Panel (Continuous coordinates)
    arch_path = DATA_DIR / "processed" / "district_architecture_panel.csv"
    assert arch_path.exists(), f"Missing {arch_path}"
    df_arch = pd.read_csv(arch_path)
    
    assert len(df_arch) == 550, f"Expected 550 rows in architecture panel, got {len(df_arch)}"
    assert df_arch["nces_lea_id"].nunique() == 55
    assert set(df_arch["school_year"].unique()) == {
        "2014-2015", "2015-2016", "2016-2017", "2017-2018", "2018-2019",
        "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"
    }

    # Macro temporal concentration across 55 balanced districts
    yearly_corsup = df_arch.groupby("school_year")["instructional_coordinators_fte"].sum().round(1).to_dict()
    assert abs(yearly_corsup["2014-2015"] - 501.3) < 0.2
    assert abs(yearly_corsup["2018-2019"] - 523.6) < 0.2
    assert abs(yearly_corsup["2019-2020"] - 598.7) < 0.2  # +75.1 pre-COVID jump
    assert abs(yearly_corsup["2023-2024"] - 756.8) < 0.2
    decade_growth = yearly_corsup["2023-2024"] - yearly_corsup["2014-2015"]
    post_1819_growth = yearly_corsup["2023-2024"] - yearly_corsup["2018-2019"]
    pct_post_1819 = (post_1819_growth / decade_growth) * 100
    assert abs(pct_post_1819 - 91.3) < 0.2

    # Pre-COVID Jump in SMSD (2011640)
    smsd_arch = df_arch[df_arch["nces_lea_id"] == 2011640].set_index("school_year")
    assert abs(smsd_arch.loc["2018-2019", "instructional_coordinators_fte"] - 46.5) < 0.1
    assert abs(smsd_arch.loc["2019-2020", "instructional_coordinators_fte"] - 78.0) < 0.1
    assert abs((smsd_arch.loc["2019-2020", "instructional_coordinators_fte"] - smsd_arch.loc["2018-2019", "instructional_coordinators_fte"]) - 31.5) < 0.1

    # Snapshots quadrant evolution
    snap_path = OUTPUTS_DIR / "district_architecture_snapshots.csv"
    assert snap_path.exists(), f"Missing {snap_path}"
    df_snap = pd.read_csv(snap_path)
    assert len(df_snap) == 220
    q_counts = df_snap.groupby(["school_year", "architecture_quadrant"]).size().unstack(fill_value=0)
    assert q_counts.loc["2014-2015", "Coaching Overlay"] == 10
    assert q_counts.loc["2018-2019", "Coaching Overlay"] == 20
    assert q_counts.loc["2023-2024", "Coaching Overlay"] == 25
    assert q_counts.loc["2014-2015", "Dual-Intensity (Coaching + School Supervision)"] == 22
    assert q_counts.loc["2023-2024", "Dual-Intensity (Coaching + School Supervision)"] == 7

    # 2. Repaired District Chronic Absenteeism Panel
    abs_path = DATA_DIR / "processed" / "district_chronic_absenteeism_panel.csv"
    assert abs_path.exists(), f"Missing {abs_path}"
    df_abs = pd.read_csv(abs_path)
    assert len(df_abs) == 216
    assert (df_abs["chronic_absent_rate_pct"] >= 0.0).all()
    assert (df_abs["chronic_absent_rate_pct"] <= 100.0).all(), "Found impossible chronic absent rate > 100%"

    # KCKPS repaired values
    kck_abs = df_abs[df_abs["nces_lea_id"] == 2007950].set_index("school_year")
    assert kck_abs.loc["2017-2018", "chronic_absent_count"] == 5075
    assert abs(kck_abs.loc["2017-2018", "chronic_absent_rate_pct"] - 22.16) < 0.05
    assert kck_abs.loc["2020-2021", "chronic_absent_count"] == 9157
    assert abs(kck_abs.loc["2020-2021", "chronic_absent_rate_pct"] - 41.36) < 0.05
    assert kck_abs.loc["2021-2022", "chronic_absent_count"] == 11132
    assert abs(kck_abs.loc["2021-2022", "chronic_absent_rate_pct"] - 54.34) < 0.05
    assert kck_abs.loc["2022-2023", "chronic_absent_count"] == 9178
    assert abs(kck_abs.loc["2022-2023", "chronic_absent_rate_pct"] - 44.00) < 0.05

    # 3. Wide Attendance Recovery Trajectory
    wide_path = OUTPUTS_DIR / "district_chronic_absenteeism_recovery_wide.csv"
    assert wide_path.exists(), f"Missing {wide_path}"
    df_wide = pd.read_csv(wide_path)
    assert len(df_wide) == 55
    kck_wide = df_wide[df_wide["nces_lea_id"] == 2007950].iloc[0]
    assert abs(kck_wide["recovery_delta_2122_to_2223_pct_pts"] - (-10.3)) < 0.05
    assert abs(kck_wide["net_disruption_delta_pct_pts"] - 21.84) < 0.05

    smsd_wide = df_wide[df_wide["nces_lea_id"] == 2011640].iloc[0]
    assert abs(smsd_wide["recovery_delta_2122_to_2223_pct_pts"] - 1.4) < 0.05
    assert abs(smsd_wide["net_disruption_delta_pct_pts"] - 7.27) < 0.05

    # 4. Phase 6 Exploratory Screening Report and Correlations Table
    corr_path = OUTPUTS_DIR / "phase6_architecture_attendance_recovery_correlations.csv"
    assert corr_path.exists(), f"Missing {corr_path}"
    df_corr = pd.read_csv(corr_path).set_index("variable_name")
    assert abs(df_corr.loc["absent_rate_2021_22_pct", "corr_recovery_delta_2122_to_2223_pct_pts"] - (-0.5300)) < 0.005

    rep_path = OUTPUTS_DIR / "phase6_exploratory_architecture_recovery_report.md"
    assert rep_path.exists(), f"Missing {rep_path}"
    rep_text = rep_path.read_text(encoding="utf-8")
    assert "-10.3 percentage points" in rep_text
    assert "44.0%" in rep_text
    assert "54.3%" in rep_text
    assert "0.521" in rep_text
    assert "0.720" in rep_text
    assert "-0.0366" in rep_text
    assert "-0.1929" in rep_text


def test_phase6c_fiscal_support_and_substitution():
    """Verify Gate 6C.0 canonical fiscal support panel and Gate 6C.1 econometric substitution models."""
    # 1. Panel Dimensions and Identity Checks
    panel_path = DATA_DIR / "processed" / "district_fiscal_support_panel.csv"
    assert panel_path.exists(), f"Missing {panel_path}"
    df_panel = pd.read_csv(panel_path)

    assert len(df_panel) == 495, f"Expected 495 rows, found {len(df_panel)}"
    assert df_panel["nces_lea_id"].nunique() == 55
    expected_years = {
        "2014-2015", "2015-2016", "2016-2017", "2017-2018", "2018-2019",
        "2019-2020", "2020-2021", "2021-2022", "2022-2023"
    }
    assert set(df_panel["school_year"].unique()) == expected_years

    # Exact mathematical identity: E07 - V13 - V14 == instr_support_nonpersonnel
    np_calc = df_panel["instr_support_total_e07"] - df_panel["instr_support_salary_v13"] - df_panel["instr_support_benefits_v14"]
    assert np.allclose(df_panel["instr_support_nonpersonnel"], np_calc)
    assert (df_panel["instr_support_nonpersonnel"] >= 0).all(), "Found negative non-personnel instructional support"

    # Only single documented anomaly in pupil support (-$1,000 in Midway R-I FY 2017)
    neg_pupil = df_panel[df_panel["pupil_support_nonpersonnel"] < 0]
    assert len(neg_pupil) == 1
    assert neg_pupil.iloc[0]["nces_lea_id"] == 2921060
    assert neg_pupil.iloc[0]["fiscal_year"] == 2017
    assert neg_pupil.iloc[0]["pupil_support_nonpersonnel"] == -1000.0

    # 2. Focal Archetype Verification
    # Shawnee Mission USD 512 (Coaching Overlay: partial substitution)
    smsd = df_panel[df_panel["nces_lea_id"] == 2011640].set_index("school_year")
    assert abs(smsd.loc["2014-2015", "real_instr_support_nonpersonnel_per_pupil"] - 63.51) < 0.1
    assert abs(smsd.loc["2018-2019", "real_instr_support_nonpersonnel_per_pupil"] - 54.26) < 0.1
    assert abs(smsd.loc["2022-2023", "real_instr_support_nonpersonnel_per_pupil"] - 41.59) < 0.1
    assert abs(smsd.loc["2022-2023", "instr_support_nonpersonnel_share_pct"] - 8.14) < 0.2

    # Lee's Summit R-VII (Lean / Direct School Supervision)
    ls = df_panel[df_panel["nces_lea_id"] == 2918300].set_index("school_year")
    assert abs(ls.loc["2022-2023", "real_instr_support_nonpersonnel_per_pupil"] - 185.77) < 0.1
    assert abs(ls.loc["2022-2023", "instr_support_nonpersonnel_share_pct"] - 36.06) < 0.2

    # North Kansas City 74 (High School Admin)
    nkc = df_panel[df_panel["nces_lea_id"] == 2922800].set_index("school_year")
    assert abs(nkc.loc["2022-2023", "real_instr_support_nonpersonnel_per_pupil"] - 436.60) < 0.1
    assert abs(nkc.loc["2022-2023", "instr_support_nonpersonnel_share_pct"] - 43.95) < 0.2

    # 3. Regression Results Table Checks
    res_path = OUTPUTS_DIR / "phase6c_fiscal_substitution_regression_results.csv"
    assert res_path.exists(), f"Missing {res_path}"
    df_res = pd.read_csv(res_path).set_index("model_name")
    assert len(df_res) == 14

    # Within-District FE Model 1 (Non-personnel): +11.85, p=0.111
    assert abs(df_res.loc["FE Model 1: Real Non-Personnel Support / Pupil", "coef"] - 11.8509) < 0.01
    assert abs(df_res.loc["FE Model 1: Real Non-Personnel Support / Pupil", "t_statistic"] - 1.59) < 0.05

    # Within-District FE Model 2 (Total E07): +19.41, p=0.216
    assert abs(df_res.loc["FE Model 2: Real Total E07 Support / Pupil", "coef"] - 19.4144) < 0.01

    # Within-District FE Sensitivities
    assert abs(df_res.loc["FE Sensitivity 1: District + State*Year FE (Real NP / Pupil)", "coef"] - 9.4365) < 0.01
    assert abs(df_res.loc["FE Sensitivity 1: District + State*Year FE (Real NP / Pupil)", "p_value"] - 0.1754) < 0.01
    assert abs(df_res.loc["FE Sensitivity 3: Winsorized NP (2.5-97.5%) + State*Year FE", "coef"] - 9.0315) < 0.01
    assert abs(df_res.loc["FE Sensitivity 3: Winsorized NP (2.5-97.5%) + State*Year FE", "p_value"] - 0.1895) < 0.01

    # Long Difference Model 1 (Delta Real Non-personnel): +14.96, p=0.221
    assert abs(df_res.loc["Long Difference Model 1: Delta Real Non-Personnel / Pupil", "coef"] - 14.9587) < 0.01

    # Contemporaneous FD & Sensitivities
    assert abs(df_res.loc["Contemporaneous FD: Delta Real NP ~ Delta CORSUP", "coef"] - (-1.3478)) < 0.01
    assert abs(df_res.loc["FD Sensitivity 1: Delta Real NP ~ Delta CORSUP + Year FE", "coef"] - (-2.6479)) < 0.01
    assert abs(df_res.loc["FD Sensitivity 1: Delta Real NP ~ Delta CORSUP + Year FE", "p_value"] - 0.7037) < 0.01
    assert abs(df_res.loc["FD Sensitivity 2: Delta Real NP ~ Delta CORSUP + State*Year FE", "coef"] - (-4.0747)) < 0.01
    assert abs(df_res.loc["FD Sensitivity 2: Delta Real NP ~ Delta CORSUP + State*Year FE", "p_value"] - 0.5629) < 0.01

    # Lead Response (Delta Real NP (t+1) ~ Delta CORSUP (t)): +10.36, p=0.274
    assert abs(df_res.loc["Lead Response: Delta Real NP (t+1) ~ Delta CORSUP (t)", "coef"] - 10.3643) < 0.01

    # 4. Synthesis Report Document Checks
    rep_path = OUTPUTS_DIR / "phase6c_fiscal_substitution_report.md"
    assert rep_path.exists(), f"Missing {rep_path}"
    rep_text = rep_path.read_text(encoding="utf-8")
    assert "$41.59" in rep_text
    assert "$185.77" in rep_text
    assert "$436.60" in rep_text
    assert "+11.85" in rep_text
    assert "+19.41" in rep_text
    assert "+14.96" in rep_text
    assert "Regime 2: Additive Internal Staffing Layer" in rep_text
    assert "Regime 4: Partial Substitution + Expansion" in rep_text


def test_phase6c2_state_object_audit():
    """
    Validates Gate 6C.2 state object-level audit data, mechanism deltas, and synthesis report.
    Tests whether the vendor insourcing hypothesis (Object 300 / 6300 substitution) is decisively rejected.
    """
    # 1. Focal Object-Level Support Panel
    p_path = DATA_DIR / "processed" / "focal_archetype_object_level_support_panel.csv"
    assert p_path.exists(), f"Missing {p_path}"
    df_p = pd.read_csv(p_path)
    assert len(df_p) == 18
    assert len(df_p.columns) == 29

    # Shawnee Mission USD 512 checks
    smsd = df_p[df_p["district_name"] == "Shawnee Mission USD 512"].set_index("school_year")
    assert abs(smsd.loc["2014-2015", "real_purchased_prof_tech_per_pupil"] - 0.09) < 0.05
    assert abs(smsd.loc["2018-2019", "real_purchased_prof_tech_per_pupil"] - 3.25) < 0.1
    assert abs(smsd.loc["2022-2023", "real_purchased_prof_tech_per_pupil"] - 4.41) < 0.1
    assert abs(smsd.loc["2022-2023", "corsup_fte"] - 93.0) < 0.1
    # Vendor spending grew, disproving insourcing
    assert smsd.loc["2022-2023", "real_purchased_prof_tech_per_pupil"] > smsd.loc["2014-2015", "real_purchased_prof_tech_per_pupil"]

    # Lee's Summit R-VII checks
    ls = df_p[df_p["district_name"] == "Lee's Summit R-VII"].set_index("school_year")
    assert abs(ls.loc["2014-2015", "real_purchased_prof_tech_per_pupil"] - 71.85) < 0.1
    assert abs(ls.loc["2022-2023", "real_purchased_prof_tech_per_pupil"] - 58.19) < 0.1
    assert abs(ls.loc["2022-2023", "real_supplies_materials_per_pupil"] - 124.39) < 0.1
    assert abs(ls.loc["2022-2023", "real_nonpersonnel_total_per_pupil"] - 185.77) < 0.1

    # 2. Mechanism Deltas Table
    d_path = OUTPUTS_DIR / "phase6c2_focal_archetype_mechanism_deltas.csv"
    assert d_path.exists(), f"Missing {d_path}"
    df_d = pd.read_csv(d_path).set_index("district_name")
    assert len(df_d) == 6

    # Shawnee Mission delta assertions
    assert abs(df_d.loc["Shawnee Mission USD 512", "delta_corsup_fte"] - 65.4) < 0.1
    assert abs(df_d.loc["Shawnee Mission USD 512", "delta_real_purchased_prof_obj300_per_pupil"] - 4.32) < 0.1
    assert abs(df_d.loc["Shawnee Mission USD 512", "delta_real_supplies_materials_obj600_per_pupil"] - 26.92) < 0.1
    assert abs(df_d.loc["Shawnee Mission USD 512", "delta_real_salaries_per_pupil"] - 99.13) < 0.1
    assert "Disproven" in df_d.loc["Shawnee Mission USD 512", "insourcing_verdict"]

    # Olathe delta assertions
    assert abs(df_d.loc["Olathe USD 233", "delta_corsup_fte"] - 35.9) < 0.1
    assert abs(df_d.loc["Olathe USD 233", "delta_real_purchased_prof_obj300_per_pupil"] - 9.55) < 0.1
    assert abs(df_d.loc["Olathe USD 233", "delta_real_supplies_materials_obj600_per_pupil"] - 21.60) < 0.1

    # 3. Report Document Integrity
    rep_path = OUTPUTS_DIR / "phase6c2_state_object_audit_report.md"
    assert rep_path.exists(), f"Missing {rep_path}"
    rep_text = rep_path.read_text(encoding="utf-8")
    assert "$0.09" in rep_text
    assert "$4.41" in rep_text
    assert "+65.4" in rep_text
    assert "Additive Internal Staffing Layer" in rep_text
    assert "The \"Vendor Insourcing / Private Substitution\" hypothesis is decisively disproven" in rep_text


def test_manifest_provenance_and_checksums():
    manifest_path = DATA_DIR / "manifest.csv"
    assert manifest_path.exists(), f"Missing {manifest_path}"
    manifest_df = pd.read_csv(manifest_path)
    
    assert len(manifest_df) >= 19, f"Expected at least 19 datasets in manifest, found {len(manifest_df)}"
    for _, row in manifest_df.iterrows():
        fpath = ROOT / row["relative_path"]
        assert fpath.exists(), f"Manifest file missing on disk: {fpath}"
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        expected_sha = row["sha256"]
        assert actual_sha == expected_sha, (
            f"SHA256 mismatch for {row['dataset_name']} ({row['relative_path']}): "
            f"actual {actual_sha} != manifest {expected_sha}"
        )


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
    test_phase5_coordinator_functional_decomposition()
    print("[PASS] Phase 5 coordinator functional decomposition & archetypes validated.")
    test_phase6_architecture_and_chronic_absenteeism()
    print("[PASS] Phase 6 architecture coordinates & repaired chronic absenteeism validated.")
    test_phase6c_fiscal_support_and_substitution()
    print("[PASS] Phase 6C fiscal support panel & substitution models validated.")
    test_phase6c2_state_object_audit()
    print("[PASS] Phase 6C.2 state object-level audit & mechanism deltas validated.")
    test_manifest_provenance_and_checksums()
    print("[PASS] Dataset manifest provenance and SHA256 checksums validated.")
    test_markdown_link_and_retraction_hygiene()
    print("[PASS] Markdown link and retraction hygiene validated.")
    print("\nALL NARRATIVE AND DATA SYNCHRONIZATION CHECKS PASSED (100% MATCH).")

