"""
Shared utilities for Slippi Server.
This module contains helper functions used across multiple modules.
Only includes functions that are actually being used in the codebase.
"""
import urllib.parse
import json
import logging
from datetime import datetime

# Get logger
logger = logging.getLogger('SlippiServer')

# =============================================================================
# URL Encoding Utilities
# =============================================================================

def encode_player_tag(tag):
    """
    URL-encode a player tag for safe use in URLs.
    
    Args:
        tag (str): Raw player tag
        
    Returns:
        str: URL-encoded player tag
    """
    if not tag:
        return ""
    return urllib.parse.quote(tag)

def decode_player_tag(encoded_tag):
    """
    Decode a URL-encoded player tag back to original form.
    
    Args:
        encoded_tag (str): URL-encoded player tag
        
    Returns:
        str: Decoded player tag
    """
    if not encoded_tag:
        return ""
    return urllib.parse.unquote(encoded_tag)

# =============================================================================
# Error Template Data Utilities
# =============================================================================

def get_error_template_data(status_code, error_description, **kwargs):
    """Generate standardized template data for error pages."""
    error_info = {
        400: {'title': 'Bad Request', 'icon': 'bi-exclamation-triangle', 'type': 'warning'},
        401: {'title': 'Unauthorized', 'icon': 'bi-shield-x', 'type': 'danger'},
        403: {'title': 'Forbidden', 'icon': 'bi-shield-exclamation', 'type': 'danger'},
        404: {'title': 'Page Not Found', 'icon': 'bi-question-circle', 'type': 'info'},
        429: {'title': 'Too Many Requests', 'icon': 'bi-clock', 'type': 'warning'},
        500: {'title': 'Server Error', 'icon': 'bi-exclamation-octagon', 'type': 'danger'}
    }
    
    error_meta = error_info.get(status_code, {'title': 'Unknown Error', 'icon': 'bi-exclamation-circle', 'type': 'secondary'})
    
    base_data = {
        'layout_type': 'error', 'has_player_search': False, 'navbar_context': 'error',
        'status_code': status_code, 'error_description': error_description,
        'error_title': error_meta['title'], 'error_icon': error_meta['icon'],
        'error_type': error_meta['type'], 'show_home_link': True,
        'show_back_link': status_code == 404
    }
    base_data.update(kwargs)
    return base_data

# =============================================================================
# Game Data Processing Utilities (Shared Business Logic)
# =============================================================================

def parse_player_data_from_game(player_json_data):
    """
    Parse player data from JSON string to structured format.
    
    Args:
        player_json_data (str): JSON string containing player data
        
    Returns:
        list: List of parsed player dictionaries
    """
    try:
        if isinstance(player_json_data, str):
            return json.loads(player_json_data)
        return player_json_data
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Could not parse player data: {e}")
        return []

def find_player_in_game_data(parsed_players, target_player_tag):
    """
    Find a specific player in parsed game data.
    
    Args:
        parsed_players (list): List of player dictionaries
        target_player_tag (str): Player tag to search for
        
    Returns:
        tuple: (player_data, opponent_data) or (None, None) if not found
    """
    target_lower = target_player_tag.lower()
    
    for player in parsed_players:
        if player.get('player_tag', '').lower() == target_lower:
            # Find opponent (the other player)
            for opponent in parsed_players:
                if opponent.get('player_tag', '').lower() != target_lower:
                    return player, opponent
            return player, None
    
    return None, None

def safe_get_player_field(player_data, field_name, default_value='Unknown'):
    """
    Safely get a field from player data with fallback.
    
    Args:
        player_data (dict): Player data dictionary
        field_name (str): Name of field to retrieve
        default_value: Default value if field missing
        
    Returns:
        Field value or default
    """
    if not player_data:
        return default_value
    return player_data.get(field_name, default_value)

def calculate_win_rate(wins, total_games):
    """
    Calculate win rate percentage with safety checks.
    
    Args:
        wins (int): Number of wins
        total_games (int): Total number of games
        
    Returns:
        float: Win rate as a decimal (0.0 to 1.0)
    """
    if total_games <= 0:
        return 0.0
    return wins / total_games

def process_raw_games_for_player(raw_games, target_player_tag):
    """
    Process raw game records to extract player-specific game data.
    
    Args:
        raw_games (list): Raw game records from database
        target_player_tag (str): Player tag to extract data for
        
    Returns:
        list: Processed game data for the specific player
    """
    processed_games = []
    
    for game in raw_games:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            if not parsed_players:
                continue
                
            player_data, opponent_data = find_player_in_game_data(parsed_players, target_player_tag)
            if not player_data:
                continue
                
            # Use the result field instead of placement
            result = safe_get_player_field(player_data, 'result', 'Loss')
            
            # Build processed game record
            processed_game = {
                'game_id': game_dict['game_id'],
                'start_time': game_dict['start_time'],
                'stage_id': game_dict['stage_id'],
                'result': result,
                'player': {
                    'player_tag': safe_get_player_field(player_data, 'player_tag'),
                    'character_name': safe_get_player_field(player_data, 'character_name'),
                    'placement': safe_get_player_field(player_data, 'placement', 999)
                },
                'opponent': {
                    'player_tag': safe_get_player_field(opponent_data, 'player_tag'),
                    'character_name': safe_get_player_field(opponent_data, 'character_name'),
                    'placement': safe_get_player_field(opponent_data, 'placement', 999)
                } if opponent_data else {
                    'player_tag': 'Unknown',
                    'character_name': 'Unknown',
                    'placement': 999
                }
            }
            
            processed_games.append(processed_game)
            
        except Exception as e:
            game_id = dict(game).get('game_id', 'unknown') if hasattr(game, 'keys') else 'unknown'
            logger.warning(f"Error processing game {game_id}: {e}")
            continue
    
    # Sort by start_time (most recent first)
    processed_games.sort(key=lambda x: x['start_time'], reverse=True)
    return processed_games

def find_flexible_player_matches(raw_games, target_player_tag):
    """
    Find potential player matches with flexible matching (case-insensitive, partial).
    
    Args:
        raw_games (list): Raw game records from database
        target_player_tag (str): Player tag to search for
        
    Returns:
        list: List of potential matches with match_type
    """
    target_lower = target_player_tag.lower()
    found_tags = set()
    matches = []
    
    for game in raw_games:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            for player in parsed_players:
                tag = player.get('player_tag', '')
                if not tag or tag in found_tags:
                    continue
                    
                tag_lower = tag.lower()
                
                # Exact match (case-insensitive)
                if tag_lower == target_lower:
                    matches.append({'tag': tag, 'match_type': 'case_insensitive'})
                    found_tags.add(tag)
                # Partial match
                elif target_lower in tag_lower or tag_lower in target_lower:
                    matches.append({'tag': tag, 'match_type': 'partial'})
                    found_tags.add(tag)
                    
        except Exception as e:
            game_id = dict(game).get('game_id', 'unknown') if hasattr(game, 'keys') else 'unknown'
            logger.warning(f"Error finding matches in game {game_id}: {e}")
            continue
    
    # Sort by match quality (exact first, then partial)
    matches.sort(key=lambda x: (x['match_type'] != 'case_insensitive', x['tag']))
    return matches

def extract_player_stats_from_games(raw_games):
    """
    Extract player statistics and rankings from raw game data.
    
    Args:
        raw_games (list): Raw game records from database
        
    Returns:
        tuple: (top_players, all_players) - both are lists of player stats
    """
    player_stats = {}
    
    for game in raw_games[:5]:  # Only debug first 5 games to avoid spam
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            logger.debug(f"Game {game_dict.get('game_id', 'unknown')}: Found {len(parsed_players)} players")
            
            for i, player in enumerate(parsed_players):
                logger.debug(f"  Player {i}: {player}")
                
                tag = player.get('player_tag', '')
                if not tag:
                    continue
                    
                if tag not in player_stats:
                    player_stats[tag] = {'games': 0, 'wins': 0}
                
                player_stats[tag]['games'] += 1
                
                # Check result field instead of placement
                result = player.get('result', '')
                logger.debug(f"  Player {tag} result: {result} (type: {type(result)})")
                
                if result == 'Win':
                    player_stats[tag]['wins'] += 1
                    logger.debug(f"  -> Counted as WIN for {tag}")
                else:
                    logger.debug(f"  -> Counted as LOSS for {tag}")
                    
        except Exception as e:
            logger.warning(f"Error extracting stats from game {game.get('game_id', 'unknown')}: {e}")
            continue
    
    # Process remaining games without debug spam
    for game in raw_games[5:]:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            for player in parsed_players:
                tag = player.get('player_tag', '')
                if not tag:
                    continue
                    
                if tag not in player_stats:
                    player_stats[tag] = {'games': 0, 'wins': 0}
                
                player_stats[tag]['games'] += 1
                if player.get('result') == 'Win':
                    player_stats[tag]['wins'] += 1
                    
        except Exception as e:
            logger.warning(f"Error extracting stats from game {game.get('game_id', 'unknown')}: {e}")
            continue
    
    # Calculate win rates and build player list
    all_players = []
    for tag, stats in player_stats.items():
        win_rate = calculate_win_rate(stats['wins'], stats['games'])
        
        all_players.append({
            # Frontend expects these field names
            'name': tag,  # Frontend expects 'name' field
            'code': tag,  # Frontend expects 'code' field  
            'code_encoded': encode_player_tag(tag),  # Frontend expects 'code_encoded'
            'games': stats['games'],
            'wins': stats['wins'],
            'win_rate': win_rate,
            
            # Legacy format for backward compatibility
            'tag': tag,
            'encoded_tag': encode_player_tag(tag)
        })
    
    # Sort all players by games played (descending)
    all_players.sort(key=lambda x: x['games'], reverse=True)
    
    # Get top players (minimum games threshold)
    min_games = 5  # Could be moved to config
    top_players = [p for p in all_players if p['games'] >= min_games]
    top_players.sort(key=lambda x: x['win_rate'], reverse=True)
    
    logger.debug(f"Returning {len(top_players)} top players and {len(all_players)} total players")
    
    return top_players, all_players

def process_recent_games_data(raw_games, limit=10):
    """
    Process raw games into recent games format for display.
    
    Args:
        raw_games (list): Raw game records from database (should be pre-sorted by recency)
        limit (int): Maximum number of games to return
        
    Returns:
        list: Processed recent games data
    """
    recent_games = []
    
    for game in raw_games[:limit]:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            if len(parsed_players) < 2:
                continue
                
            # Get both players
            player1, player2 = parsed_players[0], parsed_players[1]
            
            # Determine winner based on result field
            p1_result = player1.get('result', '')
            p2_result = player2.get('result', '')
            
            if p1_result == 'Win':
                winner, loser = player1, player2
            elif p2_result == 'Win':
                winner, loser = player2, player1
            else:
                # If no clear winner (shouldn't happen), use first player as "winner"
                winner, loser = player1, player2
            
            # Get player data
            player1_tag = safe_get_player_field(player1, 'player_tag')
            player2_tag = safe_get_player_field(player2, 'player_tag')
            player1_char = safe_get_player_field(player1, 'character_name')
            player2_char = safe_get_player_field(player2, 'character_name')
            
            # Determine the result string for the winner
            result_text = f"Win - {safe_get_player_field(winner, 'player_tag')} vs {safe_get_player_field(loser, 'player_tag')}"
            
            # Build recent game record matching frontend template expectations
            recent_game = {
                'game_id': game_dict['game_id'],
                'start_time': game_dict['start_time'],
                'time': game_dict['start_time'],  # Frontend expects 'time' field
                'stage_id': game_dict['stage_id'],
                'result': result_text,
                
                # Player 1 data
                'player1': player1_tag,
                'player1_tag_encoded': encode_player_tag(player1_tag),
                'character1': player1_char,
                
                # Player 2 data
                'player2': player2_tag,
                'player2_tag_encoded': encode_player_tag(player2_tag),
                'character2': player2_char,
                
                # Legacy format for backward compatibility
                'winner': {
                    'player_tag': safe_get_player_field(winner, 'player_tag'),
                    'character_name': safe_get_player_field(winner, 'character_name'),
                    'encoded_tag': encode_player_tag(safe_get_player_field(winner, 'player_tag'))
                },
                'loser': {
                    'player_tag': safe_get_player_field(loser, 'player_tag'),
                    'character_name': safe_get_player_field(loser, 'character_name'),
                    'encoded_tag': encode_player_tag(safe_get_player_field(loser, 'player_tag'))
                }
            }
            
            recent_games.append(recent_game)
            
        except Exception as e:
            logger.warning(f"Error processing recent game {dict(game).get('game_id', 'unknown') if hasattr(game, 'keys') else 'unknown'}: {e}")
            continue
    
    return recent_games