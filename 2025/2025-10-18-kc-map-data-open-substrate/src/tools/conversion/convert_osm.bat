@echo off
REM Simple batch script to convert OSM PBF to GeoPackage using OSGeo4W
REM Usage: convert_osm.bat input.osm.pbf output.gpkg

set OSGEO4W_ROOT=C:\Users\%USERNAME%\AppData\Local\Programs\OSGeo4W
set PATH=%OSGEO4W_ROOT%\bin;%PATH%
set GDAL_DATA=%OSGEO4W_ROOT%\apps\gdal\share\gdal

if "%1"=="" (
    echo Usage: convert_osm.bat input.osm.pbf output.gpkg
    echo Example: convert_osm.bat ..\..\data\raw\missouri.osm.pbf ..\..\data\processed\missouri.gpkg
    exit /b 1
)

if "%2"=="" (
    echo Error: Output file not specified
    echo Usage: convert_osm.bat input.osm.pbf output.gpkg
    exit /b 1
)

echo Converting %1 to %2...
ogr2ogr -f GPKG %2 %1 -overwrite -progress

if %ERRORLEVEL% EQU 0 (
    echo Conversion completed successfully!
) else (
    echo Conversion failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
