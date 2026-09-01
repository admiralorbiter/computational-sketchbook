# Employment Data API Blueprint

from .base import BaseAPI
from flask import jsonify, request
from ..services.employment_service import EmploymentService

class EmploymentAPI(BaseAPI):
    """Employment (LODES) data API endpoints"""
    
    def __init__(self):
        super().__init__('employment', __name__)
        self.employment_service = EmploymentService()
    
    def register_routes(self):
        """Register Employment API routes"""
        
        @self.bp.route('/workplace', methods=['GET'])
        def get_workplace_jobs():
            """Get jobs by workplace location (WAC)
            
            Query params:
                - bbox: comma-separated [min_x,min_y,max_x,max_y]
                - industry_sector: integer 1-20 (NAICS sector)
                - earnings_range: 'low' (<=$1250), 'mid' ($1251-3333), 'high' (>=$3334)
                - limit: maximum records to return
                - format: 'geojson' (default) or 'summary'
            """
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                industry_sector = request.args.get('industry_sector', type=int)
                earnings_range = request.args.get('earnings_range')
                limit = request.args.get('limit', 10000, type=int)
                output_format = request.args.get('format', 'geojson')
                
                # Get workplace jobs
                gdf = self.employment_service.get_workplace_jobs(
                    bbox=bbox,
                    industry_sector=industry_sector,
                    earnings_range=earnings_range,
                    limit=limit
                )
                
                if gdf.empty:
                    return jsonify({
                        'type': 'FeatureCollection',
                        'features': [],
                        'metadata': {'count': 0}
                    })
                
                if output_format == 'summary':
                    # Return summary statistics
                    total_jobs = int(gdf['C000'].sum())
                    top_industries = []
                    
                    for i in range(1, 21):
                        col = f'CNS{i:02d}'
                        if col in gdf.columns:
                            total = int(gdf[col].sum())
                            if total > 0:
                                top_industries.append({'industry': i, 'jobs': total})
                    
                    top_industries.sort(key=lambda x: x['jobs'], reverse=True)
                    
                    return jsonify({
                        'total_jobs': total_jobs,
                        'total_blocks': len(gdf),
                        'top_industries': top_industries[:10],
                        'metadata': {
                            'industry_sector': industry_sector,
                            'earnings_range': earnings_range,
                            'bbox': bbox
                        }
                    })
                else:
                    # Return GeoJSON
                    features = gdf[['w_geocode', 'C000', 'geometry']].to_crs(4326).__geo_interface__['features']
                    return jsonify({
                        'type': 'FeatureCollection',
                        'features': features,
                        'metadata': {
                            'count': len(features),
                            'total_jobs': int(gdf['C000'].sum())
                        }
                    })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/residence', methods=['GET'])
        def get_residence_jobs():
            """Get jobs by residence location (RAC)
            
            Query params:
                - bbox: comma-separated [min_x,min_y,max_x,max_y]
                - age_group: 'young' (<=29), 'middle' (30-54), 'senior' (>=55)
                - limit: maximum records to return
                - format: 'geojson' (default) or 'summary'
            """
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                age_group = request.args.get('age_group')
                limit = request.args.get('limit', 10000, type=int)
                output_format = request.args.get('format', 'geojson')
                
                gdf = self.employment_service.get_residence_jobs(
                    bbox=bbox,
                    age_group=age_group,
                    limit=limit
                )
                
                if gdf.empty:
                    return jsonify({
                        'type': 'FeatureCollection',
                        'features': [],
                        'metadata': {'count': 0}
                    })
                
                if output_format == 'summary':
                    total_workers = gdf['C000'].sum()
                    return jsonify({
                        'total_workers': int(total_workers),
                        'total_blocks': len(gdf),
                        'age_groups': {
                            'young': int(gdf['CA01'].sum()),
                            'middle': int(gdf['CA02'].sum()),
                            'senior': int(gdf['CA03'].sum())
                        },
                        'metadata': {
                            'age_group': age_group,
                            'bbox': bbox
                        }
                    })
                else:
                    features = gdf[['h_geocode', 'C000', 'geometry']].to_crs(4326).__geo_interface__['features']
                    return jsonify({
                        'type': 'FeatureCollection',
                        'features': features,
                        'metadata': {
                            'count': len(features),
                            'total_workers': int(gdf['C000'].sum())
                        }
                    })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/flows', methods=['GET'])
        def get_commute_flows():
            """Get origin-destination commute flows
            
            Query params:
                - bbox: comma-separated [min_x,min_y,max_x,max_y]
                - min_jobs: minimum jobs in a flow (default: 1)
                - limit: maximum flows to return (default: 5000)
            """
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                min_jobs = request.args.get('min_jobs', 1, type=int)
                limit = request.args.get('limit', 5000, type=int)
                
                gdf = self.employment_service.get_commute_flows(
                    bbox=bbox,
                    min_jobs=min_jobs,
                    limit=limit
                )
                
                if gdf.empty:
                    return jsonify({
                        'type': 'FeatureCollection',
                        'features': [],
                        'metadata': {'count': 0}
                    })
                
                # Convert to GeoJSON LineString features
                features = []
                for idx, row in gdf.iterrows():
                    feature = {
                        'type': 'Feature',
                        'geometry': row.geometry.__geo_interface__,
                        'properties': {
                            'w_geocode': row['w_geocode'],
                            'h_geocode': row['h_geocode'],
                            'jobs': int(row['S000']),
                            'age_young': int(row.get('SA01', 0)),
                            'age_middle': int(row.get('SA02', 0)),
                            'age_senior': int(row.get('SA03', 0)),
                            'earnings_low': int(row.get('SE01', 0)),
                            'earnings_mid': int(row.get('SE02', 0)),
                            'earnings_high': int(row.get('SE03', 0))
                        }
                    }
                    features.append(feature)
                
                return jsonify({
                    'type': 'FeatureCollection',
                    'features': features,
                    'metadata': {
                        'count': len(features),
                        'min_jobs': min_jobs,
                        'bbox': bbox
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/stats', methods=['GET'])
        def get_employment_stats():
            """Get employment statistics for a geographic area
            
            Query params:
                - geoid: census block or block group GEOID
                - level: 'block' or 'block_group'
            """
            try:
                geoid = request.args.get('geoid')
                level = request.args.get('level', 'block')
                
                if not geoid:
                    return jsonify({'error': 'geoid parameter required'}), 400
                
                # For now, return placeholder
                return jsonify({
                    'geoid': geoid,
                    'level': level,
                    'stats': {
                        'total_jobs': 0,
                        'total_workers': 0,
                        'top_industries': []
                    },
                    'message': 'Stats endpoint not yet implemented'
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/industries', methods=['GET'])
        def get_top_industries():
            """Get top industries by job count
            
            Query params:
                - bbox: spatial filter
                - limit: number of industries to return (default: 10)
            """
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                limit = request.args.get('limit', 10, type=int)
                
                df = self.employment_service.get_top_industries(bbox=bbox, limit=limit)
                
                if df.empty:
                    return jsonify({'industries': [], 'total': 0})
                
                industries = df.to_dict('records')
                total = df['job_count'].sum()
                
                return jsonify({
                    'industries': industries,
                    'total_jobs': int(total),
                    'count': len(industries)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.bp.route('/balance', methods=['GET'])
        def get_jobs_housing_balance():
            """Get jobs-to-housing balance analysis
            
            Query params:
                - bbox: spatial filter
            """
            try:
                bbox = self.validate_bbox(request.args.get('bbox'))
                
                df = self.employment_service.calculate_jobs_housing_balance(bbox=bbox)
                
                if df.empty:
                    return jsonify({'balance': [], 'summary': {}})
                
                # Calculate summary statistics
                total_jobs = df['jobs'].sum()
                total_workers = df['workers'].sum()
                balance_ratio = total_jobs / total_workers if total_workers > 0 else 0
                
                return jsonify({
                    'summary': {
                        'total_jobs': int(total_jobs),
                        'total_workers': int(total_workers),
                        'overall_balance': round(balance_ratio, 2),
                        'blocks_analyzed': len(df)
                    },
                    'details': df.to_dict('records')
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

