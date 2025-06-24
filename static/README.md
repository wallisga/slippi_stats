# Static Directory

This directory contains all client-side assets (CSS, JavaScript, images) organized by **component-based architecture** for optimal maintainability and performance.

## Component-Based Architecture

### Philosophy
Static assets follow a **component-based architecture** where:

1. **Components manage their own assets** - Each component includes its own CSS and JavaScript
2. **Base assets are minimal** - Only global foundation styles and utilities
3. **Page assets are content-specific** - Only page-specific styling and behavior
4. **No asset duplication** - Each asset loaded only where needed

### Directory Structure (Component-Based)

```
static/
├── css/
│   ├── base.css                 # Global foundation styles ONLY
│   ├── components/              # Component-specific styles
│   │   ├── search.css          # Search component styling
│   │   ├── character_icons.css # Character icon component styling
│   │   ├── player_title.css    # Player title component styling
│   │   └── game_table.css      # Game table component styling
│   └── pages/                   # Page-specific styles ONLY
│       ├── index.css           # Homepage-specific styles
│       ├── players.css         # Player index page styles
│       ├── player_basic.css    # Basic player page styles
│       └── player_detailed.css # Detailed player page styles
├── js/
│   ├── base.js                 # Global utilities ONLY
│   ├── components/             # Component-specific JavaScript
│   │   ├── search.js           # Search component behavior
│   │   ├── character_icons.js  # Character icon management
│   │   ├── player_title.js     # Player title component
│   │   └── game_table.js       # Game table interactions
│   └── pages/                  # Page-specific JavaScript ONLY
│       ├── index.js            # Homepage-specific behavior
│       ├── players.js          # Player index functionality
│       ├── player_basic.js     # Basic player page behavior
│       └── player_detailed.js  # Advanced analytics functionality
└── icons/
    └── character/              # Character icon images
        ├── neutral Fox.png
        ├── neutral Falco.png
        └── [26 total Melee characters]
```

## Asset Loading Strategy

### Base Assets (Loaded by `base.html`)
**Purpose**: Global foundation only
**Files**:
- `css/base.css` - Global styles, CSS variables, Bootstrap customizations
- `js/base.js` - Global utilities, error handling, common functions

**Contents**:
```css
/* base.css - Global foundation only */
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    /* Global CSS variables */
}

body {
    padding-top: 76px; /* Fixed navbar */
}

/* Global utility classes */
.loading-spinner { /* ... */ }
.error-message { /* ... */ }
```

```javascript
// base.js - Global utilities only
window.SlippiUtils = {
    encodePlayerTag: function(tag) { /* ... */ },
    formatTimeAgo: function(date) { /* ... */ },
    showLoading: function(element) { /* ... */ }
};
```

### Component Assets (Loaded by Components)
**Purpose**: Self-contained component functionality
**Loading**: Each component template imports its own CSS and JavaScript

#### Component Asset Pattern
```jinja2
{# components/search/_search.html #}

{# Component manages its own assets #}
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/search.css') }}">
<script src="{{ url_for('static', filename='js/components/search.js') }}"></script>

{# Component functionality #}
{% macro search_form() %}
<!-- Component HTML -->
{% endmacro %}
```

### Page Assets (Loaded by Pages)
**Purpose**: Page-specific styling and behavior only
**Loading**: Pages import only their specific CSS and JavaScript

```jinja2
{# pages/index.html #}
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/index.css') }}">
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/index.js') }}"></script>
{% endblock %}
```

## Component Asset Packages

### `search` Component Package
**Files**:
- `css/components/search.css` - Search form styling
- `js/components/search.js` - Search behavior and URL handling

**CSS Features**:
```css
/* search.css - Component-specific only */
.navbar-search .form-control {
    border-radius: 20px;
    background-color: rgba(255, 255, 255, 0.1);
}

.main-search-form .input-group-lg {
    /* Large search styling */
}

.filter-search-container {
    /* Filter search styling */
}
```

**JavaScript Features**:
```javascript
// search.js - Unified search component
class UnifiedSearch {
    constructor() {
        this.initializeAllSearchForms();
    }
    
    initializeAllSearchForms() {
        this.initializeNavbarSearch();
        this.initializeMainSearch();
        this.initializeFilterSearch();
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    new UnifiedSearch();
});
```

### `character_icons` Component Package
**Files**:
- `css/components/character_icons.css` - Icon styling and fallbacks
- `js/components/character_icons.js` - Icon loading and management

**CSS Features**:
```css
/* character_icons.css - Component-specific only */
.character-icon {
    margin-right: 8px;
    vertical-align: middle;
    width: 24px;
    height: 24px;
}

.character-icon-fallback {
    display: inline-block;
    background-color: #f8f9fa;
    border-radius: 50%;
    text-align: center;
    font-weight: bold;
}

/* Character-specific fallback colors */
.character-icon-fallback[data-character="fox"] {
    background-color: #fd7e14;
    color: white;
}
```

**JavaScript Features**:
```javascript
// character_icons.js - Component behavior
function initializeCharacterIcons(container = document) {
    const elements = container.querySelectorAll('[data-character-name]:not([data-icon-processed])');
    elements.forEach(element => {
        element.setAttribute('data-icon-processed', 'true');
        const characterName = element.getAttribute('data-character-name');
        createCharacterIcon(element, characterName);
    });
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', initializeCharacterIcons);
```

### `player_title` Component Package
**Files**:
- `css/components/player_title.css` - Player header styling
- `js/components/player_title.js` - Dynamic title generation

**CSS Features**:
```css
/* player_title.css - Component-specific only */
.player-title-section {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #dee2e6;
}

.player-main-title {
    font-size: 2.5rem;
    font-weight: 700;
}

.player-status.online {
    background-color: #28a745;
}

.player-status.offline {
    background-color: #6c757d;
}

.player-quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
}
```

**JavaScript Features**:
```javascript
// player_title.js - Component behavior
class PlayerTitle {
    constructor(playerCode, encodedPlayerCode, options = {}) {
        this.playerCode = playerCode;
        this.options = options;
        this.init();
    }
    
    init() {
        this.calculateLastPlayed();
        this.createTitle();
        this.startLastPlayedUpdates();
    }
    
    // Component functionality...
}
```

### `game_table` Component Package (Planned)
**Files**:
- `css/components/game_table.css` - Table styling
- `js/components/game_table.js` - Table interactions

**Planned Features**:
- Consistent game table styling
- Hover effects and row highlighting
- Responsive table behaviors
- Game result indicators

## Page Asset Organization

### Page-Specific CSS
**Purpose**: Styling unique to individual pages only

#### `pages/index.css` - Homepage Styles
```css
/* index.css - Homepage-specific only */
.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4rem 0;
    margin: -2rem -15px 3rem -15px;
}

.hero-stats .stat-item {
    text-align: center;
    padding: 1rem;
}

.section-title {
    color: #212529;
    font-weight: 700;
    margin-bottom: 1.5rem;
}
```

#### `pages/players.css` - Player Index Styles
```css
/* players.css - Player index specific only */
.page-header {
    color: #212529;
    font-weight: 700;
    border-bottom: 3px solid #0d6efd;
    padding-bottom: 0.5rem;
}

.player-tag {
    background-color: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
}

.player-row:hover {
    background-color: #f8f9fa;
    transform: translateY(-1px);
    transition: all 0.2s ease;
}
```

#### `pages/player_basic.css` - Basic Player Page
```css
/* player_basic.css - Basic player page specific only */
.player-overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.performance-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.game-table-container {
    max-height: 600px;
    overflow-y: auto;
}
```

#### `pages/player_detailed.css` - Advanced Analytics
```css
/* player_detailed.css - Advanced analytics specific only */
.filter-panel {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.filter-group {
    margin-bottom: 1rem;
}

.chart-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    min-height: 400px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}
```

### Page-Specific JavaScript
**Purpose**: Behavior unique to individual pages only

#### `pages/index.js` - Homepage Behavior
```javascript
// index.js - Homepage-specific behavior only
document.addEventListener('DOMContentLoaded', function() {
    // Homepage-specific functionality
    fetchLatestStats();
    initializeGameTimeFormatting();
    setupKeyboardShortcuts();
});

function fetchLatestStats() {
    // Fetch and display latest server statistics
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => updateStatsDisplay(data));
}

function initializeGameTimeFormatting() {
    // Format game times on homepage recent games
    document.querySelectorAll('.time-cell').forEach(cell => {
        const timeData = cell.getAttribute('data-time');
        cell.textContent = window.SlippiUtils.formatTimeAgo(timeData);
    });
}
```

#### `pages/players.js` - Player Index Behavior
```javascript
// players.js - Player index specific behavior only
document.addEventListener('DOMContentLoaded', function() {
    // Player index specific functionality
    setupRowInteractions();
    setupProfileLinkStates();
});

function setupRowInteractions() {
    // Make table rows clickable
    document.querySelectorAll('.player-row').forEach(row => {
        row.addEventListener('click', function(e) {
            if (!e.target.closest('a')) {
                const profileLink = this.querySelector('a[href*="/player/"]');
                if (profileLink) profileLink.click();
            }
        });
    });
}
```

#### `pages/player_detailed.js` - Advanced Analytics
```javascript
// player_detailed.js - Advanced analytics specific behavior only
document.addEventListener('DOMContentLoaded', function() {
    // Advanced analytics specific functionality
    initializeFilters();
    initializeCharts();
    setupAdvancedSearch();
});

function initializeFilters() {
    // Complex filtering logic specific to detailed page
    const filterForm = document.getElementById('advancedFilters');
    if (filterForm) {
        // Filter initialization and event handling
    }
}

function initializeCharts() {
    // Chart.js integration for detailed analytics
    if (typeof Chart !== 'undefined') {
        setupTimeSeriesChart();
        setupCharacterPerformanceChart();
    }
}
```

## Asset Loading Performance

### Loading Strategy
1. **Base Assets**: Loaded on all pages (minimal set)
2. **Component Assets**: Loaded by component templates (as needed)
3. **Page Assets**: Loaded by specific pages only (targeted)

### Benefits
- **No Duplication**: Each asset loaded only where needed
- **Component Isolation**: Components manage their own dependencies
- **Page Optimization**: Pages only load what they need
- **Maintainable**: Clear separation of concerns

### Loading Order
```html
<!-- Base assets (base.html) -->
<link rel="stylesheet" href="/static/css/base.css">
<script src="/static/js/base.js"></script>

<!-- Component assets (component templates) -->
<link rel="stylesheet" href="/static/css/components/search.css">
<script src="/static/js/components/search.js"></script>

<!-- Page assets (page templates) -->
<link rel="stylesheet" href="/static/css/pages/index.css">
<script src="/static/js/pages/index.js"></script>
```

## Development Guidelines

### Component Asset Development
1. **Self-Contained**: Components manage their own CSS and JavaScript
2. **Single Responsibility**: Each component has one clear purpose
3. **Auto-Initialization**: Components initialize themselves on page load
4. **Public APIs**: Expose clean interfaces for external use
5. **Responsive Design**: All components work across device sizes

### Page Asset Development
1. **Content-Specific**: Only styles and behavior unique to the page
2. **No Component Dependencies**: Don't duplicate component functionality
3. **Performance Focused**: Minimize asset size and loading time
4. **Maintainable**: Clear organization and naming conventions

### Asset Organization Standards
1. **File Naming**: Match component/page template names
2. **CSS Methodology**: Use BEM for component classes
3. **JavaScript Standards**: ES6+ features, proper error handling
4. **Documentation**: Comment complex functionality

## Current Status

### ✅ Foundation Complete
- **Base assets**: Minimal global foundation
- **Asset structure**: Clear separation of concerns
- **Loading strategy**: Component-based architecture

### 🔄 Component Migration In Progress
- **search component**: CSS and JS partially migrated
- **character_icons component**: Fully migrated
- **player_title component**: Fully migrated
- **game_table component**: Planned

### 📋 Next Steps
1. Complete component asset migration
2. Update component templates to import assets
3. Remove redundant asset imports from layouts
4. Optimize asset loading performance
5. Test component isolation

The static asset architecture provides optimal performance and maintainability through component-based organization while maintaining clean separation of concerns.