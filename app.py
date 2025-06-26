"""
Slippi Server - Flask web application entry point.

This is the main application file that initializes Flask and registers route blueprints.
All route logic has been moved to backend/routes/ for better organization.
"""

from flask import Flask
from backend.config import get_config
from backend.database import init_db
from backend.routes import register_blueprints

# =============================================================================
# Application Initialization
# =============================================================================

def create_app():
    """
    Application factory pattern for creating Flask app instances.
    """
    # Get configuration
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='frontend',    # Templates in frontend/
                static_folder='frontend')      # Static assets in frontend/
    
    # Configure Flask app
    app.config.update({
        'SECRET_KEY': config.SECRET_KEY,
        'DEBUG': config.DEBUG,
        'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH
    })
    
    # Initialize logging
    logger = config.init_logging()
    
    # Validate configuration
    config.validate_config()
    
    # Initialize database
    init_db()
    
    # Register all route blueprints
    register_blueprints(app)
    
    logger.info("Slippi Server application initialized successfully")
    return app

# =============================================================================
# Application Entry Point
# =============================================================================

# Create the application instance
app = create_app()

if __name__ == '__main__':
    config = get_config()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)