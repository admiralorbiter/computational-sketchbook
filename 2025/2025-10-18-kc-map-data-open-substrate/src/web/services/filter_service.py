# Filter Service

from sqlalchemy import or_, and_
from typing import Dict, List, Any
import logging
from ..models.business import Business

logger = logging.getLogger(__name__)

class FilterService:
    """Service for applying filters to queries"""
    
    def __init__(self):
        pass
    
    def apply_filters(self, query, model_class, filter_type):
        """Apply filters to the query based on model and filter type"""
        
        if model_class.__tablename__ == 'service_requests_311':
            if filter_type in ['Property Violations', 'Animal Services', 'Illegal Dumping']:
                return query.filter(model_class.issue_type == filter_type)
            elif filter_type == 'new':
                return query.filter(model_class.current_status == 'new')
            elif filter_type == 'resolved':
                return query.filter(model_class.current_status == 'resolved')
        
        elif model_class.__tablename__ == 'crime_incidents':
            if filter_type in ['Assault', 'Burglary', 'Theft', 'Robbery']:
                return query.filter(model_class.offense.like(f'%{filter_type}%'))
            elif filter_type == 'violent':
                return query.filter(
                    model_class.offense.like('%Assault%') | 
                    model_class.offense.like('%Robbery%') |
                    model_class.offense.like('%Homicide%')
                )
            elif filter_type == 'property':
                return query.filter(
                    model_class.offense.like('%Burglary%') | 
                    model_class.offense.like('%Theft%') |
                    model_class.offense.like('%Stolen%')
                )
        
        return query
    
    def apply_advanced_filters(self, query, model_class, filters):
        """Apply advanced filters to the query based on model and filter criteria"""
        
        table_name = model_class.__tablename__
        
        # Apply category filters
        if 'offense_type' in filters and filters['offense_type']:
            if table_name == 'crime_incidents':
                offense_list = filters['offense_type'] if isinstance(filters['offense_type'], list) else [filters['offense_type']]
                query = query.filter(model_class.offense.in_(offense_list))
        
        if 'issue_type' in filters and filters['issue_type']:
            if table_name == 'service_requests_311':
                issue_list = filters['issue_type'] if isinstance(filters['issue_type'], list) else [filters['issue_type']]
                query = query.filter(model_class.issue_type.in_(issue_list))
        
        if 'status' in filters and filters['status']:
            if table_name == 'service_requests_311':
                status_list = filters['status'] if isinstance(filters['status'], list) else [filters['status']]
                query = query.filter(model_class.current_status.in_(status_list))
        
        # Apply text search
        if 'search_text' in filters and filters['search_text']:
            search_text = f"%{filters['search_text']}%"
            
            if table_name == 'crime_incidents':
                query = query.filter(or_(
                    model_class.address.ilike(search_text),
                    model_class.offense.ilike(search_text),
                    model_class.report.ilike(search_text)
                ))
            elif table_name == 'service_requests_311':
                query = query.filter(or_(
                    model_class.incident_address.ilike(search_text),
                    model_class.issue_type.ilike(search_text),
                    model_class.description.ilike(search_text)
                ))
            elif table_name == 'businesses':
                query = query.filter(or_(
                    model_class.name.ilike(search_text),
                    model_class.address.ilike(search_text),
                    model_class.business_type.ilike(search_text),
                    model_class.industry.ilike(search_text)
                ))
            elif table_name == 'food_inspections':
                query = query.filter(or_(
                    model_class.establishment_name.ilike(search_text),
                    model_class.establishment_address.ilike(search_text),
                    model_class.inspection_type.ilike(search_text)
                ))
        
        # Apply date range filters
        if 'date_from' in filters and filters['date_from']:
            if table_name == 'crime_incidents' and hasattr(model_class, 'reported_date'):
                query = query.filter(model_class.reported_date >= filters['date_from'])
            elif table_name == 'service_requests_311' and hasattr(model_class, 'created_date'):
                query = query.filter(model_class.created_date >= filters['date_from'])
        
        if 'date_to' in filters and filters['date_to']:
            if table_name == 'crime_incidents' and hasattr(model_class, 'reported_date'):
                query = query.filter(model_class.reported_date <= filters['date_to'])
            elif table_name == 'service_requests_311' and hasattr(model_class, 'created_date'):
                query = query.filter(model_class.created_date <= filters['date_to'])
        
        return query
    
    def get_filter_options(self, model_class):
        """Get available filter options for a model"""
        try:
            from ..utils.database import get_db_session
            session = get_db_session()
            
            options = []
            
            table_name = model_class.__tablename__
            
            if table_name == 'crime_incidents':
                # Get distinct offense types only
                offenses = session.query(model_class.offense).distinct().all()
                options.append({
                    'field': 'offense_type',
                    'label': 'Offense Type',
                    'type': 'multi-select',
                    'options': [o[0] for o in offenses if o[0]]
                })
            
            elif table_name == 'service_requests_311':
                # Get distinct issue types only
                issue_types = session.query(model_class.issue_type).distinct().all()
                options.append({
                    'field': 'issue_type',
                    'label': 'Issue Type',
                    'type': 'multi-select',
                    'options': [i[0] for i in issue_types if i[0]]
                })
            
            elif table_name == 'businesses':
                # Get distinct business types
                business_types = session.query(model_class.business_type).distinct().all()
                options.append({
                    'field': 'business_type',
                    'label': 'Business Type',
                    'type': 'multi-select',
                    'options': [b[0] for b in business_types if b[0]]
                })
                
                # Get distinct sources
                sources = session.query(model_class.source).distinct().all()
                options.append({
                    'field': 'source',
                    'label': 'Data Source',
                    'type': 'multi-select',
                    'options': [s[0] for s in sources if s[0]]
                })
                
                # Get distinct industries
                industries = session.query(model_class.industry).distinct().all()
                options.append({
                    'field': 'industry',
                    'label': 'Industry',
                    'type': 'multi-select',
                    'options': [i[0] for i in industries if i[0]]
                })
            
            session.close()
            return options
            
        except Exception as e:
            logger.error(f"Error getting filter options: {e}")
            return []
    
    def get_business_filter_options(self):
        """Get filter options for business data"""
        try:
            from ..utils.database import get_db_session
            session = get_db_session()
            
            options = []
            
            # Get distinct business types
            business_types = session.query(Business.business_type).distinct().all()
            options.append({
                'field': 'business_type',
                'label': 'Business Type',
                'type': 'multi-select',
                'options': [b[0] for b in business_types if b[0]]
            })
            
            # Get distinct sources
            sources = session.query(Business.source).distinct().all()
            options.append({
                'field': 'source',
                'label': 'Data Source',
                'type': 'multi-select',
                'options': [s[0] for s in sources if s[0]]
            })
            
            # Get distinct industries
            industries = session.query(Business.industry).distinct().all()
            options.append({
                'field': 'industry',
                'label': 'Industry',
                'type': 'multi-select',
                'options': [i[0] for i in industries if i[0]]
            })
            
            session.close()
            return options
            
        except Exception as e:
            logger.error(f"Error getting business filter options: {e}")
            return []
    
    def get_osm_filter_options(self, layer):
        """Get filter options for OSM layers - DISABLED"""
        # No filters for OSM points
        return []
    
    def parse_layer_filters(self, request, requested_layers):
        """Parse layer-specific filters from request"""
        layer_filters = {}
        
        for layer in requested_layers:
            layer_filters[layer] = {}
            
            # Parse offense_type filter for crime
            if layer == 'crime' and request.args.get('crime_offense_type'):
                layer_filters[layer]['offense_type'] = request.args.get('crime_offense_type').split(',')
            
            # Parse issue_type and status filters for service_requests
            if layer == 'service_requests':
                if request.args.get('service_requests_issue_type'):
                    layer_filters[layer]['issue_type'] = request.args.get('service_requests_issue_type').split(',')
                if request.args.get('service_requests_status'):
                    layer_filters[layer]['status'] = request.args.get('service_requests_status').split(',')
            
            # Parse amenity_type filter for points
            if layer == 'points' and request.args.get('points_amenity_type'):
                layer_filters[layer]['amenity_type'] = request.args.get('points_amenity_type').split(',')
            
            # Parse business filters
            if layer == 'businesses':
                if request.args.get('businesses_business_type'):
                    layer_filters[layer]['business_type'] = request.args.get('businesses_business_type').split(',')
                if request.args.get('businesses_source'):
                    layer_filters[layer]['source'] = request.args.get('businesses_source').split(',')
                if request.args.get('businesses_industry'):
                    layer_filters[layer]['industry'] = request.args.get('businesses_industry').split(',')
            
            # Parse search_text for any layer
            if request.args.get(f'{layer}_search_text'):
                layer_filters[layer]['search_text'] = request.args.get(f'{layer}_search_text')
        
        return layer_filters
