"""
Database management for Slippi Server.

This module handles ONLY raw database operations - no business logic or data processing.
All data transformation and business rules are handled in the service layers.

SQL queries are now managed through external .sql files for better maintainability.
The SQL manager automatically discovers any new .sql files added to the sql/ directory.
"""

import sqlite3
import json
import logging
import secrets
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from backend.config import get_config
from backend.sql_manager import sql_manager

# Get configuration
config = get_config()
logger = logging.getLogger('SlippiServer')


class DatabaseManager:
    """Centralized database management class with dynamic external SQL file support."""
    
    def __init__(self, db_path=None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or config.get_database_path()
        self._initialized = False
        # Ensure SQL queries are loaded
        sql_manager.load_queries()
    
    def init_db(self):
        """
        Initialize the SQLite database with the required tables using external SQL files.
        """
        if self._initialized:
            logger.debug("Database already initialized")
            return
        
        logger.info(f"Initializing database at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Create tables using external SQL
            if sql_manager.has_query('schema', 'init_tables'):
                tables_sql = sql_manager.format_query('schema', 'init_tables', 
                                                    api_keys_table=config.API_KEYS_TABLE)
                
                # Split and execute each CREATE TABLE statement
                statements = [stmt.strip() for stmt in tables_sql.split(';') if stmt.strip()]
                for statement in statements:
                    c.execute(statement)
                    
            # Create indexes using external SQL
            if sql_manager.has_query('schema', 'init_indexes'):
                indexes_sql = sql_manager.format_query('schema', 'init_indexes',
                                                     api_keys_table=config.API_KEYS_TABLE)
                
                # Split and execute each CREATE INDEX statement
                index_statements = [stmt.strip() for stmt in indexes_sql.split(';') if stmt.strip()]
                for statement in index_statements:
                    try:
                        c.execute(statement)
                        logger.debug(f"Created index: {statement[:50]}...")
                    except Exception as e:
                        logger.warning(f"Could not create index: {str(e)}")
            
            conn.commit()
            self._initialized = True
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
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
            
            # Get base query from SQL file
            query = sql_manager.format_query('games', 'select_all',
                                            order_by=order_by,
                                            limit_clause=f'LIMIT {limit}' if limit else '')
            
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
    try:
        query = sql_manager.get_query('games', 'select_recent')
        return db_manager.execute_query(query, (limit,))
    except Exception as e:
        logger.error(f"Error getting recent games: {str(e)}")
        return []


def get_games_by_date_range(start_date, end_date):
    """Get games within a specific date range."""
    try:
        query = sql_manager.get_query('games', 'select_by_date_range')
        return db_manager.execute_query(query, (start_date, end_date))
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
        query = sql_manager.get_query('games', 'insert_game')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
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
        query = sql_manager.get_query('games', 'count_all')
        result = db_manager.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting games count: {str(e)}")
        return 0


def get_games_by_id(game_id):
    """Get a specific game by ID."""
    try:
        query = sql_manager.get_query('games', 'select_by_id')
        return db_manager.execute_query(query, (game_id,), fetch_one=True)
    except Exception as e:
        logger.error(f"Error getting game by ID {game_id}: {str(e)}")
        return None


def check_game_exists(game_id):
    """Check if a game exists in the database."""
    try:
        query = sql_manager.get_query('games', 'check_exists')
        result = db_manager.execute_query(query, (game_id,), fetch_one=True)
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
        query = sql_manager.get_query('clients', 'select_all')
        return db_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting all clients: {str(e)}")
        return []


def get_clients_by_id(client_id):
    """Get a specific client by ID."""
    try:
        query = sql_manager.get_query('clients', 'select_by_id')
        return db_manager.execute_query(query, (client_id,), fetch_one=True)
    except Exception as e:
        logger.error(f"Error getting client by ID {client_id}: {str(e)}")
        return None


def create_client_record(client_data):
    """Insert a new client record."""
    try:
        query = sql_manager.get_query('clients', 'insert_client')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
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
        query = sql_manager.get_query('clients', 'update_info')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (hostname, platform, version, datetime.now().isoformat(), client_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error updating client info for {client_id}: {str(e)}")
        raise


def update_clients_last_active(client_id):
    """Update the last active timestamp for a client."""
    try:
        query = sql_manager.get_query('clients', 'update_last_active')
        db_manager.execute_query(query, (datetime.now().isoformat(), client_id), fetch_all=False)
    except Exception as e:
        logger.error(f"Error updating last active for client {client_id}: {str(e)}")


def get_clients_count():
    """Get total count of clients."""
    try:
        query = sql_manager.get_query('clients', 'count_all')
        result = db_manager.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting clients count: {str(e)}")
        return 0


def check_client_exists(client_id):
    """Check if a client exists in the database."""
    try:
        query = sql_manager.get_query('clients', 'check_exists')
        result = db_manager.execute_query(query, (client_id,), fetch_one=True)
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
        query = sql_manager.format_query('api_keys', 'select_all', api_keys_table=config.API_KEYS_TABLE)
        return db_manager.execute_query(query)
    except Exception as e:
        logger.error(f"Error getting all API keys: {str(e)}")
        return []


def get_api_keys_by_client(client_id):
    """Get API key for a specific client."""
    try:
        query = sql_manager.format_query('api_keys', 'select_by_client', api_keys_table=config.API_KEYS_TABLE)
        return db_manager.execute_query(query, (client_id,), fetch_one=True)
    except Exception as e:
        logger.error(f"Error getting API key for client {client_id}: {str(e)}")
        return None


def get_api_keys_by_key(api_key):
    """Get API key record by the key value."""
    try:
        query = sql_manager.format_query('api_keys', 'select_by_key', api_keys_table=config.API_KEYS_TABLE)
        return db_manager.execute_query(query, (api_key,), fetch_one=True)
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
        query = sql_manager.format_query('api_keys', 'insert_key', api_keys_table=config.API_KEYS_TABLE)
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (client_id, api_key, created_at, expires_at))
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
        query = sql_manager.format_query('api_keys', 'update_key', api_keys_table=config.API_KEYS_TABLE)
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (api_key, created_at, expires_at, client_id))
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
        query = sql_manager.format_query('api_keys', 'delete_expired', api_keys_table=config.API_KEYS_TABLE)
        current_time = datetime.now().isoformat()
        return db_manager.execute_query(query, (current_time,), fetch_all=False)
    except Exception as e:
        logger.error(f"Error deleting expired API keys: {str(e)}")
        return 0


def get_api_keys_count():
    """Get total count of API keys."""
    try:
        query = sql_manager.format_query('api_keys', 'count_all', api_keys_table=config.API_KEYS_TABLE)
        result = db_manager.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting API keys count: {str(e)}")
        return 0


# =============================================================================
# Files Table Operations (Raw Data Access Only)
# =============================================================================

def get_files_all(limit=None, order_by='upload_date DESC'):
    """
    Get all files from the database with optional limit and ordering.
    Returns raw file records - no processing.
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = sql_manager.format_query('files', 'select_all',
                                            order_by=order_by,
                                            limit_clause=f'LIMIT {limit}' if limit else '')
            
            cursor.execute(query)
            return cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Error getting all files: {str(e)}")
        return []


def get_files_by_client(client_id, limit=None):
    """Get files uploaded by a specific client."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = sql_manager.format_query('files', 'select_by_client',
                                            limit_clause=f'LIMIT {limit}' if limit else '')
            
            cursor.execute(query, (client_id,))
            return cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Error getting files for client {client_id}: {str(e)}")
        return []


def get_file_by_hash(file_hash):
    """Get a file record by its hash."""
    try:
        query = sql_manager.get_query('files', 'select_by_hash')
        return db_manager.execute_query(query, (file_hash,), fetch_one=True)
    except Exception as e:
        logger.error(f"Error getting file by hash {file_hash}: {str(e)}")
        return None


def get_file_by_id(file_id):
    """Get a file record by its ID."""
    try:
        query = sql_manager.get_query('files', 'select_by_id')
        return db_manager.execute_query(query, (file_id,), fetch_one=True)
    except Exception as e:
        logger.error(f"Error getting file by ID {file_id}: {str(e)}")
        return None


def create_file_record(file_data):
    """
    Insert a new file record into the files table.
    
    Args:
        file_data (dict): File data with keys: file_hash, client_id, original_filename,
                         file_path, file_size, upload_date, metadata
    
    Returns:
        str: Generated file_id
    """
    try:
        file_id = str(uuid.uuid4())
        query = sql_manager.get_query('files', 'insert_file')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                file_id,
                file_data['file_hash'],
                file_data['client_id'],
                file_data['original_filename'],
                file_data['file_path'],
                file_data['file_size'],
                file_data['upload_date'],
                file_data.get('metadata', '{}')
            ))
            conn.commit()
            return file_id
            
    except Exception as e:
        logger.error(f"Error creating file record: {str(e)}")
        raise


def check_file_exists_by_hash(file_hash):
    """Check if a file with the given hash exists."""
    try:
        query = sql_manager.get_query('files', 'check_exists_by_hash')
        result = db_manager.execute_query(query, (file_hash,), fetch_one=True)
        return result is not None
    except Exception as e:
        logger.error(f"Error checking if file exists {file_hash}: {str(e)}")
        return False


def get_files_count():
    """Get total count of files in database."""
    try:
        query = sql_manager.get_query('files', 'count_all')
        result = db_manager.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting files count: {str(e)}")
        return 0


def delete_file_record(file_id):
    """Delete a file record (does not delete the actual file)."""
    try:
        query = sql_manager.get_query('files', 'delete_by_id')
        return db_manager.execute_query(query, (file_id,), fetch_all=False)
    except Exception as e:
        logger.error(f"Error deleting file record {file_id}: {str(e)}")
        raise


def update_file_metadata(file_id, metadata):
    """Update metadata for a file record."""
    try:
        query = sql_manager.get_query('files', 'update_metadata')
        metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata
        return db_manager.execute_query(query, (metadata_json, file_id), fetch_all=False)
    except Exception as e:
        logger.error(f"Error updating file metadata for {file_id}: {str(e)}")
        raise


# =============================================================================
# Statistics Functions
# =============================================================================

def get_files_stats():
    """Get file storage statistics."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total files and total size
            if sql_manager.has_query('stats', 'file_stats_totals'):
                query = sql_manager.get_query('stats', 'file_stats_totals')
            else:
                query = "SELECT COUNT(*) as count, SUM(file_size) as total_size FROM files"
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            total_files = result['count'] if result else 0
            total_size = result['total_size'] if result and result['total_size'] else 0
            
            # Get files by client
            if sql_manager.has_query('stats', 'file_stats_by_client'):
                query = sql_manager.get_query('stats', 'file_stats_by_client')
            else:
                query = """
                    SELECT client_id, COUNT(*) as file_count, SUM(file_size) as client_size
                    FROM files 
                    GROUP BY client_id 
                    ORDER BY file_count DESC
                """
            
            cursor.execute(query)
            by_client = cursor.fetchall()
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files_by_client': [dict(row) for row in by_client]
            }
            
    except Exception as e:
        logger.error(f"Error getting file stats: {str(e)}")
        return {
            'total_files': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0,
            'files_by_client': []
        }


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
# Database Statistics
# =============================================================================

def get_database_stats():
    """Get basic database statistics - simple counts only."""
    try:
        # Get simple counts
        total_clients = get_clients_count()
        total_games = get_games_count()
        total_api_keys = get_api_keys_count()
        
        # Get latest upload date
        if sql_manager.has_query('stats', 'latest_upload'):
            query = sql_manager.get_query('stats', 'latest_upload')
        else:
            query = "SELECT upload_date FROM games ORDER BY upload_date DESC LIMIT 1"
        
        latest_upload_result = db_manager.execute_query(query, fetch_one=True)
        last_upload = latest_upload_result['upload_date'] if latest_upload_result else None
        
        # Get unique players count (minimal processing)
        if sql_manager.has_query('stats', 'unique_players'):
            query = sql_manager.get_query('stats', 'unique_players')
        else:
            query = """
                WITH player_tags AS (
                    SELECT DISTINCT json_extract(p.value, '$.player_tag') as tag
                    FROM games, json_each(games.player_data) as p
                    WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
                      AND json_extract(p.value, '$.player_tag') != ''
                )
                SELECT COUNT(*) as count FROM player_tags
            """
        
        unique_players_result = db_manager.execute_query(query, fetch_one=True)
        unique_players = unique_players_result['count'] if unique_players_result else 0
        
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


def get_enhanced_database_stats():
    """Get enhanced database statistics including file information."""
    try:
        # Get existing stats
        basic_stats = get_database_stats()
        
        # Get file stats
        file_stats = get_files_stats()
        
        # Combine them
        enhanced_stats = basic_stats.copy()
        enhanced_stats.update({
            'total_files': file_stats['total_files'],
            'total_file_size_bytes': file_stats['total_size_bytes'],
            'total_file_size_mb': file_stats['total_size_mb'],
            'files_by_client': file_stats['files_by_client']
        })
        
        return enhanced_stats
        
    except Exception as e:
        logger.error(f"Error getting enhanced database stats: {str(e)}")
        # Return basic stats if file stats fail
        basic_stats = get_database_stats()
        basic_stats.update({
            'total_files': 0,
            'total_file_size_bytes': 0, 
            'total_file_size_mb': 0,
            'files_by_client': [],
            'file_stats_error': str(e)
        })
        return basic_stats


# =============================================================================
# Utility Functions for SQL Management
# =============================================================================

def reload_sql_queries():
    """
    Reload all SQL queries from files.
    Useful during development when SQL files are being modified.
    """
    sql_manager.reload_queries()
    logger.info("SQL queries reloaded from files")


def list_available_sql_queries():
    """
    List all available SQL queries by category.
    Useful for debugging and development.
    """
    return sql_manager.list_available_queries()


def add_custom_query_execution(category, query_name, params=None, fetch_one=False):
    """
    Execute any available SQL query by category and name.
    This provides a generic interface for executing any SQL file that gets added.
    
    Args:
        category (str): Query category (directory name)
        query_name (str): Query name (filename without .sql)
        params (tuple): Query parameters for ? placeholders
        fetch_one (bool): Whether to fetch only one result
        
    Returns:
        Query result(s)
    """
    try:
        query = sql_manager.get_query(category, query_name)
        return db_manager.execute_query(query, params, fetch_one=fetch_one)
    except Exception as e:
        logger.error(f"Error executing custom query {category}/{query_name}: {str(e)}")
        raise


def execute_formatted_query(category, query_name, params=None, fetch_one=False, **template_vars):
    """
    Execute a templated SQL query with both template variable substitution and parameter binding.
    
    Args:
        category (str): Query category
        query_name (str): Query name
        params (tuple): Query parameters for ? placeholders
        fetch_one (bool): Whether to fetch only one result
        **template_vars: Template variables for {} placeholders
        
    Returns:
        Query result(s)
    """
    try:
        formatted_query = sql_manager.format_query(category, query_name, **template_vars)
        return db_manager.execute_query(formatted_query, params, fetch_one=fetch_one)
    except Exception as e:
        logger.error(f"Error executing formatted query {category}/{query_name}: {str(e)}")
        raise