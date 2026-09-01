"""Geospatial utility functions."""

import logging
import geopandas as gpd
from shapely.geometry import Point

logger = logging.getLogger(__name__)


def buffer_point(point: Point, distance_meters: float):
    """Create a buffer around a point in meters.
    
    Args:
        point: Shapely Point geometry
        distance_meters: Buffer distance in meters
    
    Returns:
        Buffered polygon geometry
    """
    # TODO: Implement proper coordinate system transformation
    # May need to project to UTM or local CRS before buffering
    pass


def spatial_join_points_to_polygons(points_gdf, polygons_gdf, how: str = "left"):
    """Perform spatial join of points to polygons.
    
    Args:
        points_gdf: GeoDataFrame of points
        polygons_gdf: GeoDataFrame of polygons
        how: Type of join (left, right, inner, outer)
    
    Returns:
        GeoDataFrame with joined data
    """
    logger.info(f"Performing spatial join: {how} join")
    return gpd.sjoin(points_gdf, polygons_gdf, how=how, predicate="within")


def calculate_distance(point1: Point, point2: Point, crs: str = "EPSG:4326"):
    """Calculate distance between two points.
    
    Args:
        point1: First point
        point2: Second point
        crs: Coordinate reference system
    
    Returns:
        Distance in meters
    """
    # TODO: Implement distance calculation with proper CRS handling
    pass
