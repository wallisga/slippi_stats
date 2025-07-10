"""
Client Service Orchestrators

Main entry points for client business logic following the orchestrator pattern.
"""

import logging
from datetime import datetime
from backend.config import get_config
from .validation import validate_client_registration, validate_client_update_data, ClientValidationError, ApiKeyError
from .schemas import ClientRegistrationResponse, ApiKeyData, ClientInfo
from .processors import (
    process_client_registration_data,
    process_api_key_generation,
    process_client_update,
    get_client_information,
    validate_existing_api_key
)

# Configuration
config = get_config()
logger = config.init_logging()

# ============================================================================
# Main Orchestrator Functions
# ============================================================================

def register_client(raw_registration_data, registration_key=None):
    """
    Register a new client or update existing client information.
    
    Args:
        raw_registration_data (dict): Client registration data
        registration_key (str, optional): Registration key for validation
    
    Returns:
        dict: Standardized response with success/error status and API key
    """
    try:
        # Step 1: Validate and standardize registration data
        registration_data = validate_client_registration(raw_registration_data, registration_key)
        
        # Step 2: Process client registration (create/update)
        client_result = process_client_registration_data(registration_data)
        
        # Step 3: Generate or retrieve API key
        api_key_result = process_api_key_generation(registration_data.client_id)
        
        # Step 4: Create success response
        return _create_registration_success_response(
            registration_data.client_id,
            api_key_result,
            client_result.get('is_new_client', False)
        )
        
    except ClientValidationError as e:
        logger.warning(f"Client registration validation failed: {str(e)}")
        return _create_registration_error_response('validation_error', str(e))
    except ApiKeyError as e:
        logger.error(f"API key generation failed: {str(e)}")
        return _create_registration_error_response('api_key_error', str(e))
    except Exception as e:
        logger.error(f"Unexpected error in client registration: {str(e)}")
        return _create_registration_error_response('processing_error', 'Registration failed')

def authenticate_client(api_key):
    """
    Authenticate a client using their API key.
    
    Args:
        api_key (str): API key to validate
    
    Returns:
        dict: Client information if valid, None if invalid
    """
    try:
        # Step 1: Validate API key format
        if not api_key:
            return None
        
        # Step 2: Check API key in database
        client_info = validate_existing_api_key(api_key)
        
        # Step 3: Return client information
        return client_info
        
    except Exception as e:
        logger.error(f"Error authenticating client: {str(e)}")
        return None

def update_client_info(client_id, update_data):
    """
    Update client information.
    
    Args:
        client_id (str): Client identifier
        update_data (dict): Data to update
    
    Returns:
        dict: Update result with success/error status
    """
    try:
        # Step 1: Validate update data
        validate_client_update_data(client_id, update_data)
        
        # Step 2: Process the update
        result = process_client_update(client_id, update_data)
        
        # Step 3: Return success response
        return _create_update_success_response(result)
        
    except ClientValidationError as e:
        logger.warning(f"Client update validation failed for {client_id}: {str(e)}")
        return _create_update_error_response('validation_error', str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating client {client_id}: {str(e)}")
        return _create_update_error_response('processing_error', 'Update failed')

def get_client_details(client_id):
    """
    Get detailed client information.
    
    Args:
        client_id (str): Client identifier
    
    Returns:
        dict: Client details or None if not found
    """
    try:
        # Step 1: Validate client ID
        if not client_id:
            return None
        
        # Step 2: Get client information
        client_info = get_client_information(client_id)
        
        # Step 3: Return formatted information
        return client_info
        
    except Exception as e:
        logger.error(f"Error getting client details for {client_id}: {str(e)}")
        return None

def refresh_api_key(client_id):
    """
    Generate a new API key for an existing client.
    
    Args:
        client_id (str): Client identifier
    
    Returns:
        dict: New API key information or error
    """
    try:
        # Step 1: Validate client exists
        client_info = get_client_information(client_id)
        if not client_info:
            return _create_api_key_error_response('client_not_found', 'Client not found')
        
        # Step 2: Generate new API key
        api_key_result = process_api_key_generation(client_id, force_new=True)
        
        # Step 3: Return new API key
        return _create_api_key_success_response(api_key_result)
        
    except Exception as e:
        logger.error(f"Error refreshing API key for {client_id}: {str(e)}")
        return _create_api_key_error_response('processing_error', 'API key refresh failed')

# ============================================================================
# Helper Functions - Private Implementation Details
# ============================================================================

def _create_registration_success_response(client_id, api_key_result, is_new_client):
    """Create standardized registration success response."""
    message = "New client registered successfully" if is_new_client else "Client updated successfully"
    
    response = ClientRegistrationResponse(
        success=True,
        client_id=client_id,
        api_key=api_key_result.get('api_key'),
        expires_at=api_key_result.get('expires_at'),
        message=message
    )
    
    return response.to_dict()

def _create_registration_error_response(error_type, error_message):
    """Create standardized registration error response."""
    response = ClientRegistrationResponse(
        success=False,
        client_id="",
        error=error_message,
        message=f"Registration failed: {error_type}"
    )
    
    return response.to_dict()

def _create_update_success_response(update_result):
    """Create standardized update success response."""
    return {
        'success': True,
        'message': 'Client updated successfully',
        'updated_fields': update_result.get('updated_fields', []),
        'timestamp': datetime.now().isoformat()
    }

def _create_update_error_response(error_type, error_message):
    """Create standardized update error response."""
    return {
        'success': False,
        'error': error_message,
        'error_type': error_type,
        'timestamp': datetime.now().isoformat()
    }

def _create_api_key_success_response(api_key_result):
    """Create standardized API key success response."""
    return {
        'success': True,
        'api_key': api_key_result.get('api_key'),
        'expires_at': api_key_result.get('expires_at'),
        'message': 'API key generated successfully',
        'timestamp': datetime.now().isoformat()
    }

def _create_api_key_error_response(error_type, error_message):
    """Create standardized API key error response."""
    return {
        'success': False,
        'error': error_message,
        'error_type': error_type,
        'timestamp': datetime.now().isoformat()
    }