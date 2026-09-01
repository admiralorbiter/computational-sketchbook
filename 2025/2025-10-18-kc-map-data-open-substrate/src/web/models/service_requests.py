# Service Request Model (311 Data)

from sqlalchemy import Column, String, Date, Text, Integer, Boolean, Float, DateTime
from geoalchemy2 import Geometry
from .base import BaseModel

class ServiceRequest(BaseModel):
    """311 Service Request data from KC Open Data"""
    
    __tablename__ = 'service_requests_311'
    
    # KC Open Data fields (matching actual API structure)
    request_id = Column(String(50), unique=True, nullable=False, index=True)  # reported_issue
    issue_type = Column(String(100), nullable=False, index=True)  # issue_type
    issue_sub_type = Column(String(100), index=True)  # issue_sub_type
    
    # Status fields
    current_status = Column(String(50), nullable=False, index=True)  # current_status
    
    # Dates (matching API field names)
    open_date_time = Column(DateTime, nullable=False, index=True)  # open_date_time
    resolved_date = Column(DateTime, index=True)  # resolved_date
    last_updated = Column(DateTime, index=True)  # last_updated
    days_to_close = Column(Integer, index=True)  # days_to_close
    
    # Location fields
    incident_address = Column(String(200), index=True)  # incident_address
    council_district = Column(String(10), index=True)  # council_district
    
    # Department and assignment
    department_work_group = Column(String(100), index=True)  # department_work_group
    
    # Source information
    report_source = Column(String(50), index=True)  # report_source (Phone, iOS, Android, WEB RAI)
    source_category = Column(String(50), index=True)  # source_category (Public vs Staff)
    
    # Work order
    workorder_ = Column(String(50), index=True)  # workorder_
    
    # Additional metadata
    additional_questions = Column(Text)  # additional_questions (JSON text)
    
    # Spatial fields (nullable - not all records have coordinates)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    def __repr__(self):
        return f"<ServiceRequest(request_id='{self.request_id}', type='{self.issue_type}', status='{self.current_status}')>"
