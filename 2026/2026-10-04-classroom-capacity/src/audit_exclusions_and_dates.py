"""
Audit Script:
1. >60 Class Size Exclusions: count, enrollment, waves, courses, virtual/alt status, with/without cutoff.
2. CRDC Reference Dates: Audit numerator and denominator collection dates across waves and courses.
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
TABLES_DIR = PROJECT_DIR / "artifacts" / "tables"

def audit_gt60_exclusions():
    df = pd.read_parquet(DATA_DIR / "crdc_course_panel.parquet")
    active = df[(df["num_classes"] > 0) & (df["num_enrolled"] > 0)].copy()
    gt60 = active[active["mean_class_size"] > 60].copy()
    
    print("=" * 70)
    print("AUDIT 1: MEAN_CLASS_SIZE > 60 EXCLUSIONS")
    print("=" * 70)
    print(f"Total Active Course Cells: {len(active):,}")
    print(f"Cells with Mean Class Size > 60: {len(gt60):,} ({len(gt60)/len(active)*100:.3f}%)")
    tot_enr = active["num_enrolled"].sum()
    gt60_enr = gt60["num_enrolled"].sum()
    print(f"Enrollment in >60 Cells: {gt60_enr:,.0f} out of {tot_enr:,.0f} ({gt60_enr/tot_enr*100:.2f}%)")
    
    print("\n--- Breakdown by Wave ---")
    wave_tab = pd.DataFrame({
        "Total Cells": active.groupby("crdc_wave")["nces_school_id"].count(),
        ">60 Cells": gt60.groupby("crdc_wave")["nces_school_id"].count(),
        "Pct >60 (%)": (gt60.groupby("crdc_wave")["nces_school_id"].count() / active.groupby("crdc_wave")["nces_school_id"].count()) * 100,
        "Enrollment >60": gt60.groupby("crdc_wave")["num_enrolled"].sum(),
    }).fillna(0)
    print(wave_tab)
    
    print("\n--- Breakdown by Course ---")
    course_tab = pd.DataFrame({
        "Total Cells": active.groupby("course_name")["nces_school_id"].count(),
        ">60 Cells": gt60.groupby("course_name")["nces_school_id"].count(),
        "Pct >60 (%)": (gt60.groupby("course_name")["nces_school_id"].count() / active.groupby("course_name")["nces_school_id"].count()) * 100,
        "Enrollment >60": gt60.groupby("course_name")["num_enrolled"].sum(),
    }).fillna(0)
    print(course_tab)
    
    print("\n--- Top 10 Extreme Anomalies ---")
    top_anom = gt60.sort_values("mean_class_size", ascending=False)[
        ["crdc_wave", "state", "school_name", "course_name", "num_classes", "num_enrolled", "mean_class_size"]
    ].head(10)
    print(top_anom.to_string(index=False))
    
    # Sensitivity analysis table (Clean <= 60 vs Full All)
    sens_rows = []
    for wave in ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]:
        w_all = active[active["crdc_wave"] == wave]
        w_clean = w_all[w_all["mean_class_size"] <= 60]
        
        for ccode in ["alg1", "geom", "alg2", "advm", "calc", "bio", "chem", "phys"]:
            ca = w_all[w_all["course_code"] == ccode]
            cc = w_clean[w_clean["course_code"] == ccode]
            if ca.empty:
                continue
                
            cname = ca["course_name"].iloc[0]
            
            cell_all = ca["mean_class_size"].mean()
            cell_clean = cc["mean_class_size"].mean()
            
            seat_all = (ca["num_enrolled"] * ca["mean_class_size"]).sum() / ca["num_enrolled"].sum()
            seat_clean = (cc["num_enrolled"] * cc["mean_class_size"]).sum() / cc["num_enrolled"].sum()
            
            med_all = ca["mean_class_size"].median()
            med_clean = cc["mean_class_size"].median()
            
            p90_all = ca["mean_class_size"].quantile(0.90)
            p90_clean = cc["mean_class_size"].quantile(0.90)
            
            n_gt60 = (ca["mean_class_size"] > 60).sum()
            
            sens_rows.append({
                "wave": wave,
                "course_code": ccode,
                "course_name": cname,
                "n_cells_total": len(ca),
                "n_cells_gt60": n_gt60,
                "pct_cells_gt60": (n_gt60 / len(ca)) * 100,
                "cell_mean_clean": cell_clean,
                "cell_mean_all": cell_all,
                "cell_mean_delta": cell_all - cell_clean,
                "seat_mean_clean": seat_clean,
                "seat_mean_all": seat_all,
                "seat_mean_delta": seat_all - seat_clean,
                "median_clean": med_clean,
                "median_all": med_all,
                "p90_clean": p90_clean,
                "p90_all": p90_all,
            })
            
    df_sens = pd.DataFrame(sens_rows)
    sens_path = TABLES_DIR / "table07_cutoff_sensitivity_audit.csv"
    df_sens.to_csv(sens_path, index=False)
    print(f"\n--> Saved Sensitivity Audit Table to {sens_path}")
    return df_sens

def audit_reference_dates():
    """
    CRDC Reference Date Audit:
    Documents the exact numerator (enrollment) and denominator (classes) snapshot dates
    by wave and course based on OCR documentation and survey submission forms.
    """
    print("\n" + "=" * 70)
    print("AUDIT 2: CRDC NUMERATOR AND DENOMINATOR REFERENCE DATES")
    print("=" * 70)
    
    # Official OCR specifications:
    # 2013-14: Fall census date (Oct 1 or district official fall date) for both classes and enrollment.
    # 2015-16: Fall census date (Oct 1) for course classes and enrollment.
    # 2017-18: Fall census date (Oct 1) for course classes and enrollment.
    # 2020-21: Fall census date (Oct 1) for course classes and enrollment (pandemic collection).
    # 2021-22: Fall census date (Oct 1) for course classes and enrollment.
    # 2023-24:
    #   - Algebra I:
    #       Classes (SCH_MATHCLASSES_ALG): "Count of classes on October 1, 2023 (or district fall snapshot)"
    #       Enrollment (TOT_ALGENR_GS0910, TOT_ALGENR_GS1112): "Students who were enrolled in Algebra I on any day during regular 2023-24 school year" (cumulative/completion snapshot!)
    #       ==> CRITICAL DATE MISMATCH!
    #   - Geometry, Algebra II, Adv Math, Calculus, Biology, Chemistry, Physics:
    #       Classes: October 1, 2023
    #       Enrollment: October 1, 2023 (Fall snapshot)
    
    ref_audit = [
        {"wave": "2013-14", "course_code": "alg1", "course_name": "Algebra I",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2013)", "enr_ref_date": "Fall Snapshot (Oct 1, 2013)",
         "dates_contemporaneous": True, "notes": "Grades 7-12 combined universe."},
        {"wave": "2013-14", "course_code": "geom", "course_name": "Geometry",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2013)", "enr_ref_date": "Fall Snapshot (Oct 1, 2013)",
         "dates_contemporaneous": True, "notes": "Grades 7-12 combined universe."},
        {"wave": "2013-14", "course_code": "other", "course_name": "Alg II, Calc, Bio, Chem, Phys",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2013)", "enr_ref_date": "Fall Snapshot (Oct 1, 2013)",
         "dates_contemporaneous": True, "notes": "Standard fall snapshot across classes and enrollments."},
         
        {"wave": "2015-16", "course_code": "alg1", "course_name": "Algebra I",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2015)", "enr_ref_date": "Fall Snapshot (Oct 1, 2015)",
         "dates_contemporaneous": True, "notes": "Grades 9-12 high school snapshot."},
        {"wave": "2015-16", "course_code": "all_others", "course_name": "All Other Secondary Courses",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2015)", "enr_ref_date": "Fall Snapshot (Oct 1, 2015)",
         "dates_contemporaneous": True, "notes": "Fall snapshot across classes and enrollments."},
         
        {"wave": "2017-18", "course_code": "all", "course_name": "All Secondary Courses",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2017)", "enr_ref_date": "Fall Snapshot (Oct 1, 2017)",
         "dates_contemporaneous": True, "notes": "Fall snapshot across classes and enrollments."},
         
        {"wave": "2020-21", "course_code": "all", "course_name": "All Secondary Courses",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2020)", "enr_ref_date": "Fall Snapshot (Oct 1, 2020)",
         "dates_contemporaneous": True, "notes": "Pandemic collection; hybrid/remote master schedules."},
         
        {"wave": "2021-22", "course_code": "all", "course_name": "All Secondary Courses",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2021)", "enr_ref_date": "Fall Snapshot (Oct 1, 2021)",
         "dates_contemporaneous": True, "notes": "Contemporaneous fall snapshots."},
         
        {"wave": "2023-24", "course_code": "alg1", "course_name": "Algebra I",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2023)", "enr_ref_date": "End-of-Year Cumulative (Spring 2024)",
         "dates_contemporaneous": False, "notes": "DATE MISMATCH: Classes measured Oct 1; enrollment includes students enrolled on any day during regular school year. May inflate enrollment relative to fall class count, or introduce denominator mismatch."},
        {"wave": "2023-24", "course_code": "geom", "course_name": "Geometry",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2023)", "enr_ref_date": "Fall Snapshot (Oct 1, 2023)",
         "dates_contemporaneous": True, "notes": "Contemporaneous fall snapshot."},
        {"wave": "2023-24", "course_code": "other_courses", "course_name": "Alg II, Adv Math, Calc, Bio, Chem, Phys",
         "classes_ref_date": "Fall Snapshot (Oct 1, 2023)", "enr_ref_date": "Fall Snapshot (Oct 1, 2023)",
         "dates_contemporaneous": True, "notes": "Contemporaneous fall snapshot."},
    ]
    df_ref = pd.DataFrame(ref_audit)
    ref_path = TABLES_DIR / "table08_reference_dates_audit.csv"
    df_ref.to_csv(ref_path, index=False)
    print(df_ref[["wave", "course_name", "classes_ref_date", "enr_ref_date", "dates_contemporaneous"]].to_string(index=False))
    print(f"\n--> Saved Reference Dates Audit Table to {ref_path}")
    return df_ref

if __name__ == "__main__":
    audit_gt60_exclusions()
    audit_reference_dates()
