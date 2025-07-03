# tests/test_service_layer.py
"""
Enhanced Service Layer Contract Tests

These tests focus on business logic contracts and function signatures.
They run fast (no database) and provide quick feedback during development.
"""
import pytest
import inspect

class TestServiceContracts:
    """Test that service layer functions maintain their contracts"""
    
    def test_api_service_player_stats_returns_none_for_no_data(self):
        """API service should return None when no player data exists"""
        import backend.api_service as api_service
        
        # Test with non-existent player
        result = api_service.process_player_basic_stats('NONEXISTENT#123')
        assert result is None
    
    def test_api_service_server_stats_structure(self):
        """Server stats should always return expected structure"""
        import backend.api_service as api_service
        
        result = api_service.process_server_statistics()
        assert isinstance(result, dict)
        assert 'total_clients' in result
        assert 'total_games' in result
        assert 'unique_players' in result
    
    def test_web_service_homepage_data_structure(self):
        """Homepage data should have consistent structure"""
        import backend.web_service as web_service
        
        result = web_service.prepare_homepage_data()
        assert isinstance(result, dict)
        # Should contain keys that your homepage template expects
        assert 'recent_games' in result
        assert 'total_games' in result

    def test_validate_api_key_basic(self):
        """Test API key validation returns expected types"""
        from backend.database import validate_api_key
        
        # Test invalid key
        result = validate_api_key("invalid_key")
        assert result is None
        
        # Test None input  
        result = validate_api_key(None)
        assert result is None

class TestUploadServiceContracts:
    """Fast contract tests for upload functions - no database needed"""
    
    def test_upload_functions_exist_and_callable(self):
        """Test upload functions exist and are callable"""
        from backend.api_service import (
            upload_games_for_client,
            process_combined_upload,
            register_or_update_client,
            process_file_upload
        )
        
        # Test functions exist and are callable
        assert callable(upload_games_for_client)
        assert callable(process_combined_upload)  
        assert callable(register_or_update_client)
        assert callable(process_file_upload)
    
    def test_upload_function_signatures(self):
        """Test upload functions have expected signatures"""
        from backend.api_service import (
            upload_games_for_client,
            process_combined_upload,
            register_or_update_client,
            process_file_upload
        )
        
        # Test function signatures match expectations
        upload_games_sig = inspect.signature(upload_games_for_client)
        assert len(upload_games_sig.parameters) == 2  # client_id, games_data
        
        process_combined_sig = inspect.signature(process_combined_upload)
        assert len(process_combined_sig.parameters) == 2  # client_id, upload_data
        
        register_client_sig = inspect.signature(register_or_update_client)
        assert len(register_client_sig.parameters) == 1  # client_data
        
        process_file_sig = inspect.signature(process_file_upload)
        assert len(process_file_sig.parameters) == 3  # client_id, file_data, metadata

    def test_file_upload_helper_functions(self):
        """Test file upload helper functions"""
        from backend.api_service import allowed_file, calculate_file_hash
        
        # Test allowed_file function
        assert allowed_file('test.slp') is True
        assert allowed_file('test.SLP') is True  # Case insensitive
        assert allowed_file('test.txt') is False
        assert allowed_file('test.exe') is False
        assert allowed_file('') is False
        
        # Test calculate_file_hash function
        test_content = b"test content for hashing"
        hash1 = calculate_file_hash(test_content)
        hash2 = calculate_file_hash(test_content)
        
        assert hash1 == hash2  # Same content = same hash
        assert len(hash1) == 64  # SHA-256 produces 64-char hex string
        assert isinstance(hash1, str)
        
        # Different content = different hash
        hash3 = calculate_file_hash(b"different content")
        assert hash1 != hash3

class TestUtilsServiceContracts:
    """Test utility function contracts"""
    
    def test_url_encoding_functions(self):
        """Test encode/decode player tags work correctly"""
        from backend.utils import encode_player_tag, decode_player_tag
        
        # Test basic encoding/decoding
        test_tag = "TEST#123"
        encoded = encode_player_tag(test_tag)
        decoded = decode_player_tag(encoded)
        assert decoded == test_tag
        
        # Test special characters
        special_tag = "Player with spaces & symbols!"
        encoded_special = encode_player_tag(special_tag)
        decoded_special = decode_player_tag(encoded_special)
        assert decoded_special == special_tag
        
        # Test empty string
        assert encode_player_tag("") == ""
        assert decode_player_tag("") == ""
        
        # Test None handling
        assert encode_player_tag(None) == ""
        assert decode_player_tag(None) == ""

    def test_game_data_processing_contracts(self):
        """Test core game processing utility contracts"""
        from backend.utils import (
            parse_player_data_from_game,
            find_player_in_game_data,
            safe_get_player_field,
            calculate_win_rate
        )
        
        # Test parse_player_data_from_game
        valid_json = '[{"player_tag": "TEST#123", "character_name": "Fox"}]'
        parsed = parse_player_data_from_game(valid_json)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]['player_tag'] == "TEST#123"
        
        # Test invalid JSON handling
        invalid_result = parse_player_data_from_game("invalid json")
        assert invalid_result == []
        
        # Test find_player_in_game_data
        players = [
            {"player_tag": "PLAYER1#123", "character_name": "Fox"},
            {"player_tag": "PLAYER2#456", "character_name": "Falco"}
        ]
        
        player, opponent = find_player_in_game_data(players, "PLAYER1#123")
        assert player['player_tag'] == "PLAYER1#123"
        assert opponent['player_tag'] == "PLAYER2#456"
        
        # Test not found
        player, opponent = find_player_in_game_data(players, "NOTFOUND#999")
        assert player is None
        assert opponent is None
        
        # Test safe_get_player_field
        test_player = {"player_tag": "TEST#123", "character_name": "Fox"}
        assert safe_get_player_field(test_player, "player_tag") == "TEST#123"
        assert safe_get_player_field(test_player, "nonexistent", "default") == "default"
        assert safe_get_player_field(None, "anything", "default") == "default"
        
        # Test calculate_win_rate
        assert calculate_win_rate(5, 10) == 0.5
        assert calculate_win_rate(0, 10) == 0.0
        assert calculate_win_rate(10, 10) == 1.0
        assert calculate_win_rate(5, 0) == 0.0  # Safety check

class TestWebServiceContracts:
    """Test web service function contracts"""
    
    def test_web_service_functions_callable(self):
        """Test web service functions are accessible"""
        import backend.web_service as web_service
        
        # Test key functions exist
        assert callable(web_service.prepare_homepage_data)
        assert callable(web_service.prepare_all_players_data)
        assert callable(web_service.process_player_profile_request)
        assert callable(web_service.process_player_detailed_request)
    
    def test_web_service_data_structures(self):
        """Test web service returns expected data structures"""
        import backend.web_service as web_service
        
        # Test homepage data structure
        homepage_data = web_service.prepare_homepage_data()
        assert isinstance(homepage_data, dict)
        required_keys = ['total_games', 'total_players', 'recent_games', 'top_players']
        for key in required_keys:
            assert key in homepage_data, f"Missing key in homepage data: {key}"
        
        # Test all players data structure
        players_data = web_service.prepare_all_players_data()
        assert isinstance(players_data, dict)
        assert 'players' in players_data
        assert isinstance(players_data['players'], list)

class TestConfigServiceContracts:
    """Test configuration service contracts"""
    
    def test_config_functions_work(self):
        """Test config functions are accessible and work"""
        from backend.config import get_config
        
        config = get_config()
        assert config is not None
        
        # Test key config methods exist
        assert hasattr(config, 'init_logging')
        assert hasattr(config, 'get_database_path')
        assert callable(config.init_logging)
        assert callable(config.get_database_path)
        
        # Test they return reasonable values
        db_path = config.get_database_path()
        assert isinstance(db_path, str)
        assert len(db_path) > 0

class TestDatabaseServiceContracts:
    """Test database service function contracts"""
    
    def test_database_functions_callable(self):
        """Test database functions are accessible"""
        from backend.database import (
            validate_api_key,
            get_database_stats,
            check_client_exists,
            check_game_exists
        )
        
        # Test functions exist and are callable
        assert callable(validate_api_key)
        assert callable(get_database_stats)
        assert callable(check_client_exists)
        assert callable(check_game_exists)
    
    def test_database_stats_structure(self):
        """Test database stats returns expected structure"""
        from backend.database import get_database_stats
        
        stats = get_database_stats()
        assert isinstance(stats, dict)
        
        expected_keys = ['total_clients', 'total_games', 'unique_players']
        for key in expected_keys:
            assert key in stats, f"Missing key in database stats: {key}"
            assert isinstance(stats[key], int), f"Key {key} should be an integer"

class TestSQLManagerContracts:
    """Test SQL manager function contracts"""
    
    def test_sql_manager_functions(self):
        """Test SQL manager functions work"""
        from backend.sql_manager import sql_manager
        
        # Test core functions exist
        assert hasattr(sql_manager, 'get_query')
        assert hasattr(sql_manager, 'has_query')
        assert hasattr(sql_manager, 'format_query')
        assert callable(sql_manager.get_query)
        assert callable(sql_manager.has_query)
        assert callable(sql_manager.format_query)
        
        # Test they return expected types
        categories = sql_manager.get_categories()
        assert isinstance(categories, list)
        
        # Test has_query returns boolean
        result = sql_manager.has_query('nonexistent_category', 'nonexistent_query')
        assert isinstance(result, bool)
        assert result is False

# =============================================================================
# Business Logic Integration Tests (Lightweight)
# =============================================================================

class TestServiceIntegration:
    """Test service layer integration without heavy database operations"""
    
    def test_error_template_data_generation(self):
        """Test error template data generation works"""
        from backend.utils import get_error_template_data
        
        # Test 404 error
        error_data = get_error_template_data(404, "Page not found")
        assert isinstance(error_data, dict)
        assert error_data['status_code'] == 404
        assert 'error_description' in error_data
        assert 'error_title' in error_data
        assert 'error_icon' in error_data
        
        # Test 500 error
        error_data_500 = get_error_template_data(500, "Server error")
        assert error_data_500['status_code'] == 500
        assert error_data_500['error_type'] == 'danger'

    def test_service_layer_error_handling(self):
        """Test service layer functions handle errors gracefully"""
        import backend.api_service as api_service
        
        # Test functions don't crash with invalid input
        try:
            # These should return None or empty results, not crash
            result1 = api_service.process_player_basic_stats("")
            result2 = api_service.process_player_basic_stats(None)
            result3 = api_service.process_server_statistics()
            
            # Should not raise exceptions
            assert result1 is None or isinstance(result1, dict)
            assert result2 is None or isinstance(result2, dict)
            assert isinstance(result3, dict)
            
        except Exception as e:
            pytest.fail(f"Service layer should handle invalid input gracefully: {e}")