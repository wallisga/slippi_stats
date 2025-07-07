"""Service Layer Package - UPDATED with Upload Domain"""

# Import from existing services (backward compatibility)
from .api_service import *
from .web_service import *

# Import from new upload domain
from .upload import (
    process_combined_upload,
    upload_games_for_client,
    process_file_upload
)

__all__ = [
    # Upload domain functions (NEW)
    'process_combined_upload',
    'upload_games_for_client', 
    'process_file_upload',
    
    # Existing API Service functions (keeping current exports)
    'process_detailed_player_data', 
    'process_player_basic_stats',
    'register_or_update_client',
    
    # Existing Web Service functions  
    'prepare_homepage_data',
    'prepare_all_players_data',
    'process_player_profile_request',
    'process_player_detailed_request',
]