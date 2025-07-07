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

---

## Service Organization Approaches

We support two service organization patterns depending on complexity and team needs:

### **Approach 1: Monolithic Services** (Current - Simple)
```
backend/services/
├── api_service.py      # API business logic
└── web_service.py      # Web business logic
```

**Use when:**
- ✅ Small team (1-3 developers)
- ✅ Services under 500 lines
- ✅ Simple domain boundaries
- ✅ Rapid prototyping

### **Approach 2: Domain Services** (Recommended - Scalable)
```
backend/services/
├── README.md                    # This file
├── __init__.py                  # Backward compatibility exports
├── upload/                      # 🆕 Upload domain
│   ├── __init__.py             # Domain exports  
│   ├── schemas.py              # Data structures
│   ├── validation.py           # Business rules
│   ├── service.py              # Orchestrators
│   ├── processors.py           # Business logic
│   └── README.md              # Domain docs
├── player/                      # 🔄 Future: Player domain
└── client/                      # 🔄 Future: Client domain
```

**Use when:**
- ✅ Growing team (3+ developers)
- ✅ Services exceeding 500 lines
- ✅ Complex domain boundaries
- ✅ Need for schema standardization
- ✅ Inconsistent data formats causing issues

---

## Domain Service Pattern (NEW)

For complex domains, we use the **Domain Service Pattern** with standardized schemas to eliminate data format inconsistencies and improve maintainability.

### **Standard Domain Structure**

Every domain service follows this exact structure:

```
backend/services/{domain}/
├── __init__.py          # 🚪 PUBLIC EXPORTS - What other code can import
├── schemas.py           # 📋 DATA DEFINITIONS - Pure data structures only
├── validation.py        # ✅ VALIDATION LOGIC - Business rules and input validation  
├── service.py           # 🎯 ORCHESTRATORS - Main entry points (10-20 lines each)
├── processors.py        # ⚙️ BUSINESS LOGIC - Core operations and processing
└── README.md           # 📖 DOMAIN DOCS - Usage examples and API reference
```

### **File Responsibilities**

#### **`schemas.py` - Data Definitions ONLY**
**Purpose**: Define data structures and their serialization methods
**Contains**:
- Dataclass definitions with type hints
- Enums and constants  
- Data conversion methods (`to_dict()`, `from_upload_data()`)
- Field mappings and computed properties

**Rules**:
- ✅ Pure data structure definitions
- ✅ Data transformation methods (format conversion)
- ✅ Enum conversion helpers  
- ❌ NO validation logic
- ❌ NO business rules
- ❌ NO external dependencies (database, logging, etc.)

#### **`validation.py` - Validation Logic ONLY**
**Purpose**: Input validation and business rule enforcement
**Contains**:
- Business rule validation functions
- Input format validation
- Data integrity checks
- Custom validation exceptions

**Rules**:
- ✅ Business rule enforcement
- ✅ Input validation logic
- ✅ Data integrity checks
- ✅ Can import from schemas.py
- ❌ NO data processing (use processors.py)
- ❌ NO database operations
- ❌ NO orchestration logic

#### **`service.py` - Orchestrators ONLY**
**Purpose**: Main entry points that coordinate workflows
**Contains**:
- Public API functions (orchestrators)
- High-level error handling
- Response formatting helpers
- Workflow coordination

**Rules**:
- ✅ Orchestrator functions (10-20 lines max)
- ✅ Delegate to validation.py and processors.py
- ✅ Handle domain-level errors
- ✅ Create standardized responses
- ❌ NO complex business logic (use processors.py)
- ❌ NO direct database calls (use processors.py)
- ❌ NO detailed validation (use validation.py)

#### **`processors.py` - Business Logic ONLY**
**Purpose**: Core business operations and data processing
**Contains**:
- Business logic implementation
- Database operations
- External service calls
- Data transformation
- Side effect handling

**Rules**:
- ✅ Complex business logic
- ✅ Database operations
- ✅ External service integration
- ✅ Data processing and transformation
- ✅ Can import schemas, database, utils, config
- ❌ NO input validation (trust validation.py)
- ❌ NO orchestration logic (single responsibility)
- ❌ NO HTTP concerns (request/response handling)

#### **`__init__.py` - Public Exports ONLY**
**Purpose**: Define what other modules can import
**Contains**:
- Import statements for public functions
- `__all__` list defining public API
- Domain-level docstring

**Rules**:
- ✅ Export ONLY public orchestrator functions
- ✅ Maintain backward compatibility
- ✅ Clear domain documentation
- ❌ NO business logic
- ❌ NO complex imports

### **Domain Service Benefits**

#### **For Developers**
- ✅ **Predictable Structure** - Always know where to find/add code
- ✅ **Clear Responsibilities** - Each file has single, well-defined purpose
- ✅ **Easy Testing** - Test schemas, validation, processing independently
- ✅ **Consistent Patterns** - Same structure across all domains

#### **For Codebase**
- ✅ **Schema Standardization** - Eliminates inconsistent data formats
- ✅ **Reduced Complexity** - Large functions broken into focused pieces
- ✅ **Better Reusability** - Validation and processing logic can be reused
- ✅ **Improved Maintainability** - Easy to modify individual components

#### **For Team**
- ✅ **Faster Onboarding** - New developers know exactly how to structure code
- ✅ **Better Code Reviews** - Clear expectations for function size and responsibility
- ✅ **Easier Collaboration** - Consistent patterns reduce cognitive load
- ✅ **Scalable Architecture** - Easy to add new domains as project grows

---

## Current Services

### Core Services (Monolithic Approach)

#### `api_service.py` - API Business Logic
**Purpose**: Business logic for JSON API endpoints

**Key Responsibilities:**
- Player data processing and analysis
- ~~Game upload and file processing~~ (🔄 Moving to upload domain)
- Client registration and management
- Advanced filtering and statistics

**Major Functions:**
- ~~`process_combined_upload()` - Handle games and files upload~~ (🔄 Moved to upload domain)
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

### Domain Services (New Approach)

#### `upload/` - Upload Domain Service
**Purpose**: Handle all upload-related business logic with standardized schemas

**Key Responsibilities:**
- Combined upload processing (games + files + client info)
- Upload data validation and normalization
- Game data schema standardization
- Upload result processing and error handling

**Major Functions:**
- `process_combined_upload()` - Main upload orchestrator with schema validation

**Benefits Achieved:**
- ✅ **Eliminates result vs placement confusion** - Standardized in schemas
- ✅ **Computed display fields** - `stage_name`, `game_length_seconds` automatically available
- ✅ **Type safety** - Clear data contracts with validation
- ✅ **Consistent error handling** - Structured validation messages

---

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

---

## Import Rules & Dependencies

### Monolithic Services
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

### Domain Services
Domain services have additional import rules:

```python
# ✅ Domain files can import:
# schemas.py: No external imports (pure data structures)
# validation.py: Can import from .schemas
# service.py: Can import from .validation, .processors
# processors.py: Can import from .schemas, backend.database, backend.utils, backend.config

# ✅ Cross-domain communication:
from backend.services.other_domain import public_function  # Use public APIs only

# ❌ Domain files cannot import:
from .processors import private_function  # Don't import private functions across files
from backend.routes import *              # Routes import services, not vice versa
```

### Service Communication
When services need to share functionality:
1. **Extract to utils** - If it's a pure function without side effects
2. **Extract to database** - If it's data access logic
3. **Use domain public APIs** - Import from other domain's public exports
4. **Create shared service** - If it's complex business logic used by multiple domains

---

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

### Domain Service Testing
Domain services add schema-focused testing:

```python
def test_domain_schema_standardization():
    """Test that schemas eliminate data format inconsistencies."""
    # Test various input formats are normalized
    formats = [
        {'player_tag': 'P1', 'result': 'Win'},
        {'player_tag': 'P1', 'placement': 1},
        {'player_tag': 'P1', 'result': 'win', 'placement': 2}
    ]
    
    for format_data in formats:
        schema_obj = PlayerSchema.from_input_data(format_data)
        assert isinstance(schema_obj.result, GameResult)  # Standardized enum
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

---

## Migration Path

### When to Migrate to Domain Services

**Immediate candidates:**
- ✅ **Upload domain** - Complex data formats, validation issues
- 🔄 **Player domain** - Multiple data processing functions
- 🔄 **Client domain** - Registration and management logic

**Indicators for migration:**
- Service file exceeds 500 lines
- Inconsistent data formats causing bugs
- Multiple developers working on same domain
- Complex validation requirements
- Need for schema standardization

### Migration Process

#### **Phase 1: Create Domain Structure**
1. Create domain directory with 5 required files
2. Implement schemas first (data structures)
3. Move validation logic to validation.py
4. Create orchestrators in service.py
5. Move business logic to processors.py

#### **Phase 2: Update Integration Points**
1. Update route imports to use domain services
2. Add domain exports to main services `__init__.py`
3. Update cross-service dependencies
4. Add comprehensive tests

#### **Phase 3: Clean Up**
1. Remove old functions from monolithic services
2. Update documentation
3. Monitor for any integration issues

### Backward Compatibility
During migration, maintain compatibility through main services `__init__.py`:

```python
# backend/services/__init__.py
# Legacy imports (monolithic services)
from .api_service import process_detailed_player_data
from .web_service import prepare_homepage_data

# New domain imports
from .upload import process_combined_upload

__all__ = [
    # Domain services (new)
    'process_combined_upload',
    
    # Legacy services (during transition)
    'process_detailed_player_data',
    'prepare_homepage_data',
]
```

---

## Adding New Services

### 1. When to Create a New Service
Create a new service when:
- **Domain separation** - Distinct business domain (users, tournaments, etc.)
- **Size concerns** - Existing service exceeds 500 lines
- **Schema needs** - Need standardized data formats
- **Team organization** - Different teams own different domains
- **External integration** - Service handles external API integration

### 2. Monolithic Service Creation Template

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

### 3. Domain Service Creation Process

#### **Step 1: Create Directory Structure**
```bash
mkdir backend/services/{domain_name}
touch backend/services/{domain_name}/__init__.py
touch backend/services/{domain_name}/schemas.py
touch backend/services/{domain_name}/validation.py
touch backend/services/{domain_name}/service.py
touch backend/services/{domain_name}/processors.py
touch backend/services/{domain_name}/README.md
```

#### **Step 2: Implement in Order**
1. **Schemas first** - Define data structures
2. **Validation second** - Business rules and input validation
3. **Processors third** - Core business logic
4. **Service fourth** - Orchestrators that coordinate everything
5. **Exports last** - Public API in `__init__.py`

See the Domain Service Pattern section above for detailed file responsibilities.

### 4. Service Registration
When creating new services, update:
1. **Import in routes** - Import service functions in relevant route files
2. **Update main services init** - Add to `backend/services/__init__.py`
3. **Update tests** - Add service layer tests for new functions
4. **Document in README** - Update this README with new service description

---

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

---

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

---

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

---

## Contributing Guidelines

### Code Style
- Follow **orchestrator pattern** for complex functions
- Use **descriptive function names** that indicate business purpose
- Implement **comprehensive error handling**
- Add **type hints** for function parameters and returns
- Include **docstrings** with Args and Returns sections

### Domain Service Requirements
- **Schemas as requirement** - Every domain must have standardized schemas
- **File separation** - Strict separation between schemas, validation, service, processors
- **Public API design** - Only export orchestrator functions
- **Backward compatibility** - Maintain imports during migration

### Testing Requirements
- **Service layer tests** for all public functions
- **Schema tests** for data format standardization
- **Helper function tests** for complex validation or processing logic
- **Error scenario tests** for all expected error conditions
- **Integration tests** for complete workflows

### Review Process
- **Code reviews** should verify orchestrator pattern usage
- **Schema validation** - Ensure schemas eliminate data format inconsistencies
- **Performance impact** consideration for new service functions
- **Error handling** completeness and consistency
- **Test coverage** requirements met

This service layer architecture provides a scalable foundation for growing business logic while maintaining code quality, testability, and eliminating data format inconsistencies through standardized schemas.