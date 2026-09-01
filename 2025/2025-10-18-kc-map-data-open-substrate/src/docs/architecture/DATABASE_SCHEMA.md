# Database Schema Design - Kansas City Data Platform

## Overview

This document defines the database schema for the Kansas City Data Platform, which combines OpenStreetMap data with Kansas City Open Data sources in a unified SQLite/GeoPackage database.

## Database Structure

### File Organization
- **Primary Database**: `data/processed/kc_data.gpkg`
- **Backup Database**: `data/processed/kc_data_backup.gpkg`
- **Schema Version**: 1.0

## Table Definitions

### 1. OSM Data Tables (Existing Structure)

#### points
```sql
CREATE TABLE points (
    fid INTEGER PRIMARY KEY AUTOINCREMENT,
    osm_id INTEGER NOT NULL,
    name TEXT,
    barrier TEXT,
    highway TEXT,
    ref TEXT,
    address TEXT,
    is_in TEXT,
    place TEXT,
    man_made TEXT,
    other_tags TEXT,
    geom POINT
);

CREATE INDEX idx_points_osm_id ON points(osm_id);
CREATE INDEX idx_points_geom ON points USING rtree(geom);
```

#### lines
```sql
CREATE TABLE lines (
    fid INTEGER PRIMARY KEY AUTOINCREMENT,
    osm_id INTEGER NOT NULL,
    name TEXT,
    barrier TEXT,
    highway TEXT,
    waterway TEXT,
    aerialway TEXT,
    man_made TEXT,
    railway TEXT,
    z_order INTEGER,
    other_tags TEXT,
    geom LINESTRING
);

CREATE INDEX idx_lines_osm_id ON lines(osm_id);
CREATE INDEX idx_lines_geom ON lines USING rtree(geom);
CREATE INDEX idx_lines_highway ON lines(highway);
```

#### multipolygons
```sql
CREATE TABLE multipolygons (
    fid INTEGER PRIMARY KEY AUTOINCREMENT,
    osm_id INTEGER,
    osm_way_id INTEGER,
    name TEXT,
    type TEXT,
    aeroway TEXT,
    amenity TEXT,
    admin_level INTEGER,
    barrier TEXT,
    boundary TEXT,
    building TEXT,
    craft TEXT,
    geological TEXT,
    historic TEXT,
    land_area TEXT,
    landuse TEXT,
    leisure TEXT,
    man_made TEXT,
    military TEXT,
    natural TEXT,
    office TEXT,
    place TEXT,
    shop TEXT,
    sport TEXT,
    tourism TEXT,
    other_tags TEXT,
    geom MULTIPOLYGON
);

CREATE INDEX idx_multipolygons_osm_id ON multipolygons(osm_id);
CREATE INDEX idx_multipolygons_geom ON multipolygons USING rtree(geom);
CREATE INDEX idx_multipolygons_building ON multipolygons(building);
CREATE INDEX idx_multipolygons_amenity ON multipolygons(amenity);
```

### 2. Kansas City Open Data Tables

#### crime_incidents
```sql
CREATE TABLE crime_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT UNIQUE NOT NULL,
    report_date DATE NOT NULL,
    report_time TIME,
    offense_code TEXT,
    offense_description TEXT,
    offense_category TEXT,
    offense_type TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    district TEXT,
    beat TEXT,
    sector TEXT,
    latitude REAL,
    longitude REAL,
    geom POINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crime_case_id ON crime_incidents(case_id);
CREATE INDEX idx_crime_date ON crime_incidents(report_date);
CREATE INDEX idx_crime_category ON crime_incidents(offense_category);
CREATE INDEX idx_crime_district ON crime_incidents(district);
CREATE INDEX idx_crime_geom ON crime_incidents USING rtree(geom);
```

#### service_requests_311
```sql
CREATE TABLE service_requests_311 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT UNIQUE NOT NULL,
    request_type TEXT NOT NULL,
    request_category TEXT,
    request_subcategory TEXT,
    status TEXT NOT NULL,
    priority TEXT,
    department TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    latitude REAL,
    longitude REAL,
    geom POINT,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP,
    closed_date TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_311_request_id ON service_requests_311(request_id);
CREATE INDEX idx_311_type ON service_requests_311(request_type);
CREATE INDEX idx_311_status ON service_requests_311(status);
CREATE INDEX idx_311_department ON service_requests_311(department);
CREATE INDEX idx_311_created_date ON service_requests_311(created_date);
CREATE INDEX idx_311_geom ON service_requests_311 USING rtree(geom);
```

#### business_licenses
```sql
CREATE TABLE business_licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_number TEXT UNIQUE NOT NULL,
    business_name TEXT NOT NULL,
    dba_name TEXT,
    license_type TEXT NOT NULL,
    license_category TEXT,
    status TEXT NOT NULL,
    issue_date DATE,
    expiry_date DATE,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    latitude REAL,
    longitude REAL,
    geom POINT,
    phone TEXT,
    email TEXT,
    website TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_business_license_number ON business_licenses(license_number);
CREATE INDEX idx_business_name ON business_licenses(business_name);
CREATE INDEX idx_business_type ON business_licenses(license_type);
CREATE INDEX idx_business_status ON business_licenses(status);
CREATE INDEX idx_business_geom ON business_licenses USING rtree(geom);
```

#### food_inspections
```sql
CREATE TABLE food_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id TEXT UNIQUE NOT NULL,
    establishment_name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    latitude REAL,
    longitude REAL,
    geom POINT,
    inspection_date DATE NOT NULL,
    inspection_type TEXT,
    score INTEGER,
    grade TEXT,
    violations TEXT, -- JSON string of violations
    critical_violations INTEGER,
    non_critical_violations INTEGER,
    inspector_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inspection_id ON food_inspections(inspection_id);
CREATE INDEX idx_inspection_establishment ON food_inspections(establishment_name);
CREATE INDEX idx_inspection_date ON food_inspections(inspection_date);
CREATE INDEX idx_inspection_score ON food_inspections(score);
CREATE INDEX idx_inspection_geom ON food_inspections USING rtree(geom);
```

#### economic_indicators
```sql
CREATE TABLE economic_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    census_tract TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL,
    unit TEXT,
    date_period TEXT,
    year INTEGER,
    quarter INTEGER,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_economic_census_tract ON economic_indicators(census_tract);
CREATE INDEX idx_economic_metric_type ON economic_indicators(metric_type);
CREATE INDEX idx_economic_year ON economic_indicators(year);
```

### 3. Spatial Linking Tables

#### spatial_units
```sql
CREATE TABLE spatial_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_type TEXT NOT NULL, -- 'neighborhood', 'census_tract', 'council_district'
    unit_id TEXT NOT NULL,
    unit_name TEXT,
    geom MULTIPOLYGON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_spatial_unit_type ON spatial_units(unit_type);
CREATE INDEX idx_spatial_unit_id ON spatial_units(unit_id);
CREATE INDEX idx_spatial_geom ON spatial_units USING rtree(geom);
```

#### location_index
```sql
CREATE TABLE location_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    normalized_address TEXT,
    latitude REAL,
    longitude REAL,
    geom POINT,
    geocoding_quality TEXT, -- 'high', 'medium', 'low'
    geocoding_source TEXT, -- 'census', 'google', 'manual'
    geocoding_confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_location_address ON location_index(address);
CREATE INDEX idx_location_normalized ON location_index(normalized_address);
CREATE INDEX idx_location_geom ON location_index USING rtree(geom);
```

### 4. Cross-Reference Tables

#### business_inspections_link
```sql
CREATE TABLE business_inspections_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_license_id INTEGER NOT NULL,
    inspection_id INTEGER NOT NULL,
    relationship_type TEXT DEFAULT 'same_establishment',
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_license_id) REFERENCES business_licenses(id),
    FOREIGN KEY (inspection_id) REFERENCES food_inspections(id)
);

CREATE INDEX idx_business_inspection_business ON business_inspections_link(business_license_id);
CREATE INDEX idx_business_inspection_inspection ON business_inspections_link(inspection_id);
```

#### incident_locations_osm
```sql
CREATE TABLE incident_locations_osm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    incident_type TEXT NOT NULL, -- 'crime', '311'
    osm_feature_id INTEGER NOT NULL,
    osm_feature_type TEXT NOT NULL, -- 'point', 'line', 'multipolygon'
    distance_meters REAL,
    relationship_type TEXT, -- 'nearest_road', 'within_building', 'near_poi'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES crime_incidents(id) OR 
    FOREIGN KEY (incident_id) REFERENCES service_requests_311(id)
);

CREATE INDEX idx_incident_osm_incident ON incident_locations_osm(incident_id);
CREATE INDEX idx_incident_osm_feature ON incident_locations_osm(osm_feature_id);
```

### 5. Data Quality Tables

#### data_sync_log
```sql
CREATE TABLE data_sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL,
    sync_type TEXT NOT NULL, -- 'full', 'incremental'
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    status TEXT NOT NULL, -- 'running', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_dataset ON data_sync_log(dataset_name);
CREATE INDEX idx_sync_start_time ON data_sync_log(start_time);
CREATE INDEX idx_sync_status ON data_sync_log(status);
```

#### data_quality_issues
```sql
CREATE TABLE data_quality_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL,
    record_id TEXT,
    issue_type TEXT NOT NULL, -- 'missing_geometry', 'invalid_address', 'duplicate'
    severity TEXT NOT NULL, -- 'low', 'medium', 'high'
    description TEXT NOT NULL,
    suggested_fix TEXT,
    status TEXT DEFAULT 'open', -- 'open', 'resolved', 'ignored'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_quality_dataset ON data_quality_issues(dataset_name);
CREATE INDEX idx_quality_type ON data_quality_issues(issue_type);
CREATE INDEX idx_quality_severity ON data_quality_issues(severity);
CREATE INDEX idx_quality_status ON data_quality_issues(status);
```

## Views for Common Queries

### crime_by_neighborhood
```sql
CREATE VIEW crime_by_neighborhood AS
SELECT 
    su.unit_name as neighborhood,
    su.unit_id,
    ci.offense_category,
    COUNT(*) as incident_count,
    MIN(ci.report_date) as first_incident,
    MAX(ci.report_date) as last_incident
FROM crime_incidents ci
JOIN spatial_units su ON ST_Within(ci.geom, su.geom)
WHERE su.unit_type = 'neighborhood'
GROUP BY su.unit_id, su.unit_name, ci.offense_category;
```

### business_inspection_summary
```sql
CREATE VIEW business_inspection_summary AS
SELECT 
    bl.business_name,
    bl.license_type,
    bl.address,
    bl.status as license_status,
    AVG(fi.score) as avg_inspection_score,
    COUNT(fi.id) as inspection_count,
    MAX(fi.inspection_date) as last_inspection,
    MIN(fi.inspection_date) as first_inspection
FROM business_licenses bl
LEFT JOIN business_inspections_link bil ON bl.id = bil.business_license_id
LEFT JOIN food_inspections fi ON bil.inspection_id = fi.id
GROUP BY bl.id, bl.business_name, bl.license_type, bl.address, bl.status;
```

### service_requests_by_type
```sql
CREATE VIEW service_requests_by_type AS
SELECT 
    request_type,
    request_category,
    status,
    COUNT(*) as request_count,
    AVG(julianday(closed_date) - julianday(created_date)) as avg_days_to_close,
    MIN(created_date) as first_request,
    MAX(created_date) as last_request
FROM service_requests_311
GROUP BY request_type, request_category, status;
```

## Indexing Strategy

### Spatial Indexes (R-tree)
All geometry columns have R-tree spatial indexes for efficient spatial queries:
- `points.geom`
- `lines.geom`
- `multipolygons.geom`
- `crime_incidents.geom`
- `service_requests_311.geom`
- `business_licenses.geom`
- `food_inspections.geom`
- `spatial_units.geom`
- `location_index.geom`

### B-tree Indexes
Standard indexes on frequently queried columns:
- Primary keys (automatic)
- Foreign keys
- Date columns
- Text columns used in WHERE clauses
- Status/enum columns

### Composite Indexes
For complex queries:
```sql
CREATE INDEX idx_crime_date_category ON crime_incidents(report_date, offense_category);
CREATE INDEX idx_311_type_status ON service_requests_311(request_type, status);
CREATE INDEX idx_business_type_status ON business_licenses(license_type, status);
```

## Data Types

### Spatial Types
- **POINT**: Individual locations (crime, 311, businesses)
- **LINESTRING**: Roads, waterways, boundaries
- **MULTIPOLYGON**: Areas, buildings, neighborhoods

### Standard Types
- **INTEGER**: IDs, counts, scores
- **REAL**: Coordinates, distances, measurements
- **TEXT**: Names, descriptions, addresses
- **DATE**: Date-only values
- **TIMESTAMP**: Date and time values
- **JSON**: Complex structured data (violations)

## Constraints

### Primary Keys
All tables have auto-incrementing integer primary keys.

### Foreign Keys
- `business_inspections_link` references business and inspection tables
- `incident_locations_osm` references incident tables

### Unique Constraints
- `crime_incidents.case_id`
- `service_requests_311.request_id`
- `business_licenses.license_number`
- `food_inspections.inspection_id`

### Check Constraints
```sql
-- Crime incidents
CHECK (latitude >= -90 AND latitude <= 90)
CHECK (longitude >= -180 AND longitude <= 180)

-- Food inspections
CHECK (score >= 0 AND score <= 100)
CHECK (critical_violations >= 0)
CHECK (non_critical_violations >= 0)

-- Economic indicators
CHECK (value >= 0)
CHECK (year >= 2000 AND year <= 2030)
```

## Triggers

### Update Timestamps
```sql
CREATE TRIGGER update_crime_updated_at 
    AFTER UPDATE ON crime_incidents
    FOR EACH ROW
    BEGIN
        UPDATE crime_incidents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
```

### Data Quality Validation
```sql
CREATE TRIGGER validate_crime_geometry
    AFTER INSERT ON crime_incidents
    FOR EACH ROW
    WHEN NEW.geom IS NULL AND (NEW.latitude IS NULL OR NEW.longitude IS NULL)
    BEGIN
        INSERT INTO data_quality_issues (dataset_name, record_id, issue_type, severity, description)
        VALUES ('crime_incidents', NEW.case_id, 'missing_geometry', 'high', 'No coordinates or geometry provided');
    END;
```

## Migration Strategy

### Version 1.0 to 1.1
- Add new columns to existing tables
- Create new tables for additional data sources
- Add new indexes
- Update views

### Backup Strategy
- Full database backup before any schema changes
- Test migrations on copy of production data
- Rollback plan for each migration

## Performance Considerations

### Query Optimization
- Use EXPLAIN QUERY PLAN to analyze slow queries
- Create indexes based on actual query patterns
- Use views for complex aggregations
- Limit result sets with appropriate WHERE clauses

### Maintenance
- Regular VACUUM to reclaim space
- ANALYZE to update statistics
- Monitor database file size
- Regular backup verification

## Security

### Access Control
- Read-only access for application
- Separate admin access for schema changes
- Regular security updates

### Data Protection
- Encrypt sensitive data at rest
- Secure backup storage
- Audit trail for data changes

This schema provides a solid foundation for the Kansas City Data Platform while maintaining simplicity and performance. The SQLite/GeoPackage approach eliminates database server complexity while providing all necessary spatial and relational capabilities.
