import json
from sqlalchemy import exc
from models import MenuItem, Category, Variation, Addon
from db import get_db_session, get_access_filters, paginate_query
from utils import create_response, parse_body, get_path_parameter, get_pagination_params

def itemsHandler(event, context):
    """Handler for /items endpoints"""
    http_method = event.get('httpMethod')
    resource_path = event.get('resource', '')
    
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
    
    # Check if it's a relationship endpoint
    if '/variations/' in resource_path:
        item_id = get_path_parameter(event, 'id')
        variation_id = get_path_parameter(event, 'variation_id')
        
        if http_method == 'POST':
            return attach_variation(item_id, variation_id, access_filters)
        elif http_method == 'DELETE':
            return detach_variation(item_id, variation_id, access_filters)
    
    elif '/addons/' in resource_path:
        item_id = get_path_parameter(event, 'id')
        addon_id = get_path_parameter(event, 'addon_id')
        
        if http_method == 'POST':
            return attach_addon(item_id, addon_id, access_filters)
        elif http_method == 'DELETE':
            return detach_addon(item_id, addon_id, access_filters)
    
    # Standard CRUD operations
    if http_method == 'GET':
        # Check if it's a get by ID request
        item_id = get_path_parameter(event, 'id')
        if item_id:
            return get_item(item_id, access_filters)
        else:
            return list_items(event, access_filters)
    elif http_method == 'POST':
        return create_item(event, access_filters)
    elif http_method == 'PUT':
        item_id = get_path_parameter(event, 'id')
        return update_item(item_id, event, access_filters)
    elif http_method == 'DELETE':
        item_id = get_path_parameter(event, 'id')
        return delete_item(item_id, access_filters)
    else:
        return create_response(405, {'error': 'Method Not Allowed'})

def list_items(event, access_filters):
    """List all menu items with pagination"""
    page, limit = get_pagination_params(event)
    
    try:
        with get_db_session() as session:
            query = session.query(MenuItem)
            
            # Filter by category if specified
            category_id = get_path_parameter(event, 'category_id')
            if category_id:
                query = query.filter(MenuItem.category_id == category_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(MenuItem, key) == value)
            
            # Apply pagination
            query = paginate_query(query, page, limit)
            
            # Get results
            items = query.all()
            result = [item.to_dict() for item in items]
            
            return create_response(200, {
                'data': result,
                'page': page,
                'limit': limit,
                'count': len(result)
            })
    except Exception as e:
        print(f"Error listing menu items: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def get_item(item_id, access_filters):
    """Get menu item by ID"""
    try:
        with get_db_session() as session:
            query = session.query(MenuItem).filter(MenuItem.id == item_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(MenuItem, key) == value)
            
            item = query.first()
            
            if not item:
                return create_response(404, {'error': 'Not Found', 'message': 'Menu item not found'})
            
            return create_response(200, {'data': item.to_dict()})
    except Exception as e:
        print(f"Error getting menu item: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def create_item(event, access_filters):
    """Create a new menu item"""
    body = parse_body(event)
    
    # Validate required fields
    if not body.get('name'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Name is required'})
    if not body.get('price'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Price is required'})
    if not body.get('category_id'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Category ID is required'})
    
    # Apply access filters to the body
    body.update(access_filters)
    
    try:
        with get_db_session() as session:
            # Verify category exists and belongs to this outlet
            category = session.query(Category).filter(
                Category.id == body['category_id'],
                Category.outlet_id == body['outlet_id']
            ).first()
            
            if not category:
                return create_response(400, {'error': 'Bad Request', 'message': 'Invalid category ID'})
            
            # Create menu item
            item = MenuItem(**body)
            session.add(item)
            session.flush()  # Flush to get the ID
            
            # Convert to dictionary for response
            result = item.to_dict()
            
            return create_response(201, {'data': result, 'message': 'Menu item created successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error creating menu item: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Menu item with this name already exists'})
    except Exception as e:
        print(f"Error creating menu item: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def update_item(item_id, event, access_filters):
    """Update an existing menu item"""
    if not item_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID is required'})
    
    body = parse_body(event)
    
    try:
        with get_db_session() as session:
            # Get existing item
            query = session.query(MenuItem).filter(MenuItem.id == item_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(MenuItem, key) == value)
            
            item = query.first()
            
            if not item:
                return create_response(404, {'error': 'Not Found', 'message': 'Menu item not found'})
            
            # If category_id is being updated, verify it exists and belongs to this outlet
            if 'category_id' in body:
                category = session.query(Category).filter(
                    Category.id == body['category_id'],
                    Category.outlet_id == item.outlet_id
                ).first()
                
                if not category:
                    return create_response(400, {'error': 'Bad Request', 'message': 'Invalid category ID'})
            
            # Update fields
            for key, value in body.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            # Convert to dictionary for response
            result = item.to_dict()
            
            return create_response(200, {'data': result, 'message': 'Menu item updated successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error updating menu item: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Menu item with this name already exists'})
    except Exception as e:
        print(f"Error updating menu item: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def delete_item(item_id, access_filters):
    """Delete a menu item"""
    if not item_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID is required'})
    
    try:
        with get_db_session() as session:
            # Get existing item
            query = session.query(MenuItem).filter(MenuItem.id == item_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(MenuItem, key) == value)
            
            item = query.first()
            
            if not item:
                return create_response(404, {'error': 'Not Found', 'message': 'Menu item not found'})
            
            # Delete item
            session.delete(item)
            
            return create_response(200, {'message': 'Menu item deleted successfully'})
    except Exception as e:
        print(f"Error deleting menu item: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def attach_variation(item_id, variation_id, access_filters):
    """Attach a variation to a menu item"""
    if not item_id or not variation_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID and Variation ID are required'})
    
    try:
        with get_db_session() as session:
            # Get item and variation
            item = session.query(MenuItem).filter(
                MenuItem.id == item_id,
                MenuItem.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            variation = session.query(Variation).filter(
                Variation.id == variation_id,
                Variation.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            if not item or not variation:
                return create_response(404, {'error': 'Not Found', 'message': 'Item or variation not found'})
            
            # Check if already attached
            if variation in item.variations:
                return create_response(400, {'error': 'Bad Request', 'message': 'Variation already attached to this item'})
            
            # Attach variation
            item.variations.append(variation)
            
            return create_response(200, {'message': 'Variation attached successfully'})
    except Exception as e:
        print(f"Error attaching variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def detach_variation(item_id, variation_id, access_filters):
    """Detach a variation from a menu item"""
    if not item_id or not variation_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID and Variation ID are required'})
    
    try:
        with get_db_session() as session:
            # Get item and variation
            item = session.query(MenuItem).filter(
                MenuItem.id == item_id,
                MenuItem.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            variation = session.query(Variation).filter(
                Variation.id == variation_id,
                Variation.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            if not item or not variation:
                return create_response(404, {'error': 'Not Found', 'message': 'Item or variation not found'})
            
            # Check if attached
            if variation not in item.variations:
                return create_response(400, {'error': 'Bad Request', 'message': 'Variation not attached to this item'})
            
            # Detach variation
            item.variations.remove(variation)
            
            return create_response(200, {'message': 'Variation detached successfully'})
    except Exception as e:
        print(f"Error detaching variation: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def attach_addon(item_id, addon_id, access_filters):
    """Attach an addon to a menu item"""
    if not item_id or not addon_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID and Addon ID are required'})
    
    try:
        with get_db_session() as session:
            # Get item and addon
            item = session.query(MenuItem).filter(
                MenuItem.id == item_id,
                MenuItem.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            addon = session.query(Addon).filter(
                Addon.id == addon_id,
                Addon.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            if not item or not addon:
                return create_response(404, {'error': 'Not Found', 'message': 'Item or addon not found'})
            
            # Check if already attached
            if addon in item.addons:
                return create_response(400, {'error': 'Bad Request', 'message': 'Addon already attached to this item'})
            
            # Attach addon
            item.addons.append(addon)
            
            return create_response(200, {'message': 'Addon attached successfully'})
    except Exception as e:
        print(f"Error attaching addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def detach_addon(item_id, addon_id, access_filters):
    """Detach an addon from a menu item"""
    if not item_id or not addon_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Item ID and Addon ID are required'})
    
    try:
        with get_db_session() as session:
            # Get item and addon
            item = session.query(MenuItem).filter(
                MenuItem.id == item_id,
                MenuItem.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            addon = session.query(Addon).filter(
                Addon.id == addon_id,
                Addon.outlet_id == access_filters.get('outlet_id')
            ).first()
            
            if not item or not addon:
                return create_response(404, {'error': 'Not Found', 'message': 'Item or addon not found'})
            
            # Check if attached
            if addon not in item.addons:
                return create_response(400, {'error': 'Bad Request', 'message': 'Addon not attached to this item'})
            
            # Detach addon
            item.addons.remove(addon)
            
            return create_response(200, {'message': 'Addon detached successfully'})
    except Exception as e:
        print(f"Error detaching addon: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
