"""
Database management for Slippi Server.

This module handles ONLY raw database operations - no business logic or data processing.
All data transformation and business rules are handled in the service layers.
"""

import sqlite3
import json
import logging
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta
from backend.config import get_config
from backend.sql import get_sql

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
            "CREATE INDEX IF NOT EXISTS idx_games_start_time ON games (start_time)",
            "CREATE INDEX IF NOT EXISTS idx_games_client_id ON games (client_id)",
            "CREATE INDEX IF NOT EXISTS idx_games_upload_date ON games (upload_date)",
            f"CREATE INDEX IF NOT EXISTS idx_api_keys_key ON {config.API_KEYS_TABLE} (api_key)",
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
            conn.row_factory = sqlite3.Row
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
        """Legacy method for backward compatibility."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """Execute a database query with automatic connection management."""
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


# Global database manager instance
db_manager = DatabaseManager()


def init_db():
    """Initialize the database - backward compatibility function."""
    return db_manager.init_db()


def get_db_connection():
    """Get database connection - backward compatibility function."""
    return db_manager.get_db_connection()


# =============================================================================
# Games Table Operations (Raw Data Access Only)
# =============================================================================

def get_games_all(limit=None, order_by='start_time DESC'):
    """
    Get all games from the database with optional limit and ordering.
    Returns raw game records - no processing.
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT game_id, client_id, start_time, last_frame, stage_id, player_data, upload_date, game_type FROM games"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            return cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Error getting all games: {str(e)}")
        return []


def get_games_recent(limit=10):
    """
    Get recent games ordered by start_time.
    Returns raw game records - no processing.
    """
    return get_games_all(limit=limit, order_by='datetime(start_time) DESC')


def get_games_by_date_range(start_date, end_date):
    """Get games within a specific date range."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT game_id, client_id, start_time, last_frame, stage_id, player_data, upload_date, game_type
                FROM games 
                WHERE datetime(start_time) BETWEEN datetime(?) AND datetime(?)
                ORDER BY datetime(start_time) DESC
            """, (start_date, end_date))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting games by date range: {str(e)}")
        return []


def create_game_record(game_data):
    """
    Insert a new game record into the games table.
    
    Args:
        game_data (dict): Game data with keys: game_id, client_id, start_time, 
                         last_frame, stage_id, player_data, game_type
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO games (game_id, client_id, start_time, last_frame, stage_id, player_data, upload_date, game_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_data['game_id'],
                game_data['client_id'],
                game_data['start_time'],
                game_data['last_frame'],
                game_data['stage_id'],
                game_data['player_data'],  # Should be JSON string
                datetime.now().isoformat(),
                game_data.get('game_type', 'unknown')
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error creating game record: {str(e)}")
        raise


def get_games_count():
    """Get total count of games in database."""
    try:
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM games", fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting games count: {str(e)}")
        return 0


def get_games_by_id(game_id):
    """Get a specific game by ID."""
    try:
        return db_manager.execute_query(
            "SELECT * FROM games WHERE game_id = ?",
            (game_id,),
            fetch_one=True
        )
    except Exception as e:
        logger.error(f"Error getting game by ID {game_id}: {str(e)}")
        return None


def check_game_exists(game_id):
    """Check if a game exists in the database."""
    try:
        result = db_manager.execute_query(
            "SELECT 1 FROM games WHERE game_id = ?",
            (game_id,),
            fetch_one=True
        )
        return result is not None
    except Exception as e:
        logger.error(f"Error checking if game exists {game_id}: {str(e)}")
        return False


# =============================================================================
# Clients Table Operations (Raw Data Access Only)
# =============================================================================

def get_clients_all():
    """Get all clients from the database."""
    try:
        return db_manager.execute_query("SELECT * FROM clients ORDER BY last_active DESC")
    except Exception as e:
        logger.error(f"Error getting all clients: {str(e)}")
        return []


def get_clients_by_id(client_id):
    """Get a specific client by ID."""
    try:
        return db_manager.execute_query(
            "SELECT * FROM clients WHERE client_id = ?",
            (client_id,),
            fetch_one=True
        )
    except Exception as e:
        logger.error(f"Error getting client by ID {client_id}: {str(e)}")
        return None


def create_client_record(client_data):
    """Insert a new client record."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (client_id, hostname, platform, version, registration_date, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                client_data['client_id'],
                client_data.get('hostname', 'Unknown'),
                client_data.get('platform', 'Unknown'),
                client_data.get('version', 'Unknown'),
                client_data.get('registration_date', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error creating client record: {str(e)}")
        raise


def update_clients_info(client_id, hostname=None, platform=None, version=None):
    """Update client information."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients 
                SET hostname = ?, platform = ?, version = ?, last_active = ?
                WHERE client_id = ?
            ''', (hostname, platform, version, datetime.now().isoformat(), client_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error updating client info for {client_id}: {str(e)}")
        raise


def update_clients_last_active(client_id):
    """Update the last active timestamp for a client."""
    try:
        db_manager.execute_query(
            "UPDATE clients SET last_active = ? WHERE client_id = ?",
            (datetime.now().isoformat(), client_id),
            fetch_all=False
        )
    except Exception as e:
        logger.error(f"Error updating last active for client {client_id}: {str(e)}")


def get_clients_count():
    """Get total count of clients."""
    try:
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM clients", fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting clients count: {str(e)}")
        return 0


def check_client_exists(client_id):
    """Check if a client exists in the database."""
    try:
        result = db_manager.execute_query(
            "SELECT 1 FROM clients WHERE client_id = ?",
            (client_id,),
            fetch_one=True
        )
        return result is not None
    except Exception as e:
        logger.error(f"Error checking if client exists {client_id}: {str(e)}")
        return False


# =============================================================================
# API Keys Table Operations (Raw Data Access Only)
# =============================================================================

def get_api_keys_all():
    """Get all API keys from the database."""
    try:
        return db_manager.execute_query(f"SELECT * FROM {config.API_KEYS_TABLE}")
    except Exception as e:
        logger.error(f"Error getting all API keys: {str(e)}")
        return []


def get_api_keys_by_client(client_id):
    """Get API key for a specific client."""
    try:
        return db_manager.execute_query(
            f"SELECT * FROM {config.API_KEYS_TABLE} WHERE client_id = ?",
            (client_id,),
            fetch_one=True
        )
    except Exception as e:
        logger.error(f"Error getting API key for client {client_id}: {str(e)}")
        return None


def get_api_keys_by_key(api_key):
    """Get API key record by the key value."""
    try:
        return db_manager.execute_query(
            f"SELECT client_id, expires_at FROM {config.API_KEYS_TABLE} WHERE api_key = ?",
            (api_key,),
            fetch_one=True
        )
    except Exception as e:
        logger.error(f"Error getting API key record: {str(e)}")
        return None


def create_api_key_record(client_id, api_key=None, expires_days=None):
    """Create a new API key record."""
    if api_key is None:
        api_key = secrets.token_urlsafe(32)
    
    if expires_days is None:
        expires_days = config.TOKEN_EXPIRY_DAYS
    
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {config.API_KEYS_TABLE} (client_id, api_key, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (client_id, api_key, created_at, expires_at))
            conn.commit()
            return {
                'api_key': api_key,
                'expires_at': expires_at
            }
    except Exception as e:
        logger.error(f"Error creating API key for client {client_id}: {str(e)}")
        raise


def update_api_key_record(client_id, api_key=None, expires_days=None):
    """Update an existing API key record."""
    if api_key is None:
        api_key = secrets.token_urlsafe(32)
    
    if expires_days is None:
        expires_days = config.TOKEN_EXPIRY_DAYS
    
    created_at = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE {config.API_KEYS_TABLE}
                SET api_key = ?, created_at = ?, expires_at = ?
                WHERE client_id = ?
            ''', (api_key, created_at, expires_at, client_id))
            conn.commit()
            return {
                'api_key': api_key,
                'expires_at': expires_at
            }
    except Exception as e:
        logger.error(f"Error updating API key for client {client_id}: {str(e)}")
        raise


def delete_api_keys_expired():
    """Delete expired API keys."""
    try:
        current_time = datetime.now().isoformat()
        return db_manager.execute_query(
            f"DELETE FROM {config.API_KEYS_TABLE} WHERE expires_at < ?",
            (current_time,),
            fetch_all=False
        )
    except Exception as e:
        logger.error(f"Error deleting expired API keys: {str(e)}")
        return 0


def get_api_keys_count():
    """Get total count of API keys."""
    try:
        result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {config.API_KEYS_TABLE}", fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting API keys count: {str(e)}")
        return 0


# =============================================================================
# Simple Validation Functions (Minimal Business Logic)
# =============================================================================

def validate_api_key(api_key):
    """
    Validate an API key and return the associated client_id if valid.
    Minimal business logic - just checks existence and expiration.
    """
    if not api_key:
        return None
    
    try:
        result = get_api_keys_by_key(api_key)
        if not result:
            return None
            
        client_id, expires_at = result['client_id'], result['expires_at']
        
        # Check if key has expired
        if expires_at and datetime.now() > datetime.fromisoformat(expires_at):
            return None
            
        return client_id
        
    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return None


# =============================================================================
# Database Statistics (Simple Aggregation Only)
# =============================================================================

def get_database_stats():
    """Get basic database statistics - Phase 1: Using externalized SQL for unique_players."""
    try:
        # Get simple counts (keep existing approach for now)
        total_clients = get_clients_count()
        total_games = get_games_count()
        total_api_keys = get_api_keys_count()
        
        # Get latest upload date (keep existing approach)
        latest_upload_result = db_manager.execute_query(
            "SELECT upload_date FROM games ORDER BY upload_date DESC LIMIT 1",
            fetch_one=True
        )
        last_upload = latest_upload_result['upload_date'] if latest_upload_result else None
        
        # NEW: Use externalized SQL for unique players count
        unique_players_sql = get_sql('stats.unique_players')
        unique_players_result = db_manager.execute_query(
            unique_players_sql, 
            params=None,  # No parameters needed
            fetch_one=True
        )
        unique_players = unique_players_result['count'] if unique_players_result else 0
        
        logger.debug(f"Database stats - Games: {total_games}, Players: {unique_players}")
        
        return {
            'total_clients': total_clients,
            'total_games': total_games,
            'total_api_keys': total_api_keys,
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