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

### Backend Module Structure (Current State)
```
app.py                 # Entry point & Flask application setup
├── config.py          # Configuration & environment management
├── utils.py           # Shared utilities & business logic helpers
├── database.py        # Pure data access layer (no business logic)
├── web_service.py     # Web-specific business logic & template data
├── api_service.py     # API-specific business logic & JSON responses
└── [FUTURE]
    ├── services.py    # Unified business logic layer [PLANNED]
    └── routes/        # HTTP route handlers [PLANNED]
        ├── web_routes.py  # HTML page routes
        └── api_routes.py  # JSON API endpoints
```

### Current Module Responsibilities

#### **config.py** - Configuration Management ✅ COMPLETE
**Purpose**: Centralized configuration and environment settings

**Contains:**
- Environment variable handling (`get_config()`)
- Application settings and constants
- Logging configuration (`init_logging()`)
- Database paths and connection settings
- Feature flags and limits

**Import Rules**: Cannot import any other app modules
**Status**: Stable, well-structured

#### **utils.py** - Shared Utilities & Business Logic Helpers ✅ COMPLETE
**Purpose**: Helper functions and shared business logic used across multiple modules

**Contains:**
- URL encoding/decoding (`encode_player_tag()`, `decode_player_tag()`)
- Error template data (`get_error_template_data()`)
- **Game Data Processing** (shared between services):
  - `parse_player_data_from_game()` - Parse JSON player data
  - `find_player_in_game_data()` - Find specific player in game
  - `safe_get_player_field()` - Safe field extraction
  - `process_raw_games_for_player()` - Process games for specific player
  - `find_flexible_player_matches()` - Player search with fuzzy matching
  - `extract_player_stats_from_games()` - Extract player rankings
  - `process_recent_games_data()` - Format recent games for display

**Import Rules**: Can only import `config`
**Status**: Complete with comprehensive game processing functions

#### **database.py** - Pure Data Access Layer ✅ COMPLETE  
**Purpose**: Raw database operations ONLY - no business logic

**Contains:**
- Database connection management (`DatabaseManager` class)
- Table-specific CRUD operations
- Raw SQL queries and data retrieval
- Database initialization (`init_db()`)

**Key Functions (Table-Organized):**
- **Games**: `get_games_all()`, `get_games_recent()`, `create_game_record()`
- **Clients**: `get_clients_all()`, `create_client_record()`, `update_clients_info()`
- **API Keys**: `get_api_keys_*()`, `create_api_key_record()`, `validate_api_key()`
- **Statistics**: `get_database_stats()` (simple aggregation only)

**Import Rules**: Can import `config` only
**Status**: Complete refactoring - pure data access, no business logic

#### **web_service.py** - Web Business Logic ✅ COMPLETE
**Purpose**: Business logic for web page rendering and template data preparation

**Contains:**
- Template data preparation (`prepare_homepage_data()`, `prepare_all_players_data()`)
- Player statistics calculation (`calculate_player_stats()`)
- Data access wrappers that combine database + utils processing
- Request handling logic (`process_player_profile_request()`)

**Import Rules**: Can import `database`, `utils`, `config`
**Status**: Complete with clean separation from database layer

#### **api_service.py** - API Business Logic ✅ COMPLETE
**Purpose**: Business logic for JSON API responses and API-specific concerns

**Contains:**
- API data processing (`process_detailed_player_data()`, `process_paginated_player_games()`)
- Advanced filtering logic (`apply_game_filters()`, `calculate_filtered_stats()`)
- Client management (`register_or_update_client()`, `upload_games_for_client()`)
- Request validation and error handling

**Import Rules**: Can import `database`, `utils`, `config`
**Status**: Complete with comprehensive API functionality

#### **app.py** - Flask Application ✅ COMPLETE
**Purpose**: Flask application setup, route definitions, and HTTP handling

**Contains:**
- Flask app configuration and initialization
- Route handlers for both web and API endpoints
- Authentication decorators (`require_api_key`, `rate_limited`)
- Error handlers for all HTTP status codes
- Static file serving

**Import Rules**: Can import all service modules
**Status**: Clean and well-organized with proper service separation

### Data Flow Architecture (Current)

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

### Current Module Import Hierarchy

```
app.py (Flask routes & HTTP handling)        # Top level
    ↓ can import
web_service.py + api_service.py              # Business logic layers
    ↓ can import  
utils.py (shared helpers) + database.py (data access) + config.py  # Foundation
```

**Import Rules (Enforced):**
- ✅ Services can import: `database`, `utils`, `config`
- ✅ Utils can import: `config` only
- ✅ Database can import: `config` only
- ✅ App can import: all modules
- ❌ No circular imports between services
- ❌ Database cannot import services or utils
- ❌ Utils cannot import database or services

## Frontend Architecture (Component-Based Design)

### Component Architecture Philosophy

The frontend follows a **component-based architecture** where:

1. **Components are self-contained packages** - Each component includes its own template, CSS, and JavaScript
2. **Layouts orchestrate components** - Layouts import and compose components as needed
3. **Base template is minimal** - Only includes Bootstrap, base.css, and base.js
4. **Pages focus on content** - Page-specific functionality only, no component imports

### Directory Structure

```
templates/
├── base.html                    # Foundation: Bootstrap + base assets only
├── components/                  # Self-contained component packages
│   ├── search/
│   │   ├── _search.html        # Template
│   │   ├── search.css          # Styles (loaded by template)
│   │   └── search.js           # Behavior (loaded by template)
│   ├── character_icons/
│   │   ├── _character_icons.html
│   │   ├── character_icons.css
│   │   └── character_icons.js
│   ├── player_title/
│   │   ├── _player_title.html
│   │   ├── player_title.css
│   │   └── player_title.js
│   └── game_table/
│       ├── _game_table.html
│       ├── game_table.css
│       └── game_table.js
├── layouts/                     # Component orchestration layer
│   ├── simple.html             # Imports: search, character_icons
│   ├── player.html             # Imports: search, character_icons, player_title
│   └── error.html              # Minimal layout, no components
└── pages/                      # Content layer
    ├── index.html              # Page-specific content only
    ├── players.html            # Page-specific content only
    ├── player_basic.html       # Page-specific content only
    └── player_detailed.html    # Page-specific content only

static/
├── css/
│   ├── base.css               # Global styles only
│   └── pages/                 # Page-specific styles
│       ├── index.css
│       ├── players.css
│       └── player_*.css
├── js/
│   ├── base.js               # Global utilities only
│   └── pages/                # Page-specific JavaScript
│       ├── index.js
│       ├── players.js
│       └── player_*.js
└── icons/                    # Static assets
    └── character/
```

### Component Package Structure

Each component is a **self-contained package** consisting of:

#### Component Template (`_component.html`)
- Contains HTML structure and Jinja2 macros
- Imports its own CSS and JavaScript files
- Provides reusable macros for layouts to use

#### Component CSS (`component.css`)
- Self-contained styling for the component
- Uses BEM methodology for class naming
- Responsive design included

#### Component JavaScript (`component.js`)
- Component behavior and interactivity
- Auto-initialization on page load
- Exposes public API for external use

### Template Inheritance & Component Flow

```
base.html (Bootstrap + base assets)
    ↓ extends
layouts/*.html (imports components)
    ↓ extends  
pages/*.html (page content only)
```

**Component Import Rules:**
- ✅ **base.html** imports: Bootstrap, base.css, base.js ONLY
- ✅ **layouts/** import components via `{% include %}` or `{% from %}`
- ✅ **components/** are self-contained packages
- ❌ **pages/** should NOT import components directly
- ❌ **components/** should NOT import other components

### Layout Responsibilities

#### `base.html` - Foundation Layer
**Purpose**: Minimal foundation shared by all pages
**Imports**: Bootstrap CSS/JS, base.css, base.js ONLY
**Responsibilities:**
- HTML5 document structure
- Bootstrap framework loading
- Basic navigation shell
- Core JavaScript utilities

#### `layouts/simple.html` - Basic Layout
**Purpose**: Standard layout for content pages
**Components**: search, character_icons
**Pages**: index.html, players.html, download.html, how_to.html

#### `layouts/player.html` - Player Layout
**Purpose**: Enhanced layout for player-focused pages  
**Components**: search, character_icons, player_title, game_tables
**Pages**: player_basic.html, player_detailed.html

#### `layouts/error.html` - Error Layout
**Purpose**: Specialized layout for error pages
**Components**: None (minimal)
**Pages**: error_*.html

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
```cmd
# Clone repository
git clone <repository-url>
cd slippi_stats

# Run the Windows setup script
start_dev.bat
```

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

## Development Guidelines

### Component Development

#### Creating New Components
1. **Create component directory**: `templates/components/component_name/`
2. **Create template file**: `_component_name.html` with macros
3. **Create CSS file**: `component_name.css` with component styles
4. **Create JS file**: `component_name.js` with component behavior
5. **Import assets in template**: CSS and JS files loaded by template

#### Component Structure Example
```
templates/components/search/
├── _search.html              # Template with macros
├── search.css               # Component-specific styles  
└── search.js                # Component behavior

# In _search.html:
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/search.css') }}">
<script src="{{ url_for('static', filename='js/components/search.js') }}"></script>

{% macro search_form() %}
  <!-- Component HTML -->
{% endmacro %}
```

#### Layout Integration
```jinja2
<!-- In layouts/simple.html -->
{% include 'components/search/_search.html' %}
{% include 'components/character_icons/_character_icons.html' %}

<!-- Use component macros -->
{{ search.search_form() }}
```

### Backend Integration

#### 1. Database Operations
```python
# Add to database.py with table-specific naming
def get_games_by_stage(stage_id):
    """Get all games played on specific stage."""
    with db_manager.get_connection() as conn:
        # Raw SQL only, no business logic
        return conn.execute("SELECT * FROM games WHERE stage_id = ?", (stage_id,)).fetchall()
```

#### 2. Shared Business Logic
```python
# Add to utils.py for cross-service functionality
def process_stage_statistics(raw_games):
    """Process raw games to extract stage statistics."""
    # Shared data processing logic
    pass
```

#### 3. Service-Specific Logic
```python
# Add to web_service.py for web pages
def prepare_tournament_page_data():
    """Prepare data for tournament page rendering."""
    raw_games = get_games_all()
    return process_tournament_data(raw_games)

# Add to api_service.py for API endpoints  
def process_tournament_api_request(tournament_id, filters):
    """Process tournament API request with filtering."""
    raw_games = get_games_by_tournament(tournament_id)
    return apply_tournament_filters(raw_games, filters)
```

#### 4. Route Handlers
```python
# Add to app.py with clear separation
@app.route('/tournaments')
def web_tournaments():
    data = web_service.prepare_tournament_page_data()
    return render_template('pages/tournaments.html', **data)

@app.route('/api/tournaments/<id>')
def api_tournament_data(id):
    result = api_service.process_tournament_api_request(id, request.json)
    return jsonify(result)
```

## Completed Refactoring Status

### ✅ Phase 1: Configuration & Database (COMPLETE)
- [x] Extract configuration to `config.py`
- [x] Centralize database operations in `database.py`
- [x] Implement proper logging and error handling

### ✅ Phase 2: Services & Utilities (COMPLETE)
- [x] Extract utilities to `utils.py`
- [x] Create `web_service.py` for web-specific business logic
- [x] Create `api_service.py` for API-specific business logic
- [x] Maintain clean separation between services

### ✅ Phase 3: Data Layer Refactoring (COMPLETE)
- [x] Refactor `database.py` to pure data access layer
- [x] Move business logic from database to `utils.py`
- [x] Update services to use new architecture
- [x] Fix all import dependencies and circular references

### 🔄 Phase 4: Component Architecture (IN PROGRESS)
- [ ] Implement component-based frontend architecture
- [ ] Create self-contained component packages
- [ ] Update layouts to orchestrate components
- [ ] Eliminate direct CSS/JS imports in layouts

### Current State: ✅ PRODUCTION READY (Backend)
The backend has a clean, maintainable architecture. The frontend is transitioning to a component-based approach for improved maintainability and reusability.

## Future Enhancements

### Frontend Component System
- [ ] Search component package
- [ ] Character icons component package
- [ ] Game tables component package  
- [ ] Player title component package
- [ ] Statistics cards component package

### Feature Enhancements
- [ ] Advanced matchup analysis
- [ ] Player comparison tools
- [ ] Export functionality for statistics
- [ ] Tournament bracket system

### Performance Improvements
- [ ] Database query optimization
- [ ] Frontend bundle optimization
- [ ] Caching layer implementation
- [ ] Connection pooling

## Contributing

### Code Style
- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Component-based architecture with self-contained packages
- **Module Structure**: Follow the defined import hierarchy and naming conventions
- **Components**: Self-contained template/CSS/JS packages

### Testing
- Database functions should be testable with in-memory SQLite
- Service functions should have comprehensive unit tests
- Utils functions should be independently testable
- Components should be testable in isolation
- API endpoints should have proper error handling and validation