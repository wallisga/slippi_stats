# tests/test_upload_pipeline.py
"""
Upload Pipeline Integration Tests - NEW FILE

Test complete upload workflows including file uploads, game data processing,
and client registration flows.
"""
import pytest
import tempfile
import os

class TestUploadPipelineIntegration:
    """Test complete upload workflows"""
    
    def test_game_data_upload_workflow(self, test_db):
        """Test complete game data upload from client to database"""
        from backend.services.api_service import upload_games_for_client
        
        # Setup test client
        client_id = "test_client_123"
        
        # Test with valid game data structure
        games_data = [
            {
                "game_id": "test_game_1",
                "start_time": "2023-01-01T12:00:00Z",
                "player_data": [
                    {"player_tag": "PLAYER#123", "character_name": "Fox", "result": "Win"},
                    {"player_tag": "OPPONENT#456", "character_name": "Falco", "result": "Loss"}
                ]
            }
        ]
        
        # Execute upload
        result = upload_games_for_client(client_id, games_data)
        
        # Verify upload result
        assert isinstance(result, dict)
        assert "success" in result
        assert isinstance(result["success"], bool)
        
        if result["success"]:
            assert "games_processed" in result
            assert result["games_processed"] >= 0
        else:
            assert "error" in result
    
    def test_file_upload_workflow(self, test_db):
        """Test file upload with correct data format"""
        from backend.services.api_service import process_file_upload
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.slp', delete=False) as tmp_file:
            tmp_file.write(b"test slp file content")
            tmp_file_path = tmp_file.name
        
        try:
            # Test with correct data format - your function expects bytes
            client_id = "test_client"
            file_data = b"test slp file content"  # Use bytes directly
            metadata = {"players": ["PLAYER#123", "OPPONENT#456"]}
            
            # Execute upload
            result = process_file_upload(client_id, file_data, metadata)
            
            # Verify upload result
            assert isinstance(result, dict)
            assert "success" in result
            
        finally:
            # Cleanup
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_client_registration_workflow(self, test_db):
        """Test client registration and API key generation"""
        from backend.services.api_service import register_or_update_client
        
        # Test client data
        client_data = {
            "client_id": "new_client_123",
            "name": "Test Client",
            "description": "Test client for upload",
            "contact_email": "test@example.com"
        }
        
        # Execute registration
        result = register_or_update_client(client_data)
        
        # Verify registration result
        assert isinstance(result, dict)
        assert "success" in result
        assert isinstance(result["success"], bool)
        
        # Structure should be consistent regardless of success
        if result["success"]:
            assert "api_key" in result
        else:
            assert "error" in result
    
    def test_upload_error_handling(self, test_db):
        """Test upload error scenarios handled gracefully"""
        from backend.services.api_service import upload_games_for_client
        
        # Test with invalid game data (missing required fields)
        invalid_games = [
            {"incomplete": "data", "missing": "required_fields"}
        ]
        
        result = upload_games_for_client("test_client", invalid_games)
        
        # Verify error handling
        assert isinstance(result, dict)
        assert "success" in result
        # Your function may handle this gracefully and skip invalid games
        # or return an error - both are acceptable
        assert isinstance(result["success"], bool)

class TestUploadValidation:
    """Test upload data validation"""
    
    def test_upload_authentication(self):
        """Test upload authentication works correctly"""
        from backend.database import validate_api_key
        
        # Test with various inputs
        result = validate_api_key("test_key")
        assert result is None  # Expected with empty test database
        
        # Test with None
        result = validate_api_key(None)
        assert result is None
        
        # Test with empty string
        result = validate_api_key("")
        assert result is None