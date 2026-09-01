# Crime Incident Model

from sqlalchemy import Column, String, DateTime, Float, Text, Integer, Boolean
from .base import BaseModel

class CrimeIncident(BaseModel):
    """Crime incident data from KC Open Data"""
    
    __tablename__ = 'crime_incidents'
    
    # Primary identifier
    report = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "KC25000689"
    
    # Date/Time fields
    report_date = Column(DateTime, nullable=False, index=True)
    reported_time = Column(String(10))
    from_date = Column(DateTime, index=True)
    from_time = Column(String(10))
    to_date = Column(DateTime)
    to_time = Column(String(10))
    
    # Offense information
    offense = Column(String(200), nullable=False, index=True)
    ibrs = Column(String(10), index=True)  # IBRS code
    description = Column(String(200), index=True)  # IBRS description
    
    # Location fields
    beat = Column(String(10), index=True)
    address = Column(String(300))
    city = Column(String(100))
    zipcode = Column(String(10))
    rep_dist = Column(String(20))
    area = Column(String(10), index=True)  # CPD, EPD, MPD, NPD, SPD, SCP
    
    # Involvement/Participant info
    involvement = Column(String(50))  # VIC, SUS, ARR, CHA, etc.
    race = Column(String(10))  # W, B, A, H, U
    sex = Column(String(10))  # M, F, U
    age = Column(Integer)
    age_range = Column(String(20))  # e.g., "25-34"
    
    # Flags
    dvflag = Column(Boolean, default=False, index=True)  # Domestic violence
    firearmusedflag = Column(Boolean, default=False, index=True)
    
    # Spatial fields
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    def __repr__(self):
        return f"<CrimeIncident(report='{self.report}', offense='{self.offense}')>"
