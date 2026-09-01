#!/usr/bin/env python3
"""
Failed Geocoding Tracker

Tracks addresses that failed to geocode for analysis and retry.
"""

import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class FailedGeocodingTracker:
    """Tracks failed geocoding attempts for analysis and retry"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_failed_geocoding_table()
    
    def _init_failed_geocoding_table(self):
        """Initialize failed geocoding table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failed_geocoding (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_address TEXT NOT NULL,
                    normalized_address TEXT,
                    error_message TEXT NOT NULL,
                    geocoding_source TEXT,
                    retry_count INTEGER DEFAULT 0,
                    last_attempt TEXT NOT NULL,
                    first_attempt TEXT NOT NULL,
                    address_components TEXT,  -- JSON string of parsed components
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_original_address ON failed_geocoding(original_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_normalized_address ON failed_geocoding(normalized_address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_error_message ON failed_geocoding(error_message)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_retry_count ON failed_geocoding(retry_count)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_failed_last_attempt ON failed_geocoding(last_attempt)")
            
            conn.commit()
        finally:
            conn.close()
    
    def record_failure(self, address: str, error_message: str, 
                      geocoding_source: str = None, normalized_address: str = None,
                      address_components: Dict = None) -> int:
        """Record a failed geocoding attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if this address has failed before
            cursor.execute("""
                SELECT id, retry_count FROM failed_geocoding 
                WHERE original_address = ?
            """, (address,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing failure record
                failure_id, retry_count = existing
                cursor.execute("""
                    UPDATE failed_geocoding 
                    SET error_message = ?, geocoding_source = ?, retry_count = retry_count + 1,
                        last_attempt = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (error_message, geocoding_source, datetime.now().isoformat(), failure_id))
                
                return failure_id
            else:
                # Create new failure record
                import json
                components_json = json.dumps(address_components) if address_components else None
                
                cursor.execute("""
                    INSERT INTO failed_geocoding (
                        original_address, normalized_address, error_message, 
                        geocoding_source, retry_count, last_attempt, first_attempt,
                        address_components
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    address, normalized_address, error_message, geocoding_source,
                    1, datetime.now().isoformat(), datetime.now().isoformat(), components_json
                ))
                
                failure_id = cursor.lastrowid
                conn.commit()
                return failure_id
                
        finally:
            conn.close()
    
    def get_failed_addresses(self, limit: int = 100, retry_count_threshold: int = 3) -> List[Dict]:
        """Get addresses that have failed geocoding"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, original_address, normalized_address, error_message,
                       geocoding_source, retry_count, last_attempt, first_attempt,
                       address_components
                FROM failed_geocoding 
                WHERE retry_count < ?
                ORDER BY last_attempt DESC
                LIMIT ?
            """, (retry_count_threshold, limit))
            
            results = cursor.fetchall()
            
            failed_addresses = []
            for row in results:
                import json
                components = json.loads(row[8]) if row[8] else None
                
                failed_addresses.append({
                    'id': row[0],
                    'original_address': row[1],
                    'normalized_address': row[2],
                    'error_message': row[3],
                    'geocoding_source': row[4],
                    'retry_count': row[5],
                    'last_attempt': row[6],
                    'first_attempt': row[7],
                    'address_components': components
                })
            
            return failed_addresses
            
        finally:
            conn.close()
    
    def get_failure_stats(self) -> Dict:
        """Get statistics about failed geocoding attempts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total failures
            cursor.execute("SELECT COUNT(*) FROM failed_geocoding")
            total_failures = cursor.fetchone()[0]
            
            # Failures by error type
            cursor.execute("""
                SELECT error_message, COUNT(*) as count
                FROM failed_geocoding 
                GROUP BY error_message
                ORDER BY count DESC
            """)
            error_breakdown = dict(cursor.fetchall())
            
            # Failures by source
            cursor.execute("""
                SELECT geocoding_source, COUNT(*) as count
                FROM failed_geocoding 
                WHERE geocoding_source IS NOT NULL
                GROUP BY geocoding_source
                ORDER BY count DESC
            """)
            source_breakdown = dict(cursor.fetchall())
            
            # Retry distribution
            cursor.execute("""
                SELECT retry_count, COUNT(*) as count
                FROM failed_geocoding 
                GROUP BY retry_count
                ORDER BY retry_count
            """)
            retry_distribution = dict(cursor.fetchall())
            
            # Recent failures (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM failed_geocoding 
                WHERE last_attempt >= date('now', '-7 days')
            """)
            recent_failures = cursor.fetchone()[0]
            
            return {
                'total_failures': total_failures,
                'recent_failures': recent_failures,
                'error_breakdown': error_breakdown,
                'source_breakdown': source_breakdown,
                'retry_distribution': retry_distribution
            }
            
        finally:
            conn.close()
    
    def mark_for_retry(self, failure_id: int) -> bool:
        """Mark a failed address for retry (resets retry count)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE failed_geocoding 
                SET retry_count = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (failure_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def delete_failure(self, failure_id: int) -> bool:
        """Delete a failed geocoding record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM failed_geocoding WHERE id = ?", (failure_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
            
        finally:
            conn.close()
    
    def clear_old_failures(self, days_old: int = 30) -> int:
        """Clear failed geocoding records older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM failed_geocoding 
                WHERE last_attempt < date('now', '-{} days')
            """.format(days_old))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
            
        finally:
            conn.close()

def test_failed_tracker():
    """Test the failed geocoding tracker"""
    import tempfile
    import os
    
    # Create test database
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()
    
    tracker = FailedGeocodingTracker(test_db.name)
    
    print("Testing Failed Geocoding Tracker:")
    print("=" * 40)
    
    # Record some failures
    tracker.record_failure(
        "Invalid Address 123",
        "No results found",
        "census",
        "INVALID ADDRESS 123",
        {"street_name": "INVALID", "city": "UNKNOWN"}
    )
    
    tracker.record_failure(
        "Another Bad Address",
        "Rate limit exceeded",
        "google"
    )
    
    # Get failure stats
    stats = tracker.get_failure_stats()
    print(f"Total failures: {stats['total_failures']}")
    print(f"Error breakdown: {stats['error_breakdown']}")
    
    # Get failed addresses
    failed = tracker.get_failed_addresses()
    print(f"Failed addresses: {len(failed)}")
    for failure in failed:
        print(f"  - {failure['original_address']}: {failure['error_message']}")
    
    # Clean up
    os.unlink(test_db.name)

if __name__ == "__main__":
    test_failed_tracker()
