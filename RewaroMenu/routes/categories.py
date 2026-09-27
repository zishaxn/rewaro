from sqlalchemy import exc
from routes.common.models import Category
from routes.common.db import get_db_session, get_access_filters, paginate_query
from routes.common.utils import create_response, parse_body, get_path_parameter, get_pagination_params

def categoriesHandler(event, context):
    """Handler for /categories endpoints"""
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

    print("EVENT AAYA HAI BHAI")

    # Route based on HTTP method
    if http_method == 'GET':
        # Check if it's a get by ID request
        category_id = get_path_parameter(event, 'id')
        if category_id:
            return get_category(category_id, access_filters)
        else:
            return list_categories(event, access_filters)
    elif http_method == 'POST':
        return create_category(event, access_filters)
    elif http_method == 'PUT':
        category_id = get_path_parameter(event, 'id')
        return update_category(category_id, event, access_filters)
    elif http_method == 'DELETE':
        category_id = get_path_parameter(event, 'id')
        return delete_category(category_id, access_filters)
    else:
        return create_response(405, {'error': 'Method Not Allowed'})

def list_categories(event, access_filters):
    """List all categories with pagination"""
    page, limit = get_pagination_params(event)
    
    try:
        with get_db_session() as session:
            query = session.query(Category)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Category, key) == value)
            
            # Apply pagination
            query = paginate_query(query, page, limit)
            
            # Get results
            categories = query.all()
            result = [category.to_dict() for category in categories]
            
            return create_response(200, {
                'data': result,
                'page': page,
                'limit': limit,
                'count': len(result)
            })
    except Exception as e:
        print(f"Error listing categories: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def get_category(category_id, access_filters):
    """Get category by ID"""
    try:
        with get_db_session() as session:
            query = session.query(Category).filter(Category.id == category_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Category, key) == value)
            
            category = query.first()
            
            if not category:
                return create_response(404, {'error': 'Not Found', 'message': 'Category not found'})
            
            return create_response(200, {'data': category.to_dict()})
    except Exception as e:
        print(f"Error getting category: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def create_category(event, access_filters):
    """Create a new category"""
    body = parse_body(event)
    
    # Validate required fields
    if not body.get('name'):
        return create_response(400, {'error': 'Bad Request', 'message': 'Name is required'})
    
    # Apply access filters to the body
    body.update(access_filters)
    
    try:
        with get_db_session() as session:
            category = Category(**body)
            session.add(category)
            session.flush()  # Flush to get the ID
            
            # Convert to dictionary for response
            result = category.to_dict()
            
            return create_response(201, {'data': result, 'message': 'Category created successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error creating category: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Category with this name already exists'})
    except Exception as e:
        print(f"Error creating category: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def update_category(category_id, event, access_filters):
    """Update an existing category"""
    if not category_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Category ID is required'})
    
    body = parse_body(event)
    
    try:
        with get_db_session() as session:
            # Get existing category
            query = session.query(Category).filter(Category.id == category_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Category, key) == value)
            
            category = query.first()
            
            if not category:
                return create_response(404, {'error': 'Not Found', 'message': 'Category not found'})
            
            # Update fields
            for key, value in body.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            # Convert to dictionary for response
            result = category.to_dict()
            
            return create_response(200, {'data': result, 'message': 'Category updated successfully'})
    except exc.IntegrityError as e:
        print(f"Integrity error updating category: {str(e)}")
        return create_response(400, {'error': 'Bad Request', 'message': 'Category with this name already exists'})
    except Exception as e:
        print(f"Error updating category: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})

def delete_category(category_id, access_filters):
    """Delete a category"""
    if not category_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Category ID is required'})
    
    try:
        with get_db_session() as session:
            # Get existing category
            query = session.query(Category).filter(Category.id == category_id)
            
            # Apply access filters
            for key, value in access_filters.items():
                query = query.filter(getattr(Category, key) == value)
            
            category = query.first()
            
            if not category:
                return create_response(404, {'error': 'Not Found', 'message': 'Category not found'})
            
            # Delete category
            session.delete(category)
            
            return create_response(200, {'message': 'Category deleted successfully'})
    except Exception as e:
        print(f"Error deleting category: {str(e)}")
        return create_response(500, {'error': 'Internal Server Error', 'message': str(e)})
