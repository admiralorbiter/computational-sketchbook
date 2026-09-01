# Kansas City Data Platform - Documentation

## Overview

The Kansas City Data Platform is a comprehensive data integration and visualization system that combines OpenStreetMap (OSM) data with Kansas City Open Data sources to create a powerful tool for data journalism and urban planning analysis.

## Documentation Structure

### Architecture Documents
- **[System Architecture](architecture/SYSTEM_ARCHITECTURE.md)** - Overall system design, database architecture, and performance strategy
- **[Database Schema](architecture/DATABASE_SCHEMA.md)** - Detailed database schema with table definitions and relationships

### Feature Specifications
- **[Core Features](features/CORE_FEATURES.md)** - Multi-layer visualization, search, analysis, and export capabilities
- **[UI/UX Specifications](features/UI_UX_SPECIFICATIONS.md)** - User interface design and user experience guidelines
- **[Analytics Features](features/ANALYTICS_FEATURES.md)** - Advanced analytics and insights capabilities

### Integration Documentation
- **[Data Sources](integration/DATA_SOURCES.md)** - Complete catalog of KC Open Data sources and API endpoints
- **[KC Open Data Integration](integration/KC_OPEN_DATA_INTEGRATION.md)** - Integration plan prioritizing crime and 311 data
- **[Geocoding Guide](integration/GEOCODING_GUIDE.md)** - Complete geocoding service implementation and testing guide
- **[Data Relationships](integration/DATA_RELATIONSHIPS.md)** - Mapping relationships between OSM and KC data sources

### Implementation Guides
- **[Development Roadmap](implementation/DEVELOPMENT_ROADMAP.md)** - 16-week phased development plan
- **[Technical Implementation](implementation/TECHNICAL_IMPLEMENTATION.md)** - Detailed backend, frontend, and database implementation
- **[Testing Strategy](implementation/TESTING_STRATEGY.md)** - Comprehensive testing approach

### Data Documentation
- **[Data Dictionary](data/DATA_DICTIONARY.md)** - Complete field definitions for all datasets
- **[ACS Block Group Inventory](data/ACS_BLOCK_GROUP_INVENTORY.md)** - Comprehensive ACS data tracking
- **[ACS Data Discovery](data/ACS_DATA_DISCOVERY_SUMMARY.md)** - Test results and availability at block group level
- **[ACS Tracking Guide](data/ACS_TRACKING_README.md)** - How to use priority-based import system
- **[Data Availability Notes](data/DATA_AVAILABILITY_NOTES.md)** - What's available at block group level

### Standards & Reference
- **[Development Standards](standards/DEVELOPMENT_STANDARDS.md)** - Code style, Git workflow, and security practices
- **[Development Guide](DEVELOPMENT_GUIDE.md)** - Complete developer setup and workflow
- **[API Documentation](api/API_DOCUMENTATION.md)** - REST API reference with examples

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite with SpatiaLite extensions
- Modern web browser

### Installation
```bash
# Clone the repository
git clone https://github.com/your-org/kc-data-platform.git
cd kc-data-platform

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python tools/database/init_db.py

# Start the application
cd web
python app.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
flake8 .

# Start development server
cd web
python app.py --debug
```

## Key Features

### Multi-Layer Data Visualization
- **OSM Data**: Buildings, roads, POIs with interactive styling
- **Crime Data**: Incident locations with temporal filtering
- **311 Requests**: Service request locations and status tracking
- **Business Data**: Licensed businesses with inspection scores
- **Food Inspections**: Health inspection data with scoring

### Advanced Search & Filtering
- **Spatial Filters**: Bounding box, radius, polygon selection
- **Temporal Filters**: Date ranges, time sliders, seasonal analysis
- **Attribute Filters**: Multi-criteria filtering across all datasets
- **Cross-Dataset Queries**: Find relationships between different data types

### Analytics & Insights
- **Proximity Analysis**: Find features within specified distances
- **Correlation Analysis**: Identify relationships between datasets
- **Trend Analysis**: Time series analysis and forecasting
- **Statistical Summaries**: Aggregated data by geographic units

### Data Export & Reporting
- **Multiple Formats**: CSV, GeoJSON, Excel, PDF
- **Custom Reports**: Generate analysis reports with maps
- **API Access**: Programmatic access to all data
- **Embeddable Visualizations**: Widgets for external websites

## Technology Stack

### Backend
- **Framework**: Flask 2.0+
- **Database**: SQLite with SpatiaLite extensions
- **ORM**: SQLAlchemy with GeoAlchemy2
- **Caching**: Flask-Caching
- **ETL**: Custom Python scripts

### Frontend
- **Map**: Leaflet.js 1.9+
- **UI**: Vanilla JavaScript (ES6+)
- **Styling**: CSS3 with responsive design
- **Icons**: Font Awesome Pro

### Data Sources
- **KC Open Data Portal**: Crime, 311, business, inspection data
- **OpenStreetMap**: Global geographic data
- **Geocoding**: US Census and Google Maps APIs

## Data Sources

### Priority 1 (Phase 1)
- **Crime Data**: ~100K records/year, daily updates
- **311 Service Requests**: ~300K records/year, real-time updates

### Priority 2 (Phase 2)
- **Business Licenses**: ~50K active licenses, weekly updates
- **Food Inspections**: ~20K inspections/year, daily updates

### Future Sources
- Economic indicators
- Property data
- Transportation data
- Real-time traffic

## API Endpoints

### Core Data APIs
- `GET /api/v1/crime` - Crime incident data
- `GET /api/v1/311` - 311 service requests
- `GET /api/v1/businesses` - Business license data
- `GET /api/v1/inspections` - Food inspection data
- `GET /api/v1/osm/{layer}` - OpenStreetMap data

### Analysis APIs
- `GET /api/v1/analysis/proximity` - Proximity analysis
- `GET /api/v1/analysis/correlation` - Correlation analysis
- `GET /api/v1/combined` - Multi-dataset queries

### Export APIs
- `POST /api/v1/export` - Data export requests
- `GET /api/v1/export/{id}` - Export status and download

## Development Phases

### Phase 1: Foundation (Weeks 1-4)
- Database setup and schema creation
- ETL pipelines for crime and 311 data
- Basic API endpoints
- Core frontend architecture

### Phase 2: Core Features (Weeks 5-10)
- Multi-layer visualization
- Advanced filtering system
- Temporal analysis
- Search and discovery

### Phase 3: Analytics (Weeks 11-14)
- Cross-dataset analysis
- Business data integration
- Reporting system
- Data export functionality

### Phase 4: Polish & Launch (Weeks 15-16)
- Testing and quality assurance
- Performance optimization
- Documentation completion
- Public launch

## Performance Targets

- **API Response Time**: <1 second for 90% of requests
- **Map Rendering**: <2 seconds for initial load
- **Concurrent Users**: Support 100+ simultaneous users
- **Data Coverage**: 5+ major KC data sources integrated

## Contributing

### Development Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Write tests for new features
- Document all public APIs

### Git Workflow
- Use feature branches
- Write descriptive commit messages
- Submit pull requests for review
- Ensure all tests pass

### Code Review
- All PRs require approval
- Test coverage must be >90%
- Documentation must be updated
- Performance impact must be considered

## Support

### Documentation
- **API Reference**: [API Documentation](api/API_DOCUMENTATION.md)
- **Data Dictionary**: [Data Dictionary](data/DATA_DICTIONARY.md)
- **Development Guide**: [Technical Implementation](implementation/TECHNICAL_IMPLEMENTATION.md)

### Getting Help
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@kc-data-platform.example.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Kansas City Open Data Portal** for providing public datasets
- **OpenStreetMap contributors** for global geographic data
- **Flask and SQLAlchemy communities** for excellent Python frameworks
- **Leaflet.js team** for the mapping library

---

*This documentation is maintained as part of the Kansas City Data Platform project. For the most up-to-date information, please refer to the individual documentation files.*
