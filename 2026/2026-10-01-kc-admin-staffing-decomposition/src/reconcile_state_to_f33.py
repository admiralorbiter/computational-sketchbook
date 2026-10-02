"""
Reconciliation between State Object-Level Accounting (MO ASBR Part III-B / KS Form USD-E)
and Federal NCES F-33 Annual Survey of School System Finances for Function 2200.
Generates outputs/tables/phase6c2_focal_reconciliation_to_f33.csv.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from src.parse_ks_budget_focal import parse_ks_file
from src.parse_mo_asbr_focal import parse_all_mo_asbr

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUTS_DIR = BASE_DIR / "outputs" / "tables"

focal_ids = {
    "Shawnee Mission USD 512": 2011640,
    "Olathe USD 233": 2010140,
    "Kansas City USD 500": 2007950,
    "Lee's Summit R-VII": 2918300,
    "North Kansas City 74": 2922800,
    "Raytown C-2": 2926070,
}

def generate_reconciliation():
    df_f33 = pd.read_csv(PROCESSED_DIR / "district_fiscal_support_panel.csv")
    reconcil_records = []

    # 1. Missouri Districts from ASBR
    df_mo = parse_all_mo_asbr()
    for _, r in df_mo.iterrows():
        dname = r["district_name"]
        sy = r["school_year"]
        nid = focal_ids[dname]
        f33_row = df_f33[(df_f33["nces_lea_id"] == nid) & (df_f33["school_year"] == sy)].iloc[0]
        
        sal_state = r["nom_salaries_total"]
        ben_state = r["nom_benefits_6200"]
        cap_state = r["nom_capital_outlay_6500"]
        np_all_state = r["nom_nonpersonnel_support_total"]
        np_comp_state = np_all_state - cap_state
        tot_all_state = r["nom_total_support_2200"]
        tot_comp_state = tot_all_state - cap_state
        
        f33_e07 = f33_row["instr_support_total_e07"]
        f33_v13 = f33_row["instr_support_salary_v13"]
        f33_v14 = f33_row["instr_support_benefits_v14"]
        f33_np = f33_row["instr_support_nonpersonnel"]
        
        reconcil_records.append({
            "district_name": dname,
            "state": "MO",
            "nces_lea_id": nid,
            "school_year": sy,
            "state_salaries": sal_state,
            "f33_v13_salaries": f33_v13,
            "diff_salaries": sal_state - f33_v13,
            "state_benefits": ben_state,
            "f33_v14_benefits": f33_v14,
            "diff_benefits": ben_state - f33_v14,
            "state_capital_outlay": cap_state,
            "state_np_allobjects": np_all_state,
            "state_np_f33comp": np_comp_state,
            "f33_nonpersonnel": f33_np,
            "diff_nonpersonnel_comp_vs_f33": np_comp_state - f33_np,
            "state_total_allobjects": tot_all_state,
            "state_total_current_2200": tot_comp_state,
            "f33_e07_total": f33_e07,
            "diff_total_current_vs_e07": tot_comp_state - f33_e07,
        })

    # 2. Kansas Districts from Form USD-E
    ks_files = [
        ("Shawnee Mission USD 512", "shawnee_mission", "512", [("2014-2015", "2016", "2015"), ("2018-2019", "2020", "2019"), ("2022-2023", "2024", "2023")]),
        ("Olathe USD 233", "olathe", "233", [("2014-2015", "2016", "2015"), ("2018-2019", "2020", "2019"), ("2022-2023", "2024", "2023")]),
        ("Kansas City USD 500", "kansas_city", "500", [("2014-2015", "2016", "2015"), ("2018-2019", "2020", "2019"), ("2022-2023", "2024", "2023")]),
    ]

    for dname, slug, uid, ylist in ks_files:
        nid = focal_ids[dname]
        for sy, cyr, ayr in ylist:
            fpath = BASE_DIR / "data" / "raw" / "kansas_budget" / slug / f"{uid}_Codes{cyr}_Actuals{ayr}.pdf"
            totals, _ = parse_ks_file(fpath, target_col_idx=1)
            f33_row = df_f33[(df_f33["nces_lea_id"] == nid) & (df_f33["school_year"] == sy)].iloc[0]
            
            sal_state = totals["sal_certified"] + totals["sal_noncertified"]
            ben_state = totals["benefits_insurance"] + totals["benefits_socsec"] + totals["benefits_other"]
            cap_state = totals["property_700"]
            
            p300 = totals["purchased_prof_300"]
            p450 = totals["purchased_prop_400"] + totals["other_purch_500"]
            s600 = totals["supplies_books_640"] + totals["supplies_tech_650"] + totals["supplies_misc_680"]
            o800 = totals["other_800"]
            
            np_all_state = p300 + p450 + s600 + cap_state + o800
            np_comp_state = p300 + p450 + s600 + o800
            tot_all_state = sal_state + ben_state + np_all_state
            tot_comp_state = sal_state + ben_state + np_comp_state
            
            f33_e07 = f33_row["instr_support_total_e07"]
            f33_v13 = f33_row["instr_support_salary_v13"]
            f33_v14 = f33_row["instr_support_benefits_v14"]
            f33_np = f33_row["instr_support_nonpersonnel"]
            
            reconcil_records.append({
                "district_name": dname,
                "state": "KS",
                "nces_lea_id": nid,
                "school_year": sy,
                "state_salaries": sal_state,
                "f33_v13_salaries": f33_v13,
                "diff_salaries": sal_state - f33_v13,
                "state_benefits": ben_state,
                "f33_v14_benefits": f33_v14,
                "diff_benefits": ben_state - f33_v14,
                "state_capital_outlay": cap_state,
                "state_np_allobjects": np_all_state,
                "state_np_f33comp": np_comp_state,
                "f33_nonpersonnel": f33_np,
                "diff_nonpersonnel_comp_vs_f33": np_comp_state - f33_np,
                "state_total_allobjects": tot_all_state,
                "state_total_current_2200": tot_comp_state,
                "f33_e07_total": f33_e07,
                "diff_total_current_vs_e07": tot_comp_state - f33_e07,
            })

    df_out = pd.DataFrame(reconcil_records)
    # Sort deterministically
    df_out = df_out.sort_values(["state", "district_name", "school_year"]).reset_index(drop=True)
    out_csv = OUTPUTS_DIR / "phase6c2_focal_reconciliation_to_f33.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"Saved reconciliation table to {out_csv} ({len(df_out)} rows)")
    return df_out

if __name__ == "__main__":
    df = generate_reconciliation()
    cols = ["district_name", "school_year", "state_salaries", "f33_v13_salaries", "state_benefits", "f33_v14_benefits", "state_capital_outlay", "state_np_f33comp", "f33_nonpersonnel", "diff_total_current_vs_e07"]
    print(df[cols].to_string(index=False))
