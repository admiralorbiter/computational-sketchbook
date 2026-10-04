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
- Figure 14: 14_how_missouri_growth_works.png
  Clean conceptual infographic explaining Missouri's value-added growth model (statewide model & student residual).
- Figure 15: 15_growth_vs_poverty_clean.png
  Exact visual mirror of Figure 11 for Growth vs. Poverty, illustrating the near-zero relationship (r=.003).
- Figure 16: 16_from_residual_to_growth_points.png
  Pipeline infographic showing the transformations from raw test scores to public growth points.
- Figure 17: 17_status_vs_growth_year_to_year.png
  Two-panel scatterplot comparing year-to-year stability: Status (r=.938) vs. Growth (r=.358).
- Figure 18: 18_beating_expectations_vs_catching_up.png
  Conceptual infographic on how growth measures beating expectations, not closing absolute gaps.
- Figure 19: 19_regression_to_the_mean.png
  Conceptual infographic illustrating how baseline test noise can masquerade as growth.
- Figure 20: 20_growth_uncertainty_by_school_size.png
  Statistical infographic comparing confidence intervals for small vs. large schools.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

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

    level_names = {
        "ELEMENTARY": "Elementary",
        "MIDDLE": "Middle",
        "HIGH": "High school",
        "MIXED": "Mixed",
    }
    
    display_order = ["MIDDLE", "ELEMENTARY", "MIXED", "HIGH"]
    status_lvl["disp_order"] = status_lvl["level"].map(lambda x: display_order.index(x) if x in display_order else 99)
    status_lvl = status_lvl.sort_values("disp_order", ascending=False).reset_index(drop=True)
    status_lvl["label"] = status_lvl["level"].map(level_names)
    status_lvl["r2_pct"] = status_lvl["r2"] * 100

    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=300)

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
    rows = [
        {"comparison": "All Missouri schools", "slope_10pp": -8.31, "label": "−8.3 MPI points", "color": "#2563eb"},
        {"comparison": "Between districts", "slope_10pp": -8.48, "label": "−8.5 MPI points", "color": "#0284c7"},
        {"comparison": "Within the same district\n(adjusting for school level)", "slope_10pp": -7.38, "label": "−7.4 MPI points", "color": "#0f172a"},
    ]
    df_p = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=300)

    df_p = df_p.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(df_p))

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


def build_figure_14_infographic():
    """
    Figure 14: Conceptual Infographic explaining Missouri's value-added growth model.
    Calibrated to statewide regression and student-level standardized residual terminology.
    """
    print("[*] Generating Figure 14: Value-Added Growth Conceptual Infographic...")
    fig, ax = plt.subplots(figsize=(9.4, 5.3), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(4, 93, "HOW MISSOURI MEASURES VALUE-ADDED GROWTH", fontsize=13, fontweight="bold", color="#0f172a")
    ax.text(4, 87, "Missouri does not simply measure score gains; it measures performance relative to a statistical prediction.", fontsize=9.2, color="#64748b")

    # 3 Horizontal Cards: Card 1 (x: 4 to 31), Card 2 (x: 37 to 64), Card 3 (x: 70 to 97)
    # Card 1: Prior Information (Inputs)
    c1 = patches.FancyBboxPatch((4, 40), 27, 42, boxstyle="round,pad=0.8", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.2)
    ax.add_patch(c1)
    ax.text(6, 77, "1. PRIOR INFORMATION", fontsize=9.5, fontweight="bold", color="#1e3a8a", va="center")
    ax.text(6, 71, "What the model considers:", fontsize=8.2, color="#475569", fontstyle="italic", va="top")
    inputs_desc = (
        "• Prior MAP test scores\n"
        "  (complete ELA & Math history)\n\n"
        "• Student mobility\n"
        "  (mid-year school moves)\n\n"
        "• School & LEA prior context"
    )
    ax.text(6, 64, inputs_desc, fontsize=8.0, color="#1e293b", linespacing=1.25, va="top")

    # Arrow 1 -> 2
    ax.annotate("", xy=(35.5, 61), xytext=(32.5, 61), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#64748b", lw=1.8))

    # Card 2: Statewide Prediction Model
    c2 = patches.FancyBboxPatch((37, 40), 27, 42, boxstyle="round,pad=0.8", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.2)
    ax.add_patch(c2)
    ax.text(39, 77, "2. STATEWIDE MODEL", fontsize=9.5, fontweight="bold", color="#0284c7", va="center")
    ax.text(39, 71, "Statistical prediction:", fontsize=8.2, color="#475569", fontstyle="italic", va="top")
    exp_desc = (
        "Statewide regression predicts\n"
        "standardized performance (z-score)\n"
        "from testing history & mobility:\n\n"
        "Predicted Score (ẑ):   0.00 SD\n"
        "(Statewide statistical benchmark)"
    )
    ax.text(39, 64, exp_desc, fontsize=8.0, color="#1e293b", linespacing=1.3, va="top")

    # Arrow 2 -> 3
    ax.annotate("", xy=(68.5, 61), xytext=(65.5, 61), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#64748b", lw=1.8))

    # Card 3: Student Residual
    c3 = patches.FancyBboxPatch((70, 40), 27, 42, boxstyle="round,pad=0.8", facecolor="#f0fdf4", edgecolor="#86efac", linewidth=1.2)
    ax.add_patch(c3)
    ax.text(72, 77, "3. STUDENT RESIDUAL", fontsize=9.5, fontweight="bold", color="#15803d", va="center")
    ax.text(72, 71, "Actual minus predicted:", fontsize=8.2, color="#475569", fontstyle="italic", va="top")
    res_desc = (
        "Actual Score (z):     +0.35 SD\n"
        "Predicted Score (ẑ):   0.00 SD\n"
        "Standardized Residual: +0.35 SD\n"
        "(e = z − ẑ, in SD units)"
    )
    ax.text(72, 64, res_desc, fontsize=8.0, color="#1e293b", linespacing=1.3, va="top")

    # Badge for Above Expectation
    badge = patches.FancyBboxPatch((72, 44), 23, 6, boxstyle="round,pad=0.4", facecolor="#16a34a", edgecolor="none")
    ax.add_patch(badge)
    ax.text(83.5, 47, "ABOVE EXPECTATION", fontsize=7.8, fontweight="bold", color="#ffffff", ha="center", va="center")

    # Bottom Banner / Key Takeaway
    banner = patches.FancyBboxPatch((4, 16), 93, 18, boxstyle="round,pad=0.8", facecolor="#eff6ff", edgecolor="#bfdbfe", linewidth=1.2)
    ax.add_patch(banner)
    ax.text(6, 28, "THE KEY TAKEAWAY", fontsize=8.5, fontweight="bold", color="#1e40af", va="center")
    takeaway_quote = (
        "“Growth is not simply ‘this year’s score minus last year’s score.’\n"
        "It measures performance relative to a statistical expectation.”"
    )
    ax.text(6, 23.5, takeaway_quote, fontsize=9.2, fontweight="600", color="#0f172a", linespacing=1.3, va="top")

    fig.text(
        0.04,
        0.035,
        "Note: Missouri standardizes MAP scores (z-scores) before estimation; residuals represent standard deviations from expectation, not raw MAP scale points.\nTo produce official school growth points, Missouri averages these standardized residuals, evaluates uncertainty, and maps to discrete accountability tiers.",
        fontsize=7.3,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.08)
    out_path = FIGURES_DIR / "14_how_missouri_growth_works.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_15(df25):
    """
    Figure 15: Clean Growth vs. Poverty scatterplot (Direct Mirror of Figure 11).
    """
    print("[*] Generating Figure 15: Clean Growth vs. Poverty scatterplot (Mirror of Figure 11)...")
    sub = df25.dropna(subset=["frpl_pct", "apr_growth_pts_pct"]).copy()
    n_schools = len(sub)

    r_val, _ = pearsonr(sub["frpl_pct"], sub["apr_growth_pts_pct"])
    ols = sm.OLS(sub["apr_growth_pts_pct"], sm.add_constant(sub["frpl_pct"])).fit()
    slope = ols.params.iloc[1]
    intercept = ols.params.iloc[0]

    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)

    # 1. Light points showing density
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

    # 3. Clean editorial callout box (matching Figure 11 positioning in open space)
    callout_text = (
        "Poverty is associated with essentially none of\n"
        "the cross-school variation in reported growth points.\n\n"
        f"r = +{r_val:.3f}   ·   N = {n_schools:,} schools"
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

    # CEP Column Callout arrow pointing to the 100% vertical line
    ax.annotate(
        "Community Eligibility (CEP)\n100% free meals by policy (n=360)",
        xy=(100, 62.5),
        xytext=(68, 80),
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

    # 4. Axes & Ticks (matching Figure 11 layout exactly)
    ax.set_xlim(-2, 104)
    ax.set_ylim(-5, 105)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    ax.set_xlabel("Students eligible for free or reduced-price lunch (%)", fontsize=10.5, color="#334155", labelpad=8)
    ax.set_ylabel("Official APR Value-Added Growth Points earned (%)", fontsize=10.5, color="#334155", labelpad=8)
    ax.tick_params(colors="#475569", labelsize=9.5)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "The poverty relationship almost disappears when Missouri measures growth",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.97,
        ha="left",
    )
    ax.set_title(
        "Official APR Value-Added Growth Points earned vs. Free/Reduced-Price Lunch %, Missouri conventional public schools (2025)",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )

    fig.text(
        0.08,
        0.015,
        "Note: The vertical stripe at 100% reflects schools in the Community Eligibility Provision (CEP). Missouri's growth model evaluates student\nscale-score gains relative to statistical expectations, resulting in an accountability measure that is nearly orthogonal to poverty.",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.15)
    out_path = FIGURES_DIR / "15_growth_vs_poverty_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_16_transformation_pipeline():
    """
    Figure 16: Pipeline showing how student test scores become public growth points.
    Explains the transformation from continuous standardized residual to discrete accountability grid.
    """
    print("[*] Generating Figure 16: Transformation Pipeline...")
    fig, ax = plt.subplots(figsize=(9.8, 5.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    plt.suptitle(
        "A growth score goes through several transformations before it reaches the public",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.04,
        y=0.96,
        ha="left",
    )
    ax.text(4, 91, "How student MAP test results become official MSIP 6 school growth accountability points", fontsize=9.2, color="#64748b")

    cards = [
        ("1. TEST SCORES", "#1e3a8a", "#f8fafc", "#cbd5e1",
         "Prior MAP scores\n(ELA & Math)\n\n+ Student mobility\n\n+ School prior context"),
        ("2. MODEL PREDICTION", "#0284c7", "#f8fafc", "#cbd5e1",
         "Statewide regression\npredicts standardized\ncurrent performance\nfor each student"),
        ("3. STUDENT RESIDUAL", "#0d9488", "#f0fdfa", "#99f6e4",
         "Standardized Residual:\n\ne = z − ẑ\n(Actual − Predicted)\n\nMeasured in standard\ndeviation (SD) units\n(not raw scale points)"),
        ("4. SCHOOL ESTIMATE", "#d97706", "#fffbeb", "#fde68a",
         "Average residuals\nacross all students\n\n+ Statistical certainty\n(N & score variance)"),
        ("5. PUBLIC POINTS", "#16a34a", "#f0fdf4", "#bbf7d0",
         "Subject Growth Tiers:\nFloor, Approaching,\nTarget, Exceeding\n(0%, 25%, 50%, 75%, 100%)\n\nCombined composite\nlands on 12.5% steps"),
    ]

    card_w = 16.8
    card_h = 44.0
    start_x = 3.5
    gap = 2.9
    y_card = 41.0

    for idx, (title, text_col, bg_col, edge_col, body) in enumerate(cards):
        x = start_x + idx * (card_w + gap)
        c = patches.FancyBboxPatch((x, y_card), card_w, card_h, boxstyle="round,pad=0.6", facecolor=bg_col, edgecolor=edge_col, linewidth=1.2)
        ax.add_patch(c)
        ax.text(x + 1.2, y_card + card_h - 4.5, title, fontsize=8.2, fontweight="bold", color=text_col, va="center")
        ax.text(x + 1.2, y_card + card_h - 9.0, body, fontsize=7.6, color="#1e293b", linespacing=1.25, va="top")

        # Arrow to next card
        if idx < len(cards) - 1:
            arrow_x = x + card_w + 0.4
            arrow_y = y_card + card_h / 2
            ax.annotate("", xy=(arrow_x + gap - 0.8, arrow_y), xytext=(arrow_x, arrow_y),
                        arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#64748b", lw=1.5))

    # Bottom Banner explaining the horizontal stripes
    banner = patches.FancyBboxPatch((3.5, 14.5), 93.0, 21.0, boxstyle="round,pad=0.8", facecolor="#eff6ff", edgecolor="#bfdbfe", linewidth=1.2)
    ax.add_patch(banner)
    ax.text(5.5, 31.0, "WHY THE PUBLIC GRAPH HAS HORIZONTAL STRIPES", fontsize=8.5, fontweight="bold", color="#1e40af", va="center")
    stripes_quote = (
        "“The public number is not a continuous learning gain. Missouri assigns subject growth into discrete 25-point tiers\n"
        "(0%, 25%, 50%, 75%, 100%). When ELA and Math are averaged across student groups (All Students & Subgroup),\n"
        "they combine into the 12.5-percentage-point increments (eighths) observed on the public scatterplot.”"
    )
    ax.text(5.5, 26.5, stripes_quote, fontsize=8.5, fontweight="600", color="#0f172a", linespacing=1.35, va="top")

    fig.text(
        0.04,
        0.035,
        "Note: Missouri DESE standardizes MAP scores (z-scores) before running hierarchical regressions. Building growth determinations evaluate the mean standardized residual,\nnumber of test pairs, and score variance against discrete subject targets (0, 25, 50, 75, 100%). Averaging ELA and Math produces the observed 12.5% increments.",
        fontsize=7.3,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.08)
    out_path = FIGURES_DIR / "16_from_residual_to_growth_points.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_17(df):
    """
    Figure 17: Two-panel scatterplot comparing year-to-year stability:
    Left: Status (r = .938)
    Right: Growth (r = .358)
    """
    print("[*] Generating Figure 17: Status vs. Growth Year-to-Year Persistence...")
    df_b = df[df["sample_b_conventional"] == 1].copy()
    piv_s = df_b.pivot(index=["district_code", "building_code"], columns="school_year", values="analyst_composite_status_mpi")
    piv_g = df_b.pivot(index=["district_code", "building_code"], columns="school_year", values="apr_growth_pts_pct")

    s24_25 = piv_s[[2024, 2025]].dropna()
    g24_25 = piv_g[[2024, 2025]].dropna()

    r_s, _ = pearsonr(s24_25[2024], s24_25[2025])
    r_g, _ = pearsonr(g24_25[2024], g24_25[2025])

    ols_s = sm.OLS(s24_25[2025], sm.add_constant(s24_25[2024])).fit()
    ols_g = sm.OLS(g24_25[2025], sm.add_constant(g24_25[2024])).fit()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.8), dpi=300)

    # Left Panel: Status Persistence
    ax1.scatter(s24_25[2024], s24_25[2025], color="#2563eb", alpha=0.22, s=20, edgecolors="none", zorder=2)
    s_min, s_max = 210, 480
    ax1.plot([s_min, s_max], [s_min, s_max], color="#94a3b8", linestyle="--", linewidth=1.4, label="Identity line (y = x)", zorder=3)
    x_s = np.linspace(s_min, s_max, 200)
    ax1.plot(x_s, ols_s.params.iloc[0] + ols_s.params.iloc[1] * x_s, color="#dc2626", linewidth=2.2, label="Fitted linear trend", zorder=4)

    callout_s = (
        "Status barely moves\n\n"
        f"r = .{int(round(r_s * 1000))}   ·   R² = {r_s**2*100:.1f}%\n"
        f"N = {len(s24_25):,} schools"
    )
    ax1.text(230, 435, callout_s, fontsize=9.2, color="#0f172a", linespacing=1.35, va="center",
             bbox=dict(boxstyle="round,pad=0.7", facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.2, alpha=0.97), zorder=5)

    ax1.set_xlim(s_min, s_max)
    ax1.set_ylim(s_min, s_max)
    ax1.set_xlabel("2024 analyst composite status MPI", fontsize=10.0, color="#334155", labelpad=8)
    ax1.set_ylabel("2025 analyst composite status MPI", fontsize=10.0, color="#334155", labelpad=8)
    ax1.set_title("Academic Achievement Status (MPI)", fontsize=11.0, fontweight="bold", color="#0f172a", pad=10)
    ax1.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=8.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#cbd5e1")
    ax1.spines["bottom"].set_color("#cbd5e1")

    # Right Panel: Growth Volatility
    ax2.scatter(g24_25[2024], g24_25[2025], color="#0d9488", alpha=0.22, s=20, edgecolors="none", zorder=2)
    g_min, g_max = -5, 105
    ax2.plot([0, 100], [0, 100], color="#94a3b8", linestyle="--", linewidth=1.4, label="Identity line (y = x)", zorder=3)
    x_g = np.linspace(0, 100, 200)
    ax2.plot(x_g, ols_g.params.iloc[0] + ols_g.params.iloc[1] * x_g, color="#dc2626", linewidth=2.2, label="Fitted linear trend", zorder=4)

    callout_g = (
        "Growth moves a lot\n\n"
        f"r = .{int(round(r_g * 1000))}   ·   R² = {r_g**2*100:.1f}%\n"
        f"N = {len(g24_25):,} schools"
    )
    ax2.text(8, 85, callout_g, fontsize=9.2, color="#0f172a", linespacing=1.35, va="center",
             bbox=dict(boxstyle="round,pad=0.7", facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.2, alpha=0.97), zorder=5)

    ax2.set_xlim(g_min, g_max)
    ax2.set_ylim(g_min, g_max)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.set_xlabel("2024 APR growth points earned (%)", fontsize=10.0, color="#334155", labelpad=8)
    ax2.set_ylabel("2025 APR growth points earned (%)", fontsize=10.0, color="#334155", labelpad=8)
    ax2.set_title("Official APR Growth Points (%)", fontsize=11.0, fontweight="bold", color="#0f172a", pad=10)
    ax2.legend(loc="lower right", frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#cbd5e1")
    ax2.spines["bottom"].set_color("#cbd5e1")

    plt.suptitle(
        "Status barely moves. Growth moves a lot.",
        fontsize=13.0,
        fontweight="bold",
        color="#0f172a",
        x=0.06,
        y=0.97,
        ha="left",
    )

    fig.text(
        0.06,
        0.02,
        "Note: Status is highly persistent from one year to the next (r = .938), while reported growth points fluctuate substantially (r = .358).\nThe discrete grid on the right reflects Missouri's point-assignment scoring tiers across 1,971 conventional schools.",
        fontsize=8.0,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.15, wspace=0.22)
    out_path = FIGURES_DIR / "17_status_vs_growth_year_to_year.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_18_beating_expectations():
    """
    Figure 18: Beating Expectations vs. Catching Up.
    Two schools with identical +5 residuals that remain 110 points apart.
    """
    print("[*] Generating Figure 18: Beating Expectations vs. Catching Up...")
    fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    plt.suptitle(
        "Growth measures beating expectations, not catching up",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.04,
        y=0.96,
        ha="left",
    )
    ax.text(4, 91, "Two schools can receive identical positive growth ratings while remaining 110 points apart in achievement", fontsize=9.2, color="#64748b")

    # Card A: Affluent Suburban School
    cA = patches.FancyBboxPatch((4, 45), 44, 40, boxstyle="round,pad=0.8", facecolor="#f8fafc", edgecolor="#93c5fd", linewidth=1.4)
    ax.add_patch(cA)
    ax.text(6, 80, "AFFLUENT SUBURBAN SCHOOL", fontsize=9.2, fontweight="bold", color="#1e40af", va="center")
    ax.text(6, 74, "High starting achievement (Low Poverty)", fontsize=8.0, color="#64748b", fontstyle="italic", va="top")
    desc_A = (
        "• Expected MAP Score:     440\n"
        "• Actual MAP Score:           445\n\n"
        "• Value-Added Residual:   +5 points"
    )
    ax.text(6, 67, desc_A, fontsize=8.2, color="#1e293b", linespacing=1.25, va="top")
    badge_A = patches.FancyBboxPatch((6, 48), 24, 6, boxstyle="round,pad=0.4", facecolor="#16a34a", edgecolor="none")
    ax.add_patch(badge_A)
    ax.text(18, 51, "ABOVE EXPECTATIONS (+5)", fontsize=7.5, fontweight="bold", color="#ffffff", ha="center", va="center")

    # Card B: High-Poverty School
    cB = patches.FancyBboxPatch((52, 45), 44, 40, boxstyle="round,pad=0.8", facecolor="#f8fafc", edgecolor="#fdba74", linewidth=1.4)
    ax.add_patch(cB)
    ax.text(54, 80, "HIGH-POVERTY URBAN/RURAL SCHOOL", fontsize=9.2, fontweight="bold", color="#c2410c", va="center")
    ax.text(54, 74, "Low starting achievement (High Poverty)", fontsize=8.0, color="#64748b", fontstyle="italic", va="top")
    desc_B = (
        "• Expected MAP Score:     330\n"
        "• Actual MAP Score:           335\n\n"
        "• Value-Added Residual:   +5 points"
    )
    ax.text(54, 67, desc_B, fontsize=8.2, color="#1e293b", linespacing=1.25, va="top")
    badge_B = patches.FancyBboxPatch((54, 48), 24, 6, boxstyle="round,pad=0.4", facecolor="#16a34a", edgecolor="none")
    ax.add_patch(badge_B)
    ax.text(66, 51, "ABOVE EXPECTATIONS (+5)", fontsize=7.5, fontweight="bold", color="#ffffff", ha="center", va="center")

    # Bottom Takeaway Box
    banner = patches.FancyBboxPatch((4, 12), 92.0, 27, boxstyle="round,pad=0.8", facecolor="#eff6ff", edgecolor="#bfdbfe", linewidth=1.2)
    ax.add_patch(banner)
    ax.text(6, 33.5, "THE ACCOUNTABILITY TENSION", fontsize=8.5, fontweight="bold", color="#1e40af", va="center")
    quote_t = (
        "Both schools receive the exact same positive growth credit (+5 residual).\n"
        "Yet the 110-point achievement gap between their students remains completely unchanged.\n\n"
        "Growth doesn't ask whether poor and affluent students end up in the same place.\n"
        "It asks whether each performed better or worse than predicted given their starting position."
    )
    ax.text(6, 29.5, quote_t, fontsize=8.5, color="#0f172a", linespacing=1.35, va="top")

    fig.text(
        0.04,
        0.04,
        "Note: Value-added models condition on prior achievement, which removes the correlation with poverty by establishing separate statistical\nexpectations for students based on their starting points.",
        fontsize=7.5,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.08)
    out_path = FIGURES_DIR / "18_beating_expectations_vs_catching_up.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_19_regression_to_mean():
    """
    Figure 19: When test noise can look like growth (Regression to the mean).
    """
    print("[*] Generating Figure 19: Regression to the Mean...")
    fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    plt.suptitle(
        "When test noise can look like growth",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.04,
        y=0.96,
        ha="left",
    )
    ax.text(4, 91, "How random test-day noise and regression to the mean can simulate academic progress", fontsize=9.2, color="#64748b")

    # 3-step timeline: True Ability -> Year 1 Bad Day -> Year 2 Normal Day
    c1 = patches.FancyBboxPatch((4, 45), 28, 40, boxstyle="round,pad=0.8", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.2)
    ax.add_patch(c1)
    ax.text(6, 80, "TRUE KNOWLEDGE", fontsize=9.0, fontweight="bold", color="#1e3a8a", va="center")
    ax.text(6, 73, "Constant true ability:\n\nStudent's underlying\ntrue mastery is 380\nin both years.", fontsize=8.2, color="#1e293b", linespacing=1.3, va="top")

    ax.annotate("", xy=(34.5, 65), xytext=(32.5, 65), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#64748b", lw=1.6))

    c2 = patches.FancyBboxPatch((36, 45), 28, 40, boxstyle="round,pad=0.8", facecolor="#fef2f2", edgecolor="#fecaca", linewidth=1.2)
    ax.add_patch(c2)
    ax.text(38, 80, "YEAR 1: BAD TEST DAY", fontsize=9.0, fontweight="bold", color="#b91c1c", va="center")
    ax.text(38, 73, "Unlucky test day (−20 pts):\n\nObserved score: 360\n\nModel predicts low score\nfor Year 2: 365", fontsize=8.2, color="#1e293b", linespacing=1.3, va="top")

    ax.annotate("", xy=(66.5, 65), xytext=(64.5, 65), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#64748b", lw=1.6))

    c3 = patches.FancyBboxPatch((68, 45), 28, 40, boxstyle="round,pad=0.8", facecolor="#f0fdf4", edgecolor="#bbf7d0", linewidth=1.2)
    ax.add_patch(c3)
    ax.text(70, 80, "YEAR 2: NORMAL DAY", fontsize=9.0, fontweight="bold", color="#15803d", va="center")
    ax.text(70, 73, "Normal test day (380):\n\nActual: 380\nPredicted: 365\n\nResidual: +15 points\n(Apparent 'Growth')", fontsize=8.2, color="#1e293b", linespacing=1.3, va="top")

    # Bottom Takeaway Box
    banner = patches.FancyBboxPatch((4, 15), 92.0, 24, boxstyle="round,pad=0.8", facecolor="#eff6ff", edgecolor="#bfdbfe", linewidth=1.2)
    ax.add_patch(banner)
    ax.text(6, 33, "THE STATISTICAL MECHANISM", fontsize=8.5, fontweight="bold", color="#1e40af", va="center")
    quote_r = (
        "Prior test scores are noisy measurements of true student ability.\n"
        "An unlucky test score in Year 1 artificially depresses the statistical prediction for Year 2.\n"
        "When the student merely has an ordinary test day the following year, the model interprets the rebound as positive growth.\n"
        "Conversely, good luck on baseline tests can make normal follow-up performance look like negative growth."
    )
    ax.text(6, 29, quote_r, fontsize=8.5, color="#0f172a", linespacing=1.35, va="top")

    fig.text(
        0.04,
        0.04,
        "Note: Missouri's model incorporates multiple prior scores to mitigate noise, but ordinary least squares regressions remain vulnerable\nto errors-in-variables bias when baseline measures contain random test-day variation.",
        fontsize=7.5,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.08)
    out_path = FIGURES_DIR / "19_regression_to_the_mean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_20_uncertainty():
    """
    Figure 20: Same estimated growth, different statistical certainty.
    Comparing confidence intervals for small (n=30) vs. large (n=300) schools.
    """
    print("[*] Generating Figure 20: Growth Uncertainty by School Size...")
    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=300)

    y_pos = [1, 0]
    labels = ["Small School (n = 30 tested)", "Large School (n = 300 tested)"]
    pe = [0.15, 0.15]
    ci_low = [-0.08, 0.08]
    ci_high = [0.38, 0.22]
    colors = ["#d97706", "#2563eb"]

    for i in range(2):
        ax.plot([ci_low[i], ci_high[i]], [y_pos[i], y_pos[i]], color=colors[i], linewidth=2.4, zorder=3)
        ax.scatter([pe[i]], [y_pos[i]], color=colors[i], s=70, zorder=4)
        ax.plot([ci_low[i], ci_low[i]], [y_pos[i] - 0.08, y_pos[i] + 0.08], color=colors[i], linewidth=2.0, zorder=3)
        ax.plot([ci_high[i], ci_high[i]], [y_pos[i] - 0.08, y_pos[i] + 0.08], color=colors[i], linewidth=2.0, zorder=3)

    # Annotations
    ax.text(0.15, 1.22, "Point Estimate: +0.15\nWide confidence interval overlaps zero (Not statistically distinguishable)", fontsize=8.6, color="#b45309", ha="center")
    ax.text(0.15, 0.22, "Point Estimate: +0.15\nTight confidence interval strictly above zero (Statistically significant)", fontsize=8.6, color="#1e40af", ha="center")

    # Reference line at zero
    ax.axvline(0, color="#94a3b8", linestyle="--", linewidth=1.2, zorder=1)
    ax.text(0.005, -0.42, "State Average Growth (0.0)", fontsize=8.2, color="#64748b", fontstyle="italic")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10.0, fontweight="600", color="#0f172a")
    ax.set_xlim(-0.20, 0.50)
    ax.set_ylim(-0.55, 1.55)
    ax.set_xlabel("Estimated Average Student Growth Residual (Standard Deviations)", fontsize=9.5, color="#334155", labelpad=8)
    ax.tick_params(colors="#475569", labelsize=9.2)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.grid(axis="x", color="#e2e8f0", linestyle="-", linewidth=0.8, zorder=1)
    ax.grid(axis="y", visible=False)

    plt.suptitle(
        "Same estimated growth, different statistical certainty",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.96,
        ha="left",
    )
    ax.set_title(
        "How tested student count affects confidence intervals around building-level growth estimates",
        fontsize=9.2,
        color="#64748b",
        pad=10,
        loc="left",
    )

    fig.text(
        0.08,
        0.02,
        "Note: Missouri DESE's accountability guide explicitly notes that growth designations depend on the mean residual, score pair count, and variance.\nSmaller schools face substantially wider uncertainty, affecting whether their progress crosses accountability thresholds.",
        fontsize=7.8,
        color="#64748b",
        style="italic",
        linespacing=1.25,
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.84, bottom=0.20, left=0.28, right=0.95)
    out_path = FIGURES_DIR / "20_growth_uncertainty_by_school_size.png"
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
    build_figure_14_infographic()
    build_figure_15(df25)
    build_figure_16_transformation_pipeline()
    build_figure_17(df)
    build_figure_18_beating_expectations()
    build_figure_19_regression_to_mean()
    build_figure_20_uncertainty()
    print("[SUCCESS] All publication graphics created successfully.")


if __name__ == "__main__":
    main()
