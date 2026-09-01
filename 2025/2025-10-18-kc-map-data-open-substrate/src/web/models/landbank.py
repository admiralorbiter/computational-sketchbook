"""
Land Bank Property Model

SQLAlchemy model for Land Bank and Kansas City Homesteading Authority properties.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .base import Base

class LandBankProperty(Base):
    """Land Bank property model"""
    
    __tablename__ = 'landbank_properties'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Address information
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(10))
    zipcode = Column(String(20))  # Note: DB uses 'zipcode', not 'postal_code'
    
    # Location information
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Property details
    parcel_number = Column(String(50), unique=True, nullable=False)
    property_status = Column(String(100))  # Acquired, Available, etc.
    inventory_type = Column(String(100))   # Land Bank, Homesteading Authority
    property_class = Column(String(100))   # Residential Vacant, etc.
    property_condition = Column(String(100))  # Vacant lot, etc.
    
    # Financial information
    market_value = Column(Float)
    market_value_year = Column(Integer)
    
    # Physical details
    square_footage = Column(Float)
    demo_needed = Column(String(10))  # Y/N
    
    # Administrative information
    city_council_district = Column(String(50))
    county = Column(String(100))
    neighborhood = Column(String(100))
    school_district = Column(String(100))
    zoned_as = Column(String(100))
    
    # Dates
    date_of_acquisition = Column(String(50))  # Stored as string from API
    
    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.zipcode,  # Map zipcode to postal_code for API consistency
            'latitude': self.latitude,
            'longitude': self.longitude,
            'parcel_number': self.parcel_number,
            'property_status': self.property_status,
            'inventory_type': self.inventory_type,
            'property_class': self.property_class,
            'property_condition': self.property_condition,
            'market_value': self.market_value,
            'market_value_year': self.market_value_year,
            'square_footage': self.square_footage,
            'demo_needed': self.demo_needed,
            'city_council_district': self.city_council_district,
            'county': self.county,
            'neighborhood': self.neighborhood,
            'school_district': self.school_district,
            'zoned_as': self.zoned_as,
            'date_of_acquisition': self.date_of_acquisition,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_geojson_feature(self):
        """Convert to GeoJSON feature"""
        if not self.latitude or not self.longitude:
            return None
            
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude]
            },
            'properties': self.to_dict()
        }
