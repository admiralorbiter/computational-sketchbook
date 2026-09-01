# Configuration for Kansas City Data Platform

import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///data/processed/kc_data.gpkg'
    
    # Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # API configuration
    MAX_FEATURES_PER_REQUEST = int(os.environ.get('MAX_FEATURES_PER_REQUEST', 5000))
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    # CORS configuration
    CORS_ENABLED = os.environ.get('CORS_ENABLED', 'true').lower() == 'true'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # KC Open Data API
    KC_CRIME_API_URL = os.environ.get('KC_CRIME_API_URL', 'https://data.kcmo.org/resource/crime-data.json')
    KC_311_API_URL = os.environ.get('KC_311_API_URL', 'https://data.kcmo.org/resource/311-requests.json')
    KC_BUSINESS_API_URL = os.environ.get('KC_BUSINESS_API_URL', 'https://data.kcmo.org/resource/business-licenses.json')
    KC_INSPECTION_API_URL = os.environ.get('KC_INSPECTION_API_URL', 'https://data.kcmo.org/resource/food-inspections.json')
    KC_DATA_API_KEY = os.environ.get('KC_DATA_API_KEY')
    
    # Geocoding configuration
    GEOCODING_PROVIDER = os.environ.get('GEOCODING_PROVIDER', 'us_census')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Census Geocoding API
    CENSUS_API_URL = os.environ.get('CENSUS_API_URL', 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress')
    CENSUS_DAILY_LIMIT = int(os.environ.get('CENSUS_DAILY_LIMIT', 1000))
    CENSUS_LIMIT_THRESHOLD = float(os.environ.get('CENSUS_LIMIT_THRESHOLD', 0.9))
    
    # Census Data API (ACS demographic data)
    CENSUS_DATA_API_URL = os.environ.get('CENSUS_DATA_API_URL', 'https://api.census.gov/data/2023/acs/acs5')
    CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY')
    
    # Google Maps Geocoding API
    GOOGLE_GEOCODING_URL = os.environ.get('GOOGLE_GEOCODING_URL', 'https://maps.googleapis.com/maps/api/geocode/json')
    GOOGLE_MONTHLY_LIMIT = int(os.environ.get('GOOGLE_MONTHLY_LIMIT', 40000))
    
    # Geocoding service settings
    GEOCODING_CACHE_ENABLED = os.environ.get('GEOCODING_CACHE_ENABLED', 'true').lower() == 'true'
    GEOCODING_FUZZY_THRESHOLD = float(os.environ.get('GEOCODING_FUZZY_THRESHOLD', 0.85))
    GEOCODING_BATCH_SIZE = int(os.environ.get('GEOCODING_BATCH_SIZE', 100))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Performance configuration
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 1000))
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    # Address consolidation configuration
    CONSOLIDATION_ENABLED = os.environ.get('CONSOLIDATION_ENABLED', 'true').lower() == 'true'
    COORDINATE_TOLERANCE = float(os.environ.get('COORDINATE_TOLERANCE', 0.0001))
    CONSOLIDATION_STRATEGY = os.environ.get('CONSOLIDATION_STRATEGY', 'address_first')
    
    # Feature service configuration
    MAX_FEATURES_PER_LAYER = int(os.environ.get('MAX_FEATURES_PER_LAYER', 2000))
    CACHE_CONSOLIDATED_FEATURES = os.environ.get('CACHE_CONSOLIDATED_FEATURES', 'true').lower() == 'true'
    
    # Security configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'encryption-key-change-in-production'
    
    # Monitoring configuration
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    # Use absolute path for SQLite database
    # web/config.py -> web/ -> map-data/ -> data/processed/kc_data.gpkg
    db_path = Path(__file__).parent.parent / "data" / "processed" / "kc_data.gpkg"
    DATABASE_URL = f'sqlite:///{db_path}'
    CACHE_TYPE = 'simple'

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    CACHE_TYPE = 'redis'
    RATE_LIMIT_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    CACHE_TYPE = 'simple'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
