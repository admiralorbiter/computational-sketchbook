# LODES Data Integration

## Overview

This document describes the integration of LEHD Origin-Destination Employment Statistics (LODES) data into the Kansas City Data Platform. LODES provides census block-level employment data showing where workers live, where they work, and commuting patterns between these locations.

## Data Source

**LODES 8** (Latest Version)
- **Source**: https://lehd.ces.census.gov/data/lodes/LODES8/
- **Coverage**: Missouri and Kansas
- **Year**: 2021 (most recent available)
- **Update Frequency**: Annual (with 2+ year lag)
- **Format**: CSV.gz files

## Three Main Data Types

### 1. WAC (Workplace Area Characteristics)
Describes jobs by the census block where the workplace is located.

**File Structure**: `{state}_wac_{segment}_{jobtype}_{year}.csv.gz`
- Example: `mo_wac_S000_JT00_2021.csv.gz`

**Key Variables**:
- `w_geocode`: 15-digit census block GEOID (where job is located)
- `C000`: Total jobs
- `CA01-CA03`: Jobs by age group
- `CE01-CE03`: Jobs by earnings level
- `CNS01-CNS20`: Jobs by NAICS industry sector
- `CR01-CR07`: Jobs by race
- `CT01-CT02`: Jobs by ethnicity
- `CD01-CD04`: Jobs by education level
- `CS01-CS02`: Jobs by sex
- `CFA01-CFA05`: Jobs by firm age
- `CFS01-CFS05`: Jobs by firm size

### 2. RAC (Residence Area Characteristics)
Describes jobs by the census block where the worker lives.

**File Structure**: `{state}_rac_{segment}_{jobtype}_{year}.csv.gz`
- Example: `mo_rac_S000_JT00_2021.csv.gz`

**Key Variables**:
- `h_geocode`: 15-digit census block GEOID (where worker lives)
- `C000`: Total jobs (workers)
- (Same demographic breakdowns as WAC)

### 3. OD (Origin-Destination)
Describes commute flows between census blocks.

**File Structure**: `{state}_od_{segment}_{jobtype}_{year}.csv.gz`
- Example: `mo_od_S000_JT00_2021.csv.gz`

**Key Variables**:
- `w_geocode`: Workplace block GEOID
- `h_geocode`: Residence block GEOID
- `S000`: Total jobs in flow
- `SA01-SA03`: Jobs by age in flow
- `SE01-SE03`: Jobs by earnings in flow
- `SI01-SI03`: Jobs by industry in flow

## Segments

Each file type includes multiple segments:

| Segment | Description |
|---------|-------------|
| S000 | Total jobs (all categories) |
| SA01 | Age 29 or younger |
| SA02 | Age 30 to 54 |
| SA03 | Age 55 or older |
| SE01 | Earnings ≤$1,250/month |
| SE02 | Earnings $1,251-$3,333/month |
| SE03 | Earnings ≥$3,334/month |
| SI01 | Goods producing industries |
| SI02 | Trade, transport, utilities |
| SI03 | All other industries |

## Data Storage

**GeoPackage**: `data/processed/lodes_data.gpkg`

### Tables
- `lodes_wac`: Workplace area characteristics
- `lodes_rac`: Residence area characteristics
- `lodes_od`: Origin-destination flows

All tables link to census blocks via GEOID for spatial operations.

## Data Import

**ETL Script**: `tools/etl/load_lodes_data.py`

```bash
python tools/etl/load_lodes_data.py
```

This script:
1. Downloads all LODES files for Missouri and Kansas
2. Processes all segments (S000, SA01-SA03, SE01-SE03, SI01-SI03)
3. Combines segments into unified tables
4. Loads into `lodes_data.gpkg` with spatial indexing

**Data Volume**:
- WAC: ~150K blocks × 50 columns
- RAC: ~150K blocks × 40 columns
- OD: ~2-5M block pairs
- Total download: ~200-300MB compressed

## API Endpoints

### `/api/v1/employment/workplace`
Get jobs by workplace location (WAC).

**Query Parameters**:
- `bbox`: Spatial bounding box [min_x,min_y,max_x,max_y]
- `industry_sector`: NAICS sector code (1-20)
- `earnings_range`: 'low', 'mid', or 'high'
- `limit`: Maximum records (default: 10000)
- `format`: 'geojson' or 'summary'

**Example**:
```
GET /api/v1/employment/workplace?bbox=-94.6,39.0,-94.5,39.1&format=summary
```

**Response**: GeoJSON FeatureCollection with job counts by census block

### `/api/v1/employment/residence`
Get jobs by residence location (RAC).

**Query Parameters**:
- `bbox`: Spatial bounding box
- `age_group`: 'young', 'middle', or 'senior'
- `limit`: Maximum records
- `format`: 'geojson' or 'summary'

**Example**:
```
GET /api/v1/employment/residence?bbox=-94.6,39.0,-94.5,39.1&age_group=middle
```

**Response**: GeoJSON FeatureCollection with worker counts by census block

### `/api/v1/employment/flows`
Get origin-destination commute flows.

**Query Parameters**:
- `bbox`: Spatial filter
- `min_jobs`: Minimum jobs in flow (default: 1)
- `limit`: Maximum flows (default: 5000)

**Example**:
```
GET /api/v1/employment/flows?bbox=-94.6,39.0,-94.5,39.1&min_jobs=5
```

**Response**: GeoJSON FeatureCollection with LineString features showing commutes

### `/api/v1/employment/stats`
Get employment statistics for a geographic area.

**Query Parameters**:
- `geoid`: Census block or block group GEOID
- `level`: 'block' or 'block_group'

**Example**:
```
GET /api/v1/employment/stats?geoid=290950001001000&level=block
```

**Response**: Summary statistics including total jobs, top industries, earnings distribution

### `/api/v1/employment/industries`
Get top industries by job count.

**Query Parameters**:
- `bbox`: Spatial filter
- `limit`: Number of industries to return (default: 10)

**Example**:
```
GET /api/v1/employment/industries?bbox=-94.6,39.0,-94.5,39.1&limit=5
```

**Response**: Array of industries with job counts

### `/api/v1/employment/balance`
Get jobs-to-housing balance analysis.

**Query Parameters**:
- `bbox`: Spatial filter

**Example**:
```
GET /api/v1/employment/balance?bbox=-94.6,39.0,-94.5,39.1
```

**Response**: Jobs vs. workers ratio by block

## Use Cases

### 1. Employment Center Analysis
Identify where jobs are concentrated within the Kansas City metro.

**Query**:
```python
# Get all jobs by workplace location
wac = employment_service.get_workplace_jobs(bbox=kc_metro_bbox)
```

**Analysis**:
- Count total jobs per census block
- Identify employment density hotspots
- Map top industries by location

### 2. Workforce Catchment Areas
Determine where workers live relative to major employment centers.

**Query**:
```python
# Get workers by residence
rac = employment_service.get_residence_jobs(bbox=kc_metro_bbox)
```

**Analysis**:
- Calculate average commute distances
- Identify worker residence concentrations
- Compare jobs-to-workers ratios

### 3. Commute Pattern Visualization
Show how workers travel between home and work.

**Query**:
```python
# Get commute flows
flows = employment_service.get_commute_flows(
    bbox=kc_metro_bbox,
    min_jobs=10
)
```

**Analysis**:
- Visualize major commute corridors
- Identify reverse commute patterns
- Analyze transit accessibility

### 4. Education-to-Employment Pipeline
Combine ACS education data with LODES employment to analyze training needs.

**Data**: LODES industry sectors + ACS education attainment

**Analysis**:
- Map worker education levels to industry sectors
- Identify skill gaps by geography
- Plan workforce training programs

### 5. Jobs-Housing Balance
Evaluate whether job locations align with worker residences.

**Query**:
```python
balance = employment_service.calculate_jobs_housing_balance(bbox=kc_metro_bbox)
```

**Metrics**:
- Ratio of jobs to housing units
- Commute time averages
- Spatial mismatch indicators

## Integration with Other Data

### Census Boundaries
LODES GEOIDs match TIGER census block boundaries for accurate spatial joining.

### ACS Demographics
Compare LODES worker demographics with ACS population characteristics for:
- Labor force participation analysis
- Income-earnings correlations
- Age distribution comparisons

### Business Licenses
Correlate LODES workplace data with KC business license counts to validate employment estimates.

### Transportation Data
Overlay commute flows with OSM road and transit networks to identify infrastructure needs.

### Crime and Service Requests
Analyze whether employment centers correlate with crime rates or 311 request patterns.

## Data Quality

### Known Issues
- LODES data has 2+ year lag from current year
- Some blocks may have suppressed data (<10 jobs) for privacy
- GEOID matching requires exact 15-digit block codes

### Validation
- Compare job totals with published state aggregates
- Verify GEOID format and completeness
- Check for unrealistic commute distances (likely data errors)

## Update Process

LODES data is updated annually by the Census Bureau. To update:

1. Check for new releases: https://lehd.ces.census.gov/data/lodes/LODES8/
2. Run ETL script: `python tools/etl/load_lodes_data.py`
3. Verify data quality and migration metrics
4. Update API documentation if schema changes

## References

- [LODES Data Dictionary](https://lehd.ces.census.gov/data/schema/lodes/LODES8.0/)
- [LEHD Program](https://lehd.ces.census.gov/)
- [Geography Reference](https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html)
- [NAICS Industry Codes](https://www.census.gov/naics/)

## API Usage Examples

### Python

```python
from web.services.employment_service import EmploymentService

service = EmploymentService()

# Get jobs in downtown KC
bbox = [-94.58, 39.09, -94.57, 39.11]  # Downtown bounding box
wac = service.get_workplace_jobs(bbox=bbox)

# Filter by high-wage jobs
high_wage = service.get_workplace_jobs(
    bbox=bbox,
    earnings_range='high'
)

# Find commute flows
flows = service.get_commute_flows(
    bbox=bbox,
    min_jobs=5
)

# Get top industries
industries = service.get_top_industries(bbox=bbox, limit=10)
```

### JavaScript (Frontend)

```javascript
// Fetch workplace jobs
const response = await fetch('/api/v1/employment/workplace?bbox=-94.6,39.0,-94.5,39.1');
const data = await response.json();

// Add to map
map.addSource('jobs', {
  type: 'geojson',
  data: data
});

// Get commute flows
const flowsResponse = await fetch('/api/v1/employment/flows?bbox=-94.6,39.0,-94.5,39.1&min_jobs=10');
const flowsData = await flowsResponse.json();

// Display as flow lines
map.addSource('commutes', {
  type: 'geojson',
  data: flowsData
});
```

This comprehensive integration enables detailed employment and commute pattern analysis throughout the Kansas City metropolitan area.

