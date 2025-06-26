# Pages Architecture

This directory contains page-specific content and functionality. Pages follow the **"Pages Orchestrate"** principle - they coordinate components and handle business logic for specific user interfaces.

## Core Principle: Pages Orchestrate

Pages are responsible for:
- **✅ Business logic and data management** - API calls, data transformation, state management
- **✅ Component coordination** - Connect components together for page goals
- **✅ Page-specific styling** - Unique visual requirements not handled by components
- **✅ Error handling and user feedback** - Page-level error states and loading indicators
- **❌ NOT direct DOM manipulation** - Use components for UI interactions
- **❌ NOT component implementation** - Use existing components, don't recreate them

## Directory Structure

```
frontend/pages/
├── README.md                    # This file
├── page_name/                   # Page package
│   ├── page_name.html           # Page template extending layout
│   ├── page_name.css            # Page-specific styles
│   └── page_name.js             # Page-specific behavior (DOMContentLoaded)
└── shared/                      # Shared page utilities (if needed)
```

## Page Package Structure

Each page is a **focused package** for specific user functionality:

### Template File (`page_name.html`)
```jinja2
{% extends "layouts/layout_name.html" %}

{# NO component imports - layout provides everything #}

{% block title %}Page Title - Slippi Stats{% endblock %}

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

### CSS File (`page_name.css`)
```css
/* Page-specific styles - descriptive naming */
.page-specific-content {
    /* Styles unique to this page */
}

.page-hero-section {
    /* Page section styles */
}

.page-data-table {
    /* Page-specific table styling */
}
```

### JavaScript File (`page_name.js`)
```javascript
// Page-specific behavior - Always uses DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // 1. Initialize page-specific functionality
        initializePageFeatures();
        
        // 2. Setup component coordination
        setupComponentInteractions();
        
        // 3. Load initial data
        loadPageData();
        
        console.log('Page initialized successfully');
    } catch (error) {
        console.error('Error initializing page:', error);
        handlePageError(error);
    }
});

// Business logic functions
async function loadPageData() {
    // API calls and data management
}

function setupComponentInteractions() {
    // Connect components together
    if (window.ComponentName) {
        window.ComponentName.onEvent(handleComponentEvent);
    }
}
```

## Existing Pages

### Players Page (`pages/players/`)
**Purpose**: Browse and search all players in the system

**Layout Used**: `simple.html`
**Components Used**: Search filtering, character icons, data tables

**Business Logic**:
- Player search and filtering
- Table interaction enhancements
- Profile navigation with loading states

**Key Features**:
```javascript
// pages/players/players.js
function setupRowInteractions() {
    // Make entire rows clickable
    // Add hover effects
    // Handle keyboard navigation
}

function enhanceSearchIntegration() {
    // Connect with search component
    // Add search hints and tips
    // Handle Enter key navigation
}
```

**CSS Highlights**:
```css
/* pages/players/players.css */
.player-row {
    cursor: pointer;
    transition: all 0.2s ease;
}

.player-row:hover .player-tag {
    background-color: #007bff;
    color: white;
}
```

### Index Page (`pages/index/`)
**Purpose**: Homepage with recent games and top players

**Layout Used**: `simple.html`
**Components Used**: Hero cards, recent games cards, top players cards

**Business Logic**:
- Statistics display and formatting
- Recent games navigation
- Top players highlighting

### Player Profile Pages (`pages/player_basic/`, `pages/player_detailed/`)
**Purpose**: Individual player statistics and analysis

**Layout Used**: `player.html`
**Components Used**: Advanced filtering, charts, statistics cards

**Business Logic**:
- Player data loading and caching
- Filter coordination between components
- Chart data transformation and updates

## Page Development Guidelines

### 1. **Business Logic Ownership**
Pages own the business logic for their specific functionality:

```javascript
// ✅ Good - Page handles business logic
document.addEventListener('DOMContentLoaded', async function() {
    // Page coordinates the overall flow
    const playerData = await loadPlayerData();
    const processedStats = processPlayerStats(playerData);
    updateComponentsWithData(processedStats);
});

async function loadPlayerData() {
    // Direct API call - page responsibility
    const response = await fetch(`/api/player/${playerCode}/stats`);
    return response.json();
}

// ❌ Bad - Component handles business logic
class StatsComponent {
    async loadData() {
        // Components shouldn't make API calls
        const response = await fetch('/api/...');
    }
}
```

### 2. **Component Coordination**
Pages connect components together to achieve page goals:

```javascript
// ✅ Good - Page coordinates components
function setupComponentInteractions() {
    if (window.FilterComponent) {
        window.FilterComponent.onFilterChange(handleFilterChange);
    }
    
    if (window.ChartComponent) {
        window.ChartComponent.onChartClick(handleChartClick);
    }
}

function handleFilterChange(filters) {
    // Page handles the coordination
    updateChartsWithFilters(filters);
    updateTableWithFilters(filters);
    updateURLWithFilters(filters);
}

// ❌ Bad - Components coordinate directly
class FilterComponent {
    applyFilter() {
        // Don't let components talk to each other directly
        window.ChartComponent.updateChart();
        window.TableComponent.updateTable();
    }
}
```

### 3. **Error Handling Strategy**
Pages handle errors and provide user feedback:

```javascript
// ✅ Good - Page-level error handling
async function loadPageData() {
    try {
        const data = await fetchData();
        updatePage(data);
    } catch (error) {
        console.error('Failed to load page data:', error);
        showErrorMessage('Unable to load player data. Please try again.');
        // Graceful degradation
        showCachedData();
    }
}

function showErrorMessage(message) {
    // Page controls error display
    const errorDiv = document.getElementById('errorContainer');
    errorDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    errorDiv.style.display = 'block';
}

// ❌ Bad - No error handling
async function loadPageData() {
    const data = await fetchData(); // Could throw, no handling
    updatePage(data);
}
```

### 4. **Page-Specific Styling**
Use descriptive CSS class names for page-specific styling:

```css
/* ✅ Good - Page-specific, descriptive names */
.players-page-header {
    border-bottom: 3px solid #0d6efd;
    margin-bottom: 1.5rem;
}

.player-profile-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.tournament-bracket-container {
    overflow-x: auto;
    padding: 1rem;
}

/* ❌ Bad - Generic names that could conflict */
.header {
    /* Too generic */
}

.stats {
    /* Could apply to any stats */
}

.container {
    /* Conflicts with Bootstrap */
}
```

## Creating New Pages

### Step 1: Plan the Page
- **What's the user goal?** What does the user want to accomplish?
- **What data is needed?** What API endpoints or data sources?
- **What components are needed?** Search, tables, charts, forms?
- **What layout fits best?** Simple, player, admin, minimal?

### Step 2: Create the Page Package
```bash
# Create page directory
mkdir frontend/pages/new_page

# Create page files
touch frontend/pages/new_page/new_page.html
touch frontend/pages/new_page/new_page.css
touch frontend/pages/new_page/new_page.js
```

### Step 3: Implement the Template
```jinja2
{# frontend/pages/new_page/new_page.html #}
{% extends "layouts/simple.html" %}

{% block title %}New Page - Slippi Stats{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='pages/new_page/new_page.css') }}">
{% endblock %}

{% block content %}
<div class="new-page-container">
    <div class="new-page-header">
        <h1>New Page Title</h1>
        <p class="lead">Page description</p>
    </div>
    
    <!-- Use component macros from layout -->
    {{ filter_search("newPageTable", "Search items...") }}
    
    <div class="new-page-content">
        <!-- Page-specific content -->
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='pages/new_page/new_page.js') }}"></script>
{% endblock %}
```

### Step 4: Implement Page Styles
```css
/* frontend/pages/new_page/new_page.css */
.new-page-container {
    max-width: 1200px;
    margin: 0 auto;
}

.new-page-header {
    text-align: center;
    margin-bottom: 2rem;
}

.new-page-content {
    background: #f8f9fa;
    border-radius: 0.5rem;
    padding: 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    .new-page-container {
        padding: 0 1rem;
    }
    
    .new-page-content {
        padding: 1rem;
    }
}
```

### Step 5: Implement Page Behavior
```javascript
// frontend/pages/new_page/new_page.js
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize page functionality
        initializeNewPageFeatures();
        setupComponentConnections();
        loadInitialData();
        
        console.log('New page initialized successfully');
    } catch (error) {
        console.error('Error initializing new page:', error);
        handlePageInitializationError(error);
    }
});

async function loadInitialData() {
    try {
        showLoadingState();
        
        const response = await fetch('/api/new-page-data');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        updatePageWithData(data);
        
    } catch (error) {
        console.error('Failed to load page data:', error);
        showErrorState('Unable to load data. Please refresh the page.');
    } finally {
        hideLoadingState();
    }
}

function setupComponentConnections() {
    // Connect with search component if available
    if (window.UnifiedSearch && typeof window.filterItems === 'undefined') {
        window.filterItems = function() {
            // Page-specific filtering logic
            const searchInput = document.getElementById('itemSearch');
            const searchTerm = searchInput.value.toLowerCase();
            
            // Filter logic specific to this page
            filterTableRows(searchTerm);
        };
    }
}

function initializeNewPageFeatures() {
    // Page-specific feature initialization
    setupTableInteractions();
    setupFormValidation();
    setupRealTimeUpdates();
}

function updatePageWithData(data) {
    // Transform and display data
    const container = document.querySelector('.new-page-content');
    container.innerHTML = generatePageContent(data);
    
    // Refresh components if needed
    if (window.ComponentName && window.ComponentName.refresh) {
        window.ComponentName.refresh();
    }
}

function showLoadingState() {
    const container = document.querySelector('.new-page-content');
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p>Loading...</p></div>';
}

function showErrorState(message) {
    const container = document.querySelector('.new-page-content');
    container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
}

function hideLoadingState() {
    // Loading state cleared by updatePageWithData
}
```

### Step 6: Add Flask Route
```python
# In backend/routes/web_routes.py
@web_bp.route('/new-page')
def new_page():
    """New page description."""
    data = web_service.prepare_new_page_data()
    return render_template('pages/new_page/new_page.html', **data)
```

## Page Patterns

### Data Loading Page Pattern
```javascript
// Common pattern for pages that load data
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // 1. Show loading state
        showPageLoading();
        
        // 2. Load required data
        const [userData, statsData] = await Promise.all([
            fetchUserData(),
            fetchStatsData()
        ]);
        
        // 3. Process and display data
        const processedData = processPageData(userData, statsData);
        updatePageDisplay(processedData);
        
        // 4. Setup interactions
        setupPageInteractions();
        
    } catch (error) {
        handlePageError(error);
    } finally {
        hidePageLoading();
    }
});
```

### Interactive Dashboard Pattern
```javascript
// Pattern for pages with multiple interactive components
document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize all components
    initializeCharts();
    initializeFilters();
    initializeTables();
    
    // 2. Connect components with shared state
    const pageState = {
        filters: {},
        selectedDateRange: null,
        selectedPlayer: null
    };
    
    // 3. Setup coordinated interactions
    setupFilterCoordination(pageState);
    setupChartInteractions(pageState);
    setupTableInteractions(pageState);
});

function setupFilterCoordination(state) {
    if (window.FilterComponent) {
        window.FilterComponent.onChange = (filters) => {
            state.filters = filters;
            updateAllComponents(state);
        };
    }
}
```

### Form Processing Page Pattern
```javascript
// Pattern for pages with forms and validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pageForm');
    if (form) {
        setupFormValidation(form);
        setupFormSubmission(form);
    }
});

function setupFormSubmission(form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateForm(form)) {
            showValidationErrors();
            return;
        }
        
        try {
            showSubmissionLoading();
            const formData = new FormData(form);
            const response = await submitFormData(formData);
            
            if (response.success) {
                showSuccessMessage();
                redirectToNextPage();
            } else {
                showErrorMessage(response.error);
            }
        } catch (error) {
            showErrorMessage('Submission failed. Please try again.');
        } finally {
            hideSubmissionLoading();
        }
    });
}
```

## Page Communication Patterns

### URL State Management
```javascript
// Manage page state via URL parameters
class PageStateManager {
    constructor() {
        this.state = this.loadStateFromURL();
        this.setupStateWatching();
    }
    
    loadStateFromURL() {
        const params = new URLSearchParams(window.location.search);
        return {
            filter: params.get('filter') || '',
            page: parseInt(params.get('page')) || 1,
            sortBy: params.get('sort') || 'name'
        };
    }
    
    updateURL(newState) {
        const params = new URLSearchParams();
        Object.entries(newState).forEach(([key, value]) => {
            if (value) params.set(key, value);
        });
        
        const newURL = window.location.pathname + '?' + params.toString();
        window.history.pushState(newState, '', newURL);
    }
}
```

### Local Storage Integration
```javascript
// Persist page preferences
function savePagePreferences(preferences) {
    try {
        localStorage.setItem('pagePreferences', JSON.stringify(preferences));
    } catch (error) {
        console.warn('Unable to save preferences:', error);
    }
}

function loadPagePreferences() {
    try {
        const saved = localStorage.getItem('pagePreferences');
        return saved ? JSON.parse(saved) : getDefaultPreferences();
    } catch (error) {
        console.warn('Unable to load preferences:', error