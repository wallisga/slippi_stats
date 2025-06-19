from flask import Flask, request, jsonify, abort
import sqlite3
import json
import uuid
import hashlib
import time
import secrets
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="server.log"
)
logger = logging.getLogger('SlippiServer')

app = Flask(__name__)

# Authentication constants
REGISTRATION_SECRET = "sl1pp1-s3rv3r-r3g1str4t10n-k3y-2025"  # Change this to your secret key
API_KEYS_TABLE = "api_keys"
TOKEN_EXPIRY_DAYS = 365  # API keys valid for 1 year

# Initialize database
def init_db():
    conn = sqlite3.connect('slippi_data.db')
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
        game_hash TEXT,
        start_time TEXT,
        last_frame INTEGER,
        stage_id INTEGER,
        player_data TEXT,
        upload_date TEXT,
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
    logger.info("Database initialized")

# Generate a unique hash for game deduplication
def generate_game_hash(game_data):
    """Generate a hash for deduplication based on start time and frame count"""
    key_data = f"{game_data['metadata']['start_time']}_{game_data['metadata']['last_frame']}"
    return hashlib.md5(key_data.encode()).hexdigest()

# Authentication helper functions
def generate_api_key():
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)

def create_api_key(client_id):
    """Create a new API key for a client"""
    api_key = generate_api_key()
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS)).isoformat()
    
    conn = sqlite3.connect('slippi_data.db')
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
    """Validate an API key and return client_id if valid"""
    if not api_key:
        return None
        
    conn = sqlite3.connect('slippi_data.db')
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

# Authentication decorator
def require_api_key(f):
    """Decorator to require a valid API key for endpoint access"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        client_id = validate_api_key(api_key)
        
        if not client_id:
            abort(401, description="Invalid or missing API key")
            
        # Add client_id to kwargs
        kwargs['client_id'] = client_id
        return f(*args, **kwargs)
    
    # Rename the function to preserve the original name
    decorated_function.__name__ = f.__name__
    return decorated_function

# Request limiter for retry logic
def rate_limited(max_per_minute):
    """Simple rate limiting decorator"""
    request_counts = {}
    
    def decorator(f):
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
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    return decorator

# API Routes
@app.route('/api/clients/register', methods=['POST'])
def register_client():
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
        conn = sqlite3.connect('slippi_data.db')
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
        conn = sqlite3.connect('slippi_data.db')
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
                
                # Generate hash for deduplication
                game_hash = generate_game_hash(game)
                
                # Check if this game already exists
                c.execute("SELECT game_id FROM games WHERE game_hash = ?", (game_hash,))
                existing = c.fetchone()
                
                if not existing:
                    # This is a new game
                    game_id = str(uuid.uuid4())
                    
                    c.execute('''
                    INSERT INTO games (
                        game_id, client_id, game_hash, start_time, 
                        last_frame, stage_id, player_data, upload_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        game_id,
                        client_id,
                        game_hash,
                        game['metadata']['start_time'],
                        game['metadata']['last_frame'],
                        game['metadata']['stage_id'],
                        json.dumps(game['player_data']),
                        datetime.now().isoformat()
                    ))
                    new_games += 1
                else:
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
    try:
        conn = sqlite3.connect('slippi_data.db')
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

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "status": "error",
        "message": str(error.description)
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "status": "error",
        "message": str(error.description)
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "status": "error",
        "message": str(error.description)
    }), 403

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({
        "status": "error",
        "message": str(error.description)
    }), 429

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "status": "error",
        "message": str(error.description)
    }), 500

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)