#!/usr/bin/env python3
"""
TIGER/Line Census Boundary Data ETL Script

Downloads and processes Census TIGER/Line shapefiles for block groups and blocks
for the Kansas City metro area (Missouri and Kansas counties).

Data Source: https://www2.census.gov/geo/tiger/TIGER2025/
"""

import os
import sys
import zipfile
import tempfile
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import geopandas as gpd
    import requests
except ImportError as e:
    print(f"Error: Missing required packages. Install with: pip install geopandas requests")
    sys.exit(1)

# Kansas City metro area counties (5-digit FIPS)
KC_MO_COUNTIES = {
    '29095': 'Jackson',
    '29047': 'Clay',
    '29165': 'Platte',
    '29037': 'Cass'
}

KC_KS_COUNTIES = {
    '20091': 'Johnson',
    '20209': 'Wyandotte',
    '20103': 'Leavenworth',
    '20121': 'Miami'
}

# TIGER 2025 data URLs
TIGER_BASE_URL = 'https://www2.census.gov/geo/tiger/TIGER2025'

# Layer types
BLOCK_GROUPS = 'BG'
BLOCKS = 'TABBLOCK20'  # 2020 blocks are the latest available

def setup_logging():
    """Setup logging"""
    logger = logging.getLogger('load_tiger_boundaries')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def download_shapefile(url, output_dir):
    """Download and extract shapefile from Census FTP"""
    logger = setup_logging()
    
    logger.info(f"Downloading {url}...")
    
    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        
        # Create temp directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / 'data.zip'
            
            # Write zip file
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Extracting to {output_dir}...")
            
            # Extract to output directory
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            logger.info("Extraction complete")
            return True
            
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False

def process_county_data(county_fips, state_fips, state_name, layer_type, output_gdf_list):
    """Download and process TIGER data for a county"""
    logger = setup_logging()
    
    # Construct URL
    # Format: https://www2.census.gov/geo/tiger/TIGER2025/BG/tl_2025_29_bg.zip
    tiger_code = state_fips  # MO=29, KS=20
    url = f"{TIGER_BASE_URL}/{layer_type}/tl_2025_{tiger_code}_{layer_type.lower()}.zip"
    
    # Create temp directory for this county
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        logger.info(f"Processing {state_name} county {county_fips} - {layer_type}...")
        
        # Download if not exists
        download_dir = temp_dir / f"extracted_{layer_type}"
        if not download_shapefile(url, download_dir):
            return
        
        # Find the shapefile
        shp_files = list(download_dir.glob(f"tl_2025_{tiger_code}_{layer_type.lower()}*.shp"))
        
        if not shp_files:
            logger.warning(f"No shapefile found in {download_dir}")
            return
        
        # Read the shapefile
        logger.info(f"Reading shapefile: {shp_files[0]}")
        gdf = gpd.read_file(shp_files[0])
        
        # Get county code (last 3 digits of county FIPS)
        county_code = county_fips[-3:]
        
        # Filter to this county - check if COUNTYFP column exists
        if 'COUNTYFP' in gdf.columns:
            county_gdf = gdf[gdf['COUNTYFP'] == county_code].copy()
        elif 'COUNTYFP20' in gdf.columns:
            # Blocks use COUNTYFP20
            county_gdf = gdf[gdf['COUNTYFP20'] == county_code].copy()
        else:
            logger.error(f"No COUNTYFP column found in shapefile. Columns: {gdf.columns.tolist()}")
            return
        
        if county_gdf.empty:
            logger.warning(f"No data found for county {county_fips}")
            return
        
        logger.info(f"Found {len(county_gdf)} features for county {county_fips}")
        
        # Reproject to WGS84 (EPSG:4326) if needed
        if county_gdf.crs != 'EPSG:4326':
            logger.info(f"Reprojecting from {county_gdf.crs} to EPSG:4326")
            county_gdf = county_gdf.to_crs('EPSG:4326')
        
        # Add to list
        output_gdf_list.append(county_gdf)
        
    except Exception as e:
        logger.error(f"Error processing county {county_fips}: {e}")
    finally:
        # Cleanup temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def main():
    """Main ETL function"""
    logger = setup_logging()
    
    logger.info("Starting TIGER Boundary ETL...")
    logger.info(f"Target counties: {len(KC_MO_COUNTIES)} MO, {len(KC_KS_COUNTIES)} KS")
    
    # Output directory
    output_dir = project_root / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "tiger_boundaries.gpkg"
    
    # Track if this is the first layer
    first_layer = True
    
    # Process block groups and blocks
    for layer_type in [BLOCK_GROUPS, BLOCKS]:
        logger.info(f"\nProcessing {layer_type}...")
        
        gdf_list = []
        
        # Process Missouri counties
        for county_fips, county_name in KC_MO_COUNTIES.items():
            process_county_data(county_fips, '29', 'Missouri', layer_type, gdf_list)
        
        # Process Kansas counties
        for county_fips, county_name in KC_KS_COUNTIES.items():
            process_county_data(county_fips, '20', 'Kansas', layer_type, gdf_list)
        
        if gdf_list:
            # Concatenate all counties
            logger.info(f"Combining {len(gdf_list)} county datasets...")
            combined_gdf = gpd.pd.concat(gdf_list, ignore_index=True)
            
            logger.info(f"Total features: {len(combined_gdf)}")
            logger.info(f"CRS: {combined_gdf.crs}")
            
            # Write to GeoPackage
            layer_name = layer_type.lower()
            logger.info(f"Writing to {output_file} (layer: {layer_name})...")
            
            # Use 'w' mode for first layer, 'a' for subsequent layers
            write_mode = 'w' if first_layer else 'a'
            combined_gdf.to_file(output_file, layer=layer_name, driver='GPKG', mode=write_mode)
            first_layer = False
            
            logger.info(f"✓ Saved {len(combined_gdf)} features to layer '{layer_name}'")
        else:
            logger.error(f"No data collected for {layer_type}")
    
    logger.info("\nETL Complete!")
    logger.info(f"Output file: {output_file}")

if __name__ == "__main__":
    main()
