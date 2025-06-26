"""
Dynamic SQL Query Manager for Slippi Server Database Operations

This module automatically discovers and loads SQL queries from external files.
Just add a .sql file to the appropriate directory and it becomes available.
No need to modify Python code when adding new queries.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger('SlippiServer')

class SQLQueryManager:
    """
    Dynamically manages loading and caching of SQL queries from external files.
    
    SQL files are automatically discovered in the sql/ directory structure:
    - sql/schema/ - Table creation and indexing
    - sql/games/ - Games table operations  
    - sql/clients/ - Clients table operations
    - sql/api_keys/ - API keys table operations
    - sql/files/ - Files table operations
    - sql/stats/ - Statistics and reporting queries
    
    Any .sql file added to these directories becomes automatically available.
    """
    
    def __init__(self, sql_directory=None):
        """Initialize the SQL query manager."""
        if sql_directory is None:
            # Default to sql/ directory relative to this file
            self.sql_dir = Path(__file__).parent / "sql"
        else:
            self.sql_dir = Path(sql_directory)
        
        self._queries = {}
        self._loaded = False
        
    def load_queries(self):
        """Dynamically load all SQL queries from files into memory."""
        if self._loaded:
            return
            
        try:
            logger.info(f"Loading SQL queries from {self.sql_dir}")
            
            if not self.sql_dir.exists():
                logger.warning(f"SQL directory does not exist: {self.sql_dir}")
                return
            
            # Dynamically discover all categories (subdirectories)
            for category_dir in self.sql_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                    
                category_name = category_dir.name
                self._queries[category_name] = {}
                
                logger.debug(f"Loading queries from category: {category_name}")
                
                # Dynamically discover all SQL files in this category
                for sql_file in category_dir.glob("*.sql"):
                    query_name = sql_file.stem  # filename without .sql extension
                    
                    try:
                        with open(sql_file, 'r', encoding='utf-8') as f:
                            query_content = f.read().strip()
                            
                        self._queries[category_name][query_name] = query_content
                        logger.debug(f"Loaded {category_name}/{query_name}")
                        
                    except Exception as e:
                        logger.error(f"Error loading SQL file {sql_file}: {str(e)}")
                        continue
            
            self._loaded = True
            total_queries = sum(len(queries) for queries in self._queries.values())
            logger.info(f"Successfully loaded {total_queries} SQL queries from {len(self._queries)} categories")
            
        except Exception as e:
            logger.error(f"Error loading SQL queries: {str(e)}")
            raise
    
    def get_query(self, category, query_name):
        """
        Get a SQL query by category and name.
        
        Args:
            category (str): Query category (directory name under sql/)
            query_name (str): Query name (filename without .sql extension)
            
        Returns:
            str: SQL query string
            
        Raises:
            KeyError: If category or query not found
        """
        if not self._loaded:
            self.load_queries()
            
        try:
            return self._queries[category][query_name]
        except KeyError:
            available = self.list_available_queries()
            raise KeyError(f"SQL query not found: {category}/{query_name}. Available: {available}")
    
    def get_category_queries(self, category):
        """
        Get all queries for a specific category.
        
        Args:
            category (str): Query category name
            
        Returns:
            dict: Dictionary of query_name -> query_string
        """
        if not self._loaded:
            self.load_queries()
            
        return self._queries.get(category, {}).copy()
    
    def has_query(self, category, query_name):
        """
        Check if a specific query exists.
        
        Args:
            category (str): Query category
            query_name (str): Query name
            
        Returns:
            bool: True if query exists, False otherwise
        """
        if not self._loaded:
            self.load_queries()
            
        return category in self._queries and query_name in self._queries[category]
    
    def get_categories(self):
        """
        Get list of all available categories.
        
        Returns:
            list: List of category names
        """
        if not self._loaded:
            self.load_queries()
            
        return list(self._queries.keys())
    
    def reload_queries(self):
        """Force reload all queries from files."""
        self._loaded = False
        self._queries.clear()
        self.load_queries()
    
    def list_available_queries(self):
        """
        List all available queries by category.
        
        Returns:
            dict: Category -> list of query names
        """
        if not self._loaded:
            self.load_queries()
        
        result = {}
        for category, queries in self._queries.items():
            result[category] = list(queries.keys())
        return result
    
    def format_query(self, category, query_name, **kwargs):
        """
        Get a query and format it with the provided variables.
        
        Args:
            category (str): Query category
            query_name (str): Query name
            **kwargs: Variables to substitute in the query
            
        Returns:
            str: Formatted SQL query
        """
        query = self.get_query(category, query_name)
        
        # Replace template variables
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            query = query.replace(placeholder, str(value))
        
        return query
    
    def execute_template_query(self, category, query_name, connection, params=None, **template_vars):
        """
        Execute a templated query with both template variable substitution and parameter binding.
        
        Args:
            category (str): Query category
            query_name (str): Query name  
            connection: Database connection
            params: Query parameters for ? placeholders
            **template_vars: Template variables for {} placeholders
            
        Returns:
            Cursor result
        """
        formatted_query = self.format_query(category, query_name, **template_vars)
        
        cursor = connection.cursor()
        if params:
            return cursor.execute(formatted_query, params)
        else:
            return cursor.execute(formatted_query)
    
    def add_sql_file_discovery_rules(self):
        """
        Print information about how to add new SQL files.
        This is for documentation/debugging purposes.
        """
        print("SQL File Discovery Rules:")
        print(f"- Base directory: {self.sql_dir}")
        print("- Categories are subdirectories under the base directory")
        print("- Query files are .sql files within category directories")
        print("- Query names are filenames without the .sql extension")
        print("\nTo add a new query:")
        print("1. Create/navigate to the appropriate category directory")
        print("2. Add your .sql file with a descriptive name")
        print("3. The query becomes available as get_query('category', 'filename')")
        print("\nExample:")
        print("- File: sql/games/select_by_player.sql")
        print("- Access: get_query('games', 'select_by_player')")


# Global instance
sql_manager = SQLQueryManager()


def get_sql_query(category, query_name):
    """
    Convenience function to get a SQL query.
    
    Args:
        category (str): Query category
        query_name (str): Query name
        
    Returns:
        str: SQL query string
    """
    return sql_manager.get_query(category, query_name)


def format_sql_query(category, query_name, **kwargs):
    """
    Convenience function to get and format a SQL query.
    
    Args:
        category (str): Query category
        query_name (str): Query name
        **kwargs: Template variables
        
    Returns:
        str: Formatted SQL query string
    """
    return sql_manager.format_query(category, query_name, **kwargs)


def list_sql_queries():
    """
    Convenience function to list all available SQL queries.
    
    Returns:
        dict: Category -> list of query names
    """
    return sql_manager.list_available_queries()


def reload_sql_queries():
    """
    Convenience function to reload all SQL queries from files.
    Useful during development when SQL files are being modified.
    """
    sql_manager.reload_queries()