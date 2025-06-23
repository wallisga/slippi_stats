"""
Slippi Server - Flask web application for storing and retrieving Super Smash Bros. Melee game data.
PHASE 1 REFACTORING COMPLETED:
- All configuration moved to config.py
- All database operations moved to database.py
- Clean separation of concerns
- Maintained backward compatibility with existing templates
"""

# =============================================================================
# Base Modules
# =============================================================================

import time
import urllib.parse
from datetime import datetime
from functools import wraps

# =============================================================================
# Third Party Modules
# =============================================================================

from flask import Flask, render_template, request, jsonify, abort, redirect, send_from_directory

# =============================================================================
# App Modules
# =============================================================================

from config import get_config
from database import (
    init_db, get_player_games, find_player_matches, get_recent_games,
    get_top_players, get_all_players, validate_api_key, create_api_key_for_client,
    register_or_update_client, update_client_last_active, upload_games_for_client,
    get_database_stats
)

# =============================================================================
# Application Initialization
# =============================================================================

config = get_config()
app = Flask(__name__)
app.config.update({'SECRET_KEY': config.SECRET_KEY, 'DEBUG': config.DEBUG})
logger = config.init_logging()
config.validate_config()

@app.context_processor
def inject_request():
    return dict(request=request)

# =============================================================================
# Utility Functions
# =============================================================================

def encode_player_tag(tag):
    return urllib.parse.quote(tag)

def decode_player_tag(encoded_tag):
    return urllib.parse.unquote(encoded_tag)

# =============================================================================
# Decorator Functions
# =============================================================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        client_id = validate_api_key(api_key)
        if not client_id:
            abort(401, description="Invalid or missing API key")
        kwargs['client_id'] = client_id
        return f(*args, **kwargs)
    return decorated_function

def rate_limited(max_per_minute):
    request_counts = {}
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = kwargs.get('client_id')
            if not client_id:
                api_key = request.headers.get('X-API-Key')
                client_id = validate_api_key(api_key) or 'anonymous'
            current_minute = int(time.time() / 60)
            if client_id not in request_counts:
                request_counts[client_id] = {}
            for minute in list(request_counts[client_id].keys()):
                if minute < current_minute:
                    del request_counts[client_id][minute]
            current_count = request_counts[client_id].get(current_minute, 0)
            if current_count >= max_per_minute:
                abort(429, description=f"Rate limit exceeded. Maximum {max_per_minute} requests per minute.")
            request_counts[client_id][current_minute] = current_count + 1
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# Statistics Functions
# =============================================================================

def calculate_player_stats(games):
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
# Template Data Helper Functions
# =============================================================================    

def get_app_statistics():
    try:
        stats = get_database_stats()
        return {
            'total_games': stats.get('total_games', 0),
            'total_players': stats.get('unique_players', 0),
            'latest_game_date': stats.get('last_upload'),
            'stats_generated_at': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting app statistics: {str(e)}")
        return {'total_games': 0, 'total_players': 0, 'latest_game_date': None, 'stats_generated_at': datetime.now().isoformat(), 'error': str(e)}

def get_error_template_data(status_code, error_description, **kwargs):
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

def get_standard_player_template_data(player_code, encoded_player_code):
    games = get_player_games(player_code)
    
    if len(games) == 0:
        potential_matches = find_player_matches(player_code)
        if potential_matches:
            exact_case_insensitive = [m for m in potential_matches if m['match_type'] == 'case_insensitive']
            if exact_case_insensitive:
                correct_tag = exact_case_insensitive[0]['tag']
                return {'redirect_to': correct_tag, 'redirect_encoded': encode_player_tag(correct_tag)}
        abort(404, description=f"Player '{player_code}' not found in database.")
    
    stats = calculate_player_stats(games)
    recent_games = games[:20]
    character_list = list(set(g['player']['character_name'] for g in games))
    
    return {
        'player_code': player_code, 'encoded_player_code': encoded_player_code,
        'stats': stats, 'recent_games': recent_games, 'character_list': character_list,
        'all_games': games, 'last_game_date': recent_games[0]['start_time'] if recent_games else None
    }

# =============================================================================
# Web Routes
# =============================================================================

@app.route('/')
def index():
    app_stats = get_app_statistics()
    recent_games = get_recent_games(10)
    top_players = get_top_players(6)
    return render_template('pages/index.html', app_stats=app_stats,
                          total_games=app_stats.get('total_games', 0), 
                          total_players=app_stats.get('total_players', 0),
                          recent_games=recent_games, top_players=top_players)

@app.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    player_code = decode_player_tag(encoded_player_code)
    template_data = get_standard_player_template_data(player_code, encoded_player_code)
    if 'redirect_to' in template_data:
        return redirect(f"/player/{template_data['redirect_encoded']}")
    return render_template('pages/player_basic.html', **template_data)

@app.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    player_code = decode_player_tag(encoded_player_code)
    template_data = get_standard_player_template_data(player_code, encoded_player_code)
    if 'redirect_to' in template_data:
        return redirect(f"/player/{template_data['redirect_encoded']}/detailed")
    return render_template('pages/player_detailed.html', **template_data)

@app.route('/players')
def players():
    players_list = get_all_players()
    return render_template('pages/players.html', players=players_list)

# =============================================================================
# API Routes
# =============================================================================

# Add this route to your app.py file in the API Routes section

@app.route('/api/player/<encoded_player_code>/detailed', methods=['POST'])
def api_player_detailed_post(encoded_player_code):
    """
    POST version of the detailed player API for complex filters.
    Accepts JSON payload instead of query parameters to avoid URL length limits.
    """
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        logger.info(f"API detailed stats POST request for player: '{player_code}'")
        
        # Get filter parameters from JSON body
        filter_data = request.get_json() or {}
        character_filter = filter_data.get('character', 'all')
        opponent_filter = filter_data.get('opponent', 'all')
        opponent_character_filter = filter_data.get('opponent_character', 'all')
        
        logger.info(f"POST Filters - Character: {character_filter}, Opponent: {opponent_filter}, Opponent Character: {opponent_character_filter}")
        
        # Get all games for this player
        all_games = get_player_games(player_code)
        
        if not all_games:
            return jsonify({'error': f"Player '{player_code}' not found"}), 404
        
        # Collect all available filter options
        characters_played = set()
        opponents_faced = set()
        opponent_characters_faced = set()
        
        for game in all_games:
            characters_played.add(game['player'].get('character_name', 'Unknown'))
            opponents_faced.add(game['opponent'].get('player_tag', 'Unknown'))
            opponent_characters_faced.add(game['opponent'].get('character_name', 'Unknown'))
        
        # Apply filters
        filtered_games = all_games
        
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
        
        # Calculate overall stats
        total_filtered = len(filtered_games)
        wins_filtered = sum(1 for game in filtered_games if game['result'] == 'Win')
        overall_winrate = wins_filtered / total_filtered if total_filtered > 0 else 0
        
        # Calculate character stats
        character_stats = {}
        for char in sorted(characters_played):
            char_games = [g for g in filtered_games if g['player'].get('character_name') == char]
            char_total = len(char_games)
            char_wins = sum(1 for g in char_games if g['result'] == 'Win')
            character_stats[char] = {
                'games': char_total,
                'wins': char_wins,
                'win_rate': char_wins / char_total if char_total > 0 else 0
            }
        
        # Calculate opponent stats
        opponent_stats = {}
        for opp in sorted(opponents_faced):
            opp_games = [g for g in filtered_games if g['opponent'].get('player_tag') == opp]
            opp_total = len(opp_games)
            opp_wins = sum(1 for g in opp_games if g['result'] == 'Win')
            opponent_stats[opp] = {
                'games': opp_total,
                'wins': opp_wins,
                'win_rate': opp_wins / opp_total if opp_total > 0 else 0
            }
        
        # Calculate opponent character stats
        opponent_char_stats = {}
        for opp_char in sorted(opponent_characters_faced):
            opp_char_games = [g for g in filtered_games if g['opponent'].get('character_name') == opp_char]
            opp_char_total = len(opp_char_games)
            opp_char_wins = sum(1 for g in opp_char_games if g['result'] == 'Win')
            opponent_char_stats[opp_char] = {
                'games': opp_char_total,
                'wins': opp_char_wins,
                'win_rate': opp_char_wins / opp_char_total if opp_char_total > 0 else 0
            }
        
        # Calculate date stats
        date_stats = {}
        for game in filtered_games:
            # Extract date from start_time
            date = game['start_time'].split('T')[0] if 'T' in game['start_time'] else game['start_time']
            if date not in date_stats:
                date_stats[date] = {'games': 0, 'wins': 0}
            
            date_stats[date]['games'] += 1
            if game['result'] == 'Win':
                date_stats[date]['wins'] += 1
        
        # Calculate win rates for dates
        for date in date_stats:
            date_stats[date]['win_rate'] = date_stats[date]['wins'] / date_stats[date]['games']
        
        # Sort date stats by date
        date_stats_sorted = {k: date_stats[k] for k in sorted(date_stats.keys())}
        
        # Return response
        response = {
            'player_code': player_code,
            'total_games': total_filtered,
            'wins': wins_filtered,
            'overall_winrate': overall_winrate,
            'character_stats': character_stats,
            'opponent_stats': opponent_stats,
            'opponent_character_stats': opponent_char_stats,
            'date_stats': date_stats_sorted,
            'filter_options': {
                'characters': sorted(list(characters_played)),
                'opponents': sorted(list(opponents_faced)),
                'opponent_characters': sorted(list(opponent_characters_faced))
            },
            'applied_filters': {
                'character': character_filter,
                'opponent': opponent_filter,
                'opponent_character': opponent_character_filter
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in detailed player POST API: {str(e)}")
        return jsonify({'error': str(e)}), 500
        

@app.route('/api/player/<encoded_player_code>/games')
def api_player_games(encoded_player_code):
    try:
        player_code = decode_player_tag(encoded_player_code)
        page = max(1, int(request.args.get('page', '1')))
        all_games = get_player_games(player_code)
        total_games = len(all_games)
        total_pages = (total_games + config.GAMES_PER_PAGE - 1) // config.GAMES_PER_PAGE
        start_idx = (page - 1) * config.GAMES_PER_PAGE
        end_idx = min(start_idx + config.GAMES_PER_PAGE, total_games)
        
        if start_idx >= total_games:
            return jsonify({'total_games': total_games, 'total_pages': total_pages, 'current_page': page, 'games': []})
        
        games_page = all_games[start_idx:end_idx]
        return jsonify({'total_games': total_games, 'total_pages': total_pages, 'current_page': page, 'games': games_page})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<encoded_player_code>/stats')
def api_player_stats(encoded_player_code):
    try:
        player_code = decode_player_tag(encoded_player_code)
        games = get_player_games(player_code)
        stats = calculate_player_stats(games)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clients/register', methods=['POST'])
def register_client():
    client_data = request.json
    registration_key = request.headers.get('X-Registration-Key')
    if not registration_key or registration_key != config.REGISTRATION_SECRET:
        abort(401, description="Invalid registration key")
    try:
        result = register_or_update_client(client_data)
        return jsonify(result)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")

@app.route('/api/games/upload', methods=['POST'])
@require_api_key
@rate_limited(config.RATE_LIMIT_UPLOADS)
def upload_games(client_id):
    upload_data = request.json
    if upload_data.get('client_id') != client_id:
        abort(403, description="Client ID in request does not match API key")
    games = upload_data.get('games', [])
    try:
        result = upload_games_for_client(client_id, games)
        return jsonify(result)
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = get_database_stats()
        return jsonify({
            "total_clients": stats.get('total_clients', 0),
            "total_games": stats.get('total_games', 0),
            "unique_players": stats.get('unique_players', 0),
            "last_upload": stats.get('last_upload')
        })
    except Exception as e:
        abort(500, description=f"Server error: {str(e)}")

# =============================================================================
# Static File Routes
# =============================================================================

@app.route('/download')
def download_page():
    return render_template('pages/download.html', version=config.CLIENT_VERSION,
                          release_date=config.CLIENT_RELEASE_DATE, download_url="/download/SlippiMonitor.msi")

@app.route('/download/<filename>')
def download_file(filename):
    downloads_dir = config.get_downloads_dir()
    return send_from_directory(path=downloads_dir, filename=filename, as_attachment=True)

@app.route('/how-to')
def how_to_page():
    return render_template('pages/how_to.html')

# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(400)
def bad_request(error):
    template_data = get_error_template_data(400, str(error.description))
    return render_template('pages/error_status.html', **template_data), 400

@app.errorhandler(401)
def unauthorized(error):
    template_data = get_error_template_data(401, str(error.description))
    return render_template('pages/error_status.html', **template_data), 401

@app.errorhandler(403)
def forbidden(error):
    template_data = get_error_template_data(403, str(error.description))
    return render_template('pages/error_status.html', **template_data), 403

@app.errorhandler(404)
def page_not_found(error):
    template_data = get_error_template_data(404, str(error.description))
    return render_template('pages/error_status.html', **template_data), 404

@app.errorhandler(429)
def too_many_requests(error):
    template_data = get_error_template_data(429, str(error.description))
    return render_template('pages/error_status.html', **template_data), 429

@app.errorhandler(500)
def server_error(error):
    template_data = get_error_template_data(500, str(error))
    return render_template('pages/error_status.html', **template_data), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception: {str(error)}")
    return render_template('pages/error_exception.html', error=str(error)), 500

# =============================================================================
# Application Initialization
# =============================================================================

init_db()

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)