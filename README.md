# Slippi Stats Server

A comprehensive web application for collecting, storing, and analyzing Super Smash Bros. Melee game data from Slippi replays. Built with Flask and featuring a component-based frontend with real-time filtering and detailed player statistics.

## Overview

Slippi Stats Server provides:
- **Player Profile Pages** with comprehensive statistics and performance analysis
- **Advanced Filtering System** for detailed matchup and character analysis  
- **Real-time Data Visualization** with interactive charts and tables
- **RESTful API** for programmatic access to game data
- **Client Registration System** for automated replay collection
- **Enterprise Observability** with OpenTelemetry for monitoring and debugging

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite 3 (included with Python)
- Modern web browser with JavaScript enabled
- Git (for development)
- Docker (optional, for observability stack)

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

### Observability Setup (Optional)
```bash
# Start local observability stack with Docker
docker-compose up -d

# Access observability tools:
# - Jaeger UI: http://localhost:16686 (distributed tracing)
# - Grafana: http://localhost:3000 (dashboards, admin/admin)
# - Prometheus: http://localhost:9090 (metrics)
```

## Project Structure

```
slippi_stats/
├── README.md                    # This file - project overview
├── requirements.txt             # Python dependencies with observability
├── start_dev.bat               # Windows development script
├── docker-compose.yml          # Local observability stack
├── app.py                      # Flask application entry point (lightweight)
├── run_tests.bat               # Enhanced test runner with coverage
├── backend/                    # Backend modules (service-oriented architecture)
│   ├── README.md              # Backend architecture details
│   ├── config.py              # Configuration management
│   ├── observability.py       # OpenTelemetry instrumentation
│   ├── database.py            # Data access layer with external SQL
│   ├── sql_manager.py         # Dynamic SQL file management
│   ├── sql/                   # External SQL files organized by category
│   │   ├── README.md          # SQL architecture and query management
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
├── frontend/                  # Component-based frontend
│   ├── README.md              # Frontend architecture details
│   ├── base.html              # Foundation template
│   ├── base.css               # Global styles
│   ├── base.js                # Global utilities
│   ├── components/            # Self-contained UI components
│   │   └── README.md          # Component development guide
│   ├── layouts/               # Component orchestration
│   │   └── README.md          # Layout architecture guide
│   └── pages/                 # Page-specific content
│       └── README.md          # Page development guide
├── tests/                     # Comprehensive testing framework
│   ├── README.md              # Testing guide and architecture
│   ├── conftest.py            # Test configuration and fixtures
│   ├── pytest.ini            # Pytest configuration
│   ├── test_service_layer.py  # ⚡ Business logic contracts (ENHANCED)
│   ├── test_database_simple.py # 🔄 Database integration tests
│   ├── test_api_endpoints.py  # 🔄 HTTP endpoints (EXPANDED)
│   ├── test_web_pages.py      # 🔄 Web page rendering tests
│   ├── test_utils_functions.py # ⚡ NEW: Utils function testing
│   ├── test_upload_pipeline.py # 🔄 NEW: Upload workflow integration
│   └── test_error_scenarios.py # ⚡ NEW: Error handling & edge cases
└── observability/             # Observability configuration
    ├── otel-collector-config.yaml  # OpenTelemetry collector setup
    ├── prometheus.yml          # Metrics collection configuration
    └── grafana/               # Dashboard definitions
```

## Architecture

This project follows a **modular architecture** with clear separation of concerns and comprehensive observability:

### Backend Architecture
- **Service-Oriented Design**: Clean separation between web and API business logic
- **External SQL Management**: SQL queries stored as external files with dynamic discovery
- **Blueprint-Based Routing**: Organized route handlers with thin controllers
- **Strict Import Hierarchy**: Enforced module dependencies prevent circular imports
- **Comprehensive Testing**: Architecture-aligned testing with 75% coverage target

### Frontend Architecture
- **Component-Based System**: Self-contained UI components with clear interfaces
- **Layout Orchestration**: Flexible layout system for component composition
- **Progressive Enhancement**: Works without JavaScript, enhanced with it
- **Bootstrap Foundation**: Responsive design with custom component styling

### Observability Architecture
- **Distributed Tracing**: OpenTelemetry instrumentation across all layers
- **Business Metrics**: Custom metrics for games processed, API usage, performance
- **Real-time Monitoring**: Grafana dashboards with automated alerting
- **Development-Friendly**: Local observability stack with Docker

## Testing

The project includes a comprehensive testing framework designed for confident refactoring:

### Quick Start
```bash
# Run all tests
run_tests.bat

# Run specific test categories  
run_tests.bat quick        # Fast service layer tests
run_tests.bat api          # API endpoint tests
run_tests.bat db           # Database integration tests
run_tests.bat web          # Web page tests
run_tests.bat utils        # Utils function tests
run_tests.bat upload       # Upload pipeline tests
run_tests.bat coverage     # Generate coverage report
```

### Test Categories & Coverage
- **Service Layer Tests** (`tests/test_service_layer.py`) - Business logic contracts
- **Utils Function Tests** (`tests/test_utils_functions.py`) - Data processing utilities
- **Database Tests** (`tests/test_database_simple.py`) - SQL files and database operations  
- **API Tests** (`tests/test_api_endpoints.py`) - HTTP endpoints and responses
- **Upload Pipeline Tests** (`tests/test_upload_pipeline.py`) - Complete upload workflows
- **Error Scenarios Tests** (`tests/test_error_scenarios.py`) - Edge cases and error handling
- **Web Tests** (`tests/test_web_pages.py`) - Page rendering and navigation

### Testing Philosophy
The testing framework enables confident refactoring by:
1. **Architecture Alignment**: Tests respect the service-oriented module hierarchy
2. **Contract Focus**: Tests verify what functions return, not how they work
3. **Fast Feedback**: Service layer tests run in <1 second for rapid development
4. **Integration Coverage**: Database and API tests ensure components work together
5. **Error Resilience**: Comprehensive error scenario testing

### Coverage Goals
- **Current**: 51% overall coverage
- **Target**: 75% overall coverage
- **Priority Areas**: 
  - `web_service.py`: 21% → 60%
  - `api_service.py`: 50% → 65%
  - `utils.py`: 36% → 55%
  - `api_routes.py`: 40% → 70%

### Adding Tests
See [tests/README.md](tests/README.md) for detailed guidance on:
- When to add tests to each category
- Test templates and examples
- Best practices and troubleshooting
- Integration with development workflow

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

### Observability & Monitoring
- **Distributed Tracing**: Request flow visibility across all application layers
- **Business Metrics**: Games processed, files uploaded, API usage tracking
- **Performance Monitoring**: Response times, database query performance, error rates
- **Real-time Dashboards**: Grafana dashboards for operational insights
- **Alerting**: Automated alerts for system health and performance issues

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
- **Observability**: OpenTelemetry instrumentation and monitoring stack
- **Testing Framework**: Architecture-aligned testing with multiple categories
- **Frontend Component System**: Component-based architecture with clear separation of concerns

### 🔄 In Progress
- **Test Coverage Improvement**: 51% → 75% coverage target
- **Performance Optimization**: Database query optimization and caching

### 📋 Planned
- **Advanced Analytics**: Enhanced matchup analysis and player comparison tools
- **Export Features**: Statistics export and tournament bracket system
- **Admin Interface**: Web-based administration panel
- **Database Migration System**: Versioned schema changes with rollback capability

### 🎯 Recent Achievements
- **Architecture Refactoring**: Successfully migrated from monolithic to service-oriented architecture
- **SQL Externalization**: All database queries moved to organized external files
- **Component System**: Frontend components now follow "Components Do, Layouts Share, Pages Orchestrate" principle
- **Testing Infrastructure**: Comprehensive test categories aligned with architectural boundaries
- **Documentation**: Complete documentation coverage for all architectural layers

## Contributing

### Development Guidelines
- **Backend**: Follow the established service layer pattern and module import hierarchy
- **Routes**: Use blueprint organization with thin handlers delegating to services
- **SQL**: Add new queries as external .sql files in appropriate categories
- **Frontend**: Use the component-based architecture with self-contained packages
- **Testing**: Add tests that align with the architectural boundaries
- **Code Style**: Follow PEP 8 for Python, component patterns for frontend
- **Observability**: Use tracing decorators and custom metrics for new features

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Set up development environment using `start_dev.bat` or manual setup
4. Optional: Start observability stack with `docker-compose up -d`
5. Make your changes following the architecture patterns
6. Test your changes thoroughly using `run_tests.bat`
7. Submit a pull request

### Architecture Documentation
- For backend development details: [backend/README.md](backend/README.md)
- For routes development details: [backend/routes/README.md](backend/routes/README.md)
- For SQL query management: [backend/sql/README.md](backend/sql/README.md)
- For frontend development details: [frontend/README.md](frontend/README.md)
- For component development: [frontend/components/README.md](frontend/components/README.md)
- For layout development: [frontend/layouts/README.md](frontend/layouts/README.md)
- For page development: [frontend/pages/README.md](frontend/pages/README.md)
- For testing guidelines: [tests/README.md](tests/README.md)

### Adding New Features

#### New Web Page
1. Add route to `backend/routes/web_routes.py`
2. Add business logic to `backend/web_service.py`
3. Create template in `frontend/pages/`
4. Add any new SQL queries to appropriate `backend/sql/` category
5. Add observability decorators for tracing and metrics
6. **Add tests**: Service layer contract test + web page rendering test

#### New API Endpoint
1. Add route to `backend/routes/api_routes.py` with `@trace_api_endpoint`
2. Add business logic to `backend/api_service.py` with `@trace_function`
3. Add any new SQL queries to appropriate `backend/sql/` category
4. Add metrics for business events and performance tracking
5. Update API documentation
6. **Add tests**: Service layer contract test + API endpoint test

#### New Database Queries
1. Create .sql file in appropriate `backend/sql/` category
2. Use the query via `sql_manager.get_query()` in database functions
3. Add `@trace_database_operation` decorator for performance monitoring
4. No Python code changes needed - queries are discovered automatically
5. **Add tests**: Database integration test for new query

#### New Frontend Components
1. Create component package in `frontend/components/`
2. Follow the component development guide
3. Add to layouts as needed
4. Test component independence and reusability
5. **Add tests**: Web page test for component integration

#### New Utility Functions
1. Add function to `backend/utils.py`
2. Follow the established patterns for data processing
3. **Add tests**: Utils function test for new functionality

### Test-Driven Development Workflow
1. **Identify the change**: Determine which architectural layer is affected
2. **Add service layer test**: If business logic is involved
3. **Add integration test**: If database, API, or upload functionality is involved
4. **Add utils test**: If data processing utilities are involved
5. **Run quick tests**: `run_tests.bat quick` during development
6. **Run full tests**: `run_tests.bat` before committing
7. **Check coverage**: `run_tests.bat coverage` to ensure coverage goals

### Junior Developer Guidance
The architecture is designed to be approachable for junior developers:

1. **Start with Service Layer**: Business logic is isolated and testable
2. **Use Test Categories**: Clear guidelines on where to add tests
3. **Follow Import Rules**: Strict hierarchy prevents architectural violations
4. **Use Templates**: Provided templates for common development tasks
5. **Quick Feedback**: Fast tests provide immediate validation
6. **Documentation**: Comprehensive guides for each architectural layer

## Configuration

### Development
For development, the application uses sensible defaults. No additional configuration required.

### Production
Set environment variables for production deployment:
- `DATABASE_PATH`: Path to SQLite database file
- `SECRET_KEY`: Flask secret key for session management
- `API_KEY_LENGTH`: Length of generated API keys (default: 32)
- `MAX_UPLOAD_SIZE`: Maximum upload size in bytes
- `ENABLE_OBSERVABILITY`: Enable OpenTelemetry tracing (default: True)

### Observability
Configure observability stack:
- `JAEGER_ENDPOINT`: Jaeger collector endpoint
- `PROMETHEUS_ENDPOINT`: Prometheus metrics endpoint
- `GRAFANA_ENDPOINT`: Grafana dashboard endpoint

## License

This project is open source. Please see the LICENSE file for details.

## Support

For issues, feature requests, or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Follow the contributing guidelines for code submissions

### Development Support
- **Architecture Questions**: See module-specific README files
- **Testing Questions**: See [tests/README.md](tests/README.md)
- **Component Development**: See [frontend/components/README.md](frontend/components/README.md)
- **SQL Development**: See [backend/sql/README.md](backend/sql/README.md)