# Backend Architecture Documentation

This document provides detailed information about the Slippi Stats Server backend architecture, module design, and development guidelines.

## Architecture Overview

The backend follows a **service-oriented architecture** with clear separation of concerns and **external SQL file management**. Each module has specific responsibilities and follows strict import rules to maintain clean dependencies.

### Core Principle: "Services Process, Database Stores, Utils Help, SQL Separates"

- **Services**: Business logic and request processing (web_service.py, api_service.py)
- **Database**: Pure data access with external SQL files (database.py + sql/ directory)
- **Utils**: Shared helper functions and data processing (utils.py)
- **Config**: Centralized configuration management (config.py)
- **App**: Flask setup and HTTP routing (app.py)
- **SQL**: External .sql files organized by functionality (sql/ directory)

## Module Structure & Responsibilities

### Module Hierarchy
```
app.py (Flask routes & HTTP handling)        # Top level
    ↓ can import
web_service.py + api_service.py              # Business logic layers
    ↓ can import  
utils.py + database.py + config.py           # Foundation
    ↓ uses
sql/ directory (external SQL files)          # Data queries
```

### Import Rules (Strictly Enforced)
- ✅ **Services** can import: `backend.database`, `backend.utils`, `backend.config`
- ✅ **Utils** can import: `backend.config` only
- ✅ **Database** can import: `backend.config`, `backend.sql_manager` only
- ✅ **App** can import: all backend modules (with `backend.` prefix)
- ❌ **No circular imports** between services
- ❌ **Database cannot import** services or utils
- ❌ **Utils cannot import** database or services

## Module Documentation

### config.py - Configuration Management ✅ COMPLETE
**Purpose**: Centralized configuration and environment settings

**Contains:**
- Environment variable handling (`get_config()`)
- Application settings and constants
- Logging configuration (`init_logging()`)
- Database paths and connection settings
- Feature flags and limits

**Import Rules**: Cannot import any other app modules
**Status**: Stable, well-structured

**Key Functions:**
```python
get_config()                    # Main configuration object
init_logging()                  # Configure logging system
validate_config()               # Validate configuration values
get_database_path()             # Database file location
get_downloads_dir()             # Downloads directory path
```

### sql_manager.py - Dynamic SQL Query Management ✅ NEW
**Purpose**: Load and manage SQL queries from external .sql files

**Contains:**
- Dynamic discovery of SQL files in sql/ directory structure
- Template variable substitution for dynamic queries
- Query caching and reloading capabilities
- Category-based organization of SQL operations

**Import Rules**: Can import `backend.config` only
**Status**: New module for SQL file management

**Key Features:**
- **Automatic Discovery**: Add any .sql file to sql/category/ and it becomes available
- **Template Support**: Use `{variable}` placeholders for dynamic values
- **Category Organization**: Organize queries by functionality (games, clients, files, etc.)
- **Hot Reloading**: Reload SQL files during development without restart

**Key Functions:**
```python
load_queries()                  # Discover and load all SQL files
get_query(category, name)       # Get a specific SQL query
format_query(cat, name, **vars) # Get query with template substitution
has_query(category, name)       # Check if query exists
list_available_queries()        # List all available queries
reload_queries()                # Reload from files (development)
```

**Directory Structure:**
```
backend/sql/
├── schema/          # Table creation and indexing
├── games/           # Games table operations
├── clients/         # Client management queries
├── api_keys/        # API key operations
├── files/           # File storage queries
└── stats/           # Statistics and reporting
```

### database.py - Pure Data Access Layer ✅ REFACTORED
**Purpose**: Raw database operations ONLY - now uses external SQL files

**Contains:**
- Database connection management (`DatabaseManager` class)
- Table-specific CRUD operations using external SQL
- Raw SQL query execution with template support
- Database initialization from SQL files

**Import Rules**: Can import `config` and `sql_manager` only
**Status**: Refactored to use external SQL files - maintains same API

**Key Changes:**
- All SQL statements moved to external .sql files
- Dynamic query loading from sql/ directory
- Template variable support for configurable queries
- Maintains backward compatibility with existing functions

**Key Functions (Table-Organized):**
```python
# Database Management
init_db()                       # Initialize database schema from SQL files
DatabaseManager.get_connection() # Context manager for connections

# Games Table (using sql/games/*.sql)
get_games_all(limit, order_by)  # Uses games/select_all.sql
get_games_recent(limit)         # Uses games/select_recent.sql
create_game_record(game_data)   # Uses games/insert_game.sql
check_game_exists(game_id)      # Uses games/check_exists.sql

# Clients Table (using sql/clients/*.sql)
get_clients_all()               # Uses clients/select_all.sql
create_client_record()          # Uses clients/insert_client.sql
update_clients_info()           # Uses clients/update_info.sql

# API Keys Table (using sql/api_keys/*.sql)
get_api_keys_by_key()           # Uses api_keys/select_by_key.sql
create_api_key_record()         # Uses api_keys/insert_key.sql
validate_api_key(api_key)       # Uses api_keys/select_by_key.sql

# Files Table (using sql/files/*.sql)
get_files_by_client()           # Uses files/select_by_client.sql
create_file_record()            # Uses files/insert_file.sql
get_file_by_hash()              # Uses files/select_by_hash.sql

# Dynamic Query Execution
add_custom_query_execution()    # Execute any available SQL file
execute_formatted_query()       # Execute with template variables
reload_sql_queries()            # Reload SQL files (development)
```

### utils.py - Shared Utilities & Business Logic Helpers ✅ COMPLETE
**Purpose**: Helper functions and shared business logic used across multiple modules

**Contains:**
- URL encoding/decoding (`encode_player_tag()`, `decode_player_tag()`)
- Error template data (`get_error_template_data()`)
- **Game Data Processing** (shared between services)

**Import Rules**: Can only import `config`
**Status**: Complete with comprehensive game processing functions

**Key Functions:**
```python
# URL Utilities
encode_player_tag(tag)          # URL-encode player tags
decode_player_tag(encoded_tag)  # Decode URL-encoded tags

# Error Handling
get_error_template_data()       # Generate error page template data

# Game Data Processing (Shared Business Logic)
parse_player_data_from_game()   # Parse JSON player data
find_player_in_game_data()      # Find specific player in game
safe_get_player_field()         # Safe field extraction with defaults
process_raw_games_for_player()  # Process games for specific player
find_flexible_player_matches()  # Player search with fuzzy matching
extract_player_stats_from_games() # Extract player rankings from all games
process_recent_games_data()     # Format recent games for display
calculate_win_rate()            # Win rate calculation with safety checks
```

### web_service.py - Web Business Logic ✅ COMPLETE
**Purpose**: Business logic for web page rendering and template data preparation

**Contains:**
- Template data preparation for HTML pages
- Player statistics calculation for web display
- Data access wrappers that combine database + utils processing
- Request handling logic with redirect management

**Import Rules**: Can import `database`, `utils`, `config`
**Status**: Complete with clean separation from database layer

**Key Functions:**
```python
# Statistics Calculation
calculate_player_stats(games)   # Comprehensive player statistics

# Data Access (Web-Specific)
get_player_games(player_code)   # Get all games for player
find_player_matches()           # Find potential player matches
get_recent_games(limit)         # Get recent games for homepage
get_top_players(limit)          # Get top players by win rate
get_all_players()               # Get all players with stats

# Template Data Preparation
prepare_homepage_data()         # Homepage template data
prepare_all_players_data()      # Players page template data
prepare_standard_player_template_data() # Player page template data

# Request Processing
process_player_profile_request() # Handle player profile requests
process_player_detailed_request() # Handle detailed player requests
```

### api_service.py - API Business Logic ✅ COMPLETE
**Purpose**: Business logic for JSON API responses and API-specific concerns

**Contains:**
- API data processing and JSON response formatting
- Advanced filtering logic for detailed analysis
- Client management and authentication
- File upload processing and management
- Request validation and error handling

**Import Rules**: Can import `database`, `utils`, `config`
**Status**: Complete with comprehensive API functionality including file uploads

**Key Functions:**
```python
# Advanced Filtering (API-Specific)
apply_game_filters()            # Apply character/opponent filters
extract_filter_options()       # Extract available filter options
calculate_filtered_stats()     # Calculate stats for filtered data

# API Data Processing
process_detailed_player_data()  # Detailed player data with filtering
process_paginated_player_games() # Paginated game history
process_player_basic_stats()    # Basic player statistics
process_server_statistics()     # Server health and stats

# File Upload Management
process_file_upload()           # Handle individual file uploads
process_combined_upload()       # Handle games + files together
save_uploaded_file()            # Save files to organized directory structure
calculate_file_hash()           # SHA-256 hash calculation

# Client Management
register_or_update_client()     # Register/update client information
upload_games_for_client()       # Process game uploads

# Request Processing
process_client_registration()   # Handle client registration API
process_games_upload()          # Handle games upload API
```

### app.py - Flask Application ✅ COMPLETE
**Purpose**: Flask application setup, route definitions, and HTTP handling

**Contains:**
- Flask app configuration and initialization
- Route handlers for both web and API endpoints
- Authentication decorators (`require_api_key`, `rate_limited`)
- Error handlers for all HTTP status codes
- Static file serving and file upload endpoints

**Import Rules**: Can import all service modules
**Status**: Clean and well-organized with proper service separation

**Key Components:**
```python
# Application Setup
Flask app configuration           # Template/static folder setup
Context processors               # Inject request object
Configuration loading           # Secret key, debug settings

# Authentication Decorators
@require_api_key                # Validate API key for protected endpoints
@rate_limited(max_per_minute)   # Rate limiting by client

# Web Routes (Using web_service)
/                               # Homepage
/player/<code>                  # Player profile
/player/<code>/detailed         # Detailed player analysis
/players                        # All players listing

# API Routes (Using api_service)
/api/player/<code>/stats        # Basic player stats
/api/player/<code>/games        # Paginated game history
/api/player/<code>/detailed     # Advanced filtering (POST)
/api/clients/register           # Client registration
/api/games/upload               # Game data upload (legacy + combined)
/api/files/upload               # File upload endpoint
/api/files                      # List files by client
/api/files/<id>                 # Get file details
/api/stats                      # Server statistics

# Error Handlers
400, 401, 403, 404, 429, 500    # HTTP error pages
Exception handler               # Catch-all error handling
```

## SQL File Management System

### Overview
The new SQL management system provides:
- **Dynamic Discovery**: Automatically finds and loads .sql files
- **Category Organization**: Queries organized by database table/function
- **Template Support**: Dynamic variable substitution in queries
- **Hot Reloading**: Update SQL files without restarting the application

### Directory Structure
```
backend/sql/
├── schema/
│   ├── init_tables.sql         # Database table creation
│   └── init_indexes.sql        # Performance indexes
├── games/
│   ├── select_all.sql          # Get all games with options
│   ├── select_recent.sql       # Recent games by date
│   ├── insert_game.sql         # Insert new game record
│   └── check_exists.sql        # Check if game exists
├── clients/
│   ├── select_all.sql          # Get all clients
│   ├── insert_client.sql       # Register new client
│   └── update_last_active.sql  # Update client activity
├── api_keys/
│   ├── select_by_key.sql       # Validate API key
│   ├── insert_key.sql          # Create new API key
│   └── delete_expired.sql      # Clean up expired keys
├── files/
│   ├── select_by_client.sql    # Get files by client
│   ├── insert_file.sql         # Store file record
│   └── select_by_hash.sql      # Find file by hash
└── stats/
    ├── unique_players.sql      # Count unique players
    ├── file_stats_totals.sql   # File storage statistics
    └── latest_upload.sql       # Most recent upload time
```

### Adding New Queries

#### 1. Simple Query Addition
Create a new .sql file in the appropriate category:

```bash
# Add a query to find games by stage
cat > backend/sql/games/select_by_stage.sql << 'EOF'
SELECT * FROM games 
WHERE stage_id = ? 
ORDER BY start_time DESC
EOF
```

Use immediately in Python:
```python
# No code changes needed - automatically available
from backend.database import add_custom_query_execution
stage_games = add_custom_query_execution('games', 'select_by_stage', params=(31,))
```

#### 2. Template Query Addition
Create queries with dynamic placeholders:

```bash
# Add a flexible tournament query
cat > backend/sql/games/select_tournament_games.sql << 'EOF'
SELECT * FROM games 
WHERE game_type = '{tournament_type}'
  AND datetime(start_time) >= datetime('{start_date}')
ORDER BY {order_field} {order_direction}
LIMIT {limit_count}
EOF
```

Use with template variables:
```python
from backend.database import execute_formatted_query
tournament_games = execute_formatted_query(
    'games', 'select_tournament_games',
    tournament_type='bracket',
    start_date='2024-01-01',
    order_field='start_time',
    order_direction='DESC',
    limit_count=100
)
```

#### 3. New Category Addition
Create entirely new query categories:

```bash
# Create analytics category
mkdir backend/sql/analytics

# Add complex analysis query
cat > backend/sql/analytics/player_matchup_matrix.sql << 'EOF'
WITH matchups AS (
    SELECT 
        json_extract(p1.value, '$.player_tag') as player1,
        json_extract(p1.value, '$.character_name') as char1,
        json_extract(p2.value, '$.player_tag') as player2,
        json_extract(p2.value, '$.character_name') as char2,
        CASE WHEN json_extract(p1.value, '$.result') = 'Win' THEN 1 ELSE 0 END as p1_win
    FROM games g,
         json_each(g.player_data) p1,
         json_each(g.player_data) p2
    WHERE p1.key != p2.key
)
SELECT 
    player1, char1, player2, char2,
    COUNT(*) as total_games,
    SUM(p1_win) as wins,
    ROUND(AVG(p1_win) * 100, 2) as win_rate
FROM matchups
GROUP BY player1, char1, player2, char2
HAVING total_games >= {min_games}
ORDER BY total_games DESC, win_rate DESC
EOF
```

Use immediately:
```python
# Analytics queries become available automatically
matchup_data = execute_formatted_query(
    'analytics', 'player_matchup_matrix',
    min_games=5
)
```

## Data Flow Architecture

### Request Processing Flow with SQL Files
```
HTTP Request → app.py Route → Service Layer → Database Layer → SQL Files → Response
```

**Detailed Flow:**
1. **app.py** receives HTTP request and validates parameters
2. **app.py** calls appropriate **Service** function (web_service or api_service)
3. **Service** calls **Database** functions for raw data
4. **Database** loads appropriate **SQL file** using sql_manager
5. **Database** executes SQL with parameters/templates
6. **Service** calls **Utils** functions for data processing
7. **Service** applies business logic and returns processed data
8. **app.py** formats response (HTML template or JSON)
9. **app.py** returns HTTP response

### SQL Query Execution Patterns

#### Basic Query Execution
```python
# In database.py
def get_games_recent(limit=10):
    try:
        query = sql_manager.get_query('games', 'select_recent')
        return db_manager.execute_query(query, (limit,))
    except Exception as e:
        logger.error(f"Error getting recent games: {str(e)}")
        return []
```

#### Template Query Execution
```python
# In database.py
def get_games_all(limit=None, order_by='start_time DESC'):
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = sql_manager.format_query('games', 'select_all',
                                            order_by=order_by,
                                            limit_clause=f'LIMIT {limit}' if limit else '')
            
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting all games: {str(e)}")
        return []
```

#### Dynamic Query Discovery
```python
# Check what queries are available
available_queries = sql_manager.list_available_queries()
# Returns: {'games': ['select_all', 'select_recent', ...], 'clients': [...], ...}

# Check if a specific query exists
if sql_manager.has_query('analytics', 'player_performance'):
    # Use the query
    pass
else:
    # Fallback to different approach
    pass
```

## Development Guidelines

### Adding New Functionality

#### 1. Database Operations (New SQL File Approach)
Add new SQL files to appropriate category:
```bash
# Create the SQL file
cat > backend/sql/games/select_by_player_and_character.sql << 'EOF'
SELECT * FROM games g, json_each(g.player_data) p
WHERE json_extract(p.value, '$.player_tag') = ?
  AND json_extract(p.value, '$.character_name') = ?
ORDER BY datetime(g.start_time) DESC
EOF
```

Use in database.py:
```python
def get_games_by_player_and_character(player_tag, character):
    """Get games for specific player using specific character."""
    try:
        query = sql_manager.get_query('games', 'select_by_player_and_character')
        return db_manager.execute_query(query, (player_tag, character))
    except Exception as e:
        logger.error(f"Error getting games for {player_tag} with {character}: {str(e)}")
        return []
```

#### 2. Complex Analytics Queries
Create sophisticated analysis queries:
```bash
# Advanced statistical analysis
cat > backend/sql/analytics/stage_winrate_analysis.sql << 'EOF'
WITH stage_performance AS (
    SELECT 
        g.stage_id,
        json_extract(p.value, '$.player_tag') as player,
        json_extract(p.value, '$.character_name') as character,
        CASE WHEN json_extract(p.value, '$.result') = 'Win' THEN 1 ELSE 0 END as won
    FROM games g, json_each(g.player_data) p
    WHERE player = '{target_player}'
)
SELECT 
    stage_id,
    character,
    COUNT(*) as games_played,
    SUM(won) as wins,
    ROUND(AVG(won) * 100, 2) as win_rate,
    ROUND(
        (AVG(won) - (SELECT AVG(won) FROM stage_performance)) * 100, 
        2
    ) as win_rate_vs_average
FROM stage_performance
GROUP BY stage_id, character
HAVING games_played >= {min_games}
ORDER BY win_rate DESC
EOF
```

#### 3. Shared Business Logic
Add to utils.py for cross-service functionality:
```python
def process_stage_performance_data(raw_performance_data):
    """Process raw stage performance into display format."""
    stage_names = {
        2: "Fountain of Dreams",
        31: "Battlefield", 
        32: "Final Destination"
        # etc.
    }
    
    processed = []
    for row in raw_performance_data:
        processed.append({
            'stage_name': stage_names.get(row['stage_id'], f"Stage {row['stage_id']}"),
            'character': row['character'],
            'stats': {
                'games': row['games_played'],
                'wins': row['wins'],
                'win_rate': row['win_rate'],
                'vs_average': row['win_rate_vs_average']
            }
        })
    
    return processed
```

#### 4. Service Integration
Use in service layers:
```python
# In api_service.py
def process_player_stage_analysis(player_code, min_games=5):
    """Get stage performance analysis for a player."""
    try:
        # Use the new SQL query
        raw_data = execute_formatted_query(
            'analytics', 'stage_winrate_analysis',
            target_player=player_code,
            min_games=min_games
        )
        
        # Process using utils
        return process_stage_performance_data(raw_data)
    except Exception as e:
        logger.error(f"Error analyzing stage performance for {player_code}: {str(e)}")
        raise
```

#### 5. Route Handlers
Add to app.py:
```python
@app.route('/api/player/<encoded_player_code>/stage-analysis')
@require_api_key
def api_player_stage_analysis(encoded_player_code, client_id):
    """Get stage performance analysis for a player."""
    try:
        player_code = decode_player_tag(encoded_player_code)
        min_games = int(request.args.get('min_games', '5'))
        
        result = api_service.process_player_stage_analysis(player_code, min_games)
        return jsonify({
            'player_code': player_code,
            'stage_analysis': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### SQL File Organization Best Practices

#### 1. Naming Conventions
- **Categories**: Use table names or functional areas (games, clients, analytics)
- **Files**: Use verb_object pattern (select_all, insert_game, update_info)
- **Complex queries**: Use descriptive names (player_matchup_analysis, stage_performance_stats)

#### 2. Template Variables
- Use `{variable_name}` for dynamic substitution
- Document required variables in SQL comments
- Provide sensible defaults where possible

#### 3. Query Documentation
Add comments to complex SQL files:
```sql
-- Player matchup analysis with character breakdown
-- Template variables:
--   {target_player} - Player tag to analyze
--   {min_games} - Minimum games required for inclusion
--   {date_filter} - Optional date filter (default: all time)

WITH player_matchups AS (
    -- Get all games involving the target player
    SELECT ...
)
-- Main analysis query
SELECT ...
```

### Performance Considerations

#### 1. SQL Query Optimization
- Create appropriate indexes for new query patterns
- Use EXPLAIN QUERY PLAN for complex queries
- Consider materialized views for expensive calculations

#### 2. Query Caching
- SQL manager caches loaded queries in memory
- Use `reload_sql_queries()` during development
- Consider Redis caching for expensive query results

#### 3. File Organization
- Keep related queries in the same category
- Split very large queries into smaller, composable pieces
- Use template variables to reduce query duplication

## Testing Strategy

### SQL File Testing
```python
def test_sql_files_load():
    """Test that all SQL files load without syntax errors."""
    sql_manager.reload_queries()
    categories = sql_manager.get_categories()
    assert len(categories) > 0
    
    for category in categories:
        queries = sql_manager.get_category_queries(category)
        assert len(queries) > 0

def test_template_substitution():
    """Test template variable substitution."""
    # Assuming we have a templated query
    query = sql_manager.format_query('games', 'select_all', 
                                    order_by='start_time', 
                                    limit_clause='LIMIT 10')
    assert 'start_time' in query
    assert 'LIMIT 10' in query
```

### Database Integration Testing
```python
def test_new_query_execution():
    """Test new SQL queries work with real database."""
    # Test with in-memory database
    with db_manager.get_connection() as conn:
        # Setup test data
        # Execute new queries
        # Verify results
        pass
```

## Current Status & Future Plans

### ✅ Completed Refactoring
- **Phase 1**: Configuration & Database (COMPLETE)
- **Phase 2**: Services & Utilities (COMPLETE)  
- **Phase 3**: Data Layer Refactoring (COMPLETE)
- **Phase 4**: SQL File Externalization (COMPLETE)

### 🔄 Current State
The backend now has a **clean, maintainable architecture with external SQL file management** that is production-ready and highly extensible.

### Key Benefits of SQL File System
- **Developer Friendly**: Easy to read, write, and maintain SQL
- **Version Control**: SQL changes tracked in git like code
- **Hot Reloading**: Update queries without application restart
- **Dynamic Discovery**: Add queries without modifying Python code
- **Template Support**: Flexible, reusable query patterns
- **Category Organization**: Logical grouping of related operations

### 📋 Future Enhancements
- **Query Performance Monitoring**: Track slow queries and optimization opportunities
- **SQL Migration System**: Versioned schema changes with rollback capability  
- **Query Builder Integration**: Optional programmatic query construction for complex scenarios
- **Caching Layer**: Redis integration for expensive query result caching
- **Database Abstraction**: Support for PostgreSQL and other databases beyond SQLite