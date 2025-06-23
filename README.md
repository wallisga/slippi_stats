# Slippi Stats Server

A comprehensive web application for collecting, storing, and analyzing Super Smash Bros. Melee game data from Slippi replays. Built with Flask and featuring a modular frontend architecture with real-time filtering and detailed player statistics.

## Overview

Slippi Stats Server provides:
- **Player Profile Pages** with comprehensive statistics and performance analysis
- **Advanced Filtering System** for detailed matchup and character analysis  
- **Real-time Data Visualization** with interactive charts and tables
- **RESTful API** for programmatic access to game data
- **Client Registration System** for automated replay collection

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

## Architecture

### Frontend Architecture (Modular Design)
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

### Backend Architecture (Currently Monolithic, Refactoring in Progress)
```
├── app.py              # Main Flask application (monolithic, being refactored)
├── config.py           # Centralized configuration management
├── database.py         # Database operations and connection management
└── [Future modules]    # Planned modular refactoring
    ├── services/       # Business logic layer
    ├── routes/         # Route handlers
    └── utils/          # Shared utilities
```

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

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Run development server
python app.py
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

## Development

### Frontend Development
The frontend uses a **component-based architecture**:

1. **Base Template** (`base.html`): Core HTML structure, navigation, Bootstrap CSS/JS
2. **Layout Templates**: Add layout-specific features (player search, specialized navigation)
3. **Page Templates**: Implement specific page content and functionality
4. **JavaScript Components**: Reusable functionality (character icons, search, player titles)

### Adding New Pages
1. Create page template in `templates/pages/`
2. Choose appropriate layout in `templates/layouts/`  
3. Add page-specific CSS in `static/css/pages/`
4. Add page-specific JavaScript in `static/js/pages/`
5. Create route handler in `app.py`

### Database Operations
All database operations are centralized in `database.py`:
- Use `get_db_connection()` for direct database access
- Existing functions: `get_player_games()`, `get_top_players()`, etc.
- Follow existing patterns for new database functions

## File Structure Reference

### Templates Directory (`templates/`)
**Purpose**: Jinja2 templates using inheritance pattern for maintainable HTML

- **`base.html`**: Foundation template with navigation, footer, and core assets
- **`layouts/`**: Intermediate templates that extend base and add layout-specific features
  - `simple.html`: Minimal layout for basic pages (homepage, error pages)
  - `player.html`: Enhanced layout with player search and navigation
  - `error.html`: Specialized layout for error handling
- **`pages/`**: Final page templates with specific content
  - Extend layout templates, not base directly
  - Contain page-specific content blocks
  - Include data preparation and presentation logic

### Static Directory (`static/`)
**Purpose**: Client-side assets organized by type and function

**CSS Structure:**
- **`base.css`**: Global styles, CSS variables, utility classes
- **`components/`**: Reusable component styles (cards, tables, player elements)
- **`pages/`**: Page-specific styles that don't belong in components

**JavaScript Structure:**
- **`base.js`**: Global utilities and initialization
- **`components/`**: Reusable functionality modules
  - `player_title.js`: Dynamic player header component
  - `character_icons.js`: Character image management
  - `search.js`: Player search functionality
- **`pages/`**: Page-specific JavaScript for individual pages

## Contributing

### Code Style
- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Use consistent indentation and modern JavaScript practices
- **Templates**: Maintain Jinja2 template inheritance patterns
- **CSS**: Follow BEM methodology for component styles

### Testing
- Database functions should be testable with in-memory SQLite
- Frontend components should be modular and independently testable
- API endpoints should have proper error handling and validation

## Roadmap

### Backend Refactoring (In Progress)
- [ ] Move routes to dedicated modules
- [ ] Extract business logic to service layer
- [ ] Create proper error handling middleware
- [ ] Add comprehensive logging system

### Feature Enhancements
- [ ] Tournament bracket visualization
- [ ] Advanced matchup analysis
- [ ] Player comparison tools
- [ ] Export functionality for statistics

### Performance Improvements
- [ ] Database query optimization
- [ ] Frontend bundle optimization
- [ ] Caching layer implementation
- [ ] Progressive loading for large datasets

## License

[Add your license information here]

## Support

[Add support/contact information here]