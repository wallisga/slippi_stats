"""
SQL loading utilities for the database layer.
Phase 1: Basic query loading functionality.
"""
from .queries import query_registry

def get_sql(query_name: str) -> str:
    """Get SQL query by name."""
    return query_registry.get_query(query_name)

def get_query_info(query_name: str) -> dict:
    """Get query metadata."""
    return query_registry.get_metadata(query_name)

def list_available_queries() -> list:
    """List all available SQL queries."""
    return query_registry.list_queries()

# Convenience function for stats queries
def get_stats_sql(stat_type: str) -> str:
    """Get statistics SQL by type."""
    return get_sql(f'stats.{stat_type}')