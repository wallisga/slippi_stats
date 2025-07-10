# Contributing Guide

Welcome to the Slippi Stats Server project! This guide will help you understand our development process and architectural patterns.

## **Getting Started** 🚀

### **Development Setup**
```bash
# Fork the repository and clone
git clone <your-fork>
cd slippi-stats-server

# Windows (recommended)
start_dev.bat

# Manual setup (all platforms)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt

# Start development server
python app.py

# Optional: Start observability stack
docker-compose up -d
```

### **Project Understanding**
Before contributing, familiarize yourself with:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architectural reference
- **[SERVICE_DIRECTORY.md](SERVICE_DIRECTORY.md)** - Backend service catalog
- **[CHANGELOG.md](CHANGELOG.md)** - Recent changes and project history

## **Architecture Overview** 🏗️

### **Backend: Service-Oriented**
```
Routes → Services → Database → External SQL Files
- Thin route handlers delegate to services
- Business logic in service layer
- External SQL for all database queries
- Hybrid monolithic + domain services
```

### **Frontend: Component-Based**
```
Pages → Layouts → Components
- Pages handle business logic and API calls
- Layouts orchestrate components
- Components are self-contained with auto-initialization
```

### **Key Principles**
- **"Services Process, Database Stores, Utils Help, SQL Separates"**
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Import Hierarchy**: Strict rules prevent circular dependencies
- **External SQL**: All queries in organized .sql files

## **Development Patterns** 📋

### **Adding New Features**

#### **New API Endpoint**
1. **Add Route** to `backend/routes/api_routes.py`
   ```python
   @api_bp.route('/api/new-endpoint', methods=['POST'])
   @require_api_key  # If modifying data
   @rate_limited(60)  # Set appropriate limit
   def new_endpoint(client_id):
       result = services.process_new_feature(request.get_json())
       return jsonify(result)
   ```

2. **Add Business Logic** to appropriate service
   ```python
   # In backend/services/api_service.py or domain service
   def process_new_feature(input_data):
       """Process new feature request."""
       try:
           validated = _validate_inputs(input_data)
           processed = _process_main_logic(validated)
           return _create_response(processed)
       except Exception as e:
           logger.error(f"Error in new feature: {str(e)}")
           raise
   ```

3. **Add SQL Queries** (if needed) to `backend/sql/category/`
4. **Add Tests** - Service layer + API endpoint tests
5. **Update Documentation** - Add to API reference

#### **New Web Page**
1. **Add Route** to `backend/routes/web_routes.py`
   ```python
   @web_bp.route('/new-page')
   def new_page():
       context_data = web_service.prepare_new_page_data()
       return render_template('pages/new_page/new_page.html', **context_data)
   ```

2. **Add Service Logic** to `backend/services/web_service.py`
3. **Create Template** in `frontend/pages/new_page/`
4. **Add CSS/JS** if needed
5. **Add Tests** - Service layer + web rendering tests

#### **New Domain Service** (Complex Features)
1. **Create Domain Structure**
   ```
   backend/services/new_domain/
   ├── __init__.py          # Public exports
   ├── schemas.py           # Data structures
   ├── validation.py        # Business rules
   ├── service.py           # Orchestrators (public API)
   └── processors.py        # Core business logic
   ```

2. **Implement Schemas First** - Define data structures
3. **Add Validation Logic** - Business rules and input validation
4. **Create Orchestrators** - Main entry points (10-20 lines each)
5. **Add Processors** - Core business logic and database operations
6. **Update Service Exports** - Add to `backend/services/__init__.py`

### **Frontend Component Development**
1. **Create Component Directory** in `frontend/components/`
   ```
   frontend/components/new_component/
   ├── _new_component.html  # Template with macro
   ├── new_component.css    # Component styles
   ├── new_component.js     # Component behavior
   └── README.md           # Usage documentation
   ```

2. **Follow Component Pattern**
   ```javascript
   // Auto-initialization - no DOMContentLoaded wrapper
   class NewComponent {
       constructor(element, options = {}) {
           this.element = element;
           this.init();
       }
       
       init() {
           this.setupEventListeners();
           this.render();
       }
   }
   
   // Initialize immediately
   initializeNewComponent();
   ```

3. **Add to Layout** - Include component in appropriate layout
4. **Progressive Enhancement** - Ensure core functionality works without JS

## **Code Quality Standards** ✅

### **Service Layer**
- **Orchestrator Pattern**: Main functions coordinate workflow (10-20 lines)
- **Helper Functions**: Private functions with single responsibility
- **Error Handling**: Comprehensive exception handling with logging
- **Documentation**: Clear docstrings with Args/Returns sections

### **Database Layer**
- **External SQL Only**: All queries in organized .sql files
- **Parameterized Queries**: Use template variables `{variable}`
- **Category Organization**: Group queries by functionality
- **No Inline SQL**: Database layer loads from external files only

### **Frontend**
- **Component Isolation**: Self-contained behavior and styling
- **Progressive Enhancement**: Core functionality without JavaScript
- **Asset Ownership**: Components manage their own CSS/JS
- **Auto-Initialization**: Components work immediately when included

### **Testing Requirements**
- **Service Layer Tests**: Contract-based tests for all service functions
- **Integration Tests**: Database and HTTP endpoint coverage
- **Domain Tests**: Schema validation and business rule enforcement
- **Error Scenario Tests**: Comprehensive error handling validation

## **Testing Guidelines** 🧪

### **Test Categories**
```bash
# Service layer tests (fast - <1 second)
python -m pytest tests/test_service_layer.py

# Database integration tests
python -m pytest tests/test_database.py

# API endpoint tests
python -m pytest tests/test_api_endpoints.py

# Web page rendering tests
python -m pytest tests/test_web_pages.py

# All tests with coverage
python -m pytest --cov=backend --cov-report=html
```

### **Writing Tests**

#### **Service Layer Test Pattern**
```python
def test_service_function_contract():
    """Test service function maintains expected contract."""
    # Arrange
    test_input = create_test_data()
    
    # Act
    result = service_function(test_input)
    
    # Assert contract
    assert isinstance(result, dict)
    assert 'success' in result or 'error' in result
    
    # Don't test implementation details
    # Focus on inputs/outputs and contracts
```

#### **Domain Service Test Pattern**
```python
def test_domain_schema_standardization():
    """Test schema eliminates data format inconsistencies."""
    # Test various input formats are normalized
    formats = [
        {'player_tag': 'P1', 'result': 'Win'},
        {'player_tag': 'P1', 'placement': 1},
        {'player_tag': 'P1', 'result': 'win', 'placement': 2}
    ]
    
    for format_data in formats:
        schema_obj = DomainSchema.from_input_data(format_data)
        assert isinstance(schema_obj.result, StandardizedEnum)
```

### **Coverage Goals**
- **Current**: 51% overall coverage
- **Target**: 75% overall coverage
- **Priority**: Service layer functions, domain schemas, error handling

## **Import Rules** 📦

### **Strict Hierarchy (Enforced)**
```python
# ✅ Routes can import:
import backend.services as services
from backend.services.domain import domain_function
from backend.utils import helper_function

# ✅ Services can import:
from backend.db import execute_query
from backend.utils import process_data
from backend.config import get_config

# ✅ Utils can import:
from backend.config import get_config  # Only config

# ❌ Services cannot import:
from backend.routes import *  # Routes import services, not vice versa
from other_service import *   # Avoid service-to-service imports

# ❌ Support layers cannot import:
from backend.services import *  # Lower layers can't import higher
```

### **Domain Service Imports**
```python
# ✅ Domain files can import:
# schemas.py: No external imports (pure data structures)
# validation.py: Can import from .schemas
# service.py: Can import from .validation, .processors
# processors.py: Can import schemas, database, utils, config

# ✅ Cross-domain communication:
from backend.services.other_domain import public_function

# ❌ Don't import private functions across domain files
```

## **SQL Management** 💾

### **External SQL Organization**
```
backend/sql/
├── games/
│   ├── select_by_player.sql
│   ├── select_recent.sql
│   └── insert_game.sql
├── clients/
│   ├── select_by_id.sql
│   └── insert_client.sql
└── stats/
    └── count_unique_players.sql
```

### **SQL Guidelines**
- **All Queries External**: No inline SQL in Python code
- **Template Variables**: Use `{variable}` for dynamic values
- **Parameterized**: Always use parameters for user input
- **Documented**: Add comments for complex queries
- **Organized**: Group by functionality, not file type

### **Using External SQL**
```python
# In service functions
from backend.db import execute_query

# Execute external query with parameters
games = execute_query('games', 'select_by_player', (player_code,))
```

## **Observability** 📊

### **Logging Guidelines**
```python
# Use structured logging
logger.info(f"Processing request for player: {player_code}")
logger.error(f"Error in function {function_name}: {str(e)}")

# Log business events
logger.info(f"Games uploaded: {game_count} for client {client_id}")
```

### **Error Handling**
```python
# Comprehensive error handling
try:
    result = process_data(input_data)
    return result
except SpecificError as e:
    logger.warning(f"Expected error in {function_name}: {str(e)}")
    return {'error': str(e), 'error_type': 'validation'}
except Exception as e:
    logger.error(f"Unexpected error in {function_name}: {str(e)}")
    raise  # Re-raise unexpected errors
```

### **Performance Monitoring**
- Use external SQL for optimized queries
- Monitor database query performance
- Consider caching for expensive operations
- Profile frontend component loading

## **Documentation Standards** 📝

### **Code Documentation**
```python
def service_function(input_data, options=None):
    """
    Brief description of what the function does.
    
    Args:
        input_data (dict): Description of input parameter
        options (dict, optional): Optional configuration
    
    Returns:
        dict: Description of return value with structure
        
    Raises:
        ValueError: When input data is invalid
        DatabaseError: When database operation fails
    """
```

### **Update Documentation**
When making changes:
- **Code Comments**: Document complex business logic
- **API Documentation**: Update README.md for new endpoints
- **Architecture Changes**: Update ARCHITECTURE.md
- **Service Changes**: Update SERVICE_DIRECTORY.md
- **Changelog**: Add entry to CHANGELOG.md for significant changes

## **Pull Request Process** 🔄

### **Before Submitting**
1. **Run Tests**: Ensure all tests pass
   ```bash
   python -m pytest
   ```

2. **Check Coverage**: Maintain or improve coverage
   ```bash
   python -m pytest --cov=backend
   ```

3. **Code Quality**: Follow established patterns
4. **Documentation**: Update relevant documentation
5. **Manual Testing**: Test your changes manually

### **PR Guidelines**
- **Clear Description**: Explain what changes and why
- **Architecture Alignment**: Follow established patterns
- **Test Coverage**: Include tests for new functionality
- **Documentation Updates**: Update docs for user-facing changes
- **Small, Focused Changes**: One feature/fix per PR

### **Review Process**
- **Code Reviews**: Verify architectural pattern usage
- **Test Requirements**: Ensure comprehensive test coverage
- **Performance Impact**: Consider performance implications
- **Documentation Completeness**: Verify docs are updated

## **Common Development Tasks** 🛠️

### **Adding a New SQL Query**
1. Create `.sql` file in appropriate `backend/sql/category/`
2. Use template variables: `SELECT * FROM games WHERE player_tag = {player_tag}`
3. Use in service: `execute_query('category', 'query_name', (param,))`
4. Test with integration test

### **Debugging Issues**
1. **Check Logs**: Enable debug logging
2. **Test Service Layer**: Isolate business logic issues
3. **Database Queries**: Test SQL queries directly
4. **Frontend Console**: Check browser console for JS errors
5. **API Testing**: Use curl to test endpoints independently

### **Performance Optimization**
1. **Profile Database**: Check slow queries
2. **Frontend Performance**: Monitor component loading
3. **Caching Strategy**: Consider result caching
4. **Memory Usage**: Monitor for memory leaks

### **Adding Observability**
1. **Structured Logging**: Use consistent log formats
2. **Business Metrics**: Track key business events
3. **Error Tracking**: Comprehensive error logging
4. **Performance Metrics**: Monitor response times

## **Getting Help** 🤝

### **Resources**
- **Architecture Questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Service Reference**: See [SERVICE_DIRECTORY.md](SERVICE_DIRECTORY.md)
- **Recent Changes**: See [CHANGELOG.md](CHANGELOG.md)
- **Setup Issues**: Check development setup section

### **Communication**
1. **Search Existing Issues**: Check if question already answered
2. **Create Detailed Issues**: Include error logs and reproduction steps
3. **Ask in Discussions**: For architecture or design questions
4. **Code Reviews**: Learn from feedback on pull requests

### **Common Questions**
- **Import Errors**: Check import hierarchy rules
- **Test Failures**: Ensure following test patterns
- **Performance Issues**: Review SQL queries and caching
- **Frontend Issues**: Check component initialization and browser console

---

**Remember**: Follow the established patterns, add comprehensive tests, and update documentation. When in doubt, look at existing code for examples of the patterns in action.

**Happy Contributing!** 🎉