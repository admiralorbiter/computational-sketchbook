"""
build_publication_figures.py
----------------------------
Generates publication-ready figures for external presentation and essays:
- Figure 11: 11_status_vs_poverty_clean.png
  Clean, uncluttered bivariate scatter of Status vs. Poverty with single statewide
  regression line and editorial callout.
- Figure 12: 12_status_poverty_by_school_level.png
  Minimal horizontal bar chart showing R² of academic status with poverty across
  school levels (Elementary, Middle, High school, Mixed).
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
    slope_10pp = slope * 10

    fig, ax = plt.subplots(figsize=(8.5, 5.6), dpi=300)

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

    # 3. Clean editorial callout box in the open upper-right space (x=50 to 86)
    callout_text = (
        "Poverty explains 42% of the cross-school\n"
        "variation in academic status.\n\n"
        "r = −0.65   ·   N = 2,027 schools\n"
        "+10 pp poverty ≈ −8.2 MPI points"
    )
    ax.text(
        50,
        425,
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

    # 4. Axes & Ticks
    ax.set_xlim(-2, 102)
    ax.set_ylim(210, 475)
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

    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.12)
    out_path = FIGURES_DIR / "11_status_vs_poverty_clean.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[+] Saved {out_path}")


def build_figure_12():
    """
    Figure 12: A clean, minimal horizontal bar chart of R² by school level.
    """
    print("[*] Generating Figure 12: Status Poverty R² by School Level...")
    df_lvl = pd.read_csv(TABLES_DIR / "table_level_breakdown_2025.csv")
    status_lvl = df_lvl[df_lvl["outcome"].str.contains("Analyst Composite Status")].copy()

    # Desired order: Elementary, Middle, High school, Mixed
    level_order = ["ELEMENTARY", "MIDDLE", "HIGH", "MIXED"]
    level_names = {
        "ELEMENTARY": "Elementary",
        "MIDDLE": "Middle",
        "HIGH": "High school",
        "MIXED": "Mixed",
    }
    
    # Map into ordered dataframe
    status_lvl["order"] = status_lvl["level"].map(lambda x: level_order.index(x) if x in level_order else 99)
    status_lvl = status_lvl.sort_values("order").reset_index(drop=True)
    status_lvl["label"] = status_lvl["level"].map(level_names)
    status_lvl["r2_pct"] = status_lvl["r2"] * 100

    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=300)

    # Invert so Elementary is at the top
    y_pos = np.arange(len(status_lvl))[::-1]
    
    # Highlight Middle school slightly to let the 58% jump stand out
    colors = ["#1e40af" if lvl == "MIDDLE" else "#3b82f6" for lvl in status_lvl["level"]]

    bars = ax.barh(y_pos, status_lvl["r2_pct"], height=0.50, color=colors, edgecolor="none", zorder=3)

    # Bar labels
    for bar, (_, row) in zip(bars, status_lvl.iterrows()):
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(
            w + 1.2,
            y,
            f"{row['r2_pct']:.1f}%",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold" if row["level"] == "MIDDLE" else "normal",
            color="#0f172a",
        )

    # Y-axis
    ax.set_yticks(y_pos)
    ax.set_yticklabels(status_lvl["label"], fontsize=10.5, color="#1e293b", fontweight="500")

    # X-axis
    ax.set_xlim(0, 70)
    ax.set_xticks([0, 15, 30, 45, 60])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.tick_params(colors="#475569", labelsize=9.5)

    # Gridlines and spines
    ax.grid(axis="x", color="#e2e8f0", linestyle="-", linewidth=0.7, zorder=1)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")

    # Titles
    plt.suptitle(
        "Poverty and academic status by school level",
        fontsize=12.2,
        fontweight="bold",
        color="#0f172a",
        x=0.08,
        y=0.96,
        ha="left",
    )
    ax.set_title(
        "Share of cross-school variation in the analyst ELA–Math status composite associated with FRPL,\nMissouri conventional public schools, 2025.",
        fontsize=8.8,
        color="#64748b",
        pad=10,
        loc="left",
    )

    # Footnote note
    ax.text(
        0,
        -0.85,
        "Bivariate R²; descriptive association, not a causal estimate.",
        fontsize=8.2,
        color="#64748b",
        style="italic",
        ha="left",
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.81, bottom=0.18, left=0.16, right=0.92)
    out_path = FIGURES_DIR / "12_status_poverty_by_school_level.png"
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
    print("[SUCCESS] Publication graphics created successfully.")


if __name__ == "__main__":
    main()
