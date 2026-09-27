"""
Comparative Analysis: South Kansas City Microregion (Grandview C-4, Center 58, Hickman Mills C-1).
Triangulates:
1. DESE ASBR statutory financial filings (FY19 to FY24).
2. Kauffman Foundation Form 990-PF grant disbursements (2019 to 2024).
3. Local absorption, fiscal crowding-in, and budget headroom across peer districts.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")

DISTRICTS = [
    {
        "slug": "grandview-c4",
        "code": "048-074",
        "name": "Grandview C-4",
        "asbr_csv": BASE_DIR / "districts" / "grandview-c4" / "finance" / "grandview_asbr_longitudinal.csv",
        "funding_csv": BASE_DIR / "districts" / "grandview-c4" / "finance" / "grandview_rwl_funding_timeline.csv",
    },
    {
        "slug": "center-58",
        "code": "048-080",
        "name": "Center 58",
        "asbr_csv": BASE_DIR / "districts" / "center-58" / "finance" / "center58_asbr_longitudinal.csv",
        "funding_csv": BASE_DIR / "districts" / "center-58" / "finance" / "center58_rwl_funding_timeline.csv",
    },
    {
        "slug": "hickman-mills",
        "code": "048-072",
        "name": "Hickman Mills C-1",
        "asbr_csv": BASE_DIR / "districts" / "hickman-mills" / "finance" / "hickmanmills_asbr_longitudinal.csv",
        "funding_csv": BASE_DIR / "districts" / "hickman-mills" / "finance" / "hickmanmills_rwl_funding_timeline.csv",
    }
]

def analyze_microregion():
    out_dir = BASE_DIR / "synthesis"
    out_dir.mkdir(parents=True, exist_ok=True)

    combined_rows = []

    for d in DISTRICTS:
        asbr = pd.read_csv(d["asbr_csv"])
        funding = pd.read_csv(d["funding_csv"])

        # Filter direct Kauffman grants to district
        k_grants = funding[(funding["funder"].str.contains("Kauffman")) & (funding["recipient_type"] == "district")].copy()

        # Map tax year to school year
        grant_by_year = {}
        for _, grow in k_grants.iterrows():
            yr_str = str(grow["event_date"])
            if yr_str.isdigit():
                ty = int(yr_str)
                sy_map = {
                    2019: "2018-2019",
                    2020: "2019-2020",
                    2021: "2020-2021",
                    2022: "2021-2022",
                    2023: "2022-2023",
                    2024: "2023-2024",
                }
                sy = sy_map.get(ty)
                if sy:
                    grant_by_year[sy] = {
                        "amount_usd": float(grow["amount_usd"]),
                        "grant_id": str(grow["grant_id"]),
                        "renewal_status": str(grow["renewal_status"])
                    }

        for _, arow in asbr.iterrows():
            sy = arow["school_year"]
            ginfo = grant_by_year.get(sy, {"amount_usd": 0.0, "grant_id": "none", "renewal_status": "none"})
            k_paid = ginfo["amount_usd"]

            cte_1300 = float(arow["career_education_1311_1391"])
            acc_1921 = float(arow["area_career_center_fees_1921"])
            tot_career = cte_1300 + acc_1921
            loc_rev = float(arow["local_revenue_5100s"])
            tot_rev = float(arow["total_revenue_5899"])
            tot_exp = float(arow["total_expenditures_9999"])
            reserves = float(arow["ending_fund_balance_total_3112"])
            av = float(arow["assessed_valuation"])

            ratio = (tot_career / k_paid) if k_paid > 0 else np.nan

            combined_rows.append({
                "district_slug": d["slug"],
                "district_code": d["code"],
                "district_name": d["name"],
                "school_year": sy,
                "assessed_valuation": av,
                "local_tax_revenue_5100s": loc_rev,
                "total_revenue_5899": tot_rev,
                "total_expenditures_9999": tot_exp,
                "ending_fund_balance_total_3112": reserves,
                "internal_cte_instruction_1311_1391": cte_1300,
                "area_career_center_tuition_1921": acc_1921,
                "total_career_connected_spending": tot_career,
                "kauffman_rwl_grant_disbursement": k_paid,
                "kauffman_grant_id": ginfo["grant_id"],
                "kauffman_grant_phase": ginfo["renewal_status"],
                "district_career_to_grant_ratio": round(ratio, 2) if not np.isnan(ratio) else "N/A",
                "career_spending_share_of_exp_pct": round((tot_career / tot_exp) * 100.0, 3) if tot_exp > 0 else 0.0,
                "grant_as_pct_of_career_spending": round((k_paid / tot_career) * 100.0, 1) if tot_career > 0 else 0.0,
                "coding_method": "deterministic_primary_state_statutory_merge"
            })

    comb_df = pd.DataFrame(combined_rows)
    out_csv = out_dir / "south_kc_microregion_comparative_panel.csv"
    comb_df.to_csv(out_csv, index=False)
    print(f"Saved comparative panel to {out_csv} ({len(comb_df)} rows).")

    # Generate Comparative Summary Table
    print("\n======================= COMPARATIVE 6-YEAR TRAJECTORY (FY19 to FY24) =======================")
    summary_records = []
    for dname, group in comb_df.groupby("district_name"):
        fy19 = group[group["school_year"] == "2018-2019"].iloc[0]
        fy24 = group[group["school_year"] == "2023-2024"].iloc[0]

        av_growth = ((fy24["assessed_valuation"] - fy19["assessed_valuation"]) / fy19["assessed_valuation"]) * 100.0
        loc_growth = ((fy24["local_tax_revenue_5100s"] - fy19["local_tax_revenue_5100s"]) / fy19["local_tax_revenue_5100s"]) * 100.0
        cte_growth = ((fy24["internal_cte_instruction_1311_1391"] - fy19["internal_cte_instruction_1311_1391"]) / fy19["internal_cte_instruction_1311_1391"]) * 100.0
        tot_career_growth = ((fy24["total_career_connected_spending"] - fy19["total_career_connected_spending"]) / fy19["total_career_connected_spending"]) * 100.0
        res_growth = ((fy24["ending_fund_balance_total_3112"] - fy19["ending_fund_balance_total_3112"]) / fy19["ending_fund_balance_total_3112"]) * 100.0

        rec = {
            "District": dname,
            "FY19 Assessed Val": f"${fy19['assessed_valuation']:,.0f}",
            "FY24 Assessed Val": f"${fy24['assessed_valuation']:,.0f}",
            "AV Growth": f"{av_growth:+.1f}%",
            "FY19 Local Rev": f"${fy19['local_tax_revenue_5100s']:,.0f}",
            "FY24 Local Rev": f"${fy24['local_tax_revenue_5100s']:,.0f}",
            "Local Rev Growth": f"{loc_growth:+.1f}%",
            "FY19 Career Spending": f"${fy19['total_career_connected_spending']:,.0f}",
            "FY24 Career Spending": f"${fy24['total_career_connected_spending']:,.0f}",
            "Career Growth": f"{tot_career_growth:+.1f}%",
            "FY24 Kauffman Grant": f"${fy24['kauffman_rwl_grant_disbursement']:,.0f}",
            "FY24 Local Career to Grant Ratio": f"{fy24['district_career_to_grant_ratio']}x",
            "FY19 Reserves": f"${fy19['ending_fund_balance_total_3112']:,.0f}",
            "FY24 Reserves": f"${fy24['ending_fund_balance_total_3112']:,.0f}",
            "Reserve Growth": f"{res_growth:+.1f}%"
        }
        summary_records.append(rec)
        print(f"\n[{dname}]")
        print(f"  AV: ${fy19['assessed_valuation']:,.0f} -> ${fy24['assessed_valuation']:,.0f} ({av_growth:+.1f}%)")
        print(f"  Local Revenue: ${fy19['local_tax_revenue_5100s']:,.0f} -> ${fy24['local_tax_revenue_5100s']:,.0f} ({loc_growth:+.1f}%)")
        print(f"  Internal CTE (1300): ${fy19['internal_cte_instruction_1311_1391']:,.0f} -> ${fy24['internal_cte_instruction_1311_1391']:,.0f} ({cte_growth:+.1f}%)")
        print(f"  Total Career Spending: ${fy19['total_career_connected_spending']:,.0f} -> ${fy24['total_career_connected_spending']:,.0f} ({tot_career_growth:+.1f}%)")
        print(f"  FY24 Local-to-Grant Ratio: {fy24['district_career_to_grant_ratio']}x")
        print(f"  Reserves: ${fy19['ending_fund_balance_total_3112']:,.0f} -> ${fy24['ending_fund_balance_total_3112']:,.0f} ({res_growth:+.1f}%)")

    sum_df = pd.DataFrame(summary_records)
    sum_csv = out_dir / "south_kc_microregion_summary_table.csv"
    sum_df.to_csv(sum_csv, index=False)
    print(f"\nSaved summary table to {sum_csv}")

if __name__ == "__main__":
    analyze_microregion()
