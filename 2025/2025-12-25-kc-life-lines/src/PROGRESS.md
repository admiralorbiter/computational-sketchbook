# KC: Life Lines Data Pipeline — Progress Tracking

*Last Updated:* 2025-01-XX  
*Version:* v0.1

This document tracks implementation progress for the KC: Life Lines data pipeline, organized by pipeline stage and data source.

---

## Pipeline Stages Overview

| Stage | Status | Notes |
|-------|--------|-------|
| **1. Data Ingestion** | 🟡 Partial | Foundation datasets complete; others are stubs |
| **2. Data Processing/Normalization** | 🔴 Not Started | Placeholder functions exist |
| **3. Data Joining** | 🔴 Not Started | Placeholder functions exist |
| **4. Index Calculation** | 🔴 Not Started | Placeholder functions exist |
| **5. Data Pack Export** | 🔴 Not Started | Basic structure exists |

**Legend:** 🟢 Complete | 🟡 Partial | 🔴 Not Started

---

## 1. Data Ingestion

### 1.1 Foundation Datasets (Required)

#### ✅ TIGER/Line Shapefiles
- **Status:** Complete
- **Implementation:** `data_pipeline/ingest/census.py::ingest_tiger_shapefiles()`
- **Verified:** ✅ Works correctly
- **Coverage:** MO (state 29) and KS (state 20) tract boundaries for KC metro counties
- **Output:** GeoDataFrame with 477 tracts, GEOID indexed, filtered to KC metro
- **Notes:** Uses downloaded ZIP files from `data/raw/tiger/`

#### ✅ American Community Survey (ACS)
- **Status:** Complete
- **Implementation:** `data_pipeline/ingest/census.py::ingest_acs_data()`
- **Verified:** ✅ Works correctly (477 tracts, 49 variables)
- **Variables Fetched:**
  - Income & Poverty: `B17001`, `B19013`
  - Housing: `B25003`, `B25064`, `B25002`
  - Vehicle Access: `B25044`
  - Insurance Coverage: `B27010`
  - Commute: `B08301`, `B08013`
  - Household Structure: `B11001`, `B25010`
- **Features:** 
  - Both estimates and margins of error (MOE)
  - Descriptive column names
  - GEOID standardization (11-digit format)
  - State/county/tract derivation from GEOID
  - Error handling with retry logic
- **Integration:** ✅ Wired into `main.py::_ingest_data()`
- **Alignment:** ✅ Perfect GEOID match with TIGER data (477/477)

#### 🔴 NCES EDGE School District Boundaries
- **Status:** Not Started
- **Implementation:** Not yet created
- **Planned Location:** `data_pipeline/ingest/education.py::ingest_nces_districts()`
- **Notes:** Needed for tract-to-district assignment

### 1.2 Education Data

#### 🔴 Missouri DESE (District/School Indicators)
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/education.py::ingest_mo_dese_data()` (stub exists)
- **Source:** https://dese.mo.gov/school-data
- **Priority:** High (core gameplay system)

#### 🔴 Kansas KSDE Data Central
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/education.py::ingest_ksde_data()` (stub exists)
- **Source:** https://datacentral.ksde.gov/
- **Priority:** High (core gameplay system)

#### 🔴 College Scorecard
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/education.py::ingest_college_scorecard()` (stub exists)
- **Source:** https://collegescorecard.ed.gov/data/api-documentation
- **Join Key:** IPEDS unit ID
- **Priority:** Medium-High (postsecondary choices)

### 1.3 Labor Market Data

#### 🔴 BLS Public Data API
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/labor.py::ingest_bls_data()` (stub exists)
- **Use:** Unemployment, CPI, time-series shocks
- **Priority:** Medium (labor market system)

#### 🔴 O*NET Database
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/labor.py::ingest_onet_database()` (stub exists)
- **Use:** Occupation skills, tasks, abilities
- **License:** Creative Commons Attribution 4.0
- **Priority:** Medium (work system depth)

### 1.4 Transportation Data

#### 🔴 KCATA GTFS
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/transit.py::ingest_kcata_gtfs()` (stub exists)
- **Source:** https://www.kcata.org/transit_data/access_gtdf
- **Use:** Transit access score, commute calculations
- **Priority:** High (transportation system core)
- **License Note:** Review KCATA terms before shipping

### 1.5 Health & Vulnerability Data

#### 🔴 CDC PLACES
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/health.py::ingest_cdc_places()` (stub exists)
- **Source:** https://www.cdc.gov/places/
- **Use:** Health risk environment modifiers
- **Priority:** Medium

#### 🔴 CDC/ATSDR Social Vulnerability Index (SVI)
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/health.py::ingest_svi()` (stub exists)
- **Source:** https://atsdr.cdc.gov/place-health/php/svi/
- **Use:** Vulnerability modifiers (use cautiously)
- **Priority:** Low-Medium

### 1.6 Housing Data

#### 🔴 HUD Location Affordability Index (LAI)
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/housing.py::ingest_hud_lai()` (stub exists)
- **Source:** https://www.hudexchange.info/programs/location-affordability-index/
- **Use:** Combined housing+transport cost pressure (block group level)
- **Priority:** Medium-High (housing system)

### 1.7 Local KC Data

#### 🔴 Open Data KC (Crime)
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/local.py::ingest_kc_crime_data()` (stub exists)
- **Source:** https://data.kcmo.org/ (Socrata API)
- **Use:** Crime reports aggregated to tract (safety signals)
- **Priority:** Medium

#### 🔴 Open Data KC (311 Service Calls)
- **Status:** Not Started
- **Implementation:** `data_pipeline/ingest/local.py::ingest_kc_311_data()` (stub exists)
- **Use:** Neighborhood disorder proxies (optional)
- **Priority:** Low

---

## 2. Data Processing & Normalization

### 🔴 Geography Normalization
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/normalize.py::normalize_geography()` (stub exists)
- **Tasks:**
  - Normalize GEOIDs to consistent vintage
  - Handle tract boundary changes over time

### 🔴 Tract-to-District Assignment
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/normalize.py::assign_tract_to_district()` (stub exists)
- **Tasks:**
  - Spatial overlay of tract centroids/polygons to district boundaries
  - Handle tracts that span multiple districts

---

## 3. Data Joining

### 🔴 GEOID-based Joins
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/join.py::join_on_geoid()` (stub exists)
- **Tasks:**
  - Join ACS + TIGER + health + housing + local data on GEOID
  - Handle missing data gracefully

### 🔴 NCES ID Joins
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/join.py::join_on_nces_id()` (stub exists)
- **Tasks:**
  - Join state education data with district boundaries

### 🔴 IPEDS ID Joins
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/join.py::join_on_ipeds_id()` (stub exists)
- **Tasks:**
  - Join College Scorecard data with college metadata

---

## 4. Index Calculation

### 🔴 Opportunity Index
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/indices.py::calculate_opportunity_index()` (stub exists)
- **Components:**
  - Poverty rate (ACS)
  - Vehicle access (ACS)
  - Housing+transport cost pressure (HUD LAI)
  - Transit frequency (GTFS)
  - School district opportunity signal (state indicators)
  - Health risk environment (PLACES)

### 🔴 Transit Access Score
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/indices.py::calculate_transit_access_score()` (stub exists)
- **Components:**
  - Stops within radius
  - Service frequency
  - Transfer counts to job centers
  - Reliability penalties

### 🔴 Housing Stability Risk Score
- **Status:** Not Started
- **Implementation:** `data_pipeline/process/indices.py::calculate_housing_stability_risk()` (stub exists)
- **Components:**
  - Rent burden prevalence
  - Vacancy rate
  - Income volatility

---

## 5. Data Pack Export

### 🔴 Pack Builder
- **Status:** Not Started
- **Implementation:** `data_pipeline/export/pack_builder.py`
- **Tasks:**
  - Export tracts.parquet
  - Export districts.parquet
  - Export colleges.parquet
  - Export jobs.parquet
  - Export transit.parquet
  - Generate region.json metadata

---

## Completed Items Summary

✅ **TIGER/Line Shapefile Ingestion**
- Complete implementation with KC metro filtering
- Verified: 477 tracts loaded correctly

✅ **ACS Census Data Ingestion**
- Complete implementation with 49 variables
- Verified: 477 tracts, perfect GEOID alignment with TIGER
- Includes error handling, retry logic, MOE support

✅ **Pipeline Infrastructure**
- Config system with environment variables
- Logging setup
- Directory structure
- Basic pipeline orchestrator skeleton

✅ **Test Cleanup**
- Removed temporary test files after verification

---

## Next Steps Recommendations

Based on the GDD priorities and data dependencies, here's the recommended implementation order:

### Priority 1: Core Foundation (Required for MVP)
1. **NCES EDGE District Boundaries** (Education foundation)
   - Needed before education data ingestion
   - Required for tract-to-district assignment
   - **Estimated effort:** Medium

2. **Tract-to-District Assignment** (Processing)
   - Spatial overlay logic
   - Enables joining education data with tracts
   - **Estimated effort:** Medium

3. **State Education Data (MO DESE + KSDE)** (Education core)
   - Critical for education gameplay system
   - Join with districts via NCES ID
   - **Estimated effort:** High (scraping/API complexity)

### Priority 2: Transportation System (High Gameplay Impact)
4. **KCATA GTFS Ingestion**
   - Core for transportation system
   - Needed before Transit Access Score calculation
   - **Estimated effort:** Medium

5. **Transit Access Score Calculation**
   - Depends on GTFS data
   - High gameplay impact
   - **Estimated effort:** Medium-High

### Priority 3: Data Joining & Index Calculation
6. **GEOID-based Joining Logic**
   - Join all tract-level data
   - Foundation for Opportunity Index
   - **Estimated effort:** Low-Medium

7. **Opportunity Index Calculation**
   - Combines multiple data sources
   - Key gameplay metric
   - **Estimated effort:** Medium

### Priority 4: Additional Data Sources (Expand Capabilities)
8. **HUD Location Affordability Index**
   - Enhances housing system
   - Block group level (may need aggregation)

9. **College Scorecard**
   - Postsecondary choices
   - Lower priority than K-12 education

10. **BLS Labor Market Data**
    - Time-series context
    - Important for economic shocks

11. **Local KC Data (Crime, 311)**
    - Immersion and safety system
    - Requires Socrata API integration

### Priority 5: Export & Polish
12. **Data Pack Export**
    - Package everything for game runtime
    - Versioning and metadata

---

## Implementation Notes

### Completed Plans
- ✅ ACS Census Data Ingestion plan (all todos complete)

### Active Plans
- None currently

### Blockers/Considerations
- None currently blocking progress

### Dependencies
- Education data → Requires NCES boundaries first
- Transit Access Score → Requires GTFS data first
- Opportunity Index → Requires multiple data sources joined
- Most processing → Requires ingestion complete first

---

## Testing Status

| Component | Tested | Notes |
|-----------|--------|-------|
| TIGER Ingestion | ✅ | Verified 477 tracts |
| ACS Ingestion | ✅ | Verified 477 tracts, 49 variables |
| GEOID Alignment | ✅ | Perfect match (477/477) |
| Pipeline Integration | 🟡 | Basic structure works, processing not tested |

---

*This document should be updated as implementation progresses.*

