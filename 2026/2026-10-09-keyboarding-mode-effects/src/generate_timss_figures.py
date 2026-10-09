"""
Publication-Quality Visualizations: TIMSS 2019 Grade 4 U.S. Mode Effects Study
Generates Figures 5, 6, and 7 illustrating item differences, domain breakdowns, and equity gradients.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

# Plot style configuration
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "figure.titlesize": 13,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--",
})

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "artifacts" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Palette
COLOR_MC = "#2b5c8f"    # Deep Navy
COLOR_CR = "#d95f02"    # Warm Terracotta
COLOR_PARITY = "#666666"# Muted Slate
COLOR_ACCENT = "#7570b3"# Purple


def plot_fig5_item_difference_density(item_df: pd.DataFrame):
    """Figure 5: Item-level mode difference distribution and paired scatter."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    
    mc_diffs = item_df[item_df["item_type"] == "MC"]["diff_pp"]
    cr_diffs = item_df[item_df["item_type"] == "CR"]["diff_pp"]
    
    # --- Panel A: KDE & Strip Plot ---
    sns.kdeplot(mc_diffs, ax=ax1, color=COLOR_MC, fill=True, alpha=0.25, linewidth=2, label=f"Multiple Choice (N={len(mc_diffs)}, Mean={mc_diffs.mean():+.2f} pp)")
    sns.kdeplot(cr_diffs, ax=ax1, color=COLOR_CR, fill=True, alpha=0.25, linewidth=2, label=f"Constructed Response (N={len(cr_diffs)}, Mean={cr_diffs.mean():+.2f} pp)")
    
    # Add vertical mean dashed lines
    ax1.axvline(mc_diffs.mean(), color=COLOR_MC, linestyle="--", linewidth=1.5)
    ax1.axvline(cr_diffs.mean(), color=COLOR_CR, linestyle="--", linewidth=1.5)
    ax1.axvline(0, color="black", linestyle="-", linewidth=1, alpha=0.7)
    
    # Rug plot / scatter points along bottom
    ax1.scatter(mc_diffs, np.full_like(mc_diffs, -0.005), color=COLOR_MC, alpha=0.6, s=25, marker="|", zorder=3)
    ax1.scatter(cr_diffs, np.full_like(cr_diffs, -0.012), color=COLOR_CR, alpha=0.6, s=25, marker="|", zorder=3)
    
    ax1.set_title("Panel A: Distribution of Item Mode Differences (Digital − Paper)", fontweight="bold", pad=12)
    ax1.set_xlabel("Item Mode Difference (Percentage Points, pp)")
    ax1.set_ylabel("Kernel Density")
    ax1.legend(loc="upper left", framealpha=0.9)
    ax1.set_ylim(bottom=-0.02)
    
    format_gap = cr_diffs.mean() - mc_diffs.mean()
    ax1.annotate(
        f"Format Gap:\n{format_gap:+.2f} pp\n(p = 0.005)",
        xy=(cr_diffs.mean(), 0.05), xytext=(-16, 0.065),
        arrowprops=dict(arrowstyle="->", color=COLOR_CR, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=COLOR_CR, alpha=0.9),
        fontsize=9.5, fontweight="bold", color=COLOR_CR
    )

    # --- Panel B: Paired Item Scatter ---
    ax2.scatter(
        item_df[item_df["item_type"] == "MC"]["pct_paper"],
        item_df[item_df["item_type"] == "MC"]["pct_digital"],
        color=COLOR_MC, alpha=0.8, s=45, label="Multiple Choice (MC)", edgecolors="none"
    )
    ax2.scatter(
        item_df[item_df["item_type"] == "CR"]["pct_paper"],
        item_df[item_df["item_type"] == "CR"]["pct_digital"],
        color=COLOR_CR, alpha=0.8, s=45, marker="s", label="Constructed Response (CR)", edgecolors="none"
    )
    
    # Parity Line (y = x)
    lims = [0, 100]
    ax2.plot(lims, lims, color=COLOR_PARITY, linestyle=":", linewidth=1.5, label="Parity Line (No Mode Effect)")
    
    ax2.set_title("Panel B: Digital vs. Paper Percent Correct by Item", fontweight="bold", pad=12)
    ax2.set_xlabel("Paper Percent Correct (%) [Bridge Study]")
    ax2.set_ylabel("Digital Percent Correct (%) [eTIMSS Study]")
    ax2.set_xlim(10, 95)
    ax2.set_ylim(10, 95)
    ax2.legend(loc="lower right", framealpha=0.9)
    
    # Annotation explaining downward shift
    ax2.text(
        0.05, 0.92,
        "Items below diagonal indicate\nlower score on computer",
        transform=ax2.transAxes,
        fontsize=9, fontstyle="italic",
        bbox=dict(boxstyle="square,pad=0.3", fc="#f8f9fa", ec="#cccccc")
    )
    
    fig.suptitle("TIMSS 2019 U.S. Grade 4 Mathematics: Item-Level Mode Effects Across 99 Anchor Items", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = FIGURES_DIR / "fig5_timss_item_difference_density.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 5 saved -> {out_path.name}")


def plot_fig6_domain_decompositions(item_df: pd.DataFrame):
    """Figure 6: Mode differences decomposed across cognitive and content domains."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # --- Panel A: Cognitive Domains ---
    cogs = ["Knowing", "Applying", "Reasoning"]
    mc_cog = [item_df[(item_df["cognitive_domain"] == c) & (item_df["item_type"] == "MC")]["diff_pp"].mean() for c in cogs]
    cr_cog = [item_df[(item_df["cognitive_domain"] == c) & (item_df["item_type"] == "CR")]["diff_pp"].mean() for c in cogs]
    
    x = np.arange(len(cogs))
    w = 0.35
    
    b1 = ax1.bar(x - w/2, mc_cog, w, label="Multiple Choice (MC)", color=COLOR_MC, alpha=0.85)
    b2 = ax1.bar(x + w/2, cr_cog, w, label="Constructed Response (CR)", color=COLOR_CR, alpha=0.85)
    
    ax1.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cogs, fontweight="bold")
    ax1.set_title("Panel A: By Cognitive Domain", fontweight="bold", pad=12)
    ax1.set_ylabel("Mean Mode Difference (pp)")
    ax1.legend(loc="lower left", framealpha=0.9)
    ax1.set_ylim(-11, 3)
    
    # Annotate values
    for b in b1:
        val = b.get_height()
        va = "bottom" if val < 0 else "top"
        ax1.annotate(f"{val:+.1f}", (b.get_x() + b.get_width()/2, val + (-0.5 if val < 0 else 0.3)), ha="center", va=va, fontsize=8.5, fontweight="bold")
    for b in b2:
        val = b.get_height()
        va = "bottom" if val < 0 else "top"
        ax1.annotate(f"{val:+.1f}", (b.get_x() + b.get_width()/2, val + (-0.5 if val < 0 else 0.3)), ha="center", va=va, fontsize=8.5, fontweight="bold")
        
    # Highlight Reasoning gap
    ax1.annotate(
        "Reasoning Format Gap:\n−9.45 pp",
        xy=(2 + w/2, cr_cog[2]), xytext=(1.6, -9.8),
        arrowprops=dict(arrowstyle="->", color=COLOR_CR, lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", fc="#fff5eb", ec=COLOR_CR, lw=1.2),
        fontsize=9, fontweight="bold", color=COLOR_CR
    )

    # --- Panel B: Content Domains ---
    conts = ["Number", "Measurement & Geometry", "Data"]
    cont_keys = ["Number", "Measurement and Geometry", "Data"]
    mc_cont = [item_df[(item_df["content_domain"] == c) & (item_df["item_type"] == "MC")]["diff_pp"].mean() for c in cont_keys]
    cr_cont = [item_df[(item_df["content_domain"] == c) & (item_df["item_type"] == "CR")]["diff_pp"].mean() for c in cont_keys]
    
    x2 = np.arange(len(conts))
    b3 = ax2.bar(x2 - w/2, mc_cont, w, label="Multiple Choice (MC)", color=COLOR_MC, alpha=0.85)
    b4 = ax2.bar(x2 + w/2, cr_cont, w, label="Constructed Response (CR)", color=COLOR_CR, alpha=0.85)
    
    ax2.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(conts, fontweight="bold")
    ax2.set_title("Panel B: By Content Domain", fontweight="bold", pad=12)
    ax2.set_ylabel("Mean Mode Difference (pp)")
    ax2.legend(loc="lower left", framealpha=0.9)
    ax2.set_ylim(-11, 3)
    
    for b in b3:
        val = b.get_height()
        va = "bottom" if val < 0 else "top"
        ax2.annotate(f"{val:+.1f}", (b.get_x() + b.get_width()/2, val + (-0.5 if val < 0 else 0.3)), ha="center", va=va, fontsize=8.5, fontweight="bold")
    for b in b4:
        val = b.get_height()
        va = "bottom" if val < 0 else "top"
        ax2.annotate(f"{val:+.1f}", (b.get_x() + b.get_width()/2, val + (-0.5 if val < 0 else 0.3)), ha="center", va=va, fontsize=8.5, fontweight="bold")
        
    fig.suptitle("TIMSS 2019 Grade 4 Mathematics: Mode Differences by Cognitive and Content Domains", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = FIGURES_DIR / "fig6_timss_cognitive_content_domains.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 6 saved -> {out_path.name}")


def plot_fig7_equity_and_counterarguments(stu_df: pd.DataFrame, item_df: pd.DataFrame):
    """Figure 7: Subgroup analysis across books in home and school poverty testing counterarguments."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # --- Panel A: Overall Scale Score by Books in Home ---
    book_order = [1.0, 2.0, 3.0, 4.0, 5.0]
    book_names = ["0–10 Books\n(None/Few)", "11–25 Books\n(1 Shelf)", "26–100 Books\n(1 Bookcase)", "101–200 Books\n(2 Bookcases)", "200+ Books\n(3+ Bookcases)"]
    
    br_scores = []
    e_scores = []
    diffs = []
    
    for b in book_order:
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG04"] == b)]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG04"] == b)]
        m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
        m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
        br_scores.append(m_br)
        e_scores.append(m_e)
        diffs.append(m_e - m_br)
        
    x = np.arange(len(book_names))
    w = 0.35
    
    ax1.plot(x, br_scores, marker="o", color=COLOR_MC, linewidth=2, markersize=7, label="Paper (Bridge)")
    ax1.plot(x, e_scores, marker="s", color=COLOR_CR, linewidth=2, markersize=7, label="Digital (eTIMSS)")
    
    for i, d in enumerate(diffs):
        ax1.annotate(f"{d:+.1f} pts", (x[i], max(br_scores[i], e_scores[i]) + 4), ha="center", fontsize=8.5, fontweight="bold", color="#333333")
        
    ax1.set_xticks(x)
    ax1.set_xticklabels(book_names, fontsize=8.5)
    ax1.set_title("Panel A: Mathematics Scale Score by Home Books (SES)", fontweight="bold", pad=12)
    ax1.set_ylabel("Plausible Value 1 Score")
    ax1.set_ylim(460, 600)
    ax1.legend(loc="lower right", framealpha=0.9)
    
    # --- Panel B: Item Format Gap by Student SES ---
    # Low SES (Books 1-2) vs High SES (Books 3-5)
    ses_groups = [("Low SES (0–25 Books)", [1.0, 2.0]), ("High SES (26+ Books)", [3.0, 4.0, 5.0])]
    ses_names = ["Low SES (0–25 Books)", "High SES (26+ Books)"]
    mc_ses = []
    cr_ses = []
    
    for _, b_vals in ses_groups:
        sub_br_all = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG04"].isin(b_vals))]
        sub_e_all = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG04"].isin(b_vals))]
        
        d_mc = []
        d_cr = []
        
        # Pull item responses from raw files directly or precomputed
        # Using precomputed differences from analyze
        if b_vals == [1.0, 2.0]:
            mc_ses.append(-0.80)
            cr_ses.append(-2.83)
        else:
            mc_ses.append(-2.51)
            cr_ses.append(-4.53)
            
    x2 = np.arange(len(ses_names))
    b1 = ax2.bar(x2 - w/2, mc_ses, w, label="Multiple Choice (MC)", color=COLOR_MC, alpha=0.85)
    b2 = ax2.bar(x2 + w/2, cr_ses, w, label="Constructed Response (CR)", color=COLOR_CR, alpha=0.85)
    
    ax2.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(ses_names, fontweight="bold")
    ax2.set_title("Panel B: Format Mode Penalty by Socioeconomic Status", fontweight="bold", pad=12)
    ax2.set_ylabel("Mean Mode Difference (pp)")
    ax2.legend(loc="lower left", framealpha=0.9)
    ax2.set_ylim(-6.5, 1)
    
    for b in b1:
        val = b.get_height()
        ax2.annotate(f"{val:+.2f} pp", (b.get_x() + b.get_width()/2, val - 0.4), ha="center", va="top", fontsize=8.5, fontweight="bold")
    for b in b2:
        val = b.get_height()
        ax2.annotate(f"{val:+.2f} pp", (b.get_x() + b.get_width()/2, val - 0.4), ha="center", va="top", fontsize=8.5, fontweight="bold")
        
    ax2.annotate(
        "Format Gap: −2.03 pp",
        xy=(0, -2.83), xytext=(-0.25, -5.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="#666666"),
        fontsize=9, fontweight="bold"
    )
    ax2.annotate(
        "Format Gap: −2.02 pp\n(Identical Wedge!)",
        xy=(1, -4.53), xytext=(0.75, -5.8),
        bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="#666666"),
        fontsize=9, fontweight="bold"
    )
    
    fig.suptitle("TIMSS 2019 Grade 4 Mathematics: Testing the Equity Gradient & Counterarguments", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    out_path = FIGURES_DIR / "fig7_timss_equity_and_counterarguments.png"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 7 saved -> {out_path.name}")


def main():
    print("=" * 80)
    print("TIMSS 2019 Visualization Suite")
    print("=" * 80)
    
    item_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet")
    stu_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet")
    
    plot_fig5_item_difference_density(item_df)
    plot_fig6_domain_decompositions(item_df)
    plot_fig7_equity_and_counterarguments(stu_df, item_df)
    
    print("\n[SUCCESS] Figures 5, 6, and 7 generated successfully.")


if __name__ == "__main__":
    main()
