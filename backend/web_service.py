"""
Web Service Layer for Slippi Server.

This module contains business logic functions specifically for web page rendering.
Functions here prepare data for HTML templates and handle web-specific concerns.
"""

from datetime import datetime
from backend.config import get_config
from backend.utils import (
    encode_player_tag, decode_player_tag,
    process_raw_games_for_player, find_flexible_player_matches,
    extract_player_stats_from_games, process_recent_games_data
)
from backend.database import (
    get_games_all, get_games_recent, get_database_stats
)

import logging
from backend.logging_utils import (
    log_function_execution, 
    get_structured_logger, 
    log_business_event,
    log_performance_metric
)

# Replace the existing logger line
logger = get_structured_logger('web_service')

# =============================================================================
# Statistics Functions (Shared between web and API)
# =============================================================================

def calculate_player_stats(games):
    """Calculate comprehensive player statistics from game data."""
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
    
    most_played = max(character_stats.items(), key=lambda x: x[1]['games'])[0] if character_stats else None
    
    best_characters = [char for char, data in character_stats.items() if data['games'] >= config.MIN_GAMES_FOR_STATS]
    best_winrate_char = max([(char, character_stats[char]['win_rate']) for char in best_characters], key=lambda x: x[1])[0] if best_characters else None
    worst_winrate_char = min([(char, character_stats[char]['win_rate']) for char in best_characters], key=lambda x: x[1])[0] if best_characters else None
    
    # Opponent stats
    opponent_stats = {}
    for game in games:
        opponent_tag = game['opponent']['player_tag']
        opponent_char = game['opponent']['character_name']
        matchup_key = f"{opponent_tag}_{opponent_char}"
        
        if matchup_key not in opponent_stats:
            opponent_stats[matchup_key] = {'opponent_tag': opponent_tag, 'opponent_char': opponent_char, 'games': 0, 'wins': 0}
        
        opponent_stats[matchup_key]['games'] += 1
        if game['result'] == 'Win':
            opponent_stats[matchup_key]['wins'] += 1
    
    for key in opponent_stats:
        games_vs_opp = opponent_stats[key]['games']
        wins_vs_opp = opponent_stats[key]['wins']
        opponent_stats[key]['win_rate'] = wins_vs_opp / games_vs_opp if games_vs_opp > 0 else 0
    
    # Find rival
    rival_matchups = [key for key, data in opponent_stats.items() if data['games'] >= config.MIN_GAMES_FOR_STATS]
    rival = None
    if rival_matchups:
        rival_key = min([(key, opponent_stats[key]['win_rate']) for key in rival_matchups], key=lambda x: x[1])[0]
        rival = opponent_stats[rival_key]
    
    # Rising star
    recent_games = games[:30]
    recent_char_stats = {}
    for game in recent_games:
        char = game['player']['character_name']
        if char not in recent_char_stats:
            recent_char_stats[char] = {'games': 0, 'wins': 0}
        recent_char_stats[char]['games'] += 1
        if game['result'] == 'Win':
            recent_char_stats[char]['wins'] += 1
    
    for char in recent_char_stats:
        games_with_char = recent_char_stats[char]['games']
        wins_with_char = recent_char_stats[char]['wins']
        recent_char_stats[char]['win_rate'] = wins_with_char / games_with_char if games_with_char > 0 else 0
    
    rising_characters = [char for char, data in recent_char_stats.items() if data['games'] >= 5]
    rising_star = max([(char, recent_char_stats[char]['win_rate']) for char in rising_characters], key=lambda x: x[1])[0] if rising_characters else None
    
    # Stage stats
    stage_stats = {}
    for game in games:
        stage_id = game['stage_id']
        if stage_id not in stage_stats:
            stage_stats[stage_id] = {'games': 0, 'wins': 0}
        stage_stats[stage_id]['games'] += 1
        if game['result'] == 'Win':
            stage_stats[stage_id]['wins'] += 1
    
    for stage_id in stage_stats:
        games_on_stage = stage_stats[stage_id]['games']
        wins_on_stage = stage_stats[stage_id]['wins']
        stage_stats[stage_id]['win_rate'] = wins_on_stage / games_on_stage if games_on_stage > 0 else 0
    
    qualified_stages = [stage_id for stage_id, data in stage_stats.items() if data['games'] >= 5]
    
    best_stage = None
    worst_stage = None
    
    if qualified_stages:
        best_stage_id = max([(stage_id, stage_stats[stage_id]['win_rate']) for stage_id in qualified_stages], key=lambda x: x[1])[0]
        best_stage = {'id': best_stage_id, **stage_stats[best_stage_id]}
        
        worst_stage_id = min([(stage_id, stage_stats[stage_id]['win_rate']) for stage_id in qualified_stages], key=lambda x: x[1])[0]
        worst_stage = {'id': worst_stage_id, **stage_stats[worst_stage_id]}
    
    return {
        'total_games': total_games, 'wins': wins, 'win_rate': win_rate,
        'most_played_character': most_played, 'best_character': best_winrate_char,
        'worst_character': worst_winrate_char, 'character_stats': character_stats,
        'rival': rival, 'rising_star': rising_star, 'best_stage': best_stage,
        'worst_stage': worst_stage, 'stage_stats': stage_stats, 'opponent_stats': opponent_stats
    }

# =============================================================================
# Data Access Functions (Using New Database Layer)
# =============================================================================

def get_player_games(player_code):
    """Get all games for a specific player."""
    try:
        # Get all games from database
        raw_games = get_games_all()
        # Process them for the specific player
        return process_raw_games_for_player(raw_games, player_code)
    except Exception as e:
        logger.error(f"Error getting games for player {player_code}: {str(e)}")
        return []

def find_player_matches(player_code):
    """Find potential player matches with flexible matching."""
    try:
        # Get all games from database
        raw_games = get_games_all()
        # Find flexible matches
        return find_flexible_player_matches(raw_games, player_code)
    except Exception as e:
        logger.error(f"Error finding matches for player {player_code}: {str(e)}")
        return []

@log_function_execution(log_level=logging.INFO)
def get_recent_games(limit=10):
    """Get recent games for homepage display with structured logging."""
    logger.debug("Getting recent games", extra={
        "source_function": "get_recent_games",
        "source_module": "web_service",
        "context": {"limit": limit}
    })
    
    try:
        # Get recent raw games from database
        raw_games = get_games_recent(limit * 2)  # Get more than needed in case some are filtered out
        
        logger.debug("Raw games retrieved from database", extra={
            "source_function": "get_recent_games",
            "source_module": "web_service",
            "context": {
                "raw_games_count": len(raw_games),
                "requested_limit": limit
            }
        })
        
        # Process them for display
        processed_games = process_recent_games_data(raw_games, limit)
        
        logger.info("Recent games processed", extra={
            "source_function": "get_recent_games",
            "source_module": "web_service",
            "context": {
                "processed_games_count": len(processed_games),
                "limit": limit
            }
        })
        
        return processed_games
        
    except Exception as e:
        logger.error("Error getting recent games", extra={
            "source_function": "get_recent_games",
            "source_module": "web_service",
            "error_code": "RECENT_GAMES_ERROR",
            "context": {
                "limit": limit,
                "exception_message": str(e)
            }
        })
        return []

@log_function_execution(log_level=logging.INFO)
def get_top_players(limit=10):
    """Get top players by win rate with structured logging."""
    logger.debug("Getting top players", extra={
        "source_function": "get_top_players",
        "source_module": "web_service",
        "context": {"limit": limit}
    })
    
    try:
        # Get all games from database
        raw_games = get_games_all()
        
        logger.debug("Raw games retrieved for player stats", extra={
            "source_function": "get_top_players",
            "source_module": "web_service",
            "context": {
                "raw_games_count": len(raw_games),
                "limit": limit
            }
        })
        
        # Extract player stats
        top_players, all_players = extract_player_stats_from_games(raw_games)
        top_players_limited = top_players[:limit]
        
        logger.info("Top players calculated", extra={
            "source_function": "get_top_players",
            "source_module": "web_service",
            "context": {
                "top_players_returned": len(top_players_limited),
                "total_qualified_players": len(top_players),
                "total_players": len(all_players),
                "limit": limit
            }
        })
        
        # Log performance metric
        log_performance_metric('top_players_calculation', 
                             len(top_players_limited), 
                             'players', 
                             limit=limit)
        
        return top_players_limited
        
    except Exception as e:
        logger.error("Error getting top players", extra={
            "source_function": "get_top_players",
            "source_module": "web_service",
            "error_code": "TOP_PLAYERS_ERROR",
            "context": {
                "limit": limit,
                "exception_message": str(e)
            }
        })
        return []

@log_function_execution(log_level=logging.INFO)
def get_all_players():
    """Get all players with their stats with structured logging."""
    logger.debug("Getting all players", extra={
        "source_function": "get_all_players",
        "source_module": "web_service"
    })
    
    try:
        # Get all games from database
        raw_games = get_games_all()
        
        logger.debug("Raw games retrieved for all players", extra={
            "source_function": "get_all_players",
            "source_module": "web_service",
            "context": {"raw_games_count": len(raw_games)}
        })
        
        # Extract all player stats
        _, all_players = extract_player_stats_from_games(raw_games)
        
        logger.info("All players data prepared", extra={
            "source_function": "get_all_players",
            "source_module": "web_service",
            "context": {"total_players": len(all_players)}
        })
        
        return all_players
        
    except Exception as e:
        logger.error("Error getting all players", extra={
            "source_function": "get_all_players",
            "source_module": "web_service",
            "error_code": "ALL_PLAYERS_ERROR",
            "context": {"exception_message": str(e)}
        })
        return []
# =============================================================================
# Template Data Preparation Functions
# =============================================================================

def prepare_standard_player_template_data(player_code, encoded_player_code):
    """Generate standardized template data for player pages."""
    games = get_player_games(player_code)
    
    if len(games) == 0:
        potential_matches = find_player_matches(player_code)
        if potential_matches:
            exact_case_insensitive = [m for m in potential_matches if m['match_type'] == 'case_insensitive']
            if exact_case_insensitive:
                correct_tag = exact_case_insensitive[0]['tag']
                return {'redirect_to': correct_tag, 'redirect_encoded': encode_player_tag(correct_tag)}
        from flask import abort
        abort(404, description=f"Player '{player_code}' not found in database.")
    
    stats = calculate_player_stats(games)
    recent_games = games[:20]
    character_list = list(set(g['player']['character_name'] for g in games))
    
    return {
        'player_code': player_code, 'encoded_player_code': encoded_player_code,
        'stats': stats, 'recent_games': recent_games, 'character_list': character_list,
        'all_games': games, 'last_game_date': recent_games[0]['start_time'] if recent_games else None
    }

@log_function_execution(log_level=logging.INFO, include_args=False)
def prepare_homepage_data():
    """Prepare data for homepage template with enhanced logging."""
    logger.info("Preparing homepage data", extra={
        "source_function": "prepare_homepage_data",
        "source_module": "web_service"
    })
    
    try:
        stats = get_database_stats()
        recent_games = get_recent_games(10)
        top_players = get_top_players(6)
        
        homepage_data = {
            'total_games': stats.get('total_games', 0),
            'total_players': stats.get('unique_players', 0),
            'recent_games': recent_games,
            'top_players': top_players
        }
        
        logger.info("Homepage data prepared successfully", extra={
            "source_function": "prepare_homepage_data",
            "source_module": "web_service",
            "context": {
                "total_games": homepage_data['total_games'],
                "total_players": homepage_data['total_players'],
                "recent_games_count": len(recent_games),
                "top_players_count": len(top_players)
            }
        })
        
        # Log business event for analytics
        log_business_event('homepage_data_prepared',
                          total_games=homepage_data['total_games'],
                          total_players=homepage_data['total_players'])
        
        return homepage_data
        
    except Exception as e:
        logger.error("Failed to prepare homepage data", extra={
            "source_function": "prepare_homepage_data",
            "source_module": "web_service",
            "error_code": "HOMEPAGE_DATA_ERROR",
            "context": {"exception_message": str(e)}
        })
        raise

@log_function_execution(log_level=logging.INFO)
def prepare_all_players_data():
    """Get all players data for the players index page with structured logging."""
    logger.info("Preparing all players data", extra={
        "source_function": "prepare_all_players_data",
        "source_module": "web_service"
    })
    
    try:
        players_list = get_all_players()
        
        result = {'players': players_list}
        
        logger.info("All players data prepared successfully", extra={
            "source_function": "prepare_all_players_data",
            "source_module": "web_service",
            "context": {"players_count": len(players_list)}
        })
        
        # Log business event
        log_business_event('all_players_data_prepared', 
                          players_count=len(players_list))
        
        return result
        
    except Exception as e:
        logger.error("Error getting all players data", extra={
            "source_function": "prepare_all_players_data",
            "source_module": "web_service",
            "error_code": "ALL_PLAYERS_DATA_ERROR",
            "context": {"exception_message": str(e)}
        })
        return {'players': []}

# =============================================================================
# Web-Specific Request Handlers
# =============================================================================

def process_player_profile_request(encoded_player_code):
    """Handle logic for player profile requests with redirect handling."""
    player_code = decode_player_tag(encoded_player_code)
    template_data = prepare_standard_player_template_data(player_code, encoded_player_code)
    
    if 'redirect_to' in template_data:
        return {'redirect': True, 'url': f"/player/{template_data['redirect_encoded']}"}
    
    return {'redirect': False, 'data': template_data}

def process_player_detailed_request(encoded_player_code):
    """Handle logic for detailed player profile requests with redirect handling."""
    player_code = decode_player_tag(encoded_player_code)
    template_data = prepare_standard_player_template_data(player_code, encoded_player_code)
    
    if 'redirect_to' in template_data:
        return {'redirect': True, 'url': f"/player/{template_data['redirect_encoded']}/detailed"}
    
    return {'redirect': False, 'data': template_data}