"""
Explore Longitudinal CRDC Course-Level Class Sizes across the KC Metropolitan Area (2013-14 through 2023-24).

Investigates:
1. All available courses and waves in CRDC (Algebra I, Geometry, Algebra II, Advanced Math, Calculus, Biology, Chemistry, Physics, and Computer Science).
2. Derived school-course average section size (enrollment / classes, EDU-012).
3. Longitudinal trends across all 6 collection waves: 2013-14, 2015-16, 2017-18, 2020-21, 2021-22, 2023-24.
4. Stratifications: Regional total, Missouri vs. Kansas, Foundation Core vs. Advanced/Specialized.
5. Secondary staffing wedge: comparison against contemporaneous school macro PTR (EDU-001).
"""

from pathlib import Path
import zipfile
import pandas as pd
import numpy as np

OBS_DIR = Path(__file__).resolve().parents[2]
KC_DIR = OBS_DIR.parent / "2026-09-23-kc-education-capacity"

CRDC_LONG_PATH = KC_DIR / "data" / "processed" / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"
RAW_CRDC_DIR = KC_DIR / "data" / "raw" / "crdc"

def clean_val(v):
    try:
        f = float(v)
        return f if f >= 0 else np.nan
    except (ValueError, TypeError):
        return np.nan

def load_comprehensive_course_data():
    """Load and harmonize all CRDC course records across all 6 waves, including audited corrections."""
    df_long = pd.read_csv(CRDC_LONG_PATH, low_memory=False)
    
    # 1. Audited correction for 2015-16 Geometry enrollment
    # In raw 2015-16 CRDC, Geometry enrollment variables were TOT_GEOM_M and TOT_GEOM_F
    fpath_1516 = RAW_CRDC_DIR / "2015-2016" / "CRDC 2015-16 School Data.csv"
    if fpath_1516.exists():
        raw_1516 = pd.read_csv(fpath_1516, encoding="latin1", low_memory=False)
        raw_1516["ncessch"] = raw_1516["LEAID"].astype(str).str.zfill(7) + raw_1516["SCHID"].astype(str).str.zfill(5)
        raw_1516["geom_enr_corr"] = raw_1516["TOT_GEOM_M"].apply(clean_val).fillna(0) + raw_1516["TOT_GEOM_F"].apply(clean_val).fillna(0)
        geom_map_1516 = raw_1516.set_index("ncessch")["geom_enr_corr"].to_dict()
        
        mask_geom_1516 = (df_long["school_year"] == "2015-2016") & (df_long["course_code"] == "geom")
        df_long.loc[mask_geom_1516, "num_enrolled"] = df_long.loc[mask_geom_1516, "nces_school_id"].astype(str).str.zfill(12).map(geom_map_1516)
        # Recompute mean_class_size and allocation_wedge
        cls_15 = df_long.loc[mask_geom_1516, "num_classes"]
        enr_15 = df_long.loc[mask_geom_1516, "num_enrolled"]
        sz_15 = enr_15 / cls_15
        sz_15 = sz_15.where(cls_15 > 0, np.nan)
        df_long.loc[mask_geom_1516, "mean_class_size"] = sz_15
        df_long.loc[mask_geom_1516, "allocation_wedge"] = sz_15 - df_long.loc[mask_geom_1516, "school_ptr"]

    # 2. Audited correction for 2013-14 Geometry
    fpath_geom_1314 = RAW_CRDC_DIR / "2013-2014" / "05-2 Geometry Courses and Classes.xlsx"
    if fpath_geom_1314.exists():
        import openpyxl
        wb = openpyxl.load_workbook(fpath_geom_1314, read_only=True)
        sheet = wb.active
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows)
        idx_leaid = headers.index("LEAID")
        idx_schid = headers.index("SCHID")
        idx_cls = headers.index("SCH_GEOMCLASSES_GS0712")
        idx_enr_m = headers.index("TOT_GEOMENR_GS0712_M")
        idx_enr_f = headers.index("TOT_GEOMENR_GS0712_F")
        
        geom_data_1314 = {}
        for r in rows:
            sid = str(r[idx_leaid]).zfill(7) + str(r[idx_schid]).zfill(5)
            c = clean_val(r[idx_cls])
            em = clean_val(r[idx_enr_m])
            ef = clean_val(r[idx_enr_f])
            if pd.notna(c) and c > 0:
                e_tot = (em if pd.notna(em) else 0) + (ef if pd.notna(ef) else 0)
                geom_data_1314[sid] = (c, e_tot)
        wb.close()
        
        mask_geom_1314 = (df_long["school_year"] == "2013-2014") & (df_long["course_code"] == "geom")
        for idx in df_long[mask_geom_1314].index:
            sid = str(df_long.loc[idx, "nces_school_id"]).zfill(12)
            if sid in geom_data_1314:
                c, e = geom_data_1314[sid]
                df_long.loc[idx, "num_classes"] = c
                df_long.loc[idx, "num_enrolled"] = e
                df_long.loc[idx, "mean_class_size"] = e / c if c > 0 else np.nan
                ptr = df_long.loc[idx, "school_ptr"]
                df_long.loc[idx, "allocation_wedge"] = (e / c) - ptr if (c > 0 and pd.notna(ptr)) else np.nan

    # 3. Ingest Computer Science for 2020-21 and 2023-24
    cs_records = []
    # 2020-21 CS
    zip_2021 = RAW_CRDC_DIR / "2020-21-crdc-data.zip"
    if zip_2021.exists():
        with zipfile.ZipFile(zip_2021) as z:
            if "CRDC/School/Computer Science.csv" in z.namelist():
                with z.open("CRDC/School/Computer Science.csv") as f:
                    df_cs20 = pd.read_csv(f, encoding="latin1", low_memory=False)
                    df_cs20["sid"] = df_cs20["COMBOKEY"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
                    cs20_map = df_cs20.set_index("sid")
                    
                    sub_meta = df_long[(df_long["school_year"] == "2020-2021") & (df_long["course_code"] == "alg1")]
                    for _, r in sub_meta.iterrows():
                        sid = str(r["nces_school_id"]).zfill(12)
                        if sid in cs20_map.index:
                            row_cs = cs20_map.loc[sid]
                            c = clean_val(row_cs.get("SCH_COMPCLASSES_CSCI"))
                            em = clean_val(row_cs.get("TOT_COMPENR_CSCI_M"))
                            ef = clean_val(row_cs.get("TOT_COMPENR_CSCI_F"))
                            e = (em if pd.notna(em) else 0) + (ef if pd.notna(ef) else 0) if (pd.notna(em) or pd.notna(ef)) else np.nan
                            
                            rec = r.to_dict()
                            rec["course_code"] = "csci"
                            rec["course_name"] = "Computer Science"
                            rec["subject_area"] = "Computer Science"
                            rec["course_level"] = "Advanced / Specialized"
                            rec["num_classes"] = c
                            rec["num_enrolled"] = e
                            rec["mean_class_size"] = e / c if (pd.notna(c) and c > 0 and pd.notna(e)) else np.nan
                            ptr = r["school_ptr"]
                            rec["allocation_wedge"] = rec["mean_class_size"] - ptr if (pd.notna(rec["mean_class_size"]) and pd.notna(ptr)) else np.nan
                            cs_records.append(rec)

    # 2023-24 CS
    zip_2324 = RAW_CRDC_DIR / "2023-24-crdc-data.zip"
    if zip_2324.exists():
        with zipfile.ZipFile(zip_2324) as z:
            if "SCH/Computer Science.csv" in z.namelist():
                with z.open("SCH/Computer Science.csv") as f:
                    df_cs23 = pd.read_csv(f, encoding="latin1", low_memory=False)
                    df_cs23["sid"] = df_cs23["COMBOKEY"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
                    cs23_map = df_cs23.set_index("sid")
                    
                    sub_meta = df_long[(df_long["school_year"] == "2023-2024") & (df_long["course_code"] == "alg1")]
                    for _, r in sub_meta.iterrows():
                        sid = str(r["nces_school_id"]).zfill(12)
                        if sid in cs23_map.index:
                            row_cs = cs23_map.loc[sid]
                            c = clean_val(row_cs.get("SCH_COMPCLASSES_CSCI"))
                            em = clean_val(row_cs.get("TOT_COMPENR_CSCI_M"))
                            ef = clean_val(row_cs.get("TOT_COMPENR_CSCI_F"))
                            e = (em if pd.notna(em) else 0) + (ef if pd.notna(ef) else 0) if (pd.notna(em) or pd.notna(ef)) else np.nan
                            
                            rec = r.to_dict()
                            rec["course_code"] = "csci"
                            rec["course_name"] = "Computer Science"
                            rec["subject_area"] = "Computer Science"
                            rec["course_level"] = "Advanced / Specialized"
                            rec["num_classes"] = c
                            rec["num_enrolled"] = e
                            rec["mean_class_size"] = e / c if (pd.notna(c) and c > 0 and pd.notna(e)) else np.nan
                            ptr = r["school_ptr"]
                            rec["allocation_wedge"] = rec["mean_class_size"] - ptr if (pd.notna(rec["mean_class_size"]) and pd.notna(ptr)) else np.nan
                            cs_records.append(rec)

    if cs_records:
        df_long = pd.concat([df_long, pd.DataFrame(cs_records)], ignore_index=True)

    return df_long

def main():
    print("=" * 80)
    print("KANSAS CITY METROPOLITAN CRDC HISTORICAL COURSE-LEVEL CLASS SIZE ANALYSIS")
    print("=" * 80)
    
    df = load_comprehensive_course_data()
    
    # Filter to active operating regular schools with valid class counts and enrollment
    valid = df[(df["is_operating"] == True) & 
               (df["num_classes"] > 0) & 
               (df["num_enrolled"] > 0)].copy()
    valid["derived_size"] = valid["num_enrolled"] / valid["num_classes"]
    
    print(f"Total valid course-school observations analyzed: {len(valid):,}")
    
    # Summary by course across waves
    courses = [
        "Algebra I", "Geometry", "Algebra II", "Advanced Mathematics", "Calculus",
        "Biology", "Chemistry", "Physics", "Computer Science"
    ]
    
    waves = ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]
    
    rows = []
    for cname in courses:
        for w in waves:
            sub = valid[(valid["course_name"] == cname) & (valid["crdc_wave"] == w)]
            if len(sub) == 0:
                continue
            
            n_schools = sub["nces_school_id"].nunique()
            tot_cls = sub["num_classes"].sum()
            tot_enr = sub["num_enrolled"].sum()
            pooled_sz = tot_enr / tot_cls if tot_cls > 0 else np.nan
            unw_mean = sub["derived_size"].mean()
            median_sz = sub["derived_size"].median()
            q25 = sub["derived_size"].quantile(0.25)
            q75 = sub["derived_size"].quantile(0.75)
            
            # State splits
            mo_sub = sub[sub["state"] == "MO"]
            ks_sub = sub[sub["state"] == "KS"]
            mo_pooled = mo_sub["num_enrolled"].sum() / mo_sub["num_classes"].sum() if len(mo_sub) > 0 and mo_sub["num_classes"].sum() > 0 else np.nan
            ks_pooled = ks_sub["num_enrolled"].sum() / ks_sub["num_classes"].sum() if len(ks_sub) > 0 and ks_sub["num_classes"].sum() > 0 else np.nan
            
            # Staffing wedge (where school_ptr is valid)
            wedge_sub = sub.dropna(subset=["school_ptr"])
            mean_ptr = wedge_sub["school_ptr"].mean() if len(wedge_sub) > 0 else np.nan
            mean_wedge = (wedge_sub["derived_size"] - wedge_sub["school_ptr"]).mean() if len(wedge_sub) > 0 else np.nan
            
            rows.append({
                "course": cname,
                "wave": w,
                "schools": n_schools,
                "classes": tot_cls,
                "enrollment": tot_enr,
                "pooled_size": pooled_sz,
                "mean_size": unw_mean,
                "median_size": median_sz,
                "q25": q25,
                "q75": q75,
                "mo_pooled": mo_pooled,
                "ks_pooled": ks_pooled,
                "macro_ptr": mean_ptr,
                "staffing_wedge": mean_wedge
            })
            
    res_df = pd.DataFrame(rows)
    
    # Save output summary table
    out_csv = OBS_DIR / "outputs" / "crdc_historical_course_class_sizes_summary.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(out_csv, index=False)
    print(f"Exported summary table to {out_csv.relative_to(OBS_DIR)}")
    
    # Print formatted tables
    for cname in courses:
        c_df = res_df[res_df["course"] == cname]
        if len(c_df) == 0:
            continue
        print("\n" + "=" * 80)
        print(f"COURSE: {cname.upper()}")
        print("=" * 80)
        print(f"{'Wave':<9} | {'Schools':<7} | {'Classes':<7} | {'Enrolled':<8} | {'Pooled':<6} | {'Mean':<6} | {'Median':<6} | {'MO Pl':<6} | {'KS Pl':<6} | {'PTR':<5} | {'Wedge':<6}")
        print("-" * 80)
        for _, r in c_df.iterrows():
            mo_str = f"{r['mo_pooled']:.2f}" if pd.notna(r['mo_pooled']) else "N/A"
            ks_str = f"{r['ks_pooled']:.2f}" if pd.notna(r['ks_pooled']) else "N/A"
            ptr_str = f"{r['macro_ptr']:.1f}" if pd.notna(r['macro_ptr']) else "N/A"
            wdg_str = f"{r['staffing_wedge']:+.2f}" if pd.notna(r['staffing_wedge']) else "N/A"
            print(f"{r['wave']:<9} | {r['schools']:<7d} | {r['classes']:<7.0f} | {r['enrollment']:<8.0f} | {r['pooled_size']:<6.2f} | {r['mean_size']:<6.2f} | {r['median_size']:<6.2f} | {mo_str:<6} | {ks_str:<6} | {ptr_str:<5} | {wdg_str:<6}")

if __name__ == "__main__":
    main()
