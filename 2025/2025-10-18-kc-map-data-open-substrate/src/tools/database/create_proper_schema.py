#!/usr/bin/env python3
"""
Create proper database schema that matches ETL expectations
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def create_proper_schema():
    """Create database with proper schema for ETL scripts"""
    
    # Ensure the processed directory exists
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Database path
    db_path = processed_dir / "kc_data.gpkg"
    
    print(f"Creating proper database schema at: {db_path}")
    
    # Create SQLite database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create service_requests_311 table with proper schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_requests_311 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE NOT NULL,
            issue_type TEXT NOT NULL,
            issue_sub_type TEXT,
            current_status TEXT NOT NULL,
            open_date_time TEXT,
            resolved_date TEXT,
            last_updated TEXT,
            days_to_close INTEGER,
            incident_address TEXT,
            council_district TEXT,
            department_work_group TEXT,
            report_source TEXT,
            source_category TEXT,
            workorder_ TEXT,
            additional_questions TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create crime_incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report TEXT UNIQUE NOT NULL,
            report_date TEXT,
            reported_time TEXT,
            from_date TEXT,
            from_time TEXT,
            to_date TEXT,
            to_time TEXT,
            offense TEXT,
            ibrs TEXT,
            description TEXT,
            beat TEXT,
            address TEXT,
            city TEXT,
            zipcode TEXT,
            rep_dist TEXT,
            area TEXT,
            involvement TEXT,
            race TEXT,
            sex TEXT,
            age INTEGER,
            age_range TEXT,
            dvflag INTEGER DEFAULT 0,
            firearmusedflag INTEGER DEFAULT 0,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create businesses table (used by the application)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            business_type TEXT,
            description TEXT,
            industry TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT,
            source TEXT NOT NULL,
            source_id TEXT,
            dba_name TEXT,
            valid_license_for TEXT,
            place_id TEXT,
            place_type TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create dangerous_buildings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dangerous_buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT,
            case_opened TEXT NOT NULL,
            status_of_case TEXT NOT NULL,
            pin TEXT,
            council_district TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create landbank_properties table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS landbank_properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT,
            latitude REAL,
            longitude REAL,
            parcel_number TEXT UNIQUE NOT NULL,
            property_status TEXT,
            inventory_type TEXT,
            property_class TEXT,
            property_condition TEXT,
            market_value REAL,
            market_value_year INTEGER,
            square_footage REAL,
            demo_needed TEXT,
            city_council_district TEXT,
            county TEXT,
            neighborhood TEXT,
            school_district TEXT,
            zoned_as TEXT,
            date_of_acquisition TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create food_inspections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_id TEXT UNIQUE,
            business_name TEXT,
            address TEXT,
            inspection_date TEXT,
            score INTEGER,
            grade TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create osm_features table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS osm_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            osm_id TEXT,
            feature_type TEXT,
            name TEXT,
            tags TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance
    print("Creating database indexes...")
    
    # Service requests indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_id ON service_requests_311(request_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_issue_type ON service_requests_311(issue_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_current_status ON service_requests_311(current_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_date ON service_requests_311(open_date_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_latitude ON service_requests_311(latitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_longitude ON service_requests_311(longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coords ON service_requests_311(latitude, longitude)")
    
    # Crime incidents indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_report ON crime_incidents(report)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_date ON crime_incidents(report_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_offense ON crime_incidents(offense)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ibrs ON crime_incidents(ibrs)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_area ON crime_incidents(area)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dvflag ON crime_incidents(dvflag)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_firearmusedflag ON crime_incidents(firearmusedflag)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_latitude ON crime_incidents(latitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_longitude ON crime_incidents(longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_coords ON crime_incidents(latitude, longitude)")
    
    # Businesses indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_name ON businesses(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_type ON businesses(business_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_source ON businesses(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_latitude ON businesses(latitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_longitude ON businesses(longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_coords ON businesses(latitude, longitude)")
    
    # Dangerous buildings indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_number ON dangerous_buildings(case_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_of_case ON dangerous_buildings(status_of_case)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_council_district ON dangerous_buildings(council_district)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_latitude ON dangerous_buildings(latitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_longitude ON dangerous_buildings(longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_coords ON dangerous_buildings(latitude, longitude)")
    
    # Landbank properties indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_landbank_parcel ON landbank_properties(parcel_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_landbank_status ON landbank_properties(property_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_landbank_latitude ON landbank_properties(latitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_landbank_longitude ON landbank_properties(longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_landbank_coords ON landbank_properties(latitude, longitude)")
    
    # Food inspections indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inspection_id ON food_inspections(inspection_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inspection_date ON food_inspections(inspection_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_grade ON food_inspections(grade)")
    
    # OSM features indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_osm_id ON osm_features(osm_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feature_type ON osm_features(feature_type)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database schema created successfully: {db_path}")
    
    # Check file size
    if db_path.exists():
        file_size = db_path.stat().st_size / 1024  # Size in KB
        print(f"Database size: {file_size:.2f} KB")
    
    return True

def main():
    """Main function"""
    print("Creating proper database schema...")
    
    try:
        success = create_proper_schema()
        if success:
            print("Database schema creation completed successfully!")
            print("Database is ready for ETL scripts")
        else:
            print("Database schema creation failed!")
            return 1
    except Exception as e:
        print(f"Error during database schema creation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
