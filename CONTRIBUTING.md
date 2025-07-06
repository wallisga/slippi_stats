# Contributing to Slippi Stats Server

Thank you for your interest in contributing to Slippi Stats Server! This guide will help you understand the project structure and contribution process.

## Project Overview

Slippi Stats Server is a comprehensive web application for collecting, storing, and analyzing Super Smash Bros. Melee game data. The project follows a **service-oriented architecture** with clear separation of concerns and modern development practices.

## Architecture

### Backend Architecture ✅ COMPLETE
**Current State:** Production-ready service-oriented architecture

**Achieved Architecture:**
```
├── app.py                    # Flask application entry point (lightweight)
├── backend/
│   ├── routes/              # ✅ Blueprint-based route handlers
│   │   ├── web_routes.py    # ✅ HTML page routes
│   │   ├── api_routes.py    # ✅ JSON API routes
│   │   ├── static_routes.py # ✅ File serving routes
│   │   └── error_handlers.py # ✅ HTTP error handlers
│   ├── web_service.py       # ✅ Web page business logic
│   ├── api_service.py       # ✅ API business logic
│   ├── utils.py             # ✅ Shared utilities
│   ├── config.py            # ✅ Configuration management
│   ├── database.py          # ✅ Data access layer
│   ├── sql_manager.py       # ✅ Dynamic SQL file management
│   └── sql/                 # ✅ External SQL files organized by category
```

**Key Achievements:**
- **Service-Oriented Design**: Clean separation between web and API business logic
- **External SQL Management**: All SQL queries in organized external files with dynamic discovery
- **Blueprint-Based Routing**: Modular route organization with thin controllers
- **Strict Import Hierarchy**: Enforced module dependencies prevent circular imports
- **Comprehensive Testing**: Architecture-aligned testing framework with 51% coverage

### Frontend Architecture ✅ COMPLETE
**Current State:** Component-based architecture with clear separation of concerns

**Achieved Structure:**
```
frontend/
├── base.html              # Foundation template
├── base.css               # Global styles and utilities
├── base.js                # Global utilities and error handling
├── components/            # ✅ Self-contained UI component packages
│   ├── component_name/
│   │   ├── _component_name.html # Template with macros + asset imports
│   │   ├── component_name.css   # Component-specific styles (BEM)
│   │   └── component_name.js    # Component behavior (auto-init)
├── layouts/               # ✅ Component orchestration templates
│   └── layout_name.html   # Layout templates (no assets, just composition)
└── pages/                 # ✅ Page-specific content and business logic
    ├── page_name/
    │   ├── page_name.html # Page template extending layout
    │   ├── page_name.css  # Page-specific styles
    │   └── page_name.js   # Page-specific behavior (DOMContentLoaded)
```

**Key Principles:**
- **"Components Do, Layouts Share, Pages Orchestrate"** - Clear responsibility boundaries
- **Progressive Enhancement**: Works without JavaScript, enhanced with it
- **Asset Ownership**: Components own their assets, pages own theirs
- **Template Inheritance**: `base.html` → `layouts/*.html` → `pages/*.html`

## Types of Contributions

### 🐛 Bug Fixes
- **Small fixes** welcome without prior discussion
- **Large fixes** should have an issue first
- **Include reproduction steps** in your PR description
- **Follow existing patterns** for error handling and validation

### ✨ New Features
- **Create an issue first** to discuss the feature
- **Follow existing architecture patterns** for similar functionality
- **Update documentation** for user-facing features
- **Add tests** that align with the architectural boundaries

### 📚 Documentation
- **Improve existing docs** - fix typos, add examples, clarify instructions
- **Add missing docs** - document undocumented features or edge cases
- **Update architecture docs** when making structural changes
- **Keep cross-references accurate** between different documentation files

### 🏗️ Refactoring
- **Follow the established architecture** - service-oriented backend, component-based frontend
- **Maintain backward compatibility** whenever possible
- **Use the testing framework** to ensure refactoring doesn't break contracts
- **Update documentation** to reflect any architectural improvements

## Development Guidelines

### Backend Development
- **Services Process**: Business logic belongs in `web_service.py` or `api_service.py`
- **Database Stores**: Data access only in `database.py` using external SQL files
- **Utils Help**: Shared utilities in `utils.py` following existing patterns
- **SQL Separates**: All database queries as external `.sql` files in organized categories
- **Routes Delegate**: Route handlers should be thin and delegate to services

### Frontend Development
- **Components Do**: Self-contained UI behavior with auto-initialization
- **Layouts Share**: Component orchestration and page structure definition
- **Pages Orchestrate**: Business logic, API calls, and component coordination
- **Asset Management**: Components and pages manage their own CSS/JS assets
- **Progressive Enhancement**: Core functionality works without JavaScript

### Testing
- **Service Layer Tests**: Fast contract tests for business logic
- **Database Tests**: Integration tests for SQL files and database operations
- **API Tests**: HTTP endpoint tests for request/response validation
- **Web Tests**: Page rendering and navigation tests
- **Follow Test Categories**: Add tests to appropriate category based on what you're testing

## Getting Started

### Prerequisites
- Python 3.8+
- SQLite 3 (included with Python)
- Modern web browser with JavaScript enabled
- Git for version control

### Setup Process
1. **Fork the repository** and create a feature branch
2. **Set up development environment** using `start_dev.bat` or manual setup
3. **Understand the architecture** by reading the relevant README files
4. **Make your changes** following the established patterns
5. **Test thoroughly** using `run_tests.bat` with appropriate test categories
6. **Update documentation** if your changes affect user-facing functionality
7. **Submit a pull request** with clear description of changes

### Development Environment
```bash
# Windows (recommended)
start_dev.bat

# Manual setup (all platforms)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt
python app.py
```

### Architecture Documentation
- **High-level overview**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Backend development**: [backend/README.md](backend/README.md)
- **Routes organization**: [backend/routes/README.md](backend/routes/README.md)
- **SQL query management**: [backend/sql/README.md](backend/sql/README.md)
- **Frontend architecture**: [frontend/README.md](frontend/README.md)
- **Component development**: [frontend/components/README.md](frontend/components/README.md)
- **Layout development**: [frontend/layouts/README.md](frontend/layouts/README.md)
- **Page development**: [frontend/pages/README.md](frontend/pages/README.md)
- **Testing guidelines**: [tests/README.md](tests/README.md)

## Adding New Features

### New Web Page
1. Add route to `backend/routes/web_routes.py` with thin handler
2. Add business logic to `backend/web_service.py` following existing patterns
3. Create page template in `frontend/pages/` extending appropriate layout
4. Add any new SQL queries to appropriate `backend/sql/` category
5. Add observability decorators (`@trace_function`) for monitoring
6. **Add tests**: Service layer contract test + web page rendering test

### New API Endpoint
1. Add route to `backend/routes/api_routes.py` with `@trace_api_endpoint` decorator
2. Add business logic to `backend/api_service.py` with `@trace_function` decorator
3. Add any new SQL queries to appropriate `backend/sql/` category
4. Add metrics for business events and performance tracking
5. Update API documentation in README.md
6. **Add tests**: Service layer contract test + API endpoint test

### New Database Queries
1. Create `.sql` file in appropriate `backend/sql/` category directory
2. Use the query via `sql_manager.get_query()` in database functions
3. Add `@trace_database_operation` decorator for performance monitoring
4. No Python code changes needed - queries are discovered automatically
5. **Add tests**: Database integration test for new query functionality

### New Frontend Components
1. Create component package in `frontend/components/` following the established structure
2. Implement component following **"Components Do"** principle (self-contained behavior)
3. Add component to layouts via `{% from %}` and `{% include %}` directives
4. Test component independence and reusability across different pages
5. **Add tests**: Web page test for component integration

### New Utility Functions
1. Add function to `backend/utils.py` following established data processing patterns
2. Ensure function follows single responsibility principle
3. Add appropriate logging and error handling
4. **Add tests**: Utils function test covering expected inputs/outputs and edge cases

## Test-Driven Development Workflow

The project uses a comprehensive testing framework aligned with the architecture:

1. **Identify the change**: Determine which architectural layer is affected
2. **Add service layer test**: If business logic is involved (fast feedback)
3. **Add integration test**: If database, API, or upload functionality is involved
4. **Add utils test**: If data processing utilities are involved
5. **Run quick tests**: `run_tests.bat quick` during development for fast feedback
6. **Run full tests**: `run_tests.bat` before committing changes
7. **Check coverage**: `run_tests.bat coverage` to ensure coverage goals are met

### Test Categories
- **Quick Tests** (`run_tests.bat quick`): Service layer contract tests for rapid development
- **API Tests** (`run_tests.bat api`): HTTP endpoint testing
- **Database Tests** (`run_tests.bat db`): SQL file and database integration testing
- **Web Tests** (`run_tests.bat web`): Page rendering and navigation testing
- **Coverage** (`run_tests.bat coverage`): Generate coverage reports

## Code Quality Standards

### Code Style
- **Python**: Follow PEP 8 guidelines
- **Frontend**: Use established component patterns with BEM CSS methodology
- **SQL**: Use clear, formatted queries with appropriate comments
- **Documentation**: Keep README files updated and cross-references accurate

### Performance
- **Database**: Use appropriate indexes and efficient query patterns
- **Frontend**: Leverage component caching and progressive enhancement
- **Observability**: Use tracing decorators for monitoring performance

### Security
- **API Authentication**: Use established API key patterns
- **Input Validation**: Validate all user inputs at service layer
- **SQL Injection**: Use parameterized queries (enforced by external SQL files)

## Pull Request Process

1. **Create descriptive PR title** summarizing the change
2. **Include detailed description** explaining the motivation and implementation
3. **Reference related issues** using GitHub issue linking
4. **Ensure tests pass** - all test categories should pass
5. **Update documentation** if the change affects user-facing functionality
6. **Request review** from maintainers
7. **Address feedback** promptly and professionally
8. **Maintain clean commit history** - squash commits if requested

## Getting Help

### Resources
- **Project README**: Architecture overview and setup instructions
- **Module READMEs**: Detailed documentation for each architectural layer
- **Existing code**: Follow established patterns in similar functionality
- **Test examples**: Use existing tests as templates for new tests

### Questions and Support
- **Create an issue** for questions about contributing or architecture
- **Check existing issues** before creating new ones
- **Be specific** about your development environment and steps taken
- **Include relevant code snippets** and error messages

### Common Issues
- **Virtual environment problems**: Try the Windows batch script or recreate venv
- **Database issues**: Delete existing `.db` files and reinitialize with `python app.py`
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **Port conflicts**: Check if port 5000 is available or change in `backend/config.py`
- **Test failures**: Run specific test categories to isolate issues

## Junior Developer Guidance

The architecture is designed to be approachable for developers of all experience levels:

1. **Start with Service Layer**: Business logic is isolated and easily testable
2. **Use Test Categories**: Clear guidelines on where to add tests for different types of changes
3. **Follow Import Rules**: Strict hierarchy prevents architectural violations and maintains code quality
4. **Use Documentation Templates**: Comprehensive guides and examples for each architectural layer
5. **Get Quick Feedback**: Fast test suite provides immediate validation during development
6. **Incremental Learning**: Architecture documentation provides deep-dive information when needed

## Code of Conduct

- **Be respectful** and professional in all interactions
- **Welcome newcomers** and help them understand the architecture
- **Focus on the code** not the person when giving feedback
- **Be patient** with the review process and questions from other contributors
- **Assume good intentions** from all contributors
- **Celebrate contributions** of all sizes - documentation fixes are just as valuable as new features

## Observability and Monitoring

The project includes comprehensive observability features:

- **Distributed Tracing**: OpenTelemetry instrumentation across all layers
- **Business Metrics**: Custom metrics for games processed, API usage, and performance
- **Error Tracking**: Comprehensive error handling with structured logging
- **Performance Monitoring**: Database query performance and response time tracking

When adding new features, follow the established observability patterns using the provided decorators and metrics.

Thank you for contributing to Slippi Stats Server! Your contributions help make the Melee community's data analysis capabilities better for everyone. 🎮