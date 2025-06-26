# Components Architecture

This directory contains self-contained, reusable UI components that follow the **"Components Do"** principle. Each component is a complete package with its own template, styles, and behavior.

## Core Principle: Components Do

Components are responsible for:
- **✅ Self-contained UI behavior** - Specific, focused functionality
- **✅ DOM manipulation and event handling** - Direct interaction with UI elements
- **✅ Auto-initialization** - Ready to use when included
- **✅ Simple APIs** - Clean interfaces through macros and JavaScript methods
- **❌ NOT business logic** - No API calls or complex data processing
- **❌ NOT component coordination** - Don't orchestrate other components

## Directory Structure

```
frontend/components/
├── README.md                    # This file
├── component_name/              # Component package
│   ├── _component_name.html     # Template with macros + asset imports
│   ├── component_name.css       # Component-specific styles (BEM)
│   └── component_name.js        # Component behavior (auto-init)
└── shared/                      # Shared component utilities (if needed)
```

## Component Package Structure

Each component is a **complete, self-contained package**:

### Template File (`_component_name.html`)
```jinja2
{# Component manages its own assets #}
<link rel="stylesheet" href="{{ url_for('static', filename='components/component_name/component_name.css') }}">
<script src="{{ url_for('static', filename='components/component_name/component_name.js') }}"></script>

{# Component macros - the public API #}
{% macro component_function(param1, param2="default") %}
<div class="component-name" data-component="component_name">
    <div class="component-name__element">
        {{ param1 }}
    </div>
</div>
{% endmacro %}
```

### CSS File (`component_name.css`)
```css
/* Component: component_name.css - BEM Methodology */
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

### JavaScript File (`component_name.js`)
```javascript
// Component: component_name.js - Auto-initialization pattern
class ComponentName {
    constructor(element, options = {}) {
        this.element = element;
        this.options = { ...this.defaults, ...options };
        this.init();
    }
    
    get defaults() {
        return {
            // Default options
        };
    }
    
    init() {
        this.setupEventListeners();
        this.render();
    }
    
    // Public API methods
    refresh() { this.render(); }
    destroy() { /* cleanup */ }
}

// Auto-initialize when script loads (no DOMContentLoaded)
function initializeComponentName() {
    const elements = document.querySelectorAll('[data-component="component_name"]');
    elements.forEach(element => {
        if (!element.componentInstance) {
            element.componentInstance = new ComponentName(element);
        }
    });
}

// Initialize immediately and expose globally
initializeComponentName();
window.ComponentName = ComponentName;
```

## Existing Components

### Search Component (`components/search/`)
**Purpose**: Unified search functionality across the application

**Macros**:
- `navbar_search(show, placeholder)` - Search form for navigation bars
- `filter_search(target, placeholder, show_count)` - Filter/search for tables

**JavaScript API**:
- `navigateToPlayer(code)` - Navigate to player profile
- `filterPlayers()` - Filter visible players on current page
- Global keyboard shortcuts (Ctrl+K to focus search)

**Usage in Layout**:
```jinja2
{% from 'components/search/_search.html' import navbar_search, filter_search %}
{% include 'components/search/_search.html' %}

{{ navbar_search(true, "Find Player...") }}
{{ filter_search("playersTable", "Search players...") }}
```

### Character Icons Component (`components/character_icons/`)
**Purpose**: Display character icons and fallbacks

**Macros**:
- `character_icon(character_name, size)` - Single character icon
- `character_fallback(character_name)` - Fallback when no icon available

**JavaScript API**:
- Auto-detects `[data-character-name]` elements
- Loads icons asynchronously with fallbacks
- `refresh(container)` - Refresh icons in specific container

### Navbar Component (`components/navbar/`)
**Purpose**: Application navigation and branding

**Macros**:
- `navbar(style, config)` - Main navigation bar
- Supports different styles: "default", "simple", "minimal"

**JavaScript API**:
- Responsive collapse/expand behavior
- Active page highlighting
- Search integration

### Cards Component (`components/cards/`)
**Purpose**: Reusable card layouts and content blocks

**Macros**:
- `hero_stats_card(stats)` - Homepage statistics display
- `action_card(title, content, actions)` - Call-to-action cards
- `recent_games_card(games)` - Recent games display
- `top_players_card(players)` - Top players leaderboard

## Component Development Guidelines

### 1. **Single Responsibility**
Each component should have one clear purpose:
```javascript
// ✅ Good - Focused on search functionality
class UnifiedSearch {
    navigateToPlayer(code) { /* ... */ }
    filterPlayers() { /* ... */ }
}

// ❌ Bad - Too many responsibilities
class MegaComponent {
    search() { /* ... */ }
    uploadFiles() { /* ... */ }
    generateReports() { /* ... */ }
}
```

### 2. **Auto-Initialization**
Components should work immediately when included:
```javascript
// ✅ Good - Auto-initialize on script load
class SearchComponent {
    constructor() { this.init(); }
}
const searchComponent = new SearchComponent();

// ❌ Bad - Requires manual initialization
class SearchComponent {
    // Requires calling searchComponent.init() somewhere else
}
```

### 3. **Asset Self-Management**
Components manage their own CSS and JS:
```jinja2
{# ✅ Good - Component includes its own assets #}
<link rel="stylesheet" href="{{ url_for('static', filename='components/search/search.css') }}">
<script src="{{ url_for('static', filename='components/search/search.js') }}"></script>

{# ❌ Bad - External asset management #}
{# Assets loaded elsewhere, component doesn't know about them #}
```

### 4. **Simple Public APIs**
Provide clean, focused interfaces:
```javascript
// ✅ Good - Simple, clear API
window.SearchComponent = {
    navigateToPlayer: function(code) { /* ... */ },
    focusSearch: function() { /* ... */ }
};

// ❌ Bad - Complex, confusing API
window.SearchComponent = {
    internalState: { /* ... */ },
    _privateMethod: function() { /* ... */ },
    doComplexThing: function(a, b, c, d, options) { /* ... */ }
};
```

### 5. **BEM CSS Methodology**
Use consistent naming for styles:
```css
/* ✅ Good - BEM methodology */
.search-form { /* Block */ }
.search-form__input { /* Element */ }
.search-form--compact { /* Modifier */ }

/* ❌ Bad - Inconsistent naming */
.search { }
.searchInput { }
.search-compact-version { }
```

## Creating New Components

### Step 1: Plan the Component
- **What does it do?** Single, focused responsibility
- **Who uses it?** Which layouts and pages need it
- **What's the API?** Macros and JavaScript methods needed

### Step 2: Create the Package
```bash
# Create component directory
mkdir frontend/components/new_component

# Create template file
touch frontend/components/new_component/_new_component.html

# Create styles
touch frontend/components/new_component/new_component.css

# Create behavior
touch frontend/components/new_component/new_component.js
```

### Step 3: Implement the Template
```jinja2
{# frontend/components/new_component/_new_component.html #}
<link rel="stylesheet" href="{{ url_for('static', filename='components/new_component/new_component.css') }}">
<script src="{{ url_for('static', filename='components/new_component/new_component.js') }}"></script>

{% macro new_component_display(data, options={}) %}
<div class="new-component" data-component="new_component">
    <div class="new-component__content">
        {{ data.title }}
    </div>
</div>
{% endmacro %}
```

### Step 4: Implement Styles (BEM)
```css
/* frontend/components/new_component/new_component.css */
.new-component {
    /* Base component styles */
    display: flex;
    padding: 1rem;
    border-radius: 0.5rem;
}

.new-component__content {
    /* Element styles */
    flex: 1;
    color: #333;
}

.new-component--featured {
    /* Modifier styles */
    background-color: #007bff;
    color: white;
}
```

### Step 5: Implement Behavior (Auto-init)
```javascript
// frontend/components/new_component/new_component.js
class NewComponent {
    constructor(element, options = {}) {
        this.element = element;
        this.options = { ...this.defaults, ...options };
        this.init();
    }
    
    get defaults() {
        return {
            autoRefresh: true,
            animationDuration: 300
        };
    }
    
    init() {
        this.setupEventListeners();
        this.render();
    }
    
    setupEventListeners() {
        this.element.addEventListener('click', (e) => {
            this.handleClick(e);
        });
    }
    
    handleClick(event) {
        // Component-specific click handling
        console.log('New component clicked');
    }
    
    render() {
        // Update component display
    }
    
    // Public API
    refresh() {
        this.render();
    }
    
    destroy() {
        // Cleanup event listeners
        this.element.removeEventListener('click', this.handleClick);
    }
}

// Auto-initialize
function initializeNewComponent() {
    const elements = document.querySelectorAll('[data-component="new_component"]');
    elements.forEach(element => {
        if (!element.componentInstance) {
            element.componentInstance = new NewComponent(element);
        }
    });
}

initializeNewComponent();
window.NewComponent = NewComponent;
```

### Step 6: Use in Layout
```jinja2
{# layouts/layout_name.html #}
{% from 'components/new_component/_new_component.html' import new_component_display %}
{% include 'components/new_component/_new_component.html' %}

{# Now available for pages #}
{{ new_component_display(page_data) }}
```

## Component Communication

### Via Callbacks (Preferred)
```javascript
// Component provides callback hooks
class FilterComponent {
    constructor(element, options = {}) {
        this.onFilterChange = options.onFilterChange || (() => {});
    }
    
    applyFilter(criteria) {
        // Apply filter logic
        this.onFilterChange(criteria); // Notify parent
    }
}

// Page orchestrates via callbacks
const filter = new FilterComponent(element, {
    onFilterChange: (criteria) => {
        // Page handles the business logic
        updateResults(criteria);
    }
});
```

### Via Custom Events
```javascript
// Component dispatches events
class SearchComponent {
    performSearch(query) {
        // Search logic
        this.element.dispatchEvent(new CustomEvent('search:complete', {
            detail: { query, results }
        }));
    }
}

// Page listens for events
document.addEventListener('search:complete', (event) => {
    updatePageWithResults(event.detail.results);
});
```

### Via Global State (Minimal Use)
```javascript
// Only for truly global state
window.AppState = {
    currentPlayer: null,
    searchQuery: ''
};

// Components can read but should notify on changes
class PlayerComponent {
    updatePlayer(playerCode) {
        window.AppState.currentPlayer = playerCode;
        this.notifyPlayerChange();
    }
}
```

## Component Testing

### Unit Testing (Individual Components)
```javascript
// Test component in isolation
describe('SearchComponent', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div data-component="search"></div>';
    });
    
    test('should initialize with default options', () => {
        const component = new SearchComponent(document.querySelector('[data-component="search"]'));
        expect(component.options).toEqual(component.defaults);
    });
    
    test('should handle search input', () => {
        const component = new SearchComponent(element);
        component.performSearch('test');
        // Assert expected behavior
    });
});
```

### Integration Testing (Component + DOM)
```javascript
// Test component interaction with DOM
describe('SearchComponent Integration', () => {
    test('should filter table rows', () => {
        // Setup DOM with table
        // Initialize component
        // Trigger search
        // Assert DOM changes
    });
});
```

## Performance Considerations

### 1. **Efficient Initialization**
```javascript
// ✅ Good - Initialize only what's needed
function initializeComponents() {
    const searchElements = document.querySelectorAll('[data-component="search"]');
    if (searchElements.length > 0) {
        searchElements.forEach(element => new SearchComponent(element));
    }
}

// ❌ Bad - Initialize everything always
function initializeComponents() {
    new SearchComponent(); // Assumes elements exist
    new FilterComponent(); // Might not be needed
}
```

### 2. **Event Delegation**
```javascript
// ✅ Good - Event delegation for dynamic content
document.addEventListener('click', (e) => {
    const component = e.target.closest('[data-component="search"]');
    if (component) {
        handleSearchClick(e);
    }
});

// ❌ Bad - Direct event binding on all elements
document.querySelectorAll('.search-button').forEach(button => {
    button.addEventListener('click', handleClick);
});
```

### 3. **Memory Management**
```javascript
// ✅ Good - Cleanup when component destroyed
class Component {
    destroy() {
        this.element.removeEventListener('click', this.handleClick);
        this.element.componentInstance = null;
    }
}

// ❌ Bad - Memory leaks from uncleaned listeners
class Component {
    // No cleanup method
}
```

## Common Patterns

### Data Attribute Configuration
```html
<!-- Configure component via data attributes -->
<div data-component="search" 
     data-target="playersTable"
     data-placeholder="Search players..."
     data-auto-focus="true">
</div>
```

```javascript
class SearchComponent {
    constructor(element) {
        this.target = element.dataset.target;
        this.placeholder = element.dataset.placeholder;
        this.autoFocus = element.dataset.autoFocus === 'true';
    }
}
```

### Progressive Enhancement
```javascript
// Component enhances existing markup
class TableComponent {
    constructor(table) {
        // Start with basic HTML table
        // Add sorting, filtering, etc.
        this.enhanceTable(table);
    }
}
```

### Responsive Behavior
```css
/* Component handles its own responsive needs */
.component-name {
    display: flex;
}

@media (max-width: 768px) {
    .component-name {
        flex-direction: column;
    }
}
```

This component architecture provides a scalable foundation for building reusable UI elements that work consistently across the application while maintaining clear boundaries and responsibilities.