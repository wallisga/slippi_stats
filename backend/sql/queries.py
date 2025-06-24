"""
SQL Query Registry - Phase 1 Implementation
Starting with unique_players query as test case.
"""
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger('SlippiServer')

class QueryRegistry:
    """Central registry for SQL queries with metadata."""
    
    def __init__(self):
        self.sql_dir = Path(__file__).parent
        self._query_cache = {}
        # Start with just the unique_players query for Phase 1
        self._query_metadata = {
            'stats.unique_players': {
                'file': 'stats/unique_players.sql',
                'returns': 'single',
                'fields': ['count'],
                'params': [],
                'description': 'Count of unique players from JSON data'
            }
        }
    
    def get_query(self, query_name: str) -> str:
        """Get SQL query by name with caching."""
        if query_name not in self._query_cache:
            if query_name not in self._query_metadata:
                raise ValueError(f"Unknown query: {query_name}")
            
            file_path = self.sql_dir / self._query_metadata[query_name]['file']
            if not file_path.exists():
                raise FileNotFoundError(f"SQL file not found: {file_path}")
            
            with open(file_path, 'r') as f:
                sql_content = f.read().strip()
                # Remove comments and extra whitespace for cleaner execution
                lines = [line for line in sql_content.split('\n') 
                        if not line.strip().startswith('--')]
                self._query_cache[query_name] = '\n'.join(lines).strip()
                logger.debug(f"Loaded SQL query: {query_name}")
        
        return self._query_cache[query_name]
    
    def get_metadata(self, query_name: str) -> Dict[str, Any]:
        """Get query metadata."""
        if query_name not in self._query_metadata:
            raise ValueError(f"Unknown query: {query_name}")
        return self._query_metadata[query_name].copy()
    
    def list_queries(self) -> list:
        """List all available queries."""
        return list(self._query_metadata.keys())

# Global query registry instance
query_registry = QueryRegistry()