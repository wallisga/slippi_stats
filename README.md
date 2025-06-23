# Slippi Stats Server

A comprehensive web application for collecting, storing, and analyzing Super Smash Bros. Melee game data from Slippi replays. Built with Flask and featuring a modular architecture with real-time filtering and detailed player statistics.

## Overview

Slippi Stats Server provides:
- **Player Profile Pages** with comprehensive statistics and performance analysis
- **Advanced Filtering System** for detailed matchup and character analysis  
- **Real-time Data Visualization** with interactive charts and tables
- **RESTful API** for programmatic access to game data
- **Client Registration System** for automated replay collection

## Architecture & Module Design

### Backend Module Structure
```
app.py                 # Entry point & Flask application setup
├── config.py          # Configuration & environment management
├── utils.py           # Shared utilities & helper functions
├── database.py        # Database operations & data access layer
├── services.py        # Business logic & data processing [PLANNED]
└── routes/            # HTTP route handlers [PLANNED]
    ├── web_routes.py  # HTML page routes
    └── api_routes.py  # JSON API endpoints
```

### Module Responsibilities & Rules

#### **config.py** - Configuration Management
**Purpose**: Centralized configuration and environment settings

**Contains:**
- Environment variable handling (`get_config()`)
- Application settings and constants
- Logging configuration (`init_logging()`)
- Database paths and connection settings
- Feature flags and limits

**Import Rules**: Cannot import any other app modules
**Naming**: Configuration classes and getter functions

#### **utils.py** - Shared Utilities  
**Purpose**: Helper functions used across multiple modules

**Contains:**
- URL encoding/decoding (`encode_player_tag()`, `decode_player_tag()`)
- Data validation (`validate_filter_data()`, `is_valid_page_number()`)
- Formatting helpers (`format_win_rate()`, `format_game_duration()`)
- Safe operations (`safe_divide()`, `safe_int()`)
- Generic utilities (`ensure_list()`, `truncate_string()`)

**Import Rules**: Can only import `config`
**Naming Conventions:**
- `encode_*()` / `decode_*()` - Data conversion
- `format_*()` - Data formatting  
- `safe_*()` - Safe operations with fallbacks
- `is_*()` / `has_*()` - Boolean checks
- `validate_*()` - Input validation

#### **database.py** - Data Access Layer
**Purpose**: Raw database operations ONLY - no business logic

**Contains:**
- Database connection management (`get_db_connection()`)
- CRUD operations on specific tables
- Raw SQL queries and data retrieval
- Database initialization (`init_db()`)

**Import Rules**: Can import `config`, `utils`
**Naming Conventions (Table-Specific):**
- `get_games_*()` - Retrieve from games table
- `get_clients_*()` - Retrieve from clients table  
- `get_api_keys_*()` - Retrieve from api_keys table
- `find_games_*()` - Search games table
- `create_game_*()` - Insert into games table
- `update_clients_*()` - Modify clients table
- `delete_api_keys_*()` - Remove from api_keys table

**Example Functions:**
```python
get_games_for_player(player_code)     # Get games for specific player
find_games_by_date_range(start, end)  # Search games by date
create_client_record(client_data)     # Insert new client
update_clients_last_active(client_id) # Update client activity
```

#### **services.py** - Business Logic Layer [PLANNED]
**Purpose**: Data processing, calculations, and business rules

**Contains:**
- Data transformation and enrichment
- Statistical calculations
- Business rule validation  
- Template data preparation
- Complex operations combining multiple database calls

**Import Rules**: Can import `database`, `utils`, `config`
**Naming Conventions:**
- `calculate_*()` - Perform calculations
- `process_*()` - Transform data
- `prepare_*()` - Ready data for consumption
- `analyze_*()` - Complex analysis
- `validate_*()` - Business rule validation

#### **routes/web_routes.py** - Web Pages [PLANNED]
**Purpose**: HTML page rendering and static file serving

**Contains:**
- Route handlers that return HTML (`render_template()`)
- Static file serving
- Request parameter extraction
- Redirect logic
- Error page handling

**Import Rules**: Can import `services`, `utils`, `config`
**Naming Conventions (Layout-Aware):**
- `web_simple_*()` - Routes using simple.html layout
- `web_player_*()` - Routes using player.html layout
- `web_error_*()` - Routes using error.html layout

**Example Routes:**
```python
@app.route('/')
def web_simple_index():               # Uses simple.html layout
    return render_template('pages/index.html', **data)

@app.route('/player/<code>')  
def web_player_profile(code):         # Uses player.html layout
    return render_template('pages/player_basic.html', **data)
```

#### **routes/api_routes.py** - JSON API [PLANNED]
**Purpose**: JSON API responses for AJAX and external clients

**Contains:**
- API route handlers that return JSON (`jsonify()`)
- Request validation and parameter extraction
- JSON response formatting
- API authentication and rate limiting
- HTTP status code handling

**Import Rules**: Can import `services`, `utils`, `config`
**Naming Conventions:**
- `api_*()` - All API endpoints (no layout reference needed)

**Example Routes:**
```python
@app.route('/api/player/<code>/stats')
def api_player_stats(code):           # Returns JSON
    return jsonify(data)

@app.route('/api/games/upload', methods=['POST'])
def api_games_upload():               # Returns JSON
    return jsonify(result)
```

### Data Flow Architecture

```
HTTP Request → Route Handler → Service Layer → Database Layer → Response
```

**Detailed Flow:**
1. **Route** receives HTTP request and validates parameters
2. **Route** calls appropriate **Service** function  
3. **Service** calls **Database** functions for raw data
4. **Service** processes/transforms data (business logic)
5. **Service** returns processed data to **Route**
6. **Route** formats response (HTML template or JSON)
7. **Route** returns HTTP response

### Module Import Hierarchy

```
Routes (web_routes.py, api_routes.py)     # Top level
    ↓ can import
Services (services.py)                    # Business logic  
    ↓ can import
Database (database.py) + Utils (utils.py) + Config (config.py)  # Foundation
```

**Forbidden Imports:**
- ❌ Database cannot import Services or Routes
- ❌ Services cannot import Routes  
- ❌ Utils cannot import Database, Services, or Routes
- ❌ Config cannot import anything from the app

## Features

### Player Analytics
- **Basic Profiles**: Win rates, character usage, recent games, highlights
- **Detailed Analysis**: Advanced filtering by character, opponent, and matchup
- **Performance Trends**: Time-series charts showing improvement over time
- **Character Statistics**: Win rates and usage patterns for each character
- **Rival Detection**: Identifies frequent opponents and challenging matchups

### Data Management
- **Automated Collection**: Client applications upload replay data automatically
- **API Authentication**: Secure API key system for client access
- **Flexible Storage**: SQLite database with JSON player data for flexibility
- **Data Validation**: Comprehensive validation and error handling

### User Experience
- **Responsive Design**: Bootstrap-based UI that works on all devices
- **Character Icons**: Visual character representations throughout the interface
- **Interactive Charts**: Chart.js powered visualizations with drill-down capabilities
- **Smart Search**: Flexible player search with case-insensitive matching

## Frontend Architecture (Modular Design)

```
templates/
├── base.html                 # Foundation template with core HTML structure
├── layouts/
│   ├── simple.html          # Minimal layout for basic pages
│   ├── player.html          # Enhanced layout for player pages
│   └── error.html           # Error page layout
└── pages/
    ├── index.html           # Homepage
    ├── player_basic.html    # Basic player profile
    ├── player_detailed.html # Advanced player statistics
    └── players.html         # Player index page

static/
├── css/
│   ├── base.css            # Core styles and variables
│   ├── components/         # Reusable component styles
│   └── pages/             # Page-specific styles
└── js/
    ├── base.js            # Global JavaScript utilities
    ├── components/        # Reusable JavaScript components
    └── pages/            # Page-specific JavaScript
```

**Template Inheritance Pattern:**
- `base.html` → `layouts/*.html` → `pages/*.html`
- Each layer adds specific functionality without duplicating code
- Components are self-contained and reusable across pages

### Database Schema
- **clients**: Registered client applications with metadata
- **games**: Individual game records with JSON player data  
- **api_keys**: Authentication tokens for API access

## API Documentation

### Player Endpoints
- `GET /api/player/{code}/stats` - Basic player statistics
- `GET /api/player/{code}/games` - Paginated game history
- `POST /api/player/{code}/detailed` - Advanced filtering and analysis

### Data Endpoints  
- `POST /api/games/upload` - Upload game data (requires API key)
- `GET /api/stats` - Server statistics and health
- `POST /api/clients/register` - Client registration

### Authentication
All data modification endpoints require API key authentication via `X-API-Key` header.

## Installation & Setup

### Prerequisites
- Python 3.8+
- SQLite 3 (included with Python)
- Modern web browser with JavaScript enabled
- Git (for development)

### Quick Start

#### Windows Development Setup
For Windows developers, use the included setup script:
```cmd
# Clone repository
git clone <repository-url>
cd slippi_stats

# Run the Windows setup script
start_dev_server.bat
```

The `start_dev_server.bat` script automatically:
- Creates a Python virtual environment
- Installs all dependencies from requirements.txt
- Sets up Flask development environment variables
- Initializes the database
- Starts the development server at http://127.0.0.1:5000

#### Manual Setup (All Platforms)
```bash
# Clone repository
git clone <repository-url>
cd slippi_stats

# Run development server
start_dev.bat
```

### Configuration

#### Development
For development, the application uses sensible defaults. No additional configuration required.

#### Production
Set environment variables for production deployment:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export SLIPPI_REGISTRATION_SECRET=your-registration-secret
export DATABASE_PATH=/path/to/production.db
```

### Development Workflow
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines, pull request process, and coding standards.

## Development Guidelines

### Adding New Functionality

#### 1. Database Operations
```python
# Add to database.py with table-specific naming
def get_games_by_stage(stage_id):
    """Get all games played on specific stage."""
    pass

def create_tournament_record(tournament_data):
    """Insert new tournament record."""  
    pass
```

#### 2. Business Logic
```python
# Add to services.py with descriptive naming
def calculate_tournament_standings(tournament_id):
    """Calculate current tournament standings."""
    pass

def process_matchup_analysis(player1, player2):
    """Analyze head-to-head matchup data."""
    pass
```

#### 3. Web Routes
```python
# Add to routes/web_routes.py with layout prefix
@app.route('/tournaments')
def web_simple_tournaments():           # Uses simple.html
    data = services.get_tournaments_data()
    return render_template('pages/tournaments.html', **data)

@app.route('/tournament/<id>')  
def web_tournament_bracket(id):         # Uses tournament.html layout
    data = services.get_tournament_bracket(id)
    return render_template('pages/tournament_bracket.html', **data)
```

#### 4. API Routes  
```python
# Add to routes/api_routes.py with api_ prefix
@app.route('/api/tournaments/<id>/standings')
def api_tournament_standings(id):
    standings = services.calculate_tournament_standings(id)
    return jsonify(standings)
```

### Error Handling Strategy

#### Database Layer
```python
# Return None/empty or raise on actual errors
def get_games_for_player(player_code):
    try:
        # database operation
        return games or []  # Return empty list if no games
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise  # Re-raise actual database errors
```

#### Services Layer  
```python
# Transform data, raise business exceptions
def get_player_statistics(player_code):
    games = database.get_games_for_player(player_code)
    if not games:
        raise PlayerNotFoundError(f"Player {player_code} not found")
    return calculate_player_stats(games)
```

#### Routes Layer
```python
# Handle business exceptions, return appropriate HTTP responses
@app.route('/api/player/<code>/stats')
def api_player_stats(code):
    try:
        stats = services.get_player_statistics(code)
        return jsonify(stats)
    except PlayerNotFoundError:
        return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

## File Structure Reference

### Templates Directory (`templates/`)
**Purpose**: Jinja2 templates using inheritance pattern for maintainable HTML

- **`base.html`**: Foundation template with navigation, footer, and core assets
- **`layouts/`**: Intermediate templates that extend base and add layout-specific features
- **`pages/`**: Final page templates with specific content

### Static Directory (`static/`)
**Purpose**: Client-side assets organized by type and function

**CSS/JavaScript Structure**: Modular organization with base → components → pages pattern

## Contributing

### Code Style
- **Backend**: Follow PEP 8 for Python code
- **Module Structure**: Follow the defined import hierarchy and naming conventions
- **Static Frontend Files**: Use consistent indentation and modern JavaScript practices
- **Templates**: Maintain Jinja2 template inheritance patterns

### Testing
- Database functions should be testable with in-memory SQLite
- Service functions should have comprehensive unit tests
- Frontend components should be modular and independently testable
- API endpoints should have proper error handling and validation

## Roadmap

### Backend Refactoring (In Progress)
- [x] Extract utilities to `utils.py` 
- [ ] Create `services.py` business logic layer
- [ ] Move routes to `routes/web_routes.py` and `routes/api_routes.py`
- [ ] Add comprehensive logging and error handling
- [ ] Optimize database queries and add connection pooling

### Feature Enhancements
- [ ] Advanced matchup analysis
- [ ] Player comparison tools
- [ ] Export functionality for statistics

### Performance Improvements
- [ ] Database query optimization
- [ ] Frontend bundle optimization
- [ ] Caching layer implementation

## License

[Add your license information here]

## Support

[Add support/contact information here]