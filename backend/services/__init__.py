# backend/services/__init__.py
"""
Service Layer Package

Business logic services implementing the orchestrator pattern for
maintainable, testable code.
"""

# Import main services for backward compatibility
from .api_service import *
from .web_service import *

__all__ = [
    # API Service functions
    'process_combined_upload',
    'process_detailed_player_data', 
    'process_player_basic_stats',
    'register_or_update_client',
    'upload_games_for_client',
    
    # Web Service functions  
    'prepare_homepage_data',
    'prepare_all_players_data',
    'process_player_profile_request',
    'process_player_detailed_request',
]