#!/usr/bin/env python3
"""
Add database indexes for address consolidation performance
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.config import config

def add_consolidation_indexes():
    """Add indexes for address and coordinate lookups"""
    
    # Get database path
    config_name = os.environ.get('FLASK_ENV', 'development')
    app_config = config[config_name]
    database_url = app_config.DATABASE_URL
    
    # Extract file path from SQLite URL
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(project_root, db_path)
    else:
        print(f"Unsupported database URL: {database_url}")
        return False
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    print(f"Adding indexes to database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Indexes for service requests
        print("Adding indexes for service_requests_311...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_address_coords 
            ON service_requests_311(incident_address, latitude, longitude)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_coords 
            ON service_requests_311(latitude, longitude)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_requests_address 
            ON service_requests_311(incident_address)
        """)
        
        # Indexes for crime incidents
        print("Adding indexes for crime_incidents...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crime_address_coords 
            ON crime_incidents(address, latitude, longitude)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crime_coords 
            ON crime_incidents(latitude, longitude)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crime_address 
            ON crime_incidents(address)
        """)
        
        # Indexes for business licenses (if they have address fields)
        print("Adding indexes for business_licenses...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_business_address_coords 
                ON business_licenses(business_address, latitude, longitude)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_business_coords 
                ON business_licenses(latitude, longitude)
            """)
        except sqlite3.OperationalError as e:
            print(f"  Note: Business license indexes skipped - {e}")
        
        # Indexes for food inspections (if they have address fields)
        print("Adding indexes for food_inspections...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inspection_address_coords 
                ON food_inspections(establishment_address, latitude, longitude)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inspection_coords 
                ON food_inspections(latitude, longitude)
            """)
        except sqlite3.OperationalError as e:
            print(f"  Note: Food inspection indexes skipped - {e}")
        
        # Commit changes
        conn.commit()
        print("SUCCESS: All indexes added successfully!")
        
        # Show index information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        print(f"\nCreated {len(indexes)} indexes:")
        for (index_name,) in indexes:
            print(f"  - {index_name}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Error adding indexes: {e}")
        return False

if __name__ == "__main__":
    success = add_consolidation_indexes()
    sys.exit(0 if success else 1)
