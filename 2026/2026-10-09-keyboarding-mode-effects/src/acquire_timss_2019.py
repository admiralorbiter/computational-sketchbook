"""
Data Acquisition & Processing Pipeline: TIMSS 2019 U.S. Grade 4 Mode Effects Study
Audited public-use microdata processing for eTIMSS (digital) and Bridge (paper) studies.
"""

from pathlib import Path
import os
import urllib.request
import zipfile
import pyreadstat
import pandas as pd
import numpy as np

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2019"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ITEM_DIR = RAW_DIR / "item_info"
NCES_DIR = RAW_DIR / "nces_puf"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
ITEM_DIR.mkdir(parents=True, exist_ok=True)
NCES_DIR.mkdir(parents=True, exist_ok=True)

# URL Registry
URLS = {
    "iea_g4_usa": "https://timss2019.org/international-database/downloads/data/grade4/T19_G4_USA_SPSS.zip",
    "iea_g4_item_info": "https://timss2019.org/international-database/downloads/T19_G4_Item%20Information.zip",
    "nces_bridge_puf": "https://nces.ed.gov/pubs2022/data/bridgeTIMSS_2019_codebooks_data_code_files_PUF.zip",
    "nces_etimss_puf": "https://nces.ed.gov/pubs2022/data/eTIMSS_2019_codebooks_data_code_files_PUF.zip",
}

def download_file(url: str, dest_path: Path) -> Path:
    """Download a remote URL to local path if not already cached."""
    if not dest_path.exists():
        print(f"[DOWNLOAD] Fetching {url} -> {dest_path.name}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        print(f"[OK] Downloaded {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
    else:
        print(f"[CACHE] Using existing {dest_path.name}")
    return dest_path


def extract_files():
    """Extract required SPSS data files and Excel item information."""
    # 1. Item info
    item_zip = download_file(URLS["iea_g4_item_info"], RAW_DIR / "T19_G4_Item_Information.zip")
    with zipfile.ZipFile(item_zip) as z:
        z.extractall(ITEM_DIR)

    # 2. IEA USA SPSS files
    usa_zip = download_file(URLS["iea_g4_usa"], RAW_DIR / "T19_G4_USA_SPSS.zip")
    needed_sav = ["asausab7.sav", "asausam7.sav", "asgusab7.sav", "asgusam7.sav", "acgusab7.sav", "acgusam7.sav"]
    with zipfile.ZipFile(usa_zip) as z:
        for fname in needed_sav:
            if not (RAW_DIR / fname).exists():
                z.extract(fname, RAW_DIR)

    # 3. NCES PUF Bridge
    br_puf_zip = download_file(URLS["nces_bridge_puf"], RAW_DIR / "bridge_puf.zip")
    with zipfile.ZipFile(br_puf_zip) as z:
        z.extractall(NCES_DIR)

    # 4. NCES PUF eTIMSS
    e_puf_zip = download_file(URLS["nces_etimss_puf"], RAW_DIR / "etimss_puf.zip")
    with zipfile.ZipFile(e_puf_zip) as z:
        z.extractall(NCES_DIR)


def parse_nces_school_data() -> pd.DataFrame:
    """Parse school poverty and sector from NCES supplemental raw .dat files."""
    # Bridge schools
    br_dat = NCES_DIR / "bridgeTIMSS 2019 codebooks_data_code files PUF" / "TIMSS 2019 Grade 4 Raw Data" / "T4_SCHOOL19_BRIDGE.dat"
    br_schools = []
    with open(br_dat, "r") as f:
        for line in f:
            if len(line) >= 18:
                idschool = int(line[3:7])
                pctfrpl = line[16:17].strip()
                pubpriv = line[17:18].strip()
                br_schools.append({
                    "IDSCHOOL": idschool,
                    "PCTFRPL": int(pctfrpl) if pctfrpl.isdigit() else np.nan,
                    "PUBPRIV": int(pubpriv) if pubpriv.isdigit() else np.nan,
                    "study_mode": "Bridge_Paper"
                })
    df_br_sch = pd.DataFrame(br_schools)

    # eTIMSS schools
    e_dat = NCES_DIR / "eTIMSS 2019 codebooks_data_code files PUF" / "TIMSS 2019 Grade 4 Raw Data" / "T4_SCHOOL19.dat"
    e_schools = []
    with open(e_dat, "r") as f:
        for line in f:
            if len(line) >= 19:
                idschool = int(line[3:7])
                pctfrpl = line[17:18].strip()
                pubpriv = line[18:19].strip()
                e_schools.append({
                    "IDSCHOOL": idschool,
                    "PCTFRPL": int(pctfrpl) if pctfrpl.isdigit() else np.nan,
                    "PUBPRIV": int(pubpriv) if pubpriv.isdigit() else np.nan,
                    "study_mode": "eTIMSS_Digital"
                })
    df_e_sch = pd.DataFrame(e_schools)
    return pd.concat([df_br_sch, df_e_sch], ignore_index=True)


def build_item_contrasts() -> pd.DataFrame:
    """Calculate survey-weighted item percent correct and mode differences across all 99 common items."""
    # 1. Load item metadata
    br_item_path = ITEM_DIR / "T19Br_G4_Item Information.xlsx"
    items_df = pd.read_excel(br_item_path, sheet_name="MAT")
    items_df["core_id"] = items_df["Item ID"].str[2:]

    # 2. Load achievement files
    df_br_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausab7.sav")
    df_e_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausam7.sav")

    results = []

    for _, row in items_df.iterrows():
        cid = row["core_id"]
        itype = row["Item Type"]
        max_pts = row["Maximum Points"]
        key = row["Key"]

        col_br = "MP" + cid
        col_e = "ME" + cid

        if col_br not in df_br_ach.columns or col_e not in df_e_ach.columns:
            continue

        sub_br = df_br_ach[df_br_ach[col_br].notna()].copy()
        sub_e = df_e_ach[df_e_ach[col_e].notna()].copy()

        if len(sub_br) == 0 or len(sub_e) == 0:
            continue

        w_br = sub_br["TOTWGT"]
        w_e = sub_e["TOTWGT"]

        if itype == "MC":
            key_num = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0}.get(key)
            score_br = (sub_br[col_br] == key_num).astype(float)
            score_e = (sub_e[col_e] == key_num).astype(float)
            omit_br = (sub_br[col_br] == 9.0).astype(float)
            omit_e = (sub_e[col_e] == 9.0).astype(float)
        else: # CR
            if max_pts == 1:
                score_br = (sub_br[col_br] == 10.0).astype(float)
                score_e = (sub_e[col_e] == 10.0).astype(float)
            elif max_pts == 2:
                score_br = np.where(sub_br[col_br] == 20.0, 1.0, np.where(sub_br[col_br] == 10.0, 0.5, 0.0))
                score_e = np.where(sub_e[col_e] == 20.0, 1.0, np.where(sub_e[col_e] == 10.0, 0.5, 0.0))
            else:
                score_br = (sub_br[col_br] == 10.0).astype(float)
                score_e = (sub_e[col_e] == 10.0).astype(float)
            omit_br = (sub_br[col_br] == 99.0).astype(float)
            omit_e = (sub_e[col_e] == 99.0).astype(float)

        pct_paper = np.average(score_br, weights=w_br) * 100.0
        pct_digital = np.average(score_e, weights=w_e) * 100.0
        diff_pp = pct_digital - pct_paper

        pct_omit_paper = np.average(omit_br, weights=w_br) * 100.0
        pct_omit_digital = np.average(omit_e, weights=w_e) * 100.0

        results.append({
            "item_id": row["Item ID"],
            "core_id": cid,
            "label": row["Label"],
            "item_type": itype,
            "maximum_points": max_pts,
            "content_domain": row["Content Domain"],
            "topic_area": row["Topic Area"],
            "cognitive_domain": row["Cognitive Domain"],
            "n_paper_students": len(sub_br),
            "n_digital_students": len(sub_e),
            "pct_paper": round(pct_paper, 2),
            "pct_digital": round(pct_digital, 2),
            "diff_pp": round(diff_pp, 2),
            "omit_paper_pct": round(pct_omit_paper, 2),
            "omit_digital_pct": round(pct_omit_digital, 2),
            "omit_diff_pp": round(pct_omit_digital - pct_omit_paper, 2)
        })

    return pd.DataFrame(results)


def build_student_level_dataset() -> pd.DataFrame:
    """Merge student plausible values, sampling weights, home resources, and school characteristics."""
    # 1. Bridge
    df_br_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausab7.sav")
    df_br_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusab7.sav")
    df_br = pd.merge(
        df_br_ach[["IDSTUD", "IDSCHOOL", "IDCLASS", "TOTWGT", "ASMMAT01", "ASMMAT02", "ASMMAT03", "ASMMAT04", "ASMMAT05"]],
        df_br_stu[["IDSTUD", "ASBG04", "ASBG05A", "ASBG05D", "ASDG05S"]],
        on="IDSTUD"
    )
    df_br["study_mode"] = "Bridge_Paper"

    # 2. eTIMSS
    df_e_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausam7.sav")
    df_e_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusam7.sav")
    df_e = pd.merge(
        df_e_ach[["IDSTUD", "IDSCHOOL", "IDCLASS", "TOTWGT", "ASMMAT01", "ASMMAT02", "ASMMAT03", "ASMMAT04", "ASMMAT05"]],
        df_e_stu[["IDSTUD", "ASBG04", "ASBG05A", "ASBG05D", "ASDG05S"]],
        on="IDSTUD"
    )
    df_e["study_mode"] = "eTIMSS_Digital"

    # Combine students
    df_all_stu = pd.concat([df_br, df_e], ignore_index=True)

    # 3. Merge School Poverty from NCES
    df_sch = parse_nces_school_data()
    df_merged = pd.merge(df_all_stu, df_sch[["IDSCHOOL", "study_mode", "PCTFRPL", "PUBPRIV"]], on=["IDSCHOOL", "study_mode"], how="left")

    return df_merged


def main():
    print("=" * 80)
    print("TIMSS 2019 Grade 4 U.S. Data Acquisition & Processing")
    print("=" * 80)

    # Step 1: Extract files
    extract_files()

    # Step 2: Build Item Contrasts
    print("[PROCESS] Building item-level mode contrasts for 99 anchor items...")
    item_df = build_item_contrasts()
    item_csv = PROCESSED_DIR / "timss_2019_g4_item_contrasts.csv"
    item_parquet = PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet"
    item_df.to_csv(item_csv, index=False)
    item_df.to_parquet(item_parquet, index=False)
    print(f"[OK] Wrote {len(item_df)} item records to {item_csv.name} and {item_parquet.name}")

    # Summary by format
    print("\n--- Summary by Item Type ---")
    print(item_df.groupby("item_type")["diff_pp"].agg(["count", "mean", "std", "min", "median", "max"]))

    # Step 3: Build Student-Level Dataset
    print("\n[PROCESS] Building merged student-level dataset with Plausible Values...")
    stu_df = build_student_level_dataset()
    stu_csv = PROCESSED_DIR / "timss_2019_g4_student_pvs.csv"
    stu_parquet = PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet"
    stu_df.to_csv(stu_csv, index=False)
    stu_df.to_parquet(stu_parquet, index=False)
    print(f"[OK] Wrote {len(stu_df)} student records to {stu_csv.name} and {stu_parquet.name}")

    print("\n--- Student Counts by Mode ---")
    print(stu_df["study_mode"].value_counts())

    print("\n[SUCCESS] TIMSS 2019 Grade 4 microdata successfully acquired and processed.")


if __name__ == "__main__":
    main()
