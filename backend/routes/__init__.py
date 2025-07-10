"""
Routes package for Slippi Server.

Simplified structure with static routes merged into web routes.
"""

from .web_routes import web_bp
from .api_routes import api_bp

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    # Register route blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add context processors
    @app.context_processor
    def inject_request():
        from flask import request
        return dict(request=request)