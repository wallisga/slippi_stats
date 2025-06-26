# SQL Files Architecture

This directory contains all SQL queries organized by functionality. The SQL manager automatically discovers and loads these files, making them available throughout the application without requiring code changes.

## Directory Structure

```
backend/sql/
├── README.md              # This file
├── schema/                # Database schema and indexes
│   ├── init_tables.sql    # Table creation DDL
│   └── init_indexes.sql   # Performance indexes
├── games/                 # Game-related queries
│   ├── select_all.sql     # Get all games with options
│   ├── select_recent.sql  # Recent games by date
│   ├── insert_game.sql    # Insert new game record
│   └── check_exists.sql   # Check if game exists
├── clients/               # Client management queries
│   ├── select_all.sql     # Get all clients
│   ├── insert_client.sql  # Register new client
│   └── update_last_active.sql  # Update client activity
├── api_keys/              # Authentication queries
│   ├── select_by_key.sql  # Validate API key
│   ├── insert_key.sql     # Create new API key
│   └── delete_expired.sql # Clean up expired keys
├── files/                 # File storage queries
│   ├── select_by_client.sql # Get files by client
│   ├── insert_file.sql     # Store file record
│   └── select_by_hash.sql  # Find file by hash
└── stats/                 # Statistics and reporting
    ├── unique_players.sql  # Count unique players
    ├── file_stats_totals.sql # File storage statistics
    └── latest_upload.sql   # Most recent upload time
```

## Core Principles

### 1. **Dynamic Discovery**
- Add any `.sql` file to a category directory and it becomes available immediately
- No Python code changes required when adding new queries
- Categories are subdirectories, queries are filenames without `.sql`

### 2. **Template Support**
- Use `{variable_name}` for dynamic value substitution
- Template variables replaced at runtime using `sql_manager.format_query()`
- Enables flexible, reusable query patterns

### 3. **Category Organization**
- **schema**: Database structure and maintenance
- **games**: Game data operations
- **clients**: Client management and registration
- **api_keys**: Authentication and authorization
- **files**: File upload and storage operations
- **stats**: Analytics and reporting queries

### 4. **Naming Conventions**
- **Verbs**: `select_`, `insert_`, `update_`, `delete_`, `check_`, `count_`
- **Objects**: Table or concept being operated on
- **Modifiers**: Specific conditions or variations

## Query Categories

### Schema Queries (`schema/`)
**Purpose**: Database structure and maintenance operations

**Characteristics**:
- DDL statements (CREATE, ALTER, DROP)
- Index creation and optimization
- Template variables for configurable table names
- Used during application initialization

**Example Files**:
```sql
-- init_tables.sql
CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    client_id TEXT,
    start_time TEXT,
    -- ...
);

-- init_indexes.sql  
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games (start_time);
```

### Games Queries (`games/`)
**Purpose**: Core game data operations

**Characteristics**:
- High-frequency read operations
- Complex filtering and sorting options
- Template support for dynamic ordering and limits
- JSON player data extraction

**Common Patterns**:
```sql
-- Template query with flexible ordering
SELECT * FROM games 
ORDER BY {order_by} 
{limit_clause}

-- Parameterized query with placeholders
SELECT * FROM games WHERE game_id = ?
```

### Clients Queries (`clients/`)
**Purpose**: Client registration and management

**Characteristics**:
- CRUD operations for client records
- Activity tracking and updates
- Registration workflow support
- Metadata management

**Usage Patterns**:
- Registration: `insert_client.sql` + `check_exists.sql`
- Activity tracking: `update_last_active.sql`
- Administration: `select_all.sql` + `count_all.sql`

### API Keys Queries (`api_keys/`)
**Purpose**: Authentication and authorization

**Characteristics**:
- Security-focused operations
- Expiration management
- Template support for configurable table names
- Key validation and cleanup

**Security Considerations**:
- Never log actual API key values
- Implement key rotation via `update_key.sql`
- Regular cleanup via `delete_expired.sql`

### Files Queries (`files/`)
**Purpose**: File upload and storage operations

**Characteristics**:
- Hash-based deduplication
- Client-specific file access
- Metadata storage and retrieval
- Storage statistics and management

**Deduplication Flow**:
1. `check_exists_by_hash.sql` - Check for duplicates
2. `insert_file.sql` - Store new file record
3. `select_by_hash.sql` - Retrieve existing file info

### Stats Queries (`stats/`)
**Purpose**: Analytics and reporting

**Characteristics**:
- Complex aggregations and calculations
- JSON data extraction from player_data
- Performance-sensitive queries
- Cross-table analysis

**Performance Tips**:
- Use indexes on frequently queried columns
- Consider materialized views for expensive calculations
- Break complex queries into smaller, cacheable pieces

## Template System

### Basic Template Usage
```sql
-- Query with template variables
SELECT * FROM games 
WHERE stage_id = {stage_id} 
ORDER BY {order_field} {direction}
LIMIT {limit_count}
```

```python
# Python usage
query = sql_manager.format_query('games', 'select_by_stage',
                                stage_id=31,
                                order_field='start_time',
                                direction='DESC',
                                limit_count=10)
```

### Conditional Templates
```sql
-- Query with optional WHERE clause
SELECT * FROM games 
{where_clause}
ORDER BY start_time DESC
{limit_clause}
```

```python
# Usage with conditional clauses
query = sql_manager.format_query('games', 'select_conditional',
                                where_clause='WHERE client_id = ?',
                                limit_clause='LIMIT 50')
```

### Configuration Templates
```sql
-- Query using configuration values
SELECT * FROM {api_keys_table} 
WHERE expires_at > datetime('now')
```

```python
# Usage with config values
query = sql_manager.format_query('api_keys', 'select_valid',
                                api_keys_table=config.API_KEYS_TABLE)
```

## Adding New Queries

### 1. Simple Query Addition
```bash
# Create new query file
cat > backend/sql/games/select_by_character.sql << 'EOF'
SELECT g.*, json_extract(p.value, '$.character_name') as character
FROM games g, json_each(g.player_data) p
WHERE json_extract(p.value, '$.character_name') = ?
ORDER BY g.start_time DESC
EOF
```

```python
# Use immediately in database.py
def get_games_by_character(character_name):
    query = sql_manager.get_query('games', 'select_by_character')
    return db_manager.execute_query(query, (character_name,))
```

### 2. Template Query Addition
```bash
# Create flexible tournament query
cat > backend/sql/analytics/tournament_analysis.sql << 'EOF'
WITH tournament_games AS (
    SELECT * FROM games 
    WHERE game_type = '{tournament_type}'
      AND datetime(start_time) >= datetime('{start_date}')
      {additional_filters}
)
SELECT 
    COUNT(*) as total_games,
    COUNT(DISTINCT json_extract(p.value, '$.player_tag')) as unique_players
FROM tournament_games g, json_each(g.player_data) p
EOF
```

```python
# Use with multiple template variables
def analyze_tournament(tournament_type, start_date, additional_filters=""):
    query = sql_manager.format_query('analytics', 'tournament_analysis',
                                    tournament_type=tournament_type,
                                    start_date=start_date,
                                    additional_filters=additional_filters)
    return db_manager.execute_query(query, fetch_one=True)
```

### 3. New Category Addition
```bash
# Create new category for tournaments
mkdir backend/sql/tournaments

# Add tournament-specific queries
echo "SELECT * FROM games WHERE game_type = 'tournament'" > backend/sql/tournaments/select_all.sql
echo "INSERT INTO tournament_metadata (game_id, bracket_position) VALUES (?, ?)" > backend/sql/tournaments/insert_metadata.sql
```

```python
# Use new category immediately
tournament_games = sql_manager.get_query('tournaments', 'select_all')
```

## Query Performance Guidelines

### 1. Index Usage
- Ensure queries use existing indexes effectively
- Add new indexes in `schema/init_indexes.sql` if needed
- Use `EXPLAIN QUERY PLAN` to analyze query performance

### 2. JSON Query Optimization
```sql
-- Efficient JSON extraction with proper indexing
SELECT * FROM games 
WHERE json_extract(player_data, '$[0].player_tag') = ?
  AND start_time >= ?
ORDER BY start_time DESC
```

### 3. Parameterized Queries
- Use `?` placeholders for user input
- Avoid string concatenation in SQL
- Let SQLite handle parameter binding

### 4. Limit Result Sets
```sql
-- Always include reasonable limits
SELECT * FROM games 
ORDER BY start_time DESC 
LIMIT {max_results}
```

## Development Workflow

### Adding Queries During Development
1. **Create SQL file** in appropriate category directory
2. **Test query** in SQLite browser or similar tool
3. **Add database function** in `database.py` to use the query
4. **Update service layer** to call the new database function
5. **Test integration** through API or web interface

### Query Testing
```bash
# Test query directly in SQLite
sqlite3 data/slippi_stats.db < backend/sql/games/select_recent.sql

# Test with parameters
sqlite3 data/slippi_stats.db "$(cat backend/sql/games/select_by_id.sql)" "game_123"
```

### Query Documentation
```sql
-- Complex query with documentation
-- Purpose: Analyze player performance across different stages
-- Template variables:
--   {target_player} - Player tag to analyze
--   {min_games} - Minimum games required for inclusion
--   {date_filter} - Optional date filter (default: all time)
-- Returns: stage_id, character, games_played, wins, win_rate

WITH player_stage_performance AS (
    -- Main query logic here
)
SELECT * FROM player_stage_performance;
```

## Best Practices

### 1. Query Organization
- Keep related queries in the same category
- Use descriptive filenames that indicate purpose
- Split complex operations into multiple focused queries

### 2. Template Usage
- Document required template variables in comments
- Provide sensible defaults where possible
- Use templates for configuration values (table names, etc.)

### 3. Performance Considerations
- Include reasonable default limits
- Use indexes effectively
- Consider query complexity and execution time

### 4. Security Practices
- Always use parameterized queries for user input
- Never include sensitive data in query files
- Validate template variables before substitution

### 5. Maintainability
- Keep queries readable with proper formatting
- Add comments for complex logic
- Use consistent naming conventions across categories

This SQL architecture provides a scalable, maintainable foundation for database operations while keeping all SQL code organized, version-controlled, and easily discoverable.