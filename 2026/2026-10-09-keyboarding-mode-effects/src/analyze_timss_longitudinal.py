"""
Study D: Longitudinal Econometric Attribution & Psychometric Decomposition (TIMSS 2019–2023)
Evaluates repeated cross-sections Difference-in-Differences models, psychometric IRT benchmarks,
non-response accounting decompositions, historical 31-item mode sensitivity, and screen process timing.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pyreadstat
import statsmodels.formula.api as smf
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR_19 = PROJECT_ROOT / "data" / "raw" / "timss_2019"
RAW_DIR_23 = PROJECT_ROOT / "data" / "raw" / "timss_2023"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

LETTER_TO_NUM = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0}


def score_item(vals: np.ndarray, itype: str, max_pts: int, key: str, psi_unadmin_nr: bool = False):
    """
    Score TIMSS item responses using two-digit diagnostic keys and SPSS missing conventions.
    Returns: score array, is_admin mask, is_omit mask, is_nr mask, is_valid mask.
    """
    is_admin = pd.notna(vals)
    n = len(vals)
    score = np.zeros(n, dtype=float)
    is_omit = np.zeros(n, dtype=bool)
    is_nr = np.zeros(n, dtype=bool)
    is_valid = np.zeros(n, dtype=bool)
    
    if itype == "MC":
        correct_num = LETTER_TO_NUM.get(str(key).strip(), np.nan)
        is_omit[is_admin] = (vals[is_admin] == 9.0)
        is_nr[is_admin] = (vals[is_admin] == 6.0)
        is_valid[is_admin] = np.isin(vals[is_admin], [1.0, 2.0, 3.0, 4.0])
        score[is_admin] = np.where(vals[is_admin] == correct_num, 1.0, 0.0)
    else:  # CR
        is_omit[is_admin] = (vals[is_admin] == 99.0)
        is_nr[is_admin] = (vals[is_admin] == 96.0)
        is_valid[is_admin] = (vals[is_admin] < 90.0) & (vals[is_admin] >= 10.0)
        
        if psi_unadmin_nr:
            nr_mask = is_admin & (vals == 96.0)
            is_admin[nr_mask] = False
            
        if max_pts == 1:
            score[is_admin] = np.where((vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 1.0, 0.0)
        elif max_pts == 2:
            score[is_admin] = np.where(
                (vals[is_admin] >= 20.0) & (vals[is_admin] <= 29.0), 1.0,
                np.where((vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 0.5, 0.0)
            )
        else:
            score[is_admin] = np.where((vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 1.0, 0.0)
            
    return score, is_admin, is_omit, is_nr, is_valid


def build_stacked_panel(item_subset: pd.DataFrame, df19: pd.DataFrame, df23: pd.DataFrame, psi_unadmin: bool = False) -> pd.DataFrame:
    """Build student-by-item stacked repeated cross-sections panel."""
    recs = []
    for _, row in item_subset.iterrows():
        iid19, iid23 = row["item_id_2019"], row["item_id_2023"]
        fmt, itype, max_pts, key = row["format"], row["item_type"], row["max_points"], row["key"]
        is_cr = 1 if itype == "CR" else 0
        is_psi_block = (row["block"] == "A_MD4")
        
        # 2019
        s19, adm19, omit19, nr19, val19 = score_item(
            df19[iid19].values, itype, max_pts, key, 
            psi_unadmin_nr=(psi_unadmin and is_psi_block)
        )
        sub19 = df19[adm19].copy()
        if len(sub19) > 0:
            recs.append(pd.DataFrame({
                "idstud": sub19["IDSTUD"].astype(float).astype(int).astype(str),
                "idschool": sub19["IDSCHOOL"].astype(str) + "_19",
                "idclass": sub19["IDCLASS"].astype(str) + "_19",
                "year": 2019,
                "is_2023": 0,
                "item_id": iid23,
                "format": fmt,
                "is_cr": is_cr,
                "content_domain": row["content_domain"],
                "cognitive_domain": row["cognitive_domain"],
                "block": row["block"],
                "score": s19[adm19],
                "is_omit": omit19[adm19].astype(int),
                "is_nr": nr19[adm19].astype(int),
                "is_valid": val19[adm19].astype(int),
                "totwgt": sub19["TOTWGT"].values,
                "jkzone": sub19["JKZONE"].values,
                "jkrep": sub19["JKREP"].values
            }))
            
        # 2023
        s23, adm23, omit23, nr23, val23 = score_item(
            df23[iid23].values, itype, max_pts, key,
            psi_unadmin_nr=(psi_unadmin and is_psi_block)
        )
        sub23 = df23[adm23].copy()
        if len(sub23) > 0:
            recs.append(pd.DataFrame({
                "idstud": sub23["IDSTUD"].astype(float).astype(int).astype(str),
                "idschool": sub23["IDSCHOOL"].astype(str) + "_23",
                "idclass": sub23["IDCLASS"].astype(str) + "_23",
                "year": 2023,
                "is_2023": 1,
                "item_id": iid23,
                "format": fmt,
                "is_cr": is_cr,
                "content_domain": row["content_domain"],
                "cognitive_domain": row["cognitive_domain"],
                "block": row["block"],
                "score": s23[adm23],
                "is_omit": omit23[adm23].astype(int),
                "is_nr": nr23[adm23].astype(int),
                "is_valid": val23[adm23].astype(int),
                "totwgt": sub23["TOTWGT"].values,
                "jkzone": sub23["JKZONE"].values,
                "jkrep": sub23["JKREP"].values
            }))
            
    df_out = pd.concat(recs, ignore_index=True)
    df_out["score_100"] = df_out["score"] * 100
    df_out["cr_x_2023"] = df_out["is_cr"] * df_out["is_2023"]
    
    # Student-normalized weights
    n_items_per_stud = df_out.groupby("idstud")["item_id"].transform("count")
    df_out["norm_wgt"] = df_out["totwgt"] / n_items_per_stud
    return df_out


def run_longitudinal_models(panel_p84: pd.DataFrame, panel_s100_std: pd.DataFrame, panel_s100_psi: pd.DataFrame) -> pd.DataFrame:
    """Estimate Table 21: Difference-in-Differences models across specifications."""
    specs = [
        ("Model 1: Raw Unadjusted DiD", "score_100 ~ is_2023 + is_cr + cr_x_2023", panel_p84, "totwgt", "Primary 84 Items", 84),
        ("Model 2: Item Fixed Effects DiD (Primary)", "score_100 ~ is_2023 + cr_x_2023 + C(item_id)", panel_p84, "totwgt", "Primary 84 Items", 84),
        ("Model 3: Item FE + Content Domain x Year", "score_100 ~ is_2023 + cr_x_2023 + C(item_id) + C(content_domain):is_2023", panel_p84, "totwgt", "Primary 84 Items", 84),
        ("Model 4: Item FE + Cognitive Domain x Year", "score_100 ~ is_2023 + cr_x_2023 + C(item_id) + C(cognitive_domain):is_2023", panel_p84, "totwgt", "Primary 84 Items", 84),
        ("Model 5: Student-Normalized Weights DiD", "score_100 ~ is_2023 + cr_x_2023 + C(item_id)", panel_p84, "norm_wgt", "Primary 84 Items", 84),
        ("Model 6: Secondary 100 Items (Std Scoring)", "score_100 ~ is_2023 + cr_x_2023 + C(item_id)", panel_s100_std, "totwgt", "Secondary 100 Items", 100),
        ("Model 7: Secondary 100 Items (IEA PSI NR Unadmin)", "score_100 ~ is_2023 + cr_x_2023 + C(item_id)", panel_s100_psi, "totwgt", "Secondary 100 Items", 100),
    ]
    
    rows = []
    for name, form, df, wcol, sname, n_items in specs:
        res = smf.wls(form, data=df, weights=df[wcol]).fit(
            cov_type="cluster", cov_kwds={"groups": df["idschool"]}
        )
        b_mc = res.params["is_2023"]
        se_mc = res.bse["is_2023"]
        b_did = res.params["cr_x_2023"]
        se_did = res.bse["cr_x_2023"]
        p_did = res.pvalues["cr_x_2023"]
        ci = res.conf_int().loc["cr_x_2023"]
        
        rows.append({
            "model_specification": name,
            "sample_tier": sname,
            "n_items": n_items,
            "n_student_item_obs": len(df),
            "n_unique_students": df["idstud"].nunique(),
            "n_schools": df["idschool"].nunique(),
            "mc_baseline_trend_pp": round(b_mc, 2),
            "mc_baseline_trend_se": round(se_mc, 2),
            "did_format_interaction_pp": round(b_did, 2),
            "did_format_interaction_se": round(se_did, 2),
            "ci_95_lower_pp": round(ci[0], 2),
            "ci_95_upper_pp": round(ci[1], 2),
            "p_value": round(p_did, 4),
            "within_practical_bound_2pp": abs(b_did) <= 2.0
        })
    df_t21 = pd.DataFrame(rows)
    df_t21.to_csv(TABLES_DIR / "table21_timss_longitudinal_did_models.csv", index=False)
    return df_t21


def run_nonresponse_decomposition(panel_p84: pd.DataFrame) -> pd.DataFrame:
    """Estimate Table 22: Exact non-response accounting decomposition."""
    subgroups = [("Primary 84 Pool", panel_p84)]
    for dom in sorted(panel_p84["content_domain"].unique()):
        subgroups.append((f"Content: {dom}", panel_p84[panel_p84["content_domain"] == dom]))
    for cog in sorted(panel_p84["cognitive_domain"].unique()):
        subgroups.append((f"Cognitive: {cog}", panel_p84[panel_p84["cognitive_domain"] == cog]))
        
    decomp_records = []
    for gname, sub in subgroups:
        for fmt in ["Multiple Choice", "Constructed Response"]:
            sub_fmt = sub[sub["format"] == fmt]
            p19 = sub_fmt[sub_fmt["year"] == 2019]
            p23 = sub_fmt[sub_fmt["year"] == 2023]
            
            y19 = np.average(p19["score_100"], weights=p19["totwgt"])
            y23 = np.average(p23["score_100"], weights=p23["totwgt"])
            delta_y = y23 - y19
            
            a19 = np.average(p19["is_valid"], weights=p19["totwgt"])
            a23 = np.average(p23["is_valid"], weights=p23["totwgt"])
            delta_a = a23 - a19
            a_bar = 0.5 * (a19 + a23)
            
            s19 = np.average(p19[p19["is_valid"] == 1]["score_100"], weights=p19[p19["is_valid"] == 1]["totwgt"])
            s23 = np.average(p23[p23["is_valid"] == 1]["score_100"], weights=p23[p23["is_valid"] == 1]["totwgt"])
            delta_s = s23 - s19
            s_bar = 0.5 * (s19 + s23)
            
            comp_part = delta_a * s_bar
            perf_part = delta_s * a_bar
            
            decomp_records.append({
                "subgroup": gname,
                "format": fmt,
                "n_items": sub_fmt["item_id"].nunique(),
                "accuracy_2019_pp": round(y19, 2),
                "accuracy_2023_pp": round(y23, 2),
                "total_change_pp": round(delta_y, 2),
                "attempt_rate_2019_pct": round(a19 * 100, 2),
                "attempt_rate_2023_pct": round(a23 * 100, 2),
                "change_in_attempt_rate_pp": round(delta_a * 100, 2),
                "attempted_accuracy_2019_pp": round(s19, 2),
                "attempted_accuracy_2023_pp": round(s23, 2),
                "change_in_attempted_acc_pp": round(delta_s, 2),
                "completion_component_pp": round(comp_part, 2),
                "performance_component_pp": round(perf_part, 2),
                "share_due_to_noncompletion_pct": round((comp_part / delta_y) * 100, 1) if delta_y != 0 else np.nan
            })
            
    df_t22 = pd.DataFrame(decomp_records)
    df_t22.to_csv(TABLES_DIR / "table22_timss_longitudinal_nonresponse_decomposition.csv", index=False)
    return df_t22


def run_historical_mode_sensitivity(panel_p84: pd.DataFrame, p84_meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estimate Table 23: 31-item historical mode sensitivity linkage from Study A."""
    df_contrasts_a = pd.read_csv(PROCESSED_DIR / "timss_2019_g4_item_contrasts.csv")
    
    def get_root(s):
        if not isinstance(s, str): return ""
        for pfx in ["MP", "ME", "MQ", "M"]:
            if s.startswith(pfx): return s[len(pfx):]
        return s
        
    df_contrasts_a["root"] = df_contrasts_a["item_id"].apply(get_root)
    p84_meta["root"] = p84_meta["item_id_2019"].apply(get_root)
    
    # Calculate item-level changes
    trends = []
    for _, row in p84_meta.iterrows():
        iid23 = row["item_id_2023"]
        sub = panel_p84[panel_p84["item_id"] == iid23]
        y19 = np.average(sub[sub["year"] == 2019]["score_100"], weights=sub[sub["year"] == 2019]["totwgt"])
        y23 = np.average(sub[sub["year"] == 2023]["score_100"], weights=sub[sub["year"] == 2023]["totwgt"])
        trends.append({
            "item_id_2023": iid23,
            "root": row["root"],
            "format": row["format"],
            "content_domain": row["content_domain"],
            "cognitive_domain": row["cognitive_domain"],
            "p19": y19,
            "p23": y23,
            "delta_p": y23 - y19
        })
    df_item_trends = pd.DataFrame(trends)
    df_item_trends.to_parquet(PROCESSED_DIR / "timss_2019_2023_item_trends.parquet", index=False)
    
    # Merge with Study A
    merged31 = pd.merge(df_item_trends, df_contrasts_a[["root", "item_id", "pct_paper", "pct_digital", "diff_pp", "modality"]], on="root")
    merged31 = merged31.rename(columns={"diff_pp": "mode_diff_2019_pp", "delta_p": "trend_2019_2023_pp"})
    
    # Split-sample 2019 digital observations to eliminate mechanical correlation
    id_nums = panel_p84["idstud"].astype(str).str.split(".").str[0].astype(int)
    sub_odd = panel_p84[(panel_p84["year"] == 2019) & (id_nums % 2 == 1)]
    sub_even = panel_p84[(panel_p84["year"] == 2019) & (id_nums % 2 == 0)]
    
    odd_means = {iid: np.average(g["score_100"], weights=g["totwgt"]) for iid, g in sub_odd.groupby("item_id")}
    even_means = {iid: np.average(g["score_100"], weights=g["totwgt"]) for iid, g in sub_even.groupby("item_id")}
    
    merged31["p19_split1"] = merged31["item_id_2023"].map(odd_means)
    merged31["p19_split2"] = merged31["item_id_2023"].map(even_means)
    merged31["mode_diff_split1"] = merged31["p19_split1"] - merged31["pct_paper"]
    merged31["trend_split2"] = merged31["p23"] - merged31["p19_split2"]
    
    merged31.to_csv(TABLES_DIR / "table23_timss_historical_mode_sensitivity_31items.csv", index=False)
    return merged31, df_item_trends


def run_screen_timing_panel(df_screens: pd.DataFrame, df19_timing: pd.DataFrame, df23_p: pd.DataFrame) -> pd.DataFrame:
    """Estimate Table 24: Screen-level process timing models across 77 pure screens."""
    p_scr = df_screens[df_screens["in_primary_84_sample"]].copy()
    
    recs = []
    for _, row in p_scr.iterrows():
        sid = row["screen_id"]
        col19 = row["timing_var_2019"]
        col23 = row["timing_var_2023"]
        fmt = row["screen_format_primary_items"]
        is_cr = 1 if fmt == "Constructed Response" else (0 if fmt == "Multiple Choice" else np.nan)
        if np.isnan(is_cr):
            continue
        
        # 2019
        if col19 in df19_timing.columns:
            v19 = df19_timing[col19].dropna()
            v19 = v19[(v19 > 0) & (v19 < 90000)]
            sub19 = df19_timing.loc[v19.index]
            recs.append(pd.DataFrame({
                "idschool": sub19["IDSCHOOL"].astype(str) + "_19",
                "is_2023": 0, "screen_id": sid, "is_cr": is_cr,
                "duration_sec": v19.values, "log_dur": np.log(v19.values),
                "totwgt": sub19["TOTWGT"].values
            }))
        
        # 2023
        if col23 in df23_p.columns:
            v23 = df23_p[col23].dropna()
            v23 = v23[(v23 > 0) & (v23 < 90000)]
            sub23 = df23_p.loc[v23.index]
            recs.append(pd.DataFrame({
                "idschool": sub23["IDSCHOOL"].astype(str) + "_23",
                "is_2023": 1, "screen_id": sid, "is_cr": is_cr,
                "duration_sec": v23.values, "log_dur": np.log(v23.values),
                "totwgt": sub23["TOTWGT"].values
            }))
        
    df_stk = pd.concat(recs, ignore_index=True)
    df_stk["cr_x_2023"] = df_stk["is_cr"] * df_stk["is_2023"]
    df_stk.to_parquet(PROCESSED_DIR / "timss_2019_2023_screen_longitudinal_panel.parquet", index=False)
    
    mod_dur = smf.wls("duration_sec ~ is_2023 + cr_x_2023 + C(screen_id)", data=df_stk, weights=df_stk["totwgt"]).fit(
        cov_type="cluster", cov_kwds={"groups": df_stk["idschool"]}
    )
    mod_log = smf.wls("log_dur ~ is_2023 + cr_x_2023 + C(screen_id)", data=df_stk, weights=df_stk["totwgt"]).fit(
        cov_type="cluster", cov_kwds={"groups": df_stk["idschool"]}
    )
    
    ci_dur = mod_dur.conf_int().loc["cr_x_2023"]
    ci_log = mod_log.conf_int().loc["cr_x_2023"]
    
    t24_rows = [
        {
            "metric": "Screen Total Duration (Seconds)",
            "n_obs": len(df_stk),
            "n_screens": df_stk["screen_id"].nunique(),
            "mc_baseline_trend": round(mod_dur.params["is_2023"], 2),
            "mc_baseline_se": round(mod_dur.bse["is_2023"], 2),
            "cr_differential_interaction": round(mod_dur.params["cr_x_2023"], 2),
            "cr_differential_se": round(mod_dur.bse["cr_x_2023"], 2),
            "ci_95_lower": round(ci_dur[0], 2),
            "ci_95_upper": round(ci_dur[1], 2),
            "p_value": round(mod_dur.pvalues["cr_x_2023"], 6)
        },
        {
            "metric": "Log Screen Duration (ln Seconds)",
            "n_obs": len(df_stk),
            "n_screens": df_stk["screen_id"].nunique(),
            "mc_baseline_trend": round(mod_log.params["is_2023"], 4),
            "mc_baseline_se": round(mod_log.bse["is_2023"], 4),
            "cr_differential_interaction": round(mod_log.params["cr_x_2023"], 4),
            "cr_differential_se": round(mod_log.bse["cr_x_2023"], 4),
            "ci_95_lower": round(ci_log[0], 4),
            "ci_95_upper": round(ci_log[1], 4),
            "p_value": round(mod_log.pvalues["cr_x_2023"], 6)
        }
    ]
    df_t24 = pd.DataFrame(t24_rows)
    df_t24.to_csv(TABLES_DIR / "table24_timss_screen_behavioral_panel.csv", index=False)
    return df_t24


def run_irt_and_counterfactuals(df_did: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate Table 25: Exploratory Synthetic IRT Sensitivity Demonstration.
    Illustrates how non-linear guessing floors and item discrimination differences create 
    natural format divergence under uniform latent ability shifts.
    
    CRITICAL METHODOLOGICAL QUALIFICATION:
    This is an exploratory parameter sensitivity simulation across illustrative 3PL/2PL curves.
    It does NOT use calibrated TIMSS item parameters or empirical scale transformations.
    Consequently, it demonstrates theoretical mechanics rather than providing a causal attribution estimate.
    """
    np.random.seed(42)
    n_sim = 200_000
    th_base = np.random.normal(0.0, 1.0, n_sim)
    
    def p_3pl(th, a, b, c):
        return c + (1.0 - c) / (1.0 + np.exp(-a * (th - b)))
        
    # Baseline observed DiD interaction from Model 2
    b_obs = df_did.loc[df_did["model_specification"].str.contains("Model 2"), "did_format_interaction_pp"].iloc[0]
    
    scenarios = [
        ("Scenario 1: Canonical (a_MC=1.00, a_CR=1.20, c=0.25; TIMSS Scale SD 100)", -17.80 / 100.0, 1.00, 1.20, 0.25, 0.0, "Scale SD 100 (-0.178 SD)"),
        ("Scenario 2: Canonical (a_MC=1.00, a_CR=1.20, c=0.25; Sample SD ~80)", -17.80 / 80.0, 1.00, 1.20, 0.25, 0.0, "Sample SD ~80 (-0.223 SD)"),
        ("Scenario 3: Balanced Discrimination (a_MC=1.00, a_CR=1.05, c=0.25; Scale SD 100)", -17.80 / 100.0, 1.00, 1.05, 0.25, 0.0, "Scale SD 100 (-0.178 SD)"),
        ("Scenario 4: High CR Discrimination (a_MC=0.95, a_CR=1.35, c=0.25; Scale SD 100)", -17.80 / 100.0, 0.95, 1.35, 0.25, 0.0, "Scale SD 100 (-0.178 SD)"),
        ("Scenario 5: Lower Guessing Floor (a_MC=1.05, a_CR=1.15, c=0.15; Scale SD 100)", -17.80 / 100.0, 1.05, 1.15, 0.15, 0.0, "Scale SD 100 (-0.178 SD)"),
    ]
    
    t25_rows = []
    for sname, d_th, a_m, a_c, c_m, c_c, basis in scenarios:
        th_post = np.random.normal(d_th, 1.0, n_sim)
        
        # MC expected drop
        p19_m = p_3pl(th_base, a_m, 0.0, c_m).mean() * 100
        p23_m = p_3pl(th_post, a_m, 0.0, c_m).mean() * 100
        d_mc_exp = p23_m - p19_m
        
        # CR expected drop
        p19_c = p_3pl(th_base, a_c, 0.2, c_c).mean() * 100
        p23_c = p_3pl(th_post, a_c, 0.2, c_c).mean() * 100
        d_cr_exp = p23_c - p19_c
        
        b_exp = d_cr_exp - d_mc_exp
        gap_diff = b_obs - b_exp
        
        interpretation = (
            "Observed interaction smaller than synthetic IRT gap (relative CR stability)" 
            if gap_diff > 0.10 
            else ("Observed interaction closely matches synthetic IRT gap" if abs(gap_diff) <= 0.10 else "Observed interaction exceeds synthetic IRT gap (additional CR decline)")
        )
        
        t25_rows.append({
            "scenario": sname,
            "latent_shift_basis": basis,
            "delta_theta_sd": round(d_th, 4),
            "illustrative_a_mc": a_m,
            "illustrative_a_cr": a_c,
            "illustrative_c_mc": c_m,
            "expected_mc_drop_pp": round(d_mc_exp, 2),
            "expected_cr_drop_pp": round(d_cr_exp, 2),
            "beta_expected_pp": round(b_exp, 2),
            "beta_observed_pp": round(b_obs, 2),
            "gap_difference_pp": round(gap_diff, 2),
            "sensitivity_interpretation": interpretation
        })
        
    df_t25 = pd.DataFrame(t25_rows)
    df_t25.to_csv(TABLES_DIR / "table25_timss_longitudinal_irt_counterfactuals.csv", index=False)
    return df_t25


def main():
    print("================================================================================")
    print("STUDY D: TIMSS 2019–2023 LONGITUDINAL ATTRIBUTION & PSYCHOMETRIC PIPELINE")
    print("================================================================================")
    
    # 1. Load Crosswalk & Key Information
    print("\n[1/6] Loading Crosswalk & Codebooks...")
    df_cw = pd.read_csv(TABLES_DIR / "table19_timss_2019_2023_item_crosswalk.csv")
    p84 = df_cw[df_cw["in_primary_scaling_sample"]].copy()
    s100 = df_cw[df_cw["in_psi_robustness_sample"]].copy()
    
    df_info = pd.read_excel(RAW_DIR_23 / "T23_ItemInformation_G4.xlsx", sheet_name="T23 G4")
    key_map = dict(zip(df_info["Item ID"], df_info["Key "]))
    p84["key"] = p84["item_id_2023"].map(key_map).fillna("")
    s100["key"] = s100["item_id_2023"].map(key_map).fillna("")
    
    # 2. Load Raw Microdata
    print("\n[2/6] Loading Public-Use Microdata Files...")
    items19_p84 = p84["item_id_2019"].tolist()
    df19_std, _ = pyreadstat.read_sav(RAW_DIR_19 / "asausam7.sav", 
                                      usecols=["IDSTUD", "IDSCHOOL", "IDCLASS", "IDBOOK", "TOTWGT", "JKZONE", "JKREP"] + items19_p84, 
                                      user_missing=True)
    
    items19_s100 = s100["item_id_2019"].tolist()
    df19_psi, _ = pyreadstat.read_sav(RAW_DIR_19 / "asausaz7.sav", 
                                      usecols=["IDSTUD", "IDSCHOOL", "IDCLASS", "IDBOOK", "TOTWGT", "JKZONE", "JKREP"] + items19_s100, 
                                      user_missing=True)
    
    items23_s100 = s100["item_id_2023"].tolist()
    df23, _ = pyreadstat.read_sav(RAW_DIR_23 / "asausam8.sav", 
                                  usecols=["IDSTUD", "IDSCHOOL", "IDCLASS", "IDBOOK", "TOTWGT", "JKZONE", "JKREP"] + items23_s100, 
                                  user_missing=True)
    
    print(f"  [OK] 2019 Standard eTIMSS: N = {len(df19_std):,} examinees (Booklets 1–14)")
    print(f"  [OK] 2019 PSI Research:    N = {len(df19_psi):,} examinees (Booklets 1–16)")
    print(f"  [OK] 2023 Digital TIMSS:   N = {len(df23):,} examinees (Booklets 1–14)")
    
    # 3. Stacked Observation Panels
    print("\n[3/6] Constructing Student-by-Item Panels...")
    panel_p84 = build_stacked_panel(p84, df19_std, df23)
    panel_s100_std = build_stacked_panel(s100, df19_psi, df23, psi_unadmin=False)
    panel_s100_psi = build_stacked_panel(s100, df19_psi, df23, psi_unadmin=True)
    
    panel_p84.to_parquet(PROCESSED_DIR / "timss_2019_2023_longitudinal_student_item.parquet", index=False)
    print(f"  [OK] Primary 84 Stacked Panel: {len(panel_p84):,} rows ({panel_p84['idstud'].nunique():,} students)")
    
    # 4. Difference-in-Differences Models (Table 21)
    print("\n[4/6] Estimating Difference-in-Differences Models (Table 21)...")
    df_t21 = run_longitudinal_models(panel_p84, panel_s100_std, panel_s100_psi)
    print("  Table 21 Model 2 Primary DiD Result:")
    m2 = df_t21[df_t21["model_specification"].str.contains("Model 2")].iloc[0]
    print(f"    MC Baseline Trend:     {m2['mc_baseline_trend_pp']:+.2f} pp (SE: {m2['mc_baseline_trend_se']:.2f})")
    print(f"    CR Format Interaction: {m2['did_format_interaction_pp']:+.2f} pp (SE: {m2['did_format_interaction_se']:.2f}, p={m2['p_value']:.4f})")
    print(f"    95% Confidence Interval: [{m2['ci_95_lower_pp']:+.2f}, {m2['ci_95_upper_pp']:+.2f}] pp")
    
    # 5. Non-Response Accounting Decomposition (Table 22)
    print("\n[5/6] Computing Non-Response Accounting Decomposition (Table 22)...")
    df_t22 = run_nonresponse_decomposition(panel_p84)
    print("  Table 22 Primary Summary:")
    print(df_t22[df_t22["subgroup"] == "Primary 84 Pool"][["format", "total_change_pp", "completion_component_pp", "performance_component_pp", "share_due_to_noncompletion_pct"]])
    
    # 6. Historical 31-Item Mode Sensitivity & Screen Timing & IRT Benchmarks
    print("\n[6/6] Estimating Sensitivity, Process Timing, & Psychometric Benchmarks...")
    merged31, df_item_trends = run_historical_mode_sensitivity(panel_p84, p84)
    
    df_screens = pd.read_csv(TABLES_DIR / "table20_timss_2019_2023_screen_timing.csv")
    p_scr = df_screens[df_screens["in_primary_84_sample"]]
    tcols19 = [c for c in p_scr["timing_var_2019"] if c]
    tcols23 = [c for c in p_scr["timing_var_2023"] if c]
    df19_timing, _ = pyreadstat.read_sav(RAW_DIR_19 / "asausaz7.sav", usecols=["IDSTUD", "IDSCHOOL", "TOTWGT"] + tcols19)
    df23_p, _ = pyreadstat.read_sav(RAW_DIR_23 / "aspusam8.sav", usecols=["IDSTUD", "IDSCHOOL", "TOTWGT"] + tcols23)
    df_t24 = run_screen_timing_panel(df_screens, df19_timing, df23_p)
    
    df_t25 = run_irt_and_counterfactuals(df_t21)
    
    print("\n[SUCCESS] Study D Analysis Pipeline Complete.")
    print("================================================================================")


if __name__ == "__main__":
    main()
