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
├── backend/                    # Backend modules
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
└── observability/             # Observability configuration
    ├── otel-collector-config.yaml  # OpenTelemetry collector setup
    ├── prometheus.yml          # Metrics collection configuration
    └── grafana/               # Dashboard definitions
```

## Architecture

This project follows a **modular architecture** with clear separation of concerns and comprehensive observability:

### Backend Architecture
- **Lightweight Flask App** with application factory pattern
- **Blueprint-based Routing** organized by functionality (web, api, static, errors)
- **Service-oriented Business Logic** separated into web and API services
- **External SQL Management** with dynamic query discovery and template support
- **Pure Data Access Layer** with no business logic mixing
- **OpenTelemetry Integration** for distributed tracing and metrics

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

### SQL Management
- **External SQL Files** organized by functionality and automatically discovered
- **Template Support** for dynamic query generation with variable substitution
- **Category Organization** for logical grouping of related queries
- **Version Control** of SQL changes alongside application code

For detailed SQL architecture, see [backend/sql/README.md](backend/sql/README.md)

### Component System
- **Self-contained Packages** with templates, styles, and behavior
- **Auto-initialization** for immediate usability when included
- **Simple APIs** through macros and JavaScript methods
- **BEM CSS Methodology** for consistent styling

For component development, see [frontend/components/README.md](frontend/components/README.md)

### Layout System
- **Component Orchestration** importing and configuring components for pages
- **Template Composition** combining components into reusable patterns
- **Configuration Management** for flexible navbar and component setup

For layout development, see [frontend/layouts/README.md](frontend/layouts/README.md)

### Page System
- **Business Logic Coordination** handling API calls and component interaction
- **Error Handling Strategy** with user feedback and graceful degradation
- **Performance Optimization** with lazy loading and memory management

For page development, see [frontend/pages/README.md](frontend/pages/README.md)

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

## Testing

The project includes a comprehensive testing framework for confident development and refactoring.

### Quick Start
```bash
# Run all tests
run_tests.bat

# Run specific test categories  
run_tests.bat quick        # Fast service layer tests
run_tests.bat api          # API endpoint tests
run_tests.bat db           # Database integration tests
run_tests.bat web          # Web page tests
run_tests.bat coverage     # Generate coverage report
```

### Test Categories
- **Service Layer Tests** (`tests/test_service_layer.py`) - Business logic contracts
- **Database Tests** (`tests/test_database_simple.py`) - SQL files and database operations  
- **API Tests** (`tests/test_api_endpoints.py`) - HTTP endpoints and responses
- **Web Tests** (`tests/test_web_pages.py`) - Page rendering and navigation

### Adding Tests
See [tests/README.md](tests/README.md) for detailed guidance on:
- When to add tests to each category
- Test templates and examples
- Best practices and troubleshooting
- Integration with development workflow

### Test-Driven Development
The testing framework enables confident refactoring:
1. Tests pass = changes are safe
2. Tests fail = contracts broken, fix needed  
3. Add tests before new features
4. Use `run_tests.bat quick` during development

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

# Observability configuration
export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4317
export OTEL_SERVICE_NAME=slippi-stats-server
export OTEL_ENVIRONMENT=production
```

### Observability Configuration
```bash
# Development with console output
export OTEL_SERVICE_NAME=slippi-stats-server
export OTEL_ENVIRONMENT=development

# Production with OTLP collector
export OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
export OTEL_RESOURCE_ATTRIBUTES=service.name=slippi-stats,environment=prod
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
- **Frontend Component System**: Self-contained packages with clear APIs
- **Layout System**: Component orchestration and template composition
- **Page System**: Business logic coordination and error handling

### 🔄 In Progress
- **Observability Implementation**: OpenTelemetry integration for comprehensive monitoring
- **Performance Optimization**: Database query optimization and caching
- **Advanced Analytics**: Enhanced matchup analysis and player comparison tools

### 📋 Planned
- **Observability Rollout**: 
  - Phase 1: Core instrumentation and console output
  - Phase 2: Local development stack with Jaeger and Prometheus
  - Phase 3: Production deployment with OTLP collector
  - Phase 4: Advanced dashboards, alerts, and SLA monitoring
- **Export Features**: Statistics export and tournament bracket system
- **Admin Interface**: Web-based administration panel with observability insights
- **Database Migration System**: Versioned schema changes with rollback capability
- **Advanced Monitoring**: 
  - Business KPI tracking and alerting
  - Performance regression detection
  - Capacity planning and resource optimization
  - Security monitoring and threat detection

## Contributing

### Development Guidelines
- **Backend**: Follow the established service layer pattern and module import hierarchy
- **Routes**: Use blueprint organization with thin handlers delegating to services
- **SQL**: Add new queries as external .sql files in appropriate categories
- **Frontend**: Use the component-based architecture with self-contained packages
- **Observability**: Add tracing decorators to new functions and metrics for business events
- **Code Style**: Follow PEP 8 for Python, component patterns for frontend
- **Testing**: Database functions should be testable with in-memory SQLite

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Set up development environment using `start_dev.bat` or manual setup
4. Optional: Start observability stack with `docker-compose up -d`
5. Make your changes following the architecture patterns
6. Test your changes thoroughly
7. Submit a pull request

### Architecture Documentation
- For backend development details: [backend/README.md](backend/README.md)
- For routes development details: [backend/routes/README.md](backend/routes/README.md)
- For SQL query management: [backend/sql/README.md](backend/sql/README.md)
- For frontend development details: [frontend/README.md](frontend/README.md)
- For component development: [frontend/components/README.md](frontend/components/README.md)
- For layout development: [frontend/layouts/README.md](frontend/layouts/README.md)
- For page development: [frontend/pages/README.md](frontend/pages/README.md)

### Adding New Features

#### New Web Page
1. Add route to `backend/routes/web_routes.py`
2. Add business logic to `backend/web_service.py`
3. Create template in `frontend/pages/`
4. Add any new SQL queries to appropriate `backend/sql/` category
5. Add observability decorators for tracing and metrics

#### New API Endpoint
1. Add route to `backend/routes/api_routes.py` with `@trace_api_endpoint`
2. Add business logic to `backend/api_service.py` with `@trace_function`
3. Add any new SQL queries to appropriate `backend/sql/` category
4. Add metrics for business events and performance tracking
5. Update API documentation

#### New Database Queries
1. Create .sql file in appropriate `backend/sql/` category
2. Use the query via `sql_manager.get_query()` in database functions
3. Add `@trace_database_operation` decorator for performance monitoring
4. No Python code changes needed - queries are discovered automatically

#### New Frontend Components
1. Create component package in `frontend/components/`
2. Follow the component development guide
3. Add to layouts as needed
4. Test component independence and reusability

#### Adding Observability
1. Use `@trace_function` for business logic functions
2. Use `@trace_database_operation` for database operations
3. Use `@trace_api_endpoint` for API routes
4. Record custom metrics with `observability.record_*()` methods
5. Add custom spans for complex operations

## License

This project is open source. Please see the LICENSE file for details.

## Support

For issues, feature requests, or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Follow the contributing guidelines for code submissions

## Monitoring and Operations

### Health Checks
- Application health: `GET /api/stats`
- Database connectivity: Automatic via SQLite instrumentation
- File system access: Monitored via file upload metrics

### Performance Monitoring
- Request latency: Tracked automatically via OpenTelemetry
- Database query performance: Monitored per query type
- Business metrics: Games processed, files uploaded, API usage

### Alerting (Planned)
- High error rates (>5% for 5 minutes)
- Slow database queries (>1s p95 for 5 minutes)
- No data uploads (>1 hour without game uploads)
- High memory usage (>80% for 10 minutes)

This comprehensive architecture provides a scalable, maintainable foundation with enterprise-grade observability for monitoring, debugging, and optimizing the application in both development and production environments.