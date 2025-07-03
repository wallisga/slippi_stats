"""
API Service Layer for Slippi Server with file upload support.

This module adds file upload capabilities while maintaining existing functionality.
"""

import os
import hashlib
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from backend.config import get_config
from backend.utils import decode_player_tag, process_raw_games_for_player
from backend.database import (
    get_database_stats, create_client_record, update_clients_info,
    create_api_key_record, update_api_key_record, check_client_exists,
    create_game_record, check_game_exists, validate_api_key, get_games_all,
    update_clients_last_active, create_file_record, get_file_by_hash
)

# Get configuration and logger
config = get_config()
logger = config.init_logging()

# File upload settings
ALLOWED_EXTENSIONS = {'.slp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

def allowed_file(filename):
    """Check if file extension is allowed."""
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

def calculate_file_hash(file_content):
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()

def save_uploaded_file(file_content, filename, client_id, file_hash):
    """Save uploaded file to disk with organized directory structure."""
    try:
        # Create directory structure: uploads/client_id/YYYY/MM/
        upload_date = datetime.now()
        year_month_dir = os.path.join(
            config.get_uploads_dir(),
            client_id,
            upload_date.strftime('%Y'),
            upload_date.strftime('%m')
        )
        os.makedirs(year_month_dir, exist_ok=True)
        
        # Use hash as filename to avoid duplicates and ensure uniqueness
        safe_filename = f"{file_hash}.slp"
        file_path = os.path.join(year_month_dir, safe_filename)
        
        # Write file to disk
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved file {filename} as {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving uploaded file {filename}: {str(e)}")
        raise

def process_file_upload(client_id, file_data, metadata):
    """
    Process a file upload with metadata.
    
    Args:
        client_id (str): Client ID from API key validation
        file_data (bytes): Raw file content
        metadata (dict): File metadata including original filename, game data, etc.
    
    Returns:
        dict: Upload result with file info and processing status
    """
    try:
        original_filename = metadata.get('filename', 'unknown.slp')
        
        # Validate file
        if not allowed_file(original_filename):
            raise ValueError(f"File type not allowed: {original_filename}")
        
        if len(file_data) > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {len(file_data)} bytes (max: {MAX_FILE_SIZE})")
        
        if len(file_data) == 0:
            raise ValueError("Empty file")
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_data)
        
        # Check if file already exists
        existing_file = get_file_by_hash(file_hash)
        if existing_file:
            logger.info(f"File with hash {file_hash} already exists")
            return {
                'success': True,
                'message': 'File already exists',
                'file_hash': file_hash,
                'duplicate': True,
                'existing_file_id': existing_file['file_id']
            }
        
        # Save file to disk
        file_path = save_uploaded_file(file_data, original_filename, client_id, file_hash)
        
        # Create file record in database
        file_record = {
            'file_hash': file_hash,
            'client_id': client_id,
            'original_filename': original_filename,
            'file_path': file_path,
            'file_size': len(file_data),
            'upload_date': datetime.now().isoformat(),
            'metadata': json.dumps(metadata) if isinstance(metadata, dict) else metadata
        }
        
        file_id = create_file_record(file_record)
        
        # Update client last active
        update_clients_last_active(client_id)
        
        logger.info(f"Successfully processed file upload: {original_filename} ({file_hash})")
        
        return {
            'success': True,
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'file_hash': file_hash,
            'file_path': file_path,
            'duplicate': False
        }
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise

def process_combined_upload(client_id, upload_data):
    """
    Process combined game data and file upload.
    
    Args:
        client_id (str): Client ID from API key validation
        upload_data (dict): Contains both games data and file information
    
    Returns:
        dict: Combined upload result
    """
    try:
        games_data = upload_data.get('games', [])
        files_data = upload_data.get('files', [])
        
        # Process games data (existing functionality)
        games_result = upload_games_for_client(client_id, games_data) if games_data else {
            'uploaded': 0, 'duplicates': 0
        }
        
        # Process file uploads
        files_result = {'uploaded': 0, 'duplicates': 0, 'errors': 0}
        file_details = []
        
        for file_info in files_data:
            try:
                file_content = file_info.get('content')  # Base64 encoded content
                metadata = file_info.get('metadata', {})
                
                if not file_content:
                    logger.warning("File upload missing content")
                    files_result['errors'] += 1
                    continue
                
                # Decode base64 content
                import base64
                file_bytes = base64.b64decode(file_content)
                
                # Process the file upload
                result = process_file_upload(client_id, file_bytes, metadata)
                
                if result['duplicate']:
                    files_result['duplicates'] += 1
                else:
                    files_result['uploaded'] += 1
                
                file_details.append({
                    'filename': metadata.get('filename', 'unknown'),
                    'hash': result['file_hash'],
                    'status': 'duplicate' if result['duplicate'] else 'uploaded'
                })
                
            except Exception as e:
                logger.error(f"Error processing individual file: {str(e)}")
                files_result['errors'] += 1
                file_details.append({
                    'filename': file_info.get('metadata', {}).get('filename', 'unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'success': True,
            'message': f"Processed {games_result['uploaded']} games and {files_result['uploaded']} files",
            'games': games_result,
            'files': files_result,
            'file_details': file_details
        }
        
    except Exception as e:
        logger.error(f"Error processing combined upload: {str(e)}")
        raise

def get_player_games(player_code):
    """Get all games for a specific player."""
    try:
        raw_games = get_games_all()
        # Process them for the specific player
        return process_raw_games_for_player(raw_games, player_code)
    except Exception as e:
        logger.error(f"Error getting games for player {player_code}: {str(e)}")
        return []

def calculate_player_stats(games):
    """Calculate basic player statistics from game data."""
    if not games:
        return {}
    
    total_games = len(games)
    wins = sum(1 for game in games if game['result'] == 'Win')
    win_rate = wins / total_games if total_games > 0 else 0
    
    # Character stats
    character_stats = {}
    for game in games:
        char = game['player']['character_name']
        if char not in character_stats:
            character_stats[char] = {'games': 0, 'wins': 0}
        character_stats[char]['games'] += 1
        if game['result'] == 'Win':
            character_stats[char]['wins'] += 1
    
    for char in character_stats:
        games_with_char = character_stats[char]['games']
        wins_with_char = character_stats[char]['wins']
        character_stats[char]['win_rate'] = wins_with_char / games_with_char if games_with_char > 0 else 0
    
    return {
        'total_games': total_games,
        'wins': wins,
        'win_rate': win_rate,
        'character_stats': character_stats
    }

# =============================================================================
# Advanced Filtering Functions (API-Specific)
# =============================================================================

def apply_game_filters(games, character_filter='all', opponent_filter='all', opponent_character_filter='all'):
    """Apply filtering to a list of games based on various criteria."""
    filtered_games = games
    
    # Apply character filter
    if character_filter != 'all':
        if isinstance(character_filter, list):
            character_values = character_filter
        else:
            character_values = character_filter.split('|') if '|' in character_filter else [character_filter]
        filtered_games = [g for g in filtered_games if g['player'].get('character_name') in character_values]
    
    # Apply opponent filter
    if opponent_filter != 'all':
        if isinstance(opponent_filter, list):
            opponent_values = opponent_filter
        else:
            opponent_values = opponent_filter.split('|') if '|' in opponent_filter else [opponent_filter]
        filtered_games = [g for g in filtered_games if g['opponent'].get('player_tag') in opponent_values]
    
    # Apply opponent character filter
    if opponent_character_filter != 'all':
        if isinstance(opponent_character_filter, list):
            opp_char_values = opponent_character_filter
        else:
            opp_char_values = opponent_character_filter.split('|') if '|' in opponent_character_filter else [opponent_character_filter]
        filtered_games = [g for g in filtered_games if g['opponent'].get('character_name') in opp_char_values]
    
    return filtered_games

def extract_filter_options(games):
    """Extract all available filter options from a set of games."""
    characters_played = set()
    opponents_faced = set()
    opponent_characters_faced = set()
    
    for game in games:
        characters_played.add(game['player'].get('character_name', 'Unknown'))
        opponents_faced.add(game['opponent'].get('player_tag', 'Unknown'))
        opponent_characters_faced.add(game['opponent'].get('character_name', 'Unknown'))
    
    return {
        'characters': sorted(list(characters_played)),
        'opponents': sorted(list(opponents_faced)),
        'opponent_characters': sorted(list(opponent_characters_faced))
    }

def calculate_filtered_stats(filtered_games, filter_options):
    """Calculate comprehensive statistics for filtered game data."""
    total_filtered = len(filtered_games)
    wins_filtered = sum(1 for game in filtered_games if game['result'] == 'Win')
    overall_winrate = wins_filtered / total_filtered if total_filtered > 0 else 0
    
    # Character stats
    character_stats = {}
    for char in filter_options['characters']:
        char_games = [g for g in filtered_games if g['player'].get('character_name') == char]
        char_total = len(char_games)
        char_wins = sum(1 for g in char_games if g['result'] == 'Win')
        character_stats[char] = {
            'games': char_total,
            'wins': char_wins,
            'win_rate': char_wins / char_total if char_total > 0 else 0
        }
    
    # Opponent stats
    opponent_stats = {}
    for opp in filter_options['opponents']:
        opp_games = [g for g in filtered_games if g['opponent'].get('player_tag') == opp]
        opp_total = len(opp_games)
        opp_wins = sum(1 for g in opp_games if g['result'] == 'Win')
        opponent_stats[opp] = {
            'games': opp_total,
            'wins': opp_wins,
            'win_rate': opp_wins / opp_total if opp_total > 0 else 0
        }
    
    # Opponent character stats
    opponent_char_stats = {}
    for opp_char in filter_options['opponent_characters']:
        opp_char_games = [g for g in filtered_games if g['opponent'].get('character_name') == opp_char]
        opp_char_total = len(opp_char_games)
        opp_char_wins = sum(1 for g in opp_char_games if g['result'] == 'Win')
        opponent_char_stats[opp_char] = {
            'games': opp_char_total,
            'wins': opp_char_wins,
            'win_rate': opp_char_wins / opp_char_total if opp_char_total > 0 else 0
        }
    
    # Date stats
    date_stats = {}
    for game in filtered_games:
        date = game['start_time'].split('T')[0] if 'T' in game['start_time'] else game['start_time']
        if date not in date_stats:
            date_stats[date] = {'games': 0, 'wins': 0}
        
        date_stats[date]['games'] += 1
        if game['result'] == 'Win':
            date_stats[date]['wins'] += 1
    
    # Calculate win rates for dates and sort
    for date in date_stats:
        date_stats[date]['win_rate'] = date_stats[date]['wins'] / date_stats[date]['games']
    
    date_stats_sorted = {k: date_stats[k] for k in sorted(date_stats.keys())}
    
    return {
        'total_games': total_filtered,
        'wins': wins_filtered,
        'overall_winrate': overall_winrate,
        'character_stats': character_stats,
        'opponent_stats': opponent_stats,
        'opponent_character_stats': opponent_char_stats,
        'date_stats': date_stats_sorted
    }

# =============================================================================
# API Data Processing Functions
# =============================================================================

def process_detailed_player_data(player_code, filter_data=None):
    """Get detailed player data with optional filtering for API consumption."""
    if filter_data is None:
        filter_data = {}
    
    # Get all games for this player
    all_games = get_player_games(player_code)
    if not all_games:
        return None
    
    # Extract filter options from all games
    filter_options = extract_filter_options(all_games)
    
    # Get filter parameters
    character_filter = filter_data.get('character', 'all')
    opponent_filter = filter_data.get('opponent', 'all')
    opponent_character_filter = filter_data.get('opponent_character', 'all')
    
    # Apply filters
    filtered_games = apply_game_filters(
        all_games, character_filter, opponent_filter, opponent_character_filter
    )
    
    # Calculate statistics
    stats = calculate_filtered_stats(filtered_games, filter_options)
    
    # Build response
    response = {
        'player_code': player_code,
        'filter_options': filter_options,
        'applied_filters': {
            'character': character_filter,
            'opponent': opponent_filter,
            'opponent_character': opponent_character_filter
        }
    }
    response.update(stats)
    
    return response

def process_paginated_player_games(player_code, page=1):
    """Get paginated games for a player for API consumption."""
    try:
        all_games = get_player_games(player_code)
        total_games = len(all_games)
        total_pages = (total_games + config.GAMES_PER_PAGE - 1) // config.GAMES_PER_PAGE
        start_idx = (page - 1) * config.GAMES_PER_PAGE
        end_idx = min(start_idx + config.GAMES_PER_PAGE, total_games)
        
        if start_idx >= total_games:
            games_page = []
        else:
            games_page = all_games[start_idx:end_idx]
        
        return {
            'total_games': total_games,
            'total_pages': total_pages,
            'current_page': page,
            'games': games_page
        }
    except Exception as e:
        logger.error(f"Error getting paginated games for player {player_code}: {str(e)}")
        raise

def process_player_basic_stats(player_code):
    """Get basic player statistics for API consumption."""
    try:
        games = get_player_games(player_code)
        if not games:
            return None
        stats = calculate_player_stats(games)
        return stats
    except Exception as e:
        logger.error(f"Error getting basic stats for player {player_code}: {str(e)}")
        raise

def process_server_statistics():
    """Get server statistics for API consumption."""
    try:
        stats = get_database_stats()
        return {
            "total_clients": stats.get('total_clients', 0),
            "total_games": stats.get('total_games', 0),
            "unique_players": stats.get('unique_players', 0),
            "last_upload": stats.get('last_upload')
        }
    except Exception as e:
        logger.error(f"Error getting server statistics: {str(e)}")
        raise

# =============================================================================
# Client Registration and Management
# =============================================================================

def register_or_update_client(client_data):
    """Register a new client or update existing client information."""
    try:
        client_id = client_data.get('client_id')
        if not client_id:
            raise ValueError("Client ID is required")
        
        # Check if client exists
        if check_client_exists(client_id):
            # Update existing client
            update_clients_info(
                client_id,
                hostname=client_data.get('hostname'),
                platform=client_data.get('platform'),
                version=client_data.get('version')
            )
            
            # Update or create API key
            try:
                api_key_data = update_api_key_record(client_id)
            except Exception:
                # If update fails, create new API key
                api_key_data = create_api_key_record(client_id)
                
            logger.info(f"Updated existing client: {client_id}")
        else:
            # Create new client
            create_client_record(client_data)
            api_key_data = create_api_key_record(client_id)
            logger.info(f"Registered new client: {client_id}")
        
        return {
            'success': True,
            'message': 'Client registered successfully',
            'api_key': api_key_data['api_key'],
            'expires_at': api_key_data['expires_at']
        }
        
    except Exception as e:
        logger.error(f"Error registering client: {str(e)}")
        raise

def upload_games_for_client(client_id, games_data):
    """Process and upload games for a specific client."""
    try:
        if not games_data:
            return {'success': True, 'message': 'No games to upload', 'uploaded': 0, 'duplicates': 0}
        
        # Update client last active
        update_clients_last_active(client_id)
        
        uploaded_count = 0
        duplicate_count = 0
        
        for game_data in games_data:
            game_id = game_data.get('game_id')
            if not game_id:
                logger.warning("Game missing game_id, skipping")
                continue
            
            # Check if game already exists
            if check_game_exists(game_id):
                duplicate_count += 1
                continue
            
            # Prepare game record
            game_record = {
                'game_id': game_id,
                'client_id': client_id,
                'start_time': game_data.get('start_time', ''),
                'last_frame': game_data.get('last_frame', 0),
                'stage_id': game_data.get('stage_id', 0),
                'player_data': game_data.get('player_data', '[]'),
                'game_type': game_data.get('game_type', 'unknown')
            }
            
            # Ensure player_data is a JSON string
            if isinstance(game_record['player_data'], (list, dict)):
                import json
                game_record['player_data'] = json.dumps(game_record['player_data'])
            
            # Create game record
            create_game_record(game_record)
            uploaded_count += 1
        
        logger.info(f"Client {client_id} uploaded {uploaded_count} games ({duplicate_count} duplicates)")
        
        return {
            'success': True,
            'message': f'Uploaded {uploaded_count} games',
            'uploaded': uploaded_count,
            'duplicates': duplicate_count
        }
        
    except Exception as e:
        logger.error(f"Error uploading games for client {client_id}: {str(e)}")
        raise