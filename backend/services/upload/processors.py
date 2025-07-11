"""
Upload Domain Processing Logic

FIXED: Complete file with architecture-compliant schema construction helpers.
Core business logic operations for upload processing.
Handles games, files, client info, and side effects.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import get_config
from backend.db import execute_query
from .schemas import (
    CombinedUploadData, UploadGameData, PlayerUploadData, 
    GameResult, UploadValidationError
)

# Configuration  
config = get_config()
logger = config.init_logging()

# ============================================================================
# Schema Construction Helpers (Database-Related Logic)
# ============================================================================

def create_player_upload_from_raw_data(raw_player: Dict[str, Any]) -> PlayerUploadData:
    """
    Create PlayerUploadData from raw upload data.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    player_tag = raw_player.get('player_tag', '')
    character_name = raw_player.get('character_name', 'Unknown')
    placement = int(raw_player.get('placement', 0))
    
    # Determine result from multiple possible fields
    result = GameResult.NO_CONTEST
    if 'result' in raw_player:
        result = GameResult.from_string(raw_player['result'])
    elif placement > 0:
        result = GameResult.from_placement(placement)
    
    return PlayerUploadData(
        player_tag=player_tag,
        character_name=character_name,
        placement=placement,
        result=result,
        raw_data=raw_player
    )

def create_upload_game_from_raw_data(raw_game: Dict[str, Any], client_id: str) -> UploadGameData:
    """
    Create UploadGameData from raw upload data.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    # Generate game ID if not provided
    game_id = raw_game.get('game_id', str(uuid.uuid4()))
    
    # Extract basic fields
    stage_id = int(raw_game.get('stage_id', 0))
    start_time = raw_game.get('start_time', datetime.now().isoformat())
    game_length_frames = int(raw_game.get('game_length_frames', 0))
    
    # Process player data
    player_data = []
    for raw_player in raw_game.get('player_data', []):
        player = create_player_upload_from_raw_data(raw_player)
        player_data.append(player)
    
    # Compute derived fields
    stage_name = _get_stage_name(stage_id)
    game_length_seconds = game_length_frames / 60.0 if game_length_frames > 0 else 0.0
    
    return UploadGameData(
        game_id=game_id,
        client_id=client_id,
        stage_id=stage_id,
        start_time=start_time,
        game_length_frames=game_length_frames,
        player_data=player_data,
        stage_name=stage_name,
        game_length_seconds=game_length_seconds,
        raw_data=raw_game
    )

def create_combined_upload_from_request(client_id: str, raw_upload: Dict[str, Any]) -> CombinedUploadData:
    """
    Create CombinedUploadData from raw upload request.
    
    FIXED: This database-related construction belongs in processors, not schemas.
    """
    games = []
    for raw_game in raw_upload.get('games', []):
        try:
            game_data = create_upload_game_from_raw_data(raw_game, client_id)
            games.append(game_data)
        except Exception as e:
            logger.warning(f"Skipping invalid game data: {str(e)}")
    
    return CombinedUploadData(
        client_id=client_id,
        client_info=raw_upload.get('client_info'),
        games=games,
        files=raw_upload.get('files', []),
        metadata=raw_upload.get('metadata', {})
    )

def _get_stage_name(stage_id: int) -> Optional[str]:
    """
    Get stage name from stage ID.
    
    Helper function for computed fields in upload data.
    """
    stage_names = {
        2: "Fountain of Dreams",
        3: "Pokemon Stadium",
        8: "Yoshi's Story",
        28: "Dream Land N64",
        31: "Battlefield",
        32: "Final Destination"
    }
    return stage_names.get(stage_id, f"Unknown Stage ({stage_id})")

# ============================================================================
# Main Processing Functions
# ============================================================================

def process_upload_components(client_id: str, validated_data: CombinedUploadData) -> Dict[str, Any]:
    """
    Process upload components using standardized schemas.
    
    Args:
        client_id: Client identifier
        validated_data: Standardized upload data
    
    Returns:
        dict: Processing results
    """
    results = {}
    
    # Process client info if provided
    if validated_data.client_info:
        results['client'] = _process_client_info(validated_data.client_info)
    
    # Process games using schemas
    if validated_data.games:
        results['games'] = _process_standardized_games(client_id, validated_data.games)
    
    # Process files if provided
    if validated_data.files:
        results['files'] = _process_files_data(client_id, validated_data.files)
    
    return results

def process_games_upload(client_id: str, games_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process games upload with improved error handling.
    
    Args:
        client_id: Client identifier
        games_data: List of game data to upload
    
    Returns:
        dict: Upload results with counts and status
    """
    if not client_id or not games_data:
        return {'error': 'Invalid client_id or games_data'}
    
    try:
        uploaded_count = 0
        duplicate_count = 0
        error_count = 0
        processed_games = []
        
        for game_data in games_data:
            try:
                # Generate game ID if not provided
                game_id = game_data.get('game_id', str(uuid.uuid4()))
                
                # Check if game exists
                existing_game = execute_query('games', 'check_exists', (game_id,), fetch_one=True)
                
                if existing_game:
                    logger.info(f"Game {game_id} already exists, skipping")
                    duplicate_count += 1
                    continue
                
                # Insert new game using execute_query
                execute_query('games', 'insert_game', (
                    game_id,
                    client_id,
                    game_data.get('start_time', datetime.now().isoformat()),
                    game_data.get('last_frame', 0),
                    game_data.get('stage_id', 0),
                    json.dumps(game_data.get('player_data', [])),
                    datetime.now().isoformat(),  # upload_date
                    game_data.get('game_type', 'unknown')
                ))
                
                uploaded_count += 1
                processed_games.append({
                    'game_id': game_id,
                    'status': 'uploaded'
                })
                
            except Exception as e:
                logger.error(f"Error processing game {game_data.get('game_id', 'unknown')}: {str(e)}")
                error_count += 1
                processed_games.append({
                    'game_id': game_data.get('game_id', 'unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'uploaded': uploaded_count,
            'duplicates': duplicate_count,
            'errors': error_count,
            'total': len(games_data),
            'processed_games': processed_games,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error in games upload for client {client_id}: {str(e)}")
        return {'error': str(e), 'success': False}

def process_file_upload_logic(client_id: str, file_info: Dict[str, Any], file_content: bytes) -> Dict[str, Any]:
    """
    Process individual file upload with metadata.
    
    Args:
        client_id: Client identifier
        file_info: File metadata
        file_content: File content
    
    Returns:
        dict: File upload result
    """
    try:
        file_id = str(uuid.uuid4())
        file_hash = file_info.get('hash', 'unknown')
        filename = file_info.get('filename', 'unknown')
        
        # Check if file with same hash already exists
        existing_file = execute_query('files', 'select_by_hash', (file_hash,), fetch_one=True)
        
        if existing_file:
            return {
                'file_id': existing_file['file_id'],
                'status': 'duplicate',
                'message': 'File already exists'
            }
        
        # Store file metadata
        execute_query('files', 'insert_file', (
            file_id,
            file_hash,
            client_id,
            filename,
            f"/uploads/{client_id}/{file_id}",  # file_path
            len(file_content),  # file_size
            datetime.now().isoformat(),  # upload_date
            json.dumps(file_info)  # metadata
        ))
        
        return {
            'file_id': file_id,
            'status': 'uploaded',
            'size': len(file_content),
            'filename': filename
        }
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return {'error': str(e), 'status': 'error'}

def handle_upload_side_effects(client_id: str, upload_results: Dict[str, Any]) -> None:
    """
    Handle side effects like activity tracking and notifications.
    
    Args:
        client_id: Client identifier
        upload_results: Results from upload processing
    """
    try:
        # Update client last activity if any processing was successful
        if _has_successful_uploads(upload_results):
            _update_client_activity(client_id)
        
        # Could add other side effects like:
        # - Analytics tracking
        # - Notification sending  
        # - Background processing triggers
        
    except Exception as e:
        # Side effects shouldn't fail the main upload
        logger.warning(f"Upload side effects failed for client {client_id}: {str(e)}")

# ============================================================================
# Helper Functions - Private Implementation Details
# ============================================================================

def _process_standardized_games(client_id: str, games: List[UploadGameData]) -> Dict[str, Any]:
    """
    Process standardized game data.
    
    Args:
        client_id: Client identifier
        games: List of standardized game data
    
    Returns:
        dict: Processing results
    """
    try:
        uploaded_count = 0
        duplicate_count = 0
        error_count = 0
        processed_games = []
        
        for game in games:
            try:
                # Check if game exists
                existing_game = execute_query('games', 'check_exists', (game.game_id,), fetch_one=True)
                
                if existing_game:
                    duplicate_count += 1
                    processed_games.append({
                        'game_id': game.game_id,
                        'status': 'duplicate'
                    })
                    continue
                
                # Insert new game
                execute_query('games', 'insert_game', (
                    game.game_id,
                    game.client_id,
                    game.start_time,
                    game.game_length_frames,
                    game.stage_id,
                    json.dumps([player.to_dict() for player in game.player_data]),
                    datetime.now().isoformat(),  # upload_date
                    'standard'  # game_type
                ))
                
                uploaded_count += 1
                processed_games.append({
                    'game_id': game.game_id,
                    'status': 'uploaded',
                    'stage_name': game.stage_name,
                    'player_count': len(game.player_data)
                })
                
            except Exception as e:
                logger.error(f"Error processing standardized game {game.game_id}: {str(e)}")
                error_count += 1
                processed_games.append({
                    'game_id': game.game_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'uploaded_count': uploaded_count,
            'duplicate_count': duplicate_count,
            'error_count': error_count,
            'total_submitted': len(games),
            'processed_games': processed_games,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error processing standardized games for {client_id}: {str(e)}")
        return {'error': str(e), 'status': 'error'}

def _process_client_info(client_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process client info updates.
    
    Args:
        client_info: Client information to update
    
    Returns:
        dict: Processing result
    """
    try:
        # For now, just acknowledge receipt - could extend to update client records
        return {
            'status': 'acknowledged',
            'client_info_received': bool(client_info)
        }
        
    except Exception as e:
        logger.error(f"Error processing client info: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def _process_files_data(client_id: str, files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process files data.
    
    Args:
        client_id: Client identifier
        files_data: List of file data to process
    
    Returns:
        dict: Processing results
    """
    try:
        uploaded_count = 0
        duplicate_count = 0
        error_count = 0
        file_results = []
        
        for file_data in files_data:
            try:
                # Extract file content if present
                file_content = file_data.get('content', b'')
                if isinstance(file_content, str):
                    # Handle base64 encoded content
                    import base64
                    file_content = base64.b64decode(file_content)
                
                file_info = {
                    'filename': file_data.get('filename', 'unknown'),
                    'hash': file_data.get('hash', 'unknown'),
                    'metadata': file_data.get('metadata', {})
                }
                
                result = process_file_upload_logic(client_id, file_info, file_content)
                file_results.append(result)
                
                if result.get('status') == 'uploaded':
                    uploaded_count += 1
                elif result.get('status') == 'duplicate':
                    duplicate_count += 1
                elif result.get('status') == 'error':
                    error_count += 1
                    
            except Exception as e:
                logger.warning(f"Error processing file: {str(e)}")
                error_count += 1
                file_results.append({'error': str(e), 'status': 'error'})
        
        return {
            'uploaded_count': uploaded_count,
            'duplicate_count': duplicate_count,
            'error_count': error_count,
            'total_submitted': len(files_data),
            'file_results': file_results,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error processing files for {client_id}: {str(e)}")
        return {'error': str(e), 'status': 'error'}

def _update_client_activity(client_id: str) -> None:
    """Update client last activity timestamp."""
    try:
        execute_query('clients', 'update_last_active', (
            datetime.now().isoformat(),
            client_id
        ))
        logger.debug(f"Updated activity for client {client_id}")
        
    except Exception as e:
        logger.warning(f"Failed to update activity for client {client_id}: {str(e)}")

def _has_successful_uploads(upload_results: Dict[str, Any]) -> bool:
    """Check if any uploads were successful."""
    for component_result in upload_results.values():
        if isinstance(component_result, dict):
            if component_result.get('uploaded_count', 0) > 0:
                return True
            if component_result.get('uploaded', 0) > 0:
                return True
    return False