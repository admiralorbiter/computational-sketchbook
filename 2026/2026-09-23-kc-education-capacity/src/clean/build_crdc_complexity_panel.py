"""
src/clean/build_crdc_complexity_panel.py
Task 004C.1: Public KC School Complexity Panel Construction (Calibrated & Extended)

Ingests and harmonizes student need and classroom complexity indicators from CRDC,
EDFacts FS195, and CCD across all available survey waves:
  - IDEA (Special Education) student counts and enrollment shares (CRDC)
  - Section 504 accommodation student counts and enrollment shares (CRDC)
  - English Learner (LEP/EL) counts and enrollment shares (CRDC)
  - Chronic Absenteeism student counts and rates from:
      * CRDC (2017-18, 2020-21)
      * EDFacts FS195 (2021-22, 2022-23)
  - Free and Reduced-Price Lunch (FRL) rates from longitudinal CCD panel
  - Balanced panel eligibility flag (from kc_school_balanced_panel_2014_15_2024_25.csv)

Outputs:
  - data/processed/kc_school_complexity_panel_2015_2024.csv
  - logs entry in data/manifest.csv
"""

import os
import zipfile
import numpy as np
import pandas as pd

def build_complexity_panel():
    print("=== Building Task 004C.1: KC School Complexity Panel ===")
    
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
    
    # Load balanced panel eligibility
    bal_path = "data/processed/kc_school_balanced_panel_2014_15_2024_25.csv"
    bal_sids = set()
    if os.path.exists(bal_path):
        bdf = pd.read_csv(bal_path, low_memory=False)
        bal_sids = set(bdf[bdf["balanced_panel_eligible"] == True]["nces_school_id"].astype(str).str.zfill(12).unique())
        print(f"Identified {len(bal_sids)} balanced panel eligible schools.")
        
    records = []
    
    # ---------------------------------------------------------
    # Wave 2015-16 (CRDC)
    # ---------------------------------------------------------
    z16_path = "data/raw/crdc/2015-16-crdc-data.zip"
    if os.path.exists(z16_path):
        print("Extracting 2015-16 CRDC complexity...")
        with zipfile.ZipFile(z16_path, "r") as z:
            with z.open("Data Files and Layouts/CRDC 2015-16 School Data.csv") as f:
                df16 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df16["nces_school_id"] = df16["LEAID"].astype(str).str.replace(".0", "", regex=False).str.zfill(7) + df16["SCHID"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
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
                        "data_source": "CRDC",
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
    # Wave 2017-18 (CRDC)
    # ---------------------------------------------------------
    z18_path = "data/raw/crdc/2017-18-crdc-data.zip"
    if os.path.exists(z18_path):
        print("Extracting 2017-18 CRDC complexity...")
        abs_map = {}
        with zipfile.ZipFile(z18_path, "r") as z:
            for n in z.namelist():
                if "Chronic" in n:
                    with z.open(n) as f:
                        adf = pd.read_csv(f, encoding="latin1", low_memory=False)
                        adf["nces_school_id"] = adf["NCESSCH"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
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
                df18["nces_school_id"] = df18["LEAID"].astype(str).str.replace(".0", "", regex=False).str.zfill(7) + df18["SCHID"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
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
                        "data_source": "CRDC",
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
    # Wave 2020-21 (CRDC)
    # ---------------------------------------------------------
    z21_path = "data/raw/crdc/2020-21-crdc-data.zip"
    if os.path.exists(z21_path):
        print("Extracting 2020-21 CRDC complexity...")
        abs_map = {}
        with zipfile.ZipFile(z21_path, "r") as z:
            for n in z.namelist():
                if "Chronic" in n:
                    with z.open(n) as f:
                        adf = pd.read_csv(f, encoding="latin1", low_memory=False)
                        adf["nces_school_id"] = adf["NCESSCH"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
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
                df21["nces_school_id"] = df21["LEAID"].astype(str).str.replace(".0", "", regex=False).str.zfill(7) + df21["SCHID"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
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
                        "data_source": "CRDC",
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
    # Wave 2021-22 (EDFacts FS195 Chronic Absenteeism)
    # ---------------------------------------------------------
    ed22_zip = "data/raw/edfacts/edfacts_chronic_absenteeism_2021_22.zip"
    if os.path.exists(ed22_zip):
        print("Extracting 2021-22 EDFacts FS195 chronic absenteeism...")
        with zipfile.ZipFile(ed22_zip, "r") as z:
            with z.open("SY2122_FS195_DG814_SCH_110124.csv") as f:
                df_ed22 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df_ed22["nces_school_id"] = df_ed22["NCES_SCH"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
                kc_ed22 = df_ed22[(df_ed22["nces_school_id"].isin(uni_sids)) & (df_ed22["SUBGROUP"] == "ALLSCH")].copy()
                kc_ed22["abs_count"] = pd.to_numeric(kc_ed22["NUMERIC_VALUE"], errors="coerce")
                
                # Attach to records
                for _, r in kc_ed22.iterrows():
                    sid = r["nces_school_id"]
                    records.append({
                        "school_year": "2021-2022",
                        "crdc_wave": "2021-22",
                        "data_source": "EDFacts",
                        "nces_school_id": sid,
                        "school_name": r.get("SCHOOL_NAME", ""),
                        "enrollment_crdc": np.nan,
                        "idea_count": np.nan,
                        "idea_share": np.nan,
                        "section_504_count": np.nan,
                        "section_504_share": np.nan,
                        "lep_count": np.nan,
                        "lep_share": np.nan,
                        "accommodations_count": np.nan,
                        "accommodations_share": np.nan,
                        "chronic_absent_count": r["abs_count"],
                        "chronic_absent_rate": np.nan, # will be populated from CCD enrollment below
                    })

    # ---------------------------------------------------------
    # Wave 2022-23 (EDFacts FS195 Chronic Absenteeism)
    # ---------------------------------------------------------
    ed23_zip = "data/raw/edfacts/edfacts_chronic_absenteeism_2022_23.zip"
    if os.path.exists(ed23_zip):
        print("Extracting 2022-23 EDFacts FS195 chronic absenteeism...")
        with zipfile.ZipFile(ed23_zip, "r") as z:
            with z.open("SY2223_FS195_DG814_SCH_091924.csv") as f:
                df_ed23 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df_ed23["nces_school_id"] = df_ed23["NCES_SCH"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
                kc_ed23 = df_ed23[(df_ed23["nces_school_id"].isin(uni_sids)) & (df_ed23["SUBGROUP"] == "ALLSCH")].copy()
                kc_ed23["abs_count"] = pd.to_numeric(kc_ed23["NUMERIC_VALUE"], errors="coerce")
                
                # Attach to records
                for _, r in kc_ed23.iterrows():
                    sid = r["nces_school_id"]
                    records.append({
                        "school_year": "2022-2023",
                        "crdc_wave": "2022-23",
                        "data_source": "EDFacts",
                        "nces_school_id": sid,
                        "school_name": r.get("SCHOOL_NAME", ""),
                        "enrollment_crdc": np.nan,
                        "idea_count": np.nan,
                        "idea_share": np.nan,
                        "section_504_count": np.nan,
                        "section_504_share": np.nan,
                        "lep_count": np.nan,
                        "lep_share": np.nan,
                        "accommodations_count": np.nan,
                        "accommodations_share": np.nan,
                        "chronic_absent_count": r["abs_count"],
                        "chronic_absent_rate": np.nan, # will be populated from CCD enrollment below
                    })

    # ---------------------------------------------------------
    # Wave 2023-24 (CRDC)
    # ---------------------------------------------------------
    z24_path = "data/raw/crdc/2023-24-crdc-data.zip"
    if os.path.exists(z24_path):
        print("Extracting 2023-24 CRDC complexity...")
        with zipfile.ZipFile(z24_path, "r") as z:
            with z.open("SCH/Enrollment.csv") as f:
                df24 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df24["nces_school_id"] = df24["LEAID"].astype(str).str.replace(".0", "", regex=False).str.zfill(7) + df24["SCHID"].astype(str).str.replace(".0", "", regex=False).str.zfill(5)
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
                        "data_source": "CRDC",
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
    print(f"Constructed {len(comp_df):,} school-wave complexity records across all sources.")
    
    # ---------------------------------------------------------
    # Merge with CCD Panel (Staffing, PTR, FRL, Locales, Enrollment)
    # ---------------------------------------------------------
    ccd_sub = ccd[[
        "school_year", "nces_school_id", "district_name", "state", "county_name", 
        "locale_group", "school_level", "school_type", "is_virtual", "is_operating",
        "enrollment_total", "enrollment_k12", "classroom_teacher_fte", "students_per_classroom_teacher_fte_allgrades",
        "frl_eligible", "frl_rate"
    ]].copy()
    ccd_sub.rename(columns={"students_per_classroom_teacher_fte_allgrades": "school_ptr"}, inplace=True)
    
    merged = pd.merge(comp_df, ccd_sub, on=["school_year", "nces_school_id"], how="left")
    
    # Fill chronic absent rate where missing using CCD enrollment
    # For EDFacts rows (2021-22, 2022-23), calculate rate based on CCD enrollment_k12
    ed_mask = merged["data_source"] == "EDFacts"
    merged.loc[ed_mask & (merged["enrollment_k12"] > 0), "chronic_absent_rate"] = (
        merged.loc[ed_mask, "chronic_absent_count"] / merged.loc[ed_mask, "enrollment_k12"]
    )
    
    # Attach balanced panel flag
    merged["is_balanced_school"] = merged["nces_school_id"].isin(bal_sids)
    
    # Clean numeric columns
    for col in [
        "enrollment_crdc", "enrollment_total", "enrollment_k12", 
        "idea_count", "idea_share", "section_504_count", "section_504_share", 
        "lep_count", "lep_share", "accommodations_count", "accommodations_share", 
        "chronic_absent_count", "chronic_absent_rate", "school_ptr", "frl_rate"
    ]:
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
        # Update or append
        if "kc_school_complexity_panel_2015_2024.csv" in mdf["filename"].values:
            mdf.loc[mdf["filename"] == "kc_school_complexity_panel_2015_2024.csv", "notes"] = (
                f"Task 004C.1: {len(merged):,} records across 4 CRDC waves + 2 EDFacts FS195 waves; includes balanced panel flags"
            )
        else:
            new_row = {
                "source": "CRDC Public-Use Files, EDFacts FS195, & CCD Longitudinal Panel",
                "source_url": "internal",
                "filename": "kc_school_complexity_panel_2015_2024.csv",
                "school_year": "2015-2016 to 2023-2024",
                "download_date": "2026-09-24",
                "sha256": "",
                "description": "School-level student complexity panel tracking IDEA (SPED), Section 504 accommodations, English Learners (EL), chronic absenteeism, and FRL rates",
                "notes": f"Task 004C.1: {len(merged):,} school-wave records across 4 CRDC waves + 2 EDFacts FS195 waves"
            }
            mdf = pd.concat([mdf, pd.DataFrame([new_row])], ignore_index=True)
        mdf.to_csv(manifest_path, index=False)
        print("Updated data/manifest.csv")
        
    return merged

if __name__ == "__main__":
    build_complexity_panel()
