#!/usr/bin/env python3
"""
Task 003 Cross-Stream Synthesis: Grandview C-4 Empirical Trajectory Analysis.
Integrates:
1. Kauffman Foundation Form 990-PF grant disbursements (2019-2024).
2. DESE Annual Secretary of the Board Reports (ASBR FY19-FY24).
3. Longitudinal Staff Directory Panel (2019-2026).
4. Board Governance & Priority Meeting Records (2024-2026).
5. CTE & Pathway Operations Agreements.

Maintains strict epistemic boundaries: zero composite scoring formulas,
zero subjective sentiment classification, strictly observable metrics.
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

def run_synthesis():
    base_dir = Path("2026/2026-09-26-rwl-institutionalization")
    dist_dir = base_dir / "districts" / "grandview-c4"
    synthesis_dir = dist_dir / "synthesis"
    synthesis_dir.mkdir(parents=True, exist_ok=True)

    print("=== Loading Primary Datasets ===")
    asbr_path = dist_dir / "finance" / "grandview_asbr_longitudinal.csv"
    funding_path = dist_dir / "finance" / "grandview_rwl_funding_timeline.csv"
    staff_path = dist_dir / "organization" / "staff_directory_longitudinal.csv"
    agreements_path = dist_dir / "operations" / "pathway_and_cte_agreements.csv"
    governance_path = dist_dir / "governance" / "priority_meeting_items.csv"

    asbr_df = pd.read_csv(asbr_path)
    funding_df = pd.read_csv(funding_path)
    staff_df = pd.read_csv(staff_path)
    agreements_df = pd.read_csv(agreements_path)
    gov_df = pd.read_csv(governance_path)

    print(f"ASBR Rows: {len(asbr_df)}")
    print(f"Funding Rows: {len(funding_df)}")
    print(f"Staff Records: {len(staff_df)}")
    print(f"Agreements: {len(agreements_df)}")
    print(f"Priority Gov Items: {len(gov_df)}")

    # 1. Map Kauffman direct grants to school years
    # Kauffman Form 990-PF reports on calendar tax year ending Dec 31
    # TY2019: $70,435 -> SY 2018-2019 / 2019-2020 planning
    # TY2020: $150,000 -> SY 2019-2020 / 2020-2021 implementation 1
    # TY2021: $150,000 -> SY 2020-2021 / 2021-2022 implementation 1 tranche 2
    # TY2022: $0 -> SY 2021-2022 / 2022-2023 gap year
    # TY2023: $135,000 -> SY 2022-2023 / 2023-2024 implementation 2
    # TY2024: $135,000 -> SY 2023-2024 / 2024-2025 implementation 2 tranche 2
    
    grant_schedule = {
        "2018-2019": {
            "kauffman_disbursement_usd": 70435.0,
            "kauffman_grant_id": "201904-6368",
            "kauffman_grant_phase": "Design & Planning",
            "kauffman_irs_tax_year": 2019,
            "kauffman_future_approved_usd": 0.0
        },
        "2019-2020": {
            "kauffman_disbursement_usd": 150000.0,
            "kauffman_grant_id": "202007-8824",
            "kauffman_grant_phase": "Implementation Phase 1 Tranche 1",
            "kauffman_irs_tax_year": 2020,
            "kauffman_future_approved_usd": 0.0
        },
        "2020-2021": {
            "kauffman_disbursement_usd": 150000.0,
            "kauffman_grant_id": "202007-8824",
            "kauffman_grant_phase": "Implementation Phase 1 Tranche 2",
            "kauffman_irs_tax_year": 2021,
            "kauffman_future_approved_usd": 0.0
        },
        "2021-2022": {
            "kauffman_disbursement_usd": 0.0,
            "kauffman_grant_id": "none",
            "kauffman_grant_phase": "Interim Absorption Gap Year",
            "kauffman_irs_tax_year": 2022,
            "kauffman_future_approved_usd": 0.0
        },
        "2022-2023": {
            "kauffman_disbursement_usd": 135000.0,
            "kauffman_grant_id": "202307-14162",
            "kauffman_grant_phase": "Implementation Phase 2 Tranche 1",
            "kauffman_irs_tax_year": 2023,
            "kauffman_future_approved_usd": 135000.0
        },
        "2023-2024": {
            "kauffman_disbursement_usd": 135000.0,
            "kauffman_grant_id": "202307-14162",
            "kauffman_grant_phase": "Implementation Phase 2 Tranche 2 (Final)",
            "kauffman_irs_tax_year": 2024,
            "kauffman_future_approved_usd": 0.0
        }
    }

    # Synthesize Financial Panel
    panel_rows = []
    for _, row in asbr_df.iterrows():
        sy = row["school_year"]
        g = grant_schedule.get(sy, {})
        k_paid = g.get("kauffman_disbursement_usd", 0.0)
        cte_1300 = float(row["career_education_1311_1391"])
        acc_1921 = float(row["area_career_center_fees_1921"])
        total_career_spending = cte_1300 + acc_1921
        local_rev = float(row["local_revenue_5100s"])
        total_rev = float(row["total_revenue_5899"])
        total_exp = float(row["total_expenditures_9999"])
        ending_bal = float(row["ending_fund_balance_total_3112"])
        av = float(row["assessed_valuation"])

        ratio = (total_career_spending / k_paid) if k_paid > 0 else np.nan
        cte_pct_exp = (total_career_spending / total_exp) * 100.0
        grant_pct_career = (k_paid / total_career_spending * 100.0) if total_career_spending > 0 else 0.0

        panel_rows.append({
            "school_year": sy,
            "assessed_valuation": av,
            "local_tax_revenue_5100s": local_rev,
            "total_revenue_5899": total_rev,
            "total_expenditures_9999": total_exp,
            "ending_fund_balance_total_3112": ending_bal,
            "career_education_instruction_1311_1391": cte_1300,
            "area_career_center_tuition_1921": acc_1921,
            "total_career_connected_spending": total_career_spending,
            "kauffman_grant_disbursement_usd": k_paid,
            "kauffman_grant_id": g.get("kauffman_grant_id", "none"),
            "kauffman_grant_phase": g.get("kauffman_grant_phase", "none"),
            "kauffman_future_approved_usd": g.get("kauffman_future_approved_usd", 0.0),
            "ratio_district_career_to_kauffman_grant": round(ratio, 2) if not np.isnan(ratio) else "N/A",
            "career_spending_share_of_budget_pct": round(cte_pct_exp, 3),
            "grant_as_pct_of_career_spending": round(grant_pct_career, 1),
            "grant_regime": row["grant_regime"],
            "coding_method": "deterministic_primary_cross_stream_merge"
        })

    synthesis_panel_df = pd.DataFrame(panel_rows)
    synthesis_csv_path = synthesis_dir / "grandview_cross_stream_synthesis_panel.csv"
    synthesis_panel_df.to_csv(synthesis_csv_path, index=False)
    print(f"Saved synthesis panel: {synthesis_csv_path}")

    # 2. Staffing panel trajectory summary
    # Group by school year and key positions
    staff_summary = []
    for sy, group in staff_df.groupby("school_year"):
        ci_leaders = group[group["job_title"].str.contains("Curriculum", case=False, na=False)]["staff_name"].unique().tolist()
        supt = group[group["job_title"] == "Superintendent"]["staff_name"].unique().tolist()
        hr_asst = group[group["job_title"].str.contains("Assistant Superintendent of Human Resources", case=False, na=False)]["staff_name"].unique().tolist()
        total_titles = group["job_title"].nunique()
        total_staff_entries = len(group)
        staff_summary.append({
            "school_year": sy,
            "total_directory_entries": total_staff_entries,
            "unique_job_titles": total_titles,
            "superintendent": "; ".join(supt) if supt else "Vacant / Unlisted",
            "curriculum_instruction_leadership": "; ".join(ci_leaders) if ci_leaders else "Vacant / Unlisted",
            "human_resources_leadership": "; ".join(hr_asst) if hr_asst else "Vacant / Unlisted"
        })
    staff_summary_df = pd.DataFrame(staff_summary)
    staff_summary_path = synthesis_dir / "grandview_leadership_trajectory.csv"
    staff_summary_df.to_csv(staff_summary_path, index=False)
    print(f"Saved leadership trajectory: {staff_summary_path}")

    print("\n=== FISCAL SUBSTITUTION VS ABSORPTION FINDINGS ===")
    for row in panel_rows:
        print(f"SY {row['school_year']}: District Career Spending = ${row['total_career_connected_spending']:,.0f} | Kauffman Grant = ${row['kauffman_grant_disbursement_usd']:,.0f} | Ratio = {row['ratio_district_career_to_kauffman_grant']} | Reserve Bal = ${row['ending_fund_balance_total_3112']:,.0f}")

    print("\n=== EXECUTIVE LEADERSHIP TRAJECTORY ===")
    for row in staff_summary:
        print(f"SY {row['school_year']}: Supt: {row['superintendent']} | C&I: {row['curriculum_instruction_leadership']} | HR: {row['human_resources_leadership']}")

if __name__ == "__main__":
    run_synthesis()
