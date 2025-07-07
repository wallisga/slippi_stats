"""
Simplified Database Layer for Slippi Server.

Usage in service layers:
    from backend.db import connection, sql_manager, execute_query
    
    # Direct usage
    with connection.get_connection() as conn:
        query = sql_manager.get_query('games', 'select_by_player')
        cursor = conn.cursor()
        cursor.execute(query, (player_code,))
        results = cursor.fetchall()
    
    # Or use helper
    results = execute_query('games', 'select_by_player', (player_code,))
"""

import logging
from .connection import connection
from .manager import sql_manager

# Get logger
logger = logging.getLogger('SlippiServer')

# Initialize SQL queries on import
sql_manager.load_queries()

def execute_query(category, query_name, params=None, fetch_one=False):
    """
    Standard database query execution with consistent error handling.
    
    Args:
        category (str): SQL category (e.g., 'games')
        query_name (str): SQL file name (e.g., 'select_by_player')  
        params (tuple): Query parameters for ? placeholders
        fetch_one (bool): Return single result vs all results
    
    Returns:
        Query results
        
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
            return cursor.fetchone()
        else:
            return cursor.fetchall()

# Available exports
__all__ = [
    'connection',
    'sql_manager', 
    'execute_query'
]