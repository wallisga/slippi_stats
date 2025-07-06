# Refactored api_service.py - Single Combined Upload Approach

import os
import hashlib
import json
import base64
from datetime import datetime
from backend.config import get_config
from backend.database import (
    create_file_record, get_file_by_hash, create_game_record, 
    check_game_exists, update_clients_last_active
)

# Get configuration and logger
config = get_config()
logger = config.init_logging()

# File upload settings
ALLOWED_EXTENSIONS = {'.slp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

# ============================================================================
# Public API - Single Combined Upload Function
# ============================================================================

def process_combined_upload(client_id, upload_data):
    """
    Process combined games and files upload.
    
    This is the main upload function that handles both games and files
    in a single request, matching your client implementation.
    
    Args:
        client_id (str): Client ID from API key validation
        upload_data (dict): Contains both games data and file information
    
    Returns:
        dict: Combined upload result with games and files statistics
    """
    try:
        games_data = upload_data.get('games', [])
        files_data = upload_data.get('files', [])
        
        logger.info(f"Processing combined upload for {client_id}: "
                   f"{len(games_data)} games, {len(files_data)} files")
        
        # Process games and files
        games_result = _process_games_data(client_id, games_data)
        files_result = _process_files_data(client_id, files_data)
        
        # Update client activity
        update_clients_last_active(client_id)
        
        return _create_combined_response(games_result, files_result)
        
    except Exception as e:
        logger.error(f"Error processing combined upload: {str(e)}")
        raise

def process_detailed_player_data(player_code, filters=None):
    """
    Process detailed player data with filtering.
    
    Args:
        player_code (str): Player tag/code
        filters (dict): Optional filters for character, opponent, etc.
    
    Returns:
        dict: Detailed player data with applied filters
    """
    try:
        logger.info(f"Processing detailed player data for: {player_code}")
        if filters:
            logger.info(f"Applying filters: {filters}")
        
        # Get all games for the player
        from backend.database import get_player_games
        games = get_player_games(player_code)
        
        if not games:
            return {
                'success': False,
                'error': 'No games found for player',
                'player_code': player_code
            }
        
        # Apply filters if provided
        if filters:
            games = apply_game_filters(games, filters)
        
        # Process the filtered games data
        from backend.utils import process_raw_games_for_player
        processed_data = process_raw_games_for_player(games, player_code)
        
        return {
            'success': True,
            'player_code': player_code,
            'filters_applied': filters or {},
            'total_games': len(games),
            'data': processed_data
        }
        
    except Exception as e:
        logger.error(f"Error processing detailed player data for {player_code}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'player_code': player_code
        }

def apply_game_filters(games, filters):
    """
    Apply character and opponent filters to games list.
    
    Args:
        games (list): List of game records
        filters (dict): Filters to apply
    
    Returns:
        list: Filtered games
    """
    if not filters:
        return games
    
    filtered_games = games
    
    # Apply character filter
    character_filter = filters.get('character', 'all')
    if character_filter and character_filter != 'all':
        filtered_games = [
            game for game in filtered_games 
            if _game_matches_character_filter(game, character_filter)
        ]
    
    # Apply opponent filter
    opponent_filter = filters.get('opponent', 'all')
    if opponent_filter and opponent_filter != 'all':
        filtered_games = [
            game for game in filtered_games
            if _game_matches_opponent_filter(game, opponent_filter)
        ]
    
    # Apply opponent character filter
    opponent_char_filter = filters.get('opponent_character', 'all')
    if opponent_char_filter and opponent_char_filter != 'all':
        filtered_games = [
            game for game in filtered_games
            if _game_matches_opponent_character_filter(game, opponent_char_filter)
        ]
    
    return filtered_games


def process_player_basic_stats(player_code):
    """
    Process basic player statistics.
    
    Args:
        player_code (str): Player tag/code
    
    Returns:
        dict: Basic player statistics
    """
    try:
        if not player_code:
            return None
            
        logger.info(f"Processing basic stats for player: {player_code}")
        
        # Get player games
        from backend.database import get_player_games
        games = get_player_games(player_code)
        
        if not games:
            return {
                'player_code': player_code,
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0
            }
        
        # Calculate basic stats
        total_games = len(games)
        wins = sum(1 for game in games if _is_player_win(game, player_code))
        losses = total_games - wins
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        
        return {
            'player_code': player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2)
        }
        
    except Exception as e:
        logger.error(f"Error processing basic stats for {player_code}: {str(e)}")
        return None

def process_server_statistics():
    """
    Process server statistics.
    
    Returns:
        dict: Server statistics
    """
    try:
        from backend.database import get_database_stats
        stats = get_database_stats()
        
        return {
            'total_games': stats.get('total_games', 0),
            'total_players': stats.get('total_players', 0),
            'total_clients': stats.get('total_clients', 0),
            'server_status': 'active'
        }
        
    except Exception as e:
        logger.error(f"Error processing server statistics: {str(e)}")
        return {
            'total_games': 0,
            'total_players': 0, 
            'total_clients': 0,
            'server_status': 'error'
        }    

# ============================================================================
# Helper Functions - Focused and Testable
# ============================================================================

def _is_player_win(game, player_code):
    """Check if the game was a win for the specified player."""
    try:
        player_data = json.loads(game.get('player_data', '[]'))
        for player in player_data:
            if player.get('player_tag') == player_code:
                return player.get('result') == 'Win'
        return False
    except Exception:
        return False
    
def _game_matches_opponent_filter(game, opponent_filter):
    """Check if game matches opponent filter."""
    try:
        player_data = json.loads(game.get('player_data', '[]'))
        for player in player_data:
            player_tag = player.get('player_tag', '').lower()
            if opponent_filter.lower() in player_tag:
                return True
        return False
    except Exception:
        return False

def _game_matches_opponent_character_filter(game, opponent_char_filter):
    """Check if game matches opponent character filter."""
    try:
        player_data = json.loads(game.get('player_data', '[]'))
        for player in player_data:
            character_name = player.get('character_name', '').lower()
            if opponent_char_filter.lower() in character_name:
                return True
        return False
    except Exception:
        return False

def _game_matches_character_filter(game, character_filter):
    """Check if game matches character filter."""
    try:
        player_data = json.loads(game.get('player_data', '[]'))
        for player in player_data:
            character_name = player.get('character_name', '').lower()
            if character_filter.lower() in character_name:
                return True
        return False
    except Exception:
        return False

def _process_games_data(client_id, games_data):
    """Process games portion of combined upload."""
    if not games_data:
        return {'uploaded': 0, 'duplicates': 0, 'errors': 0}
    
    # Use existing upload_games_for_client function
    from backend.api_service import upload_games_for_client
    return upload_games_for_client(client_id, games_data)

def _process_files_data(client_id, files_data):
    """Process files portion of combined upload."""
    files_result = {'uploaded': 0, 'duplicates': 0, 'errors': 0}
    file_details = []
    
    for file_info in files_data:
        file_result = _process_single_file(client_id, file_info)
        _update_file_counts(files_result, file_result)
        file_details.append(file_result['detail'])
    
    files_result['file_details'] = file_details
    return files_result

def _process_single_file(client_id, file_info):
    """Process a single file within a batch upload."""
    try:
        # Extract and validate file data
        file_data = _extract_file_data(file_info)
        
        # Check for duplicates
        if duplicate := _check_file_duplicate(file_data['hash']):
            return _create_duplicate_file_result(file_data, duplicate)
        
        # Process new file
        return _process_new_file(client_id, file_data)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return _create_file_error_result(file_info, str(e))

def _extract_file_data(file_info):
    """Extract and validate file data from upload info."""
    content = file_info.get('content')
    metadata = file_info.get('metadata', {})
    
    if not content:
        raise ValueError("File upload missing content")
    
    # Decode base64 content
    try:
        file_bytes = base64.b64decode(content)
    except Exception as e:
        raise ValueError(f"Invalid base64 content: {str(e)}")
    
    # Validate file
    _validate_file_data(file_bytes, metadata)
    
    return {
        'bytes': file_bytes,
        'size': len(file_bytes),
        'hash': _calculate_file_hash(file_bytes),
        'filename': metadata.get('filename', 'unknown.slp'),
        'metadata': metadata
    }

def _validate_file_data(file_bytes, metadata):
    """Validate file data and metadata."""
    filename = metadata.get('filename', 'unknown.slp')
    
    # Check file extension
    if not _is_allowed_file(filename):
        raise ValueError(f"File type not allowed: {filename}")
    
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {len(file_bytes)} bytes (max: {MAX_FILE_SIZE})")
    
    if len(file_bytes) == 0:
        raise ValueError("Empty file")

def _check_file_duplicate(file_hash):
    """Check if file already exists by hash."""
    return get_file_by_hash(file_hash)

def _process_new_file(client_id, file_data):
    """Process a new file upload."""
    try:
        # Save file to disk
        file_path = _save_file_to_disk(client_id, file_data)
        
        # Create database record
        file_record = _create_file_record_data(client_id, file_data, file_path)
        file_id = create_file_record(file_record)
        
        logger.info(f"Successfully processed file upload: {file_data['filename']} ({file_data['hash']})")
        
        return {
            'success': True,
            'detail': {
                'filename': file_data['filename'],
                'hash': file_data['hash'],
                'status': 'uploaded',
                'file_id': file_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error saving file {file_data['filename']}: {str(e)}")
        raise

def _save_file_to_disk(client_id, file_data):
    """Save uploaded file to organized directory structure."""
    # Create directory structure: uploads/client_id/YYYY/MM/
    upload_date = datetime.now()
    year_month_dir = os.path.join(
        config.get_uploads_dir(),
        client_id,
        upload_date.strftime('%Y'),
        upload_date.strftime('%m')
    )
    os.makedirs(year_month_dir, exist_ok=True)
    
    # Use hash as filename to avoid duplicates
    safe_filename = f"{file_data['hash']}.slp"
    file_path = os.path.join(year_month_dir, safe_filename)
    
    # Write file to disk
    with open(file_path, 'wb') as f:
        f.write(file_data['bytes'])
    
    logger.info(f"Saved file {file_data['filename']} as {file_path}")
    return file_path

def _create_file_record_data(client_id, file_data, file_path):
    """Create file record data for database insertion."""
    return {
        'file_hash': file_data['hash'],
        'client_id': client_id,
        'original_filename': file_data['filename'],
        'file_path': file_path,
        'file_size': file_data['size'],
        'upload_date': datetime.now().isoformat(),
        'metadata': json.dumps(file_data['metadata']) if isinstance(file_data['metadata'], dict) else file_data['metadata']
    }

def _create_combined_response(games_result, files_result):
    """Create standardized combined upload response."""
    total_games = games_result.get('uploaded', 0)
    total_files = files_result.get('uploaded', 0)
    
    return {
        'success': True,
        'message': f"Processed {total_games} games and {total_files} files",
        'games': games_result,
        'files': files_result
    }

def _create_duplicate_file_result(file_data, existing_file):
    """Create result for duplicate file."""
    return {
        'success': True,
        'detail': {
            'filename': file_data['filename'],
            'hash': file_data['hash'],
            'status': 'duplicate',
            'existing_file_id': existing_file.get('file_id')
        }
    }

def _create_file_error_result(file_info, error_message):
    """Create result for file processing error."""
    filename = file_info.get('metadata', {}).get('filename', 'unknown')
    return {
        'success': False,
        'detail': {
            'filename': filename,
            'status': 'error',
            'error': error_message
        }
    }

def _update_file_counts(files_result, file_result):
    """Update file processing counts based on result."""
    if file_result['success']:
        status = file_result['detail']['status']
        if status == 'uploaded':
            files_result['uploaded'] += 1
        elif status == 'duplicate':
            files_result['duplicates'] += 1
    else:
        files_result['errors'] += 1

# ============================================================================
# Utility Functions
# ============================================================================

def _is_allowed_file(filename):
    """Check if file extension is allowed."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

def _calculate_file_hash(file_content):
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()

# ============================================================================
# Backward Compatibility (if needed during transition)
# ============================================================================

def process_file_upload(client_id, file_data, metadata):
    """
    DEPRECATED: Use process_combined_upload instead.
    
    This function is maintained for backward compatibility but should
    be phased out in favor of the combined upload approach.
    """
    logger.warning("process_file_upload is deprecated. Use process_combined_upload instead.")
    
    # Convert to combined format and delegate
    upload_data = {
        'games': [],
        'files': [{
            'content': base64.b64encode(file_data).decode('utf-8'),
            'metadata': metadata
        }]
    }
    
    result = process_combined_upload(client_id, upload_data)
    
    # Extract file result for backward compatibility
    if result.get('files', {}).get('file_details'):
        file_detail = result['files']['file_details'][0]
        return {
            'success': file_detail['status'] != 'error',
            'message': 'File processed',
            'file_hash': file_detail.get('hash'),
            'duplicate': file_detail['status'] == 'duplicate',
            'file_id': file_detail.get('file_id'),
            'existing_file_id': file_detail.get('existing_file_id')
        }
    
    return {'success': False, 'message': 'File processing failed'}