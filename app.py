"""
Slippi Server - Flask web application for storing and retrieving Super Smash Bros. Melee game data.

This application provides a web interface and API for:
1. Registering Slippi clients
2. Uploading game data from Slippi replays
3. Viewing player statistics and game history
4. Accessing game data through a REST API

The server uses SQLite for data storage and provides authentication through API keys.
"""

import sqlite3
import json
import time
import secrets
import os
import logging
import urllib.parse
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, send_from_directory

# =============================================================================
# Configuration
# =============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="server.log"
)
logger = logging.getLogger('SlippiServer')

# Application constants
REGISTRATION_SECRET = "sl1pp1-s3rv3r-r3g1str4t10n-k3y-2025"  # Change this to your secret key
API_KEYS_TABLE = "api_keys"
TOKEN_EXPIRY_DAYS = 365  # API keys valid for 1 year
DATABASE_PATH = 'slippi_data.db'  # Path to the SQLite database
# Uncomment for testing on local Windows Machine
# DATABASE_PATH = 'C:\\Users\\Gavin\\Code\\slippiscrape\\server\\slippi_data.db'
GAMES_PER_PAGE = 20  # Number of games to show per page
MIN_GAMES_FOR_STATS = 10  # Minimum number of games needed for meaningful statistics

app = Flask(__name__)

# Make request available in all templates
@app.context_processor
def inject_request():
    """
    Make request object available in all templates.
    """
    return dict(request=request)

# =============================================================================
# Database Functions
# =============================================================================

def init_db():
    """
    Initialize the SQLite database with the required tables:
    - clients: Stores information about registered clients
    - games: Stores game data from uploaded replays
    - api_keys: Stores API keys for client authentication
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Create clients table
    c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        hostname TEXT,
        platform TEXT,
        version TEXT,
        registration_date TEXT,
        last_active TEXT
    )
    ''')
    
    # Create games table
    c.execute('''
    CREATE TABLE IF NOT EXISTS games (
        game_id TEXT PRIMARY KEY,
        client_id TEXT,
        start_time TEXT,
        last_frame INTEGER,
        stage_id INTEGER,
        player_data TEXT,
        upload_date TEXT,
        game_type TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    ''')
    
    # Create API keys table
    c.execute(f'''
    CREATE TABLE IF NOT EXISTS {API_KEYS_TABLE} (
        client_id TEXT PRIMARY KEY,
        api_key TEXT UNIQUE,
        created_at TEXT,
        expires_at TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DATABASE_PATH}")

def get_db_connection():
    """
    Create a connection to the SQLite database with Row factory enabled.
    
    Returns:
        sqlite3.Connection: Database connection with row_factory set to sqlite3.Row
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# =============================================================================
# Authentication Functions
# =============================================================================

def generate_api_key():
    """
    Generate a secure random API key.
    
    Returns:
        str: A cryptographically secure API key string
    """
    return secrets.token_urlsafe(32)

def create_api_key(client_id):
    """
    Create a new API key for a client or update an existing one.
    
    Args:
        client_id (str): The client's unique identifier
        
    Returns:
        dict: Dictionary containing the API key and expiration date
    """
    api_key = generate_api_key()
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS)).isoformat()
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Check if key already exists for this client
    c.execute(f"SELECT api_key FROM {API_KEYS_TABLE} WHERE client_id = ?", (client_id,))
    existing = c.fetchone()
    
    if existing:
        # Update existing key
        c.execute(f'''
        UPDATE {API_KEYS_TABLE}
        SET api_key = ?, created_at = ?, expires_at = ?
        WHERE client_id = ?
        ''', (api_key, created_at, expires_at, client_id))
    else:
        # Create new key
        c.execute(f'''
        INSERT INTO {API_KEYS_TABLE} (client_id, api_key, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        ''', (client_id, api_key, created_at, expires_at))
    
    conn.commit()
    conn.close()
    
    return {
        "api_key": api_key,
        "expires_at": expires_at
    }

def validate_api_key(api_key):
    """
    Validate an API key and return the associated client_id if valid.
    
    Args:
        api_key (str): The API key to validate
        
    Returns:
        str or None: The client_id if the key is valid, None otherwise
    """
    if not api_key:
        return None
        
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute(f'''
    SELECT client_id, expires_at 
    FROM {API_KEYS_TABLE} 
    WHERE api_key = ?
    ''', (api_key,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return None
        
    client_id, expires_at = result
    
    # Check if key has expired
    if expires_at and datetime.now() > datetime.fromisoformat(expires_at):
        return None
        
    return client_id

# =============================================================================
# Decorator Functions
# =============================================================================

def require_api_key(f):
    """
    Decorator to require a valid API key for endpoint access.
    
    Args:
        f (function): The function to decorate
        
    Returns:
        function: The decorated function that checks for a valid API key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        client_id = validate_api_key(api_key)
        
        if not client_id:
            abort(401, description="Invalid or missing API key")
            
        # Add client_id to kwargs
        kwargs['client_id'] = client_id
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limited(max_per_minute):
    """
    Simple rate limiting decorator to limit requests per client.
    
    Args:
        max_per_minute (int): Maximum number of requests allowed per minute
        
    Returns:
        function: Decorator function that enforces rate limits
    """
    request_counts = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = kwargs.get('client_id')
            if not client_id:
                api_key = request.headers.get('X-API-Key')
                client_id = validate_api_key(api_key) or 'anonymous'
                
            # Get current minute
            current_minute = int(time.time() / 60)
            
            # Initialize request counts for this client if needed
            if client_id not in request_counts:
                request_counts[client_id] = {}
                
            # Clean old entries
            for minute in list(request_counts[client_id].keys()):
                if minute < current_minute:
                    del request_counts[client_id][minute]
            
            # Check current count
            current_count = request_counts[client_id].get(current_minute, 0)
            
            if current_count >= max_per_minute:
                abort(429, description=f"Rate limit exceeded. Maximum {max_per_minute} requests per minute.")
                
            # Increment count
            request_counts[client_id][current_minute] = current_count + 1
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

# =============================================================================
# Game Data Helper Functions
# =============================================================================

def encode_player_tag(tag):
    """
    URL-encode a player tag for use in URLs.
    
    Args:
        tag (str): The player tag to encode
        
    Returns:
        str: URL-encoded player tag
    """
    return urllib.parse.quote(tag)

def decode_player_tag(encoded_tag):
    """
    Decode a URL-encoded player tag.
    
    Args:
        encoded_tag (str): The URL-encoded player tag
        
    Returns:
        str: Decoded player tag
    """
    return urllib.parse.unquote(encoded_tag)

def calculate_character_stats(games):
    """
    Calculate statistics for a player using a specific character.
    
    Args:
        games (list): List of game dictionaries for a player with a specific character
        
    Returns:
        dict: Dictionary containing character-specific statistics
    """
    if not games:
        return {}
    
    # Basic stats
    total_games = len(games)
    wins = sum(1 for game in games if game['result'] == 'Win')
    win_rate = wins / total_games if total_games > 0 else 0
    
    # Matchup stats
    matchups = {}
    for game in games:
        opponent_char = game['opponent']['character_name']
        if opponent_char not in matchups:
            matchups[opponent_char] = {'games': 0, 'wins': 0}
        
        matchups[opponent_char]['games'] += 1
        if game['result'] == 'Win':
            matchups[opponent_char]['wins'] += 1
    
    # Calculate win rates for each matchup
    for char in matchups:
        games_vs_char = matchups[char]['games']
        wins_vs_char = matchups[char]['wins']
        matchups[char]['win_rate'] = wins_vs_char / games_vs_char if games_vs_char > 0 else 0
    
    # Find best and worst matchups (min 3 games)
    qualified_matchups = [char for char, data in matchups.items() if data['games'] >= 3]
    
    best_matchup = None
    worst_matchup = None
    
    if qualified_matchups:
        best_matchup_name = max(
            [(char, matchups[char]['win_rate']) for char in qualified_matchups],
            key=lambda x: x[1]
        )[0]
        best_matchup = {'character': best_matchup_name, **matchups[best_matchup_name]}
        
        worst_matchup_name = min(
            [(char, matchups[char]['win_rate']) for char in qualified_matchups],
            key=lambda x: x[1]
        )[0]
        worst_matchup = {'character': worst_matchup_name, **matchups[worst_matchup_name]}
    
    # Performance over time
    time_stats = {}
    for game in games:
        date = game['start_time'].split('T')[0] if 'T' in game['start_time'] else game['start_time']
        if date not in time_stats:
            time_stats[date] = {'games': 0, 'wins': 0}
        
        time_stats[date]['games'] += 1
        if game['result'] == 'Win':
            time_stats[date]['wins'] += 1
    
    # Calculate win rates for each date
    for date in time_stats:
        games_on_date = time_stats[date]['games']
        wins_on_date = time_stats[date]['wins']
        time_stats[date]['win_rate'] = wins_on_date / games_on_date if games_on_date > 0 else 0
    
    # Calculate trend (recent vs overall)
    recent_games = games[:min(30, len(games))]
    recent_wins = sum(1 for game in recent_games if game['result'] == 'Win')
    recent_win_rate = recent_wins / len(recent_games) if recent_games else 0
    trend = (recent_win_rate - win_rate) * 100  # Percentage point difference
    
    return {
        'games': total_games,
        'wins': wins,
        'win_rate': win_rate,
        'matchups': [{'character': char, **data} for char, data in matchups.items()],
        'best_matchup': best_matchup,
        'worst_matchup': worst_matchup,
        'time_stats': time_stats,
        'trend': trend
    }    

# =============================================================================
# Player Data Functions
# =============================================================================

def player_exists(player_code):
    """
    Check if a player exists in the database.
    
    Args:
        player_code (str): The player tag to check
        
    Returns:
        bool: True if player exists, False otherwise
    """
    logger.info(f"Checking if player exists: '{player_code}'")
    # For debugging: log JSON data from 5 random games
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT player_data FROM games LIMIT 5")
    sample_rows = cursor.fetchall()
    logger.info("Sample player_data from database:")
    
    exists = False
    for i, row in enumerate(sample_rows):
        logger.info(f"Sample {i+1}: {row['player_data']}")
        
        # Check each player in the JSON data
        players = json.loads(row['player_data'])
        for player in players:
            if player.get('player_tag') == player_code:
                logger.info(f"Found exact match for '{player_code}' in game data!")
                exists = True
    
    conn.close()
    
    return exists

def get_player_games(player_code):
    """
    Get all games for a specific player.
    
    Args:
        player_code (str): The player tag to look up
        
    Returns:
        list: List of game dictionaries for the specified player
    """
    logger.info(f"Getting games for player: '{player_code}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all games
    cursor.execute("SELECT game_id, game_type, start_time, last_frame, stage_id, player_data FROM games")
    games_raw = cursor.fetchall()
    conn.close()
    
    logger.info(f"Fetched {len(games_raw)} total games to process")
    
    # Process the games data
    games = []
    for game in games_raw:
        try:
            player_data = json.loads(game['player_data'])
            
            # Find the target player's data
            player_info = None
            opponent_info = None
            
            for player in player_data:
                if player.get('player_tag') == player_code:
                    player_info = player
            
            # Skip games where the player wasn't found
            if not player_info:
                continue
                
            # Find the opponent
            for player in player_data:
                if player != player_info:
                    opponent_info = player
                    break
            
            # Skip games without an opponent
            if not opponent_info:
                continue
                
            games.append({
                'game_id': game['game_id'],
                'start_time': game['start_time'],
                'last_frame': game['last_frame'],
                'game_duration_seconds': game['last_frame'] / 60,
                'stage_id': game['stage_id'],
                'player': player_info,
                'opponent': opponent_info,
                'result': player_info.get('result', 'Unknown')
            })
        except Exception as e:
            logger.error(f"Error processing game: {str(e)}")
            continue
    
    logger.info(f"Found {len(games)} games for player '{player_code}'")
    return games

def find_player_with_flexible_matching(player_code):
    """
    Find a player with more flexible matching criteria to help identify issues
    with exact matching that's failing.
    
    Args:
        player_code (str): The player tag to look up with flexible matching
        
    Returns:
        list: List of potential matches with match type and player data
    """
    logger.info(f"Trying flexible matching for player: '{player_code}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get a sample of games
    cursor.execute("SELECT player_data FROM games")
    games = cursor.fetchall()
    
    # Look for any matches
    matches = []
    
    for game in games:
        try:
            player_data = json.loads(game['player_data'])
            for player in player_data:
                if 'player_tag' not in player or not player['player_tag']:
                    continue
                    
                tag = player['player_tag']
                
                # Try different matching criteria
                exact_match = (tag == player_code)
                case_insensitive = (tag.lower() == player_code.lower())
                contains = (player_code in tag or tag in player_code)
                
                if exact_match or case_insensitive or contains:
                    matches.append({
                        'tag': tag,
                        'match_type': 'exact' if exact_match else ('case_insensitive' if case_insensitive else 'contains'),
                        'player_data': player
                    })
        except Exception as e:
            logger.error(f"Error parsing game data: {str(e)}")
            continue
    
    conn.close()
    logger.info(f"Flexible matching found {len(matches)} potential matches")
    for match in matches:
        logger.info(f"Match ({match['match_type']}): '{match['tag']}'")
    
    return matches

def calculate_player_stats(games):
    """
    Calculate comprehensive statistics for a player based on their games.
    
    Args:
        games (list): List of game dictionaries
        
    Returns:
        dict: Dictionary containing various player statistics
    """
    if not games:
        return {}
    
    # Basic stats
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
    
    # Calculate win rates for each character
    for char in character_stats:
        games_with_char = character_stats[char]['games']
        wins_with_char = character_stats[char]['wins']
        character_stats[char]['win_rate'] = wins_with_char / games_with_char if games_with_char > 0 else 0
    
    # Find most played character
    most_played = max(character_stats.items(), key=lambda x: x[1]['games'])[0] if character_stats else None
    
    # Find character with best win rate (min 10 games)
    best_characters = [char for char, data in character_stats.items() if data['games'] >= MIN_GAMES_FOR_STATS]
    best_winrate_char = max(
        [(char, character_stats[char]['win_rate']) for char in best_characters],
        key=lambda x: x[1]
    )[0] if best_characters else None
    
    # Find character with worst win rate (min 10 games)
    worst_winrate_char = min(
        [(char, character_stats[char]['win_rate']) for char in best_characters],
        key=lambda x: x[1]
    )[0] if best_characters else None
    
    # Opponent stats
    opponent_stats = {}
    for game in games:
        opponent_tag = game['opponent']['player_tag']
        opponent_char = game['opponent']['character_name']
        matchup_key = f"{opponent_tag}_{opponent_char}"
        
        if matchup_key not in opponent_stats:
            opponent_stats[matchup_key] = {
                'opponent_tag': opponent_tag,
                'opponent_char': opponent_char,
                'games': 0,
                'wins': 0
            }
        
        opponent_stats[matchup_key]['games'] += 1
        if game['result'] == 'Win':
            opponent_stats[matchup_key]['wins'] += 1
    
    # Calculate win rates for each opponent matchup
    for key in opponent_stats:
        games_vs_opp = opponent_stats[key]['games']
        wins_vs_opp = opponent_stats[key]['wins']
        opponent_stats[key]['win_rate'] = wins_vs_opp / games_vs_opp if games_vs_opp > 0 else 0
    
    # Find rival (worst matchup with at least 10 games)
    rival_matchups = [key for key, data in opponent_stats.items() if data['games'] >= MIN_GAMES_FOR_STATS]
    rival = None
    if rival_matchups:
        rival_key = min(
            [(key, opponent_stats[key]['win_rate']) for key in rival_matchups],
            key=lambda x: x[1]
        )[0]
        rival = opponent_stats[rival_key]
    
    # "On The Rise" - best character in last 30 games
    recent_games = games[:30]
    recent_char_stats = {}
    for game in recent_games:
        char = game['player']['character_name']
        if char not in recent_char_stats:
            recent_char_stats[char] = {'games': 0, 'wins': 0}
        
        recent_char_stats[char]['games'] += 1
        if game['result'] == 'Win':
            recent_char_stats[char]['wins'] += 1
    
    # Calculate win rates for recent characters
    for char in recent_char_stats:
        games_with_char = recent_char_stats[char]['games']
        wins_with_char = recent_char_stats[char]['wins']
        recent_char_stats[char]['win_rate'] = wins_with_char / games_with_char if games_with_char > 0 else 0
    
    # Find character with best recent performance (min 5 games)
    rising_characters = [char for char, data in recent_char_stats.items() if data['games'] >= 5]
    rising_star = None
    if rising_characters:
        rising_star = max(
            [(char, recent_char_stats[char]['win_rate']) for char in rising_characters],
            key=lambda x: x[1]
        )[0]
    
    # Stage stats
    stage_stats = {}
    for game in games:
        stage_id = game['stage_id']
        if stage_id not in stage_stats:
            stage_stats[stage_id] = {'games': 0, 'wins': 0}
        
        stage_stats[stage_id]['games'] += 1
        if game['result'] == 'Win':
            stage_stats[stage_id]['wins'] += 1
    
    # Calculate win rates for each stage
    for stage_id in stage_stats:
        games_on_stage = stage_stats[stage_id]['games']
        wins_on_stage = stage_stats[stage_id]['wins']
        stage_stats[stage_id]['win_rate'] = wins_on_stage / games_on_stage if games_on_stage > 0 else 0
    
    # Find best and worst stages (min 5 games)
    qualified_stages = [stage_id for stage_id, data in stage_stats.items() if data['games'] >= 5]
    
    best_stage = None
    worst_stage = None
    
    if qualified_stages:
        best_stage_id = max(
            [(stage_id, stage_stats[stage_id]['win_rate']) for stage_id in qualified_stages],
            key=lambda x: x[1]
        )[0]
        best_stage = {'id': best_stage_id, **stage_stats[best_stage_id]}
        
        worst_stage_id = min(
            [(stage_id, stage_stats[stage_id]['win_rate']) for stage_id in qualified_stages],
            key=lambda x: x[1]
        )[0]
        worst_stage = {'id': worst_stage_id, **stage_stats[worst_stage_id]}
    
    return {
        'total_games': total_games,
        'wins': wins,
        'win_rate': win_rate,
        'most_played_character': most_played,
        'best_character': best_winrate_char,
        'worst_character': worst_winrate_char,
        'character_stats': character_stats,
        'rival': rival,
        'rising_star': rising_star,
        'best_stage': best_stage,
        'worst_stage': worst_stage,
        'stage_stats': stage_stats,
        'opponent_stats': opponent_stats
    }

# =============================================================================
# Web Routes
# =============================================================================

@app.route('/')
def index():
    """
    Main landing page displaying statistics and recent games.
    
    Returns:
        str: Rendered HTML template
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total games
    cursor.execute("SELECT COUNT(*) FROM games")
    total_games = cursor.fetchone()[0]
    
    # Log the total games count for debugging
    logger.info(f"Current total games in database: {total_games}")
    
    # Use a better query for counting unique players
    cursor.execute("""
    WITH player_tags AS (
        SELECT DISTINCT json_extract(p.value, '$.player_tag') as tag
        FROM games, json_each(games.player_data) as p
        WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
          AND json_extract(p.value, '$.player_tag') != ''
    )
    SELECT COUNT(*) FROM player_tags
    """)
    total_players = cursor.fetchone()[0]
    
    # Get recent games with proper ordering
    cursor.execute("""
    SELECT start_time, player_data, game_id
    FROM games
    ORDER BY datetime(start_time) DESC
    LIMIT 10
    """)
    recent_games_raw = cursor.fetchall()
    
    recent_games = []
    for game in recent_games_raw:
        player_data = json.loads(game['player_data'])
        player1 = player_data[0] if len(player_data) > 0 else {"player_name": "Unknown", "character_name": "Unknown", "player_tag": "Unknown"}
        player2 = player_data[1] if len(player_data) > 1 else {"player_name": "Unknown", "character_name": "Unknown", "player_tag": "Unknown"}
        
        recent_games.append({
            'time': game['start_time'],
            'game_id': game['game_id'],
            'player1': player1.get('player_name', 'Unknown'),
            'player1_tag': player1.get('player_tag', 'Unknown'),
            'player1_tag_encoded': encode_player_tag(player1.get('player_tag', 'Unknown')),
            'character1': player1.get('character_name', 'Unknown'),
            'player2': player2.get('player_name', 'Unknown'),
            'player2_tag': player2.get('player_tag', 'Unknown'),
            'player2_tag_encoded': encode_player_tag(player2.get('player_tag', 'Unknown')),
            'character2': player2.get('character_name', 'Unknown'),
            'result': f"{player1.get('result', 'Unknown')} - {player2.get('result', 'Unknown')}"
        })
    
    # Use a smarter query to get player stats directly
    cursor.execute("""
    WITH player_data_expanded AS (
        SELECT 
            json_extract(p.value, '$.player_tag') as tag,
            json_extract(p.value, '$.player_name') as name,
            json_extract(p.value, '$.character_name') as character,
            json_extract(p.value, '$.result') as result
        FROM games, json_each(games.player_data) as p
        WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
          AND json_extract(p.value, '$.player_tag') != ''
    ),
    player_stats AS (
        SELECT 
            tag,
            name,
            COUNT(*) as games,
            SUM(CASE WHEN result = 'Win' THEN 1 ELSE 0 END) as wins
        FROM player_data_expanded
        GROUP BY tag
        ORDER BY games DESC
        LIMIT 6
    )
    SELECT * FROM player_stats
    """)
    
    top_players_rows = cursor.fetchall()
    
    top_players = []
    for player in top_players_rows:
        win_rate = player['wins'] / player['games'] if player['games'] > 0 else 0
        top_players.append({
            'code': player['tag'],
            'code_encoded': encode_player_tag(player['tag']),
            'name': player['name'],
            'games': player['games'],
            'win_rate': win_rate
        })
    
    conn.close()
    
    return render_template('pages/index.html', 
                          total_games=total_games, 
                          total_players=total_players,
                          recent_games=recent_games,
                          top_players=top_players)

@app.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    """
    Player profile page displaying player statistics and recent games.
    
    Args:
        encoded_player_code (str): URL-encoded player tag
        
    Returns:
        str: Rendered HTML template
    """

    # Decode the player code from URL
    player_code = decode_player_tag(encoded_player_code)
    logger.info(f"Requested player profile: '{player_code}' (encoded as '{encoded_player_code}')")
    
    # Get all games for this player with proper ordering
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all games with descending time order
    cursor.execute("""
    SELECT game_id, start_time, last_frame, stage_id, player_data 
    FROM games 
    ORDER BY datetime(start_time) DESC
    """)
    games_raw = cursor.fetchall()
    conn.close()
    
    # Process the games data
    games = []
    for game in games_raw:
        try:
            player_data = json.loads(game['player_data'])
            
            # Find the target player's data
            player_info = None
            opponent_info = None
            
            for player in player_data:
                if player.get('player_tag') == player_code:
                    player_info = player
            
            # Skip games where the player wasn't found
            if not player_info:
                continue
                
            # Find the opponent
            for player in player_data:
                if player != player_info:
                    opponent_info = player
                    break
            
            # Skip games without an opponent
            if not opponent_info:
                continue
                
            games.append({
                'game_id': game['game_id'],
                'start_time': game['start_time'],
                'last_frame': game['last_frame'],
                'game_duration_seconds': game['last_frame'] / 60,
                'stage_id': game['stage_id'],
                'player': player_info,
                'opponent': opponent_info,
                'result': player_info.get('result', 'Unknown')
            })
        except Exception as e:
            logger.error(f"Error processing game: {str(e)}")
            continue
    
    logger.info(f"Found {len(games)} games for player '{player_code}'")
    
    if len(games) == 0:
        # Try flexible matching
        potential_matches = find_player_with_flexible_matching(player_code)
        
        if potential_matches:
            # If we have an exact case-insensitive match, redirect to it
            exact_case_insensitive = [m for m in potential_matches if m['match_type'] == 'case_insensitive']
            if exact_case_insensitive:
                correct_tag = exact_case_insensitive[0]['tag']
                logger.info(f"Redirecting to case-correct tag: '{correct_tag}'")
                return redirect(f"/player/{encode_player_tag(correct_tag)}")
                
            # If we have exact matches but no games were found, something else is wrong
            exact_matches = [m for m in potential_matches if m['match_type'] == 'exact']
            if exact_matches:
                logger.error(f"Found {len(exact_matches)} exact matches for '{player_code}' but no games were found")
                
        abort(404, description=f"Player '{player_code}' was found but no games could be loaded. Please check the debug page for a list of available players.")
    
    # Calculate player statistics
    stats = calculate_player_stats(games)
    
    # Get recent games (last 20)
    recent_games = games[:GAMES_PER_PAGE]
    
    # Get character list for dropdown navigation
    character_list = list(set(g['player']['character_name'] for g in games))
    
    # Updated to use the new template path - simple page in pages directory
    return render_template('pages/player_basic.html', 
                          player_code=player_code,
                          encoded_player_code=encoded_player_code,
                          stats=stats,
                          recent_games=recent_games,
                          character_list=character_list)
                          

@app.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    """
    Detailed player profile page with filtering capabilities.
    
    Args:
        encoded_player_code (str): URL-encoded player tag
        
    Returns:
        str: Rendered HTML template
    """

    # Decode the player code from URL
    player_code = decode_player_tag(encoded_player_code)
    logger.info(f"Requested detailed profile for: '{player_code}' (encoded as '{encoded_player_code}')")
    
    return render_template('pages/player_detailed.html', 
                          player_code=player_code,
                          encoded_player_code=encoded_player_code)


@app.route('/players')
def players():
    """
    Debug endpoint to see all players in the database.
    
    Returns:
        str: Rendered HTML template with player list
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use a better query to get player data directly
    cursor.execute("""
    WITH player_data_expanded AS (
        SELECT 
            json_extract(p.value, '$.player_tag') as tag,
            json_extract(p.value, '$.player_name') as name,
            json_extract(p.value, '$.character_name') as character
        FROM games, json_each(games.player_data) as p
        WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
          AND json_extract(p.value, '$.player_tag') != ''
    ),
    player_char_counts AS (
        SELECT 
            tag, 
            name,
            character,
            COUNT(*) as count
        FROM player_data_expanded
        GROUP BY tag, character
    ),
    player_totals AS (
        SELECT 
            tag,
            name,
            SUM(count) as total_count
        FROM player_char_counts
        GROUP BY tag
    ),
    player_characters AS (
        SELECT 
            pcc.tag,
            GROUP_CONCAT(pcc.character) as characters
        FROM player_char_counts pcc
        GROUP BY pcc.tag
    )
    SELECT 
        pt.tag, 
        pt.name, 
        pc.characters, 
        pt.total_count
    FROM player_totals pt
    JOIN player_characters pc ON pt.tag = pc.tag
    ORDER BY pt.total_count DESC
    """)
    
    players_rows = cursor.fetchall()
    
    # Convert to list for template rendering
    players_list = []
    for row in players_rows:
        players_list.append({
            'tag': row['tag'],
            'encoded_tag': encode_player_tag(row['tag']),
            'name': row['name'],
            'characters': row['characters'],
            'count': row['total_count']
        })
    
    conn.close()
    
    return render_template('pages/players.html', players=players_list)

# =============================================================================
# API Routes
# =============================================================================

@app.route('/api/player/<encoded_player_code>/games')
def api_player_games(encoded_player_code):
    """
    API endpoint to get a player's games with pagination.
    
    Args:
        encoded_player_code (str): URL-encoded player tag
        
    Returns:
        flask.Response: JSON response with games data
    """
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        logger.info(f"API request for games of player: '{player_code}'")
        
        # Get page parameter
        page = request.args.get('page', '1')
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
            
        logger.info(f"Requested page {page} for player '{player_code}'")
        
        # Get all games for this player
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all games
        cursor.execute("""
        SELECT game_id, start_time, last_frame, stage_id, player_data 
        FROM games 
        ORDER BY datetime(start_time) DESC
        """)
        games_raw = cursor.fetchall()
        conn.close()
        
        # Process the games data to find this player's games
        all_games = []
        for game in games_raw:
            try:
                player_data = json.loads(game['player_data'])
                
                # Find the target player's data
                player_info = None
                opponent_info = None
                
                for player in player_data:
                    if player.get('player_tag') == player_code:
                        player_info = player
                
                # Skip games where the player wasn't found
                if not player_info:
                    continue
                    
                # Find the opponent
                for player in player_data:
                    if player != player_info:
                        opponent_info = player
                        break
                
                # Skip games without an opponent
                if not opponent_info:
                    continue
                    
                all_games.append({
                    'game_id': game['game_id'],
                    'start_time': game['start_time'],
                    'last_frame': game['last_frame'],
                    'game_duration_seconds': game['last_frame'] / 60,
                    'stage_id': game['stage_id'],
                    'player': player_info,
                    'opponent': opponent_info,
                    'result': player_info.get('result', 'Unknown')
                })
            except Exception as e:
                logger.error(f"Error processing game: {str(e)}")
                continue
        
        logger.info(f"Found {len(all_games)} games for player '{player_code}'")
        
        # Calculate total pages
        total_games = len(all_games)
        total_pages = (total_games + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE
        
        # Get games for the requested page
        start_idx = (page - 1) * GAMES_PER_PAGE
        end_idx = min(start_idx + GAMES_PER_PAGE, total_games)  # Ensure we don't go out of bounds
        
        # Check if request is for valid page
        if start_idx >= total_games:
            logger.warning(f"Requested page {page} exceeds available data (max page: {total_pages})")
            return jsonify({
                'total_games': total_games,
                'total_pages': total_pages,
                'current_page': page,
                'games': []
            })
            
        games_page = all_games[start_idx:end_idx]
        
        # Return JSON response
        response_data = {
            'total_games': total_games,
            'total_pages': total_pages,
            'current_page': page,
            'games': games_page
        }
        
        logger.info(f"Returning {len(games_page)} games for page {page}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in API games route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<encoded_player_code>/stats')
def api_player_stats(encoded_player_code):
    """
    API endpoint to get a player's statistics.
    
    Args:
        encoded_player_code (str): URL-encoded player tag
        
    Returns:
        flask.Response: JSON response with player statistics
    """
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        
        # Get all games for this player
        games = get_player_games(player_code)
        
        # Calculate player statistics
        stats = calculate_player_stats(games)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error in API stats route: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add this new route to your Flask app
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
        
        # Rest of your existing logic remains the same...
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT game_id, start_time, last_frame, stage_id, player_data 
        FROM games 
        ORDER BY datetime(start_time) DESC
        """)
        games_raw = cursor.fetchall()
        conn.close()
        
        # Process games (same as your existing code)
        all_games = []
        characters_played = set()
        opponents_faced = set()
        opponent_characters_faced = set()
        
        for game in games_raw:
            try:
                player_data = json.loads(game['player_data'])
                
                player_info = None
                opponent_info = None
                
                for player in player_data:
                    if player.get('player_tag') == player_code:
                        player_info = player
                
                if not player_info:
                    continue
                    
                for player in player_data:
                    if player != player_info:
                        opponent_info = player
                        break
                
                if not opponent_info:
                    continue
                
                characters_played.add(player_info.get('character_name', 'Unknown'))
                opponents_faced.add(opponent_info.get('player_tag', 'Unknown'))
                opponent_characters_faced.add(opponent_info.get('character_name', 'Unknown'))
                
                game_obj = {
                    'game_id': game['game_id'],
                    'start_time': game['start_time'],
                    'last_frame': game['last_frame'],
                    'game_duration_seconds': game['last_frame'] / 60,
                    'stage_id': game['stage_id'],
                    'player': player_info,
                    'opponent': opponent_info,
                    'result': player_info.get('result', 'Unknown'),
                    'date': game['start_time'].split('T')[0] if 'T' in game['start_time'] else game['start_time']
                }
                
                all_games.append(game_obj)
            except Exception as e:
                logger.error(f"Error processing game: {str(e)}")
                continue
        
        logger.info(f"Found {len(all_games)} total games for player '{player_code}'")
        
        # Apply filters with support for arrays (from POST data)
        filtered_games = all_games
        
        if character_filter != 'all':
            # Handle both string and array formats
            if isinstance(character_filter, str):
                character_values = character_filter.split('|') if '|' in character_filter else [character_filter]
            else:
                character_values = character_filter  # Already an array
            filtered_games = [g for g in filtered_games if g['player'].get('character_name') in character_values]
        
        if opponent_filter != 'all':
            if isinstance(opponent_filter, str):
                opponent_values = opponent_filter.split('|') if '|' in opponent_filter else [opponent_filter]
            else:
                opponent_values = opponent_filter
            filtered_games = [g for g in filtered_games if g['opponent'].get('player_tag') in opponent_values]
        
        if opponent_character_filter != 'all':
            if isinstance(opponent_character_filter, str):
                opp_char_values = opponent_character_filter.split('|') if '|' in opponent_character_filter else [opponent_character_filter]
            else:
                opp_char_values = opponent_character_filter
            filtered_games = [g for g in filtered_games if g['opponent'].get('character_name') in opp_char_values]
        
        logger.info(f"After filtering: {len(filtered_games)} games remain")
        
        # Rest of your calculation logic remains the same...
        total_filtered = len(filtered_games)
        wins_filtered = sum(1 for game in filtered_games if game['result'] == 'Win')
        overall_winrate = wins_filtered / total_filtered if total_filtered > 0 else 0
        
        # Calculate stats (same as existing code)...
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
        
        date_stats = {}
        for game in filtered_games:
            date = game['date']
            if date not in date_stats:
                date_stats[date] = {'games': 0, 'wins': 0}
            
            date_stats[date]['games'] += 1
            if game['result'] == 'Win':
                date_stats[date]['wins'] += 1
        
        for date in date_stats:
            date_stats[date]['win_rate'] = date_stats[date]['wins'] / date_stats[date]['games']
        
        date_stats_sorted = {k: date_stats[k] for k in sorted(date_stats.keys())}
        
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

@app.route('/api/player/<encoded_player_code>/character/<encoded_character>/games')
def api_player_character_games(encoded_player_code, encoded_character):
    try:
        # Decode the player code and character
        player_code = decode_player_tag(encoded_player_code)
        character_name = decode_player_tag(encoded_character)
        
        # Get page parameter
        page = request.args.get('page', '1')
        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        # Get all games for this player with this character
        games = get_player_games(player_code)
        character_games = [g for g in games if g['player']['character_name'] == character_name]
        
        # Calculate total pages
        total_games = len(character_games)
        total_pages = (total_games + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE
        
        # Get games for the requested page
        start_idx = (page - 1) * GAMES_PER_PAGE
        end_idx = min(start_idx + GAMES_PER_PAGE, total_games)
        
        # Check if request is for valid page
        if start_idx >= total_games:
            return jsonify({
                'total_games': total_games,
                'total_pages': total_pages,
                'current_page': page,
                'games': []
            })
            
        games_page = character_games[start_idx:end_idx]
        
        # Format games for response
        formatted_games = []
        for game in games_page:
            formatted_games.append({
                'date': game['start_time'],
                'opponent': game['opponent']['player_name'],
                'opponent_code': game['opponent']['player_tag'],
                'opponent_character': game['opponent']['character_name'],
                'stage': game['stage_id'],
                'result': game['result']
            })
        
        # Return JSON response
        response_data = {
            'total_games': total_games,
            'total_pages': total_pages,
            'current_page': page,
            'games': formatted_games
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in API character games route: {str(e)}")
        return jsonify({'error': str(e)}), 500        

@app.route('/api/clients/register', methods=['POST'])
def register_client():
    """
    API endpoint to register a new client.
    
    Returns:
        flask.Response: JSON response with registration status
    """
    client_data = request.json
    
    # Validate registration key
    registration_key = request.headers.get('X-Registration-Key')
    if not registration_key or registration_key != REGISTRATION_SECRET:
        logger.warning(f"Registration attempt with invalid key from {request.remote_addr}")
        abort(401, description="Invalid registration key")
    
    client_id = client_data.get('client_id')
    if not client_id:
        abort(400, description="Missing client_id in request")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Check if client already exists
        c.execute("SELECT client_id FROM clients WHERE client_id = ?", (client_id,))
        existing = c.fetchone()
        
        if existing:
            # Update client info
            c.execute('''
            UPDATE clients 
            SET hostname = ?, platform = ?, version = ?, last_active = ?
            WHERE client_id = ?
            ''', (
                client_data.get('hostname', 'Unknown'), 
                client_data.get('platform', 'Unknown'), 
                client_data.get('version', 'Unknown'),
                datetime.now().isoformat(),
                client_id
            ))
        else:
            # Insert new client
            c.execute('''
            INSERT INTO clients (client_id, hostname, platform, version, registration_date, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                client_id,
                client_data.get('hostname', 'Unknown'),
                client_data.get('platform', 'Unknown'),
                client_data.get('version', 'Unknown'),
                client_data.get('registration_date', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        
        # Generate API key for the client
        api_key_data = create_api_key(client_id)
        
        logger.info(f"Client registered/updated: {client_id}")
        
        return jsonify({
            "status": "success", 
            "message": "Client registered successfully",
            "api_key": api_key_data['api_key'],
            "expires_at": api_key_data['expires_at']
        })
        
    except Exception as e:
        logger.error(f"Error registering client: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/games/upload', methods=['POST'])
@require_api_key
@rate_limited(60)  # Limit to 60 uploads per minute per client
def upload_games(client_id):
    """
    API endpoint for uploading game data.
    
    Args:
        client_id (str): Client ID from the API key validation
        
    Returns:
        flask.Response: JSON response with upload status
    """
    upload_data = request.json
    
    # Verify client_id in token matches client_id in request
    if upload_data.get('client_id') != client_id:
        logger.warning(f"Client ID mismatch: {upload_data.get('client_id')} vs {client_id}")
        abort(403, description="Client ID in request does not match API key")
    
    games = upload_data.get('games', [])
    
    if not games:
        return jsonify({
            "status": "success",
            "message": "No games to process",
            "new_games": 0,
            "duplicates": 0
        })
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Update client last active time
        c.execute('''
        UPDATE clients SET last_active = ? WHERE client_id = ?
        ''', (datetime.now().isoformat(), client_id))
        
        # Process each game
        new_games = 0
        duplicates = 0
        errors = 0
        
        for game in games:
            try:
                # Validate game data structure
                if 'metadata' not in game or 'player_data' not in game:
                    errors += 1
                    continue

                logger.info(f"Checking for existing game with ID: {game.get('id', 'No ID found')}")
                
                # Check if this game already exists
                c.execute("SELECT game_id FROM games WHERE game_id = ?", (game["id"],))
                existing = c.fetchone()

                if not existing:
                    logger.info(f"New game with ID: {game.get('id', 'No ID found')}")
                    # Get game_type, if present, otherwise use "unknown"
                    game_type = game.get("type", "unknown")
                    
                    c.execute('''
                    INSERT INTO games (
                        game_id, client_id, start_time, 
                        last_frame, stage_id, player_data, upload_date, game_type
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        game["id"],
                        client_id,
                        game['metadata']['start_time'],
                        game['metadata']['last_frame'],
                        game['metadata']['stage_id'],
                        json.dumps(game['player_data']),
                        datetime.now().isoformat(),
                        game_type
                    ))
                    new_games += 1
                else:
                    logger.info(f"Found duplicate game with ID: {game.get('id', 'No ID found')}")
                    duplicates += 1
            except Exception as e:
                logger.error(f"Error processing game: {str(e)}")
                errors += 1
        
        conn.commit()
        
        logger.info(f"Upload from {client_id}: {new_games} new, {duplicates} duplicates, {errors} errors")
        
        return jsonify({
            "status": "success", 
            "new_games": new_games,
            "duplicates": duplicates,
            "errors": errors
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    API endpoint to get server statistics.
    
    Returns:
        flask.Response: JSON response with server statistics
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Get total counts
        c.execute("SELECT COUNT(*) FROM clients")
        client_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM games")
        game_count = c.fetchone()[0]
        
        # Get recent uploads
        c.execute("SELECT upload_date FROM games ORDER BY upload_date DESC LIMIT 1")
        latest_game = c.fetchone()
        last_upload = latest_game[0] if latest_game else None
        
        return jsonify({
            "total_clients": client_count,
            "total_games": game_count,
            "last_upload": last_upload
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        abort(500, description=f"Server error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/download')
def download_page():
    """
    Download page for the Slippi Stats Client.
    
    Returns:
        str: Rendered HTML template
    """
    # Get the latest version information
    # You can modify this to dynamically get the version from your file system
    version = "1.0.0"
    release_date = "May 4, 2025"
    download_url = "/download/SlippiMonitor.msi"
    
    return render_template('pages/download.html', 
                          version=version,
                          release_date=release_date,
                          download_url=download_url)

@app.route('/download/<filename>')
def download_file(filename):
    """
    Handle the actual file download.
    
    Args:
        filename (str): Name of the file to download
        
    Returns:
        flask.Response: File download response
    """
    # Path to your downloads directory
    downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    
    # Ensure the directory exists
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Return the file
    return send_from_directory(path=downloads_dir, filename=filename, as_attachment=True)

@app.route('/how-to')
def how_to_page():
    """
    How-to page with instructions for using the Slippi Stats Client.
    
    Returns:
        str: Rendered HTML template
    """
    return render_template('pages/how_to.html')            

# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return render_template('pages/error_status.html', 
                          status_code=400,
                          error_description=str(error.description)), 400

@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    return render_template('pages/error_status.html', 
                          status_code=401,
                          error_description=str(error.description)), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return render_template('pages/error_status.html', 
                          status_code=403,
                          error_description=str(error.description)), 403

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 Not Found errors with enhanced template"""
    return render_template('pages/error_status.html', 
                          status_code=404,
                          error_description=str(error.description)), 404

@app.errorhandler(429)
def too_many_requests(error):
    """Handle 429 Too Many Requests errors"""
    return render_template('pages/error_status.html', 
                          status_code=429,
                          error_description=str(error.description)), 429

@app.errorhandler(500)
def server_error(error):
    """Handle 500 Internal Server Error with enhanced template"""
    return render_template('pages/error_status.html', 
                          status_code=500,
                          error_description=str(error)), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all other exceptions with the exception template"""
    logger.error(f"Unhandled exception: {str(error)}")
    return render_template('pages/error_exception.html', 
                          error=str(error)), 500

# =============================================================================
# Application Initialization
# =============================================================================

# Initialize the database when the module is loaded
init_db()

# Run the application if this file is executed directly
if __name__ == '__main__':
    # Create templates directory if running standalone
    os.makedirs('templates', exist_ok=True)
    # Start the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)