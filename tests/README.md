# Testing Guide

This directory contains all tests for the Slippi Stats Server. The testing framework is designed to be simple, reliable, and provide confidence when refactoring.

## Test Structure

```
tests/
├── README.md                    # This file - testing guide
├── conftest.py                  # Test configuration and fixtures
├── pytest.ini                  # Pytest configuration
├── test_service_layer.py        # Business logic contract tests
├── test_database_simple.py      # Database integration tests
├── test_api_endpoints.py        # API endpoint tests
├── test_web_pages.py           # Web page rendering tests
```

## Running Tests

### Test Runner Script
Use the provided test runner for easy execution:

```bash
# Run all tests
run_tests.bat

# Run specific test categories
run_tests.bat quick        # Fast service layer tests only
run_tests.bat api          # API endpoint tests
run_tests.bat web          # Web page tests  
run_tests.bat db           # Database tests
run_tests.bat service      # Service layer tests
run_tests.bat verbose      # All tests with detailed output
run_tests.bat coverage     # Tests with coverage report
```

### Manual Execution
```bash
# Activate virtual environment first
venv\Scripts\activate.bat

# Run specific test files
python -m pytest tests/test_service_layer.py -v
python -m pytest tests/test_database_simple.py -v
python -m pytest tests/test_api_endpoints.py -v

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

## Test Categories

### Service Layer Tests (`test_service_layer.py`)
**Purpose**: Contract tests for business logic functions
**Speed**: ⚡ Very Fast (no database, no HTTP)
**Coverage**: Service layer APIs and return structures

**When to add tests here:**
- New business logic functions in `api_service.py` or `web_service.py`
- Changes to service function signatures or return formats
- Core utility functions in `utils.py`

**Example:**
```python
def test_new_service_function():
    """Test that new service function maintains expected contract"""
    from backend.api_service import new_function
    
    result = new_function(test_input)
    
    # Test contract - ensure return structure doesn't change
    assert isinstance(result, dict)
    assert 'required_key' in result
    assert isinstance(result['required_key'], expected_type)
```

### Database Tests (`test_database_simple.py`)
**Purpose**: Integration tests for database operations and SQL files
**Speed**: 🔄 Medium (creates temporary databases)
**Coverage**: SQL files, database operations, data persistence

**When to add tests here:**
- New SQL files added to `backend/sql/`
- New database functions in `database.py`
- Changes to database schema
- Complex query operations

**Example:**
```python
def test_new_database_operation(self):
    """Test new database operation with real database"""
    db_manager, db_path = self.create_test_database()
    
    try:
        # Test your new database operation
        from backend.sql_manager import sql_manager
        query = sql_manager.get_query('category', 'new_query')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, test_params)
            result = cursor.fetchone()
            
            assert result is not None
            assert result['expected_column'] == expected_value
    
    finally:
        self.cleanup_test_database(db_path)
```

### API Endpoint Tests (`test_api_endpoints.py`)
**Purpose**: HTTP API integration tests
**Speed**: 🔄 Medium (creates Flask test client)
**Coverage**: API routes, request/response formats, error handling

**When to add tests here:**
- New API endpoints in `backend/routes/api_routes.py`
- Changes to API response formats
- Authentication/authorization changes
- Rate limiting changes

**Example:**
```python
def test_new_api_endpoint(self, client):
    """Test new API endpoint returns correct format"""
    response = client.get('/api/new/endpoint')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'expected_key' in data
    assert isinstance(data['expected_key'], expected_type)
```

### Web Page Tests (`test_web_pages.py`)
**Purpose**: Web page rendering and basic functionality
**Speed**: 🔄 Medium (creates Flask test client)
**Coverage**: HTML pages, template rendering, basic navigation

**When to add tests here:**
- New web pages in `backend/routes/web_routes.py`
- Changes to page templates
- New frontend components that affect page rendering

**Example:**
```python
def test_new_web_page(self, client):
    """Test new web page renders without crashing"""
    response = client.get('/new-page')
    assert response.status_code == 200
    assert b'Expected Content' in response.data
```

## Adding New Tests

### Quick Decision Guide

**I added a new service function** → Add to `test_service_layer.py`
**I added a new SQL file** → Add to `test_database_simple.py`
**I added a new API endpoint** → Add to `test_api_endpoints.py`
**I added a new web page** → Add to `test_web_pages.py`

### Service Layer Test Template
```python
def test_your_new_function():
    """Test your new service function contract"""
    from backend.api_service import your_new_function  # or web_service
    
    # Test with valid input
    result = your_new_function(valid_input)
    
    # Assert contract - what your function promises to return
    assert isinstance(result, dict)  # or list, str, etc.
    assert 'required_field' in result
    
    # Test with edge cases
    empty_result = your_new_function(empty_input)
    assert empty_result is None  # or [], {}, etc.
```

### Database Test Template
```python
def test_your_new_database_operation(self):
    """Test your new database operation"""
    db_manager, db_path = self.create_test_database()
    
    try:
        # Your test logic here
        from backend.sql_manager import sql_manager
        query = sql_manager.get_query('your_category', 'your_query')
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test insert/update/delete
            cursor.execute(query, your_test_data)
            conn.commit()
            
            # Test select/verify
            cursor.execute(verification_query)
            result = cursor.fetchone()
            
            assert result['expected_field'] == expected_value
            
    finally:
        self.cleanup_test_database(db_path)
```

### API Test Template
```python
def test_your_new_api_endpoint(self, client):
    """Test your new API endpoint"""
    # Test GET request
    response = client.get('/api/your/endpoint')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'expected_field' in data
    
    # Test POST request with data
    post_data = {'test': 'data'}
    response = client.post('/api/your/endpoint', 
                          json=post_data,
                          headers={'X-API-Key': 'test-key'})
    # Note: Will return 401 without valid API key in test environment
    assert response.status_code in [200, 401]
```

## Best Practices

### Test Naming
- **Files**: `test_[component]_[type].py` (e.g., `test_api_endpoints.py`)
- **Classes**: `Test[Component][Type]` (e.g., `TestPlayerEndpoints`)
- **Methods**: `test_[what_it_tests]` (e.g., `test_player_stats_returns_correct_format`)

### Test Structure
```python
def test_descriptive_name(self, fixtures):
    """Clear description of what this test validates"""
    # Arrange - set up test data
    test_data = create_test_data()
    
    # Act - perform the operation being tested
    result = function_under_test(test_data)
    
    # Assert - verify the results
    assert result == expected_value
    assert isinstance(result, expected_type)
```

### Test Independence
- Each test should be completely independent
- Tests should not depend on order of execution
- Use fixtures for shared setup (see `conftest.py`)
- Clean up after yourself (especially in database tests)

### What to Test
**✅ Do test:**
- Function contracts (inputs/outputs)
- Error conditions and edge cases
- Integration between components
- API response formats
- Database operations with real SQL

**❌ Don't test:**
- Implementation details that might change
- External library functionality
- Simple getters/setters
- Private methods (unless complex)

## Troubleshooting

### Common Issues

**Import errors**: Make sure `PYTHONPATH` is set correctly (test runner handles this)
**Slow tests**: Run `run_tests.bat quick` for fast feedback during development

### Debugging Tests
```bash
# Run specific test with detailed output
python -m pytest tests/test_specific.py::test_function -v -s

# Run with debugger
python -m pytest tests/test_specific.py::test_function --pdb

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=term-missing
```

### When Tests Fail
1. **Read the error message carefully** - pytest gives good error details
2. **Run the specific failing test** with `-v -s` flags for details
3. **Use print statements** in tests for debugging (they'll show with `-s`)
4. **Check if it's a contract change** - update test if business logic changed

## Integration with Development

### Before Committing
```bash
# Run quick tests for fast feedback
run_tests.bat quick

# Run all tests before major changes
run_tests.bat

# Generate coverage report
run_tests.bat coverage
```

### During Refactoring
1. **Run tests before** starting refactoring (ensure they pass)
2. **Keep tests running** during refactoring
3. **Tests failing** = you broke a contract, fix it
4. **Tests passing** = refactoring is safe

### When Adding Features
1. **Add service layer test** for business logic
2. **Add database test** if using new SQL
3. **Add API test** if creating new endpoints
4. **Add web test** if creating new pages

This testing framework gives you confidence to refactor and extend the application while maintaining stability and catching regressions early.