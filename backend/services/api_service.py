"""
API Service - Business Logic for JSON API Responses

COMPLETE VERSION: Includes all functions needed by API routes
Updated to use the new backend/db/ layer instead of backend.database
"""

import logging
import json
import uuid
from datetime import datetime

# NEW: Use the simplified db layer
from backend.db import execute_query, connection, sql_manager
from backend.utils import (
    process_raw_games_for_player
)
from backend.config import get_config

config = get_config()
logger = logging.getLogger('SlippiServer')


def process_server_statistics():
    """Get server statistics for API response."""
    try:
        # Use simpler queries that definitely exist
        total_clients = execute_query('clients', 'count_all', fetch_one=True)
        total_games = execute_query('games', 'count_all', fetch_one=True)
        
        # Use existing unique_players query instead of count_unique_players
        try:
            unique_players = execute_query('stats', 'count_unique_players', fetch_one=True)
        except:
            # Fallback if stats query doesn't work
            unique_players = {'count': 0}
        
        return {
            'total_clients': total_clients['count'] if total_clients else 0,
            'total_games': total_games['count'] if total_games else 0,
            'unique_players': unique_players.get('count', 0) if unique_players else 0,
            'server_status': 'operational'
        }
    except Exception as e:
        logger.error(f"Error getting server statistics: {str(e)}")
        return {
            'total_clients': 0,
            'total_games': 0,
            'unique_players': 0,
            'server_status': 'error'
        }


def process_player_basic_stats(player_code):
    """Get basic player statistics for API response - FIXED FORMAT."""
    if not player_code:
        return None
    
    try:
        # Get games with correct SQL parameters
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            return None
        
        processed_games = process_raw_games_for_player(games, player_code)
        
        if not processed_games:
            return None
        
        # Calculate basic statistics
        total_games = len(processed_games)
        wins = len([g for g in processed_games if g.get('result') == 'Win'])
        win_rate_decimal = wins / total_games if total_games > 0 else 0
        
        return {
            'player_code': player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': win_rate_decimal * 100,  # As percentage for display
            'overall_winrate': win_rate_decimal  # As decimal for calculations
        }
        
    except Exception as e:
        logger.error(f"Error getting basic stats for {player_code}: {str(e)}")
        return None


def validate_api_key(api_key):
    """Validate API key and return client info."""
    if not api_key:
        return None
    
    try:
        result = execute_query('api_keys', 'select_by_key', (api_key,), fetch_one=True)
        
        if not result:
            return None
        
        # Check if key is expired
        if result.get('expires_at'):
            expires_at = datetime.fromisoformat(result['expires_at'])
            if datetime.now() > expires_at:
                return None
        
        return result
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None


def process_client_registration(client_data, registration_key):
    """Process client registration request."""
    try:
        # Validate registration key if configured
        if hasattr(config, 'REGISTRATION_SECRET') and config.REGISTRATION_SECRET:
            if registration_key != config.REGISTRATION_SECRET:
                return {'error': 'Invalid registration key'}, 401
        
        result = register_or_update_client(client_data)
        return result
    except Exception as e:
        logger.error(f"Error processing client registration: {str(e)}")
        return {'error': str(e)}


def register_or_update_client(client_data):
    """Register a new client or update existing client info."""
    try:
        client_id = client_data.get('client_id')
        hostname = client_data.get('hostname', 'Unknown')
        platform = client_data.get('platform', 'Unknown')
        version = client_data.get('version', '1.0.0')
        
        if not client_id:
            client_id = str(uuid.uuid4())
        
        # Check if client exists
        existing = execute_query('clients', 'select_by_id', (client_id,), fetch_one=True)
        
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            
            if existing:
                # Update existing client
                query = sql_manager.get_query('clients', 'update_info')
                cursor.execute(query, (hostname, platform, version, datetime.now().isoformat(), client_id))
            else:
                # Insert new client
                query = sql_manager.get_query('clients', 'insert_client')
                cursor.execute(query, (client_id, hostname, platform, version, 
                                     datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
        
        return {
            'client_id': client_id,
            'status': 'updated' if existing else 'registered'
        }
    except Exception as e:
        logger.error(f"Error registering/updating client: {str(e)}")
        raise


def get_player_detailed_stats(player_code, filters=None):
    """Get detailed player statistics with optional filtering - FIXED RESPONSE FORMAT."""
    if not player_code:
        return None
    
    try:
        # Get games with correct SQL parameters
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            return None
        
        processed_games = process_raw_games_for_player(games, player_code)
        
        # Apply filters if provided
        if filters:
            processed_games = apply_game_filters(processed_games, filters)
        
        if not processed_games:
            return None
        
        # Calculate detailed statistics
        total_games = len(processed_games)
        wins = len([g for g in processed_games if g.get('result') == 'Win'])
        win_rate_decimal = wins / total_games if total_games > 0 else 0
        
        # Character breakdown
        character_stats = {}
        opponent_stats = {}
        stage_stats = {}
        date_stats = {}
        opponent_character_stats = {}  # FIXED: Added this missing variable
        
        for game in processed_games:
            # FIXED: Character stats - access nested player data
            char = game.get('player', {}).get('character_name', 'Unknown')
            if char not in character_stats:
                character_stats[char] = {'games': 0, 'wins': 0}
            character_stats[char]['games'] += 1
            if game.get('result') == 'Win':
                character_stats[char]['wins'] += 1
            
            # FIXED: Opponent stats - access nested opponent data
            opp = game.get('opponent', {}).get('player_tag', 'Unknown')
            if opp not in opponent_stats:
                opponent_stats[opp] = {'games': 0, 'wins': 0}
            opponent_stats[opp]['games'] += 1
            if game.get('result') == 'Win':
                opponent_stats[opp]['wins'] += 1
            
            # Stage stats
            stage = game.get('stage_id', 'Unknown')
            if stage not in stage_stats:
                stage_stats[stage] = {'games': 0, 'wins': 0}
            stage_stats[stage]['games'] += 1
            if game.get('result') == 'Win':
                stage_stats[stage]['wins'] += 1
            
            # FIXED: Opponent character stats - access nested opponent data
            opp_char = game.get('opponent', {}).get('character_name', 'Unknown')
            if opp_char not in opponent_character_stats:
                opponent_character_stats[opp_char] = {'games': 0, 'wins': 0}
            opponent_character_stats[opp_char]['games'] += 1
            if game.get('result') == 'Win':
                opponent_character_stats[opp_char]['wins'] += 1
            
            # Date stats for win rate over time
            try:
                game_date = game.get('start_time', '')[:10]  # Get YYYY-MM-DD
                if game_date:
                    if game_date not in date_stats:
                        date_stats[game_date] = {'games': 0, 'wins': 0}
                    date_stats[game_date]['games'] += 1
                    if game.get('result') == 'Win':
                        date_stats[game_date]['wins'] += 1
            except:
                pass  # Skip invalid dates
        
        # Calculate win rates and convert to frontend format
        character_breakdown_frontend = {}
        for char, stats in character_stats.items():
            win_rate = (stats['wins'] / stats['games']) if stats['games'] > 0 else 0
            character_breakdown_frontend[char] = {
                'games': stats['games'],
                'wins': stats['wins'],
                'win_rate': win_rate  # As decimal for frontend
            }
        
        opponent_breakdown_frontend = {}
        for opp, stats in opponent_stats.items():
            win_rate = (stats['wins'] / stats['games']) if stats['games'] > 0 else 0
            opponent_breakdown_frontend[opp] = {
                'games': stats['games'],
                'wins': stats['wins'],
                'win_rate': win_rate  # As decimal for frontend
            }
        
        stage_breakdown_frontend = {}
        for stage, stats in stage_stats.items():
            win_rate = (stats['wins'] / stats['games']) if stats['games'] > 0 else 0
            stage_breakdown_frontend[stage] = {
                'games': stats['games'],
                'wins': stats['wins'],
                'win_rate': win_rate  # As decimal for frontend
            }
        
        # FIXED: Process opponent character stats for frontend (this was missing!)
        opponent_character_breakdown_frontend = {}
        for opp_char, stats in opponent_character_stats.items():
            win_rate = (stats['wins'] / stats['games']) if stats['games'] > 0 else 0
            opponent_character_breakdown_frontend[opp_char] = {
                'games': stats['games'],
                'wins': stats['wins'],
                'win_rate': win_rate  # As decimal for frontend
            }
        
        # Process date stats for time chart
        date_breakdown_frontend = {}
        for date, stats in date_stats.items():
            win_rate = (stats['wins'] / stats['games']) if stats['games'] > 0 else 0
            date_breakdown_frontend[date] = {
                'games': stats['games'],
                'wins': stats['wins'],
                'win_rate': win_rate  # As decimal for frontend
            }
        
        # FIXED: Return data in format that frontend expects
        return {
            'player_code': player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': win_rate_decimal * 100,  # Frontend expects percentage for display
            'overall_winrate': win_rate_decimal,  # Frontend expects decimal for calculations
            
            # Frontend expects these specific field names
            'character_stats': character_breakdown_frontend,
            'opponent_stats': opponent_breakdown_frontend,
            'stage_stats': stage_breakdown_frontend,
            'date_stats': date_breakdown_frontend,
            
            # FIXED: Now this variable actually exists!
            'opponent_character_stats': opponent_character_breakdown_frontend,
            
            # Keep original format for compatibility
            'character_breakdown': character_breakdown_frontend,
            'opponent_breakdown': opponent_breakdown_frontend,
            'stage_breakdown': stage_breakdown_frontend,
            
            'recent_games': processed_games[:20],  # Latest 20 games
            'filters_applied': filters or {}
        }
        
    except Exception as e:
        logger.error(f"Error getting detailed stats for {player_code}: {str(e)}")
        return None

def process_detailed_player_data(player_code, character='all', opponent='all', stage='all', limit=100, opponent_character='all'):
    """
    Process detailed player data with comprehensive filtering.
    
    UPDATED: Added opponent_character parameter to match frontend expectations.
    The frontend JavaScript sends this filter and expects it to work.
    
    Args:
        player_code (str): Player tag to analyze
        character (str): Filter by player's character (default: 'all')
        opponent (str): Filter by opponent player tag (default: 'all') 
        stage (str): Filter by stage (default: 'all')
        limit (int): Maximum number of games to return (default: 100)
        opponent_character (str): Filter by opponent's character (default: 'all') - NEW
    
    Returns:
        dict: Comprehensive player analysis with filtered data
        
    Example frontend call:
        POST /api/player/TEST%23123/detailed
        {
            "character": "Fox",
            "opponent": "all", 
            "opponent_character": "Falco",
            "stage": "all",
            "limit": 50
        }
    """
    try:
        logger.info(f"🔍 Processing detailed player data for: {player_code}")
        logger.info(f"   📊 Filters - Character: {character}, Opponent: {opponent}, OpponentChar: {opponent_character}, Stage: {stage}, Limit: {limit}")
        
        # Validate input parameters
        validated_data = _validate_detailed_player_inputs(player_code, character, opponent, stage, limit, opponent_character)
        
        # Get base player data
        player_games = _get_player_games_for_analysis(validated_data['player_code'])
        
        # Apply all filters including opponent_character
        filtered_games = _apply_comprehensive_filters(
            player_games, 
            validated_data['character'], 
            validated_data['opponent'], 
            validated_data['stage'],
            validated_data['opponent_character']  # NEW: Include opponent character filter
        )
        
        # Limit results
        limited_games = filtered_games[:validated_data['limit']]
        
        # Calculate comprehensive statistics
        analysis_result = _calculate_comprehensive_analysis(filtered_games, player_code)
        
        # Add filter metadata for frontend
        analysis_result['applied_filters'] = {
            'character': character,
            'opponent': opponent,
            'opponent_character': opponent_character,  # NEW: Include in response
            'stage': stage,
            'limit': limit
        }
        
        # Add filter options for frontend dropdowns/checkboxes
        analysis_result['filter_options'] = _generate_filter_options(player_games)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error processing detailed player data for {player_code}: {str(e)}")
        raise

def _validate_detailed_player_inputs(player_code, character, opponent, stage, limit, opponent_character):
    """Validate all input parameters including new opponent_character."""
    if not player_code:
        raise ValueError("Player code is required")
    
    # Validate limit
    if not isinstance(limit, int) or limit < 1:
        limit = 100
    elif limit > 1000:  # Prevent excessive queries
        limit = 1000
    
    return {
        'player_code': player_code,
        'character': character or 'all',
        'opponent': opponent or 'all',
        'stage': stage or 'all',
        'limit': limit,
        'opponent_character': opponent_character or 'all'  # NEW: Include opponent character
    }

def _apply_comprehensive_filters(games, character_filter, opponent_filter, stage_filter, opponent_character_filter):
    """
    Apply all filters to the game list.
    
    FIXED: Use correct data structure for character access.
    """
    filtered_games = games
    initial_count = len(filtered_games)
    
    logger.info(f"   📊 Starting with {initial_count} games, applying filters...")
    
    # FILTER 1: Player Character - FIXED data access
    if character_filter and character_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(character_filter, g.get('player', {}).get('character_name', 'Unknown'), 'character')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Character filter: {before_count} → {after_count} games ({character_filter})")
    
    # FILTER 2: Opponent Tag  
    if opponent_filter and opponent_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(opponent_filter, g.get('opponent', {}).get('player_tag', 'Unknown'), 'opponent_tag')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Opponent filter: {before_count} → {after_count} games ({opponent_filter})")
    
    # FILTER 3: Opponent Character
    if opponent_character_filter and opponent_character_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(opponent_character_filter, g.get('opponent', {}).get('character_name', 'Unknown'), 'opponent_char')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Opponent character filter: {before_count} → {after_count} games ({opponent_character_filter})")
    
    # FILTER 4: Stage
    if stage_filter and stage_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(stage_filter, str(g.get('stage_id', 'Unknown')), 'stage')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Stage filter: {before_count} → {after_count} games ({stage_filter})")
    
    final_count = len(filtered_games)
    logger.info(f"   ✅ Final result: {initial_count} → {final_count} games after all filters")
    
    return filtered_games

def _generate_filter_options(all_games):
    """
    Generate filter options for frontend dropdowns/checkboxes.
    
    FIXED: Use correct data structure for character access.
    """
    characters = set()
    opponents = set()
    opponent_characters = set()
    stages = set()
    
    for game in all_games:
        # FIXED: Player characters - use correct nested structure
        char = game.get('player', {}).get('character_name')
        if char and char != 'Unknown':
            characters.add(char)
        
        # Opponent info
        opponent = game.get('opponent', {})
        opp_tag = opponent.get('player_tag')
        if opp_tag and opp_tag != 'Unknown':
            opponents.add(opp_tag)
        
        # FIXED: Opponent characters - use correct nested structure
        opp_char = opponent.get('character_name')
        if opp_char and opp_char != 'Unknown':
            opponent_characters.add(opp_char)
        
        # Stages
        stage = game.get('stage_name', game.get('stage_id'))
        if stage and stage != 'Unknown':
            stages.add(str(stage))
    
    return {
        'characters': sorted(list(characters)),
        'opponents': sorted(list(opponents)),
        'opponent_characters': sorted(list(opponent_characters)),
        'stages': sorted(list(stages))
    }


def process_paginated_player_games(player_code, page=1, per_page=20):
    """Get paginated games for a player."""
    try:
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            return {
                'games': [],
                'page': page,
                'per_page': per_page,
                'total': 0,
                'total_pages': 0
            }
        
        # Process games
        processed_games = process_raw_games_for_player(games, player_code)
        
        # Calculate pagination
        total = len(processed_games)
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_games = processed_games[start:end]
        
        return {
            'games': paginated_games,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
        
    except Exception as e:
        logger.error(f"Error getting paginated games for {player_code}: {str(e)}")
        return {
            'games': [],
            'page': page,
            'per_page': per_page,
            'total': 0,
            'total_pages': 0,
            'error': str(e)
        }


def get_client_files(client_id, limit=50):
    """Get files uploaded by a client."""
    try:
        files = execute_query('files', 'select_by_client', (client_id, limit))
        
        # Convert to JSON-serializable format
        files_data = []
        for file_record in files:
            files_data.append({
                'file_id': file_record['file_id'],
                'file_hash': file_record['file_hash'],
                'original_filename': file_record['original_filename'],
                'file_size': file_record['file_size'],
                'upload_date': file_record['upload_date'],
                'metadata': json.loads(file_record['metadata']) if file_record.get('metadata') else {}
            })
        
        return {
            'files': files_data,
            'count': len(files_data)
        }
    except Exception as e:
        logger.error(f"Error getting files for client {client_id}: {str(e)}")
        return {'error': str(e)}


def get_file_details(file_id, client_id):
    """Get details about a specific file."""
    try:
        file_record = execute_query('files', 'select_by_id', (file_id,), fetch_one=True)
        
        if not file_record:
            return None
        
        # Check if client owns this file
        if file_record['client_id'] != client_id:
            return {'error': 'Access denied'}
        
        return {
            'file_id': file_record['file_id'],
            'file_hash': file_record['file_hash'],
            'original_filename': file_record['original_filename'],
            'file_size': file_record['file_size'],
            'upload_date': file_record['upload_date'],
            'metadata': json.loads(file_record['metadata']) if file_record.get('metadata') else {}
        }
    except Exception as e:
        logger.error(f"Error getting file details for {file_id}: {str(e)}")
        return {'error': str(e)}


def get_admin_file_stats():
    """Get file storage statistics for admin endpoint."""
    try:
        # Get basic file statistics
        total_files = execute_query('files', 'count_all', fetch_one=True)
        
        # Calculate total file size
        try:
            file_stats = execute_query('stats', 'file_stats_total', fetch_one=True)
            total_size = file_stats['total_size'] if file_stats else 0
        except:
            total_size = 0
        
        return {
            'total_files': total_files['count'] if total_files else 0,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0
        }
    except Exception as e:
        logger.error(f"Error getting admin file stats: {str(e)}")
        return {'error': str(e)}

# CRITICAL FIX: Replace the apply_game_filters function in your api_service.py

def apply_game_filters(games, filters):
    """
    Apply filters to a list of processed games using AND logic.
    
    FIXED: Use correct data structure for character access.
    The games come from process_raw_games_for_player which creates nested structure.
    
    Args:
        games (list): List of processed game dictionaries
        filters (dict): Filter criteria with arrays or 'all'
        
    Returns:
        list: Filtered games that match ALL criteria
    """
    if not games or not filters:
        logger.info("No games or no filters provided")
        return games
    
    logger.info(f"🔍 Starting filter process with {len(games)} games")
    logger.info(f"🔍 Filters received: {filters}")
    
    # Debug: Log the structure of the first game to understand data format
    if games:
        logger.info(f"🔍 Sample game structure: {games[0]}")
    
    filtered_games = games
    original_count = len(filtered_games)
    
    # Helper function to check if filter matches
    def filter_matches(filter_value, actual_value, filter_name="unknown"):
        if filter_value == 'all':
            return True
        if isinstance(filter_value, list):
            matches = actual_value in filter_value
            if not matches:
                logger.debug(f"   ❌ {filter_name}: '{actual_value}' not in {filter_value[:3]}...")
            return matches
        matches = actual_value == filter_value
        if not matches:
            logger.debug(f"   ❌ {filter_name}: '{actual_value}' != '{filter_value}'")
        return matches
    
    # FILTER 1: Player Character - FIXED to use correct nested structure
    character_filter = filters.get('character')
    if character_filter and character_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(character_filter, g.get('player', {}).get('character_name', 'Unknown'), 'player_char')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Character filter: {before_count} → {after_count} games ({character_filter})")
    
    # FILTER 2: Opponent Tag  
    opponent_filter = filters.get('opponent')
    if opponent_filter and opponent_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(opponent_filter, g.get('opponent', {}).get('player_tag', 'Unknown'), 'opponent_tag')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Opponent filter: {before_count} → {after_count} games ({len(opponent_filter) if isinstance(opponent_filter, list) else opponent_filter} opponents)")
    
    # FILTER 3: Opponent Character
    opponent_char_filter = filters.get('opponent_character')
    if opponent_char_filter and opponent_char_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(opponent_char_filter, g.get('opponent', {}).get('character_name', 'Unknown'), 'opponent_char')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Opponent character filter: {before_count} → {after_count} games ({opponent_char_filter})")
    
    # FILTER 4: Stage (if implemented)
    stage_filter = filters.get('stage')
    if stage_filter and stage_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(stage_filter, str(g.get('stage_id', 'Unknown')), 'stage')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Stage filter: {before_count} → {after_count} games ({stage_filter})")
    
    # FILTER 5: Result (Win/Loss)
    result_filter = filters.get('result')
    if result_filter and result_filter != 'all':
        before_count = len(filtered_games)
        filtered_games = [
            g for g in filtered_games 
            if filter_matches(result_filter, g.get('result', 'Unknown'), 'result')
        ]
        after_count = len(filtered_games)
        logger.info(f"   📊 Result filter: {before_count} → {after_count} games ({result_filter})")
    
    # FILTER 6: Date range (unchanged)
    if filters.get('date_from') or filters.get('date_to'):
        from datetime import datetime
        
        date_from = None
        date_to = None
        
        try:
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
        except ValueError:
            logger.warning(f"Invalid date format in filters: {filters}")
        
        if date_from or date_to:
            before_count = len(filtered_games)
            date_filtered = []
            for game in filtered_games:
                try:
                    game_date = datetime.fromisoformat(game.get('start_time', '').replace('Z', '+00:00'))
                    
                    if date_from and game_date < date_from:
                        continue
                    if date_to and game_date > date_to:
                        continue
                    
                    date_filtered.append(game)
                except ValueError:
                    # Skip games with invalid dates
                    continue
            
            filtered_games = date_filtered
            after_count = len(filtered_games)
            logger.info(f"   📊 Date filter: {before_count} → {after_count} games")
    
    final_count = len(filtered_games)
    logger.info(f"✅ Final result: {original_count} → {final_count} games after filtering")
    
    return filtered_games

def _get_player_games_for_analysis(player_code):
    """Get and process player games for analysis."""
    try:
        # Get raw games from database
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            logger.info(f"No games found for player: {player_code}")
            return []
        
        # Process games using utils
        processed_games = process_raw_games_for_player(games, player_code)
        
        if not processed_games:
            logger.info(f"No processed games for player: {player_code}")
            return []
        
        logger.info(f"Retrieved {len(processed_games)} games for analysis")
        return processed_games
        
    except Exception as e:
        logger.error(f"Error getting player games for analysis: {str(e)}")
        return []


def _calculate_comprehensive_analysis(filtered_games, player_code):
    """Calculate comprehensive analysis from filtered games."""
    if not filtered_games:
        return {
            'player_code': player_code,
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0,
            'overall_winrate': 0,
            'character_stats': {},
            'opponent_stats': {},
            'opponent_character_stats': {},
            'stage_stats': {},
            'date_stats': {},
            'recent_games': []
        }
    
    try:
        # Basic statistics
        total_games = len(filtered_games)
        wins = len([g for g in filtered_games if g.get('result') == 'Win'])
        win_rate_decimal = wins / total_games if total_games > 0 else 0
        
        # Initialize stat containers
        character_stats = {}
        opponent_stats = {}
        opponent_character_stats = {}
        stage_stats = {}
        date_stats = {}
        
        # Process each game for detailed statistics
        for game in filtered_games:
            # FIXED: Player character stats - use correct nested structure
            char = game.get('player', {}).get('character_name', 'Unknown')
            if char not in character_stats:
                character_stats[char] = {'games': 0, 'wins': 0}
            character_stats[char]['games'] += 1
            if game.get('result') == 'Win':
                character_stats[char]['wins'] += 1
            
            # FIXED: Opponent stats - use correct nested structure
            opponent = game.get('opponent', {})
            opp_tag = opponent.get('player_tag', 'Unknown')
            if opp_tag not in opponent_stats:
                opponent_stats[opp_tag] = {'games': 0, 'wins': 0}
            opponent_stats[opp_tag]['games'] += 1
            if game.get('result') == 'Win':
                opponent_stats[opp_tag]['wins'] += 1
            
            # FIXED: Opponent character stats - use correct nested structure
            opp_char = opponent.get('character_name', 'Unknown')
            if opp_char not in opponent_character_stats:
                opponent_character_stats[opp_char] = {'games': 0, 'wins': 0}
            opponent_character_stats[opp_char]['games'] += 1
            if game.get('result') == 'Win':
                opponent_character_stats[opp_char]['wins'] += 1
            
            # Stage stats - this may need fixing too depending on your data
            stage = game.get('stage_name', game.get('stage_id', 'Unknown'))
            if stage not in stage_stats:
                stage_stats[stage] = {'games': 0, 'wins': 0}
            stage_stats[stage]['games'] += 1
            if game.get('result') == 'Win':
                stage_stats[stage]['wins'] += 1
            
            # Date stats
            try:
                game_date = game.get('start_time', '')[:10]  # Get YYYY-MM-DD
                if game_date:
                    if game_date not in date_stats:
                        date_stats[game_date] = {'games': 0, 'wins': 0}
                    date_stats[game_date]['games'] += 1
                    if game.get('result') == 'Win':
                        date_stats[game_date]['wins'] += 1
            except:
                pass  # Skip invalid dates
        
        # Calculate win rates for all stat categories
        for stats_dict in [character_stats, opponent_stats, opponent_character_stats, stage_stats, date_stats]:
            for key, data in stats_dict.items():
                data['win_rate'] = data['wins'] / data['games'] if data['games'] > 0 else 0
        
        return {
            'player_code': player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': win_rate_decimal * 100,  # As percentage for display
            'overall_winrate': win_rate_decimal,  # As decimal for calculations
            'character_stats': character_stats,
            'opponent_stats': opponent_stats,
            'opponent_character_stats': opponent_character_stats,
            'stage_stats': stage_stats,
            'date_stats': date_stats,
            'recent_games': filtered_games[:20]  # Latest 20 games
        }
        
    except Exception as e:
        logger.error(f"Error calculating comprehensive analysis: {str(e)}")
        raise

def filter_matches(filter_value, actual_value, filter_name="unknown"):
    """Helper function to check if filter matches actual value."""
    if filter_value == 'all':
        return True
    if isinstance(filter_value, list):
        matches = actual_value in filter_value
        if not matches:
            logger.debug(f"   ❌ {filter_name}: '{actual_value}' not in {filter_value[:3]}...")
        return matches
    matches = actual_value == filter_value
    if not matches:
        logger.debug(f"   ❌ {filter_name}: '{actual_value}' != '{filter_value}'")
    return matches

def extract_filter_options(games):
    """
    Extract available filter options from games list.
    
    FIXED: Use correct data structure for character access.
    """
    characters = set()
    opponents = set()
    opponent_characters = set()
    stages = set()
    
    for game in games:
        # FIXED: Player characters - use correct nested structure
        char = game.get('player', {}).get('character_name')
        if char and char != 'Unknown':
            characters.add(char)
        
        # Opponent info
        opponent = game.get('opponent', {})
        opp_tag = opponent.get('player_tag')
        if opp_tag and opp_tag != 'Unknown':
            opponents.add(opp_tag)
        
        # FIXED: Opponent characters - use correct nested structure
        opp_char = opponent.get('character_name')
        if opp_char and opp_char != 'Unknown':
            opponent_characters.add(opp_char)
        
        # Stages
        stage = game.get('stage_name', game.get('stage_id'))
        if stage and stage != 'Unknown':
            stages.add(str(stage))
    
    return {
        'characters': sorted(list(characters)),
        'opponents': sorted(list(opponents)),
        'opponent_characters': sorted(list(opponent_characters)),
        'stages': sorted(list(stages))
    }

def calculate_filtered_stats(games, filter_options):
    """
    Calculate statistics for filtered games.
    
    FIXED: Use correct data structure for character access.
    """
    if not games:
        return {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'overall_winrate': 0,
            'character_breakdown': {},
            'opponent_breakdown': {},
            'opponent_character_breakdown': {}
        }
    
    # Basic stats
    total_games = len(games)
    wins = len([g for g in games if g.get('result') == 'Win'])
    win_rate = wins / total_games if total_games > 0 else 0
    
    # Character breakdown
    character_breakdown = {}
    opponent_breakdown = {}
    opponent_character_breakdown = {}
    
    for game in games:
        # FIXED: Character stats - use correct nested structure
        char = game.get('player', {}).get('character_name', 'Unknown')
        if char not in character_breakdown:
            character_breakdown[char] = {'games': 0, 'wins': 0}
        character_breakdown[char]['games'] += 1
        if game.get('result') == 'Win':
            character_breakdown[char]['wins'] += 1
        
        # FIXED: Opponent stats - use correct nested structure
        opponent = game.get('opponent', {})
        opp_tag = opponent.get('player_tag', 'Unknown')
        if opp_tag not in opponent_breakdown:
            opponent_breakdown[opp_tag] = {'games': 0, 'wins': 0}
        opponent_breakdown[opp_tag]['games'] += 1
        if game.get('result') == 'Win':
            opponent_breakdown[opp_tag]['wins'] += 1
        
        # FIXED: Opponent character stats - use correct nested structure
        opp_char = opponent.get('character_name', 'Unknown')
        if opp_char not in opponent_character_breakdown:
            opponent_character_breakdown[opp_char] = {'games': 0, 'wins': 0}
        opponent_character_breakdown[opp_char]['games'] += 1
        if game.get('result') == 'Win':
            opponent_character_breakdown[opp_char]['wins'] += 1
    
    # Calculate win rates
    for breakdown in [character_breakdown, opponent_breakdown, opponent_character_breakdown]:
        for key, data in breakdown.items():
            data['win_rate'] = data['wins'] / data['games'] if data['games'] > 0 else 0
    
    return {
        'total_games': total_games,
        'wins': wins,
        'losses': total_games - wins,
        'overall_winrate': win_rate,
        'character_breakdown': character_breakdown,
        'opponent_breakdown': opponent_breakdown,
        'opponent_character_breakdown': opponent_character_breakdown
    }