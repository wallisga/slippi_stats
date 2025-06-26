"""
Slippi Server - Flask web application for storing and retrieving Super Smash Bros. Melee game data.
PHASE 1 REFACTORING COMPLETED:
- All configuration moved to config.py
- All database operations moved to database.py
- Clean separation of concerns
- Maintained backward compatibility with existing templates

PHASE 2 REFACTORING COMPLETED:
- CLEANUP: Removed unused functions and fixed handler usage
- UTILS: Moved utilities to utils.py module (minimal version)
- SERVICES: Split business logic into web_service.py and api_service.py

PHASE 3 REFACTORING COMPLETED:
- DATABASE: Pure data access layer with table-specific functions
- UTILS: Added shared business logic functions
- SERVICES: Updated to use new database functions and utils
"""

# =============================================================================
# Base Modules
# =============================================================================

import time
from functools import wraps

# =============================================================================
# Third Party Modules
# =============================================================================

from flask import Flask, render_template, request, jsonify, abort, redirect, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

# =============================================================================
# App Modules
# =============================================================================

from backend.config import get_config
from backend.utils import decode_player_tag, get_error_template_data
from backend.database import init_db, validate_api_key
import backend.web_service as web_service
import backend.api_service as api_service

# =============================================================================
# Application Initialization
# =============================================================================

config = get_config()
app = Flask(__name__, 
            template_folder='frontend',    # Templates now in frontend/
            static_folder='frontend')      # Static assets now in frontend/
app.config.update({'SECRET_KEY': config.SECRET_KEY, 'DEBUG': config.DEBUG})
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
logger = config.init_logging()
config.validate_config()

@app.context_processor
def inject_request():
    return dict(request=request)

# =============================================================================
# Decorator Functions
# =============================================================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        client_id = validate_api_key(api_key)
        if not client_id:
            abort(401, description="Invalid or missing API key")
        kwargs['client_id'] = client_id
        return f(*args, **kwargs)
    return decorated_function

def rate_limited(max_per_minute):
    request_counts = {}
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = kwargs.get('client_id')
            if not client_id:
                api_key = request.headers.get('X-API-Key')
                client_id = validate_api_key(api_key) or 'anonymous'
            current_minute = int(time.time() / 60)
            if client_id not in request_counts:
                request_counts[client_id] = {}
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
# Web Routes (Using Web Service)
# =============================================================================

@app.route('/')
def web_simple_index():
    """Homepage with recent games and top players."""
    data = web_service.prepare_homepage_data()
    return render_template('pages/index/index.html', **data)

@app.route('/player/<encoded_player_code>')
def web_player_profile(encoded_player_code):
    """Basic player profile page."""
    result = web_service.process_player_profile_request(encoded_player_code)
    if result['redirect']:
        return redirect(result['url'])
    return render_template('pages/player_basic/player_basic.html', **result['data'])

@app.route('/player/<encoded_player_code>/detailed')
def web_player_detailed(encoded_player_code):
    """Detailed player analysis page."""
    result = web_service.process_player_detailed_request(encoded_player_code)
    if result['redirect']:
        return redirect(result['url'])
    return render_template('pages/player_detailed/player_detailed.html', **result['data'])

@app.route('/players')
def web_simple_players():
    """All players index page."""
    data = web_service.prepare_all_players_data()
    return render_template('pages/players/players.html', **data)

# =============================================================================
# API Routes (Using API Service)
# =============================================================================

@app.route('/api/player/<encoded_player_code>/detailed', methods=['POST'])
def api_player_detailed_post(encoded_player_code):
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

@app.route('/api/player/<encoded_player_code>/games')
def api_player_games(encoded_player_code):
    """Get paginated games for a player."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        page = max(1, int(request.args.get('page', '1')))
        
        result = api_service.process_paginated_player_games(player_code, page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<encoded_player_code>/stats')
def api_player_stats(encoded_player_code):
    """Get basic player statistics."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        result = api_service.process_player_basic_stats(player_code)
        if result is None:
            return jsonify({'error': f"Player '{player_code}' not found"}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/register', methods=['POST'])
def api_clients_register():
    """Register a new client."""
    client_data = request.json
    registration_key = request.headers.get('X-Registration-Key')
    result = api_service.process_client_registration(client_data, registration_key)
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def api_server_stats():
    """Get server statistics."""
    try:
        stats = api_service.process_server_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
@require_api_key
@rate_limited(config.RATE_LIMIT_UPLOADS)
def api_files_upload(client_id):
    """
    Upload files with metadata.
    Expects JSON payload with files data including base64 encoded content.
    """
    try:
        upload_data = request.json
        if not upload_data:
            abort(400, description="No upload data provided")
        
        result = api_service.process_combined_upload(client_id, upload_data)
        return jsonify(result)
        
    except RequestEntityTooLarge:
        abort(413, description="File too large")
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error in file upload API: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")

@app.route('/api/files', methods=['GET'])
@require_api_key
@rate_limited(60)  # 60 requests per minute for file listing
def api_files_list(client_id):
    """List files uploaded by the client."""
    try:
        limit = min(100, int(request.args.get('limit', '50')))  # Max 100 files per request
        
        from backend.database import get_files_by_client
        files = get_files_by_client(client_id, limit=limit)
        
        # Convert to JSON-serializable format
        files_data = []
        for file_record in files:
            files_data.append({
                'file_id': file_record['file_id'],
                'file_hash': file_record['file_hash'],
                'original_filename': file_record['original_filename'],
                'file_size': file_record['file_size'],
                'upload_date': file_record['upload_date'],
                'metadata': json.loads(file_record['metadata']) if file_record['metadata'] else {}
            })
        
        return jsonify({
            'files': files_data,
            'count': len(files_data)
        })
        
    except Exception as e:
        logger.error(f"Error listing files for client {client_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<file_id>', methods=['GET'])
@require_api_key
@rate_limited(30)  # 30 requests per minute for file details
def api_file_details(file_id, client_id):
    """Get details about a specific file."""
    try:
        from backend.database import get_file_by_id
        file_record = get_file_by_id(file_id)
        
        if not file_record:
            abort(404, description="File not found")
        
        # Check if client owns this file
        if file_record['client_id'] != client_id:
            abort(403, description="Access denied")
        
        file_data = {
            'file_id': file_record['file_id'],
            'file_hash': file_record['file_hash'],
            'original_filename': file_record['original_filename'],
            'file_size': file_record['file_size'],
            'upload_date': file_record['upload_date'],
            'metadata': json.loads(file_record['metadata']) if file_record['metadata'] else {}
        }
        
        return jsonify(file_data)
        
    except Exception as e:
        logger.error(f"Error getting file details for {file_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/files/stats', methods=['GET'])
def api_admin_file_stats():
    """Get file storage statistics (admin endpoint)."""
    try:
        # You might want to add admin authentication here
        from backend.database import get_enhanced_database_stats
        stats = get_enhanced_database_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting file stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Enhanced games upload endpoint (backward compatible)
@app.route('/api/games/upload', methods=['POST'])
@require_api_key
@rate_limited(config.RATE_LIMIT_UPLOADS)
def api_games_upload(client_id):
    """
    Games upload endpoint that supports both legacy format and new combined format.
    
    Legacy format: {"client_id": "...", "games": [...]}
    New format: {"client_id": "...", "games": [...], "files": [...]}
    """
    try:
        upload_data = request.json
        if not upload_data:
            abort(400, description="No upload data provided")
        
        # Check if this is the new combined format (has files) or legacy format
        if 'files' in upload_data and upload_data['files']:
            # New combined format
            result = api_service.process_combined_upload(client_id, upload_data)
        else:
            # Legacy format - just process games
            result = api_service.process_games_upload(client_id, upload_data)
        
        return jsonify(result)
        
    except RequestEntityTooLarge:
        abort(413, description="Upload too large")
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced games upload API: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")        

# =============================================================================
# Static File Routes
# =============================================================================

@app.route('/download')
def web_simple_download():
    """Client download page."""
    return render_template('pages/download/download.html', 
                          version=config.CLIENT_VERSION,
                          release_date=config.CLIENT_RELEASE_DATE, 
                          download_url="/download/SlippiMonitor.msi")

@app.route('/download/<filename>')
def web_download_file(filename):
    """Serve download files."""
    downloads_dir = config.get_downloads_dir()
    return send_from_directory(path=downloads_dir, filename=filename, as_attachment=True)

@app.route('/how-to')
def how_to_page():
    """Instructions page."""
    return render_template('pages/how_to/how_to.html')

# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(400)
def bad_request(error):
    template_data = get_error_template_data(400, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 400

@app.errorhandler(401)
def unauthorized(error):
    template_data = get_error_template_data(401, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 401

@app.errorhandler(403)
def forbidden(error):
    template_data = get_error_template_data(403, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 403

@app.errorhandler(404)
def page_not_found(error):
    template_data = get_error_template_data(404, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    template_data = get_error_template_data(413, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 413

@app.errorhandler(429)
def too_many_requests(error):
    template_data = get_error_template_data(429, str(error.description))
    return render_template('pages/error_status/error_status.html', **template_data), 429

@app.errorhandler(500)
def server_error(error):
    template_data = get_error_template_data(500, str(error))
    return render_template('pages/error_status/error_status.html', **template_data), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception: {str(error)}")
    # Use get_error_template_data for consistency
    template_data = get_error_template_data(500, f"An unexpected error occurred: {str(error)}")
    return render_template('pages/error_exception/error_exception.html', **template_data), 500

# =============================================================================
# Application Initialization
# =============================================================================

init_db()

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)