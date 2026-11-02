"""
Generate Figure 16: The Crowded Classroom Reality across Major Kansas City High Schools (SY 2023-24).

Panels:
1. Panel A: Flagship High School Section Size Leaderboard (Top 25 Largest High Schools in Metro)
2. Panel B: Student Exposure Thresholds (% of Students in Classes >= 20, >= 22, >= 24, >= 25, >= 28)
3. Panel C: The "Two Metros" Divide (Section Sizes by High School Enrollment Tier)
4. Panel D: District Averages across Major Suburban & Urban Districts (Shawnee Mission, Olathe, Blue Springs, Liberty, Park Hill, Blue Valley, NKC)
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import shutil

OBS_DIR = Path(__file__).resolve().parents[2]
DASHBOARD_DIR = OBS_DIR / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = DASHBOARD_DIR / "fig16_crowded_classroom_reality.png"

def plot_figure():
    crdc_long = OBS_DIR.parent / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"
    df_long = pd.read_csv(crdc_long, low_memory=False)
    
    v24 = df_long[(df_long["school_year"] == "2023-2024") & 
                  (df_long["num_classes"] > 0) & 
                  (df_long["num_enrolled"] > 0) & 
                  (df_long["is_operating"] == True)].copy()
    v24["size"] = v24["num_enrolled"] / v24["num_classes"]

    fig, axes = plt.subplots(2, 2, figsize=(17, 13.5), dpi=300)
    plt.subplots_adjust(top=0.91, bottom=0.07, left=0.08, right=0.96, hspace=0.62, wspace=0.30)

    # ----------------------------------------------------
    # PANEL A: Flagship High School Leaderboard (Prominent Comprehensive High Schools)
    # ----------------------------------------------------
    ax_a = axes[0, 0]
    
    # Core math courses
    core_math = v24[v24["course_code"].isin(["alg1", "geom", "alg2"])].copy()
    
    # Clean school names and calculate pooled core math size per school
    hs_agg = core_math.groupby(["nces_school_id", "school_name", "state", "enrollment_k12"]).agg(
        tot_classes=("num_classes", "sum"),
        tot_enrolled=("num_enrolled", "sum")
    ).reset_index()
    hs_agg["core_size"] = hs_agg["tot_enrolled"] / hs_agg["tot_classes"]
    
    # Filter out known CRDC reporting block anomalies (e.g. Fort Osage reporting 50/section)
    hs_clean = hs_agg[(hs_agg["enrollment_k12"] >= 1400) & (hs_agg["core_size"] < 35.0)].copy()
    
    # Select top 18 high schools ranked by core size
    top_hs = hs_clean.sort_values("core_size", ascending=True).tail(18).copy()
    
    def clean_name(row):
        n = row["school_name"].title()
        n = n.replace(" Sr High", " High").replace(" High School", " High")
        n = n.replace("Pub Sch", "").replace("R-Iv", "").replace("R-V", "")
        return f"{n} ({row['state']})"
        
    top_hs["display_name"] = top_hs.apply(clean_name, axis=1)
    
    bar_colors = ["#d73027" if s >= 25.0 else ("#fc8d59" if s >= 22.0 else "#4575b4") for s in top_hs["core_size"]]
    bars_a = ax_a.barh(top_hs["display_name"], top_hs["core_size"], color=bar_colors, alpha=0.88, height=0.68)
    
    for bar in bars_a:
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax_a.text(w + 0.3, y, f"{w:.1f}", va="center", ha="left", fontsize=8.5, fontweight="bold")
        
    ax_a.axvline(17.3, color="gray", linestyle="--", linewidth=1.2, label="Regional Unweighted Mean (17.3)")
    ax_a.axvline(25.0, color="#d73027", linestyle=":", linewidth=1.5, label="High-Density Threshold (25+)")
    ax_a.set_xlabel("Average Core Math Section Size (Algebra I, Geom, Alg II)", fontsize=9.5, fontweight="bold")
    ax_a.set_title("A. Core Math Section Sizes in Flagship High Schools (2023-24)", fontsize=11.5, fontweight="bold", pad=12)
    ax_a.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_a.set_xlim(0, 31)
    ax_a.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.9)

    # ----------------------------------------------------
    # PANEL B: Student Exposure: Mutually Exclusive Class-Size Bins (Sum to 100%)
    # ----------------------------------------------------
    ax_b = axes[0, 1]
    
    large_hs = v24[v24["enrollment_k12"] >= 1500].copy()
    
    def get_bucket(sz):
        if sz < 20: return "< 20"
        elif sz < 24: return "20–23"
        elif sz < 28: return "24–27"
        else: return "28+"
        
    large_hs["bucket"] = large_hs["size"].apply(get_bucket)
    
    categories = [
        ("Combined Core Math", large_hs[large_hs["course_code"].isin(["alg1", "geom", "alg2"])]),
        ("Algebra I", large_hs[large_hs["course_code"] == "alg1"]),
        ("Geometry", large_hs[large_hs["course_code"] == "geom"]),
        ("Algebra II", large_hs[large_hs["course_code"] == "alg2"]),
    ]
    
    bins = ["< 20", "20–23", "24–27", "28+"]
    bin_labels = [
        "< 20 students (Manageable)",
        "20–23 students (Moderate)",
        "24–27 students (Crowded)",
        "28+ students (Severe / Overcrowded)"
    ]
    bin_colors = ["#4575b4", "#fee090", "#f46d43", "#a50026"]
    
    y_labels = []
    plot_data = {b: [] for b in bins}
    
    for cat_name, cat_df in categories:
        tot = cat_df["num_enrolled"].sum()
        y_labels.append(f"{cat_name}\n(N={tot:,.0f} kids)")
        for b in bins:
            pct = cat_df[cat_df["bucket"] == b]["num_enrolled"].sum() / tot * 100
            plot_data[b].append(pct)
            
    y_pos = np.arange(len(categories))
    left = np.zeros(len(categories))
    
    legend_bars = []
    for b, label, color in zip(bins, bin_labels, bin_colors):
        widths = np.array(plot_data[b])
        bars = ax_b.barh(y_pos, widths, left=left, height=0.55, color=color, label=label, edgecolor="white", linewidth=1.2, alpha=0.92)
        legend_bars.append(bars[0])
        
        for i, (w, l) in enumerate(zip(widths, left)):
            if w >= 6.0:
                txt_color = "white" if b in ["< 20", "28+"] else "black"
                ax_b.text(l + w / 2, y_pos[i], f"{w:.1f}%", ha="center", va="center", fontsize=8.5, fontweight="bold", color=txt_color)
            elif w >= 5.0:
                txt_color = "white" if b in ["< 20", "28+"] else "black"
                ax_b.text(l + w / 2, y_pos[i], f"{w:.0f}%", ha="center", va="center", fontsize=7.5, fontweight="bold", color=txt_color)
        left += widths
        
    ax_b.set_yticks(y_pos)
    ax_b.set_yticklabels(y_labels, fontsize=9, fontweight="bold")
    ax_b.invert_yaxis()
    ax_b.set_xlim(0, 100)
    ax_b.xaxis.set_major_formatter(ticker.PercentFormatter())
    ax_b.set_xlabel("% of Enrolled Students in Large High Schools (≥1,500)", fontsize=9.5, fontweight="bold")
    ax_b.set_title("B. Student Exposure: Mutually Exclusive Class-Size Bins (Sum to 100%)", fontsize=11.5, fontweight="bold", pad=12)
    ax_b.grid(True, linestyle="--", alpha=0.35, axis="x")
    
    # Place legend as a compact single row in the vertical gap between Panel B and Panel D
    fig.legend(
        handles=legend_bars,
        labels=bin_labels,
        title="Class Size Slices (Sum to 100% per course):",
        title_fontsize=8.5,
        loc="center",
        bbox_to_anchor=(0.77, 0.495),
        ncol=4,
        fontsize=7.8,
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc"
    )

    # ----------------------------------------------------
    # PANEL C: The "Two Metros" Divide by School Enrollment Tier
    # ----------------------------------------------------
    ax_c = axes[1, 0]
    
    def get_tier(enr):
        if enr >= 1500: return "Large (>=1,500)"
        elif enr >= 1000: return "Mid-Large (1,000-1,499)"
        elif enr >= 500: return "Medium (500-999)"
        else: return "Small (<500)"
        
    v24["tier"] = v24["enrollment_k12"].apply(get_tier)
    tier_order = ["Large (>=1,500)", "Mid-Large (1,000-1,499)", "Medium (500-999)", "Small (<500)"]
    
    tier_core = v24[v24["course_code"].isin(["alg1", "geom", "alg2"])].copy()
    tier_stats = []
    for t in tier_order:
        sub = tier_core[tier_core["tier"] == t]
        pooled_sz = sub["num_enrolled"].sum() / sub["num_classes"].sum()
        p25 = sub["size"].quantile(0.25)
        p50 = sub["size"].median()
        p75 = sub["size"].quantile(0.75)
        p90 = sub["size"].quantile(0.90)
        n_schools = sub["nces_school_id"].nunique()
        tot_students = sub["num_enrolled"].sum()
        tier_stats.append({
            "tier": f"{t}\n(N={n_schools} schools, {tot_students:,.0f} kids)",
            "pooled": pooled_sz, "p25": p25, "p50": p50, "p75": p75, "p90": p90
        })
    df_t = pd.DataFrame(tier_stats)
    
    y_pos_c = np.arange(len(df_t))
    ax_c.barh(y_pos_c, df_t["pooled"], height=0.55, color=["#e6550d", "#fdae6b", "#9ecae1", "#3182bd"], alpha=0.88)
    
    xerr_low = df_t["pooled"] - df_t["p25"]
    xerr_high = df_t["p75"] - df_t["pooled"]
    ax_c.errorbar(df_t["pooled"], y_pos_c, xerr=[xerr_low, xerr_high], fmt="none", color="black", capsize=5, linewidth=1.5)
    
    for i, (_, r) in enumerate(df_t.iterrows()):
        txt_x = max(r["p75"], r["pooled"]) + 0.6
        ax_c.text(txt_x, i, f"Pooled: {r['pooled']:.1f}\nIQR: {r['p25']:.1f}–{r['p75']:.1f} | P90: {r['p90']:.1f}", va="center", ha="left", fontsize=7.8, fontweight="bold")
        
    ax_c.set_yticks(y_pos_c)
    ax_c.set_yticklabels(df_t["tier"], fontsize=9)
    ax_c.set_xlabel("Pooled Section Size & Interquartile Spread (Students / Class)", fontsize=9.5, fontweight="bold")
    ax_c.set_title("C. The 'Two Metros' Scale Polarization: Core Math (2023-24)", fontsize=11.5, fontweight="bold", pad=12)
    ax_c.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_c.set_xlim(0, 34)
    ax_c.invert_yaxis()

    # ----------------------------------------------------
    # PANEL D: Major Suburban & Urban District Core Math Averages
    # ----------------------------------------------------
    ax_d = axes[1, 1]
    
    major_districts = [
        "Shawnee Mission Pub Sch", "Olathe", "BLUE SPRINGS R-IV", "LIBERTY 53",
        "Blue Valley", "PARK HILL", "GRAIN VALLEY R-V", "NORTH KANSAS CITY 74",
        "LEE'S SUMMIT R-VII", "Kansas City"
    ]
    
    dist_map_name = {
        "Shawnee Mission Pub Sch": "Shawnee Mission (5 HS)",
        "Olathe": "Olathe (5 HS)",
        "BLUE SPRINGS R-IV": "Blue Springs (2 HS)",
        "LIBERTY 53": "Liberty (2 HS)",
        "Blue Valley": "Blue Valley (5 HS)",
        "PARK HILL": "Park Hill (2 HS)",
        "GRAIN VALLEY R-V": "Grain Valley (1 HS)",
        "NORTH KANSAS CITY 74": "North Kansas City (4 HS)",
        "LEE'S SUMMIT R-VII": "Lee's Summit (3 HS)",
        "Kansas City": "Kansas City, KS (5 HS)"
    }
    
    dist_data = []
    for d in major_districts:
        sub_d = v24[(v24["district_name"] == d) & (v24["course_code"].isin(["alg1", "geom", "alg2"])) & (v24["school_level"] == "High")]
        if len(sub_d) == 0:
            continue
        tot_c = sub_d["num_classes"].sum()
        tot_e = sub_d["num_enrolled"].sum()
        pooled = tot_e / tot_c if tot_c > 0 else np.nan
        dist_data.append({"district": dist_map_name.get(d, d), "pooled": pooled})
        
    df_d = pd.DataFrame(dist_data).sort_values("pooled", ascending=True)
    
    bar_colors_d = ["#d73027" if s >= 24.5 else ("#fc8d59" if s >= 22.0 else "#4575b4") for s in df_d["pooled"]]
    bars_d = ax_d.barh(df_d["district"], df_d["pooled"], color=bar_colors_d, alpha=0.88, height=0.65)
    
    for bar in bars_d:
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax_d.text(w + 0.3, y, f"{w:.1f}", va="center", ha="left", fontsize=9, fontweight="bold")
        
    ax_d.axvline(17.3, color="gray", linestyle="--", linewidth=1.2, label="Regional Unweighted Average (17.3)")
    ax_d.set_xlabel("District High School Core Math Section Size (Students / Class)", fontsize=9.5, fontweight="bold")
    ax_d.set_title("D. Major District High School Core Math Averages (2023-24)", fontsize=11.5, fontweight="bold", pad=10)
    ax_d.grid(True, linestyle="--", alpha=0.4, axis="x")
    ax_d.set_xlim(0, 30)
    ax_d.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white")

    plt.suptitle("The Classroom Density Reality across Kansas City High Schools (SY 2023-24)\nWhy Simple Averages Conceal 25 to 28+ Student Classrooms in Flagship Schools", fontsize=14, fontweight="bold", y=0.98)
    
    fig.subplots_adjust(top=0.91, bottom=0.07, left=0.10, right=0.96, hspace=0.32, wspace=0.26)
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 16 to {OUT_PNG.relative_to(OBS_DIR)}")

    # Copy to artifacts directory
    art_dir = Path.home() / ".gemini" / "antigravity" / "brain" / "341419bd-5669-4622-8d51-d6eecec301ff"
    if art_dir.exists():
        shutil.copy(OUT_PNG, art_dir / "fig16_crowded_classroom_reality.png")
        print("Copied Figure 16 to artifacts directory.")

if __name__ == "__main__":
    plot_figure()
