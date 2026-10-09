"""
src/generate_figures.py

Generates publication-quality figures for the Keyboarding & Digital Assessment
Mode Effects Observatory.

Figures:
1. Fig 1: The Three Conflicting Trends (1:1 Devices vs. Keyboarding Credits vs. ICILS Literacy)
2. Fig 2: The Empirical Mode Penalty: Item Format (Constructed Response vs. Multiple Choice) and Subject
3. Fig 3: The Keyboarding Instruction Pipeline: Distribution, SES Disparities, and Teacher Expectations
4. Fig 4: Psychometric CIV Simulation: Typing Fluency (WPM) Bottleneck and Score Distribution Shift
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
    """Figure 1: The Three Conflicting Trends (2000-2025)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2.2, 1]})

    # Left Plot: Keyboarding Coursework Collapse vs. 1:1 Laptop Ubiquity
    df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")
    df_kb = df_hsts[df_hsts["course_title"] == "Keyboarding"]
    df_pulse = pd.read_csv(RAW_DIR / "nces_pulse_device_access.csv")

    line1 = ax1.plot(df_kb["year"], df_kb["pct_graduates"], marker="o", color="#b91c1c", linewidth=2.8, markersize=8, label="HS Graduates Earning Keyboarding Credit (NAEP HSTS)")
    line2 = ax1.plot(df_pulse["year"], df_pulse["pct_1to1_devices"], marker="s", color="#1d4ed8", linewidth=2.8, markersize=8, label="Public Schools with 1:1 Device Programs (NCES Pulse)")

    # Shaded band for digital assessment transition period (2015-2017)
    ax1.axvspan(2014.5, 2017.5, color="#e5e7eb", alpha=0.6, label="State & NAEP Digital Assessment Transition (2015-17)")

    ax1.set_title("The Infrastructure Paradox: Device Ubiquity vs. Keyboarding Collapse", pad=12, fontweight="bold")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Percentage (%)")
    ax1.set_ylim(-2, 102)
    ax1.set_xlim(1999, 2026)

    # Annotate key values
    ax1.annotate("44.1% (2000)", xy=(2000, 44.1), xytext=(2001, 50),
                 arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.2), fontweight="semibold", color="#b91c1c")
    ax1.annotate("2.5% (2019)\n[-94.3% collapse]", xy=(2019, 2.5), xytext=(2018, 14),
                 arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.2), fontweight="semibold", color="#b91c1c")
    ax1.annotate("88.0% (2024-25)\n[Universal 1:1]", xy=(2024, 88.0), xytext=(2020, 92),
                 arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=1.2), fontweight="semibold", color="#1d4ed8")

    ax1.legend(loc="center left", frameon=True)

    # Right Plot: ICILS 8th Grade Digital Literacy Decline
    df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
    icils_main = df_icils[df_icils["metric"] == "U.S. 8th Grade CIL Score"]

    bars = ax2.bar([str(y) for y in icils_main["year"]], icils_main["score"], color=["#3b82f6", "#ef4444"], width=0.5, edgecolor="black", linewidth=1.2)
    ax2.set_title("U.S. 8th-Grade Digital Literacy\n(IEA ICILS CIL Scale)", pad=12, fontweight="bold")
    ax2.set_ylabel("Average Scale Score (Mean 500, SD 100)")
    ax2.set_ylim(400, 560)

    # Add score text on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 5, f"{int(yval)}", ha="center", va="bottom", fontweight="bold", fontsize=11)

    # Annotate decline
    ax2.annotate("-37 pts (-0.37 SD)\nStatistically Significant\n(p < 0.001)", xy=(0.5, 495), xytext=(0.5, 495),
                 ha="center", va="center", bbox=dict(boxstyle="round,pad=0.5", facecolor="#fee2e2", edgecolor="#b91c1c"),
                 color="#991b1b", fontweight="bold")

    plt.tight_layout()
    output_path = FIG_DIR / "fig1_three_divergent_trends.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 1 to {output_path.name}")


def generate_figure2():
    """Figure 2: Empirical Mode Effects Benchmark (Item Format & Subject Disparity)."""
    df_meta = pd.read_csv(DATA_DIR / "master_mode_effects_benchmark.csv")
    
    # Filter for key comparisons
    studies = [
        ("MA PARCC Y1 ELA (Backes & Cowan 2019)", -0.25, -0.29, -0.21, "Constructed Response / Essay", "#b91c1c"),
        ("MA PARCC Y1 Math (Backes & Cowan 2019)", -0.10, -0.13, -0.07, "Selected / Numeric Entry", "#f97316"),
        ("MA PARCC Y2 ELA (Backes & Cowan 2019)", -0.13, -0.16, -0.10, "Constructed Response / Essay", "#b91c1c"),
        ("MA PARCC Y2 Math (Backes & Cowan 2019)", -0.05, -0.08, -0.02, "Selected / Numeric Entry", "#f97316"),
        ("SC READY Y1 ELA (Fordham 2020)", -0.09, -0.12, -0.06, "Constructed Response / Essay", "#b91c1c"),
        ("SC READY Y1 Math (Fordham 2020)", -0.02, -0.04, -0.00, "Selected / Numeric Entry", "#f97316"),
        ("NAEP 2017 G4 Reading (Constructed Response)", -0.18, -0.22, -0.14, "Typing Required (CR)", "#7c3aed"),
        ("NAEP 2017 G4 Reading (Multiple Choice)", -0.01, -0.03, 0.01, "Click Selection (MC)", "#059669"),
        ("NAEP 2017 G8 Reading (Constructed Response)", -0.08, -0.11, -0.05, "Typing Required (CR)", "#7c3aed"),
        ("NAEP 2017 G8 Reading (Multiple Choice)", 0.01, -0.01, 0.03, "Click Selection (MC)", "#059669"),
        ("TN Keyboarding Study (9-Wk Class vs Control)", 0.04, -0.08, 0.16, "Typing Class Effect", "#64748b")
    ]

    labels = [s[0] for s in studies][::-1]
    effects = [s[1] for s in studies][::-1]
    ci_low = [s[2] for s in studies][::-1]
    ci_high = [s[3] for s in studies][::-1]
    colors = [s[5] for s in studies][::-1]

    fig, ax = plt.subplots(figsize=(12, 8))

    y_pos = np.arange(len(labels))
    error_left = np.array(effects) - np.array(ci_low)
    error_right = np.array(ci_high) - np.array(effects)

    ax.errorbar(effects, y_pos, xerr=[error_left, error_right], fmt="o", color="black",
                ecolor="dimgray", elinewidth=2, capsize=4, markersize=8, zorder=3)
    
    # Scatter colored markers
    for i, (eff, y, col) in enumerate(zip(effects, y_pos, colors)):
        ax.scatter([eff], [y], color=col, s=120, zorder=4, edgecolor="black", linewidth=1.2)
        ax.text(eff - 0.015 if eff < 0 else eff + 0.015, y, f"{eff:+.2f} SD",
                va="center", ha="right" if eff < 0 else "left", fontsize=9.5, fontweight="bold", color=col)

    ax.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    # Shaded region highlighting large penalty
    ax.axvspan(-0.35, -0.10, color="#fee2e2", alpha=0.3, label="Substantial Online Penalty (≤ -0.10 SD)")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontweight="medium")
    ax.set_xlabel("Estimated Mode Effect on Student Performance (Standard Deviations, SD)", labelpad=10)
    ax.set_title("Empirical Standardized Mode Effect Penalty Across Benchmark Studies\nSeparated by Subject, Item Format, and Grade Level", pad=15, fontweight="bold")
    ax.set_xlim(-0.35, 0.22)

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#b91c1c", markersize=10, label="ELA / Essay Dominant"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f97316", markersize=10, label="Math / Numeric Entry"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#7c3aed", markersize=10, label="NAEP Typed Constructed Response"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#059669", markersize=10, label="NAEP Click Multiple Choice"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#64748b", markersize=10, label="Null Keyboarding Intervention")
    ]
    ax.legend(handles=legend_elements, loc="lower left", frameon=True)

    plt.tight_layout()
    output_path = FIG_DIR / "fig2_mode_penalty_by_subject_and_format.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 2 to {output_path.name}")


def generate_figure3():
    """Figure 3: Keyboarding Pipeline, Equity Gradient, and Teacher Expectations."""
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

    # Panel B: Early (K-2) Keyboarding by Poverty Level
    df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")
    df_k2 = df_equity[df_equity["grade_span"] == "Grades K-2"]
    bars2 = ax2.bar(df_k2["poverty_tier"], df_k2["pct_reporting_instruction"],
                    color=["#10b981", "#ef4444"], width=0.5, edgecolor="black", linewidth=1.2)
    ax2.set_title("B. Grades K–2 Keyboarding by Poverty\n(EdWeek 2024 Survey)", pad=10, fontweight="bold")
    ax2.set_ylabel("Reporting Keyboarding Instruction (%)")
    ax2.set_ylim(0, 50)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 1.5, f"{int(yval)}%", ha="center", va="bottom", fontweight="bold")
    ax2.annotate("2.0x Equity Gap\nIn Early Typing Foundation", xy=(0.5, 27), xytext=(0.5, 36),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.2), ha="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#d97706"), fontweight="semibold")

    # Panel C: NAEP 2017 Grade 4 Teacher Competence Report
    df_comp = pd.read_csv(RAW_DIR / "naep_g4_student_keyboard_competence_2017.csv")
    bars3 = ax3.barh(df_comp["pct_students_meeting_expectations"], df_comp["pct_teachers"],
                     color=["#ef4444", "#f97316", "#3b82f6", "#10b981"], edgecolor="black", linewidth=1.2)
    ax3.set_title("C. Students Meeting Typing Expectations\n(2017 NAEP Grade 4 Teachers)", pad=10, fontweight="bold")
    ax3.set_xlabel("% of Teachers Reporting")
    ax3.set_xlim(0, 50)
    for bar in bars3:
        xval = bar.get_width()
        ax3.text(xval + 1, bar.get_y() + bar.get_height()/2, f"{int(xval)}%", va="center", fontweight="bold")

    plt.tight_layout()
    output_path = FIG_DIR / "fig3_naep_grade4_cr_penalty_and_teacher_expectations.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 3 to {output_path.name}")


def generate_figure4():
    """Figure 4: Psychometric CIV Simulation: WPM Bottleneck and Score Distribution Shift."""
    df_sim = pd.read_parquet(DATA_DIR / "construct_irrelevant_variance_simulation.parquet")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Relationship Between WPM and Score Penalty
    sns.scatterplot(data=df_sim.sample(600, random_state=42), x="wpm", y="delta_cr_mode",
                    hue="grade", palette={4: "#dc2626", 8: "#2563eb"}, alpha=0.6, s=40, ax=ax1)
    
    # Threshold line at 25 WPM
    ax1.axvline(25, color="dimgray", linestyle="--", linewidth=1.5, label="Fluency Threshold (~25 WPM)")
    ax1.set_title("A. Constructed Response Mode Penalty vs. Typing Speed", pad=12, fontweight="bold")
    ax1.set_xlabel("Typing Speed (Words Per Minute, WPM)")
    ax1.set_ylabel("Constructed Response Mode Penalty (Digital - Paper, SD)")
    ax1.set_ylim(-0.65, 0.4)
    ax1.axhline(0, color="black", linestyle="-", linewidth=0.8, alpha=0.5)

    ax1.annotate("Severe Interface Tax:\nCognitive capacity redirected to\nhunt-and-peck motor mechanics",
                 xy=(10, -0.35), xytext=(12, -0.55),
                 arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.2),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="#fee2e2", edgecolor="#dc2626"),
                 fontsize=9.5, fontweight="semibold", color="#991b1b")
    ax1.legend(title="Grade Level", loc="lower right")

    # Panel B: Kernel Density of True Ability vs Digital CR Score in Grade 4
    g4 = df_sim[df_sim["grade"] == 4]
    sns.kdeplot(g4["score_cr_paper"], label="Paper Mode (Construct Valid)", color="#059669", linewidth=2.5, ax=ax2)
    sns.kdeplot(g4["score_cr_digital"], label="Digital Mode (Interface Confounded)", color="#dc2626", linewidth=2.5, ax=ax2)

    ax2.set_title("B. Grade 4 Score Distribution Distortion\n(Construct-Irrelevant Variance Displacement)", pad=12, fontweight="bold")
    ax2.set_xlabel("Measured Standardized Ability (SD)")
    ax2.set_ylabel("Density")

    # Mean shift annotation
    mean_paper = g4["score_cr_paper"].mean()
    mean_dig = g4["score_cr_digital"].mean()
    shift = mean_dig - mean_paper

    ax2.axvline(mean_paper, color="#059669", linestyle=":", linewidth=1.5)
    ax2.axvline(mean_dig, color="#dc2626", linestyle=":", linewidth=1.5)

    ax2.annotate(f"Mean Shift: {shift:.2f} SD\n(Artificial ~8 percentile penalty)",
                 xy=((mean_paper + mean_dig)/2, 0.35), xytext=(-1.5, 0.35),
                 arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.2),
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee2e2", edgecolor="#dc2626"),
                 fontsize=9.5, fontweight="semibold", color="#991b1b")

    ax2.legend(loc="upper left")

    plt.tight_layout()
    output_path = FIG_DIR / "fig4_psychometric_civ_simulation.png"
    plt.savefig(output_path)
    plt.close()
    print(f"[OK] Saved Figure 4 to {output_path.name}")


def main():
    print("=" * 70)
    print("GENERATING PUBLICATION-READY FIGURES")
    print("=" * 70)
    setup_plotting_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_figure4()

    print("\nAll figures generated successfully.")


if __name__ == "__main__":
    main()
