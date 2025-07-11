"""
Client Domain Processing Logic

FIXED: Added database construction methods that belong in processors, not schemas.
All database-related construction logic now properly placed in processors.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import secrets
import hashlib
from backend.config import get_config
from backend.db import execute_query
from .schemas import ClientRegistrationData, ApiKeyData, ClientInfo, ClientStatus, PlatformType

# Configuration
config = get_config()
logger = config.init_logging()

# ============================================================================
# Schema Construction Helpers (Database-Related Logic)
# ============================================================================

def create_client_registration_from_request(raw_data: Dict[str, Any]) -> ClientRegistrationData:
    """
    Create ClientRegistrationData from raw registration request data.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    client_id = raw_data.get('client_id')
    if not client_id:
        import uuid
        client_id = str(uuid.uuid4())
    
    platform_str = raw_data.get('platform', 'unknown')
    platform = PlatformType.from_string(platform_str)
    
    return ClientRegistrationData(
        client_id=client_id,
        hostname=raw_data.get('hostname', 'unknown'),
        platform=platform,
        version=raw_data.get('version', '1.0.0'),
        registration_date=raw_data.get('registration_date', datetime.now().isoformat()),
        user_agent=raw_data.get('user_agent'),
        ip_address=raw_data.get('ip_address'),
        additional_info={k: v for k, v in raw_data.items() 
                       if k not in ['client_id', 'hostname', 'platform', 'version', 'registration_date']}
    )

def create_api_key_from_database_record(record: Dict[str, Any]) -> ApiKeyData:
    """
    Create ApiKeyData from database record.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    if not record:
        raise ValueError("Cannot create ApiKeyData from empty record")
        
    return ApiKeyData(
        client_id=record['client_id'],
        api_key=record['api_key'],
        created_at=record.get('created_at', datetime.now().isoformat()),
        expires_at=record.get('expires_at'),
        is_active=record.get('is_active', True),
        last_used_at=record.get('last_used_at'),
        usage_count=record.get('usage_count', 0)
    )

def create_new_api_key(client_id: str, expiry_days: int = 365) -> ApiKeyData:
    """
    Create a new API key with expiration.
    
    FIXED: This creation logic belongs in processors, not schemas.
    """
    # Generate secure API key
    current_time = datetime.now().isoformat()
    random_bytes = secrets.token_bytes(32)
    api_key = hashlib.sha256(f"{client_id}:{current_time}:{random_bytes.hex()}".encode()).hexdigest()
    
    # Calculate expiration
    expires_at = (datetime.now() + timedelta(days=expiry_days)).isoformat()
    
    return ApiKeyData(
        client_id=client_id,
        api_key=api_key,
        created_at=current_time,
        expires_at=expires_at,
        is_active=True
    )

def create_client_info_from_database_records(client_record: Dict[str, Any], 
                                           api_key_record: Optional[Dict[str, Any]] = None) -> ClientInfo:
    """
    Create ClientInfo from database records.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    # Create registration data
    registration = ClientRegistrationData(
        client_id=client_record['client_id'],
        hostname=client_record.get('hostname', 'unknown'),
        platform=PlatformType.from_string(client_record.get('platform', 'unknown')),
        version=client_record.get('version', '1.0.0'),
        registration_date=client_record.get('registration_date', datetime.now().isoformat())
    )
    
    # Create API key data if available
    api_key = None
    if api_key_record:
        api_key = create_api_key_from_database_record(api_key_record)
    
    return ClientInfo(
        registration=registration,
        api_key=api_key,
        status=ClientStatus(client_record.get('status', 'active')),
        total_uploads=client_record.get('total_uploads', 0),
        total_games_uploaded=client_record.get('total_games_uploaded', 0),
        total_files_uploaded=client_record.get('total_files_uploaded', 0),
        last_activity=client_record.get('last_active')
    )

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
            existing_api_key = execute_query('api_keys', 'select_by_client', (client_id,), fetch_one=True)
            
            if existing_api_key:
                # FIXED: Use processor helper instead of schema method
                api_key_data = create_api_key_from_database_record(existing_api_key)
                if api_key_data.is_valid():
                    logger.info(f"Using existing valid API key for client {client_id}")
                    return {
                        'api_key': api_key_data.api_key,
                        'expires_at': api_key_data.expires_at,
                        'client_id': client_id,
                        'status': 'existing'
                    }
        
        # Generate new API key
        # FIXED: Use processor helper instead of schema method
        new_api_key_data = create_new_api_key(client_id, config.TOKEN_EXPIRY_DAYS)
        
        # Store API key in database
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

def validate_existing_api_key(api_key: str) -> Optional[ApiKeyData]:
    """
    Validate an existing API key.
    
    Args:
        api_key: API key to validate
    
    Returns:
        ApiKeyData if valid, None otherwise
    """
    try:
        api_key_record = execute_query('api_keys', 'select_by_key', (api_key,), fetch_one=True)
        
        if not api_key_record:
            return None
        
        # FIXED: Use processor helper instead of schema method
        api_key_data = create_api_key_from_database_record(api_key_record)
        
        if not api_key_data.is_valid():
            logger.warning(f"Invalid or expired API key used: {api_key[:10]}...")
            return None
        
        # Update usage tracking (non-critical)
        try:
            logger.debug(f"API key usage tracking skipped for {api_key_data.client_id} (no SQL file)")
        except Exception as e:
            logger.warning(f"Failed to update API key usage for {api_key_data.client_id}: {str(e)}")
        
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
        client_record = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        if not client_record:
            return None
        
        # Get API key record
        api_key_record = execute_query('api_keys', 'select_by_client', (client_id,), fetch_one=True)
        
        # FIXED: Use processor helper instead of schema method
        client_info = create_client_info_from_database_records(client_record, api_key_record)
        
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
        existing_client = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        if not existing_client:
            raise ValueError(f"Client {client_id} not found")
        
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
    """Update client last activity timestamp."""
    try:
        execute_query('clients', 'update_last_active', (
            datetime.now().isoformat(),
            client_id
        ))
        
        logger.debug(f"Updated activity for client {client_id}: {activity_type}")
        
    except Exception as e:
        logger.warning(f"Failed to update activity for client {client_id}: {str(e)}")

def get_client_statistics() -> Dict[str, Any]:
    """Get overall client statistics."""
    try:
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