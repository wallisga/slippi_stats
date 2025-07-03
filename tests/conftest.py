# tests/conftest.py
"""
Simplified test configuration that works with your actual code structure.
"""
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
    
    # Initialize the database with tables
    test_db_manager.init_db()
    
    # Verify tables were created
    with test_db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[DEBUG] Test fixture created tables: {[table['name'] for table in tables]}")
    
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
def sample_game_data():
    """Sample game data matching your client format"""
    return {
        'game_id': 'test_game_123',
        'client_id': 'test_client',
        'start_time': '2024-01-01T12:00:00Z',
        'last_frame': 1000,
        'stage_id': 31,  # Battlefield
        'player_data': [
            {
                'port': 1,
                'player_name': 'TestPlayer1',
                'player_tag': 'TEST#123',
                'character_name': 'Fox',
                'result': 'Win'
            },
            {
                'port': 2,
                'player_name': 'TestPlayer2',
                'player_tag': 'OPPO#456',
                'character_name': 'Falco',
                'result': 'Loss'
            }
        ],
        'game_type': 'ranked'
    }

@pytest.fixture
def valid_api_key(test_db):
    """Create a valid API key for testing"""
    from backend.database import create_client_record, create_api_key_record
    
    # Create test client
    client_data = {
        'client_id': 'test_client',
        'hostname': 'test-host',
        'platform': 'test-platform',
        'version': '1.0.0'
    }
    create_client_record(client_data)
    
    # Create API key
    api_data = create_api_key_record('test_client')
    return api_data['api_key']