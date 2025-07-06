"""
Shared utilities for Slippi Server.
This module contains helper functions used across multiple modules.
Only includes functions that are actually being used in the codebase.
"""
import urllib.parse
import json
import logging
from datetime import datetime
from backend.logging_utils import get_structured_logger

# Replace the existing logger line
logger = get_structured_logger('utils')

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
    """Parse player data from game JSON with None safety and structured logging."""
    logger.debug("Parsing player data from game", extra={
        "source_function": "parse_player_data_from_game",
        "source_module": "utils",
        "context": {
            "has_data": player_json_data is not None,
            "data_type": type(player_json_data).__name__ if player_json_data else "None"
        }
    })
    
    if not player_json_data:
        logger.debug("No player data provided", extra={
            "source_function": "parse_player_data_from_game",
            "source_module": "utils",
            "context": {"result": "empty_list"}
        })
        return []
    
    try:
        # If it's a string, parse as JSON
        if isinstance(player_json_data, str):
            parsed_data = json.loads(player_json_data)
        else:
            parsed_data = player_json_data
        
        # Ensure it's a list
        if not isinstance(parsed_data, list):
            logger.warning("Player data is not a list", extra={
                "source_function": "parse_player_data_from_game",
                "source_module": "utils",
                "error_code": "INVALID_DATA_FORMAT",
                "context": {
                    "actual_type": type(parsed_data).__name__,
                    "expected_type": "list"
                }
            })
            return []
        
        logger.debug("Player data parsed successfully", extra={
            "source_function": "parse_player_data_from_game",
            "source_module": "utils",
            "context": {
                "players_count": len(parsed_data),
                "data_format": "valid"
            }
        })
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse player JSON data", extra={
            "source_function": "parse_player_data_from_game",
            "source_module": "utils",
            "error_code": "JSON_DECODE_ERROR",
            "context": {
                "exception_message": str(e),
                "data_preview": str(player_json_data)[:100] if player_json_data else "None"
            }
        })
        return []
    except Exception as e:
        logger.error("Unexpected error parsing player data", extra={
            "source_function": "parse_player_data_from_game",
            "source_module": "utils",
            "error_code": "PARSE_ERROR",
            "context": {
                "exception_type": type(e).__name__,
                "exception_message": str(e)
            }
        })
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
    if total_games is None or wins is None or total_games <= 0:
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
    if raw_games is None:
        return []  # Return empty list instead of trying to iterate None
    
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

# Updated extract_player_stats_from_games function
def extract_player_stats_from_games(raw_games):
    """
    Extract player statistics from all games with structured logging.
    """
    logger.debug("Starting player stats extraction", extra={
        "source_function": "extract_player_stats_from_games",
        "source_module": "utils",
        "context": {"raw_games_count": len(raw_games)}
    })
    
    player_stats = {}
    processed_games = 0
    skipped_games = 0
    
    for game in raw_games:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            game_id = game_dict.get('id', 'unknown')
            
            # Parse player data from JSON
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            
            if len(parsed_players) < 2:
                logger.debug("Game skipped - insufficient players", extra={
                    "source_function": "extract_player_stats_from_games",
                    "source_module": "utils",
                    "context": {
                        "game_id": game_id,
                        "players_found": len(parsed_players)
                    }
                })
                skipped_games += 1
                continue
            
            logger.debug("Game processing", extra={
                "source_function": "extract_player_stats_from_games",
                "source_module": "utils",
                "context": {
                    "game_id": game_id,
                    "players_found": len(parsed_players)
                }
            })
            
            for player in parsed_players:
                tag = player.get('player_tag', 'Unknown')
                character = player.get('character_name', 'Unknown')
                result = player.get('result', '')
                
                logger.debug("Processing player result", extra={
                    "source_function": "extract_player_stats_from_games",
                    "source_module": "utils",
                    "context": {
                        "game_id": game_id,
                        "player_tag": tag,
                        "character": character,
                        "result": result,
                        "result_type": type(result).__name__
                    }
                })
                
                # Initialize player stats if first time seeing this player
                if tag not in player_stats:
                    player_stats[tag] = {
                        'games': 0,
                        'wins': 0,
                        'characters': {}
                    }
                
                # Update game count
                player_stats[tag]['games'] += 1
                
                # Update character usage
                if character not in player_stats[tag]['characters']:
                    player_stats[tag]['characters'][character] = 0
                player_stats[tag]['characters'][character] += 1
                
                # Process wins with structured logging
                if result == 'Win':
                    player_stats[tag]['wins'] += 1
                    logger.debug("Win recorded", extra={
                        "source_function": "extract_player_stats_from_games",
                        "source_module": "utils",
                        "context": {
                            "game_id": game_id,
                            "player_tag": tag,
                            "total_wins": player_stats[tag]['wins']
                        }
                    })
                elif result == 'Loss':
                    logger.debug("Loss recorded", extra={
                        "source_function": "extract_player_stats_from_games",
                        "source_module": "utils",
                        "context": {
                            "game_id": game_id,
                            "player_tag": tag,
                            "total_games": player_stats[tag]['games']
                        }
                    })
                else:
                    logger.warning("Unknown result type", extra={
                        "source_function": "extract_player_stats_from_games",
                        "source_module": "utils",
                        "error_code": "UNKNOWN_RESULT",
                        "context": {
                            "game_id": game_id,
                            "player_tag": tag,
                            "result": result,
                            "result_type": type(result).__name__
                        }
                    })
            
            processed_games += 1
            
        except Exception as e:
            skipped_games += 1
            logger.error("Error processing game", extra={
                "source_function": "extract_player_stats_from_games",
                "source_module": "utils",
                "error_code": "GAME_PROCESSING_ERROR",
                "context": {
                    "game_id": game_dict.get('id', 'unknown'),
                    "exception_message": str(e)
                }
            })
            continue
    
    # Calculate win rates and build player list
    all_players = []
    for tag, stats in player_stats.items():
        win_rate = calculate_win_rate(stats['wins'], stats['games'])
        
        # Calculate most played character
        most_played_character = None
        if stats['characters']:
            most_played_character = max(stats['characters'].items(), key=lambda x: x[1])[0]
        
        all_players.append({
            'name': tag,
            'code': tag,
            'code_encoded': encode_player_tag(tag),
            'games': stats['games'],
            'wins': stats['wins'],
            'win_rate': win_rate,
            'most_played_character': most_played_character,
            'tag': tag,
            'encoded_tag': encode_player_tag(tag)
        })
    
    # Sort all players by games played (descending)
    all_players.sort(key=lambda x: x['games'], reverse=True)
    
    # Get top players (minimum games threshold)
    min_games = 5
    top_players = [p for p in all_players if p['games'] >= min_games]
    top_players.sort(key=lambda x: x['win_rate'], reverse=True)
    
    logger.info("Player stats extraction completed", extra={
        "source_function": "extract_player_stats_from_games",
        "source_module": "utils",
        "context": {
            "processed_games": processed_games,
            "skipped_games": skipped_games,
            "total_players": len(all_players),
            "qualified_top_players": len(top_players),
            "min_games_threshold": min_games
        }
    })
    
    return top_players, all_players

def process_recent_games_data(raw_games, limit=10):
    """Process raw games into recent games format for display with structured logging."""
    logger.debug("Processing recent games data", extra={
        "source_function": "process_recent_games_data",
        "source_module": "utils",
        "context": {
            "raw_games_count": len(raw_games),
            "limit": limit
        }
    })
    
    recent_games = []
    processed_count = 0
    skipped_count = 0
    
    for game in raw_games[:limit]:
        try:
            # Convert sqlite3.Row to dict for easier access
            game_dict = dict(game) if hasattr(game, 'keys') else game
            game_id = game_dict.get('id', 'unknown')
            
            parsed_players = parse_player_data_from_game(game_dict['player_data'])
            if len(parsed_players) < 2:
                logger.debug("Game skipped - insufficient players for recent games", extra={
                    "source_function": "process_recent_games_data",
                    "source_module": "utils",
                    "context": {
                        "game_id": game_id,
                        "players_found": len(parsed_players)
                    }
                })
                skipped_count += 1
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
                # If no clear winner, use first player as "winner"
                winner, loser = player1, player2
                logger.warning("No clear winner found in game", extra={
                    "source_function": "process_recent_games_data",
                    "source_module": "utils",
                    "error_code": "NO_CLEAR_WINNER",
                    "context": {
                        "game_id": game_id,
                        "p1_result": p1_result,
                        "p2_result": p2_result
                    }
                })
            
            recent_game = {
                'game_id': game_dict.get('id'),
                'start_time': game_dict.get('start_time'),
                'winner': {
                    'name': winner.get('player_name', 'Unknown'),
                    'tag': winner.get('player_tag', 'Unknown'),
                    'encoded_tag': encode_player_tag(winner.get('player_tag', 'Unknown')),
                    'character': winner.get('character_name', 'Unknown')
                },
                'loser': {
                    'name': loser.get('player_name', 'Unknown'),
                    'tag': loser.get('player_tag', 'Unknown'),
                    'encoded_tag': encode_player_tag(loser.get('player_tag', 'Unknown')),
                    'character': loser.get('character_name', 'Unknown')
                }
            }
            
            recent_games.append(recent_game)
            processed_count += 1
            
        except Exception as e:
            skipped_count += 1
            logger.error("Error processing recent game", extra={
                "source_function": "process_recent_games_data",
                "source_module": "utils",
                "error_code": "RECENT_GAME_PROCESSING_ERROR",
                "context": {
                    "game_id": game_dict.get('id', 'unknown') if 'game_dict' in locals() else 'unknown',
                    "exception_message": str(e)
                }
            })
            continue
    
    logger.info("Recent games processing completed", extra={
        "source_function": "process_recent_games_data",
        "source_module": "utils",
        "context": {
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "returned_count": len(recent_games),
            "limit": limit
        }
    })
    
    return recent_games