# OSM Feature Model

from sqlalchemy import Column, String, Text, Integer, Float, Boolean
from geoalchemy2 import Geometry
from .base import BaseModel

class OSMFeature(BaseModel):
    """OpenStreetMap feature data"""
    
    __tablename__ = 'osm_features'
    
    # OSM fields
    osm_id = Column(Integer, unique=True, nullable=False, index=True)
    osm_type = Column(String(10), nullable=False, index=True)  # node, way, relation
    feature_type = Column(String(50), nullable=False, index=True)  # building, road, poi, etc.
    
    # Geometry
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    
    # Tags (stored as JSON string for flexibility)
    tags = Column(Text)  # JSON string of OSM tags
    
    # Common tag fields (indexed for performance)
    name = Column(String(200), index=True)
    amenity = Column(String(100), index=True)
    shop = Column(String(100), index=True)
    tourism = Column(String(100), index=True)
    leisure = Column(String(100), index=True)
    office = Column(String(100), index=True)
    healthcare = Column(String(100), index=True)
    education = Column(String(100), index=True)
    
    # Address fields
    street = Column(String(200), index=True)
    housenumber = Column(String(20), index=True)
    city = Column(String(100), index=True)
    state = Column(String(50), index=True)
    postcode = Column(String(20), index=True)
    
    # Additional fields
    website = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100))
    opening_hours = Column(String(200))
    
    def __repr__(self):
        return f"<OSMFeature(osm_id={self.osm_id}, type='{self.feature_type}')>"
