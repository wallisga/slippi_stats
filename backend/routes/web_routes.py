# Fixed backend/routes/web_routes.py - Player Profile Routes
# These routes now handle the simplified service function responses

"""
Web routes for Slippi Server.

This module contains all web page routes that serve HTML templates.
Uses web_service for business logic and data preparation.
"""

from flask import Blueprint, render_template, redirect
import backend.services.web_service as web_service

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

# =============================================================================
# Main Web Pages
# =============================================================================

@web_bp.route('/')
def index():
    """Homepage with recent games and top players."""
    data = web_service.prepare_homepage_data()
    return render_template('pages/index/index.html', **data)

@web_bp.route('/players')
def players():
    """All players index page."""
    data = web_service.prepare_all_players_data()
    return render_template('pages/players/players.html', **data)

# =============================================================================
# Player Profile Pages - FIXED
# =============================================================================

@web_bp.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    """
    Basic player profile page.
    """
    # Service function will abort(404) or abort(500) if there are issues
    # Flask error handlers will catch these and show proper error pages
    data = web_service.process_player_profile_request(encoded_player_code)
    return render_template('pages/player_basic/player_basic.html', **data)

@web_bp.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    """
    Detailed player analysis page.
    """
    # Service function will abort(404) or abort(500) if there are issues
    # Flask error handlers will catch these and show proper error pages
    data = web_service.process_player_detailed_request(encoded_player_code)
    return render_template('pages/player_detailed/player_detailed.html', **data)

# =============================================================================
# Information Pages
# =============================================================================

@web_bp.route('/how-to')
def how_to():
    """Instructions page."""
    return render_template('pages/how_to/how_to.html')