# Database Layer

**Core Principle: Raw SQL execution only - no business logic, no fallbacks.**

## Overview

The database layer provides direct access to SQL operations via external `.sql` files. Each function executes **one specific SQL statement** with no data processing or business logic.

```
backend/db/
├── README.md           # This file
├── operations.py       # Raw SQL execution functions  
└── sql/               # SQL files organized by table/purpose
    ├── games/         # Game table operations
    ├── clients/       # Client table operations
    ├── files/         # File table operations
    ├── stats/         # Statistics queries
    ├── api_keys/      # API key operations
    └── schema/        # Table creation and indexes
```

## Design Principles

### 1. **One SQL Statement Per Function**
Each database function executes exactly one SQL statement:

```python
def get_games_for_player(player_code):
    """Get all games containing specific player."""
    with db.get_connection() as conn:
        query = sql.get_query('games', 'select_by_player')
        cursor = conn.cursor()
        cursor.execute(query, (player_code,))
        return cursor.fetchall()
```

### 2. **No Business Logic**
Database functions only execute SQL - no data processing:

```python
# ❌ WRONG - business logic in database layer
def get_player_stats(player_code):
    games = get_games_for_player(player_code)
    wins = sum(1 for game in games if is_win(game))  # ❌ Processing
    return {'wins': wins, 'total': len(games)}

# ✅ CORRECT - raw data only
def get_games_for_player(player_code):
    # Just execute SQL and return raw results
    return cursor.fetchall()
```

### 3. **No Fallbacks - Fail Fast**
Database functions let exceptions bubble up to service layers:

```python
# ❌ WRONG - hides problems
def get_all_games():
    try:
        return execute_query()
    except Exception:
        return []  # ❌ Hides real errors

# ✅ CORRECT - fail fast
def get_all_games():
    with db.get_connection() as conn:
        query = sql.get_query('games', 'select_all')
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()  # ✅ Let exceptions bubble up
```

### 4. **External SQL Files**
All SQL statements are stored in external `.sql` files:

```sql
-- backend/db/sql/games/select_by_player.sql
SELECT DISTINCT g.* 
FROM games g, json_each(g.player_data) p
WHERE json_extract(p.value, '$.player_tag') = ?
ORDER BY datetime(g.start_time) DESC
```

## Usage in Service Layers

Service layers call database operations and handle all data processing:

```python
# In web_service.py or api_service.py
def get_player_games(player_code):
    """Get processed games for a player."""
    try:
        # 1. Get raw data from database
        raw_games = db_operations.get_games_for_player(player_code)
        
        # 2. Process the data (service layer responsibility)
        processed_games = process_raw_games_for_player(raw_games, player_code)
        
        return processed_games
        
    except Exception as e:
        logger.error(f"Error getting games for {player_code}: {e}")
        # Service layer decides how to handle errors
        raise  # or return default value, or redirect, etc.
```

## Adding New Operations

### 1. Create SQL File
```bash
# Create the SQL file
cat > backend/db/sql/games/select_by_character.sql << 'EOF'
SELECT DISTINCT g.* 
FROM games g, json_each(g.player_data) p
WHERE json_extract(p.value, '$.player_tag') = ?
  AND json_extract(p.value, '$.character_name') = ?
ORDER BY datetime(g.start_time) DESC
EOF
```

### 2. Add Database Function
```python
# In backend/db/operations.py
def get_games_for_player_character(player_code, character):
    """Get games for player using specific character."""
    with db.get_connection() as conn:
        query = sql.get_query('games', 'select_by_character')
        cursor = conn.cursor()
        cursor.execute(query, (player_code, character))
        return cursor.fetchall()
```

### 3. Use in Service Layer
```python
# In web_service.py or api_service.py
def get_character_performance(player_code, character):
    """Get processed character performance data."""
    try:
        raw_games = db_operations.get_games_for_player_character(player_code, character)
        return calculate_character_stats(raw_games)  # Process in service layer
    except Exception as e:
        logger.error(f"Error getting character performance: {e}")
        raise
```

## SQL File Organization

### Games Table (`backend/db/sql/games/`)
- `select_all.sql` - Get all games
- `select_recent.sql` - Get recent games
- `select_by_player.sql` - Get games for specific player
- `insert_game.sql` - Insert new game
- `count_all.sql` - Count total games
- `check_exists.sql` - Check if game exists

### Clients Table (`backend/db/sql/clients/`)
- `select_all.sql` - Get all clients
- `select_by_id.sql` - Get client by ID
- `insert_client.sql` - Insert new client
- `update_last_active.sql` - Update last active timestamp
- `count_all.sql` - Count total clients

### Statistics (`backend/db/sql/stats/`)
- `basic_counts.sql` - Basic count statistics
- `unique_players.sql` - Count unique players
- `file_stats.sql` - File storage statistics

### Schema (`backend/db/sql/schema/`)
- `create_tables.sql` - Create all tables
- `create_indexes.sql` - Create database indexes

## Error Handling

Database layer functions **never** catch exceptions except for connection cleanup:

```python
def get_all_games():
    with db.get_connection() as conn:  # ✅ Connection cleanup only
        query = sql.get_query('games', 'select_all')
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()  # ✅ Let service layer handle errors
```

Service layers handle errors appropriately for their context:

```python
# Web service - might redirect or show error page
def get_player_games(player_code):
    try:
        return db_operations.get_games_for_player(player_code)
    except Exception as e:
        logger.error(f"Database error: {e}")
        from flask import abort
        abort(500, "Database temporarily unavailable")

# API service - might return error JSON
def get_player_games(player_code):
    try:
        return db_operations.get_games_for_player(player_code)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {'error': 'Database error', 'details': str(e)}
```

## Development Workflow

1. **Identify data need** in service layer
2. **Check if SQL file exists** in appropriate category
3. **If not, create SQL file** with simple, readable query
4. **Add database function** that executes the SQL
5. **Call from service layer** and process the results
6. **Test with real database** to ensure query works

## Benefits

- **Clear separation** - Database layer only does SQL, service layer only does business logic
- **Easy testing** - Mock database operations, test business logic separately  
- **Simple debugging** - Exceptions show real problems, no hidden failures
- **Easy optimization** - SQL files can be optimized without changing Python code
- **Version control** - SQL changes are tracked in git like code changes