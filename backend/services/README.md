# Service Layer Architecture

This directory contains the business logic services for the Slippi Stats Server. Services implement the core application functionality using the **Orchestrator Pattern** for maintainable, testable code.

## Overview

The service layer sits between the HTTP routes and the data access layer, implementing business logic and coordinating between different components of the application.

### Service Layer Responsibilities

**✅ Services DO:**
- Implement business logic and workflows
- Coordinate between database, utils, and external services
- Handle complex data processing and validation
- Manage transactions and error handling
- Transform data between different formats

**❌ Services DON'T:**
- Handle HTTP requests/responses directly (routes do this)
- Contain SQL queries (database layer does this)
- Implement utility functions (utils layer does this)
- Manage configuration (config module does this)

## Current Services

### Core Services

#### `api_service.py` - API Business Logic
**Purpose**: Business logic for JSON API endpoints

**Key Responsibilities:**
- Player data processing and analysis
- Game upload and file processing
- Client registration and management
- Advanced filtering and statistics

**Major Functions:**
- `process_combined_upload()` - Handle games and files upload
- `process_detailed_player_data()` - Advanced player analysis
- `process_player_basic_stats()` - Basic player statistics
- `register_or_update_client()` - Client management

#### `web_service.py` - Web Business Logic  
**Purpose**: Business logic for HTML page rendering

**Key Responsibilities:**
- Template data preparation
- Player profile data assembly
- Homepage statistics calculation
- Navigation and redirect logic

**Major Functions:**
- `prepare_homepage_data()` - Homepage template data
- `prepare_all_players_data()` - Players listing data
- `process_player_profile_request()` - Player profile handling
- `process_player_detailed_request()` - Detailed analysis handling

## Orchestrator Pattern

All service functions follow the **Orchestrator Pattern** for maintainable, testable code. See [ORCHESTRATOR_PATTERN.md](ORCHESTRATOR_PATTERN.md) for detailed implementation guidelines.

### Pattern Summary

```python
def public_service_function(main_args):
    """Orchestrator - coordinates the workflow (10-20 lines)."""
    try:
        validated_data = _validate_inputs(main_args)
        processed_data = _process_main_logic(validated_data)
        _handle_side_effects(processed_data)
        return _create_response(processed_data)
    except SpecificError as e:
        return _handle_specific_error(e)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def _validate_inputs(inputs):
    """Helper - focused validation (5-15 lines)."""
    pass

def _process_main_logic(data):
    """Helper - core business logic (5-15 lines)."""
    pass
```

## Import Rules & Dependencies

Services follow strict import hierarchy:

```python
# ✅ Services can import:
from backend.database import *    # Data access functions
from backend.utils import *       # Utility functions
from backend.config import *      # Configuration
import json, datetime, etc.       # Standard library

# ❌ Services cannot import:
from backend.routes import *      # Routes import services, not vice versa
from other_service import *       # Services should not import each other
```

### Service Communication
When services need to share functionality:
1. **Extract to utils** - If it's a pure function without side effects
2. **Extract to database** - If it's data access logic
3. **Create shared service** - If it's complex business logic used by multiple services

## Testing Strategy

### Service Layer Testing
Services use **contract-based testing** focusing on inputs/outputs:

```python
def test_service_function_contract():
    """Test that service function maintains expected contract."""
    # Arrange
    test_input = create_test_data()
    
    # Act
    result = service_function(test_input)
    
    # Assert contract
    assert isinstance(result, dict)
    assert 'success' in result
    assert 'data' in result or 'error' in result
```

### Helper Function Testing
Test orchestrator helpers independently:

```python
def test_validate_inputs():
    """Test validation logic in isolation."""
    # Test with valid data
    valid_result = _validate_inputs(valid_data)
    assert valid_result is not None
    
    # Test with invalid data
    with pytest.raises(ValidationError):
        _validate_inputs(invalid_data)
```

See [tests/README.md](../tests/README.md) for complete testing guidelines.

## Service Organization Patterns

### Current Structure (Working Well)
```
backend/services/
├── api_service.py      # API business logic
└── web_service.py      # Web business logic
```

### Future Organization (When Services Grow)
When individual services become large (>500 lines), consider splitting by domain:

```
backend/services/
├── README.md
├── player/
│   ├── __init__.py
│   ├── player_analysis_service.py
│   ├── player_profile_service.py
│   └── player_stats_service.py
├── upload/
│   ├── __init__.py
│   ├── game_upload_service.py
│   ├── file_upload_service.py
│   └── combined_upload_service.py
├── client/
│   ├── __init__.py
│   ├── client_registration_service.py
│   └── client_management_service.py
└── shared/
    ├── __init__.py
    └── validation_service.py
```

## Adding New Services

### 1. When to Create a New Service
Create a new service when:
- **Domain separation** - Distinct business domain (users, tournaments, etc.)
- **Size concerns** - Existing service exceeds 500 lines
- **Team organization** - Different teams own different domains
- **External integration** - Service handles external API integration

### 2. Service Creation Template

```python
"""
[Service Name] Service

Business logic for [domain description].
"""

import logging
from datetime import datetime
from backend.config import get_config
from backend.database import [required_functions]
from backend.utils import [required_functions]

# Configuration and logging
config = get_config()
logger = config.init_logging()

# ============================================================================
# Public API - Orchestrator Functions
# ============================================================================

def main_service_function(primary_args):
    """
    Main service function description.
    
    Args:
        primary_args: Description of arguments
    
    Returns:
        dict: Standardized response with success/error
    """
    try:
        # Implementation using orchestrator pattern
        pass
    except Exception as e:
        logger.error(f"Error in main_service_function: {str(e)}")
        raise

# ============================================================================
# Helper Functions - Implementation Details
# ============================================================================

def _helper_function(data):
    """Helper function with focused responsibility."""
    pass
```

### 3. Service Registration
When creating new services, update:
1. **Import in routes** - Import service functions in relevant route files
2. **Update tests** - Add service layer tests for new functions
3. **Document in README** - Update this README with new service description

## Error Handling Patterns

### Standardized Error Responses
All services return consistent error response format:

```python
# Success response
{
    'success': True,
    'data': {...},
    'message': 'Operation completed successfully'
}

# Error response
{
    'success': False,
    'error': 'Error description',
    'error_code': 'VALIDATION_ERROR',  # Optional
    'details': {...}  # Optional additional context
}
```

### Error Logging Strategy
```python
def service_function(data):
    try:
        # Business logic
        pass
    except ValidationError as e:
        # Log validation errors as warnings
        logger.warning(f"Validation error in service_function: {str(e)}")
        return {'success': False, 'error': str(e)}
    except DatabaseError as e:
        # Log database errors as errors
        logger.error(f"Database error in service_function: {str(e)}")
        return {'success': False, 'error': 'Database operation failed'}
    except Exception as e:
        # Log unexpected errors and re-raise
        logger.error(f"Unexpected error in service_function: {str(e)}")
        raise
```

## Performance Considerations

### Caching Strategy
Services should implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _expensive_calculation(cache_key):
    """Cache expensive calculations at service layer."""
    pass
```

### Database Optimization
- **Batch operations** when possible
- **Use database indexes** effectively
- **Limit result sets** with reasonable defaults
- **Monitor query performance** through logging

### Memory Management
- **Stream large datasets** instead of loading entirely into memory
- **Clean up temporary data** after processing
- **Use generators** for large data processing

## Observability Integration

All services integrate with the observability stack:

```python
from backend.observability import trace_function

@trace_function
def service_function(data):
    """Service function with automatic tracing."""
    # Function automatically traced for performance monitoring
    pass
```

## Migration from Current Structure

### Phase 1: Current State (✅ Complete)
- `api_service.py` and `web_service.py` in `backend/`
- Functions follow orchestrator pattern
- Clear separation of concerns

### Phase 2: Service Directory Creation
1. **Create `backend/services/` directory**
2. **Move existing services** to new directory
3. **Update imports** in routes and tests
4. **Create this README**

### Phase 3: Future Organization (When Needed)
1. **Identify service boundaries** by domain
2. **Split large services** into focused domain services
3. **Maintain backward compatibility** during transition
4. **Update documentation** and tests

## Contributing Guidelines

### Code Style
- Follow **orchestrator pattern** for complex functions
- Use **descriptive function names** that indicate business purpose
- Implement **comprehensive error handling**
- Add **type hints** for function parameters and returns
- Include **docstrings** with Args and Returns sections

### Testing Requirements
- **Service layer tests** for all public functions
- **Helper function tests** for complex validation or processing logic
- **Error scenario tests** for all expected error conditions
- **Integration tests** for complete workflows

### Review Process
- **Code reviews** should verify orchestrator pattern usage
- **Performance impact** consideration for new service functions
- **Error handling** completeness and consistency
- **Test coverage** requirements met

This service layer architecture provides a scalable foundation for growing business logic while maintaining code quality and testability.