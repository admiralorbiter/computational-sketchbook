"""
Gate 6C.2: State Object-Level Mechanism Audit Panel Builder.
Consolidates audited statutory object-level accounting records across the six focal archetypes:
- Kansas (KSDE Form USD-E Codes Actuals): Shawnee Mission USD 512, Olathe USD 233, Kansas City USD 500
- Missouri (DESE ASBR statutory workbooks Part III-B): Lee's Summit R-VII, North Kansas City 74, Raytown C-2
Benchmark years: 2014-15, 2018-19, 2022-23.

Provides dual non-personnel measures:
1. NP_allobjects: All objects including capital outlay (KS Object 700 / MO Object 6500)
2. NP_f33comp: F-33-comparable current operating expenditures (excluding capital outlay)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
from src.parse_mo_asbr_focal import parse_all_mo_asbr
from src.parse_ks_budget_focal import parse_ks_file

RAW_KS_DIR = BASE_DIR / "data" / "raw" / "kansas_budget"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "outputs" / "tables"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

CPI_DEFLATORS = {
    "2014-2015": 1.2307,
    "2018-2019": 1.1578,
    "2022-2023": 1.0000,
}

KS_DISTRICTS = [
    {
        "district_name": "Shawnee Mission USD 512",
        "state": "KS",
        "nces_lea_id": 2011640,
        "state_id": "USD 512",
        "archetype": "Coaching Overlay",
        "slug": "shawnee_mission",
        "uid": "512",
        "years": [
            ("2014-2015", "2016", "2015", 27.6, 27461),
            ("2018-2019", "2020", "2019", 46.5, 27725),
            ("2022-2023", "2024", "2023", 93.0, 26084),
        ]
    },
    {
        "district_name": "Olathe USD 233",
        "state": "KS",
        "nces_lea_id": 2010140,
        "state_id": "USD 233",
        "archetype": "Lean / Department Chair",
        "slug": "olathe",
        "uid": "233",
        "years": [
            ("2014-2015", "2016", "2015", 31.9, 29119),
            ("2018-2019", "2020", "2019", 39.3, 30129),
            ("2022-2023", "2024", "2023", 67.8, 30171),
        ]
    },
    {
        "district_name": "Kansas City USD 500",
        "state": "KS",
        "nces_lea_id": 2007950,
        "state_id": "USD 500",
        "archetype": "Dual-Intensity (Coaching + School Supervision)",
        "slug": "kansas_city",
        "uid": "500",
        "years": [
            ("2014-2015", "2016", "2015", 106.9, 21545),
            ("2018-2019", "2020", "2019", 99.6, 22449),
            ("2022-2023", "2024", "2023", 112.5, 21976),
        ]
    },
]

# Note: Raytown NCES ID is 2926070 (canonical throughout study)
MO_ARCHETYPES = {
    "Lee's Summit R-VII": ("Direct School Supervision", 2918300),
    "North Kansas City 74": ("Direct School Supervision", 2922800),
    "Raytown C-2": ("Coaching Overlay", 2926070),
}


def build_focal_object_panel():
    print("Building Gate 6C.2 State Object-Level Support Panel...")
    records = []

    # 1. Process Missouri records from ASBR
    df_mo = parse_all_mo_asbr()
    for _, row in df_mo.iterrows():
        dname = row["district_name"]
        arch, nces_id = MO_ARCHETYPES.get(dname, ("Unknown", 0))
        sy = row["school_year"]
        cpi = CPI_DEFLATORS[sy]
        enr = row["enrollment"]

        sal = row["nom_salaries_total"]
        ben = row["nom_benefits_6200"]
        p300_6300 = row["nom_purchased_services_6300"]
        s600_6400 = row["nom_supplies_materials_6400"]
        cap_6500 = row["nom_capital_outlay_6500"]
        oth_6600 = row["nom_other_objects_6600"]
        np_all = row["nom_nonpersonnel_support_total"]
        np_f33comp = np_all - cap_6500
        tot_all = row["nom_total_support_2200"]
        tot_f33comp = tot_all - cap_6500

        rec = {
            "district_name": dname,
            "state": "MO",
            "nces_lea_id": nces_id,
            "state_id": row["dese_code"],
            "organizational_archetype": arch,
            "school_year": sy,
            "enrollment": enr,
            "corsup_fte": row["corsup_fte"],
            "corsup_per_1000_pupils": row["corsup_per_1000_pupils"],
            # Nominal amounts
            "nom_salaries": sal,
            "nom_benefits": ben,
            "nom_purchased_prof_tech_or_services": p300_6300,
            "nom_other_purchased_services": 0.0,
            "nom_supplies_materials": s600_6400,
            "nom_capital_outlay": cap_6500,
            "nom_other_objects": oth_6600,
            "nom_nonpersonnel_allobjects": np_all,
            "nom_nonpersonnel_f33comp": np_f33comp,
            "nom_nonpersonnel_total": np_all,  # backward compatibility alias
            "nom_total_support_allobjects": tot_all,
            "nom_total_support_f33comp": tot_f33comp,
            "nom_total_support_2200": tot_all,  # backward compatibility alias
            # Real Per-Pupil Amounts (Constant 2023 Dollars)
            "real_salaries_per_pupil": row["real_salaries_per_pupil"],
            "real_benefits_per_pupil": row["real_benefits_per_pupil"],
            "real_purchased_prof_tech_per_pupil": row["real_purchased_services_6300_per_pupil"],
            "real_other_purchased_services_per_pupil": 0.0,
            "real_supplies_materials_per_pupil": row["real_supplies_materials_6400_per_pupil"],
            "real_capital_outlay_per_pupil": row["real_capital_outlay_6500_per_pupil"],
            "real_nonpersonnel_allobjects_per_pupil": row["real_nonpersonnel_support_per_pupil"],
            "real_nonpersonnel_f33comp_per_pupil": round((np_f33comp / enr) * cpi, 2),
            "real_nonpersonnel_total_per_pupil": row["real_nonpersonnel_support_per_pupil"],  # alias
            "real_total_support_allobjects_per_pupil": row["real_total_support_2200_per_pupil"],
            "real_total_support_f33comp_per_pupil": round((tot_f33comp / enr) * cpi, 2),
            "real_total_support_2200_per_pupil": row["real_total_support_2200_per_pupil"],  # alias
            # Proportions
            "purchased_prof_share_of_np_pct": row["purchased_services_share_of_np_pct"],
            "supplies_materials_share_of_np_pct": row["supplies_materials_share_of_np_pct"],
            "capital_outlay_share_of_allobjects_pct": round((cap_6500 / tot_all * 100) if tot_all > 0 else 0, 1),
            "nonpersonnel_share_of_total_e07_pct": row["nonpersonnel_share_of_total_e07_pct"],
        }
        records.append(rec)

    # 2. Process Kansas records from Form USD-E actuals
    for dist in KS_DISTRICTS:
        dname = dist["district_name"]
        slug = dist["slug"]
        uid = dist["uid"]
        arch = dist["archetype"]
        nces_id = dist["nces_lea_id"]

        for sy, cyr, ayr, corsup, enr in dist["years"]:
            fpath = RAW_KS_DIR / slug / f"{uid}_Codes{cyr}_Actuals{ayr}.pdf"
            totals, _ = parse_ks_file(str(fpath), target_col_idx=1)

            cpi = CPI_DEFLATORS[sy]

            sal = totals["sal_certified"] + totals["sal_noncertified"]
            ben = totals["benefits_insurance"] + totals["benefits_socsec"] + totals["benefits_other"]
            p300 = totals["purchased_prof_300"]
            p450 = totals["purchased_prop_400"] + totals["other_purch_500"]
            s600 = totals["supplies_books_640"] + totals["supplies_tech_650"] + totals["supplies_misc_680"]
            c700 = totals["property_700"]
            o800 = totals["other_800"]
            np_all = p300 + p450 + s600 + c700 + o800
            np_f33comp = p300 + p450 + s600 + o800
            tot_all = sal + ben + np_all
            tot_f33comp = sal + ben + np_f33comp

            rec = {
                "district_name": dname,
                "state": "KS",
                "nces_lea_id": nces_id,
                "state_id": dist["state_id"],
                "organizational_archetype": arch,
                "school_year": sy,
                "enrollment": enr,
                "corsup_fte": corsup,
                "corsup_per_1000_pupils": round(corsup / enr * 1000, 3),
                # Nominal amounts
                "nom_salaries": sal,
                "nom_benefits": ben,
                "nom_purchased_prof_tech_or_services": p300,
                "nom_other_purchased_services": p450,
                "nom_supplies_materials": s600,
                "nom_capital_outlay": c700,
                "nom_other_objects": o800,
                "nom_nonpersonnel_allobjects": np_all,
                "nom_nonpersonnel_f33comp": np_f33comp,
                "nom_nonpersonnel_total": np_all,  # backward compatibility alias
                "nom_total_support_allobjects": tot_all,
                "nom_total_support_f33comp": tot_f33comp,
                "nom_total_support_2200": tot_all,  # backward compatibility alias
                # Real Per-Pupil Amounts (Constant 2023 Dollars)
                "real_salaries_per_pupil": round((sal / enr) * cpi, 2),
                "real_benefits_per_pupil": round((ben / enr) * cpi, 2),
                "real_purchased_prof_tech_per_pupil": round((p300 / enr) * cpi, 2),
                "real_other_purchased_services_per_pupil": round((p450 / enr) * cpi, 2),
                "real_supplies_materials_per_pupil": round((s600 / enr) * cpi, 2),
                "real_capital_outlay_per_pupil": round((c700 / enr) * cpi, 2),
                "real_nonpersonnel_allobjects_per_pupil": round((np_all / enr) * cpi, 2),
                "real_nonpersonnel_f33comp_per_pupil": round((np_f33comp / enr) * cpi, 2),
                "real_nonpersonnel_total_per_pupil": round((np_all / enr) * cpi, 2),  # alias
                "real_total_support_allobjects_per_pupil": round((tot_all / enr) * cpi, 2),
                "real_total_support_f33comp_per_pupil": round((tot_f33comp / enr) * cpi, 2),
                "real_total_support_2200_per_pupil": round((tot_all / enr) * cpi, 2),  # alias
                # Proportions
                "purchased_prof_share_of_np_pct": round((p300 / np_all * 100) if np_all > 0 else 0, 1),
                "supplies_materials_share_of_np_pct": round((s600 / np_all * 100) if np_all > 0 else 0, 1),
                "capital_outlay_share_of_allobjects_pct": round((c700 / tot_all * 100) if tot_all > 0 else 0, 1),
                "nonpersonnel_share_of_total_e07_pct": round((np_all / tot_all * 100) if tot_all > 0 else 0, 1),
            }
            records.append(rec)

    df_panel = pd.DataFrame(records)
    # Sort deterministically
    df_panel = df_panel.sort_values(by=["state", "district_name", "school_year"]).reset_index(drop=True)

    out_csv = PROCESSED_DIR / "focal_archetype_object_level_support_panel.csv"
    df_panel.to_csv(out_csv, index=False)
    print(f"Saved canonical object-level panel to {out_csv} ({len(df_panel)} rows, {len(df_panel.columns)} columns)")

    # Produce delta summary table (2014-15 -> 2022-23)
    deltas = []
    for dname, grp in df_panel.groupby("district_name"):
        grp = grp.set_index("school_year")
        if "2014-2015" in grp.index and "2022-2023" in grp.index:
            r15 = grp.loc["2014-2015"]
            r23 = grp.loc["2022-2023"]

            d_corsup = r23["corsup_fte"] - r15["corsup_fte"]
            d_p300 = r23["real_purchased_prof_tech_per_pupil"] - r15["real_purchased_prof_tech_per_pupil"]
            d_p450 = r23["real_other_purchased_services_per_pupil"] - r15["real_other_purchased_services_per_pupil"]
            d_s600 = r23["real_supplies_materials_per_pupil"] - r15["real_supplies_materials_per_pupil"]
            d_np_all = r23["real_nonpersonnel_allobjects_per_pupil"] - r15["real_nonpersonnel_allobjects_per_pupil"]
            d_np_comp = r23["real_nonpersonnel_f33comp_per_pupil"] - r15["real_nonpersonnel_f33comp_per_pupil"]
            d_sal = r23["real_salaries_per_pupil"] - r15["real_salaries_per_pupil"]
            d_ben = r23["real_benefits_per_pupil"] - r15["real_benefits_per_pupil"]
            d_tot_all = r23["real_total_support_allobjects_per_pupil"] - r15["real_total_support_allobjects_per_pupil"]
            d_tot_comp = r23["real_total_support_f33comp_per_pupil"] - r15["real_total_support_f33comp_per_pupil"]

            deltas.append({
                "district_name": dname,
                "state": r15["state"],
                "nces_lea_id": r15["nces_lea_id"],
                "organizational_archetype": r15["organizational_archetype"],
                "delta_corsup_fte": round(d_corsup, 1),
                "delta_real_purchased_prof_obj300_per_pupil": round(d_p300, 2),
                "delta_real_supplies_materials_obj600_per_pupil": round(d_s600, 2),
                "delta_real_nonpersonnel_allobjects_per_pupil": round(d_np_all, 2),
                "delta_real_nonpersonnel_f33comp_per_pupil": round(d_np_comp, 2),
                "delta_real_salaries_per_pupil": round(d_sal, 2),
                "delta_real_total_support_allobjects_per_pupil": round(d_tot_all, 2),
                "delta_real_total_support_f33comp_per_pupil": round(d_tot_comp, 2),
                # Backward compatibility aliases
                "delta_real_nonpersonnel_total_per_pupil": round(d_np_all, 2),
                "delta_real_total_support_2200_per_pupil": round(d_tot_all, 2),
                "insourcing_verdict": (
                    "Inconsistent with Function 2200 Insourcing (Obj 300 was negligible and grew; non-personnel is supplies/curriculum)"
                    if dname == "Shawnee Mission USD 512"
                    else ("Additive Layering / Apparatus Expansion" if d_tot_all > 0 and d_np_all >= 0 else "Budget Realignment / Other")
                )
            })

    df_deltas = pd.DataFrame(deltas)
    delta_csv = TABLES_DIR / "phase6c2_focal_archetype_mechanism_deltas.csv"
    df_deltas.to_csv(delta_csv, index=False)
    print(f"Saved mechanism deltas table to {delta_csv}")

    return df_panel, df_deltas


if __name__ == "__main__":
    build_focal_object_panel()
