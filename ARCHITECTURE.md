# Architecture Overview

This document provides a high-level overview of the Slippi Stats Server architecture and the refactoring journey that led to the current production-ready design.

## Executive Summary

Slippi Stats Server has evolved from a monolithic application into a **modern, service-oriented architecture** with clear separation of concerns, comprehensive testing, and production-ready observability. The current architecture enables confident refactoring, rapid feature development, and long-term maintainability.

## Architecture Evolution

### Before: Monolithic Structure (Legacy)
```
├── app.py                 # 🔴 Large monolithic file (500+ lines)
│   ├── Flask setup        # Mixed with business logic
│   ├── Route handlers     # Mixed with data processing
│   ├── Database operations # Embedded SQL strings
│   ├── Business logic     # Tightly coupled
│   └── Error handling     # Scattered throughout
├── config.py              # ✅ Already modular
└── database.py            # ✅ Already modular
```

**Problems with Legacy Architecture:**
- **Tight Coupling**: Business logic mixed with HTTP handling and database operations
- **Embedded SQL**: Database queries scattered throughout Python files as strings
- **Difficult Testing**: Monolithic structure made unit testing challenging
- **Poor Separation**: No clear boundaries between different responsibilities
- **Hard to Maintain**: Changes often affected multiple unrelated areas

### After: Service-Oriented Architecture (Current) ✅
```
├── app.py                      # ✅ Lightweight entry point (40 lines)
├── backend/
│   ├── routes/                 # ✅ HTTP layer - thin controllers
│   │   ├── web_routes.py       # HTML page endpoints
│   │   ├── api_routes.py       # JSON API endpoints
│   │   ├── static_routes.py    # File serving
│   │   └── error_handlers.py   # HTTP error responses
│   ├── web_service.py          # ✅ Web business logic
│   ├── api_service.py          # ✅ API business logic
│   ├── utils.py                # ✅ Shared utilities
│   ├── database.py             # ✅ Pure data access
│   ├── sql_manager.py          # ✅ SQL file management
│   ├── config.py               # ✅ Configuration management
│   └── sql/                    # ✅ External SQL files
│       ├── schema/             # Database structure
│       ├── games/              # Game operations
│       ├── clients/            # Client management
│       ├── api_keys/           # Authentication
│       ├── files/              # File operations
│       └── stats/              # Analytics queries
├── frontend/                   # ✅ Component-based architecture
│   ├── components/             # Self-contained UI packages
│   ├── layouts/                # Component orchestration
│   └── pages/                  # Page-specific functionality
└── tests/                      # ✅ Architecture-aligned testing
    ├── test_service_layer.py   # Business logic contracts
    ├── test_database_simple.py # SQL and database integration
    ├── test_api_endpoints.py   # HTTP API testing
    └── test_web_pages.py       # Page rendering testing
```

## Current Architecture Benefits

### 1. **Maintainability** 🔧
- **Clear Module Boundaries**: Each file has a single, well-defined responsibility
- **External SQL Management**: Database queries are version-controlled, readable, and organized
- **Component Isolation**: Frontend components are self-contained with clear interfaces
- **Enforced Import Rules**: Strict hierarchy prevents architectural violations

### 2. **Testability** 🧪
- **Service Layer Tests**: Fast business logic validation (runs in <1 second)
- **Integration Tests**: Database and API endpoint coverage with real data
- **Component Tests**: UI behavior validation independent of business logic
- **Architecture Alignment**: Tests respect module boundaries and contracts

### 3. **Developer Experience** 👨‍💻
- **Hot Reloading**: SQL queries can be updated without application restart
- **Clear Guidelines**: Comprehensive documentation for each architectural layer
- **Quick Feedback**: Fast test suite provides immediate validation during development
- **Predictable Patterns**: Consistent conventions across all modules

### 4. **Scalability** 📈
- **Service Boundaries**: Easy to extract microservices if needed in the future
- **Component Reusability**: Frontend components work across different pages and layouts
- **External SQL**: Database queries are optimized, organized, and discoverable
- **Horizontal Scaling**: Clean separation enables database read replicas and caching

### 5. **Observability** 📊
- **Distributed Tracing**: Request flow visibility across all application layers
- **Business Metrics**: Games processed, files uploaded, API usage tracking
- **Performance Monitoring**: Response times, database query performance, error rates
- **Development-Friendly**: Local observability stack with Docker for debugging

## Architectural Principles

### Backend: "Services Process, Database Stores, Utils Help, SQL Separates"

#### **Service Layer** (`web_service.py`, `api_service.py`)
- **Responsibility**: Business logic and request processing
- **Imports**: Can use `database`, `utils`, `config` modules
- **Testing**: Fast contract tests validate inputs/outputs
- **Principles**: Single responsibility, clear interfaces, no direct SQL

#### **Database Layer** (`database.py` + `sql/`)
- **Responsibility**: Pure data access using external SQL files
- **Imports**: Only `config` and `sql_manager`
- **Testing**: Integration tests with real SQLite databases
- **Principles**: No business logic, parameterized queries, organized SQL

#### **Utils Layer** (`utils.py`)
- **Responsibility**: Shared data processing and helper functions
- **Imports**: Only `config` module
- **Testing**: Function-level tests for data transformation
- **Principles**: Stateless, reusable, well-documented functions

#### **Routes Layer** (`routes/*.py`)
- **Responsibility**: HTTP request/response handling only
- **Imports**: Services and error handling utilities
- **Testing**: HTTP endpoint tests with request/response validation
- **Principles**: Thin controllers, delegate to services, consistent error handling

### Frontend: "Components Do, Layouts Share, Pages Orchestrate"

#### **Component Layer** (`components/*/`)
- **Responsibility**: Self-contained UI behavior and styling
- **Assets**: Own CSS/JS files with auto-initialization
- **Testing**: Independent component behavior validation
- **Principles**: Single responsibility, reusable, no business logic

#### **Layout Layer** (`layouts/*.html`)
- **Responsibility**: Component orchestration and page structure
- **Assets**: No CSS/JS files - templates only
- **Testing**: Integration via page rendering tests
- **Principles**: Composition over inheritance, component coordination

#### **Page Layer** (`pages/*/`)
- **Responsibility**: Business logic, API calls, component coordination
- **Assets**: Page-specific CSS/JS with DOMContentLoaded patterns
- **Testing**: Full page rendering and functionality tests
- **Principles**: Orchestration, error handling, user experience

## Module Import Hierarchy

The architecture enforces strict import rules to prevent circular dependencies and maintain clean boundaries:

```
┌─────────────────────────────────────────────┐
│                  app.py                     │ ← Top Level
│           (Flask setup only)                │
└─────────────────┬───────────────────────────┘
                  │ can import ↓
┌─────────────────┴───────────────────────────┐
│              routes/*.py                    │ ← HTTP Layer
│        (Blueprint registration)             │
└─────────────────┬───────────────────────────┘
                  │ can import ↓
┌─────────────────┴───────────────────────────┐
│        web_service.py + api_service.py      │ ← Business Logic
│           (Service layer)                   │
└─────────────────┬───────────────────────────┘
                  │ can import ↓
┌─────────────────┴───────────────────────────┐
│    utils.py + database.py + config.py      │ ← Foundation
│         (Shared utilities)                  │
└─────────────────┬───────────────────────────┘
                  │ uses ↓
┌─────────────────┴───────────────────────────┐
│              sql/ directory                 │ ← Data Queries
│          (External SQL files)               │
└─────────────────────────────────────────────┘
```

**Enforced Rules:**
- ✅ **Services** can import: `database`, `utils`, `config`
- ✅ **Utils** can import: `config` only
- ✅ **Database** can import: `config`, `sql_manager` only
- ✅ **Routes** can import: services and utilities
- ❌ **No circular imports** between any modules
- ❌ **Lower layers cannot import** higher layers

## Data Flow Architecture

### Request Processing Flow
```
HTTP Request → Routes → Services → Database → SQL Files → Response
     ↓            ↓         ↓          ↓         ↓
   Validation   Business   Utils    External   Formatted
   & Routing     Logic   Functions   Queries     Data
```

**Detailed Flow:**
1. **Routes** receive HTTP request and validate parameters
2. **Routes** delegate to appropriate **Service** function
3. **Service** processes business logic using **Utils** for data transformation
4. **Service** calls **Database** functions for data persistence/retrieval
5. **Database** loads appropriate **SQL file** using sql_manager
6. **Database** executes SQL with parameters and returns raw data
7. **Service** formats data using **Utils** and returns to **Routes**
8. **Routes** render template or return JSON response

### Component Interaction Flow (Frontend)
```
Page JavaScript → Component APIs → DOM Manipulation → User Interface
      ↓               ↓              ↓                    ↓
  Business Logic   UI Behavior   Visual Updates     User Experience
```

## Key Innovations

### 1. **External SQL File Management**
- **Dynamic Discovery**: Add `.sql` files and they become available automatically
- **Template Support**: Use `{variable}` placeholders for flexible queries
- **Category Organization**: Logical grouping by functionality (games, clients, etc.)
- **Version Control**: SQL changes tracked in git like code
- **Hot Reloading**: Update queries without application restart in development

### 2. **Component-Based Frontend**
- **Asset Ownership**: Components manage their own CSS/JS files
- **Auto-Initialization**: Components work immediately when included
- **Template Macros**: Clean interfaces between layouts and pages
- **Progressive Enhancement**: Core functionality works without JavaScript

### 3. **Architecture-Aligned Testing**
- **Service Layer Tests**: Fast contract validation for business logic
- **Integration Tests**: Real database and HTTP testing for confidence
- **Clear Categories**: Each test type has specific purpose and speed characteristics
- **Refactoring Safety**: Tests validate contracts, not implementation details

## Production Readiness

### Current Status ✅
- **Service-Oriented Architecture**: Complete and stable
- **External SQL Management**: All queries externalized and organized
- **Blueprint-Based Routing**: Modular HTTP handling implemented
- **Component-Based Frontend**: Clear separation of concerns achieved
- **Comprehensive Testing**: 51% coverage with multiple test categories
- **Observability**: OpenTelemetry tracing and metrics implemented

### Performance Characteristics
- **Service Layer Tests**: < 1 second execution time
- **Database Operations**: Optimized with appropriate indexes
- **Frontend Components**: Progressive enhancement with minimal JavaScript
- **API Responses**: Structured error handling and consistent formatting

### Scalability Features
- **Database**: SQLite with external query management (easy to migrate to PostgreSQL)
- **Services**: Clear boundaries enable microservice extraction if needed
- **Frontend**: Component reusability reduces duplication and maintenance
- **Observability**: Production-ready monitoring and alerting capabilities

## Future Architecture Considerations

### Potential Enhancements
1. **Caching Layer**: Redis integration for expensive query result caching
2. **Query Performance Monitoring**: Track slow queries and optimization opportunities
3. **Database Migration System**: Versioned schema changes with rollback capability
4. **API Versioning**: Support for multiple API versions as the system evolves

### Migration Paths
- **Database**: External SQL files make PostgreSQL migration straightforward
- **Microservices**: Service boundaries enable gradual extraction if needed
- **Frontend Framework**: Component architecture provides clear migration path
- **Deployment**: Docker support for containerized deployment

## Conclusion

The current architecture represents a **significant improvement** over the legacy monolithic structure. It provides:

- **Developer Confidence**: Comprehensive testing enables fearless refactoring
- **Maintainability**: Clear boundaries and external SQL make changes predictable
- **Scalability**: Service-oriented design supports future growth
- **Quality**: Enforced patterns prevent architectural violations

This architecture serves as a **solid foundation** for continued development and provides clear patterns for contributors of all experience levels.

## Related Documentation

- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Backend Details**: [backend/README.md](backend/README.md)
- **Frontend Details**: [frontend/README.md](frontend/README.md)
- **Testing Guide**: [tests/README.md](tests/README.md)
- **SQL Management**: [backend/sql/README.md](backend/sql/README.md)