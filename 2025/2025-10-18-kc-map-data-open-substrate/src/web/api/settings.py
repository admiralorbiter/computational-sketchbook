# Settings API Blueprint

from .base import BaseAPI
from flask import jsonify, request

class SettingsAPI(BaseAPI):
    """User settings API endpoints"""
    
    def __init__(self):
        super().__init__('settings', __name__)
    
    def register_routes(self):
        """Register settings API routes"""
        
        @self.bp.route('/', methods=['GET'])
        def get_settings():
            """Get current user settings"""
            try:
                # Default settings
                default_settings = {
                    'consolidation': {
                        'enabled': True,
                        'strategy': 'hybrid',
                        'address_tolerance': 0.0001,
                        'coordinate_precision': 1,
                        'min_records_to_consolidate': 2
                    },
                    'map': {
                        'default_zoom': 18,
                        'default_center': [38.99, -94.56]
                    },
                    'filters': {
                        'persist_on_reload': True
                    }
                }
                
                return jsonify({
                    'settings': default_settings,
                    'metadata': {
                        'version': '1.0'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/', methods=['PUT'])
        def update_settings():
            """Update user settings"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                # Validate settings structure
                if 'consolidation' in data:
                    consolidation = data['consolidation']
                    if 'enabled' in consolidation:
                        if not isinstance(consolidation['enabled'], bool):
                            return jsonify({'error': 'consolidation.enabled must be boolean'}), 400
                
                # For now, just return success (settings stored in localStorage on frontend)
                return jsonify({
                    'message': 'Settings updated successfully',
                    'settings': data
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/consolidation/presets', methods=['GET'])
        def get_consolidation_presets():
            """Get consolidation presets"""
            try:
                presets = {
                    'aggressive': {
                        'address_tolerance': 0.0001,
                        'coordinate_precision': 2,
                        'min_records': 1,
                        'description': 'Groups records very tightly together'
                    },
                    'balanced': {
                        'address_tolerance': 0.00005,
                        'coordinate_precision': 3,
                        'min_records': 2,
                        'description': 'Balanced grouping for most use cases'
                    },
                    'loose': {
                        'address_tolerance': 0.00001,
                        'coordinate_precision': 4,
                        'min_records': 3,
                        'description': 'Minimal grouping, shows more individual records'
                    }
                }
                
                return jsonify({
                    'presets': presets,
                    'metadata': {
                        'default': 'balanced'
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
