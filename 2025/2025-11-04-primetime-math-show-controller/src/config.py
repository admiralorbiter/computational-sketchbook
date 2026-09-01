"""Configuration management for PrimeTime Flask application."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{BASE_DIR / "data" / "primetime.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logging
    
    # Flask-SocketIO settings
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    # Handle CORS: '*' means allow all, otherwise split comma-separated origins
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*' if cors_origins == '*' else cors_origins.split(',')
    
    # Static files
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    
    # Asset directories
    ASSETS_DIR = BASE_DIR / 'assets'
    PHOTOS_DIR = ASSETS_DIR / 'photos'
    VIDEOS_DIR = ASSETS_DIR / 'videos'
    MUSIC_DIR = ASSETS_DIR / 'music'
    LOGOS_DIR = ASSETS_DIR / 'logos'
    
    # Other directories
    THEMES_DIR = BASE_DIR / 'themes'
    LOGS_DIR = BASE_DIR / 'logs'
    DATA_DIR = BASE_DIR / 'data'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

