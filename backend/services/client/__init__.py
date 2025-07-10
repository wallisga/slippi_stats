"""
Client Service Domain

Handles all client-related business logic including registration,
authentication, API key management, and client information.
"""

# Import main orchestrators
from .service import (
    register_client,
    authenticate_client,
    update_client_info,
    get_client_details,
    refresh_api_key
)

# Export public API - only these functions should be imported by other modules
__all__ = [
    'register_client',
    'authenticate_client', 
    'update_client_info',
    'get_client_details',
    'refresh_api_key'
]