import json
import decimal
from datetime import datetime

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types by converting them to floats"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code, body=None):
    """Create a standardized API response"""
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # CORS support
            'Access-Control-Allow-Credentials': True
        }
    }
    
    if body is not None:
        response['body'] = json.dumps(body, cls=DecimalEncoder)
    
    return response

def parse_body(event):
    """Parse JSON body from event"""
    try:
        body = event.get('body')
        if body:
            return json.loads(body)
        return {}
    except Exception as e:
        print(f"Error parsing request body: {str(e)}")
        return {}

def get_path_parameter(event, param_name):
    """Safely extract a path parameter"""
    path_parameters = event.get('pathParameters', {}) or {}
    return path_parameters.get(param_name)

def get_query_parameter(event, param_name):
    """Safely extract a query parameter"""
    query_parameters = event.get('queryStringParameters', {}) or {}
    return query_parameters.get(param_name)

def get_pagination_params(event):
    """Extract pagination parameters from request"""
    query_params = event.get('queryStringParameters', {}) or {}
    
    # Get page and limit with defaults
    try:
        page = int(query_params.get('page', '1'))
        limit = int(query_params.get('limit', '20'))
        
        # Validate values
        page = max(1, page)  # Minimum page is 1
        limit = min(max(1, limit), 100)  # Limit between 1 and 100
        
        return page, limit
    except (ValueError, TypeError):
        return 1, 20  # Default values
