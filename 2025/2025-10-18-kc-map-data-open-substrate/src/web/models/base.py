# Base Model for SQLAlchemy

from sqlalchemy import Column, Integer, DateTime, func, Float
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class SpatialMixin:
    """Mixin for spatial geometry columns"""
    
    geometry = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column('lat', Float, nullable=False)
    longitude = Column('lon', Float, nullable=False)

class BaseModel(Base, TimestampMixin):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
