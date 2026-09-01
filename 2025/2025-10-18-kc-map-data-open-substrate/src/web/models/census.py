# Census TIGER Boundary Models

from sqlalchemy import Column, String, Integer, Float, Text
from geoalchemy2 import Geometry
from .base import Base, TimestampMixin

class BlockGroup(Base, TimestampMixin):
    """Census Block Group Model
    
    Census block groups are the smallest geographic unit for which
    the Census Bureau tabulates sample data from American Community Survey (ACS).
    """
    
    __tablename__ = 'block_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geoid = Column(String(12), nullable=False, unique=True, index=True)
    
    # Geography codes
    statefp = Column('statefp', String(2), nullable=False, index=True)
    countyfp = Column('countyfp', String(3), nullable=False, index=True)
    tractce = Column('tractce', String(6), nullable=False, index=True)
    blkgrpce = Column('blkgrpce', String(1), nullable=False)
    
    # Geometry (POLYGON)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Display names
    name = Column(String(100))
    namelsad = Column(String(100))
    
    # Additional TIGER attributes
    lsad = Column(String(2))
    aland = Column(Float)
    awater = Column(Float)
    
    # ACS Demographic Data (2019-2023 5-year estimates)
    # Population
    population = Column(Integer)
    
    # Median Household Income
    median_household_income = Column(Integer)
    mhi_moe = Column(Integer)  # Margin of Error at 90% confidence level
    
    # Poverty Statistics
    poverty_universe = Column(Integer)
    poverty_count = Column(Integer)
    poverty_rate = Column(Float)  # Calculated: poverty_count / poverty_universe
    
    # Race and Ethnicity
    total_race = Column(Integer)  # B03002_001E
    white_alone = Column(Integer)  # B03002_003E
    black_alone = Column(Integer)  # B03002_004E
    hispanic_latino = Column(Integer)  # B03002_012E
    
    # ACS Metadata
    acs_year = Column(String(10))  # e.g., "2019-2023"
    acs_release = Column(String(20))  # Release date or version
    
    def __repr__(self):
        return f"<BlockGroup(geoid='{self.geoid}', state={self.statefp}, county={self.countyfp})>"


class Block(Base, TimestampMixin):
    """Census Block Model
    
    Census blocks are the smallest geographic unit used by the Census Bureau
    for decennial census tabulation. Blocks are defined by streets, roads,
    railroads, rivers, and other visible features.
    """
    
    __tablename__ = 'blocks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geoid = Column(String(15), nullable=False, unique=True, index=True)
    
    # Geography codes (full hierarchy)
    statefp = Column('statefp', String(2), nullable=False, index=True)
    countyfp = Column('countyfp', String(3), nullable=False, index=True)
    tractce = Column('tractce', String(6), nullable=False, index=True)
    blockce = Column('blockce', String(4), nullable=False)
    
    # Geometry (POLYGON)
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Display names
    name = Column(String(100))
    
    # Additional TIGER attributes
    aland = Column(Float)
    awater = Column(Float)
    
    def __repr__(self):
        return f"<Block(geoid='{self.geoid}', state={self.statefp}, county={self.countyfp}, tract={self.tractce}, block={self.blockce})>"

