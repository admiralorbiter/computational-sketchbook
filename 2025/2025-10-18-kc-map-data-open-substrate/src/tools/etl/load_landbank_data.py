#!/usr/bin/env python3
"""
Land Bank Data ETL Pipeline

Loads Land Bank and Kansas City Homesteading Authority data from KC Open Data
into the database with geocoding integration.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.etl.utils import SodaApiClient, DatabaseHelper, ETLStats, ProgressTracker, setup_logging, DataValidator

class LandBankRecord:
    """Land Bank data model"""
    
    def __init__(self, data: Dict):
        self.address = data.get('address', '').strip()
        self.city = data.get('city', '').strip()
        self.state = data.get('state', '').strip()
        self.postal_code = data.get('postal_code', '').strip()
        self.city_council_district = data.get('city_council_district', '').strip()
        self.county = data.get('county', '').strip()
        self.date_of_acquisition = data.get('date_of_acquisition', '').strip()
        self.demo_needed = data.get('demo_needed', '').strip()
        self.inventory_type = data.get('inventory_type', '').strip()
        self.market_value = self._parse_numeric(data.get('market_value'))
        self.market_value_year = self._parse_numeric(data.get('market_value_year'))
        self.neighborhood = data.get('neighborhood', '').strip()
        self.parcel_number = data.get('parcel_number', '').strip()
        self.property_class = data.get('property_class', '').strip()
        self.property_condition = data.get('property_condition', '').strip()
        self.property_status = data.get('property_status', '').strip()
        self.school_district = data.get('school_district', '').strip()
        self.square_footage = self._parse_numeric(data.get('square_footage'))
        self.zoned_as = data.get('zoned_as', '').strip()
        
        # Geocoding fields (will be populated by geocoding service)
        self.latitude = None
        self.longitude = None
    
    def _parse_numeric(self, value) -> Optional[float]:
        """Parse numeric values safely"""
        if not value or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database insertion"""
        return {
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'city_council_district': self.city_council_district,
            'county': self.county,
            'date_of_acquisition': self.date_of_acquisition,
            'demo_needed': self.demo_needed,
            'inventory_type': self.inventory_type,
            'market_value': self.market_value,
            'market_value_year': self.market_value_year,
            'neighborhood': self.neighborhood,
            'parcel_number': self.parcel_number,
            'property_class': self.property_class,
            'property_condition': self.property_condition,
            'property_status': self.property_status,
            'school_district': self.school_district,
            'square_footage': self.square_footage,
            'zoned_as': self.zoned_as,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
    
    def get_full_address(self) -> str:
        """Get full address for geocoding"""
        if not self.address:
            return ""
        
        # Add city and state if not already present
        full_address = self.address
        if self.city and self.city.lower() not in full_address.lower():
            full_address += f", {self.city}"
        if self.state and self.state.lower() not in full_address.lower():
            full_address += f", {self.state}"
        
        return full_address

class LoadLandBankData:
    """Land Bank Data ETL Pipeline"""
    
    def __init__(self, verbose: bool = False):
        log_file = project_root / "logs" / "landbank_etl.log"
        self.logger = setup_logging('landbank_etl', str(log_file), logging.DEBUG if verbose else logging.INFO)
        self.db_helper = DatabaseHelper()
        self.api_client = SodaApiClient()
        self.stats = ETLStats()
        
        # Land Bank dataset endpoint
        self.endpoint = "2ebw-sp7f"  # Land Bank and Kansas City Homesteading Authority
    
    def create_table(self):
        """Create landbank_properties table if it doesn't exist"""
        import sqlite3
        
        # Get database path
        db_path = self.db_helper.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='landbank_properties'
            """)
            
            if not cursor.fetchone():
                # Create table
                cursor.execute("""
                    CREATE TABLE landbank_properties (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        postal_code TEXT,
                        city_council_district TEXT,
                        county TEXT,
                        date_of_acquisition TEXT,
                        demo_needed TEXT,
                        inventory_type TEXT,
                        market_value REAL,
                        market_value_year INTEGER,
                        neighborhood TEXT,
                        parcel_number TEXT UNIQUE NOT NULL,
                        property_class TEXT,
                        property_condition TEXT,
                        property_status TEXT,
                        school_district TEXT,
                        square_footage REAL,
                        zoned_as TEXT,
                        latitude REAL,
                        longitude REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_parcel_number ON landbank_properties(parcel_number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_address ON landbank_properties(address)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON landbank_properties(city)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON landbank_properties(state)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_neighborhood ON landbank_properties(neighborhood)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_property_class ON landbank_properties(property_class)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_property_status ON landbank_properties(property_status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_type ON landbank_properties(inventory_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_latitude ON landbank_properties(latitude)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_longitude ON landbank_properties(longitude)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_coords ON landbank_properties(latitude, longitude)")
                
                conn.commit()
                self.logger.info("Created landbank_properties table with indexes")
            else:
                self.logger.info("landbank_properties table already exists")
                
        finally:
            conn.close()
    
    def extract_data(self, limit: Optional[int] = None) -> List[Dict]:
        """Extract data from KC Open Data API"""
        self.logger.info("Extracting Land Bank data from KC Open Data...")
        
        try:
            # Build query parameters
            params = {}
            if limit:
                params['$limit'] = limit
            
            # Fetch data
            raw_data = self.api_client.fetch_data(self.endpoint, params)
            
            self.logger.info(f"Fetched {len(raw_data)} records from Land Bank dataset")
            return raw_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract data: {e}")
            raise
    
    def transform_data(self, raw_data: List[Dict]) -> List[LandBankRecord]:
        """Transform raw data into LandBankRecord objects"""
        self.logger.info("Transforming Land Bank data...")
        
        records = []
        for i, item in enumerate(raw_data):
            try:
                # Create LandBankRecord
                record = LandBankRecord(item)
                
                # Validate required fields
                if not record.parcel_number:
                    self.logger.warning(f"Record {i} missing parcel_number, skipping")
                    continue
                
                records.append(record)
                
            except Exception as e:
                self.logger.error(f"Error transforming record {i}: {e}")
                continue
        
        self.logger.info(f"Transformed {len(records)} valid records")
        return records
    
    def load_data(self, records: List[LandBankRecord]) -> Dict[str, int]:
        """Load records into database"""
        self.logger.info("Loading Land Bank data into database...")
        
        # Convert to dictionaries
        record_dicts = [record.to_dict() for record in records]
        
        # Use batch upsert
        stats = self.db_helper.batch_upsert_landbank(record_dicts)
        
        self.logger.info(f"Load complete: {stats['inserted']} inserted, {stats['updated']} updated, {stats['errors']} errors")
        return stats
    
    def geocode_records(self, records: List[LandBankRecord], batch_size: int = 100) -> Dict[str, int]:
        """Geocode records that don't have coordinates"""
        from tools.geocoding.geocoding_service import GeocodingService
        import os
        
        # Get database path and API key
        db_path = self.db_helper.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        geocoding_service = GeocodingService(db_path, google_api_key)
        
        # Find records that need geocoding
        records_to_geocode = [r for r in records if r.address and not r.latitude and not r.longitude]
        
        if not records_to_geocode:
            self.logger.info("No records need geocoding")
            return {'geocoded': 0, 'errors': 0, 'skipped': 0}
        
        self.logger.info(f"Geocoding {len(records_to_geocode)} records...")
        
        geocoded = 0
        errors = 0
        
        # Process in batches
        for i in range(0, len(records_to_geocode), batch_size):
            batch = records_to_geocode[i:i + batch_size]
            
            for record in batch:
                try:
                    # Get full address
                    full_address = record.get_full_address()
                    if not full_address:
                        continue
                    
                    # Geocode
                    result = geocoding_service.geocode_address(full_address)
                    
                    if result['success']:
                        record.latitude = result['latitude']
                        record.longitude = result['longitude']
                        geocoded += 1
                        self.logger.debug(f"Geocoded: {full_address}")
                    else:
                        errors += 1
                        self.logger.warning(f"Failed to geocode: {full_address} - {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    errors += 1
                    self.logger.error(f"Error geocoding {record.address}: {e}")
        
        self.logger.info(f"Geocoding complete: {geocoded} geocoded, {errors} errors")
        return {'geocoded': geocoded, 'errors': errors, 'skipped': 0}
    
    def run_etl(self, limit: Optional[int] = None) -> ETLStats:
        """Run the complete ETL pipeline"""
        try:
            self.stats.start_time = datetime.now()
            
            # Create table
            self.logger.info("Setting up database...")
            self.create_table()
            
            # Extract
            raw_data = self.extract_data(limit)
            self.stats.total_fetched = len(raw_data)
            
            if limit:
                self.logger.info(f"Limited to {limit} records for testing")
            
            # Transform
            records = self.transform_data(raw_data)
            self.stats.total_processed = len(records)
            
            # Geocode
            self.logger.info("Geocoding addresses...")
            geocoding_stats = self.geocode_records(records)
            
            # Load
            load_stats = self.load_data(records)
            
            # Update stats
            self.stats.total_inserted = load_stats['inserted']
            self.stats.total_updated = load_stats['updated']
            self.stats.total_errors += load_stats['errors']
            self.stats.end_time = datetime.now()
            
            self.logger.info("Land Bank ETL completed successfully")
            self.logger.info(f"Processed: {self.stats.total_processed:,}")
            self.logger.info(f"Inserted: {self.stats.total_inserted:,}")
            self.logger.info(f"Updated: {self.stats.total_updated:,}")
            self.logger.info(f"Errors: {self.stats.total_errors:,}")
            self.logger.info(f"Geocoded: {geocoding_stats['geocoded']:,}")
            self.logger.info(f"Geocoding errors: {geocoding_stats['errors']:,}")
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"ETL failed: {e}")
            raise

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Load Land Bank data from KC Open Data")
    
    # Operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--initial", action="store_true", help="Initial load (all data)")
    group.add_argument("--test", action="store_true", help="Test with small dataset")
    
    # Other options
    parser.add_argument("--limit", type=int, help="Limit number of records to process")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Create ETL instance
    etl = LoadLandBankData(verbose=args.verbose)
    
    # Set limit for test mode
    if args.test and not args.limit:
        args.limit = 50
    
    # Run ETL
    try:
        stats = etl.run_etl(limit=args.limit)
        
        # Print summary
        print(f"\nLand Bank ETL Complete!")
        print("=" * 50)
        print(f"Summary:")
        print(f"   - Total fetched: {stats.total_fetched:,}")
        print(f"   - Total processed: {stats.total_processed:,}")
        print(f"   - Inserted (new): {stats.total_inserted:,}")
        print(f"   - Updated (existing): {stats.total_updated:,}")
        print(f"   - Errors: {stats.total_errors:,}")
        print(f"   - Success rate: {stats.success_rate:.1f}%")
        if stats.duration:
            print(f"   - Duration: {stats.duration:.1f}s")
        print()
        
    except Exception as e:
        print(f"ETL failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
