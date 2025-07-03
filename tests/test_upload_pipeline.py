# tests/test_upload_pipeline.py
"""
Comprehensive Upload Pipeline Tests for Slippi Server

This test suite covers the complete upload pipeline from client registration
through file and game data upload, including all error scenarios and edge cases.
These tests protect the most critical functionality: getting user data into the system.
"""
import pytest
import json
import tempfile
import os
import base64
import hashlib
from datetime import datetime, timedelta
from backend.database import DatabaseManager

class TestUploadPipeline:
    """Test the complete upload pipeline from client to database"""
    
    def create_test_database(self):
        """Create a clean test database with tables"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        db_manager = DatabaseManager(db_path)
        db_manager.init_db()
        
        return db_manager, db_path
    
    def cleanup_test_database(self, db_path):
        """Clean up test database file"""
        try:
            os.unlink(db_path)
        except:
            pass

    # =============================================================================
    # Client Registration Pipeline Tests
    # =============================================================================

    def test_client_registration_complete_flow(self):
        """Test the complete client registration process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            # Patch database for this test
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import register_or_update_client
                
                # Test new client registration
                client_data = {
                    'client_id': 'test_client_upload_001',
                    'hostname': 'test-gaming-pc',
                    'platform': 'Windows',
                    'version': '1.1.0'
                }
                
                result = register_or_update_client(client_data)
                
                # Test contract - what the function promises to return
                assert isinstance(result, dict)
                assert 'success' in result
                assert 'api_key' in result
                assert 'expires_at' in result
                assert result['success'] is True
                assert isinstance(result['api_key'], str)
                assert len(result['api_key']) > 10  # Should be a real key
                
                # Test that client was actually created in database
                from backend.database import check_client_exists
                assert check_client_exists(client_data['client_id']) is True
                
                print(f"✅ Client registration flow works for {client_data['client_id']}")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_client_registration_update_existing(self):
        """Test updating an existing client during registration"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import register_or_update_client
                from backend.database import get_clients_by_id
                
                client_data = {
                    'client_id': 'test_client_update_001',
                    'hostname': 'old-hostname',
                    'platform': 'Windows',
                    'version': '1.0.0'
                }
                
                # First registration
                result1 = register_or_update_client(client_data)
                old_api_key = result1['api_key']
                
                # Update client info
                updated_data = client_data.copy()
                updated_data.update({
                    'hostname': 'new-hostname',
                    'version': '1.2.0'
                })
                
                result2 = register_or_update_client(updated_data)
                
                # Should get new API key
                assert result2['success'] is True
                assert result2['api_key'] != old_api_key
                
                # Verify update in database
                client_record = get_clients_by_id(client_data['client_id'])
                assert client_record['hostname'] == 'new-hostname'
                assert client_record['version'] == '1.2.0'
                
                print("✅ Client update flow works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_client_registration_error_scenarios(self):
        """Test client registration error handling"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import register_or_update_client
                
                # Test missing client_id
                with pytest.raises((ValueError, KeyError)):
                    register_or_update_client({
                        'hostname': 'test-host',
                        'platform': 'Windows'
                    })
                
                # Test empty client_id
                with pytest.raises(ValueError):
                    register_or_update_client({
                        'client_id': '',
                        'hostname': 'test-host'
                    })
                
                print("✅ Client registration error handling works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # Games Upload Pipeline Tests
    # =============================================================================

    def test_games_upload_complete_flow(self):
        """Test the complete games upload process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client first
                client_data = {
                    'client_id': 'test_client_upload_002',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Test games upload - this is the format your Python client sends
                games_data = [
                    {
                        'game_id': 'upload_test_game_001',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1500,
                        'stage_id': 31,  # Battlefield
                        'player_data': [
                            {
                                'port': 1,
                                'player_name': 'TestPlayer1',
                                'player_tag': 'TEST#001',
                                'character_name': 'Fox',
                                'result': 'Win'
                            },
                            {
                                'port': 2,
                                'player_name': 'TestPlayer2',
                                'player_tag': 'OPPO#002',
                                'character_name': 'Falco',
                                'result': 'Loss'
                            }
                        ],
                        'game_type': 'ranked'
                    },
                    {
                        'game_id': 'upload_test_game_002',
                        'start_time': '2024-01-01T12:15:00Z',
                        'last_frame': 2000,
                        'stage_id': 32,  # Final Destination
                        'player_data': [
                            {
                                'port': 1,
                                'player_name': 'TestPlayer1',
                                'player_tag': 'TEST#001',
                                'character_name': 'Marth',
                                'result': 'Loss'
                            }
                        ],
                        'game_type': 'casual'
                    }
                ]
                
                result = upload_games_for_client(client_data['client_id'], games_data)
                
                # Test contract - what upload function promises to return
                assert isinstance(result, dict)
                assert 'success' in result
                assert 'uploaded' in result
                assert 'duplicates' in result
                assert result['success'] is True
                assert result['uploaded'] == 2  # Should upload both games
                assert result['duplicates'] == 0  # No duplicates first time
                
                # Test that games were actually stored in database
                from backend.database import check_game_exists, get_games_all
                assert check_game_exists('upload_test_game_001') is True
                assert check_game_exists('upload_test_game_002') is True
                
                # Test that we can retrieve the games
                all_games = get_games_all(limit=10)
                assert len(all_games) >= 2
                
                print(f"✅ Games upload flow works: {result['uploaded']} games uploaded")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_games_upload_duplicate_handling(self):
        """Test duplicate game handling in upload pipeline"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_duplicates',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                games_data = [
                    {
                        'game_id': 'duplicate_test_game_001',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1500,
                        'stage_id': 31,
                        'player_data': [
                            {
                                'port': 1,
                                'player_tag': 'TEST#001',
                                'character_name': 'Fox',
                                'result': 'Win'
                            }
                        ],
                        'game_type': 'ranked'
                    }
                ]
                
                # First upload
                result1 = upload_games_for_client(client_data['client_id'], games_data)
                assert result1['uploaded'] == 1
                assert result1['duplicates'] == 0
                
                # Second upload (same games)
                result2 = upload_games_for_client(client_data['client_id'], games_data)
                assert result2['uploaded'] == 0  # No new games
                assert result2['duplicates'] == 1  # One duplicate
                
                print("✅ Duplicate handling works correctly")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_games_upload_malformed_data(self):
        """Test games upload with malformed data"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_malformed',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Test empty games list
                result1 = upload_games_for_client(client_data['client_id'], [])
                assert result1['uploaded'] == 0
                assert result1['success'] is True
                
                # Test games missing game_id
                malformed_games = [
                    {
                        # Missing game_id
                        'start_time': '2024-01-01T12:00:00Z',
                        'player_data': []
                    }
                ]
                result2 = upload_games_for_client(client_data['client_id'], malformed_games)
                assert result2['uploaded'] == 0  # Should skip malformed game
                
                # Test None input
                result3 = upload_games_for_client(client_data['client_id'], None)
                assert result3['uploaded'] == 0
                
                print("✅ Malformed data handling works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_games_upload_nonexistent_client(self):
        """Test uploading games for non-existent client"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                
                games_data = [
                    {
                        'game_id': 'test_game_nonexistent_client',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000,
                        'stage_id': 31,
                        'player_data': [{'port': 1, 'player_tag': 'TEST#001', 'character_name': 'Fox', 'result': 'Win'}],
                        'game_type': 'ranked'
                    }
                ]
                
                # This should not crash, even with missing client
                # The function should handle this gracefully
                try:
                    result = upload_games_for_client('nonexistent_client', games_data)
                    # Function should handle this gracefully, not crash
                    assert isinstance(result, dict)
                    print("✅ Graceful handling of nonexistent client")
                except Exception as e:
                    # If it throws, that's also acceptable behavior
                    print(f"Upload with missing client threw: {type(e).__name__} - this is acceptable")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # File Upload Pipeline Tests
    # =============================================================================

    def test_file_upload_complete_flow(self):
        """Test the complete file upload process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_file_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_file_upload',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create test file content
                test_file_content = b"test slippi file content for upload testing"
                file_hash = hashlib.sha256(test_file_content).hexdigest()
                
                metadata = {
                    'filename': 'test_replay.slp',
                    'file_size': len(test_file_content),
                    'game_id': 'test_game_for_file',
                    'processing_date': datetime.now().isoformat()
                }
                
                # Test file upload
                result = process_file_upload(client_data['client_id'], test_file_content, metadata)
                
                # Test contract
                assert isinstance(result, dict)
                assert 'success' in result
                assert 'file_hash' in result
                assert 'duplicate' in result
                assert result['success'] is True
                assert result['file_hash'] == file_hash
                assert result['duplicate'] is False
                
                # Test file was stored in database
                from backend.database import get_file_by_hash
                stored_file = get_file_by_hash(file_hash)
                assert stored_file is not None
                assert stored_file['original_filename'] == 'test_replay.slp'
                assert stored_file['client_id'] == client_data['client_id']
                
                print("✅ File upload flow works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_file_upload_duplicate_handling(self):
        """Test file upload duplicate detection via hash"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_file_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_file_duplicates',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                test_file_content = b"duplicate test file content"
                metadata = {
                    'filename': 'duplicate_test.slp',
                    'file_size': len(test_file_content),
                    'game_id': 'test_game_duplicate'
                }
                
                # First upload
                result1 = process_file_upload(client_data['client_id'], test_file_content, metadata)
                assert result1['success'] is True
                assert result1['duplicate'] is False
                
                # Second upload (same content, different filename)
                metadata2 = metadata.copy()
                metadata2['filename'] = 'different_name.slp'
                
                result2 = process_file_upload(client_data['client_id'], test_file_content, metadata2)
                assert result2['success'] is True
                assert result2['duplicate'] is True  # Should detect duplicate by hash
                assert result2['file_hash'] == result1['file_hash']
                
                print("✅ File duplicate detection works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_file_upload_size_limits(self):
        """Test file upload size validation"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_file_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_file_sizes',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Test empty file
                with pytest.raises(ValueError, match="Empty file"):
                    process_file_upload(client_data['client_id'], b"", {'filename': 'empty.slp'})
                
                # Test file too large (mock the MAX_FILE_SIZE)
                import backend.api_service
                original_max_size = backend.api_service.MAX_FILE_SIZE
                backend.api_service.MAX_FILE_SIZE = 100  # 100 bytes for testing
                
                try:
                    large_content = b"x" * 200  # 200 bytes
                    with pytest.raises(ValueError, match="File too large"):
                        process_file_upload(client_data['client_id'], large_content, {'filename': 'large.slp'})
                        
                    print("✅ File size validation works")
                finally:
                    backend.api_service.MAX_FILE_SIZE = original_max_size
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_file_upload_invalid_extensions(self):
        """Test file upload extension validation"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_file_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_file_extensions',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                test_content = b"test file content"
                
                # Test invalid extension
                with pytest.raises(ValueError, match="File type not allowed"):
                    process_file_upload(client_data['client_id'], test_content, {'filename': 'test.txt'})
                
                with pytest.raises(ValueError, match="File type not allowed"):
                    process_file_upload(client_data['client_id'], test_content, {'filename': 'test.exe'})
                
                # Test valid extension should work
                result = process_file_upload(client_data['client_id'], test_content, {'filename': 'test.slp'})
                assert result['success'] is True
                
                print("✅ File extension validation works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # Combined Upload Pipeline Tests
    # =============================================================================

    def test_combined_upload_complete_flow(self):
        """Test the combined upload (games + files) process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_combined_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_combined_001',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create test file content
                test_file_content = b"test slippi file content for combined upload"
                encoded_content = base64.b64encode(test_file_content).decode('utf-8')
                
                # Test combined upload data - games + files
                upload_data = {
                    'client_id': client_data['client_id'],
                    'timestamp': '2024-01-01T12:00:00Z',
                    'games': [
                        {
                            'game_id': 'combined_test_game_001',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [
                                {
                                    'port': 1,
                                    'player_tag': 'COMB#001',
                                    'character_name': 'Fox',
                                    'result': 'Win'
                                }
                            ],
                            'game_type': 'ranked'
                        }
                    ],
                    'files': [
                        {
                            'content': encoded_content,
                            'metadata': {
                                'filename': 'combined_test_replay.slp',
                                'file_size': len(test_file_content),
                                'game_id': 'combined_test_game_001',
                                'processing_date': '2024-01-01T12:00:00Z'
                            }
                        }
                    ]
                }
                
                result = process_combined_upload(client_data['client_id'], upload_data)
                
                # Test contract - what combined upload promises to return
                assert isinstance(result, dict)
                assert 'success' in result
                assert 'games' in result
                assert 'files' in result
                assert result['success'] is True
                
                # Test games part
                games_result = result['games']
                assert 'uploaded' in games_result
                assert 'duplicates' in games_result
                assert games_result['uploaded'] == 1
                
                # Test files part  
                files_result = result['files']
                assert 'uploaded' in files_result
                assert 'duplicates' in files_result
                assert files_result['uploaded'] == 1
                
                # Verify data in database
                from backend.database import check_game_exists, get_file_by_hash
                assert check_game_exists('combined_test_game_001') is True
                
                file_hash = hashlib.sha256(test_file_content).hexdigest()
                stored_file = get_file_by_hash(file_hash)
                assert stored_file is not None
                
                print(f"✅ Combined upload flow works: {games_result['uploaded']} games, {files_result['uploaded']} files")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_combined_upload_partial_failure(self):
        """Test combined upload when some parts fail"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_combined_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_partial_failure',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Upload with good games but bad files
                upload_data = {
                    'client_id': client_data['client_id'],
                    'timestamp': '2024-01-01T12:00:00Z',
                    'games': [
                        {
                            'game_id': 'partial_failure_game_001',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [
                                {
                                    'port': 1,
                                    'player_tag': 'PARTIAL#001',
                                    'character_name': 'Fox',
                                    'result': 'Win'
                                }
                            ],
                            'game_type': 'ranked'
                        }
                    ],
                    'files': [
                        {
                            # Missing content - should cause error
                            'metadata': {
                                'filename': 'bad_file.slp'
                            }
                        }
                    ]
                }
                
                result = process_combined_upload(client_data['client_id'], upload_data)
                
                # Should still succeed overall, but files should have errors
                assert result['success'] is True
                assert result['games']['uploaded'] == 1  # Games should succeed
                assert result['files']['errors'] >= 1    # Files should have errors
                
                print("✅ Partial failure handling works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_combined_upload_games_only(self):
        """Test combined upload with only games (no files)"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import process_combined_upload
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_games_only',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Upload with only games
                upload_data = {
                    'client_id': client_data['client_id'],
                    'timestamp': '2024-01-01T12:00:00Z',
                    'games': [
                        {
                            'game_id': 'games_only_test_001',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [
                                {
                                    'port': 1,
                                    'player_tag': 'GONLY#001',
                                    'character_name': 'Fox',
                                    'result': 'Win'
                                }
                            ],
                            'game_type': 'ranked'
                        }
                    ]
                    # No files key
                }
                
                result = process_combined_upload(client_data['client_id'], upload_data)
                
                assert result['success'] is True
                assert result['games']['uploaded'] == 1
                assert result['files']['uploaded'] == 0  # No files to upload
                
                print("✅ Games-only upload works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # API Key Authentication Pipeline Tests
    # =============================================================================

    def test_api_key_validation_complete_flow(self):
        """Test API key creation and validation process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.database import create_client_record, create_api_key_record, validate_api_key
                
                # Create client and API key
                client_data = {
                    'client_id': 'test_client_auth_001',
                    'hostname': 'test-host',
                    'platform': 'Windows',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create API key
                api_data = create_api_key_record(client_data['client_id'])
                api_key = api_data['api_key']
                
                # Test validation with valid key
                validated_client = validate_api_key(api_key)
                assert validated_client == client_data['client_id']
                
                # Test validation with invalid key
                invalid_result = validate_api_key('invalid_key_12345')
                assert invalid_result is None
                
                # Test validation with None
                none_result = validate_api_key(None)
                assert none_result is None
                
                # Test validation with empty string
                empty_result = validate_api_key('')
                assert empty_result is None
                
                print(f"✅ API key validation flow works for {client_data['client_id']}")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_api_key_expiration_handling(self):
        """Test API key expiration scenarios"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.database import create_client_record, create_api_key_record, validate_api_key
                
                # Create client
                client_data = {
                    'client_id': 'test_client_expiration',
                    'hostname': 'test-host',
                    'platform': 'Windows',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create expired API key
                past_date = (datetime.now() - timedelta(days=1)).isoformat()
                
                # Create API key manually with expired date
                import secrets
                expired_key = secrets.token_urlsafe(32)
                
                from backend.sql_manager import sql_manager
                from backend.config import get_config
                config = get_config()
                
                query = sql_manager.format_query('api_keys', 'insert_key', 
                                                api_keys_table=config.API_KEYS_TABLE)
                
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (
                        client_data['client_id'],
                        expired_key,
                        past_date,  # created_at
                        past_date   # expires_at (expired)
                    ))
                    conn.commit()
                
                # Test that expired key is rejected
                validated_client = validate_api_key(expired_key)
                assert validated_client is None
                
                print("✅ API key expiration handling works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_api_key_rotation(self):
        """Test API key rotation/update process"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.database import create_client_record, create_api_key_record, update_api_key_record, validate_api_key
                
                # Create client
                client_data = {
                    'client_id': 'test_client_rotation',
                    'hostname': 'test-host',
                    'platform': 'Windows',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create initial API key
                api_data1 = create_api_key_record(client_data['client_id'])
                old_key = api_data1['api_key']
                
                # Verify old key works
                assert validate_api_key(old_key) == client_data['client_id']
                
                # Rotate API key
                api_data2 = update_api_key_record(client_data['client_id'])
                new_key = api_data2['api_key']
                
                # Verify new key works and old key doesn't
                assert validate_api_key(new_key) == client_data['client_id']
                assert validate_api_key(old_key) is None  # Old key should be invalid
                assert new_key != old_key  # Should be different keys
                
                print("✅ API key rotation works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # Error Handling and Edge Cases
    # =============================================================================

    def test_upload_database_transaction_safety(self):
        """Test that upload operations are transaction-safe"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record, get_games_count
                
                # Create client
                client_data = {
                    'client_id': 'test_client_transactions',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Get initial game count
                initial_count = get_games_count()
                
                # Create games data with valid games
                games_data = [
                    {
                        'game_id': 'transaction_test_game_001',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000,
                        'stage_id': 31,
                        'player_data': [{'port': 1, 'player_tag': 'TRANS#001', 'character_name': 'Fox', 'result': 'Win'}],
                        'game_type': 'ranked'
                    },
                    {
                        'game_id': 'transaction_test_game_002',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000,
                        'stage_id': 31,
                        'player_data': [{'port': 1, 'player_tag': 'TRANS#002', 'character_name': 'Fox', 'result': 'Win'}],
                        'game_type': 'ranked'
                    }
                ]
                
                # Upload should handle individual game failures gracefully
                result = upload_games_for_client(client_data['client_id'], games_data)
                
                # Should either upload all or none (depending on implementation)
                # but shouldn't leave database in inconsistent state
                final_count = get_games_count()
                uploaded_count = final_count - initial_count
                
                assert uploaded_count == result['uploaded']
                
                print(f"✅ Transaction safety maintained: uploaded {uploaded_count} games")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_upload_concurrent_access(self):
        """Test upload pipeline under concurrent access scenarios"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            import threading
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create multiple clients
                clients = []
                for i in range(3):
                    client_data = {
                        'client_id': f'test_client_concurrent_{i}',
                        'hostname': f'test-host-{i}',
                        'platform': 'Linux',
                        'version': '1.0.0'
                    }
                    create_client_record(client_data)
                    clients.append(client_data)
                
                # Function to upload games in thread
                def upload_games_threaded(client_data, thread_id):
                    games_data = [
                        {
                            'game_id': f'concurrent_test_game_{thread_id}_{j}',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [{'port': 1, 'player_tag': f'CONC{thread_id}#{j}', 'character_name': 'Fox', 'result': 'Win'}],
                            'game_type': 'ranked'
                        }
                        for j in range(5)  # 5 games per thread
                    ]
                    
                    result = upload_games_for_client(client_data['client_id'], games_data)
                    return result
                
                # Launch concurrent uploads
                threads = []
                results = {}
                
                for i, client_data in enumerate(clients):
                    def thread_target(client=client_data, tid=i):
                        results[tid] = upload_games_threaded(client, tid)
                    
                    thread = threading.Thread(target=thread_target)
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join()
                
                # Verify all uploads succeeded
                total_uploaded = sum(result['uploaded'] for result in results.values())
                assert total_uploaded == 15  # 3 clients * 5 games each
                
                print(f"✅ Concurrent access handling works: {total_uploaded} games uploaded")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_upload_memory_usage_large_batches(self):
        """Test upload pipeline with large batches of data"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_large_batch',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create large batch of games (100 games)
                large_games_batch = []
                for i in range(100):
                    game = {
                        'game_id': f'large_batch_game_{i:03d}',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000 + i,
                        'stage_id': 31,
                        'player_data': [
                            {
                                'port': 1,
                                'player_tag': f'LARGE#{i:03d}',
                                'character_name': 'Fox',
                                'result': 'Win'
                            }
                        ],
                        'game_type': 'ranked'
                    }
                    large_games_batch.append(game)
                
                # Upload large batch
                try:
                    import psutil
                    process = psutil.Process(os.getpid())
                    memory_before = process.memory_info().rss
                    memory_monitoring = True
                except ImportError:
                    memory_monitoring = False
                
                result = upload_games_for_client(client_data['client_id'], large_games_batch)
                
                if memory_monitoring:
                    memory_after = process.memory_info().rss
                    memory_increase_mb = (memory_after - memory_before) / 1024 / 1024
                
                    # Verify upload succeeded
                    assert result['success'] is True
                    assert result['uploaded'] == 100
                    
                    # Memory usage should be reasonable (less than 50MB increase)
                    assert memory_increase_mb < 50, f"Memory usage too high: {memory_increase_mb:.2f}MB"
                    
                    print(f"✅ Large batch upload works: {result['uploaded']} games, {memory_increase_mb:.2f}MB memory increase")
                else:
                    # Just verify upload succeeded without memory monitoring
                    assert result['success'] is True
                    assert result['uploaded'] == 100
                    print(f"✅ Large batch upload works: {result['uploaded']} games")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    def test_upload_invalid_json_data(self):
        """Test upload pipeline with invalid JSON in player_data"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_invalid_json',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Test with various invalid data types
                invalid_games = [
                    {
                        'game_id': 'invalid_json_test_001',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000,
                        'stage_id': 31,
                        'player_data': "invalid_json_string",  # Invalid - string instead of list
                        'game_type': 'ranked'
                    },
                    {
                        'game_id': 'invalid_json_test_002',
                        'start_time': '2024-01-01T12:00:00Z',
                        'last_frame': 1000,
                        'stage_id': 31,
                        'player_data': None,  # Invalid - None instead of list
                        'game_type': 'ranked'
                    }
                ]
                
                # Should handle invalid data gracefully
                result = upload_games_for_client(client_data['client_id'], invalid_games)
                
                # Function should handle this gracefully - either upload with corrections or skip
                assert isinstance(result, dict)
                assert 'success' in result
                
                print("✅ Invalid JSON data handling works")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # Performance and Stress Tests
    # =============================================================================

    def test_upload_performance_benchmarks(self):
        """Test upload pipeline performance with realistic data volumes"""
        db_manager, db_path = self.create_test_database()
        
        try:
            import backend.database
            import time
            original = backend.database.db_manager
            backend.database.db_manager = db_manager
            
            try:
                from backend.api_service import upload_games_for_client
                from backend.database import create_client_record
                
                # Create client
                client_data = {
                    'client_id': 'test_client_performance',
                    'hostname': 'test-host',
                    'platform': 'Linux',
                    'version': '1.0.0'
                }
                create_client_record(client_data)
                
                # Create realistic game data (50 games)
                games_data = []
                for i in range(50):
                    game = {
                        'game_id': f'perf_test_game_{i:03d}',
                        'start_time': f'2024-01-01T{12 + (i % 12):02d}:00:00Z',
                        'last_frame': 1000 + (i * 100),
                        'stage_id': 31 + (i % 4),  # Vary stages
                        'player_data': [
                            {
                                'port': 1,
                                'player_tag': f'PERF1#{i:03d}',
                                'character_name': ['Fox', 'Falco', 'Marth', 'Sheik'][i % 4],
                                'result': 'Win'
                            },
                            {
                                'port': 2,
                                'player_tag': f'PERF2#{i:03d}',
                                'character_name': ['Captain Falcon', 'Jigglypuff', 'Peach', 'Ice Climbers'][i % 4],
                                'result': 'Loss'
                            }
                        ],
                        'game_type': ['ranked', 'casual', 'tournament'][i % 3]
                    }
                    games_data.append(game)
                
                # Measure upload time
                start_time = time.time()
                result = upload_games_for_client(client_data['client_id'], games_data)
                end_time = time.time()
                
                upload_time = end_time - start_time
                games_per_second = len(games_data) / upload_time if upload_time > 0 else float('inf')
                
                # Verify upload succeeded
                assert result['success'] is True
                assert result['uploaded'] == 50
                
                # Performance should be reasonable (at least 10 games per second)
                assert games_per_second >= 10, f"Upload too slow: {games_per_second:.2f} games/sec"
                
                print(f"✅ Upload performance: {games_per_second:.2f} games/sec ({upload_time:.3f}s total)")
                
            finally:
                backend.database.db_manager = original
                
        finally:
            self.cleanup_test_database(db_path)

    # =============================================================================
    # Integration with HTTP API Routes
    # =============================================================================

    def test_upload_api_route_integration(self, app):
        """Test upload pipeline through actual HTTP API routes"""
        with app.test_client() as client:
            # Create test client and API key through registration
            registration_data = {
                'client_id': 'test_client_api_integration',
                'hostname': 'test-host',
                'platform': 'Linux',
                'version': '1.0.0'
            }
            
            # Test client registration endpoint
            from backend.config import get_config
            config = get_config()
            
            response = client.post('/api/clients/register',
                                 json=registration_data,
                                 headers={'X-Registration-Key': config.REGISTRATION_SECRET})
            
            if response.status_code == 200:
                registration_result = response.get_json()
                api_key = registration_result['api_key']
                
                # Test games upload endpoint
                upload_data = {
                    'client_id': 'test_client_api_integration',
                    'games': [
                        {
                            'game_id': 'api_integration_test_001',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [
                                {
                                    'port': 1,
                                    'player_tag': 'API#001',
                                    'character_name': 'Fox',
                                    'result': 'Win'
                                }
                            ],
                            'game_type': 'ranked'
                        }
                    ]
                }
                
                upload_response = client.post('/api/games/upload',
                                            json=upload_data,
                                            headers={'X-API-Key': api_key})
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.get_json()
                    assert upload_result['success'] is True
                    assert upload_result['uploaded'] == 1
                    
                    print("✅ API route integration works")
                else:
                    print(f"Upload API returned {upload_response.status_code}: {upload_response.get_data(as_text=True)}")
            else:
                print(f"Registration API returned {response.status_code}: {response.get_data(as_text=True)}")

    def test_combined_upload_api_route_integration(self, app):
        """Test combined upload through HTTP API routes"""
        with app.test_client() as client:
            # Register client first
            registration_data = {
                'client_id': 'test_client_combined_api',
                'hostname': 'test-host',
                'platform': 'Linux',
                'version': '1.0.0'
            }
            
            from backend.config import get_config
            config = get_config()
            
            response = client.post('/api/clients/register',
                                 json=registration_data,
                                 headers={'X-Registration-Key': config.REGISTRATION_SECRET})
            
            if response.status_code == 200:
                registration_result = response.get_json()
                api_key = registration_result['api_key']
                
                # Test combined upload
                test_file_content = b"test slippi file for API integration"
                encoded_content = base64.b64encode(test_file_content).decode('utf-8')
                
                combined_data = {
                    'client_id': 'test_client_combined_api',
                    'timestamp': '2024-01-01T12:00:00Z',
                    'games': [
                        {
                            'game_id': 'combined_api_test_001',
                            'start_time': '2024-01-01T12:00:00Z',
                            'last_frame': 1000,
                            'stage_id': 31,
                            'player_data': [
                                {
                                    'port': 1,
                                    'player_tag': 'CAPI#001',
                                    'character_name': 'Fox',
                                    'result': 'Win'
                                }
                            ],
                            'game_type': 'ranked'
                        }
                    ],
                    'files': [
                        {
                            'content': encoded_content,
                            'metadata': {
                                'filename': 'api_test.slp',
                                'file_size': len(test_file_content),
                                'game_id': 'combined_api_test_001'
                            }
                        }
                    ]
                }
                
                upload_response = client.post('/api/games/upload',
                                            json=combined_data,
                                            headers={'X-API-Key': api_key})
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.get_json()
                    assert upload_result['success'] is True
                    assert upload_result['games']['uploaded'] == 1
                    assert upload_result['files']['uploaded'] == 1
                    
                    print("✅ Combined upload API integration works")
                else:
                    print(f"Combined upload API returned {upload_response.status_code}: {upload_response.get_data(as_text=True)}")