"""
Web routes for Slippi Server.

This module contains all HTML page routes and static file serving.
Merged from web_routes.py and static_routes.py for simplicity.
"""

import logging
from flask import Blueprint, render_template, send_from_directory, abort, request
from backend.config import get_config
from backend.utils import decode_player_tag
import backend.services.web_service as web_service

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

# Get configuration and logger
config = get_config()
logger = logging.getLogger('SlippiServer')

# =============================================================================
# HTML Page Routes
# =============================================================================

@web_bp.route('/')
def homepage():
    """Homepage with server statistics and recent activity."""
    try:
        context_data = web_service.prepare_homepage_data()
        return render_template('pages/index/index.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading homepage"), 500

@web_bp.route('/players')
def players_list():
    """All players listing page."""
    try:
        context_data = web_service.prepare_all_players_data()
        return render_template('pages/players/players.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading players list: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading players list"), 500

@web_bp.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    """Player profile page."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        context_data = web_service.process_player_profile_request(player_code)
        return render_template('pages/player_basic/player_basic.html', **context_data)
    except ValueError:
        return render_template('pages/error_status/error_status.html',
                              status_code=400,
                              error_title="Invalid Player Code",
                              error_description="The player code format is invalid"), 400
    except Exception as e:
        logger.error(f"Error loading player profile: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error", 
                              error_description="Error loading player profile"), 500

@web_bp.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    """Detailed player analysis page."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        
        # Get optional query parameters for filtering
        character = request.args.get('character', 'all')
        opponent = request.args.get('opponent', 'all')
        stage = request.args.get('stage', 'all')
        limit = int(request.args.get('limit', '100'))
        
        context_data = web_service.process_player_detailed_request(
            player_code
        )
        return render_template('pages/player_detailed/player_detailed.html', **context_data)
    except ValueError:
        return render_template('pages/error_status/error_status.html',
                              status_code=400,
                              error_title="Invalid Player Code",
                              error_description="The player code format is invalid"), 400
    except Exception as e:
        logger.error(f"Error loading detailed player analysis: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading detailed analysis"), 500

@web_bp.route('/server/stats')
def server_stats():
    """Server statistics page."""
    try:
        context_data = web_service.prepare_server_stats_data()
        return render_template('pages/server_stats/server_stats.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading server stats: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading server statistics"), 500

@web_bp.route('/about')
def about():
    """About page with project information."""
    try:
        context_data = {
            'app_version': config.APP_VERSION,
            'client_version': config.CLIENT_VERSION,
            'client_release_date': config.CLIENT_RELEASE_DATE
        }
        return render_template('pages/about/about.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading about page: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading about page"), 500

# =============================================================================
# Client Download Routes (merged from static_routes.py)
# =============================================================================

@web_bp.route('/download')
def download_page():
    """Client download page."""
    try:
        context_data = {
            'version': config.CLIENT_VERSION,
            'release_date': config.CLIENT_RELEASE_DATE,
            'download_url': '/download/SlippiMonitor.msi',
            'app_version': config.APP_VERSION
        }
        return render_template('pages/download/download.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading download page: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error loading download page"), 500

@web_bp.route('/download/<filename>')
def download_file(filename):
    """Serve download files securely."""
    try:
        # Security: Only allow specific file types
        allowed_extensions = {'.msi', '.exe', '.zip', '.tar.gz'}
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            abort(403, "File type not allowed")
        
        downloads_dir = config.get_downloads_dir()
        
        # FIXED: Correct send_from_directory syntax
        return send_from_directory(
            directory=downloads_dir, 
            path=filename, 
            as_attachment=True
        )
    except FileNotFoundError:
        return render_template('pages/error_status/error_status.html',
                              status_code=404,
                              error_title="File Not Found",
                              error_description=f"The file {filename} was not found"), 404
    except Exception as e:
        logger.error(f"Error serving download file {filename}: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error serving file"), 500

# =============================================================================
# File Serving Routes (for uploaded .slp files)
# =============================================================================

@web_bp.route('/files/<file_id>')
def serve_file(file_id):
    """Serve uploaded files securely (requires authentication in future)."""
    try:
        # TODO: Add authentication check here in future
        # For now, this is a placeholder for future file serving functionality
        
        # Get file info from database
        from backend.services.api_service import get_file_details
        file_info = get_file_details(file_id, client_id=None)  # No auth for now
        
        if not file_info:
            return render_template('pages/error_status/error_status.html',
                                  status_code=404,
                                  error_title="File Not Found",
                                  error_description="The requested file was not found"), 404
        
        # Serve file from uploads directory
        uploads_dir = config.get_uploads_dir()
        filename = file_info.get('original_filename', f"{file_id}.slp")
        
        # FIXED: Correct send_from_directory syntax
        return send_from_directory(
            directory=uploads_dir,
            path=filename,
            as_attachment=True
        )
        
    except Exception as e:
        logger.error(f"Error serving file {file_id}: {str(e)}")
        return render_template('pages/error_status/error_status.html',
                              status_code=500,
                              error_title="Server Error",
                              error_description="Error serving file"), 500

# =============================================================================
# Error Handlers (moved from error_handlers.py for simplicity)
# =============================================================================

@web_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors with custom page."""
    return render_template('pages/error_status/error_status.html',
                          status_code=404,
                          error_title="Page Not Found",
                          error_description="The page you're looking for doesn't exist.",
                          error_type="not_found"), 404

@web_bp.app_errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    return render_template('pages/error_status/error_status.html',
                          status_code=403,
                          error_title="Access Forbidden",
                          error_description="You don't have permission to access this resource.",
                          error_type="forbidden"), 403

@web_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('pages/error_status/error_status.html',
                          status_code=500,
                          error_title="Internal Server Error",
                          error_description="Something went wrong on our end.",
                          error_type="server_error"), 500