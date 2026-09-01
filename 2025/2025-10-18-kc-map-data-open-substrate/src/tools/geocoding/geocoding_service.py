#!/usr/bin/env python3
"""
Geocoding Service

Main service class that orchestrates geocoding operations with caching,
rate limiting, and fallback between Census and Google Maps APIs.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .address_normalizer import AddressNormalizer, AddressComponents
from .census_geocoder import CensusGeocoder, GeocodingResult as CensusResult
from .google_geocoder import GoogleGeocoder, GeocodingResult as GoogleResult
from .rate_limiter import GeocodingRateLimiter
from .failed_geocoding_tracker import FailedGeocodingTracker

class GeocodingService:
    """Main geocoding service with caching and rate limiting"""
    
    def __init__(self, db_path: str, google_api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        self.db_path = db_path
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.normalizer = AddressNormalizer()
        self.rate_limiter = GeocodingRateLimiter(db_path)
        self.census_geocoder = CensusGeocoder(self.logger)
        self.google_geocoder = GoogleGeocoder(google_api_key, self.logger) if google_api_key else None
        self.failed_tracker = FailedGeocodingTracker(db_path)
        
        # Configuration
        self.fuzzy_threshold = 0.95  # Higher threshold to avoid matching different house numbers
        self.component_threshold = 0.7
        
        # Ensure database tables exist
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        # Import and run the cache creation script
        from ..database.create_geocoding_cache import create_geocoding_cache_table
        create_geocoding_cache_table(self.db_path)
    
    def geocode_address(self, address: str, source_priority: List[str] = None) -> Dict:
        """Geocode a single address with caching and fallback"""
        if not address or not address.strip():
            return {
                'success': False,
                'error': 'Empty address provided',
                'latitude': None,
                'longitude': None
            }
        
        if source_priority is None:
            source_priority = ['census', 'google']
        
        # Normalize address
        normalized_address = self.normalizer.normalize_address(address)
        address_hash = self.normalizer.generate_address_hash(normalized_address)
        
        # Check cache for exact match
        cached_result = self._check_cache_exact(address_hash)
        if cached_result:
            self._increment_cache_usage(cached_result['id'])
            return self._format_result(cached_result, from_cache=True)
        
        # Check cache for fuzzy match
        cached_result = self._check_cache_fuzzy(normalized_address)
        if cached_result:
            self._increment_cache_usage(cached_result['id'])
            return self._format_result(cached_result, from_cache=True)
        
        # Check cache for component match
        components = self.normalizer.parse_address(address)
        cached_result = self._check_cache_components(components)
        if cached_result:
            self._increment_cache_usage(cached_result['id'])
            return self._format_result(cached_result, from_cache=True)
        
        # Cache miss - geocode via API
        return self._geocode_and_cache(address, normalized_address, address_hash, components, source_priority)
    
    def _check_cache_exact(self, address_hash: str) -> Optional[Dict]:
        """Check cache for exact address hash match"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, original_address, normalized_address, latitude, longitude,
                       geocoding_source, geocoding_quality, confidence_score, match_type,
                       last_geocoded, times_used
                FROM geocoding_cache 
                WHERE address_hash = ?
            """, (address_hash,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'original_address': result[1],
                    'normalized_address': result[2],
                    'latitude': result[3],
                    'longitude': result[4],
                    'geocoding_source': result[5],
                    'geocoding_quality': result[6],
                    'confidence_score': result[7],
                    'match_type': result[8],
                    'last_geocoded': result[9],
                    'times_used': result[10]
                }
            return None
            
        finally:
            conn.close()
    
    def _check_cache_fuzzy(self, normalized_address: str) -> Optional[Dict]:
        """Check cache for fuzzy address match"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all cached addresses for comparison
            cursor.execute("""
                SELECT id, original_address, normalized_address, latitude, longitude,
                       geocoding_source, geocoding_quality, confidence_score, match_type,
                       last_geocoded, times_used
                FROM geocoding_cache 
                WHERE geocoding_quality IN ('high', 'medium')
            """)
            
            results = cursor.fetchall()
            
            best_match = None
            best_score = 0.0
            
            for result in results:
                cached_normalized = result[2]
                score = self.normalizer.fuzzy_match_score(normalized_address, cached_normalized)
                
                if score >= self.fuzzy_threshold and score > best_score:
                    best_score = score
                    best_match = {
                        'id': result[0],
                        'original_address': result[1],
                        'normalized_address': result[2],
                        'latitude': result[3],
                        'longitude': result[4],
                        'geocoding_source': result[5],
                        'geocoding_quality': result[6],
                        'confidence_score': result[7],
                        'match_type': result[8],
                        'last_geocoded': result[9],
                        'times_used': result[10],
                        'fuzzy_score': score
                    }
            
            return best_match
            
        finally:
            conn.close()
    
    def _check_cache_components(self, components: AddressComponents) -> Optional[Dict]:
        """Check cache for component-based match"""
        if not components.street_name or not components.city or not components.state:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Try exact component match first (including street number)
            cursor.execute("""
                SELECT id, original_address, normalized_address, latitude, longitude,
                       geocoding_source, geocoding_quality, confidence_score, match_type,
                       last_geocoded, times_used
                FROM geocoding_cache 
                WHERE street_number = ? AND street_name = ? AND city = ? AND state = ?
                ORDER BY confidence_score DESC, times_used DESC
                LIMIT 1
            """, (components.street_number, components.street_name, components.city, components.state))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'original_address': result[1],
                    'normalized_address': result[2],
                    'latitude': result[3],
                    'longitude': result[4],
                    'geocoding_source': result[5],
                    'geocoding_quality': result[6],
                    'confidence_score': result[7],
                    'match_type': result[8],
                    'last_geocoded': result[9],
                    'times_used': result[10]
                }
            
            # Try partial component match
            cursor.execute("""
                SELECT id, original_address, normalized_address, latitude, longitude,
                       geocoding_source, geocoding_quality, confidence_score, match_type,
                       last_geocoded, times_used, street_name, city, state
                FROM geocoding_cache 
                WHERE (street_name = ? OR city = ? OR state = ?)
                AND geocoding_quality = 'high'
            """, (components.street_name, components.city, components.state))
            
            results = cursor.fetchall()
            
            best_match = None
            best_score = 0.0
            
            for result in results:
                cached_components = AddressComponents(
                    street_name=result[11],
                    city=result[12],
                    state=result[13]
                )
                
                score = self.normalizer.component_match_score(components, cached_components)
                
                if score >= self.component_threshold and score > best_score:
                    best_score = score
                    best_match = {
                        'id': result[0],
                        'original_address': result[1],
                        'normalized_address': result[2],
                        'latitude': result[3],
                        'longitude': result[4],
                        'geocoding_source': result[5],
                        'geocoding_quality': result[6],
                        'confidence_score': result[7],
                        'match_type': result[8],
                        'last_geocoded': result[9],
                        'times_used': result[10],
                        'component_score': score
                    }
            
            return best_match
            
        finally:
            conn.close()
    
    def _geocode_and_cache(self, address: str, normalized_address: str, address_hash: str, 
                          components: AddressComponents, source_priority: List[str]) -> Dict:
        """Geocode address via API and cache the result"""
        
        self.logger.debug(f"Geocoding address: {address}")
        
        # Try each service in priority order
        for service in source_priority:
            if service == 'census' and self.rate_limiter.can_make_request('census'):
                self.logger.debug(f"Calling Census geocoder for: {address}")
                result = self.census_geocoder.geocode(address)
                self.logger.debug(f"Census result: {result.latitude}, {result.longitude}, error: {result.error_message}")
                if result.error_message is None:
                    self.rate_limiter.record_request('census', success=True)
                    return self._cache_and_format_result(address, normalized_address, address_hash, components, result)
                else:
                    self.rate_limiter.record_request('census', success=False)
                    self.logger.warning(f"Census geocoding failed: {result.error_message}")
            
            elif service == 'google' and self.google_geocoder and self.rate_limiter.can_make_request('google'):
                result = self.google_geocoder.geocode(address)
                if result.error_message is None:
                    self.rate_limiter.record_request('google', success=True)
                    return self._cache_and_format_result(address, normalized_address, address_hash, components, result)
                else:
                    self.rate_limiter.record_request('google', success=False)
                    self.logger.warning(f"Google geocoding failed: {result.error_message}")
        
        # All services failed - record the failure
        error_message = 'All geocoding services failed or rate limited'
        self.failed_tracker.record_failure(
            address=address,
            error_message=error_message,
            geocoding_source=None,
            normalized_address=normalized_address,
            address_components=components.__dict__ if components else None
        )
        
        return {
            'success': False,
            'error': error_message,
            'latitude': None,
            'longitude': None
        }
    
    def _cache_and_format_result(self, address: str, normalized_address: str, address_hash: str,
                                components: AddressComponents, result) -> Dict:
        """Cache geocoding result and return formatted response"""
        
        # Store in cache
        cache_id = self._store_in_cache(address, normalized_address, address_hash, components, result)
        
        # Format result
        formatted_result = self._format_result({
            'id': cache_id,
            'original_address': address,
            'normalized_address': normalized_address,
            'latitude': result.latitude,
            'longitude': result.longitude,
            'geocoding_source': result.source,
            'geocoding_quality': result.geocoding_quality,
            'confidence_score': result.confidence_score,
            'match_type': result.match_type,
            'last_geocoded': datetime.now().isoformat(),
            'times_used': 1
        }, from_cache=False)
        
        return formatted_result
    
    def _store_in_cache(self, address: str, normalized_address: str, address_hash: str,
                       components: AddressComponents, result) -> int:
        """Store geocoding result in cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO geocoding_cache (
                    original_address, normalized_address, address_hash,
                    street_number, street_name, city, state, zipcode,
                    latitude, longitude, geocoding_source, geocoding_quality,
                    confidence_score, match_type, last_geocoded, times_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                address, normalized_address, address_hash,
                components.street_number, components.street_name, components.city, 
                components.state, components.zipcode,
                result.latitude, result.longitude, result.source, result.geocoding_quality,
                result.confidence_score, result.match_type, datetime.now().isoformat(), 1
            ))
            
            cache_id = cursor.lastrowid
            conn.commit()
            return cache_id
            
        finally:
            conn.close()
    
    def _increment_cache_usage(self, cache_id: int):
        """Increment usage counter for cached result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE geocoding_cache 
                SET times_used = times_used + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (cache_id,))
            conn.commit()
        finally:
            conn.close()
    
    def _format_result(self, cached_result: Dict, from_cache: bool = False) -> Dict:
        """Format geocoding result for API response"""
        return {
            'success': True,
            'latitude': cached_result['latitude'],
            'longitude': cached_result['longitude'],
            'formatted_address': cached_result.get('normalized_address'),
            'confidence_score': cached_result['confidence_score'],
            'geocoding_quality': cached_result['geocoding_quality'],
            'match_type': cached_result['match_type'],
            'source': cached_result['geocoding_source'],
            'from_cache': from_cache,
            'times_used': cached_result.get('times_used', 1)
        }
    
    def batch_geocode(self, addresses: List[str], batch_size: int = 100) -> List[Dict]:
        """Geocode multiple addresses in batches"""
        results = []
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} addresses")
            
            for address in batch:
                result = self.geocode_address(address)
                results.append(result)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        from ..database.create_geocoding_cache import get_cache_stats
        return get_cache_stats(self.db_path)
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        return self.rate_limiter.get_all_usage_stats()
    
    def clear_cache(self, confirm: bool = False):
        """Clear the geocoding cache"""
        from ..database.create_geocoding_cache import clear_cache
        clear_cache(self.db_path, confirm)
    
    def get_failed_addresses(self, limit: int = 100, retry_count_threshold: int = 3) -> List[Dict]:
        """Get addresses that failed to geocode"""
        return self.failed_tracker.get_failed_addresses(limit, retry_count_threshold)
    
    def get_failure_stats(self) -> Dict:
        """Get statistics about failed geocoding attempts"""
        return self.failed_tracker.get_failure_stats()
    
    def retry_failed_addresses(self, limit: int = 50) -> Dict:
        """Retry geocoding failed addresses"""
        failed_addresses = self.get_failed_addresses(limit, retry_count_threshold=5)
        
        results = {
            'total_retried': len(failed_addresses),
            'successful': 0,
            'still_failed': 0,
            'errors': 0
        }
        
        for failure in failed_addresses:
            try:
                # Retry geocoding
                result = self.geocode_address(failure['original_address'])
                
                if result['success']:
                    results['successful'] += 1
                    # Remove from failed list since it succeeded
                    self.failed_tracker.delete_failure(failure['id'])
                else:
                    results['still_failed'] += 1
                    
            except Exception as e:
                results['errors'] += 1
                self.logger.error(f"Error retrying address {failure['original_address']}: {e}")
        
        return results

def test_geocoding_service():
    """Test the geocoding service"""
    import os
    
    # Create test database
    test_db = "test_geocoding.db"
    
    # Get Google API key if available
    google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Create service
    service = GeocodingService(test_db, google_api_key)
    
    test_addresses = [
        "123 Main St, Kansas City, MO 64101",
        "456 Oak Ave, Kansas City, MO 64102",
        "789 Broadway, Kansas City, MO",
        "123 Main St, Kansas City, MO 64101",  # Duplicate to test caching
    ]
    
    print("Testing Geocoding Service:")
    print("=" * 40)
    
    for address in test_addresses:
        print(f"\nGeocoding: {address}")
        result = service.geocode_address(address)
        
        if result['success']:
            print(f"  Coordinates: {result['latitude']}, {result['longitude']}")
            print(f"  Confidence: {result['confidence_score']:.1f}%")
            print(f"  Quality: {result['geocoding_quality']}")
            print(f"  Source: {result['source']}")
            print(f"  From Cache: {result['from_cache']}")
        else:
            print(f"  Error: {result['error']}")
    
    # Show stats
    print(f"\nCache Stats:")
    cache_stats = service.get_cache_stats()
    print(f"  Total cached: {cache_stats['total_cached']}")
    print(f"  High quality: {cache_stats['high_quality']}")
    print(f"  Average confidence: {cache_stats['avg_confidence']}%")
    
    print(f"\nUsage Stats:")
    usage_stats = service.get_usage_stats()
    print(f"  Total requests: {usage_stats['total_requests']}")
    print(f"  Overall success rate: {usage_stats['overall_success_rate']:.1f}%")
    
    # Clean up
    import os
    if os.path.exists(test_db):
        os.remove(test_db)

if __name__ == "__main__":
    test_geocoding_service()
