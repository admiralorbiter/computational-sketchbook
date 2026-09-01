#!/usr/bin/env python3
"""
Kansas City Data Platform - Refactored Application

Clean, modular Flask application using blueprints and service layer.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, request
from flask_caching import Cache

# Import configuration
from web.config import config

# Import API blueprints
from web.api.crime import CrimeAPI
from web.api.service_requests import ServiceRequestsAPI
from web.api.businesses import BusinessAPI
from web.api.dangerous_buildings import DangerousBuildingsAPI
from web.api.landbank import LandBankAPI
from web.api.osm import OSMAPI
from web.api.combined import CombinedAPI
from web.api.settings import SettingsAPI
from web.api.geocoding import geocoding_bp
from web.api.census import CensusAPI
from web.api.block_group_analysis import BlockGroupAnalysisAPI
from web.api.employment import EmploymentAPI

def create_app(config_name=None):
    """Create and configure Flask application"""
    
    # Determine config
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Initialize Flask app
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize cache
    cache = Cache(app)
    
    # Initialize global consolidation service
    from web.services.consolidation_service import ConsolidationService
    global_consolidation_service = ConsolidationService()
    
    # Initialize API blueprints
    crime_api = CrimeAPI()
    service_requests_api = ServiceRequestsAPI()
    businesses_api = BusinessAPI()
    dangerous_buildings_api = DangerousBuildingsAPI()
    landbank_api = LandBankAPI()
    osm_api = OSMAPI()
    combined_api = CombinedAPI()
    settings_api = SettingsAPI()
    census_api = CensusAPI()
    analysis_api = BlockGroupAnalysisAPI()
    employment_api = EmploymentAPI()
    
    # Register blueprints
    app.register_blueprint(crime_api.bp, url_prefix='/api/v1/crime')
    app.register_blueprint(service_requests_api.bp, url_prefix='/api/v1/311')
    app.register_blueprint(businesses_api.bp, url_prefix='/api/v1/businesses')
    app.register_blueprint(dangerous_buildings_api.bp, url_prefix='/api/v1/dangerous_buildings')
    app.register_blueprint(landbank_api.bp, url_prefix='/api/v1/landbank')
    app.register_blueprint(osm_api.bp, url_prefix='/api/v1/osm')
    app.register_blueprint(combined_api.bp, url_prefix='/api/v1/combined')
    app.register_blueprint(settings_api.bp, url_prefix='/api/v1/settings')
    app.register_blueprint(census_api.bp, url_prefix='/api/v1/census')
    app.register_blueprint(analysis_api.bp, url_prefix='/api/v1/analysis')
    app.register_blueprint(employment_api.bp, url_prefix='/api/v1/employment')
    app.register_blueprint(geocoding_bp)
    
    # Legacy endpoints for backward compatibility
    @app.route('/')
    def index():
        """Serve the main map interface"""
        return render_template('index.html')
    
    @app.route('/analysis')
    def analysis():
        """Serve the analysis view"""
        return render_template('analysis.html')
    
    @app.route('/api/layers')
    def api_layers():
        """Get information about available layers (legacy endpoint)"""
        try:
            from web.services.data_service import DataService
            data_service = DataService()
            layers = data_service.get_all_layer_info()
            return jsonify(layers)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """Get database statistics (legacy endpoint)"""
        try:
            from web.services.data_service import DataService
            data_service = DataService()
            layers = data_service.get_all_layer_info()
            total_features = sum(layer.get('count', 0) for layer in layers.values())
            
            return jsonify({
                "total_features": total_features,
                "layers": layers,
                "consolidation_enabled": app.config.get('CONSOLIDATION_ENABLED', True)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/features/<layer_name>')
    def api_features_legacy(layer_name):
        """Legacy features endpoint for backward compatibility"""
        try:
            from web.services.data_service import DataService
            data_service = DataService()
            
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
            filter_type = request.args.get('filter')
            consolidate = request.args.get('consolidate', 'false').lower() == 'true'
            
            # Get features
            features = data_service.get_layer_features(layer_name, bbox, limit)
            
            # Apply consolidation if requested
            if consolidate and features:
                from web.services.consolidation_service import ConsolidationService
                consolidation_service = ConsolidationService()
                
                if layer_name in ['service_requests', 'crime']:
                    features = consolidation_service.aggregate_kc_features(features, layer_name)
                elif layer_name == 'points':
                    features = consolidation_service.aggregate_osm_points(features)
            
            return jsonify({
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "layer": layer_name,
                    "consolidated": consolidate,
                    "count": len(features)
                }
            })
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/features/consolidated')
    def api_consolidated_features_legacy():
        """Legacy consolidated features endpoint"""
        try:
            from web.services.data_service import DataService
            from web.services.consolidation_service import ConsolidationService
            from web.services.filter_service import FilterService
            
            data_service = DataService()
            consolidation_service = ConsolidationService()
            filter_service = FilterService()
            
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
            
            # Parse filters for each layer
            layers_param = request.args.get('layers', 'service_requests,crime,points')
            requested_layers = [l.strip() for l in layers_param.split(',')]
            
            # Parse filters for each layer
            layer_filters = {}
            for layer in requested_layers:
                layer_filters[layer] = {}
                
                # Parse issue_type filter for service_requests
                if layer == 'service_requests' and request.args.get('service_requests_issue_type'):
                    layer_filters[layer]['issue_type'] = request.args.get('service_requests_issue_type')
                
                # Parse offense_type filter for crime
                if layer == 'crime' and request.args.get('crime_offense_type'):
                    layer_filters[layer]['offense_type'] = request.args.get('crime_offense_type')
                
                # Parse business filters
                if layer == 'businesses':
                    if request.args.get('businesses_source'):
                        source_val = request.args.get('businesses_source')
                        layer_filters[layer]['source'] = source_val.split(',') if ',' in source_val else [source_val]
                    if request.args.get('businesses_business_type'):
                        type_val = request.args.get('businesses_business_type')
                        layer_filters[layer]['business_type'] = type_val.split(',') if ',' in type_val else [type_val]
                    if request.args.get('businesses_industry'):
                        industry_val = request.args.get('businesses_industry')
                        layer_filters[layer]['industry'] = industry_val.split(',') if ',' in industry_val else [industry_val]
                    if request.args.get('businesses_search_text'):
                        layer_filters[layer]['search_text'] = request.args.get('businesses_search_text')
                
                # Parse dangerous buildings filters
                if layer == 'dangerous_buildings':
                    if request.args.get('dangerous_buildings_status_of_case'):
                        status_val = request.args.get('dangerous_buildings_status_of_case')
                        layer_filters[layer]['status_of_case'] = status_val.split(',') if ',' in status_val else [status_val]
                    if request.args.get('dangerous_buildings_council_district'):
                        district_val = request.args.get('dangerous_buildings_council_district')
                        layer_filters[layer]['council_district'] = district_val.split(',') if ',' in district_val else [district_val]
                    if request.args.get('dangerous_buildings_search_text'):
                        layer_filters[layer]['search_text'] = request.args.get('dangerous_buildings_search_text')
            
            # Get features from requested layers only
            all_features = {}
            for layer in requested_layers:
                filters = layer_filters.get(layer, {})
                features = data_service.get_layer_features(layer, bbox, limit, filters)
                if features:
                    all_features[layer] = features
            
            # Apply cross-layer consolidation using global service
            consolidated_features = global_consolidation_service.aggregate_cross_layer_features(all_features)
            
            # Calculate source counts for each layer
            source_counts = {}
            for layer_name, features in all_features.items():
                source_counts[layer_name] = len(features)
            
            return jsonify({
                "type": "FeatureCollection",
                "features": consolidated_features,
                "metadata": {
                    "consolidated": True,
                    "cross_layer": True,
                    "count": len(consolidated_features),
                    "source_layers": list(all_features.keys()),
                    "source_counts": source_counts
                }
            })
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/filters/<layer_name>')
    def api_filters_legacy(layer_name):
        """Legacy filters endpoint for backward compatibility"""
        try:
            from web.services.filter_service import FilterService
            filter_service = FilterService()
            
            if layer_name == 'service_requests':
                from web.models.service_requests import ServiceRequest
                options = filter_service.get_filter_options(ServiceRequest)
            elif layer_name == 'crime':
                from web.models.crime import CrimeIncident
                options = filter_service.get_filter_options(CrimeIncident)
            elif layer_name == 'businesses':
                from web.models.business import Business
                options = filter_service.get_filter_options(Business)
            elif layer_name == 'points':
                options = filter_service.get_osm_filter_options('points')
            else:
                return jsonify({'error': f'Unknown layer: {layer_name}'}), 400
            
            return jsonify({
                'filters': options,
                'metadata': {
                    'layer': layer_name
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/consolidation', methods=['PUT'])
    def update_consolidation_settings():
        """Update global consolidation settings"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Apply settings to global consolidation service
            global_consolidation_service.apply_settings(data)
            
            return jsonify({
                'message': 'Consolidation settings updated successfully',
                'settings': data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "cache": "active",
            "architecture": "blueprint-based"
        })
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("Starting Kansas City Data Platform (Refactored)...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {app.config['DEBUG']}")
    
    # Get and display layer information
    try:
        from web.services.data_service import DataService
        data_service = DataService()
        layers = data_service.get_all_layer_info()
        print("\nAvailable layers:")
        for layer_name, info in layers.items():
            print(f"  {info['name']}: {info['count']} features")
    except Exception as e:
        print(f"Could not read layer information: {e}")
    
    print("\nStarting server at http://localhost:5000")
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
