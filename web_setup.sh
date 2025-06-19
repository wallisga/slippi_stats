#!/bin/bash
# Setup script for Slippi Stats Web Service

# Exit on any error
set -e

echo "Setting up Slippi Stats Web Service..."

# Variables
APP_DIR="/opt/slippi-web"
API_DIR="/opt/slippi-server/app"
STATIC_DIR="$APP_DIR/static"
TEMPLATES_DIR="$APP_DIR/templates"
SERVICE_NAME="slippi-web"
PORT=8000

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Create directories
echo "Creating application directories..."
mkdir -p $APP_DIR
mkdir -p $STATIC_DIR
mkdir -p $STATIC_DIR/characters
mkdir -p $STATIC_DIR/stages
mkdir -p $TEMPLATES_DIR

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install flask gunicorn

# Create systemd service
echo "Setting up systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Slippi Stats Web Service
After=network.target

[Service]
User=slippi
Group=slippi
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create main application file
echo "Creating application file..."
cat > $APP_DIR/app.py << 'EOF'
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os
import logging
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="stats_server.log"
)
logger = logging.getLogger('SlippiStatsWeb')

app = Flask(__name__)

# Configuration
DATABASE_PATH = '/opt/slippi-server/app/slippi_data.db'  # Path to the SQLite database from the API server

# Uncomment for testing on local Windows Machine
DATABASE_PATH = 'C:\\Users\\Gavin\\Code\\slippiscrape\\server\\slippi_data.db'

GAMES_PER_PAGE = 20  # Number of games to show per page
MIN_GAMES_FOR_STATS = 10  # Minimum number of games needed for meaningful statistics

# Helper Functions
def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def player_exists(player_code):
    """Check if a player exists in the database"""
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
    """Get all games for a specific player"""
    logger.info(f"Getting games for player: '{player_code}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all games
    cursor.execute("SELECT game_id, start_time, last_frame, stage_id, player_data FROM games")
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

def calculate_player_stats(games):
    """Calculate comprehensive statistics for a player"""
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

# Helper function to encode player tag for URL
def encode_player_tag(tag):
    return urllib.parse.quote(tag)

# Helper function to decode player tag from URL
def decode_player_tag(encoded_tag):
    return urllib.parse.unquote(encoded_tag)

def find_player_with_flexible_matching(player_code):
    """
    Find a player with more flexible matching criteria.
    This can help identify issues with exact matching that's failing.
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

# Routes
@app.route('/')
def index():
    """Main landing page"""
    # Count total games and players in database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count total games
        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]
        
        # Count unique player tags (simplified approach)
        cursor.execute("SELECT COUNT(DISTINCT substr(player_data, instr(player_data, 'player_tag')+13, 10)) FROM games")
        total_players = cursor.fetchone()[0]
        
        # Get recent games
        cursor.execute("""
        SELECT start_time, player_data
        FROM games
        ORDER BY start_time DESC
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
        
        # Process data in Python to get top players
        cursor.execute("SELECT player_data FROM games")
        all_games = cursor.fetchall()
        
        # Process the data in Python instead of complex SQLite JSON queries
        players_data = {}
        
        for row in all_games:
            try:
                player_data = json.loads(row['player_data'])
                for player in player_data:
                    if 'player_tag' not in player or not player['player_tag']:
                        continue
                        
                    tag = player['player_tag']
                    if tag not in players_data:
                        players_data[tag] = {
                            'name': player.get('player_name', tag),
                            'games': 0,
                            'wins': 0
                        }
                    
                    players_data[tag]['games'] += 1
                    if player.get('result') == 'Win':
                        players_data[tag]['wins'] += 1
            except Exception as e:
                logger.error(f"Error processing player data: {str(e)}")
                continue
        
        # Sort players by number of games
        top_players_list = sorted(
            [{'tag': tag, **data} for tag, data in players_data.items()],
            key=lambda x: x['games'],
            reverse=True
        )[:6]
        
        # Calculate win rates
        top_players = []
        for player in top_players_list:
            win_rate = player['wins'] / player['games'] if player['games'] > 0 else 0
            top_players.append({
                'code': player['tag'],
                'code_encoded': encode_player_tag(player['tag']),
                'name': player['name'],
                'games': player['games'],
                'win_rate': win_rate
            })
        
        conn.close()
        
        return render_template('index.html', 
                              total_games=total_games, 
                              total_players=total_players,
                              recent_games=recent_games,
                              top_players=top_players)
                              
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/player/<encoded_player_code>')
def player_profile(encoded_player_code):
    """Player profile page"""
    try:
        # Decode the player code from URL
        player_code = decode_player_tag(encoded_player_code)
        logger.info(f"Requested player profile: '{player_code}' (encoded as '{encoded_player_code}')")
        
        # Get all games for this player - bypass player_exists check
        games = get_player_games(player_code)
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
        
        return render_template('player.html', 
                              player_code=player_code,
                              encoded_player_code=encoded_player_code,
                              stats=stats,
                              recent_games=recent_games)
                              
    except Exception as e:
        logger.error(f"Error in player profile route: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/api/player/<encoded_player_code>/games')
def api_player_games(encoded_player_code):
    """API endpoint to get a player's games with pagination"""
    try:
        # Decode the player code
        player_code = decode_player_tag(encoded_player_code)
        
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
        
        # Get all games for this player
        all_games = get_player_games(player_code)
        
        # Calculate total pages
        total_games = len(all_games)
        total_pages = (total_games + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE
        
        # Get games for the requested page
        start_idx = (page - 1) * GAMES_PER_PAGE
        end_idx = start_idx + GAMES_PER_PAGE
        games_page = all_games[start_idx:end_idx]
        
        return jsonify({
            'total_games': total_games,
            'total_pages': total_pages,
            'current_page': page,
            'games': games_page
        })
        
    except Exception as e:
        logger.error(f"Error in API games route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/player/<encoded_player_code>/stats')
def api_player_stats(encoded_player_code):
    """API endpoint to get a player's statistics"""
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

@app.route('/api/stats')
def api_general_stats():
    """API endpoint to get general statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get last upload time using start_time instead of timestamp
        cursor.execute("SELECT MAX(start_time) as last_upload FROM games")
        last_upload = cursor.fetchone()['last_upload']
        
        conn.close()
        
        return jsonify({
            'last_upload': last_upload
        })
        
    except Exception as e:
        logger.error(f"Error in API general stats route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/players')
def players():
    """Debug endpoint to see all players in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all games data
        cursor.execute("SELECT player_data FROM games")
        games = cursor.fetchall()
        
        # Extract all player tags
        all_players = {}
        for row in games:
            try:
                players = json.loads(row['player_data'])
                for player in players:
                    if 'player_tag' in player and player['player_tag']:
                        tag = player['player_tag']
                        if tag not in all_players:
                            all_players[tag] = {
                                'name': player.get('player_name', ''),
                                'characters': set(),
                                'count': 0
                            }
                        
                        all_players[tag]['count'] += 1
                        if 'character_name' in player:
                            all_players[tag]['characters'].add(player['character_name'])
            except Exception as e:
                logger.error(f"Error processing player data: {str(e)}")
                continue
        
        # Convert to list for template rendering
        players_list = []
        for tag, data in all_players.items():
            players_list.append({
                'tag': tag,
                'encoded_tag': encode_player_tag(tag),
                'name': data['name'],
                'characters': ', '.join(data['characters']),
                'count': data['count']
            })
        
        # Sort by count descending
        players_list.sort(key=lambda x: x['count'], reverse=True)
        
        conn.close()
        
        return render_template('players.html', players=players_list)
        
    except Exception as e:
        logger.error(f"Error in debug players route: {str(e)}")
        return render_template('error.html', error=str(e))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e.description), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', error=str(e)), 500

if __name__ == '__main__':
    # Create templates directory if running standalone
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
EOF

# Create template files
echo "Creating template files..."
cat > $TEMPLATES_DIR/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .jumbotron {
            padding: 2rem;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .stat-card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            margin-bottom: 1.5rem;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .player-card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 1.5rem;
            cursor: pointer;
        }
        .player-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .search-container {
            max-width: 500px;
            margin: 0 auto 2rem auto;
        }
        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        .error-message {
            text-align: center;
            padding: 2rem;
            color: #dc3545;
        }
        
        /* Character icons */
        .character-icon {
            margin-right: 8px;
            vertical-align: middle;
        }
        
        .character-icon-fallback {
            display: inline-block;
            width: 24px;
            height: 24px;
            background-color: #f8f9fa;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            text-align: center;
            line-height: 24px;
            font-size: 10px;
            font-weight: bold;
            color: #495057;
        }
        
        /* Character-specific fallback colors */
        .character-icon-fallback[data-character="fox"] {
            background-color: #fd7e14;
            color: white;
        }
        
        .character-icon-fallback[data-character="falco"] {
            background-color: #0d6efd;
            color: white;
        }
        
        .character-icon-fallback[data-character="marth"] {
            background-color: #0dcaf0;
            color: white;
        }
        
        .character-container {
            display: inline-flex;
            align-items: center;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/#recent">Recent</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/players">Player Index</a>
                    </li> 
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="jumbotron">
            <h1 class="display-4">Slippi Stats</h1>
            <p class="lead">Analyze your Super Smash Bros. Melee gameplay with detailed statistics.</p>
            <hr class="my-4">
            <p>Track your performance across different characters, stages, and matchups to improve your game.</p>
        </div>

        <div class="search-container">
            <form id="playerSearchForm" class="d-flex">
                <input class="form-control me-2" type="search" placeholder="Enter player tag (e.g. TEKT#518)" aria-label="Search" id="playerCodeInput">
                <button class="btn btn-primary" type="submit">Find Player</button>
            </form>
        </div>

        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Games</h5>
                        <p class="display-4">{{ total_games }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Players</h5>
                        <p class="display-4">{{ total_players }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stat-card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Last Updated</h5>
                        <p class="h4" id="lastUpdated">Loading...</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-7">
                <h2 class="mb-3" id="stats">Recent Games</h2>
                <div class="card stat-card">
                    <div class="card-body">
                        {% if recent_games %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Player 1</th>
                                        <th>Character</th>
                                        <th>Player 2</th>
                                        <th>Character</th>
                                        <th>Winner</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for game in recent_games %}
                                    <tr>
                                        <td>{{ game.time }}</td>
                                        <td>
                                            <a href="/player/{{ game.player1_tag_encoded }}">{{ game.player1 }}</a>
                                        </td>
                                        <td>
                                            <span data-character-name="{{ game.character1 }}" class="character-container"></span>
                                            {{ game.character1 }}
                                        </td>
                                        <td>
                                            <a href="/player/{{ game.player2_tag_encoded }}">{{ game.player2 }}</a>
                                        </td>
                                        <td>
                                            <span data-character-name="{{ game.character2 }}" class="character-container"></span>
                                            {{ game.character2 }}
                                        </td>
                                        <td>
                                            {% if game.player1.result == 'Win' %}
                                            <a href="/player/{{ game.player1_tag_encoded }}">{{ game.player1 }}</a>
                                            {% else %}
                                            <a href="/player/{{ game.player2_tag_encoded }}">{{ game.player2 }}</a>
                                            {% endif %}
                                        </td>                                        
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="error-message">
                            <p>No recent games found.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <div class="col-md-5">
                <h2 class="mb-3" id="players">Top Players</h2>
                <div id="topPlayersContainer" class="row">
                    {% if top_players %}
                        {% for player in top_players %}
                        <div class="col-md-6">
                            <div class="card player-card" onclick="window.location.href='/player/{{ player.code_encoded }}'">
                                <div class="card-body">
                                    <h5 class="card-title">{{ player.name }}</h5>
                                    <p class="card-text">
                                        Games: {{ player.games }}<br>
                                        Win Rate: {{ (player.win_rate * 100) | round(1) }}%
                                    </p>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="error-message">
                            <p>No top players data available.</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>Slippi Stats - A tool for Super Smash Bros. Melee statistics</p>
            <p class="small">Powered by the Slippi Stats Collector</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Character icon handling
        function initializeCharacterIcons() {
            // Define the character mapping based on the config
            const characterMapping = {
                "Mario": "Mario",
                "Fox": "Fox",
                "Captain Falcon": "Captain Falcon",
                "Donkey Kong": "Donkey Kong",
                "Kirby": "Kirby",
                "Bowser": "Bowser",
                "Link": "Link",
                "Sheik": "Sheik", 
                "Ness": "Ness",
                "Peach": "Peach",
                "Ice Climbers": "Ice Climbers",
                "Yoshi": "Yoshi",
                "Pikachu": "Pikachu",
                "Samus": "Samus",
                "Jigglypuff": "Jigglypuff",
                "Mewtwo": "Mewtwo",
                "Luigi": "Luigi",
                "Marth": "Marth",
                "Zelda": "Zelda",
                "Young Link": "Young Link",
                "Doctor Mario": "Doctor Mario",
                "Dr. Mario": "Doctor Mario",
                "Falco": "Falco",
                "Pichu": "Pichu",
                "Game & Watch": "Game & Watch",
                "Mr. Game & Watch": "Game & Watch",
                "Ganondorf": "Ganondorf",
                "Roy": "Roy"
            };

            document.querySelectorAll('[data-character-name]').forEach(function(element) {
                const characterName = element.getAttribute('data-character-name');
                if (characterName && characterMapping[characterName]) {
                    // Create the image element
                    const img = document.createElement('img');
                    img.src = `/static/icons/character/neutral ${characterMapping[characterName]}.png`;
                    img.alt = characterName;
                    img.width = 24;
                    img.height = 24;
                    img.className = 'character-icon';
                    
                    // Add error handling
                    img.onerror = function() {
                        // If image fails to load, replace with character initial
                        this.style.display = 'none';
                        const span = document.createElement('span');
                        span.className = 'character-icon-fallback';
                        span.textContent = characterName.charAt(0);
                        // Add the character as data attribute for styling
                        span.setAttribute('data-character', characterName.toLowerCase().replace(/ /g, '_'));
                        this.parentNode.insertBefore(span, this.nextSibling);
                    };
                    
                    // Add to the DOM
                    element.appendChild(img);
                } else {
                    // Fallback for unknown characters
                    const span = document.createElement('span');
                    span.className = 'character-icon-fallback';
                    span.textContent = characterName ? characterName.charAt(0) : '?';
                    if (characterName) {
                        span.setAttribute('data-character', characterName.toLowerCase().replace(/ /g, '_'));
                    }
                    element.appendChild(span);
                }
            });
        }
        
        // Update last updated time
        function updateLastUpdated() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.last_upload) {
                        const date = new Date(data.last_upload);
                        document.getElementById('lastUpdated').textContent = date.toLocaleString();
                    } else {
                        document.getElementById('lastUpdated').textContent = 'No data yet';
                    }
                })
                .catch(error => {
                    console.error('Error fetching stats:', error);
                    document.getElementById('lastUpdated').textContent = 'Error loading data';
                });
        }
        
        // Player search form
        document.getElementById('playerSearchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const playerCode = document.getElementById('playerCodeInput').value.trim();
            if (playerCode) {
                // Encode the player tag for URL
                const encodedTag = encodeURIComponent(playerCode);
                window.location.href = `/player/${encodedTag}`;
            }
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateLastUpdated();
            initializeCharacterIcons();
        });
    </script>
</body>
</html>
EOF

cat > $TEMPLATES_DIR/player.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ player_code }} | Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .stat-card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .win-rate-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#198754 0% calc(var(--win-rate) * 100%), #dee2e6 calc(var(--win-rate) * 100%) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            position: relative;
        }
        .win-rate-inner {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
        }
        .character-badge {
            text-align: center;
            margin-bottom: 15px;
        }
        .matchup-bar {
            height: 24px;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        .error-message {
            text-align: center;
            padding: 2rem;
            color: #dc3545;
        }
        .no-data-message {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }
        
        /* Character icons */
        .character-icon {
            display: inline-block;
            width: 24px;
            height: 24px;
            background-color: #f8f9fa;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            position: relative;
            text-align: center;
            line-height: 24px;
            font-size: 10px;
            font-weight: bold;
            color: #495057;
        }
        
        .character-badge .character-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 10px auto;
            display: block;
            line-height: 64px;
            font-size: 24px;
        }
        
        /* Character-specific colors */
        .character-icon[data-character="fox"] {
            background-color: #fd7e14;
            color: white;
        }
        
        .character-icon[data-character="falco"] {
            background-color: #0d6efd;
            color: white;
        }
        
        .character-icon[data-character="marth"] {
            background-color: #0dcaf0;
            color: white;
        }
        
        .character-icon[data-character="captain_falcon"] {
            background-color: #dc3545;
            color: white;
        }
        
        .character-icon[data-character="jigglypuff"] {
            background-color: #d63384;
            color: white;
        }
        
        .character-icon[data-character="peach"] {
            background-color: #ffc107;
        }
        
        .character-icon[data-character="sheik"] {
            background-color: #6f42c1;
            color: white;
        }
        
        .character-icon[data-character="ice_climbers"] {
            background-color: #6c757d;
            color: white;
        }
        
        .character-icon[data-character="pikachu"] {
            background-color: #ffc107;
        }
        
        .character-icon[data-character="samus"] {
            background-color: #fd7e14;
            color: white;
        }
        
        .character-icon[data-character="ganondorf"] {
            background-color: #6c757d;
            color: white;
        }
        
        .character-icon[data-character="young_link"] {
            background-color: #20c997;
            color: white;
        }
        
        .character-icon[data-character="mario"] {
            background-color: #dc3545;
            color: white;
        }
        
        .character-icon[data-character="luigi"] {
            background-color: #198754;
            color: white;
        }
        
        .character-icon[data-character="dr_mario"] {
            background-color: #0d6efd;
            color: white;
        }
        
        .character-icon[data-character="donkey_kong"] {
            background-color: #6c757d;
            color: white;
        }
        
        .character-icon[data-character="link"] {
            background-color: #20c997;
            color: white;
        }
        
        .character-icon[data-character="zelda"] {
            background-color: #d63384;
            color: white;
        }
        
        .character-icon[data-character="mewtwo"] {
            background-color: #6f42c1;
            color: white;
        }
        
        .character-icon[data-character="game_&_watch"] {
            background-color: #000000;
            color: white;
        }
        
        .character-icon[data-character="bowser"] {
            background-color: #fd7e14;
            color: white;
        }
        
        .character-icon[data-character="ness"] {
            background-color: #6f42c1;
            color: white;
        }
        
        .character-icon[data-character="pichu"] {
            background-color: #ffc107;
        }
        
        .character-icon[data-character="yoshi"] {
            background-color: #20c997;
            color: white;
        }
        
        .character-icon[data-character="kirby"] {
            background-color: #d63384;
            color: white;
        }
        
        .character-icon[data-character="roy"] {
            background-color: #dc3545;
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/#recent">Recent</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/players">Player Index</a>
                    </li> 
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col-md-12">
                <h1 class="display-4">{{ player_code }}</h1>
                <p class="lead">Player Statistics</p>
            </div>
        </div>

        {% if stats and stats.total_games > 0 %}
        <div class="row mb-4">
            <!-- Overall Stats Card -->
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Overall Performance</h5>
                        <div class="win-rate-circle my-3" style="--win-rate: {{ stats.win_rate }}">
                            <div class="win-rate-inner">{{ (stats.win_rate * 100) | round(1) }}%</div>
                        </div>
                        <p class="card-text">
                            <strong>{{ stats.wins }}</strong> wins out of <strong>{{ stats.total_games }}</strong> games
                        </p>
                    </div>
                </div>
            </div>

            <!-- Most Played Character Card -->
            {% if stats.most_played_character %}
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Most Played Character</h5>
                        <div class="character-badge">
                            <span class="character-icon" data-character="{{ stats.most_played_character | lower | replace(' ', '_') }}">
                                {{ stats.most_played_character | truncate(1, true, '') }}
                            </span>
                            <h3>{{ stats.most_played_character }}</h3>
                        </div>
                        <p class="card-text">
                            <strong>{{ stats.character_stats[stats.most_played_character].games }}</strong> games
                            <br>
                            <strong>{{ (stats.character_stats[stats.most_played_character].win_rate * 100) | round(1) }}%</strong> win rate
                        </p>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- Best Character Card -->
            {% if stats.best_character %}
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Best Character</h5>
                        <div class="character-badge">
                            <span class="character-icon" data-character="{{ stats.best_character | lower | replace(' ', '_') }}">
                                {{ stats.best_character | truncate(1, true, '') }}
                            </span>
                            <h3>{{ stats.best_character }}</h3>
                        </div>
                        <p class="card-text">
                            <strong>{{ stats.character_stats[stats.best_character].games }}</strong> games
                            <br>
                            <strong>{{ (stats.character_stats[stats.best_character].win_rate * 100) | round(1) }}%</strong> win rate
                        </p>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <div class="row mb-4">
            <!-- Rising Star Card -->
            {% if stats.rising_star %}
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100 text-white bg-primary">
                    <div class="card-body text-center">
                        <h5 class="card-title">On The Rise</h5>
                        <div class="character-badge">
                            <span class="character-icon" data-character="{{ stats.rising_star | lower | replace(' ', '_') }}" style="background-color: #fff; color: #0d6efd;">
                                {{ stats.rising_star | truncate(1, true, '') }}
                            </span>
                            <h3>{{ stats.rising_star }}</h3>
                        </div>
                        <p class="card-text">
                            Best recent performance
                            <br>
                            <small>Based on last 30 games</small>
                        </p>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- Rival Card -->
            {% if stats.rival %}
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100 text-white bg-danger">
                    <div class="card-body text-center">
                        <h5 class="card-title">Rival</h5>
                        <div class="d-flex justify-content-center align-items-center my-3">
                            <strong class="me-2">{{ stats.rival.opponent_tag }}</strong>
                            playing
                            <span class="character-icon ms-2" data-character="{{ stats.rival.opponent_char | lower | replace(' ', '_') }}" style="background-color: #fff; color: #dc3545;">
                                {{ stats.rival.opponent_char | truncate(1, true, '') }}
                            </span>
                        </div>
                        <h3>{{ stats.rival.opponent_tag }}</h3>
                        <p class="card-text">
                            <strong>{{ stats.rival.win_rate * 100 | round(1) }}%</strong> win rate against them
                            <br>
                            <small>{{ stats.rival.wins }} wins out of {{ stats.rival.games }} games</small>
                        </p>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- Worst Character Card -->
            {% if stats.worst_character %}
            <div class="col-md-4 mb-4">
                <div class="card stat-card h-100 text-white bg-dark">
                    <div class="card-body text-center">
                        <h5 class="card-title">Toxic Relationship</h5>
                        <div class="character-badge">
                            <span class="character-icon" data-character="{{ stats.worst_character | lower | replace(' ', '_') }}" style="background-color: #fff; color: #212529;">
                                {{ stats.worst_character | truncate(1, true, '') }}
                            </span>
                            <h3>{{ stats.worst_character }}</h3>
                        </div>
                        <p class="card-text">
                            <strong>{{ stats.character_stats[stats.worst_character].games }}</strong> games
                            <br>
                            <strong>{{ (stats.character_stats[stats.worst_character].win_rate * 100) | round(1) }}%</strong> win rate
                        </p>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <div class="row mb-4">
            <!-- Character Stats -->
            {% if stats.character_stats and stats.character_stats|length > 0 %}
            <div class="col-md-6 mb-4">
                <div class="card stat-card">
                    <div class="card-header">
                        <h5>Character Stats</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container" style="position: relative; height:400px;">
                            <canvas id="characterStatsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- Stage Stats -->
            {% if stats.stage_stats and stats.stage_stats|length > 0 %}
            <div class="col-md-6 mb-4">
                <div class="card stat-card">
                    <div class="card-header">
                        <h5>Stage Performance</h5>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                {% if stats.best_stage %}
                                <div class="card bg-success text-white mb-3">
                                    <div class="card-body">
                                        <h6 class="card-title">Best Stage</h6>
                                        <p class="card-text">
                                            Stage ID: {{ stats.best_stage.id }}<br>
                                            Win Rate: {{ (stats.best_stage.win_rate * 100) | round(1) }}%<br>
                                            Games: {{ stats.best_stage.games }}
                                        </p>
                                    </div>
                                </div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                {% if stats.worst_stage %}
                                <div class="card bg-danger text-white">
                                    <div class="card-body">
                                        <h6 class="card-title">Worst Stage</h6>
                                        <p class="card-text">
                                            Stage ID: {{ stats.worst_stage.id }}<br>
                                            Win Rate: {{ (stats.worst_stage.win_rate * 100) | round(1) }}%<br>
                                            Games: {{ stats.worst_stage.games }}
                                        </p>
                                    </div>
                                </div>
                                {% endif %}
                            </div>
                        </div>
                        <div class="chart-container" style="position: relative; height:300px;">
                            <canvas id="stageStatsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>

        <!-- Recent Games -->
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="card stat-card">
                    <div class="card-header">
                        <h5>Recent Games</h5>
                    </div>
                    <div class="card-body">
                        {% if recent_games and recent_games|length > 0 %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Character</th>
                                        <th>Opponent</th>
                                        <th>Opponent's Character</th>
                                        <th>Result</th>
                                    </tr>
                                </thead>
                                <tbody id="recentGamesTable">
                                    {% for game in recent_games %}
                                    <tr>
                                        <td>{{ game.start_time }}</td>
                                        <td>
                                            <span class="character-icon" data-character="{{ game.player.character_name | lower | replace(' ', '_') }}">
                                                {{ game.player.character_name | truncate(1, true, '') }}
                                            </span>
                                            {{ game.player.character_name }}
                                        </td>
                                        <td>
                                            {% set opponent_tag_encoded = game.opponent.player_tag | urlencode %}
                                            <a href="/player/{{ opponent_tag_encoded }}">
                                                {{ game.opponent.player_name }}
                                            </a>
                                        </td>
                                        <td>
                                            <span class="character-icon" data-character="{{ game.opponent.character_name | lower | replace(' ', '_') }}">
                                                {{ game.opponent.character_name | truncate(1, true, '') }}
                                            </span>
                                            {{ game.opponent.character_name }}
                                        </td>
                                        <td>
                                            {% if game.result == 'Win' %}
                                            <span class="badge bg-success">Win</span>
                                            {% else %}
                                            <span class="badge bg-danger">Loss</span>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        <div class="d-flex justify-content-center mt-3">
                            <button id="loadMoreGames" class="btn btn-primary">Load More Games</button>
                        </div>
                        {% else %}
                        <div class="no-data-message">
                            <p>No recent games found for this player.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% else %}
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <div class="no-data-message">
                            <h3>No statistics available</h3>
                            <p>This player has no recorded games yet or not enough data to generate statistics.</p>
                            <a href="/" class="btn btn-primary mt-3">Return to Home</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>Slippi Stats - A tool for Super Smash Bros. Melee statistics</p>
            <p class="small">Powered by the Slippi Stats Collector</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    {% if stats and stats.character_stats and stats.character_stats|length > 0 %}
    <script>
        // Character Stats Chart
        const charCtx = document.getElementById('characterStatsChart').getContext('2d');
        const characterData = {
            labels: [
                {% for char, data in stats.character_stats.items() %}
                '{{ char }}',
                {% endfor %}
            ],
            datasets: [
                {
                    label: 'Games',
                    data: [
                        {% for char, data in stats.character_stats.items() %}
                        {{ data.games }},
                        {% endfor %}
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Win Rate (%)',
                    data: [
                        {% for char, data in stats.character_stats.items() %}
                        {{ data.win_rate * 100 }},
                        {% endfor %}
                    ],
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        };
        
        new Chart(charCtx, {
            type: 'bar',
            data: characterData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Games Played'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Win Rate (%)'
                        },
                        max: 100,
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    </script>
    {% endif %}

    {% if stats and stats.stage_stats and stats.stage_stats|length > 0 %}
    <script>
        // Stage Stats Chart
        const stageCtx = document.getElementById('stageStatsChart').getContext('2d');
        const stageData = {
            labels: [
                {% for stage_id, data in stats.stage_stats.items() %}
                'Stage {{ stage_id }}',
                {% endfor %}
            ],
            datasets: [{
                label: 'Win Rate (%)',
                data: [
                    {% for stage_id, data in stats.stage_stats.items() %}
                    {{ data.win_rate * 100 }},
                    {% endfor %}
                ],
                backgroundColor: [
                    {% for stage_id, data in stats.stage_stats.items() %}
                    `rgba(${Math.min(255, 255 * (1 - data.win_rate * 2 + 1))}, ${Math.min(255, 255 * data.win_rate * 2)}, 0, 0.7)`,
                    {% endfor %}
                ],
                borderWidth: 1
            }]
        };
        
        new Chart(stageCtx, {
            type: 'bar',
            data: stageData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Win Rate (%)'
                        }
                    }
                }
            }
        });
    </script>
    {% endif %}

    <script>
        // Initialize character icons
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize all character icons
            initializeCharacterIcons();
        });
        
        function initializeCharacterIcons() {
            // For each character icon, set the first letter as content if not already set
            document.querySelectorAll('.character-icon:not([data-initialized])').forEach(function(icon) {
                const character = icon.getAttribute('data-character');
                if (character) {
                    // Set initials to first letter (or first letters if multiple words)
                    const initials = character.split('_')
                                           .map(word => word.charAt(0))
                                           .join('')
                                           .toUpperCase();
                                           
                    icon.setAttribute('data-initials', initials);
                    icon.setAttribute('data-initialized', 'true');
                    
                    // Set the initial as content
                    icon.textContent = initials;
                }
            });
        }
        
        // Load More Games Button
        let currentPage = 1;
        const loadMoreGames = document.getElementById('loadMoreGames');
        
        if (loadMoreGames) {
            loadMoreGames.addEventListener('click', function() {
                currentPage++;
                
                fetch(`/api/player/{{ encoded_player_code }}/games?page=${currentPage}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.games && data.games.length > 0) {
                            const tableBody = document.getElementById('recentGamesTable');
                            
                            data.games.forEach(game => {
                                const row = document.createElement('tr');
                                const opponentTagEncoded = encodeURIComponent(game.opponent.player_tag);
                                const playerCharacter = game.player.character_name.toLowerCase().replace(' ', '_');
                                const opponentCharacter = game.opponent.character_name.toLowerCase().replace(' ', '_');
                                const playerInitial = game.player.character_name.charAt(0);
                                const opponentInitial = game.opponent.character_name.charAt(0);
                                
                                row.innerHTML = `
                                    <td>${game.start_time}</td>
                                    <td>
                                        <span class="character-icon" data-character="${playerCharacter}">
                                            ${playerInitial}
                                        </span>
                                        ${game.player.character_name}
                                    </td>
                                    <td>
                                        <a href="/player/${opponentTagEncoded}">
                                            ${game.opponent.player_name}
                                        </a>
                                    </td>
                                    <td>
                                        <span class="character-icon" data-character="${opponentCharacter}">
                                            ${opponentInitial}
                                        </span>
                                        ${game.opponent.character_name}
                                    </td>
                                    <td>
                                        ${game.result === 'Win' 
                                            ? '<span class="badge bg-success">Win</span>' 
                                            : '<span class="badge bg-danger">Loss</span>'}
                                    </td>
                                `;
                                tableBody.appendChild(row);
                            });
                            
                            // Initialize the character icons in the new rows
                            initializeCharacterIcons();
                            
                            if (currentPage >= data.total_pages) {
                                loadMoreGames.disabled = true;
                                loadMoreGames.textContent = 'No More Games';
                            }
                        } else {
                            loadMoreGames.disabled = true;
                            loadMoreGames.textContent = 'No More Games';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading more games:', error);
                        loadMoreGames.textContent = 'Error Loading Games';
                        loadMoreGames.classList.remove('btn-primary');
                        loadMoreGames.classList.add('btn-danger');
                    });
            });
        }
    </script>
</body>
</html>
EOF

cat > $TEMPLATES_DIR/players.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug Players | Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .search-container {
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/#recent">Recent</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/players">Player Index</a>
                    </li>                    
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Player Index</h1>
        <p class="lead">Showing all player tags found in recent games</p>
        
        <div class="search-container">
            <input type="text" id="playerSearch" class="form-control" placeholder="Filter players...">
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover" id="playersTable">
                        <thead>
                            <tr>
                                <th>Player Tag</th>
                                <th>Player Name</th>
                                <th>Characters</th>
                                <th>Game Count</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for player in players %}
                            <tr>
                                <td><code>{{ player.tag }}</code></td>
                                <td>{{ player.name }}</td>
                                <td>{{ player.characters }}</td>
                                <td>{{ player.count }}</td>
                                <td>
                                    <a href="/player/{{ player.encoded_tag }}" class="btn btn-sm btn-primary">View Profile</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Filter table based on search input
        document.getElementById('playerSearch').addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const table = document.getElementById('playersTable');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const tag = row.querySelector('td:first-child').textContent.toLowerCase();
                const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                
                if (tag.includes(searchTerm) || name.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
EOF

cat > $TEMPLATES_DIR/404.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Not Found | Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .error-container {
            text-align: center;
            padding: 5rem 1rem;
        }
        .error-icon {
            font-size: 5rem;
            color: #dc3545;
            margin-bottom: 2rem;
        }
        .error-message {
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-body error-container">
                        <div class="error-icon">
                            <i class="bi bi-exclamation-circle"></i>
                            ❌
                        </div>
                        <h1 class="display-4">Player Not Found</h1>
                        <div class="error-message">
                            <p class="lead">{{ error }}</p>
                            <p>The player tag you're looking for doesn't exist in our database or might be incorrectly formatted.</p>
                            <p>Player tags are case sensitive and should include the formatting used in-game (e.g., "TEKT#518").</p>
                        </div>
                        <div class="d-grid gap-2 col-6 mx-auto">
                            <a href="/" class="btn btn-primary btn-lg">Return to Home</a>
                        </div>
                    </div>
                </div>
                
                <div class="card mt-4">
                    <div class="card-body">
                        <h5 class="card-title">Searching Tips</h5>
                        <ul>
                            <li>Make sure to include any special characters like # and numbers</li>
                            <li>Check the capitalization of your player tag</li>
                            <li>Try searching for a different variation of your tag</li>
                            <li>Only players with recorded matches will appear in the database</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>Slippi Stats - A tool for Super Smash Bros. Melee statistics</p>
            <p class="small">Powered by the Slippi Stats Collector</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

cat > $TEMPLATES_DIR/500.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error | Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .error-container {
            text-align: center;
            padding: 5rem 1rem;
        }
        .error-icon {
            font-size: 5rem;
            color: #dc3545;
            margin-bottom: 2rem;
        }
        .error-message {
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-body error-container">
                        <div class="error-icon">
                            <i class="bi bi-exclamation-triangle"></i>
                            ⚠️
                        </div>
                        <h1 class="display-4">Something Went Wrong</h1>
                        <div class="error-message">
                            <p class="lead">We encountered an error while processing your request.</p>
                            {% if error %}
                            <div class="alert alert-danger">
                                <p>{{ error }}</p>
                            </div>
                            {% endif %}
                            <p>Please try again later or return to the home page.</p>
                        </div>
                        <div class="d-grid gap-2 col-6 mx-auto">
                            <a href="/" class="btn btn-primary btn-lg">Return to Home</a>
                            <button class="btn btn-outline-secondary" onclick="window.history.back()">Go Back</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>Slippi Stats - A tool for Super Smash Bros. Melee statistics</p>
            <p class="small">Powered by the Slippi Stats Collector</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

cat > $TEMPLATES_DIR/error.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error | Slippi Stats</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .error-container {
            text-align: center;
            padding: 5rem 1rem;
        }
        .error-icon {
            font-size: 5rem;
            color: #dc3545;
            margin-bottom: 2rem;
        }
        .error-message {
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Slippi Stats</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 offset-md-2">
                <div class="card">
                    <div class="card-body error-container">
                        <div class="error-icon">
                            <i class="bi bi-exclamation-triangle"></i>
                            ⚠️
                        </div>
                        <h1 class="display-4">Something Went Wrong</h1>
                        <div class="error-message">
                            <p class="lead">We encountered an error while processing your request.</p>
                            {% if error %}
                            <div class="alert alert-danger">
                                <p>{{ error }}</p>
                            </div>
                            {% endif %}
                            <p>Please try again later or return to the home page.</p>
                        </div>
                        <div class="d-grid gap-2 col-6 mx-auto">
                            <a href="/" class="btn btn-primary btn-lg">Return to Home</a>
                            <button class="btn btn-outline-secondary" onclick="window.history.back()">Go Back</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p>Slippi Stats - A tool for Super Smash Bros. Melee statistics</p>
            <p class="small">Powered by the Slippi Stats Collector</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF

# Set proper permissions
echo "Setting permissions..."
chown -R slippi:slippi $APP_DIR
chmod -R 755 $APP_DIR

# Enable and start the service
echo "Starting the web service..."
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Setup complete! Slippi Stats Web Service is now running on port $PORT"
echo "You can access it through your web browser at the server's IP address"
echo "Check the service status with: systemctl status $SERVICE_NAME"