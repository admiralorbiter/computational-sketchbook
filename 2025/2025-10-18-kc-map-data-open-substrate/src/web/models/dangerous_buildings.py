# Dangerous Buildings Model

from sqlalchemy import Column, String, Date, Text, Integer, Float, DateTime
from geoalchemy2 import Geometry
from .base import BaseModel

class DangerousBuilding(BaseModel):
    """Dangerous Buildings data from KC Open Data"""
    
    __tablename__ = 'dangerous_buildings'
    
    # Primary identifier
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Address fields
    address = Column(String(200), index=True)
    city = Column(String(100), index=True)
    state = Column(String(10), index=True)
    zipcode = Column(String(10), index=True)
    
    # Case information
    case_opened = Column(DateTime, nullable=False, index=True)
    status_of_case = Column(String(100), nullable=False, index=True)
    
    # Additional identifiers
    pin = Column(String(50), index=True)
    council_district = Column(String(10), index=True)
    
    # Spatial fields (nullable - not all records have coordinates)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    def __repr__(self):
        return f"<DangerousBuilding(case_number='{self.case_number}', address='{self.address}', status='{self.status_of_case}')>"
