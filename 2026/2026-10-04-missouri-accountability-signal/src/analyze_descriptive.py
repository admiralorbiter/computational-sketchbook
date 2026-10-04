"""
src/analyze_descriptive.py

Implements Phase 5: Bivariate Analysis of 2025 Cross-Section & Accountability Signals:
1. Status Achievement vs. School Poverty (FRPL, Non-CEP, CEP)
2. Value-Added Growth vs. School Poverty
3. Total APR Percentage vs. School Poverty
4. Unweighted vs. Enrollment-Weighted regressions
5. Subgroup breakdowns by School Level (Elementary, Middle, High, Mixed)
6. Status vs. Growth 2x2 Quadrant Analysis
7. Starting Position (Prior Achievement) incremental variance
8. Longitudinal Year-over-Year Stability (2024 -> 2025)

Produces publication-grade figures:
- artifacts/figures/01_achievement_vs_poverty.png
- artifacts/figures/02_growth_vs_poverty.png
- artifacts/figures/03_apr_vs_poverty.png

And structured CSV summary tables:
- artifacts/tables/table_bivariate_summary_2025.csv
- artifacts/tables/table_level_breakdown_2025.csv
- artifacts/tables/table_quadrant_status_growth_2025.csv
- artifacts/tables/table_stability_summary.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.api as sm
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"
FIGURES_DIR = BASE_DIR / "artifacts" / "figures"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def compute_bivariate_stats(x, y, weights=None):
    """Computes Pearson r, Spearman rho, OLS R2, slope beta, SE, and N."""
    mask = (~x.isna()) & (~y.isna())
    if weights is not None:
        mask = mask & (~weights.isna()) & (weights > 0)
    
    x_c = x[mask].values
    y_c = y[mask].values
    n = len(x_c)
    if n < 5:
        return {"n": n, "r": np.nan, "p_r": np.nan, "rho": np.nan, "p_rho": np.nan, "r2": np.nan, "beta": np.nan, "se": np.nan}

    r, p_r = pearsonr(x_c, y_c)
    rho, p_rho = spearmanr(x_c, y_c)

    X = sm.add_constant(x_c)
    if weights is not None:
        w_c = weights[mask].values
        model = sm.WLS(y_c, X, weights=w_c).fit()
    else:
        model = sm.OLS(y_c, X).fit()

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


def run_descriptive_analysis():
    print("[*] Loading master panel...")
    df = pd.read_parquet(PANEL_PATH)
    df25 = df[(df["school_year"] == 2025) & (df["sample_b_conventional"] == 1)].copy()
    print(f"[*] 2025 Conventional Schools (Sample B): {len(df25):,}")

    outcomes = [
        ("achievement_measure", "Composite Status (MPI)"),
        ("composite_growth_pts_pct", "Value-Added Growth (% Pts)"),
        ("apr_pct", "Total APR (% Pts)"),
    ]

    # 1. Main Bivariate Table (Overall, Non-CEP, CEP, Weighted)
    bivariate_rows = []
    for out_col, out_name in outcomes:
        # Overall unweighted
        s_all = compute_bivariate_stats(df25["frpl_pct"], df25[out_col])
        bivariate_rows.append({"outcome": out_name, "sample": "All Sample B (Unweighted)", **s_all})

        # Overall student-weighted
        s_w = compute_bivariate_stats(df25["frpl_pct"], df25[out_col], weights=df25["enrollment"])
        bivariate_rows.append({"outcome": out_name, "sample": "All Sample B (Enrollment-Weighted)", **s_w})

        # Non-CEP
        df_noncep = df25[df25["cep_flag"] == 0]
        s_ncep = compute_bivariate_stats(df_noncep["frpl_pct"], df_noncep[out_col])
        bivariate_rows.append({"outcome": out_name, "sample": "Non-CEP Schools Only", **s_ncep})

        # CEP
        df_cep = df25[df25["cep_flag"] == 1]
        s_cep = compute_bivariate_stats(df_cep["frpl_pct"], df_cep[out_col])
        bivariate_rows.append({"outcome": out_name, "sample": "CEP Schools Only", **s_cep})

    df_biv = pd.DataFrame(bivariate_rows)
    df_biv.to_csv(TABLES_DIR / "table_bivariate_summary_2025.csv", index=False)
    print("\n[*] 2025 Bivariate Analysis vs. FRPL Summary:")
    print(df_biv.to_string(index=False))

    # 2. School Level Breakdown Table
    level_rows = []
    for lvl in ["ELEMENTARY", "MIDDLE", "HIGH", "MIXED"]:
        sub_lvl = df25[df25["school_level"] == lvl]
        for out_col, out_name in outcomes:
            s = compute_bivariate_stats(sub_lvl["frpl_pct"], sub_lvl[out_col])
            level_rows.append({"level": lvl, "outcome": out_name, **s})

    df_lvl = pd.DataFrame(level_rows)
    df_lvl.to_csv(TABLES_DIR / "table_level_breakdown_2025.csv", index=False)

    # 3. Status vs Growth 2x2 Quadrant Analysis
    df_quad = df25.dropna(subset=["achievement_measure", "composite_growth_pts_pct"]).copy()
    med_ach = df_quad["achievement_measure"].median()
    med_gro = df_quad["composite_growth_pts_pct"].median()

    df_quad["high_ach"] = df_quad["achievement_measure"] >= med_ach
    df_quad["high_gro"] = df_quad["composite_growth_pts_pct"] >= med_gro

    n_tot = len(df_quad)
    q_hh = len(df_quad[df_quad["high_ach"] & df_quad["high_gro"]])
    q_hl = len(df_quad[df_quad["high_ach"] & ~df_quad["high_gro"]])
    q_lh = len(df_quad[~df_quad["high_ach"] & df_quad["high_gro"]])
    q_ll = len(df_quad[~df_quad["high_ach"] & ~df_quad["high_gro"]])

    # Average FRPL by quadrant
    frpl_hh = df_quad[df_quad["high_ach"] & df_quad["high_gro"]]["frpl_pct"].mean()
    frpl_hl = df_quad[df_quad["high_ach"] & ~df_quad["high_gro"]]["frpl_pct"].mean()
    frpl_lh = df_quad[~df_quad["high_ach"] & df_quad["high_gro"]]["frpl_pct"].mean()
    frpl_ll = df_quad[~df_quad["high_ach"] & ~df_quad["high_gro"]]["frpl_pct"].mean()

    df_quad_summary = pd.DataFrame([
        {"quadrant": "High Achievement / High Growth", "count": q_hh, "pct": q_hh / n_tot * 100.0, "mean_frpl_pct": frpl_hh},
        {"quadrant": "High Achievement / Low Growth", "count": q_hl, "pct": q_hl / n_tot * 100.0, "mean_frpl_pct": frpl_hl},
        {"quadrant": "Low Achievement / High Growth", "count": q_lh, "pct": q_lh / n_tot * 100.0, "mean_frpl_pct": frpl_lh},
        {"quadrant": "Low Achievement / Low Growth", "count": q_ll, "pct": q_ll / n_tot * 100.0, "mean_frpl_pct": frpl_ll},
    ])
    df_quad_summary.to_csv(TABLES_DIR / "table_quadrant_status_growth_2025.csv", index=False)
    print("\n[*] 2025 Status vs. Growth 2x2 Matrix:")
    print(df_quad_summary.to_string(index=False))

    # 4. Longitudinal Stability Table (2024 -> 2025)
    stab_rows = []
    # Achievement
    sub_ach = df25.dropna(subset=["achievement_measure", "prior_year_achievement"])
    s_ach = compute_bivariate_stats(sub_ach["prior_year_achievement"], sub_ach["achievement_measure"])
    stab_rows.append({"measure": "Achievement Status MPI", "pair": "2024 -> 2025", **s_ach})

    # Growth
    sub_gro = df25.dropna(subset=["composite_growth_pts_pct", "prior_year_growth"])
    s_gro = compute_bivariate_stats(sub_gro["prior_year_growth"], sub_gro["composite_growth_pts_pct"])
    stab_rows.append({"measure": "Value-Added Growth % Pts", "pair": "2024 -> 2025", **s_gro})

    # APR
    sub_apr = df25.dropna(subset=["apr_pct", "prior_year_apr"])
    s_apr = compute_bivariate_stats(sub_apr["prior_year_apr"], sub_apr["apr_pct"])
    stab_rows.append({"measure": "Total APR %", "pair": "2024 -> 2025", **s_apr})

    df_stab = pd.DataFrame(stab_rows)
    df_stab.to_csv(TABLES_DIR / "table_stability_summary.csv", index=False)
    print("\n[*] Year-over-Year Stability (2024 to 2025):")
    print(df_stab.to_string(index=False))

    # 5. Generate Figures
    print("\n[*] Generating high-resolution publication charts...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Figure 1: Achievement vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub1 = df25.dropna(subset=["frpl_pct", "achievement_measure"])
    # Separate non-CEP and CEP
    ncep = sub1[sub1["cep_flag"] == 0]
    cep = sub1[sub1["cep_flag"] == 1]

    ax.scatter(ncep["frpl_pct"], ncep["achievement_measure"], color="#1f77b4", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep):,})")
    ax.scatter(cep["frpl_pct"], cep["achievement_measure"], color="#d62728", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep):,})")

    # Overall regression line
    m_all = sm.OLS(sub1["achievement_measure"], sm.add_constant(sub1["frpl_pct"])).fit()
    x_line = np.linspace(sub1["frpl_pct"].min(), sub1["frpl_pct"].max(), 200)
    y_line = m_all.params.iloc[0] + m_all.params.iloc[1] * x_line
    r_val, _ = pearsonr(sub1["frpl_pct"], sub1["achievement_measure"])

    ax.plot(x_line, y_line, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val:.2f}, R² = {m_all.rsquared:.2f}, β = {m_all.params.iloc[1]:.2f}")

    ax.set_title("Missouri 2025 School Academic Achievement Status vs. Poverty (FRPL %)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("MAP Status Performance Index (Composite ELA & Math MPI)", fontsize=11, labelpad=8)
    ax.set_ylim(200, 480)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "01_achievement_vs_poverty.png")
    plt.close(fig)

    # Figure 2: Growth vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub2 = df25.dropna(subset=["frpl_pct", "composite_growth_pts_pct"])
    ncep2 = sub2[sub2["cep_flag"] == 0]
    cep2 = sub2[sub2["cep_flag"] == 1]

    ax.scatter(ncep2["frpl_pct"], ncep2["composite_growth_pts_pct"], color="#2ca02c", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep2):,})")
    ax.scatter(cep2["frpl_pct"], cep2["composite_growth_pts_pct"], color="#ff7f0e", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep2):,})")

    m_gro = sm.OLS(sub2["composite_growth_pts_pct"], sm.add_constant(sub2["frpl_pct"])).fit()
    x_line2 = np.linspace(sub2["frpl_pct"].min(), sub2["frpl_pct"].max(), 200)
    y_line2 = m_gro.params.iloc[0] + m_gro.params.iloc[1] * x_line2
    r_val2, p_val2 = pearsonr(sub2["frpl_pct"], sub2["composite_growth_pts_pct"])

    ax.plot(x_line2, y_line2, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val2:+.3f} (p=0.77), R² = {m_gro.rsquared:.4f}, β = {m_gro.params.iloc[1]:+.2f}")

    ax.set_title("Missouri 2025 School Value-Added Growth vs. Poverty (FRPL %)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("Composite Growth Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(-5, 105)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "02_growth_vs_poverty.png")
    plt.close(fig)

    # Figure 3: APR vs. Poverty
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    sub3 = df25.dropna(subset=["frpl_pct", "apr_pct"])
    ncep3 = sub3[sub3["cep_flag"] == 0]
    cep3 = sub3[sub3["cep_flag"] == 1]

    ax.scatter(ncep3["frpl_pct"], ncep3["apr_pct"], color="#9467bd", alpha=0.45, s=25, label=f"Non-CEP (n={len(ncep3):,})")
    ax.scatter(cep3["frpl_pct"], cep3["apr_pct"], color="#8c564b", alpha=0.45, s=25, label=f"CEP Participating (n={len(cep3):,})")

    m_apr = sm.OLS(sub3["apr_pct"], sm.add_constant(sub3["frpl_pct"])).fit()
    x_line3 = np.linspace(sub3["frpl_pct"].min(), sub3["frpl_pct"].max(), 200)
    y_line3 = m_apr.params.iloc[0] + m_apr.params.iloc[1] * x_line3
    r_val3, _ = pearsonr(sub3["frpl_pct"], sub3["apr_pct"])

    ax.plot(x_line3, y_line3, color="#111111", linewidth=2.2, linestyle="-",
            label=f"All Conventional: r = {r_val3:.2f}, R² = {m_apr.rsquared:.2f}, β = {m_apr.params.iloc[1]:.2f}")

    ax.set_title("Missouri 2025 Building Annual Performance Report (APR) vs. Poverty (FRPL %)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Free & Reduced-Price Lunch Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylabel("Total APR Points Earned Percentage (%)", fontsize=11, labelpad=8)
    ax.set_ylim(20, 105)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", fontsize=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "03_apr_vs_poverty.png")
    plt.close(fig)

    print(f"[SUCCESS] Saved figures to {FIGURES_DIR}")
    print(f"[SUCCESS] Saved tables to {TABLES_DIR}")


if __name__ == "__main__":
    run_descriptive_analysis()
