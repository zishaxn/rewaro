import json
from sqlalchemy import exc
from models import Addon
from db import get_db_session, get_access_filters, paginate_query
from utils import create_response, parse_body, get_path_parameter, get_pagination_params

def addonsHandler(event, context):
    """Handler for /addons endpoints"""
    http_method = event.get('httpMethod')
    
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
    
    # Route based on HTTP method
    if http_method == 'GET':
        # Check if it's a get by ID request
        addon_id = get_path_parameter(event, 'id')
        if addon_id:
            return get_addon(addon_id, access_filters)
        else:
            return list_addons(event, access_filters)
    elif http_method == 'POST':
        return create_addon(event, access_filters)
    elif http_method == 'PUT':
        addon_id = get_path_parameter(event, 'id')
        return update_addon(addon_id, event, access_filters)
    elif http_method == 'DELETE':
        addon_id = get_path_parameter(event, 'id')
        return delete_addon(addon_id, access_filters)
    else:
        return create_response(405, {'error': 'Method Not Allowed'})

def list_addons(event, access_filters):
    """List all addons with pagination"""
    page, limit = get_pagination_params(event)
    
    try:
        with get_db_session() as session:
            query = session.query(Addon)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Addon, key) == value)
            
            # Apply pagination
            query = paginate_query(query, page, limit)
            
            # Get results
            addons = query.all()
            result = [addon.to_dict() for addon in addons]
            
            return create_response(200, {
                'data': result,
                'page': page,
                'limit': limit,
                'count': len(result)
            })
    except Exception as e:
        print(f"Error listing addons: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def get_addon(addon_id, access_filters):
    """Get addon by ID"""
    try:
        with get_db_session() as session:
            query = session.query(Addon).filter(Addon.id == addon_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Addon, key) == value)
            
            addon = query.first()
            
            if not addon:
                return create_response(404, {'error': 'Not Found', 'message': 'Addon not found'})
            
            return create_response(200, {'data': addon.to_dict()})
    except Exception as e:
        print(f"Error getting addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def create_addon(event, access_filters):
    """Create a new addon"""
    body = parse_body(event)
    
    # Validate required fields
    if not body.get('name'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Name is required'})
    if not body.get('price') and body.get('price') != 0:
        return create_response(400, {'error': 'Bad Request', 'message': 'Price is required'})
    
    # Apply access filters to the body
    body.update(access_filters)
    
    try:
        with get_db_session() as session:
            addon = Addon(**body)
            session.add(addon)
            session.flush()  # Flush to get the ID
            
            # Convert to dictionary for response
            result = addon.to_dict()
            
            return create_response(201, {'data': result, 'message': 'Addon created successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error creating addon: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Addon with this name already exists'})
    except Exception as e:
        print(f"Error creating addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def update_addon(addon_id, event, access_filters):
    """Update an existing addon"""
    if not addon_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Addon ID is required'})
    
    body = parse_body(event)
    
    try:
        with get_db_session() as session:
            # Get existing addon
            query = session.query(Addon).filter(Addon.id == addon_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Addon, key) == value)
            
            addon = query.first()
            
            if not addon:
                return create_response(404, {'error': 'Not Found', 'message': 'Addon not found'})
            
            # Update fields
            for key, value in body.items():
                if hasattr(addon, key):
                    setattr(addon, key, value)
            
            # Convert to dictionary for response
            result = addon.to_dict()
            
            return create_response(200, {'data': result, 'message': 'Addon updated successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error updating addon: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Addon with this name already exists'})
    except Exception as e:
        print(f"Error updating addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def delete_addon(addon_id, access_filters):
    """Delete an addon"""
    if not addon_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Addon ID is required'})
    
    try:
        with get_db_session() as session:
            # Get existing addon
            query = session.query(Addon).filter(Addon.id == addon_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Addon, key) == value)
            
            addon = query.first()
            
            if not addon:
                return create_response(404, {'error': 'Not Found', 'message': 'Addon not found'})
            
            # Check if it's being used by any menu items
            if addon.items and len(addon.items) > 0:
                return create_response(400, {
                    'error': 'Bad Request', 
                    'message': 'Cannot delete addon as it is attached to menu items.'
                })
            
            # Delete addon
            session.delete(addon)
            
            return create_response(200, {'message': 'Addon deleted successfully'})
    except Exception as e:
        print(f"Error deleting addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
