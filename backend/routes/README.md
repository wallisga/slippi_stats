# Slippi Stats Server

A comprehensive web application for collecting, storing, and analyzing Super Smash Bros. Melee game data from Slippi replays. Built with Flask and featuring a component-based frontend with real-time filtering and detailed player statistics.

## Overview

Slippi Stats Server provides:
- **Player Profile Pages** with comprehensive statistics and performance analysis
- **Advanced Filtering System** for detailed matchup and character analysis  
- **Real-time Data Visualization** with interactive charts and tables
- **RESTful API** for programmatic access to game data
- **Client Registration System** for automated replay collection

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite 3 (included with Python)
- Modern web browser with JavaScript enabled
- Git (for development)

### Windows Development Setup
```cmd
# Clone repository
git clone <repository-url>
cd slippi_stats

# Run the Windows setup script
start_dev.bat
```

The development server will be available at: http://127.0.0.1:5000

### Manual Setup (All Platforms)
```bash
# Clone repository
git clone <repository-url>
cd slippi_stats

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

## Project Structure

```
slippi_stats/
├── README.md                    # This file - project overview
├── requirements.txt             # Python dependencies
├── start_dev.bat               # Windows development script
├── app.py                      # Flask application entry point (lightweight)
├── backend/                    # Backend modules
│   ├── README.md              # Backend architecture details
│   ├── config.py              # Configuration management
│   ├── database.py            # Data access layer with external SQL
│   ├── sql_manager.py         # Dynamic SQL file management
│   ├── sql/                   # External SQL files organized by category
│   │   ├── schema/            # Database schema and indexes
│   │   ├── games/             # Game-related queries
│   │   ├── clients/           # Client management queries
│   │   ├── api_keys/          # Authentication queries
│   │   ├── files/             # File storage queries
│   │   └── stats/             # Statistics and reporting queries
│   ├── routes/                # Flask route blueprints
│   │   ├── README.md          # Routes architecture details
│   │   ├── __init__.py        # Blueprint registration
│   │   ├── web_routes.py      # HTML page routes
│   │   ├── api_routes.py      # JSON API routes
│   │   ├── static_routes.py   # File serving routes
│   │   └── error_handlers.py  # HTTP error handlers
│   ├── web_service.py         # Web page business logic
│   ├── api_service.py         # API business logic
│   └── utils.py               # Shared utilities
└── frontend/                  # Component-based frontend
    ├── README.md              # Frontend architecture details
    ├── base.html              # Foundation template
    ├── base.css               # Global styles
    ├── base.js                # Global utilities
    ├── components/            # Self-contained UI components
    ├── layouts/               # Component orchestration
    └── pages/                 # Page-specific content
```

## Architecture

This project follows a **modular architecture** with clear separation of concerns:

### Backend Architecture
- **Lightweight Flask App** with application factory pattern
- **Blueprint-based Routing** organized by functionality (web, api, static, errors)
- **Service-oriented Business Logic** separated into web and API services
- **External SQL Management** with dynamic query discovery and template support
- **Pure Data Access Layer** with no business logic mixing

For detailed backend architecture, see [backend/README.md](backend/README.md)

### Frontend Architecture
- **Component-based Design** with self-contained packages
- **Template Inheritance** following base → layout → page pattern
- **Asset Management** where components own their CSS/JS
- **Bootstrap Integration** with modern responsive design

For detailed frontend architecture, see [frontend/README.md](frontend/README.md)

### Routes Architecture
- **Blueprint Organization** separating web pages, API endpoints, and static files
- **Thin Route Handlers** with business logic delegated to service layers
- **Authentication & Rate Limiting** implemented as decorators
- **Comprehensive Error Handling** with user-friendly error pages

For detailed routes architecture, see [backend/routes/README.md](backend/routes/README.md)

## Features

### Player Analytics
- **Basic Profiles**: Win rates, character usage, recent games, performance highlights
- **Detailed Analysis**: Advanced filtering by character, opponent, and matchup
- **Performance Trends**: Time-series charts showing improvement over time
- **Character Statistics**: Win rates and usage patterns for each character
- **Rival Detection**: Identifies frequent opponents and challenging matchups

### Data Management
- **Automated Collection**: Client applications upload replay data automatically
- **File Upload System**: Secure upload and storage of .slp replay files
- **API Authentication**: Secure API key system for client access
- **Flexible Storage**: SQLite database with external SQL file management
- **Data Validation**: Comprehensive validation and error handling

### User Experience
- **Responsive Design**: Bootstrap-based UI that works on all devices
- **Character Icons**: Visual character representations throughout the interface
- **Interactive Charts**: Chart.js powered visualizations with drill-down capabilities
- **Smart Search**: Flexible player search with case-insensitive matching
- **Error Handling**: User-friendly error pages with helpful navigation

## API Documentation

### Player Endpoints
- `GET /api/player/{code}/stats` - Basic player statistics
- `GET /api/player/{code}/games` - Paginated game history
- `POST /api/player/{code}/detailed` - Advanced filtering and analysis

### Data Endpoints  
- `POST /api/games/upload` - Upload game data (supports legacy and combined formats)
- `POST /api/files/upload` - Upload replay files with metadata
- `GET /api/files` - List uploaded files
- `GET /api/files/{id}` - Get file details
- `GET /api/stats` - Server statistics and health
- `POST /api/clients/register` - Client registration

### Authentication
All data modification endpoints require API key authentication via `X-API-Key` header.

## Configuration

### Development
For development, the application uses sensible defaults. No additional configuration required.

### Production
Set environment variables for production deployment:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export SLIPPI_REGISTRATION_SECRET=your-registration-secret
export DATABASE_PATH=/path/to/production.db
```

## Database Schema
- **clients**: Registered client applications with metadata
- **games**: Individual game records with JSON player data  
- **api_keys**: Authentication tokens for API access
- **files**: Uploaded replay files with metadata and hash tracking

All SQL queries are managed through external .sql files for better maintainability and version control.

## Development Status

### ✅ Completed
- **Backend Architecture**: Clean service-oriented design with separation of concerns
- **Database Layer**: Pure data access with external SQL file management
- **Routes Architecture**: Blueprint-based organization with thin route handlers
- **Business Logic**: Separated into web and API service layers
- **SQL Management**: Dynamic discovery and template support for external SQL files
- **File Upload System**: Secure upload and storage with deduplication
- **Configuration Management**: Centralized with environment variable support
- **Error Handling**: Comprehensive validation and user feedback

### 🔄 In Progress
- **Frontend Component System**: Migrating to component-based architecture
- **Performance Optimization**: Database query optimization and caching

### 📋 Planned
- **Advanced Analytics**: Enhanced matchup analysis and player comparison tools
- **Export Features**: Statistics export and tournament bracket system
- **Admin Interface**: Web-based administration panel
- **Database Migration System**: Versioned schema changes with rollback capability

## Contributing

### Development Guidelines
- **Backend**: Follow the established service layer pattern and module import hierarchy
- **Routes**: Use blueprint organization with thin handlers delegating to services
- **SQL**: Add new queries as external .sql files in appropriate categories
- **Frontend**: Use the component-based architecture with self-contained packages
- **Code Style**: Follow PEP 8 for Python, component patterns for frontend
- **Testing**: Database functions should be testable with in-memory SQLite

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Set up development environment using `start_dev.bat` or manual setup
4. Make your changes following the architecture patterns
5. Test your changes thoroughly
6. Submit a pull request

### Architecture Documentation
- For backend development details: [backend/README.md](backend/README.md)
- For routes development details: [backend/routes/README.md](backend/routes/README.md)
- For frontend development details: [frontend/README.md](frontend/README.md)

### Adding New Features

#### New Web Page
1. Add route to `backend/routes/web_routes.py`
2. Add business logic to `backend/web_service.py`
3. Create template in `frontend/pages/`
4. Add any new SQL queries to appropriate `backend/sql/` category

#### New API Endpoint
1. Add route to `backend/routes/api_routes.py`
2. Add business logic to `backend/api_service.py`
3. Add any new SQL queries to appropriate `backend/sql/` category
4. Update API documentation

#### New Database Queries
1. Create .sql file in appropriate `backend/sql/` category
2. Use the query via `sql_manager.get_query()` in database functions
3. No Python code changes needed - queries are discovered automatically

## License

This project is open source. Please see the LICENSE file for details.

## Support

For issues, feature requests, or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Follow the contributing guidelines for code submissions