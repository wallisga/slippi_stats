"""Service Layer Package - UPDATED with Upload and Client Domains"""

# Import from existing services (backward compatibility)
from .api_service import *
from .web_service import *

# Import from new upload domain
from .upload import (
    process_combined_upload,
    upload_games_for_client,
    process_file_upload
)

# Import from new client domain
from .client import (
    register_client,
    authenticate_client,
    update_client_info,
    get_client_details,
    refresh_api_key
)

__all__ = [
    # Upload domain functions (MIGRATED)
    'process_combined_upload',
    'upload_games_for_client', 
    'process_file_upload',
    
    # Client domain functions (NEW)
    'register_client',
    'authenticate_client',
    'update_client_info', 
    'get_client_details',
    'refresh_api_key',
    
    # Existing API Service functions (keeping current exports)
    'process_detailed_player_data', 
    'process_player_basic_stats',
    
    # Existing Web Service functions  
    'prepare_homepage_data',
    'prepare_all_players_data',
    'process_player_profile_request',
    'process_player_detailed_request',
]