"""
Flask Application Entry Point

Updated to use the new backend/db/ layer and handle missing config attributes gracefully
"""

import os
from flask import Flask, render_template
from backend.config import get_config

# NEW: Import from the new db layer instead of old database.py
from backend.db import connection, sql_manager

# Import route blueprints
from backend.routes.web_routes import web_bp
from backend.routes.api_routes import api_bp

# Get configuration and logger
config = get_config()
logger = config.init_logging()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='frontend', 
                template_folder='frontend')
    
    # Configure Flask app with safe defaults
    app.config['SECRET_KEY'] = getattr(config, 'SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # FIXED: Handle missing MAX_REQUEST_SIZE attribute
    max_request_size = getattr(config, 'MAX_REQUEST_SIZE', 16 * 1024 * 1024)  # Default 16MB
    app.config['MAX_CONTENT_LENGTH'] = max_request_size
    
    # NEW: Initialize database using new layer
    init_database()
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('pages/error_status/error.html', 
                             status_code=404, 
                             error_title="Page Not Found",
                             error_description="The page you're looking for doesn't exist."), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('pages/error_status/error.html',
                             status_code=500,
                             error_title="Internal Server Error", 
                             error_description="Something went wrong on our end."), 500
    
    logger.info("Slippi Server application initialized successfully")
    return app

def init_database():
    """Initialize the database using the new db layer."""
    try:
        db_path = getattr(config, 'get_database_path', lambda: 'slippi_data.db')()
        logger.info(f"Initializing database at {db_path}")
        
        # Use the new connection manager to initialize database
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables using external SQL
            if sql_manager.has_query('schema', 'init_tables'):
                # FIXED: Handle missing API_KEYS_TABLE attribute
                api_keys_table = getattr(config, 'API_KEYS_TABLE', 'api_keys')
                tables_sql = sql_manager.format_query('schema', 'init_tables', 
                                                    api_keys_table=api_keys_table)
                
                # Split and execute each CREATE TABLE statement
                statements = [stmt.strip() for stmt in tables_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
                    
            # Create indexes using external SQL
            if sql_manager.has_query('schema', 'init_indexes'):
                api_keys_table = getattr(config, 'API_KEYS_TABLE', 'api_keys')
                indexes_sql = sql_manager.format_query('schema', 'init_indexes',
                                                     api_keys_table=api_keys_table)
                
                # Split and execute each CREATE INDEX statement
                index_statements = [stmt.strip() for stmt in indexes_sql.split(';') if stmt.strip()]
                for statement in index_statements:
                    try:
                        cursor.execute(statement)
                        logger.debug(f"Created index: {statement[:50]}...")
                    except Exception as e:
                        logger.warning(f"Could not create index: {str(e)}")
            
            conn.commit()
            logger.info(f"Database initialized successfully at {db_path}")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )