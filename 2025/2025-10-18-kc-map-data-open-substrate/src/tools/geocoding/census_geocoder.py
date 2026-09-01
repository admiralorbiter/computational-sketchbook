#!/usr/bin/env python3
"""
Census Geocoder API Client

Handles geocoding requests to the US Census Geocoding API
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
    source: str = "census"
    error_message: Optional[str] = None

class CensusGeocoder:
    """US Census Geocoding API client"""
    
    BASE_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    TIMEOUT = 30  # seconds
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Kansas City Data Platform Geocoding Service/1.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting tracking
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()
        self.daily_limit = 1000
        self.limit_threshold = 0.9  # Switch at 90% of limit
    
    def geocode(self, address: str) -> GeocodingResult:
        """Geocode a single address using Census API"""
        
        # Check rate limits
        if not self._check_rate_limit():
            return GeocodingResult(
                error_message="Daily rate limit exceeded",
                source="census"
            )
        
        # Prepare request
        params = {
            'address': address,
            'benchmark': '2020',
            'format': 'json'
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
                    self.logger.warning("Rate limited by Census API")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY * (2 ** attempt))
                        continue
                    else:
                        return GeocodingResult(
                            error_message="Rate limited by Census API",
                            source="census"
                        )
                
                response.raise_for_status()
                data = response.json()
                
                # Parse response
                result = self._parse_response(data, address)
                self.daily_requests += 1
                
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
                        source="census"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error geocoding address {address}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                    continue
                else:
                    return GeocodingResult(
                        error_message=f"Request error: {str(e)}",
                        source="census"
                    )
                    
            except Exception as e:
                self.logger.error(f"Unexpected error geocoding address {address}: {e}")
                return GeocodingResult(
                    error_message=f"Unexpected error: {str(e)}",
                    source="census"
                )
        
        return GeocodingResult(
            error_message="Max retries exceeded",
            source="census"
        )
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_date = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if current_date != self.last_reset_date:
            self.daily_requests = 0
            self.last_reset_date = current_date
        
        # Check if we're approaching the limit
        if self.daily_requests >= self.daily_limit * self.limit_threshold:
            self.logger.warning(f"Approaching Census API daily limit: {self.daily_requests}/{self.daily_limit}")
            return False
        
        return self.daily_requests < self.daily_limit
    
    def _parse_response(self, data: Dict, original_address: str) -> GeocodingResult:
        """Parse Census API response"""
        try:
            result = data.get('result', {})
            address_matches = result.get('addressMatches', [])
            
            if not address_matches:
                return GeocodingResult(
                    error_message="No address matches found",
                    source="census"
                )
            
            # Take the first (best) match
            match = address_matches[0]
            coordinates = match.get('coordinates', {})
            
            latitude = coordinates.get('y')
            longitude = coordinates.get('x')
            
            if latitude is None or longitude is None:
                return GeocodingResult(
                    error_message="No coordinates in response",
                    source="census"
                )
            
            # Calculate confidence score based on match quality
            confidence_score = self._calculate_confidence_score(match, original_address)
            
            # Determine geocoding quality
            geocoding_quality = self._determine_quality(confidence_score)
            
            # Determine match type
            match_type = self._determine_match_type(match)
            
            return GeocodingResult(
                latitude=float(latitude),
                longitude=float(longitude),
                formatted_address=match.get('matchedAddress'),
                confidence_score=confidence_score,
                geocoding_quality=geocoding_quality,
                match_type=match_type,
                source="census"
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing Census API response: {e}")
            return GeocodingResult(
                error_message=f"Error parsing response: {str(e)}",
                source="census"
            )
    
    def _calculate_confidence_score(self, match: Dict, original_address: str) -> float:
        """Calculate confidence score based on match quality"""
        base_score = 50.0  # Start with base score
        
        # Check if coordinates are present
        coordinates = match.get('coordinates', {})
        if coordinates.get('x') and coordinates.get('y'):
            base_score += 20.0
        
        # Check address components completeness
        address_components = match.get('addressComponents', {})
        components_present = 0
        total_components = 0
        
        for component in ['streetNumber', 'streetName', 'city', 'state', 'zip']:
            total_components += 1
            if address_components.get(component):
                components_present += 1
        
        if total_components > 0:
            component_score = (components_present / total_components) * 20.0
            base_score += component_score
        
        # Check if matched address is similar to original
        matched_address = match.get('matchedAddress', '')
        if matched_address:
            # Simple similarity check
            original_lower = original_address.lower()
            matched_lower = matched_address.lower()
            
            # Check for common words
            original_words = set(original_lower.split())
            matched_words = set(matched_lower.split())
            common_words = original_words.intersection(matched_words)
            
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
    
    def _determine_match_type(self, match: Dict) -> str:
        """Determine match type based on response data"""
        # Census API doesn't provide detailed match type info
        # We'll use a simple heuristic based on address completeness
        address_components = match.get('addressComponents', {})
        
        has_street_number = bool(address_components.get('streetNumber'))
        has_street_name = bool(address_components.get('streetName'))
        has_city = bool(address_components.get('city'))
        has_state = bool(address_components.get('state'))
        
        if has_street_number and has_street_name and has_city and has_state:
            return "exact"
        elif has_street_name and has_city and has_state:
            return "fuzzy"
        else:
            return "component"
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            'daily_requests': self.daily_requests,
            'daily_limit': self.daily_limit,
            'limit_threshold': self.limit_threshold,
            'remaining_requests': self.daily_limit - self.daily_requests,
            'last_reset_date': self.last_reset_date.isoformat(),
            'within_limit': self.daily_requests < self.daily_limit,
            'approaching_limit': self.daily_requests >= self.daily_limit * self.limit_threshold
        }
    
    def reset_daily_counter(self):
        """Reset daily request counter (for testing)"""
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()

def test_census_geocoder():
    """Test the Census geocoder with sample addresses"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    geocoder = CensusGeocoder(logger)
    
    test_addresses = [
        "123 Main St, Kansas City, MO 64101",
        "456 Oak Ave, Kansas City, MO 64102",
        "789 Broadway, Kansas City, MO",
        "Invalid Address That Should Fail"
    ]
    
    print("Testing Census Geocoder:")
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
    test_census_geocoder()
