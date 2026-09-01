#!/usr/bin/env python3
"""
Geocoding Cache Database Schema

Creates the geocoding_cache table for storing geocoded addresses
with comprehensive indexing for fast lookups and fuzzy matching.
"""

import sqlite3
from pathlib import Path
from typing import Optional

def create_geocoding_cache_table(db_path: str) -> None:
    """Create the geocoding_cache table with all necessary indexes"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create geocoding_cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geocoding_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_address TEXT NOT NULL,
                normalized_address TEXT NOT NULL,
                address_hash TEXT UNIQUE NOT NULL,
                street_number TEXT,
                street_name TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                latitude REAL,
                longitude REAL,
                geocoding_source TEXT NOT NULL CHECK(geocoding_source IN ('census', 'google', 'manual')),
                geocoding_quality TEXT NOT NULL CHECK(geocoding_quality IN ('high', 'medium', 'low')),
                confidence_score REAL NOT NULL CHECK(confidence_score >= 0 AND confidence_score <= 100),
                match_type TEXT NOT NULL CHECK(match_type IN ('exact', 'fuzzy', 'component')),
                census_attempts INTEGER DEFAULT 0,
                google_attempts INTEGER DEFAULT 0,
                last_geocoded TEXT NOT NULL,
                times_used INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for fast lookups
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_address_hash ON geocoding_cache(address_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_normalized_address ON geocoding_cache(normalized_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city_state ON geocoding_cache(city, state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_street_city_state ON geocoding_cache(street_name, city, state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_components ON geocoding_cache(street_name, city, state, zipcode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_coordinates ON geocoding_cache(latitude, longitude)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_geocoding_source ON geocoding_cache(geocoding_source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality ON geocoding_cache(geocoding_quality)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON geocoding_cache(confidence_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_geocoded ON geocoding_cache(last_geocoded)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_times_used ON geocoding_cache(times_used)")
        
        # Create usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS geocoding_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                usage_date TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(service_name, usage_date)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_service_date ON geocoding_usage(service_name, usage_date)")
        
        conn.commit()
        print("Geocoding cache table created successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating geocoding cache table: {e}")
        raise
    finally:
        conn.close()

def get_cache_stats(db_path: str) -> dict:
    """Get cache statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache")
        total_cached = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache WHERE geocoding_source = 'census'")
        census_cached = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache WHERE geocoding_source = 'google'")
        google_cached = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache WHERE geocoding_quality = 'high'")
        high_quality = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache WHERE geocoding_quality = 'medium'")
        medium_quality = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM geocoding_cache WHERE geocoding_quality = 'low'")
        low_quality = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence_score) FROM geocoding_cache")
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Most used addresses
        cursor.execute("""
            SELECT original_address, times_used 
            FROM geocoding_cache 
            ORDER BY times_used DESC 
            LIMIT 5
        """)
        most_used = cursor.fetchall()
        
        return {
            'total_cached': total_cached,
            'census_cached': census_cached,
            'google_cached': google_cached,
            'high_quality': high_quality,
            'medium_quality': medium_quality,
            'low_quality': low_quality,
            'avg_confidence': round(avg_confidence, 2),
            'most_used': most_used
        }
        
    finally:
        conn.close()

def clear_cache(db_path: str, confirm: bool = False) -> None:
    """Clear the geocoding cache"""
    if not confirm:
        print("This will delete all cached geocoding data. Use confirm=True to proceed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM geocoding_cache")
        cursor.execute("DELETE FROM geocoding_usage")
        conn.commit()
        print("Geocoding cache cleared")
    except Exception as e:
        conn.rollback()
        print(f"Error clearing cache: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Get database path from project root
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "processed" / "kc_data.gpkg"
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create the table
    create_geocoding_cache_table(str(db_path))
    
    # Show stats
    stats = get_cache_stats(str(db_path))
    print(f"\nCache Statistics:")
    print(f"  Total cached addresses: {stats['total_cached']}")
    print(f"  Census geocoded: {stats['census_cached']}")
    print(f"  Google geocoded: {stats['google_cached']}")
    print(f"  High quality: {stats['high_quality']}")
    print(f"  Medium quality: {stats['medium_quality']}")
    print(f"  Low quality: {stats['low_quality']}")
    print(f"  Average confidence: {stats['avg_confidence']}%")
