# ACS Demographic Data Integration

This document describes the integration of American Community Survey (ACS) demographic data into the Kansas City Data Platform.

## Overview

The platform now integrates ACS 5-year demographic data at the block group level for the Kansas City metro area. This enables demographic visualization and analysis across Missouri and Kansas counties.

## Data Source

**ACS 5-Year Detailed Tables** (2019-2023)
- **Release Date**: December 12, 2024
- **Base URL**: https://api.census.gov/data/2023/acs/acs5
- **Geography**: Block Groups (smallest geographic unit for ACS data)
- **Coverage**: 8 Kansas City metro counties

## Counties Covered

### Missouri
- **29095** - Jackson County
- **29047** - Clay County
- **29165** - Platte County
- **29037** - Cass County

### Kansas
- **20091** - Johnson County
- **20209** - Wyandotte County
- **20103** - Leavenworth County
- **20121** - Miami County

## Variables Included

### Population
- **Total Population** (`population`) - B01001_001E

### Economic Indicators
- **Median Household Income** (`median_household_income`) - B19013_001E
- **Income MOE** (`mhi_moe`) - B19013_001M (90% confidence level)

### Poverty Statistics
- **Poverty Universe** (`poverty_universe`) - B17001_001E
- **Below Poverty** (`poverty_count`) - B17001_002E
- **Poverty Rate** (`poverty_rate`) - Calculated as poverty_count / poverty_universe

### Race and Ethnicity
- **Total Race** (`total_race`) - B03002_001E
- **White Alone** (`white_alone`) - B03002_003E
- **Black Alone** (`black_alone`) - B03002_004E
- **Hispanic/Latino** (`hispanic_latino`) - B03002_012E

### Metadata
- **ACS Year** (`acs_year`) - e.g., "2019-2023"
- **Release Date** (`acs_release`) - Release date or version

## Setup

### 1. Environment Configuration

Add your Census API key to the `.env` file:

```bash
CENSUS_API_KEY=your-census-api-key-here
```

You can obtain a free API key from: https://api.census.gov/data/key_signup.html

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add ACS Columns to Database

```bash
python tools/database/add_acs_columns.py
```

This script adds the necessary columns to the `block_groups` table. It's safe to run multiple times - it will only add columns that don't already exist.

### 4. Load ACS Data

```bash
python tools/etl/load_acs_data.py
```

This script will:
1. Fetch ACS data from Census API for all 8 KC metro counties
2. Calculate derived metrics (e.g., poverty_rate)
3. Update the `block_groups` table with demographic data

Expected output:
```
Starting ACS Data ETL...
Census API: https://api.census.gov/data/2023/acs/acs5
ACS Year: 2019-2023
Target counties: 8
Fetching ACS data for state=29, county=095...
Fetched 689 block groups for county 095
...
Total block groups processed: 1245
```

## API Endpoints

### Block Groups with ACS Data

**GET** `/api/v1/census/block_groups`

Returns GeoJSON FeatureCollection of block group boundaries with ACS demographic data.

**Query Parameters:**
- `bbox` (required) - Bounding box: `minx,miny,maxx,maxy`
- `simplify` (optional) - Simplification in meters (e.g., `20`)

**Example:**
```
GET /api/v1/census/block_groups?bbox=-94.7,38.9,-94.5,39.2&simplify=20
```

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {...},
      "properties": {
        "geoid": "290950001001",
        "population": 1243,
        "median_household_income": 45234,
        "poverty_rate": 0.15,
        "white_alone": 823,
        "black_alone": 234,
        "hispanic_latino": 156,
        "acs_year": "2019-2023"
      }
    }
  ]
}
```

## Frontend Visualization

The ACS data is displayed using choropleth mapping with color-coded poverty rates:

### Poverty Rate Color Scale
- **≥30%** - Dark red (#67000d)
- **20-30%** - Red (#cb181d)
- **10-20%** - Light red (#ef3b2c)
- **5-10%** - Pink (#fb6a4a)
- **>0-5%** - Light pink (#fcae91)
- **0%** - Very light gray (#f7f7f7)

### Popup Information

When clicking on a block group, a popup displays:
- GEOID
- Population
- Median Household Income
- Poverty Rate
- Race/Ethnicity breakdown (White, Black, Hispanic/Latino)

## Database Schema

ACS columns are stored directly in the `block_groups` table:

```sql
ALTER TABLE block_groups ADD COLUMN population INTEGER;
ALTER TABLE block_groups ADD COLUMN median_household_income INTEGER;
ALTER TABLE block_groups ADD COLUMN mhi_moe INTEGER;
ALTER TABLE block_groups ADD COLUMN poverty_universe INTEGER;
ALTER TABLE block_groups ADD COLUMN poverty_count INTEGER;
ALTER TABLE block_groups ADD COLUMN poverty_rate REAL;
ALTER TABLE block_groups ADD COLUMN total_race INTEGER;
ALTER TABLE block_groups ADD COLUMN white_alone INTEGER;
ALTER TABLE block_groups ADD COLUMN black_alone INTEGER;
ALTER TABLE block_groups ADD COLUMN hispanic_latino INTEGER;
ALTER TABLE block_groups ADD COLUMN acs_year TEXT;
ALTER TABLE block_groups ADD COLUMN acs_release TEXT;
```

## Current Implementation Status

### Imported Categories (17 categories, 200+ variables) ✅

1. **Core Demographics** - Population, median age, income, poverty
2. **Age Distribution** - 46 age brackets by sex
3. **Race & Ethnicity** - Basic categories (White, Black, Hispanic)
4. **Housing Basic** - Occupancy, tenure, value, rent
5. **Housing Cost Burden** - Housing costs as % of income
6. **Housing Year Built** - Decade ranges (1939-2014+)
7. **Housing Units in Structure** - Single, multi-unit, mobile homes
8. **Vehicle Availability** - 0-4+ vehicles per household
9. **Income Distribution** - 17 income brackets
10. **Education** - High school through doctorate
11. **Employment** - Labor force participation
12. **Commuting** - Mode of transportation to work
13. **Health Insurance** - Coverage type
14. **Disability** - Basic disability status
15. **Veterans** - Basic veteran status
16. **Language** - English proficiency
17. **Citizenship** - Nativity and citizenship status
18. **Family Structure** - Family vs non-family households

### Available but Not Yet Imported

See [ACS_BLOCK_GROUP_INVENTORY.md](data/ACS_BLOCK_GROUP_INVENTORY.md) for comprehensive tracking of:
- Computer and internet access (P0)
- Detailed race categories (P1)
- Detailed occupation categories (P0)
- Detailed industry categories (P0)
- Commute time (P3)
- Migration/mobility (P1)
- Marital status (P2)
- Fertility rates (P2)
- Grandparents as caregivers (P2)
- Group quarters population (P2)
- School enrollment by level (P2)
- Income by source (P2)
- Housing physical characteristics (P1)
- Housing costs detailed (P1)

### Importing Additional Data

To import additional ACS variables by priority:

```bash
# Import P0 (Critical) variables
python tools/etl/load_acs_data_by_priority.py --priority P0

# Import P1 (High Value) variables
python tools/etl/load_acs_data_by_priority.py --priority P1

# Check import status
python tools/etl/load_acs_data_by_priority.py --priority status
```

### Geographic Expansion

Currently limited to block groups, we could add:
- Tract-level data for broader demographic indicators
- County-level summaries
- Statistical comparison features

### Advanced Visualizations

- Heat maps for density indicators
- Comparison tools between geographic areas
- Time series analysis (when multi-year data available)
- Demographic overlays on other datasets

## Technical Notes

### Data Refresh

ACS data is updated annually. To refresh:

1. Update `ACS_YEAR` and `ACS_RELEASE` in `load_acs_data.py`
2. Run the ETL script to fetch and load new data
3. The database columns remain the same; only data values change

### API Rate Limits

The Census API has rate limits:
- **Without API key**: 500 requests/day
- **With API key**: Higher limits

The ETL script includes a 200ms delay between requests to respect rate limits.

### Margin of Error (MOE)

ACS estimates include margins of error at 90% confidence level. The `mhi_moe` field stores the margin of error for median household income. These should be taken into account when making decisions based on the data.

### Geographic Matching

Block groups are matched between TIGER boundaries and ACS data using the 12-digit GEOID (state + county + tract + block group).

## Troubleshooting

### API Key Issues

**Error**: "CENSUS_API_KEY not found"
- **Solution**: Add your Census API key to `.env` file
- Get a free key at: https://api.census.gov/data/key_signup.html

### No ACS Data Displayed

**Symptoms**: Block groups show gray colors (no choropleth)
- **Solution**: Run `python tools/etl/load_acs_data.py` to fetch and load data

### Database Column Errors

**Error**: "no such column: population"
- **Solution**: Run `python tools/database/add_acs_columns.py` to add missing columns

### Data Quality Issues

**Margins of Error**: Remember ACS estimates have margins of error. Small block groups or sparsely populated areas may have larger margins of error.

**Missing Data**: Some block groups may not have complete data if the sample size was too small for reliable estimates.

## References

- [Census ACS API](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [ACS Variable Definitions](https://www.census.gov/programs-surveys/acs/data.html)
- [Understanding ACS MOE](https://www.census.gov/programs-surveys/acs/guidance/predicting-acs-values-for-year-between-release.html)
- [TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)

