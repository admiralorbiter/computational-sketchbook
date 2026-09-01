#!/usr/bin/env python3
"""
Geocoding Rate Limiter

Manages rate limiting and usage tracking for geocoding services
to stay within API limits and optimize costs.
"""

import sqlite3
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

class GeocodingRateLimiter:
    """Rate limiter for geocoding services"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_usage_table()
    
    def _init_usage_table(self):
        """Initialize usage tracking table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
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
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_usage_service_date 
                ON geocoding_usage(service_name, usage_date)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def can_make_request(self, service_name: str) -> bool:
        """Check if we can make a request to the specified service"""
        usage = self.get_daily_usage(service_name)
        
        if service_name == 'census':
            return usage['request_count'] < 1000
        elif service_name == 'google':
            return usage['request_count'] < 40000  # Monthly limit, but we check daily
        else:
            return True
    
    def record_request(self, service_name: str, success: bool = True):
        """Record a request to the specified service"""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current usage
            cursor.execute("""
                SELECT request_count, success_count, error_count 
                FROM geocoding_usage 
                WHERE service_name = ? AND usage_date = ?
            """, (service_name, today))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                request_count, success_count, error_count = result
                request_count += 1
                if success:
                    success_count += 1
                else:
                    error_count += 1
                
                cursor.execute("""
                    UPDATE geocoding_usage 
                    SET request_count = ?, success_count = ?, error_count = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE service_name = ? AND usage_date = ?
                """, (request_count, success_count, error_count, service_name, today))
            else:
                # Create new record
                request_count = 1
                success_count = 1 if success else 0
                error_count = 0 if success else 1
                
                cursor.execute("""
                    INSERT INTO geocoding_usage (service_name, usage_date, request_count, success_count, error_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (service_name, today, request_count, success_count, error_count))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def get_daily_usage(self, service_name: str) -> Dict:
        """Get daily usage statistics for a service"""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT request_count, success_count, error_count 
                FROM geocoding_usage 
                WHERE service_name = ? AND usage_date = ?
            """, (service_name, today))
            
            result = cursor.fetchone()
            
            if result:
                request_count, success_count, error_count = result
            else:
                request_count = success_count = error_count = 0
            
            # Get limits
            if service_name == 'census':
                daily_limit = 1000
            elif service_name == 'google':
                daily_limit = 40000  # Monthly limit, but we track daily
            else:
                daily_limit = 1000  # Default
            
            return {
                'service_name': service_name,
                'date': today,
                'request_count': request_count,
                'success_count': success_count,
                'error_count': error_count,
                'daily_limit': daily_limit,
                'remaining_requests': daily_limit - request_count,
                'success_rate': (success_count / request_count * 100) if request_count > 0 else 0,
                'within_limit': request_count < daily_limit,
                'approaching_limit': request_count >= daily_limit * 0.9
            }
            
        finally:
            conn.close()
    
    def get_usage_history(self, service_name: str, days: int = 30) -> list:
        """Get usage history for a service over the specified number of days"""
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT usage_date, request_count, success_count, error_count
                FROM geocoding_usage 
                WHERE service_name = ? AND usage_date >= ?
                ORDER BY usage_date DESC
            """, (service_name, start_date))
            
            results = cursor.fetchall()
            
            history = []
            for row in results:
                usage_date, request_count, success_count, error_count = row
                success_rate = (success_count / request_count * 100) if request_count > 0 else 0
                
                history.append({
                    'date': usage_date,
                    'request_count': request_count,
                    'success_count': success_count,
                    'error_count': error_count,
                    'success_rate': round(success_rate, 2)
                })
            
            return history
            
        finally:
            conn.close()
    
    def get_all_usage_stats(self) -> Dict:
        """Get usage statistics for all services"""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get today's usage for all services
            cursor.execute("""
                SELECT service_name, request_count, success_count, error_count
                FROM geocoding_usage 
                WHERE usage_date = ?
            """, (today,))
            
            results = cursor.fetchall()
            
            stats = {
                'date': today,
                'services': {},
                'total_requests': 0,
                'total_success': 0,
                'total_errors': 0
            }
            
            for service_name, request_count, success_count, error_count in results:
                # Get limits
                if service_name == 'census':
                    daily_limit = 1000
                elif service_name == 'google':
                    daily_limit = 40000
                else:
                    daily_limit = 1000
                
                success_rate = (success_count / request_count * 100) if request_count > 0 else 0
                
                stats['services'][service_name] = {
                    'request_count': request_count,
                    'success_count': success_count,
                    'error_count': error_count,
                    'daily_limit': daily_limit,
                    'remaining_requests': daily_limit - request_count,
                    'success_rate': round(success_rate, 2),
                    'within_limit': request_count < daily_limit,
                    'approaching_limit': request_count >= daily_limit * 0.9
                }
                
                stats['total_requests'] += request_count
                stats['total_success'] += success_count
                stats['total_errors'] += error_count
            
            # Calculate overall success rate
            if stats['total_requests'] > 0:
                stats['overall_success_rate'] = round(stats['total_success'] / stats['total_requests'] * 100, 2)
            else:
                stats['overall_success_rate'] = 0
            
            return stats
            
        finally:
            conn.close()
    
    def should_use_census(self) -> bool:
        """Determine if we should use Census API based on current usage"""
        census_usage = self.get_daily_usage('census')
        return census_usage['within_limit'] and not census_usage['approaching_limit']
    
    def should_use_google(self) -> bool:
        """Determine if we should use Google API based on current usage"""
        google_usage = self.get_daily_usage('google')
        return google_usage['within_limit'] and not google_usage['approaching_limit']
    
    def get_recommended_service(self) -> str:
        """Get the recommended service to use based on current usage"""
        if self.should_use_census():
            return 'census'
        elif self.should_use_google():
            return 'google'
        else:
            return 'none'  # Both services are at or near limits
    
    def reset_usage(self, service_name: str, date: str = None):
        """Reset usage for a service (for testing)"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM geocoding_usage 
                WHERE service_name = ? AND usage_date = ?
            """, (service_name, date))
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_old_usage(self, days_to_keep: int = 90):
        """Clean up old usage records to keep database size manageable"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM geocoding_usage 
                WHERE usage_date < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
            
        finally:
            conn.close()

def test_rate_limiter():
    """Test the rate limiter"""
    # Create a test database
    test_db = "test_geocoding_usage.db"
    
    limiter = GeocodingRateLimiter(test_db)
    
    print("Testing Rate Limiter:")
    print("=" * 30)
    
    # Test recording requests
    print("Recording some requests...")
    limiter.record_request('census', success=True)
    limiter.record_request('census', success=True)
    limiter.record_request('census', success=False)
    limiter.record_request('google', success=True)
    
    # Test getting usage stats
    print("\nCensus usage:")
    census_usage = limiter.get_daily_usage('census')
    print(f"  Requests: {census_usage['request_count']}")
    print(f"  Success: {census_usage['success_count']}")
    print(f"  Errors: {census_usage['error_count']}")
    print(f"  Success rate: {census_usage['success_rate']:.1f}%")
    print(f"  Within limit: {census_usage['within_limit']}")
    
    print("\nGoogle usage:")
    google_usage = limiter.get_daily_usage('google')
    print(f"  Requests: {google_usage['request_count']}")
    print(f"  Success: {google_usage['success_count']}")
    print(f"  Errors: {google_usage['error_count']}")
    print(f"  Success rate: {google_usage['success_rate']:.1f}%")
    print(f"  Within limit: {google_usage['within_limit']}")
    
    # Test service recommendation
    print(f"\nRecommended service: {limiter.get_recommended_service()}")
    
    # Test all usage stats
    print("\nAll usage stats:")
    all_stats = limiter.get_all_usage_stats()
    print(f"  Total requests: {all_stats['total_requests']}")
    print(f"  Overall success rate: {all_stats['overall_success_rate']:.1f}%")
    
    # Clean up
    import os
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    test_rate_limiter()
