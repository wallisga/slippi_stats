"""
Database Connection Management for Slippi Server.

Simple, focused connection management with context manager support.
No business logic - just connection handling.
"""

import sqlite3
import logging
from contextlib import contextmanager
from backend.config import get_config

# Get configuration
config = get_config()
logger = logging.getLogger('SlippiServer')


class DatabaseConnection:
    """
    Simple database connection manager.
    
    Provides context manager for safe connection handling with proper cleanup.
    All connections use Row factory for dict-like access to results.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize connection manager.
        
        Args:
            db_path (str, optional): Database path. Defaults to config value.
        """
        self.db_path = db_path or config.get_database_path()
        logger.debug(f"Database connection manager initialized for: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Provides automatic connection cleanup and rollback on errors.
        Sets Row factory for dict-like access to query results.
        
        Yields:
            sqlite3.Connection: Database connection with Row factory
            
        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM games")
                results = cursor.fetchall()
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
            
        except Exception as e:
            # Rollback on any exception
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise  # Let calling code handle the exception
            
        finally:
            # Always close connection
            if conn:
                conn.close()
    
    def get_legacy_connection(self):
        """
        Get raw connection for backward compatibility.
        
        Returns:
            sqlite3.Connection: Raw connection with Row factory
            
        Note:
            Caller is responsible for closing the connection.
            Prefer using get_connection() context manager.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def test_connection(self):
        """
        Test database connectivity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global connection instance
connection = DatabaseConnection()