from routes.common.db import get_db_session, get_access_filters, paginate_query
from routes.common.models import Category, MenuItem, Variation, Addon
from routes.common.utils import create_response, parse_body, get_path_parameter, get_pagination_params
def menuHandler(event, context):
    """Handler for /menu endpoints"""
    http_method = event.get('httpMethod')
    
    # This endpoint should only support GET
    if http_method != 'GET':
        return create_response(405, {'error': 'Method Not Allowed'})
    
    try:
        # Get outlet_id for access control
        access_filters = get_access_filters(event)
        if access_filters.get('statusCode') != 200:
            return access_filters
            
        # Extract outlet_id from response for database filtering
        outlet_id = access_filters.get('body', {}).get('outlet_id')
        access_filters = {'outlet_id': outlet_id}
    except Exception as e:
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
    
    return get_complete_menu(event, access_filters)

def get_complete_menu(event, access_filters):
    """Get the complete menu for an outlet"""
    try:
        with get_db_session() as session:
            # Get all active categories for the outlet
            categories = session.query(Category).filter(
                Category.outlet_id == access_filters.get('outlet_id'),
                Category.is_active == True
            ).order_by(Category.display_order).all()
            
            # Build the complete menu structure
            menu = {
                'outlet_id': access_filters.get('outlet_id'),
                'categories': []
            }
            
            for category in categories:
                # Get all active items in this category
                items = session.query(MenuItem).filter(
                    MenuItem.category_id == category.id,
                    MenuItem.is_active == True
                ).all()
                
                category_dict = category.to_dict()
                category_dict['items'] = []
                
                for item in items:
                    # Include variations and addons
                    item_dict = item.to_dict(include_relations=True)
                    
                    # Only add active variations and addons
                    active_variations = [v for v in item.variations if v.is_active]
                    active_addons = [a for a in item.addons if a.is_active]
                    
                    item_dict['variations'] = [v.to_dict(include_relations=False) for v in active_variations]
                    item_dict['addons'] = [a.to_dict(include_relations=False) for a in active_addons]
                    
                    category_dict['items'].append(item_dict)
                
                # Only add the category if it has items
                if category_dict['items']:
                    menu['categories'].append(category_dict)
            
            return create_response(200, {'data': menu})
    except Exception as e:
        print(f"Error getting menu: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
