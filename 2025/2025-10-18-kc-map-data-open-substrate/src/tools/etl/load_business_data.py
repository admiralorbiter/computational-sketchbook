#!/usr/bin/env python3
"""
Business Data ETL Pipeline

Loads business data from CSV files (business-license-list.csv and company-list.csv)
into the database, filtering to Kansas and Missouri only.
"""

import os
import sys
import csv
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.models import Business
from tools.etl.utils import DatabaseHelper, ETLStats, ProgressTracker, setup_logging

class LoadBusinessData:
    """Business Data ETL Pipeline"""
    
    def __init__(self, verbose: bool = False):
        log_file = project_root / "logs" / "business_etl.log"
        self.logger = setup_logging('business_etl', str(log_file), logging.DEBUG if verbose else logging.INFO)
        self.db_helper = DatabaseHelper()
        self.stats = ETLStats()
        
        # File paths
        self.license_file = project_root / "data" / "raw" / "business-license-list.csv"
        self.company_file = project_root / "data" / "raw" / "company-list.csv"
    
    def extract_data(self) -> Dict[str, List[Dict]]:
        """Extract data from CSV files"""
        self.logger.info("Extracting business data from CSV files...")
        
        data = {
            'licenses': [],
            'companies': []
        }
        
        # Extract business license data
        if self.license_file.exists():
            self.logger.info(f"Reading business license data from {self.license_file}")
            with open(self.license_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter to MO and KS only
                    state = row.get('State', '').strip().upper()
                    if state in ['MO', 'KS']:
                        data['licenses'].append(row)
            
            self.logger.info(f"Found {len(data['licenses'])} business licenses in MO/KS")
        else:
            self.logger.warning(f"Business license file not found: {self.license_file}")
        
        # Extract company data
        if self.company_file.exists():
            self.logger.info(f"Reading company data from {self.company_file}")
            with open(self.company_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter to MO and KS only (check address field)
                    address = row.get('address', '')
                    if any(state in address.upper() for state in ['MO', 'KS', 'MISSOURI', 'KANSAS']):
                        data['companies'].append(row)
            
            self.logger.info(f"Found {len(data['companies'])} companies in MO/KS")
        else:
            self.logger.warning(f"Company file not found: {self.company_file}")
        
        return data
    
    def transform_data(self, data: Dict[str, List[Dict]]) -> List[Dict]:
        """Transform raw CSV data to database format"""
        self.logger.info("Transforming business data...")
        
        transformed = []
        skipped = 0
        
        # Transform business license data
        for record in data['licenses']:
            try:
                # Parse coordinates (will be geocoded later if missing)
                lat = self._parse_float(record.get('Latitude'))
                lon = self._parse_float(record.get('Longitude'))
                
                transformed_record = {
                    'name': record.get('Business Name', '').strip(),
                    'business_type': record.get('Business Type', '').strip(),
                    'address': record.get('Address', '').strip(),
                    'city': record.get('City', '').strip(),
                    'state': record.get('State', '').strip(),
                    'zipcode': record.get('Zipcode', '').strip(),
                    'dba_name': record.get('DBA Name', '').strip(),
                    'valid_license_for': record.get('Valid License For', '').strip(),
                    'latitude': lat,
                    'longitude': lon,
                    'source': 'license',
                    'source_id': record.get('ID', ''),
                    'description': f"Business License - {record.get('Business Type', '')}",
                    'industry': record.get('Business Type', '').strip()
                }
                
                transformed.append(transformed_record)
                
            except Exception as e:
                self.logger.error(f"Error transforming license record {record.get('ID', 'unknown')}: {e}")
                skipped += 1
                continue
        
        # Transform company data
        for record in data['companies']:
            try:
                # Parse coordinates (will be geocoded later if missing)
                lat = self._parse_float(record.get('lat'))
                lon = self._parse_float(record.get('lon'))
                
                # Extract state from address
                address = record.get('address', '')
                state = self._extract_state_from_address(address)
                
                transformed_record = {
                    'name': record.get('matched_name', '').strip(),
                    'business_type': record.get('Industry', '').strip(),
                    'address': address,
                    'city': self._extract_city_from_address(address),
                    'state': state,
                    'zipcode': self._extract_zip_from_address(address),
                    'place_id': record.get('place_id', ''),
                    'place_type': record.get('place_type', ''),
                    'latitude': lat,
                    'longitude': lon,
                    'source': 'company',
                    'source_id': record.get('input_name', ''),
                    'description': record.get('Description', '').strip(),
                    'industry': record.get('Industry', '').strip()
                }
                
                transformed.append(transformed_record)
                
            except Exception as e:
                self.logger.error(f"Error transforming company record {record.get('input_name', 'unknown')}: {e}")
                skipped += 1
                continue
        
        self.logger.info(f"Transformation complete: {len(transformed):,} records, {skipped:,} skipped")
        return transformed
    
    def load_data(self, records: List[Dict]) -> Dict[str, int]:
        """Load transformed data into database"""
        self.logger.info("Loading business data into database...")
        
        if not records:
            self.logger.warning("No records to load")
            return {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Create tables if they don't exist
        self.db_helper.create_tables(drop_existing=False)
        
        # Load data using batch upsert
        stats = self.db_helper.batch_upsert(
            model_class=Business,
            records=records,
            key_field='source_id',  # Use source_id as unique key
            batch_size=1000
        )
        
        self.logger.info(f"Load complete: {stats['inserted']:,} inserted, {stats['updated']:,} updated, {stats['errors']:,} errors")
        return stats
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Parse float value from string"""
        if not value:
            return None
        try:
            return float(value.strip())
        except (ValueError, TypeError):
            return None
    
    def _extract_state_from_address(self, address: str) -> str:
        """Extract state abbreviation from address"""
        if not address:
            return ''
        
        # Look for state abbreviations
        state_abbrevs = ['MO', 'KS']
        for state in state_abbrevs:
            if state in address.upper():
                return state
        
        # Look for full state names
        if 'MISSOURI' in address.upper():
            return 'MO'
        elif 'KANSAS' in address.upper():
            return 'KS'
        
        return ''
    
    def _extract_city_from_address(self, address: str) -> str:
        """Extract city from address (simplified)"""
        if not address:
            return ''
        
        # Split by comma and take the second part (city, state zip)
        parts = address.split(',')
        if len(parts) >= 2:
            return parts[1].strip().split()[0]  # First word before state
        
        return ''
    
    def _extract_zip_from_address(self, address: str) -> str:
        """Extract zip code from address"""
        if not address:
            return ''
        
        # Look for 5-digit zip code
        import re
        zip_match = re.search(r'\b(\d{5})\b', address)
        if zip_match:
            return zip_match.group(1)
        
        return ''
    
    def run_etl(self, limit: Optional[int] = None) -> ETLStats:
        """Run complete ETL process"""
        self.logger.info("Starting business data ETL...")
        
        try:
            # Extract
            raw_data = self.extract_data()
            
            # Apply limit if specified
            if limit:
                raw_data['licenses'] = raw_data['licenses'][:limit//2]
                raw_data['companies'] = raw_data['companies'][:limit//2]
                self.logger.info(f"Limited to {limit} records for testing")
            
            # Transform
            transformed_data = self.transform_data(raw_data)
            
            # Load
            load_stats = self.load_data(transformed_data)
            
            # Geocode missing coordinates
            self.logger.info("Geocoding missing coordinates...")
            geocoding_stats = self.db_helper.geocode_missing_coordinates(Business, batch_size=100)
            
            # Update stats
            self.stats.total_processed = len(transformed_data)
            self.stats.total_inserted = load_stats['inserted']
            self.stats.total_updated = load_stats['updated']
            self.stats.total_errors += load_stats['errors']
            
            self.logger.info("Business data ETL completed successfully")
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
    parser = argparse.ArgumentParser(description="Load business data from CSV files")
    
    # Operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--initial", action="store_true", help="Initial load (all data)")
    group.add_argument("--test", action="store_true", help="Test with small dataset")
    
    # Other options
    parser.add_argument("--limit", type=int, help="Limit number of records to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be loaded without actually loading")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Create ETL instance
    etl = LoadBusinessData(verbose=args.verbose)
    
    # Create database tables if they don't exist
    etl.logger.info("Setting up database...")
    # Always use drop_existing=False to preserve other tables
    etl.db_helper.create_tables(drop_existing=False)
    etl.logger.info("   Database ready")
    
    # Determine operation
    if args.initial:
        etl.logger.info("Running initial load...")
        limit = args.limit
    elif args.test:
        etl.logger.info("Running test load...")
        limit = args.limit or 100
    
    # Run ETL
    if args.dry_run:
        etl.logger.info("DRY RUN - No data will be loaded")
        # Just extract and transform to show what would be loaded
        raw_data = etl.extract_data()
        transformed_data = etl.transform_data(raw_data)
        etl.logger.info(f"Would load {len(transformed_data)} records")
    else:
        stats = etl.run_etl(limit)
        etl.logger.info(f"ETL completed: {stats.total_processed} processed, {stats.total_inserted} inserted")

if __name__ == "__main__":
    main()
