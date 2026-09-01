#!/usr/bin/env python3
"""
Google Maps Geocoding API Client

Handles geocoding requests to Google Maps Geocoding API
with rate limiting, retry logic, and error handling.
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class GeocodingResult:
    """Geocoding result with metadata"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
    confidence_score: float = 0.0
    geocoding_quality: str = "low"
    match_type: str = "unknown"
    source: str = "google"
    error_message: Optional[str] = None

class GoogleGeocoder:
    """Google Maps Geocoding API client"""
    
    BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    TIMEOUT = 30  # seconds
    
    def __init__(self, api_key: str, logger: Optional[logging.Logger] = None):
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Kansas City Data Platform Geocoding Service/1.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting tracking
        self.monthly_requests = 0
        self.last_reset_date = datetime.now().replace(day=1)  # First day of current month
        self.monthly_limit = 40000  # Free tier limit
        self.limit_threshold = 0.9  # Switch at 90% of limit
    
    def geocode(self, address: str) -> GeocodingResult:
        """Geocode a single address using Google Maps API"""
        
        # Check rate limits
        if not self._check_rate_limit():
            return GeocodingResult(
                error_message="Monthly rate limit exceeded",
                source="google"
            )
        
        # Prepare request
        params = {
            'address': address,
            'key': self.api_key,
            'region': 'us-mo',  # Bias towards Missouri
            'components': 'country:US'  # Restrict to US addresses
        }
        
        # Make request with retries
        for attempt in range(self.MAX_RETRIES):
            try:
                self.logger.debug(f"Geocoding address (attempt {attempt + 1}): {address}")
                
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.TIMEOUT
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    self.logger.warning("Rate limited by Google Maps API")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY * (2 ** attempt))
                        continue
                    else:
                        return GeocodingResult(
                            error_message="Rate limited by Google Maps API",
                            source="google"
                        )
                
                response.raise_for_status()
                data = response.json()
                
                # Check for API errors
                if data.get('status') != 'OK':
                    error_message = self._get_error_message(data)
                    return GeocodingResult(
                        error_message=error_message,
                        source="google"
                    )
                
                # Parse response
                result = self._parse_response(data, address)
                self.monthly_requests += 1
                
                self.logger.debug(f"Geocoding successful: {result}")
                return result
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout geocoding address: {address}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                    continue
                else:
                    return GeocodingResult(
                        error_message="Request timeout",
                        source="google"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error geocoding address {address}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                    continue
                else:
                    return GeocodingResult(
                        error_message=f"Request error: {str(e)}",
                        source="google"
                    )
                    
            except Exception as e:
                self.logger.error(f"Unexpected error geocoding address {address}: {e}")
                return GeocodingResult(
                    error_message=f"Unexpected error: {str(e)}",
                    source="google"
                )
        
        return GeocodingResult(
            error_message="Max retries exceeded",
            source="google"
        )
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_date = datetime.now()
        current_month_start = current_date.replace(day=1)
        
        # Reset monthly counter if it's a new month
        if current_month_start != self.last_reset_date:
            self.monthly_requests = 0
            self.last_reset_date = current_month_start
        
        # Check if we're approaching the limit
        if self.monthly_requests >= self.monthly_limit * self.limit_threshold:
            self.logger.warning(f"Approaching Google Maps API monthly limit: {self.monthly_requests}/{self.monthly_limit}")
            return False
        
        return self.monthly_requests < self.monthly_limit
    
    def _get_error_message(self, data: Dict) -> str:
        """Extract error message from Google API response"""
        status = data.get('status', 'UNKNOWN_ERROR')
        error_message = data.get('error_message', '')
        
        error_messages = {
            'ZERO_RESULTS': 'No results found for this address',
            'OVER_DAILY_LIMIT': 'Daily quota exceeded',
            'OVER_QUERY_LIMIT': 'Query limit exceeded',
            'REQUEST_DENIED': 'Request denied - check API key',
            'INVALID_REQUEST': 'Invalid request parameters',
            'UNKNOWN_ERROR': 'Unknown error occurred'
        }
        
        base_message = error_messages.get(status, f'API error: {status}')
        if error_message:
            return f"{base_message}: {error_message}"
        
        return base_message
    
    def _parse_response(self, data: Dict, original_address: str) -> GeocodingResult:
        """Parse Google Maps API response"""
        try:
            results = data.get('results', [])
            
            if not results:
                return GeocodingResult(
                    error_message="No results found",
                    source="google"
                )
            
            # Take the first (best) result
            result = results[0]
            geometry = result.get('geometry', {})
            location = geometry.get('location', {})
            
            latitude = location.get('lat')
            longitude = location.get('lng')
            
            if latitude is None or longitude is None:
                return GeocodingResult(
                    error_message="No coordinates in response",
                    source="google"
                )
            
            # Calculate confidence score based on match quality
            confidence_score = self._calculate_confidence_score(result, original_address)
            
            # Determine geocoding quality
            geocoding_quality = self._determine_quality(confidence_score)
            
            # Determine match type
            match_type = self._determine_match_type(result)
            
            return GeocodingResult(
                latitude=float(latitude),
                longitude=float(longitude),
                formatted_address=result.get('formatted_address'),
                confidence_score=confidence_score,
                geocoding_quality=geocoding_quality,
                match_type=match_type,
                source="google"
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing Google Maps API response: {e}")
            return GeocodingResult(
                error_message=f"Error parsing response: {str(e)}",
                source="google"
            )
    
    def _calculate_confidence_score(self, result: Dict, original_address: str) -> float:
        """Calculate confidence score based on match quality"""
        base_score = 50.0  # Start with base score
        
        # Check location type (Google provides this)
        geometry = result.get('geometry', {})
        location_type = geometry.get('location_type', '')
        
        location_type_scores = {
            'ROOFTOP': 30.0,
            'RANGE_INTERPOLATED': 25.0,
            'GEOMETRIC_CENTER': 20.0,
            'APPROXIMATE': 15.0
        }
        
        base_score += location_type_scores.get(location_type, 10.0)
        
        # Check address components completeness
        address_components = result.get('address_components', [])
        components_present = 0
        total_components = 0
        
        required_components = ['street_number', 'route', 'locality', 'administrative_area_level_1', 'postal_code']
        
        for component in required_components:
            total_components += 1
            if any(comp.get('types', []) == [component] for comp in address_components):
                components_present += 1
        
        if total_components > 0:
            component_score = (components_present / total_components) * 20.0
            base_score += component_score
        
        # Check if matched address is similar to original
        formatted_address = result.get('formatted_address', '')
        if formatted_address:
            # Simple similarity check
            original_lower = original_address.lower()
            formatted_lower = formatted_address.lower()
            
            # Check for common words
            original_words = set(original_lower.split())
            formatted_words = set(formatted_lower.split())
            common_words = original_words.intersection(formatted_words)
            
            if len(original_words) > 0:
                similarity = len(common_words) / len(original_words)
                base_score += similarity * 10.0
        
        return min(base_score, 100.0)
    
    def _determine_quality(self, confidence_score: float) -> str:
        """Determine geocoding quality based on confidence score"""
        if confidence_score >= 85:
            return "high"
        elif confidence_score >= 70:
            return "medium"
        else:
            return "low"
    
    def _determine_match_type(self, result: Dict) -> str:
        """Determine match type based on Google's location type"""
        geometry = result.get('geometry', {})
        location_type = geometry.get('location_type', '')
        
        if location_type == 'ROOFTOP':
            return "exact"
        elif location_type in ['RANGE_INTERPOLATED', 'GEOMETRIC_CENTER']:
            return "fuzzy"
        else:
            return "component"
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            'monthly_requests': self.monthly_requests,
            'monthly_limit': self.monthly_limit,
            'limit_threshold': self.limit_threshold,
            'remaining_requests': self.monthly_limit - self.monthly_requests,
            'last_reset_date': self.last_reset_date.isoformat(),
            'within_limit': self.monthly_requests < self.monthly_limit,
            'approaching_limit': self.monthly_requests >= self.monthly_limit * self.limit_threshold
        }
    
    def reset_monthly_counter(self):
        """Reset monthly request counter (for testing)"""
        self.monthly_requests = 0
        self.last_reset_date = datetime.now().replace(day=1)

def test_google_geocoder():
    """Test the Google geocoder with sample addresses"""
    import os
    
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("GOOGLE_MAPS_API_KEY environment variable not set")
        return
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    geocoder = GoogleGeocoder(api_key, logger)
    
    test_addresses = [
        "123 Main St, Kansas City, MO 64101",
        "456 Oak Ave, Kansas City, MO 64102",
        "789 Broadway, Kansas City, MO",
        "Invalid Address That Should Fail"
    ]
    
    print("Testing Google Maps Geocoder:")
    print("=" * 50)
    
    for address in test_addresses:
        print(f"\nGeocoding: {address}")
        result = geocoder.geocode(address)
        
        if result.error_message:
            print(f"  Error: {result.error_message}")
        else:
            print(f"  Coordinates: {result.latitude}, {result.longitude}")
            print(f"  Formatted: {result.formatted_address}")
            print(f"  Confidence: {result.confidence_score:.1f}%")
            print(f"  Quality: {result.geocoding_quality}")
            print(f"  Match Type: {result.match_type}")
    
    print(f"\nUsage Stats: {geocoder.get_usage_stats()}")

if __name__ == "__main__":
    test_google_geocoder()
