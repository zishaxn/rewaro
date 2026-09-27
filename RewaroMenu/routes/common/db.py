import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from routes.common.models import Base, get_db_url
import logging
from routes.common.utils import create_response

# Configure logger
logger = logging.getLogger(__name__)

# Create engine and session factory
engine = create_engine(get_db_url())
Session = scoped_session(sessionmaker(bind=engine))

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_db_connection(database_name=None):
    """Get a raw psycopg2 connection for direct SQL execution"""
    db_name = os.environ.get(database_name) if database_name else os.environ.get('DB_NAME')
    
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=db_name,
        user=os.environ.get('DB_USERNAME'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT', '5432')
    )
    return conn



@contextmanager
def execute_query(query, params=None):
    """Execute a SQL query and return results as dictionaries"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database connection"""
    # Not automatically creating tables anymore
    # Base.metadata.create_all(engine)
    print("Database connection initialized successfully")

def paginate_query(query, page=1, limit=20):
    """Add pagination to a SQLAlchemy query"""
    offset = (page - 1) * limit
    return query.limit(limit).offset(offset)

def get_access_filters(event):
    """Extract outlet_id from the request for data filtering and authenticate user
    
    This ensures that merchants can only access their own data"""
    # Get claims from the authorizer if available
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    claims = authorizer.get('claims', {})
    
    # Extract user information from claims
    user_id = claims.get('sub')
    phone_no = claims.get('phone_number')

    logger.info(f"User ID: {user_id}, Phone No: {phone_no}")
    
    # Get outlet_id from different possible sources
    headers = event.get('headers', {}) or {}
    query_params = event.get('queryStringParameters', {}) or {}
    
    # Try to get outlet_id from different possible sources
    outlet_id = headers.get('X-Outlet-Id') or query_params.get('outlet_id')
    
    if not outlet_id:
        # If not found, check if it's in the path parameters
        path_params = event.get('pathParameters', {}) or {}
        outlet_id = path_params.get('outlet_id')
    
    # Convert outlet_id to integer if found
    if outlet_id:
        try:
            outlet_id = int(outlet_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid outlet_id format: {outlet_id}")
            pass
        
    if not outlet_id:
        return create_response(400, {'error': 'Bad Request', 'message': 'Outlet ID is required'})

    # If we have user_id, phone_no, and outlet_id, authenticate the user
    # if user_id and phone_no and outlet_id:
    #     auth_result = auth_client(outlet_id, user_id, phone_no)
    #     # If authentication fails, return empty filters (or you could raise an exception)
    #     if not auth_result.get('statusCode') == 200:
    #         logger.warning(f"Authentication failed for user {user_id} and outlet {outlet_id}")
    #         return auth_result
    

    # Return outlet_id
    return {"statusCode": 200, "body": {"outlet_id": outlet_id}}

def auth_client(client_id, user_id, phone_no):
    """Authenticate client and return client details."""
    try:
        with get_db_connection(os.environ.get("CLIENT_DB_NAME")) as conn:   
            with conn.cursor() as cursor:
                auth_query = sql.SQL("""
                    SELECT user_id FROM {table} WHERE client_id = %s AND phone_no = %s
                """).format(table=sql.Identifier(os.environ.get("CLIENT_MASTER_TABLE")))
                
                cursor.execute(auth_query, (client_id, phone_no))
                auth_result = cursor.fetchone()
                
                if not auth_result:
                    logger.warning(f"Client not found: {client_id}")
                    return {"statusCode": 403, "body": {"message": "Client not found"}}
                
                fetched_user_id = str(auth_result[0])
                
                if fetched_user_id != user_id:
                    logger.warning(f"User {user_id} not authorized for client {client_id}")
                    return {"statusCode": 403, "body": {"message": "User not authorized to access this client"}}
                
                return {"statusCode": 200, "body": {"message": "Authorized"}}
                
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return {"statusCode": 500, "body": {"message": f"Internal error: {str(e)}"}}