"""
src/generate_figures.py

Generates publication-quality figures for the Keyboarding & Digital Assessment
Mode Effects Observatory with audited source fidelity.

Figures:
1. Fig 1: The Infrastructure Paradox (HSTS Keyboarding Collapse vs. School Pulse 1:1 Access & ICILS)
2. Fig 2: Empirical Mode Penalties from Published Studies (Economics of Education Review, Ed Finance & Policy)
3. Fig 3: Keyboarding Delivery (EdWeek 74% vs 51% K-2) & NAEP Table 4.1c Item Differences (in Percentage Points)
4. Fig 4: Parameter Sensitivity Analysis: Exploring Hypothetical Transcription Thresholds and Score Gaps
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
FIG_DIR = PROJECT_ROOT / "artifacts" / "figures"


def setup_plotting_style():
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
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })


def generate_figure1():
    """Figure 1: The Infrastructure Paradox (Audited HSTS, School Pulse, and ICILS)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2.2, 1]})

    df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")
    df_kb = df_hsts[df_hsts["course_title"] == "Keyboarding"]
    df_ca = df_hsts[df_hsts["course_title"] == "Computer Applications"]

    # Plot HSTS verified trends
    ax1.plot(df_kb["year"], df_kb["pct_graduates"], marker="o", color="#b91c1c", linewidth=2.8, markersize=8, label="HS Graduates with Keyboarding Credit (HSTS Table 1)")
    ax1.plot(df_ca["year"], df_ca["pct_graduates"], marker="^", color="#4b5563", linewidth=2.0, linestyle=":", markersize=7, label="HS Graduates with Computer Applications (HSTS Table 1)")

    # Plot verified School Pulse Panel points (collection began in 2021)
    pulse_years = [2021, 2024]
    pulse_vals = [83.0, 88.0]
    ax1.scatter(pulse_years, pulse_vals, marker="s", color="#1d4ed8", s=130, zorder=5, label="NCES School Pulse: 1:1 Device Programs (2021-2025)")
    ax1.plot(pulse_years, pulse_vals, color="#1d4ed8", linewidth=2.5, linestyle="--")

    # Shaded band for state & NAEP digital testing transition (2015-2017)
    ax1.axvspan(2014.5, 2017.5, color="#e5e7eb", alpha=0.6, label="State & NAEP Digital Testing Transition (2015-17)")

    ax1.set_title("The Infrastructure Paradox: Keyboarding Collapse vs. 1:1 Device Programs", pad=12, fontweight="bold")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Percentage of Students / Schools (%)")
    ax1.set_ylim(-2, 102)
    ax1.set_xlim(1999, 2026)

    # Annotations
    ax1.annotate("44.1% (2000)", xy=(2000, 44.1), xytext=(2001, 52),
                 arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.2), fontweight="semibold", color="#b91c1c")
    ax1.annotate("2.5% (2019)\n[-94.3% collapse]", xy=(2019, 2.5), xytext=(2017.5, 12),
                 arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.2), fontweight="semibold", color="#b91c1c")
    ax1.annotate("88.0% (2024-25)\n[School Pulse Panel]", xy=(2024, 88.0), xytext=(2020, 92),
                 arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=1.2), fontweight="semibold", color="#1d4ed8")

    ax1.legend(loc="center left", frameon=True)

    # Right Plot: ICILS 8th Grade Digital Literacy Score
    df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
    icils_main = df_icils[df_icils["metric"] == "U.S. 8th Grade CIL Score"]

    bars = ax2.bar([str(y) for y in icils_main["year"]], icils_main["score"], color=["#3b82f6", "#ef4444"], width=0.5, edgecolor="black", linewidth=1.2)
    ax2.set_title("U.S. 8th-Grade Digital Literacy\n(IEA ICILS CIL Scale)", pad=12, fontweight="bold")
    ax2.set_ylabel("Average Scale Score (Mean 500, SD 100)")
    ax2.set_ylim(400, 560)

    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 5, f"{int(yval)}", ha="center", va="bottom", fontweight="bold", fontsize=11)

    ax2.annotate("-37 pts (-0.37 SD)\nStatistically Significant\n(p < 0.001)", xy=(0.5, 495), xytext=(0.5, 495),
                 ha="center", va="center", bbox=dict(boxstyle="round,pad=0.5", facecolor="#fee2e2", edgecolor="#b91c1c"),
                 color="#991b1b", fontweight="bold")

    plt.tight_layout()
    output_path = FIG_DIR / "fig1_three_divergent_trends.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 1 to {output_path.name}")


def generate_figure2():
    """Figure 2: Empirical Mode Penalties from Published Literature."""
    studies = [
        ("MA PARCC Y1 ELA (Backes & Cowan 2019, EER)", -0.25, "Standard Deviations", "#b91c1c", "Year 1 ELA penalty (-0.25 SD)"),
        ("MA PARCC Y1 Math (Backes & Cowan 2019, EER)", -0.10, "Standard Deviations", "#f97316", "Year 1 Math penalty (-0.10 SD)"),
        ("MA PARCC Y2 ELA (Backes & Cowan 2019, EER)", -0.13, "Standard Deviations", "#b91c1c", "Year 2 ELA persistence (-0.13 SD)"),
        ("MA PARCC Y2 Math (Backes & Cowan 2019, EER)", -0.05, "Standard Deviations", "#f97316", "Year 2 Math persistence (-0.05 SD)"),
        ("SC Rollout ELA/Math (Gordanier et al. 2023, EFP)", -0.08, "Standard Deviations", "#7c3aed", "Significant negative penalty; larger for poor students"),
        ("TN Keyboarding Writing (Parker 2018, JRBE)", 0.00, "Qualitative Null", "#64748b", "Non-significant (Chi-square test, p > 0.05)"),
    ]

    labels = [s[0] for s in studies][::-1]
    effects = [s[1] for s in studies][::-1]
    colors = [s[3] for s in studies][::-1]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    y_pos = np.arange(len(labels))

    bars = ax.barh(y_pos, effects, color=colors, height=0.55, edgecolor="black", linewidth=1.2)
    ax.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    for i, (bar, eff, s) in enumerate(zip(bars, effects, studies[::-1])):
        if s[2] == "Qualitative Null":
            ax.text(0.01, bar.get_y() + bar.get_height() / 2, "Null Association (p > 0.05, N=916/906)",
                    va="center", ha="left", fontsize=9.5, fontweight="bold", color="#475569")
        else:
            ax.text(eff - 0.015, bar.get_y() + bar.get_height() / 2, f"{eff:+.2f} SD",
                    va="center", ha="right", fontsize=9.5, fontweight="bold", color=s[3])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontweight="medium")
    ax.set_xlabel("Reported Standardized Mode Effect (Standard Deviations, SD)")
    ax.set_title("Empirical Standardized Mode Effect Estimates Across Benchmark Studies\n(Reconciled with Original Peer-Reviewed Publications)", pad=15, fontweight="bold")
    ax.set_xlim(-0.35, 0.15)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#b91c1c", markersize=10, label="ELA / Essay Dominant (Backes & Cowan 2019)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#f97316", markersize=10, label="Math / Numeric (Backes & Cowan 2019)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#7c3aed", markersize=10, label="South Carolina CBT Panel (Gordanier et al. 2023)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#64748b", markersize=10, label="Null Keyboarding Association (Parker 2018)")
    ]
    ax.legend(handles=legend_elements, loc="lower right", frameon=True)

    plt.tight_layout()
    output_path = FIG_DIR / "fig2_mode_penalty_by_subject_and_format.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 2 to {output_path.name}")


def generate_figure3():
    """Figure 3: Keyboarding Delivery (EdWeek 74% vs 51%) & NAEP Table 4.1c (Percentage Points)."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5))

    # Panel A: EdWeek 2024 Instruction Models
    df_deliv = pd.read_csv(RAW_DIR / "edweek_keyboarding_survey_2024.csv")
    colors_deliv = ["#1e40af", "#3b82f6", "#60a5fa", "#94a3b8"]
    wedges, texts, autotexts = ax1.pie(df_deliv["pct"], labels=df_deliv["mode"], autopct="%1.0f%%",
                                       colors=colors_deliv, startangle=140,
                                       textprops=dict(fontsize=9.5),
                                       wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for at in autotexts:
        at.set_color("white")
        at.set_weight("bold")
    ax1.set_title("A. How Keyboarding is Taught\n(EdWeek 2024 Survey, N=404)", pad=10, fontweight="bold")

    # Panel B: Audited EdWeek 2024 K-2 Keyboarding by Poverty (74% vs 51%)
    df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")
    df_k2 = df_equity[df_equity["grade_span"] == "Grades K-2"]
    bars2 = ax2.bar(df_k2["poverty_tier"], df_k2["pct_reporting_instruction"],
                    color=["#10b981", "#ef4444"], width=0.45, edgecolor="black", linewidth=1.2)
    ax2.set_title("B. Grades K–2 Keyboarding by Poverty\n(EdWeek 2024: 74% vs. 51%)", pad=10, fontweight="bold")
    ax2.set_ylabel("Reporting Keyboarding Instruction (%)")
    ax2.set_ylim(0, 95)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 2, f"{int(yval)}%", ha="center", va="bottom", fontweight="bold")
    ax2.annotate("1.45x Disparity Ratio\n(74% vs. 51%)", xy=(0.5, 62.5), xytext=(0.5, 78),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.2), ha="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#d97706"), fontweight="semibold")

    # Panel C: Verified NAEP 2017 Mode Evaluation (Table 4.1c: Reading in Percentage Points)
    df_41c = pd.read_csv(RAW_DIR / "naep_2017_mode_table41c.csv")
    x = np.arange(2)  # Grade 4, Grade 8
    width = 0.35

    sr_diffs = [
        df_41c[(df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0],
        df_41c[(df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    ]
    cr_diffs = [
        df_41c[(df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0],
        df_41c[(df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    ]

    rects1 = ax3.bar(x - width/2, sr_diffs, width, label="Selected Response (SR)", color="#059669", edgecolor="black")
    rects2 = ax3.bar(x + width/2, cr_diffs, width, label="Constructed Response (CR)", color="#7c3aed", edgecolor="black")

    ax3.set_title("C. 2017 NAEP Reading: Digital - Paper\n(Table 4.1c, Percentage Points)", pad=10, fontweight="bold")
    ax3.set_ylabel("Mean Item Score Difference (Percentage Points, pp)")
    ax3.set_xticks(x)
    ax3.set_xticklabels(["Grade 4", "Grade 8"], fontweight="semibold")
    ax3.set_ylim(-8.5, 1.0)
    ax3.axhline(0, color="black", linestyle="--", linewidth=0.8)

    for rect in rects1:
        h = rect.get_height()
        ax3.text(rect.get_x() + rect.get_width()/2, h - 0.6, f"{h:.1f} pp", ha="center", va="top", fontweight="bold", fontsize=9.5, color="#059669")
    for rect in rects2:
        h = rect.get_height()
        ax3.text(rect.get_x() + rect.get_width()/2, h - 0.6, f"{h:.1f} pp", ha="center", va="top", fontweight="bold", fontsize=9.5, color="#7c3aed")

    # Format gap annotation in Grade 4
    ax3.annotate("Format Gap: -3.0 pp\n(Both types negative)", xy=(0, -5.3), xytext=(0.4, -6.8),
                 arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.2),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#ede9fe", edgecolor="#7c3aed"),
                 fontweight="bold", fontsize=9, color="#5b21b6")

    ax3.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    output_path = FIG_DIR / "fig3_naep_grade4_cr_penalty_and_teacher_expectations.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 3 to {output_path.name}")


def generate_figure4():
    """Figure 4: Parameter Sensitivity Analysis (Hypothetical WPM Thresholds)."""
    df_grid = pd.read_parquet(DATA_DIR / "typing_threshold_sensitivity_grid.parquet")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Simulated Score Penalty across Thresholds and Slopes
    sns.lineplot(data=df_grid, x="threshold_wpm", y="g4_mean_simulated_penalty_sd",
                 hue="penalty_slope_sd_per_wpm", marker="o", linewidth=2.2, ax=ax1,
                 palette=["#2563eb", "#d97706", "#dc2626"])

    ax1.set_title("A. Sensitivity of Grade 4 Score Penalty to WPM Assumptions\n(Exploratory Parameter Sensitivity Analysis)", pad=12, fontweight="bold")
    ax1.set_xlabel("Hypothesized Transcription Automaticity Threshold (WPM)")
    ax1.set_ylabel("Simulated Mean Score Penalty (Standard Deviations, SD)")
    ax1.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax1.legend(title="Penalty Slope (SD / WPM deficit)", loc="lower left")

    ax1.annotate("Model Sensitivity:\nMean penalty varies from -0.04 to -0.38 SD\ndepending on assumed threshold and slope.",
                 xy=(25, -0.22), xytext=(16, -0.32),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef3c7", edgecolor="#d97706"),
                 fontweight="semibold", fontsize=9.5)

    # Panel B: Distribution Comparison under Baseline vs. Hypothesized Digital Constraint
    np.random.seed(42)
    n = 1000
    theta = np.random.normal(0, 1, n)
    wpm_g4 = np.clip(np.random.normal(14, 5, n), 4, 45)
    
    # Paper baseline (handwritten)
    score_paper = theta + np.random.normal(0, 0.3, n)
    # Digital under tau=20
    score_dig_tau20 = theta - 0.018 * np.maximum(0, 20 - wpm_g4) + np.random.normal(0, 0.3, n)
    # Digital under tau=25
    score_dig_tau25 = theta - 0.018 * np.maximum(0, 25 - wpm_g4) + np.random.normal(0, 0.3, n)

    sns.kdeplot(score_paper, label="Paper Assessment Baseline (Handwritten)", color="#059669", linewidth=2.5, ax=ax2)
    sns.kdeplot(score_dig_tau20, label="Digital Simulation (Tau = 20 WPM)", color="#d97706", linestyle="--", linewidth=2.2, ax=ax2)
    sns.kdeplot(score_dig_tau25, label="Digital Simulation (Tau = 25 WPM)", color="#dc2626", linewidth=2.2, ax=ax2)

    ax2.set_title("B. Grade 4 Distribution Shift Under Hypothesized Thresholds\n(Illustrative Simulation, Not Causal Proof)", pad=12, fontweight="bold")
    ax2.set_xlabel("Standardized Score Metric (SD)")
    ax2.set_ylabel("Density")
    ax2.legend(loc="upper left")

    # Disclaimer text box
    ax2.text(0.03, 0.05, "Note: Handwriting also imposes motor transcription burdens (fatigue/dysgraphia).\nDigital interfaces may benefit some students.",
             transform=ax2.transAxes, fontsize=8.5, fontstyle="italic",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8fafc", edgecolor="#cbd5e1"))

    plt.tight_layout()
    output_path = FIG_DIR / "fig4_psychometric_civ_simulation.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 4 to {output_path.name}")


def main():
    print("=" * 70)
    print("GENERATING AUDITED PUBLICATION FIGURES")
    print("=" * 70)
    setup_plotting_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_figure4()

    print("\nAll audited figures generated successfully.")


if __name__ == "__main__":
    main()
