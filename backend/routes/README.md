# Routes Architecture

This directory contains Flask route blueprints that handle HTTP requests and responses. Routes follow the **"Routes Delegate"** principle - they are thin controllers that validate input and delegate business logic to service layers.

## Architecture Overview

Routes are organized into focused blueprints with clear responsibilities:

```
backend/routes/
├── __init__.py           # Blueprint registration
├── web_routes.py         # HTML page routes
├── api_routes.py         # JSON API routes  
├── static_routes.py      # File serving routes
└── error_handlers.py     # HTTP error handlers
```

## Core Principle: Routes Delegate

Routes should be **thin controllers** that:
- **✅ Validate input parameters** and request format
- **✅ Delegate to service layers** for business logic
- **✅ Handle authentication and authorization** 
- **✅ Format responses consistently** (HTML templates or JSON)
- **✅ Provide observability** through tracing decorators
- **❌ NOT contain business logic** - delegate to services
- **❌ NOT access database directly** - use service layer
- **❌ NOT process complex data** - use utils via services

## Blueprint Organization

### Web Routes (`web_routes.py`)
**Purpose**: HTML page endpoints for user interface

**Characteristics**:
- Render Jinja2 templates with context data
- Delegate to `web_service.py` for business logic
- Handle user-facing error scenarios gracefully
- Use `@trace_endpoint` for observability

**Example Pattern**:
```python
@web_bp.route('/player/<encoded_player_code>')
@trace_endpoint
def player_profile(encoded_player_code):
    try:
        player_code = decode_player_tag(encoded_player_code)
        context_data = web_service.get_player_profile_context(player_code)
        return render_template('pages/player/player.html', **context_data)
    except Exception as e:
        logger.error(f"Error loading player profile: {str(e)}")
        return render_template('pages/error/error.html'), 500
```

### API Routes (`api_routes.py`)
**Purpose**: JSON API endpoints for programmatic access

**Characteristics**:
- Return structured JSON responses
- Delegate to `api_service.py` for business logic
- Require API key authentication for data modification
- Use `@trace_api_endpoint` for observability
- Handle rate limiting and error responses consistently

**Example Pattern**:
```python
@api_bp.route('/player/<encoded_player_code>/stats')
@trace_api_endpoint
def api_player_stats(encoded_player_code):
    try:
        player_code = decode_player_tag(encoded_player_code)
        stats_data = api_service.get_player_basic_stats(player_code)
        return jsonify({
            'player_code': player_code,
            'stats': stats_data
        })
    except Exception as e:
        logger.error(f"API error for player stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

### Static Routes (`static_routes.py`)
**Purpose**: File serving and download endpoints

**Characteristics**:
- Serve uploaded replay files securely
- Handle file download with proper headers
- Validate file access permissions
- Support range requests for large files

### Error Handlers (`error_handlers.py`)
**Purpose**: Centralized HTTP error response handling

**Characteristics**:
- Consistent error page rendering
- Structured error logging
- User-friendly error messages
- Proper HTTP status codes

## Development Guidelines

### Adding New Routes

#### New Web Page Route
1. **Add route to `web_routes.py`** with descriptive endpoint name
2. **Add business logic to `backend/web_service.py`** following existing patterns
3. **Create page template** in `frontend/pages/` extending appropriate layout
4. **Add SQL queries** to appropriate `backend/sql/` category if needed
5. **Add observability decorators** for tracing and metrics
6. **Add tests**: Service layer contract test + web page rendering test

#### New API Endpoint Route
1. **Add route to `api_routes.py`** with `@trace_api_endpoint` decorator
2. **Add business logic to `backend/api_service.py`** with `@trace_function` decorator
3. **Add SQL queries** to appropriate `backend/sql/` category if needed
4. **Add authentication** if endpoint modifies data (`@require_api_key`)
5. **Update API documentation** in main README.md
6. **Add tests**: Service layer contract test + API endpoint test

### Route Handler Patterns

#### Input Validation
```python
@web_bp.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    # Validate and decode parameters
    try:
        player_code = decode_player_tag(encoded_player_code)
    except ValueError:
        abort(400, "Invalid player code format")
    
    # Get optional parameters with defaults
    character = request.args.get('character', 'all')
    limit = int(request.args.get('limit', '50'))
    
    # Delegate to service layer
    context_data = web_service.get_detailed_player_analysis(
        player_code, character, limit
    )
    return render_template('pages/player_detailed/player_detailed.html', **context_data)
```

#### Error Handling
```python
@api_bp.route('/games/upload', methods=['POST'])
@require_api_key
@trace_api_endpoint
def upload_games(client_id):
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        games_data = request.get_json()
        if not isinstance(games_data, list):
            return jsonify({'error': 'Games data must be a list'}), 400
        
        # Delegate to service layer
        result = api_service.upload_games_for_client(client_id, games_data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Error uploading games for client {client_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
```

#### Authentication Decorators
```python
@api_bp.route('/protected-endpoint')
@require_api_key
@trace_api_endpoint
def protected_endpoint(client_id):
    # client_id is automatically provided by @require_api_key decorator
    result = api_service.process_authenticated_request(client_id)
    return jsonify(result)
```

### Observability Integration

All routes should include appropriate observability:

```python
from backend.observability import trace_endpoint, trace_api_endpoint

# Web routes
@trace_endpoint
def web_handler():
    pass

# API routes  
@trace_api_endpoint
def api_handler():
    pass
```

## Testing Strategy

### Route Testing
Routes are tested via HTTP requests using Flask test client:

```python
def test_player_profile_route(client):
    """Test player profile page renders correctly"""
    response = client.get('/player/TEST%23123')
    assert response.status_code == 200
    assert b'Player Profile' in response.data

def test_api_player_stats(client):
    """Test API player stats endpoint"""
    response = client.get('/api/player/TEST%23123/stats')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'player_code' in data
    assert 'stats' in data
```

## Import Rules

Routes can import:
- ✅ **Service modules**: `web_service`, `api_service`
- ✅ **Utilities**: `utils` functions for common operations
- ✅ **Configuration**: `config` for application settings
- ✅ **Flask components**: `render_template`, `jsonify`, `abort`, etc.
- ✅ **Observability**: Tracing decorators and logging

Routes should NOT import:
- ❌ **Database directly**: Use service layer instead
- ❌ **SQL manager**: Database access through services only
- ❌ **Other route modules**: Keep blueprints independent

## Blueprint Registration

All blueprints are registered in `__init__.py`:

```python
from .web_routes import web_bp
from .api_routes import api_bp
from .static_routes import static_bp
from .error_handlers import register_error_handlers

def register_blueprints(app):
    """Register all blueprints with the Flask application."""
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(static_bp)
    register_error_handlers(app)
```

## Architecture Documentation

For comprehensive architectural information, see:
- **High-level overview**: [ARCHITECTURE.md](../../ARCHITECTURE.md)
- **Backend development**: [backend/README.md](../README.md)
- **SQL query management**: [backend/sql/README.md](../sql/README.md)
- **Frontend architecture**: [frontend/README.md](../../frontend/README.md)
- **Component development**: [frontend/components/README.md](../../frontend/components/README.md)
- **Layout development**: [frontend/layouts/README.md](../../frontend/layouts/README.md)
- **Page development**: [frontend/pages/README.md](../../frontend/pages/README.md)
- **Testing guidelines**: [tests/README.md](../../tests/README.md)
- **Contributing guide**: [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

This project is open source. Please see the LICENSE file for details.