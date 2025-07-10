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
        
        # Step 3: Handle side effects
        _handle_upload_side_effects(client_id, upload_results)
        
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
        dict: File upload result with ID and status
    """
    try:
        # Step 1: Validate inputs
        if not client_id or not file_info or not file_content:
            return {'error': 'Invalid file upload parameters'}
        
        # Step 2: Process file upload
        result = process_file_upload_logic(client_id, file_info, file_content)
        
        # Step 3: Return results
        return result
        
    except Exception as e:
        logger.error(f"Error processing file upload for client {client_id}: {str(e)}")
        return {'error': str(e)}

# =============================================================================
# Helper Functions - Private Implementation Details
# =============================================================================

def _create_success_response(upload_results, message):
    """Create standardized success response."""
    return {
        'success': True,
        'message': message,
        'data': upload_results,
        'timestamp': datetime.now().isoformat()
    }

def _create_error_response(error_type, error_message):
    """Create standardized error response."""
    return {
        'success': False,
        'error': error_message,
        'error_type': error_type,
        'timestamp': datetime.now().isoformat()
    }

def _handle_upload_side_effects(client_id, upload_results):
    """Handle side effects after successful upload processing."""
    try:
        # Update client last active time
        from backend.db import connection, manager
        
        mgr = manager.SQLManager()
        
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            update_query = mgr.get_query('clients', 'update_last_active')
            cursor.execute(update_query, (datetime.now().isoformat(), client_id))
            conn.commit()
        
        logger.info(f"Updated last active time for client {client_id}")
        
    except Exception as e:
        # Log the error but don't fail the upload
        logger.warning(f"Failed to update client last active time: {str(e)}")

# Add this to upload/service.py to match client expectations

def _create_success_response(upload_results, message):
    """Create standardized success response that matches client expectations."""
    # Extract game results
    games_result = upload_results.get('games', {})
    files_result = upload_results.get('files', {})
    
    return {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        
        # Games section - matches client log parsing
        'games': {
            'uploaded': games_result.get('uploaded_count', 0),
            'duplicates': games_result.get('skipped_count', 0),
            'total_submitted': games_result.get('total_submitted', 0),
            'errors': len(games_result.get('processing_errors', []))
        },
        
        # Files section - matches client log parsing  
        'files': {
            'uploaded': files_result.get('uploaded_count', 0),
            'duplicates': files_result.get('duplicate_count', 0),
            'total_submitted': files_result.get('total_submitted', 0),
            'errors': files_result.get('error_count', 0)
        },
        
        # Additional data for debugging
        'data': upload_results
    }