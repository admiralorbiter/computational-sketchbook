"""
Update data/manifest.csv with calibrated hashes, row counts, and new artifacts.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def update_manifest():
    manifest_path = ROOT / "data" / "manifest.csv"
    manifest_df = pd.read_csv(manifest_path)
    
    now_utc = datetime.now(timezone.utc).isoformat()
    
    files_to_track = [
        {
            "dataset_name": "district_staff_year",
            "relative_path": "data/processed/district_staff_year.csv",
            "calibration_phase": "Phase 1.1 Final Calibrated Patch",
            "format": "csv / parquet",
            "years_covered": "2004-2005 to 2024-2025",
            "district_count": 84,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "district_demand_year",
            "relative_path": "data/processed/district_demand_year.csv",
            "calibration_phase": "Phase 2A Demand & Finance Ingestion",
            "format": "csv / parquet",
            "years_covered": "2004-2005 to 2024-2025",
            "district_count": 84,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "compensation_benchmarks",
            "relative_path": "data/processed/compensation_benchmarks.csv",
            "calibration_phase": "Phase 4 Compensation Provenance",
            "format": "csv",
            "years_covered": "2023-2024",
            "district_count": "N/A",
            "balanced_presence_cohort_55": "N/A",
            "complete_outcome_cohort_53": "N/A"
        },
        {
            "dataset_name": "phase3_claim_evidence",
            "relative_path": "outputs/tables/phase3_claim_evidence.csv",
            "calibration_phase": "Phase 3 Board Qualitative Audit",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 4,
            "balanced_presence_cohort_55": "N/A",
            "complete_outcome_cohort_53": "N/A"
        },
        {
            "dataset_name": "long_difference_regression_results",
            "relative_path": "outputs/tables/long_difference_regression_results.csv",
            "calibration_phase": "Phase 2B Long-Difference Growth Model",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "shapley_decomposition_results",
            "relative_path": "outputs/tables/shapley_decomposition_results.csv",
            "calibration_phase": "Phase 2C Shapley Growth Decomposition",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "model_regression_results",
            "relative_path": "outputs/tables/model_regression_results.csv",
            "calibration_phase": "Phase 2B Econometric Demand Models",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "peer_expected_staffing_residuals",
            "relative_path": "outputs/tables/peer_expected_staffing_residuals.csv",
            "calibration_phase": "Phase 2B Peer Expected Models",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "persistent_peer_outliers",
            "relative_path": "outputs/tables/persistent_peer_outliers.csv",
            "calibration_phase": "Phase 2B Peer Outliers",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 4,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "fiscal_materiality_counterfactuals",
            "relative_path": "outputs/tables/fiscal_materiality_counterfactuals.csv",
            "calibration_phase": "Phase 4 Fiscal Materiality Simulation",
            "format": "csv",
            "years_covered": "2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "fiscal_materiality_annual_trajectory",
            "relative_path": "outputs/tables/fiscal_materiality_annual_trajectory.csv",
            "calibration_phase": "Phase 4 Fiscal Materiality Simulation",
            "format": "csv",
            "years_covered": "2014-2015 to 2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        },
        {
            "dataset_name": "fiscal_materiality_peer_summary",
            "relative_path": "outputs/tables/fiscal_materiality_peer_summary.csv",
            "calibration_phase": "Phase 4 Fiscal Materiality Simulation",
            "format": "csv",
            "years_covered": "2023-2024",
            "district_count": 55,
            "balanced_presence_cohort_55": 55,
            "complete_outcome_cohort_53": 53
        }
    ]
    
    rows = []
    for item in files_to_track:
        fp = ROOT / item["relative_path"]
        if fp.exists():
            df_curr = pd.read_csv(fp)
            rows_count = len(df_curr)
            cols_count = len(df_curr.columns)
            sha256 = compute_sha256(fp)
        else:
            rows_count = "N/A"
            cols_count = "N/A"
            sha256 = "MISSING"
            
        rows.append({
            "dataset_name": item["dataset_name"],
            "relative_path": item["relative_path"],
            "rows_count": rows_count,
            "columns_count": cols_count,
            "years_covered": item["years_covered"],
            "district_count": item["district_count"],
            "balanced_presence_cohort_55": item["balanced_presence_cohort_55"],
            "complete_outcome_cohort_53": item["complete_outcome_cohort_53"],
            "sha256": sha256,
            "calibration_phase": item["calibration_phase"],
            "created_at_utc": now_utc,
            "format": item["format"]
        })
        
    updated_df = pd.DataFrame(rows)
    updated_df.to_csv(manifest_path, index=False)
    print(f"Updated {manifest_path} with {len(updated_df)} artifacts.")

if __name__ == "__main__":
    update_manifest()
