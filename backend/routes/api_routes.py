"""
API routes for Slippi Server.

This module contains all API endpoints that return JSON responses.
Uses ONLY service imports through backend.services - no direct imports.
"""

import time
from functools import wraps
from flask import Blueprint, request, jsonify, abort
from werkzeug.exceptions import RequestEntityTooLarge

from backend.config import get_config
from backend.utils import decode_player_tag

# FIXED: Import ALL services through the main services module
# This avoids circular imports and uses the proper domain exports
import backend.services as services

# Create blueprint for API routes
api_bp = Blueprint('api', __name__)

# Get configuration and logger
config = get_config()
logger = config.init_logging()

# =============================================================================
# Authentication Decorators
# =============================================================================

def require_api_key(f):
    """Decorator to require API key authentication for protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        client_info = services.authenticate_client(api_key)
        
        if not client_info:
            abort(401, description="Invalid or missing API key")
        
        kwargs['client_id'] = client_info.get('client_id')
        return f(*args, **kwargs)
    return decorated_function

def rate_limited(max_per_minute):
    """Decorator to implement rate limiting by client."""
    request_counts = {}
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = kwargs.get('client_id')
            if not client_id:
                api_key = request.headers.get('X-API-Key')
                client_info = services.validate_api_key(api_key)
                client_id = client_info.get('client_id') if client_info else 'anonymous'
            
            current_minute = int(time.time() / 60)
            if client_id not in request_counts:
                request_counts[client_id] = {}
            
            # Clean up old entries
            for minute in list(request_counts[client_id].keys()):
                if minute < current_minute:
                    del request_counts[client_id][minute]
            
            current_count = request_counts[client_id].get(current_minute, 0)
            if current_count >= max_per_minute:
                abort(429, description=f"Rate limit exceeded. Maximum {max_per_minute} requests per minute.")
            
            request_counts[client_id][current_minute] = current_count + 1
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# Player Statistics Endpoints
# =============================================================================

@api_bp.route('/player/<encoded_player_code>/stats', methods=['GET'])
@rate_limited(config.RATE_LIMIT_API)
def player_stats(encoded_player_code):
    """Get basic player statistics."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        stats = services.process_player_basic_stats(player_code)
        return jsonify(stats)
    except ValueError:
        abort(400, description="Invalid player code format")
    except Exception as e:
        logger.error(f"Error fetching player stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch player statistics'}), 500

@api_bp.route('/player/<encoded_player_code>/detailed', methods=['GET', 'POST'])
@rate_limited(config.RATE_LIMIT_API)
def player_detailed_stats(encoded_player_code):
    """
    Get detailed player statistics and analysis.
    
    Supports both GET (query params) and POST (JSON body) for filters.
    The frontend JavaScript uses POST with JSON for complex filter combinations.
    """
    try:
        player_code = decode_player_tag(encoded_player_code)
        
        # Handle different request methods
        if request.method == 'POST':
            # POST: Get filters from JSON body (frontend expects this)
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            filter_data = request.get_json() or {}
            character = filter_data.get('character', 'all')
            opponent = filter_data.get('opponent', 'all')
            opponent_character = filter_data.get('opponent_character', 'all')
            stage = filter_data.get('stage', 'all')
            limit = int(filter_data.get('limit', 100))
            
            logger.info(f"POST request with filters: {filter_data}")
            
        else:
            # GET: Get filters from query parameters (for direct URL access)
            character = request.args.get('character', 'all')
            opponent = request.args.get('opponent', 'all')
            opponent_character = request.args.get('opponent_character', 'all')
            stage = request.args.get('stage', 'all')
            limit = int(request.args.get('limit', 100))
            
            logger.info(f"GET request with query params")
        
        # Call the API service with all filter parameters
        detailed_stats = services.process_detailed_player_data(
            player_code, character, opponent, stage, limit, opponent_character
        )
        
        return jsonify(detailed_stats)
        
    except ValueError:
        return jsonify({'error': 'Invalid player code format'}), 400
    except Exception as e:
        logger.error(f"Error fetching detailed player stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch detailed player statistics'}), 500

# =============================================================================
# Client Registration Endpoints  
# =============================================================================

@api_bp.route('/clients/register', methods=['POST'])
@rate_limited(config.RATE_LIMIT_REGISTRATION)
def client_registration():
    """Register or update client information using new client domain."""
    try:
        client_data = request.json
        registration_key = request.headers.get('X-Registration-Key')
        
        # UPDATED: Use new client domain service
        result = services.register_client(client_data, registration_key)
        
        # Handle response status codes
        if result.get('success'):
            return jsonify(result), 200
        else:
            # Return appropriate error status
            error_type = result.get('error_type', 'unknown')
            if error_type == 'validation_error':
                return jsonify(result), 400
            elif error_type == 'api_key_error':
                return jsonify(result), 500
            else:
                return jsonify(result), 500
                
    except Exception as e:
        logger.error(f"Unexpected error in client registration: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_type': 'server_error'
        }), 500

@api_bp.route('/clients/me', methods=['GET'])
@require_api_key
def get_my_client_info(client_id):
    """Get current client information."""
    try:
        client_info = services.get_client_details(client_id)
        
        if not client_info:
            return jsonify({'error': 'Client not found'}), 404
        
        return jsonify({
            'success': True,
            'client': client_info
        })
        
    except Exception as e:
        logger.error(f"Error getting client info for {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to get client information'}), 500

@api_bp.route('/clients/me/refresh-key', methods=['POST'])
@require_api_key
def refresh_my_api_key(client_id):
    """Refresh API key for current client."""
    try:
        result = services.refresh_api_key(client_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            error_type = result.get('error_type', 'unknown')
            if error_type == 'client_not_found':
                return jsonify(result), 404
            else:
                return jsonify(result), 500
                
    except Exception as e:
        logger.error(f"Error refreshing API key for {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to refresh API key'}), 500


# =============================================================================
# Data Upload Endpoints
# =============================================================================

@api_bp.route('/games/upload', methods=['POST'])
@require_api_key
@rate_limited(config.RATE_LIMIT_UPLOADS)
def games_upload(client_id):
    """
    Combined games and files upload endpoint.
    
    Supports both:
    - Legacy format: {"games": [...]}
    - Combined format: {"games": [...], "files": [...]}
    """
    try:
        upload_data = _validate_upload_request()
        # FIXED: Use services.process_combined_upload
        result = services.process_combined_upload(client_id, upload_data)
        return jsonify(result)
        
    except (RequestEntityTooLarge, ValueError) as e:
        return _handle_upload_error(e)
    except Exception as e:
        logger.error(f"Unexpected error in games upload: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/files/upload', methods=['POST'])
@require_api_key  
@rate_limited(config.RATE_LIMIT_UPLOADS)
def files_upload(client_id):
    """
    Files upload endpoint - delegates to combined upload.
    
    This endpoint exists for API consistency but uses the same
    combined upload logic internally.
    """
    try:
        upload_data = _validate_upload_request()
        
        # Ensure files are present for files-only endpoint
        if not upload_data.get('files'):
            return jsonify({'error': 'No files provided'}), 400
        
        # Add empty games array if not present
        upload_data.setdefault('games', [])
        
        # FIXED: Use services.process_combined_upload
        result = services.process_combined_upload(client_id, upload_data)
        return jsonify(result)
        
    except (RequestEntityTooLarge, ValueError) as e:
        return _handle_upload_error(e)
    except Exception as e:
        logger.error(f"Unexpected error in files upload: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# File Management Endpoints
# =============================================================================

@api_bp.route('/files', methods=['GET'])
@require_api_key
@rate_limited(60)  # 60 requests per minute for file listing
def files_list(client_id):
    """List files uploaded by the client."""
    try:
        files = services.get_client_files(client_id)
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing files for client {client_id}: {str(e)}")
        return jsonify({'error': 'Failed to list files'}), 500

# =============================================================================
# Server Information Endpoints
# =============================================================================

@api_bp.route('/server/stats', methods=['GET'])
@rate_limited(30)  # 30 requests per minute for server stats
def server_statistics():
    """Get server statistics and health information."""
    try:
        stats = services.process_server_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching server statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch server statistics'}), 500

# =============================================================================
# Helper Functions
# =============================================================================

def _validate_upload_request():
    """Validate upload request data."""
    if not request.is_json:
        raise ValueError('Content-Type must be application/json')
    
    data = request.get_json()
    if not isinstance(data, dict):
        raise ValueError('Request data must be a JSON object')
    
    return data

def _handle_upload_error(error):
    """Handle upload-specific errors."""
    if isinstance(error, RequestEntityTooLarge):
        return jsonify({'error': 'Upload too large'}), 413
    elif isinstance(error, ValueError):
        return jsonify({'error': str(error)}), 400
    else:
        return jsonify({'error': 'Upload error'}), 500