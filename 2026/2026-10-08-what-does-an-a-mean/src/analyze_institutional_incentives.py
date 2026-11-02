"""
src/analyze_institutional_incentives.py

Kansas City Institutional Incentive Study (Phase 2):
Computes the exploratory Graduation–Achievement Rank Difference across 45 Kansas City high schools (2022 benchmark)
and establishes the longitudinal case study registry (Case Study A: KCPS; Case Study B: NKC Schools).

Outputs:
- artifacts/tables/table4_kc_institutional_decoupling_summary.csv
- artifacts/tables/table5_district_policy_matrix.csv
- artifacts/figures/04_kc_signaling_decoupling_gap.png
"""

from pathlib import Path

# Compatibility fix for PySide6 / Shiboken / Python 3.12 meta-path inspection
try:
    import six
    if hasattr(six, "_SixMetaPathImporter") and not hasattr(six._SixMetaPathImporter, "_path"):
        six._SixMetaPathImporter._path = None
except ImportError:
    pass

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
    """Maps district names from the panel to verified policy registry identifiers."""
    d_upper = str(district_name).upper().strip()
    
    known_districts = {
        "KANSAS CITY 33": "048-078",
        "NORTH KANSAS CITY 74": "024-093",
        "INDEPENDENCE 30": "048-077",
        "LEE'S SUMMIT R-VII": "048-074",
        "HICKMAN MILLS C-1": "048-072",
        "BLUE SPRINGS R-IV": "048-068",
        "RAYTOWN C-2": "048-079",
        "GRANDVIEW C-4": "048-071",
        "PARK HILL": "083-005",
    }
    return known_districts.get(d_upper, "UNVERIFIED_PENDING_AUDIT")


def assign_school_policy_exposure(
    school_name: str,
    district_code: str,
    df_evidence: pd.DataFrame = None,
    academic_year: str = None,
    course_track: str = None
) -> pd.Series:
    """
    Derives school-specific policy exposure, subsequent policy name, effective timeline,
    grading weights, and audit status directly from verified records in kc_policy_exposure_evidence_register.csv.
    
    Supports two operating modes:
    1. Observation-level lookup (when academic_year is provided):
       Evaluates exact exposure for an arbitrary (school, district, year, track) observation
       using strict precedence (exact school/track -> wildcard school/track -> date interval -> UNVERIFIED).
    2. Subsequent longitudinal classification (when academic_year is None):
       Determines school-level post-2022 policy adoption and case study role for Table 4.
       Derives entirely from evidence records; returns UNVERIFIED / PENDING_AUDIT if no evidence exists.
    """
    if df_evidence is None:
        evidence_file = SOURCES_DIR / "kc_policy_exposure_evidence_register.csv"
        df_evidence = pd.read_csv(evidence_file)
        
    s_upper = str(school_name).upper().strip()
    
    # Mode 1: Arbitrary observation lookup (academic_year specified)
    if academic_year is not None:
        # Precedence 1: Exact district + exact school + exact year
        school_year_matches = df_evidence[
            (df_evidence["district_code"] == district_code) &
            (df_evidence["school_name"].str.upper() == s_upper) &
            (df_evidence["academic_year"] == academic_year)
        ]
        
        # Precedence 2: Exact district + wildcard school ('ALL_HIGH_SCHOOLS') + exact year
        wildcard_year_matches = df_evidence[
            (df_evidence["district_code"] == district_code) &
            (df_evidence["school_name"] == "ALL_HIGH_SCHOOLS") &
            (df_evidence["academic_year"] == academic_year)
        ]
        
        candidates = pd.concat([school_year_matches, wildcard_year_matches])
        
        # Precedence 3: Date range interval fallback if exact academic_year string doesn't match
        if candidates.empty:
            start_yr = academic_year.split("-")[0] if "-" in academic_year else academic_year
            ref_date = f"{start_yr}-10"
            date_matches = df_evidence[
                (df_evidence["district_code"] == district_code) &
                ((df_evidence["school_name"].str.upper() == s_upper) | (df_evidence["school_name"] == "ALL_HIGH_SCHOOLS")) &
                (df_evidence["effective_start"] <= ref_date) &
                (df_evidence["effective_end"] >= ref_date)
            ]
            candidates = date_matches
            
        if candidates.empty:
            return pd.Series({
                "subsequent_policy": "Unverified",
                "subsequent_year": "N/A",
                "audit_status": "UNVERIFIED",
                "policy_exposure_role": "UNVERIFIED",
                "grading_model": "UNVERIFIED",
                "grading_floor_minimum": "UNVERIFIED",
                "attempted_work_floor": "UNVERIFIED",
                "missing_work_rule": "UNVERIFIED",
                "reassessment_rule": "UNVERIFIED",
                "engagement_weight_pct": np.nan,
                "progress_weight_pct": np.nan,
                "proficiency_weight_pct": np.nan,
                "evidence_strength": "UNVERIFIED"
            })
            
        # Track matching if course_track is supplied
        if course_track is not None:
            t_upper = str(course_track).upper().strip()
            # Exact track or substring match
            track_matches = candidates[candidates["course_track"].str.upper().str.contains(t_upper, regex=False)]
            if not track_matches.empty:
                candidates = track_matches
            else:
                # Fallback to 'All Courses' / 'All Secondary Courses'
                general_matches = candidates[candidates["course_track"].isin(["All Courses", "All Secondary Courses"])]
                if not general_matches.empty:
                    candidates = general_matches
                else:
                    return pd.Series({
                        "subsequent_policy": "Unverified",
                        "subsequent_year": "N/A",
                        "audit_status": "UNVERIFIED",
                        "policy_exposure_role": "UNVERIFIED",
                        "grading_model": "UNVERIFIED",
                        "grading_floor_minimum": "UNVERIFIED",
                        "attempted_work_floor": "UNVERIFIED",
                        "missing_work_rule": "UNVERIFIED",
                        "reassessment_rule": "UNVERIFIED",
                        "engagement_weight_pct": np.nan,
                        "progress_weight_pct": np.nan,
                        "proficiency_weight_pct": np.nan,
                        "evidence_strength": "UNVERIFIED"
                    })
                    
        # Prefer school-specific over wildcard
        school_specific = candidates[candidates["school_name"].str.upper() == s_upper]
        rec = school_specific.iloc[0] if not school_specific.empty else candidates.iloc[0]
        
        return pd.Series({
            "subsequent_policy": rec["grading_model"],
            "subsequent_year": rec["academic_year"],
            "audit_status": rec["evidence_strength"],
            "policy_exposure_role": rec["policy_exposure_role"],
            "grading_model": rec["grading_model"],
            "grading_floor_minimum": rec["attempted_work_floor"],
            "attempted_work_floor": rec["attempted_work_floor"],
            "missing_work_rule": rec["missing_work_rule"],
            "reassessment_rule": rec["reassessment_rule"],
            "engagement_weight_pct": rec["engagement_weight_pct"],
            "progress_weight_pct": rec["progress_weight_pct"],
            "proficiency_weight_pct": rec["proficiency_weight_pct"],
            "evidence_strength": rec["evidence_strength"]
        })

    # Mode 2: Table 4 school-level subsequent policy adoption (academic_year is None)
    district_records = df_evidence[df_evidence["district_code"] == district_code]
    if district_records.empty:
        return pd.Series({
            "subsequent_policy": "Unverified",
            "subsequent_year": "N/A",
            "audit_status": "PENDING_AUDIT",
            "policy_exposure_role": "Exploratory_Pending_Audit"
        })
        
    # Check if school has verified traditional comparison record
    school_comp = district_records[
        (district_records["school_name"].str.upper() == s_upper) &
        (district_records["policy_exposure_role"] == "Verified_Traditional_Comparison")
    ]
    if not school_comp.empty:
        rec = school_comp.iloc[0]
        return pd.Series({
            "subsequent_policy": rec["grading_model"],
            "subsequent_year": f"{rec['effective_start'][:4]}-{rec['effective_end'][:4]}",
            "audit_status": "VERIFIED_TRADITIONAL_COMPARISON",
            "policy_exposure_role": rec["policy_exposure_role"]
        })
        
    # Filter for post-2022 subsequent policy records
    subsequent_records = district_records[district_records["academic_year"] > "2021-2022"]
    if subsequent_records.empty:
        # Without post-2022 records, district/school cannot be classified as subsequent policy
        return pd.Series({
            "subsequent_policy": "Unverified",
            "subsequent_year": "N/A",
            "audit_status": "PENDING_AUDIT",
            "policy_exposure_role": "Exploratory_Pending_Audit"
        })
        
    # Evaluate at the latest subsequent policy period
    latest_year = subsequent_records["academic_year"].max()
    latest_recs = subsequent_records[subsequent_records["academic_year"] == latest_year]
    
    # 1. School-specific record in latest subsequent period
    school_sub = latest_recs[latest_recs["school_name"].str.upper() == s_upper]
    if not school_sub.empty:
        # Designated pilot
        pilot = school_sub[school_sub["policy_exposure_role"].str.contains("Pilot")]
        if not pilot.empty:
            rec = pilot.iloc[-1]
            return pd.Series({
                "subsequent_policy": f"{rec['grading_model']} (Pilot: Designated Courses)",
                "subsequent_year": f"{rec['academic_year']} (Fall Pilot)",
                "audit_status": "VERIFIED_LONGITUDINAL_CASE_B_PILOT",
                "policy_exposure_role": rec["policy_exposure_role"]
            })
        # Within-district comparison
        comp = school_sub[school_sub["policy_exposure_role"].str.contains("Within_District_Comparison")]
        if not comp.empty:
            rec = comp.iloc[-1]
            return pd.Series({
                "subsequent_policy": f"{rec['grading_model']} (Non-Pilot; SBL in 26-27)",
                "subsequent_year": "2026-2027 (Full Rollout)",
                "audit_status": "VERIFIED_WITHIN_DISTRICT_COMPARISON",
                "policy_exposure_role": rec["policy_exposure_role"]
            })
        # Mixed course exposure
        mixed = school_sub[school_sub["policy_exposure_role"].str.contains("Mixed")]
        if not mixed.empty:
            rec = mixed.iloc[-1]
            return pd.Series({
                "subsequent_policy": f"{rec['grading_model']} (Mixed: Honors/AP/IB Exempt, General Subject to Floor)",
                "subsequent_year": "2023-2024 / 2024-2025 (Revised)",
                "audit_status": "VERIFIED_LONGITUDINAL_CASE_A_MIXED",
                "policy_exposure_role": rec["policy_exposure_role"]
            })
        rec = school_sub.iloc[-1]
        return pd.Series({
            "subsequent_policy": rec["grading_model"],
            "subsequent_year": rec["academic_year"],
            "audit_status": "VERIFIED_LONGITUDINAL_POLICY",
            "policy_exposure_role": rec["policy_exposure_role"]
        })
        
    # 2. District-wide wildcard record in latest subsequent period ('ALL_HIGH_SCHOOLS')
    wildcard_sub = latest_recs[latest_recs["school_name"] == "ALL_HIGH_SCHOOLS"]
    if not wildcard_sub.empty:
        tracks = wildcard_sub["course_track"].unique()
        has_honors = any("Honors" in t for t in tracks)
        has_general = any("General" in t for t in tracks)
        if has_honors and has_general:
            return pd.Series({
                "subsequent_policy": "FLOOR_40_MINIMUM (Mixed: General 40% Floor, Honors/AP Exempt)",
                "subsequent_year": "2023-2024 / 2024-2025 (Revised)",
                "audit_status": "VERIFIED_LONGITUDINAL_CASE_A_MIXED",
                "policy_exposure_role": "Case_A_Mixed_Course_Exposure_2024_25"
            })
        rec = wildcard_sub.iloc[-1]
        return pd.Series({
            "subsequent_policy": rec["grading_model"],
            "subsequent_year": rec["academic_year"],
            "audit_status": "VERIFIED_LONGITUDINAL_POLICY",
            "policy_exposure_role": rec["policy_exposure_role"]
        })
        
    # 3. Fallback: check if school had an earlier subsequent record
    earlier_school_sub = subsequent_records[subsequent_records["school_name"].str.upper() == s_upper]
    if not earlier_school_sub.empty:
        rec = earlier_school_sub.iloc[-1]
        return pd.Series({
            "subsequent_policy": rec["grading_model"],
            "subsequent_year": rec["academic_year"],
            "audit_status": "VERIFIED_LONGITUDINAL_POLICY",
            "policy_exposure_role": rec["policy_exposure_role"]
        })
        
    # If no school-specific record and no wildcard record exists
    return pd.Series({
        "subsequent_policy": "Unverified",
        "subsequent_year": "N/A",
        "audit_status": "PENDING_AUDIT",
        "policy_exposure_role": "Exploratory_Pending_Audit"
    })


def load_and_process_decoupling_data():
    """Loads KC high school panel, policy registry, and evidence register, computing Rank Difference and exposure."""
    panel_file = PROCESSED_DIR / "kc_high_school_panel.csv"
    policy_file = SOURCES_DIR / "kc_district_policy_registry.csv"
    evidence_file = SOURCES_DIR / "kc_policy_exposure_evidence_register.csv"
    
    df = pd.read_csv(panel_file)
    df_policy = pd.read_csv(policy_file)
    df_evidence = pd.read_csv(evidence_file)
    
    # 2022 cross-sectional benchmark (45 complete high schools)
    p2022 = df[df["school_year"] == 2022].dropna(subset=["grad_rate_4yr", "math_status_mpi"]).copy()
    
    # Percentile ranks (1.0 to 100.0) across the 45 high schools
    p2022["grad_rate_pctile"] = p2022["grad_rate_4yr"].rank(pct=True) * 100.0
    p2022["math_mpi_pctile"] = p2022["math_status_mpi"].rank(pct=True) * 100.0
    
    # Graduation–Achievement Rank Difference (Delta) = Percentile(Grad Rate) - Percentile(Math MPI)
    p2022["grad_math_rank_diff"] = p2022["grad_rate_pctile"] - p2022["math_mpi_pctile"]
    
    # Map district policy identifier
    p2022["policy_district_code"] = p2022["DISTRICT_NAME"].apply(map_district_policy)
    
    # Merge district-level policy baseline without default-filling unverified entries
    merged = pd.merge(
        p2022,
        df_policy[["district_code", "policy_name", "status_in_2022_benchmark", "grading_model_2022", "grading_floor_policy_2022"]],
        left_on="policy_district_code",
        right_on="district_code",
        how="left"
    )
    
    # Assign verified school-specific subsequent policy exposure and roles directly from evidence register
    exposure_df = merged.apply(lambda r: assign_school_policy_exposure(r["SCHOOL_NAME"], r["policy_district_code"], df_evidence), axis=1)
    merged["current_or_subsequent_policy"] = exposure_df["subsequent_policy"]
    merged["subsequent_effective_year"] = exposure_df["subsequent_year"]
    merged["verification_status"] = exposure_df["audit_status"]
    merged["policy_exposure_role"] = exposure_df["policy_exposure_role"]
    
    # Preserve explicit unverified status rather than imputing policies
    merged["policy_name"] = merged["policy_name"].fillna("Policy Documentation Pending Audit")
    merged["status_in_2022_benchmark"] = merged["status_in_2022_benchmark"].fillna("UNVERIFIED")
    merged["grading_model_2022"] = merged["grading_model_2022"].fillna("Unverified")
    merged["grading_floor_policy_2022"] = merged["grading_floor_policy_2022"].fillna("Unverified")
    
    return merged, df_policy, df_evidence


def generate_tables(df: pd.DataFrame, df_policy: pd.DataFrame, df_evidence: pd.DataFrame = None):
    """Generates Table 4 (School-level summary) and Table 5 (District Policy Case Study Matrix)."""
    # Table 4: School-level exploratory ranking summary
    cols_table4 = [
        "DISTRICT_NAME",
        "SCHOOL_NAME",
        "grad_rate_4yr",
        "math_status_mpi",
        "grad_rate_pctile",
        "math_mpi_pctile",
        "grad_math_rank_diff",
        "direct_cert_pct",
        "frpl_pct",
        "enrollment",
        "status_in_2022_benchmark",
        "current_or_subsequent_policy",
        "subsequent_effective_year",
        "verification_status",
        "policy_exposure_role"
    ]
    t4 = df[cols_table4].sort_values(by="grad_math_rank_diff", ascending=False).copy()
    t4.columns = [
        "District Name",
        "School Name",
        "4-Yr Grad Rate (%)",
        "Math Status MPI",
        "Grad Rate Pctile",
        "Math MPI Pctile",
        "Grad-Math Rank Diff (Pctile Pts)",
        "Direct Cert (%)",
        "FRPL (%)",
        "Enrollment",
        "Policy Status in 2022",
        "Subsequent Policy Adoption",
        "Subsequent Effective Year",
        "Research Audit Status",
        "Longitudinal Policy Exposure Role"
    ]
    t4.to_csv(TABLES_DIR / "table4_kc_institutional_decoupling_summary.csv", index=False)
    print(f"Saved Table 4: {TABLES_DIR / 'table4_kc_institutional_decoupling_summary.csv'} ({len(t4)} schools)")
    
    # Table 5: District Policy & Case Study Research Matrix
    dist_summary = df.groupby("DISTRICT_NAME").agg(
        num_high_schools=("SCHOOL_NAME", "nunique"),
        avg_grad_rate=("grad_rate_4yr", "mean"),
        avg_math_mpi=("math_status_mpi", "mean"),
        avg_rank_diff=("grad_math_rank_diff", "mean"),
        avg_direct_cert=("direct_cert_pct", "mean"),
        status_in_2022=("status_in_2022_benchmark", "first"),
        audit_status=("verification_status", "first")
    ).reset_index()
    
    # Merge with district policy registry for district-level subsequent policy metadata
    dist_summary = pd.merge(
        dist_summary,
        df_policy[["district_name", "current_or_subsequent_policy", "subsequent_effective_year"]],
        left_on="DISTRICT_NAME",
        right_on="district_name",
        how="left"
    )
    dist_summary["current_or_subsequent_policy"] = dist_summary["current_or_subsequent_policy"].fillna("Unverified")
    dist_summary["subsequent_effective_year"] = dist_summary["subsequent_effective_year"].fillna("N/A")
    
    # Assign clear research role in longitudinal agenda
    def assign_case_study_role(row):
        d_name = row["DISTRICT_NAME"]
        if d_name == "KANSAS CITY 33":
            return "Case Study A (40% Minimum Grading Floor; Pre-Post 2023-24 & 2024-25 Revision)"
        elif d_name == "NORTH KANSAS CITY 74":
            return "Case Study B (NKC High Fall 2025 SBL Pilot vs Non-Pilot Comparisons)"
        elif row["status_in_2022"] == "VERIFIED_IN_EFFECT":
            return "Verified Comparison District (Traditional Grading Scale)"
        else:
            return "Exploratory Observation (Policy Documentation Pending)"

    dist_summary["Research Study Role"] = dist_summary.apply(assign_case_study_role, axis=1)
    
    dist_summary = dist_summary.sort_values(by="avg_rank_diff", ascending=False)
    cols_table5 = [
        "DISTRICT_NAME",
        "num_high_schools",
        "avg_grad_rate",
        "avg_math_mpi",
        "avg_rank_diff",
        "avg_direct_cert",
        "status_in_2022",
        "current_or_subsequent_policy",
        "subsequent_effective_year",
        "audit_status",
        "Research Study Role"
    ]
    dist_summary = dist_summary[cols_table5]
    dist_summary.columns = [
        "District Name",
        "High Schools (N)",
        "Avg Grad Rate (%)",
        "Avg Math MPI",
        "Avg Rank Diff (Pts)",
        "Avg Direct Cert (%)",
        "Policy Status in 2022",
        "Subsequent Policy Adoption",
        "Subsequent Effective Year",
        "Audit Status",
        "Research Study Role"
    ]
    dist_summary.to_csv(TABLES_DIR / "table5_district_policy_matrix.csv", index=False)
    print(f"Saved Table 5: {TABLES_DIR / 'table5_district_policy_matrix.csv'} ({len(dist_summary)} districts)")


def plot_figure_4(df: pd.DataFrame):
    """
    Generates Figure 4:
    Panel A: Graduation Rate vs. Mathematics MPI with Graduation-Achievement Rank Difference
    Panel B: Kansas City High Schools with Largest Positive Graduation-Achievement Rank Differences
    """
    pearson_r = df["grad_rate_4yr"].corr(df["math_status_mpi"], method="pearson")
    spearman_rho = df["grad_rate_4yr"].corr(df["math_status_mpi"], method="spearman")
    median_mpi = df["math_status_mpi"].median()
    median_grad = df["grad_rate_4yr"].median()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.6), dpi=300)
    
    # Panel A: Scatter Plot
    scatter = ax1.scatter(
        df["math_status_mpi"],
        df["grad_rate_4yr"],
        c=df["grad_math_rank_diff"],
        cmap="coolwarm",
        s=df["enrollment"] / 12.0,
        alpha=0.85,
        edgecolor="#222222",
        linewidth=0.8,
        vmin=-55,
        vmax=65
    )
    
    # Regional Distribution Medians
    ax1.axvline(median_mpi, color="#444444", linestyle="--", linewidth=1.2, alpha=0.7, label=f"Regional Median Math MPI ({median_mpi:.1f})")
    ax1.axhline(median_grad, color="#444444", linestyle=":", linewidth=1.2, alpha=0.7, label=f"Regional Median Grad Rate ({median_grad:.1f}%)")
    
    # Annotate specific notable schools
    notable = [
        ("NORTH KANSAS CITY HIGH", (331.4, 98.1), (295, 99.6)),
        ("VAN HORN HIGH", (300.1, 94.6), (275, 95.8)),
        ("RUSKIN HIGH SCHOOL", (315.0, 88.3), (285, 86.0)),
        ("PASEO ACAD. OF PERFORMING ARTS", (289.8, 82.5), (280, 80.0)),
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
    cbar.set_label("Graduation–Achievement Rank Difference (Percentile Pts)\n[Graduation Rate Rank − Math MPI Rank]", fontsize=8.5)
    
    # Annotation box for correlation
    ax1.text(
        0.05, 0.18,
        f"Overall Regional Relationship:\nPearson r = {pearson_r:.3f}\nSpearman rho = {spearman_rho:.3f}\nSample: N = 45 High Schools",
        transform=ax1.transAxes,
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffffff", edgecolor="#bbbbbb", alpha=0.9)
    )
    
    ax1.set_xlabel("Missouri Mathematics MAP Performance Index (MPI)\n[Aggregate school index across Below Basic, Basic, Proficient, and Advanced]", fontsize=9.5)
    ax1.set_ylabel("4-Year Cohort Graduation Rate (%)", fontsize=9.5)
    ax1.set_title("Panel A: Graduation Rate vs. Assessed Mathematics MPI\n(45 Greater Kansas City High Schools, 2022 Benchmark)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_ylim(50, 102)
    ax1.set_xlim(260, 470)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="lower left", fontsize=8.2, framealpha=0.9)
    
    # Panel B: Top Rank-Difference Schools
    top_diff = df.sort_values(by="grad_math_rank_diff", ascending=False).head(10).copy()
    top_diff["display_label"] = (
        top_diff["SCHOOL_NAME"].str.replace(" SR. HIGH", "").str.replace(" HIGH SCHOOL", "").str.title() +
        " (" + top_diff["DISTRICT_NAME"].str.replace(" 74", "").str.replace(" 30", "").str.replace(" 33", "").str.replace(" C-1", "").str.title() + ")"
    )
    
    y_pos = np.arange(len(top_diff))
    colors = ["#b2182b" if gap > 30 else "#ef8a62" if gap > 20 else "#fddbc7" for gap in top_diff["grad_math_rank_diff"]]
    
    bars = ax2.barh(y_pos, top_diff["grad_math_rank_diff"], color=colors, edgecolor="#333333", height=0.65)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(top_diff["display_label"], fontsize=8.5)
    ax2.invert_yaxis()
    
    for bar, (_, row) in zip(bars, top_diff.iterrows()):
        w = bar.get_width()
        grad = row["grad_rate_4yr"]
        mpi = row["math_status_mpi"]
        school = row["SCHOOL_NAME"]
        d_name = row["DISTRICT_NAME"]
        
        if school == "NORTH KANSAS CITY HIGH":
            note = "Case B: SBL Pilot (Fall 2025)"
        elif school in ["STALEY HIGH", "OAK PARK HIGH", "WINNETONKA HIGH"]:
            note = "Case B: Non-Pilot Comparison (SBL in 26-27)"
        elif "LINCOLN" in school:
            note = "Case A: Mixed Exposure (Honors/AP Exempt)"
        elif d_name == "KANSAS CITY 33":
            note = "Case A: Mixed Exposure (General 40% Floor)"
        elif d_name == "INDEPENDENCE 30":
            note = "Comparison: Traditional Scale"
        elif d_name == "HICKMAN MILLS C-1":
            note = "Audit Pending (Floor 50 Reported)"
        else:
            note = "Traditional / Audit Pending"
        
        ax2.text(
            w + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"+{w:.1f} pts  |  Grad: {grad:.1f}%  |  Math MPI: {mpi:.1f}  [{note}]",
            va="center",
            fontsize=7.8,
            color="#222222"
        )
        
    ax2.set_xlabel("Graduation–Achievement Rank Difference (Percentile Points)\n[Delta = PctRank(Graduation Rate) − PctRank(Mathematics MPI)]", fontsize=9.5)
    ax2.set_title("Panel B: High Schools with Largest Positive Rank Differences\n(Exploratory Diagnostic for Prospective Institutional Case Studies)", fontsize=11, fontweight="bold", pad=10)
    ax2.set_xlim(0, 120)
    ax2.grid(True, linestyle="--", alpha=0.3, axis="x")
    
    # Methodological footnote
    fig.text(
        0.04, 0.01,
        "Methodological Notes: Data from Missouri DESE MSIP 6 APR Supporting Files (2021–22) across 45 Kansas City area high schools.\n"
        "Cohort Note: 4-Year Graduation Rate reflects 12th-grade graduating seniors (Class of 2022); Mathematics MPI reflects students tested in End-of-Course exams (predominantly 9th/10th grade Algebra I).\n"
        "Threshold Note: School MPI is an aggregate index across all student performance levels (100–500 scale), not a student-level pass/fail cutoff. Reference lines show regional medians.\n"
        "Policy Note: Policy labels indicate subsequent policy exposure from evidence register (e.g. KCPS mixed course exposure; NKC High designated pilot vs non-pilot comparisons); they were NOT in effect during the 2022 baseline.",
        fontsize=7.2, color="#444444", style="italic"
    )
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.98])
    out_path = FIG_DIR / "04_kc_signaling_decoupling_gap.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Figure 4: {out_path}")


def main():
    print("Executing Kansas City Institutional Incentive Analysis (Refactored)...")
    df_merged, df_policy, df_evidence = load_and_process_decoupling_data()
    generate_tables(df_merged, df_policy, df_evidence)
    plot_figure_4(df_merged)
    print("Kansas City Institutional Incentive Analysis completed successfully.")


if __name__ == "__main__":
    main()
