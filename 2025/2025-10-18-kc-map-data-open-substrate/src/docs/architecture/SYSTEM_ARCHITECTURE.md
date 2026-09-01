# System Architecture - Kansas City Data Platform

## Overview

The Kansas City Data Platform is a comprehensive data integration and visualization system that combines OpenStreetMap (OSM) data with Kansas City Open Data sources to create a powerful tool for data journalism and urban planning analysis.

## Architecture Principles

- **Simplicity First**: Use proven, maintainable technologies
- **Performance**: Optimize for sub-second query responses
- **Scalability**: Design for growth without over-engineering
- **Reliability**: Robust error handling and data validation
- **Extensibility**: Easy to add new data sources and features

## System Components

### 1. Database Layer

#### Primary Database: SQLite/GeoPackage
- **File**: `data/processed/kc_data.gpkg`
- **Type**: SQLite with SpatiaLite extensions
- **Purpose**: Unified storage for all spatial and non-spatial data
- **Advantages**:
  - Zero configuration - file-based
  - No separate database server to manage
  - Built-in spatial support (R-tree indexes)
  - Easy backup and version control
  - Works well up to 1M+ records with proper indexing

#### Database Structure
```
kc_data.gpkg
├── OSM Data (existing structure)
│   ├── points
│   ├── lines
│   ├── multipolygons
│   ├── multilinestrings
│   └── other_relations
├── KC Open Data
│   ├── crime_incidents
│   ├── service_requests_311
│   ├── business_licenses
│   ├── food_inspections
│   └── economic_indicators
├── Spatial Linking
│   ├── spatial_units
│   ├── location_index
│   └── cross_references
└── Views & Indexes
    ├── crime_by_neighborhood
    ├── business_inspection_summary
    └── spatial_indexes
```

#### ORM Layer: SQLAlchemy + GeoAlchemy2
- **Location**: `web/models/`
- **Purpose**: Clean abstraction over raw SQL
- **Benefits**:
  - Type-safe queries
  - Easy migrations
  - Database-agnostic (can switch to PostgreSQL later)
  - Automatic relationship handling

### 2. Data Integration Layer

#### ETL Pipeline
- **Location**: `tools/etl/`
- **Components**:
  - `kc_data_ingest.py` - Main orchestrator
  - `soda_client.py` - KC Open Data API client
  - `geocoding.py` - Address geocoding utilities
  - `data_validation.py` - Data quality checks

#### Data Sources Integration
- **KC Open Data Portal**: SODA API endpoints
- **Geocoding**: US Census Geocoder (primary), Google Maps (fallback)
- **Update Strategy**: Incremental updates with timestamp tracking
- **Error Handling**: Retry logic, dead letter queues, monitoring

### 3. API Layer

#### RESTful API Design
- **Framework**: Flask with blueprints
- **Location**: `web/api/`
- **Structure**:
  ```
  /api/v1/
  ├── crime/           # Crime incidents
  ├── 311/             # Service requests
  ├── osm/             # OSM data (existing)
  ├── combined/        # Multi-dataset queries
  └── settings/        # User preferences & consolidation settings
  ```

#### Service Layer Architecture
- **Location**: `web/services/`
- **Components**:
  ```
  services/
  ├── data_service.py      # Database access & queries
  ├── consolidation_service.py  # Feature consolidation logic
  ├── spatial_service.py   # Spatial operations
  └── filter_service.py    # Filter management
  ```

#### Blueprint Structure
- **Base Blueprint**: `web/api/base.py` - Common functionality
- **Individual APIs**: Each data source has its own blueprint
- **Legacy Support**: Backward-compatible endpoints maintained

#### Query Capabilities
- **Spatial Filtering**: Bounding box, radius, polygon
- **Temporal Filtering**: Date ranges, time periods
- **Attribute Filtering**: Any field with operators (=, >, <, LIKE, IN)
- **Combined Queries**: Multiple datasets with spatial joins
- **Aggregations**: Count, sum, average by geographic unit

#### Response Format
- **Standard**: GeoJSON for spatial data, JSON for tabular
- **Pagination**: Limit/offset with total count
- **Metadata**: Query execution time, result count, data source info

### 4. Caching Strategy

#### Application-Level Caching
- **Framework**: Flask-Caching
- **Backend**: Simple memory cache (dev), file cache (production)
- **TTL**: 5 minutes for spatial queries, 1 hour for static data
- **Keys**: Based on query parameters and data version

#### Cache Invalidation
- **Time-based**: Automatic expiration
- **Data-driven**: Invalidate when source data updates
- **Manual**: Admin interface for cache clearing

### 5. Frontend Architecture

#### Current Stack (Enhanced)
- **Map**: Leaflet.js with custom markers
- **UI**: Vanilla JavaScript with modular components
- **Styling**: CSS3 with responsive design
- **Data**: REST API consumption

#### New Features (Post-Refactor)
- **Settings UI**: Consolidation presets (Aggressive, Balanced, Loose, Custom)
- **Filter System**: Simplified filtering (311 issue types, Crime offense types)
- **Cross-Layer Consolidation**: Proximity-based feature grouping
- **Real-time Updates**: Settings changes apply immediately

#### Performance Optimizations
- **Lazy Loading**: Load features on map viewport change
- **Feature Limiting**: Max 2000 features per view
- **Progressive Enhancement**: Load detail on zoom
- **Caching**: Browser cache for static assets
- **Consolidation**: Reduce marker count through intelligent grouping

### 6. Performance Strategy

#### Database Optimization
- **Spatial Indexes**: R-tree on all geometry columns
- **B-tree Indexes**: On foreign keys and filter columns
- **Query Analysis**: EXPLAIN QUERY PLAN for optimization
- **Views**: Pre-computed aggregations for common queries

#### Application Optimization
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: N+1 query prevention
- **Response Compression**: Gzip compression
- **Static Assets**: Minification and CDN (future)

#### Monitoring
- **Query Performance**: Log slow queries (>1s)
- **Memory Usage**: Monitor SQLite cache size
- **API Response Times**: Track endpoint performance
- **Error Rates**: Log and alert on failures

## Data Flow

### 1. Data Ingestion
```
KC Open Data Portal → ETL Pipeline → Validation → Geocoding → Database
```

### 2. API Request
```
Client Request → Flask App → SQLAlchemy ORM → SQLite → Response Cache → Client
```

### 3. Map Rendering
```
Map Viewport → API Query → Spatial Filter → Feature Limit → GeoJSON → Leaflet
```

## Security Considerations

### Data Access
- **Public Data**: All KC Open Data is public
- **API Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize all query parameters
- **SQL Injection**: Prevented by SQLAlchemy ORM

### Infrastructure
- **File Permissions**: Secure database file access
- **Backup Strategy**: Regular automated backups
- **Version Control**: Track data changes

## Scalability Path

### Current (SQLite)
- **Capacity**: 1M+ records
- **Concurrency**: Single writer, multiple readers
- **Performance**: Sub-second queries with proper indexing

### Future (PostgreSQL)
- **Migration**: Change connection string in SQLAlchemy
- **Benefits**: Concurrent writes, advanced spatial functions
- **When**: When hitting SQLite limitations

### Horizontal Scaling
- **Load Balancer**: Multiple Flask instances
- **Database Replicas**: Read-only copies
- **CDN**: Static asset distribution

## Technology Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask 2.0+
- **ORM**: SQLAlchemy 1.4+ with GeoAlchemy2
- **Database**: SQLite with SpatiaLite
- **Caching**: Flask-Caching
- **HTTP Client**: Requests

### Frontend
- **Map**: Leaflet.js 1.9+
- **UI**: Vanilla JavaScript (ES6+)
- **Styling**: CSS3
- **Icons**: Font Awesome Pro

### Development
- **Version Control**: Git
- **Testing**: pytest
- **Code Quality**: flake8, black
- **Documentation**: Markdown

## Deployment Architecture

### Development
- **Local**: SQLite file + Flask dev server
- **Database**: Single `.gpkg` file
- **Caching**: Memory-based

### Production
- **Server**: Single server with file-based database
- **Database**: SQLite with WAL mode
- **Caching**: File-based cache
- **Monitoring**: Basic logging

### Future Production
- **Load Balancer**: Nginx
- **Application**: Multiple Flask workers
- **Database**: PostgreSQL with read replicas
- **Caching**: Redis
- **Monitoring**: Prometheus + Grafana

## Error Handling

### Database Errors
- **Connection Issues**: Retry with exponential backoff
- **Query Errors**: Log and return user-friendly message
- **Data Corruption**: Restore from backup

### API Errors
- **Validation**: Return 400 with error details
- **Not Found**: Return 404 with helpful message
- **Server Error**: Return 500 with request ID for tracking

### Data Quality
- **Missing Data**: Log warnings, continue processing
- **Invalid Data**: Skip with error logging
- **Geocoding Failures**: Flag for manual review

## Monitoring & Alerting

### Key Metrics
- **API Response Time**: <1s for 90% of requests
- **Database Query Time**: <500ms for 95% of queries
- **Error Rate**: <1% of requests
- **Data Freshness**: Alert if data >24h old

### Logging
- **Application Logs**: Flask logging
- **Query Logs**: Slow query detection
- **Error Logs**: Exception tracking
- **Access Logs**: API usage patterns

## Backup & Recovery

### Database Backup
- **Frequency**: Daily automated backup
- **Retention**: 30 days of backups
- **Location**: Separate storage location
- **Testing**: Monthly restore tests

### Data Recovery
- **Point-in-time**: Not available with SQLite
- **Full Restore**: Replace database file
- **Partial Restore**: Re-run ETL for specific datasets

## Future Enhancements

### Phase 2
- **Real-time Updates**: WebSocket for live data
- **Advanced Analytics**: Machine learning integration
- **Mobile App**: React Native application

### Phase 3
- **Microservices**: Split into specialized services
- **Event Streaming**: Apache Kafka for real-time data
- **Advanced Visualization**: D3.js integration

## Conclusion

This architecture prioritizes simplicity and maintainability while providing a solid foundation for growth. The SQLite/GeoPackage approach eliminates database server complexity while SQLAlchemy provides a clean migration path to PostgreSQL when needed. The REST API design is straightforward and extensible, supporting both simple queries and complex multi-dataset analysis.
