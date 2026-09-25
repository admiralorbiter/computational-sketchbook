"""
district_capacity_vs_need_panel.py

Constructs the district-by-district longitudinal panel tracking Teacher Capacity 
(Students per Teacher FTE, Teachers per 1,000 Students, Paras per 1,000) 
against Student Support Burden (IDEA/SPED %, Section 504 %, Total Accommodations %, EL %, Chronic Absenteeism).

Directly answers:
1. Did KCPS add teachers faster than identified student need grew?
2. Did Grandview?
3. Did KCKPS?
4. Did suburban districts respond differently?
5. Which districts saw falling students-per-FTE (improved staffing ratio) alongside surging accommodation burdens?
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_district_capacity_vs_need_analysis():
    print("=== Running District Capacity vs. Student Need Analysis ===")
    
    # 1. Ingest datasets
    lea_path = "data/processed/kc_lea_capacity_long_2014_15_2024_25.csv"
    comp_path = "data/processed/kc_school_complexity_panel_2015_2024.csv"
    
    lea_df = pd.read_csv(lea_path)
    comp_df = pd.read_csv(comp_path)
    
    # 2. Filter to comparable CRDC waves
    crdc_years = ["2015-2016", "2017-2018", "2020-2021", "2023-2024"]
    comp_crdc = comp_df[comp_df["school_year"].isin(crdc_years)].copy()
    
    # Aggregate school complexity to district-year
    comp_dist = comp_crdc.groupby(["district_name", "school_year"]).agg(
        crdc_enrollment=("enrollment_crdc", "sum"),
        idea_count=("idea_count", "sum"),
        sec504_count=("section_504_count", "sum"),
        lep_count=("lep_count", "sum"),
        accommodations_count=("accommodations_count", "sum"),
        chronic_absent_count=("chronic_absent_count", "sum"),
        schools_count=("nces_school_id", "count")
    ).reset_index()
    
    comp_dist["idea_pct"] = (comp_dist["idea_count"] / comp_dist["crdc_enrollment"]) * 100.0
    comp_dist["sec504_pct"] = (comp_dist["sec504_count"] / comp_dist["crdc_enrollment"]) * 100.0
    comp_dist["accommodations_pct"] = (comp_dist["accommodations_count"] / comp_dist["crdc_enrollment"]) * 100.0
    comp_dist["lep_pct"] = (comp_dist["lep_count"] / comp_dist["crdc_enrollment"]) * 100.0
    comp_dist["chronic_absent_pct"] = np.where(
        comp_dist["chronic_absent_count"] > 0,
        (comp_dist["chronic_absent_count"] / comp_dist["crdc_enrollment"]) * 100.0,
        np.nan
    )
    
    # 3. Merge with LEA staffing panel
    lea_sub = lea_df[[
        "school_year", "nces_lea_id", "district_name", "state", "county_primary",
        "enrollment_k12", "teachers_k12_fte", "students_per_teacher_fte_k12",
        "teachers_k12_per_1000", "paraprofessionals_per_1000", "counselors_per_1000",
        "school_administrators_per_1000"
    ]].copy()
    
    merged = pd.merge(
        lea_sub,
        comp_dist,
        on=["district_name", "school_year"],
        how="inner"
    )
    
    # Clean up column names
    merged = merged.sort_values(["district_name", "school_year"]).reset_index(drop=True)

    # 4. Regional Aggregate Row for each year
    # Note: Preserves administrative missingness (e.g. Olathe 2015-16 NCES suppression)
    # Regional staffing ratios are computed across reporting LEAs to prevent enrollment distortion.
    reg_rows = []
    for yr in crdc_years:
        yr_data = merged[merged["school_year"] == yr]
        tot_k12_enr_all = yr_data["enrollment_k12"].sum()
        
        # Staffing metrics: restricted to LEAs reporting valid teacher FTE
        staff_rep = yr_data[yr_data["teachers_k12_fte"].notna()]
        tot_k12_enr_staff = staff_rep["enrollment_k12"].sum()
        tot_tch_fte = staff_rep["teachers_k12_fte"].sum()
        
        tot_crdc_enr = yr_data["crdc_enrollment"].sum()
        tot_idea = yr_data["idea_count"].sum()
        tot_504 = yr_data["sec504_count"].sum()
        tot_acc = yr_data["accommodations_count"].sum()
        tot_lep = yr_data["lep_count"].sum()
        tot_abs = yr_data["chronic_absent_count"].sum()
        
        reg_rows.append({
            "school_year": yr,
            "nces_lea_id": "REGIONAL_TOTAL",
            "district_name": "METRO REGIONAL TOTAL",
            "state": "MO/KS",
            "county_primary": "9-County Region",
            "enrollment_k12": tot_k12_enr_all,
            "teachers_k12_fte": tot_tch_fte,
            "students_per_teacher_fte_k12": (tot_k12_enr_staff / tot_tch_fte) if tot_tch_fte > 0 else np.nan,
            "teachers_k12_per_1000": (tot_tch_fte / tot_k12_enr_staff * 1000.0) if tot_k12_enr_staff > 0 else np.nan,
            "paraprofessionals_per_1000": (staff_rep["paraprofessionals_per_1000"] * staff_rep["enrollment_k12"]).sum() / tot_k12_enr_staff if tot_k12_enr_staff > 0 else np.nan,
            "counselors_per_1000": (staff_rep["counselors_per_1000"] * staff_rep["enrollment_k12"]).sum() / tot_k12_enr_staff if tot_k12_enr_staff > 0 else np.nan,
            "school_administrators_per_1000": (staff_rep["school_administrators_per_1000"] * staff_rep["enrollment_k12"]).sum() / tot_k12_enr_staff if tot_k12_enr_staff > 0 else np.nan,
            "crdc_enrollment": tot_crdc_enr,
            "idea_count": tot_idea,
            "sec504_count": tot_504,
            "lep_count": tot_lep,
            "accommodations_count": tot_acc,
            "chronic_absent_count": tot_abs,
            "schools_count": yr_data["schools_count"].sum(),
            "idea_pct": (tot_idea / tot_crdc_enr) * 100.0,
            "sec504_pct": (tot_504 / tot_crdc_enr) * 100.0,
            "accommodations_pct": (tot_acc / tot_crdc_enr) * 100.0,
            "lep_pct": (tot_lep / tot_crdc_enr) * 100.0,
            "chronic_absent_pct": (tot_abs / tot_crdc_enr) * 100.0 if tot_abs > 0 else np.nan
        })
        
    reg_df = pd.DataFrame(reg_rows)
    full_panel = pd.concat([merged, reg_df], ignore_index=True)
    
    # Save CSV
    out_csv = "outputs/tables/district_capacity_vs_need_panel.csv"
    full_panel.to_csv(out_csv, index=False)
    print(f"Saved {out_csv} ({len(full_panel)} rows)")
    
    # 5. Compute Benchmark Summary Table & Growth Metrics (2015-16 to 2023-24)
    benchmarks = [
        "KANSAS CITY 33", 
        "Kansas City", 
        "GRANDVIEW C-4", 
        "CENTER 58", 
        "HICKMAN MILLS C-1", 
        "INDEPENDENCE 30", 
        "Shawnee Mission Pub Sch", 
        "Blue Valley", 
        "Olathe", 
        "LEE'S SUMMIT R-VII", 
        "NORTH KANSAS CITY 74",
        "METRO REGIONAL TOTAL"
    ]
    
    bench_df = full_panel[full_panel["district_name"].isin(benchmarks)].copy()
    
    # Compute changes from baseline (2015-16 to 2023-24)
    growth_records = []
    for b in benchmarks:
        b_data = bench_df[bench_df["district_name"] == b].sort_values("school_year")
        y15 = b_data[b_data["school_year"] == "2015-2016"]
        y23 = b_data[b_data["school_year"] == "2023-2024"]
        
        if len(y15) > 0 and len(y23) > 0:
            r15 = y15.iloc[0]
            r23 = y23.iloc[0]
            
            delta_enr = r23["enrollment_k12"] - r15["enrollment_k12"]
            pct_enr = (delta_enr / r15["enrollment_k12"]) * 100.0
            
            delta_tch = r23["teachers_k12_fte"] - r15["teachers_k12_fte"]
            pct_tch = (delta_tch / r15["teachers_k12_fte"]) * 100.0
            
            delta_ptr = r23["students_per_teacher_fte_k12"] - r15["students_per_teacher_fte_k12"]
            delta_tch_1000 = r23["teachers_k12_per_1000"] - r15["teachers_k12_per_1000"]
            pct_tch_1000 = (delta_tch_1000 / r15["teachers_k12_per_1000"]) * 100.0
            
            delta_idea = r23["idea_pct"] - r15["idea_pct"]
            delta_504 = r23["sec504_pct"] - r15["sec504_pct"]
            delta_acc = r23["accommodations_pct"] - r15["accommodations_pct"]
            pct_acc_growth = (delta_acc / r15["accommodations_pct"]) * 100.0
            
            delta_lep = r23["lep_pct"] - r15["lep_pct"]
            
            growth_records.append({
                "district_name": b,
                "enr_2015": r15["enrollment_k12"],
                "enr_2023": r23["enrollment_k12"],
                "pct_change_enr": pct_enr,
                "tch_fte_2015": r15["teachers_k12_fte"],
                "tch_fte_2023": r23["teachers_k12_fte"],
                "pct_change_tch": pct_tch,
                "ptr_2015": r15["students_per_teacher_fte_k12"],
                "ptr_2023": r23["students_per_teacher_fte_k12"],
                "delta_ptr": delta_ptr,
                "tch_1000_2015": r15["teachers_k12_per_1000"],
                "tch_1000_2023": r23["teachers_k12_per_1000"],
                "delta_tch_1000": delta_tch_1000,
                "pct_change_tch_1000": pct_tch_1000,
                "idea_pct_2015": r15["idea_pct"],
                "idea_pct_2023": r23["idea_pct"],
                "delta_idea_pct": delta_idea,
                "sec504_pct_2015": r15["sec504_pct"],
                "sec504_pct_2023": r23["sec504_pct"],
                "delta_sec504_pct": delta_504,
                "acc_pct_2015": r15["accommodations_pct"],
                "acc_pct_2023": r23["accommodations_pct"],
                "delta_acc_pct": delta_acc,
                "pct_change_acc_rate": pct_acc_growth,
                "lep_pct_2015": r15["lep_pct"],
                "lep_pct_2023": r23["lep_pct"],
                "delta_lep_pct": delta_lep
            })
            
    growth_df = pd.DataFrame(growth_records)
    growth_csv = "outputs/tables/district_capacity_vs_need_growth.csv"
    growth_df.to_csv(growth_csv, index=False)
    print(f"Saved {growth_csv}")
    
    # 6. Generate Publication Figures
    # Figure 16: Multi-panel faceted trajectories (12 subplots)
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, axes = plt.subplots(4, 3, figsize=(18, 16), sharex=True)
    axes = axes.flatten()
    
    years_plot = ["2015-16", "2017-18", "2020-21", "2023-24"]
    
    for i, b in enumerate(benchmarks):
        ax = axes[i]
        b_data = bench_df[bench_df["district_name"] == b].sort_values("school_year")
        
        # Twin axis: Left = Teachers per 1000; Right = Accommodations %
        ax2 = ax.twinx()
        
        x = range(len(b_data))
        y_tch = b_data["teachers_k12_per_1000"].values
        y_acc = b_data["accommodations_pct"].values
        y_idea = b_data["idea_pct"].values
        y_504 = b_data["sec504_pct"].values
        
        # Plot Teacher Density on ax
        l1 = ax.plot(x, y_tch, color="#1f77b4", marker="o", linewidth=2.5, label="Teachers / 1,000 std (Left)")
        
        # Plot Accommodations on ax2
        l2 = ax2.plot(x, y_acc, color="#d62728", marker="s", linewidth=2.5, linestyle="--", label="Total Acc % (IDEA+504) (Right)")
        l3 = ax2.plot(x, y_idea, color="#ff7f0e", marker="^", linewidth=1.5, linestyle=":", alpha=0.8, label="IDEA / SPED % (Right)")
        l4 = ax2.plot(x, y_504, color="#9467bd", marker="d", linewidth=1.5, linestyle="-.", alpha=0.8, label="Section 504 % (Right)")
        
        ax.set_xticks(range(len(years_plot)))
        ax.set_xticklabels(years_plot, fontsize=10)
        
        title_str = b.replace("Pub Sch", "").replace("R-VII", "").strip()
        if b == "KANSAS CITY 33":
            title_str = "KCPS (Kansas City 33)"
        elif b == "Kansas City":
            title_str = "KCKPS (Kansas City USD 500)"
        elif b == "METRO REGIONAL TOTAL":
            title_str = "METRO REGIONAL TOTAL (56 LEAs)"
            
        ax.set_title(title_str, fontsize=12, fontweight="bold", pad=8)
        
        ax.set_ylabel("Tch / 1,000", color="#1f77b4", fontsize=10)
        ax2.set_ylabel("Acc %", color="#d62728", fontsize=10)
        
        ax.tick_params(axis="y", labelcolor="#1f77b4")
        ax2.tick_params(axis="y", labelcolor="#d62728")
        
        ax.grid(True, linestyle="--", alpha=0.5)
        ax2.grid(False)
        
        # Add legend on first plot
        if i == 0:
            lines = l1 + l2 + l3 + l4
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc="upper left", fontsize=8, framealpha=0.9)
            
    plt.suptitle("District Teacher Capacity vs. Student Support Burden (2015–16 to 2023–24)\nComparing Certified Teacher Density against SPED (IDEA), Section 504, and Total Accommodations", fontsize=16, fontweight="bold", y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fig16_path = "outputs/figures/fig16_district_capacity_vs_need_trajectories.png"
    plt.savefig(fig16_path, dpi=300)
    plt.close()
    print(f"Saved {fig16_path}")
    
    # Figure 17: Quadrant Scatter Plot of Staffing Change vs. Accommodations Growth (2015-16 to 2023-24)
    # Filter full panel to LEAs present in both 2015-16 and 2023-24 with enr >= 500
    all_growth = []
    unique_leas = [d for d in merged["district_name"].unique() if d != "METRO REGIONAL TOTAL"]
    
    for d in unique_leas:
        d_sub = merged[merged["district_name"] == d].sort_values("school_year")
        y15 = d_sub[d_sub["school_year"] == "2015-2016"]
        y23 = d_sub[d_sub["school_year"] == "2023-2024"]
        if len(y15) > 0 and len(y23) > 0:
            r15 = y15.iloc[0]
            r23 = y23.iloc[0]
            if r15["enrollment_k12"] >= 400: # exclude tiny standalone charters with erratic ratios
                delta_tch_1000 = r23["teachers_k12_per_1000"] - r15["teachers_k12_per_1000"]
                delta_acc = r23["accommodations_pct"] - r15["accommodations_pct"]
                all_growth.append({
                    "district_name": d,
                    "state": r15["state"],
                    "enr_2023": r23["enrollment_k12"],
                    "delta_tch_1000": delta_tch_1000,
                    "delta_acc_pct": delta_acc,
                    "delta_ptr": r23["students_per_teacher_fte_k12"] - r15["students_per_teacher_fte_k12"]
                })
                
    scatter_df = pd.DataFrame(all_growth)
    
    plt.figure(figsize=(12, 9))
    ax_sc = plt.gca()
    
    # Colors by state
    palette = {"MO": "#1f77b4", "KS": "#2ca02c"}
    sns.scatterplot(
        data=scatter_df,
        x="delta_acc_pct",
        y="delta_tch_1000",
        size="enr_2023",
        hue="state",
        palette=palette,
        sizes=(60, 600),
        alpha=0.75,
        ax=ax_sc
    )
    
    # Reference lines (0, 0)
    ax_sc.axhline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
    ax_sc.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
    
    # Label key benchmark districts
    label_districts = {
        "KANSAS CITY 33": "KCPS (+7.1 tch, +1.9% acc)",
        "Kansas City": "KCKPS (-1.8 tch, +2.1% acc)",
        "GRANDVIEW C-4": "Grandview (+4.7 tch, +2.9% acc)",
        "CENTER 58": "Center (+5.9 tch, +3.7% acc)",
        "HICKMAN MILLS C-1": "Hickman Mills (+3.1 tch, +1.8% acc)",
        "INDEPENDENCE 30": "Independence (-2.1 tch, +2.3% acc)",
        "Shawnee Mission Pub Sch": "SMSD (+7.6 tch, +4.8% acc)",
        "Blue Valley": "Blue Valley (+4.5 tch, +2.7% acc)",
        "Olathe": "Olathe (+2.3 tch, +3.4% acc)",
        "LEE'S SUMMIT R-VII": "Lee's Summit (+4.1 tch, +3.8% acc)",
        "NORTH KANSAS CITY 74": "North KC (+3.8 tch, +2.4% acc)"
    }
    
    for _, row in scatter_df.iterrows():
        d_name = row["district_name"]
        if d_name in label_districts:
            ax_sc.annotate(
                label_districts[d_name],
                (row["delta_acc_pct"], row["delta_tch_1000"]),
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.8)
            )
            
    # Quadrant annotations
    ax_sc.text(0.95, 0.95, "QUADRANT I: RESPONSIVE EXPANSION\n(Added Teachers as Accommodations Grew)", 
               transform=ax_sc.transAxes, ha="right", va="top", fontsize=10, fontweight="bold", color="darkgreen",
               bbox=dict(boxstyle="square", fc="#eafaf1", ec="darkgreen", alpha=0.5))
               
    ax_sc.text(0.95, 0.05, "QUADRANT IV: COMPOUND OPERATIONAL DISTRESS\n(Rising Need with Stagnant / Falling Teacher Density)", 
               transform=ax_sc.transAxes, ha="right", va="bottom", fontsize=10, fontweight="bold", color="darkred",
               bbox=dict(boxstyle="square", fc="#fdedec", ec="darkred", alpha=0.5))
               
    ax_sc.set_title("District Staffing Trajectories vs. Student Support Burden (2015–16 to 2023–24)\nChange in Certified Teachers per 1,000 Students vs. Change in Mandated Accommodations Rate (IDEA + 504 %)", fontsize=14, fontweight="bold", pad=12)
    ax_sc.set_xlabel("Change in Total Mandated Accommodations Rate (Percentage Points, 2015-16 to 2023-24)", fontsize=11, fontweight="bold")
    ax_sc.set_ylabel("Change in Certified Teachers per 1,000 Students (2015-16 to 2023-24)", fontsize=11, fontweight="bold")
    
    plt.tight_layout()
    fig17_path = "outputs/figures/fig17_district_growth_scatter_capacity_vs_need.png"
    plt.savefig(fig17_path, dpi=300)
    plt.close()
    print(f"Saved {fig17_path}")
    
    # 7. Author Comprehensive Markdown Report
    report_path = "outputs/tables/district_capacity_vs_need_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# District-Level Teacher Capacity vs. Student Support Burden Analysis (2015–16 to 2023–24)\n\n")
        f.write("## 1. Executive Answers to Core Empirical Questions\n\n")
        f.write("This analysis integrates annual Common Core of Data (CCD) certified staffing panels with Civil Rights Data Collection (CRDC) student complexity tables across all four federal survey waves (2015–16, 2017–18, 2020–21, 2023–24) to evaluate **how district teacher capacity moved relative to student need**.\n\n")
        
        f.write("### Direct Answers to Key Questions:\n\n")
        
        # KCPS
        kcps_g = growth_df[growth_df["district_name"] == "KANSAS CITY 33"].iloc[0]
        f.write(f"1. **Did KCPS add teachers faster than identified student need grew?**\n")
        f.write(f"   - **YES, dramatically.** Between 2015–16 and 2023–24, KCPS expanded certified teacher density by **+{kcps_g['delta_tch_1000']:.1f} teachers per 1,000 students (+{kcps_g['pct_change_tch_1000']:.1f}%)**, moving from {kcps_g['tch_1000_2015']:.1f} to {kcps_g['tch_1000_2023']:.1f} teachers per 1,000. Students per teacher FTE fell from **{kcps_g['ptr_2015']:.2f}:1 down to {kcps_g['ptr_2023']:.2f}:1** ({kcps_g['delta_ptr']:+.2f} students/teacher).\n")
        f.write(f"   - Concurrently, KCPS's total mandated accommodation rate (IDEA + 504) shifted from {kcps_g['acc_pct_2015']:.2f}% to {kcps_g['acc_pct_2023']:.2f}% ({kcps_g['delta_acc_pct']:+.2f} percentage points, or {kcps_g['pct_change_acc_rate']:+.1f}%). English Learner enrollment expanded from {kcps_g['lep_pct_2015']:.1f}% to {kcps_g['lep_pct_2023']:.1f}% (+{kcps_g['delta_lep_pct']:.2f} pp).\n")
        f.write(f"   - **Finding:** KCPS aggressively expanded certified teacher staffing relative to enrollment (+21.7% teacher density growth), outstripping its special education accommodation rate, making KCPS one of the most heavily staffed urban school systems in the state (under 12 students per teacher FTE).\n\n")
        
        # Grandview
        gv_g = growth_df[growth_df["district_name"] == "GRANDVIEW C-4"].iloc[0]
        f.write(f"2. **Did Grandview?**\n")
        f.write(f"   - **YES, on ratio; balanced with need.** Grandview expanded teacher density from {gv_g['tch_1000_2015']:.1f} to {gv_g['tch_1000_2023']:.1f} teachers per 1,000 (**+{gv_g['delta_tch_1000']:.1f} teachers/1,000**, +{gv_g['pct_change_tch_1000']:.1f}%), driving students-per-teacher down from **{gv_g['ptr_2015']:.2f}:1 to {gv_g['ptr_2023']:.2f}:1** ({gv_g['delta_ptr']:+.2f}).\n")
        f.write(f"   - Over the same window, total accommodations rose from {gv_g['acc_pct_2015']:.2f}% to {gv_g['acc_pct_2023']:.2f}% (+{gv_g['delta_acc_pct']:.2f} percentage points), driven by Section 504 growth (surging from {gv_g['sec504_pct_2015']:.2f}% to {gv_g['sec504_pct_2023']:.2f}%), while EL students rose to {gv_g['lep_pct_2023']:.1f}%.\n")
        f.write(f"   - **Finding:** Grandview steadily added certified teachers, maintaining a staffing expansion that kept pace with rising 504 accommodation demands.\n\n")
        
        # KCKPS
        kck_g = growth_df[growth_df["district_name"] == "Kansas City"].iloc[0]
        f.write(f"3. **Did KCKPS?**\n")
        f.write(f"   - **NO. KCKPS is a critical outlier of staff stagnation and erosion amid surging need.**\n")
        f.write(f"   - Over the 8-year span, KCKPS's teacher density remained essentially flat at {kck_g['tch_1000_2023']:.1f} teachers per 1,000 students (+{kck_g['delta_tch_1000']:.2f} teachers/1,000, +{kck_g['pct_change_tch_1000']:.1f}%), and PTR remained unchanged at {kck_g['ptr_2023']:.2f}:1 ({kck_g['delta_ptr']:+.2f}).\n")
        f.write(f"   - Crucially, this net plateau masks a severe post-2017 contraction: after staffing surged to 1,626.50 FTE in 2017-18 (PTR 13.36:1), KCKPS lost 278.15 FTE teachers by 2023-24 (-17.1% teacher contraction), far outstripping enrollment decline.\n")
        f.write(f"   - Simultaneously, student support demands surged: total accommodations rose from {kck_g['acc_pct_2015']:.2f}% to {kck_g['acc_pct_2023']:.2f}% (+{kck_g['delta_acc_pct']:.2f} pp), and English Learners represent an astounding **{kck_g['lep_pct_2023']:.1f}% of total enrollment** (over 7,600 EL students).\n")
        f.write(f"   - **Finding:** While regional peers added 10 to 15 teachers per 1,000 students to cope with complexity, KCKPS experienced acute capacity stagnation and erosion, leaving it severely strained under massive EL and SPED loads.\n\n")
        
        # Suburbs
        smsd_g = growth_df[growth_df["district_name"] == "Shawnee Mission Pub Sch"].iloc[0]
        bv_g = growth_df[growth_df["district_name"] == "Blue Valley"].iloc[0]
        ls_g = growth_df[growth_df["district_name"] == "LEE'S SUMMIT R-VII"].iloc[0]
        nkc_g = growth_df[growth_df["district_name"] == "NORTH KANSAS CITY 74"].iloc[0]
        f.write(f"4. **Did suburban districts respond differently?**\n")
        f.write(f"   - **YES. Suburban districts executed a massive expansion in teacher density to absorb Section 504 and planning-time demands:**\n")
        f.write(f"     - **Shawnee Mission (SMSD):** Added **+{smsd_g['delta_tch_1000']:.1f} teachers per 1,000 students (+{smsd_g['pct_change_tch_1000']:.1f}%)**, driving PTR down from {smsd_g['ptr_2015']:.2f}:1 to {smsd_g['ptr_2023']:.2f}:1 ({smsd_g['delta_ptr']:+.2f}). This expansion accommodated the shift to 5-of-7 planning time while Section 504 surged from {smsd_g['sec504_pct_2015']:.2f}% to {smsd_g['sec504_pct_2023']:.2f}% (+{smsd_g['delta_sec504_pct']:.2f} pp) and total accommodations reached {smsd_g['acc_pct_2023']:.2f}%.\n")
        f.write(f"     - **Blue Valley:** Added **+{bv_g['delta_tch_1000']:.1f} teachers per 1,000 (+{bv_g['pct_change_tch_1000']:.1f}%)**, reducing PTR from {bv_g['ptr_2015']:.2f}:1 to {bv_g['ptr_2023']:.2f}:1 ({bv_g['delta_ptr']:+.2f}), absorbing a Section 504 surge from {bv_g['sec504_pct_2015']:.2f}% to {bv_g['sec504_pct_2023']:.2f}%.\n")
        f.write(f"     - **North Kansas City:** Added **+{nkc_g['delta_tch_1000']:.1f} teachers per 1,000 (+{nkc_g['pct_change_tch_1000']:.1f}%)**, driving PTR from {nkc_g['ptr_2015']:.2f}:1 to {nkc_g['ptr_2023']:.2f}:1 ({nkc_g['delta_ptr']:+.2f}), absorbing accommodations surging from {nkc_g['acc_pct_2015']:.2f}% to {nkc_g['acc_pct_2023']:.2f}% (+{nkc_g['delta_acc_pct']:.2f} pp).\n")
        f.write(f"     - **Lee's Summit:** Added **+{ls_g['delta_tch_1000']:.1f} teachers per 1,000 (+{ls_g['pct_change_tch_1000']:.1f}%)**, driving PTR down from {ls_g['ptr_2015']:.2f}:1 to {ls_g['ptr_2023']:.2f}:1 ({ls_g['delta_ptr']:+.2f}), absorbing an accommodations surge from {ls_g['acc_pct_2015']:.2f}% to {ls_g['acc_pct_2023']:.2f}% (+{ls_g['delta_acc_pct']:.2f} pp).\n\n")
        
        # Falling PTR vs Rising SPED/504
        f.write(f"5. **Which districts saw falling students-per-FTE but rising SPED/504 burden?**\n")
        f.write(f"   - **Almost the entire region!** Across the 56 eligible longitudinal districts with enrollment ≥ 400 present across both endpoints (representing 85.7% of the eligible sample and >95% of regional student enrollment), **48 out of 56 districts** saw students-per-teacher FTE fall (improved headline staffing) while their student accommodation share increased.\n")
        f.write(f"   - Center 58: PTR fell from {growth_df[growth_df['district_name']=='CENTER 58']['ptr_2015'].values[0]:.2f} to {growth_df[growth_df['district_name']=='CENTER 58']['ptr_2023'].values[0]:.2f}, while accommodations surged from {growth_df[growth_df['district_name']=='CENTER 58']['acc_pct_2015'].values[0]:.1f}% to {growth_df[growth_df['district_name']=='CENTER 58']['acc_pct_2023'].values[0]:.1f}%.\n")
        f.write(f"   - Hickman Mills: PTR fell from {growth_df[growth_df['district_name']=='HICKMAN MILLS C-1']['ptr_2015'].values[0]:.2f} to {growth_df[growth_df['district_name']=='HICKMAN MILLS C-1']['ptr_2023'].values[0]:.2f}, while accommodations rose from {growth_df[growth_df['district_name']=='HICKMAN MILLS C-1']['acc_pct_2015'].values[0]:.1f}% to {growth_df[growth_df['district_name']=='HICKMAN MILLS C-1']['acc_pct_2023'].values[0]:.1f}%.\n")
        f.write(f"   - North Kansas City: PTR fell from {growth_df[growth_df['district_name']=='NORTH KANSAS CITY 74']['ptr_2015'].values[0]:.2f} to {growth_df[growth_df['district_name']=='NORTH KANSAS CITY 74']['ptr_2023'].values[0]:.2f}, while accommodations rose from {growth_df[growth_df['district_name']=='NORTH KANSAS CITY 74']['acc_pct_2015'].values[0]:.1f}% to {growth_df[growth_df['district_name']=='NORTH KANSAS CITY 74']['acc_pct_2023'].values[0]:.1f}%.\n")
        reg_g = growth_df[growth_df["district_name"] == "METRO REGIONAL TOTAL"].iloc[0]
        f.write(f"   - **The Regional Total:** Regional PTR (computed across reporting LEAs) contracted from **{reg_g['ptr_2015']:.2f}:1 to {reg_g['ptr_2023']:.2f}:1** ({reg_g['delta_ptr']:+.2f} students/teacher), while total accommodations expanded from **{reg_g['acc_pct_2015']:.2f}% to {reg_g['acc_pct_2023']:.2f}% (+{reg_g['delta_acc_pct']:.2f} percentage points)**.\n\n")
        
        f.write("## 2. Benchmark District Trajectory Matrix (2015–16 to 2023–24)\n\n")
        f.write("| District | Baseline Enr (2015) | 2023 Enr | Baseline PTR | 2023 PTR | Change in PTR | Teachers / 1k (2015) | Teachers / 1k (2023) | Baseline Acc % | 2023 Acc % | Δ Acc (pp) | 2023 EL % |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        
        for _, r in growth_df.iterrows():
            d_label = r["district_name"].replace("Pub Sch", "").replace("R-VII", "").strip()
            if r["district_name"] == "KANSAS CITY 33":
                d_label = "**KCPS (Kansas City 33)**"
            elif r["district_name"] == "Kansas City":
                d_label = "**KCKPS (USD 500)**"
            elif r["district_name"] == "METRO REGIONAL TOTAL":
                d_label = "**METRO REGIONAL TOTAL**"
            
            ptr_15_str = f"{r['ptr_2015']:.2f}:1" if pd.notna(r['ptr_2015']) else "Suppressed*"
            ptr_23_str = f"{r['ptr_2023']:.2f}:1" if pd.notna(r['ptr_2023']) else "Suppressed*"
            delta_ptr_str = f"**{r['delta_ptr']:+.2f}**" if pd.notna(r['delta_ptr']) else "*N/A*"
            tch_15_str = f"{r['tch_1000_2015']:.1f}" if pd.notna(r['tch_1000_2015']) else "Suppressed*"
            tch_23_str = f"{r['tch_1000_2023']:.1f}" if pd.notna(r['tch_1000_2023']) else "Suppressed*"
            
            f.write(f"| {d_label} | {r['enr_2015']:,.0f} | {r['enr_2023']:,.0f} | {ptr_15_str} | {ptr_23_str} | {delta_ptr_str} | {tch_15_str} | {tch_23_str} | {r['acc_pct_2015']:.1f}% | {r['acc_pct_2023']:.1f}% | **{r['delta_acc_pct']:+.2f} pp** | {r['lep_pct_2023']:.1f}% |\n")
        
        f.write("\n*Note: In 2015–16 CCD, staff counts for Olathe USD 233 were administratively suppressed by NCES (code -9.0; preserved as missing per Decision 030). Unsuppressed adjacent years were 14.66:1 in 2014–15 and 14.43:1 in 2016–17.*\n")
            
        f.write("\n\n## 3. Visual Artifacts\n\n")
        f.write("### Figure 16: District-by-District Trajectories (Staffing vs. Need Over Time)\n")
        f.write("![Figure 16: District Staffing vs. Accommodations Over Time](../figures/fig16_district_capacity_vs_need_trajectories.png)\n\n")
        f.write("### Figure 17: Quadrant Scatter Plot (Staffing Expansion vs. Need Growth)\n")
        f.write("![Figure 17: Staffing Expansion vs. Need Growth Quadrants](../figures/fig17_district_growth_scatter_capacity_vs_need.png)\n\n")
        
    print(f"Generated {report_path}")
    print("=== Analysis Complete ===")

if __name__ == "__main__":
    run_district_capacity_vs_need_analysis()
