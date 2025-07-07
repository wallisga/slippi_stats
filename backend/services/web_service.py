"""
Web Service - Business Logic for Web Page Rendering

FINAL VERSION: Now properly handles character data and names
"""

import logging
from flask import abort
from datetime import datetime

# NEW: Use the simplified db layer
from backend.db import execute_query, connection, sql_manager
from backend.utils import (
    encode_player_tag, decode_player_tag, get_error_template_data,
    parse_player_data_from_game, find_player_in_game_data,
    safe_get_player_field, process_raw_games_for_player,
    find_flexible_player_matches, extract_player_stats_from_games,
    process_recent_games_data, calculate_win_rate
)
from backend.config import get_config

config = get_config()
logger = logging.getLogger('SlippiServer')


def prepare_homepage_data():
    """Prepare data for the homepage template."""
    try:
        # Use execute_query instead of old database functions
        total_games = execute_query('games', 'count_all', fetch_one=True)
        
        # Try the new count_unique_players, fallback to unique_players
        try:
            total_players = execute_query('stats', 'count_unique_players', fetch_one=True)
        except:
            total_players = execute_query('stats', 'unique_players', fetch_one=True)
        
        recent_games = execute_query('games', 'select_recent', (10,))
        
        # Get top players - try new query, fallback to processing if needed
        try:
            top_players_raw = execute_query('stats', 'top_players_by_winrate', (5, 10))
        except:
            # Fallback: use all players and filter
            all_players = execute_query('stats', 'all_players_with_stats')
            top_players_raw = sorted(all_players, key=lambda x: x.get('win_rate', 0), reverse=True)[:10]
        
        # Process recent games for display
        processed_recent = []
        for game in recent_games:
            try:
                player_data = game.get('player_data', '[]')
                if isinstance(player_data, str):
                    import json
                    player_data = json.loads(player_data)
                
                # Extract player names for display
                players = []
                for player in player_data:
                    if isinstance(player, dict):
                        tag = player.get('player_tag', 'Unknown')
                        char = player.get('character_name', 'Unknown')
                        players.append(f"{tag} ({char})")
                
                processed_recent.append({
                    'game_id': game['game_id'],
                    'start_time': game['start_time'],
                    'players': players[:2],  # Show first 2 players
                    'player_count': len(players)
                })
            except Exception as e:
                logger.warning(f"Error processing recent game {game.get('game_id')}: {str(e)}")
                continue
        
        # Process top players
        top_players = []
        for player in top_players_raw:
            try:
                player_tag = player.get('player_tag', '')
                top_players.append({
                    'player_tag': player_tag,
                    'encoded_tag': encode_player_tag(player_tag),
                    'total_games': player.get('total_games', 0),
                    'win_rate': round(player.get('win_rate', 0), 1)
                })
            except Exception as e:
                logger.warning(f"Error processing top player: {str(e)}")
                continue
        
        return {
            'total_games': total_games['count'] if total_games else 0,
            'total_players': total_players['count'] if total_players else 0,
            'recent_games': processed_recent,
            'top_players': top_players
        }
    except Exception as e:
        logger.error(f"Error preparing homepage data: {str(e)}")
        return {
            'total_games': 0,
            'total_players': 0,
            'recent_games': [],
            'top_players': []
        }


def prepare_all_players_data():
    """Prepare data for the all players page - FINAL VERSION with character support."""
    try:
        # Use execute_query to get all players with their stats
        try:
            players_raw = execute_query('stats', 'all_players_with_stats')
        except Exception as e:
            logger.error(f"Failed to get all_players_with_stats: {e}")
            # Fallback: return empty for now
            return {
                'players': [],
                'total_count': 0
            }
        
        # DEBUG: Log what we got
        print(f"DEBUG: Got {len(players_raw)} players from DB")
        if players_raw:
            print(f"DEBUG: First player: {players_raw[0]}")
        
        players = []
        for player in players_raw:
            try:
                player_tag = player.get('player_tag', '')
                win_rate_percent = player.get('win_rate', 0)
                most_played_character = player.get('most_played_character')
                
                # FINAL VERSION: Use exact field names that template expects
                player_data = {
                    # Template uses: {{ player.code }}
                    'code': player_tag,
                    
                    # Template uses: {{ player.name }} 
                    # FIXED: Use the actual player tag as the display name for now
                    # In the future, you could add a separate display_name field
                    'name': player_tag,
                    
                    # Template uses: {{ player.games }}
                    'games': player.get('total_games', 0),
                    
                    # Template uses: {{ player.code_encoded }}
                    'code_encoded': encode_player_tag(player_tag),
                    
                    # Template uses: {{ (player.win_rate * 100) | round(1) }}% 
                    # So it expects win_rate as decimal (0.6 = 60%)
                    'win_rate': win_rate_percent / 100.0,  # Convert 62.36 -> 0.6236
                    
                    # FIXED: Character data for icons component
                    'most_played_character': most_played_character,
                    
                    # Additional data for potential use
                    'wins': player.get('wins', 0),
                    'losses': player.get('total_games', 0) - player.get('wins', 0),
                    'last_game': player.get('last_game', 'Unknown')
                }
                
                players.append(player_data)
                
            except Exception as e:
                logger.warning(f"Error processing player {player.get('player_tag')}: {str(e)}")
                continue
        
        # Sort by total games (most active first)
        players.sort(key=lambda x: x['games'], reverse=True)
        
        print(f"DEBUG: Processed {len(players)} players successfully")
        if players:
            print(f"DEBUG: First processed player: {players[0]}")
        
        return {
            'players': players,
            'total_count': len(players)
        }
    except Exception as e:
        logger.error(f"Error preparing all players data: {str(e)}")
        return {
            'players': [],
            'total_count': 0
        }


def process_player_profile_request(encoded_player_code):
    """Process a player profile page request with error handling."""
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        
        # Get player games
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            logger.info(f"No games found for player: {player_code}")
            abort(404)
        
        # Process games using utils
        processed_games = process_raw_games_for_player(games, player_code)
        
        if not processed_games:
            logger.info(f"No processed games for player: {player_code}")
            abort(404)
        
        # Prepare template data
        template_data = prepare_standard_player_template_data(player_code, encoded_player_code)
        template_data['games'] = processed_games[:20]  # Show last 20 games
        
        return template_data
    except Exception as e:
        logger.error(f"Error processing player profile request for {encoded_player_code}: {str(e)}")
        abort(500)


def process_player_detailed_request(encoded_player_code):
    """Process a detailed player page request with advanced stats."""
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        
        # Get player games
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            abort(404)
        
        # Process games
        processed_games = process_raw_games_for_player(games, player_code)
        
        if not processed_games:
            abort(404)
        
        # Calculate detailed statistics
        total_games = len(processed_games)
        wins = len([g for g in processed_games if g.get('result') == 'Win'])
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Character usage analysis
        character_stats = {}
        opponent_stats = {}
        stage_stats = {}
        
        for game in processed_games:
            # Character analysis
            char = game.get('character_name', 'Unknown')
            if char not in character_stats:
                character_stats[char] = {'games': 0, 'wins': 0}
            character_stats[char]['games'] += 1
            if game.get('result') == 'Win':
                character_stats[char]['wins'] += 1
            
            # Opponent analysis
            opp = game.get('opponent_tag', 'Unknown')
            if opp not in opponent_stats:
                opponent_stats[opp] = {'games': 0, 'wins': 0}
            opponent_stats[opp]['games'] += 1
            if game.get('result') == 'Win':
                opponent_stats[opp]['wins'] += 1
            
            # Stage analysis
            stage = game.get('stage_name', 'Unknown')
            if stage not in stage_stats:
                stage_stats[stage] = {'games': 0, 'wins': 0}
            stage_stats[stage]['games'] += 1
            if game.get('result') == 'Win':
                stage_stats[stage]['wins'] += 1
        
        # Calculate win rates
        for stats in [character_stats, opponent_stats, stage_stats]:
            for stat_data in stats.values():
                stat_data['win_rate'] = (stat_data['wins'] / stat_data['games']) * 100 if stat_data['games'] > 0 else 0
        
        # Sort by usage (games played)
        sorted_characters = sorted(character_stats.items(), key=lambda x: x[1]['games'], reverse=True)
        sorted_opponents = sorted(opponent_stats.items(), key=lambda x: x[1]['games'], reverse=True)
        sorted_stages = sorted(stage_stats.items(), key=lambda x: x[1]['games'], reverse=True)
        
        return {
            'player_tag': player_code,
            'encoded_tag': encoded_player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': round(win_rate, 1),
            'character_breakdown': sorted_characters,
            'opponent_breakdown': sorted_opponents[:10],  # Top 10 opponents
            'stage_breakdown': sorted_stages,
            'recent_games': processed_games[:10]
        }
    except Exception as e:
        logger.error(f"Error processing detailed request for {encoded_player_code}: {str(e)}")
        abort(500)


def prepare_standard_player_template_data(player_tag, encoded_player_code):
    """Prepare standard template data for player pages."""
    try:
        # Get player games
        games = execute_query('games', 'select_by_player', (player_tag,))
        
        if not games:
            return {'error': 'Player not found'}
        
        # Process games using utils
        processed_games = process_raw_games_for_player(games, player_tag)
        
        # Calculate basic stats
        total_games = len(processed_games)
        wins = len([g for g in processed_games if g.get('result') == 'Win'])
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Get most used character
        character_usage = {}
        for game in processed_games:
            char = game.get('character_name', 'Unknown')
            character_usage[char] = character_usage.get(char, 0) + 1
        
        most_used_character = max(character_usage.items(), key=lambda x: x[1])[0] if character_usage else 'Unknown'
        
        # Get recent opponents
        recent_opponents = []
        for game in processed_games[:10]:
            opp = game.get('opponent_tag')
            if opp and opp not in recent_opponents:
                recent_opponents.append(opp)
        
        return {
            'player_tag': player_tag,
            'encoded_tag': encoded_player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': round(win_rate, 1),
            'most_used_character': most_used_character,
            'character_usage_count': character_usage.get(most_used_character, 0),
            'recent_opponents': recent_opponents[:5],
            'last_game_date': processed_games[0].get('start_time') if processed_games else None
        }
    except Exception as e:
        logger.error(f"Error preparing template data for {player_tag}: {str(e)}")
        return {'error': str(e)}


# Helper functions that call the database layer
def get_player_games(player_code, limit=None):
    """Get games for a specific player (web service helper)."""
    try:
        if limit:
            games = execute_query('games', 'select_by_player_limit', (player_code, limit))
        else:
            games = execute_query('games', 'select_by_player', (player_code,))
        
        return games
    except Exception as e:
        logger.error(f"Error getting games for player {player_code}: {str(e)}")
        return []


def get_recent_games(limit=10):
    """Get recent games for homepage display."""
    try:
        return execute_query('games', 'select_recent', (limit,))
    except Exception as e:
        logger.error(f"Error getting recent games: {str(e)}")
        return []


def get_top_players(limit=10):
    """Get top players by win rate."""
    try:
        return execute_query('stats', 'top_players_by_winrate', (5, limit))  # Min 5 games
    except Exception as e:
        logger.error(f"Error getting top players: {str(e)}")
        return []


def get_all_players():
    """Get all players with basic stats."""
    try:
        return execute_query('stats', 'all_players_with_stats')
    except Exception as e:
        logger.error(f"Error getting all players: {str(e)}")
        return []


def find_player_matches(search_term):
    """Find players matching a search term."""
    try:
        return execute_query('stats', 'search_players', (f'%{search_term}%',))
    except Exception as e:
        logger.error(f"Error searching for players with term '{search_term}': {str(e)}")
        return []


def calculate_player_stats(games, player_code):
    """Calculate comprehensive player statistics from games list."""
    if not games:
        return None
    
    try:
        # Use utils for processing
        processed_games = process_raw_games_for_player(games, player_code)
        
        total_games = len(processed_games)
        wins = len([g for g in processed_games if g.get('result') == 'Win'])
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Character usage
        character_usage = {}
        for game in processed_games:
            char = game.get('character_name', 'Unknown')
            character_usage[char] = character_usage.get(char, 0) + 1
        
        # Most common opponent
        opponent_usage = {}
        for game in processed_games:
            opp = game.get('opponent_tag')
            if opp:
                opponent_usage[opp] = opponent_usage.get(opp, 0) + 1
        
        most_common_opponent = max(opponent_usage.items(), key=lambda x: x[1])[0] if opponent_usage else None
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': round(win_rate, 1),
            'character_usage': character_usage,
            'most_used_character': max(character_usage.items(), key=lambda x: x[1])[0] if character_usage else 'Unknown',
            'most_common_opponent': most_common_opponent,
            'games_vs_common_opponent': opponent_usage.get(most_common_opponent, 0) if most_common_opponent else 0
        }
    except Exception as e:
        logger.error(f"Error calculating player stats: {str(e)}")
        return None