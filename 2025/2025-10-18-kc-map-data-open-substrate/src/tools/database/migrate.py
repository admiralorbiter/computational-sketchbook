#!/usr/bin/env python3
"""
Database migration tool for Kansas City Data Platform
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_database():
    """Create the database and all tables"""
    
    # Database path
    db_path = project_root / "data" / "processed" / "kc_data.gpkg"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print(f"✅ Database created at {db_path}")
    print(f"✅ Created {len(Base.metadata.tables)} tables")
    
    return engine

def create_spatial_indexes(engine):
    """Create spatial indexes for better performance"""
    
    with engine.connect() as conn:
        # Enable SpatiaLite
        conn.execute("SELECT load_extension('mod_spatialite')")
        
        # Create spatial indexes
        spatial_tables = [
            'crime_incidents',
            'service_requests_311', 
            'business_licenses',
            'food_inspections',
            'osm_features',
            'spatial_units',
            'location_index'
        ]
        
        for table in spatial_tables:
            try:
                conn.execute(f"SELECT CreateSpatialIndex('{table}', 'geometry')")
                print(f"✅ Created spatial index for {table}")
            except Exception as e:
                print(f"⚠️  Could not create spatial index for {table}: {e}")

def main():
    """Main migration function"""
    
    print("🚀 Starting database migration...")
    
    # Create database
    engine = create_database()
    
    # Create spatial indexes
    create_spatial_indexes(engine)
    
    print("✅ Database migration completed successfully!")

if __name__ == "__main__":
    main()
