# Spatial Utilities

def validate_bbox(bbox):
    """Validate bounding box format and values"""
    if not bbox or len(bbox) != 4:
        return False
    
    minx, miny, maxx, maxy = bbox
    
    # Check that min < max for both dimensions
    if minx >= maxx or miny >= maxy:
        return False
    
    # Check reasonable coordinate ranges (rough bounds for continental US)
    if not (-180 <= minx <= 180) or not (-180 <= maxx <= 180):
        return False
    if not (-90 <= miny <= 90) or not (-90 <= maxy <= 90):
        return False
    
    return True

def parse_bbox(bbox_param):
    """Parse and validate bbox parameter"""
    if not bbox_param:
        return None
    
    try:
        bbox = [float(x) for x in bbox_param.split(',')]
        if len(bbox) != 4:
            raise ValueError("bbox must have 4 coordinates")
        
        if validate_bbox(bbox):
            return bbox
        else:
            raise ValueError("Invalid bbox values")
            
    except ValueError as e:
        raise ValueError(f"Invalid bbox format: {e}")

def parse_radius(radius_param):
    """Parse and validate radius parameter"""
    try:
        radius = float(radius_param)
        if radius <= 0:
            raise ValueError("Radius must be positive")
        if radius > 50000:  # Max 50km
            raise ValueError("Radius too large")
        return radius
    except ValueError as e:
        raise ValueError(f"Invalid radius: {e}")
