"""
Build 2013–14 CCD School Capacity & Metadata Panel for MARC Kansas City Region.
Fetches official NCES CCD school directory data via Urban Institute Education Data Portal API,
filters to the 9-county MARC region, harmonizes variables with the longitudinal capacity panel,
and computes contemporaneous 2013–14 school pupil/teacher ratios (PTR).
"""

import sys
import json
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_MANIFEST = PROJECT_ROOT / "data" / "manifest.csv"

MARC_COUNTIES = {
    "20091": ("Johnson", "KS"),
    "20209": ("Wyandotte", "KS"),
    "20103": ("Leavenworth", "KS"),
    "20121": ("Miami", "KS"),
    "29095": ("Jackson", "MO"),
    "29047": ("Clay", "MO"),
    "29165": ("Platte", "MO"),
    "29037": ("Cass", "MO"),
    "29177": ("Ray", "MO"),
}

LEVEL_MAP = {
    1: "Primary",
    2: "Middle",
    3: "High",
    4: "Other",
}

TYPE_MAP = {
    1: "Regular School",
    2: "Special Education",
    3: "Career and Technical",
    4: "Alternative",
}

LOCALE_MAP = {
    11: "City", 12: "City", 13: "City",
    21: "Suburb", 22: "Suburb", 23: "Suburb",
    31: "Town", 32: "Town", 33: "Town",
    41: "Rural", 42: "Rural", 43: "Rural",
}

def fetch_ccd_2013_marc():
    print("Fetching 2013-14 CCD school directory data for Kansas and Missouri...")
    records = []
    for fips in ["20", "29"]:
        page = 1
        while True:
            url = f"https://educationdata.urban.org/api/v1/schools/ccd/directory/2013/?fips={fips}&page={page}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            try:
                with urllib.request.urlopen(req) as resp:
                    payload = json.loads(resp.read().decode())
            except Exception as e:
                print(f"Error fetching fips {fips} page {page}: {e}")
                break
            
            results = payload.get("results", [])
            if not results:
                break
            for r in results:
                county = str(r.get("county_code", "")).zfill(5)
                if county in MARC_COUNTIES:
                    records.append(r)
            
            if not payload.get("next"):
                break
            page += 1
            
    print(f"Retrieved {len(records)} MARC school records for SY 2013-14.")
    raw_df = pd.DataFrame(records)
    
    # Harmonize fields
    clean_records = []
    for _, r in raw_df.iterrows():
        county_code = str(r.get("county_code", "")).zfill(5)
        county_name, state = MARC_COUNTIES[county_code]
        
        nces_sch = str(r.get("ncessch", "")).strip()
        if len(nces_sch) < 12:
            nces_sch = nces_sch.zfill(12)
            
        nces_lea = str(r.get("leaid", "")).strip()
        if len(nces_lea) < 7:
            nces_lea = nces_lea.zfill(7)
            
        sch_level_code = r.get("school_level")
        sch_level = LEVEL_MAP.get(sch_level_code, "Other")
        
        sch_type_code = r.get("school_type")
        sch_type = TYPE_MAP.get(sch_type_code, "Regular School")
        
        op_status = r.get("school_status")
        is_operating = op_status in [1, 3, 8]  # Standard NCES operating codes
        
        locale_code = r.get("urban_centric_locale")
        locale_group = LOCALE_MAP.get(locale_code, "Unknown")
        
        is_charter = bool(r.get("charter") == 1)
        is_virtual = bool(r.get("virtual") == 1)
        
        raw_enr = r.get("enrollment")
        enrollment = float(raw_enr) if raw_enr is not None and raw_enr >= 0 else np.nan
        
        raw_fte = r.get("teachers_fte")
        fte = float(raw_fte) if raw_fte is not None and raw_fte > 0 else np.nan
        
        ptr = np.nan
        if pd.notna(enrollment) and pd.notna(fte) and fte > 0:
            ptr = round(enrollment / fte, 2)
            
        clean_records.append({
            "school_year": "2013-2014",
            "nces_school_id": nces_sch,
            "nces_lea_id": nces_lea,
            "school_name": r.get("school_name", "").strip(),
            "district_name": r.get("lea_name", "").strip(),
            "state": state,
            "county_name": county_name,
            "county_fips": county_code,
            "school_level": sch_level,
            "school_type": sch_type,
            "operational_status": op_status,
            "is_operating": is_operating,
            "locale_code": locale_code,
            "locale_group": locale_group,
            "is_charter": is_charter,
            "is_virtual": is_virtual,
            "enrollment_total": enrollment,
            "classroom_teacher_fte": fte,
            "school_ptr": ptr
        })
        
    out_df = pd.DataFrame(clean_records)
    out_path = DATA_PROCESSED / "kc_ccd_school_capacity_2013_14.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Saved {len(out_df)} records to {out_path}")
    
    # Summary QA
    print(f"Operational schools: {out_df['is_operating'].sum()}")
    print(f"Schools with valid PTR: {out_df['school_ptr'].notna().sum()}")
    print(f"High schools: {(out_df['school_level'] == 'High').sum()}")
    print(f"High school PTR median: {out_df[out_df['school_level'] == 'High']['school_ptr'].median():.2f}")
    
    return out_path

if __name__ == "__main__":
    fetch_ccd_2013_marc()
