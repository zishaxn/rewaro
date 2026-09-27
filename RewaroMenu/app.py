import json
import traceback
import logging
from routes import categoriesHandler, itemsHandler, variationsHandler, addonsHandler, menuHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map API resource paths to handler functions
ROUTE_MAP = {
    '/categories': categoriesHandler,
    '/items': itemsHandler,
    '/variations': variationsHandler,
    '/addons': addonsHandler,
    '/menu': menuHandler,
}

def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        # Print event for debugging
        logger.info(f"Event received: {json.dumps(event)}")
        
        # Extract path and HTTP method
        resource_path = event.get('resource', '')
        
        # Route to appropriate handler
        if resource_path in ROUTE_MAP:
            return ROUTE_MAP[resource_path](event, context)
        
        # If path not found, check if it's a nested path
        for base_path, handler in ROUTE_MAP.items():
            if resource_path.startswith(base_path + '/'):
                return handler(event, context)
        
        # Path not found
        return {
            'statusCode': 404,
            'body': json.dumps({
                'error': 'Not Found',
                'message': f'Resource {resource_path} not found'
            })
        }
        
    except Exception as e:
        # Log the full exception for debugging
        logger.error(f"Error processing request: {str(e)}")
        traceback.print_exc()
        
        # Return a 500 error
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }
