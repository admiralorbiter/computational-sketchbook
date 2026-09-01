#!/usr/bin/env python3
"""
Shared ETL utilities for Kansas City Data Platform

Reusable components for all KC Open Data ETL pipelines:
- SODA 2 API client
- Progress tracking
- Logging system
- Data validation
- Database helpers
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from web.config import config

def setup_logging(name: str, log_file: str = 'etl.log', level=logging.INFO) -> logging.Logger:
    """Setup logging for ETL processes"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

@dataclass
class ETLStats:
    """Statistics tracking for ETL operations"""
    total_fetched: int = 0
    total_processed: int = 0
    total_inserted: int = 0
    total_updated: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        if self.total_processed == 0:
            return 0.0
        return (self.total_inserted + self.total_updated) / self.total_processed * 100

class SodaApiClient:
    """SODA 2 API client for KC Open Data"""
    
    def __init__(self, base_url: str = "https://data.kcmo.org/resource", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Kansas City Data Platform ETL/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Fetch data from SODA 2 API with error handling"""
        url = f"{self.base_url}/{endpoint}.json"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    def fetch_paginated(self, endpoint: str, limit: int = 1000, 
                       where_clause: str = None, order_by: str = None) -> Generator[List[Dict], None, None]:
        """Fetch data with pagination"""
        offset = 0
        params = {
            "$limit": limit,
            "$offset": offset
        }
        
        if where_clause:
            params["$where"] = where_clause
        if order_by:
            params["$order"] = order_by
        
        while True:
            params["$offset"] = offset
            data = self.fetch_data(endpoint, params)
            
            if not data:
                break
            
            yield data
            offset += limit
            
            # If we got fewer records than requested, we're done
            if len(data) < limit:
                break

class ProgressTracker:
    """Progress tracking with visual indicators"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        now = time.time()
        
        # Update display every 0.5 seconds
        if now - self.last_update >= 0.5 or self.current >= self.total:
            self._display_progress()
            self.last_update = now
    
    def _display_progress(self):
        """Display progress bar"""
        if self.total == 0:
            return
        
        percent = (self.current / self.total) * 100
        bar_length = 50
        filled_length = int(bar_length * self.current // self.total)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        
        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.0f}s"
        else:
            eta_str = "ETA: --"
        
        # Calculate rate
        rate = self.current / elapsed if elapsed > 0 else 0
        rate_str = f"{rate:.1f}/s"
        
        print(f"\r{self.description}: |{bar}| {percent:.1f}% ({self.current}/{self.total}) {rate_str} {eta_str}", end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete
    
    def complete(self):
        """Mark as complete"""
        self.current = self.total
        self._display_progress()

class Logger:
    """Structured logging for ETL operations"""
    
    def __init__(self, log_name: str, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler
        log_file = self.log_dir / f"{log_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class DataValidator:
    """Data validation utilities"""
    
    # Kansas City approximate bounds
    KC_BOUNDS = {
        'min_lat': 38.8,
        'max_lat': 39.3,
        'min_lon': -94.7,
        'max_lon': -94.4
    }
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate coordinates are within Kansas City area"""
        if lat is None or lon is None:
            return False
        
        bounds = DataValidator.KC_BOUNDS
        return (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
                bounds['min_lon'] <= lon <= bounds['max_lon'])
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support"""
        if not date_str:
            return None
        
        # Common date formats in KC data
        formats = [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def validate_required_fields(record: Dict, required_fields: List[str]) -> List[str]:
        """Validate required fields are present and not empty"""
        missing = []
        for field in required_fields:
            if field not in record or not record[field]:
                missing.append(field)
        return missing
    
    @staticmethod
    def clean_string(value: str) -> Optional[str]:
        """Clean string values"""
        if not value:
            return None
        return value.strip() or None
    
    @staticmethod
    def parse_location_field(location_str: str) -> tuple:
        """Parse location field to extract address and coordinates
        
        Expected format: "2612 E 26th St Kansas City MO (39.0789°, -94.55167°)"
        Returns: (address, latitude, longitude)
        """
        if not location_str:
            return None, None, None
        
        try:
            # Find coordinates in parentheses
            import re
            coord_pattern = r'\(([+-]?\d+\.?\d*°?),\s*([+-]?\d+\.?\d*°?)\)'
            coord_match = re.search(coord_pattern, location_str)
            
            if coord_match:
                # Extract coordinates
                lat_str = coord_match.group(1).replace('°', '').strip()
                lon_str = coord_match.group(2).replace('°', '').strip()
                
                try:
                    latitude = float(lat_str)
                    longitude = float(lon_str)
                except ValueError:
                    latitude = longitude = None
                
                # Extract address (everything before the parentheses)
                address = location_str[:coord_match.start()].strip()
                
                return address, latitude, longitude
            else:
                # No coordinates found, return the whole string as address
                return location_str.strip(), None, None
                
        except Exception:
            # If parsing fails, return the original string as address
            return location_str.strip(), None, None

class DatabaseHelper:
    """Database operations and connection management"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            config_name = os.environ.get('FLASK_ENV', 'development')
            app_config = config[config_name]
            database_url = app_config.DATABASE_URL
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = setup_logging("DatabaseHelper")
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self, drop_existing=False):
        """Create all tables without spatial extensions"""
        import sqlite3
        from pathlib import Path
        
        # Get database path
        db_path = self.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create tables using direct SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Only drop existing tables if explicitly requested
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS service_requests_311")
            cursor.execute("DROP TABLE IF EXISTS crime_incidents")
            cursor.execute("DROP TABLE IF EXISTS businesses")
            cursor.execute("DROP TABLE IF EXISTS dangerous_buildings")
        
        # Check which tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('service_requests_311', 'crime_incidents', 'businesses', 'dangerous_buildings')")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Create service_requests table only if it doesn't exist
        if 'service_requests_311' not in existing_tables:
            cursor.execute("""
                CREATE TABLE service_requests_311 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE NOT NULL,
                issue_type TEXT NOT NULL,
                issue_sub_type TEXT,
                current_status TEXT NOT NULL,
                open_date_time TEXT NOT NULL,
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
        
        # Create crime_incidents table only if it doesn't exist
        if 'crime_incidents' not in existing_tables:
            cursor.execute("""
                CREATE TABLE crime_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report TEXT UNIQUE NOT NULL,
                report_date TEXT NOT NULL,
                reported_time TEXT,
                from_date TEXT,
                from_time TEXT,
                to_date TEXT,
                to_time TEXT,
                offense TEXT NOT NULL,
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
        
        # Create businesses table only if it doesn't exist
        if 'businesses' not in existing_tables:
            cursor.execute("""
                CREATE TABLE businesses (
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
        
        # Create dangerous_buildings table only if it doesn't exist
        if 'dangerous_buildings' not in existing_tables:
            cursor.execute("""
                CREATE TABLE dangerous_buildings (
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
        
        # Create service_requests indexes only if table was just created
        if 'service_requests_311' not in existing_tables:
            cursor.execute("CREATE INDEX idx_request_id ON service_requests_311(request_id)")
            cursor.execute("CREATE INDEX idx_issue_type ON service_requests_311(issue_type)")
            cursor.execute("CREATE INDEX idx_current_status ON service_requests_311(current_status)")
            cursor.execute("CREATE INDEX idx_latitude ON service_requests_311(latitude)")
            cursor.execute("CREATE INDEX idx_longitude ON service_requests_311(longitude)")
            cursor.execute("CREATE INDEX idx_coords ON service_requests_311(latitude, longitude)")
        
        # Create crime_incidents indexes only if table was just created
        if 'crime_incidents' not in existing_tables:
            cursor.execute("CREATE INDEX idx_report ON crime_incidents(report)")
            cursor.execute("CREATE INDEX idx_report_date ON crime_incidents(report_date)")
            cursor.execute("CREATE INDEX idx_offense ON crime_incidents(offense)")
            cursor.execute("CREATE INDEX idx_ibrs ON crime_incidents(ibrs)")
            cursor.execute("CREATE INDEX idx_area ON crime_incidents(area)")
            cursor.execute("CREATE INDEX idx_dvflag ON crime_incidents(dvflag)")
            cursor.execute("CREATE INDEX idx_firearmusedflag ON crime_incidents(firearmusedflag)")
            cursor.execute("CREATE INDEX idx_crime_latitude ON crime_incidents(latitude)")
            cursor.execute("CREATE INDEX idx_crime_longitude ON crime_incidents(longitude)")
            cursor.execute("CREATE INDEX idx_crime_coords ON crime_incidents(latitude, longitude)")
        
        # Create businesses indexes only if table was just created
        if 'businesses' not in existing_tables:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_name ON businesses(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_type ON businesses(business_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON businesses(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_id ON businesses(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_industry ON businesses(industry)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON businesses(city)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON businesses(state)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_latitude ON businesses(latitude)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_longitude ON businesses(longitude)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_coords ON businesses(latitude, longitude)")
        
        # Create dangerous_buildings indexes only if table was just created
        if 'dangerous_buildings' not in existing_tables:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_number ON dangerous_buildings(case_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_address ON dangerous_buildings(address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON dangerous_buildings(city)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_state ON dangerous_buildings(state)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_opened ON dangerous_buildings(case_opened)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_of_case ON dangerous_buildings(status_of_case)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pin ON dangerous_buildings(pin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_council_district ON dangerous_buildings(council_district)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dangerous_latitude ON dangerous_buildings(latitude)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dangerous_longitude ON dangerous_buildings(longitude)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dangerous_coords ON dangerous_buildings(latitude, longitude)")
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database tables created successfully (without spatial extensions)")
    
    def batch_upsert(self, model_class, records: List[Dict], 
                    key_field: str = 'request_id', batch_size: int = 1000) -> Dict[str, int]:
        """Batch upsert records using direct SQLite"""
        import sqlite3
        from pathlib import Path
        
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Get database path
        db_path = self.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Determine table name and field mappings based on model
        if model_class.__name__ == 'ServiceRequest':
            table_name = 'service_requests_311'
            key_field = 'request_id'
        elif model_class.__name__ == 'CrimeIncident':
            table_name = 'crime_incidents'
            key_field = 'report'
        elif model_class.__name__ == 'Business':
            table_name = 'businesses'
            key_field = 'source_id'
        elif model_class.__name__ == 'DangerousBuilding':
            table_name = 'dangerous_buildings'
            key_field = 'case_number'
        else:
            raise ValueError(f"Unsupported model class: {model_class.__name__}")
        
        try:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                for record in batch:
                    try:
                        # Check if record exists
                        cursor.execute(f"SELECT id FROM {table_name} WHERE {key_field} = ?", (record[key_field],))
                        existing = cursor.fetchone()
                        
                        if table_name == 'service_requests_311':
                            if existing:
                                # Update existing service request
                                cursor.execute("""
                                    UPDATE service_requests_311 SET
                                        issue_type = ?, issue_sub_type = ?, current_status = ?,
                                        open_date_time = ?, resolved_date = ?, last_updated = ?,
                                        days_to_close = ?, incident_address = ?, council_district = ?,
                                        department_work_group = ?, report_source = ?, source_category = ?,
                                        workorder_ = ?, additional_questions = ?, latitude = ?, longitude = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE request_id = ?
                                """, (
                                    record.get('issue_type'), record.get('issue_sub_type'), record.get('current_status'),
                                    record.get('open_date_time'), record.get('resolved_date'), record.get('last_updated'),
                                    record.get('days_to_close'), record.get('incident_address'), record.get('council_district'),
                                    record.get('department_work_group'), record.get('report_source'), record.get('source_category'),
                                    record.get('workorder_'), record.get('additional_questions'), record.get('latitude'), record.get('longitude'),
                                    record[key_field]
                                ))
                                stats['updated'] += 1
                            else:
                                # Insert new service request
                                cursor.execute("""
                                    INSERT INTO service_requests_311 (
                                        request_id, issue_type, issue_sub_type, current_status,
                                        open_date_time, resolved_date, last_updated, days_to_close,
                                        incident_address, council_district, department_work_group,
                                        report_source, source_category, workorder_, additional_questions,
                                        latitude, longitude
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    record.get('request_id'), record.get('issue_type'), record.get('issue_sub_type'), record.get('current_status'),
                                    record.get('open_date_time'), record.get('resolved_date'), record.get('last_updated'), record.get('days_to_close'),
                                    record.get('incident_address'), record.get('council_district'), record.get('department_work_group'),
                                    record.get('report_source'), record.get('source_category'), record.get('workorder_'), record.get('additional_questions'),
                                    record.get('latitude'), record.get('longitude')
                                ))
                                stats['inserted'] += 1
                        
                        elif table_name == 'crime_incidents':
                            if existing:
                                # Update existing crime incident
                                cursor.execute("""
                                    UPDATE crime_incidents SET
                                        report_date = ?, reported_time = ?, from_date = ?, from_time = ?,
                                        to_date = ?, to_time = ?, offense = ?, ibrs = ?, description = ?,
                                        beat = ?, address = ?, city = ?, zipcode = ?, rep_dist = ?, area = ?,
                                        involvement = ?, race = ?, sex = ?, age = ?, age_range = ?,
                                        dvflag = ?, firearmusedflag = ?, latitude = ?, longitude = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE report = ?
                                """, (
                                    record.get('report_date'), record.get('reported_time'), record.get('from_date'), record.get('from_time'),
                                    record.get('to_date'), record.get('to_time'), record.get('offense'), record.get('ibrs'), record.get('description'),
                                    record.get('beat'), record.get('address'), record.get('city'), record.get('zipcode'), record.get('rep_dist'), record.get('area'),
                                    record.get('involvement'), record.get('race'), record.get('sex'), record.get('age'), record.get('age_range'),
                                    record.get('dvflag'), record.get('firearmusedflag'), record.get('latitude'), record.get('longitude'),
                                    record[key_field]
                                ))
                                stats['updated'] += 1
                            else:
                                # Insert new crime incident
                                cursor.execute("""
                                    INSERT INTO crime_incidents (
                                        report, report_date, reported_time, from_date, from_time,
                                        to_date, to_time, offense, ibrs, description,
                                        beat, address, city, zipcode, rep_dist, area,
                                        involvement, race, sex, age, age_range,
                                        dvflag, firearmusedflag, latitude, longitude
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    record.get('report'), record.get('report_date'), record.get('reported_time'), record.get('from_date'), record.get('from_time'),
                                    record.get('to_date'), record.get('to_time'), record.get('offense'), record.get('ibrs'), record.get('description'),
                                    record.get('beat'), record.get('address'), record.get('city'), record.get('zipcode'), record.get('rep_dist'), record.get('area'),
                                    record.get('involvement'), record.get('race'), record.get('sex'), record.get('age'), record.get('age_range'),
                                    record.get('dvflag'), record.get('firearmusedflag'), record.get('latitude'), record.get('longitude')
                                ))
                                stats['inserted'] += 1
                        
                        elif table_name == 'businesses':
                            if existing:
                                # Update existing business
                                cursor.execute("""
                                    UPDATE businesses SET
                                        name = ?, business_type = ?, description = ?, industry = ?,
                                        address = ?, city = ?, state = ?, zipcode = ?,
                                        source = ?, dba_name = ?, valid_license_for = ?,
                                        place_id = ?, place_type = ?, latitude = ?, longitude = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE source_id = ?
                                """, (
                                    record.get('name'), record.get('business_type'), record.get('description'), record.get('industry'),
                                    record.get('address'), record.get('city'), record.get('state'), record.get('zipcode'),
                                    record.get('source'), record.get('dba_name'), record.get('valid_license_for'),
                                    record.get('place_id'), record.get('place_type'), record.get('latitude'), record.get('longitude'),
                                    record[key_field]
                                ))
                                stats['updated'] += 1
                            else:
                                # Insert new business
                                cursor.execute("""
                                    INSERT INTO businesses (
                                        name, business_type, description, industry,
                                        address, city, state, zipcode,
                                        source, source_id, dba_name, valid_license_for,
                                        place_id, place_type, latitude, longitude
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    record.get('name'), record.get('business_type'), record.get('description'), record.get('industry'),
                                    record.get('address'), record.get('city'), record.get('state'), record.get('zipcode'),
                                    record.get('source'), record.get('source_id'), record.get('dba_name'), record.get('valid_license_for'),
                                    record.get('place_id'), record.get('place_type'), record.get('latitude'), record.get('longitude')
                                ))
                                stats['inserted'] += 1
                        
                        elif table_name == 'dangerous_buildings':
                            if existing:
                                # Update existing dangerous building
                                cursor.execute("""
                                    UPDATE dangerous_buildings SET
                                        address = ?, city = ?, state = ?, zipcode = ?,
                                        case_opened = ?, status_of_case = ?, pin = ?, council_district = ?,
                                        latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
                                    WHERE case_number = ?
                                """, (
                                    record.get('address'), record.get('city'), record.get('state'), record.get('zipcode'),
                                    record.get('case_opened'), record.get('status_of_case'), record.get('pin'), record.get('council_district'),
                                    record.get('latitude'), record.get('longitude'), record[key_field]
                                ))
                                stats['updated'] += 1
                            else:
                                # Insert new dangerous building
                                cursor.execute("""
                                    INSERT INTO dangerous_buildings (
                                        case_number, address, city, state, zipcode,
                                        case_opened, status_of_case, pin, council_district,
                                        latitude, longitude
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    record.get('case_number'), record.get('address'), record.get('city'), record.get('state'), record.get('zipcode'),
                                    record.get('case_opened'), record.get('status_of_case'), record.get('pin'), record.get('council_district'),
                                    record.get('latitude'), record.get('longitude')
                                ))
                                stats['inserted'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error processing record {record.get(key_field, 'unknown')}: {e}")
                        stats['errors'] += 1
                
                conn.commit()
                
        finally:
            conn.close()
                
        return stats
    
    def batch_upsert_landbank(self, records: List[Dict], batch_size: int = 1000) -> Dict[str, int]:
        """Batch upsert Land Bank records using direct SQLite"""
        import sqlite3
        
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        # Get database path
        db_path = self.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                for record in batch:
                    try:
                        # Check if record exists
                        cursor.execute("SELECT id FROM landbank_properties WHERE parcel_number = ?", (record['parcel_number'],))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing record
                            cursor.execute("""
                                UPDATE landbank_properties SET
                                    address = ?, city = ?, state = ?, postal_code = ?,
                                    city_council_district = ?, county = ?, date_of_acquisition = ?,
                                    demo_needed = ?, inventory_type = ?, market_value = ?,
                                    market_value_year = ?, neighborhood = ?, property_class = ?,
                                    property_condition = ?, property_status = ?, school_district = ?,
                                    square_footage = ?, zoned_as = ?, latitude = ?, longitude = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE parcel_number = ?
                            """, (
                                record.get('address'), record.get('city'), record.get('state'), record.get('postal_code'),
                                record.get('city_council_district'), record.get('county'), record.get('date_of_acquisition'),
                                record.get('demo_needed'), record.get('inventory_type'), record.get('market_value'),
                                record.get('market_value_year'), record.get('neighborhood'), record.get('property_class'),
                                record.get('property_condition'), record.get('property_status'), record.get('school_district'),
                                record.get('square_footage'), record.get('zoned_as'), record.get('latitude'), record.get('longitude'),
                                record['parcel_number']
                            ))
                            stats['updated'] += 1
                        else:
                            # Insert new record
                            cursor.execute("""
                                INSERT INTO landbank_properties (
                                    address, city, state, postal_code, city_council_district,
                                    county, date_of_acquisition, demo_needed, inventory_type,
                                    market_value, market_value_year, neighborhood, parcel_number,
                                    property_class, property_condition, property_status,
                                    school_district, square_footage, zoned_as, latitude, longitude
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                record.get('address'), record.get('city'), record.get('state'), record.get('postal_code'),
                                record.get('city_council_district'), record.get('county'), record.get('date_of_acquisition'),
                                record.get('demo_needed'), record.get('inventory_type'), record.get('market_value'),
                                record.get('market_value_year'), record.get('neighborhood'), record.get('parcel_number'),
                                record.get('property_class'), record.get('property_condition'), record.get('property_status'),
                                record.get('school_district'), record.get('square_footage'), record.get('zoned_as'),
                                record.get('latitude'), record.get('longitude')
                            ))
                            stats['inserted'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error processing record {record.get('parcel_number', 'unknown')}: {e}")
                        stats['errors'] += 1
                
                conn.commit()
                
        finally:
            conn.close()
                
        return stats
    
    def get_table_count(self, table_name: str) -> int:
        """Get count of records in table"""
        with self.get_session() as session:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    
    def geocode_missing_coordinates(self, model_class, batch_size: int = 100) -> Dict[str, int]:
        """Find records without coordinates and geocode them"""
        from tools.geocoding.geocoding_service import GeocodingService
        import os
        import sqlite3
        
        # Get database path
        db_path = self.engine.url.database
        if not db_path:
            db_path = "data/processed/kc_data.gpkg"
        
        # Get Google API key
        google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        
        # Initialize geocoding service
        geocoding_service = GeocodingService(db_path, google_api_key)
        
        # Determine table name and address field based on model
        if model_class.__name__ == 'ServiceRequest':
            table_name = 'service_requests_311'
            address_field = 'incident_address'
            lat_field = 'latitude'
            lon_field = 'longitude'
        elif model_class.__name__ == 'CrimeIncident':
            table_name = 'crime_incidents'
            address_field = 'address'
            lat_field = 'latitude'
            lon_field = 'longitude'
        elif model_class.__name__ == 'Business':
            table_name = 'businesses'
            address_field = 'address'
            lat_field = 'latitude'
            lon_field = 'longitude'
        elif model_class.__name__ == 'DangerousBuilding':
            table_name = 'dangerous_buildings'
            address_field = 'address'
            lat_field = 'latitude'
            lon_field = 'longitude'
        else:
            raise ValueError(f"Unsupported model class: {model_class.__name__}")
        
        # Find records without coordinates but with addresses
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Get records that need geocoding
            cursor.execute(f"""
                SELECT id, {address_field}
                FROM {table_name}
                WHERE ({lat_field} IS NULL OR {lon_field} IS NULL)
                AND {address_field} IS NOT NULL
                AND {address_field} != ''
                LIMIT ?
            """, (batch_size,))
            
            records_to_geocode = cursor.fetchall()
            
            if not records_to_geocode:
                return {'geocoded': 0, 'errors': 0, 'skipped': 0}
            
            self.logger.info(f"Found {len(records_to_geocode)} records to geocode")
            
            geocoded = 0
            errors = 0
            skipped = 0
            
            for record_id, address in records_to_geocode:
                try:
                    # Geocode the address
                    result = geocoding_service.geocode_address(address)
                    
                    if result['success']:
                        # Update the record with coordinates
                        cursor.execute(f"""
                            UPDATE {table_name}
                            SET {lat_field} = ?, {lon_field} = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (result['latitude'], result['longitude'], record_id))
                        
                        geocoded += 1
                        self.logger.debug(f"Geocoded record {record_id}: {address}")
                    else:
                        errors += 1
                        self.logger.warning(f"Failed to geocode record {record_id}: {address} - {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    errors += 1
                    self.logger.error(f"Error geocoding record {record_id}: {e}")
            
            conn.commit()
            
            self.logger.info(f"Geocoding complete: {geocoded} geocoded, {errors} errors")
            
            return {
                'geocoded': geocoded,
                'errors': errors,
                'skipped': skipped
            }
            
        finally:
            conn.close()

def create_point_geometry(lat: float, lon: float) -> str:
    """Create WKT POINT geometry from lat/lon"""
    if lat is None or lon is None:
        return None
    return f"POINT({lon} {lat})"

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def print_etl_summary(stats: ETLStats, dataset_name: str):
    """Print ETL summary statistics"""
    print(f"\n{dataset_name} ETL Complete!")
    print("=" * 50)
    print(f"Summary:")
    print(f"   - Total fetched: {stats.total_fetched:,}")
    print(f"   - Total processed: {stats.total_processed:,}")
    print(f"   - Inserted (new): {stats.total_inserted:,}")
    print(f"   - Updated (existing): {stats.total_updated:,}")
    print(f"   - Skipped (errors): {stats.total_skipped:,}")
    print(f"   - Success rate: {stats.success_rate:.1f}%")
    if stats.duration:
        print(f"   - Duration: {format_duration(stats.duration)}")
    print()
