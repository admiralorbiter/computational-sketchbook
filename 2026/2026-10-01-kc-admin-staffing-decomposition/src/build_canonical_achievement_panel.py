"""
src/build_canonical_achievement_panel.py

Constructs the canonical student academic achievement panel and recovery dataset
for the 55 balanced Kansas City metropolitan districts across 2018-19 to 2023-24.

Outputs:
1. data/processed/district_achievement_panel.csv (55 districts x 5 years x 2 subjects)
2. data/processed/district_achievement_recovery_wide.csv (55 districts x recovery metrics & architecture predictors)
"""

import numpy as np
import pandas as pd


def load_kansas_data():
    perf = pd.read_csv("data/raw/ks_assessment/ks_assessment_performance.csv")
    part = pd.read_csv("data/raw/ks_assessment/ks_assessment_participation.csv")

    # Filter to District rows (not State)
    dist_perf = perf[perf["org_level"].str.startswith("Dist")].copy()

    # Convert numeric columns
    num_cols = ["pct_level_1", "pct_level_2", "pct_level_3", "pct_level_4", "pct_not_tested"]
    for c in num_cols:
        dist_perf[c] = pd.to_numeric(dist_perf[c], errors="coerce")

    # Performance Index (100 to 450 scale matching MSIP 5 weighting: L1=100, L2=250, L3=375, L4=450)
    dist_perf["performance_index"] = (
        100.0 * dist_perf["pct_level_1"]
        + 250.0 * dist_perf["pct_level_2"]
        + 375.0 * dist_perf["pct_level_3"]
        + 450.0 * dist_perf["pct_level_4"]
    ) / 100.0
    dist_perf["pct_proficient_or_advanced"] = dist_perf["pct_level_3"] + dist_perf["pct_level_4"]

    # Deduplicate in case multiple query years returned the same program year
    dist_perf = dist_perf.sort_values(["usd_code", "subject", "program_year", "query_year_opt"])
    dist_perf = dist_perf.drop_duplicates(subset=["usd_code", "subject", "program_year"], keep="last")

    # Prepare participation
    part["school_year"] = pd.to_numeric(part["school_year"], errors="coerce")
    part["total_tested_n"] = pd.to_numeric(part["total_tested_n"], errors="coerce")
    part["test_pool"] = pd.to_numeric(part["test_pool"], errors="coerce")
    part["part_rate_pct"] = pd.to_numeric(part["part_rate_pct"], errors="coerce")

    # Merge
    merged = pd.merge(
        dist_perf,
        part[["usd_code", "subject", "school_year", "test_pool", "total_tested_n", "part_rate_pct"]],
        left_on=["usd_code", "subject", "program_year"],
        right_on=["usd_code", "subject", "school_year"],
        how="left",
    )

    merged["state"] = "KS"
    merged["school_year"] = merged["program_year"]
    merged["accountable_n"] = merged["test_pool"]
    merged["tested_n"] = merged["total_tested_n"]
    merged["participation_rate"] = merged["part_rate_pct"]

    cols = [
        "nces_lea_id", "state_district_id", "district_name", "state", "school_year",
        "subject", "pct_proficient_or_advanced", "performance_index", "accountable_n",
        "tested_n", "participation_rate", "pct_level_1", "pct_level_2", "pct_level_3", "pct_level_4"
    ]
    merged["state_district_id"] = merged["usd_code"].apply(lambda u: f"D0{u}" if len(str(u)) == 3 else f"D{u}")
    
    # Filter to benchmark years: 2019, 2021, 2022, 2023, 2024
    merged = merged[merged["school_year"].isin([2019, 2021, 2022, 2023, 2024])]
    return merged[[c for c in cols if c in merged.columns]]


def load_missouri_data():
    mo = pd.read_csv("data/raw/mo_assessment/mo_district_assessment_panel.csv")
    mo["pct_proficient_or_advanced"] = pd.to_numeric(mo["pct_proficient_total"], errors="coerce")
    mo["performance_index"] = pd.to_numeric(mo["mpi"], errors="coerce")
    mo["accountable_n"] = pd.to_numeric(mo["accountable_n"], errors="coerce")
    mo["tested_n"] = pd.to_numeric(mo["tested_n"], errors="coerce")
    mo["participation_rate"] = pd.to_numeric(mo["participation_rate"], errors="coerce")
    mo["pct_level_1"] = np.nan
    mo["pct_level_2"] = np.nan
    mo["pct_level_3"] = np.nan
    mo["pct_level_4"] = np.nan

    cols = [
        "nces_lea_id", "state_district_id", "district_name", "state", "school_year",
        "subject", "pct_proficient_or_advanced", "performance_index", "accountable_n",
        "tested_n", "participation_rate", "pct_level_1", "pct_level_2", "pct_level_3", "pct_level_4"
    ]
    return mo[cols]


def compute_standardized_scores(df):
    """
    Standardize achievement scores within each state:
    1. Baseline-anchored z-score: relative to state's 2018-19 mean and std.
    2. Contemporaneous z-score: relative to state's mean and std within year t.
    """
    df = df.copy()

    # Compute 2018-19 state baseline statistics by state and subject
    b_stats = (
        df[df["school_year"] == 2019]
        .groupby(["state", "subject"])["pct_proficient_or_advanced"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "base_mean_2019", "std": "base_std_2019"})
    )

    # Compute contemporaneous state statistics by state, subject, and year
    c_stats = (
        df.groupby(["state", "subject", "school_year"])["pct_proficient_or_advanced"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": "contemp_mean", "std": "contemp_std"})
    )

    df = pd.merge(df, b_stats, on=["state", "subject"], how="left")
    df = pd.merge(df, c_stats, on=["state", "subject", "school_year"], how="left")

    df["z_anchor"] = (df["pct_proficient_or_advanced"] - df["base_mean_2019"]) / df["base_std_2019"]
    df["z_contemp"] = (df["pct_proficient_or_advanced"] - df["contemp_mean"]) / df["contemp_std"]

    return df


def build_recovery_wide(panel_df, arch_df):
    """
    Pivots achievement panel to district level wide format and merges architecture predictors.
    """
    # Filter to 2019 and 2024
    p19 = panel_df[panel_df["school_year"] == 2019].copy()
    p24 = panel_df[panel_df["school_year"] == 2024].copy()

    # Pivot 2019 and 2024 by subject
    piv19 = p19.pivot(index="nces_lea_id", columns="subject", values=["pct_proficient_or_advanced", "z_anchor", "z_contemp", "participation_rate", "tested_n"])
    piv19.columns = [f"{col[0]}_{col[1].lower()}_2019" for col in piv19.columns]

    piv24 = p24.pivot(index="nces_lea_id", columns="subject", values=["pct_proficient_or_advanced", "z_anchor", "z_contemp", "participation_rate", "tested_n"])
    piv24.columns = [f"{col[0]}_{col[1].lower()}_2024" for col in piv24.columns]

    wide = pd.merge(piv19, piv24, left_index=True, right_index=True, how="outer")

    # Composite scores (average of Math and ELA)
    wide["pct_prof_combined_2019"] = (wide["pct_proficient_or_advanced_math_2019"] + wide["pct_proficient_or_advanced_ela_2019"]) / 2.0
    wide["pct_prof_combined_2024"] = (wide["pct_proficient_or_advanced_math_2024"] + wide["pct_proficient_or_advanced_ela_2024"]) / 2.0

    wide["z_anchor_combined_2019"] = (wide["z_anchor_math_2019"] + wide["z_anchor_ela_2019"]) / 2.0
    wide["z_anchor_combined_2024"] = (wide["z_anchor_math_2024"] + wide["z_anchor_ela_2024"]) / 2.0

    wide["z_contemp_combined_2019"] = (wide["z_contemp_math_2019"] + wide["z_contemp_ela_2019"]) / 2.0
    wide["z_contemp_combined_2024"] = (wide["z_contemp_math_2024"] + wide["z_contemp_ela_2024"]) / 2.0

    # Recovery deltas (2024 anchored z minus 2019 anchored z)
    wide["delta_z_recovery_math"] = wide["z_anchor_math_2024"] - wide["z_anchor_math_2019"]
    wide["delta_z_recovery_ela"] = wide["z_anchor_ela_2024"] - wide["z_anchor_ela_2019"]
    wide["delta_z_recovery_combined"] = wide["z_anchor_combined_2024"] - wide["z_anchor_combined_2019"]

    # Percent proficient changes
    wide["delta_pct_prof_math"] = wide["pct_proficient_or_advanced_math_2024"] - wide["pct_proficient_or_advanced_math_2019"]
    wide["delta_pct_prof_ela"] = wide["pct_proficient_or_advanced_ela_2024"] - wide["pct_proficient_or_advanced_ela_2019"]
    wide["delta_pct_prof_combined"] = wide["pct_prof_combined_2024"] - wide["pct_prof_combined_2019"]

    # Extract architecture predictors from arch_df
    # We need: baseline (2018-2019), expansion (2018-2019 -> 2021-2022), endpoint (2023-2024), and pandemic mean residual
    arch19 = arch_df[arch_df["school_year"] == "2018-2019"].set_index("nces_lea_id")
    arch22 = arch_df[arch_df["school_year"] == "2021-2022"].set_index("nces_lea_id")
    arch24 = arch_df[arch_df["school_year"] == "2023-2024"].set_index("nces_lea_id")

    # Pandemic residuals (2019-2020, 2020-2021, 2021-2022, 2022-2023)
    pan_years = ["2019-2020", "2020-2021", "2021-2022", "2022-2023"]
    pan_resid = (
        arch_df[arch_df["school_year"].isin(pan_years)]
        .groupby("nces_lea_id")["corsup_stud_resid"]
        .mean()
        .rename("mean_corsup_resid_2020_2023")
    )

    wide = wide.join(pan_resid)

    # Architecture features
    wide["district_name"] = arch19["district_name"]
    wide["state"] = arch19["state"]
    wide["enrollment_2019"] = arch19["enrollment_total"]
    wide["log_enrollment_2019"] = np.log(arch19["enrollment_total"])
    wide["teachers_k12_fte_2019"] = arch19["teachers_k12_fte"]
    wide["architecture_quadrant"] = arch19["architecture_quadrant"]

    wide["corsup_intensity_2019"] = arch19["corsup_per_100_teachers"]
    wide["corsup_intensity_2022"] = arch22["corsup_per_100_teachers"]
    wide["corsup_intensity_2024"] = arch24["corsup_per_100_teachers"]

    wide["delta_corsup_2019_to_2022"] = wide["corsup_intensity_2022"] - wide["corsup_intensity_2019"]
    wide["delta_corsup_2019_to_2024"] = wide["corsup_intensity_2024"] - wide["corsup_intensity_2019"]

    wide["schadm_intensity_2019"] = arch19["schadm_per_school"]
    wide["schadm_intensity_2024"] = arch24["schadm_per_school"]
    wide["delta_schadm_2019_to_2024"] = wide["schadm_intensity_2024"] - wide["schadm_intensity_2019"]

    wide["leaadm_intensity_2019"] = arch19["leaadm_per_1000_pupils"]
    wide["supervisory_intensity_2019"] = arch19["supervisory_per_100_teachers"]

    # Minimum participation rate guardrail flags
    wide["min_part_rate_2024"] = wide[["participation_rate_math_2024", "participation_rate_ela_2024"]].min(axis=1)
    wide["part_ge_90_flag"] = (wide["min_part_rate_2024"] >= 90.0) | wide["min_part_rate_2024"].isna()
    wide["part_ge_95_flag"] = (wide["min_part_rate_2024"] >= 95.0) | wide["min_part_rate_2024"].isna()

    return wide.reset_index()


def main():
    print("Loading Kansas assessment data...")
    ks = load_kansas_data()
    print(f"  Loaded {len(ks)} Kansas records across {ks['nces_lea_id'].nunique()} districts")

    print("Loading Missouri assessment data...")
    mo = load_missouri_data()
    print(f"  Loaded {len(mo)} Missouri records across {mo['nces_lea_id'].nunique()} districts")

    # Combine
    combined = pd.concat([ks, mo], ignore_index=True)
    print(f"Combined assessment records: {len(combined)} across {combined['nces_lea_id'].nunique()} districts")

    # Standardize
    standardized = compute_standardized_scores(combined)
    panel_out = "data/processed/district_achievement_panel.csv"
    standardized.to_csv(panel_out, index=False)
    print(f"Saved standardized achievement panel to {panel_out}")

    # Build Wide Recovery Dataset
    arch_df = pd.read_csv("data/processed/district_architecture_panel.csv")
    wide = build_recovery_wide(standardized, arch_df)
    wide_out = "data/processed/district_achievement_recovery_wide.csv"
    wide.to_csv(wide_out, index=False)
    print(f"Saved wide achievement recovery dataset to {wide_out} ({len(wide)} districts x {len(wide.columns)} columns)")

    # Print summary of focal archetypes
    focal_ids = [2011640, 2007950, 2010140, 2918300, 2922800, 2926070]
    focal = wide[wide["nces_lea_id"].isin(focal_ids)][
        ["nces_lea_id", "district_name", "state", "z_anchor_combined_2019", "z_anchor_combined_2024",
         "delta_z_recovery_combined", "corsup_intensity_2019", "delta_corsup_2019_to_2022", "delta_corsup_2019_to_2024"]
    ]
    print("\n=== Focal Archetypes Achievement Recovery Summary ===")
    print(focal.to_string(index=False))


if __name__ == "__main__":
    main()
