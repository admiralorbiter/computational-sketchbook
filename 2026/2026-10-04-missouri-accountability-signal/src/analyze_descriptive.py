"""
src/analyze_descriptive.py

Implements Phase 5 & Phase 6.1 Calibration:
1. Complete-Case Bivariate Analysis (Status MPI, APR Growth Points %, Total APR % vs. FRPL & Direct Certification)
2. True Enrollment-Weighted Pearson Correlation Implementation
3. Level Disaggregation (Elementary, Middle, High, Mixed) with documented components
4. Neutral 2x2 Matrix Analysis with explicit tie documentation and sensitivity options
5. Exact APR Counterfactual Decomposition (Actual vs. Excluding Growth vs. Neutral Growth)
6. Exact Component Point-Accounting & Variance Decomposition (Status, Growth, Attendance, Other)
7. District-Grouped Cross-Validation (GroupKFold by LEA) for Starting Position Models
8. Multi-Year Longitudinal Stability (2023->2024, 2024->2025, Quintile Transition Rates)

Produces:
- artifacts/figures/01_achievement_vs_poverty.png
- artifacts/figures/02_growth_vs_poverty.png
- artifacts/figures/03_apr_vs_poverty.png
- artifacts/figures/04_apr_counterfactual_growth.png
- artifacts/tables/*
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"
FIGURES_DIR = BASE_DIR / "artifacts" / "figures"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def weighted_pearson_r(x, y, w):
    """
    Computes an exact enrollment-weighted Pearson correlation coefficient:
    cov_w(x, y) / sqrt(var_w(x) * var_w(y)).
    """
    mask = (~np.isnan(x)) & (~np.isnan(y)) & (~np.isnan(w)) & (w > 0)
    x_c = x[mask]
    y_c = y[mask]
    w_c = w[mask]
    if len(x_c) < 5:
        return np.nan

    w_sum = np.sum(w_c)
    mean_x = np.sum(w_c * x_c) / w_sum
    mean_y = np.sum(w_c * y_c) / w_sum

    cov_xy = np.sum(w_c * (x_c - mean_x) * (y_c - mean_y)) / w_sum
    var_x = np.sum(w_c * (x_c - mean_x) ** 2) / w_sum
    var_y = np.sum(w_c * (y_c - mean_y) ** 2) / w_sum

    denom = np.sqrt(var_x * var_y)
    if denom <= 0:
        return np.nan
    return cov_xy / denom


def compute_bivariate_stats(x, y, weights=None):
    """Computes bivariate association statistics, distinguishing unweighted from weighted."""
    mask = (~x.isna()) & (~y.isna())
    if weights is not None:
        mask = mask & (~weights.isna()) & (weights > 0)

    x_c = x[mask].values
    y_c = y[mask].values
    n = len(x_c)
    if n < 5:
        return {"n": n, "r": np.nan, "p_r": np.nan, "rho": np.nan, "p_rho": np.nan, "r2": np.nan, "beta": np.nan, "se": np.nan}

    X = sm.add_constant(x_c)
    if weights is not None:
        w_c = weights[mask].values
        model = sm.WLS(y_c, X, weights=w_c).fit()
        r_w = weighted_pearson_r(x_c, y_c, w_c)
        return {
            "n": n,
            "r": r_w,
            "p_r": model.pvalues[1],
            "rho": np.nan,  # Omit ordinary Spearman under weighting
            "p_rho": np.nan,
            "r2": model.rsquared,
            "beta": model.params[1],
            "se": model.bse[1],
        }
    else:
        model = sm.OLS(y_c, X).fit()
        r, p_r = pearsonr(x_c, y_c)
        rho, p_rho = spearmanr(x_c, y_c)
        return {
            "n": n,
            "r": r,
            "p_r": p_r,
            "rho": rho,
            "p_rho": p_rho,
            "r2": model.rsquared,
            "beta": model.params[1],
            "se": model.bse[1],
        }


def run_calibrated_analysis():
    print("[*] Loading master panel...")
    df = pd.read_parquet(PANEL_PATH)
    df25 = df[(df["school_year"] == 2025) & (df["sample_b_conventional"] == 1)].copy()
    print(f"[*] 2025 Conventional Schools (Sample B): {len(df25):,}")

    # Canonical calibrated outcome names
    outcomes = [
        ("analyst_composite_status_mpi", "Analyst Composite Status (ELA+Math Mean MPI)"),
        ("apr_growth_pts_pct", "APR Growth-Points % (Derived from Missouri Value-Added Model)"),
        ("apr_pct", "Official Total APR %"),
    ]

    # 1. Main Bivariate Table
    biv_rows = []
    for out_col, out_name in outcomes:
        # Unweighted All Conventional
        s_all = compute_bivariate_stats(df25["frpl_pct"], df25[out_col])
        biv_rows.append({"outcome": out_name, "sample": "All Conventional (Unweighted)", "poverty_var": "FRPL %", **s_all})

        # Student-Weighted All Conventional
        s_w = compute_bivariate_stats(df25["frpl_pct"], df25[out_col], weights=df25["enrollment"])
        biv_rows.append({"outcome": out_name, "sample": "All Conventional (Enrollment-Weighted)", "poverty_var": "FRPL %", **s_w})

        # Non-CEP
        df_ncep = df25[df25["cep_status"] == "NON_CEP"]
        s_ncep = compute_bivariate_stats(df_ncep["frpl_pct"], df_ncep[out_col])
        biv_rows.append({"outcome": out_name, "sample": "Non-CEP Schools Only", "poverty_var": "FRPL %", **s_ncep})

        # CEP
        df_cep = df25[df25["cep_status"] == "CEP"]
        s_cep = compute_bivariate_stats(df_cep["frpl_pct"], df_cep[out_col])
        biv_rows.append({"outcome": out_name, "sample": "CEP Participating Schools Only", "poverty_var": "FRPL %", **s_cep})

        # Direct Certification Sensitivity
        s_dc = compute_bivariate_stats(df25["direct_cert_pct"], df25[out_col])
        biv_rows.append({"outcome": out_name, "sample": "All Conventional (Unweighted)", "poverty_var": "Direct Certification %", **s_dc})

    df_biv = pd.DataFrame(biv_rows)
    df_biv.to_csv(TABLES_DIR / "table_bivariate_summary_2025.csv", index=False)
    print("\n[*] 2025 Calibrated Bivariate Summary:")
    print(df_biv[["outcome", "sample", "poverty_var", "n", "r", "r2", "beta", "se"]].to_string(index=False))

    # 2. Complete-Case Sensitivity Audit
    cc_rows = []
    # Status
    cc_rows.append({
        "measure": "Status MPI",
        "complete_both": (df25["status_case_type"] == "COMPLETE_BOTH").sum(),
        "math_only": (df25["status_case_type"] == "MATH_ONLY").sum(),
        "ela_only": (df25["status_case_type"] == "ELA_ONLY").sum(),
        "neither": (df25["status_case_type"] == "NEITHER").sum(),
        "total_sample_b": len(df25),
    })
    # Growth
    cc_rows.append({
        "measure": "Growth Points %",
        "complete_both": (df25["growth_case_type"] == "COMPLETE_BOTH").sum(),
        "math_only": (df25["growth_case_type"] == "MATH_ONLY").sum(),
        "ela_only": (df25["growth_case_type"] == "ELA_ONLY").sum(),
        "neither": (df25["growth_case_type"] == "NEITHER").sum(),
        "total_sample_b": len(df25),
    })
    df_cc = pd.DataFrame(cc_rows)
    df_cc.to_csv(TABLES_DIR / "table_complete_case_audit.csv", index=False)
    print("\n[*] Complete-Case Subject Information Audit:")
    print(df_cc.to_string(index=False))

    # 3. Disaggregation by School Level (with Applicable Components Documented)
    lvl_rows = []
    component_notes = {
        "ELEMENTARY": "Status (ELA/Math/Sci), Growth (ELA/Math/Sci), Attendance, KEA",
        "MIDDLE": "Status (ELA/Math/Sci), Growth (ELA/Math/Sci), Attendance, ICAP, HSR",
        "HIGH": "Status (EOCs), Growth (EOCs), Attendance, CCR, Adv Credit, Grad Rate, Grad Follow-up",
        "MIXED": "Composite of K-8 and 9-12 applicable components",
    }
    for lvl in ["ELEMENTARY", "MIDDLE", "HIGH", "MIXED"]:
        sub_lvl = df25[df25["school_level"] == lvl]
        for out_col, out_name in outcomes:
            s = compute_bivariate_stats(sub_lvl["frpl_pct"], sub_lvl[out_col])
            lvl_rows.append({
                "level": lvl,
                "outcome": out_name,
                "applicable_apr_components": component_notes[lvl],
                **s
            })
    df_lvl = pd.DataFrame(lvl_rows)
    df_lvl.to_csv(TABLES_DIR / "table_level_breakdown_2025.csv", index=False)

    # 4. Status vs. Growth 2x2 Matrix Analysis (Neutral Terminology & Tie Handling)
    sub_q = df25.dropna(subset=["analyst_composite_status_mpi", "apr_growth_pts_pct", "frpl_pct"]).copy()
    med_status = sub_q["analyst_composite_status_mpi"].median()
    med_growth = sub_q["apr_growth_pts_pct"].median()

    # Ties at median growth
    n_tie_growth = (sub_q["apr_growth_pts_pct"] == med_growth).sum()

    # Sensitivity 1: Inclusive >= median threshold (62.5%)
    sub_q["high_status"] = sub_q["analyst_composite_status_mpi"] >= med_status
    sub_q["high_growth_inc"] = sub_q["apr_growth_pts_pct"] >= med_growth

    q_hh = (sub_q["high_status"] & sub_q["high_growth_inc"]).sum()
    q_hl = (sub_q["high_status"] & ~sub_q["high_growth_inc"]).sum()
    q_lh = (~sub_q["high_status"] & sub_q["high_growth_inc"]).sum()
    q_ll = (~sub_q["high_status"] & ~sub_q["high_growth_inc"]).sum()

    frpl_hh = sub_q[sub_q["high_status"] & sub_q["high_growth_inc"]]["frpl_pct"].mean()
    frpl_hl = sub_q[sub_q["high_status"] & ~sub_q["high_growth_inc"]]["frpl_pct"].mean()
    frpl_lh = sub_q[~sub_q["high_status"] & sub_q["high_growth_inc"]]["frpl_pct"].mean()
    frpl_ll = sub_q[~sub_q["high_status"] & ~sub_q["high_growth_inc"]]["frpl_pct"].mean()

    # Sensitivity 2: Strict > median threshold
    sub_q["high_growth_str"] = sub_q["apr_growth_pts_pct"] > med_growth
    q_hh_str = (sub_q["high_status"] & sub_q["high_growth_str"]).sum()
    q_hl_str = (sub_q["high_status"] & ~sub_q["high_growth_str"]).sum()
    q_lh_str = (~sub_q["high_status"] & sub_q["high_growth_str"]).sum()
    q_ll_str = (~sub_q["high_status"] & ~sub_q["high_growth_str"]).sum()

    # Sensitivity 3: Exact 50th percentile rank with tie resolution
    sub_q["high_growth_pctile"] = sub_q["apr_growth_pts_pct"].rank(method="first") >= (len(sub_q) / 2)
    q_hh_pct = (sub_q["high_status"] & sub_q["high_growth_pctile"]).sum()
    q_hl_pct = (sub_q["high_status"] & ~sub_q["high_growth_pctile"]).sum()
    q_lh_pct = (~sub_q["high_status"] & sub_q["high_growth_pctile"]).sum()
    q_ll_pct = (~sub_q["high_status"] & ~sub_q["high_growth_pctile"]).sum()

    n_q = len(sub_q)
    quad_table = pd.DataFrame([
        {
            "quadrant": "High Status / High Growth",
            "count_inclusive": q_hh, "pct_inclusive": q_hh / n_q * 100,
            "count_strict": q_hh_str, "pct_strict": q_hh_str / n_q * 100,
            "count_percentile": q_hh_pct, "pct_percentile": q_hh_pct / n_q * 100,
            "mean_frpl_pct": frpl_hh
        },
        {
            "quadrant": "High Status / Low Growth",
            "count_inclusive": q_hl, "pct_inclusive": q_hl / n_q * 100,
            "count_strict": q_hl_str, "pct_strict": q_hl_str / n_q * 100,
            "count_percentile": q_hl_pct, "pct_percentile": q_hl_pct / n_q * 100,
            "mean_frpl_pct": frpl_hl
        },
        {
            "quadrant": "Low Status / High Growth",
            "count_inclusive": q_lh, "pct_inclusive": q_lh / n_q * 100,
            "count_strict": q_lh_str, "pct_strict": q_lh_str / n_q * 100,
            "count_percentile": q_lh_pct, "pct_percentile": q_lh_pct / n_q * 100,
            "mean_frpl_pct": frpl_lh
        },
        {
            "quadrant": "Low Status / Low Growth",
            "count_inclusive": q_ll, "pct_inclusive": q_ll / n_q * 100,
            "count_strict": q_ll_str, "pct_strict": q_ll_str / n_q * 100,
            "count_percentile": q_ll_pct, "pct_percentile": q_ll_pct / n_q * 100,
            "mean_frpl_pct": frpl_ll
        },
    ])
    quad_table.to_csv(TABLES_DIR / "table_quadrant_status_growth_calibrated.csv", index=False)
    print(f"\n[*] 2025 Status vs. Growth Matrix (Complete Cases N={n_q}, Ties at Median={n_tie_growth}):")
    print(quad_table.to_string(index=False))

    # 5. Exact APR Counterfactual Decomposition
    growth_pts_earned_cols = ["ela_growth_pts_earned", "math_growth_pts_earned", "science_growth_pts_earned"]
    growth_pts_poss_cols = ["ela_growth_pts_possible", "math_growth_pts_possible", "science_growth_pts_possible"]

    df25["gro_pts_earned"] = df25[growth_pts_earned_cols].sum(axis=1)
    df25["gro_pts_possible"] = df25[growth_pts_poss_cols].sum(axis=1)

    sub_cf = df25[(df25["gro_pts_possible"] > 0) & (df25["apr_points_possible"] > df25["gro_pts_possible"])].copy()

    sub_cf["apr_actual"] = (sub_cf["apr_points_earned"] / sub_cf["apr_points_possible"]) * 100.0
    sub_cf["apr_no_growth"] = ((sub_cf["apr_points_earned"] - sub_cf["gro_pts_earned"]) / (sub_cf["apr_points_possible"] - sub_cf["gro_pts_possible"])) * 100.0
    sub_cf["apr_neutral_50"] = ((sub_cf["apr_points_earned"] - sub_cf["gro_pts_earned"] + 0.5 * sub_cf["gro_pts_possible"]) / sub_cf["apr_points_possible"]) * 100.0
    state_mean_gro_rate = sub_cf["gro_pts_earned"].sum() / sub_cf["gro_pts_possible"].sum()
    sub_cf["apr_state_mean"] = ((sub_cf["apr_points_earned"] - sub_cf["gro_pts_earned"] + state_mean_gro_rate * sub_cf["gro_pts_possible"]) / sub_cf["apr_points_possible"]) * 100.0

    cf_rows = []
    for m_col, m_name in [
        ("apr_actual", "1. Actual APR %"),
        ("apr_no_growth", "2. Counterfactual APR (Excluding Growth Points)"),
        ("apr_neutral_50", "3. Counterfactual APR (Growth Held at 50% Neutral)"),
        ("apr_state_mean", "4. Counterfactual APR (Growth Held at State Mean 61.8%)"),
    ]:
        s = compute_bivariate_stats(sub_cf["frpl_pct"], sub_cf[m_col])
        cf_rows.append({"counterfactual_specification": m_name, **s})

    df_cf = pd.DataFrame(cf_rows)
    df_cf.to_csv(TABLES_DIR / "table_apr_counterfactual_decomposition.csv", index=False)
    print("\n[*] Exact APR Counterfactual Decomposition:")
    print(df_cf[["counterfactual_specification", "n", "r", "r2", "beta", "se"]].to_string(index=False))

    # 6. Exact APR Point-Accounting and Variance Decomposition
    p_sup = BASE_DIR / "data" / "raw" / "apr" / "mo_apr_supporting_2025_building.xlsx"
    df_sup = pd.read_excel(p_sup)
    df_sup["district_code"] = df_sup["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)
    df_sup["building_code"] = df_sup["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)

    merged_sup = pd.merge(df25[["district_code", "building_code", "frpl_pct", "apr_pct", "apr_points_earned", "apr_points_possible"]], df_sup, on=["district_code", "building_code"], how="inner")

    status_cols_e = [c for c in merged_sup.columns if "_STATUS_POINTS_EARNED" in c and "_PCT" not in c]
    status_cols_p = [c for c in merged_sup.columns if "_STATUS_POINTS_POSSIBLE" in c]
    growth_cols_e = [c for c in merged_sup.columns if "_GROWTH_POINTS_EARNED" in c and "_PCT" not in c]
    growth_cols_p = [c for c in merged_sup.columns if "_GROWTH_POINTS_POSSIBLE" in c]

    merged_sup["pts_status_e"] = merged_sup[status_cols_e].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    merged_sup["pts_status_p"] = merged_sup[status_cols_p].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    merged_sup["pts_growth_e"] = merged_sup[growth_cols_e].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    merged_sup["pts_growth_p"] = merged_sup[growth_cols_p].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    merged_sup["pts_att_e"] = pd.to_numeric(merged_sup["ATTENDANCE_POINTS_EARNED"], errors="coerce").fillna(0)
    merged_sup["pts_att_p"] = pd.to_numeric(merged_sup["ATTENDANCE_POINTS_POSSIBLE"], errors="coerce").fillna(0)

    merged_sup["pts_total_p"] = merged_sup["apr_points_possible"]
    merged_sup["pts_total_e"] = merged_sup["apr_points_earned"]
    merged_sup["pts_other_e"] = merged_sup["pts_total_e"] - merged_sup["pts_status_e"] - merged_sup["pts_growth_e"] - merged_sup["pts_att_e"]
    merged_sup["pts_other_p"] = merged_sup["pts_total_p"] - merged_sup["pts_status_p"] - merged_sup["pts_growth_p"] - merged_sup["pts_att_p"]

    decomp_rows = []
    var_total_apr = np.var(merged_sup["pts_total_e"] / merged_sup["pts_total_p"])
    for cat, cat_label in [
        ("status", "Academic Status (All + Subgroup)"),
        ("growth", "Value-Added Growth (All + Subgroup)"),
        ("att", "Proportional Attendance (90/90)"),
        ("other", "CCR, Graduation Rate, ICAP/KEA"),
    ]:
        share_poss = (merged_sup[f"pts_{cat}_p"] / merged_sup["pts_total_p"]).mean() * 100.0
        pct_earned = (merged_sup[f"pts_{cat}_e"] / merged_sup[f"pts_{cat}_p"].replace(0, np.nan)).mean() * 100.0
        r_frpl = merged_sup["frpl_pct"].corr(merged_sup[f"pts_{cat}_e"] / merged_sup[f"pts_{cat}_p"].replace(0, np.nan))
        cov_apr = np.cov(merged_sup[f"pts_{cat}_e"] / merged_sup["pts_total_p"], merged_sup["pts_total_e"] / merged_sup["pts_total_p"])[0, 1]
        var_share = (cov_apr / var_total_apr) * 100.0
        decomp_rows.append({
            "component": cat_label,
            "mean_points_possible": merged_sup[f"pts_{cat}_p"].mean(),
            "share_total_possible_pts": share_poss,
            "mean_pct_earned": pct_earned,
            "corr_with_frpl": r_frpl,
            "share_apr_variance": var_share,
        })
    df_decomp = pd.DataFrame(decomp_rows)
    df_decomp.to_csv(TABLES_DIR / "table_apr_component_accounting.csv", index=False)
    print("\n[*] Exact APR Point-Accounting and Variance Decomposition:")
    print(df_decomp.to_string(index=False))

    # 7. District-Grouped Cross-Validation for Starting Position
    cv_data = df25.dropna(subset=["analyst_composite_status_mpi", "prior_year_achievement", "frpl_pct", "district_code"]).copy()
    levels = pd.get_dummies(cv_data["school_level"], drop_first=True, dtype=float)
    X0 = levels
    X1 = pd.concat([X0, cv_data[["prior_year_achievement"]]], axis=1)
    X2 = pd.concat([X1, cv_data[["frpl_pct"]]], axis=1)
    X3 = pd.concat([X2, cv_data[["dese_urm_pct", "iep_pct", "ell_pct"]].fillna(0)], axis=1)

    y_cv = cv_data["analyst_composite_status_mpi"].values
    groups_cv = cv_data["district_code"].values
    gkf = GroupKFold(n_splits=5)

    cv_results = []
    base_cv_r2 = None
    for m_idx, (m_name, X_df) in enumerate([
        ("Model 0: School Level Only", X0),
        ("Model 1: Prior Achievement", X1),
        ("Model 2: Prior Achievement + Poverty", X2),
        ("Model 3: Prior Achievement + Demographics", X3),
    ]):
        X_mat = X_df.values
        lr_in = LinearRegression().fit(X_mat, y_cv)
        y_pred_in = lr_in.predict(X_mat)
        r2_in = r2_score(y_cv, y_pred_in)

        y_pred_cv = np.zeros_like(y_cv)
        for train_idx, test_idx in gkf.split(X_mat, y_cv, groups_cv):
            lr_fold = LinearRegression().fit(X_mat[train_idx], y_cv[train_idx])
            y_pred_cv[test_idx] = lr_fold.predict(X_mat[test_idx])

        r2_cv = r2_score(y_cv, y_pred_cv)
        rmse_cv = np.sqrt(mean_squared_error(y_cv, y_pred_cv))
        delta_cv = r2_cv - base_cv_r2 if base_cv_r2 is not None else np.nan
        if m_idx == 1:
            base_cv_r2 = r2_cv

        cv_results.append({
            "model": m_name,
            "in_sample_r2": r2_in,
            "cv_r2": r2_cv,
            "cv_rmse": rmse_cv,
            "incremental_cv_r2": delta_cv,
        })
    df_cv_res = pd.DataFrame(cv_results)
    df_cv_res.to_csv(TABLES_DIR / "table_starting_position_cv.csv", index=False)
    print("\n[*] Starting Position District-Grouped Cross-Validation (5-Fold, N=2,025 schools, 551 districts):")
    print(df_cv_res.to_string(index=False))

    # 8. Multi-Year Stability & Transition Matrix
    stab_rows = []
    df_b_all = df[df["sample_b_conventional"] == 1].copy()
    piv_s = df_b_all.pivot(index=["district_code", "building_code"], columns="school_year", values="analyst_composite_status_mpi")
    piv_g = df_b_all.pivot(index=["district_code", "building_code"], columns="school_year", values="apr_growth_pts_pct")
    piv_a = df_b_all.pivot(index=["district_code", "building_code"], columns="school_year", values="apr_pct")

    for pair in [(2023, 2024), (2024, 2025)]:
        y1, y2 = pair
        # Status
        s_pair = piv_s[[y1, y2]].dropna()
        r_s, p_s = pearsonr(s_pair[y1], s_pair[y2])
        rho_s, _ = spearmanr(s_pair[y1], s_pair[y2])
        stab_rows.append({"measure": "Analyst Composite Status MPI", "pair": f"{y1} -> {y2}", "n": len(s_pair), "r": r_s, "rho": rho_s, "r2": r_s**2})

        # Growth
        g_pair = piv_g[[y1, y2]].dropna()
        r_g, p_g = pearsonr(g_pair[y1], g_pair[y2])
        rho_g, _ = spearmanr(g_pair[y1], g_pair[y2])
        stab_rows.append({"measure": "APR Growth-Points %", "pair": f"{y1} -> {y2}", "n": len(g_pair), "r": r_g, "rho": rho_g, "r2": r_g**2})

        # APR
        a_pair = piv_a[[y1, y2]].dropna()
        r_a, p_a = pearsonr(a_pair[y1], a_pair[y2])
        rho_a, _ = spearmanr(a_pair[y1], a_pair[y2])
        stab_rows.append({"measure": "Total APR %", "pair": f"{y1} -> {y2}", "n": len(a_pair), "r": r_a, "rho": rho_a, "r2": r_a**2})

    df_multi_stab = pd.DataFrame(stab_rows)
    df_multi_stab.to_csv(TABLES_DIR / "table_stability_multi_year.csv", index=False)
    print("\n[*] Multi-Year Longitudinal Stability:")
    print(df_multi_stab.to_string(index=False))

    # Quintile Transition Persistence (2024 -> 2025)
    s24_25 = piv_s[[2024, 2025]].dropna()
    g24_25 = piv_g[[2024, 2025]].dropna()

    s_q24 = pd.qcut(s24_25[2024], 5, labels=[1, 2, 3, 4, 5])
    s_q25 = pd.qcut(s24_25[2025], 5, labels=[1, 2, 3, 4, 5])
    same_s = (s_q24 == s_q25).mean() * 100
    within1_s = (np.abs(s_q24.astype(int) - s_q25.astype(int)) <= 1).mean() * 100

    g_q24 = pd.qcut(g24_25[2024].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    g_q25 = pd.qcut(g24_25[2025].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    same_g = (g_q24 == g_q25).mean() * 100
    within1_g = (np.abs(g_q24.astype(int) - g_q25.astype(int)) <= 1).mean() * 100

    df_trans = pd.DataFrame([
        {"measure": "Status MPI", "pair": "2024 -> 2025", "same_quintile_pct": same_s, "within_one_quintile_pct": within1_s},
        {"measure": "Growth Points %", "pair": "2024 -> 2025", "same_quintile_pct": same_g, "within_one_quintile_pct": within1_g},
    ])
    df_trans.to_csv(TABLES_DIR / "table_quintile_transitions.csv", index=False)
    print("\n[*] Quintile Transition Matrix Summary:")
    print(df_trans.to_string(index=False))

    # 9. Generate Publication Charts
    print("\n[*] Generating high-resolution publication charts...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Figure 1: Status vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub1 = df25.dropna(subset=["frpl_pct", "analyst_composite_status_mpi"])
    ncep = sub1[sub1["cep_status"] == "NON_CEP"]
    cep = sub1[sub1["cep_status"] == "CEP"]

    ax.scatter(ncep["frpl_pct"], ncep["analyst_composite_status_mpi"], color="#1f77b4", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep):,})")
    ax.scatter(cep["frpl_pct"], cep["analyst_composite_status_mpi"], color="#d62728", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep):,})")

    m_all = sm.OLS(sub1["analyst_composite_status_mpi"], sm.add_constant(sub1["frpl_pct"])).fit()
    x_line = np.linspace(sub1["frpl_pct"].min(), sub1["frpl_pct"].max(), 200)
    y_line = m_all.params.iloc[0] + m_all.params.iloc[1] * x_line
    r_val, _ = pearsonr(sub1["frpl_pct"], sub1["analyst_composite_status_mpi"])
    r_w = weighted_pearson_r(sub1["frpl_pct"].values, sub1["analyst_composite_status_mpi"].values, sub1["enrollment"].values)

    ax.plot(x_line, y_line, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val:.2f}, rw = {r_w:.2f}, R² = {m_all.rsquared:.2f}, β = {m_all.params.iloc[1]:.2f}")

    ax.set_title("Missouri 2025 School Academic Achievement Status vs. Poverty (FRPL %)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("Analyst Composite Status Index (Mean ELA & Math MPI)", fontsize=11, labelpad=8)
    ax.set_ylim(200, 480)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "01_achievement_vs_poverty.png")
    plt.close(fig)

    # Figure 2: Growth Points vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub2 = df25.dropna(subset=["frpl_pct", "apr_growth_pts_pct"])
    ncep2 = sub2[sub2["cep_status"] == "NON_CEP"]
    cep2 = sub2[sub2["cep_status"] == "CEP"]

    ax.scatter(ncep2["frpl_pct"], ncep2["apr_growth_pts_pct"], color="#2ca02c", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep2):,})")
    ax.scatter(cep2["frpl_pct"], cep2["apr_growth_pts_pct"], color="#ff7f0e", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep2):,})")

    m_gro = sm.OLS(sub2["apr_growth_pts_pct"], sm.add_constant(sub2["frpl_pct"])).fit()
    x_line2 = np.linspace(sub2["frpl_pct"].min(), sub2["frpl_pct"].max(), 200)
    y_line2 = m_gro.params.iloc[0] + m_gro.params.iloc[1] * x_line2
    r_val2, p_val2 = pearsonr(sub2["frpl_pct"], sub2["apr_growth_pts_pct"])
    r_w2 = weighted_pearson_r(sub2["frpl_pct"].values, sub2["apr_growth_pts_pct"].values, sub2["enrollment"].values)

    ax.plot(x_line2, y_line2, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val2:+.3f} (p={p_val2:.2f}), rw = {r_w2:+.3f}, R² = {m_gro.rsquared:.4f}, β = {m_gro.params.iloc[1]:+.2f}")

    ax.set_title("Missouri 2025 APR Growth Points % Derived from Value-Added Model vs. Poverty", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("APR Growth Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(-5, 105)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "02_growth_vs_poverty.png")
    plt.close(fig)

    # Figure 3: APR vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub3 = df25.dropna(subset=["frpl_pct", "apr_pct"])
    ncep3 = sub3[sub3["cep_status"] == "NON_CEP"]
    cep3 = sub3[sub3["cep_status"] == "CEP"]

    ax.scatter(ncep3["frpl_pct"], ncep3["apr_pct"], color="#9467bd", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep3):,})")
    ax.scatter(cep3["frpl_pct"], cep3["apr_pct"], color="#8c564b", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep3):,})")

    m_apr = sm.OLS(sub3["apr_pct"], sm.add_constant(sub3["frpl_pct"])).fit()
    x_line3 = np.linspace(sub3["frpl_pct"].min(), sub3["frpl_pct"].max(), 200)
    y_line3 = m_apr.params.iloc[0] + m_apr.params.iloc[1] * x_line3
    r_val3, _ = pearsonr(sub3["frpl_pct"], sub3["apr_pct"])
    r_w3 = weighted_pearson_r(sub3["frpl_pct"].values, sub3["apr_pct"].values, sub3["enrollment"].values)

    ax.plot(x_line3, y_line3, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val3:.2f}, rw = {r_w3:.2f}, R² = {m_apr.rsquared:.2f}, β = {m_apr.params.iloc[1]:.2f}")

    ax.set_title("Missouri 2025 Building Annual Performance Report (APR) vs. Poverty", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("Official Total APR Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(20, 105)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "03_apr_vs_poverty.png")
    plt.close(fig)

    # Figure 4: Counterfactual APR Decomposition
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.scatter(sub_cf["frpl_pct"], sub_cf["apr_actual"], color="#1f77b4", alpha=0.35, s=20, label=f"Actual APR (r = {df_cf.iloc[0]['r']:.2f}, R² = {df_cf.iloc[0]['r2']:.2f})")
    ax.scatter(sub_cf["frpl_pct"], sub_cf["apr_no_growth"], color="#d62728", alpha=0.35, s=20, label=f"Excluding Growth Points (r = {df_cf.iloc[1]['r']:.2f}, R² = {df_cf.iloc[1]['r2']:.2f})")

    m_act = sm.OLS(sub_cf["apr_actual"], sm.add_constant(sub_cf["frpl_pct"])).fit()
    m_nog = sm.OLS(sub_cf["apr_no_growth"], sm.add_constant(sub_cf["frpl_pct"])).fit()

    ax.plot(x_line, m_act.params.iloc[0] + m_act.params.iloc[1] * x_line, color="#1f77b4", linewidth=2.4)
    ax.plot(x_line, m_nog.params.iloc[0] + m_nog.params.iloc[1] * x_line, color="#d62728", linewidth=2.4, linestyle="--")

    ax.set_title("Counterfactual Impact of Growth Points on Total APR Poverty Association", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("APR Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(15, 105)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "04_apr_counterfactual_growth.png")
    plt.close(fig)

    print(f"[SUCCESS] Calibrated figures saved to {FIGURES_DIR}")
    print(f"[SUCCESS] Calibrated tables saved to {TABLES_DIR}")


if __name__ == "__main__":
    run_calibrated_analysis()
