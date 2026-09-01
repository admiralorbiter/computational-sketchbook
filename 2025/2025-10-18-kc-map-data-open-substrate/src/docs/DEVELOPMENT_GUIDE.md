# Kansas City Data Platform - Development Guide

Complete guide for developers working on the KC Data Platform.

## Quick Start

```bash
# Start the application
python start_app.py

# Then visit
http://localhost:5000
```

## What Works Now

### OSM Data Viewer
- **Missouri OSM Data**: Interactive map with 3.1M+ features
- **Layer Support**: Points, Lines, and Polygons
- **Filtering**: Filter by highway, building, amenity, shop, tourism, etc.
- **Performance**: Spatial queries with bounding box filtering
- **Real-time**: Dynamic loading based on map viewport

### Kansas City Platform Architecture
- **Database Models**: Crime, 311 requests, businesses, inspections
- **API Endpoints**: Ready for KC data
- **Configuration**: Environment-based config system
- **Caching**: Flask-Caching for performance
- **Health Check**: `/health` endpoint for monitoring

### ACS Demographic Data
- **200+ variables** across 1,717 block groups
- **8 KC metro counties** coverage
- **Comprehensive analysis view** with 9 organized tabs
- **Choropleth visualization** for income, age, population

## Project Structure

```
map-data/
├── start_app.py              # Application entry point
├── .env                       # Environment configuration
├── web/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py
│   │   ├── crime.py
│   │   ├── service_requests.py
│   │   ├── businesses.py
│   │   ├── inspections.py
│   │   └── osm.py
│   ├── api/                   # API blueprints
│   │   ├── base.py
│   │   ├── crime.py
│   │   ├── service_requests.py
│   │   ├── businesses.py
│   │   ├── dangerous_buildings.py
│   │   ├── landbank.py
│   │   ├── osm.py
│   │   ├── census.py
│   │   ├── geocoding.py
│   │   └── combined.py
│   ├── services/              # Business logic layer
│   │   ├── data_service.py
│   │   ├── consolidation_service.py
│   │   ├── spatial_service.py
│   │   ├── filter_service.py
│   │   └── analysis_service.py
│   ├── static/                # Frontend assets
│   │   ├── app.js
│   │   ├── style.css
│   │   ├── analysis.js
│   │   └── analysis.css
│   └── templates/             # HTML templates
│       ├── index.html
│       └── analysis.html
├── data/
│   ├── raw/                   # Raw data files
│   │   └── missouri.osm.pbf
│   ├── processed/             # Processed databases
│   │   ├── kc_data.gpkg       # KC Open Data
│   │   ├── tiger_boundaries.gpkg  # Census boundaries + ACS data
│   │   └── missouri.gpkg      # OSM data
│   └── exports/               # Data exports
├── tools/
│   ├── conversion/            # OSM data conversion
│   ├── database/              # Database management
│   ├── etl/                   # ETL pipelines
│   └── geocoding/             # Geocoding service
├── docs/                      # Comprehensive documentation
│   ├── architecture/
│   ├── features/
│   ├── implementation/
│   ├── integration/
│   └── data/
└── tests/                      # Test suite
```

### Directory Overview

**`data/`** - Data Storage
- `raw/` - Original, unprocessed data files
- `processed/` - Converted GeoPackage files
- `exports/` - Data exports and outputs

**`web/`** - Flask Web Application
- `app.py` - Main application server
- `api/` - REST API endpoints
- `services/` - Business logic and data access
- `models/` - SQLAlchemy ORM models
- `static/` - Frontend JavaScript and CSS
- `templates/` - HTML templates

**`tools/`** - Utility Scripts
- `conversion/` - OSM data conversion tools
- `database/` - Database schema and migrations
- `etl/` - Data ETL pipelines
- `geocoding/` - Address geocoding service

**`docs/`** - Documentation
- Architecture, features, implementation guides
- Integration documentation for data sources
- API reference and standards

## Development Workflow

### 1. Start Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Start the app
python start_app.py
```

### 2. Run ETL Pipelines

```bash
# Load KC Open Data
python tools/etl/kc_data_ingest.py

# Load ACS demographic data
python tools/etl/load_acs_data.py

# Load Census boundaries
python tools/etl/load_tiger_boundaries.py
```

### 3. Test Features

- Visit `http://localhost:5000`
- Check API endpoints: `/api/layers`, `/api/stats`
- Test health check: `/health`
- Test analysis view: click on any block group

## Available Endpoints

### Map Interface
- `GET /` - Main map interface
- `GET /analysis` - Block group analysis view

### API Endpoints
- `GET /api/layers` - Available data layers
- `GET /api/crime` - Crime incidents
- `GET /api/service-requests` - 311 requests
- `GET /api/businesses` - Business licenses
- `GET /api/census/block_groups` - Census block groups with ACS data
- `GET /api/analysis/block_groups/<geoid>` - Block group analysis
- `GET /api/geocoding/geocode` - Geocode address
- `GET /health` - Health check

### Query Parameters
- `bbox` - Bounding box (minx,miny,maxx,maxy)
- `limit` - Maximum features to return
- `filter` - Filter by type

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///data/processed/kc_data.gpkg
CENSUS_DATABASE_PATH=data/processed/tiger_boundaries.gpkg
OSM_DATABASE_PATH=data/processed/missouri.gpkg

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# APIs
CENSUS_API_KEY=your-census-api-key
GOOGLE_MAPS_API_KEY=your-google-api-key

# Geocoding
GEOCODING_CACHE_ENABLED=true
CENSUS_DAILY_LIMIT=1000
GOOGLE_MONTHLY_LIMIT=40000
```

### Database Configuration
- **KC Data**: `kc_data.gpkg` with SQLAlchemy ORM
- **Census/ACS**: `tiger_boundaries.gpkg` with GeoPandas
- **OSM Data**: `missouri.gpkg` for geographic features

## Code Quality

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 web/

# Format code
black .

# Type checking
mypy web/

# Run tests
pytest tests/
```

## Next Steps

### Immediate (This Week)
1. **Test the app** - Ensure all features work correctly
2. **Load KC data** - Run ETL pipelines
3. **Geocoding** - Set up address-to-coordinate conversion

### Short Term (Next 2 Weeks)
1. **311 data integration** - Load and visualize service requests
2. **Enhanced UI** - Improve map interface
3. **Filtering system** - Advanced filtering across datasets

### Medium Term (Next Month)
1. **Business data** - License and inspection data
2. **Analytics dashboard** - Cross-dataset analysis
3. **Export features** - Data export and reporting

## Troubleshooting

### Common Issues

1. **Database file not found**
   - Run ETL pipelines in `tools/etl/`
   - Check database file paths in `.env`

2. **Module not found errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Activate virtual environment

3. **No data showing on map**
   - Check browser console for errors
   - Verify database files exist
   - Check API endpoints: `/api/layers`

4. **Performance issues**
   - Reduce `MAX_FEATURES_PER_REQUEST` in config
   - Enable caching in production
   - Check database indexes

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=True
python start_app.py
```

## Resources

- **Documentation**: See `docs/` directory
- **API Reference**: `docs/api/API_DOCUMENTATION.md`
- **Database Schema**: `docs/architecture/DATABASE_SCHEMA.md`
- **Development Standards**: `docs/standards/DEVELOPMENT_STANDARDS.md`
- **ACS Integration**: `docs/ACS_INTEGRATION.md`
- **Geocoding Guide**: `docs/integration/GEOCODING_GUIDE.md`

## Support

- **Issues**: Check logs in `logs/` directory
- **API Testing**: Use `/health` endpoint
- **Database**: Check `/api/stats` for layer information
