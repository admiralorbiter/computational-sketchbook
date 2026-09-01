"""Census data ingestion: ACS and TIGER/Line shapefiles."""

import logging
from pathlib import Path
import time
import geopandas as gpd
import pandas as pd
import requests
from typing import List, Dict, Optional

from data_pipeline.config import Config

logger = logging.getLogger(__name__)


def ingest_acs_data(geography: str = "tract", year: int = 2023, acs_type: str = "5year"):
    """Ingest American Community Survey data via Census Data API.
    
    Args:
        geography: Geography level (tract, block_group, county)
        year: Year of ACS data
        acs_type: 1year or 5year estimates
    
    Returns:
        DataFrame with ACS data, indexed by GEOID
    """
    logger.info(f"Ingesting ACS {acs_type} data for {geography} level, year {year}")
    
    # Validate API key
    if not Config.CENSUS_API_KEY:
        raise ValueError("CENSUS_API_KEY not found in configuration. Please set it in .env file.")
    
    # Map acs_type to API endpoint
    acs_endpoint = "acs1" if acs_type == "1year" else "acs5"
    
    # Define key ACS variables to fetch based on documentation requirements
    # Format: variable_code: (estimate_code, moe_code, description)
    acs_variables = {
        # Income & Poverty
        "poverty_total": ("B17001_001E", "B17001_001M", "Total population for whom poverty status determined"),
        "poverty_below": ("B17001_002E", "B17001_002M", "Income below poverty level"),
        "median_household_income": ("B19013_001E", "B19013_001M", "Median household income"),
        
        # Housing
        "total_occupied": ("B25003_001E", "B25003_001M", "Total occupied housing units"),
        "owner_occupied": ("B25003_002E", "B25003_002M", "Owner-occupied housing units"),
        "renter_occupied": ("B25003_003E", "B25003_003M", "Renter-occupied housing units"),
        "median_gross_rent": ("B25064_001E", "B25064_001M", "Median gross rent"),
        "vacancy_rate": ("B25002_003E", "B25002_003M", "Vacant housing units"),
        "total_housing_units": ("B25002_001E", "B25002_001M", "Total housing units"),
        
        # Vehicle Access
        "households_no_vehicle": ("B25044_003E", "B25044_003M", "Owner-occupied: No vehicle available"),
        "households_no_vehicle_renter": ("B25044_010E", "B25044_010M", "Renter-occupied: No vehicle available"),
        "total_households_vehicle": ("B25044_001E", "B25044_001M", "Total occupied housing units (vehicle data)"),
        
        # Insurance Coverage (simplified - using overall uninsured rate)
        "total_civilian_pop": ("B27010_001E", "B27010_001M", "Total civilian noninstitutionalized population"),
        "uninsured": ("B27010_017E", "B27010_017M", "No health insurance coverage"),
        
        # Commute
        "workers_16_over": ("B08301_001E", "B08301_001M", "Workers 16 years and over"),
        "commute_car": ("B08301_002E", "B08301_002M", "Car, truck, or van"),
        "commute_public_transit": ("B08301_010E", "B08301_010M", "Public transportation"),
        "median_commute_minutes": ("B08013_001E", "B08013_001M", "Median travel time to work (minutes)"),
        
        # Household Structure
        "total_households": ("B11001_001E", "B11001_001M", "Total households"),
        "family_households": ("B11001_002E", "B11001_002M", "Family households"),
        "avg_household_size": ("B25010_001E", "B25010_001M", "Average household size"),
    }
    
    # Build list of variable codes to request
    variables_to_get = ["NAME", "GEO_ID"]
    for var_name, (est_code, moe_code, _) in acs_variables.items():
        variables_to_get.append(est_code)
        variables_to_get.append(moe_code)
    
    # Build API base URL
    base_url = f"{Config.CENSUS_API_BASE}/{year}/acs/{acs_endpoint}"
    
    # Separate MO and KS counties
    mo_counties = [code[-3:] for code in Config.KC_METRO_COUNTIES if code.startswith("29")]
    ks_counties = [code[-3:] for code in Config.KC_METRO_COUNTIES if code.startswith("20")]
    
    all_dataframes = []
    
    # Fetch data for Missouri counties
    if mo_counties:
        mo_data = _fetch_acs_county_data(
            base_url=base_url,
            state_fips="29",
            counties=mo_counties,
            geography=geography,
            variables=",".join(variables_to_get),
            api_key=Config.CENSUS_API_KEY
        )
        if mo_data is not None and len(mo_data) > 0:
            all_dataframes.append(mo_data)
            logger.info(f"Fetched ACS data for {len(mo_data)} Missouri {geography} records")
    
    # Fetch data for Kansas counties
    if ks_counties:
        ks_data = _fetch_acs_county_data(
            base_url=base_url,
            state_fips="20",
            counties=ks_counties,
            geography=geography,
            variables=",".join(variables_to_get),
            api_key=Config.CENSUS_API_KEY
        )
        if ks_data is not None and len(ks_data) > 0:
            all_dataframes.append(ks_data)
            logger.info(f"Fetched ACS data for {len(ks_data)} Kansas {geography} records")
    
    # Combine all DataFrames
    if not all_dataframes:
        logger.warning("No ACS data fetched. Returning empty DataFrame.")
        return pd.DataFrame()
    
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    logger.info(f"Combined ACS data contains {len(combined_df)} {geography} records")
    
    # Standardize GEOID format
    # GEO_ID from API is like "1400000US29047021003", extract the last 11 digits
    if "GEO_ID" in combined_df.columns:
        combined_df["GEOID"] = combined_df["GEO_ID"].str[-11:].str.strip()
        combined_df = combined_df.drop(columns=["GEO_ID"])
    
    # Derive state, county, tract from GEOID (11 digits: SSCCCEEEEEE)
    if "GEOID" in combined_df.columns:
        combined_df["state_fips"] = combined_df["GEOID"].str[:2]
        combined_df["county_fips"] = combined_df["GEOID"].str[2:5]
        combined_df["tract_fips"] = combined_df["GEOID"].str[5:]
    
    # Rename columns from variable codes to descriptive names
    column_mapping = {"NAME": "tract_name"}
    for var_name, (est_code, moe_code, _) in acs_variables.items():
        column_mapping[est_code] = var_name
        column_mapping[moe_code] = f"{var_name}_moe"
    
    combined_df = combined_df.rename(columns=column_mapping)
    
    # Set GEOID as index
    if "GEOID" in combined_df.columns:
        combined_df = combined_df.set_index("GEOID")
    
    # Convert numeric columns (handle string values like -999999 which indicate suppressed data)
    numeric_cols = [col for col in combined_df.columns if col not in ["tract_name", "state_fips", "county_fips", "tract_fips"]]
    for col in numeric_cols:
        combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce")
        # Replace suppressed values (typically -999999 or similar) with NaN
        combined_df[col] = combined_df[col].replace([-999999, -888888, -666666], pd.NA)
    
    logger.info(f"ACS data ingestion complete: {len(combined_df)} {geography} records with {len(combined_df.columns)} variables")
    
    return combined_df


def _fetch_acs_county_data(
    base_url: str,
    state_fips: str,
    counties: List[str],
    geography: str,
    variables: str,
    api_key: str,
    max_retries: int = 3
) -> Optional[pd.DataFrame]:
    """Fetch ACS data for specific state and counties.
    
    Args:
        base_url: Census API base URL
        state_fips: State FIPS code (2 digits)
        counties: List of county FIPS codes (3 digits each)
        geography: Geography level (tract, block_group, etc.)
        variables: Comma-separated list of variable codes
        api_key: Census API key
        max_retries: Maximum number of retry attempts
    
    Returns:
        DataFrame with ACS data or None if fetch fails
    """
    # Build county filter string
    county_filter = ",".join(counties)
    
    # Build API request URL
    # Format: for=tract:*&in=state:29+county:047,095,165
    url = f"{base_url}"
    params = {
        "get": variables,
        "for": f"{geography}:*",
        "in": f"state:{state_fips}+county:{county_filter}",
        "key": api_key
    }
    
    # Make request with retry logic
    for attempt in range(max_retries):
        try:
            logger.debug(f"Fetching ACS data from {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if not data or len(data) < 2:
                logger.warning(f"Empty or invalid response from Census API")
                return None
            
            # First row is headers, rest is data
            headers = data[0]
            rows = data[1:]
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            return df
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit
                wait_time = (2 ** attempt) * 2  # Exponential backoff
                logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"HTTP error fetching ACS data: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching ACS data: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
        
        except Exception as e:
            logger.error(f"Unexpected error fetching ACS data: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    
    return None


def ingest_tiger_shapefiles(geography: str = "tract", vintage: int = 2020):
    """Ingest TIGER/Line shapefiles for geographic boundaries.
    
    Args:
        geography: Geography type (tract, county, congressional_district, etc.)
        vintage: Year of TIGER/Line data
    
    Returns:
        GeoDataFrame with boundaries filtered to KC metro counties
    """
    logger.info(f"Ingesting TIGER/Line {geography} boundaries, vintage {vintage}")
    
    # Build paths to ZIP files
    tiger_dir = Config.RAW_DATA_DIR / "tiger"
    
    # File naming: tl_YYYY_SS_tract.zip (SS = state FIPS)
    # MO = 29, KS = 20
    mo_zip_path = tiger_dir / f"tl_{vintage}_29_{geography}.zip"
    ks_zip_path = tiger_dir / f"tl_{vintage}_20_{geography}.zip"
    
    # Validate files exist
    if not mo_zip_path.exists():
        raise FileNotFoundError(f"Missouri TIGER shapefile not found: {mo_zip_path}")
    if not ks_zip_path.exists():
        raise FileNotFoundError(f"Kansas TIGER shapefile not found: {ks_zip_path}")
    
    logger.info(f"Loading Missouri {geography} boundaries from {mo_zip_path.name}")
    mo_gdf = gpd.read_file(mo_zip_path)
    logger.info(f"Loaded {len(mo_gdf)} Missouri {geography} records")
    
    logger.info(f"Loading Kansas {geography} boundaries from {ks_zip_path.name}")
    ks_gdf = gpd.read_file(ks_zip_path)
    logger.info(f"Loaded {len(ks_gdf)} Kansas {geography} records")
    
    # Filter to KC metro counties
    # TIGER files include COUNTYFP column (3-digit county FIPS)
    # KC_METRO_COUNTIES are 5-digit codes (state + county)
    # Extract county codes from KC_METRO_COUNTIES (last 3 digits)
    kc_county_codes = [code[-3:] for code in Config.KC_METRO_COUNTIES]
    
    # Filter Missouri (state FIPS 29)
    mo_counties = [code[-3:] for code in Config.KC_METRO_COUNTIES if code.startswith("29")]
    mo_filtered = mo_gdf[mo_gdf["COUNTYFP"].isin(mo_counties)].copy()
    logger.info(f"Filtered Missouri {geography} to {len(mo_filtered)} records in {len(mo_counties)} counties")
    
    # Filter Kansas (state FIPS 20)
    ks_counties = [code[-3:] for code in Config.KC_METRO_COUNTIES if code.startswith("20")]
    ks_filtered = ks_gdf[ks_gdf["COUNTYFP"].isin(ks_counties)].copy()
    logger.info(f"Filtered Kansas {geography} to {len(ks_filtered)} records in {len(ks_counties)} counties")
    
    # Combine both states
    combined_gdf = pd.concat([mo_filtered, ks_filtered], ignore_index=True)
    logger.info(f"Combined GeoDataFrame contains {len(combined_gdf)} {geography} records")
    
    # Ensure CRS is set (TIGER files typically use EPSG:4269)
    if combined_gdf.crs is None:
        logger.warning("CRS not set in shapefile, assuming EPSG:4269 (NAD83)")
        combined_gdf.set_crs("EPSG:4269", inplace=True)
    else:
        logger.info(f"GeoDataFrame CRS: {combined_gdf.crs}")
    
    # Validate GEOID column exists
    if "GEOID" not in combined_gdf.columns:
        logger.warning("GEOID column not found in shapefile")
        # TIGER files might use different column names, try common alternatives
        if "TRACTCE" in combined_gdf.columns and "STATEFP" in combined_gdf.columns and "COUNTYFP" in combined_gdf.columns:
            combined_gdf["GEOID"] = (
                combined_gdf["STATEFP"].astype(str) + 
                combined_gdf["COUNTYFP"].astype(str) + 
                combined_gdf["TRACTCE"].astype(str)
            )
            logger.info("Constructed GEOID from STATEFP + COUNTYFP + TRACTCE")
    
    # Validate geometry
    if combined_gdf.geometry.isnull().any():
        logger.warning(f"Found {combined_gdf.geometry.isnull().sum()} null geometries, removing")
        combined_gdf = combined_gdf[combined_gdf.geometry.notnull()].copy()
    
    logger.info(f"TIGER/Line ingestion complete: {len(combined_gdf)} {geography} boundaries ready")
    
    return combined_gdf
