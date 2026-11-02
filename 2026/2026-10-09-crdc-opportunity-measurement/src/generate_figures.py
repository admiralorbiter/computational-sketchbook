"""
Generate publication-quality figures for the Missouri CRDC Measurement Study.

Figures:
1. fig1_ap_dual_contingency.png: 4-Cell Matrix & Dual Opportunity Rates (Non-AP vs. Either Route)
2. fig2_ap_cs_concealment.png: Reported Student Participation in AP Computer Science
3. fig3_physics_denominator_wedge.png: Institutional Availability vs. Student Exposure in Physics Provision
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Styling defaults
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 0.8,
    "grid.color": "#f1f5f9",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
})


def load_data():
    df = pd.read_parquet(DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet")
    return df[df["flag_consistent_9_12"]].copy(), df[df["flag_matched_crdc"]].copy()


def plot_fig1(df_307):
    """Figure 1: 4-Cell Pathway Matrix & Non-AP Dual Enrollment Rate."""
    fig, (ax_mat, ax_bar) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1.1, 1]})

    # 1. 2x2 Matrix
    matrix_vals = np.array([
        [8, 105],   # No AP
        [14, 180]   # Yes AP
    ])
    total = 307

    cax = ax_mat.matshow(matrix_vals, cmap="Blues", alpha=0.85)

    for i in range(2):
        for j in range(2):
            count = matrix_vals[i, j]
            pct = count / total * 100
            label = f"{count} schools\n({pct:.1f}%)"
            color = "white" if count > 100 else "#0f172a"
            ax_mat.text(j, i, label, ha="center", va="center", fontsize=12, fontweight="bold", color=color)

    ax_mat.set_xticks([0, 1])
    ax_mat.set_yticks([0, 1])
    ax_mat.set_xticklabels(["No Dual\n(N=22)", "Yes Dual\n(N=285)"], fontsize=11)
    ax_mat.set_yticklabels(["No AP\n(N=113)", "Yes AP\n(N=194)"], fontsize=11)
    ax_mat.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
    ax_mat.set_xlabel("Dual-Enrollment Participation Indicator", fontsize=11, fontweight="semibold", labelpad=8)
    ax_mat.set_ylabel("AP Participation Indicator", fontsize=11, fontweight="semibold", labelpad=8)
    ax_mat.set_title("Missouri Grades 9–12 Public High Schools (N=307)\nFour-Cell Participation Matrix", fontsize=12, fontweight="bold", pad=12)

    # 2. Dual Enrollment Rates Under Alternate Denominators
    rate_no_ap = 105 / 113 * 100         # 92.9%
    rate_either = 105 / 299 * 100        # 35.1%

    bar_labels = [
        "Conditional Rate:\nAmong Non-AP Schools\n(105 / 113)",
        "Overall Miss Rate:\nAmong Either Route\n(105 / 299)"
    ]
    colors = ["#2563eb", "#0ea5e9"]

    bars = ax_bar.bar([0, 1], [rate_no_ap, rate_either], color=colors, width=0.52, edgecolor="#0f172a", linewidth=0.8)
    ax_bar.set_xticks([0, 1])
    ax_bar.set_xticklabels(bar_labels, fontsize=10.5)
    ax_bar.set_ylabel("Percentage (%)", fontsize=11, fontweight="semibold")
    ax_bar.set_ylim(0, 110)
    ax_bar.set_title("Dual Enrollment Metrics by Denominator Choice", fontsize=12, fontweight="bold", pad=12)
    ax_bar.grid(axis="y", alpha=0.7)

    for bar, val, count, denom in zip(bars, [rate_no_ap, rate_either], [105, 105], [113, 299]):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2.5, f"{val:.1f}%\n({count}/{denom})", ha="center", va="bottom", fontsize=11, fontweight="bold", color="#0f172a")

    plt.tight_layout()
    fig.savefig(ARTIFACTS_DIR / "fig1_ap_dual_contingency.png", dpi=250)
    plt.close(fig)
    print("Saved fig1_ap_dual_contingency.png")


def plot_fig2(df_307):
    """Figure 2: AP Computer Science Reported Participation Concealment."""
    ap_schools = df_307[df_307["ap_participating"]].copy()
    n_ap = len(ap_schools)
    n_no_cs = (ap_schools["ap_cs_indicator_raw"] == "No").sum()
    n_yes_cs = (ap_schools["ap_cs_indicator_raw"] == "Yes").sum()

    fig, ax = plt.subplots(figsize=(8.5, 5))
    bars = ax.barh(
        ["Reported AP CS Participation\n(SCH_APCOMPENR_IND = Yes)", "Reported Zero AP CS Participation\n(SCH_APCOMPENR_IND = No)"],
        [n_yes_cs / n_ap * 100, n_no_cs / n_ap * 100],
        color=["#10b981", "#ef4444"],
        height=0.45,
        edgecolor="#0f172a",
        linewidth=0.8
    )

    ax.set_xlim(0, 80)
    ax.set_xlabel("Percentage of AP-Participating High Schools (%)", fontsize=11, fontweight="semibold", labelpad=8)
    ax.set_title(f"Reported AP Computer Science Participation in AP Schools (N={n_ap})\n65.5% of AP Schools Report Zero AP Computer Science Enrollment", fontsize=12, fontweight="bold", pad=14)
    ax.grid(axis="x", alpha=0.7)

    for bar, val, count in zip(bars, [n_yes_cs / n_ap * 100, n_no_cs / n_ap * 100], [n_yes_cs, n_no_cs]):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2, f"{val:.1f}% ({count} schools)", va="center", fontsize=11, fontweight="bold", color="#0f172a")

    plt.tight_layout()
    fig.savefig(ARTIFACTS_DIR / "fig2_ap_cs_concealment.png", dpi=250)
    plt.close(fig)
    print("Saved fig2_ap_cs_concealment.png")


def plot_fig3(df_307):
    """Figure 3: Physics Provision Denominator Divergence & School Scale."""
    zero_phys = df_307["physics_classes"] == 0
    school_pct = zero_phys.mean() * 100

    rel_enr = df_307["crdc_released_enrollment"].sum()
    zero_rel_enr = df_307.loc[zero_phys, "crdc_released_enrollment"].sum()
    student_pct = zero_rel_enr / rel_enr * 100
    wedge = school_pct - student_pct

    fig, (ax_bar, ax_box) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1, 1.2]})

    # 1. Denominator comparison
    bars = ax_bar.bar(
        [0, 1],
        [school_pct, student_pct],
        color=["#f59e0b", "#3b82f6"],
        width=0.5,
        edgecolor="#0f172a",
        linewidth=0.8
    )
    ax_bar.set_xticks([0, 1])
    ax_bar.set_xticklabels([f"School Denominator\n(101 / 307 schools)", f"Student Denominator\n(41,616 / 228,637 released)"], fontsize=10.5)
    ax_bar.set_ylabel("Share Reporting Zero Physics Classes (%)", fontsize=11, fontweight="semibold")
    ax_bar.set_ylim(0, 42)
    ax_bar.set_title(f"Institutional Availability vs. Student Exposure\nDivergence: {wedge:.2f} Percentage Points", fontsize=12, fontweight="bold", pad=12)
    ax_bar.grid(axis="y", alpha=0.7)

    for bar, val in zip(bars, [school_pct, student_pct]):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.0, f"{val:.2f}%", ha="center", va="bottom", fontsize=12, fontweight="bold")

    # Annotate divergence arrow
    ax_bar.annotate(
        f"Divergence: -{wedge:.2f} pp",
        xy=(1, student_pct), xytext=(0.5, (school_pct + student_pct) / 2 + 5),
        arrowprops=dict(facecolor="#dc2626", shrink=0.08, width=1.5, headwidth=6),
        fontsize=10.5, fontweight="bold", color="#dc2626", ha="center"
    )

    # 2. Enrollment scale explanation
    box_data = [
        df_307.loc[zero_phys, "crdc_released_enrollment"].dropna(),
        df_307.loc[~zero_phys, "crdc_released_enrollment"].dropna()
    ]
    ax_box.boxplot(
        box_data,
        tick_labels=["Zero Physics Classes\n(Mean: 412, Med: 280)", ">=1 Physics Class\n(Mean: 908, Med: 728)"],
        widths=0.45,
        patch_artist=True,
        boxprops=dict(facecolor="#e2e8f0", color="#334155", linewidth=1.2),
        medianprops=dict(color="#2563eb", linewidth=2),
        whiskerprops=dict(color="#334155"),
        capprops=dict(color="#334155"),
        flierprops=dict(marker="o", color="#94a3b8", alpha=0.5, markersize=4)
    )
    ax_box.set_ylabel("Released Student Enrollment Headcount", fontsize=11, fontweight="semibold")
    ax_box.set_title("Institutional Scale Explains the Divergence:\nZero-Physics High Schools Are Systematically Smaller", fontsize=12, fontweight="bold", pad=12)
    ax_box.grid(axis="y", alpha=0.7)

    plt.tight_layout()
    fig.savefig(ARTIFACTS_DIR / "fig3_physics_denominator_wedge.png", dpi=250)
    plt.close(fig)
    print("Saved fig3_physics_denominator_wedge.png")


def main():
    df_307, df_317 = load_data()
    plot_fig1(df_307)
    plot_fig2(df_307)
    plot_fig3(df_307)
    print("All figures generated successfully in artifacts/.")


if __name__ == "__main__":
    main()
