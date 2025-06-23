"""
Shared utilities for Slippi Server.

This module contains helper functions used across multiple modules.
Only includes functions that are actually being used in the codebase.
"""

import urllib.parse

# =============================================================================
# URL Encoding Utilities
# =============================================================================

def encode_player_tag(tag):
    """
    URL-encode a player tag for safe use in URLs.
    
    Args:
        tag (str): Raw player tag
        
    Returns:
        str: URL-encoded player tag
    """
    if not tag:
        return ""
    return urllib.parse.quote(tag)

def decode_player_tag(encoded_tag):
    """
    Decode a URL-encoded player tag back to original form.
    
    Args:
        encoded_tag (str): URL-encoded player tag
        
    Returns:
        str: Decoded player tag
    """
    if not encoded_tag:
        return ""
    return urllib.parse.unquote(encoded_tag)

# =============================================================================
# Error Template Data Utilities
# =============================================================================

def get_error_template_data(status_code, error_description, **kwargs):
    """Generate standardized template data for error pages."""
    error_info = {
        400: {'title': 'Bad Request', 'icon': 'bi-exclamation-triangle', 'type': 'warning'},
        401: {'title': 'Unauthorized', 'icon': 'bi-shield-x', 'type': 'danger'},
        403: {'title': 'Forbidden', 'icon': 'bi-shield-exclamation', 'type': 'danger'},
        404: {'title': 'Page Not Found', 'icon': 'bi-question-circle', 'type': 'info'},
        429: {'title': 'Too Many Requests', 'icon': 'bi-clock', 'type': 'warning'},
        500: {'title': 'Server Error', 'icon': 'bi-exclamation-octagon', 'type': 'danger'}
    }
    
    error_meta = error_info.get(status_code, {'title': 'Unknown Error', 'icon': 'bi-exclamation-circle', 'type': 'secondary'})
    
    base_data = {
        'layout_type': 'error', 'has_player_search': False, 'navbar_context': 'error',
        'status_code': status_code, 'error_description': error_description,
        'error_title': error_meta['title'], 'error_icon': error_meta['icon'],
        'error_type': error_meta['type'], 'show_home_link': True,
        'show_back_link': status_code == 404
    }
    base_data.update(kwargs)
    return base_data