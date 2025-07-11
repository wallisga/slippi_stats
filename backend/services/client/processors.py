"""
Client Domain Processing Logic

Core business logic operations for client management.
Handles client registration, API keys, updates, and data access.

FIXED: Updated to use standardized backend.db layer instead of direct SQL manager imports
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from backend.config import get_config
from backend.db import execute_query  # FIXED: Use standardized db layer
from .schemas import ClientRegistrationData, ApiKeyData, ClientInfo, ClientStatus

# Configuration
config = get_config()
logger = config.init_logging()

# REMOVED: Direct SQL manager import - now using backend.db.execute_query()

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
        # Check if client already exists - FIXED: Use standardized execute_query
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
        # FIXED: Use standardized execute_query for insert operations
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
        # FIXED: Use standardized execute_query for update operations
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
        dict: API key data or error information
    """
    try:
        # Check for existing valid API key if not forcing new
        if not force_new:
            # FIXED: Use standardized execute_query
            existing_api_key = execute_query('api_keys', 'select_by_client', (client_id,), fetch_one=True)
            
            if existing_api_key:
                api_key_data = ApiKeyData.from_database_record(existing_api_key)
                if api_key_data.is_valid():
                    logger.info(f"Using existing valid API key for client {client_id}")
                    return {
                        'api_key': api_key_data.api_key,
                        'expires_at': api_key_data.expires_at,
                        'client_id': client_id,
                        'status': 'existing'
                    }
        
        # Generate new API key
        new_api_key_data = _generate_new_api_key(client_id)
        
        # Store API key in database
        # FIXED: Use standardized execute_query
        execute_query('api_keys', 'insert_key', (
            new_api_key_data.client_id,
            new_api_key_data.api_key,
            new_api_key_data.created_at,
            new_api_key_data.expires_at
        ))
        
        logger.info(f"Generated new API key for client {client_id}")
        
        return {
            'api_key': new_api_key_data.api_key,
            'expires_at': new_api_key_data.expires_at,
            'client_id': client_id,
            'status': 'new'
        }
        
    except Exception as e:
        logger.error(f"Error processing API key generation for {client_id}: {str(e)}")
        raise

def _generate_new_api_key(client_id: str) -> ApiKeyData:
    """Generate new API key data."""
    import uuid
    from datetime import timedelta
    
    api_key = f"slippi_api_{uuid.uuid4().hex}"
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=config.TOKEN_EXPIRY_DAYS)).isoformat()
    
    return ApiKeyData(
        client_id=client_id,
        api_key=api_key,
        created_at=created_at,
        expires_at=expires_at
    )

def validate_existing_api_key(api_key: str) -> Optional[ApiKeyData]:
    """
    Validate an existing API key.
    
    Args:
        api_key: API key to validate
    
    Returns:
        ApiKeyData if valid, None otherwise
    """
    try:
        # FIXED: Use standardized execute_query
        api_key_record = execute_query('api_keys', 'select_by_key', (api_key,), fetch_one=True)
        
        if not api_key_record:
            return None
        
        api_key_data = ApiKeyData.from_database_record(api_key_record)
        
        if not api_key_data.is_valid():
            logger.warning(f"Invalid or expired API key used: {api_key[:10]}...")
            return None
        
        # Update usage tracking (non-critical)
        try:
            # Note: We don't have update_usage.sql yet, and usage tracking is non-critical
            # For now, we'll skip this feature to avoid inline SQL
            # TODO: Create api_keys/update_usage.sql if usage tracking is needed
            logger.debug(f"API key usage tracking skipped for {api_key_data.client_id} (no SQL file)")
            
        except Exception as e:
            logger.warning(f"Failed to update API key usage for {api_key_data.client_id}: {str(e)}")
            # Don't raise - usage tracking is non-critical
        
        return api_key_data
        
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None

def get_client_information(client_id: str) -> Optional[Dict[str, Any]]:
    """
    Get complete client information.
    
    Args:
        client_id: Client identifier
    
    Returns:
        dict: Complete client information or None if not found
    """
    try:
        # FIXED: Use standardized execute_query
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
        
        # FIXED: Use standardized execute_query
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
        # FIXED: Use standardized execute_query
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
        # FIXED: Use standardized execute_query
        total_clients = execute_query('clients', 'count_all', fetch_one=True)
        active_clients = execute_query('clients', 'count_active', fetch_one=True)
        
        return {
            'total_clients': total_clients.get('count', 0) if total_clients else 0,
            'active_clients': active_clients.get('count', 0) if active_clients else 0,
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting client statistics: {str(e)}")
        return {
            'total_clients': 0,
            'active_clients': 0,
            'last_updated': datetime.now().isoformat(),
            'error': str(e)
        }