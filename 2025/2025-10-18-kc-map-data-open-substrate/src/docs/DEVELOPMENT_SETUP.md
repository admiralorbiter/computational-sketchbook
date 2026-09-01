# Kansas City Data Platform - Development Setup

## 🚀 **Quick Start Guide**

### Prerequisites

- **Python 3.9+** (recommended: 3.11)
- **Git** for version control
- **VS Code** or preferred IDE
- **PostgreSQL 13+** (for production database)
- **Redis** (for caching, optional for development)

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd map-data

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file in project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///data/processed/kc_data.gpkg
# For PostgreSQL: postgresql://user:password@localhost:5432/kc_data

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# KC Open Data API
KC_DATA_API_KEY=your-api-key-here

# Geocoding Services
GEOCODING_PROVIDER=us_census
GOOGLE_MAPS_API_KEY=your-google-api-key

# Caching
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 3. Database Setup

#### Option A: SQLite/GeoPackage (Development)
```bash
# Create data directories
mkdir -p data/processed data/raw data/exports

# The GeoPackage will be created automatically when you run the app
```

#### Option B: PostgreSQL (Production)
```bash
# Install PostgreSQL
# Create database
createdb kc_data

# Run migrations
python tools/database/migrate.py
```

### 4. Development Server

```bash
# Start Flask development server
cd web
python app.py

# Or use Flask CLI
flask run --host=0.0.0.0 --port=5000
```

### 5. Data Ingestion

```bash
# Run ETL pipeline for KC Open Data
python tools/etl/kc_data_ingest.py

# Or run specific data sources
python tools/etl/crime_data_ingest.py
python tools/etl/service_requests_ingest.py
```

## 🛠️ **Development Tools**

### Code Quality

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 web/
black web/
isort web/

# Run type checking
mypy web/

# Run tests
pytest tests/
```

### Database Management

```bash
# Create new migration
python tools/database/create_migration.py "Add crime incidents table"

# Apply migrations
python tools/database/migrate.py

# Rollback migration
python tools/database/rollback.py

# Seed database
python tools/database/seed.py
```

### API Testing

```bash
# Start development server
python web/app.py

# Test API endpoints
curl http://localhost:5000/api/v1/crime?bbox=39.0,-94.6,39.1,-94.5

# Run API tests
pytest tests/api/
```

## 📁 **Project Structure**

```
map-data/
├── data/                    # Data storage
│   ├── processed/          # Processed GeoPackage files
│   ├── raw/               # Raw data files
│   └── exports/           # Exported data
├── docs/                   # Documentation
├── tools/                  # Development tools
│   ├── database/          # Database scripts
│   ├── etl/              # ETL pipelines
│   └── analysis/         # Analysis tools
├── web/                   # Flask application
│   ├── models/           # SQLAlchemy models
│   ├── services/         # Business logic
│   ├── api/              # API routes
│   ├── static/           # Frontend assets
│   └── templates/        # HTML templates
├── tests/                 # Test suite
├── logs/                  # Log files
└── venv/                  # Virtual environment
```

## 🔧 **Development Workflow**

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/crime-data-integration

# Make changes
# Test changes
pytest tests/

# Commit changes
git add .
git commit -m "feat: add crime data integration"

# Push and create PR
git push origin feature/crime-data-integration
```

### 2. Database Changes

```bash
# Create migration
python tools/database/create_migration.py "Add new table"

# Edit migration file
# Apply migration
python tools/database/migrate.py

# Test migration
pytest tests/database/
```

### 3. API Development

```bash
# Add new endpoint
# Test endpoint
curl http://localhost:5000/api/v1/new-endpoint

# Update API documentation
# Run API tests
pytest tests/api/
```

## 🐛 **Debugging**

### Flask Debug Mode

```bash
# Enable debug mode
export FLASK_DEBUG=1
python web/app.py
```

### Database Debugging

```bash
# Connect to database
sqlite3 data/processed/kc_data.gpkg

# Or for PostgreSQL
psql kc_data
```

### Logging

```bash
# View logs
tail -f logs/app.log

# Debug specific module
export LOG_LEVEL=DEBUG
python web/app.py
```

## 🚀 **Deployment**

### Development Deployment

```bash
# Build for development
python tools/build.py --env=development

# Deploy to development server
python tools/deploy.py --env=development
```

### Production Deployment

```bash
# Build for production
python tools/build.py --env=production

# Deploy to production
python tools/deploy.py --env=production
```

## 📊 **Monitoring**

### Health Checks

```bash
# Check API health
curl http://localhost:5000/health

# Check database connectivity
curl http://localhost:5000/health/database

# Check data freshness
curl http://localhost:5000/health/data
```

### Performance Monitoring

```bash
# Monitor API performance
curl http://localhost:5000/metrics

# Database performance
python tools/analysis/performance_analysis.py
```

## 🔒 **Security**

### Environment Security

```bash
# Secure environment variables
chmod 600 .env

# Use secrets management
python tools/security/setup_secrets.py
```

### API Security

```bash
# Enable rate limiting
export RATE_LIMIT_ENABLED=true

# Enable CORS
export CORS_ENABLED=true
```

## 📚 **Additional Resources**

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [GeoAlchemy2 Documentation](https://geoalchemy-2.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenStreetMap Data](https://wiki.openstreetmap.org/wiki/Downloading_data)

## 🆘 **Troubleshooting**

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env
   - Ensure database is running
   - Verify credentials

2. **Import Errors**
   - Activate virtual environment
   - Install missing dependencies
   - Check Python path

3. **API Errors**
   - Check Flask debug mode
   - Verify endpoint URLs
   - Check request parameters

4. **Data Issues**
   - Verify data file paths
   - Check data format
   - Run data validation

### Getting Help

- Check logs in `logs/app.log`
- Run tests: `pytest tests/`
- Check API documentation: `http://localhost:5000/docs`
- Review error messages in browser console
