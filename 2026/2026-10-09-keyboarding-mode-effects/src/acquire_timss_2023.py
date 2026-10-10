"""
TIMSS 2023 U.S. Grade 4 Microdata Acquisition & Admission Pipeline
Streams and extracts U.S. Grade 4 public-use microdata (SPSS files) directly from
the official IEA TIMSS 2023 International Database using HTTP Range requests.
Downloads Item Information codebooks and establishes exact sample accounting.
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
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2023"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"

RAW_DIR.mkdir(parents=True, exist_ok=True)
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
    dest = RAW_DIR / "T23_ItemInformation_G4.xlsx"
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
    
    needed = [f for f in target_files if not (RAW_DIR / Path(f).name).exists()]
    if not needed:
        print("[OK] All U.S. 2023 microdata files already present in raw directory.")
        return
        
    print(f"Connecting to remote ZIP archive ({SPSS_ZIP_URL}) via HTTP Range requests...")
    remote_f = RemoteZipFile(SPSS_ZIP_URL)
    with zipfile.ZipFile(remote_f) as zf:
        for tf in needed:
            dest_file = RAW_DIR / Path(tf).name
            print(f"Extracting {tf} -> {dest_file.name}...")
            with zf.open(tf) as src, open(dest_file, "wb") as out:
                chunk = src.read(1024 * 1024)
                while chunk:
                    out.write(chunk)
                    chunk = src.read(1024 * 1024)
            print(f"  [OK] Saved {dest_file.name} ({dest_file.stat().st_size / (1024*1024):.2f} MB)")


def audit_sample_and_crosswalk(df_info23: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Establish exact sample accounting for U.S. Grade 4 in TIMSS 2023 and crosswalk
    common trend items against 2019 eTIMSS (asausam7.sav).
    """
    asa_path = RAW_DIR / "asausam8.sav"
    df_asa23, meta23 = pyreadstat.read_sav(asa_path)
    
    # 1. Sample Accounting
    n_students_23 = len(df_asa23)
    n_schools_23 = df_asa23["IDSCHOOL"].nunique()
    n_classes_23 = df_asa23["IDCLASS"].nunique()
    n_booklets_23 = df_asa23["IDBOOK"].nunique()
    
    # Plausible values
    pv_cols = [c for c in df_asa23.columns if c.startswith("ASMMAT0")]
    mean_pv1 = df_asa23["ASMMAT01"].mean() if pv_cols else np.nan
    w_mean_pv1 = np.average(df_asa23["ASMMAT01"], weights=df_asa23["TOTWGT"]) if pv_cols else np.nan
    
    sample_acc = pd.DataFrame([{
        "assessment_cycle": "TIMSS 2023 (Cycle 8)",
        "grade": "Grade 4",
        "sample_design": "Group-Adaptive Digital (Chromebooks)",
        "total_assessed_students": n_students_23,
        "total_schools": n_schools_23,
        "total_classes": n_classes_23,
        "total_booklets": n_booklets_23,
        "unweighted_math_pv1": round(float(mean_pv1), 2),
        "population_weighted_math_pv1": round(float(w_mean_pv1), 2),
        "official_published_math_scale_score": 517.0
    }])
    
    # 2. Common Trend Items with 2019 eTIMSS
    raw_19_path = PROJECT_ROOT / "data" / "raw" / "timss_2019" / "asausam7.sav"
    df_asa19, meta19 = pyreadstat.read_sav(raw_19_path)
    items19 = set([c for c in meta19.column_names if c.startswith("M")])
    
    math23 = df_info23[df_info23["Subject"] == "M"].copy()
    math23["in_2019_etimss"] = math23["Item ID"].isin(items19)
    math23["in_2023_asa"] = math23["Item ID"].isin(df_asa23.columns)
    
    common = math23[math23["in_2019_etimss"] & math23["in_2023_asa"]].copy()
    
    # Add response counts for both cycles and administration flags
    common_records = []
    for _, row in common.iterrows():
        iid = row["Item ID"]
        itype = row["Item Type"]
        max_pts = float(row["Maximum Points"]) if pd.notna(row["Maximum Points"]) else 1.0
        c_domain = row.get("Content Domain", "")
        cog_domain = row.get("Cognitive Domain", "")
        sec_status = row.get("Secure Status", "")
        scale_status = row.get("Scaling Status", "")
        block = row.get("Block", "")
        
        n19 = int(df_asa19[iid].notna().sum()) if iid in df_asa19.columns else 0
        n23 = int(df_asa23[iid].notna().sum()) if iid in df_asa23.columns else 0
        
        common_records.append({
            "item_id": iid,
            "item_type": itype,
            "format": "Multiple Choice" if itype == "MC" else "Constructed Response",
            "max_points": max_pts,
            "content_domain": c_domain,
            "cognitive_domain": cog_domain,
            "secure_status": sec_status,
            "scaling_status": scale_status,
            "block_2023": block,
            "n_examinees_2019": n19,
            "n_examinees_2023": n23,
            "administered_2019": n19 > 0,
            "administered_2023": n23 > 0,
            "administered_both": (n19 > 0) and (n23 > 0)
        })
        
    df_common = pd.DataFrame(common_records)
    return sample_acc, df_common


def main():
    print("=" * 80)
    print("TIMSS 2023 U.S. Grade 4 Microdata Acquisition & Admission Pipeline")
    print("=" * 80)
    
    # 1. Acquire Item Info
    df_info23 = acquire_item_metadata()
    print(f"[OK] Loaded TIMSS 2023 Item Information: {len(df_info23)} total items")
    
    # 2. Extract US files from remote zip
    extract_us_microdata_files()
    
    # 3. Sample accounting and common-item crosswalk
    sample_acc, df_common = audit_sample_and_crosswalk(df_info23)
    
    # Export Table 18: Sample Accounting
    t18_path = TABLES_DIR / "table18_timss_2023_sample_accounting.csv"
    sample_acc.to_csv(t18_path, index=False)
    print(f"\n[OK] Table 18 generated -> {t18_path.name}")
    print(sample_acc.to_string(index=False))
    
    # Export Table 19: Common Item Crosswalk
    t19_path = TABLES_DIR / "table19_timss_2019_2023_item_crosswalk.csv"
    df_common.to_csv(t19_path, index=False)
    print(f"\n[OK] Table 19 generated -> {t19_path.name}")
    print(f"     Matched Common Mathematics Trend Items: {len(df_common)}")
    print(f"     Multiple Choice:     {(df_common['item_type']=='MC').sum()} items")
    print(f"     Constructed Response: {(df_common['item_type']=='CR').sum()} items")
    print(f"     Scaling Items:       {(df_common['scaling_status']=='Yes').sum()} items")
    
    # Export parquet
    crosswalk_parquet = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    df_common.to_parquet(crosswalk_parquet, index=False)
    print(f"[OK] Saved crosswalk parquet -> {crosswalk_parquet.name}")
    
    print("\n[SUCCESS] TIMSS 2023 admission & crosswalk pipeline complete.")


if __name__ == "__main__":
    main()
