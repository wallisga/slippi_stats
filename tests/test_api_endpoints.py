# tests/test_api_endpoints.py
"""
Test your actual API endpoints - simplified version that works.
"""
import pytest
import json

class TestServerEndpoints:
    """Test basic server endpoints that don't require complex setup"""
    
    def test_server_stats_endpoint(self, client):
        """Server stats should always return valid structure"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = response.get_json()
        # Your process_server_statistics should return these
        expected_keys = ['total_clients', 'total_games', 'unique_players']
        for key in expected_keys:
            assert key in data, f"Server stats missing key: {key}"

class TestPlayerEndpoints:
    """Test player endpoints with simple cases"""
    
    def test_player_stats_404_for_nonexistent_player(self, client):
        """Player stats should return 404 for non-existent player"""
        response = client.get('/api/player/FAKE%23123/stats')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()

class TestUploadEndpoints:
    """Test upload endpoints basic behavior"""
    
    def test_games_upload_requires_api_key(self, client):
        """Upload should require valid API key"""
        upload_data = {
            'client_id': 'test_client',
            'games': []
        }
        
        response = client.post('/api/games/upload', 
                             json=upload_data)
        assert response.status_code == 401