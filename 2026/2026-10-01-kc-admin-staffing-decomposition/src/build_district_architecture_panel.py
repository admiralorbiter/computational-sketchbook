"""
src/build_district_architecture_panel.py

Phase 6A: Regional Architecture Map.
Constructs the continuous organizational architecture panel for all 55 balanced districts
from 2014-15 through 2023-24 (550 district-years).

Translates categorical archetypes into continuous coordinate space:
1. corsup_per_100_teachers & peer-adjusted corsup_resid_rate (Model 3)
2. schadm_per_school & peer-adjusted schadm_resid_rate (Model 1)
3. leaadm_per_1000_pupils & peer-adjusted leaadm_resid_rate (Model 2)
4. supervisory_per_100_teachers & broad supervisory footprint (Model 4)
5. Continuous quadrant typologies across 4 snapshot benchmark years (2014-15, 2018-19, 2020-21, 2023-24).
"""

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"


def build_architecture_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    staff_path = DATA_PROCESSED / "district_staff_year.csv"
    res_path = OUTPUTS_TABLES / "peer_expected_staffing_residuals.csv"

    df_staff = pd.read_csv(staff_path)
    df_res = pd.read_csv(res_path)

    # Filter to balanced 55 cohort across the 10-year study window (2014-15 to 2023-24)
    b55_staff = df_staff[
        (df_staff["is_balanced_presence_cohort_55"] == 1) &
        (df_staff["school_year"] >= "2014-2015") &
        (df_staff["school_year"] <= "2023-2024")
    ].copy()

    # Pivot peer model residuals and predictions
    model_map = {
        "Model 1: SCHADM (Peer)": "schadm",
        "Model 2: LEAADM (Peer)": "leaadm",
        "Model 3: CORSUP (Peer)": "corsup",
        "Model 4: Central+Coord Footprint (Peer)": "footprint"
    }
    df_res["prefix"] = df_res["model_name"].map(model_map)

    res_pivot = df_res.pivot(
        index=["school_year", "nces_lea_id"],
        columns="prefix",
        values=["pred_peer", "residual_peer", "stud_resid", "resid_rate"]
    )
    res_pivot.columns = [f"{col[1]}_{col[0]}" for col in res_pivot.columns]
    res_pivot = res_pivot.reset_index()

    # Merge staffing and residuals
    panel = pd.merge(
        b55_staff,
        res_pivot,
        on=["school_year", "nces_lea_id"],
        how="left"
    )

    # Calculate raw structural rates
    panel["corsup_per_100_teachers"] = (
        panel["instructional_coordinators_fte"] / panel["teachers_k12_fte"] * 100.0
    ).round(4)

    panel["schadm_per_school"] = (
        panel["school_administrators_fte"] / panel["operating_schools_count"]
    ).round(4)

    panel["leaadm_per_1000_pupils"] = (
        panel["lea_administrators_fte"] / panel["enrollment_total"] * 1000.0
    ).round(4)

    panel["supervisory_per_100_teachers"] = (
        panel["central_mgmt_and_coordinators_fte"] / panel["teachers_k12_fte"] * 100.0
    ).round(4)

    # Classify empirical typology quadrant based on peer-expected residuals
    def assign_typology(row):
        c_res = row.get("corsup_resid_rate")
        s_res = row.get("schadm_resid_rate")
        if pd.isna(c_res) or pd.isna(s_res):
            # Fallback to sample median rates if peer residual is unavailable (e.g. KS 2015-16 reconstruction)
            return "Unassigned Baseline"
        if c_res > 0 and s_res > 0:
            return "Dual-Intensity (Coaching + School Supervision)"
        elif c_res > 0 and s_res <= 0:
            return "Coaching Overlay"
        elif c_res <= 0 and s_res > 0:
            return "Direct School Supervision"
        else:
            return "Lean / Department Chair"

    panel["architecture_quadrant"] = panel.apply(assign_typology, axis=1)

    # Select and order final canonical columns
    cols = [
        "school_year",
        "nces_lea_id",
        "district_name",
        "state",
        "enrollment_total",
        "operating_schools_count",
        "teachers_k12_fte",
        "teachers_total_reported_fte",
        "instructional_coordinators_fte",
        "school_administrators_fte",
        "lea_administrators_fte",
        "central_mgmt_and_coordinators_fte",
        "corsup_per_100_teachers",
        "schadm_per_school",
        "leaadm_per_1000_pupils",
        "supervisory_per_100_teachers",
        "corsup_pred_peer",
        "corsup_residual_peer",
        "corsup_stud_resid",
        "corsup_resid_rate",
        "schadm_pred_peer",
        "schadm_residual_peer",
        "schadm_stud_resid",
        "schadm_resid_rate",
        "leaadm_pred_peer",
        "leaadm_residual_peer",
        "leaadm_stud_resid",
        "leaadm_resid_rate",
        "footprint_pred_peer",
        "footprint_residual_peer",
        "footprint_stud_resid",
        "footprint_resid_rate",
        "architecture_quadrant"
    ]

    panel_clean = panel[cols].sort_values(["school_year", "state", "district_name"]).reset_index(drop=True)

    # Construct snapshots dataset for 4 benchmark years
    benchmark_years = ["2014-2015", "2018-2019", "2020-2021", "2023-2024"]
    snapshots = panel_clean[panel_clean["school_year"].isin(benchmark_years)].copy()

    return panel_clean, snapshots


def main():
    print("Building Phase 6A: Regional Architecture Map...")
    panel, snapshots = build_architecture_panel()

    out_panel_path = DATA_PROCESSED / "district_architecture_panel.csv"
    out_snap_path = OUTPUTS_TABLES / "district_architecture_snapshots.csv"

    panel.to_csv(out_panel_path, index=False)
    snapshots.to_csv(out_snap_path, index=False)

    print(f"Saved complete 55-district architecture panel to {out_panel_path} ({len(panel)} rows)")
    print(f"Saved 4-benchmark snapshots to {out_snap_path} ({len(snapshots)} rows)")

    # Print summary of typology transitions
    print("\nArchitecture Quadrant Distribution Across Benchmark Years:")
    print(pd.crosstab(snapshots["school_year"], snapshots["architecture_quadrant"]))


if __name__ == "__main__":
    main()
