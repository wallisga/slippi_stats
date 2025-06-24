"""
API Service Layer for Slippi Server.

This module contains business logic functions specifically for API endpoints.
Functions here prepare data for JSON responses and handle API-specific concerns.
"""

from backend.config import get_config
from backend.utils import decode_player_tag, process_raw_games_for_player
from backend.database import (
    get_database_stats, create_client_record, update_clients_info,
    create_api_key_record, update_api_key_record, check_client_exists,
    create_game_record, check_game_exists, validate_api_key, get_games_all,
    update_clients_last_active
)

# Get configuration and logger
config = get_config()
logger = config.init_logging()

# =============================================================================
# Helper Functions (Duplicated from web_service to avoid circular imports)
# =============================================================================

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

# =============================================================================
# API Request Validation and Processing
# =============================================================================

def process_client_registration(client_data, registration_key):
    """Handle client registration with validation for API."""
    from flask import abort
    
    if not registration_key or registration_key != config.REGISTRATION_SECRET:
        abort(401, description="Invalid registration key")
    
    try:
        result = register_or_update_client(client_data)
        return result
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")

def process_games_upload(client_id, upload_data):
    """Handle games upload with validation for API."""
    from flask import abort
    
    if upload_data.get('client_id') != client_id:
        abort(403, description="Client ID in request does not match API key")
    
    games = upload_data.get('games', [])
    try:
        result = upload_games_for_client(client_id, games)
        return result
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")