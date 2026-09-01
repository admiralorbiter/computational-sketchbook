#!/usr/bin/env python3
"""
Data Setup Script for Kansas City Data Platform

This script helps users download and set up the required data files
for the Kansas City Data Platform application.

The .gpkg files are excluded from Git due to their large size (1GB+).
This script provides instructions for obtaining the data files.
"""

import os
import sys
from pathlib import Path

def check_data_files():
    """Check if required data files exist"""
    data_dir = Path("data/processed")
    required_files = [
        "kc_data.gpkg",
        "missouri.gpkg"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    return missing_files

def print_setup_instructions():
    """Print instructions for setting up data files"""
    print("=" * 60)
    print("KANSAS CITY DATA PLATFORM - DATA SETUP")
    print("=" * 60)
    print()
    print("The following data files are required but excluded from Git due to size:")
    print()
    print("Required files:")
    print("  - data/processed/kc_data.gpkg (Kansas City Open Data)")
    print("  - data/processed/missouri.gpkg (Missouri OSM Data)")
    print("  - data/raw/missouri.osm.pbf (Missouri OSM Raw Data - 171MB)")
    print()
    print("To obtain these files:")
    print()
    print("1. Kansas City Data (kc_data.gpkg):")
    print("   Run the ETL scripts in tools/etl/ to download and process KC Open Data")
    print("   python tools/etl/kc_data_ingest.py")
    print()
    print("2. Missouri OSM Data (missouri.gpkg):")
    print("   First download the raw OSM data:")
    print("   - Download missouri.osm.pbf from https://download.geofabrik.de/north-america/us/missouri.html")
    print("   - Place it in data/raw/missouri.osm.pbf")
    print("   Then run the conversion script:")
    print("   python tools/conversion/convert_osm_to_geopackage.py")
    print()
    print("3. Alternative - Download pre-processed files:")
    print("   Contact the project maintainer for access to pre-processed data files")
    print()
    print("Once you have the data files, you can start the application with:")
    print("   python start_app.py")
    print()

def main():
    """Main setup function"""
    missing_files = check_data_files()
    
    if not missing_files:
        print("[OK] All required data files are present!")
        print("You can start the application with: python start_app.py")
        return
    
    print(f"[ERROR] Missing {len(missing_files)} required data file(s):")
    for file in missing_files:
        print(f"   - {file}")
    print()
    
    print_setup_instructions()

if __name__ == "__main__":
    main()
