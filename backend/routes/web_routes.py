"""
Web routes for Slippi Server.

This module contains all web page routes that serve HTML templates.
Uses web_service for business logic and data preparation.
"""

from flask import Blueprint, render_template, redirect
import backend.web_service as web_service

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
# Player Profile Pages
# =============================================================================

@web_bp.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    """Basic player profile page."""
    result = web_service.process_player_profile_request(encoded_player_code)
    if result['redirect']:
        return redirect(result['url'])
    return render_template('pages/player_basic/player_basic.html', **result['data'])

@web_bp.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    """Detailed player analysis page."""
    result = web_service.process_player_detailed_request(encoded_player_code)
    if result['redirect']:
        return redirect(result['url'])
    return render_template('pages/player_detailed/player_detailed.html', **result['data'])

# =============================================================================
# Information Pages
# =============================================================================

@web_bp.route('/how-to')
def how_to():
    """Instructions page."""
    return render_template('pages/how_to/how_to.html')