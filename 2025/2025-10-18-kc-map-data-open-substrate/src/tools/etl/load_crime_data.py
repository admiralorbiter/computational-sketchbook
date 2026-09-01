#!/usr/bin/env python3
"""
Crime Data ETL Pipeline

Loads crime incident data from Kansas City Open Data into the database.
Supports initial load, incremental updates, and various filtering options.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.etl.utils import (
    SodaApiClient, ProgressTracker, Logger, DataValidator, 
    DatabaseHelper, ETLStats, create_point_geometry, print_etl_summary
)
from web.models import CrimeIncident

class LoadCrimeData:
    """Crime Data ETL Pipeline"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = Logger("crime_etl")
        self.api_client = SodaApiClient()
        self.db_helper = DatabaseHelper()
        self.validator = DataValidator()
        self.stats = ETLStats()
        
        # Required fields for crime data
        self.required_fields = ['report', 'report_date', 'offense']
    
    def extract_data(self, limit: Optional[int] = None, 
                    where_clause: Optional[str] = None) -> List[Dict]:
        """Extract data from KC Open Data Crime API"""
        self.logger.info("Extracting data from KC Open Data Crime API...")
        
        endpoint = "dmnp-9ajg"  # KCPD Crime Data 2025
        order_by = "report_date DESC"
        
        all_records = []
        
        try:
            # Extract data in batches using fetch_paginated
            batch_size = 1000
            records_processed = 0
            
            progress = ProgressTracker(limit or 10000, "Extracting crime data")
            for batch in self.api_client.fetch_paginated(
                endpoint=endpoint,
                limit=batch_size,
                where_clause=where_clause,
                order_by=order_by
            ):
                if not batch:
                    break
                
                all_records.extend(batch)
                records_processed += len(batch)
                progress.update(len(batch))
                
                self.logger.info(f"Extracted {len(all_records):,} records so far...")
                
                # Stop if we've reached the limit
                if limit and len(all_records) >= limit:
                    all_records = all_records[:limit]
                    break
            
            progress.complete()
            
            self.logger.info(f"Extraction complete: {len(all_records):,} records")
            return all_records
            
        except Exception as e:
            self.logger.error(f"Error extracting data: {e}")
            raise
    
    def transform_data(self, records: List[Dict]) -> List[Dict]:
        """Transform raw API data to database format"""
        self.logger.info("Transforming crime data...")
        
        transformed = []
        skipped = 0
        
        for record in records:
            try:
                # Validate required fields
                if not all(record.get(field) for field in self.required_fields):
                    skipped += 1
                    continue
                
                # Parse dates
                report_date = self._parse_datetime(record.get('report_date'))
                from_date = self._parse_datetime(record.get('from_date'))
                to_date = self._parse_datetime(record.get('to_date'))
                
                # Extract coordinates from location
                latitude, longitude = self._extract_coordinates(record.get('location'))
                
                # Parse boolean flags
                dvflag = self._parse_boolean(record.get('dvflag'))
                firearmusedflag = self._parse_boolean(record.get('firearmusedflag'))
                
                # Parse age as integer
                age = self._parse_age(record.get('age'))
                
                transformed_record = {
                    'report': record.get('report'),
                    'report_date': report_date.isoformat() if report_date else None,
                    'reported_time': record.get('reported_time'),
                    'from_date': from_date.isoformat() if from_date else None,
                    'from_time': record.get('from_time'),
                    'to_date': to_date.isoformat() if to_date else None,
                    'to_time': record.get('to_time'),
                    'offense': record.get('offense'),
                    'ibrs': record.get('ibrs'),
                    'description': record.get('description'),
                    'beat': record.get('beat'),
                    'address': record.get('address'),
                    'city': record.get('city'),
                    'zipcode': record.get('zipcode'),
                    'rep_dist': record.get('rep_dist'),
                    'area': record.get('area'),
                    'involvement': record.get('involvement'),
                    'race': record.get('race'),
                    'sex': record.get('sex'),
                    'age': age,
                    'age_range': record.get('age_range'),
                    'dvflag': dvflag,
                    'firearmusedflag': firearmusedflag,
                    'latitude': latitude,
                    'longitude': longitude
                }
                
                # Validate coordinates
                if latitude and longitude:
                    if not self.validator.validate_coordinates(latitude, longitude):
                        self.logger.warning(f"Invalid coordinates for report {record.get('report')}: {latitude}, {longitude}")
                        transformed_record['latitude'] = None
                        transformed_record['longitude'] = None
                
                transformed.append(transformed_record)
                
            except Exception as e:
                self.logger.error(f"Error transforming record {record.get('report', 'unknown')}: {e}")
                skipped += 1
                continue
        
        self.logger.info(f"Transformation complete: {len(transformed):,} records, {skipped:,} skipped")
        return transformed
    
    def load_data(self, records: List[Dict]) -> Dict[str, int]:
        """Load transformed data into database"""
        self.logger.info("Loading crime data into database...")
        
        if not records:
            self.logger.warning("No records to load")
            return {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Create tables if they don't exist (only for crime table)
        self.db_helper.create_tables(drop_existing=False)
        
        # Load data using batch upsert
        stats = self.db_helper.batch_upsert(
            model_class=CrimeIncident,
            records=records,
            key_field='report',
            batch_size=1000
        )
        
        self.logger.info(f"Load complete: {stats['inserted']:,} inserted, {stats['updated']:,} updated, {stats['errors']:,} errors")
        return stats
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse datetime string from API"""
        if not date_str:
            return None
        
        try:
            # Handle various datetime formats from the API
            if 'T' in date_str:
                # ISO format: "2025-01-04T10:39:59.000"
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Date only: "2025-01-04"
                return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    def _extract_coordinates(self, location_data: Dict) -> tuple:
        """Extract latitude and longitude from location object"""
        if not location_data or not isinstance(location_data, dict):
            return None, None
        
        coordinates = location_data.get('coordinates', [])
        if len(coordinates) == 2:
            # API returns [longitude, latitude]
            longitude, latitude = coordinates
            return float(latitude), float(longitude)
        
        return None, None
    
    def _parse_boolean(self, value) -> bool:
        """Parse boolean value from API"""
        if value is None:
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'y')
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        return False
    
    def _parse_age(self, age_str) -> Optional[int]:
        """Parse age string to integer"""
        if not age_str:
            return None
        
        try:
            return int(age_str)
        except (ValueError, TypeError):
            return None
    
    def run_etl(self, limit: Optional[int] = None, 
                where_clause: Optional[str] = None) -> ETLStats:
        """Run complete ETL pipeline"""
        start_time = datetime.now()
        
        try:
            # Extract
            self.stats.start_time = start_time
            raw_data = self.extract_data(limit, where_clause)
            self.stats.records_extracted = len(raw_data)
            
            # Transform
            transform_start = datetime.now()
            transformed_data = self.transform_data(raw_data)
            self.stats.transform_time = (datetime.now() - transform_start).total_seconds()
            self.stats.records_transformed = len(transformed_data)
            
            # Load
            load_start = datetime.now()
            load_stats = self.load_data(transformed_data)
            self.stats.load_time = (datetime.now() - load_start).total_seconds()
            self.stats.records_loaded = load_stats['inserted'] + load_stats['updated']
            self.stats.load_errors = load_stats['errors']
            
            # Final stats
            self.stats.end_time = datetime.now()
            self.stats.total_time = (self.stats.end_time - self.stats.start_time).total_seconds()
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"ETL pipeline failed: {e}")
            raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Load Kansas City Crime Data')
    parser.add_argument('--initial', action='store_true', 
                       help='Initial load (recreate tables)')
    parser.add_argument('--limit', type=int, 
                       help='Limit number of records to process')
    parser.add_argument('--date-range', type=str, 
                       help='Date range filter (e.g., "2025-01-01 to 2025-01-31")')
    parser.add_argument('--incremental', action='store_true',
                       help='Incremental load (last 7 days)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Build where clause
    where_clause = None
    if args.date_range:
        start_date, end_date = args.date_range.split(' to ')
        where_clause = f"report_date between '{start_date}' and '{end_date}'"
    elif args.incremental:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        where_clause = f"report_date between '{start_date}' and '{end_date}'"
    
    # Run ETL
    etl = LoadCrimeData(verbose=args.verbose)
    
    try:
        stats = etl.run_etl(limit=args.limit, where_clause=where_clause)
        print_etl_summary(stats, "Crime Data")
        
        if stats.load_errors > 0:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
