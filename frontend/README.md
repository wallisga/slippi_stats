# Frontend Architecture

This document defines the frontend architecture, conventions, and patterns used in the Slippi Stats application. The frontend follows a **component-based architecture** with clear separation of concerns.

## Core Principle: "Components Do, Layouts Share, Pages Orchestrate"

### Layer Responsibilities

#### **Component JavaScript** (`components/*/component.js`)
- **✅ DO**: Self-contained UI behavior, DOM manipulation, event handling
- **✅ DO**: Provide simple APIs and callbacks  
- **✅ DO**: Auto-initialize when included
- **❌ DON'T**: Make API calls, know about other components, handle business logic

#### **Layout Templates** (`layouts/*.html`) 
- **✅ DO**: Import and orchestrate components via `{% from %}` and `{% include %}`
- **✅ DO**: Define page structure and navigation patterns
- **❌ DON'T**: Have their own CSS/JS files, contain business logic

#### **Page JavaScript** (`pages/*/page.js`)
- **✅ DO**: Orchestrate components, API calls, business logic, data management
- **✅ DO**: Connect components together for page goals
- **❌ DON'T**: Direct DOM manipulation (use components), low-level library code

### Decision Matrix

| Functionality | Component | Layout | Page |
|---|---|---|---|
| Chart.js wrapper | ✅ | ❌ | ❌ |
| API calls | ❌ | ❌ | ✅ |
| DOM manipulation | ✅ | ❌ | ❌ |
| Business logic | ❌ | ❌ | ✅ |
| Error handling | 🔧 Local | ❌ | ✅ |
| Data transformation | 🔧 Display | ❌ | ✅ |
| Event coordination | ❌ | ❌ | ✅ |
| Loading states | 🔧 Local | ❌ | ✅ |
| Component orchestration | ❌ | ✅ | ❌ |

**Legend:** ✅ Primary responsibility, 🔧 Helper/Service, ❌ Not responsible

## Overview

The frontend is organized into four distinct layers, each with specific responsibilities:

1. **Base Layer** - Foundation assets (Bootstrap + global utilities)
2. **Component Layer** - Self-contained, reusable UI packages
3. **Layout Layer** - Component orchestration and page structure
4. **Page Layer** - Content-specific functionality and styling

## Directory Structure

```
frontend/
├── base.html                    # Foundation template
├── base.css                     # Global styles and utilities
├── base.js                      # Global utilities and error handling
├── components/                  # Self-contained component packages
│   ├── component_name/
│   │   ├── _component_name.html # Template with macros + asset imports
│   │   ├── component_name.css   # Component-specific styles
│   │   └── component_name.js    # Component behavior (auto-initialization)
├── layouts/                     # Layout templates (component orchestration)
│   └── layout_name.html         # Layout template extending base (templates only)
└── pages/                       # Page-specific content and assets
    ├── page_name/
    │   ├── page_name.html       # Page template extending layout
    │   ├── page_name.css        # Page-specific styles
    │   └── page_name.js         # Page-specific behavior (DOMContentLoaded)
```

## Architectural Principles

### 1. **Separation of Concerns**
- **Base**: Foundation only (Bootstrap + core utilities)
- **Components**: Self-contained packages with single responsibility
- **Layouts**: Orchestrate components, define page structure (templates only)
- **Pages**: Content-specific functionality and business logic only

### 2. **Asset Management**
- **Components manage their own assets** (CSS + JS)
- **Layouts import components** via `{% from %}` and `{% include %}`
- **Pages import only page-specific assets**
- **No asset duplication** - each file loaded once

### 3. **Template Inheritance Flow**
```
base.html → layouts/*.html → pages/*.html
```

### 4. **Component Import Rules**
- ✅ **Layouts** can import components
- ✅ **Components** manage their own assets
- ✅ **Pages** use macros provided by layouts
- ❌ **Pages** should NOT import components directly
- ❌ **Components** should NOT import other components

## Base Layer

### Purpose
Provides the minimal foundation shared by all pages.

### Files
- **`base.html`** - Foundation template structure
- **`base.css`** - Global styles, CSS variables, Bootstrap customizations
- **`base.js`** - Global utilities, error handling, common functions

### Responsibilities
- HTML5 document structure and Bootstrap integration
- Core navigation shell and global JavaScript utilities
- Global error handling and common CSS variables
- Foundation for all responsive design

### Example: Global Utilities (`base.js`)
```javascript
// Global utilities available on all pages
window.SlippiUtils = {
    encodePlayerTag: function(tag) { return encodeURIComponent(tag); },
    formatTimeAgo: function(date) { /* time formatting logic */ },
    showLoading: function(element) { /* loading state logic */ }
};

// Global error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});
```

## Component Layer

### Purpose
Self-contained, reusable UI packages with single responsibility.

### Component Package Structure
Each component is a complete package:
```
components/component_name/
├── _component_name.html     # Template + macros + asset imports
├── component_name.css       # Component-specific styles
└── component_name.js        # Component behavior
```

### Responsibilities
- **Encapsulate specific UI behavior** that can be reused across pages
- **Manage their own styling and interactions** 
- **Provide simple APIs** through macros and JavaScript methods
- **Auto-initialize** when included, handle their own lifecycle

### Example: Search Component
```javascript
// components/search/search.js
class UnifiedSearch {
    constructor() {
        this.init();
    }
    
    navigateToPlayer(playerCode) {
        // Pure UI logic - no business logic
        window.location.href = `/player/${encodeURIComponent(playerCode)}`;
    }
    
    filterPlayers() {
        // Component-specific filtering logic
    }
}

// Auto-initialize when component loads
const unifiedSearch = new UnifiedSearch();
```

### Component Template Pattern
```jinja2
{# Component manages its own assets #}
<link rel="stylesheet" href="{{ url_for('static', filename='components/component_name/component_name.css') }}">
<script src="{{ url_for('static', filename='components/component_name/component_name.js') }}"></script>

{# Component macros #}
{% macro component_function(param1, param2="default") %}
<div class="component-name" data-component="component_name">
    {{ param1 }}
</div>
{% endmacro %}
```

## Layout Layer

### Purpose
Orchestrate components and define page structure through template composition only.

### Responsibilities
- **Import and configure components** for use by pages
- **Define page structure and navigation** patterns
- **Provide component macros to pages** via `{% from %}` imports
- **Template composition only** - no assets or business logic

### Example: Layout Template Only
```jinja2
{% extends "base.html" %}

{# Import component macros #}
{% from 'components/search/_search.html' import navbar_search %}
{% from 'components/cards/_cards.html' import stat_card %}

{# Include components for asset loading #}
{% include 'components/search/_search.html' %}
{% include 'components/cards/_cards.html' %}

{% block nav_extras %}
{# Use component macros #}
{{ navbar_search(true) }}
{% endblock %}

{% block layout_js %}
{# Component JS loaded by includes above - no layout JS files #}
{% endblock %}
```

If you need shared functionality across pages in a layout family, create a **shared utility component** instead:

```jinja2
{# Example: components/player_utils/_player_utils.html #}
<script src="{{ url_for('static', filename='components/player_utils/player_utils.js') }}"></script>

{% macro player_api_helper() %}
{# Component provides the shared functionality #}
{% endmacro %}
```

### Layout Template Pattern
```jinja2
{% extends "base.html" %}

{# Import component macros #}
{% from 'components/search/_search.html' import navbar_search %}
{% from 'components/cards/_cards.html' import stat_card %}

{# Include components for asset loading #}
{% include 'components/search/_search.html' %}
{% include 'components/cards/_cards.html' %}

{% block nav_extras %}
{# Use component macros #}
{{ navbar_search(true) }}
{% endblock %}

{% block layout_js %}
{# Component JS loaded by includes above - no layout-specific JS #}
{% endblock %}
```

## Page Layer

### Purpose
Content-specific functionality, business logic, and orchestration of components.

### Page Package Structure
```
pages/page_name/
├── page_name.html           # Page template extending layout
├── page_name.css            # Page-specific styles
└── page_name.js             # Page-specific behavior
```

### Responsibilities
- **Orchestrate components** to achieve page goals
- **Handle page-specific business logic** and data management
- **Make API calls** (using layout services when available)
- **Connect components together** through callbacks and data flow

### Example: Page Orchestration
```javascript
// pages/player_detailed/player_detailed.js
document.addEventListener('DOMContentLoaded', async function() {
    // 1. Get page data
    const pageData = getPageDataFromTemplate();
    
    // 2. Initialize page-specific components
    initializePlayerTitle(pageData);
    
    // 3. Connect component interactions
    if (window.advancedFilters) {
        window.advancedFilters.onFilterChange(handleFilterChange);
    }
    
    // 4. Load initial data
    await loadInitialData();
});

// Business logic - handle API calls directly in page
async function handleFilterChange(filters) {
    try {
        // Direct API call - no layout services
        const encodedCode = encodeURIComponent(playerCode);
        const response = await fetch(`/api/player/${encodedCode}/detailed`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });
        const data = await response.json();
        
        updatePageWithData(data);
    } catch (error) {
        console.error('Filter change error:', error);
        // Handle error directly in page
    }
}

// Component coordination - if shared functionality needed, create a component
function updatePageWithData(data) {
    // Update charts using component
    ChartsComponent.updateTimeChart('timeChart', data.date_stats);
    
    // Update filters using component  
    window.advancedFilters.populateFilterOptions(data.filter_options);
    
    // For shared API calls, create a utility component instead of layout services
}
```

### Page Template Pattern
```jinja2
{% extends "layouts/layout_name.html" %}

{# NO component imports - layout provides everything #}

{% block title %}Page Title{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='pages/page_name/page_name.css') }}">
{% endblock %}

{% block content %}
<!-- Page content using component macros from layout -->
{{ component_macro("param1", "param2") }}

<div class="page-specific-content">
    <!-- Page-specific HTML -->
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='pages/page_name/page_name.js') }}"></script>
{% endblock %}
```

## JavaScript Patterns

### Component JavaScript Pattern
```javascript
// Auto-initialization - No DOMContentLoaded wrapper
class ComponentName {
    constructor(element, options = {}) {
        this.element = element;
        this.options = { ...this.defaults, ...options };
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.render();
    }
    
    // Public API methods
    refresh() { this.render(); }
    destroy() { /* cleanup */ }
}

// Initialize immediately when script loads
initializeComponentName();
window.ComponentName = ComponentName;
```

### Page JavaScript Pattern
```javascript
// Page-specific behavior with DOMContentLoaded wrapper
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Page initialization
        initializePageFeature();
        loadPageData();
        setupPageEventHandlers();
        
        console.log('Page initialized successfully');
    } catch (error) {
        console.error('Error initializing page:', error);
    }
});

// Business logic functions
async function loadPageData() {
    // API calls and data management
}

function setupPageEventHandlers() {
    // Page-specific event listeners
}
```

## CSS Methodology

### Component CSS (BEM)
```css
/* Component: component_name.css */
.component-name {
    /* Base component styles */
}

.component-name__element {
    /* Component element styles */
}

.component-name--modifier {
    /* Component modifier styles */
}
```

### Page CSS (Descriptive)
```css
/* Page: page_name.css */
.page-specific-content {
    /* Styles unique to this page */
}

.page-hero {
    /* Page section styles */
}
```

## Development Workflow

### Creating a New Component

1. **Create directory**: `frontend/components/new_component/`
2. **Create template**: `_new_component.html` with macros and asset imports
3. **Create styles**: `new_component.css` with BEM methodology
4. **Create behavior**: `new_component.js` with auto-initialization
5. **Import in layout**: Use `{% from %}` and `{% include %}`
6. **Use in pages**: Call macros provided by layout

### Creating a New Page

1. **Create directory**: `frontend/pages/new_page/`
2. **Create template**: `new_page.html` extending appropriate layout
3. **Create styles**: `new_page.css` for page-specific styling
4. **Create behavior**: `new_page.js` with `DOMContentLoaded` wrapper
5. **Add route**: Update Flask route to render the template

## Best Practices

### Architecture
1. **Component Independence**: Components should work in isolation
2. **Single Responsibility**: Each component/page has one clear purpose
3. **Asset Ownership**: Components own their assets, pages own theirs
4. **Template Hierarchy**: Always follow base → layout → page

### JavaScript
5. **Initialization Patterns**: Components auto-initialize, pages wait for DOM
6. **API Responsibility**: Pages handle API calls, components handle UI
7. **Error Handling**: Components degrade gracefully, pages show user feedback

### CSS
8. **Methodology**: Use BEM for components, descriptive names for pages
9. **Responsive Design**: Components handle their responsive needs
10. **No Duplication**: Reuse component styles instead of copying

This architecture provides a scalable, maintainable frontend structure with clear separation of concerns and reusable components.