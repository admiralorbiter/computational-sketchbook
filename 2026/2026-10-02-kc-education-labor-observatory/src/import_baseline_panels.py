"""
import_baseline_panels.py
-------------------------
Imports and harmonizes longitudinal district staffing, demand, and fiscal panels
from kc_admin_staffing_decomposition and kc_education_capacity to establish
the foundational district_labor_panel for the Kansas City Education Labor Observatory.
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
STAFFING_DIR = WORKSPACE_ROOT / "kc_admin_staffing_decomposition" / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Focal Districts Definition
FOCAL_DISTRICTS = {
    "2007950": {
        "district_code": "USD500",
        "district_clean_name": "Kansas City, KS Public Schools (USD 500)",
        "union_name": "Kansas City Kansas NEA (KCK-NEA)",
        "union_affiliation": "NEA",
        "governance_model": "KS_PNA_STRONG_MANAGEMENT_RIGHTS",
        "key_institutional_feature": "Sole and unquestioned board prerogative; strict 8-hr day / 186-day contract limits"
    },
    "2011640": {
        "district_code": "USD512",
        "district_clean_name": "Shawnee Mission School District (USD 512)",
        "union_name": "National Education Association - Shawnee Mission (NEA-SM)",
        "union_affiliation": "NEA",
        "governance_model": "KS_PNA_PROTECTED_TIME_ARCHETYPE",
        "key_institutional_feature": "Contractually guaranteed 230 min/wk elementary plan time; duty-free lunch; $53k+ starting base"
    },
    "2010140": {
        "district_code": "USD233",
        "district_clean_name": "Olathe Public Schools (USD 233)",
        "union_name": "Olathe NEA (ONEA)",
        "union_affiliation": "NEA",
        "governance_model": "KS_PNA_COLLABORATIVE_COUNCIL",
        "key_institutional_feature": "Bilateral 6-teacher / 6-admin Professional Council resolving terms and working conditions"
    },
    "2916400": {
        "district_code": "KCPS",
        "district_clean_name": "Kansas City Public Schools (KCPS)",
        "union_name": "Kansas City Federation of Teachers (KCFT Local 691)",
        "union_affiliation": "AFT",
        "governance_model": "MO_AFT_RESTRICTED_ARBITRATION",
        "key_institutional_feature": "Urban core AFT local; annual salary reopener; arbitration gated to nonpayment/class actions"
    },
    "2915480": {
        "district_code": "ISD30",
        "district_clean_name": "Independence School District (ISD 30)",
        "union_name": "Independence NEA (INNEA)",
        "union_affiliation": "NEA",
        "governance_model": "MO_NEA_CONSTITUTIONAL_LANDMARK",
        "key_institutional_feature": "Epicenter of landmark 2007 MO Supreme Court ruling establishing public employee bargaining rights"
    },
    "2922800": {
        "district_code": "NKC74",
        "district_clean_name": "North Kansas City Schools (NKC 74)",
        "union_name": "North Kansas City NEA (NKC-NEA)",
        "union_affiliation": "NEA",
        "governance_model": "MO_NEA_COLLABORATIVE_CONTINGENCY",
        "key_institutional_feature": "Collaborative Team for Teacher Negotiations (CTTN); state foundation formula escalation clauses"
    },
    "2923550": {
        "district_code": "PH5",
        "district_clean_name": "Park Hill School District",
        "union_name": "Park Hill NEA (PH-NEA)",
        "union_affiliation": "NEA",
        "governance_model": "MO_NEA_COMMITTEE_ADVISORY",
        "key_institutional_feature": "Educator participation on standing policy/calendar committees; board preserves final authority"
    }
}

def load_and_enrich_panel():
    source_parquet = STAFFING_DIR / "district_demand_year.parquet"
    if not source_parquet.exists():
        raise FileNotFoundError(f"Source file not found: {source_parquet}")
    
    print(f"Reading source demand & staffing panel from {source_parquet}...")
    df = pd.read_parquet(source_parquet)
    print(f"Loaded {len(df)} rows across {df['school_year'].nunique()} school years and {df['nces_lea_id'].nunique()} LEAs.")

    # Core derived labor & fiscal ratios
    df["pupil_teacher_ratio"] = np.where(df["teachers_k12_fte"] > 0, df["enrollment_k12"] / df["teachers_k12_fte"], np.nan)
    df["teachers_per_total_admin"] = np.where(df["total_admin_and_coordinators_fte"] > 0, df["teachers_k12_fte"] / df["total_admin_and_coordinators_fte"], np.nan)
    df["teachers_per_building_admin"] = np.where(df["school_administrators_fte"] > 0, df["teachers_k12_fte"] / df["school_administrators_fte"], np.nan)
    df["instructional_share_of_exp"] = np.where(df["exp_total"] > 0, df["exp_current_instruction_total"] / df["exp_total"], np.nan)
    df["admin_overhead_ratio"] = np.where(df["exp_current_instruction_total"] > 0, (df["exp_current_general_admin"] + df["exp_current_sch_admin"]) / df["exp_current_instruction_total"], np.nan)
    df["local_revenue_share"] = np.where(df["rev_total"] > 0, df["rev_local_total"] / df["rev_total"], np.nan)
    df["state_revenue_share"] = np.where(df["rev_total"] > 0, df["rev_state_total"] / df["rev_total"], np.nan)
    df["federal_revenue_share"] = np.where(df["rev_total"] > 0, df["rev_fed_total"] / df["rev_total"], np.nan)

    # Focal Panel Flagging
    df["is_focal_7_panel"] = df["nces_lea_id"].isin(FOCAL_DISTRICTS.keys())
    
    # Map metadata for focal districts
    df["focal_district_code"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["district_code"] if x in FOCAL_DISTRICTS else None)
    df["focal_clean_name"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["district_clean_name"] if x in FOCAL_DISTRICTS else None).fillna(df["district_name"])
    df["union_affiliation"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["union_affiliation"] if x in FOCAL_DISTRICTS else "OTHER")
    df["union_name"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["union_name"] if x in FOCAL_DISTRICTS else None)
    df["governance_model"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["governance_model"] if x in FOCAL_DISTRICTS else None)
    df["key_institutional_feature"] = df["nces_lea_id"].map(lambda x: FOCAL_DISTRICTS[x]["key_institutional_feature"] if x in FOCAL_DISTRICTS else None)

    # Export full regional labor panel
    out_parquet = OUTPUT_DIR / "district_labor_panel.parquet"
    out_csv = OUTPUT_DIR / "district_labor_panel.csv"
    df.to_parquet(out_parquet, index=False)
    df.to_csv(out_csv, index=False)
    print(f"Saved full district labor panel to:\n  - {out_parquet}\n  - {out_csv}")

    # Export focal 7 panel
    df_focal = df[df["is_focal_7_panel"]].copy()
    focal_csv = OUTPUT_DIR / "focal_7_labor_panel.csv"
    df_focal.to_csv(focal_csv, index=False)
    print(f"Saved focal 7 panel ({len(df_focal)} observations) to:\n  - {focal_csv}")

    # Print summary benchmark for latest clean year (2023-2024)
    latest_year = "2023-2024"
    bench = df_focal[df_focal["school_year"] == latest_year][[
        "focal_district_code", "state", "union_affiliation", "enrollment_k12",
        "teachers_k12_fte", "pupil_teacher_ratio", "instructional_coordinators_fte",
        "school_administrators_fte", "local_revenue_share", "state_revenue_share"
    ]].sort_values("enrollment_k12", ascending=False)

    print("\n--- Focal 7 Labor Panel Baseline Snapshot (2023-2024) ---")
    print(bench.to_string(index=False))

if __name__ == "__main__":
    load_and_enrich_panel()
