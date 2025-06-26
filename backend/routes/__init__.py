"""
Routes package for Slippi Server.

This package contains all Flask route definitions organized by functionality.
Routes are implemented as blueprints for better organization and modularity.
"""

from .web_routes import web_bp
from .api_routes import api_bp
from .static_routes import static_bp
from .error_handlers import register_error_handlers

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    # Register route blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(static_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add context processors
    @app.context_processor
    def inject_request():
        from flask import request
        return dict(request=request)