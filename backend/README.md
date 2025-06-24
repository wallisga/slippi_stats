# Backend Architecture Documentation

This document provides detailed information about the Slippi Stats Server backend architecture, module design, and development guidelines.

## Architecture Overview

The backend follows a **service-oriented architecture** with clear separation of concerns. Each module has specific responsibilities and follows strict import rules to maintain clean dependencies.

### Core Principle: "Services Process, Database Stores, Utils Help"

- **Services**: Business logic and request processing (web_service.py, api_service.py)
- **Database**: Pure data access with no business logic (database.py)
- **Utils**: Shared helper functions and data processing (utils.py)
- **Config**: Centralized configuration management (config.py)
- **App**: Flask setup and HTTP routing (app.py)

## Module Structure & Responsibilities

### Module Hierarchy
```
app.py (Flask routes & HTTP handling)        # Top level
    ↓ can import
web_service.py + api_service.py              # Business logic layers
    ↓ can import  
utils.py (shared helpers) + database.py (data access) + config.py  # Foundation
```

### Import Rules (Strictly Enforced)
- ✅ **Services** can import: `backend.database`, `backend.utils`, `backend.config`
- ✅ **Utils** can import: `backend.config` only
- ✅ **Database** can import: `backend.config` only
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

### database.py - Pure Data Access Layer ✅ COMPLETE  
**Purpose**: Raw database operations ONLY - no business logic

**Contains:**
- Database connection management (`DatabaseManager` class)
- Table-specific CRUD operations
- Raw SQL queries and data retrieval
- Database initialization (`init_db()`)

**Import Rules**: Can import `config` only
**Status**: Complete refactoring - pure data access, no business logic

**Key Functions (Table-Organized):**
```python
# Database Management
init_db()                       # Initialize database schema
DatabaseManager.get_connection() # Context manager for connections

# Games Table
get_games_all(limit, order_by)  # Get all games with optional limit/ordering
get_games_recent(limit)         # Get recent games by start_time
get_games_by_date_range()       # Get games within date range
create_game_record(game_data)   # Insert new game record
check_game_exists(game_id)      # Check if game exists
get_games_count()               # Total games count

# Clients Table
get_clients_all()               # Get all registered clients
get_clients_by_id(client_id)    # Get specific client
create_client_record()          # Insert new client
update_clients_info()           # Update client information
update_clients_last_active()    # Update last active timestamp
check_client_exists()           # Check if client exists
get_clients_count()             # Total clients count

# API Keys Table
get_api_keys_all()              # Get all API keys
get_api_keys_by_client()        # Get API key for client
get_api_keys_by_key()           # Get API key record by key value
create_api_key_record()         # Create new API key
update_api_key_record()         # Update existing API key
delete_api_keys_expired()       # Clean up expired keys
validate_api_key(api_key)       # Validate API key and return client_id

# Statistics
get_database_stats()            # Basic database statistics (counts only)
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
- Request validation and error handling

**Import Rules**: Can import `database`, `utils`, `config`
**Status**: Complete with comprehensive API functionality

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
- Static file serving

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
/api/games/upload               # Game data upload
/api/stats                      # Server statistics

# Error Handlers
400, 401, 403, 404, 429, 500    # HTTP error pages
Exception handler               # Catch-all error handling
```

## Data Flow Architecture

### Request Processing Flow
```
HTTP Request → app.py Route → Service Layer → Utils + Database → Response
```

**Detailed Flow:**
1. **app.py** receives HTTP request and validates parameters
2. **app.py** calls appropriate **Service** function (web_service or api_service)
3. **Service** calls **Database** functions for raw data
4. **Service** calls **Utils** functions for data processing
5. **Service** applies business logic and returns processed data
6. **app.py** formats response (HTML template or JSON)
7. **app.py** returns HTTP response

### Data Processing Patterns

#### Web Pages (Template Rendering)
```python
# In backend/web_service.py
def prepare_homepage_data():
    raw_games = database.get_games_recent(10)     # Raw data access
    recent_games = utils.process_recent_games_data(raw_games)  # Processing
    # Apply web-specific business logic
    return template_data

# In app.py
@app.route('/')
def homepage():
    data = web_service.prepare_homepage_data()    # Service handles logic
    return render_template('pages/index/index.html', **data)
```

#### API Endpoints (JSON Responses)
```python
# In backend/api_service.py
def process_detailed_player_data(player_code, filters):
    raw_games = database.get_games_all()         # Raw data access
    player_games = utils.process_raw_games_for_player(raw_games, player_code)
    filtered_games = apply_game_filters(player_games, **filters)  # API logic
    return json_response_data

# In app.py
@app.route('/api/player/<code>/detailed', methods=['POST'])
def api_detailed(code):
    filters = request.get_json()
    result = api_service.process_detailed_player_data(code, filters)
    return jsonify(result)
```

## Development Guidelines

### Adding New Functionality

#### 1. Database Operations
Add new functions to `database.py` with table-specific naming:
```python
def get_games_by_stage(stage_id):
    """Get all games played on specific stage."""
    with db_manager.get_connection() as conn:
        # Raw SQL only, no business logic
        return conn.execute("SELECT * FROM games WHERE stage_id = ?", (stage_id,)).fetchall()
```

#### 2. Shared Business Logic
Add cross-service functionality to `utils.py`:
```python
def process_stage_statistics(raw_games):
    """Process raw games to extract stage statistics."""
    # Shared data processing logic
    pass
```

#### 3. Service-Specific Logic
Add to appropriate service module:
```python
# In web_service.py for web pages
def prepare_tournament_page_data():
    """Prepare data for tournament page rendering."""
    raw_games = database.get_games_all()
    return utils.process_tournament_data(raw_games)

# In api_service.py for API endpoints  
def process_tournament_api_request(tournament_id, filters):
    """Process tournament API request with filtering."""
    raw_games = database.get_games_by_tournament(tournament_id)
    return apply_tournament_filters(raw_games, filters)
```

#### 4. Route Handlers
Add to `app.py` with clear service separation:
```python
@app.route('/tournaments')
def web_tournaments():
    data = web_service.prepare_tournament_page_data()
    return render_template('pages/tournaments.html', **data)

@app.route('/api/tournaments/<id>')
def api_tournament_data(id):
    result = api_service.process_tournament_api_request(id, request.json)
    return jsonify(result)
```

### Module Design Principles

#### 1. Single Responsibility
- Each module has one clear purpose
- Functions within modules have specific, focused responsibilities
- No mixing of concerns between layers

#### 2. Dependency Direction
- Higher-level modules depend on lower-level modules
- No circular dependencies allowed
- Database layer is the foundation, services build on top

#### 3. Data Flow Consistency
- Raw data comes from database layer
- Processing happens in utils or services
- Business logic stays in service layers
- HTTP handling only in app.py

#### 4. Error Handling Strategy
- Database layer: Log errors and raise exceptions
- Utils layer: Handle data processing errors gracefully
- Service layer: Validate inputs and handle business logic errors
- App layer: Convert exceptions to appropriate HTTP responses

## Testing Strategy

### Database Layer Testing
```python
# Test with in-memory SQLite
def test_game_operations():
    # Create test database in memory
    # Test CRUD operations
    # Verify data integrity
```

### Service Layer Testing
```python
# Mock database calls, test business logic
def test_player_stats_calculation():
    # Mock raw game data
    # Test statistics calculation
    # Verify output format
```

### Integration Testing
```python
# Test full request flow
def test_player_profile_endpoint():
    # Mock database with test data
    # Make HTTP request
    # Verify response content and format
```

## Performance Considerations

### Database Query Optimization
- Use indexes for frequently queried columns
- Limit result sets with LIMIT clauses
- Use prepared statements for repeated queries
- Consider pagination for large datasets

### Caching Strategy
- Cache expensive calculations in service layer
- Use database connection pooling for high traffic
- Consider Redis for session storage in production

### Memory Management
- Process large datasets in chunks
- Use generators for streaming large result sets
- Clean up temporary data structures

## Deployment Considerations

### Environment Configuration
```bash
# Production environment variables
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_PATH=/path/to/production.db
export SLIPPI_REGISTRATION_SECRET=your-registration-secret
```

### Database Management
- Regular backups of SQLite database
- Monitor database size and performance
- Consider PostgreSQL for high-volume deployments

### Security
- API key management and rotation
- Rate limiting configuration
- Input validation and sanitization
- HTTPS in production

## Current Status & Future Plans

### ✅ Completed Refactoring
- **Phase 1**: Configuration & Database (COMPLETE)
- **Phase 2**: Services & Utilities (COMPLETE)  
- **Phase 3**: Data Layer Refactoring (COMPLETE)

### 🔄 Current State
The backend has a **clean, maintainable architecture** that is production-ready.

### 📋 Future Enhancements
- **Route Blueprints**: Organize routes into blueprint modules
- **Service Layer Expansion**: More granular service modules for complex features
- **Background Tasks**: Celery integration for heavy processing
- **API Versioning**: Version management for API endpoints