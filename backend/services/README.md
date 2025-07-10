# Service Directory - Backend Services Reference

Quick reference guide to all backend services, their responsibilities, and current status.

## **Service Layer Overview** 🏗️

### **Current Architecture Pattern**
The backend uses a **hybrid service architecture** combining:
- **Monolithic Services**: Legacy pattern for stable, well-defined business logic
- **Domain Services**: New pattern for complex areas requiring schema standardization

### **Import Pattern**
```python
# Standard import pattern for services
from backend.services import function_name

# Domain-specific imports (when needed)
from backend.services.domain_name import specific_function
```

---

## **Monolithic Services** (Legacy Pattern - Stable)

### **`api_service.py` - API Business Logic** ✅
**Purpose**: JSON API responses and API-specific processing

#### **Player Analysis Functions**
- `process_detailed_player_data(player_code, character, opponent, stage, limit, opponent_character)`
  - **Purpose**: Advanced player analysis with comprehensive filtering
  - **Returns**: Detailed stats with character/opponent/stage breakdowns
  - **Usage**: API endpoint for detailed player pages

- `process_player_basic_stats(player_code)`
  - **Purpose**: Basic player statistics for API responses
  - **Returns**: Win/loss record, win rate, total games
  - **Usage**: Simple player stat API endpoints

#### **Filtering & Analysis Functions**
- `apply_game_filters(games, filters)`
  - **Purpose**: Apply character/opponent/stage filters to game lists
  - **Usage**: Filter games by multiple criteria with AND logic
  - **Recently Fixed**: Character data structure access

- `extract_filter_options(games)`
  - **Purpose**: Extract available filter options from game data
  - **Returns**: Lists of characters, opponents, stages for UI dropdowns

- `calculate_filtered_stats(games, filter_options)`
  - **Purpose**: Calculate statistics from filtered game data
  - **Returns**: Win rates and breakdowns for filtered results

#### **Server & Admin Functions**
- `process_server_statistics()`
  - **Purpose**: Server-wide statistics for admin/API endpoints
  - **Returns**: Total clients, games, players, server status

- `validate_api_key(api_key)`
  - **Purpose**: API key validation for authentication
  - **Returns**: Client info if valid, None if invalid

#### **File Management Functions**
- `get_client_files(client_id, limit)`
  - **Purpose**: Retrieve files uploaded by specific client
  - **Returns**: List of file metadata with upload dates

- `get_file_details(file_id, client_id)`
  - **Purpose**: Get detailed info about specific uploaded file
  - **Returns**: File metadata or access error

### **`web_service.py` - Web Business Logic** ✅
**Purpose**: HTML page rendering and template data preparation

#### **Page Data Preparation**
- `prepare_homepage_data()`
  - **Purpose**: Homepage template data (recent games, top players, stats)
  - **Returns**: Dict with all homepage sections populated

- `prepare_all_players_data()`
  - **Purpose**: Players listing page with pagination and search
  - **Returns**: Formatted player list with stats and encoding

#### **Player Page Processing**
- `process_player_profile_request(encoded_player_code)`
  - **Purpose**: Basic player profile page data
  - **Returns**: Player stats, recent games, character usage
  - **Error Handling**: Uses Flask abort() for 404/500 errors

- `process_player_detailed_request(encoded_player_code)`
  - **Purpose**: Detailed player analysis page with filters
  - **Returns**: Comprehensive stats with filter options
  - **Recently Fixed**: Now handles request context for filter parameters

#### **Data Processing Helpers**
- `prepare_standard_player_template_data(player_code, encoded_player_code)`
  - **Purpose**: Common player page data structure
  - **Returns**: Standardized player data for templates

---

## **Domain Services** (New Pattern - Schema-Driven)

### **`upload/` - Upload Domain Service** ✅ **COMPLETE**
**Purpose**: Handle all upload-related business logic with standardized schemas

#### **Main Orchestrator Functions**
- `process_combined_upload(client_id, upload_data)`
  - **Purpose**: Main upload orchestrator handling games + files + client info
  - **Input**: Combined upload data with validation
  - **Returns**: Standardized upload result with detailed breakdown
  - **Benefits**: Eliminates result vs placement confusion via schemas

- `upload_games_for_client(client_id, games_data)`
  - **Purpose**: Process game data uploads for specific client
  - **Input**: List of game data with player information
  - **Returns**: Upload results with success/duplicate/error counts

- `process_file_upload(client_id, file_info, file_content)`
  - **Purpose**: Handle individual file upload with metadata
  - **Input**: File data and content for processing
  - **Returns**: File upload result with generated ID

#### **Schema Benefits Achieved**
- ✅ **Standardized game data** with computed display fields
- ✅ **Type safety** through validation and clear contracts
- ✅ **Consistent error handling** with structured messages
- ✅ **Automatic field computation** (stage names, game length, etc.)

#### **Domain Structure**
```
upload/
├── schemas.py          # Data structures and validation schemas  
├── validation.py       # Business rule validation
├── service.py          # Main orchestrator functions (public API)
├── processors.py       # Core business logic and database operations
└── __init__.py         # Public exports
```

### **`client/` - Client Domain Service** ✅ **COMPLETE**
**Purpose**: Complete client lifecycle management and authentication

#### **Main Orchestrator Functions**
- `register_client(client_data, registration_key)`
  - **Purpose**: Register new client with API key generation
  - **Input**: Client registration data with optional registration key
  - **Returns**: Client ID and generated API key
  - **Recently Fixed**: Proper API key file generation (was writing None)

- `authenticate_client(api_key)`
  - **Purpose**: Validate API key and return client information
  - **Input**: API key string for validation
  - **Returns**: Client data if valid, error if invalid

- `update_client_info(client_id, update_data)`
  - **Purpose**: Update client information (hostname, version, etc.)
  - **Input**: Client ID and fields to update
  - **Returns**: Update success confirmation

- `get_client_details(client_id)`
  - **Purpose**: Retrieve complete client information
  - **Input**: Client ID for lookup
  - **Returns**: Full client data including registration date

- `refresh_api_key(client_id)`
  - **Purpose**: Generate new API key for existing client
  - **Input**: Client ID for key regeneration
  - **Returns**: New API key and update confirmation

#### **Authentication & Security**
- **API Key Generation**: Secure random key generation with file storage
- **Validation**: Client data validation with business rules
- **Security**: Prevents duplicate registrations and invalid updates

#### **Domain Structure**
```
client/
├── schemas.py          # Client data structures and registration formats
├── validation.py       # Client validation rules and security checks
├── service.py          # Main client orchestrator functions (public API)  
├── processors.py       # Database operations and API key management
└── __init__.py         # Public exports
```

---

## **Support Layers** 🔧

### **`database.py` - Data Access Layer** ✅
**Current Implementation**: Uses simplified `backend.db` layer

#### **Main Functions**
- `execute_query(category, query_name, params, fetch_one=False)`
  - **Purpose**: Execute external SQL queries with parameters
  - **Input**: SQL category, query name, and parameters
  - **Returns**: Query results as list of dicts or single dict

#### **SQL Integration**
- **External SQL Files**: All queries stored in organized `sql/` directory
- **Dynamic Discovery**: SQL files automatically available after creation
- **Template Support**: Use `{variable}` placeholders for flexible queries
- **Category Organization**: Queries organized by functionality (games, clients, files)

### **`utils.py` - Shared Utilities** ✅
**Purpose**: Data processing and helper functions used across services

#### **Game Processing Functions**
- `process_raw_games_for_player(raw_games, target_player_tag)`
  - **Purpose**: Convert raw database games to player-specific format
  - **Returns**: Processed games with nested player/opponent structure
  - **Recently Fixed**: Character data now properly nested in player object

- `parse_player_data_from_game(game_data)`
  - **Purpose**: Parse JSON player data from game records
  - **Returns**: List of player data dictionaries

#### **Player Tag Functions**  
- `encode_player_tag(player_tag)` / `decode_player_tag(encoded_tag)`
  - **Purpose**: URL-safe encoding/decoding of player tags
  - **Usage**: Handle special characters in URLs (# becomes %23)

#### **Statistics Functions**
- `calculate_win_rate(wins, total_games)`
  - **Purpose**: Safe win rate calculation with error handling
  - **Returns**: Decimal win rate (0.0 to 1.0)

### **`config.py` - Configuration Management** ✅
**Purpose**: Centralized application configuration

#### **Main Functions**
- `get_config()` - Main configuration object with all settings
- `init_logging()` - Configure logging system for application
- `get_database_path()` - Database file location for data storage  
- `get_downloads_dir()` - Downloads directory for static files

---

## **Routes Layer** 🌐
**Purpose**: HTTP request/response handling - delegates to services

### **Route Organization**
- **`web_routes.py`**: HTML page routes (player pages, homepage, etc.)
- **`api_routes.py`**: JSON API endpoints with authentication
- **`static_routes.py`**: File serving for downloads and uploads

### **Route Pattern**
```python
@web_bp.route('/player/<encoded_player_code>/detailed')
def player_detailed(encoded_player_code):
    """Route handler - thin controller pattern."""
    try:
        # Minimal validation
        player_code = decode_player_tag(encoded_player_code)
        
        # Delegate to service layer
        context_data = web_service.process_player_detailed_request(encoded_player_code)
        
        # Return response
        return render_template('pages/player_detailed/player_detailed.html', **context_data)
    except Exception as e:
        # Error handling
        return handle_error(e)
```

---

## **Service Usage Examples** 💡

### **API Endpoint Implementation**
```python
# In api_routes.py
@api_bp.route('/player/<encoded_player_code>/detailed', methods=['GET', 'POST'])
def player_detailed_stats(encoded_player_code):
    # Get filters from request (GET params or POST JSON)
    if request.method == 'POST':
        filter_data = request.get_json() or {}
        character = filter_data.get('character', 'all')
        opponent_character = filter_data.get('opponent_character', 'all')
    else:
        character = request.args.get('character', 'all')
        opponent_character = request.args.get('opponent_character', 'all')
    
    # Delegate to service layer
    player_code = decode_player_tag(encoded_player_code)
    detailed_stats = api_service.process_detailed_player_data(
        player_code, character, opponent, stage, limit, opponent_character
    )
    
    return jsonify(detailed_stats)
```

### **Client Registration Example**
```python
# In api_routes.py
@api_bp.route('/clients/register', methods=['POST'])
def client_registration():
    client_data = request.json
    registration_key = request.headers.get('X-Registration-Key')
    
    # Delegate to client domain service
    result = client_service.register_client(client_data, registration_key)
    
    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 400
```

### **Upload Processing Example**
```python
# In api_routes.py
@api_bp.route('/games/upload', methods=['POST'])
@require_api_key
def games_upload(client_id):
    upload_data = request.get_json()
    
    # Delegate to upload domain service
    result = upload_service.process_combined_upload(client_id, upload_data)
    
    return jsonify(result)
```

### **Web Page Example**
```python
# In web_routes.py
@web_bp.route('/player/<encoded_player_code>')
def player_basic(encoded_player_code):
    try:
        # Delegate to web service
        context_data = web_service.process_player_profile_request(encoded_player_code)
        
        # Render template with data
        return render_template('pages/player_basic/player_basic.html', **context_data)
    except Exception as e:
        return render_template('pages/error_status/error_status.html',
                              status_code=500, error_type="danger")
```

---

## **Data Flow Examples** 🔄

### **Frontend Filter Request Flow**
```
Frontend JavaScript (POST /api/player/CODE/detailed)
    ↓ JSON: {character: "Fox", opponent_character: "Falco"}
API Route (api_routes.py)
    ↓ delegates to
API Service (process_detailed_player_data)
    ↓ calls helpers
Filter Functions (_apply_comprehensive_filters)
    ↓ access data
Database Layer (execute_query)
    ↓ loads SQL
External SQL File (games/select_by_player.sql)
    ↓ returns processed data
Frontend Updates (charts, tables, filter options)
```

### **Client Registration Flow**
```
Client Application (POST /api/clients/register)
    ↓ JSON: {client_name: "MyApp", version: "1.0.0"}
API Route (client_registration)
    ↓ delegates to
Client Domain Service (register_client)
    ↓ orchestrates
Validation (validate_client_registration_data)
    ↓ then
Processors (create_client_in_database + generate_api_key)
    ↓ creates
Database Record + API Key File
    ↓ returns
{success: true, client_id: "...", api_key: "..."}
```

### **Game Upload Flow**
```
Client Upload (POST /api/games/upload with API key)
    ↓ JSON: {games: [...], files: [...]}
API Route (games_upload)
    ↓ authenticates via @require_api_key
Upload Domain Service (process_combined_upload)
    ↓ orchestrates
Schemas (normalize game data formats)
    ↓ then
Validation (business rules + data integrity)
    ↓ then  
Processors (database operations + file handling)
    ↓ returns
{success: true, games_processed: 5, files_uploaded: 2}
```

---

## **Migration Status & Future Plans** 🗺️

### **Current State: Hybrid Architecture**
- ✅ **Monolithic Services**: Stable, well-tested, handling core functionality
- ✅ **Domain Services**: New pattern for complex areas (client, upload)
- 🔄 **Gradual Migration**: Moving complex logic to domain pattern over time

### **Migration Candidates**

#### **Player Domain** (High Priority)
**Current**: Scattered across api_service.py and web_service.py
**Proposed**: `backend/services/player/`
- `get_player_stats()`
- `get_detailed_analysis()`  
- `process_player_search()`
- **Benefits**: Standardized player data schemas, better caching

#### **Stats Domain** (Medium Priority)
**Current**: Mixed into various services
**Proposed**: `backend/services/stats/`
- `get_server_statistics()`
- `calculate_leaderboards()`
- `generate_analytics_reports()`
- **Benefits**: Centralized statistics logic, performance optimization

#### **File Domain** (Low Priority)
**Current**: Basic file handling in api_service.py
**Proposed**: `backend/services/files/`
- `process_file_upload()`
- `manage_file_storage()`
- `handle_file_downloads()`
- **Benefits**: Advanced file processing, better storage management

### **Service Architecture Evolution**
```
Current State:
├── Monolithic Services (70% of functionality)
├── Domain Services (30% of functionality)
└── Support Layers (100% stable)

Target State:
├── Domain Services (80% of functionality)  
├── Monolithic Services (20% of simple functionality)
└── Support Layers (enhanced with caching)
```

---

## **Service Dependencies** 📊

### **Import Hierarchy (Enforced)**
```
Routes Layer
    ↓ can import
Service Layer (all services)
    ↓ can import
Support Layer (database, utils, config)
    ↓ uses
External Resources (SQL files, static files)
```

### **Cross-Service Communication**
```python
# ✅ Allowed: Routes import any service
from backend.services import api_service, web_service
from backend.services.client import register_client

# ✅ Allowed: Services import support layers
from backend.db import execute_query
from backend.utils import process_raw_games_for_player

# ✅ Allowed: Domain services use other domain public APIs
from backend.services.upload import process_file_upload

# ❌ Forbidden: Services import routes
# ❌ Forbidden: Support layers import services  
# ❌ Forbidden: Circular imports between services
```

### **Database Dependencies**
- **All Services** → `backend.db.execute_query()`
- **All SQL** → External files in `sql/` directory
- **SQL Organization**: `sql/{category}/{operation}.sql`
- **Template Support**: `{variable}` substitution in SQL files

---

## **Testing Strategy** 🧪

### **Service Layer Testing**
```python
# Contract-based testing - validate inputs/outputs
def test_service_function_contract():
    # Test that function maintains expected contract
    result = service_function(test_input)
    assert isinstance(result, dict)
    assert 'success' in result or 'error' in result
```

### **Domain Service Testing**
```python
# Schema-focused testing - ensure data standardization
def test_domain_schema_standardization():
    # Test that various input formats are normalized
    schema_obj = DomainSchema.from_input_data(test_data)
    assert isinstance(schema_obj.result, StandardizedEnum)
```

### **Integration Testing**
```python
# End-to-end workflow testing
def test_complete_upload_workflow():
    # Test complete upload from API call to database
    response = client.post('/api/games/upload', 
                          headers={'X-API-Key': test_key},
                          json=test_upload_data)
    assert response.status_code == 200
```

---

## **Performance Considerations** ⚡

### **Current Performance Profile**
- **Response Times**: Sub-second for most operations
- **Database**: SQLite with external SQL optimization
- **Memory**: Efficient data processing with streaming for large uploads
- **Caching**: Minimal (opportunity for improvement)

### **Optimization Opportunities**
1. **Query Result Caching**: Redis layer for expensive player statistics
2. **Database Connection Pooling**: Better resource utilization
3. **API Response Caching**: Cache stable data like player basic stats
4. **Frontend Caching**: Browser caching for character icons and static data

### **Scaling Considerations**
- **Service Boundaries**: Ready for microservice extraction if needed
- **Database**: External SQL makes PostgreSQL migration straightforward  
- **Frontend**: Component architecture supports CDN and caching
- **Observability**: Full tracing enables performance monitoring

---

## **Troubleshooting Guide** 🔧

### **Common Issues**

#### **Character Names Show as "Unknown"**
- **Cause**: Incorrect data structure access in filtering functions
- **Fix**: Use `game.get('player', {}).get('character_name')` instead of `game.get('character_name')`
- **Status**: ✅ Fixed in recent update

#### **Frontend Filters Not Working**
- **Cause**: Missing POST API endpoint for detailed filtering
- **Fix**: Added POST support to `/api/player/{code}/detailed` route
- **Status**: ✅ Fixed in recent update

#### **Template Errors (JSON serialization)**
- **Cause**: Missing `error_type` variable in error handlers
- **Fix**: Add `error_type` parameter to all error template calls
- **Status**: ✅ Fixed in recent update

#### **Client Registration Fails**
- **Cause**: API key generation writing None to files
- **Fix**: Implemented proper client domain service with validation
- **Status**: ✅ Fixed with client domain implementation

### **Debugging Tips**
1. **Check Service Layer First**: Most business logic issues are in services
2. **Verify Data Structure**: Use logging to inspect actual data formats
3. **Test API Endpoints**: Use curl to test API calls independently
4. **Check SQL Files**: Verify external SQL queries are correct
5. **Validate Imports**: Ensure using correct import patterns

---

## **Quick Reference** 📋

### **Most Used Functions**
```python
# Player analysis
api_service.process_detailed_player_data(player_code, filters...)
web_service.process_player_profile_request(encoded_player_code)

# Upload processing  
upload_service.process_combined_upload(client_id, upload_data)

# Client management
client_service.register_client(client_data, registration_key)
client_service.authenticate_client(api_key)

# Data access
execute_query('games', 'select_by_player', (player_code,))
```

### **Import Patterns**
```python
# Standard service imports
from backend.services import api_service, web_service

# Domain service imports
from backend.services.client import register_client
from backend.services.upload import process_combined_upload

# Support layer imports
from backend.db import execute_query
from backend.utils import decode_player_tag
```

---

**Maintained by**: Gavin
**Last Updated**: July 2025  
**Version**: Current working state with recent fixes