# GeoJSON Utilities

def model_to_geojson(instance, layer_type):
    """Convert SQLAlchemy model instance to GeoJSON feature"""
    try:
        # Get basic properties
        properties = {
            'id': instance.id,
            'type': layer_type
        }
        
        # Add table-specific properties
        if layer_type == 'service_requests':
            properties.update({
                'request_id': getattr(instance, 'request_id', None),
                'issue_type': getattr(instance, 'issue_type', None),
                'current_status': getattr(instance, 'current_status', None),
                'incident_address': getattr(instance, 'incident_address', None),
                'latitude': getattr(instance, 'latitude', None),
                'longitude': getattr(instance, 'longitude', None)
            })
        elif layer_type == 'crime':
            properties.update({
                'report': getattr(instance, 'report', None),
                'offense': getattr(instance, 'offense', None),
                'address': getattr(instance, 'address', None),
                'latitude': getattr(instance, 'latitude', None),
                'longitude': getattr(instance, 'longitude', None)
            })
        elif layer_type == 'businesses':
            properties.update({
                'business_name': getattr(instance, 'business_name', None),
                'license_type': getattr(instance, 'license_type', None),
                'business_address': getattr(instance, 'business_address', None),
                'latitude': getattr(instance, 'latitude', None),
                'longitude': getattr(instance, 'longitude', None)
            })
        elif layer_type == 'inspections':
            properties.update({
                'establishment_name': getattr(instance, 'establishment_name', None),
                'inspection_type': getattr(instance, 'inspection_type', None),
                'establishment_address': getattr(instance, 'establishment_address', None),
                'latitude': getattr(instance, 'latitude', None),
                'longitude': getattr(instance, 'longitude', None)
            })
        
        # Create geometry
        geometry = {
            'type': 'Point',
            'coordinates': [instance.longitude, instance.latitude]
        }
        
        return {
            'type': 'Feature',
            'properties': properties,
            'geometry': geometry
        }
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error converting item to GeoJSON: {e}")
        return None

def convert_to_geojson(item, table_name):
    """Convert a database item to GeoJSON feature (legacy compatibility)"""
    try:
        # Get basic properties
        properties = {
            'id': item.id,
            'type': table_name
        }
            
        # Add table-specific properties
        if table_name == 'service_requests_311':
            properties.update({
                'request_id': getattr(item, 'request_id', None),
                'issue_type': getattr(item, 'issue_type', None),
                'current_status': getattr(item, 'current_status', None),
                'incident_address': getattr(item, 'incident_address', None),
                'latitude': getattr(item, 'latitude', None),
                'longitude': getattr(item, 'longitude', None)
            })
        elif table_name == 'crime_incidents':
            properties.update({
                'report': getattr(item, 'report', None),
                'offense': getattr(item, 'offense', None),
                'address': getattr(item, 'address', None),
                'latitude': getattr(item, 'latitude', None),
                'longitude': getattr(item, 'longitude', None)
            })
        elif table_name == 'business_licenses':
            properties.update({
                'business_name': getattr(item, 'business_name', None),
                'license_type': getattr(item, 'license_type', None),
                'business_address': getattr(item, 'business_address', None),
                'latitude': getattr(item, 'latitude', None),
                'longitude': getattr(item, 'longitude', None)
            })
        elif table_name == 'food_inspections':
            properties.update({
                'establishment_name': getattr(item, 'establishment_name', None),
                'inspection_type': getattr(item, 'inspection_type', None),
                'establishment_address': getattr(item, 'establishment_address', None),
                'latitude': getattr(item, 'latitude', None),
                'longitude': getattr(item, 'longitude', None)
            })
        
        # Create geometry
        geometry = {
            'type': 'Point',
            'coordinates': [item.longitude, item.latitude]
        }
        
        return {
            'type': 'Feature',
            'properties': properties,
            'geometry': geometry
        }
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error converting item to GeoJSON: {e}")
        return None
