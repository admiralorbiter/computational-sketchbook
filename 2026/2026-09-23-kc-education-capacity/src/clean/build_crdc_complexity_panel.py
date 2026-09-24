"""
src/clean/build_crdc_complexity_panel.py
Task 004C: Public KC School Complexity Panel Construction

Ingests and harmonizes student need and classroom complexity indicators from CRDC
and CCD across all available survey waves:
  - IDEA (Special Education) student counts and enrollment shares
  - Section 504 accommodation student counts and enrollment shares
  - English Learner (LEP/EL) counts and enrollment shares
  - Chronic Absenteeism student counts and rates (EDFacts FS195)
  - Free and Reduced-Price Lunch (FRL) rates from longitudinal CCD panel

Outputs:
  - data/processed/kc_school_complexity_panel_2015_2024.csv
  - logs entry in data/manifest.csv
"""

import os
import zipfile
import numpy as np
import pandas as pd

def build_complexity_panel():
    print("=== Building Task 004C: KC School Complexity Panel ===")
    
    # 1. Load universe of KC schools
    uni_path = "data/processed/kc_school_universe_2024_2025.csv"
    uni = pd.read_csv(uni_path, low_memory=False)
    uni["nces_school_id"] = uni["nces_school_id"].astype(str).str.zfill(12)
    uni_sids = set(uni["nces_school_id"])
    print(f"Loaded {len(uni_sids)} target schools from universe.")
    
    # Load longitudinal CCD panel for metadata and FRL rates
    ccd_path = "data/processed/kc_school_capacity_long_2014_15_2024_25.csv"
    ccd = pd.read_csv(ccd_path, low_memory=False)
    ccd["nces_school_id"] = ccd["nces_school_id"].astype(str).str.zfill(12)
    
    records = []
    
    # ---------------------------------------------------------
    # Wave 2015-16
    # ---------------------------------------------------------
    z16_path = "data/raw/crdc/2015-16-crdc-data.zip"
    if os.path.exists(z16_path):
        print("Extracting 2015-16 complexity...")
        with zipfile.ZipFile(z16_path, "r") as z:
            with z.open("Data Files and Layouts/CRDC 2015-16 School Data.csv") as f:
                df16 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df16["nces_school_id"] = df16["LEAID"].astype(str).str.replace(".0", "").str.zfill(7) + df16["SCHID"].astype(str).str.replace(".0", "").str.zfill(5)
                kc16 = df16[df16["nces_school_id"].isin(uni_sids)].copy()
                
                cols_to_clean = ["TOT_ENR_M", "TOT_ENR_F", "TOT_IDEAENR_M", "TOT_IDEAENR_F", "TOT_LEPENR_M", "TOT_LEPENR_F", "TOT_504ENR_M", "TOT_504ENR_F"]
                for c in cols_to_clean:
                    kc16[c] = pd.to_numeric(kc16[c], errors="coerce").fillna(0)
                    kc16.loc[kc16[c] < 0, c] = 0
                    
                for _, r in kc16.iterrows():
                    sid = r["nces_school_id"]
                    enr = r["TOT_ENR_M"] + r["TOT_ENR_F"]
                    idea = r["TOT_IDEAENR_M"] + r["TOT_IDEAENR_F"]
                    lep = r["TOT_LEPENR_M"] + r["TOT_LEPENR_F"]
                    s504 = r["TOT_504ENR_M"] + r["TOT_504ENR_F"]
                    
                    records.append({
                        "school_year": "2015-2016",
                        "crdc_wave": "2015-16",
                        "nces_school_id": sid,
                        "school_name": r.get("SCH_NAME", ""),
                        "enrollment_crdc": enr,
                        "idea_count": idea,
                        "idea_share": idea / enr if enr > 0 else np.nan,
                        "section_504_count": s504,
                        "section_504_share": s504 / enr if enr > 0 else np.nan,
                        "lep_count": lep,
                        "lep_share": lep / enr if enr > 0 else np.nan,
                        "accommodations_count": idea + s504,
                        "accommodations_share": (idea + s504) / enr if enr > 0 else np.nan,
                        "chronic_absent_count": np.nan,
                        "chronic_absent_rate": np.nan,
                    })

    # ---------------------------------------------------------
    # Wave 2017-18
    # ---------------------------------------------------------
    z18_path = "data/raw/crdc/2017-18-crdc-data.zip"
    if os.path.exists(z18_path):
        print("Extracting 2017-18 complexity...")
        # Chronic absent map
        abs_map = {}
        with zipfile.ZipFile(z18_path, "r") as z:
            for n in z.namelist():
                if "Chronic" in n:
                    with z.open(n) as f:
                        adf = pd.read_csv(f, encoding="latin1", low_memory=False)
                        adf["nces_school_id"] = adf["NCESSCH"].astype(str).str.replace(".0", "").str.zfill(12)
                        kca = adf[adf["nces_school_id"].isin(uni_sids)].copy()
                        count_cols = [c for c in kca.columns if c.endswith("_7") and not c.startswith("TOTAL")]
                        for c in count_cols:
                            kca[c] = pd.to_numeric(kca[c], errors="coerce").fillna(0)
                            kca.loc[kca[c] < 0, c] = 0
                        kca["tot_abs"] = kca[count_cols].sum(axis=1)
                        for _, ar in kca.iterrows():
                            abs_map[ar["nces_school_id"]] = ar["tot_abs"]
                            
            with z.open("2017-18-crdc-data-corrected-publication 2/2017-18 Public-Use Files/Data/SCH/CRDC/CSV/Enrollment.csv") as f:
                df18 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df18["nces_school_id"] = df18["LEAID"].astype(str).str.replace(".0", "").str.zfill(7) + df18["SCHID"].astype(str).str.replace(".0", "").str.zfill(5)
                kc18 = df18[df18["nces_school_id"].isin(uni_sids)].copy()
                
                cols_to_clean = ["TOT_ENR_M", "TOT_ENR_F", "TOT_IDEAENR_M", "TOT_IDEAENR_F", "TOT_LEPENR_M", "TOT_LEPENR_F", "TOT_504ENR_M", "TOT_504ENR_F"]
                for c in cols_to_clean:
                    kc18[c] = pd.to_numeric(kc18[c], errors="coerce").fillna(0)
                    kc18.loc[kc18[c] < 0, c] = 0
                    
                for _, r in kc18.iterrows():
                    sid = r["nces_school_id"]
                    enr = r["TOT_ENR_M"] + r["TOT_ENR_F"]
                    idea = r["TOT_IDEAENR_M"] + r["TOT_IDEAENR_F"]
                    lep = r["TOT_LEPENR_M"] + r["TOT_LEPENR_F"]
                    s504 = r["TOT_504ENR_M"] + r["TOT_504ENR_F"]
                    c_abs = abs_map.get(sid, np.nan)
                    
                    records.append({
                        "school_year": "2017-2018",
                        "crdc_wave": "2017-18",
                        "nces_school_id": sid,
                        "school_name": r.get("SCH_NAME", ""),
                        "enrollment_crdc": enr,
                        "idea_count": idea,
                        "idea_share": idea / enr if enr > 0 else np.nan,
                        "section_504_count": s504,
                        "section_504_share": s504 / enr if enr > 0 else np.nan,
                        "lep_count": lep,
                        "lep_share": lep / enr if enr > 0 else np.nan,
                        "accommodations_count": idea + s504,
                        "accommodations_share": (idea + s504) / enr if enr > 0 else np.nan,
                        "chronic_absent_count": c_abs,
                        "chronic_absent_rate": c_abs / enr if (enr > 0 and pd.notna(c_abs)) else np.nan,
                    })

    # ---------------------------------------------------------
    # Wave 2020-21
    # ---------------------------------------------------------
    z21_path = "data/raw/crdc/2020-21-crdc-data.zip"
    if os.path.exists(z21_path):
        print("Extracting 2020-21 complexity...")
        abs_map = {}
        with zipfile.ZipFile(z21_path, "r") as z:
            for n in z.namelist():
                if "Chronic" in n:
                    with z.open(n) as f:
                        adf = pd.read_csv(f, encoding="latin1", low_memory=False)
                        adf["nces_school_id"] = adf["NCESSCH"].astype(str).str.replace(".0", "").str.zfill(12)
                        kca = adf[adf["nces_school_id"].isin(uni_sids)].copy()
                        count_cols = [c for c in kca.columns if "SCH_ABSENT_" in c]
                        for c in count_cols:
                            kca[c] = pd.to_numeric(kca[c], errors="coerce").fillna(0)
                            kca.loc[kca[c] < 0, c] = 0
                        kca["tot_abs"] = kca[count_cols].sum(axis=1)
                        for _, ar in kca.iterrows():
                            abs_map[ar["nces_school_id"]] = ar["tot_abs"]
                            
            with z.open("CRDC/School/Enrollment.csv") as f:
                df21 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df21["nces_school_id"] = df21["LEAID"].astype(str).str.replace(".0", "").str.zfill(7) + df21["SCHID"].astype(str).str.replace(".0", "").str.zfill(5)
                kc21 = df21[df21["nces_school_id"].isin(uni_sids)].copy()
                
                cols_to_clean = ["TOT_ENR_M", "TOT_ENR_F", "TOT_IDEAENR_M", "TOT_IDEAENR_F", "TOT_LEPENR_M", "TOT_LEPENR_F", "TOT_504ENR_M", "TOT_504ENR_F"]
                for c in cols_to_clean:
                    kc21[c] = pd.to_numeric(kc21[c], errors="coerce").fillna(0)
                    kc21.loc[kc21[c] < 0, c] = 0
                    
                for _, r in kc21.iterrows():
                    sid = r["nces_school_id"]
                    enr = r["TOT_ENR_M"] + r["TOT_ENR_F"]
                    idea = r["TOT_IDEAENR_M"] + r["TOT_IDEAENR_F"]
                    lep = r["TOT_LEPENR_M"] + r["TOT_LEPENR_F"]
                    s504 = r["TOT_504ENR_M"] + r["TOT_504ENR_F"]
                    c_abs = abs_map.get(sid, np.nan)
                    
                    records.append({
                        "school_year": "2020-2021",
                        "crdc_wave": "2020-21",
                        "nces_school_id": sid,
                        "school_name": r.get("SCH_NAME", ""),
                        "enrollment_crdc": enr,
                        "idea_count": idea,
                        "idea_share": idea / enr if enr > 0 else np.nan,
                        "section_504_count": s504,
                        "section_504_share": s504 / enr if enr > 0 else np.nan,
                        "lep_count": lep,
                        "lep_share": lep / enr if enr > 0 else np.nan,
                        "accommodations_count": idea + s504,
                        "accommodations_share": (idea + s504) / enr if enr > 0 else np.nan,
                        "chronic_absent_count": c_abs,
                        "chronic_absent_rate": c_abs / enr if (enr > 0 and pd.notna(c_abs)) else np.nan,
                    })

    # ---------------------------------------------------------
    # Wave 2023-24
    # ---------------------------------------------------------
    z24_path = "data/raw/crdc/2023-24-crdc-data.zip"
    if os.path.exists(z24_path):
        print("Extracting 2023-24 complexity...")
        with zipfile.ZipFile(z24_path, "r") as z:
            with z.open("SCH/Enrollment.csv") as f:
                df24 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df24["nces_school_id"] = df24["LEAID"].astype(str).str.replace(".0", "").str.zfill(7) + df24["SCHID"].astype(str).str.replace(".0", "").str.zfill(5)
                kc24 = df24[df24["nces_school_id"].isin(uni_sids)].copy()
                
                cols_to_clean = ["TOT_ENR_M", "TOT_ENR_F", "TOT_ENR_X", "TOT_IDEAENR_M", "TOT_IDEAENR_F", "TOT_IDEAENR_X", "TOT_ELENR_M", "TOT_ELENR_F", "TOT_ELENR_X", "TOT_504ENR_M", "TOT_504ENR_F", "TOT_504ENR_X"]
                for c in cols_to_clean:
                    if c in kc24.columns:
                        kc24[c] = pd.to_numeric(kc24[c], errors="coerce").fillna(0)
                        kc24.loc[kc24[c] < 0, c] = 0
                    else:
                        kc24[c] = 0
                        
                for _, r in kc24.iterrows():
                    sid = r["nces_school_id"]
                    enr = r["TOT_ENR_M"] + r["TOT_ENR_F"] + r["TOT_ENR_X"]
                    idea = r["TOT_IDEAENR_M"] + r["TOT_IDEAENR_F"] + r["TOT_IDEAENR_X"]
                    lep = r["TOT_ELENR_M"] + r["TOT_ELENR_F"] + r["TOT_ELENR_X"]
                    s504 = r["TOT_504ENR_M"] + r["TOT_504ENR_F"] + r["TOT_504ENR_X"]
                    
                    records.append({
                        "school_year": "2023-2024",
                        "crdc_wave": "2023-24",
                        "nces_school_id": sid,
                        "school_name": r.get("SCH_NAME", ""),
                        "enrollment_crdc": enr,
                        "idea_count": idea,
                        "idea_share": idea / enr if enr > 0 else np.nan,
                        "section_504_count": s504,
                        "section_504_share": s504 / enr if enr > 0 else np.nan,
                        "lep_count": lep,
                        "lep_share": lep / enr if enr > 0 else np.nan,
                        "accommodations_count": idea + s504,
                        "accommodations_share": (idea + s504) / enr if enr > 0 else np.nan,
                        "chronic_absent_count": np.nan,
                        "chronic_absent_rate": np.nan,
                    })
                    
    comp_df = pd.DataFrame(records)
    print(f"Constructed {len(comp_df):,} school-wave complexity records.")
    
    # ---------------------------------------------------------
    # Merge with CCD Panel (Staffing, PTR, FRL, Locales)
    # ---------------------------------------------------------
    # CCD panel has school_year like '2015-2016'
    ccd_sub = ccd[[
        "school_year", "nces_school_id", "district_name", "state", "county_name", 
        "locale_group", "school_level", "school_type", "is_virtual", "is_operating",
        "enrollment_k12", "classroom_teacher_fte", "students_per_classroom_teacher_fte_allgrades",
        "frl_eligible", "frl_rate"
    ]].copy()
    ccd_sub.rename(columns={"students_per_classroom_teacher_fte_allgrades": "school_ptr"}, inplace=True)
    
    merged = pd.merge(comp_df, ccd_sub, on=["school_year", "nces_school_id"], how="left")
    
    # Clean numeric columns
    for col in ["enrollment_crdc", "idea_count", "idea_share", "section_504_count", "section_504_share", "lep_count", "lep_share", "accommodations_count", "accommodations_share", "chronic_absent_count", "chronic_absent_rate", "school_ptr", "frl_rate"]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
        
    out_path = "data/processed/kc_school_complexity_panel_2015_2024.csv"
    merged.to_csv(out_path, index=False)
    print(f"Saved canonical complexity panel to {out_path} ({len(merged)} rows)")
    
    # ---------------------------------------------------------
    # Update manifest.csv
    # ---------------------------------------------------------
    manifest_path = "data/manifest.csv"
    if os.path.exists(manifest_path):
        mdf = pd.read_csv(manifest_path)
        if "kc_school_complexity_panel_2015_2024.csv" not in mdf["filename"].values:
            new_row = {
                "source": "CRDC Public-Use Files & CCD Longitudinal Panel",
                "source_url": "internal",
                "filename": "kc_school_complexity_panel_2015_2024.csv",
                "school_year": "2015-2016 to 2023-2024",
                "download_date": "2026-09-24",
                "sha256": "",
                "description": "School-level student complexity panel tracking IDEA (SPED), Section 504 accommodations, English Learners (EL), chronic absenteeism, and FRL rates",
                "notes": f"Task 004C: {len(merged):,} school-wave records across 4 CRDC waves"
            }
            mdf = pd.concat([mdf, pd.DataFrame([new_row])], ignore_index=True)
            mdf.to_csv(manifest_path, index=False)
            print("Updated data/manifest.csv")
            
    return merged

if __name__ == "__main__":
    build_complexity_panel()
