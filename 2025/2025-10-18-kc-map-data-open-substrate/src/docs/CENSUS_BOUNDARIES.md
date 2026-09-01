# Census TIGER Boundaries Integration

This document describes the Census TIGER boundary data integration for the Kansas City Data Platform.

## Overview

The platform now supports Census TIGER/Line boundary data for Block Groups and Blocks in the Kansas City metro area. This enables users to visualize census geographic boundaries and provides a foundation for future demographic data joins.

## Data Sources

### TIGER/Line Shapefiles

Data is downloaded from the U.S. Census Bureau's TIGER/Line files:

- **Base URL**: https://www2.census.gov/geo/tiger/TIGER2025/
- **Block Groups**: `BG/` directory
- **Blocks**: `TABBLOCK20/` directory (2020 blocks are latest available)

### Target Counties

#### Missouri Counties
- **29095** - Jackson County
- **29047** - Clay County
- **29165** - Platte County
- **29037** - Cass County

#### Kansas Counties
- **20091** - Johnson County
- **20209** - Wyandotte County
- **20103** - Leavenworth County
- **20121** - Miami County

## Data Storage

All TIGER boundary data is stored in a GeoPackage located at:
```
data/processed/tiger_boundaries.gpkg
```

The GeoPackage contains two layers:
- `block_groups` - Census Block Group boundaries
- `blocks` - Census Block boundaries (2020)

All geometries are reprojected to WGS84 (EPSG:4326) for web map compatibility.

## Running the ETL Script

### Prerequisites

Install required dependencies:
```bash
pip install geopandas requests shapely
```

### Running the Script

From the project root:
```bash
cd tools/etl
python load_tiger_boundaries.py
```

The script will:
1. Download TIGER 2025 shapefiles for Missouri (state FIPS 29) and Kansas (state FIPS 20)
2. Filter to KC metro counties
3. Reproject from NAD83 to WGS84
4. Combine all counties into a single GeoPackage
5. Save to `data/processed/tiger_boundaries.gpkg`

### Output

Upon completion, you'll have:
- `data/processed/tiger_boundaries.gpkg` with two layers
- All boundary features with GEOID and TIGER attributes
- Properly formatted for web map display

## API Endpoints

### Block Groups

**GET** `/api/v1/census/block_groups`

Returns GeoJSON FeatureCollection of block group boundaries.

**Query Parameters:**
- `bbox` (required) - Bounding box: `minx,miny,maxx,maxy`
- `simplify` (optional) - Simplification in meters (e.g., `20`)

**Example:**
```
/api/v1/census/block_groups?bbox=-95.0,38.9,-94.0,39.3&simplify=20
```

### Blocks

**GET** `/api/v1/census/blocks`

Returns GeoJSON FeatureCollection of block boundaries.

**Query Parameters:**
- `bbox` (required) - Bounding box: `minx,miny,maxx,maxy`
- `simplify` (optional) - Simplification in meters (e.g., `20`)

**Example:**
```
/api/v1/census/blocks?bbox=-95.0,38.9,-94.0,39.3&simplify=20
```

## Frontend Integration

### Layer Configuration

Block groups and blocks are integrated as standard map layers with:

- **Block Groups**: Medium gray (#95a5a6) with border icon
- **Blocks**: Light gray (#bdc3c7) with grid icon

### Rendering

Polygon features are rendered using Leaflet's `L.geoJSON()` with:
- Semi-transparent fills (10% opacity)
- Color-coded borders
- Thicker borders for block groups (2px) vs blocks (1px)
- Click handlers showing GEOID and attributes in popups

### Layer Controls

Users can toggle Census boundaries on/off via checkboxes in the layer control panel under "Census Boundaries" section.

## Technical Details

### Coordinate Systems

- **Source**: NAD83 (EPSG:4269) from Census Bureau
- **Storage**: WGS84 (EPSG:4326) for web compatibility
- **Display**: EPSG:3857 (Web Mercator) for Leaflet rendering

### Geometry Simplification

The API supports on-the-fly geometry simplification to reduce payload size:

1. Convert to Web Mercator (EPSG:3857)
2. Apply Douglas-Peucker simplification
3. Convert back to WGS84 (EPSG:4326)

The `simplify` parameter specifies tolerance in meters.

### Attributes

Each feature includes:
- `geoid` - Full geographic identifier
- `statefp` - State FIPS code
- `countyfp` - County FIPS code
- `tractce` - Census tract code
- `blkgrpce` - Block group code (for block groups)
- `blockce` - Block code (for blocks)
- Additional TIGER/Line attributes as available

## Future Enhancements

### Demographic Data Integration

The GEOID field enables joining with American Community Survey (ACS) demographic data:

- Income statistics
- Housing characteristics
- Population demographics
- Education levels
- Employment statistics

### Suggested Next Steps

1. Add ACS data loading ETL script
2. Create demographic data models
3. Add data join logic in data service
4. Create new API endpoints for demographic queries
5. Add demographic visualization controls to frontend

### Data Refresh

TIGER files are updated annually by the Census Bureau. To refresh:

1. Update the year in `load_tiger_boundaries.py` (line 32)
2. Update URLs to new TIGER year
3. Re-run the ETL script
4. Update any hardcoded year references

## Troubleshooting

### Common Issues

**FileNotFoundError: tiger_boundaries.gpkg**
- Run the ETL script to download and process data
- Check that `data/processed/` directory exists

**ImportError: geopandas**
- Install: `pip install geopandas shapely`

**API returns empty results**
- Verify bbox covers Kansas City metro area
- Check that tiger_boundaries.gpkg exists and has data
- Review logs for spatial intersection errors

**Polygons not rendering on map**
- Check browser console for GeoJSON parsing errors
- Verify geometry types are Polygon or MultiPolygon
- Ensure EPSG:4326 coordinate system

### Performance Optimization

For large datasets:

1. Use the `simplify` parameter (e.g., 20-50 meters)
2. Set appropriate zoom levels for loading
3. Consider minimum zoom thresholds
4. Use spatial indexing in queries

## References

- [Census TIGER/Line Files](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
- [GeoPandas Documentation](https://geopandas.org/)
- [Leaflet GeoJSON](https://leafletjs.com/examples/geojson/)
- [American Community Survey Data](https://www.census.gov/programs-surveys/acs/data.html)

