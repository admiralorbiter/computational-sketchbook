"""
Generate Figure 15: CRDC Longitudinal High School Course Section Size Dynamics & The Student Experience Paradox.

4-Panel Architecture:
- Panel A: Longitudinal Section Size Trajectories across 9 Courses (2013-14 to 2023-24)
- Panel B: Subject Hierarchy & Section Scale in 2023-24
- Panel C: The Class-Size Paradox: School Average vs. Student-Weighted Experience vs. Large High Schools (>=1,500)
- Panel D: Kansas vs. Missouri Metro Sub-regions (2023-24)
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shutil

OBS_DIR = Path(__file__).resolve().parents[2]
SUMMARY_CSV = OBS_DIR / "outputs" / "crdc_historical_course_class_sizes_summary.csv"
DASHBOARD_DIR = OBS_DIR / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = DASHBOARD_DIR / "fig15_crdc_longitudinal_course_class_sizes.png"

def plot_figure():
    df_summary = pd.read_csv(SUMMARY_CSV)
    
    # Load microdata for student-weighted and tier calculations
    crdc_long = OBS_DIR.parent / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"
    df_long = pd.read_csv(crdc_long, low_memory=False)
    v24 = df_long[(df_long["school_year"] == "2023-2024") & 
                  (df_long["num_classes"] > 0) & 
                  (df_long["num_enrolled"] > 0) & 
                  (df_long["is_operating"] == True)].copy()
    v24["size"] = v24["num_enrolled"] / v24["num_classes"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    plt.subplots_adjust(hspace=0.32, wspace=0.24)

    colors = {
        "Algebra I": "#1f77b4", "Geometry": "#2ca02c", "Algebra II": "#ff7f0e",
        "Advanced Mathematics": "#9467bd", "Calculus": "#d62728", "Biology": "#8c564b",
        "Chemistry": "#e377c2", "Physics": "#7f7f7f", "Computer Science": "#17becf"
    }

    courses_order = [
        "Algebra I", "Geometry", "Algebra II", "Advanced Mathematics",
        "Calculus", "Biology", "Chemistry", "Physics"
    ]

    # ----------------------------------------------------
    # PANEL A: Longitudinal Section Size Trajectories
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    waves = ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]
    wave_x = {w: i for i, w in enumerate(waves)}

    for cname in courses_order + ["Computer Science"]:
        sub = df_summary[df_summary["course"] == cname].sort_values("wave")
        xs = [wave_x[w] for w in sub["wave"]]
        ys = sub["pooled_size"]
        lw = 2.4 if cname in ["Algebra I", "Biology", "Calculus", "Computer Science"] else 1.6
        marker = "s" if cname in ["Calculus", "Computer Science"] else "o"
        ax_a.plot(xs, ys, marker=marker, markersize=5.5, linewidth=lw, color=colors[cname], label=cname)

    ax_a.axvspan(2.6, 3.4, color="#fee0d2", alpha=0.5, label="COVID Disruption")
    ax_a.set_xticks(range(len(waves)))
    ax_a.set_xticklabels(waves, fontsize=9.5, fontweight="bold")
    ax_a.set_ylabel("Pooled Section Size (Students / Class)", fontsize=10, fontweight="bold")
    ax_a.set_title("A. Longitudinal Trajectories across KC Metro High Schools (2013-14 to 2023-24)", fontsize=11.5, fontweight="bold", pad=10)
    ax_a.grid(True, linestyle="--", alpha=0.4)
    ax_a.set_ylim(6, 23)
    ax_a.legend(loc="lower left", fontsize=8, ncol=2, frameon=True, facecolor="white", framealpha=0.9)

    # ----------------------------------------------------
    # PANEL B: Subject Hierarchy in 2023-24
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    df_24 = df_summary[df_summary["wave"] == "2023-24"].sort_values("pooled_size", ascending=True)
    bars = ax_b.barh(df_24["course"], df_24["pooled_size"], color=[colors[c] for c in df_24["course"]], alpha=0.85, height=0.62)
    for bar in bars:
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax_b.text(w + 0.3, y, f"{w:.1f}", va="center", ha="left", fontsize=9, fontweight="bold")
    ax_b.set_xlabel("Pooled Section Size in 2023-24", fontsize=10, fontweight="bold")
    ax_b.set_title("B. Subject Hierarchy: Pooled Section Size in 2023-24", fontsize=11.5, fontweight="bold", pad=10)
    ax_b.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_b.set_xlim(0, 22)

    # ----------------------------------------------------
    # PANEL C: The Class-Size Paradox (School Mean vs Student-Weighted vs Large High Schools)
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    c_data = []
    for c in courses_order:
        sub = v24[v24["course_name"] == c]
        u_mean = sub["size"].mean()
        w_mean = np.average(sub["size"], weights=sub["num_enrolled"])
        large_mean = sub[sub["enrollment_k12"] >= 1500]["size"].mean()
        c_data.append({"course": c, "u_mean": u_mean, "w_mean": w_mean, "large_mean": large_mean})
    df_c = pd.DataFrame(c_data)

    y_pos = np.arange(len(df_c))
    bar_w = 0.27
    ax_c.barh(y_pos - bar_w, df_c["u_mean"], height=bar_w, color="#9ecae1", label="School Unweighted Mean (~17)", alpha=0.9)
    ax_c.barh(y_pos, df_c["w_mean"], height=bar_w, color="#2171b5", label="Student-Weighted Mean (Kid Exp. ~21)", alpha=0.9)
    ax_c.barh(y_pos + bar_w, df_c["large_mean"], height=bar_w, color="#fc8d59", label="Large High Schools (>=1500, ~22-24)", alpha=0.9)

    for i, (_, r) in enumerate(df_c.iterrows()):
        ax_c.text(r["u_mean"] + 0.2, i - bar_w, f"{r['u_mean']:.1f}", va="center", ha="left", fontsize=7.5, color="#08519c", fontweight="bold")
        ax_c.text(r["w_mean"] + 0.2, i, f"{r['w_mean']:.1f}", va="center", ha="left", fontsize=7.5, color="#08306b", fontweight="bold")
        ax_c.text(r["large_mean"] + 0.2, i + bar_w, f"{r['large_mean']:.1f}", va="center", ha="left", fontsize=7.5, color="#b30000", fontweight="bold")

    ax_c.set_yticks(y_pos)
    ax_c.set_yticklabels(df_c["course"], fontsize=8.5)
    ax_c.set_xlabel("Class Section Size (Students / Class)", fontsize=10, fontweight="bold")
    ax_c.set_title("C. The Class-Size Paradox: School Average vs. Student Experience (2023-24)", fontsize=11.5, fontweight="bold", pad=10)
    ax_c.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_c.set_xlim(0, 28)
    ax_c.legend(loc="lower right", fontsize=8.5)
    ax_c.invert_yaxis()

    # ----------------------------------------------------
    # PANEL D: Kansas vs. Missouri Metro Sub-regions
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    df_state = df_summary[df_summary["wave"] == "2023-24"].copy()
    df_state["sort_key"] = df_state["course"].map({c: i for i, c in enumerate(courses_order + ["Computer Science"])})
    df_state = df_state.sort_values("sort_key")

    y_pos_d = np.arange(len(df_state))
    bar_w_d = 0.38
    ax_d.barh(y_pos_d - bar_w_d/2, df_state["mo_pooled"], height=bar_w_d, color="#3182bd", alpha=0.85, label="Missouri (5 Counties)")
    ax_d.barh(y_pos_d + bar_w_d/2, df_state["ks_pooled"], height=bar_w_d, color="#e6550d", alpha=0.85, label="Kansas (4 Counties)")

    for i, (_, r) in enumerate(df_state.iterrows()):
        ax_d.text(r["mo_pooled"] + 0.25, i - bar_w_d/2, f"{r['mo_pooled']:.1f}", va="center", ha="left", fontsize=8, color="#3182bd", fontweight="bold")
        ax_d.text(r["ks_pooled"] + 0.25, i + bar_w_d/2, f"{r['ks_pooled']:.1f}", va="center", ha="left", fontsize=8, color="#e6550d", fontweight="bold")

    ax_d.set_yticks(y_pos_d)
    ax_d.set_yticklabels(df_state["course"], fontsize=8.5)
    ax_d.set_xlabel("Pooled Section Size (Students / Class)", fontsize=10, fontweight="bold")
    ax_d.set_title("D. Kansas vs. Missouri Metro Sub-regions (2023-24)", fontsize=11.5, fontweight="bold", pad=10)
    ax_d.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_d.set_xlim(0, 24)
    ax_d.legend(loc="lower right", fontsize=8.5)
    ax_d.invert_yaxis()

    plt.suptitle("Kansas City Metropolitan Civil Rights Data Collection (CRDC)\nHigh School Course Section Size Dynamics & The Student Experience Paradox", fontsize=14, fontweight="bold", y=0.98)
    
    fig.subplots_adjust(top=0.92, bottom=0.07, left=0.08, right=0.96, hspace=0.30, wspace=0.24)
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 15 to {OUT_PNG.relative_to(OBS_DIR)}")

    # Copy to artifacts directory
    art_dir = Path.home() / ".gemini" / "antigravity" / "brain" / "341419bd-5669-4622-8d51-d6eecec301ff"
    if art_dir.exists():
        shutil.copy(OUT_PNG, art_dir / "fig15_crdc_longitudinal_course_class_sizes.png")
        print("Copied Figure 15 to artifacts directory.")

if __name__ == "__main__":
    plot_figure()
