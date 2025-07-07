"""
SQL Query Manager for Database Operations.

Loads and manages SQL queries from external .sql files in the backend/db/sql/ directory.
Automatically discovers new SQL files - just add a .sql file and it becomes available.
"""

import logging
from pathlib import Path

logger = logging.getLogger('SlippiServer')


class SQLManager:
    """
    Manages loading and caching of SQL queries from external files.
    
    SQL files are organized in backend/db/sql/ directory:
    - sql/games/     - Game table operations
    - sql/clients/   - Client table operations  
    - sql/files/     - File table operations
    - sql/stats/     - Statistics queries
    - sql/schema/    - Table creation and indexes
    - sql/api_keys/  - API key operations
    
    Any .sql file added to these directories becomes automatically available.
    """
    
    def __init__(self, sql_directory=None):
        """
        Initialize SQL manager.
        
        Args:
            sql_directory (str, optional): Path to SQL directory. 
                                         Defaults to backend/db/sql/
        """
        if sql_directory is None:
            # Default to sql/ directory next to this file
            self.sql_dir = Path(__file__).parent / "sql"
        else:
            self.sql_dir = Path(sql_directory)
        
        self._queries = {}
        self._loaded = False
        logger.debug(f"SQL manager initialized for directory: {self.sql_dir}")
    
    def load_queries(self):
        """
        Load all SQL queries from files into memory.
        
        Discovers all .sql files in subdirectories and loads them.
        Query access: get_query(category, filename_without_extension)
        """
        if self._loaded:
            logger.debug("SQL queries already loaded")
            return
            
        logger.info(f"Loading SQL queries from {self.sql_dir}")
        
        if not self.sql_dir.exists():
            logger.warning(f"SQL directory does not exist: {self.sql_dir}")
            return
        
        total_loaded = 0
        
        # Discover all category directories
        for category_dir in self.sql_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            category_name = category_dir.name
            self._queries[category_name] = {}
            
            logger.debug(f"Loading SQL queries from category: {category_name}")
            
            # Discover all .sql files in this category
            for sql_file in category_dir.glob("*.sql"):
                query_name = sql_file.stem  # filename without .sql
                
                try:
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        query_content = f.read().strip()
                    
                    self._queries[category_name][query_name] = query_content
                    total_loaded += 1
                    logger.debug(f"Loaded {category_name}/{query_name}")
                    
                except Exception as e:
                    logger.error(f"Error loading SQL file {sql_file}: {e}")
                    continue
        
        self._loaded = True
        category_count = len(self._queries)
        logger.info(f"Successfully loaded {total_loaded} SQL queries from {category_count} categories")
    
    def get_query(self, category, query_name):
        """
        Get a SQL query by category and name.
        
        Args:
            category (str): Query category (directory name)
            query_name (str): Query name (filename without .sql)
            
        Returns:
            str: SQL query string
            
        Raises:
            KeyError: If category or query not found
            
        Example:
            query = sql.get_query('games', 'select_by_player')
        """
        if not self._loaded:
            self.load_queries()
        
        try:
            return self._queries[category][query_name]
        except KeyError:
            available = self.list_available_queries()
            raise KeyError(
                f"SQL query not found: {category}/{query_name}. "
                f"Available queries: {available}"
            )
    
    def has_query(self, category, query_name):
        """
        Check if a specific query exists.
        
        Args:
            category (str): Query category
            query_name (str): Query name
            
        Returns:
            bool: True if query exists
        """
        if not self._loaded:
            self.load_queries()
        
        return (category in self._queries and 
                query_name in self._queries[category])
    
    def get_categories(self):
        """
        Get list of all available categories.
        
        Returns:
            list: List of category names
        """
        if not self._loaded:
            self.load_queries()
        
        return list(self._queries.keys())
    
    def list_available_queries(self):
        """
        List all available queries by category.
        
        Returns:
            dict: Category -> list of query names
            
        Example:
            {
                'games': ['select_all', 'select_by_player', 'insert_game'],
                'clients': ['select_all', 'insert_client']
            }
        """
        if not self._loaded:
            self.load_queries()
        
        result = {}
        for category, queries in self._queries.items():
            result[category] = list(queries.keys())
        return result
    
    def reload_queries(self):
        """
        Force reload all queries from files.
        
        Useful during development when SQL files are being modified.
        """
        logger.info("Reloading SQL queries from files")
        self._loaded = False
        self._queries.clear()
        self.load_queries()
    
    def format_query(self, category, query_name, **template_vars):
        """
        Get a query and format it with template variables.
        
        Args:
            category (str): Query category
            query_name (str): Query name
            **template_vars: Variables to substitute in {variable} placeholders
            
        Returns:
            str: Formatted SQL query
            
        Example:
            # SQL file contains: SELECT * FROM {table_name} WHERE id = ?
            query = sql.format_query('schema', 'select_by_id', table_name='games')
            # Returns: SELECT * FROM games WHERE id = ?
        """
        query = self.get_query(category, query_name)
        
        # Replace template variables in {variable} format
        for key, value in template_vars.items():
            placeholder = '{' + key + '}'
            query = query.replace(placeholder, str(value))
        
        return query


# Global SQL manager instance
sql_manager = SQLManager()


# Convenience functions for backward compatibility
def get_sql_query(category, query_name):
    """Get a SQL query - convenience function."""
    return sql_manager.get_query(category, query_name)


def format_sql_query(category, query_name, **kwargs):
    """Format a SQL query with template variables - convenience function."""
    return sql_manager.format_query(category, query_name, **kwargs)


def reload_sql_queries():
    """Reload all SQL queries from files - convenience function."""
    sql_manager.reload_queries()


def list_sql_queries():
    """List all available SQL queries - convenience function."""
    return sql_manager.list_available_queries()