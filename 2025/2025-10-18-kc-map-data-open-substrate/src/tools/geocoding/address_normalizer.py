#!/usr/bin/env python3
"""
Address Normalization Module

Provides robust address parsing, normalization, and fuzzy matching
for the geocoding service.
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AddressComponents:
    """Parsed address components"""
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_suffix: Optional[str] = None
    directional: Optional[str] = None
    unit: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    full_address: str = ""

class AddressNormalizer:
    """Address normalization and parsing utilities"""
    
    # Common street suffix abbreviations
    STREET_SUFFIXES = {
        'ST': 'STREET',
        'AVE': 'AVENUE', 
        'AV': 'AVENUE',
        'BLVD': 'BOULEVARD',
        'DR': 'DRIVE',
        'CT': 'COURT',
        'PL': 'PLACE',
        'CIR': 'CIRCLE',
        'LN': 'LANE',
        'RD': 'ROAD',
        'WAY': 'WAY',
        'TRL': 'TRAIL',
        'PKWY': 'PARKWAY',
        'HWY': 'HIGHWAY',
        'SQ': 'SQUARE',
        'TER': 'TERRACE'
    }
    
    # Directional abbreviations
    DIRECTIONALS = {
        'N': 'NORTH',
        'S': 'SOUTH', 
        'E': 'EAST',
        'W': 'WEST',
        'NE': 'NORTHEAST',
        'NW': 'NORTHWEST',
        'SE': 'SOUTHEAST',
        'SW': 'SOUTHWEST'
    }
    
    # State abbreviations
    STATES = {
        'MO': 'MISSOURI',
        'KS': 'KANSAS',
        'MISSOURI': 'MISSOURI',
        'KANSAS': 'KANSAS'
    }
    
    # Kansas City variations
    KC_VARIATIONS = {
        'KC': 'KANSAS CITY',
        'K.C.': 'KANSAS CITY',
        'KANSAS CITY': 'KANSAS CITY',
        'KANSAS CITY, MO': 'KANSAS CITY',
        'KANSAS CITY, MISSOURI': 'KANSAS CITY'
    }
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.street_number_pattern = re.compile(r'^\d+[A-Z]?')
        self.zipcode_pattern = re.compile(r'\b(\d{5}(?:-\d{4})?)\b')
        self.unit_pattern = re.compile(r'\b(?:APT|APARTMENT|SUITE|UNIT|STE|#)\s*([A-Z0-9]+)\b', re.IGNORECASE)
        
    def normalize_address(self, address: str) -> str:
        """Normalize address string to standard format"""
        if not address:
            return ""
        
        # Convert to uppercase and clean whitespace
        normalized = re.sub(r'\s+', ' ', address.strip().upper())
        
        # Remove extra punctuation except hyphens
        normalized = re.sub(r'[^\w\s\-]', '', normalized)
        
        # Handle Kansas City variations
        for variation, standard in self.KC_VARIATIONS.items():
            normalized = normalized.replace(variation, standard)
        
        # Expand street suffixes
        for abbrev, full in self.STREET_SUFFIXES.items():
            # Match word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            normalized = re.sub(pattern, full, normalized)
        
        # Expand directionals
        for abbrev, full in self.DIRECTIONALS.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            normalized = re.sub(pattern, full, normalized)
        
        # Normalize state names
        for abbrev, full in self.STATES.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            normalized = re.sub(pattern, full, normalized)
        
        return normalized.strip()
    
    def parse_address(self, address: str) -> AddressComponents:
        """Parse address into components"""
        if not address:
            return AddressComponents()
        
        normalized = self.normalize_address(address)
        components = AddressComponents(full_address=normalized)
        
        # Extract street number
        street_match = self.street_number_pattern.match(normalized)
        if street_match:
            components.street_number = street_match.group()
        
        # Extract ZIP code
        zip_match = self.zipcode_pattern.search(normalized)
        if zip_match:
            components.zipcode = zip_match.group(1)
        
        # Extract unit information
        unit_match = self.unit_pattern.search(normalized)
        if unit_match:
            components.unit = unit_match.group(1)
        
        # Split by comma to separate address from city/state
        parts = [part.strip() for part in normalized.split(',')]
        
        if len(parts) >= 2:
            # Address part (everything before first comma)
            address_part = parts[0]
            components.street_name, components.street_suffix = self._parse_street_name(address_part)
            
            # City/state part
            city_state_part = parts[1]
            components.city, components.state = self._parse_city_state(city_state_part)
            
            # Check for directional in address
            components.directional = self._extract_directional(address_part)
        
        elif len(parts) == 1:
            # Single part - try to parse as complete address
            address_part = parts[0]
            components.street_name, components.street_suffix = self._parse_street_name(address_part)
            components.directional = self._extract_directional(address_part)
            
            # Try to extract city/state from the end
            city_state = self._extract_city_state_from_end(address_part)
            if city_state:
                components.city, components.state = city_state
        
        return components
    
    def _parse_street_name(self, address_part: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse street name and suffix from address part"""
        # Remove street number and unit
        street_part = re.sub(r'^\d+[A-Z]?\s*', '', address_part)
        street_part = re.sub(r'\b(?:APT|APARTMENT|SUITE|UNIT|STE|#)\s*[A-Z0-9]+', '', street_part)
        
        # Find street suffix
        for suffix in self.STREET_SUFFIXES.values():
            if street_part.endswith(' ' + suffix):
                street_name = street_part[:-len(' ' + suffix)].strip()
                return street_name, suffix
        
        # No suffix found
        return street_part.strip(), None
    
    def _parse_city_state(self, city_state_part: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse city and state from city/state part"""
        parts = city_state_part.split()
        
        if len(parts) >= 2:
            # Last part is likely state
            state = parts[-1]
            city = ' '.join(parts[:-1])
            return city, state
        elif len(parts) == 1:
            # Could be city or state
            if parts[0] in self.STATES:
                return None, parts[0]
            else:
                return parts[0], None
        
        return None, None
    
    def _extract_city_state_from_end(self, address_part: str) -> Optional[Tuple[str, str]]:
        """Try to extract city and state from the end of address"""
        # Look for state at the end
        for state in self.STATES:
            if address_part.endswith(' ' + state):
                # Extract city before state
                before_state = address_part[:-len(' ' + state)].strip()
                # Find last word as potential city
                words = before_state.split()
                if len(words) >= 2:
                    city = ' '.join(words[-2:])  # Take last two words as city
                    return city, state
        
        return None
    
    def _extract_directional(self, address_part: str) -> Optional[str]:
        """Extract directional from address part"""
        for directional in self.DIRECTIONALS:
            if directional in address_part:
                return directional
        return None
    
    def generate_address_hash(self, normalized_address: str) -> str:
        """Generate hash for fast address lookups"""
        return hashlib.md5(normalized_address.encode('utf-8')).hexdigest()
    
    def fuzzy_match_score(self, address1: str, address2: str) -> float:
        """Calculate similarity score between two addresses using component-based matching"""
        if not address1 or not address2:
            return 0.0
        
        # Normalize both addresses
        norm1 = self.normalize_address(address1)
        norm2 = self.normalize_address(address2)
        
        if norm1 == norm2:
            return 1.0
        
        # Parse addresses into components
        components1 = self.parse_address(address1)
        components2 = self.parse_address(address2)
        
        # Calculate component-based similarity
        return self._component_similarity(components1, components2)
    
    def _component_similarity(self, comp1: AddressComponents, comp2: AddressComponents) -> float:
        """Calculate similarity based on address components"""
        if not comp1 or not comp2:
            return 0.0
        
        # Weight different components differently
        weights = {
            'street_number': 0.4,    # House number is most important
            'street_name': 0.3,       # Street name is important
            'street_suffix': 0.1,     # Street suffix is less important
            'city': 0.1,              # City is less important
            'state': 0.05,            # State is least important
            'zipcode': 0.05           # ZIP is least important
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for component, weight in weights.items():
            val1 = getattr(comp1, component, '')
            val2 = getattr(comp2, component, '')
            
            if val1 and val2:
                # Calculate similarity for this component
                if val1 == val2:
                    score = 1.0
                else:
                    # Use Levenshtein distance for partial matches
                    distance = self._levenshtein_distance(val1, val2)
                    max_len = max(len(val1), len(val2))
                    score = 1.0 - (distance / max_len) if max_len > 0 else 1.0
                
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def component_match_score(self, components1: AddressComponents, components2: AddressComponents) -> float:
        """Calculate match score based on address components"""
        if not components1 or not components2:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        # Street number match (high weight)
        if components1.street_number and components2.street_number:
            total_weight += 0.3
            if components1.street_number == components2.street_number:
                score += 0.3
        
        # Street name match (high weight)
        if components1.street_name and components2.street_name:
            total_weight += 0.3
            if components1.street_name == components2.street_name:
                score += 0.3
            else:
                # Partial match
                name1 = components1.street_name.lower()
                name2 = components2.street_name.lower()
                if name1 in name2 or name2 in name1:
                    score += 0.15
        
        # City match (medium weight)
        if components1.city and components2.city:
            total_weight += 0.2
            if components1.city == components2.city:
                score += 0.2
        
        # State match (medium weight)
        if components1.state and components2.state:
            total_weight += 0.1
            if components1.state == components2.state:
                score += 0.1
        
        # ZIP code match (low weight, but exact)
        if components1.zipcode and components2.zipcode:
            total_weight += 0.1
            if components1.zipcode == components2.zipcode:
                score += 0.1
        
        if total_weight == 0:
            return 0.0
        
        return score / total_weight
    
    def create_search_components(self, components: AddressComponents) -> Dict[str, str]:
        """Create searchable component dictionary for database queries"""
        search_components = {}
        
        if components.street_name:
            search_components['street_name'] = components.street_name
        if components.city:
            search_components['city'] = components.city
        if components.state:
            search_components['state'] = components.state
        if components.zipcode:
            search_components['zipcode'] = components.zipcode
        
        return search_components

# Convenience functions for easy import
def normalize_address(address: str) -> str:
    """Normalize a single address"""
    normalizer = AddressNormalizer()
    return normalizer.normalize_address(address)

def parse_address(address: str) -> AddressComponents:
    """Parse a single address into components"""
    normalizer = AddressNormalizer()
    return normalizer.parse_address(address)

def fuzzy_match_score(address1: str, address2: str) -> float:
    """Calculate fuzzy match score between two addresses"""
    normalizer = AddressNormalizer()
    return normalizer.fuzzy_match_score(address1, address2)

if __name__ == "__main__":
    # Test the normalizer
    normalizer = AddressNormalizer()
    
    test_addresses = [
        "123 Main St, Kansas City, MO 64101",
        "456 Oak Ave, KC, Missouri 64102", 
        "789 N Broadway Blvd, Kansas City, MO",
        "321 S 12th St Apt 4B, Kansas City, MO 64105",
        "654 E 18th St, Kansas City, KS 66102"
    ]
    
    print("Address Normalization Test:")
    print("=" * 50)
    
    for addr in test_addresses:
        normalized = normalizer.normalize_address(addr)
        components = normalizer.parse_address(addr)
        address_hash = normalizer.generate_address_hash(normalized)
        
        print(f"Original: {addr}")
        print(f"Normalized: {normalized}")
        print(f"Components: {components}")
        print(f"Hash: {address_hash}")
        print("-" * 30)
