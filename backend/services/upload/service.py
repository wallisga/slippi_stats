"""
Upload Service Orchestrators

Main entry points for upload business logic following the orchestrator pattern.
"""

import logging
from datetime import datetime
from backend.config import get_config
from .validation import validate_combined_upload_data, UploadValidationError
from .processors import (
    process_upload_components, 
    handle_upload_side_effects,
    process_games_upload,
    process_file_upload_logic
)

# Configuration
config = get_config()
logger = config.init_logging()

def process_combined_upload(client_id, upload_data):
    """
    Process combined upload using standardized schemas.
    
    Args:
        client_id (str): Client identifier
        upload_data (dict): Upload payload containing games, files, client_info
    
    Returns:
        dict: Standardized response with success/error status and results
    """
    try:
        # Step 1: Validate and standardize upload data
        validated_data = validate_combined_upload_data(client_id, upload_data)
        
        # Step 2: Process upload components (now uses standardized data)
        upload_results = process_upload_components(client_id, validated_data)
        
        # Step 3: Handle side effects (unchanged)
        handle_upload_side_effects(client_id, upload_results)
        
        # Step 4: Create standardized response
        return _create_success_response(upload_results, 'Combined upload processed successfully')
        
    except UploadValidationError as e:
        logger.warning(f"Upload validation failed for client {client_id}: {str(e)}")
        return _create_error_response('validation_error', str(e))
    except Exception as e:
        logger.error(f"Unexpected error in combined upload for client {client_id}: {str(e)}")
        return _create_error_response('processing_error', 'Upload processing failed')

def upload_games_for_client(client_id, games_data):
    """
    Upload games for a specific client.
    
    Args:
        client_id (str): Client identifier
        games_data (list): List of game data to upload
    
    Returns:
        dict: Upload results with counts and status
    """
    try:
        # Step 1: Validate games data
        if not client_id or not games_data:
            return {'error': 'Invalid client_id or games_data'}
        
        # Step 2: Process games upload
        result = process_games_upload(client_id, games_data)
        
        # Step 3: Return results
        return result
        
    except Exception as e:
        logger.error(f"Error uploading games for client {client_id}: {str(e)}")
        return {'error': str(e)}

def process_file_upload(client_id, file_info, file_content):
    """
    Process individual file upload.
    
    Args:
        client_id (str): Client identifier
        file_info (dict): File metadata
        file_content (bytes): File content
    
    Returns:
        dict: File upload result
    """
    try:
        # Step 1: Process file upload
        result = process_file_upload_logic(client_id, file_info, file_content)
        
        # Step 2: Return results
        return result
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return {'error': str(e)}

# Helper functions remain the same
def _create_success_response(data, message):
    """Create standardized success response."""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

def _create_error_response(error_type, error_message):
    """Create standardized error response."""
    return {
        'success': False,
        'error_type': error_type,
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    }