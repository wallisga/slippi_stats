import pytest
import tempfile
import os
import sys
import json

# Add the server root directory to Python path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def test_db():
    """Clean in-memory database for each test that needs database"""
    from backend.database import DatabaseManager
    from backend.config import get_config
    import backend.database
    
    # Get config and ensure API_KEYS_TABLE is set
    config = get_config()
    if not hasattr(config, 'API_KEYS_TABLE'):
        config.API_KEYS_TABLE = 'api_keys'
    
    # Create in-memory database
    test_db_manager = DatabaseManager(':memory:')
    
    # CRITICAL FIX: Actually initialize the database with tables
    test_db_manager.init_db()
    
    # Verify tables were created
    with test_db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table['name'] for table in tables]
        print(f"[DEBUG] Test fixture created tables: {table_names}")
        
        # Verify we have the expected tables
        expected_tables = ['clients', 'games', 'api_keys', 'files']
        for table in expected_tables:
            if table not in table_names:
                print(f"[WARNING] Expected table '{table}' not found in: {table_names}")
    
    # Patch the global db_manager to use our test database
    original_db_manager = backend.database.db_manager
    backend.database.db_manager = test_db_manager
    
    # Also patch the global get_db_connection function
    original_get_db_connection = backend.database.get_db_connection
    def test_get_db_connection():
        return test_db_manager.get_db_connection()
    backend.database.get_db_connection = test_get_db_connection
    
    yield test_db_manager
    
    # Restore originals
    backend.database.db_manager = original_db_manager
    backend.database.get_db_connection = original_get_db_connection

@pytest.fixture
def app():
    """Create test Flask app with minimal configuration"""
    import tempfile
    
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Set environment variables for testing
    os.environ['DATABASE_PATH'] = db_path
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['FLASK_ENV'] = 'testing'
    
    # Import and create app after setting environment
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    if 'DATABASE_PATH' in os.environ:
        del os.environ['DATABASE_PATH']
    if 'SECRET_KEY' in os.environ:
        del os.environ['SECRET_KEY']

@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Test runner for CLI commands"""
    return app.test_cli_runner()