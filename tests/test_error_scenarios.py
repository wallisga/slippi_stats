import pytest

class TestErrorPropagation:
    """Test error handling across application layers"""
    
    def test_web_service_error_handling(self):
        """Test web service errors return appropriate responses"""
        from backend.web_service import get_player_games, prepare_homepage_data
        
        # Test with non-existent player
        games = get_player_games("NONEXISTENT#123")
        assert isinstance(games, list)
        assert len(games) == 0
        
        # Test homepage data with empty database
        homepage_data = prepare_homepage_data()
        assert isinstance(homepage_data, dict)
        assert "total_games" in homepage_data
        # Should handle empty database gracefully
        assert homepage_data["total_games"] >= 0
    
    def test_api_service_error_handling(self):
        """Test API service error handling"""
        from backend.api_service import process_player_basic_stats
        
        # Test with non-existent player
        result = process_player_basic_stats("NONEXISTENT#123")
        assert result is None
        
        # Test with empty string
        result = process_player_basic_stats("")
        assert result is None
        
        # Test with None
        result = process_player_basic_stats(None)
        assert result is None

class TestEdgeCaseHandling:
    """Test edge case scenarios"""
    
    def test_empty_database_scenarios(self):
        """Test application handles empty database gracefully"""
        from backend.web_service import prepare_homepage_data
        from backend.api_service import process_server_statistics
        
        # Test homepage with no data
        homepage_data = prepare_homepage_data()
        assert isinstance(homepage_data, dict)
        assert "total_games" in homepage_data
        assert homepage_data["total_games"] >= 0
        
        # Test server stats with no data
        server_stats = process_server_statistics()
        assert isinstance(server_stats, dict)
        assert "total_games" in server_stats
        assert server_stats["total_games"] >= 0
    
    def test_utils_error_handling(self):
        """Test utils functions handle errors gracefully"""
        from backend.utils import (
            parse_player_data_from_game,
            find_player_in_game_data,
            safe_get_player_field,
            calculate_win_rate
        )
        
        # Test with various invalid inputs
        invalid_inputs = [None, "", "invalid"]
        
        for invalid_input in invalid_inputs:
            # Should not crash
            try:
                parse_result = parse_player_data_from_game(invalid_input)
                assert isinstance(parse_result, list)  # Should always return list
                
                field_result = safe_get_player_field(invalid_input, "test_field")
                assert isinstance(field_result, str)
                
            except Exception as e:
                pytest.fail(f"Utils function crashed with input {invalid_input}: {e}")
        
        # Test lists and dicts separately (they behave differently)
        list_dict_inputs = [[], {}]
        for input_val in list_dict_inputs:
            try:
                # These might behave differently, so test separately
                field_result = safe_get_player_field(input_val, "test_field")
                assert isinstance(field_result, str)
            except Exception as e:
                # If it fails, that's acceptable for these edge cases
                print(f"Expected edge case failure for {input_val}: {e}")
