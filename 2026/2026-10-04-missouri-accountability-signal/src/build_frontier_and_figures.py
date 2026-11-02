"""
src/build_frontier_and_figures.py

Generates the core empirical visualizations and analytical tables for
the Stage I synthesis "What Does a School Score Measure?":
1. Figure 05: The Accountability Design Frontier (Persistence vs. Poverty Association)
2. Figure 06: APR Growth Counterfactual Waterfall & Shapley Decomposition
3. Figure 07: Status x Growth Divergence (Extreme Quintiles Colored by Poverty)
4. Figure 08: Between vs. Within District Poverty Slopes (Robustness with Fixed Effects)
5. Figure 09: Prior-Status Prediction Staircase (Out-of-District CV R²)
6. Figure 10: Growth Contextual Correlations Audit (Horizontal Dot Plot)

Outputs saved to:
- artifacts/figures/
- artifacts/tables/
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"
APR_SUP_PATH = BASE_DIR / "data" / "raw" / "apr" / "mo_apr_supporting_2025_building.xlsx"
FIGURES_DIR = BASE_DIR / "artifacts" / "figures"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def build_frontier_and_figures():
    print("[*] Loading master panel for synthesis figures...")
    df = pd.read_parquet(PANEL_PATH)
    d25 = df[(df["school_year"] == 2025) & (df["sample_b_conventional"] == 1)].copy()

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"]

    # =========================================================================
    # 1. Figure 05: Accountability Design Frontier
    # =========================================================================
    print("[*] Generating Figure 05: Accountability Design Frontier...")
    piv_s = df[df["sample_b_conventional"] == 1].pivot(index=["district_code", "building_code"], columns="school_year", values="analyst_composite_status_mpi")
    piv_g = df[df["sample_b_conventional"] == 1].pivot(index=["district_code", "building_code"], columns="school_year", values="apr_growth_pts_pct")
    piv_a = df[df["sample_b_conventional"] == 1].pivot(index=["district_code", "building_code"], columns="school_year", values="apr_pct")
    piv_f = df[df["sample_b_conventional"] == 1].pivot(index=["district_code", "building_code"], columns="school_year", values="frpl_pct")

    common = pd.DataFrame({
        "s24": piv_s[2024], "s25": piv_s[2025],
        "g24": piv_g[2024], "g25": piv_g[2025],
        "a24": piv_a[2024], "a25": piv_a[2025],
        "f25": piv_f[2025]
    }).dropna()

    zs24 = (common["s24"] - common["s24"].mean()) / common["s24"].std()
    zs25 = (common["s25"] - common["s25"].mean()) / common["s25"].std()
    zg24 = (common["g24"] - common["g24"].mean()) / common["g24"].std()
    zg25 = (common["g25"] - common["g25"].mean()) / common["g25"].std()

    weights = np.linspace(0, 1, 41)
    frontier_pts = []
    for w in weights:
        sc24 = w * zs24 + (1 - w) * zg24
        sc25 = w * zs25 + (1 - w) * zg25
        r_pov = sc25.corr(common["f25"])
        pers = sc24.corr(sc25)
        frontier_pts.append({"w_status": w, "r_poverty": r_pov, "r2_poverty": r_pov**2, "persistence": pers})
    df_front = pd.DataFrame(frontier_pts)
    df_front.to_csv(TABLES_DIR / "table_accountability_frontier.csv", index=False)

    apr_r_pov = common["a25"].corr(common["f25"])
    apr_r2_pov = apr_r_pov**2
    apr_pers = common["a24"].corr(common["a25"])

    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=300)
    # Plot curve
    ax.plot(df_front["r2_poverty"] * 100, df_front["persistence"], color="#1f77b4", linewidth=2.8, label="Synthetic Status–Growth Blends: w·Status + (1-w)·Growth", zorder=2)
    
    # Marked weights
    for w_mark, lbl, pos in [
        (0.0, "Pure Growth (w=0.0)\nr²=0.0%, pers=0.358", (0.5, 0.38)),
        (0.25, "w=0.25", (4.2, 0.44)),
        (0.50, "w=0.50 (50/50 Blend)\nr²=17.7%, pers=0.632", (18.5, 0.65)),
        (0.75, "w=0.75", (35.0, 0.85)),
        (1.0, "Pure Status (w=1.0)\nr²=43.1%, pers=0.939", (38.0, 0.95))
    ]:
        row = df_front.iloc[(df_front["w_status"] - w_mark).abs().argmin()]
        ax.scatter(row["r2_poverty"] * 100, row["persistence"], color="#1f77b4", s=60, zorder=3)
        ax.annotate(lbl, (row["r2_poverty"] * 100, row["persistence"]), xytext=pos, fontsize=8.5,
                    fontweight="bold" if w_mark in [0.0, 0.5, 1.0] else "normal",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#f0f4f8", edgecolor="#b0c4de", alpha=0.9))

    # Official APR
    ax.scatter(apr_r2_pov * 100, apr_pers, color="#d62728", s=140, marker="*", edgecolor="#111111", linewidth=1.2, zorder=4, label=f"Official MSIP 6 APR Score (r²={apr_r2_pov*100:.1f}%, pers={apr_pers:.3f})")
    ax.annotate("Official APR Score\n(Resembles ~50/50 blend in r² and persistence)", (apr_r2_pov * 100, apr_pers),
                xytext=(apr_r2_pov * 100 - 15.5, apr_pers - 0.08), fontsize=9, fontweight="bold", color="#d62728",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff0f0", edgecolor="#d62728", alpha=0.9))

    ax.set_title("Single-Year Status–Growth Design Frontier: Persistence vs. Socioeconomic Association", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Socioeconomic Association with School Poverty (% Variance Explained, R²)", fontsize=11, labelpad=8)
    ax.set_ylabel("Year-to-Year Persistence Correlation (r 2024 → 2025)", fontsize=11, labelpad=8)
    ax.set_xlim(-2, 48)
    ax.set_ylim(0.25, 1.02)
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "05_accountability_frontier.png")
    plt.close(fig)

    # =========================================================================
    # 2. Figure 06: APR Counterfactual Waterfall & Shapley Decomposition
    # =========================================================================
    print("[*] Generating Figure 06: APR Growth Counterfactual Waterfall...")
    # Load supporting file to run exact counterfactuals
    df_sup = pd.read_excel(APR_SUP_PATH)
    df_sup["district_code"] = df_sup["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)
    df_sup["building_code"] = df_sup["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)
    m_cf = pd.merge(d25, df_sup, on=["district_code", "building_code"], how="inner")

    all_gro_e = ["ELA_ALL_GROWTH_POINTS_EARNED", "MATH_ALL_GROWTH_POINTS_EARNED", "SCIENCE_ALL_GROWTH_POINTS_EARNED", "SOC_STUD_ALL_GROWTH_POINTS_EARNED"]
    all_gro_p = ["ELA_ALL_GROWTH_POINTS_POSSIBLE", "MATH_ALL_GROWTH_POINTS_POSSIBLE", "SCIENCE_ALL_GROWTH_POINTS_POSSIBLE", "SOC_STUD_ALL_GROWTH_POINTS_POSSIBLE"]
    sg_gro_e = ["ELA_SG_GROWTH_POINTS_EARNED", "MATH_SG_GROWTH_POINTS_EARNED", "SCIENCE_SG_GROWTH_POINTS_EARNED", "SOC_STUD_SG_GROWTH_POINTS_EARNED"]
    sg_gro_p = ["ELA_SG_GROWTH_POINTS_POSSIBLE", "MATH_SG_GROWTH_POINTS_POSSIBLE", "SCIENCE_SG_GROWTH_POINTS_POSSIBLE", "SOC_STUD_SG_GROWTH_POINTS_POSSIBLE"]

    m_cf["gro_all_e"] = m_cf[all_gro_e].fillna(0).sum(axis=1)
    m_cf["gro_all_p"] = m_cf[all_gro_p].fillna(0).sum(axis=1)
    m_cf["gro_sg_e"] = m_cf[sg_gro_e].fillna(0).sum(axis=1)
    m_cf["gro_sg_p"] = m_cf[sg_gro_p].fillna(0).sum(axis=1)
    m_cf["gro_tot_e"] = m_cf["gro_all_e"] + m_cf["gro_sg_e"]
    m_cf["gro_tot_p"] = m_cf["gro_all_p"] + m_cf["gro_sg_p"]

    sub_cf = m_cf[(m_cf["gro_tot_p"] > 0) & (m_cf["apr_points_possible"] > m_cf["gro_tot_p"])].copy()

    r2_act = (sub_cf["frpl_pct"].corr((sub_cf["apr_points_earned"] / sub_cf["apr_points_possible"]) * 100))**2 * 100
    r2_no_sg = (sub_cf["frpl_pct"].corr(((sub_cf["apr_points_earned"] - sub_cf["gro_sg_e"]) / (sub_cf["apr_points_possible"] - sub_cf["gro_sg_p"])) * 100))**2 * 100
    r2_no_all = (sub_cf["frpl_pct"].corr(((sub_cf["apr_points_earned"] - sub_cf["gro_all_e"]) / (sub_cf["apr_points_possible"] - sub_cf["gro_all_p"])) * 100))**2 * 100
    r2_no_tot = (sub_cf["frpl_pct"].corr(((sub_cf["apr_points_earned"] - sub_cf["gro_tot_e"]) / (sub_cf["apr_points_possible"] - sub_cf["gro_tot_p"])) * 100))**2 * 100
    r2_raw_status = (d25["frpl_pct"].corr(d25["analyst_composite_status_mpi"]))**2 * 100

    # Shapley marginal contributions
    shapley_all = ((r2_no_all - r2_act) + (r2_no_tot - r2_no_sg)) / 2.0
    shapley_sg = ((r2_no_sg - r2_act) + (r2_no_tot - r2_no_all)) / 2.0
    total_attenuation = r2_no_tot - r2_act

    df_shapley = pd.DataFrame([
        {"growth_domain": "All-Student Growth Points", "marginal_contribution_pct_pts": shapley_all, "share_of_attenuation_pct": shapley_all / total_attenuation * 100},
        {"growth_domain": "Student-Group (Subgroup) Growth Points", "marginal_contribution_pct_pts": shapley_sg, "share_of_attenuation_pct": shapley_sg / total_attenuation * 100},
        {"growth_domain": "Total Value-Added Growth Domain", "marginal_contribution_pct_pts": total_attenuation, "share_of_attenuation_pct": 100.0}
    ])
    df_shapley.to_csv(TABLES_DIR / "table_growth_shapley_decomposition.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    cats = [
        "1. Actual APR %\n(Official Score)",
        "2. Remove Subgroup\nGrowth Only",
        "3. Remove All-Student\nGrowth Only",
        "4. Remove ALL Growth\n(All + Subgroup)",
        "Benchmark:\nRaw Status MPI"
    ]
    vals = [r2_act, r2_no_sg, r2_no_all, r2_no_tot, r2_raw_status]
    colors = ["#1f77b4", "#aec7e8", "#ffbb78", "#d62728", "#7f7f7f"]

    bars = ax.bar(cats, vals, color=colors, width=0.55, edgecolor="#111111", linewidth=1.0)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.0, f"{val:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.annotate(f"Shapley Attribution of +21.8% Attenuation:\n• All-Student Growth: +14.2 pts (65.1%)\n• Subgroup Growth: +7.6 pts (34.9%)\n(Decomposition of statistical association)",
                xy=(1.5, 34), xytext=(0.5, 35),
                fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff9e6", edgecolor="#e6c200", alpha=0.95))

    ax.set_title("How the Value-Added Growth Domain Reshapes APR Poverty Association", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Poverty Variance Explained (% R² with FRPL)", fontsize=11, labelpad=8)
    ax.set_ylim(0, 48)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "06_apr_counterfactual_waterfall.png")
    plt.close(fig)

    # =========================================================================
    # 3. Figure 07: Status x Growth Divergence (Extreme Quintiles)
    # =========================================================================
    print("[*] Generating Figure 07: Status x Growth Divergence Scatter...")
    d25_div = d25.dropna(subset=["analyst_composite_status_mpi", "apr_growth_pts_pct", "frpl_pct"]).copy()
    d25_div["status_q"] = pd.qcut(d25_div["analyst_composite_status_mpi"], 5, labels=[1, 2, 3, 4, 5])
    d25_div["growth_q"] = pd.qcut(d25_div["apr_growth_pts_pct"].rank(method="average"), 5, labels=[1, 2, 3, 4, 5])

    g_lh = d25_div[(d25_div["status_q"] == 1) & (d25_div["growth_q"] == 5)]
    g_hl = d25_div[(d25_div["status_q"] == 5) & (d25_div["growth_q"] == 1)]

    cols_prof = ["frpl_pct", "dese_urm_pct", "iep_pct", "ell_pct", "proportional_attendance_pct", "mobility_pct", "enrollment"]
    df_prof = pd.DataFrame({
        "Low Status / High Growth (Q1/Q5)": g_lh[cols_prof].mean(),
        "High Status / Low Growth (Q5/Q1)": g_hl[cols_prof].mean(),
        "All Conventional Schools": d25_div[cols_prof].mean()
    })
    df_prof.to_csv(TABLES_DIR / "table_divergent_schools_profile.csv")

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
    sc = ax.scatter(d25_div["analyst_composite_status_mpi"], d25_div["apr_growth_pts_pct"],
                    c=d25_div["frpl_pct"], cmap="viridis_r", alpha=0.45, s=22, edgecolors="none")
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Free & Reduced-Price Lunch Percentage (%)", fontsize=10, labelpad=8)

    # Highlight extreme divergent schools
    ax.scatter(g_lh["analyst_composite_status_mpi"], g_lh["apr_growth_pts_pct"],
               facecolors="none", edgecolors="#d62728", s=70, linewidth=1.5, label=f"Low Status / High Growth (Q1/Q5, n={len(g_lh)})")
    ax.scatter(g_hl["analyst_composite_status_mpi"], g_hl["apr_growth_pts_pct"],
               facecolors="none", edgecolors="#1f77b4", s=70, linewidth=1.5, label=f"High Status / Low Growth (Q5/Q1, n={len(g_hl)})")

    # Medians
    ax.axvline(d25_div["analyst_composite_status_mpi"].median(), color="#333333", linestyle="--", alpha=0.7, linewidth=1)
    ax.axhline(d25_div["apr_growth_pts_pct"].median(), color="#333333", linestyle="--", alpha=0.7, linewidth=1)

    ax.annotate(f"Low Status / High Growth (n={len(g_lh)}):\n• 92.0% FRPL | 74.2% URM\n• 58.2% Proportional Attendance\n• 30.7% Annual Mobility Rate\n• Top-quintile growth points",
                xy=(270, 85), xytext=(220, 80), fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff0f0", edgecolor="#d62728", alpha=0.9))

    ax.annotate(f"High Status / Low Growth (n={len(g_hl)}):\n• 28.7% FRPL | 11.8% URM\n• 87.3% Proportional Attendance\n• 12.5% Annual Mobility Rate\n• Bottom-quintile growth points",
                xy=(430, 20), xytext=(365, 12), fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f4f8", edgecolor="#1f77b4", alpha=0.9))

    ax.set_title("Missouri 2025 Conventional Schools: Status vs. Value-Added Growth Divergence", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Analyst Composite Status Index (Mean ELA & Math MPI)", fontsize=11, labelpad=8)
    ax.set_ylabel("APR Growth Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(-5, 105)
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "07_status_growth_divergence.png")
    plt.close(fig)

    # =========================================================================
    # 4. Figure 08: Between vs. Within District Poverty Slopes
    # =========================================================================
    print("[*] Generating Figure 08: Between vs. Within District Poverty Slopes...")
    dist_counts = d25["district_code"].value_counts()
    multi_dist = dist_counts[dist_counts > 1].index
    d25_multi = d25[d25["district_code"].isin(multi_dist)].dropna(subset=["analyst_composite_status_mpi", "frpl_pct", "district_code", "school_level"]).copy()

    # Decompositions
    dist_mean = d25_multi.groupby("district_code")["frpl_pct"].transform("mean")
    d25_multi["frpl_between"] = dist_mean
    d25_multi["frpl_within"] = d25_multi["frpl_pct"] - dist_mean

    m_tot = sm.OLS(d25_multi["analyst_composite_status_mpi"], sm.add_constant(d25_multi["frpl_pct"])).fit(cov_type="cluster", cov_kwds={"groups": d25_multi["district_code"]})
    m_bw = sm.OLS(d25_multi["analyst_composite_status_mpi"], sm.add_constant(d25_multi[["frpl_between", "frpl_within"]])).fit(cov_type="cluster", cov_kwds={"groups": d25_multi["district_code"]})
    d_dummies = pd.get_dummies(d25_multi["district_code"], drop_first=True, dtype=float)
    lvl_dummies = pd.get_dummies(d25_multi["school_level"], drop_first=True, dtype=float)
    X_fe_lvl = sm.add_constant(pd.concat([d25_multi[["frpl_pct"]], lvl_dummies, d_dummies], axis=1))
    m_fe_lvl = sm.OLS(d25_multi["analyst_composite_status_mpi"], X_fe_lvl).fit(cov_type="cluster", cov_kwds={"groups": d25_multi["district_code"]})

    df_slopes = pd.DataFrame([
        {"model": "1. Overall Bivariate Slope", "beta": m_tot.params["frpl_pct"], "se": m_tot.bse["frpl_pct"], "ci_low": m_tot.conf_int().loc["frpl_pct", 0], "ci_high": m_tot.conf_int().loc["frpl_pct", 1], "p_value": m_tot.pvalues["frpl_pct"]},
        {"model": "2. Between-District Slope (District Mean FRPL)", "beta": m_bw.params["frpl_between"], "se": m_bw.bse["frpl_between"], "ci_low": m_bw.conf_int().loc["frpl_between", 0], "ci_high": m_bw.conf_int().loc["frpl_between", 1], "p_value": m_bw.pvalues["frpl_between"]},
        {"model": "3. Within-District Slope (Unadjusted)", "beta": m_bw.params["frpl_within"], "se": m_bw.bse["frpl_within"], "ci_low": m_bw.conf_int().loc["frpl_within", 0], "ci_high": m_bw.conf_int().loc["frpl_within", 1], "p_value": m_bw.pvalues["frpl_within"]},
        {"model": "4. Within-District Slope (District FE + School Levels)", "beta": m_fe_lvl.params["frpl_pct"], "se": m_fe_lvl.bse["frpl_pct"], "ci_low": m_fe_lvl.conf_int().loc["frpl_pct", 0], "ci_high": m_fe_lvl.conf_int().loc["frpl_pct", 1], "p_value": m_fe_lvl.pvalues["frpl_pct"]},
    ])
    df_slopes.to_csv(TABLES_DIR / "table_between_within_fixed_effects.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    y_pos = np.arange(len(df_slopes))[::-1]
    xerr_low = df_slopes["beta"] - df_slopes["ci_low"]
    xerr_high = df_slopes["ci_high"] - df_slopes["beta"]
    ax.errorbar(df_slopes["beta"], y_pos, xerr=[xerr_low, xerr_high], fmt="o", color="#1f77b4", ecolor="#1f77b4", elinewidth=2.2, capsize=5, markersize=8)
    
    for idx, r in df_slopes.iterrows():
        y_p = y_pos[idx]
        ax.text(r["beta"], y_p + 0.18, f"β = {r['beta']:.3f} (Clustered SE: {r['se']:.3f})", ha="center", fontsize=9, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_slopes["model"], fontsize=9.5)
    ax.axvline(0, color="#333333", linestyle="--", linewidth=1.0)
    ax.set_title("The Poverty Gradient Does Not Disappear at the District Boundary", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Estimated Slope on Free & Reduced-Price Lunch % (Points MPI per 1% Poverty)", fontsize=10.5, labelpad=8)
    ax.set_xlim(-1.15, 0.05)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "08_between_within_district_slopes.png")
    plt.close(fig)

    # =========================================================================
    # 5. Figure 09: Prior-Status Prediction Staircase
    # =========================================================================
    print("[*] Generating Figure 09: Prior-Status Prediction Staircase...")
    df_cv_tab = pd.read_csv(TABLES_DIR / "table_starting_position_cv.csv")
    df_cv_full = df_cv_tab[df_cv_tab["sample_specification"].str.contains("Full Conventional")].copy()

    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=300)
    models_clean = ["1. School Level Only", "2. + Prior Achievement", "3. + School Poverty", "4. + Demographics & Attendance"]
    cv_r2_vals = [max(0.0, v * 100) for v in df_cv_full["cv_r2"]]
    colors_stair = ["#cccccc", "#1f77b4", "#2ca02c", "#d62728"]

    bars_stair = ax.bar(models_clean, cv_r2_vals, color=colors_stair, width=0.55, edgecolor="#111111", linewidth=1.0)
    for bar, val in zip(bars_stair, cv_r2_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.2, f"{val:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.annotate("Prior Achievement accounts for 88.0% of variance.\nPoverty adds +0.24%; All other demographics add +0.19%.",
                xy=(1.0, 88.0), xytext=(0.8, 50.0),
                fontsize=9.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#111111", lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", edgecolor="#1f77b4", alpha=0.95))

    ax.set_title("Out-of-District Predictive Power: Prior Status Overwhelmingly Predicts Contemporary Status", fontsize=11.5, fontweight="bold", pad=12)
    ax.set_ylabel("Out-of-District Cross-Validated R² (%)", fontsize=11, labelpad=8)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "09_prior_status_prediction_staircase.png")
    plt.close(fig)

    # =========================================================================
    # 6. Figure 10: Growth Contextual Correlations Audit
    # =========================================================================
    print("[*] Generating Figure 10: Growth Contextual Correlations Audit...")
    features_audit = [
        ("frpl_pct", "Free/Reduced Lunch Rate (FRPL %)"),
        ("iep_pct", "Special Education Incidence (IEP %)"),
        ("enrollment", "School K-12 Enrollment Headcount"),
        ("proportional_attendance_pct", "Proportional Attendance Rate (90/90 %)"),
        ("mobility_pct", "Student Mobility Rate (%)"),
        ("ell_pct", "English Language Learner Rate (ELL %)"),
        ("dese_urm_pct", "Underrepresented Minority (DESE URM %)"),
    ]
    corrs = []
    for col, lbl in features_audit:
        sub = d25.dropna(subset=["apr_growth_pts_pct", col])
        r, p = pearsonr(sub["apr_growth_pts_pct"], sub[col])
        n = len(sub)
        z = np.arctanh(r)
        se_z = 1.0 / np.sqrt(n - 3)
        ci_low = float(np.tanh(z - 1.95996 * se_z))
        ci_high = float(np.tanh(z + 1.95996 * se_z))
        corrs.append({"feature": lbl, "r": r, "fisher_z_se": se_z, "ci_low": ci_low, "ci_high": ci_high, "p_value": p, "n": n})
    df_audit = pd.DataFrame(corrs)
    df_audit.to_csv(TABLES_DIR / "table_growth_nonpoverty_audit.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=300)
    y_pos_aud = np.arange(len(df_audit))[::-1]
    ax.axvspan(-0.10, 0.10, color="#e6f2ff", alpha=0.6, label="Trivial Association Zone (|r| ≤ 0.10)")
    ax.axvline(0, color="#333333", linestyle="--", linewidth=1.0)
    
    xerr_aud_low = df_audit["r"] - df_audit["ci_low"]
    xerr_aud_high = df_audit["ci_high"] - df_audit["r"]
    ax.errorbar(df_audit["r"], y_pos_aud, xerr=[xerr_aud_low, xerr_aud_high], fmt="o", color="#d62728", ecolor="#d62728", elinewidth=2.0, capsize=4, markersize=7)

    for idx, r in df_audit.iterrows():
        y_p = y_pos_aud[idx]
        sign = "+" if r["r"] >= 0 else ""
        ax.text(r["r"] + (0.015 if r["r"] >= 0 else -0.015), y_p - 0.05, f"r = {sign}{r['r']:.3f}",
                ha="left" if r["r"] >= 0 else "right", va="center", fontsize=8.5, fontweight="bold")

    ax.set_yticks(y_pos_aud)
    ax.set_yticklabels(df_audit["feature"], fontsize=9.5)
    ax.set_title("Missouri Value-Added Growth Audit: Cross-Sectional Association with Student Circumstances", fontsize=11.5, fontweight="bold", pad=12)
    ax.set_xlabel("Pearson Correlation (r) with APR Growth Points Earned % (Fisher-z 95% CI)", fontsize=10.5, labelpad=8)
    ax.set_xlim(-0.15, 0.15)
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "10_growth_demographic_correlations.png")
    plt.close(fig)

    print(f"[SUCCESS] All 6 synthesis figures saved to {FIGURES_DIR}")
    print(f"[SUCCESS] All companion tables saved to {TABLES_DIR}")


if __name__ == "__main__":
    build_frontier_and_figures()
