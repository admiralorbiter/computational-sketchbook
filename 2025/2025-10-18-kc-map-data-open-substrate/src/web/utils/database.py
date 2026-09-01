# Database Utilities

import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..config import config
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def get_db_session():
    """Get database session for KC data"""
    current_config = config['development']  # TODO: Make configurable
    engine = create_engine(current_config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def get_db_connection():
    """Get a connection to the OSM GeoPackage database."""
    osm_path = Path(__file__).parent.parent.parent / "data" / "processed" / "missouri.gpkg"
    if not osm_path.exists():
        raise FileNotFoundError(f"OSM database file {osm_path} not found")
    
    conn = sqlite3.connect(str(osm_path))
    return conn
