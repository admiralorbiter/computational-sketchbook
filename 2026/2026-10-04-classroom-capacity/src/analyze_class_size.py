"""
Analysis Suite for Study A: Empirical Classroom Size & Capacity Measurement.
Covers:
- Analysis A1: Longitudinal distributions across National, State, and Kansas City populations.
- Analysis A2: Course-level hierarchy (Foundation Core vs. Advanced Electives).
- Analysis A3: Weighting sensitivity (Course-Cell vs. Section-Weighted vs. Student/Seat-Weighted).
- Analysis A4: Staffing allocation wedge (Class Size vs. Contemporaneous PTR).
- Analysis A5: Within-school course hierarchy (School Fixed Effects).
- Analysis A6: Longitudinal robustness (Repeated Cross-Section vs. Balanced Panel).
Outputs tables to artifacts/tables/ and figures to artifacts/figures/.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

DATA_DIR = PROJECT_DIR / "data" / "processed"
TABLES_DIR = PROJECT_DIR / "artifacts" / "tables"
FIGURES_DIR = PROJECT_DIR / "artifacts" / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Visual styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

def load_data():
    """Load the harmonized parquet panel and clean bounds."""
    df = pd.read_parquet(DATA_DIR / "crdc_course_panel.parquet")
    # Clean analytical sample: non-zero, plausible bounds (<= 60 for clean distributions)
    valid_mask = (df["mean_class_size"] > 0) & (df["mean_class_size"] <= 60)
    df_valid = df[valid_mask].copy()
    df_valid["school_wave_id"] = df_valid["nces_school_id"] + "_" + df_valid["crdc_wave"]
    return df, df_valid

def run_analysis_a1_and_a2(df_valid):
    """
    Analysis A1 & A2: Distribution of school-course mean class sizes by wave and course.
    Calculates course-cell mean, section-weighted mean, seat-weighted mean, percentiles,
    and exposure bins (<20, 20-24, 25-29, 30-34, 35+).
    """
    print("--> Running Analysis A1 & A2: Wave & Course Distributions...")
    results = []
    
    for (wave, ccode), g in df_valid.groupby(["crdc_wave", "course_code"]):
        cname = g["course_name"].iloc[0]
        clevel = g["course_level"].iloc[0]
        n_schools = g["nces_school_id"].nunique()
        tot_cls = g["num_classes"].sum()
        tot_enr = g["num_enrolled"].sum()
        cs = g["mean_class_size"]
        
        unwt_mean = cs.mean()
        sec_wt = tot_enr / tot_cls if tot_cls > 0 else np.nan
        seat_wt = (g["num_enrolled"] * cs).sum() / tot_enr if tot_enr > 0 else np.nan
        
        med = cs.median()
        p25 = cs.quantile(0.25)
        p75 = cs.quantile(0.75)
        p90 = cs.quantile(0.90)
        p95 = cs.quantile(0.95)
        std = cs.std()
        
        # Exposure shares across bins
        sh_under_20 = (cs < 20).mean() * 100
        sh_20_24 = ((cs >= 20) & (cs < 25)).mean() * 100
        sh_25_29 = ((cs >= 25) & (cs < 30)).mean() * 100
        sh_30_34 = ((cs >= 30) & (cs < 35)).mean() * 100
        sh_35_plus = (cs >= 35).mean() * 100
        
        sh_ge_25 = (cs >= 25).mean() * 100
        sh_ge_30 = (cs >= 30).mean() * 100
        sh_ge_35 = (cs >= 35).mean() * 100
        
        # Seat-weighted exposure shares (the share of student enrollment in those cells)
        seat_ge_25 = (g.loc[cs >= 25, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        seat_ge_30 = (g.loc[cs >= 30, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        seat_ge_35 = (g.loc[cs >= 35, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        
        results.append({
            "crdc_wave": wave,
            "course_code": ccode,
            "course_name": cname,
            "course_level": clevel,
            "n_schools": n_schools,
            "total_classes": tot_cls,
            "total_students": tot_enr,
            "course_cell_mean": unwt_mean,
            "section_weighted_mean": sec_wt,
            "seat_weighted_mean": seat_wt,
            "std_dev": std,
            "median": med,
            "p25": p25,
            "p75": p75,
            "p90": p90,
            "p95": p95,
            "cell_pct_under_20": sh_under_20,
            "cell_pct_20_24": sh_20_24,
            "cell_pct_25_29": sh_25_29,
            "cell_pct_30_34": sh_30_34,
            "cell_pct_35_plus": sh_35_plus,
            "cell_pct_ge_25": sh_ge_25,
            "cell_pct_ge_30": sh_ge_30,
            "cell_pct_ge_35": sh_ge_35,
            "seat_pct_ge_25": seat_ge_25,
            "seat_pct_ge_30": seat_ge_30,
            "seat_pct_ge_35": seat_ge_35,
        })
        
    df_res = pd.DataFrame(results)
    out_csv = TABLES_DIR / "table01_national_course_distributions.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"--> Saved Table 01 to {out_csv}")
    return df_res

def run_analysis_a3(df_valid):
    """
    Analysis A3: Weighting sensitivity.
    Directly quantifies the divergence between:
    - Quantity A: Unweighted course-cell mean (mean of school-course averages)
    - Quantity B: Section-weighted mean (total enrollment / total classes)
    - Quantity C: Enrollment-weighted course-cell mean (lower-bound proxy for student-experienced size)
    And calculates the three distinct gaps:
    - Gap C - A: Enrollment-weighted vs. unweighted course-cell mean
    - Gap C - B: Enrollment-weighted vs. section-weighted mean (Jensen's inequality gap)
    - Gap B - A: Section-weighted vs. unweighted course-cell mean (institutional size gap)
    """
    print("--> Running Analysis A3: Weighting Sensitivity Analysis...")
    rows = []
    
    for wave in ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]:
        w_df = df_valid[df_valid["crdc_wave"] == wave]
        for ccode in ["alg1", "geom", "alg2", "calc", "bio", "chem", "phys", "advm"]:
            cg = w_df[w_df["course_code"] == ccode]
            if cg.empty:
                continue
            cname = cg["course_name"].iloc[0]
            n_cells = len(cg)
            unwt_a = cg["mean_class_size"].mean()
            tot_enr = cg["num_enrolled"].sum()
            tot_cls = cg["num_classes"].sum()
            sec_wt_b = tot_enr / tot_cls if tot_cls > 0 else np.nan
            enr_wt_c = (cg["num_enrolled"] * cg["mean_class_size"]).sum() / tot_enr if tot_enr > 0 else np.nan
            
            gap_c_minus_a = enr_wt_c - unwt_a
            pct_gap_c_minus_a = (gap_c_minus_a / unwt_a) * 100 if unwt_a > 0 else np.nan
            
            gap_c_minus_b = enr_wt_c - sec_wt_b
            pct_gap_c_minus_b = (gap_c_minus_b / sec_wt_b) * 100 if sec_wt_b > 0 else np.nan
            
            gap_b_minus_a = sec_wt_b - unwt_a
            pct_gap_b_minus_a = (gap_b_minus_a / unwt_a) * 100 if unwt_a > 0 else np.nan
            
            rows.append({
                "wave": wave,
                "course_code": ccode,
                "course_name": cname,
                "valid_cells_n": n_cells,
                "unweighted_cell_mean_a": unwt_a,
                "section_weighted_mean_b": sec_wt_b,
                "enrollment_weighted_mean_c": enr_wt_c,
                "gap_c_minus_a": gap_c_minus_a,
                "pct_gap_c_minus_a": pct_gap_c_minus_a,
                "gap_c_minus_b": gap_c_minus_b,
                "pct_gap_c_minus_b": pct_gap_c_minus_b,
                "gap_b_minus_a": gap_b_minus_a,
                "pct_gap_b_minus_a": pct_gap_b_minus_a,
                # Retain legacy column names for compatibility
                "course_cell_mean": unwt_a,
                "section_weighted_mean": sec_wt_b,
                "seat_weighted_mean": enr_wt_c,
                "seat_minus_cell_gap": gap_c_minus_a,
                "seat_minus_sec_gap": gap_c_minus_b,
                "pct_increase_seat_weighting": pct_gap_c_minus_a,
            })
            
    df_wt = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table02_weighting_comparison.csv"
    df_wt.to_csv(out_csv, index=False)
    print(f"--> Saved Table 02 to {out_csv}")
    return df_wt

def run_analysis_a4(df_valid):
    """
    Analysis A4: PTR Staffing Wedge.
    Computes absolute wedge (ClassSize - PTR) and wedge ratio (ClassSize / PTR).
    Compares national, Missouri, Kansas, and Kansas City metro.
    """
    print("--> Running Analysis A4: Staffing Allocation Wedge...")
    sub = df_valid[pd.notnull(df_valid["school_ptr"]) & (df_valid["school_ptr"] > 0) & (df_valid["school_ptr"] <= 50)].copy()
    
    rows = []
    pops = [
        ("National", sub),
        ("Missouri (Statewide)", sub[sub["state"] == "MO"]),
        ("Kansas (Statewide)", sub[sub["state"] == "KS"]),
        ("Kansas City Metro", sub[sub["is_kc_metro"] == True]),
    ]
    
    for pop_name, pop_df in pops:
        if pop_df.empty:
            continue
        for wave in ["2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]:
            w_df = pop_df[pop_df["crdc_wave"] == wave]
            if w_df.empty:
                continue
            
            mean_cs = w_df["mean_class_size"].mean()
            median_cs = w_df["mean_class_size"].median()
            tot_enr = w_df["num_enrolled"].sum()
            tot_cls = w_df["num_classes"].sum()
            sec_wt_cs = tot_enr / tot_cls if tot_cls > 0 else np.nan
            enr_wt_cs = (w_df["num_enrolled"] * w_df["mean_class_size"]).sum() / tot_enr if tot_enr > 0 else np.nan
            
            mean_ptr = w_df["school_ptr"].mean()
            median_ptr = w_df["school_ptr"].median()
            
            cell_wedge = w_df["ptr_wedge"]
            cell_ratio = w_df["ptr_wedge_ratio"]
            enr_wedge = enr_wt_cs - mean_ptr
            enr_ratio = enr_wt_cs / mean_ptr if mean_ptr > 0 else np.nan
            
            rows.append({
                "population": pop_name,
                "wave": wave,
                "n_observations": len(w_df),
                "schools_n": w_df["nces_school_id"].nunique(),
                "mean_class_size_cell": mean_cs,
                "median_class_size_cell": median_cs,
                "section_weighted_class_size": sec_wt_cs,
                "enrollment_weighted_class_size": enr_wt_cs,
                "mean_school_ptr": mean_ptr,
                "median_school_ptr": median_ptr,
                "mean_cell_wedge": cell_wedge.mean(),
                "median_cell_wedge": cell_wedge.median(),
                "mean_cell_wedge_ratio": cell_ratio.mean(),
                "median_cell_wedge_ratio": cell_ratio.median(),
                "enrollment_weighted_wedge": enr_wedge,
                "enrollment_weighted_wedge_ratio": enr_ratio,
                "pct_schools_class_size_gt_ptr": (cell_wedge > 0).mean() * 100,
                # Legacy compatibility
                "mean_class_size": mean_cs,
                "median_class_size": median_cs,
                "mean_absolute_wedge": cell_wedge.mean(),
                "median_absolute_wedge": cell_wedge.median(),
                "mean_wedge_ratio": cell_ratio.mean(),
                "median_wedge_ratio": cell_ratio.median(),
            })
            
    df_wedge = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table03_ptr_wedge_summary.csv"
    df_wedge.to_csv(out_csv, index=False)
    print(f"--> Saved Table 03 to {out_csv}")
    return df_wedge

def estimate_fe_demeaned(df_sample, depvar="mean_class_size", weights_col=None, cluster_col="nces_school_id", group_col="school_wave_id", ref_course="geom"):
    """
    Frisch-Waugh-Lovell within-estimator for school x wave fixed effects + course fixed effects,
    with clustered standard errors at the school level, absorbed-FE finite-sample degrees-of-freedom adjustment, and Student's t inference.
    Excludes non-informative groups with fewer than 2 distinct courses.
    """
    df = df_sample.copy()
    
    # Filter out non-informative groups with < 2 courses
    grp_counts = df.groupby(group_col)["course_code"].nunique()
    valid_groups = grp_counts[grp_counts >= 2].index
    df = df[df[group_col].isin(valid_groups)].copy()
    
    all_courses = sorted(df["course_code"].unique())
    reg_courses = [c for c in all_courses if c != ref_course]
    
    for c in reg_courses:
        df[f"d_{c}"] = (df["course_code"] == c).astype(float)
        
    dummy_cols = [f"d_{c}" for c in reg_courses]
    
    if weights_col is not None:
        w = df[weights_col].values
        df["_w"] = w
        df["_wy"] = w * df[depvar]
        for c in dummy_cols:
            df[f"_w_{c}"] = w * df[c]
            
        grp_w = df.groupby(group_col)["_w"].transform("sum")
        df["_y_mean"] = df.groupby(group_col)["_wy"].transform("sum") / grp_w
        df["_y_tilde"] = df[depvar] - df["_y_mean"]
        
        for c in dummy_cols:
            mean_c = df.groupby(group_col)[f"_w_{c}"].transform("sum") / grp_w
            df[f"_{c}_tilde"] = df[c] - mean_c
            
        X_tilde = df[[f"_{c}_tilde" for c in dummy_cols]]
        y_tilde = df["_y_tilde"]
        mod = sm.WLS(y_tilde, X_tilde, weights=w)
    else:
        df["_y_mean"] = df.groupby(group_col)[depvar].transform("mean")
        df["_y_tilde"] = df[depvar] - df["_y_mean"]
        
        for c in dummy_cols:
            mean_c = df.groupby(group_col)[c].transform("mean")
            df[f"_{c}_tilde"] = df[c] - mean_c
            
        X_tilde = df[[f"_{c}_tilde" for c in dummy_cols]]
        y_tilde = df["_y_tilde"]
        mod = sm.OLS(y_tilde, X_tilde)
        
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": df[cluster_col]})
    
    N = len(df)
    K = len(dummy_cols)
    G = df[group_col].nunique()
    n_clusters = df[cluster_col].nunique()
    # Absorbed-FE finite-sample adjustment factor:
    # Statsmodels cluster covariance scales by (N-1)/(N-K), but demeaned OLS does not subtract
    # the G absorbed fixed effects from residual degrees of freedom. Multiplying SE by
    # sqrt((N-K)/(N-K-G)) adjusts for absorbed dimensions.
    absorbed_fe_factor = np.sqrt((N - K) / max(1, (N - K - G)))
    df_t = max(1, n_clusters - 1)
    t_crit = stats.t.ppf(0.975, df=df_t)
    
    course_labels = {
        "alg1": "Algebra I", "geom": "Geometry (Ref)", "alg2": "Algebra II",
        "advm": "Advanced Math", "calc": "Calculus", "bio": "Biology",
        "chem": "Chemistry", "phys": "Physics"
    }
    
    results = []
    for c in reg_courses:
        col_name = f"_d_{c}_tilde"
        coef = res.params[col_name]
        se_cluster_only = res.bse[col_name]
        se = se_cluster_only * absorbed_fe_factor
        tstat = coef / se
        pval = 2 * (1 - stats.t.cdf(abs(tstat), df=df_t))
        results.append({
            "course_code": c,
            "course_name": course_labels.get(c, c),
            "coef_vs_geom": coef,
            "std_err": se,
            "std_err_cluster_only": se_cluster_only,
            "absorbed_fe_factor": absorbed_fe_factor,
            "t_stat": tstat,
            "p_value": pval,
            "ci_95_low": coef - t_crit * se,
            "ci_95_high": coef + t_crit * se,
        })
        
    return pd.DataFrame(results), N, G, n_clusters

def estimate_fe_pairwise(df_sample, target_course, ref_course="geom", weights_col=None, cluster_col="nces_school_id", group_col="school_wave_id"):
    """
    Direct pairwise within-school comparison: restrict strictly to school-waves containing
    BOTH ref_course and target_course. Fits school x wave FE with school-level clustering.
    Applies absorbed-FE finite-sample adjustment.
    """
    sub = df_sample[df_sample["course_code"].isin([ref_course, target_course])].copy()
    counts = sub.groupby(group_col)["course_code"].nunique()
    both_sw = counts[counts == 2].index
    pair_df = sub[sub[group_col].isin(both_sw)].copy()
    
    pair_df["d_target"] = (pair_df["course_code"] == target_course).astype(float)
    
    if weights_col is not None:
        w = pair_df[weights_col].values
        pair_df["_w"] = w
        pair_df["_wy"] = w * pair_df["mean_class_size"]
        pair_df["_wd"] = w * pair_df["d_target"]
        
        grp_w = pair_df.groupby(group_col)["_w"].transform("sum")
        y_mean = pair_df.groupby(group_col)["_wy"].transform("sum") / grp_w
        d_mean = pair_df.groupby(group_col)["_wd"].transform("sum") / grp_w
        
        pair_df["y_tilde"] = pair_df["mean_class_size"] - y_mean
        pair_df["d_tilde"] = pair_df["d_target"] - d_mean
        
        mod = sm.WLS(pair_df["y_tilde"], pair_df[["d_tilde"]], weights=w)
    else:
        y_mean = pair_df.groupby(group_col)["mean_class_size"].transform("mean")
        d_mean = pair_df.groupby(group_col)["d_target"].transform("mean")
        pair_df["y_tilde"] = pair_df["mean_class_size"] - y_mean
        pair_df["d_tilde"] = pair_df["d_target"] - d_mean
        mod = sm.OLS(pair_df["y_tilde"], pair_df[["d_tilde"]])
        
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": pair_df[cluster_col]})
    
    N = len(pair_df)
    K = 1
    G = pair_df[group_col].nunique()
    n_clusters = pair_df[cluster_col].nunique()
    absorbed_fe_factor = np.sqrt((N - K) / max(1, (N - K - G)))
    df_t = max(1, n_clusters - 1)
    
    coef = res.params["d_tilde"]
    se_cluster_only = res.bse["d_tilde"]
    se = se_cluster_only * absorbed_fe_factor
    tstat = coef / se
    pval = 2 * (1 - stats.t.cdf(abs(tstat), df=df_t))
    t_crit = stats.t.ppf(0.975, df=df_t)
    
    course_labels = {
        "alg1": "Algebra I", "geom": "Geometry (Ref)", "alg2": "Algebra II",
        "advm": "Advanced Math", "calc": "Calculus", "bio": "Biology",
        "chem": "Chemistry", "phys": "Physics"
    }
    
    return {
        "target_course": target_course,
        "target_course_name": course_labels.get(target_course, target_course),
        "ref_course": ref_course,
        "ref_course_name": course_labels.get(ref_course, ref_course),
        "n_obs": N,
        "n_school_wave_fe": G,
        "n_clusters": n_clusters,
        "coef_pairwise": coef,
        "std_err": se,
        "std_err_cluster_only": se_cluster_only,
        "absorbed_fe_factor": absorbed_fe_factor,
        "t_stat": tstat,
        "p_value": pval,
        "ci_95_low": coef - t_crit * se,
        "ci_95_high": coef + t_crit * se,
    }

def run_analysis_a5(df_valid):
    """
    Analysis A5: Within-School Course Hierarchy (School x Wave Fixed Effects).
    ClassSize_{sct} = alpha_{st} + gamma_c + epsilon_{sct}
    Estimates whether foundation core courses absorb systematically larger classes
    than advanced electives within the exact same school building during the exact same year.
    Reference course: Geometry (due to contemporaneous fall snapshot alignment).
    Clusters standard errors at the school level with absorbed-FE finite-sample adjustment and Student's t inference.
    Runs unweighted, section-weighted, Algebra-I-excluded, and direct pairwise Geometry models.
    """
    print("--> Running Analysis A5: Within-School Fixed Effects Models (School x Wave FE)...")
    
    samples = [
        ("Kansas City Metro", df_valid[df_valid["is_kc_metro"] == True]),
        ("MO and KS Statewide", df_valid[df_valid["state"].isin(["MO", "KS"])]),
        ("National Full Panel", df_valid),
    ]
    
    all_results = []
    
    for sname, sdata in samples:
        # Require at least 2 courses per school-wave
        multi = sdata.groupby("school_wave_id")["course_code"].nunique()
        valid_sw = multi[multi >= 2].index
        reg_df = sdata[sdata["school_wave_id"].isin(valid_sw)].copy()
        
        # 1. Unweighted OLS (School x Wave FE, Clustered SE by School)
        res_unwt, n_obs, n_fe, n_clusters = estimate_fe_demeaned(reg_df, weights_col=None)
        res_unwt["sample"] = sname
        res_unwt["weighting"] = "Unweighted"
        res_unwt["specification"] = "Full Hierarchy (Ref: Geometry)"
        res_unwt["n_obs"] = n_obs
        res_unwt["n_school_wave_fe"] = n_fe
        res_unwt["n_clusters"] = n_clusters
        all_results.append(res_unwt)
        
        # 2. Section-Weighted WLS (School x Wave FE, Clustered SE by School)
        res_wt, n_obs, n_fe, n_clusters = estimate_fe_demeaned(reg_df, weights_col="num_classes")
        res_wt["sample"] = sname
        res_wt["weighting"] = "Section-Weighted"
        res_wt["specification"] = "Full Hierarchy (Ref: Geometry)"
        res_wt["n_obs"] = n_obs
        res_wt["n_school_wave_fe"] = n_fe
        res_wt["n_clusters"] = n_clusters
        all_results.append(res_wt)
        
        # 3. Sensitivity: Excluding Algebra I (Section-Weighted)
        reg_df_no_alg1 = reg_df[reg_df["course_code"] != "alg1"].copy()
        multi_no_alg1 = reg_df_no_alg1.groupby("school_wave_id")["course_code"].nunique()
        reg_df_no_alg1 = reg_df_no_alg1[reg_df_no_alg1["school_wave_id"].isin(multi_no_alg1[multi_no_alg1 >= 2].index)]
        res_no_alg1, n_obs, n_fe, n_clusters = estimate_fe_demeaned(reg_df_no_alg1, weights_col="num_classes")
        res_no_alg1["sample"] = sname
        res_no_alg1["weighting"] = "Section-Weighted"
        res_no_alg1["specification"] = "Sensitivity: Excluding Algebra I (Ref: Geometry)"
        res_no_alg1["n_obs"] = n_obs
        res_no_alg1["n_school_wave_fe"] = n_fe
        res_no_alg1["n_clusters"] = n_clusters
        all_results.append(res_no_alg1)
        
    df_fe = pd.concat(all_results, ignore_index=True)
    out_csv = TABLES_DIR / "table04_fixed_effects_coefficients.csv"
    df_fe.to_csv(out_csv, index=False)
    print(f"--> Saved Table 04 to {out_csv}")
    
    # 4. Direct Pairwise Geometry Models (Table 04b)
    print("--> Running Direct Pairwise Geometry Robustness Models...")
    pairwise_rows = []
    nat_df = df_valid.copy()
    multi_nat = nat_df.groupby("school_wave_id")["course_code"].nunique()
    nat_reg = nat_df[nat_df["school_wave_id"].isin(multi_nat[multi_nat >= 2].index)].copy()
    
    target_courses = ["calc", "phys", "advm", "chem", "alg2", "bio", "alg1"]
    for tc in target_courses:
        # Section-weighted pairwise
        r_wt = estimate_fe_pairwise(nat_reg, target_course=tc, ref_course="geom", weights_col="num_classes")
        r_wt["sample"] = "National Full Panel"
        r_wt["weighting"] = "Section-Weighted"
        pairwise_rows.append(r_wt)
        
        # Unweighted pairwise
        r_unwt = estimate_fe_pairwise(nat_reg, target_course=tc, ref_course="geom", weights_col=None)
        r_unwt["sample"] = "National Full Panel"
        r_unwt["weighting"] = "Unweighted"
        pairwise_rows.append(r_unwt)
        
    df_pw = pd.DataFrame(pairwise_rows)
    out_pw_csv = TABLES_DIR / "table04b_pairwise_geometry_robustness.csv"
    df_pw.to_csv(out_pw_csv, index=False)
    print(f"--> Saved Table 04b to {out_pw_csv}")
    
    return df_fe, df_pw

def run_analysis_a6(df_valid):
    """
    Analysis A6: Longitudinal Robustness: Course-Specific Balanced Panels vs. Repeated Cross-Sections.
    Examines whether secular trends from 2013-14 to 2023-24 hold when restricting to
    course-specific balanced panels of schools continuously reporting that course:
    - Geometry & Algebra I: 5 waves (2015-16 to 2023-24) due to 2013-14 grade span coverage.
    - Biology, Chemistry, Calculus, Algebra II, Physics, Advanced Math: 6 waves (2013-14 to 2023-24).
    """
    print("--> Running Analysis A6: Course-Specific Balanced Panel Robustness...")
    
    courses_config = [
        ("geom", "Geometry", ["2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 5),
        ("alg1", "Algebra I", ["2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 5),
        ("bio", "Biology", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
        ("chem", "Chemistry", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
        ("alg2", "Algebra II", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
        ("calc", "Calculus", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
        ("phys", "Physics", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
        ("advm", "Advanced Mathematics", ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"], 6),
    ]
    
    rows = []
    for ccode, cname, waves, n_req in courses_config:
        c_df = df_valid[df_valid["course_code"] == ccode]
        c_sub = c_df[c_df["crdc_wave"].isin(waves)]
        w_counts = c_sub.groupby("nces_school_id")["crdc_wave"].nunique()
        bal_sids = set(w_counts[w_counts == n_req].index)
        n_bal_schools = len(bal_sids)
        print(f"    {cname}: {n_bal_schools:,} continuously reporting schools across {n_req} waves.")
        
        bal_df = c_sub[c_sub["nces_school_id"].isin(bal_sids)]
        
        for w in waves:
            cr_w = c_sub[c_sub["crdc_wave"] == w]
            ba_w = bal_df[bal_df["crdc_wave"] == w]
            
            cell_cr = cr_w["mean_class_size"].mean() if not cr_w.empty else np.nan
            sec_cr = cr_w["num_enrolled"].sum() / cr_w["num_classes"].sum() if not cr_w.empty and cr_w["num_classes"].sum() > 0 else np.nan
            enr_cr = (cr_w["num_enrolled"] * cr_w["mean_class_size"]).sum() / cr_w["num_enrolled"].sum() if not cr_w.empty and cr_w["num_enrolled"].sum() > 0 else np.nan
            
            cell_ba = ba_w["mean_class_size"].mean() if not ba_w.empty else np.nan
            sec_ba = ba_w["num_enrolled"].sum() / ba_w["num_classes"].sum() if not ba_w.empty and ba_w["num_classes"].sum() > 0 else np.nan
            enr_ba = (ba_w["num_enrolled"] * ba_w["mean_class_size"]).sum() / ba_w["num_enrolled"].sum() if not ba_w.empty and ba_w["num_enrolled"].sum() > 0 else np.nan
            
            rows.append({
                "course_code": ccode,
                "course_name": cname,
                "balanced_school_n": n_bal_schools,
                "wave": w,
                "repeated_cross_cell_mean": cell_cr,
                "repeated_cross_sec_mean": sec_cr,
                "repeated_cross_enr_mean": enr_cr,
                "balanced_cell_mean": cell_ba,
                "balanced_sec_mean": sec_ba,
                "balanced_enr_mean": enr_ba,
                "diff_cell_bal_minus_cross": cell_ba - cell_cr,
                "diff_sec_bal_minus_cross": sec_ba - sec_cr,
                "diff_enr_bal_minus_cross": enr_ba - enr_cr,
            })
            
    df_rob = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table06_balanced_panel_robustness.csv"
    df_rob.to_csv(out_csv, index=False)
    print(f"--> Saved Table 06 to {out_csv}")
    return df_rob

def generate_analytical_figures(df_valid, df_res, df_wt, df_wedge):
    """Generate high-resolution analytical figures for the Study A artifact."""
    print("--> Generating Analytical Figures...")
    
    # -------------------------------------------------------------
    # Figure 1: Weighting Wedge Divergence across Courses (2023-24)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    df_23 = df_res[df_res["crdc_wave"] == "2023-24"].sort_values("seat_weighted_mean", ascending=True)
    
    y = np.arange(len(df_23))
    height = 0.28
    
    ax.barh(y - height, df_23["course_cell_mean"], height, label="Course-Cell Unweighted Mean", color="#4a7c59", alpha=0.85)
    ax.barh(y, df_23["section_weighted_mean"], height, label="Section-Weighted Mean", color="#33658a", alpha=0.85)
    ax.barh(y + height, df_23["seat_weighted_mean"], height, label="Enrollment-Weighted Mean (Lower-Bound Proxy)", color="#f26419", alpha=0.90)
    
    ax.set_yticks(y)
    ax.set_yticklabels(df_23["course_name"], fontweight="bold")
    ax.set_xlabel("Mean Students per Class")
    ax.set_title("Figure 1: The Weighting Wedge in U.S. Classrooms (CRDC 2023–24 Census)\n"
                 "Institutional Course Averages vs. Enrollment-Weighted Course-Cell Mean (Lower-Bound Proxy)", pad=15)
    ax.legend(loc="lower right", frameon=True)
    ax.set_xlim(0, 24)
    
    for i, (_, r) in enumerate(df_23.iterrows()):
        ax.text(r["seat_weighted_mean"] + 0.3, i + height, f"{r['seat_weighted_mean']:.1f}", va="center", fontsize=9, fontweight="bold", color="#d64900")
        ax.text(r["course_cell_mean"] - 1.2, i - height, f"{r['course_cell_mean']:.1f}", va="center", fontsize=9, color="white", fontweight="bold")
        
    plt.tight_layout()
    fig1_path = FIGURES_DIR / "fig01_weighting_wedge_divergence.png"
    plt.savefig(fig1_path)
    plt.close()
    print(f"    Saved {fig1_path}")
    
    # -------------------------------------------------------------
    # Figure 2: The Curriculum Hierarchy (Foundation Core vs. Advanced Electives)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    order = ["Algebra I", "Biology", "Geometry", "Algebra II", "Chemistry", "Advanced Mathematics", "Physics", "Calculus"]
    df_23_full = df_valid[(df_valid["crdc_wave"] == "2023-24") & (df_valid["course_name"].isin(order))]
    
    palette = {"Foundation Core": "#2a9d8f", "Advanced / Specialized": "#e76f51"}
    sns.boxplot(
        data=df_23_full,
        x="course_name",
        y="mean_class_size",
        order=order,
        hue="course_level",
        palette=palette,
        showmeans=True,
        meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "yellow", "markersize": 6},
        ax=ax,
        fliersize=1,
        boxprops=dict(alpha=0.8)
    )
    
    # Calculate and overlay actual enrollment-weighted means (Quantity C)
    enr_means = []
    for cname in order:
        cg = df_23_full[df_23_full["course_name"] == cname]
        em = (cg["num_enrolled"] * cg["mean_class_size"]).sum() / cg["num_enrolled"].sum() if cg["num_enrolled"].sum() > 0 else np.nan
        enr_means.append(em)
        
    ax.scatter(range(len(order)), enr_means, color="#d90429", s=70, marker="*", zorder=5, label="Enrollment-Weighted Mean (Lower-Bound Proxy)")
    
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=25, ha="right")
    ax.set_xlabel("Secondary Course Offering")
    ax.set_ylabel("School-Course Mean Class Size")
    ax.set_title("Figure 2: Distribution of School-Course Mean Class Sizes Across Subjects (CRDC 2023–24)\n"
                 "Yellow Diamonds = Course-Cell Mean (Unweighted); Red Stars = Enrollment-Weighted Mean; Solid Lines = Median", pad=15)
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles, labels=labels, title="Legend", loc="upper right")
    ax.set_ylim(0, 45)
    
    plt.tight_layout()
    fig2_path = FIGURES_DIR / "fig02_course_size_hierarchy.png"
    plt.savefig(fig2_path)
    plt.close()
    print(f"    Saved {fig2_path}")
    
    # -------------------------------------------------------------
    # Figure 3: Student Seat Exposure to Large Classrooms (>= 25, 30, 35)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    df_23_exp = df_res[df_res["crdc_wave"] == "2023-24"].sort_values("seat_pct_ge_25", ascending=False)
    
    x = np.arange(len(df_23_exp))
    width = 0.25
    
    ax.bar(x - width, df_23_exp["seat_pct_ge_25"], width, label="Enrollment in Cells ≥ 25", color="#e9c46a", alpha=0.9)
    ax.bar(x, df_23_exp["seat_pct_ge_30"], width, label="Enrollment in Cells ≥ 30", color="#f4a261", alpha=0.9)
    ax.bar(x + width, df_23_exp["seat_pct_ge_35"], width, label="Enrollment in Cells ≥ 35", color="#e76f51", alpha=0.9)
    
    ax.set_xticks(x)
    ax.set_xticklabels(df_23_exp["course_name"], rotation=30, ha="right", fontweight="bold")
    ax.set_ylabel("Share of Enrolled Students (%)")
    ax.set_title("Figure 3: Upper-Tail Classroom Concentration in U.S. Secondary Schools (CRDC 2023–24)\n"
                 "Share of Student Enrollment in School-Course Cells Averaging ≥ 25, ≥ 30, and ≥ 35", pad=15)
    ax.legend(loc="upper right", frameon=True)
    ax.set_ylim(0, 35)
    
    for i, (_, r) in enumerate(df_23_exp.iterrows()):
        ax.text(i - width, r["seat_pct_ge_25"] + 0.5, f"{r['seat_pct_ge_25']:.1f}%", ha="center", fontsize=8)
        ax.text(i, r["seat_pct_ge_30"] + 0.5, f"{r['seat_pct_ge_30']:.1f}%", ha="center", fontsize=8)
        
    plt.tight_layout()
    fig3_path = FIGURES_DIR / "fig03_upper_tail_seat_exposure.png"
    plt.savefig(fig3_path)
    plt.close()
    print(f"    Saved {fig3_path}")
    
    # -------------------------------------------------------------
    # Figure 4: The Staffing Allocation Wedge (Actual Class Size vs. PTR)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 7))
    kc_23 = df_valid[(df_valid["is_kc_metro"] == True) & (df_valid["crdc_wave"] == "2023-24") & pd.notnull(df_valid["school_ptr"])].copy()
    
    sns.scatterplot(
        data=kc_23,
        x="school_ptr",
        y="mean_class_size",
        hue="course_level",
        palette={"Foundation Core": "#264653", "Advanced / Specialized": "#e76f51"},
        alpha=0.7,
        s=40,
        ax=ax
    )
    
    # 45-degree line (Class Size = PTR)
    lims = [5, 35]
    ax.plot(lims, lims, "k--", alpha=0.6, label="Parity (Class Size = PTR)")
    
    # Schedule factor line (Class Size = 1.4 * PTR, representing 5/7 period day)
    ax.plot(lims, [1.4 * x for x in lims], "b-.", alpha=0.6, label="5/7 Schedule Line (Class Size = 1.4 × PTR)")
    
    ax.set_xlim(lims)
    ax.set_ylim(5, 45)
    ax.set_xlabel("Contemporaneous School Pupil-Teacher Ratio (PTR)")
    ax.set_ylabel("School-Course Mean Class Size")
    ax.set_title("Figure 4: Secondary Staffing Wedge in Greater Kansas City (2023–24)\n"
                 "Observed Course Class Sizes (1.20×–1.31×) vs. Theoretical 5/7 Schedule Line (1.40× PTR)", pad=15)
    ax.legend(loc="upper left")
    
    plt.tight_layout()
    fig4_path = FIGURES_DIR / "fig04_ptr_wedge_distribution.png"
    plt.savefig(fig4_path)
    plt.close()
    print(f"    Saved {fig4_path}")
    
    # -------------------------------------------------------------
    # Figure 5: Longitudinal Trajectory (2013-14 through 2023-24)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    trend_courses = ["Algebra I", "Geometry", "Biology", "Chemistry", "Calculus"]
    df_trend = df_res[df_res["course_name"].isin(trend_courses)].copy()
    
    wave_map = {
        "2013-14": 2014, "2015-16": 2016, "2017-18": 2018,
        "2020-21": 2021, "2021-22": 2022, "2023-24": 2024
    }
    df_trend["year_num"] = df_trend["crdc_wave"].map(wave_map)
    
    colors = {
        "Algebra I": "#1f77b4", "Geometry": "#ff7f0e", "Biology": "#2ca02c",
        "Chemistry": "#d62728", "Calculus": "#9467bd"
    }
    
    for cname in trend_courses:
        cg = df_trend[df_trend["course_name"] == cname].sort_values("year_num")
        if cname in ["Algebra I", "Geometry"]:
            cg_break = cg[cg["year_num"].isin([2014, 2016])]
            cg_primary = cg[cg["year_num"] >= 2016]
            ax.plot(cg_break["year_num"], cg_break["seat_weighted_mean"], linestyle="--", marker="o", color=colors[cname], alpha=0.5)
            ax.plot(cg_primary["year_num"], cg_primary["seat_weighted_mean"], linestyle="-", marker="o", linewidth=2.2, color=colors[cname], label=f"{cname} (Primary 9–12 Series)")
        else:
            ax.plot(cg["year_num"], cg["seat_weighted_mean"], marker="o", linewidth=2.2, color=colors[cname], label=f"{cname}")
        
    ax.axvspan(2020.5, 2021.5, color="gray", alpha=0.2, label="COVID-19 Discontinuity (Peak Remote/Hybrid)")
    ax.axvspan(2013.7, 2014.3, color="lightcoral", alpha=0.15, label="2013–14 Break (Alg1/Geom Covered Grades 7–12)")
    ax.set_xticks([2014, 2016, 2018, 2021, 2022, 2024])
    ax.set_xticklabels(["2013–14\n(Grades 7–12*)", "2015–16", "2017–18", "2020–21\n(COVID)", "2021–22", "2023–24"])
    ax.set_ylabel("Enrollment-Weighted Mean Class Size (Lower-Bound Proxy)")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_title("Figure 5: A Decade of Secondary Class Size in the United States (2013–14 to 2023–24)\n"
                 "Primary Comparable Series 2015–16 to 2023–24 (*2013–14 Alg1/Geom Spanned Grades 7–12)", pad=15)
    ax.legend(loc="lower left", frameon=True, fontsize=9)
    ax.set_ylim(16, 26)
    
    plt.tight_layout()
    fig5_path = FIGURES_DIR / "fig05_longitudinal_trajectory.png"
    plt.savefig(fig5_path)
    plt.close()
    print(f"    Saved {fig5_path}")

def main():
    print("=" * 70)
    print("EXECUTING STUDY A STATISTICAL & ECONOMETRIC ANALYSIS SUITE")
    print("=" * 70)
    
    _, df_valid = load_data()
    print(f"Loaded {len(df_valid):,} valid school-course observations across all waves.")
    
    df_res = run_analysis_a1_and_a2(df_valid)
    df_wt = run_analysis_a3(df_valid)
    df_wedge = run_analysis_a4(df_valid)
    df_fe, df_pw = run_analysis_a5(df_valid)
    df_rob = run_analysis_a6(df_valid)
    
    generate_analytical_figures(df_valid, df_res, df_wt, df_wedge)
    
    print("\nALL STUDY A ANALYSES & ARTIFACTS GENERATED SUCCESSFULLY.")

if __name__ == "__main__":
    main()
