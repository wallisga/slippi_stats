"""
Upload Domain Processing Logic

Core business logic operations for upload processing.
Handles games, files, client info, and side effects.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import List
from backend.config import get_config
from backend.db import connection, manager
from backend.services.api_service import register_or_update_client
from .schemas import CombinedUploadData, UploadGameData

# Configuration  
config = get_config()
logger = config.init_logging()

mgr = manager.SQLManager()


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
    
    # Process client info if provided (unchanged)
    if validated_data.client_info:
        results['client'] = _process_client_info(validated_data.client_info)
    
    # Process games using schemas
    if validated_data.games:
        results['games'] = _process_standardized_games(client_id, validated_data.games)
    
    # Process files if provided (unchanged for now)
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
        
        # Update client last active
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            update_query = mgr.get_query('clients', 'update_last_active')
            cursor.execute(update_query, (datetime.now().isoformat(), client_id))
            conn.commit()
        
        return {
            'uploaded_count': uploaded_count,
            'total_submitted': len(games_data),
            'status': 'success'
        }
    except Exception as e:
        logger.error(f"Error uploading games for client {client_id}: {str(e)}")
        return {'error': str(e)}

# NEW: Add the file upload logic from api_service.py
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
        existing = execute_query('files', 'select_by_hash', (file_hash,), fetch_one=True)
        
        if existing:
            return {
                'file_id': existing['file_id'],
                'status': 'duplicate',
                'message': 'File already exists'
            }
        
        # Store file metadata
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            query = mgr.get_query('files', 'insert_file')
            cursor.execute(query, (
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
                        json.dumps([p.to_dict() for p in game.players]),
                        json.dumps({
                            'game_id': game.game_id,
                            'start_time': game.start_time,
                            'stage_id': game.stage_id,
                            'stage_name': game.stage_name,
                            'game_length_frames': game.game_length_frames,
                            'game_length_seconds': game.game_length_seconds,
                            'game_type': game.game_type,
                            'player_data': [p.to_dict() for p in game.players],
                            'metadata': game.metadata
                        })
                    ))
                    
                    uploaded_count += 1
                    
                except Exception as e:
                    processing_errors.append(f"Game {game.game_id}: {str(e)}")
                    continue
            
            conn.commit()
        
        # Update client last activity
        _update_client_activity(client_id)
        
        return {
            'success': uploaded_count > 0,
            'games_processed': uploaded_count,
            'games_skipped': skipped_count,
            'total_submitted': len(games),
            'processing_errors': processing_errors
        }
        
    except Exception as e:
        logger.error(f"Error processing games for client {client_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'games_processed': 0,
            'games_skipped': 0,
            'total_submitted': len(games)
        }

def _process_client_info(client_info):
    """Process client information update."""
    try:
        return register_or_update_client(client_info)
    except Exception as e:
        logger.warning(f"Client info processing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def _process_files_data(client_id, files_data):
    """Process files data upload."""
    try:
        processed_files = []
        for file_data in files_data:
            processed_files.append({
                'filename': file_data.get('filename', 'unknown'),
                'status': 'processed'
            })
        
        return {
            'success': True,
            'files_processed': len(processed_files),
            'files': processed_files
        }
    except Exception as e:
        logger.warning(f"Files data processing failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def _update_client_activity(client_id):
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

def _has_successful_uploads(upload_results):
    """Check if any upload components were successful."""
    for component_result in upload_results.values():
        if isinstance(component_result, dict) and component_result.get('success', True):
            return True
    return False