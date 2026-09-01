#!/usr/bin/env python3
"""
LODES (LEHD Origin-Destination Employment Statistics) Data ETL Script

Downloads and loads LODES employment data for Missouri and Kansas into a GeoPackage.
Includes WAC (workplace), RAC (residence), and OD (flows) data with all segments.

Data Source: https://lehd.ces.census.gov/data/lodes/LODES8/
"""

import os
import sys
import gzip
import logging
from pathlib import Path
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    import geopandas as gpd
    import pandas as pd
except ImportError as e:
    print(f"Error: Missing required packages. Install with: pip install requests geopandas pandas")
    sys.exit(1)

# LODES configuration
LODES_BASE_URL = "https://lehd.ces.census.gov/data/lodes/LODES8"
LODES_YEARS = ["2021", "2020"]  # Try most recent first
LODES_FILE_TYPE = "od"  # Will be expanded to include wac, rac, od

# States to download
STATES = {
    'mo': 'Missouri',
    'ks': 'Kansas'
}

# Job type and segment configurations
JT_TYPES = {
    'JT00': 'All Jobs',
    'JT01': 'Primary Jobs',
}

SEGMENTS = {
    # Total jobs
    'S000': 'Total Jobs',
    # Age groups
    'SA01': 'Age 29 or younger',
    'SA02': 'Age 30 to 54',
    'SA03': 'Age 55 or older',
    # Earnings groups
    'SE01': 'Earnings $1,250/month or less',
    'SE02': 'Earnings $1,251-$3,333/month',
    'SE03': 'Earnings $3,334/month or more',
    # Industry groups
    'SI01': 'Goods Producing',
    'SI02': 'Trade/Transport/Utilities',
    'SI03': 'All Other',
}

# WAC segment columns (workplace area characteristics)
WAC_COLUMNS = {
    'w_geocode': str,  # 15-digit GEOID
    'createdate': str,  # Creation date
    # Total jobs
    'C000': int,  # Total jobs
    # Age groups
    'CA01': int,  # Age 29 or younger
    'CA02': int,  # Age 30 to 54
    'CA03': int,  # Age 55 or older
    # Earnings
    'CE01': int,  # Earnings $1,250/month or less
    'CE02': int,  # Earnings $1,251-$3,333/month
    'CE03': int,  # Earnings $3,334/month or more
    # Industry sectors
    'CNS01': int,  # Agriculture, forestry, fishing and hunting, and mining
    'CNS02': int,  # Utilities
    'CNS03': int,  # Construction
    'CNS04': int,  # Manufacturing
    'CNS05': int,  # Wholesale trade
    'CNS06': int,  # Retail trade
    'CNS07': int,  # Transportation and warehousing
    'CNS08': int,  # Information
    'CNS09': int,  # Finance and insurance
    'CNS10': int,  # Real estate, rental and leasing
    'CNS11': int,  # Professional, scientific, and technical services
    'CNS12': int,  # Management of companies and enterprises
    'CNS13': int,  # Administrative and support and waste management and remediation services
    'CNS14': int,  # Educational services
    'CNS15': int,  # Health care and social assistance
    'CNS16': int,  # Arts, entertainment, and recreation
    'CNS17': int,  # Accommodation and food services
    'CNS18': int,  # Other services (except public administration)
    'CNS19': int,  # Public administration
    'CNS20': int,  # Unclassified
    # Race
    'CR01': int,  # White alone
    'CR02': int,  # Black or African American alone
    'CR03': int,  # American Indian or Alaska Native alone
    'CR04': int,  # Asian alone
    'CR05': int,  # Native Hawaiian or Other Pacific Islander alone
    'CR07': int,  # Two or More Race groups
    # Ethnicity
    'CT01': int,  # Not Hispanic or Latino
    'CT02': int,  # Hispanic or Latino
    # Education
    'CD01': int,  # Less than high school
    'CD02': int,  # High school or equivalent
    'CD03': int,  # Some college or Associate degree
    'CD04': int,  # Bachelor's degree or advanced degree
    # Sex
    'CS01': int,  # Male
    'CS02': int,  # Female
    # Firm age
    'CFA01': int,  # Firm age 0-2 years
    'CFA02': int,  # Firm age 3-5 years
    'CFA03': int,  # Firm age 6-10 years
    'CFA04': int,  # Firm age 11+ years
    'CFA05': int,  # Firm age unknown
    # Firm size
    'CFS01': int,  # 0-19 employees
    'CFS02': int,  # 20-49 employees
    'CFS03': int,  # 50-249 employees
    'CFS04': int,  # 250-499 employees
    'CFS05': int,  # 500+ employees
}

# RAC columns (same as WAC but for residence)
RAC_COLUMNS = WAC_COLUMNS.copy()
RAC_COLUMNS['h_geocode'] = RAC_COLUMNS.pop('w_geocode')  # Use home geocode

# OD columns (origin-destination flows)
OD_COLUMNS = {
    'w_geocode': str,  # Workplace block GEOID
    'h_geocode': str,  # Residence block GEOID
    'createdate': str,  # Creation date
    'S000': int,  # Total jobs
    'SA01': int,  # Age 29 or younger
    'SA02': int,  # Age 30 to 54
    'SA03': int,  # Age 55 or older
    'SE01': int,  # Earnings $1,250/month or less
    'SE02': int,  # Earnings $1,251-$3,333/month
    'SE03': int,  # Earnings $3,334/month or more
    'SI01': int,  # Goods Producing
    'SI02': int,  # Trade/Transport/Utilities
    'SI03': int,  # All Other
}

def setup_logging():
    """Setup logging"""
    logger = logging.getLogger('load_lodes_data')
    logger.setLevel(logging.INFO)
    
    # File handler
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / 'lodes_etl.log')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def download_lodes_file(state, year, file_type, job_type, segment):
    """Download a LODES file from Census FTP"""
    logger = logging.getLogger('load_lodes_data')
    
    filename = f"{state}_{file_type}_{segment}_{job_type}_{year}.csv.gz"
    url = f"{LODES_BASE_URL}/{state}/{file_type}/{filename}"
    
    logger.info(f"Downloading {filename}...")
    
    try:
        response = requests.get(url, timeout=300)
        
        if response.status_code == 404:
            logger.warning(f"File not found: {url}")
            return None
        
        response.raise_for_status()
        
        logger.info(f"Downloaded {len(response.content)} bytes")
        
        # Decompress
        decompressed = gzip.decompress(response.content)
        
        # Read CSV into DataFrame
        df = pd.read_csv(BytesIO(decompressed), dtype=str)
        
        logger.info(f"Parsed {len(df)} records")
        
        return df
        
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return None

def parse_wac_data(state, year, job_type, segment):
    """Parse WAC (workplace area characteristics) data"""
    logger = logging.getLogger('load_lodes_data')
    
    df = download_lodes_file(state, year, 'wac', job_type, segment)
    
    if df is None or df.empty:
        return None
    
    # Convert columns to appropriate types
    for col, dtype in WAC_COLUMNS.items():
        if col in df.columns:
            if dtype == int:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            else:
                df[col] = df[col].astype(dtype)
    
    df['state'] = state
    df['year'] = year
    df['job_type'] = job_type
    df['segment'] = segment
    
    return df

def parse_rac_data(state, year, job_type, segment):
    """Parse RAC (residence area characteristics) data"""
    logger = logging.getLogger('load_lodes_data')
    
    df = download_lodes_file(state, year, 'rac', job_type, segment)
    
    if df is None or df.empty:
        return None
    
    # Convert columns
    for col, dtype in RAC_COLUMNS.items():
        if col in df.columns:
            if dtype == int:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            else:
                df[col] = df[col].astype(dtype)
    
    df['state'] = state
    df['year'] = year
    df['job_type'] = job_type
    df['segment'] = segment
    
    return df

def parse_od_data(state, year, job_type, segment):
    """Parse OD (origin-destination) data"""
    logger = logging.getLogger('load_lodes_data')
    
    df = download_lodes_file(state, year, 'od', job_type, segment)
    
    if df is None or df.empty:
        return None
    
    # Convert columns
    for col, dtype in OD_COLUMNS.items():
        if col in df.columns:
            if dtype == int:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            else:
                df[col] = df[col].astype(dtype)
    
    df['state'] = state
    df['year'] = year
    df['job_type'] = job_type
    df['segment'] = segment
    
    return df

def load_to_geopackage(wac_data, rac_data, od_data, year, logger, state):
    """Load LODES data into GeoPackage"""
    
    import sqlite3
    
    output_file = project_root / "data" / "processed" / "lodes_data.gpkg"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Loading data to {output_file}...")
    
    # Create SQLite connection
    conn = sqlite3.connect(output_file)
    
    try:
        # Load WAC data
        if wac_data is not None and not wac_data.empty:
            logger.info(f"Writing {len(wac_data)} WAC records from {state.upper()}...")
            # Use append for subsequent states, replace for first
            import os
            table_exists = any('lodes_wac' in t for t in [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")])
            wac_data.to_sql('lodes_wac', conn, if_exists='append' if table_exists else 'replace', index=False)
            logger.info("[OK] WAC data loaded")
        
        # Load RAC data
        if rac_data is not None and not rac_data.empty:
            logger.info(f"Writing {len(rac_data)} RAC records from {state.upper()}...")
            import os
            table_exists = any('lodes_rac' in t for t in [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")])
            rac_data.to_sql('lodes_rac', conn, if_exists='append' if table_exists else 'replace', index=False)
            logger.info("[OK] RAC data loaded")
        
        # Load OD data (skip if empty - may not be available for all years)
        if od_data is not None and not od_data.empty:
            logger.info(f"Writing {len(od_data)} OD records from {state.upper()}...")
            import os
            table_exists = any('lodes_od' in t for t in [x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")])
            od_data.to_sql('lodes_od', conn, if_exists='append' if table_exists else 'replace', index=False)
            logger.info("[OK] OD data loaded")
        else:
            logger.info("No OD data to load (may not be available for this year)")
    
    finally:
        conn.close()

def main():
    """Main ETL function"""
    logger = setup_logging()
    
    logger.info("Starting LODES Data ETL...")
    logger.info(f"Target states: {', '.join(STATES.values())}")
    
    # Try to find most recent available year
    year = None
    for test_year in LODES_YEARS:
        test_file = download_lodes_file('mo', test_year, 'wac', 'JT00', 'S000')
        if test_file is not None and not test_file.empty:
            year = test_year
            logger.info(f"Using year {year}")
            break
    
    if year is None:
        logger.error("Could not find available LODES data")
        return
    
    # Process each state
    for state, state_name in STATES.items():
        logger.info(f"\nProcessing {state_name} (state={state})...")
        
        # Collect WAC data (workplace)
        logger.info("Processing WAC data...")
        wac_frames = []
        for segment in SEGMENTS.keys():
            df = parse_wac_data(state, year, 'JT00', segment)
            if df is not None and not df.empty:
                wac_frames.append(df)
        
        wac_data = pd.concat(wac_frames, ignore_index=True) if wac_frames else None
        logger.info(f"Collected {len(wac_data) if wac_data is not None else 0} WAC records")
        
        # Collect RAC data (residence)
        logger.info("Processing RAC data...")
        rac_frames = []
        for segment in SEGMENTS.keys():
            df = parse_rac_data(state, year, 'JT00', segment)
            if df is not None and not df.empty:
                rac_frames.append(df)
        
        rac_data = pd.concat(rac_frames, ignore_index=True) if rac_frames else None
        logger.info(f"Collected {len(rac_data) if rac_data is not None else 0} RAC records")
        
        # Collect OD data (flows)
        logger.info("Processing OD data...")
        od_frames = []
        for segment in SEGMENTS.keys():
            df = parse_od_data(state, year, 'JT00', segment)
            if df is not None and not df.empty:
                od_frames.append(df)
        
        if od_frames:
            od_data = pd.concat(od_frames, ignore_index=True)
        else:
            od_data = None
        logger.info(f"Collected {len(od_data) if od_data is not None else 0} OD records")
        
        # Load to GeoPackage
        load_to_geopackage(wac_data, rac_data, od_data, year, logger, state)
    
    logger.info("\nLODES Data ETL Complete!")

if __name__ == "__main__":
    main()

