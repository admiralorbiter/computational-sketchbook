# Base API Blueprint Class

from flask import Blueprint, jsonify, request
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class BaseAPI:
    """Base class for API blueprints with common functionality"""
    
    def __init__(self, name, import_name):
        self.bp = Blueprint(name, import_name)
        self.register_routes()
        self.register_error_handlers()
    
    def register_routes(self):
        """Override in subclass"""
        pass
    
    def register_error_handlers(self):
        """Common error handlers for all blueprints"""
        @self.bp.errorhandler(400)
        def bad_request(e):
            return jsonify({'error': 'Bad request', 'message': str(e)}), 400
        
        @self.bp.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Not found'}), 404
        
        @self.bp.errorhandler(500)
        def internal_error(e):
            logger.error(f"Internal server error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def validate_bbox(self, bbox_param):
        """Validate and parse bbox parameter"""
        if not bbox_param:
            return None
        
        try:
            bbox = [float(x) for x in bbox_param.split(',')]
            if len(bbox) != 4:
                raise ValueError("bbox must have 4 coordinates")
            return bbox
        except ValueError as e:
            raise ValueError(f"Invalid bbox format: {e}")
    
    def validate_limit(self, limit_param, default=2000, max_limit=5000):
        """Validate and parse limit parameter"""
        try:
            limit = int(limit_param) if limit_param else default
            return min(limit, max_limit)
        except ValueError:
            return default
    
    def validate_offset(self, offset_param):
        """Validate and parse offset parameter"""
        try:
            return int(offset_param) if offset_param else 0
        except ValueError:
            return 0
