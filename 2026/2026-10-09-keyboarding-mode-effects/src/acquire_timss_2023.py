"""
TIMSS 2023 U.S. Grade 4 Microdata Acquisition, Admission & Longitudinal Crosswalk Pipeline
Streams and extracts U.S. Grade 4 public-use microdata (SPSS files) directly from
the official IEA TIMSS 2023 International Database using HTTP Range requests.
Audits sample accounting against official national benchmarks across all 5 plausible values.
Reconciles the 2019-2023 common mathematics items across all 8 trend blocks, complete
denominators with user-missing recovery, official 107-item trend scaling, and screen timing metrics.
"""

from pathlib import Path
import urllib.request
import zipfile
import io
import os
import openpyxl
import numpy as np
import pandas as pd
import pyreadstat

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_23_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2023"
RAW_19_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2019"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"

RAW_23_DIR.mkdir(parents=True, exist_ok=True)
RAW_19_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

ITEM_INFO_URL = "https://timss2023.org/wp-content/uploads/data/T23_ItemInformation_G4.xlsx"
SPSS_ZIP_URL = "https://timss2023.org/wp-content/uploads/data/T23_Data_SPSS_G4.zip"


class RemoteZipFile:
    """File-like object supporting seek/read via HTTP Range requests."""
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as resp:
            self.length = int(resp.headers["Content-Length"])
        self.pos = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.pos = offset
        elif whence == io.SEEK_CUR:
            self.pos += offset
        elif whence == io.SEEK_END:
            self.pos = self.length + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        if size == -1:
            end = self.length - 1
        else:
            end = min(self.pos + size - 1, self.length - 1)
        if self.pos > end:
            return b""
        
        req = urllib.request.Request(self.url)
        req.headers["Range"] = f"bytes={self.pos}-{end}"
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
        self.pos += len(data)
        return data


def acquire_item_metadata() -> pd.DataFrame:
    """Download and return the official TIMSS 2023 Grade 4 Item Information dictionary."""
    dest = RAW_23_DIR / "T23_ItemInformation_G4.xlsx"
    if not dest.exists():
        print(f"Downloading Item Information codebook from {ITEM_INFO_URL}...")
        urllib.request.urlretrieve(ITEM_INFO_URL, dest)
        print(f"[OK] Downloaded {dest.name} ({dest.stat().st_size / 1024:.1f} KB)")
        
    df = pd.read_excel(dest, sheet_name="T23 G4")
    df.columns = [c.strip() for c in df.columns]
    return df


def extract_us_microdata_files():
    """Extract U.S. Grade 4 SPSS files from remote ZIP archive using Range requests."""
    target_files = [
        "SPSS Data/asausam8.sav",
        "SPSS Data/asrusam8.sav",
        "SPSS Data/asgusam8.sav",
        "SPSS Data/ashusam8.sav",
        "SPSS Data/acgusam8.sav",
        "SPSS Data/aspusam8.sav",
        "SPSS Data/astusam8.sav",
        "SPSS Data/atgusam8.sav"
    ]
    
    needed = [f for f in target_files if not (RAW_23_DIR / Path(f).name).exists()]
    if not needed:
        print("[OK] All U.S. 2023 microdata files already present in raw directory.")
    else:
        print(f"Connecting to remote ZIP archive ({SPSS_ZIP_URL}) via HTTP Range requests...")
        remote_f = RemoteZipFile(SPSS_ZIP_URL)
        with zipfile.ZipFile(remote_f) as zf:
            for tf in needed:
                dest_file = RAW_23_DIR / Path(tf).name
                print(f"Extracting {tf} -> {dest_file.name}...")
                with zf.open(tf) as src, open(dest_file, "wb") as out:
                    chunk = src.read(1024 * 1024)
                    while chunk:
                        out.write(chunk)
                        chunk = src.read(1024 * 1024)
                print(f"  [OK] Saved {dest_file.name} ({dest_file.stat().st_size / (1024*1024):.2f} MB)")

    # Ensure 2019 asausaz7.sav (eTIMSS with PSI) is extracted locally
    z7_dest = RAW_19_DIR / "asausaz7.sav"
    if not z7_dest.exists():
        zip_19_path = RAW_19_DIR / "T19_G4_USA_SPSS.zip"
        if zip_19_path.exists():
            print("Extracting 2019 asausaz7.sav from local T19_G4_USA_SPSS.zip...")
            with zipfile.ZipFile(zip_19_path) as zf:
                zf.extract("asausaz7.sav", RAW_19_DIR)
            print(f"  [OK] Extracted {z7_dest.name} ({z7_dest.stat().st_size / (1024*1024):.2f} MB)")


def audit_sample_and_crosswalk(df_info23: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Establish exact sample accounting across 5 plausible values for both 2019 and 2023,
    and build the three-tier longitudinal common-item crosswalk.
    """
    # 1. Load microdata with user_missing=True to recover complete response codes
    df_asa23, meta23 = pyreadstat.read_sav(RAW_23_DIR / "asausam8.sav", user_missing=True)
    df_asp23, meta_asp23 = pyreadstat.read_sav(RAW_23_DIR / "aspusam8.sav", user_missing=False)
    df_asa19, meta19 = pyreadstat.read_sav(RAW_19_DIR / "asausaz7.sav", user_missing=True)
    df_asa19_m7, _ = pyreadstat.read_sav(RAW_19_DIR / "asausam7.sav", user_missing=True)
    
    # 2. National Sample Accounting (Replicating Official 5-PV Benchmarks)
    pv_cols = [f"ASMMAT0{i}" for i in range(1, 6)]
    
    w_23 = df_asa23["TOTWGT"]
    pv_means_23 = [np.average(df_asa23[pv], weights=w_23) for pv in pv_cols]
    overall_mean_23 = np.mean(pv_means_23)
    
    w_19_m7 = df_asa19_m7["TOTWGT"]
    pv_means_19_m7 = [np.average(df_asa19_m7[pv], weights=w_19_m7) for pv in pv_cols]
    overall_mean_19_m7 = np.mean(pv_means_19_m7)
    
    w_19_z7 = df_asa19["TOTWGT"]
    pv_means_19_z7 = [np.average(df_asa19[pv], weights=w_19_z7) for pv in pv_cols]
    overall_mean_19_z7 = np.mean(pv_means_19_z7)
    
    sample_acc = pd.DataFrame([
        {
            "assessment_cycle": "TIMSS 2019 (Official eTIMSS)",
            "grade": "Grade 4",
            "sample_design": "eTIMSS Digital (Booklets 1–14)",
            "total_assessed_students": len(df_asa19_m7),
            "total_schools": df_asa19_m7["IDSCHOOL"].nunique(),
            "total_classes": df_asa19_m7["IDCLASS"].nunique(),
            "total_booklets": df_asa19_m7["IDBOOK"].nunique(),
            "population_weighted_pv1": round(float(pv_means_19_m7[0]), 2),
            "population_weighted_5pv_mean": round(float(overall_mean_19_m7), 2),
            "official_published_math_scale_score": 535.0,
            "reconciliation_delta": round(float(overall_mean_19_m7 - 535.0), 2)
        },
        {
            "assessment_cycle": "TIMSS 2019 (eTIMSS + PSI)",
            "grade": "Grade 4",
            "sample_design": "eTIMSS Digital + PSI (Booklets 1–16)",
            "total_assessed_students": len(df_asa19),
            "total_schools": df_asa19["IDSCHOOL"].nunique(),
            "total_classes": df_asa19["IDCLASS"].nunique(),
            "total_booklets": df_asa19["IDBOOK"].nunique(),
            "population_weighted_pv1": round(float(pv_means_19_z7[0]), 2),
            "population_weighted_5pv_mean": round(float(overall_mean_19_z7), 2),
            "official_published_math_scale_score": 535.0,
            "reconciliation_delta": round(float(overall_mean_19_z7 - 535.0), 2)
        },
        {
            "assessment_cycle": "TIMSS 2023 (Official Digital)",
            "grade": "Grade 4",
            "sample_design": "Group-Adaptive Digital (Booklets 1–14)",
            "total_assessed_students": len(df_asa23),
            "total_schools": df_asa23["IDSCHOOL"].nunique(),
            "total_classes": df_asa23["IDCLASS"].nunique(),
            "total_booklets": df_asa23["IDBOOK"].nunique(),
            "population_weighted_pv1": round(float(pv_means_23[0]), 2),
            "population_weighted_5pv_mean": round(float(overall_mean_23), 2),
            "official_published_math_scale_score": 517.0,
            "reconciliation_delta": round(float(overall_mean_23 - 517.0), 2)
        }
    ])
    
    # 3. Longitudinal Common-Item Crosswalk across all 8 Trend Blocks
    trend_blocks = ["A_MD1", "A_MD2", "A_MD4", "A_ME2", "A_ME4", "A_MM2", "A_MM3", "A_MM4"]
    trend_info = df_info23[(df_info23["Subject"] == "M") & (df_info23["Block"].isin(trend_blocks))].copy()
    
    cols19 = set(df_asa19.columns)
    cols23 = set(df_asa23.columns)
    cols23_p = set(df_asp23.columns)
    
    crosswalk_records = []
    for _, row in trend_info.iterrows():
        iid23 = row["Item ID"]
        itype = row["Item Type"]
        block = row["Block"]
        scale_stat = row["Scaling Status"]
        max_pts = float(row["Maximum Points"]) if pd.notna(row["Maximum Points"]) else 1.0
        lbl = row["Label"]
        c_domain = row.get("Content Domain", "")
        cog_domain = row.get("Cognitive Domain", "")
        screen_id = str(row.get("Screen ID", iid23))
        
        # In 2019, block A_MD4 (PSI MI01) items were coded MQ11... instead of MQ71...
        iid19 = iid23.replace("MQ71", "MQ11") if block == "A_MD4" else iid23
        screen19 = screen_id.replace("M71", "M11") if block == "A_MD4" else screen_id
        
        # 2019 Response Status Breakdown (user_missing=True)
        if iid19 in cols19:
            s19 = df_asa19[iid19].dropna()
            n_admin_19 = len(s19)
            if itype == "MC":
                n_omit_19 = int((s19 == 9.0).sum())
                n_nr_19 = int((s19 == 6.0).sum())
            else:
                n_omit_19 = int((s19 == 99.0).sum())
                n_nr_19 = int((s19 == 96.0).sum())
            n_ans_19 = n_admin_19 - n_omit_19 - n_nr_19
        else:
            n_admin_19 = n_ans_19 = n_omit_19 = n_nr_19 = 0
            
        # 2023 Response Status Breakdown (user_missing=True)
        if iid23 in cols23:
            s23 = df_asa23[iid23].dropna()
            n_admin_23 = len(s23)
            if itype == "MC":
                n_omit_23 = int((s23 == 9.0).sum())
                n_nr_23 = int((s23 == 6.0).sum())
            else:
                n_omit_23 = int((s23 == 99.0).sum())
                n_nr_23 = int((s23 == 96.0).sum())
            n_ans_23 = n_admin_23 - n_omit_23 - n_nr_23
        else:
            n_admin_23 = n_ans_23 = n_omit_23 = n_nr_23 = 0
            
        # Process Screen Timing (Seconds on Screen)
        # 2019 timing candidates: item_S, screen_S, or base 7-char screen_S
        tcol19 = None
        for cand in [f"{iid19}_S", f"{screen19}_S", f"{iid19[:7]}_S"]:
            if cand in cols19:
                tcol19 = cand
                break
        if tcol19 is not None and n_admin_19 > 0:
            ts19 = df_asa19[tcol19].dropna()
            ts19 = ts19[ts19 < 90000]
            if len(ts19) > 0:
                m_t19 = round(float(ts19.mean()), 1)
                med_t19 = round(float(ts19.median()), 1)
                has_t19 = True
            else:
                m_t19 = med_t19 = np.nan
                has_t19 = False
        else:
            m_t19 = med_t19 = np.nan
            has_t19 = False
            
        # 2023 timing candidates in aspusam8.sav
        tcol23 = None
        for cand in [f"{screen_id}_S", f"{iid23}_S", f"{iid23[:7]}_S"]:
            if cand in cols23_p:
                tcol23 = cand
                break
        if tcol23 is not None and n_admin_23 > 0:
            ts23 = df_asp23[tcol23].dropna()
            ts23 = ts23[ts23 < 90000]
            if len(ts23) > 0:
                m_t23 = round(float(ts23.mean()), 1)
                med_t23 = round(float(ts23.median()), 1)
                has_t23 = True
            else:
                m_t23 = med_t23 = np.nan
                has_t23 = False
        else:
            m_t23 = med_t23 = np.nan
            has_t23 = False
            
        # Three-way reconciliation taxonomy
        admin_both = bool(n_admin_19 > 0 and n_admin_23 > 0)
        is_scale = (scale_stat == "Yes")
        is_standalone_unscaled = iid23 in ["ME61021", "MQ71A01", "MQ71A03A"]
        is_official_trend = bool(is_scale or is_standalone_unscaled)
        
        in_primary = bool(is_scale and admin_both)
        in_standard = bool(block != "A_MD4" and admin_both)
        in_full = bool(admin_both)
        
        if in_primary:
            tier = "Primary Scaling (100)"
        elif in_standard:
            tier = "Standard eTIMSS Subpart (44)"
        elif in_full:
            tier = "PSI Interactive Unit (7)"
        else:
            tier = "Single-Cycle Unadministered (6)"
            
        crosswalk_records.append({
            "item_id_2023": iid23,
            "item_id_2019": iid19,
            "screen_id": screen_id,
            "block": block,
            "format": "Multiple Choice" if itype == "MC" else "Constructed Response",
            "item_type": itype,
            "content_domain": c_domain,
            "cognitive_domain": cog_domain,
            "scaling_status": scale_stat,
            "max_points": max_pts,
            "is_official_trend_item": is_official_trend,
            "in_primary_scaling_sample": in_primary,
            "in_standard_etimss_sample": in_standard,
            "in_full_trend_sample": in_full,
            "sample_tier": tier,
            "n_admin_2019": n_admin_19,
            "n_answered_2019": n_ans_19,
            "n_omitted_2019": n_omit_19,
            "n_not_reached_2019": n_nr_19,
            "omission_rate_2019": round(n_omit_19 / n_admin_19, 4) if n_admin_19 > 0 else 0.0,
            "not_reached_rate_2019": round(n_nr_19 / n_admin_19, 4) if n_admin_19 > 0 else 0.0,
            "n_admin_2023": n_admin_23,
            "n_answered_2023": n_ans_23,
            "n_omitted_2023": n_omit_23,
            "n_not_reached_2023": n_nr_23,
            "omission_rate_2023": round(n_omit_23 / n_admin_23, 4) if n_admin_23 > 0 else 0.0,
            "not_reached_rate_2023": round(n_nr_23 / n_admin_23, 4) if n_admin_23 > 0 else 0.0,
            "has_timing_2019": has_t19,
            "mean_screen_time_2019": m_t19,
            "median_screen_time_2019": med_t19,
            "has_timing_2023": has_t23,
            "mean_screen_time_2023": m_t23,
            "median_screen_time_2023": med_t23,
            "screen_time_change": round(m_t23 - m_t19, 1) if (has_t19 and has_t23 and pd.notna(m_t23) and pd.notna(m_t19)) else np.nan,
            "label": lbl
        })
        
    df_cw = pd.DataFrame(crosswalk_records)
    return sample_acc, df_cw


def main():
    print("=" * 80)
    print("TIMSS 2023 U.S. Grade 4 Admission, Sample Accounting & Common-Item Crosswalk")
    print("=" * 80)
    
    # 1. Acquire Item Info
    df_info23 = acquire_item_metadata()
    print(f"[OK] Loaded TIMSS 2023 Item Information: {len(df_info23)} total items")
    
    # 2. Extract US files from remote zip & ensure 2019 asausaz7.sav is extracted
    extract_us_microdata_files()
    
    # 3. Sample accounting and common-item crosswalk
    sample_acc, df_cw = audit_sample_and_crosswalk(df_info23)
    
    # Export Table 18: Sample Accounting
    t18_path = TABLES_DIR / "table18_timss_2023_sample_accounting.csv"
    sample_acc.to_csv(t18_path, index=False)
    print(f"\n[OK] Table 18 generated -> {t18_path.name}")
    print(sample_acc.to_string(index=False))
    
    # Export Table 19: Common Item Crosswalk
    t19_path = TABLES_DIR / "table19_timss_2019_2023_item_crosswalk.csv"
    df_cw.to_csv(t19_path, index=False)
    print(f"\n[OK] Table 19 generated -> {t19_path.name}")
    print(f"     Total Items in 8 Trend Blocks:             {len(df_cw)}")
    print(f"     Official 2023 Trend Items (NCES Notes):   {df_cw['is_official_trend_item'].sum()} items (104 scaling + 3 unscaled standalone)")
    print(f"     Primary Analytical Sample (Scaling Both): {df_cw['in_primary_scaling_sample'].sum()} items ({(df_cw[df_cw['in_primary_scaling_sample']]['item_type']=='MC').sum()} MC, {(df_cw[df_cw['in_primary_scaling_sample']]['item_type']=='CR').sum()} CR)")
    print(f"     Standard eTIMSS Sample (7 Blocks Both):   {df_cw['in_standard_etimss_sample'].sum()} items ({(df_cw[df_cw['in_standard_etimss_sample']]['item_type']=='MC').sum()} MC, {(df_cw[df_cw['in_standard_etimss_sample']]['item_type']=='CR').sum()} CR)")
    print(f"     Full Trend Pool (8 Blocks Both):          {df_cw['in_full_trend_sample'].sum()} items ({(df_cw[df_cw['in_full_trend_sample']]['item_type']=='MC').sum()} MC, {(df_cw[df_cw['in_full_trend_sample']]['item_type']=='CR').sum()} CR)")
    print(f"     Single-Cycle Unadministered:              {(~df_cw['in_full_trend_sample']).sum()} items")
    
    # Export parquet
    crosswalk_parquet = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    df_cw.to_parquet(crosswalk_parquet, index=False)
    print(f"[OK] Saved crosswalk parquet -> {crosswalk_parquet.name}")
    
    print("\n[SUCCESS] TIMSS 2023 admission & crosswalk pipeline complete.")


if __name__ == "__main__":
    main()
