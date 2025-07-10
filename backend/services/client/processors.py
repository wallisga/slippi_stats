"""
Client Domain Processing Logic

Core business logic operations for client management.
Handles client registration, API keys, updates, and data access.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from backend.config import get_config
from backend.db import connection, manager
from .schemas import ClientRegistrationData, ApiKeyData, ClientInfo, ClientStatus

# Configuration
config = get_config()
logger = config.init_logging()

# SQL Manager for database operations
sql_mgr = manager.SQLManager()

def execute_query(category, query_name, params=(), fetch_one=False, fetch_many=None):
    """Helper function to execute SQL queries using the new db layer."""
    try:
        query = sql_mgr.get_query(category, query_name)
        
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_many:
                return cursor.fetchmany(fetch_many)
            elif query_name.startswith('select') or query_name.startswith('get'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
                
    except Exception as e:
        logger.error(f"Database query error ({category}.{query_name}): {str(e)}")
        raise

# ============================================================================
# Client Registration Processing
# ============================================================================

def process_client_registration_data(registration_data: ClientRegistrationData) -> Dict[str, Any]:
    """
    Process client registration data (create new or update existing).
    
    Args:
        registration_data: Validated client registration data
    
    Returns:
        dict: Processing result with client information
    """
    client_id = registration_data.client_id
    
    try:
        # Check if client already exists
        existing_client = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        if existing_client:
            # Update existing client
            result = _update_existing_client(registration_data, existing_client)
            result['is_new_client'] = False
            logger.info(f"Updated existing client: {client_id}")
        else:
            # Create new client
            result = _create_new_client(registration_data)
            result['is_new_client'] = True
            logger.info(f"Created new client: {client_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing client registration for {client_id}: {str(e)}")
        raise

def _create_new_client(registration_data: ClientRegistrationData) -> Dict[str, Any]:
    """Create a new client record."""
    try:
        # Insert new client record
        execute_query('clients', 'insert_client', (
            registration_data.client_id,
            registration_data.hostname,
            registration_data.platform.value,
            registration_data.version,
            registration_data.registration_date,
            datetime.now().isoformat()  # last_active
        ))
        
        return {
            'client_id': registration_data.client_id,
            'status': 'created',
            'registration_date': registration_data.registration_date
        }
        
    except Exception as e:
        logger.error(f"Error creating client {registration_data.client_id}: {str(e)}")
        raise

def _update_existing_client(registration_data: ClientRegistrationData, 
                          existing_client: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing client record."""
    try:
        # Update client with new information using existing SQL file
        execute_query('clients', 'update_info', (
            registration_data.hostname,
            registration_data.platform.value,
            registration_data.version,
            datetime.now().isoformat(),  # last_active
            registration_data.client_id
        ))
        
        return {
            'client_id': registration_data.client_id,
            'status': 'updated',
            'previous_version': existing_client.get('version'),
            'new_version': registration_data.version
        }
        
    except Exception as e:
        logger.error(f"Error updating client {registration_data.client_id}: {str(e)}")
        raise

# ============================================================================
# API Key Processing
# ============================================================================

def process_api_key_generation(client_id: str, force_new: bool = False) -> Dict[str, Any]:
    """
    Generate or retrieve API key for client.
    
    Args:
        client_id: Client identifier
        force_new: Force generation of new API key
    
    Returns:
        dict: API key information
    """
    try:
        # Check for existing valid API key
        if not force_new:
            existing_key = _get_existing_valid_api_key(client_id)
            if existing_key:
                logger.info(f"Returning existing API key for client: {client_id}")
                return {
                    'api_key': existing_key.api_key,
                    'expires_at': existing_key.expires_at,
                    'created_at': existing_key.created_at,
                    'is_new': False
                }
        
        # Generate new API key
        new_api_key = ApiKeyData.create_new(client_id, config.TOKEN_EXPIRY_DAYS)
        
        # Store in database
        _store_api_key(new_api_key, force_new)
        
        logger.info(f"Generated new API key for client: {client_id}")
        return {
            'api_key': new_api_key.api_key,
            'expires_at': new_api_key.expires_at,
            'created_at': new_api_key.created_at,
            'is_new': True
        }
        
    except Exception as e:
        logger.error(f"Error generating API key for {client_id}: {str(e)}")
        raise

def _get_existing_valid_api_key(client_id: str) -> Optional[ApiKeyData]:
    """Get existing valid API key for client."""
    try:
        api_key_record = execute_query('api_keys', 'select_by_client', (client_id,), fetch_one=True)
        
        if not api_key_record:
            return None
        
        api_key = ApiKeyData(
            client_id=api_key_record['client_id'],
            api_key=api_key_record['api_key'],
            created_at=api_key_record.get('created_at', datetime.now().isoformat()),
            expires_at=api_key_record.get('expires_at'),
            is_active=api_key_record.get('is_active', True),
            last_used_at=api_key_record.get('last_used_at'),
            usage_count=api_key_record.get('usage_count', 0)
        )
        
        if api_key.is_valid():
            return api_key
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking existing API key for {client_id}: {str(e)}")
        return None

def _store_api_key(api_key_data: ApiKeyData, is_update: bool = False) -> None:
    """Store API key in database."""
    try:
        if is_update:
            # Update existing API key
            execute_query('api_keys', 'update_key', (
                api_key_data.api_key,
                api_key_data.created_at,
                api_key_data.expires_at,
                api_key_data.client_id
            ))
        else:
            # Insert new API key
            execute_query('api_keys', 'insert_key', (
                api_key_data.client_id,
                api_key_data.api_key,
                api_key_data.created_at,
                api_key_data.expires_at
            ))
            
    except Exception as e:
        logger.error(f"Error storing API key for {api_key_data.client_id}: {str(e)}")
        raise

# ============================================================================
# Client Information and Validation
# ============================================================================

def validate_existing_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Validate an existing API key and return client information.
    
    Args:
        api_key: API key to validate
    
    Returns:
        dict: Client information if valid, None if invalid
    """
    try:
        # Get API key record
        api_key_record = execute_query('api_keys', 'select_by_key', (api_key,), fetch_one=True)
        
        if not api_key_record:
            return None
        
        # Create API key object for validation
        api_key_obj = ApiKeyData(
            client_id=api_key_record['client_id'],
            api_key=api_key_record['api_key'],
            created_at=api_key_record.get('created_at', datetime.now().isoformat()),
            expires_at=api_key_record.get('expires_at'),
            is_active=api_key_record.get('is_active', True),
            last_used_at=api_key_record.get('last_used_at'),
            usage_count=api_key_record.get('usage_count', 0)
        )
        
        # Check if API key is valid
        if not api_key_obj.is_valid():
            return None
        
        # Update last used time
        _update_api_key_usage(api_key_obj)
        
        # Return client information
        return {
            'client_id': api_key_obj.client_id,
            'api_key': api_key_obj.api_key,
            'expires_at': api_key_obj.expires_at,
            'last_used_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None

def _update_api_key_usage(api_key_data: ApiKeyData) -> None:
    """Update API key usage statistics."""
    try:
        # Note: We don't have update_usage.sql yet, and usage tracking is non-critical
        # For now, we'll skip this feature to avoid inline SQL
        # TODO: Create api_keys/update_usage.sql if usage tracking is needed
        logger.debug(f"API key usage tracking skipped for {api_key_data.client_id} (no SQL file)")
        
    except Exception as e:
        logger.warning(f"Failed to update API key usage for {api_key_data.client_id}: {str(e)}")
        # Don't raise - usage tracking is non-critical

def get_client_information(client_id: str) -> Optional[Dict[str, Any]]:
    """
    Get complete client information.
    
    Args:
        client_id: Client identifier
    
    Returns:
        dict: Complete client information or None if not found
    """
    try:
        # Get client record
        client_record = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        if not client_record:
            return None
        
        # Get API key record
        api_key_record = execute_query('api_keys', 'select_by_client', (client_id,), fetch_one=True)
        
        # Create client info object
        client_info = ClientInfo.from_database_records(client_record, api_key_record)
        
        return {
            'client_id': client_info.registration.client_id,
            'hostname': client_info.registration.hostname,
            'platform': client_info.registration.platform.value,
            'version': client_info.registration.version,
            'registration_date': client_info.registration.registration_date,
            'last_activity': client_info.last_activity,
            'status': client_info.status.value,
            'has_valid_api_key': client_info.api_key and client_info.api_key.is_valid(),
            'total_uploads': client_info.total_uploads,
            'total_games_uploaded': client_info.total_games_uploaded,
            'total_files_uploaded': client_info.total_files_uploaded
        }
        
    except Exception as e:
        logger.error(f"Error getting client information for {client_id}: {str(e)}")
        return None

# ============================================================================
# Client Updates
# ============================================================================

def process_client_update(client_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process client information update.
    
    Args:
        client_id: Client identifier
        update_data: Data to update
    
    Returns:
        dict: Update result
    """
    try:
        # Check if client exists
        existing_client = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        if not existing_client:
            raise ValueError(f"Client {client_id} not found")
        
        # Use the existing update_info.sql file
        # Build parameters in the order expected by the SQL file
        updated_fields = []
        
        hostname = update_data.get('hostname', existing_client['hostname'])
        platform = update_data.get('platform', existing_client['platform'])
        version = update_data.get('version', existing_client['version'])
        
        if 'hostname' in update_data:
            updated_fields.append('hostname')
        if 'platform' in update_data:
            updated_fields.append('platform')
        if 'version' in update_data:
            updated_fields.append('version')
        
        # Execute update using existing SQL file
        execute_query('clients', 'update_info', (
            hostname,
            platform,
            version,
            datetime.now().isoformat(),  # last_active
            client_id  # WHERE clause
        ))
        
        logger.info(f"Updated client {client_id}, fields: {updated_fields}")
        
        return {
            'updated_fields': updated_fields,
            'update_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {str(e)}")
        raise

# ============================================================================
# Client Activity Tracking
# ============================================================================

def update_client_activity(client_id: str, activity_type: str = 'general') -> None:
    """
    Update client last activity timestamp.
    
    Args:
        client_id: Client identifier
        activity_type: Type of activity (for future analytics)
    """
    try:
        execute_query('clients', 'update_last_active', (
            datetime.now().isoformat(),
            client_id
        ))
        
        logger.debug(f"Updated activity for client {client_id}: {activity_type}")
        
    except Exception as e:
        logger.warning(f"Failed to update activity for client {client_id}: {str(e)}")
        # Don't raise - activity tracking is non-critical

def get_client_statistics() -> Dict[str, Any]:
    """Get overall client statistics."""
    try:
        # Use existing queries or provide basic stats
        # For now, return basic stats without complex queries
        # TODO: Add dedicated stats SQL files if detailed analytics are needed
        
        all_clients = execute_query('clients', 'select_all', ())
        total_clients = len(all_clients) if all_clients else 0
        
        return {
            'total_clients': total_clients,
            'active_clients_30_days': 0,  # TODO: Add SQL file for this
            'new_clients_this_month': 0,  # TODO: Add SQL file for this
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting client statistics: {str(e)}")
        return {
            'total_clients': 0,
            'active_clients_30_days': 0,
            'new_clients_this_month': 0,
            'timestamp': datetime.now().isoformat()
        }