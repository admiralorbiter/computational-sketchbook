# Business Model

from sqlalchemy import Column, String, Text, Integer, Numeric, Float
from .base import BaseModel

class Business(BaseModel):
    """Generic Business model for CSV data sources"""
    
    __tablename__ = 'businesses'
    
    # Core business information
    name = Column(String(200), nullable=False, index=True)
    business_type = Column(String(100), index=True)
    description = Column(Text)
    industry = Column(String(100), index=True)
    
    # Location information
    address = Column(String(200), index=True)
    city = Column(String(100), index=True)
    state = Column(String(10), index=True)
    zipcode = Column(String(10), index=True)
    
    # Source tracking
    source = Column(String(20), nullable=False, index=True)  # 'license' or 'company'
    source_id = Column(String(50), index=True)  # Original ID from source data
    
    # Additional fields for business licenses
    dba_name = Column(String(200), index=True)  # Doing business as
    valid_license_for = Column(String(50))  # License expiry date
    
    # Additional fields for companies
    place_id = Column(String(100))  # Google Places ID
    place_type = Column(String(50))  # Google Places type
    
    # Spatial fields (not using SpatialMixin to avoid geometry column)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    
    def __repr__(self):
        return f"<Business(name='{self.name}', source='{self.source}')>"
