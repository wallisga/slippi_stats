"""
Upload Domain Validation Logic

Input validation and business rules for upload operations.
Contains all validation functions and business rule enforcement.
"""

import logging
from typing import Dict, Any
from .schemas import CombinedUploadData, UploadValidationError

logger = logging.getLogger(__name__)

def validate_combined_upload_data(client_id: str, upload_data: Dict[str, Any]) -> CombinedUploadData:
    """
    Validate complete upload payload and return standardized data.
    
    Args:
        client_id: Client identifier
        upload_data: Raw upload data from request
    
    Returns:
        CombinedUploadData: Validated and standardized upload data
        
    Raises:
        UploadValidationError: If validation fails
    """
    # Validate client ID
    if not client_id or not isinstance(client_id, str) or len(client_id.strip()) == 0:
        raise UploadValidationError("Valid client_id is required")
    
    # Validate upload data structure
    if not upload_data or not isinstance(upload_data, dict):
        raise UploadValidationError("Upload data must be a non-empty dictionary")
    
    # Use business rule validation
    try:
        validate_combined_upload_business_rules(upload_data)
    except UploadValidationError as e:
        raise UploadValidationError(f"Upload validation failed: {str(e)}")
    
    # Convert to standardized format
    try:
        combined_upload = CombinedUploadData.from_upload_request(client_id, upload_data)
    except Exception as e:
        raise UploadValidationError(f"Failed to process upload data: {str(e)}")
    
    return combined_upload

def validate_combined_upload_business_rules(raw_upload: Dict[str, Any]) -> None:
    """Validate business rules for combined upload."""
    if not isinstance(raw_upload, dict):
        raise UploadValidationError("Upload data must be a dictionary")
    
    # Validate games if present
    games = raw_upload.get('games', [])
    if games:
        if not isinstance(games, list):
            raise UploadValidationError("Games must be a list")
        
        for i, game in enumerate(games):
            try:
                validate_game_business_rules(game)
            except UploadValidationError as e:
                raise UploadValidationError(f"Game {i}: {str(e)}")
    
    # Ensure at least one type of data is provided
    has_client_info = bool(raw_upload.get('client_info'))
    has_games = bool(games)
    has_files = bool(raw_upload.get('files'))
    
    if not any([has_client_info, has_games, has_files]):
        raise UploadValidationError("Upload must contain at least client_info, games, or files")

def validate_game_business_rules(raw_game: Dict[str, Any]) -> None:
    """Validate business rules for individual game."""
    if not isinstance(raw_game, dict):
        raise UploadValidationError("Game data must be a dictionary")
    
    # Validate required fields
    stage_id = raw_game.get('stage_id')
    if stage_id is None:
        raise UploadValidationError("Stage ID is required")
    
    try:
        int(stage_id)
    except (ValueError, TypeError):
        raise UploadValidationError("Stage ID must be a number")
    
    # Validate player data
    player_data = raw_game.get('player_data', [])
    if not isinstance(player_data, list):
        raise UploadValidationError("Player data must be a list")
    
    if len(player_data) < 2:
        raise UploadValidationError("Game must have at least 2 players")
    
    if len(player_data) > 4:
        raise UploadValidationError("Game cannot have more than 4 players")
    
    for i, player in enumerate(player_data):
        try:
            validate_player_business_rules(player)
        except UploadValidationError as e:
            raise UploadValidationError(f"Player {i}: {str(e)}")

def validate_player_business_rules(raw_player: Dict[str, Any]) -> None:
    """Validate business rules for individual player."""
    if not isinstance(raw_player, dict):
        raise UploadValidationError("Player data must be a dictionary")
    
    player_tag = raw_player.get('player_tag')
    if not player_tag or not isinstance(player_tag, str) or not player_tag.strip():
        raise UploadValidationError("Player tag is required and must be non-empty string")
    
    character_name = raw_player.get('character_name')
    if not character_name or not isinstance(character_name, str):
        raise UploadValidationError("Character name is required and must be a string")