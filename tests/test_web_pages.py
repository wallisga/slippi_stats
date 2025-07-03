# tests/test_web_pages.py
"""
Test that your web pages render without crashing - simplified version.
"""
import pytest

class TestWebPages:
    """Test web page routes"""
    
    def test_homepage_renders(self, client):
        """Homepage should render successfully"""
        response = client.get('/')
        # Should not crash (200 or redirect, but not 500)
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            # Should contain HTML
            assert b'html' in response.data.lower() or b'<' in response.data
    
    def test_players_page_renders(self, client):
        """Players page should render successfully"""
        response = client.get('/players')
        # Should not crash
        assert response.status_code in [200, 302]
    
    def test_how_to_page_renders(self, client):
        """How-to page should render successfully"""
        response = client.get('/how-to')
        # Should not crash
        assert response.status_code in [200, 302]
    
    def test_nonexistent_page_returns_404(self, client):
        """Non-existent pages should return 404"""
        response = client.get('/this-page-does-not-exist')
        assert response.status_code == 404