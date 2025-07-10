"""
Upload Domain Processing Logic

Core business logic operations for upload processing.
Handles games, files, client info, and side effects.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.config import get_config
from backend.db import connection, manager
from .schemas import CombinedUploadData, UploadGameData

# Configuration  
config = get_config()
logger = config.init_logging()

mgr = manager.SQLManager()

# ============================================================================
# Main Processing Functions
# ============================================================================

def process_upload_components(client_id, validated_data):
    """
    Process upload components using standardized schemas.
    
    Args:
        client_id (str): Client identifier
        validated_data (CombinedUploadData): Standardized upload data
    
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

def process_games_upload(client_id, games_data):
    """
    Process games upload - moved from api_service.py
    
    Args:
        client_id (str): Client identifier
        games_data (list): List of game data to upload
    
    Returns:
        dict: Upload results
    """
    if not client_id or not games_data:
        return {'error': 'Invalid client_id or games_data'}
    
    try:
        uploaded_count = 0
        skipped_count = 0
        
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            
            for game_data in games_data:
                try:
                    # Generate game ID if not provided
                    game_id = game_data.get('game_id', str(uuid.uuid4()))
                    
                    # Check if game exists
                    existing_query = mgr.get_query('games', 'check_exists')
                    cursor.execute(existing_query, (game_id,))
                    
                    if cursor.fetchone():
                        skipped_count += 1
                        continue  # Skip duplicate
                    
                    # Insert new game
                    insert_query = mgr.get_query('games', 'insert_game')
                    cursor.execute(insert_query, (
                        game_id,
                        client_id,
                        game_data.get('start_time', datetime.now().isoformat()),
                        game_data.get('stage_id', 0),
                        game_data.get('game_length_frames', 0),
                        json.dumps(game_data.get('player_data', [])),
                        json.dumps(game_data)  # full_data
                    ))
                    
                    uploaded_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing individual game: {str(e)}")
                    continue
            
            conn.commit()
        
        return {
            'uploaded_count': uploaded_count,
            'skipped_count': skipped_count,
            'total_submitted': len(games_data),
            'status': 'success'
        }
    except Exception as e:
        logger.error(f"Error uploading games for client {client_id}: {str(e)}")
        return {'error': str(e)}

def process_file_upload_logic(client_id, file_info, file_content):
    """
    Process file upload logic - moved from api_service.py
    
    Args:
        client_id (str): Client identifier
        file_info (dict): File metadata
        file_content (bytes): File content
    
    Returns:
        dict: File upload result
    """
    try:
        file_id = str(uuid.uuid4())
        file_hash = file_info.get('hash', 'unknown')
        filename = file_info.get('filename', 'unknown')
        
        # Check if file with same hash already exists
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            check_query = mgr.get_query('files', 'select_by_hash')
            cursor.execute(check_query, (file_hash,))
            existing = cursor.fetchone()
            
            if existing:
                return {
                    'file_id': existing['file_id'],
                    'status': 'duplicate',
                    'message': 'File already exists'
                }
            
            # Store file metadata
            insert_query = mgr.get_query('files', 'insert_file')
            cursor.execute(insert_query, (
                file_id,
                client_id,
                filename,
                len(file_content),
                file_hash,
                datetime.now().isoformat()
            ))
            conn.commit()
        
        return {
            'file_id': file_id,
            'status': 'uploaded',
            'size': len(file_content)
        }
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return {'error': str(e)}

def handle_upload_side_effects(client_id, upload_results):
    """
    Handle side effects like activity tracking and notifications.
    
    Args:
        client_id (str): Client identifier
        upload_results (dict): Results from upload processing
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

def _process_standardized_games(client_id: str, games: List[UploadGameData]) -> dict:
    """
    Process standardized game data.
    
    Args:
        client_id (str): Client identifier
        games (List[UploadGameData]): Validated and standardized games
    
    Returns:
        dict: Processing results
    """
    try:
        uploaded_count = 0
        skipped_count = 0
        processing_errors = []
        
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            
            for game in games:
                try:
                    # Check if game already exists
                    existing_query = mgr.get_query('games', 'check_exists')
                    cursor.execute(existing_query, (game.game_id,))
                    
                    if cursor.fetchone():
                        skipped_count += 1
                        continue  # Skip duplicate
                    
                    # Insert with standardized format (compatible with existing schema)
                    insert_query = mgr.get_query('games', 'insert_game')
                    cursor.execute(insert_query, (
                        game.game_id,
                        game.client_id,
                        game.start_time,
                        game.stage_id,
                        game.game_length_frames,
                        json.dumps([player.to_dict() for player in game.player_data]),
                        json.dumps(game.to_dict())  # full_data with all standardized fields
                    ))
                    
                    uploaded_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing game {game.game_id}: {str(e)}")
                    processing_errors.append(str(e))
                    continue
            
            conn.commit()
        
        return {
            'uploaded_count': uploaded_count,
            'skipped_count': skipped_count,
            'total_submitted': len(games),
            'processing_errors': processing_errors,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error processing standardized games for {client_id}: {str(e)}")
        return {'error': str(e)}

def _process_client_info(client_info: Dict[str, Any]) -> dict:
    """
    Process client information updates.
    
    Args:
        client_info (dict): Client information to update
    
    Returns:
        dict: Processing result
    """
    try:
        # Import register_or_update_client from api_service
        from backend.services.api_service import register_or_update_client
        
        result = register_or_update_client(client_info)
        return {
            'status': 'processed',
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error processing client info: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def _process_files_data(client_id: str, files_data: List[Dict[str, Any]]) -> dict:
    """
    Process files data.
    
    Args:
        client_id (str): Client identifier
        files_data (list): List of file data to process
    
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
                # Extract file content if present (this is simplified)
                file_content = file_data.get('content', b'')
                file_info = {
                    'filename': file_data.get('filename', 'unknown'),
                    'hash': file_data.get('hash', 'unknown')
                }
                
                result = process_file_upload_logic(client_id, file_info, file_content)
                file_results.append(result)
                
                if result.get('status') == 'uploaded':
                    uploaded_count += 1
                elif result.get('status') == 'duplicate':
                    duplicate_count += 1
                elif 'error' in result:
                    error_count += 1
                    
            except Exception as e:
                logger.warning(f"Error processing file: {str(e)}")
                error_count += 1
                file_results.append({'error': str(e)})
        
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
        return {'error': str(e)}

def _update_client_activity(client_id: str):
    """Update client last activity timestamp."""
    try:
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            update_query = mgr.get_query('clients', 'update_last_active')
            cursor.execute(update_query, (datetime.now().isoformat(), client_id))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to update client activity for {client_id}: {str(e)}")
        raise

def _has_successful_uploads(upload_results: Dict[str, Any]) -> bool:
    """Check if any upload components were successful."""
    for component_result in upload_results.values():
        if isinstance(component_result, dict):
            # Check for successful uploads in the result
            if (component_result.get('uploaded_count', 0) > 0 or 
                component_result.get('status') == 'success' or
                component_result.get('status') == 'processed'):
                return True
    return False