"""
Upload Service Domain

Handles all upload-related business logic including combined uploads,
game data processing, file uploads, and client management.
"""

# Import main orchestrators
from .service import (
    process_combined_upload,
    upload_games_for_client,
    process_file_upload,
)

# Export public API - only these functions should be imported by other modules
__all__ = [
    'process_combined_upload',
    'upload_games_for_client', 
    'process_file_upload',
]