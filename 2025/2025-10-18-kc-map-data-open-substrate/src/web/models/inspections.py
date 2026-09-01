# Food Inspection Model

from sqlalchemy import Column, String, Date, Text, Integer, Numeric, Boolean
from geoalchemy2 import Geometry
from .base import BaseModel, SpatialMixin

class FoodInspection(BaseModel, SpatialMixin):
    """Food Inspection data from KC Open Data"""
    
    __tablename__ = 'food_inspections'
    
    # KC Open Data fields
    inspection_id = Column(String(50), unique=True, nullable=False, index=True)
    establishment_name = Column(String(200), nullable=False, index=True)
    establishment_type = Column(String(100), index=True)
    
    # Inspection details
    inspection_date = Column(Date, nullable=False, index=True)
    inspection_type = Column(String(50), nullable=False, index=True)
    inspection_score = Column(Integer, index=True)
    inspection_grade = Column(String(5), index=True)
    
    # Location fields
    address = Column(String(200), index=True)
    neighborhood = Column(String(100), index=True)
    council_district = Column(String(10), index=True)
    zip_code = Column(String(10), index=True)
    
    # Violations
    critical_violations = Column(Integer, default=0)
    non_critical_violations = Column(Integer, default=0)
    total_violations = Column(Integer, default=0)
    violation_details = Column(Text)
    
    # Inspector information
    inspector_name = Column(String(100))
    inspector_id = Column(String(20))
    
    # Additional fields
    permit_number = Column(String(50), index=True)
    risk_level = Column(String(20), index=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    
    # Spatial fields (inherited from SpatialMixin)
    # geometry, latitude, longitude
    
    def __repr__(self):
        return f"<FoodInspection(inspection_id='{self.inspection_id}', name='{self.establishment_name}')>"
