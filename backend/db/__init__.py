"""
Simplified Database Layer for Slippi Server - UPDATED

Usage in service layers:
    from backend.db import connection, sql_manager, execute_query
    
    # Direct usage
    with connection.get_connection() as conn:
        query = sql_manager.get_query('games', 'select_by_player')
        cursor = conn.cursor()
        cursor.execute(query, (player_code,))
        results = cursor.fetchall()
    
    # Or use helper (returns clean dicts)
    results = execute_query('games', 'select_by_player', (player_code,))

FIXED: Now converts sqlite3.Row objects to dictionaries automatically
"""

import logging
from .connection import connection
from .manager import sql_manager

# Get logger
logger = logging.getLogger('SlippiServer')

# Initialize SQL queries on import
sql_manager.load_queries()


def row_to_dict(row):
    """Convert sqlite3.Row to dict for easier handling."""
    if row is None:
        return None
    if hasattr(row, 'keys'):  # sqlite3.Row has keys() method
        return {key: row[key] for key in row.keys()}
    return row  # Already a dict or other type


def rows_to_dicts(rows):
    """Convert list of sqlite3.Row objects to list of dicts."""
    if not rows:
        return []
    return [row_to_dict(row) for row in rows]


def execute_query(category, query_name, params=None, fetch_one=False):
    """
    Standard database query execution with consistent error handling.
    
    Args:
        category (str): SQL category (e.g., 'games')
        query_name (str): SQL file name (e.g., 'select_by_player')  
        params (tuple): Query parameters for ? placeholders
        fetch_one (bool): Return single result vs all results
    
    Returns:
        Clean dictionary or list of dictionaries (never sqlite3.Row objects)
        
    Raises:
        Exception: Database errors bubble up to service layer
    """
    with connection.get_connection() as conn:
        query = sql_manager.get_query(category, query_name)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            return row_to_dict(result)
        else:
            results = cursor.fetchall()
            return rows_to_dicts(results)


def execute_query_raw(category, query_name, params=None):
    """
    Execute query and return raw results (for special cases).
    
    Most code should use execute_query() instead for automatic dict conversion.
    """
    with connection.get_connection() as conn:
        query = sql_manager.get_query(category, query_name)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()


# Available exports
__all__ = [
    'connection',
    'sql_manager', 
    'execute_query',
    'execute_query_raw',
    'row_to_dict',
    'rows_to_dicts'
]