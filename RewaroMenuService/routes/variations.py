import json
from sqlalchemy import exc
from models import Variation
from db import get_db_session, get_access_filters, paginate_query
from utils import create_response, parse_body, get_path_parameter, get_pagination_params

def variationsHandler(event, context):
    """Handler for /variations endpoints"""
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
        variation_id = get_path_parameter(event, 'id')
        if variation_id:
            return get_variation(variation_id, access_filters)
        else:
            return list_variations(event, access_filters)
    elif http_method == 'POST':
        return create_variation(event, access_filters)
    elif http_method == 'PUT':
        variation_id = get_path_parameter(event, 'id')
        return update_variation(variation_id, event, access_filters)
    elif http_method == 'DELETE':
        variation_id = get_path_parameter(event, 'id')
        return delete_variation(variation_id, access_filters)
    else:
        return create_response(405, {'error': 'Method Not Allowed'})

def list_variations(event, access_filters):
    """List all variations with pagination"""
    page, limit = get_pagination_params(event)
    
    try:
        with get_db_session() as session:
            query = session.query(Variation)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Variation, key) == value)
            
            # Apply pagination
            query = paginate_query(query, page, limit)
            
            # Get results
            variations = query.all()
            result = [variation.to_dict() for variation in variations]
            
            return create_response(200, {
                'data': result,
                'page': page,
                'limit': limit,
                'count': len(result)
            })
    except Exception as e:
        print(f"Error listing variations: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def get_variation(variation_id, access_filters):
    """Get variation by ID"""
    try:
        with get_db_session() as session:
            query = session.query(Variation).filter(Variation.id == variation_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Variation, key) == value)
            
            variation = query.first()
            
            if not variation:
                return create_response(404, {'error': 'Not Found', 'message': 'Variation not found'})
            
            return create_response(200, {'data': variation.to_dict()})
    except Exception as e:
        print(f"Error getting variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def create_variation(event, access_filters):
    """Create a new variation"""
    body = parse_body(event)
    
    # Validate required fields
    if not body.get('name'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Name is required'})
    
    # Ensure price_adjustment has a default if not specified
    if 'price_adjustment' not in body:
        body['price_adjustment'] = 0.0
    
    # Apply access filters to the body
    body.update(access_filters)
    
    try:
        with get_db_session() as session:
            variation = Variation(**body)
            session.add(variation)
            session.flush()  # Flush to get the ID
            
            # Convert to dictionary for response
            result = variation.to_dict()
            
            return create_response(201, {'data': result, 'message': 'Variation created successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error creating variation: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Variation with this name already exists'})
    except Exception as e:
        print(f"Error creating variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def update_variation(variation_id, event, access_filters):
    """Update an existing variation"""
    if not variation_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Variation ID is required'})
    
    body = parse_body(event)
    
    try:
        with get_db_session() as session:
            # Get existing variation
            query = session.query(Variation).filter(Variation.id == variation_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Variation, key) == value)
            
            variation = query.first()
            
            if not variation:
                return create_response(404, {'error': 'Not Found', 'message': 'Variation not found'})
            
            # Update fields
            for key, value in body.items():
                if hasattr(variation, key):
                    setattr(variation, key, value)
            
            # Convert to dictionary for response
            result = variation.to_dict()
            
            return create_response(200, {'data': result, 'message': 'Variation updated successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error updating variation: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Variation with this name already exists'})
    except Exception as e:
        print(f"Error updating variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def delete_variation(variation_id, access_filters):
    """Delete a variation"""
    if not variation_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Variation ID is required'})
    
    try:
        with get_db_session() as session:
            # Get existing variation
            query = session.query(Variation).filter(Variation.id == variation_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Variation, key) == value)
            
            variation = query.first()
            
            if not variation:
                return create_response(404, {'error': 'Not Found', 'message': 'Variation not found'})
            
            # Check if it's being used by any menu items
            if variation.items and len(variation.items) > 0:
                return create_response(400, {
                    'error': 'Bad Request', 
                    'message': 'Cannot delete variation as it is attached to menu items.'
                })
            
            # Delete variation
            session.delete(variation)
            
            return create_response(200, {'message': 'Variation deleted successfully'})
    except Exception as e:
        print(f"Error deleting variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
