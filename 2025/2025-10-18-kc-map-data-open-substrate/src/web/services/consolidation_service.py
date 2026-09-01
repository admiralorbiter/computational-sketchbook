"""
Consolidation Service

Handles feature consolidation logic for grouping nearby data points.
Supports both address-based and coordinate-based consolidation strategies.
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConsolidationSettings:
    """Configuration for consolidation behavior"""
    
    def __init__(self, 
                 enabled=True,
                 strategy='hybrid',
                 address_tolerance=0.0001,
                 coordinate_precision=1,
                 min_records_to_consolidate=2):
        self.enabled = enabled
        self.strategy = strategy  # 'address_first', 'coordinate_first', 'hybrid'
        self.address_tolerance = address_tolerance
        self.coordinate_precision = coordinate_precision
        self.min_records_to_consolidate = min_records_to_consolidate

class ConsolidationService:
    """Service for consolidating features by location"""
    
    def __init__(self):
        self.settings = ConsolidationSettings()
        
        # Consolidation presets
        self.presets = {
            "aggressive": ConsolidationSettings(
                address_tolerance=0.001,    # ~110m - moderate grouping
                coordinate_precision=3,     # 3 decimal places
                min_records_to_consolidate=3
            ),
            "balanced": ConsolidationSettings(
                address_tolerance=0.0005,   # ~55m - minimal grouping
                coordinate_precision=4,     # 4 decimal places
                min_records_to_consolidate=4
            ),
            "loose": ConsolidationSettings(
                address_tolerance=0.0002,   # ~22m - very minimal grouping
                coordinate_precision=5,     # 5 decimal places
                min_records_to_consolidate=5
            )
        }
    
    def apply_settings(self, settings_dict):
        """Apply user settings"""
        if 'consolidation' in settings_dict:
            consolidation = settings_dict['consolidation']
            
            if 'enabled' in consolidation:
                self.settings.enabled = consolidation['enabled']
            if 'strategy' in consolidation:
                self.settings.strategy = consolidation['strategy']
            if 'address_tolerance' in consolidation:
                self.settings.address_tolerance = consolidation['address_tolerance']
            if 'coordinate_precision' in consolidation:
                self.settings.coordinate_precision = consolidation['coordinate_precision']
            if 'min_records_to_consolidate' in consolidation:
                self.settings.min_records_to_consolidate = consolidation['min_records_to_consolidate']
        else:
            # Direct consolidation settings
            if 'enabled' in settings_dict:
                self.settings.enabled = settings_dict['enabled']
            if 'strategy' in settings_dict:
                self.settings.strategy = settings_dict['strategy']
            if 'address_tolerance' in settings_dict:
                self.settings.address_tolerance = settings_dict['address_tolerance']
            if 'coordinate_precision' in settings_dict:
                self.settings.coordinate_precision = settings_dict['coordinate_precision']
            if 'min_records_to_consolidate' in settings_dict:
                self.settings.min_records_to_consolidate = settings_dict['min_records_to_consolidate']
    
    def apply_preset(self, preset_name):
        """Apply a consolidation preset"""
        if preset_name in self.presets:
            self.settings = self.presets[preset_name]
    
    def normalize_address(self, address):
        """Normalize address for grouping - FIXED NORMALIZATION"""
        if not address or not address.strip():
            return None
        
        # Lowercase, remove extra spaces
        normalized = address.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove zip codes (5 digits at end)
        normalized = re.sub(r'\s+\d{5}(-\d{4})?$', '', normalized)
        
        # Remove city/state suffixes
        normalized = re.sub(r'\s+(kansas city|kc|mo|missouri)\s*$', '', normalized)
        
        # Remove apartment/unit numbers
        normalized = re.sub(r'\s+(apt|apartment|unit|ste|suite|#)\s*\w*\b', '', normalized)
        
        # Remove directional prefixes and articles
        normalized = re.sub(r'^(north|south|east|west|n|s|e|w)\s+', '', normalized)
        normalized = re.sub(r'\bthe\s+', '', normalized)
        
        # Standardize street type abbreviations
        replacements = {
            ' street': ' st', ' avenue': ' ave', ' road': ' rd', 
            ' drive': ' dr', ' boulevard': ' blvd', ' lane': ' ln', 
            ' court': ' ct', ' place': ' pl', ' circle': ' cir', 
            ' way': ' wy', ' trail': ' trl', ' terrace': ' ter'
        }
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces and clean up
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def create_location_key(self, address, lat, lng):
        """Create a location key for grouping - COORDINATE-BASED APPROACH"""
        if lat and lng:
            # Use coordinates as primary grouping method
            # Round to specified precision for grouping
            precision = self.settings.coordinate_precision
            return f"coord_{round(lat, precision)}_{round(lng, precision)}"
        
        if address and address.strip():
            # Use normalized address as fallback for features without coordinates
            normalized_address = self.normalize_address(address)
            if normalized_address:
                return f"addr_{normalized_address}"
        
        return None
    
    def find_nearby_group(self, lat, lng, existing_groups):
        """Find an existing group that this coordinate should join based on tolerance"""
        tolerance = self.settings.address_tolerance
        
        for group_key, group in existing_groups.items():
            if group_key.startswith('coord_'):
                # Extract coordinates from group key
                try:
                    coord_part = group_key.replace('coord_', '')
                    group_lat, group_lng = map(float, coord_part.split('_'))
                    
                    # Calculate distance (simple Euclidean distance for small areas)
                    lat_diff = abs(lat - group_lat)
                    lng_diff = abs(lng - group_lng)
                    distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
                    
                    # If within tolerance, join this group
                    if distance <= tolerance:
                        return group_key
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def are_addresses_similar(self, addr1, addr2):
        """Check if two addresses are similar enough to be grouped together"""
        if not addr1 or not addr2:
            return False
        
        # Normalize both addresses
        norm1 = self.normalize_address(addr1)
        norm2 = self.normalize_address(addr2)
        
        if not norm1 or not norm2:
            return False
        
        # If they're exactly the same, group them
        if norm1 == norm2:
            return True
        
        # For now, use exact matching only
        # TODO: Implement fuzzy matching based on address_tolerance
        return False
    
    def aggregate_kc_features(self, features, layer_name):
        """Aggregate KC features by location - HYBRID APPROACH (address + coordinates)"""
        if not self.settings.enabled:
            return features
        
        # Debug logging can be enabled here if needed
        
        location_groups = {}
        
        for feature in features:
            props = feature['properties']
            
            # Get address based on layer
            if layer_name == 'service_requests':
                address = props.get('incident_address')
            elif layer_name == 'crime':
                address = props.get('address')
            else:
                address = None
                
            lat = props.get('latitude')
            lng = props.get('longitude')
            
            # Create location key - HYBRID APPROACH
            location_key = self.create_location_key(address, lat, lng)
            if not location_key:
                # Skip features without address or coordinates
                continue
                
            if location_key not in location_groups:
                location_groups[location_key] = {
                    'address': address,
                    'latitude': lat,
                    'longitude': lng,
                    'count': 0,
                    'entries': []
                }
            
            location_groups[location_key]['count'] += 1
            location_groups[location_key]['entries'].append(feature)
        
        # Convert to consolidated features
        consolidated_features = []
        for location_key, group in location_groups.items():
            if group['count'] == 1:
                # Single feature - return as-is
                consolidated_features.append(group['entries'][0])
            else:
                # Multiple features - create consolidated feature
                consolidated_feature = {
                    "type": "Feature",
                    "properties": {
                        "id": f"consolidated_{location_key}",
                        "name": group['address'] or f"Location {location_key}",
                        "type": f"consolidated_{layer_name}",
                        "count": group['count'],
                        "address": group['address'],
                        "entries": group['entries'],
                        "consolidated": True
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [group['longitude'], group['latitude']]
                    }
                }
                consolidated_features.append(consolidated_feature)
        
        return consolidated_features
    
    def aggregate_cross_layer_features(self, all_features):
        """Aggregate features across all layers by location - CROSS-LAYER CONSOLIDATION"""
        if not self.settings.enabled:
            return []
        
        total_features = sum(len(features) for features in all_features.values())
        # Debug logging can be enabled here if needed
        
        location_groups = {}
        
        for layer_name, features in all_features.items():
            for feature in features:
                props = feature['properties']
                
                # Get address based on layer
                if layer_name == 'service_requests':
                    address = props.get('incident_address')
                elif layer_name == 'crime':
                    address = props.get('address')
                elif layer_name == 'points':
                    # Extract address from OSM tags
                    if 'addr:street' in props.get('tags', {}) and 'addr:housenumber' in props.get('tags', {}):
                        address = f"{props['tags']['addr:housenumber']} {props['tags']['addr:street']}"
                    elif 'name' in props.get('tags', {}):
                        address = props['tags']['name']
                    else:
                        address = None
                else:
                    address = None
                    
                # Get coordinates
                if 'geometry' in feature and 'coordinates' in feature['geometry']:
                    coords = feature['geometry']['coordinates']
                    lat = coords[1]
                    lng = coords[0]
                else:
                    lat = props.get('latitude')
                    lng = props.get('longitude')
                
                # Skip features without coordinates
                if not lat or not lng:
                    continue
                
                # Try to find an existing nearby group first
                location_key = self.find_nearby_group(lat, lng, location_groups)
                
                # If no nearby group found, create a new one
                if not location_key:
                    location_key = self.create_location_key(address, lat, lng)
                    if not location_key:
                        continue
                    
                if location_key not in location_groups:
                    location_groups[location_key] = {
                        'address': address,
                        'latitude': lat,
                        'longitude': lng,
                        'count': 0,
                        'entries': [],
                        'layers': set()
                    }
                
                location_groups[location_key]['count'] += 1
                location_groups[location_key]['entries'].append(feature)
                location_groups[location_key]['layers'].add(layer_name)
        
        # Convert to consolidated features
        consolidated_features = []
        for location_key, group in location_groups.items():
            if group['count'] == 1:
                # Single feature - return as-is
                consolidated_features.append(group['entries'][0])
            else:
                # Multiple features - create consolidated feature
                consolidated_feature = {
                    "type": "Feature",
                    "properties": {
                        "id": f"consolidated_{location_key}",
                        "name": group['address'] or f"Location {location_key}",
                        "type": "consolidated_cross_layer",
                        "count": group['count'],
                        "address": group['address'],
                        "layers": list(group['layers']),
                        "entries": group['entries'],
                        "consolidated": True
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [group['longitude'], group['latitude']]
                    }
                }
                consolidated_features.append(consolidated_feature)
        
        return consolidated_features
    
    def aggregate_osm_points(self, features):
        """Aggregate OSM points by location - COORDINATE-BASED GROUPING"""
        if not self.settings.enabled:
            return features
        
        location_groups = {}
        
        for feature in features:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            lat = coords[1]
            lng = coords[0]
            
            # Extract address from tags if available
            address = None
            if 'addr:street' in props['tags'] and 'addr:housenumber' in props['tags']:
                address = f"{props['tags']['addr:housenumber']} {props['tags']['addr:street']}"
            elif 'name' in props['tags']:
                address = props['tags']['name']
            
            # Create location key - HYBRID APPROACH for OSM
            location_key = self.create_location_key(address, lat, lng)
            if not location_key:
                # Skip features without address or coordinates
                continue
                
            if location_key not in location_groups:
                location_groups[location_key] = {
                    'address': address,
                    'latitude': lat,
                    'longitude': lng,
                    'count': 0,
                    'entries': []
                }
            
            location_groups[location_key]['count'] += 1
            location_groups[location_key]['entries'].append(feature)
        
        # Convert to consolidated features
        consolidated_features = []
        for location_key, group in location_groups.items():
            if group['count'] == 1:
                # Single feature - return as-is
                consolidated_features.append(group['entries'][0])
            else:
                # Multiple features - create consolidated feature
                consolidated_feature = {
                    "type": "Feature",
                    "properties": {
                        "id": f"consolidated_{location_key}",
                        "name": group['address'] or f"OSM Location {location_key}",
                        "type": "consolidated_points",
                        "count": group['count'],
                        "address": group['address'],
                        "entries": group['entries'],
                        "consolidated": True
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [group['longitude'], group['latitude']]
                    }
                }
                consolidated_features.append(consolidated_feature)
        
        return consolidated_features
