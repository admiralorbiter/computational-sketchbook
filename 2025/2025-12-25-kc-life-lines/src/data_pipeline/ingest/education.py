"""Education data ingestion: MO DESE, KSDE, NCES, College Scorecard."""

import logging
from pathlib import Path
import geopandas as gpd
import pandas as pd

from data_pipeline.config import Config

logger = logging.getLogger(__name__)


def ingest_mo_dese_data():
    """Ingest Missouri DESE district/school indicators."""
    logger.info("Ingesting Missouri DESE data")
    # TODO: Implement MO DESE data download/API calls
    pass


def ingest_ksde_data():
    """Ingest Kansas KSDE Data Central indicators."""
    logger.info("Ingesting Kansas KSDE data")
    # TODO: Implement KSDE data download/API calls
    pass


def ingest_nces_districts(vintage: int = 2023):
    """Ingest NCES EDGE school district boundaries.
    
    Args:
        vintage: Year of district boundaries (school year, e.g., 2023 for 2022-2023)
    
    Returns:
        GeoDataFrame with district boundaries filtered to KC metro area
    """
    logger.info(f"Ingesting NCES EDGE district boundaries, vintage {vintage}")
    
    # Build path to ZIP file
    nces_dir = Config.RAW_DATA_DIR / "nces"
    
    # NCES EDGE files are typically named: schooldistrict_sy{YYYY}_tl.zip
    # Try common naming patterns
    possible_names = [
        f"schooldistrict_sy{vintage}_tl.zip",
        f"EDGE_SCHOOLDISTRICT_TL{vintage}.zip",
        f"School_District_Boundaries_{vintage}.zip"
    ]
    
    zip_path = None
    for name in possible_names:
        candidate = nces_dir / name
        if candidate.exists():
            zip_path = candidate
            logger.info(f"Found NCES file: {name}")
            break
    
    if zip_path is None:
        # Try to find any ZIP file in the directory
        zip_files = list(nces_dir.glob("*.zip"))
        if zip_files:
            zip_path = zip_files[0]
            logger.info(f"Using found ZIP file: {zip_path.name}")
        else:
            raise FileNotFoundError(
                f"NCES EDGE district boundary ZIP file not found in {nces_dir}. "
                f"Expected one of: {', '.join(possible_names)}. "
                f"Please download from https://nces.ed.gov/programs/edge/Geographic/DistrictBoundaries"
            )
    
    # Load the shapefile from ZIP
    logger.info(f"Loading NCES district boundaries from {zip_path.name}")
    try:
        gdf = gpd.read_file(zip_path)
        logger.info(f"Loaded {len(gdf)} district records from NCES file")
    except Exception as e:
        logger.error(f"Failed to load NCES shapefile: {e}")
        raise
    
    # Filter to KC metro states (Missouri = 29, Kansas = 20)
    # NCES files typically use STATEFP or STATE column
    state_column = None
    for col in ["STATEFP", "STATE", "STATEFIPS", "STATE_FIPS"]:
        if col in gdf.columns:
            state_column = col
            break
    
    if state_column is None:
        logger.warning("State FIPS column not found. Available columns: " + ", ".join(gdf.columns))
        logger.warning("Attempting to load all districts (no state filtering)")
    else:
        # Filter to Missouri (29) and Kansas (20)
        kc_states = ["29", "20"]
        initial_count = len(gdf)
        gdf = gdf[gdf[state_column].astype(str).isin(kc_states)].copy()
        logger.info(f"Filtered to KC metro states: {len(gdf)} districts (from {initial_count} total)")
        
        # Log breakdown by state
        if state_column in gdf.columns:
            state_counts = gdf[state_column].value_counts()
            for state_code, count in state_counts.items():
                state_name = "Missouri" if state_code == "29" else "Kansas" if state_code == "20" else f"State {state_code}"
                logger.info(f"  {state_name}: {count} districts")
    
    # Extract and standardize key fields
    # LEAID is the 7-digit NCES district identifier
    # NCES EDGE files may use: LEAID, ELSDLEA, SCSDLEA, UNSDLEA, SDADMLEA, or GEOID
    # Priority: LEAID > UNSDLEA > ELSDLEA > SCSDLEA > SDADMLEA > GEOID
    nces_id_column = None
    for col in ["LEAID", "NCESID", "NCES_ID", "DISTRICTID"]:
        if col in gdf.columns:
            nces_id_column = col
            break
    
    # If not found, try the LEA columns (Elementary, Secondary, Unified, Administrative)
    # These are the actual NCES district IDs
    if nces_id_column is None:
        # Prefer Unified School District LEA (most common)
        for col in ["UNSDLEA", "ELSDLEA", "SCSDLEA", "SDADMLEA"]:
            if col in gdf.columns and gdf[col].notna().any():
                nces_id_column = col
                break
    
    # Fallback to GEOID if no LEA columns found
    if nces_id_column is None and "GEOID" in gdf.columns:
        nces_id_column = "GEOID"
    
    if nces_id_column:
        # Standardize to NCESID
        if nces_id_column != "NCESID":
            # For LEA columns, use the first non-null value
            if nces_id_column in ["UNSDLEA", "ELSDLEA", "SCSDLEA", "SDADMLEA"]:
                # Use the specified column, but fill nulls by checking other LEA columns
                nces_id = gdf[nces_id_column].copy()
                # Fill nulls with other LEA columns in priority order
                if nces_id.isna().any():
                    for fallback_col in ["UNSDLEA", "ELSDLEA", "SCSDLEA", "SDADMLEA"]:
                        if fallback_col != nces_id_column and fallback_col in gdf.columns:
                            nces_id = nces_id.fillna(gdf[fallback_col])
                gdf["NCESID"] = nces_id.astype(str).str.replace(".0", "", regex=False)
            else:
                gdf["NCESID"] = gdf[nces_id_column].astype(str)
            logger.info(f"Mapped {nces_id_column} to NCESID")
    else:
        logger.warning("NCES ID column (LEAID/NCESID/GEOID/LEA columns) not found. Available columns: " + ", ".join(gdf.columns))
    
    # Extract district name
    name_column = None
    for col in ["NAME", "DISTRICT_NAME", "NAME_LONG", "NAMELSAD"]:
        if col in gdf.columns:
            name_column = col
            break
    
    if name_column and name_column != "NAME":
        gdf["NAME"] = gdf[name_column]
        logger.info(f"Mapped {name_column} to NAME")
    
    # Extract district type
    # NCES EDGE files may use: SDTYP, TYPE, DISTRICT_TYPE, TYPE_CODE
    # SDTYP codes: 1=Elementary, 2=Secondary, 3=Unified (numeric)
    #              E=Elementary, S=Secondary, U=Unified (string)
    type_column = None
    for col in ["SDTYP", "TYPE", "DISTRICT_TYPE", "TYPE_CODE"]:
        if col in gdf.columns:
            type_column = col
            break
    
    if type_column:
        if type_column != "TYPE":
            gdf["TYPE"] = gdf[type_column].copy()
            logger.info(f"Mapped {type_column} to TYPE")
        # Map SDTYP codes to readable types
        if type_column == "SDTYP" and "TYPE" in gdf.columns:
            # Handle both numeric and string codes
            type_map_numeric = {1: "Elementary", 2: "Secondary", 3: "Unified"}
            type_map_string = {"E": "Elementary", "S": "Secondary", "U": "Unified", 
                              "1": "Elementary", "2": "Secondary", "3": "Unified"}
            
            # Try numeric mapping first
            sdtyp_numeric = pd.to_numeric(gdf["SDTYP"], errors='coerce')
            mapped = sdtyp_numeric.map(type_map_numeric)
            
            # Fill remaining with string mapping
            remaining = mapped.isna()
            if remaining.any():
                mapped[remaining] = gdf.loc[remaining, "SDTYP"].astype(str).map(type_map_string)
            
            # Fill any remaining with original value (or "Unknown" if null)
            gdf["TYPE"] = mapped.fillna(gdf["SDTYP"].astype(str).replace("None", "Unknown"))
            logger.info(f"Mapped SDTYP codes to district types")
            
            # Log type distribution
            type_counts = gdf["TYPE"].value_counts()
            logger.info(f"District type distribution: {dict(type_counts)}")
    else:
        logger.warning("District type column (SDTYP/TYPE) not found. Available columns: " + ", ".join(gdf.columns))
    
    # Ensure CRS is set (NCES files typically use EPSG:4269 or EPSG:3857)
    if gdf.crs is None:
        logger.warning("CRS not set in shapefile, assuming EPSG:4269 (NAD83)")
        gdf.set_crs("EPSG:4269", inplace=True)
    else:
        logger.info(f"GeoDataFrame CRS: {gdf.crs}")
        # Ensure we're in a standard CRS for spatial operations
        if gdf.crs.to_string() != "EPSG:4269":
            logger.info(f"Reprojecting from {gdf.crs} to EPSG:4269 for consistency")
            gdf = gdf.to_crs("EPSG:4269")
    
    # Validate geometry
    if gdf.geometry.isnull().any():
        null_count = gdf.geometry.isnull().sum()
        logger.warning(f"Found {null_count} null geometries, removing")
        gdf = gdf[gdf.geometry.notnull()].copy()
    
    # Validate geometries are valid
    invalid_count = (~gdf.geometry.is_valid).sum()
    if invalid_count > 0:
        logger.warning(f"Found {invalid_count} invalid geometries, attempting to fix")
        gdf.geometry = gdf.geometry.buffer(0)  # Fix invalid geometries
    
    # Set NCESID as index if available
    # Note: Some districts may have duplicate NCES IDs (e.g., overlapping districts)
    # In that case, we'll keep GEOID as a unique identifier or use a composite key
    if "NCESID" in gdf.columns:
        # Check for duplicates
        duplicate_count = gdf["NCESID"].duplicated().sum()
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} duplicate NCES IDs")
            # For duplicates, create a composite identifier using GEOID
            if "GEOID" in gdf.columns:
                # Use GEOID as the index instead for uniqueness
                logger.info("Using GEOID as index instead (more unique than NCESID)")
                if gdf["GEOID"].duplicated().any():
                    logger.warning("GEOID also has duplicates, keeping both columns")
                else:
                    gdf = gdf.set_index("GEOID")
            else:
                # Keep NCESID but don't set as index if duplicates exist
                logger.info("Keeping NCESID as column due to duplicates")
        else:
            gdf = gdf.set_index("NCESID")
            logger.info("Set NCESID as index")
    
    logger.info(f"NCES EDGE ingestion complete: {len(gdf)} district boundaries ready")
    
    return gdf


def ingest_college_scorecard():
    """Ingest College Scorecard data via API or bulk download.
    
    Returns:
        DataFrame with college data (net price, graduation rates, earnings)
    """
    logger.info("Ingesting College Scorecard data")
    # TODO: Implement College Scorecard API calls or bulk download
    pass
