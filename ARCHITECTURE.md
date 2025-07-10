# Architecture Documentation - Slippi Stats Server

Complete architectural reference for the current service-oriented implementation.

## **Overview** 🏗️

The Slippi Stats Server follows a **service-oriented architecture** with clear separation of concerns, external SQL management, and hybrid service patterns. The architecture successfully migrated from a monolithic structure to enable maintainability, testability, and scalability.

### **Core Architectural Principle**
> **"Services Process, Database Stores, Utils Help, SQL Separates"**

## **Current Architecture State** ✅

### **Backend Layer Structure**
```
┌─────────────────────────────────────────────────┐
│                Routes Layer                     │ ← HTTP handling, thin controllers
│        (web_routes.py, api_routes.py)          │
└─────────────────┬───────────────────────────────┘
                  │ delegates to ↓
┌─────────────────┴───────────────────────────────┐
│              Service Layer                      │ ← Business logic
│   Monolithic Services + Domain Services        │
│     (api_service.py, web_service.py)           │
│     (client/, upload/ domains)                 │
└─────────────────┬───────────────────────────────┘
                  │ uses ↓
┌─────────────────┴───────────────────────────────┐
│              Support Layer                      │ ← Foundation
│    (backend.db, utils.py, config.py)          │
└─────────────────┬───────────────────────────────┘
                  │ loads ↓
┌─────────────────┴───────────────────────────────┐
│             External SQL Files                  │ ← Organized queries
│              (sql/ directory)                   │
└─────────────────────────────────────────────────┘
```

### **Frontend Architecture**
```
┌─────────────────────────────────────────────────┐
│                 Pages Layer                     │ ← Business logic, API calls
│           (pages/ directory)                    │
└─────────────────┬───────────────────────────────┘
                  │ uses ↓
┌─────────────────┴───────────────────────────────┐
│               Layouts Layer                     │ ← Component orchestration
│           (layouts/ directory)                  │
└─────────────────┬───────────────────────────────┘
                  │ provides ↓
┌─────────────────┴───────────────────────────────┐
│             Components Layer                    │ ← Self-contained UI behavior
│          (components/ directory)                │
└─────────────────────────────────────────────────┘
```

## **Service Layer Architecture** 🔧

### **Hybrid Service Pattern**
The backend uses a **hybrid approach** combining two service patterns:

#### **Monolithic Services** (Legacy - Stable)
- **Purpose**: Well-defined, stable business logic
- **Files**: `api_service.py`, `web_service.py`
- **Characteristics**: Single file per service type, comprehensive functionality
- **Status**: Mature, well-tested, handles core features

#### **Domain Services** (New - Schema-Driven)
- **Purpose**: Complex business areas requiring standardized data formats
- **Structure**: `backend/services/{domain}/` with 5-file structure
- **Characteristics**: Schema validation, type safety, clear boundaries
- **Current Domains**: `client/`, `upload/`

### **Service Layer Import Rules** (Strictly Enforced)
```python
# ✅ Services can import:
from backend.db import execute_query        # Data access
from backend.utils import helper_function   # Shared utilities
from backend.config import get_config       # Configuration

# ✅ Routes can import:
import backend.services as services         # All service functions
from backend.services.client import register_client  # Domain-specific

# ❌ Services cannot import:
from backend.routes import *               # Routes import services, not vice versa
from other_service import *                # Services should not import each other

# ❌ Support layers cannot import:
from backend.services import *             # Lower layers can't import higher
```

## **Database Layer** 💾

### **Current Implementation: backend.db**
The database layer uses a simplified architecture with external SQL management:

```python
# Database access pattern
from backend.db import execute_query

# Execute external SQL queries
games = execute_query('games', 'select_by_player', (player_code,))
```

### **External SQL Organization**
```
sql/
├── games/
│   ├── select_by_player.sql      # Get games for specific player
│   ├── select_recent.sql         # Get recent games for homepage
│   └── insert_game.sql           # Insert new game record
├── clients/
│   ├── select_by_id.sql          # Get client by ID
│   ├── insert_client.sql         # Register new client
│   └── update_last_active.sql    # Update client activity
├── files/
│   ├── select_by_client.sql      # Get files for client
│   └── insert_file.sql           # Store file metadata
└── stats/
    ├── count_unique_players.sql  # Server statistics
    └── file_stats_total.sql      # File storage stats
```

### **SQL Query Features**
- **Dynamic Discovery**: Add `.sql` files and they're automatically available
- **Template Support**: Use `{variable}` placeholders for dynamic queries
- **Category Organization**: Logical grouping by functionality
- **Hot Reloading**: Update queries without application restart (development)

## **Service Catalog** 📋

### **Monolithic Services**

#### **`api_service.py` - API Business Logic**
```python
# Player analysis
process_detailed_player_data(player_code, character, opponent, stage, limit, opponent_character)
process_player_basic_stats(player_code)
apply_game_filters(games, filters)

# Server management
process_server_statistics()
validate_api_key(api_key)

# File management
get_client_files(client_id, limit)
get_file_details(file_id, client_id)
```

#### **`web_service.py` - Web Business Logic**
```python
# Page data preparation
prepare_homepage_data()
prepare_all_players_data()
process_player_profile_request(encoded_player_code)
process_player_detailed_request(encoded_player_code)

# Template data helpers
prepare_standard_player_template_data(player_code, encoded_player_code)
```

### **Domain Services**

#### **`client/` - Client Domain Service**
```python
# Client lifecycle management
register_client(client_data, registration_key)
authenticate_client(api_key)
update_client_info(client_id, update_data)
get_client_details(client_id)
refresh_api_key(client_id)
```

#### **`upload/` - Upload Domain Service**
```python
# Upload orchestration
process_combined_upload(client_id, upload_data)
upload_games_for_client(client_id, games_data)
process_file_upload(client_id, file_info, file_content)
```

### **Support Layers**

#### **`backend.db` - Data Access**
```python
# Simple database interface
execute_query(category, query_name, params, fetch_one=False)
```

#### **`utils.py` - Shared Utilities**
```python
# Game processing
process_raw_games_for_player(raw_games, target_player_tag)
parse_player_data_from_game(game_data)

# Player tag handling
encode_player_tag(player_tag)
decode_player_tag(encoded_tag)

# Statistics
calculate_win_rate(wins, total_games)
```

## **Data Flow Architecture** 🔄

### **Frontend Filter Request Flow**
```
Frontend JavaScript
    ↓ POST /api/player/{code}/detailed
    ↓ JSON: {character: "Fox", opponent_character: "Falco"}
API Route (api_routes.py)
    ↓ delegates to
API Service (process_detailed_player_data)
    ↓ calls helpers
Filter Functions (_apply_comprehensive_filters)
    ↓ access data via
Database Layer (execute_query)
    ↓ loads SQL from
External SQL File (games/select_by_player.sql)
    ↓ returns processed data to
Frontend (updates charts, tables, filter options)
```

### **Client Registration Flow**
```
Client Application
    ↓ POST /api/clients/register
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
Client Upload
    ↓ POST /api/games/upload (with API key)
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

## **Frontend Architecture** 🎨

### **Component-Based Design**
The frontend follows **"Components Do, Layouts Share, Pages Orchestrate"**:

#### **Components** (Self-Contained Behavior)
- **Auto-Initialization**: No manual setup required
- **Asset Management**: Components manage their own CSS/JS
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Reusability**: Used across multiple pages and layouts

#### **Layouts** (Component Orchestration)
- **Component Imports**: Make components available to pages
- **Shared Structure**: Common page elements (navbar, footer)
- **Asset Loading**: Include component CSS/JS files
- **Template Inheritance**: Provide base structure for pages

#### **Pages** (Business Logic)
- **API Calls**: Handle data fetching and processing
- **Component Coordination**: Connect components for page functionality
- **User Interactions**: Handle form submissions and user actions
- **Data Management**: Process and display dynamic content

### **Data Structure Example**
```javascript
// Pages handle API calls and data processing
async function fetchPlayerData(filters = {}) {
    const response = await fetch(`/api/player/${encodedPlayerCode}/detailed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
    });
    const data = await response.json();
    
    // Coordinate components with processed data
    updateCharacterFilters(data.character_stats);
    updateGamesTables(data.recent_games);
    updateCharts(data.date_stats);
}
```

## **Key Architectural Innovations** 💡

### **1. External SQL Management**
- **Dynamic Discovery**: SQL files automatically available
- **Template Variables**: `{variable}` substitution for flexible queries
- **Category Organization**: Logical grouping by functionality
- **Version Control**: SQL tracked in git like code
- **Hot Reloading**: Update queries without restart (development)

### **2. Hybrid Service Architecture**
- **Monolithic Services**: For stable, well-defined business logic
- **Domain Services**: For complex areas requiring schema standardization
- **Backward Compatibility**: Both patterns coexist during migration
- **Clear Migration Path**: Guidelines for when to use each pattern

### **3. Schema-Driven Domain Services**
- **Type Safety**: Clear data contracts with validation
- **Standardization**: Eliminates data format inconsistencies
- **Error Handling**: Structured validation messages
- **Computed Fields**: Automatic field generation (stage names, etc.)

### **4. Component-Based Frontend**
- **Progressive Enhancement**: Works without JavaScript
- **Auto-Initialization**: Components set themselves up
- **Asset Ownership**: Components manage their own CSS/JS
- **Reusability**: Clear interfaces for component reuse

## **Performance Characteristics** ⚡

### **Current Performance Profile**
- **Response Times**: Sub-second for most operations
- **Database**: SQLite with optimized external SQL queries
- **Memory Usage**: Efficient data processing with streaming for large uploads
- **Frontend**: Progressive loading with component-based architecture

### **Optimization Opportunities**
1. **Query Result Caching**: Redis layer for expensive player statistics
2. **Database Connection Pooling**: Better resource utilization
3. **API Response Caching**: Cache stable data like basic player stats
4. **Frontend Optimization**: Browser caching for static assets

### **Scaling Considerations**
- **Service Boundaries**: Ready for microservice extraction
- **Database Migration**: External SQL makes PostgreSQL migration straightforward
- **Frontend Scaling**: Component architecture supports CDN deployment
- **Observability**: Full tracing enables performance monitoring

## **Testing Architecture** 🧪

### **Architecture-Aligned Testing**
Tests respect the service-oriented module hierarchy:

#### **Service Layer Tests** (Fast - <1 second)
```python
# Contract-based testing - validate inputs/outputs
def test_service_function_contract():
    result = service_function(test_input)
    assert isinstance(result, dict)
    assert 'success' in result or 'error' in result
```

#### **Domain Service Tests** (Schema-Focused)
```python
# Schema standardization testing
def test_domain_schema_standardization():
    schema_obj = DomainSchema.from_input_data(test_data)
    assert isinstance(schema_obj.result, StandardizedEnum)
```

#### **Integration Tests** (Database + HTTP)
```python
# End-to-end workflow testing
def test_complete_upload_workflow():
    response = client.post('/api/games/upload', 
                          headers={'X-API-Key': test_key},
                          json=test_upload_data)
    assert response.status_code == 200
```

### **Current Test Coverage**
- **Overall Coverage**: 51%
- **Target Coverage**: 75%
- **Priority Areas**: Service layer contract tests, domain schema validation

## **Security Architecture** 🔒

### **API Authentication**
```python
# API key-based authentication
@require_api_key
def protected_endpoint(client_id):
    # client_id automatically provided by decorator
    pass
```

### **Rate Limiting**
```python
# Client-based rate limiting
@rate_limited(max_per_minute=30)
def upload_endpoint():
    pass
```

### **Input Validation**
- **Service Layer**: Business rule validation
- **Domain Services**: Schema-based validation with type safety
- **Route Layer**: Basic parameter validation

## **Observability & Monitoring** 📊

### **Current Implementation**
- **OpenTelemetry Tracing**: Request flow visibility across all layers
- **Prometheus Metrics**: Business and performance monitoring
- **Structured Logging**: Comprehensive error tracking and debugging
- **Grafana Dashboards**: Operational insights and alerting

### **Monitoring Coverage**
- **Business Metrics**: Games processed, files uploaded, API usage
- **Performance Metrics**: Response times, database query performance
- **Error Tracking**: Exception rates, error patterns
- **Resource Monitoring**: Memory usage, database performance

## **Configuration Management** ⚙️

### **Environment-Based Configuration**
```python
class DevelopmentConfig:
    DEBUG = True
    RATE_LIMIT_API = 60
    RATE_LIMIT_UPLOADS = 30
    RATE_LIMIT_REGISTRATION = 5

class ProductionConfig:
    DEBUG = False
    RATE_LIMIT_API = 120
    RATE_LIMIT_UPLOADS = 60
    RATE_LIMIT_REGISTRATION = 10
```

### **Configuration Categories**
- **Database**: Connection settings, file paths
- **Rate Limiting**: API endpoint limits
- **File Storage**: Upload directories, size limits
- **Security**: API key settings, authentication
- **Observability**: Tracing endpoints, metrics configuration

## **Migration Status & Future Plans** 🗺️

### **Current Migration State**
- ✅ **External SQL**: 100% of queries externalized
- ✅ **Service Layer**: Complete service-oriented architecture
- ✅ **Domain Services**: Client and upload domains implemented
- ✅ **Frontend**: Component-based architecture complete
- ✅ **Testing**: Architecture-aligned test framework
- ✅ **Observability**: Production-ready monitoring

### **Future Migration Candidates**

#### **Player Domain** (High Priority)
- **Current**: Scattered across `api_service.py` and `web_service.py`
- **Benefits**: Standardized player data schemas, better caching
- **Scope**: Player statistics, analysis, search functionality

#### **Stats Domain** (Medium Priority)
- **Current**: Mixed into various services
- **Benefits**: Centralized statistics logic, performance optimization
- **Scope**: Server statistics, leaderboards, analytics

### **Architectural Evolution Timeline**
```
Current: Hybrid (70% monolithic, 30% domain services)
    ↓ 3-6 months
Target: Domain-oriented (80% domain, 20% monolithic)
    ↓ 6-12 months
Future: Microservice-ready (service extraction capability)
```

## **Development Guidelines** 📝

### **Adding New Features**

#### **New Web Page**
1. Add route to `web_routes.py` with thin handler
2. Add business logic to appropriate service
3. Create page template extending appropriate layout
4. Add SQL queries to `sql/` category if needed
5. Add service layer and integration tests

#### **New API Endpoint**
1. Add route to `api_routes.py` with authentication/rate limiting
2. Add business logic to appropriate service
3. Update API documentation
4. Add comprehensive tests
5. Consider domain service if complex

#### **New Domain Service**
1. Create domain directory with 5-file structure
2. Implement schemas first (data structures)
3. Add validation logic and business rules
4. Create orchestrators and processors
5. Add comprehensive domain tests
6. Update service exports

### **Code Quality Standards**
- **Service Functions**: Follow orchestrator pattern (10-20 lines)
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Clear docstrings with Args/Returns
- **Testing**: Contract-based tests for all service functions
- **Import Rules**: Strict hierarchy enforcement

### **Performance Guidelines**
- **Database Queries**: Use external SQL with parameters
- **Caching**: Consider caching for expensive operations
- **Streaming**: Use generators for large data processing
- **Frontend**: Progressive enhancement, component optimization

---

**This architecture successfully serves production traffic with:**
- **Zero-downtime deployments**
- **Sub-second response times**
- **Comprehensive observability**
- **Clear migration paths for future scaling**

**Last Updated**: December 2024  
**Architecture Status**: Production-ready, actively maintained