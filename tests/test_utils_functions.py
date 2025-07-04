# tests/test_utils_functions.py
"""
Utils Function Tests - NEW FILE

Test utility functions for data processing, calculations, and file handling.
These tests are fast (no I/O) and focus on pure function behavior.
"""
import pytest

class TestUtilsDataProcessing:
    """Test data processing utility functions"""
    
    def test_calculate_win_rate_edge_cases(self):
        """Test win rate calculation handles edge cases safely"""
        from backend.utils import calculate_win_rate
        
        # Normal cases
        assert calculate_win_rate(5, 10) == 0.5
        assert calculate_win_rate(0, 10) == 0.0
        assert calculate_win_rate(10, 10) == 1.0
        
        # Edge cases - your function doesn't handle None, so test actual behavior
        assert calculate_win_rate(5, 0) == 0.0  # Division by zero safety
        
        # Test with different numbers
        assert calculate_win_rate(3, 7) == 3/7
        assert calculate_win_rate(1, 3) == 1/3
    
    def test_encode_decode_player_tag(self):
        """Test player tag encoding/decoding works correctly"""
        from backend.utils import encode_player_tag, decode_player_tag
        
        # Test basic encoding/decoding
        test_tag = "PLAYER#123"
        encoded = encode_player_tag(test_tag)
        decoded = decode_player_tag(encoded)
        assert decoded == test_tag
        
        # Test with special characters
        special_tag = "Player with spaces & symbols!"
        encoded_special = encode_player_tag(special_tag)
        decoded_special = decode_player_tag(encoded_special)
        assert decoded_special == special_tag
        
        # Test edge cases
        assert decode_player_tag("") == ""
        assert encode_player_tag("") == ""
    
    def test_safe_get_player_field(self):
        """Test safe player field extraction"""
        from backend.utils import safe_get_player_field
        
        # Test with valid data
        player_data = {"player_tag": "TEST#123", "character_name": "Fox"}
        assert safe_get_player_field(player_data, "player_tag") == "TEST#123"
        assert safe_get_player_field(player_data, "character_name") == "Fox"
        
        # Test with missing field
        assert safe_get_player_field(player_data, "missing_field") == "Unknown"
        assert safe_get_player_field(player_data, "missing_field", "Custom") == "Custom"
        
        # Test with None/empty data
        assert safe_get_player_field(None, "any_field") == "Unknown"
        assert safe_get_player_field({}, "any_field") == "Unknown"


class TestUtilsGameProcessing:
    """Test game processing utilities"""
    
    def test_parse_player_data_from_game(self):
        """Test parsing player data from game JSON"""
        from backend.utils import parse_player_data_from_game
        
        # Test with valid JSON string
        json_data = '[{"player_tag": "TEST#123", "character_name": "Fox"}]'
        result = parse_player_data_from_game(json_data)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["player_tag"] == "TEST#123"
        
        # Test with already parsed data
        parsed_data = [{"player_tag": "TEST#123", "character_name": "Fox"}]
        result = parse_player_data_from_game(parsed_data)
        assert result == parsed_data
        
        # Test with invalid JSON - should return empty list
        result = parse_player_data_from_game("invalid json")
        assert result == []  # Expect empty list, not None
        
        # Test with None - should return empty list
        result = parse_player_data_from_game(None)
        assert result == []  # Expect empty list, not None
    
    def test_process_raw_games_for_player(self):
        """Test processing raw games for specific player"""
        from backend.utils import process_raw_games_for_player
        
        # Test with empty games
        result = process_raw_games_for_player([], "TEST#123")
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Test with None - should return empty list
        result = process_raw_games_for_player(None, "TEST#123")
        assert isinstance(result, list)
        assert len(result) == 0