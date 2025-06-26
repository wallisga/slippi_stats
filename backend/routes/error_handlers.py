"""
Error handlers for Slippi Server.

This module contains all HTTP error handlers that return appropriate error pages.
"""

from flask import render_template
from backend.config import get_config
from backend.utils import get_error_template_data

# Get configuration and logger
config = get_config()
logger = config.init_logging()

def register_error_handlers(app):
    """
    Register all error handlers with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    
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
        template_data = get_error_template_data(500, f"An unexpected error occurred: {str(error)}")
        return render_template('pages/error_exception/error_exception.html', **template_data), 500