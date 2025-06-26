"""
Static file routes for Slippi Server.

This module contains routes for serving static files, downloads, and other non-API content.
"""

from flask import Blueprint, render_template, send_from_directory
from backend.config import get_config

# Create blueprint for static routes
static_bp = Blueprint('static', __name__)

# Get configuration
config = get_config()

# =============================================================================
# Download Routes
# =============================================================================

@static_bp.route('/download')
def download_page():
    """Client download page."""
    return render_template('pages/download/download.html', 
                          version=config.CLIENT_VERSION,
                          release_date=config.CLIENT_RELEASE_DATE, 
                          download_url="/download/SlippiMonitor.msi")

@static_bp.route('/download/<filename>')
def download_file(filename):
    """Serve download files."""
    downloads_dir = config.get_downloads_dir()
    return send_from_directory(path=downloads_dir, filename=filename, as_attachment=True)