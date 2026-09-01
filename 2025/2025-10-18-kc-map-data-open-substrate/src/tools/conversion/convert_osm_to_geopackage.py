#!/usr/bin/env python3
"""
OSM to GeoPackage/SQLite Converter

This script converts OpenStreetMap (.osm.pbf) files to GeoPackage or SQLite format
using OSGeo4W's GDAL/OGR tools.

Requirements:
- OSGeo4W installed (typically at C:\\Users\\<username>\\AppData\\Local\\Programs\\OSGeo4W)
- Python 3.6+

Usage:
    python convert_osm_to_geopackage.py input.osm.pbf output.gpkg
    python convert_osm_to_geopackage.py input.osm.pbf output.sqlite
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import platform


def find_osgeo4w_path():
    """Find the OSGeo4W installation path."""
    system = platform.system().lower()
    
    if system == "windows":
        # Common OSGeo4W installation paths
        possible_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "OSGeo4W",
            Path.home() / "AppData" / "Local" / "Programs" / "OSGeo4W64",
            Path("C:/OSGeo4W"),
            Path("C:/OSGeo4W64"),
            Path("C:/Program Files/OSGeo4W"),
            Path("C:/Program Files/OSGeo4W64")
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "bin" / "ogr2ogr.exe").exists():
                return path
        
        # If not found, try the user-specified path
        user_path = Path.home() / "AppData" / "Local" / "Programs" / "OSGeo4W"
        if user_path.exists():
            return user_path
    
    return None


def setup_osgeo4w_environment(osgeo4w_path):
    """Set up environment variables for OSGeo4W."""
    if not osgeo4w_path:
        return False
    
    bin_path = osgeo4w_path / "bin"
    etc_path = osgeo4w_path / "etc"
    
    # Add OSGeo4W bin directory to PATH
    current_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_path) + os.pathsep + current_path
    
    # Set GDAL_DATA environment variable
    gdal_data = osgeo4w_path / "apps" / "gdal" / "share" / "gdal"
    if gdal_data.exists():
        os.environ["GDAL_DATA"] = str(gdal_data)
    
    # Set PROJ_LIB environment variable
    proj_lib = etc_path / "proj"
    if proj_lib.exists():
        os.environ["PROJ_LIB"] = str(proj_lib)
    
    # Set GDAL_DRIVER_PATH environment variable
    gdal_driver_path = bin_path / "gdal" / "plugins"
    if gdal_driver_path.exists():
        os.environ["GDAL_DRIVER_PATH"] = str(gdal_driver_path)
    
    return True


def get_ogr2ogr_command():
    """Get the appropriate ogr2ogr command for the current platform."""
    system = platform.system().lower()
    
    if system == "windows":
        return "ogr2ogr.exe"
    else:
        return "ogr2ogr"


def convert_osm_to_geopackage(input_file, output_file, osgeo4w_path=None):
    """
    Convert OSM PBF file to GeoPackage or SQLite format.
    
    Args:
        input_file (str): Path to input OSM PBF file
        output_file (str): Path to output GeoPackage/SQLite file
        osgeo4w_path (str): Optional path to OSGeo4W installation
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    # Validate input file
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        return False
    
    if not input_path.suffix.lower() in ['.pbf', '.osm.pbf']:
        print(f"Error: Input file must be a .pbf or .osm.pbf file.")
        return False
    
    # Determine output format based on file extension
    output_ext = output_path.suffix.lower()
    if output_ext == '.gpkg':
        output_format = "GPKG"
    elif output_ext == '.sqlite':
        output_format = "SQLite"
    else:
        print(f"Error: Output format '{output_ext}' not supported. Use .gpkg or .sqlite")
        return False
    
    # Set up OSGeo4W environment
    if osgeo4w_path:
        osgeo4w_path = Path(osgeo4w_path)
    else:
        osgeo4w_path = find_osgeo4w_path()
    
    if not setup_osgeo4w_environment(osgeo4w_path):
        print("Error: Could not find or set up OSGeo4W installation.")
        print("Please ensure OSGeo4W is installed and accessible.")
        return False
    
    # Get ogr2ogr command
    ogr2ogr_cmd = get_ogr2ogr_command()
    
    # Build the conversion command
    cmd = [
        ogr2ogr_cmd,
        "-f", output_format,
        str(output_path),
        str(input_path),
        "-overwrite",  # Overwrite output file if it exists
        "-progress"    # Show progress
    ]
    
    print(f"Converting '{input_file}' to '{output_file}'...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run the conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Conversion completed successfully!")
        
        # Print any warnings
        if result.stderr:
            print("Warnings:")
            print(result.stderr)
        
        # Check if output file was created
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"Output file created: {output_path}")
            print(f"File size: {file_size:.2f} MB")
            return True
        else:
            print("Error: Output file was not created.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion:")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: Could not find '{ogr2ogr_cmd}' command.")
        print("Please ensure OSGeo4W is properly installed and ogr2ogr is available.")
        return False


def main():
    """Main function to handle command line arguments and run conversion."""
    parser = argparse.ArgumentParser(
        description="Convert OSM PBF files to GeoPackage or SQLite format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_osm_to_geopackage.py data/missouri.osm.pbf missouri.gpkg
  python convert_osm_to_geopackage.py data/missouri.osm.pbf missouri.sqlite
  python convert_osm_to_geopackage.py data/missouri.osm.pbf missouri.gpkg --osgeo4w "C:/OSGeo4W"
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to input OSM PBF file"
    )
    
    parser.add_argument(
        "output_file", 
        help="Path to output GeoPackage (.gpkg) or SQLite (.sqlite) file"
    )
    
    parser.add_argument(
        "--osgeo4w",
        help="Path to OSGeo4W installation directory (optional)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Run the conversion
    success = convert_osm_to_geopackage(
        args.input_file,
        args.output_file,
        args.osgeo4w
    )
    
    if success:
        print("\nConversion completed successfully!")
        sys.exit(0)
    else:
        print("\nConversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
