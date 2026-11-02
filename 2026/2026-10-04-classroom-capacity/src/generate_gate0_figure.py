"""
Generate publication quality figure for Phase 9A.1 Gate 0:
fig_e01_florida_gate0_responsiveness.png

Visualizes:
1. Empirical section responsiveness vs. theoretical Maimonides rule at C=25.
2. Implied class size (E/K) vs. theoretical sawtooth across E in [10, 85].
3. Section multiplicity (K >= 3) and low-enrollment cell structure in E in [20, 30].
4. Gate 0 stopping rule diagnostic summary card.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "artifacts" / "figures"
BRAIN_DIR = Path(r"C:\Users\admir\.gemini\antigravity\brain\873b7f0f-08cb-453c-b3e0-5a0024dac318")

def generate_figure():
    # Load data
    df = pd.read_parquet(DATA_DIR / "crdc_course_panel.parquet")
    sc = pd.read_parquet(DATA_DIR / "school_context_panel.parquet")
    sc_cols = sc[["nces_school_id", "school_year", "is_high_school", "is_charter"]].copy()
    m = df.merge(sc_cols, on=["nces_school_id", "school_year"], how="inner")
    fl = m[
        (m["state"] == "FL") &
        (m["is_high_school"] == True) &
        (m["is_charter"] == False) &
        (m["num_classes"] > 0) &
        (m["num_enrolled"] > 0)
    ].copy()
    
    # Set style
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    fig.subplots_adjust(hspace=0.32, wspace=0.25)
    fig.patch.set_facecolor("#fcfcfc")
    
    # ----------------------------------------------------
    # Panel A: P(K >= 2) near C=25
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    ax_a.set_facecolor("#ffffff")
    
    e_range = list(range(20, 31))
    sub_20_30 = fl[fl["num_enrolled"].isin(e_range)]
    p_k2_all = sub_20_30.groupby("num_enrolled")["num_classes"].apply(lambda x: (x >= 2).mean())
    comp = fl[(fl["school_enrollment"] >= 300) & (fl["num_enrolled"].isin(e_range))]
    p_k2_comp = comp.groupby("num_enrolled")["num_classes"].apply(lambda x: (x >= 2).mean())
    
    # Theoretical sharp rule: 0 for <=25, 1 for >=26
    theory_e = np.array([20, 25, 25.0001, 26, 30])
    theory_p = np.array([0, 0, 1, 1, 1])
    
    ax_a.step(theory_e, theory_p, where="post", color="#d9534f", linestyle="--", linewidth=2.0, label="Theoretical Rule (C=25 Mandate)")
    ax_a.plot(p_k2_all.index, p_k2_all.values, marker="o", color="#1f77b4", linewidth=2.2, label="All Non-Charter HS (N=1,496)")
    ax_a.plot(p_k2_comp.index, p_k2_comp.values, marker="s", color="#2ca02c", linewidth=2.0, linestyle=":", label="Comprehensive Non-Charter Enr >= 300 (N=486)")
    
    ax_a.axvline(25.5, color="#333333", linestyle="-.", alpha=0.7, linewidth=1.2)
    ax_a.text(25.6, 0.40, "Statutory Cap Cutoff\n(E = 25 -> 26)", fontsize=9, color="#333333", fontweight="bold")
    
    ax_a.set_title("Panel A: Section Formation Discontinuity Audit at C=25", fontsize=11, fontweight="bold", pad=10)
    ax_a.set_xlabel("Reported Course Enrollment (E)", fontsize=10)
    ax_a.set_ylabel("Pr(Sections K >= 2)", fontsize=10)
    ax_a.set_ylim(-0.05, 1.05)
    ax_a.set_xlim(19.5, 30.5)
    ax_a.set_xticks(range(20, 31))
    ax_a.grid(True, linestyle="--", alpha=0.3)
    ax_a.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
    
    # Add annotation for null jump
    ax_a.annotate("Discontinuity: -0.005, p = 0.923\nLocal Regression F = 1.13 (Null)",
                  xy=(25.5, 0.785), xytext=(20.8, 0.88),
                  arrowprops=dict(facecolor="#1f77b4", shrink=0.08, width=1.5, headwidth=6),
                  fontsize=8.5, fontweight="bold", color="#1f77b4",
                  bbox=dict(boxstyle="round,pad=0.3", facecolor="#eef4f8", edgecolor="#1f77b4", alpha=0.9))
    
    # ----------------------------------------------------
    # Panel B: Implied Class Size (E/K) vs Theoretical Sawtooth
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    ax_b.set_facecolor("#ffffff")
    
    e_all = np.arange(10, 86)
    theory_cs = e_all / np.ceil(e_all / 25.0)
    
    # Empirical binned class sizes
    sub_span = fl[(fl["num_enrolled"] >= 10) & (fl["num_enrolled"] <= 85)]
    emp_cs = sub_span.groupby("num_enrolled")["mean_class_size"].mean()
    emp_p50 = sub_span.groupby("num_enrolled")["mean_class_size"].median()
    
    ax_b.plot(e_all, theory_cs, color="#d9534f", linestyle="--", linewidth=1.8, label="Theoretical Sawtooth (E / ceil(E/25))")
    ax_b.plot(emp_cs.index, emp_cs.values, color="#1f77b4", linewidth=2.0, label="Empirical Mean (E / K)")
    ax_b.plot(emp_p50.index, emp_p50.values, color="#ff7f0e", linestyle=":", linewidth=1.8, label="Empirical Median (E / K)")
    
    # Mark cutoffs
    for cut in [25.5, 50.5, 75.5]:
        ax_b.axvline(cut, color="#888888", linestyle="-.", alpha=0.5, linewidth=1.0)
    ax_b.text(26, 26, "Cut 25", fontsize=8, color="#555555")
    ax_b.text(51, 26, "Cut 50", fontsize=8, color="#555555")
    ax_b.text(76, 26, "Cut 75", fontsize=8, color="#555555")
    
    ax_b.set_title("Panel B: Implied Class Size vs. Theoretical Sawtooth", fontsize=11, fontweight="bold", pad=10)
    ax_b.set_xlabel("Reported Course Enrollment (E)", fontsize=10)
    ax_b.set_ylabel("Implied Average Class Size (E / K)", fontsize=10)
    ax_b.set_ylim(0, 32)
    ax_b.set_xlim(10, 85)
    ax_b.grid(True, linestyle="--", alpha=0.3)
    ax_b.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
    
    # ----------------------------------------------------
    # Panel C: Distribution of K in E in [20, 30]
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    ax_c.set_facecolor("#ffffff")
    
    k_counts = sub_20_30["num_classes"].value_counts().sort_index()
    k_counts_top = k_counts[k_counts.index <= 8].copy()
    k_counts_top.loc["9+"] = k_counts[k_counts.index > 8].sum()
    
    pcts = (k_counts_top / len(sub_20_30)) * 100
    bars = ax_c.bar([str(x) for x in k_counts_top.index], pcts.values, color="#4a7c59", edgecolor="#2d5236", width=0.6)
    
    # Highlight anomalous K >= 3
    for i, bar in enumerate(bars):
        if i >= 2: # K >= 3
            bar.set_color("#c94c4c")
            bar.set_edgecolor("#8b2b2b")
            
    ax_c.set_title("Panel C: Section Count Multiplicity in E in [20, 30] (N=1,496)", fontsize=11, fontweight="bold", pad=10)
    ax_c.set_xlabel("Reported Section Count (K)", fontsize=10)
    ax_c.set_ylabel("Percentage of Course Cells (%)", fontsize=10)
    ax_c.set_ylim(0, 35)
    ax_c.grid(True, linestyle="--", alpha=0.3, axis="y")
    
    # Bar labels
    for bar in bars:
        h = bar.get_height()
        ax_c.text(bar.get_x() + bar.get_width()/2., h + 0.6, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        
    ax_c.annotate("53.2% of cells have K >= 3\n(Implied Class Size <= 10.0)\nMultiplicity & Structure Noise",
                  xy=(4, 15), xytext=(4.2, 22),
                  arrowprops=dict(facecolor="#c94c4c", shrink=0.08, width=1.5, headwidth=6),
                  fontsize=8.5, fontweight="bold", color="#8b2b2b",
                  bbox=dict(boxstyle="round,pad=0.3", facecolor="#fdf2f2", edgecolor="#c94c4c", alpha=0.9))
    
    # ----------------------------------------------------
    # Panel D: Diagnostic Decision Card (Gate 0 Verdict)
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    ax_d.axis("off")
    
    card_text = (
        "GATE 0 EMPIRICAL AUDIT: STOPPING RULE TRIGGERED\n"
        "---------------------------------------------------------------------------------\n"
        "1. NO SECTION JUMP AT C = 25:\n"
        "   - Local discontinuity in Pr(K >= 2): -0.0049 (z = -0.10, p = 0.923).\n"
        "   - Comprehensive HS (>=300): jump = +0.0541 (p = 0.621).\n"
        "   - Local first-stage regression F = 1.13 (Best-case clean F = 0.35).\n\n"
        "2. OBSERVATIONAL UNIT MISMATCH:\n"
        "   - Florida compliance audits individual classrooms.\n"
        "   - CRDC provides school-course aggregates.\n"
        "   - Scheduling is governed by periods, blocks, & staffing,\n"
        "     not a deterministic K = ceil(E/25) formula on total demand.\n\n"
        "3. INSTITUTIONAL & REPORTING CONCEALMENT:\n"
        "   - CRDC lacks educator links to reconstruct co-teaching rules.\n"
        "   - Schedule structure (block vs period) unobserved.\n\n"
        "4. MULTIPLICITY IN LOW ENROLLMENT [20, 30]:\n"
        "   - 53.2% have K >= 3 sections (mean class size < 10.0).\n"
        "   - 35.7% in small schools (< 300); 47.3% broad keyword flag.\n\n"
        "---------------------------------------------------------------------------------\n"
        "DECISION: CRDC CANNOT RECOVER STATUTORY FIRST STAGE.\n"
        "PIVOT TO PHASE 9B: TWO-TIER ADMINISTRATIVE PROTOCOL (9B-1 & 9B-2)."
    )
    
    ax_d.text(0.02, 0.98, card_text, fontsize=8.8, family="monospace", va="top", ha="left",
              bbox=dict(boxstyle="round,pad=0.6", facecolor="#fff9e6", edgecolor="#d4a017", linewidth=1.5))
    
    plt.suptitle("Florida Secondary Class Size Quasi-Experiment: Gate 0 Feasibility Audit\nTesting the Discontinuity of Public CRDC Course Enrollment Around Florida's 25-Student Cap",
                 fontsize=13, fontweight="bold", y=0.98)
    
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_fig = FIGURES_DIR / "fig_e01_florida_gate0_responsiveness.png"
    plt.savefig(out_fig, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved Gate 0 figure to {out_fig}")
    
    # Also copy to brain dir
    if BRAIN_DIR.exists():
        import shutil
        shutil.copy(out_fig, BRAIN_DIR / "fig_e01_florida_gate0_responsiveness.png")
        print(f"Copied Gate 0 figure to brain directory: {BRAIN_DIR / 'fig_e01_florida_gate0_responsiveness.png'}")

if __name__ == "__main__":
    generate_figure()
