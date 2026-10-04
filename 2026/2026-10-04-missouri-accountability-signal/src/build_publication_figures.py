"""
build_publication_figures.py
----------------------------
Generates publication-ready figures for external presentation and essays:
- Figure 11: 11_status_vs_poverty_clean.png
  Clean bivariate scatter of Status vs. Poverty with single statewide regression line,
  CEP callout arrow, and associational language.
- Figure 12: 12_status_poverty_by_school_level.png
  Calibrated horizontal bar chart showing R² of academic status with poverty across
  school levels (Elementary, Middle, High school, Mixed).
- Figure 12b: 12b_within_district_gradient.png
  Clean comparison of the poverty gradient overall, between districts, and within districts.
- Figure 13: 13_prior_status_vs_current_status_clean.png
  Scatterplot of 2024 Status vs. 2025 Status showing extreme longitudinal persistence (r=.938, R²=88%).
- Figure 13b: 13b_prediction_staircase_clean.png
  Minimal horizontal chart showing incremental predictive power of demographics once prior status is known.
- Figure 14: 14_growth_vs_poverty_clean.png
  Mirror of Figure 11 for Growth vs. Poverty, illustrating the near-zero relationship (r=.003).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PANEL_PATH = PROJECT_ROOT / "data" / "processed" / "mo_school_accountability_panel.parquet"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
FIGURES_DIR = PROJECT_ROOT / "artifacts" / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def setup_style():
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial", "sans-serif"]
    plt.rcParams["axes.edgecolor"] = "#cbd5e1"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#f1f5f9"
    plt.rcParams["grid.linewidth"] = 0.8


def build_figure_11(df25):
    """
    Figure 11: A clean, publication-grade scatterplot of Poverty vs. Status.
    """
    print("[*] Generating Figure 11: Clean Status vs. Poverty scatterplot...")
    sub = df25.dropna(subset=["frpl_pct", "analyst_composite_status_mpi"]).copy()
    n_schools = len(sub)

    r_val, _ = pearsonr(sub["frpl_pct"], sub["analyst_composite_status_mpi"])
    ols = sm.OLS(sub["analyst_composite_status_mpi"], sm.add_constant(sub["frpl_pct"])).fit()
    r2_pct = ols.rsquared * 100
    slope = ols.params.iloc[1]
    intercept = ols.params.iloc[0]

    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)

    # 1. Light points showing density
    ax.scatter(
        sub["frpl_pct"],
        sub["analyst_composite_status_mpi"],
        color="#2563eb",
        alpha=0.22,
        s=20,
        edgecolors="none",
        zorder=2,
    )

    # 2. Single statewide regression line
    x_line = np.linspace(sub["frpl_pct"].min(), sub["frpl_pct"].max(), 200)
    y_line = intercept + slope * x_line
    ax.plot(x_line, y_line, color="#dc2626", linewidth=2.4, zorder=3)

    # 3. Clean editorial callout box (associational framing)
    callout_text = (
        "FRPL is associated with 42% of the cross-school\n"
        "variation in academic status.\n\n"
        "r = −0.65   ·   N = 2,027 schools\n"
        "+10 pp poverty ≈ −8.2 MPI points"
    )
    ax.text(
        38,
        428,
        callout_text,
        fontsize=9.2,
        color="#0f172a",
        linespacing=1.35,
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.75",
            facecolor="#ffffff",
            edgecolor="#cbd5e1",
            linewidth=1.2,
            alpha=0.97,
        ),
        zorder=4,
    )

    # CEP Column Callout arrow pointing to the 100% vertical line
    ax.annotate(
        "Community Eligibility (CEP)\n100% free meals by policy (n=360)",
        xy=(100, 310),
        xytext=(68, 245),
        fontsize=8.5,
        color="#1e293b",
        linespacing=1.25,
        arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2, shrinkA=3, shrinkB=4),
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="#ffffff",
            edgecolor="#cbd5e1",
            linewidth=1.0,
            alpha=0.96,
        ),
        zorder=4,
    )

    # 4. Axes & Ticks
    ax.set_xlim(-2, 104)
    ax.set_ylim(205, 478)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    ax.set_xlabel("Students eligible for free or reduced-price lunch (%)", fontsize=10.5, color="#334155", labelpad=8)
    ax.set_ylabel("Analyst ELA–Math status composite (Mean MPI)", fontsize=10.5, color="#334155", labelpad=8)
    ax.tick_params(colors="#475569", labelsize=9.5)

    # Clean spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    # Titles
    plt.suptitle(
        "A school's poverty rate predicts a remarkable amount of its academic status",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.97,
        ha="left",
    )
    ax.set_title(
        "Analyst ELA–Math status composite vs. Free/Reduced-Price Lunch %, Missouri conventional public schools (2025)",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )

    # Simplified footnote
    fig.text(
        0.08,
        0.015,
        "Note: The vertical stripe at 100% reflects schools in the Community Eligibility Provision (CEP), where all students receive free meals\nby administrative policy rather than household income forms (mean Direct Certification = 45%).",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.15)
    out_path = FIGURES_DIR / "11_status_vs_poverty_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_12():
    """
    Figure 12: Calibrated horizontal bar chart of R² by school level.
    """
    print("[*] Generating Figure 12: Status Poverty R² by School Level (Calibrated)...")
    df_lvl = pd.read_csv(TABLES_DIR / "table_level_breakdown_2025.csv")
    status_lvl = df_lvl[df_lvl["outcome"].str.contains("Analyst Composite Status")].copy()

    level_order = ["ELEMENTARY", "MIDDLE", "HIGH", "MIXED"]
    level_names = {
        "ELEMENTARY": "Elementary",
        "MIDDLE": "Middle",
        "HIGH": "High school",
        "MIXED": "Mixed",
    }
    
    status_lvl["order"] = status_lvl["level"].map(lambda x: level_order.index(x) if x in level_order else 99)
    status_lvl = status_lvl.sort_values("order").reset_index(drop=True)
    status_lvl["label"] = status_lvl["level"].map(level_names)
    status_lvl["r2_pct"] = status_lvl["r2"] * 100

    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=300)

    # Reorder so Middle and Elementary are prominent
    # Order: Middle, Elementary, Mixed, High school (or Elementary, Middle, Mixed, High school)
    # Let's display: Middle, Elementary, Mixed, High school
    display_order = ["MIDDLE", "ELEMENTARY", "MIXED", "HIGH"]
    status_lvl["disp_order"] = status_lvl["level"].map(lambda x: display_order.index(x))
    status_lvl = status_lvl.sort_values("disp_order", ascending=False).reset_index(drop=True)

    y_pos = np.arange(len(status_lvl))
    colors = ["#1e3a8a" if lvl in ["MIDDLE", "ELEMENTARY"] else "#64748b" for lvl in status_lvl["level"]]

    bars = ax.barh(y_pos, status_lvl["r2_pct"], height=0.48, color=colors, edgecolor="none", zorder=3)

    for bar, (_, row) in zip(bars, status_lvl.iterrows()):
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(w + 1.2, y, f"{row['r2_pct']:.0f}%", va="center", ha="left", fontsize=9.8, fontweight="bold", color="#0f172a")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(status_lvl["label"], fontsize=10.5, color="#0f172a", fontweight="600")

    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.grid(axis="x", color="#e2e8f0", linestyle="-", linewidth=0.8, zorder=1)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "The poverty–status relationship is strongest in middle and elementary schools",
        fontsize=11.8,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.96,
        ha="left",
    )
    ax.set_xlabel("Share of cross-school variation in academic status associated with FRPL (R²)", fontsize=9.5, color="#334155", labelpad=8)

    fig.text(
        0.08,
        0.02,
        "Note: Based on 2025 MAP scores across 2,027 conventional public schools (1,043 elementary, 349 middle, 450 high school, 185 mixed).",
        fontsize=7.8,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.84, bottom=0.18, left=0.18, right=0.95)
    out_path = FIGURES_DIR / "12_status_poverty_by_school_level.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_12b():
    """
    Figure 12b: The poverty gradient remains inside school districts.
    A clean 3-row horizontal chart comparing overall, between-district, and within-district slopes.
    """
    print("[*] Generating Figure 12b: Within-District Poverty Gradient...")
    # Comparison data from table_between_within_fixed_effects.csv
    # All Missouri schools: -8.3 MPI
    # Between districts: -8.5 MPI
    # Within the same district, adjusting for school level: -7.4 MPI
    rows = [
        {"comparison": "All Missouri schools", "slope_10pp": -8.31, "label": "−8.3 MPI points", "color": "#2563eb"},
        {"comparison": "Between districts", "slope_10pp": -8.48, "label": "−8.5 MPI points", "color": "#0284c7"},
        {"comparison": "Within the same district\n(adjusting for school level)", "slope_10pp": -7.38, "label": "−7.4 MPI points", "color": "#0f172a"},
    ]
    df_p = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=300)

    # Invert order for display: All Missouri schools at top, Within at bottom
    df_p = df_p.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(df_p))

    # Plot bars
    bars = ax.barh(y_pos, np.abs(df_p["slope_10pp"]), height=0.45, color=df_p["color"], edgecolor="none", zorder=3)

    for bar, (_, row) in zip(bars, df_p.iterrows()):
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(w + 0.25, y, row["label"], va="center", ha="left", fontsize=10.0, fontweight="bold", color=row["color"])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_p["comparison"], fontsize=10.0, color="#0f172a", fontweight="600")

    ax.set_xlim(0, 11)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.grid(axis="x", color="#e2e8f0", linestyle="-", linewidth=0.8, zorder=1)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "The poverty gradient remains inside school districts",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.96,
        ha="left",
    )
    ax.set_title(
        "Estimated reduction in academic status for each +10 percentage point increase in FRPL (2025)",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )
    ax.set_xlabel("Academic status drop per +10 pp poverty (MPI points)", fontsize=9.5, color="#334155", labelpad=8)

    fig.text(
        0.08,
        0.02,
        "Note: Within-district estimate controls for district fixed effects and school grade levels, with standard errors clustered at the\ndistrict level (p < 0.0001). N = 2,027 conventional public schools across 551 districts.",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.84, bottom=0.20, left=0.28, right=0.95)
    out_path = FIGURES_DIR / "12b_within_district_gradient.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_13(df):
    """
    Figure 13: 2024 Status vs. 2025 Status (Extreme Longitudinal Persistence).
    """
    print("[*] Generating Figure 13: Prior Status vs. Current Status Scatterplot...")
    p24 = df[(df["school_year"] == 2024) & (df["sample_b_conventional"] == 1)][["district_code", "building_code", "analyst_composite_status_mpi"]]
    p25 = df[(df["school_year"] == 2025) & (df["sample_b_conventional"] == 1)][["district_code", "building_code", "analyst_composite_status_mpi"]]

    m = pd.merge(p24, p25, on=["district_code", "building_code"], suffixes=("_2024", "_2025")).dropna(
        subset=["analyst_composite_status_mpi_2024", "analyst_composite_status_mpi_2025"]
    )
    n_schools = len(m)

    r_val, _ = pearsonr(m["analyst_composite_status_mpi_2024"], m["analyst_composite_status_mpi_2025"])
    ols = sm.OLS(m["analyst_composite_status_mpi_2025"], sm.add_constant(m["analyst_composite_status_mpi_2024"])).fit()

    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)

    # 1. Light points showing density
    ax.scatter(
        m["analyst_composite_status_mpi_2024"],
        m["analyst_composite_status_mpi_2025"],
        color="#2563eb",
        alpha=0.22,
        s=20,
        edgecolors="none",
        zorder=2,
    )

    # 2. Faint 45-degree identity line (y = x)
    lim_min, lim_max = 210, 480
    ax.plot([lim_min, lim_max], [lim_min, lim_max], color="#94a3b8", linestyle="--", linewidth=1.4, label="Identity line (y = x)", zorder=3)

    # 3. Fitted regression line
    x_line = np.linspace(lim_min, lim_max, 200)
    y_line = ols.params.iloc[0] + ols.params.iloc[1] * x_line
    ax.plot(x_line, y_line, color="#dc2626", linewidth=2.2, label="Fitted linear trend", zorder=4)

    # 4. Editorial Callout Box
    callout_text = (
        "Last year's academic status accounts for 88% of\n"
        "the cross-school variation in this year's status.\n\n"
        f"r = .938   ·   N = {n_schools:,} schools"
    )
    ax.text(
        230,
        430,
        callout_text,
        fontsize=9.2,
        color="#0f172a",
        linespacing=1.35,
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.75",
            facecolor="#ffffff",
            edgecolor="#cbd5e1",
            linewidth=1.2,
            alpha=0.97,
        ),
        zorder=5,
    )

    ax.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=8.8)

    # Axes & Ticks
    ax.set_xlim(lim_min, lim_max)
    ax.set_ylim(lim_min, lim_max)
    ax.set_xlabel("2024 analyst ELA–Math status composite (Mean MPI)", fontsize=10.5, color="#334155", labelpad=8)
    ax.set_ylabel("2025 analyst ELA–Math status composite (Mean MPI)", fontsize=10.5, color="#334155", labelpad=8)
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "Academic status is remarkably persistent from one year to the next",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.97,
        ha="left",
    )
    ax.set_title(
        "Where a school starts overwhelmingly predicts where it will be a year later (2024 to 2025)",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )

    fig.text(
        0.08,
        0.015,
        "Note: A district-grouped out-of-sample model produces essentially the same result: CV-R² = 88.0%.\nEvaluated across 2,018 conventional public schools open and tested in both 2024 and 2025.",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.15)
    out_path = FIGURES_DIR / "13_prior_status_vs_current_status_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_13b():
    """
    Figure 13b: Simplified Prediction Staircase (Incremental Value of Demographics).
    """
    print("[*] Generating Figure 13b: Prediction Staircase...")
    rows = [
        {"model": "Prior status alone", "r2": 87.95, "delta": "", "color": "#1e3a8a"},
        {"model": "+ Poverty rate (FRPL)", "r2": 88.16, "delta": "+0.21%", "color": "#2563eb"},
        {"model": "+ Demographics & Attendance", "r2": 88.38, "delta": "+0.22%", "color": "#3b82f6"},
    ]
    df_p = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(df_p))

    fig, ax = plt.subplots(figsize=(8.8, 3.8), dpi=300)

    bars = ax.barh(y_pos, df_p["r2"], height=0.42, color=df_p["color"], edgecolor="none", zorder=3)

    for bar, (_, row) in zip(bars, df_p.iterrows()):
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        lbl = f"{row['r2']:.1f}%"
        if row["delta"]:
            lbl += f"  ({row['delta']})"
        ax.text(w + 0.8, y, lbl, va="center", ha="left", fontsize=9.5, fontweight="bold", color="#0f172a")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_p["model"], fontsize=10.0, color="#0f172a", fontweight="600")

    ax.set_xlim(80, 95)
    ax.set_xticks([80, 85, 90, 95])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.grid(axis="x", color="#e2e8f0", linestyle="-", linewidth=0.8, zorder=1)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "Once you know last year's status, today's demographics add very little predictive information",
        fontsize=11.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.96,
        ha="left",
    )
    ax.set_title(
        "Out-of-sample cross-validation predictive accuracy (CV-R²) for 2025 academic status",
        fontsize=9.0,
        color="#64748b",
        pad=10,
        loc="left",
    )
    ax.set_xlabel("District-Grouped Out-of-Sample Predictive Accuracy (CV-R²)", fontsize=9.2, color="#334155", labelpad=8)

    fig.text(
        0.08,
        0.02,
        "Note: 5-fold cross-validation with entire districts held out (N = 2,010 conventional schools).",
        fontsize=7.8,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.82, bottom=0.22, left=0.28, right=0.95)
    out_path = FIGURES_DIR / "13b_prediction_staircase_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_14(df25):
    """
    Figure 14: Poverty vs. Growth (Mirror of Figure 11).
    """
    print("[*] Generating Figure 14: Clean Growth vs. Poverty scatterplot...")
    sub = df25.dropna(subset=["frpl_pct", "apr_growth_pts_pct"]).copy()
    n_schools = len(sub)

    r_val, _ = pearsonr(sub["frpl_pct"], sub["apr_growth_pts_pct"])
    ols = sm.OLS(sub["apr_growth_pts_pct"], sm.add_constant(sub["frpl_pct"])).fit()
    slope = ols.params.iloc[1]
    intercept = ols.params.iloc[0]

    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)

    # 1. Light points showing density (using teal/green tone to distinguish from status blue)
    ax.scatter(
        sub["frpl_pct"],
        sub["apr_growth_pts_pct"],
        color="#0d9488",
        alpha=0.22,
        s=20,
        edgecolors="none",
        zorder=2,
    )

    # 2. Single statewide regression line (almost flat)
    x_line = np.linspace(sub["frpl_pct"].min(), sub["frpl_pct"].max(), 200)
    y_line = intercept + slope * x_line
    ax.plot(x_line, y_line, color="#dc2626", linewidth=2.4, zorder=3)

    # 3. Clean editorial callout box
    callout_text = (
        "Value-added growth points show near-zero\n"
        "association with school poverty.\n\n"
        "r = +0.003   ·   R² ≈ 0.0%   ·   N = 1,984 schools\n"
        "+10 pp poverty ≈ +0.02 growth points"
    )
    ax.text(
        38,
        22,
        callout_text,
        fontsize=9.2,
        color="#0f172a",
        linespacing=1.35,
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.75",
            facecolor="#ffffff",
            edgecolor="#cbd5e1",
            linewidth=1.2,
            alpha=0.97,
        ),
        zorder=4,
    )

    # Axes & Ticks (matching Figure 11 layout exactly)
    ax.set_xlim(-2, 104)
    ax.set_ylim(-5, 105)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    ax.set_xlabel("Students eligible for free or reduced-price lunch (%)", fontsize=10.5, color="#334155", labelpad=8)
    ax.set_ylabel("Official APR Growth Points earned (%)", fontsize=10.5, color="#334155", labelpad=8)
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "Unlike achievement status, Missouri's growth metric shows almost no link to poverty",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.97,
        ha="left",
    )
    ax.set_title(
        "Official Value-Added Growth Points earned vs. Free/Reduced-Price Lunch %, Missouri conventional schools (2025)",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )

    fig.text(
        0.08,
        0.015,
        "Note: Includes 1,984 conventional public schools with reported growth points. Missouri's growth model evaluates student\nscale-score gains relative to statewide academic peers, resulting in an accountability signal orthogonal to poverty.",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.15)
    out_path = FIGURES_DIR / "14_growth_vs_poverty_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def main():
    setup_style()
    print("[*] Loading master panel for publication figures...")
    df = pd.read_parquet(PANEL_PATH)
    df25 = df[(df["school_year"] == 2025) & (df["sample_b_conventional"] == 1)].copy()

    build_figure_11(df25)
    build_figure_12()
    build_figure_12b()
    build_figure_13(df)
    build_figure_13b()
    build_figure_14(df25)
    print("[SUCCESS] All publication graphics created successfully.")


if __name__ == "__main__":
    main()
