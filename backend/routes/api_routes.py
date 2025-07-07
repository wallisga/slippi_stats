"""
API routes for Slippi Server.

This module contains all API endpoints that return JSON responses.
Uses ONLY api_service for business logic - no direct database imports.
"""

import time
from functools import wraps
from flask import Blueprint, request, jsonify, abort
from werkzeug.exceptions import RequestEntityTooLarge

from backend.config import get_config
from backend.utils import decode_player_tag
import backend.services.api_service as api_service
from backend.services import (
    process_combined_upload,
    upload_games_for_client, 
    process_file_upload
)

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
        # FIXED: Use service layer for validation
        client_info = api_service.validate_api_key(api_key)
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
                client_info = api_service.validate_api_key(api_key)
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
# Player API Endpoints
# =============================================================================

@api_bp.route('/player/<encoded_player_code>/stats')
def player_stats(encoded_player_code):
    """Get basic player statistics."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        result = api_service.process_player_basic_stats(player_code)
        if result is None:
            return jsonify({'error': f"Player '{player_code}' not found"}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/player/<encoded_player_code>/games')
def player_games(encoded_player_code):
    """Get paginated games for a player."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        page = max(1, int(request.args.get('page', '1')))
        
        result = api_service.process_paginated_player_games(player_code, page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/player/<encoded_player_code>/detailed', methods=['POST'])
def player_detailed_post(encoded_player_code):
    """POST version of the detailed player API for complex filters."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        logger.info(f"API detailed stats POST request for player: '{player_code}'")
        
        filter_data = request.get_json() or {}
        logger.info(f"POST Filters: {filter_data}")
        
        result = api_service.process_detailed_player_data(player_code, filter_data)
        if result is None:
            return jsonify({'error': f"Player '{player_code}' not found"}), 404
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in detailed player POST API: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# Client Management Endpoints
# =============================================================================

@api_bp.route('/clients/register', methods=['POST'])
def clients_register():
    """Register a new client."""
    client_data = request.json
    registration_key = request.headers.get('X-Registration-Key')
    result = api_service.process_client_registration(client_data, registration_key)
    return jsonify(result)

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
        result = process_combined_upload(client_id, upload_data)
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
        
        result = api_service.process_combined_upload(client_id, upload_data)
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
        limit = min(100, int(request.args.get('limit', '50')))  # Max 100 files per request
        
        # FIXED: Use service layer instead of direct database call
        result = api_service.get_client_files(client_id, limit=limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error listing files for client {client_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files/<file_id>', methods=['GET'])
@require_api_key
@rate_limited(30)  # 30 requests per minute for file details
def file_details(file_id, client_id):
    """Get details about a specific file."""
    try:
        # FIXED: Use service layer instead of direct database call
        result = api_service.get_file_details(file_id, client_id)
        
        if result is None:
            abort(404, description="File not found")
            
        if 'error' in result:
            if 'Access denied' in result['error']:
                abort(403, description="Access denied")
            else:
                abort(404, description="File not found")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting file details for {file_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# Server Information Endpoints
# =============================================================================

@api_bp.route('/stats', methods=['GET'])
def server_stats():
    """Get server statistics."""
    try:
        stats = api_service.process_server_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/files/stats', methods=['GET'])
def admin_file_stats():
    """Get file storage statistics (admin endpoint)."""
    try:
        # FIXED: Use service layer instead of direct database call
        stats = api_service.get_admin_file_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting file stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# ============================================================================
# Route Helper Functions
# ============================================================================

def _validate_upload_request():
    """Validate upload request data."""
    if not request.is_json:
        raise ValueError("Content-Type must be application/json")
    
    upload_data = request.get_json()
    if not upload_data:
        raise ValueError("No upload data provided")
    
    return upload_data

def _handle_upload_error(error):
    """Handle upload errors with appropriate HTTP responses."""
    if isinstance(error, RequestEntityTooLarge):
        return jsonify({'error': 'Upload too large'}), 413
    elif isinstance(error, ValueError):
        return jsonify({'error': str(error)}), 400
    else:
        return jsonify({'error': 'Internal server error'}), 500