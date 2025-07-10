"""
Flask Application Entry Point

Updated to use the new backend/db/ layer and handle missing config attributes gracefully
"""

import os
from flask import Flask, render_template
from backend.config import get_config

# NEW: Import from the new db layer instead of old database.py
from backend.db import connection, sql_manager

# Import route blueprints - FIXED: Import register_blueprints function
from backend.routes import register_blueprints

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
    
    # FIXED: Register blueprints properly (this handles error handlers)
    register_blueprints(app)
    
    logger.info("Slippi Server application initialized successfully")
    return app

def init_database():
    """Initialize the database using the new db layer."""
    try:
        # Initialize database connection and run schema if needed
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Initialize tables if they don't exist
            try:
                schema_queries = sql_manager.get_queries_in_category('schema')
                for query_name, query_sql in schema_queries.items():
                    if 'init_tables' in query_name or 'init_indexes' in query_name:
                        cursor.executescript(query_sql)
                logger.info("Database schema initialized")
            except Exception as e:
                logger.warning(f"Schema initialization issue (may be normal): {str(e)}")
            
            conn.commit()
            
        logger.info(f"Database initialized successfully at {config.get_database_path()}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )