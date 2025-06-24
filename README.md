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
├── app.py                      # Flask application entry point
├── config.py                   # Configuration management
├── database.py                 # Data access layer
├── web_service.py              # Web page business logic
├── api_service.py              # API business logic
├── utils.py                    # Shared utilities
├── backend/                    # Backend documentation and future expansion
│   └── README.md              # Backend architecture details
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
- **Flask Application** with service-oriented design
- **Component-based Business Logic** separated into web and API services
- **Pure Data Access Layer** with no business logic mixing
- **Shared Utilities** for common functionality across services

For detailed backend architecture, see [backend/README.md](backend/README.md)

### Frontend Architecture
- **Component-based Design** with self-contained packages
- **Template Inheritance** following base → layout → page pattern
- **Asset Management** where components own their CSS/JS
- **Bootstrap Integration** with modern responsive design

For detailed frontend architecture, see [frontend/README.md](frontend/README.md)

## Features

### Player Analytics
- **Basic Profiles**: Win rates, character usage, recent games, performance highlights
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

## Development Status

### ✅ Completed
- **Backend Architecture**: Clean service-oriented design with separation of concerns
- **Database Layer**: Pure data access with comprehensive CRUD operations
- **Business Logic**: Separated into web and API service layers
- **Configuration Management**: Centralized with environment variable support
- **Error Handling**: Comprehensive validation and user feedback

### 🔄 In Progress
- **Frontend Component System**: Migrating to component-based architecture
- **Documentation Restructuring**: Decoupling architecture documentation

### 📋 Planned
- **Advanced Analytics**: Enhanced matchup analysis and player comparison tools
- **Performance Optimization**: Database query optimization and caching
- **Export Features**: Statistics export and tournament bracket system

## Contributing

### Development Guidelines
- **Backend**: Follow the established service layer pattern and module import hierarchy
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
- For frontend development details: [frontend/README.md](frontend/README.md)

## License

This project is open source. Please see the LICENSE file for details.

## Support

For issues, feature requests, or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Follow the contributing guidelines for code submissions