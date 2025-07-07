"""
API Service - Business Logic for JSON API Responses

COMPLETE VERSION: Includes all functions needed by API routes
Updated to use the new backend/db/ layer instead of backend.database
"""

import logging
import json
import secrets
import uuid
from datetime import datetime, timedelta
from flask import abort

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


def process_server_statistics():
    """Get server statistics for API response."""
    try:
        # Use simpler queries that definitely exist
        total_clients = execute_query('clients', 'count_all', fetch_one=True)
        total_games = execute_query('games', 'count_all', fetch_one=True)
        
        # Use existing unique_players query instead of count_unique_players
        try:
            unique_players = execute_query('stats', 'unique_players', fetch_one=True)
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
    """Get basic player statistics for API response."""
    if not player_code:
        return None
    
    try:
        # Direct query execution
        games = execute_query('games', 'select_by_player', (player_code,))
        
        if not games:
            return None
        
        # Use utils for data processing (unchanged)
        processed_games = process_raw_games_for_player(games, player_code)
        win_rate = calculate_win_rate(processed_games)
        
        # Extract character usage
        character_stats = {}
        for game in processed_games:
            char = game.get('character_name', 'Unknown')
            if char not in character_stats:
                character_stats[char] = {'games': 0, 'wins': 0}
            character_stats[char]['games'] += 1
            if game.get('result') == 'Win':
                character_stats[char]['wins'] += 1
        
        # Calculate character win rates
        for char_data in character_stats.values():
            char_data['win_rate'] = (char_data['wins'] / char_data['games']) * 100 if char_data['games'] > 0 else 0
        
        return {
            'player_code': player_code,
            'total_games': len(processed_games),
            'win_rate': round(win_rate, 2),
            'character_usage': character_stats,
            'recent_games': processed_games[:10]  # Last 10 games
        }
    except Exception as e:
        logger.error(f"Error processing player stats for {player_code}: {str(e)}")
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


def upload_games_for_client(client_id, games_data):
    """Process game upload for a specific client."""
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
                    existing_query = sql_manager.get_query('games', 'check_exists')
                    cursor.execute(existing_query, (game_id,))
                    
                    if cursor.fetchone():
                        continue  # Skip duplicate
                    
                    # Insert new game
                    insert_query = sql_manager.get_query('games', 'insert_game')
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
            update_query = sql_manager.get_query('clients', 'update_last_active')
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


def process_combined_upload(client_id, upload_data):
    """Process combined upload (games + client info)."""
    try:
        results = {}
        
        # Update client info if provided
        if 'client_info' in upload_data:
            client_result = register_or_update_client(upload_data['client_info'])
            results['client'] = client_result
        
        # Upload games if provided
        if 'games' in upload_data:
            games_result = upload_games_for_client(client_id, upload_data['games'])
            results['games'] = games_result
        
        return results
    except Exception as e:
        logger.error(f"Error processing combined upload: {str(e)}")
        return {'error': str(e)}


def process_file_upload(client_id, file_info, file_content):
    """Process file upload and store metadata."""
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
            query = sql_manager.get_query('files', 'insert_file')
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


def get_player_detailed_stats(player_code, filters=None):
    """Get detailed player statistics with optional filtering."""
    if not player_code:
        return None
    
    try:
        # Get all games for player
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
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Character breakdown
        character_stats = {}
        opponent_stats = {}
        
        for game in processed_games:
            # Character stats
            char = game.get('character_name', 'Unknown')
            if char not in character_stats:
                character_stats[char] = {'games': 0, 'wins': 0}
            character_stats[char]['games'] += 1
            if game.get('result') == 'Win':
                character_stats[char]['wins'] += 1
            
            # Opponent stats
            opp = game.get('opponent_tag', 'Unknown')
            if opp not in opponent_stats:
                opponent_stats[opp] = {'games': 0, 'wins': 0}
            opponent_stats[opp]['games'] += 1
            if game.get('result') == 'Win':
                opponent_stats[opp]['wins'] += 1
        
        # Calculate win rates
        for stats in character_stats.values():
            stats['win_rate'] = (stats['wins'] / stats['games']) * 100 if stats['games'] > 0 else 0
        
        for stats in opponent_stats.values():
            stats['win_rate'] = (stats['wins'] / stats['games']) * 100 if stats['games'] > 0 else 0
        
        return {
            'player_code': player_code,
            'total_games': total_games,
            'wins': wins,
            'losses': total_games - wins,
            'win_rate': round(win_rate, 2),
            'character_breakdown': character_stats,
            'opponent_breakdown': opponent_stats,
            'recent_games': processed_games[:20]
        }
    except Exception as e:
        logger.error(f"Error getting detailed stats for {player_code}: {str(e)}")
        return None


# ADDED: Missing function that was referenced in the logs
def process_detailed_player_data(player_code, filters=None):
    """
    Process detailed player data with filters - wrapper for get_player_detailed_stats.
    This function was missing and being called by routes.
    """
    return get_player_detailed_stats(player_code, filters)


def process_paginated_player_games(player_code, page=1, per_page=20):
    """Get paginated games for a player."""
    try:
        # Get all games for player
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


def apply_game_filters(games, filters):
    """Apply filters to game list."""
    filtered_games = games
    
    if filters.get('character'):
        filtered_games = [g for g in filtered_games if g.get('character_name') == filters['character']]
    
    if filters.get('opponent'):
        filtered_games = [g for g in filtered_games if g.get('opponent_tag') == filters['opponent']]
    
    if filters.get('result'):
        filtered_games = [g for g in filtered_games if g.get('result') == filters['result']]
    
    if filters.get('start_date'):
        start_date = datetime.fromisoformat(filters['start_date'])
        filtered_games = [g for g in filtered_games 
                         if datetime.fromisoformat(g.get('start_time', '1970-01-01')) >= start_date]
    
    if filters.get('end_date'):
        end_date = datetime.fromisoformat(filters['end_date'])
        filtered_games = [g for g in filtered_games 
                         if datetime.fromisoformat(g.get('start_time', '1970-01-01')) <= end_date]
    
    return filtered_games