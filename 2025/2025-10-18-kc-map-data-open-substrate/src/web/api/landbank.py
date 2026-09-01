"""
Land Bank API Blueprint

Provides REST API endpoints for Land Bank and Kansas City Homesteading Authority data.
"""

from flask import Blueprint, request, jsonify
from web.services.data_service import DataService
from web.services.filter_service import FilterService
from web.models.landbank import LandBankProperty
import logging

logger = logging.getLogger(__name__)

class LandBankAPI:
    """Land Bank API endpoints"""
    
    def __init__(self):
        self.bp = Blueprint('landbank', __name__)
        self.data_service = DataService()
        self.filter_service = FilterService()
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.bp.route('/properties', methods=['GET'])
        def get_properties():
            """Get Land Bank properties within bounding box"""
            try:
                # Get query parameters
                bbox_param = request.args.get('bbox')
                if not bbox_param:
                    return jsonify({"error": "bbox parameter required"}), 400
                
                try:
                    bbox = [float(x) for x in bbox_param.split(',')]
                    if len(bbox) != 4:
                        raise ValueError("bbox must have 4 coordinates")
                except ValueError as e:
                    return jsonify({"error": f"Invalid bbox format: {e}"}), 400
                
                limit = request.args.get('limit', 2000, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                # Parse filters
                filters = {}
                if request.args.get('property_status'):
                    filters['property_status'] = request.args.get('property_status')
                if request.args.get('inventory_type'):
                    filters['inventory_type'] = request.args.get('inventory_type')
                if request.args.get('neighborhood'):
                    filters['neighborhood'] = request.args.get('neighborhood')
                if request.args.get('council_district'):
                    filters['city_council_district'] = request.args.get('council_district')
                if request.args.get('property_class'):
                    filters['property_class'] = request.args.get('property_class')
                if request.args.get('property_condition'):
                    filters['property_condition'] = request.args.get('property_condition')
                if request.args.get('demo_needed'):
                    filters['demo_needed'] = request.args.get('demo_needed')
                if request.args.get('search'):
                    filters['search_text'] = request.args.get('search')
                
                # Get features using data service
                features = self.data_service.get_layer_features('landbank_properties', bbox, limit, filters)
                
                return jsonify({
                    "type": "FeatureCollection",
                    "features": features,
                    "metadata": {
                        "layer": "landbank_properties",
                        "count": len(features),
                        "filters_applied": filters
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting Land Bank properties: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.bp.route('/properties/<int:property_id>', methods=['GET'])
        def get_property(property_id):
            """Get single Land Bank property by ID"""
            try:
                # This would need to be implemented in DataService
                # For now, return a placeholder
                return jsonify({"error": "Single property endpoint not yet implemented"}), 501
                
            except Exception as e:
                logger.error(f"Error getting Land Bank property {property_id}: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_stats():
            """Get Land Bank statistics"""
            try:
                # Get basic stats from all layer info
                all_layers = self.data_service.get_all_layer_info()
                stats = all_layers.get('landbank_properties', {})
                
                # Get additional statistics
                additional_stats = self._get_additional_stats()
                
                return jsonify({
                    "total_properties": stats.get('count', 0),
                    "properties_with_coordinates": additional_stats.get('with_coordinates', 0),
                    "properties_by_status": additional_stats.get('by_status', {}),
                    "properties_by_type": additional_stats.get('by_type', {}),
                    "properties_by_neighborhood": additional_stats.get('by_neighborhood', {}),
                    "average_market_value": additional_stats.get('avg_market_value', 0),
                    "total_market_value": additional_stats.get('total_market_value', 0)
                })
                
            except Exception as e:
                logger.error(f"Error getting Land Bank stats: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.bp.route('/filters', methods=['GET'])
        def get_filters():
            """Get available filter options for Land Bank properties"""
            try:
                options = self.filter_service.get_filter_options(LandBankProperty)
                return jsonify({
                    'filters': options,
                    'metadata': {
                        'layer': 'landbank_properties'
                    }
                })
                
            except Exception as e:
                logger.error(f"Error getting Land Bank filters: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _get_additional_stats(self):
        """Get additional statistics for Land Bank properties"""
        try:
            # This would query the database for additional stats
            # For now, return placeholder data
            return {
                'with_coordinates': 0,
                'by_status': {},
                'by_type': {},
                'by_neighborhood': {},
                'avg_market_value': 0,
                'total_market_value': 0
            }
        except Exception as e:
            logger.error(f"Error getting additional stats: {e}")
            return {}
