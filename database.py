"""
Database management for Slippi Server.

This module handles all database operations including initialization,
connection management, and core database functions.
"""

import sqlite3
import json
import logging
from contextlib import contextmanager
from config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger('SlippiServer')


class DatabaseManager:
    """Centralized database management class."""
    
    def __init__(self, db_path=None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or config.get_database_path()
        self._initialized = False
    
    def init_db(self):
        """
        Initialize the SQLite database with the required tables:
        - clients: Stores information about registered clients
        - games: Stores game data from uploaded replays
        - api_keys: Stores API keys for client authentication
        """
        if self._initialized:
            logger.debug("Database already initialized")
            return
        
        logger.info(f"Initializing database at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
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
            CREATE TABLE IF NOT EXISTS {config.API_KEYS_TABLE} (
                client_id TEXT PRIMARY KEY,
                api_key TEXT UNIQUE,
                created_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (client_id)
            )
            ''')
            
            # Create indexes for better performance
            self._create_indexes(c)
            
            conn.commit()
            self._initialized = True
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _create_indexes(self, cursor):
        """Create database indexes for better query performance."""
        indexes = [
            # Index on games.start_time for chronological queries
            "CREATE INDEX IF NOT EXISTS idx_games_start_time ON games (start_time)",
            
            # Index on games.client_id for client-specific queries
            "CREATE INDEX IF NOT EXISTS idx_games_client_id ON games (client_id)",
            
            # Index on games.upload_date for recent uploads
            "CREATE INDEX IF NOT EXISTS idx_games_upload_date ON games (upload_date)",
            
            # Index on api_keys.api_key for authentication
            f"CREATE INDEX IF NOT EXISTS idx_api_keys_key ON {config.API_KEYS_TABLE} (api_key)",
            
            # Index on clients.last_active for activity tracking
            "CREATE INDEX IF NOT EXISTS idx_clients_last_active ON clients (last_active)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.debug(f"Created index: {index_sql}")
            except Exception as e:
                logger.warning(f"Could not create index: {index_sql}, Error: {str(e)}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with Row factory enabled.
        
        Yields:
            sqlite3.Connection: Database connection with row_factory set to sqlite3.Row
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_db_connection(self):
        """
        Legacy method for backward compatibility.
        
        Returns:
            sqlite3.Connection: Database connection with row_factory set to sqlite3.Row
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """
        Execute a database query with automatic connection management.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            fetch_one (bool): Whether to fetch only one result
            fetch_all (bool): Whether to fetch all results
            
        Returns:
            Query results or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
    
    def check_database_health(self):
        """
        Check database health and return status information.
        
        Returns:
            dict: Database health status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check table existence
                cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('clients', 'games', ?)
                """, (config.API_KEYS_TABLE,))
                
                tables = [row['name'] for row in cursor.fetchall()]
                expected_tables = {'clients', 'games', config.API_KEYS_TABLE}
                missing_tables = expected_tables - set(tables)
                
                # Check record counts
                counts = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    counts[table] = cursor.fetchone()['count']
                
                # Check database file size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_bytes = page_count * page_size
                
                health_status = {
                    'status': 'healthy' if not missing_tables else 'unhealthy',
                    'database_path': self.db_path,
                    'tables_present': list(tables),
                    'missing_tables': list(missing_tables),
                    'record_counts': counts,
                    'database_size_bytes': db_size_bytes,
                    'database_size_mb': round(db_size_bytes / (1024 * 1024), 2)
                }
                
                return health_status
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'database_path': self.db_path
            }


# Global database manager instance
db_manager = DatabaseManager()


def init_db():
    """Initialize the database - backward compatibility function."""
    return db_manager.init_db()


def get_db_connection():
    """Get database connection - backward compatibility function."""
    return db_manager.get_db_connection()


# Convenience functions for common database operations
def get_table_count(table_name):
    """Get the number of records in a table."""
    return db_manager.execute_query(
        f"SELECT COUNT(*) as count FROM {table_name}",
        fetch_one=True
    )['count']


def get_latest_game_date():
    """Get the date of the most recent game."""
    result = db_manager.execute_query(
        "SELECT start_time FROM games ORDER BY datetime(start_time) DESC LIMIT 1",
        fetch_one=True
    )
    return result['start_time'] if result else None


# =============================================================================
# Player Data Functions
# =============================================================================

def get_player_games(player_code):
    """
    Get all games for a specific player, properly sorted by date (most recent first).
    
    Args:
        player_code (str): The player tag to look up
        
    Returns:
        list: List of game dictionaries for the specified player, sorted by start_time DESC
    """
    logger.info(f"Getting games for player: '{player_code}'")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all games sorted by date (most recent first)
            cursor.execute("""
            SELECT game_id, game_type, start_time, last_frame, stage_id, player_data 
            FROM games 
            ORDER BY datetime(start_time) DESC
            """)
            games_raw = cursor.fetchall()
            
            logger.info(f"Fetched {len(games_raw)} total games from database")
            
            # Process the games data to find this player's games
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
            
            # Ensure proper sorting (double-check)
            games_sorted = sorted(games, key=lambda x: x['start_time'], reverse=True)
            
            if games and games_sorted[0]['start_time'] != games[0]['start_time']:
                logger.warning(f"Database sort didn't work properly for {player_code}. "
                              f"DB first: {games[0]['start_time']}, "
                              f"Python sort first: {games_sorted[0]['start_time']}")
            
            return games_sorted
            
    except Exception as e:
        logger.error(f"Error getting games for player {player_code}: {str(e)}")
        return []


def find_player_matches(player_code):
    """
    Find potential player matches with flexible matching criteria.
    
    Args:
        player_code (str): The player tag to look up with flexible matching
        
    Returns:
        list: List of potential matches with match type and player data
    """
    logger.info(f"Finding flexible matches for player: '{player_code}'")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get a sample of games to check for matches
            cursor.execute("SELECT player_data FROM games LIMIT 1000")
            games = cursor.fetchall()
            
            matches = []
            seen_tags = set()  # Avoid duplicates
            
            for game in games:
                try:
                    player_data = json.loads(game['player_data'])
                    for player in player_data:
                        if 'player_tag' not in player or not player['player_tag']:
                            continue
                            
                        tag = player['player_tag']
                        
                        # Skip if we've already seen this tag
                        if tag in seen_tags:
                            continue
                        
                        # Try different matching criteria
                        exact_match = (tag == player_code)
                        case_insensitive = (tag.lower() == player_code.lower())
                        contains = (player_code in tag or tag in player_code)
                        
                        if exact_match or case_insensitive or contains:
                            seen_tags.add(tag)
                            matches.append({
                                'tag': tag,
                                'match_type': 'exact' if exact_match else ('case_insensitive' if case_insensitive else 'contains'),
                                'player_data': player
                            })
                except Exception as e:
                    logger.error(f"Error parsing game data: {str(e)}")
                    continue
            
            logger.info(f"Flexible matching found {len(matches)} potential matches")
            return matches
            
    except Exception as e:
        logger.error(f"Error finding player matches: {str(e)}")
        return []


def get_recent_games(limit=10):
    """
    Get recent games data for overview pages.
    
    Args:
        limit (int): Number of recent games to fetch
        
    Returns:
        list: List of recent game dictionaries with processed player data
    """
    logger.info(f"Getting {limit} recent games")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT start_time, player_data, game_id
            FROM games
            ORDER BY datetime(start_time) DESC
            LIMIT ?
            """, (limit,))
            
            games_raw = cursor.fetchall()
            
            recent_games = []
            for game in games_raw:
                try:
                    import urllib.parse  # Import here to avoid circular imports
                    
                    player_data = json.loads(game['player_data'])
                    player1 = player_data[0] if len(player_data) > 0 else {
                        "player_name": "Unknown", "character_name": "Unknown", "player_tag": "Unknown"
                    }
                    player2 = player_data[1] if len(player_data) > 1 else {
                        "player_name": "Unknown", "character_name": "Unknown", "player_tag": "Unknown"
                    }
                    
                    recent_games.append({
                        'time': game['start_time'],
                        'game_id': game['game_id'],
                        'player1': player1.get('player_name', 'Unknown'),
                        'player1_tag': player1.get('player_tag', 'Unknown'),
                        'player1_tag_encoded': urllib.parse.quote(player1.get('player_tag', 'Unknown')),
                        'character1': player1.get('character_name', 'Unknown'),
                        'player2': player2.get('player_name', 'Unknown'),
                        'player2_tag': player2.get('player_tag', 'Unknown'),
                        'player2_tag_encoded': urllib.parse.quote(player2.get('player_tag', 'Unknown')),
                        'character2': player2.get('character_name', 'Unknown'),
                        'result': f"{player1.get('result', 'Unknown')} - {player2.get('result', 'Unknown')}"
                    })
                except Exception as e:
                    logger.error(f"Error processing recent game: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(recent_games)} recent games")
            return recent_games
            
    except Exception as e:
        logger.error(f"Error getting recent games: {str(e)}")
        return []


def get_top_players(limit=6):
    """
    Get top players data for overview pages.
    
    Args:
        limit (int): Number of top players to fetch
        
    Returns:
        list: List of top player dictionaries
    """
    logger.info(f"Getting top {limit} players")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
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
                LIMIT ?
            )
            SELECT * FROM player_stats
            """, (limit,))
            
            players_raw = cursor.fetchall()
            
            import urllib.parse  # Import here to avoid circular imports
            
            top_players = []
            for player in players_raw:
                win_rate = player['wins'] / player['games'] if player['games'] > 0 else 0
                top_players.append({
                    'code': player['tag'],
                    'code_encoded': urllib.parse.quote(player['tag']),
                    'name': player['name'],
                    'games': player['games'],
                    'wins': player['wins'],
                    'win_rate': win_rate
                })
            
            logger.info(f"Retrieved {len(top_players)} top players")
            return top_players
            
    except Exception as e:
        logger.error(f"Error getting top players: {str(e)}")
        return []


def get_all_players():
    """
    Get all players data for the players index page.
    
    Returns:
        list: List of all player dictionaries with stats
    """
    logger.info("Getting all players data")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
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
            
            players_raw = cursor.fetchall()
            
            import urllib.parse  # Import here to avoid circular imports
            
            players_list = []
            for row in players_raw:
                players_list.append({
                    'tag': row['tag'],
                    'encoded_tag': urllib.parse.quote(row['tag']),
                    'name': row['name'],
                    'characters': row['characters'],
                    'character_list': row['characters'].split(',') if row['characters'] else [],
                    'total_games': row['total_count']
                })
            
            logger.info(f"Retrieved {len(players_list)} players")
            return players_list
            
    except Exception as e:
        logger.error(f"Error getting all players: {str(e)}")
        return []


# =============================================================================
# API Key Management Functions
# =============================================================================

def create_api_key_for_client(client_id):
    """
    Create a new API key for a client or update an existing one.
    
    Args:
        client_id (str): The client's unique identifier
        
    Returns:
        dict: Dictionary containing the API key and expiration date
    """
    import secrets
    from datetime import datetime, timedelta
    
    api_key = secrets.token_urlsafe(32)
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=config.TOKEN_EXPIRY_DAYS)).isoformat()
    
    try:
        with db_manager.get_connection() as conn:
            c = conn.cursor()
            
            # Check if key already exists for this client
            c.execute(f"SELECT api_key FROM {config.API_KEYS_TABLE} WHERE client_id = ?", (client_id,))
            existing = c.fetchone()
            
            if existing:
                # Update existing key
                c.execute(f'''
                UPDATE {config.API_KEYS_TABLE}
                SET api_key = ?, created_at = ?, expires_at = ?
                WHERE client_id = ?
                ''', (api_key, created_at, expires_at, client_id))
            else:
                # Create new key
                c.execute(f'''
                INSERT INTO {config.API_KEYS_TABLE} (client_id, api_key, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                ''', (client_id, api_key, created_at, expires_at))
            
            conn.commit()
            
            return {
                "api_key": api_key,
                "expires_at": expires_at
            }
            
    except Exception as e:
        logger.error(f"Error creating API key for client {client_id}: {str(e)}")
        raise


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
    
    try:
        result = db_manager.execute_query(
            f'''
            SELECT client_id, expires_at 
            FROM {config.API_KEYS_TABLE} 
            WHERE api_key = ?
            ''',
            (api_key,),
            fetch_one=True
        )
        
        if not result:
            return None
            
        client_id, expires_at = result
        
        # Check if key has expired
        from datetime import datetime
        if expires_at and datetime.now() > datetime.fromisoformat(expires_at):
            return None
            
        return client_id
        
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None


# =============================================================================
# Client Management Functions
# =============================================================================

def register_or_update_client(client_data):
    """
    Register a new client or update an existing one.
    
    Args:
        client_data (dict): Client registration data
        
    Returns:
        dict: Registration result with API key
    """
    client_id = client_data.get('client_id')
    if not client_id:
        raise ValueError("Missing client_id in request")
    
    try:
        from datetime import datetime
        
        with db_manager.get_connection() as conn:
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
                logger.info(f"Updated existing client: {client_id}")
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
                logger.info(f"Registered new client: {client_id}")
            
            conn.commit()
            
            # Generate API key for the client
            api_key_data = create_api_key_for_client(client_id)
            
            return {
                "status": "success", 
                "message": "Client registered successfully",
                "api_key": api_key_data['api_key'],
                "expires_at": api_key_data['expires_at']
            }
        
    except Exception as e:
        logger.error(f"Error registering client {client_id}: {str(e)}")
        raise


def update_client_last_active(client_id):
    """
    Update the last active time for a client.
    
    Args:
        client_id (str): The client ID to update
    """
    try:
        from datetime import datetime
        
        db_manager.execute_query(
            "UPDATE clients SET last_active = ? WHERE client_id = ?",
            (datetime.now().isoformat(), client_id),
            fetch_all=False
        )
        
    except Exception as e:
        logger.error(f"Error updating last active for client {client_id}: {str(e)}")


# =============================================================================
# Game Upload Functions
# =============================================================================

def upload_games_for_client(client_id, games_data):
    """
    Process and upload games for a specific client.
    
    Args:
        client_id (str): The client ID uploading the games
        games_data (list): List of game data dictionaries
        
    Returns:
        dict: Upload results with counts of new games, duplicates, and errors
    """
    if not games_data:
        return {
            "status": "success",
            "message": "No games to process",
            "new_games": 0,
            "duplicates": 0,
            "errors": 0
        }
    
    try:
        import json
        from datetime import datetime
        
        with db_manager.get_connection() as conn:
            c = conn.cursor()
            
            # Update client last active time
            update_client_last_active(client_id)
            
            # Process each game
            new_games = 0
            duplicates = 0
            errors = 0
            
            for game in games_data:
                try:
                    # Validate game data structure
                    if 'metadata' not in game or 'player_data' not in game:
                        errors += 1
                        continue

                    game_id = game.get('id')
                    if not game_id:
                        errors += 1
                        continue
                    
                    # Check if this game already exists
                    c.execute("SELECT game_id FROM games WHERE game_id = ?", (game_id,))
                    existing = c.fetchone()

                    if not existing:
                        # Get game_type, if present, otherwise use "unknown"
                        game_type = game.get("type", "unknown")
                        
                        c.execute('''
                        INSERT INTO games (
                            game_id, client_id, start_time, 
                            last_frame, stage_id, player_data, upload_date, game_type
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            game_id,
                            client_id,
                            game['metadata']['start_time'],
                            game['metadata']['last_frame'],
                            game['metadata']['stage_id'],
                            json.dumps(game['player_data']),
                            datetime.now().isoformat(),
                            game_type
                        ))
                        new_games += 1
                        logger.debug(f"Inserted new game with ID: {game_id}")
                    else:
                        duplicates += 1
                        logger.debug(f"Found duplicate game with ID: {game_id}")
                        
                except Exception as e:
                    logger.error(f"Error processing individual game: {str(e)}")
                    errors += 1
            
            conn.commit()
            
            logger.info(f"Upload from {client_id}: {new_games} new, {duplicates} duplicates, {errors} errors")
            
            return {
                "status": "success", 
                "new_games": new_games,
                "duplicates": duplicates,
                "errors": errors
            }
        
    except Exception as e:
        logger.error(f"Error processing games upload for client {client_id}: {str(e)}")
        raise


def get_database_stats():
    """Get comprehensive database statistics."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) as count FROM clients")
            client_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM games")
            game_count = cursor.fetchone()['count']
            
            cursor.execute(f"SELECT COUNT(*) as count FROM {config.API_KEYS_TABLE}")
            api_key_count = cursor.fetchone()['count']
            
            # Get latest upload
            cursor.execute("SELECT upload_date FROM games ORDER BY upload_date DESC LIMIT 1")
            latest_upload = cursor.fetchone()
            last_upload = latest_upload['upload_date'] if latest_upload else None
            
            # Count unique players
            cursor.execute("""
            WITH player_tags AS (
                SELECT DISTINCT json_extract(p.value, '$.player_tag') as tag
                FROM games, json_each(games.player_data) as p
                WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
                  AND json_extract(p.value, '$.player_tag') != ''
            )
            SELECT COUNT(*) as count FROM player_tags
            """)
            unique_players = cursor.fetchone()['count']
            
            return {
                'total_clients': client_count,
                'total_games': game_count,
                'total_api_keys': api_key_count,
                'unique_players': unique_players,
                'last_upload': last_upload
            }
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {
            'total_clients': 0,
            'total_games': 0,
            'total_api_keys': 0,
            'unique_players': 0,
            'last_upload': None,
            'error': str(e)
        }