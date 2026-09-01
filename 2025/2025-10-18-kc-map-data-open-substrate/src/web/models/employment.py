# Employment Models - LODES Data

from sqlalchemy import Column, String, Integer, Float, Text, BigInteger
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class WorkplaceAreaCharacteristics(Base, TimestampMixin):
    """LODES Workplace Area Characteristics (WAC)
    
    Describes jobs by census block of workplace location.
    Includes all demographic, industrial, and firm characteristics.
    """
    
    __tablename__ = 'lodes_wac'
    __table_args__ = {'extend_existing': True}
    
    # Primary key and geography
    w_geocode = Column(String(15), primary_key=True, comment="15-digit GEOID of workplace block")
    state = Column(String(2), index=True, comment="State FIPS code")
    year = Column(String(4), index=True, comment="Data year")
    
    # Total jobs
    C000 = Column(Integer, comment="Total jobs")
    
    # Age groups
    CA01 = Column(Integer, comment="Jobs: Age 29 or younger")
    CA02 = Column(Integer, comment="Jobs: Age 30 to 54")
    CA03 = Column(Integer, comment="Jobs: Age 55 or older")
    
    # Earnings
    CE01 = Column(Integer, comment="Jobs: Earnings $1,250/month or less")
    CE02 = Column(Integer, comment="Jobs: Earnings $1,251-$3,333/month")
    CE03 = Column(Integer, comment="Jobs: Earnings $3,334/month or more")
    
    # Industry sectors (NAICS)
    CNS01 = Column(Integer, comment="Agriculture, forestry, fishing, hunting, mining")
    CNS02 = Column(Integer, comment="Utilities")
    CNS03 = Column(Integer, comment="Construction")
    CNS04 = Column(Integer, comment="Manufacturing")
    CNS05 = Column(Integer, comment="Wholesale trade")
    CNS06 = Column(Integer, comment="Retail trade")
    CNS07 = Column(Integer, comment="Transportation and warehousing")
    CNS08 = Column(Integer, comment="Information")
    CNS09 = Column(Integer, comment="Finance and insurance")
    CNS10 = Column(Integer, comment="Real estate, rental, leasing")
    CNS11 = Column(Integer, comment="Professional, scientific, technical services")
    CNS12 = Column(Integer, comment="Management of companies")
    CNS13 = Column(Integer, comment="Administrative and support services")
    CNS14 = Column(Integer, comment="Educational services")
    CNS15 = Column(Integer, comment="Health care and social assistance")
    CNS16 = Column(Integer, comment="Arts, entertainment, recreation")
    CNS17 = Column(Integer, comment="Accommodation and food services")
    CNS18 = Column(Integer, comment="Other services")
    CNS19 = Column(Integer, comment="Public administration")
    CNS20 = Column(Integer, comment="Unclassified")
    
    # Race
    CR01 = Column(Integer, comment="White alone")
    CR02 = Column(Integer, comment="Black or African American alone")
    CR03 = Column(Integer, comment="American Indian or Alaska Native alone")
    CR04 = Column(Integer, comment="Asian alone")
    CR05 = Column(Integer, comment="Native Hawaiian or Pacific Islander alone")
    CR07 = Column(Integer, comment="Two or More Race groups")
    
    # Ethnicity
    CT01 = Column(Integer, comment="Not Hispanic or Latino")
    CT02 = Column(Integer, comment="Hispanic or Latino")
    
    # Education
    CD01 = Column(Integer, comment="Less than high school")
    CD02 = Column(Integer, comment="High school or equivalent")
    CD03 = Column(Integer, comment="Some college or Associate degree")
    CD04 = Column(Integer, comment="Bachelor's degree or advanced degree")
    
    # Sex
    CS01 = Column(Integer, comment="Male")
    CS02 = Column(Integer, comment="Female")
    
    # Firm age
    CFA01 = Column(Integer, comment="Firm age 0-2 years")
    CFA02 = Column(Integer, comment="Firm age 3-5 years")
    CFA03 = Column(Integer, comment="Firm age 6-10 years")
    CFA04 = Column(Integer, comment="Firm age 11+ years")
    CFA05 = Column(Integer, comment="Firm age unknown")
    
    # Firm size
    CFS01 = Column(Integer, comment="0-19 employees")
    CFS02 = Column(Integer, comment="20-49 employees")
    CFS03 = Column(Integer, comment="50-249 employees")
    CFS04 = Column(Integer, comment="250-499 employees")
    CFS05 = Column(Integer, comment="500+ employees")
    
    job_type = Column(String(4), comment="Job type code (JT00 = all)")
    segment = Column(String(4), comment="Segment code")
    createdate = Column(String(20), comment="Data creation date")
    
    def __repr__(self):
        return f"<WorkplaceAreaCharacteristics(w_geocode='{self.w_geocode}', jobs={self.C000})>"


class ResidenceAreaCharacteristics(Base, TimestampMixin):
    """LODES Residence Area Characteristics (RAC)
    
    Describes jobs by census block of worker residence.
    Similar structure to WAC but for where workers live.
    """
    
    __tablename__ = 'lodes_rac'
    __table_args__ = {'extend_existing': True}
    
    # Primary key and geography
    h_geocode = Column(String(15), primary_key=True, comment="15-digit GEOID of residence block")
    state = Column(String(2), index=True, comment="State FIPS code")
    year = Column(String(4), index=True, comment="Data year")
    
    # Total jobs (same structure as WAC)
    C000 = Column(Integer, comment="Total jobs")
    
    # Age groups
    CA01 = Column(Integer, comment="Jobs: Age 29 or younger")
    CA02 = Column(Integer, comment="Jobs: Age 30 to 54")
    CA03 = Column(Integer, comment="Jobs: Age 55 or older")
    
    # Earnings
    CE01 = Column(Integer, comment="Jobs: Earnings $1,250/month or less")
    CE02 = Column(Integer, comment="Jobs: Earnings $1,251-$3,333/month")
    CE03 = Column(Integer, comment="Jobs: Earnings $3,334/month or more")
    
    # Industry sectors (NAICS) - same as WAC
    CNS01 = Column(Integer, comment="Agriculture, forestry, fishing, hunting, mining")
    CNS02 = Column(Integer, comment="Utilities")
    CNS03 = Column(Integer, comment="Construction")
    CNS04 = Column(Integer, comment="Manufacturing")
    CNS05 = Column(Integer, comment="Wholesale trade")
    CNS06 = Column(Integer, comment="Retail trade")
    CNS07 = Column(Integer, comment="Transportation and warehousing")
    CNS08 = Column(Integer, comment="Information")
    CNS09 = Column(Integer, comment="Finance and insurance")
    CNS10 = Column(Integer, comment="Real estate, rental, leasing")
    CNS11 = Column(Integer, comment="Professional, scientific, technical services")
    CNS12 = Column(Integer, comment="Management of companies")
    CNS13 = Column(Integer, comment="Administrative and support services")
    CNS14 = Column(Integer, comment="Educational services")
    CNS15 = Column(Integer, comment="Health care and social assistance")
    CNS16 = Column(Integer, comment="Arts, entertainment, recreation")
    CNS17 = Column(Integer, comment="Accommodation and food services")
    CNS18 = Column(Integer, comment="Other services")
    CNS19 = Column(Integer, comment="Public administration")
    CNS20 = Column(Integer, comment="Unclassified")
    
    # Race, ethnicity, education, sex, firm characteristics (same as WAC)
    CR01 = Column(Integer, comment="White alone")
    CR02 = Column(Integer, comment="Black or African American alone")
    CR03 = Column(Integer, comment="American Indian or Alaska Native alone")
    CR04 = Column(Integer, comment="Asian alone")
    CR05 = Column(Integer, comment="Native Hawaiian or Pacific Islander alone")
    CR07 = Column(Integer, comment="Two or More Race groups")
    
    CT01 = Column(Integer, comment="Not Hispanic or Latino")
    CT02 = Column(Integer, comment="Hispanic or Latino")
    
    CD01 = Column(Integer, comment="Less than high school")
    CD02 = Column(Integer, comment="High school or equivalent")
    CD03 = Column(Integer, comment="Some college or Associate degree")
    CD04 = Column(Integer, comment="Bachelor's degree or advanced degree")
    
    CS01 = Column(Integer, comment="Male")
    CS02 = Column(Integer, comment="Female")
    
    CFA01 = Column(Integer, comment="Firm age 0-2 years")
    CFA02 = Column(Integer, comment="Firm age 3-5 years")
    CFA03 = Column(Integer, comment="Firm age 6-10 years")
    CFA04 = Column(Integer, comment="Firm age 11+ years")
    CFA05 = Column(Integer, comment="Firm age unknown")
    
    CFS01 = Column(Integer, comment="0-19 employees")
    CFS02 = Column(Integer, comment="20-49 employees")
    CFS03 = Column(Integer, comment="50-249 employees")
    CFS04 = Column(Integer, comment="250-499 employees")
    CFS05 = Column(Integer, comment="500+ employees")
    
    job_type = Column(String(4), comment="Job type code (JT00 = all)")
    segment = Column(String(4), comment="Segment code")
    createdate = Column(String(20), comment="Data creation date")
    
    def __repr__(self):
        return f"<ResidenceAreaCharacteristics(h_geocode='{self.h_geocode}', jobs={self.C000})>"


class OriginDestination(Base, TimestampMixin):
    """LODES Origin-Destination (OD) Flow Data
    
    Describes commute flows between census blocks
    (where workers live vs. where they work).
    """
    
    __tablename__ = 'lodes_od'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Geography
    w_geocode = Column(String(15), index=True, comment="Workplace block GEOID")
    h_geocode = Column(String(15), index=True, comment="Residence block GEOID")
    state = Column(String(2), index=True, comment="State FIPS code")
    year = Column(String(4), index=True, comment="Data year")
    
    # Job flows by segment
    S000 = Column(Integer, comment="Total jobs in flow")
    SA01 = Column(Integer, comment="Age 29 or younger")
    SA02 = Column(Integer, comment="Age 30 to 54")
    SA03 = Column(Integer, comment="Age 55 or older")
    SE01 = Column(Integer, comment="Earnings $1,250/month or less")
    SE02 = Column(Integer, comment="Earnings $1,251-$3,333/month")
    SE03 = Column(Integer, comment="Earnings $3,334/month or more")
    SI01 = Column(Integer, comment="Goods Producing")
    SI02 = Column(Integer, comment="Trade/Transport/Utilities")
    SI03 = Column(Integer, comment="All Other")
    
    job_type = Column(String(4), comment="Job type code (JT00 = all)")
    segment = Column(String(4), comment="Segment code")
    createdate = Column(String(20), comment="Data creation date")
    
    def __repr__(self):
        return f"<OriginDestination(w='{self.w_geocode}', h='{self.h_geocode}', jobs={self.S000})>"

