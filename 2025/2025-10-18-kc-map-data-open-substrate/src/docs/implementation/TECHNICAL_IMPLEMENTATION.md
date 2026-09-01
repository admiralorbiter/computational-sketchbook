# Technical Implementation - Kansas City Data Platform

## Overview

This document provides detailed technical implementation guidance for the Kansas City Data Platform, covering backend architecture, frontend development, database operations, and deployment strategies.

## Backend Implementation

### Flask Application Structure

#### Project Organization
```
web/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── models/               # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py          # Base model class
│   ├── osm.py           # OSM data models
│   ├── crime.py         # Crime data models
│   ├── service_requests.py  # 311 data models
│   ├── business.py      # Business data models
│   └── inspection.py    # Inspection data models
├── api/                 # API route handlers
│   ├── __init__.py
│   ├── crime.py         # Crime API endpoints
│   ├── service_requests.py  # 311 API endpoints
│   ├── business.py      # Business API endpoints
│   ├── inspection.py    # Inspection API endpoints
│   ├── osm.py           # OSM API endpoints
│   └── combined.py      # Multi-dataset endpoints
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── data_service.py  # Data access service
│   ├── analysis_service.py  # Analysis operations
│   ├── geocoding_service.py  # Geocoding operations
│   └── export_service.py  # Export operations
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── database.py      # Database utilities
│   ├── spatial.py       # Spatial operations
│   └── validation.py    # Data validation
└── static/              # Static assets (existing)
    ├── app.js
    └── style.css
```

#### Main Application (app.py)
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    
    # Register blueprints
    from api.crime import bp as crime_bp
    from api.service_requests import bp as service_requests_bp
    from api.business import bp as business_bp
    from api.inspection import bp as inspection_bp
    from api.osm import bp as osm_bp
    from api.combined import bp as combined_bp
    
    app.register_blueprint(crime_bp, url_prefix='/api/v1/crime')
    app.register_blueprint(service_requests_bp, url_prefix='/api/v1/311')
    app.register_blueprint(business_bp, url_prefix='/api/v1/businesses')
    app.register_blueprint(inspection_bp, url_prefix='/api/v1/inspections')
    app.register_blueprint(osm_bp, url_prefix='/api/v1/osm')
    app.register_blueprint(combined_bp, url_prefix='/api/v1/combined')
    
    return app

# Initialize extensions
db = SQLAlchemy()
cache = Cache()
```

#### Configuration Management (config.py)
```python
import os
from pathlib import Path

class Config:
    # Database configuration
    DATABASE_PATH = os.path.join(
        Path(__file__).parent.parent, 
        'data', 'processed', 'kc_data.gpkg'
    )
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache configuration
    CACHE_TYPE = 'simple'  # Use 'filesystem' for production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # API configuration
    MAX_FEATURES_PER_REQUEST = 5000
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    # Geocoding configuration
    CENSUS_GEOCODER_URL = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress'
    GOOGLE_GEOCODER_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # KC Open Data configuration
    KC_OPEN_DATA_BASE_URL = 'https://data.kcmo.org/resource/'
    KC_OPEN_DATA_APP_TOKEN = os.environ.get('KC_OPEN_DATA_TOKEN')
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
```

### SQLAlchemy ORM Models

#### Base Model (models/base.py)
```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), 
                       onupdate=func.current_timestamp())
```

#### Crime Model (models/crime.py)
```python
from sqlalchemy import Column, String, Date, Time, Float, Text
from geoalchemy2 import Geometry
from .base import BaseModel

class CrimeIncident(BaseModel):
    __tablename__ = 'crime_incidents'
    
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)
    report_time = Column(Time)
    offense_code = Column(String(20))
    offense_description = Column(Text)
    offense_category = Column(String(100), index=True)
    offense_type = Column(String(100))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(10))
    zip_code = Column(String(10))
    district = Column(String(50), index=True)
    beat = Column(String(50))
    sector = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry('POINT', srid=4326), index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'report_time': self.report_time.isoformat() if self.report_time else None,
            'offense_code': self.offense_code,
            'offense_description': self.offense_description,
            'offense_category': self.offense_category,
            'offense_type': self.offense_type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'district': self.district,
            'beat': self.beat,
            'sector': self.sector,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
```

#### Service Request Model (models/service_requests.py)
```python
from sqlalchemy import Column, String, DateTime, Text, Float
from geoalchemy2 import Geometry
from .base import BaseModel

class ServiceRequest311(BaseModel):
    __tablename__ = 'service_requests_311'
    
    request_id = Column(String(50), unique=True, nullable=False, index=True)
    request_type = Column(String(100), nullable=False, index=True)
    request_category = Column(String(100))
    request_subcategory = Column(String(100))
    status = Column(String(50), nullable=False, index=True)
    priority = Column(String(50))
    department = Column(String(100), index=True)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(10))
    zip_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry('POINT', srid=4326), index=True)
    created_date = Column(DateTime, nullable=False, index=True)
    updated_date = Column(DateTime)
    closed_date = Column(DateTime)
    resolution_notes = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'request_type': self.request_type,
            'request_category': self.request_category,
            'request_subcategory': self.request_subcategory,
            'status': self.status,
            'priority': self.priority,
            'department': self.department,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None,
            'resolution_notes': self.resolution_notes
        }
```

### API Implementation

#### Crime API (api/crime.py)
```python
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_
from geoalchemy2.functions import ST_Within, ST_DWithin
from models.crime import CrimeIncident
from services.data_service import DataService
from utils.spatial import parse_bbox, parse_radius
from utils.validation import validate_date_range

bp = Blueprint('crime', __name__)

@bp.route('/', methods=['GET'])
def get_crime_incidents():
    """Get crime incidents with filtering and pagination"""
    try:
        # Parse query parameters
        bbox = request.args.get('bbox')
        radius = request.args.get('radius')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        offense_category = request.args.get('offense_category')
        district = request.args.get('district')
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = CrimeIncident.query
        
        # Spatial filtering
        if bbox:
            minx, miny, maxx, maxy = parse_bbox(bbox)
            query = query.filter(
                and_(
                    CrimeIncident.longitude >= minx,
                    CrimeIncident.longitude <= maxx,
                    CrimeIncident.latitude >= miny,
                    CrimeIncident.latitude <= maxy
                )
            )
        elif radius and lat and lng:
            center_lat, center_lng = float(lat), float(lng)
            radius_meters = parse_radius(radius)
            query = query.filter(
                ST_DWithin(
                    CrimeIncident.geom,
                    f'POINT({center_lng} {center_lat})',
                    radius_meters
                )
            )
        
        # Attribute filtering
        if date_from:
            query = query.filter(CrimeIncident.report_date >= date_from)
        if date_to:
            query = query.filter(CrimeIncident.report_date <= date_to)
        if offense_category:
            query = query.filter(CrimeIncident.offense_category == offense_category)
        if district:
            query = query.filter(CrimeIncident.district == district)
        
        # Pagination
        total = query.count()
        incidents = query.offset(offset).limit(limit).all()
        
        # Convert to GeoJSON
        features = []
        for incident in incidents:
            feature = {
                'type': 'Feature',
                'properties': incident.to_dict(),
                'geometry': {
                    'type': 'Point',
                    'coordinates': [incident.longitude, incident.latitude]
                } if incident.longitude and incident.latitude else None
            }
            features.append(feature)
        
        return jsonify({
            'type': 'FeatureCollection',
            'features': features,
            'total': total,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_crime_stats():
    """Get crime statistics"""
    try:
        # Parse query parameters
        bbox = request.args.get('bbox')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build base query
        query = CrimeIncident.query
        
        # Apply filters
        if bbox:
            minx, miny, maxx, maxy = parse_bbox(bbox)
            query = query.filter(
                and_(
                    CrimeIncident.longitude >= minx,
                    CrimeIncident.longitude <= maxx,
                    CrimeIncident.latitude >= miny,
                    CrimeIncident.latitude <= maxy
                )
            )
        
        if date_from:
            query = query.filter(CrimeIncident.report_date >= date_from)
        if date_to:
            query = query.filter(CrimeIncident.report_date <= date_to)
        
        # Calculate statistics
        total_incidents = query.count()
        
        # By category
        category_stats = db.session.query(
            CrimeIncident.offense_category,
            db.func.count(CrimeIncident.id).label('count')
        ).group_by(CrimeIncident.offense_category).all()
        
        # By district
        district_stats = db.session.query(
            CrimeIncident.district,
            db.func.count(CrimeIncident.id).label('count')
        ).group_by(CrimeIncident.district).all()
        
        return jsonify({
            'total_incidents': total_incidents,
            'by_category': [{'category': cat, 'count': count} for cat, count in category_stats],
            'by_district': [{'district': dist, 'count': count} for dist, count in district_stats]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Data Services

#### Data Service (services/data_service.py)
```python
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from geoalchemy2 import functions as geo_funcs
from models.base import Base
from models.crime import CrimeIncident
from models.service_requests import ServiceRequest311
from config import Config

class DataService:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_spatial_features(self, model_class, bbox=None, radius=None, 
                           center_lat=None, center_lng=None, **filters):
        """Get features with spatial filtering"""
        session = self.Session()
        try:
            query = session.query(model_class)
            
            # Apply spatial filters
            if bbox:
                minx, miny, maxx, maxy = bbox
                query = query.filter(
                    and_(
                        model_class.longitude >= minx,
                        model_class.longitude <= maxx,
                        model_class.latitude >= miny,
                        model_class.latitude <= maxy
                    )
                )
            elif radius and center_lat and center_lng:
                query = query.filter(
                    geo_funcs.ST_DWithin(
                        model_class.geom,
                        f'POINT({center_lng} {center_lat})',
                        radius
                    )
                )
            
            # Apply attribute filters
            for key, value in filters.items():
                if hasattr(model_class, key) and value is not None:
                    query = query.filter(getattr(model_class, key) == value)
            
            return query.all()
        finally:
            session.close()
    
    def get_proximity_analysis(self, source_model, target_model, 
                             source_id, max_distance=1000):
        """Find features within specified distance"""
        session = self.Session()
        try:
            # Get source feature
            source = session.query(source_model).filter(
                source_model.id == source_id
            ).first()
            
            if not source or not source.geom:
                return []
            
            # Find nearby features
            nearby = session.query(target_model).filter(
                geo_funcs.ST_DWithin(
                    target_model.geom,
                    source.geom,
                    max_distance
                )
            ).all()
            
            return nearby
        finally:
            session.close()
    
    def get_aggregated_data(self, model_class, group_by, 
                          bbox=None, date_from=None, date_to=None):
        """Get aggregated data by specified field"""
        session = self.Session()
        try:
            query = session.query(
                getattr(model_class, group_by),
                db.func.count(model_class.id).label('count')
            )
            
            # Apply filters
            if bbox:
                minx, miny, maxx, maxy = bbox
                query = query.filter(
                    and_(
                        model_class.longitude >= minx,
                        model_class.longitude <= maxx,
                        model_class.latitude >= miny,
                        model_class.latitude <= maxy
                    )
                )
            
            if date_from and hasattr(model_class, 'report_date'):
                query = query.filter(model_class.report_date >= date_from)
            if date_to and hasattr(model_class, 'report_date'):
                query = query.filter(model_class.report_date <= date_to)
            
            results = query.group_by(getattr(model_class, group_by)).all()
            return [{'value': value, 'count': count} for value, count in results]
        finally:
            session.close()
```

## Frontend Implementation

### Enhanced JavaScript Architecture

#### Module Structure (static/app.js)
```javascript
// Main application module
const KCDataPlatform = (function() {
    'use strict';
    
    // Private variables
    let map;
    let layers = {};
    let currentFilters = {};
    let dataCache = new Map();
    
    // Public API
    return {
        init: init,
        addLayer: addLayer,
        removeLayer: removeLayer,
        applyFilters: applyFilters,
        clearFilters: clearFilters,
        exportData: exportData
    };
    
    // Private functions
    function init() {
        initializeMap();
        setupEventListeners();
        loadInitialData();
    }
    
    function initializeMap() {
        map = L.map('map', {
            center: [39.0997, -94.5786], // Kansas City
            zoom: 12,
            minZoom: 8,
            maxZoom: 18
        });
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Initialize layer groups
        layers.crime = L.layerGroup().addTo(map);
        layers.serviceRequests = L.layerGroup().addTo(map);
        layers.businesses = L.layerGroup().addTo(map);
        layers.inspections = L.layerGroup().addTo(map);
        layers.osm = L.layerGroup().addTo(map);
    }
    
    function addLayer(layerName, layerData) {
        if (!layers[layerName]) {
            layers[layerName] = L.layerGroup();
        }
        
        const geoJsonLayer = L.geoJSON(layerData, {
            pointToLayer: createCustomMarker,
            style: getLayerStyle(layerName),
            onEachFeature: createFeatureHandler(layerName)
        });
        
        layers[layerName].addLayer(geoJsonLayer);
        map.addLayer(layers[layerName]);
    }
    
    function applyFilters(filters) {
        currentFilters = { ...currentFilters, ...filters };
        refreshAllLayers();
    }
    
    function refreshAllLayers() {
        Object.keys(layers).forEach(layerName => {
            if (layers[layerName].hasLayers()) {
                loadLayerData(layerName);
            }
        });
    }
    
    function loadLayerData(layerName) {
        const bbox = map.getBounds();
        const params = new URLSearchParams({
            bbox: `${bbox.getWest()},${bbox.getSouth()},${bbox.getEast()},${bbox.getNorth()}`,
            ...currentFilters
        });
        
        fetch(`/api/v1/${layerName}?${params}`)
            .then(response => response.json())
            .then(data => {
                layers[layerName].clearLayers();
                addLayer(layerName, data);
            })
            .catch(error => console.error('Error loading layer:', error));
    }
    
    // Additional private functions...
})();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', KCDataPlatform.init);
```

#### Layer Management System
```javascript
// Layer management module
const LayerManager = (function() {
    'use strict';
    
    const layerConfigs = {
        crime: {
            name: 'Crime Incidents',
            color: '#e74c3c',
            icon: 'fa-exclamation-triangle',
            visible: true,
            opacity: 0.8
        },
        serviceRequests: {
            name: '311 Service Requests',
            color: '#3498db',
            icon: 'fa-phone',
            visible: true,
            opacity: 0.8
        },
        businesses: {
            name: 'Businesses',
            color: '#2ecc71',
            icon: 'fa-store',
            visible: false,
            opacity: 0.8
        },
        inspections: {
            name: 'Food Inspections',
            color: '#f39c12',
            icon: 'fa-utensils',
            visible: false,
            opacity: 0.8
        }
    };
    
    function createLayerControls() {
        const container = document.getElementById('layer-controls');
        
        Object.keys(layerConfigs).forEach(layerName => {
            const config = layerConfigs[layerName];
            const control = createLayerControl(layerName, config);
            container.appendChild(control);
        });
    }
    
    function createLayerControl(layerName, config) {
        const div = document.createElement('div');
        div.className = 'layer-control';
        div.innerHTML = `
            <label>
                <input type="checkbox" ${config.visible ? 'checked' : ''} 
                       onchange="toggleLayer('${layerName}')">
                <i class="fas ${config.icon}" style="color: ${config.color}"></i>
                ${config.name}
            </label>
            <input type="range" min="0" max="100" value="${config.opacity * 100}"
                   onchange="setLayerOpacity('${layerName}', this.value / 100)">
        `;
        return div;
    }
    
    function toggleLayer(layerName) {
        const config = layerConfigs[layerName];
        config.visible = !config.visible;
        
        if (config.visible) {
            KCDataPlatform.addLayer(layerName, {});
        } else {
            KCDataPlatform.removeLayer(layerName);
        }
    }
    
    function setLayerOpacity(layerName, opacity) {
        layerConfigs[layerName].opacity = opacity;
        // Update layer opacity
    }
    
    return {
        createLayerControls,
        toggleLayer,
        setLayerOpacity
    };
})();
```

## Database Operations

### ETL Pipeline Implementation

#### Crime Data ETL (tools/etl/crime_etl.py)
```python
import requests
import json
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.crime import CrimeIncident
from services.geocoding_service import GeocodingService
from config import Config

class CrimeETL:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.geocoding_service = GeocodingService()
        self.api_url = f"{Config.KC_OPEN_DATA_BASE_URL}4i7q-w5kf.json"
    
    def extract_data(self, limit=1000, offset=0):
        """Extract crime data from KC Open Data API"""
        params = {
            '$limit': limit,
            '$offset': offset,
            '$order': 'report_date DESC'
        }
        
        if Config.KC_OPEN_DATA_APP_TOKEN:
            params['$$app_token'] = Config.KC_OPEN_DATA_APP_TOKEN
        
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def transform_data(self, raw_data):
        """Transform raw API data to database format"""
        transformed = []
        
        for record in raw_data:
            try:
                # Parse dates
                report_date = None
                if record.get('report_date'):
                    report_date = datetime.strptime(
                        record['report_date'], '%Y-%m-%dT%H:%M:%S.%f'
                    ).date()
                
                report_time = None
                if record.get('report_time'):
                    report_time = datetime.strptime(
                        record['report_time'], '%H:%M:%S'
                    ).time()
                
                # Create incident object
                incident = CrimeIncident(
                    case_id=record.get('report_no'),
                    report_date=report_date,
                    report_time=report_time,
                    offense_code=record.get('offense_code'),
                    offense_description=record.get('offense_description'),
                    offense_category=record.get('offense_category'),
                    offense_type=record.get('offense_type'),
                    address=record.get('address'),
                    city=record.get('city'),
                    state=record.get('state'),
                    zip_code=record.get('zip_code'),
                    district=record.get('district'),
                    beat=record.get('beat'),
                    sector=record.get('sector'),
                    latitude=float(record['latitude']) if record.get('latitude') else None,
                    longitude=float(record['longitude']) if record.get('longitude') else None
                )
                
                # Geocode if coordinates missing
                if not incident.latitude or not incident.longitude:
                    if incident.address:
                        coords = self.geocoding_service.geocode(incident.address)
                        if coords:
                            incident.latitude, incident.longitude = coords
                
                transformed.append(incident)
                
            except Exception as e:
                print(f"Error transforming record {record.get('report_no', 'unknown')}: {e}")
                continue
        
        return transformed
    
    def load_data(self, incidents):
        """Load transformed data into database"""
        session = self.Session()
        try:
            for incident in incidents:
                # Check if incident already exists
                existing = session.query(CrimeIncident).filter(
                    CrimeIncident.case_id == incident.case_id
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in incident.__dict__.items():
                        if not key.startswith('_') and key != 'id':
                            setattr(existing, key, value)
                else:
                    # Insert new record
                    session.add(incident)
            
            session.commit()
            print(f"Loaded {len(incidents)} crime incidents")
            
        except Exception as e:
            session.rollback()
            print(f"Error loading data: {e}")
            raise
        finally:
            session.close()
    
    def run_etl(self, limit=1000):
        """Run complete ETL process"""
        print("Starting crime data ETL...")
        
        # Extract
        raw_data = self.extract_data(limit=limit)
        print(f"Extracted {len(raw_data)} records")
        
        # Transform
        incidents = self.transform_data(raw_data)
        print(f"Transformed {len(incidents)} records")
        
        # Load
        self.load_data(incidents)
        print("ETL completed successfully")

if __name__ == '__main__':
    etl = CrimeETL()
    etl.run_etl()
```

## Deployment Configuration

### Production Configuration
```python
# config/production.py
import os

class ProductionConfig(Config):
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///data/processed/kc_data.gpkg'
    
    # Cache
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache'
    
    # Logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/kc-data-platform/app.log'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Performance
    MAX_FEATURES_PER_REQUEST = 10000
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutes
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data/processed cache logs

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "web.app:app"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///data/processed/kc_data.gpkg
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped
```

This technical implementation provides a solid foundation for building the Kansas City Data Platform with clean architecture, maintainable code, and production-ready deployment strategies.
