"""
Data Acquisition & Processing Pipeline: TIMSS 2019 U.S. Grade 4 Mode Effects Study
Audited public-use microdata processing for eTIMSS (digital) and Bridge (paper) studies.
Implements IEA two-digit diagnostic response scoring, user-missing code recovery,
input modality classifications, and student-level format difference scores.
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
    "iea_g4_item_percent_correct": "https://timss2019.org/international-database/downloads/T19_G4_Item%20Percent%20Correct%20Statistics.zip",
    "nces_bridge_puf": "https://nces.ed.gov/pubs2022/data/bridgeTIMSS_2019_codebooks_data_code_files_PUF.zip",
    "nces_etimss_puf": "https://nces.ed.gov/pubs2022/data/eTIMSS_2019_codebooks_data_code_files_PUF.zip",
}

LETTER_TO_NUM = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0}

# Input modality taxonomies based on the TIMSS Equivalence Study (Fishbein, Foy, & Yin / Mullis et al.)
DRAWING_ITEMS = {
    "MP61080", "MP61076", "MP61084", "MP51080", "MP61079",
    "MP51079", "MP61081A", "MP61081B", "MP61264", "MP61224"
}
TEXT_ITEMS = {
    "MP51008", "MP61228", "MP61248", "MP61255", "MP61256"
}
TABLE_ITEMS = {
    "MP51043", "MP51508", "MP61018", "MP61240", "MP61266",
    "MP61095", "MP61254", "MP61236"
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
    needed_sav = [
        "asausab7.sav", "asausam7.sav", "asgusab7.sav", "asgusam7.sav",
        "acgusab7.sav", "acgusam7.sav", "asrusab7.sav", "asrusam7.sav"
    ]
    with zipfile.ZipFile(usa_zip) as z:
        for fname in needed_sav:
            dest = RAW_DIR / fname
            if not dest.exists():
                z.extract(fname, RAW_DIR)

    # 3. NCES PUF Bridge
    br_puf_zip = download_file(URLS["nces_bridge_puf"], RAW_DIR / "bridge_puf.zip")
    with zipfile.ZipFile(br_puf_zip) as z:
        z.extractall(NCES_DIR)

    # 4. NCES PUF eTIMSS
    e_puf_zip = download_file(URLS["nces_etimss_puf"], RAW_DIR / "etimss_puf.zip")
    with zipfile.ZipFile(e_puf_zip) as z:
        z.extractall(NCES_DIR)

    # 5. IEA Published Item Percent Correct Statistics
    pct_dir = RAW_DIR / "iea_item_percent_correct"
    pct_dir.mkdir(exist_ok=True)
    pct_zip = download_file(URLS["iea_g4_item_percent_correct"], RAW_DIR / "T19_G4_Item_Percent_Correct.zip")
    with zipfile.ZipFile(pct_zip) as z:
        for fname in ["T19Br_G4_MAT_Item Percent Correct.xlsx", "eT19_G4_MAT_Item Percent Correct.xlsx"]:
            dest = pct_dir / fname
            if not dest.exists():
                z.extract(fname, pct_dir)


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


def score_response_series(s: pd.Series, itype: str, max_pts: int, key: str):
    """
    Apply official IEA TIMSS two-digit diagnostic scoring and response classification.
    
    Returns:
        score: float array (0.0 to 1.0 representing proportion of maximum item points)
        is_admin: boolean mask of administered students (s is not NaN)
        is_omit: boolean mask of omitted items (code 9.0 on MC, 99.0 on CR)
        is_nr: boolean mask of not reached items (code 6.0 on MC, 96.0 on CR)
        is_valid: boolean mask of valid attempted responses
    """
    is_admin = s.notna().values
    vals = s.values
    n = len(vals)
    score = np.zeros(n, dtype=float)
    is_omit = np.zeros(n, dtype=bool)
    is_nr = np.zeros(n, dtype=bool)
    is_valid = np.zeros(n, dtype=bool)

    if itype == "MC":
        key_str = str(key).strip() if pd.notna(key) else ""
        correct_num = LETTER_TO_NUM.get(key_str, np.nan)
        is_omit[is_admin] = (vals[is_admin] == 9.0)
        is_nr[is_admin] = (vals[is_admin] == 6.0)
        is_valid[is_admin] = np.isin(vals[is_admin], [1.0, 2.0, 3.0, 4.0])
        score[is_admin] = np.where(vals[is_admin] == correct_num, 1.0, 0.0)
    else:  # CR
        is_omit[is_admin] = (vals[is_admin] == 99.0)
        is_nr[is_admin] = (vals[is_admin] == 96.0)
        is_valid[is_admin] = (vals[is_admin] < 90.0) & (vals[is_admin] >= 10.0)
        
        if max_pts == 1:
            # Codes 10-19 represent full credit (1 pt) across all diagnostic strategies
            score[is_admin] = np.where(
                (vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 1.0, 0.0
            )
        elif max_pts == 2:
            # Codes 20-29 = 2 pts (full credit = 1.0); 10-19 = 1 pt (partial credit = 0.5)
            score[is_admin] = np.where(
                (vals[is_admin] >= 20.0) & (vals[is_admin] <= 29.0), 1.0,
                np.where((vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 0.5, 0.0)
            )
        else:
            score[is_admin] = np.where(
                (vals[is_admin] >= 10.0) & (vals[is_admin] <= 19.0), 1.0, 0.0
            )

    return score, is_admin, is_omit, is_nr, is_valid


def build_item_contrasts() -> pd.DataFrame:
    """
    Calculate survey-weighted item percent correct, omission rates, and mode differences
    across all 99 common anchor items under verified two-digit diagnostic scoring.
    """
    # 1. Load item metadata
    br_item_path = ITEM_DIR / "T19Br_G4_Item Information.xlsx"
    items_df = pd.read_excel(br_item_path, sheet_name="MAT")
    items_df["core_id"] = items_df["Item ID"].str[2:]

    # 2. Load achievement files with user_missing=True to preserve 96/99/6/9
    df_br_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausab7.sav", user_missing=True)
    df_e_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausam7.sav", user_missing=True)

    w_br_all = df_br_ach["TOTWGT"].values
    w_e_all = df_e_ach["TOTWGT"].values

    results = []

    for _, row in items_df.iterrows():
        iid = row["Item ID"]
        cid = row["core_id"]
        itype = row["Item Type"]
        max_pts = int(row["Maximum Points"])
        key = row["Key"]

        col_br = "MP" + cid
        col_e = "ME" + cid

        if col_br not in df_br_ach.columns or col_e not in df_e_ach.columns:
            continue

        s_br = df_br_ach[col_br]
        s_e = df_e_ach[col_e]

        sc_br, adm_br, om_br, nr_br, val_br = score_response_series(s_br, itype, max_pts, key)
        sc_e, adm_e, om_e, nr_e, val_e = score_response_series(s_e, itype, max_pts, key)

        n_br = int(np.sum(adm_br))
        n_e = int(np.sum(adm_e))
        if n_br == 0 or n_e == 0:
            continue

        w_br = w_br_all[adm_br]
        w_e = w_e_all[adm_e]

        # 1. Standard Intent-to-Treat Percent Correct (Omitted & Not-Reached in denominator, scored 0)
        pct_paper = float(np.average(sc_br[adm_br], weights=w_br) * 100.0)
        pct_digital = float(np.average(sc_e[adm_e], weights=w_e) * 100.0)
        diff_pp = pct_digital - pct_paper

        # 2. Response Status Rates
        omit_paper = float(np.average(om_br[adm_br], weights=w_br) * 100.0)
        omit_digital = float(np.average(om_e[adm_e], weights=w_e) * 100.0)
        omit_diff = omit_digital - omit_paper

        nr_paper = float(np.average(nr_br[adm_br], weights=w_br) * 100.0)
        nr_digital = float(np.average(nr_e[adm_e], weights=w_e) * 100.0)

        # 3. Sensitivity: Answered-Only Percent Correct (Conditional on attempting)
        answered_br = adm_br & (~om_br) & (~nr_br)
        answered_e = adm_e & (~om_e) & (~nr_e)
        if np.sum(answered_br) > 0 and np.sum(answered_e) > 0:
            pct_paper_ans = float(np.average(sc_br[answered_br], weights=w_br_all[answered_br]) * 100.0)
            pct_digital_ans = float(np.average(sc_e[answered_e], weights=w_e_all[answered_e]) * 100.0)
            diff_pp_ans = pct_digital_ans - pct_paper_ans
        else:
            pct_paper_ans = pct_paper
            pct_digital_ans = pct_digital
            diff_pp_ans = diff_pp

        # 4. Input Modality Taxonomy
        if itype == "MC":
            modality = "Multiple Choice"
        elif iid in DRAWING_ITEMS:
            modality = "CR: Drawing / Graphing"
        elif iid in TEXT_ITEMS:
            modality = "CR: Text / Explanation"
        elif iid in TABLE_ITEMS:
            modality = "CR: Interactive / Table"
        else:
            modality = "CR: Number-pad / Numeric"

        results.append({
            "item_id": iid,
            "core_id": cid,
            "label": row["Label"],
            "item_type": itype,
            "modality": modality,
            "maximum_points": max_pts,
            "content_domain": row["Content Domain"],
            "topic_area": row["Topic Area"],
            "cognitive_domain": row["Cognitive Domain"],
            "n_paper_students": n_br,
            "n_digital_students": n_e,
            "pct_paper": round(pct_paper, 2),
            "pct_digital": round(pct_digital, 2),
            "diff_pp": round(diff_pp, 2),
            "pct_paper_answered": round(pct_paper_ans, 2),
            "pct_digital_answered": round(pct_digital_ans, 2),
            "diff_pp_answered": round(diff_pp_ans, 2),
            "omit_paper_pct": round(omit_paper, 2),
            "omit_digital_pct": round(omit_digital, 2),
            "omit_diff_pp": round(omit_diff, 2),
            "nr_paper_pct": round(nr_paper, 2),
            "nr_digital_pct": round(nr_digital, 2)
        })

    return pd.DataFrame(results)


def compute_student_format_scores(df_ach: pd.DataFrame, items_df: pd.DataFrame, mode_prefix: str) -> pd.DataFrame:
    """Compute individual student-level performance on MC and CR items, and within-student format gap."""
    n_students = len(df_ach)
    mc_pts_earned = np.zeros(n_students, dtype=float)
    mc_pts_possible = np.zeros(n_students, dtype=float)
    cr_pts_earned = np.zeros(n_students, dtype=float)
    cr_pts_possible = np.zeros(n_students, dtype=float)
    
    mc_omitted = np.zeros(n_students, dtype=float)
    cr_omitted = np.zeros(n_students, dtype=float)

    for _, row in items_df.iterrows():
        cid = row["core_id"]
        itype = row["Item Type"]
        max_pts = int(row["Maximum Points"])
        key = row["Key"]
        col = mode_prefix + cid
        if col not in df_ach.columns:
            continue
        
        s = df_ach[col]
        sc, adm, om, nr, val = score_response_series(s, itype, max_pts, key)

        if itype == "MC":
            mc_pts_earned[adm] += sc[adm]
            mc_pts_possible[adm] += 1.0
            mc_omitted[adm] += om[adm].astype(float)
        else:
            cr_pts_earned[adm] += sc[adm]
            cr_pts_possible[adm] += 1.0
            cr_omitted[adm] += om[adm].astype(float)

    with np.errstate(divide="ignore", invalid="ignore"):
        mc_pct = np.where(mc_pts_possible > 0, (mc_pts_earned / mc_pts_possible) * 100.0, np.nan)
        cr_pct = np.where(cr_pts_possible > 0, (cr_pts_earned / cr_pts_possible) * 100.0, np.nan)
        format_gap = cr_pct - mc_pct
        mc_omit_rate = np.where(mc_pts_possible > 0, (mc_omitted / mc_pts_possible) * 100.0, np.nan)
        cr_omit_rate = np.where(cr_pts_possible > 0, (cr_omitted / cr_pts_possible) * 100.0, np.nan)

    return pd.DataFrame({
        "IDSTUD": df_ach["IDSTUD"],
        "mc_pct": mc_pct,
        "cr_pct": cr_pct,
        "format_gap": format_gap,
        "mc_items_taken": mc_pts_possible,
        "cr_items_taken": cr_pts_possible,
        "mc_omit_rate": mc_omit_rate,
        "cr_omit_rate": cr_omit_rate
    })


def build_student_level_dataset() -> pd.DataFrame:
    """
    Merge student plausible values, survey weights, background variables,
    school poverty, and student-level format performance scores.
    """
    br_item_path = ITEM_DIR / "T19Br_G4_Item Information.xlsx"
    items_df = pd.read_excel(br_item_path, sheet_name="MAT")
    items_df["core_id"] = items_df["Item ID"].str[2:]

    # 1. Bridge
    df_br_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausab7.sav", user_missing=True)
    df_br_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusab7.sav", user_missing=True)
    sc_br = compute_student_format_scores(df_br_ach, items_df, "MP")

    cols_ach = ["IDSTUD", "IDSCHOOL", "IDCLASS", "TOTWGT", "JKZONE", "JKREP",
                "ASMMAT01", "ASMMAT02", "ASMMAT03", "ASMMAT04", "ASMMAT05"]
    cols_stu = ["IDSTUD", "ASBG04", "ASBG05A", "ASBG05D", "ASDG05S"]

    df_br = pd.merge(df_br_ach[cols_ach], df_br_stu[cols_stu], on="IDSTUD", how="left")
    df_br = pd.merge(df_br, sc_br, on="IDSTUD", how="left")
    df_br["study_mode"] = "Bridge_Paper"
    df_br["is_digital"] = 0

    # 2. eTIMSS
    df_e_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausam7.sav", user_missing=True)
    df_e_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusam7.sav", user_missing=True)
    sc_e = compute_student_format_scores(df_e_ach, items_df, "ME")

    df_e = pd.merge(df_e_ach[cols_ach], df_e_stu[cols_stu], on="IDSTUD", how="left")
    df_e = pd.merge(df_e, sc_e, on="IDSTUD", how="left")
    df_e["study_mode"] = "eTIMSS_Digital"
    df_e["is_digital"] = 1

    # Combine students
    df_all_stu = pd.concat([df_br, df_e], ignore_index=True)

    # 3. Merge School Poverty and Sector from NCES
    df_sch = parse_nces_school_data()
    df_merged = pd.merge(
        df_all_stu,
        df_sch[["IDSCHOOL", "study_mode", "PCTFRPL", "PUBPRIV"]],
        on=["IDSCHOOL", "study_mode"],
        how="left"
    )

    # Socioeconomic classification based on home books (ASBG04)
    # 1: 0-10 books, 2: 11-25 books -> Low SES (0-25 books)
    # 3: 26-100, 4: 101-200, 5: >200 -> High SES (26+ books)
    df_merged["is_low_ses"] = np.where(df_merged["ASBG04"].isin([1.0, 2.0]), 1.0,
                              np.where(df_merged["ASBG04"].isin([3.0, 4.0, 5.0]), 0.0, np.nan))

    return df_merged


def build_stacked_student_item_dataset() -> pd.DataFrame:
    """
    Construct stacked student-by-item response panel across all 99 common items (N = 164,653).
    Contains item metadata, student weights, cluster IDs, Jackknife zones, and scored performance.
    Used for item fixed-effects regressions controlling for booklet matrix-sampling composition.
    """
    br_item_path = ITEM_DIR / "T19Br_G4_Item Information.xlsx"
    items_df = pd.read_excel(br_item_path, sheet_name="MAT")
    items_df["core_id"] = items_df["Item ID"].str[2:]

    df_br_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausab7.sav", user_missing=True)
    df_e_ach, _ = pyreadstat.read_sav(RAW_DIR / "asausam7.sav", user_missing=True)

    df_br_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusab7.sav", user_missing=True)
    df_e_stu, _ = pyreadstat.read_sav(RAW_DIR / "asgusam7.sav", user_missing=True)

    cols_stu = ["IDSTUD", "ASBG04", "ASBG05A"]
    df_br_ach = df_br_ach.merge(df_br_stu[cols_stu], on="IDSTUD", how="left")
    df_e_ach = df_e_ach.merge(df_e_stu[cols_stu], on="IDSTUD", how="left")

    df_sch = parse_nces_school_data()

    stacked_rows = []
    for _, row in items_df.iterrows():
        iid = row["Item ID"]
        cid = row["core_id"]
        itype = row["Item Type"]
        max_pts = int(row["Maximum Points"])
        key = row["Key"]
        is_cr = 1 if itype == "CR" else 0

        if itype == "MC":
            modality = "Multiple Choice"
        elif iid in DRAWING_ITEMS:
            modality = "CR: Drawing / Graphing"
        elif iid in TEXT_ITEMS:
            modality = "CR: Text / Explanation"
        elif iid in TABLE_ITEMS:
            modality = "CR: Interactive / Table"
        else:
            modality = "CR: Number-pad / Numeric"

        col_br = "MP" + cid
        col_e = "ME" + cid

        # Bridge
        if col_br in df_br_ach.columns:
            s_br = df_br_ach[col_br]
            sc_br, adm_br, om_br, nr_br, _ = score_response_series(s_br, itype, max_pts, key)
            df_sub = df_br_ach[adm_br][["IDSTUD", "IDSCHOOL", "IDCLASS", "TOTWGT", "JKZONE", "JKREP", "ASBG04", "ASBG05A"]].copy()
            df_sub["item_id"] = iid
            df_sub["core_id"] = cid
            df_sub["item_type"] = itype
            df_sub["is_cr"] = is_cr
            df_sub["modality"] = modality
            df_sub["cognitive_domain"] = row["Cognitive Domain"]
            df_sub["content_domain"] = row["Content Domain"]
            df_sub["max_points"] = max_pts
            df_sub["score_pct"] = sc_br[adm_br] * 100.0
            df_sub["score_pts"] = sc_br[adm_br] * max_pts
            df_sub["is_omit"] = om_br[adm_br].astype(int)
            df_sub["is_not_reached"] = nr_br[adm_br].astype(int)
            df_sub["study_mode"] = "Bridge_Paper"
            df_sub["is_digital"] = 0
            stacked_rows.append(df_sub)

        # eTIMSS
        if col_e in df_e_ach.columns:
            s_e = df_e_ach[col_e]
            sc_e, adm_e, om_e, nr_e, _ = score_response_series(s_e, itype, max_pts, key)
            df_sub = df_e_ach[adm_e][["IDSTUD", "IDSCHOOL", "IDCLASS", "TOTWGT", "JKZONE", "JKREP", "ASBG04", "ASBG05A"]].copy()
            df_sub["item_id"] = iid
            df_sub["core_id"] = cid
            df_sub["item_type"] = itype
            df_sub["is_cr"] = is_cr
            df_sub["modality"] = modality
            df_sub["cognitive_domain"] = row["Cognitive Domain"]
            df_sub["content_domain"] = row["Content Domain"]
            df_sub["max_points"] = max_pts
            df_sub["score_pct"] = sc_e[adm_e] * 100.0
            df_sub["score_pts"] = sc_e[adm_e] * max_pts
            df_sub["is_omit"] = om_e[adm_e].astype(int)
            df_sub["is_not_reached"] = nr_e[adm_e].astype(int)
            df_sub["study_mode"] = "eTIMSS_Digital"
            df_sub["is_digital"] = 1
            stacked_rows.append(df_sub)

    df_stacked = pd.concat(stacked_rows, ignore_index=True)
    df_stacked = df_stacked.merge(
        df_sch[["IDSCHOOL", "study_mode", "PCTFRPL", "PUBPRIV"]],
        on=["IDSCHOOL", "study_mode"],
        how="left"
    )
    df_stacked["is_low_ses"] = np.where(df_stacked["ASBG04"].isin([1.0, 2.0]), 1.0,
                               np.where(df_stacked["ASBG04"].isin([3.0, 4.0, 5.0]), 0.0, np.nan))
    return df_stacked


def main():
    print("=" * 80)
    print("TIMSS 2019 Grade 4 U.S. Data Acquisition & Processing (Audited Pipeline)")
    print("=" * 80)

    # Step 1: Extract files
    extract_files()

    # Step 2: Build Item Contrasts
    print("[PROCESS] Building audited item-level mode contrasts for 99 anchor items...")
    item_df = build_item_contrasts()
    item_csv = PROCESSED_DIR / "timss_2019_g4_item_contrasts.csv"
    item_parquet = PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet"
    item_df.to_csv(item_csv, index=False)
    item_df.to_parquet(item_parquet, index=False)
    print(f"[OK] Wrote {len(item_df)} item records to {item_csv.name} and {item_parquet.name}")

    # Summary by format
    print("\n--- Summary by Item Type (Audited Two-Digit Diagnostic Scoring) ---")
    print(item_df.groupby("item_type")[["diff_pp", "diff_pp_answered", "omit_paper_pct", "omit_digital_pct"]].mean())

    print("\n--- Summary by Input Modality ---")
    print(item_df.groupby("modality")["diff_pp"].agg(["count", "mean", "std"]))

    # Step 3: Build Student-Level Dataset
    print("\n[PROCESS] Building merged student-level dataset with Plausible Values & format scores...")
    stu_df = build_student_level_dataset()
    stu_csv = PROCESSED_DIR / "timss_2019_g4_student_pvs.csv"
    stu_parquet = PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet"
    stu_df.to_csv(stu_csv, index=False)
    stu_df.to_parquet(stu_parquet, index=False)
    print(f"[OK] Wrote {len(stu_df)} student records to {stu_csv.name} and {stu_parquet.name}")

    print("\n--- Student Counts by Mode ---")
    print(stu_df["study_mode"].value_counts())

    # Step 4: Build Stacked Student-Item Panel Dataset
    print("\n[PROCESS] Building stacked student-by-item panel dataset (164,653 observations)...")
    stk_df = build_stacked_student_item_dataset()
    stk_csv = PROCESSED_DIR / "timss_2019_g4_student_item_stacked.csv"
    stk_parquet = PROCESSED_DIR / "timss_2019_g4_student_item_stacked.parquet"
    stk_df.to_csv(stk_csv, index=False)
    stk_df.to_parquet(stk_parquet, index=False)
    print(f"[OK] Wrote {len(stk_df)} stacked records to {stk_csv.name} and {stk_parquet.name}")

    print("\n[SUCCESS] TIMSS 2019 Grade 4 microdata successfully acquired and processed.")


if __name__ == "__main__":
    main()
