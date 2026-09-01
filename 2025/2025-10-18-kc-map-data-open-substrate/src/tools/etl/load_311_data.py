#!/usr/bin/env python3
"""
311 Service Request Data ETL Pipeline

Loads 311 service request data from Kansas City Open Data into the database.
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
from web.models import ServiceRequest

class Load311Data:
    """311 Service Request Data ETL Pipeline"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = Logger("311_etl")
        self.api_client = SodaApiClient()
        self.db_helper = DatabaseHelper()
        self.validator = DataValidator()
        self.stats = ETLStats()
        
        # Required fields for 311 data
        self.required_fields = ['reported_issue', 'current_status', 'open_date_time']
    
    def extract_data(self, limit: Optional[int] = None, 
                    where_clause: Optional[str] = None) -> List[Dict]:
        """Extract data from KC Open Data 311 API"""
        self.logger.info("Extracting data from KC Open Data...")
        
        endpoint = "d4px-6rwg"  # 311 Call Center Reported Issues
        order_by = "open_date_time DESC"
        
        all_records = []
        
        try:
            if limit:
                # Single request with limit
                params = {"$limit": limit, "$order": order_by}
                if where_clause:
                    params["$where"] = where_clause
                
                records = self.api_client.fetch_data(endpoint, params)
                all_records.extend(records)
                self.logger.info(f"   Fetched {len(records)} records (limit: {limit})")
            else:
                # Paginated requests
                page_count = 0
                for page_records in self.api_client.fetch_paginated(
                    endpoint, where_clause=where_clause, order_by=order_by
                ):
                    all_records.extend(page_records)
                    page_count += 1
                    self.logger.info(f"   Page {page_count}: {len(page_records)} records")
        
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise
        
        self.stats.total_fetched = len(all_records)
        self.logger.info(f"   Total fetched: {len(all_records):,} records")
        return all_records
    
    def transform_record(self, record: Dict) -> Optional[Dict]:
        """Transform API record to database model format"""
        try:
            # Validate required fields
            missing_fields = self.validator.validate_required_fields(record, self.required_fields)
            if missing_fields:
                self.logger.warning(f"Skipping record {record.get('reported_issue', 'unknown')}: missing fields {missing_fields}")
                return None
            
            # Parse dates
            open_date = self.validator.parse_date(record.get('open_date_time'))
            resolved_date = self.validator.parse_date(record.get('resolved_date'))
            last_updated = self.validator.parse_date(record.get('last_updated'))
            
            if not open_date:
                self.logger.warning(f"Skipping record {record['reported_issue']}: invalid open_date_time")
                return None
            
            # Parse coordinates
            lat = None
            lon = None
            geometry = None
            
            if record.get('latitude') and record.get('longitude'):
                try:
                    lat = float(record['latitude'])
                    lon = float(record['longitude'])
                    
                    # Validate coordinates are within KC area
                    if self.validator.validate_coordinates(lat, lon):
                        geometry = create_point_geometry(lat, lon)
                    else:
                        self.logger.warning(f"Coordinates outside KC area for record {record['reported_issue']}: {lat}, {lon}")
                        lat = lon = None
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid coordinates for record {record['reported_issue']}: {record.get('latitude')}, {record.get('longitude')}")
            
            # Parse days_to_close
            days_to_close = None
            if record.get('days_to_close'):
                try:
                    days_to_close = int(record['days_to_close'])
                except (ValueError, TypeError):
                    pass
            
            # Transform to database format
            transformed = {
                'request_id': record['reported_issue'],
                'issue_type': self.validator.clean_string(record.get('issue_type')),
                'issue_sub_type': self.validator.clean_string(record.get('issue_sub_type')),
                'current_status': record['current_status'],
                'open_date_time': open_date,
                'resolved_date': resolved_date,
                'last_updated': last_updated,
                'days_to_close': days_to_close,
                'incident_address': self.validator.clean_string(record.get('incident_address')),
                'council_district': self.validator.clean_string(record.get('council_district')),
                'department_work_group': self.validator.clean_string(record.get('department_work_group')),
                'report_source': self.validator.clean_string(record.get('report_source')),
                'source_category': self.validator.clean_string(record.get('source_category')),
                'workorder_': self.validator.clean_string(record.get('workorder_')),
                'additional_questions': self.validator.clean_string(record.get('additional_questions')),
                'latitude': lat,
                'longitude': lon,
                'geometry': geometry,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming record {record.get('reported_issue', 'unknown')}: {e}")
            return None
    
    def transform_data(self, records: List[Dict]) -> List[Dict]:
        """Transform all records"""
        self.logger.info("Transforming data...")
        
        transformed_records = []
        progress = ProgressTracker(len(records), "Transforming")
        
        for record in records:
            transformed = self.transform_record(record)
            if transformed:
                transformed_records.append(transformed)
                self.stats.total_processed += 1
            else:
                self.stats.total_skipped += 1
            
            progress.update()
        
        progress.complete()
        
        # Log transformation stats
        with_coords = sum(1 for r in transformed_records if r.get('latitude') and r.get('longitude'))
        without_coords = len(transformed_records) - with_coords
        
        self.logger.info(f"   Processed: {len(transformed_records):,} records")
        self.logger.info(f"   With coordinates: {with_coords:,} ({with_coords/len(transformed_records)*100:.1f}%)")
        self.logger.info(f"   Without coordinates: {without_coords:,} ({without_coords/len(transformed_records)*100:.1f}%)")
        
        return transformed_records
    
    def load_data(self, records: List[Dict]) -> Dict[str, int]:
        """Load records into database"""
        self.logger.info("Loading into database...")
        
        progress = ProgressTracker(len(records), "Loading")
        
        # Use batch upsert for performance
        load_stats = self.db_helper.batch_upsert(
            ServiceRequest, 
            records, 
            key_field='request_id',
            batch_size=1000
        )
        
        progress.complete()
        
        self.stats.total_inserted = load_stats['inserted']
        self.stats.total_updated = load_stats['updated']
        self.stats.total_errors += load_stats['errors']
        
        self.logger.info(f"   Inserted (new): {load_stats['inserted']:,}")
        self.logger.info(f"   Updated (existing): {load_stats['updated']:,}")
        self.logger.info(f"   Errors: {load_stats['errors']:,}")
        
        return load_stats
    
    def run_etl(self, limit: Optional[int] = None, 
                where_clause: Optional[str] = None) -> ETLStats:
        """Run complete ETL pipeline"""
        self.stats.start_time = datetime.now()
        
        try:
            # Extract
            records = self.extract_data(limit, where_clause)
            
            if not records:
                self.logger.warning("No records found to process")
                return self.stats
            
            # Transform
            transformed_records = self.transform_data(records)
            
            if not transformed_records:
                self.logger.warning("No valid records after transformation")
                return self.stats
            
            # Load
            self.load_data(transformed_records)
            
        except Exception as e:
            self.logger.error(f"ETL pipeline failed: {e}")
            raise
        finally:
            self.stats.end_time = datetime.now()
        
        return self.stats

def create_date_filter(days: int = None, from_date: str = None, to_date: str = None) -> str:
    """Create SODA where clause for date filtering"""
    if days:
        # Last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return f"open_date_time >= '{start_date.strftime('%Y-%m-%d')}'"
    
    elif from_date and to_date:
        # Specific date range
        return f"open_date_time >= '{from_date}' AND open_date_time <= '{to_date}'"
    
    elif from_date:
        # From specific date
        return f"open_date_time >= '{from_date}'"
    
    elif to_date:
        # Until specific date
        return f"open_date_time <= '{to_date}'"
    
    return None

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Load 311 service request data from KC Open Data")
    
    # Operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--initial", action="store_true", help="Initial load (all data)")
    group.add_argument("--update", action="store_true", help="Incremental update")
    group.add_argument("--test", action="store_true", help="Test with small dataset")
    
    # Date filtering
    parser.add_argument("--days", type=int, help="Number of days for incremental update")
    parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")
    
    # Other options
    parser.add_argument("--limit", type=int, help="Limit number of records to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be loaded without actually loading")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Create ETL instance
    etl = Load311Data(verbose=args.verbose)
    
    # Create database tables if they don't exist
    etl.logger.info("Setting up database...")
    # Always use drop_existing=False to preserve other tables
    etl.db_helper.create_tables(drop_existing=False)
    etl.logger.info("   Database ready")
    
    # Determine operation
    if args.initial:
        etl.logger.info("Starting initial load of 311 data...")
        where_clause = None
        limit = args.limit
        
    elif args.update:
        etl.logger.info("Starting incremental update...")
        where_clause = create_date_filter(days=args.days, from_date=args.from_date, to_date=args.to_date)
        limit = args.limit
        
    elif args.test:
        etl.logger.info("Starting test load...")
        where_clause = None
        limit = args.limit or 100
    
    # Dry run mode
    if args.dry_run:
        etl.logger.info("DRY RUN MODE - No data will be loaded")
        records = etl.extract_data(limit, where_clause)
        etl.logger.info(f"Would process {len(records)} records")
        return
    
    # Run ETL
    try:
        stats = etl.run_etl(limit, where_clause)
        print_etl_summary(stats, "311 Service Requests")
        
    except KeyboardInterrupt:
        etl.logger.info("ETL interrupted by user")
        sys.exit(1)
    except Exception as e:
        etl.logger.error(f"ETL failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
