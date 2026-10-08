"""
src/analyze_institutional_incentives.py

Kansas City Institutional Incentive Study (Phase 2):
Analyzes the empirical Signaling Decoupling Gap across 45 Kansas City high schools,
linking observed graduation-to-achievement divergence to district grading policies,
credit recovery systems, and MSIP 6 accountability incentives.

Outputs:
- artifacts/tables/table4_kc_institutional_decoupling_summary.csv
- artifacts/tables/table5_district_policy_matrix.csv
- artifacts/figures/04_kc_signaling_decoupling_gap.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SOURCES_DIR = BASE_DIR / "sources"
FIG_DIR = BASE_DIR / "artifacts" / "figures"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"

FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Styling defaults
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8


def map_district_policy(district_name: str) -> str:
    """Maps district names from the panel to the standardized policy registry identifiers."""
    d_upper = str(district_name).upper().strip()
    
    charter_leas = [
        "CROSSROADS CHARTER SCHOOLS",
        "DE LASALLE CHARTER SCHOOL",
        "EWING MARION KAUFFMAN SCHOOL",
        "FRONTIER SCHOOLS",
        "GUADALUPE CENTERS SCHOOLS",
        "HOGAN PREPARATORY ACADEMY",
        "UNIVERSITY ACADEMY"
    ]
    if d_upper in charter_leas:
        return "KC_CHARTER_LEAS"
    
    known_districts = {
        "KANSAS CITY 33": "048-078",
        "INDEPENDENCE 30": "048-077",
        "NORTH KANSAS CITY 74": "024-093",
        "LEE'S SUMMIT R-VII": "048-074",
        "HICKMAN MILLS C-1": "048-072",
        "BLUE SPRINGS R-IV": "048-068",
        "RAYTOWN C-2": "048-079",
        "GRANDVIEW C-4": "048-071",
        "PARK HILL": "083-005",
    }
    return known_districts.get(d_upper, "SUBURBAN_MSBA_STANDARD")


def load_and_process_decoupling_data():
    """Loads KC high school panel and policy registry, computes Signaling Decoupling Gap."""
    panel_file = PROCESSED_DIR / "kc_high_school_panel.csv"
    policy_file = SOURCES_DIR / "kc_district_policy_registry.csv"
    
    df = pd.read_csv(panel_file)
    df_policy = pd.read_csv(policy_file)
    
    # 2022 cross-sectional benchmark (45 complete high schools)
    p2022 = df[df["school_year"] == 2022].dropna(subset=["grad_rate_4yr", "math_status_mpi"]).copy()
    
    # Percentile ranks (1.0 to 100.0) across the 45 high schools
    p2022["grad_rate_pctile"] = p2022["grad_rate_4yr"].rank(pct=True) * 100.0
    p2022["math_mpi_pctile"] = p2022["math_status_mpi"].rank(pct=True) * 100.0
    
    # Signaling Decoupling Gap (Delta) = Percentile(Graduation Rate) - Percentile(Math MPI)
    p2022["signaling_decoupling_gap"] = p2022["grad_rate_pctile"] - p2022["math_mpi_pctile"]
    
    # Map policy codes
    p2022["policy_district_code"] = p2022["DISTRICT_NAME"].apply(map_district_policy)
    
    # Merge policy details
    merged = pd.merge(
        p2022,
        df_policy,
        left_on="policy_district_code",
        right_on="district_code",
        how="left"
    )
    
    # For suburban districts using general MSBA standard
    merged["grading_model"] = merged["grading_model"].fillna("TRADITIONAL_PCT")
    merged["grade_floor_policy"] = merged["grade_floor_policy"].fillna("NO_FLOOR_ZERO_ALLOWED")
    merged["retake_rule"] = merged["retake_rule"].fillna("TEACHER_DISCRETION")
    merged["credit_recovery_platform"] = merged["credit_recovery_platform"].fillna("IN_HOUSE")
    merged["credit_recovery_cutoff"] = merged["credit_recovery_cutoff"].fillna(60.0)
    
    return merged, df_policy


def generate_tables(df: pd.DataFrame, df_policy: pd.DataFrame):
    """Generates Table 4 (School-level summary) and Table 5 (District Policy Matrix)."""
    # Table 4: School-level decoupling summary
    cols_table4 = [
        "DISTRICT_NAME",
        "SCHOOL_NAME",
        "grad_rate_4yr",
        "math_status_mpi",
        "grad_rate_pctile",
        "math_mpi_pctile",
        "signaling_decoupling_gap",
        "direct_cert_pct",
        "frpl_pct",
        "enrollment",
        "grading_model",
        "grade_floor_policy",
        "retake_rule",
        "credit_recovery_platform"
    ]
    t4 = df[cols_table4].sort_values(by="signaling_decoupling_gap", ascending=False).copy()
    t4.columns = [
        "District Name",
        "School Name",
        "4-Yr Grad Rate (%)",
        "Math Status MPI",
        "Grad Rate Pctile",
        "Math MPI Pctile",
        "Decoupling Gap (Pctile Pts)",
        "Direct Cert (%)",
        "FRPL (%)",
        "Enrollment",
        "Grading Model",
        "Grade Floor Policy",
        "Retake Rule",
        "Credit Recovery Platform"
    ]
    t4.to_csv(TABLES_DIR / "table4_kc_institutional_decoupling_summary.csv", index=False)
    print(f"Saved Table 4: {TABLES_DIR / 'table4_kc_institutional_decoupling_summary.csv'} ({len(t4)} schools)")
    
    # Table 5: District Policy & Decoupling Matrix
    dist_summary = df.groupby("DISTRICT_NAME").agg(
        num_high_schools=("SCHOOL_NAME", "nunique"),
        avg_grad_rate=("grad_rate_4yr", "mean"),
        avg_math_mpi=("math_status_mpi", "mean"),
        avg_decoupling_gap=("signaling_decoupling_gap", "mean"),
        avg_direct_cert=("direct_cert_pct", "mean"),
        grading_model=("grading_model", "first"),
        grade_floor_policy=("grade_floor_policy", "first"),
        retake_rule=("retake_rule", "first"),
        credit_recovery_platform=("credit_recovery_platform", "first")
    ).reset_index()
    
    dist_summary = dist_summary.sort_values(by="avg_decoupling_gap", ascending=False)
    dist_summary.columns = [
        "District Name",
        "High Schools (N)",
        "Avg Grad Rate (%)",
        "Avg Math MPI",
        "Avg Decoupling Gap (Pts)",
        "Avg Direct Cert (%)",
        "Grading Model",
        "Grade Floor Policy",
        "Retake Rule",
        "Credit Recovery Platform"
    ]
    dist_summary.to_csv(TABLES_DIR / "table5_district_policy_matrix.csv", index=False)
    print(f"Saved Table 5: {TABLES_DIR / 'table5_district_policy_matrix.csv'} ({len(dist_summary)} districts)")


def plot_figure_4(df: pd.DataFrame):
    """
    Generates Figure 4:
    Panel A: The Signaling Decoupling Landscape (Graduation Rate vs. Math MPI with Decoupling Colormap)
    Panel B: Kansas City High Schools with Largest Positive Decoupling Gaps and Policy Annotations
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=300)
    
    # Panel A: Scatter Plot
    scatter = ax1.scatter(
        df["math_status_mpi"],
        df["grad_rate_4yr"],
        c=df["signaling_decoupling_gap"],
        cmap="coolwarm",
        s=df["enrollment"] / 12.0,
        alpha=0.85,
        edgecolor="#222222",
        linewidth=0.8,
        vmin=-55,
        vmax=65
    )
    
    # Threshold lines
    ax1.axvline(350, color="#d62728", linestyle="--", linewidth=1.4, alpha=0.8, label="State Proficient Baseline (MPI = 350)")
    ax1.axhline(90, color="#2ca02c", linestyle=":", linewidth=1.4, alpha=0.8, label="90% Graduation Target")
    
    # Annotate specific notable schools
    notable = [
        ("NORTH KANSAS CITY HIGH", (331.4, 98.1), (300, 99.5)),
        ("VAN HORN HIGH", (300.1, 94.6), (280, 95.8)),
        ("RUSKIN HIGH SCHOOL", (315.0, 88.3), (290, 86.0)),
        ("PASEO ACAD. OF PERFORMING ARTS", (289.8, 82.5), (282, 80.0)),
        ("PARK HILL SOUTH HIGH", (426.2, 87.6), (405, 84.5)),
        ("STALEY HIGH", (366.7, 98.7), (375, 99.2)),
        ("LEE'S SUMMIT SR. HIGH", (407.7, 93.9), (410, 92.0)),
    ]
    for name, (x, y), (text_x, text_y) in notable:
        match = df[df["SCHOOL_NAME"] == name]
        if not match.empty:
            ax1.annotate(
                name.replace(" HIGH SCHOOL", "").replace(" SR. HIGH", "").title(),
                xy=(x, y),
                xytext=(text_x, text_y),
                fontsize=8,
                fontweight="bold",
                color="#111111",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=0.7)
            )
            
    cbar = plt.colorbar(scatter, ax=ax1, orientation="vertical", shrink=0.85, pad=0.03)
    cbar.set_label("Signaling Decoupling Gap (Percentile Pts)\n[Graduation Rank − Math MPI Rank]", fontsize=8.5)
    
    ax1.set_xlabel("Missouri Mathematics MAP Performance Index (MPI)\n[100=Below Basic, 250=Basic, 350=Proficient, 450=Advanced]", fontsize=9.5)
    ax1.set_ylabel("4-Year Cohort Graduation Rate (%)", fontsize=9.5)
    ax1.set_title("Panel A: Graduation Rate vs. Assessed Mathematics MPI\n(45 Greater Kansas City High Schools, 2022 Benchmark)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_ylim(50, 102)
    ax1.set_xlim(260, 470)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="lower left", fontsize=8.5, framealpha=0.9)
    
    # Panel B: Top Decoupled Schools
    top_decoupled = df.sort_values(by="signaling_decoupling_gap", ascending=False).head(10).copy()
    top_decoupled["display_label"] = (
        top_decoupled["SCHOOL_NAME"].str.replace(" SR. HIGH", "").str.replace(" HIGH SCHOOL", "").str.title() +
        " (" + top_decoupled["DISTRICT_NAME"].str.replace(" 74", "").str.replace(" 30", "").str.replace(" 33", "").str.replace(" C-1", "").str.title() + ")"
    )
    
    y_pos = np.arange(len(top_decoupled))
    colors = ["#b2182b" if gap > 30 else "#ef8a62" if gap > 20 else "#fddbc7" for gap in top_decoupled["signaling_decoupling_gap"]]
    
    bars = ax2.barh(y_pos, top_decoupled["signaling_decoupling_gap"], color=colors, edgecolor="#333333", height=0.65)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top_decoupled["display_label"], fontsize=8.5)
    ax2.invert_yaxis()  # Top school at top
    
    # Add data annotations on bars
    for bar, (_, row) in zip(bars, top_decoupled.iterrows()):
        w = bar.get_width()
        grad = row["grad_rate_4yr"]
        mpi = row["math_status_mpi"]
        policy = row["grade_floor_policy"].replace("FLOOR_", "Floor: ").replace("NO_FLOOR_ZERO_ALLOWED", "No Floor")
        if row["grading_model"] == "STANDARDS_BASED":
            policy = "Standards-Based (SBL)"
        
        ax2.text(
            w + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"+{w:.1f} pts  |  Grad: {grad:.1f}%  |  Math MPI: {mpi:.1f}  [{policy}]",
            va="center",
            fontsize=7.8,
            color="#222222"
        )
        
    ax2.set_xlabel("Signaling Decoupling Gap (Percentile Points)\n[Graduation Rate Rank − Mathematics MPI Rank]", fontsize=9.5)
    ax2.set_title("Panel B: High Schools with Largest Positive Decoupling\n(Graduation Rank Drastically Exceeding Tested Math Achievement)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(0, 85)
    ax2.grid(True, linestyle="--", alpha=0.3, axis="x")
    
    # Footnote
    fig.text(
        0.05, 0.01,
        "Data Sources: Missouri Department of Elementary and Secondary Education (DESE) MSIP 6 APR panel (2021–22) and Kansas City District Policy Registry.\n"
        "Bubble size in Panel A represents total school enrollment. Signaling Decoupling Gap = Percentile(Graduation Rate) − Percentile(Math MPI) across 45 KC-area high schools.\n"
        "State MPI benchmarks: 100 = Below Basic, 250 = Basic, 350 = Proficient, 450 = Advanced. A positive gap indicates graduation rates outpace standardized math achievement.",
        fontsize=7.5, color="#555555", style="italic"
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    out_path = FIG_DIR / "04_kc_signaling_decoupling_gap.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 4: {out_path}")


def main():
    print("Executing Kansas City Institutional Incentive Analysis...")
    df_merged, df_policy = load_and_process_decoupling_data()
    generate_tables(df_merged, df_policy)
    plot_figure_4(df_merged)
    print("Kansas City Institutional Incentive Analysis completed successfully.")


if __name__ == "__main__":
    main()
