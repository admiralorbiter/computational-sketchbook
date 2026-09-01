# Next Steps Recommendations

*Generated:* 2025-01-XX  
*Current Status:* Foundation datasets (TIGER + ACS) complete

---

## Recommended Next Work Item

### 🎯 **NCES EDGE School District Boundaries Ingestion**

**Why this should be next:**
1. **Foundation dependency:** Required before implementing state education data (MO DESE, KSDE)
2. **Core gameplay system:** Education system is a major gameplay pillar
3. **Blocking other work:** Needed for tract-to-district assignment logic
4. **Clear scope:** Well-defined API/download source, straightforward implementation

**What needs to be implemented:**
- Function: `data_pipeline/ingest/education.py::ingest_nces_districts()`
- Download/load NCES EDGE district boundary shapefiles
- Filter to KC metro area (can use state/county filtering or spatial clipping)
- Extract relevant fields (NCES ID, district name, district type)
- Return GeoDataFrame with district boundaries

**Source:** https://nces.ed.gov/programs/edge/Geographic/DistrictBoundaries

**Estimated Effort:** Medium (2-4 hours)

**Dependencies:** None (can start immediately)

---

## Alternative: Transportation System Path

If you want to work on a different high-impact system, consider:

### 🚌 **KCATA GTFS Ingestion + Transit Access Score**

**Why this could be next:**
1. **Independent system:** Doesn't depend on other incomplete work
2. **High gameplay impact:** Transportation constraints are core to gameplay
3. **Clear data source:** GTFS is a standard format
4. **Self-contained:** Can build Transit Access Score immediately after ingestion

**What needs to be implemented:**
1. GTFS ingestion (`data_pipeline/ingest/transit.py::ingest_kcata_gtfs()`)
   - Download GTFS feed from KCATA
   - Parse stops, routes, trips, stop_times tables
   - Return dictionary of DataFrames

2. Transit Access Score (`data_pipeline/process/indices.py::calculate_transit_access_score()`)
   - Spatial join: stops within radius of tract centroids
   - Calculate service frequency from stop_times
   - Count transfers to major job centers
   - Combine into score

**Estimated Effort:** Medium-High (4-6 hours)

**License Note:** Review KCATA GTFS terms before implementation (noted in GDD)

---

## Implementation Strategy Recommendations

### Option A: Continue Education System (Recommended)
**Path:** NCES Boundaries → Tract-to-District Assignment → State Education Data

**Pros:**
- Builds on foundation work logically
- Education is core gameplay system
- Clear dependency chain
- Each step unlocks the next

**Timeline:** 
- Week 1: NCES boundaries + tract assignment
- Week 2: MO DESE + KSDE (may be complex)
- Week 3: Integration and testing

### Option B: Parallel Development
**Path:** NCES Boundaries (Education) + GTFS (Transportation) in parallel

**Pros:**
- Work on independent systems simultaneously
- Faster overall progress
- More variety in work

**Cons:**
- More context switching
- May need to coordinate later

### Option C: Complete Foundation First
**Path:** All ingestion → All processing → All joining → All indices → Export

**Pros:**
- Clear separation of concerns
- Test each stage completely before moving on

**Cons:**
- Delays end-to-end testing
- May discover integration issues late

---

## Quick Wins (Low Effort, High Value)

These can be done alongside larger work:

1. **GEOID-based Joining Logic** (1-2 hours)
   - Simple pandas merge logic
   - Useful immediately for ACS + TIGER
   - Can test with existing data

2. **Basic Geography Normalization** (2-3 hours)
   - GEOID validation
   - Handle tract boundary changes (if needed)
   - Ensures consistency

3. **Data Pack Export Skeleton** (2-3 hours)
   - Basic structure for exporting parquet files
   - Metadata JSON generation
   - Enables end-to-end testing with current data

---

## Questions to Consider

Before starting next work, consider:

1. **Data freshness:** How often should data packs be rebuilt?
   - This affects API caching strategies
   - Influences download vs. API decisions

2. **Testing approach:** Unit tests vs. integration tests?
   - Current approach: Manual verification (worked well for ACS)
   - May want to add automated tests as complexity grows

3. **Error handling:** How strict should validation be?
   - ACS implementation handles missing data gracefully
   - Apply similar patterns to new ingestion functions

4. **Data versioning:** How to handle different data years/vintages?
   - Currently using Config for year/vintage
   - May need more sophisticated versioning as sources diverge

---

## Blocked Work (Can't Start Yet)

These items are blocked and shouldn't be started until dependencies are complete:

- **State Education Data (MO DESE, KSDE)** → Needs NCES boundaries first
- **Transit Access Score** → Needs GTFS ingestion first
- **Opportunity Index** → Needs multiple data sources joined first
- **Housing Stability Risk Score** → Needs HUD LAI data first (if using that component)

---

## Recommended Immediate Action

**Start with:** NCES EDGE District Boundaries Ingestion

**Rationale:**
- Unblocks education system development
- Clear, achievable scope
- No external blockers
- Sets up next logical step (tract-to-district assignment)

**After completion, next step:** Implement tract-to-district spatial assignment logic (can use geopandas spatial joins with tract centroids or polygons).

