#!/usr/bin/env python3
"""
Small Test of ACS Data Loading - Single County

Loads ACS data for just Jackson County to test the full pipeline
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pandas as pd
    import requests
    import geopandas as gpd
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required packages. Install with: pip install pandas requests geopandas python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv(project_root / '.env')

# ACS Configuration
ACS_BASE_URL = 'https://api.census.gov/data/2023/acs/acs5'
ACS_YEAR = '2019-2023'
ACS_RELEASE = '2023-12-12'

# ACS Variables to Fetch
# Primary variables (always fetched)
ACS_VARIABLES = {
    'B01001_001E': 'total_population',
    'B19013_001E': 'median_household_income',
    'B03002_001E': 'total_race',
    'B03002_003E': 'white_alone',
    'B03002_004E': 'black_alone',
    'B03002_012E': 'hispanic_latino'
}

# Secondary variables (may not be available for all block groups)
ACS_OPTIONAL_VARIABLES = {
    'B19013_001M': 'mhi_moe',
    'B17001_001E': 'poverty_universe',
    'B17001_002E': 'poverty_count'
}

def setup_logging():
    """Setup logging"""
    logger = logging.getLogger('load_acs_data_small_test')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def fetch_acs_data(state_fips, county_fips, logger):
    """Fetch ACS data for a specific county"""
    
    # Build variable list - include both required and optional
    vars_list = list(ACS_VARIABLES.keys()) + list(ACS_OPTIONAL_VARIABLES.keys())
    vars_string = 'NAME,' + ','.join(vars_list)
    
    # Build API request
    params = {
        'get': vars_string,
        'for': 'block group:*',
        'in': f'state:{state_fips} county:{county_fips} tract:*'
    }
    
    try:
        logger.info(f"Fetching ACS data for state={state_fips}, county={county_fips}...")
        
        response = requests.get(ACS_BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Convert to DataFrame
        if len(data) < 2:
            logger.warning("No data returned")
            return None
        
        # First row is headers
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        # Build GEOID
        df['GEOID'] = df['state'] + df['county'] + df['tract'] + df['block group']
        
        # Rename variables
        rename_map = {k: ACS_VARIABLES[k] for k in ACS_VARIABLES.keys() if k in df.columns}
        df = df.rename(columns=rename_map)
        
        # Convert numeric columns
        for col in list(ACS_VARIABLES.values()) + list(ACS_OPTIONAL_VARIABLES.values()):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate poverty_rate if data available
        if 'poverty_universe' in df.columns and 'poverty_count' in df.columns:
            # Calculate where both values are valid
            df['poverty_rate'] = df.apply(lambda row: 
                row['poverty_count'] / row['poverty_universe'] 
                if pd.notna(row.get('poverty_count')) and pd.notna(row.get('poverty_universe')) and row.get('poverty_universe', 0) > 0 
                else None, axis=1)
        else:
            df['poverty_rate'] = None
        
        # Rename these optional columns too
        rename_map_optional = {k: ACS_OPTIONAL_VARIABLES[k] for k in ACS_OPTIONAL_VARIABLES.keys() if k in df.columns}
        df = df.rename(columns=rename_map_optional)
        
        # Add metadata
        df['acs_year'] = ACS_YEAR
        df['acs_release'] = ACS_RELEASE
        
        logger.info(f"Fetched {len(df)} block groups")
        
        return df
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_to_database(df, logger):
    """Load ACS data into the tiger_boundaries.gpkg file"""
    
    try:
        logger.info(f"Loading {len(df)} records into tiger_boundaries.gpkg...")
        
        # Path to TIGER GeoPackage
        tiger_path = project_root / "data" / "processed" / "tiger_boundaries.gpkg"
        
        if not tiger_path.exists():
            logger.error(f"TIGER boundaries file not found")
            return
        
        # Read existing block groups
        gdf = gpd.read_file(tiger_path, layer='bg')
        
        logger.info(f"Found {len(gdf)} block groups in TIGER file")
        
        # Merge ACS data with TIGER data
        logger.info("Merging ACS data with TIGER boundaries...")
        
        # Create lookup dictionary
        df_lookup = df.set_index('GEOID').to_dict('index')
        
        # Convert all ACS columns to proper numeric types BEFORE merging
        # Primary columns
        numeric_cols = ['total_population', 'median_household_income', 'total_race', 
                       'white_alone', 'black_alone', 'hispanic_latino']
        # Optional columns that may not exist for all block groups
        optional_cols = ['mhi_moe', 'poverty_universe', 'poverty_count', 'poverty_rate']
        
        for col in numeric_cols + optional_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Also handle renamed columns
        if 'total_population' in df.columns:
            df['population'] = df['total_population']
        
        # Update matching rows
        updated = 0
        for idx, row in gdf.iterrows():
            geoid = str(row['GEOID'])
            if geoid in df_lookup:
                for col, value in df_lookup[geoid].items():
                    if col in gdf.columns and pd.notna(value):
                        # Just assign - we already converted types above
                        gdf.loc[idx, col] = value
                updated += 1
        
        logger.info(f"Updated {updated} block groups with ACS data")
        
        # Write back to GeoPackage
        logger.info("Saving to GeoPackage...")
        gdf.to_file(tiger_path, layer='bg', driver='GPKG')
        
        logger.info("Successfully saved!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("ACS Data Load Test - Jackson County Only")
    logger.info("=" * 60)
    
    # Fetch data for just Jackson County
    logger.info("\nFetching ACS data for Jackson County, MO...")
    df = fetch_acs_data('29', '095', logger)
    
    if df is None:
        logger.error("Failed to fetch data")
        return
    
    logger.info(f"\nLoaded {len(df)} block groups")
    
    # Load to database
    logger.info("\nLoading to database...")
    load_to_database(df, logger)
    
    logger.info("\n" + "=" * 60)
    logger.info("Test complete!")
    logger.info("Check the map to see poverty rate choropleth for Jackson County")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

