# Templates Directory

This directory contains all Jinja2 templates organized using a **component-based architecture** for maximum maintainability and code reuse.

## Component Architecture Overview

The templates follow a **component-based architecture** where each component is a self-contained package of template, CSS, and JavaScript files.

```
templates/
├── base.html                    # Foundation: Bootstrap + base assets only
├── components/                  # Self-contained component packages
│   ├── search/
│   │   ├── _search.html        # Template + macros
│   │   ├── search.css          # Component styles
│   │   └── search.js           # Component behavior
│   ├── character_icons/
│   │   ├── _character_icons.html
│   │   ├── character_icons.css
│   │   └── character_icons.js
│   ├── player_title/
│   │   ├── _player_title.html
│   │   ├── player_title.css
│   │   └── player_title.js
│   └── game_table/
│       ├── _game_table.html
│       ├── game_table.css
│       └── game_table.js
├── layouts/                     # Component orchestration layer
│   ├── simple.html             # Basic layout with search + character icons
│   ├── player.html             # Enhanced layout with player components
│   └── error.html              # Minimal layout, no components
└── pages/                      # Content layer (no component imports)
    ├── index.html              # Homepage content
    ├── players.html            # Player index content
    ├── player_basic.html       # Basic player profile content
    └── player_detailed.html    # Detailed player analytics content
```

## Template Inheritance & Component Flow

### Inheritance Hierarchy
```
base.html (Foundation)
    ↓ extends
layouts/*.html (Component orchestration)
    ↓ extends
pages/*.html (Content only)
```

### Component Integration Flow
```
1. base.html provides foundation (Bootstrap + base assets)
2. layouts/ include and orchestrate components
3. components/ are self-contained packages
4. pages/ focus purely on content
```

## Layer Responsibilities

### Layer 1: Base Template (`base.html`)
**Purpose**: Minimal foundation shared by all pages

**Responsibilities:**
- HTML5 document structure
- Bootstrap CSS/JS integration (CDN)
- Core navigation shell
- Basic responsive layout
- Global JavaScript utilities (base.js only)

**Import Rules:**
- ✅ **ONLY** imports: Bootstrap, base.css, base.js
- ❌ **NO** component imports
- ❌ **NO** page-specific assets

**Key Blocks:**
- `title` - Page title
- `nav_items` - Navigation menu items
- `content_wrapper` - Main content container
- `extra_css` - Page-specific stylesheets only
- `extra_js` - Page-specific JavaScript only

### Layer 2: Layout Templates (`layouts/`)
**Purpose**: Component orchestration and layout-specific functionality

#### `simple.html` - Basic Layout
**Use Cases**: Homepage, player index, download pages, instructions
**Components Imported**: 
- `search` - Player search functionality
- `character_icons` - Character display system

**Component Integration:**
```jinja2
{% include 'components/search/_search.html' %}
{% include 'components/character_icons/_character_icons.html' %}

<!-- Use component macros in layout -->
{{ search.navbar_form() }}
```

#### `player.html` - Enhanced Player Layout  
**Use Cases**: Player profile pages, detailed analytics
**Components Imported**:
- `search` - Player search functionality
- `character_icons` - Character display system
- `player_title` - Dynamic player header
- `game_table` - Game data tables

**Enhanced Features:**
- Player dropdown navigation
- Player title component container
- Enhanced search integration
- Chart.js integration for analytics

#### `error.html` - Error Layout
**Use Cases**: Error pages (404, 500, etc.)
**Components Imported**: None (minimal layout)
**Features**: Error-specific styling and messaging

### Layer 3: Component Packages (`components/`)
**Purpose**: Self-contained, reusable UI components

Each component is a **complete package** containing:

#### Component Structure
```
components/component_name/
├── _component_name.html     # Template with macros + asset imports
├── component_name.css       # Component-specific styles
└── component_name.js        # Component behavior
```

#### Component Template Pattern
```jinja2
{# components/search/_search.html #}

{# Component assets - imported by the component itself #}
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/search.css') }}">
<script src="{{ url_for('static', filename='js/components/search.js') }}"></script>

{# Component macros #}
{% macro navbar_form(placeholder="Find Player...") %}
<form class="d-flex navbar-search" id="playerSearchForm">
    <input class="form-control me-2" type="search" placeholder="{{ placeholder }}">
    <button class="btn btn-outline-light" type="submit">
        <i class="bi bi-search"></i>
    </button>
</form>
{% endmacro %}

{% macro main_search(title="Find a Player") %}
<!-- Main page search implementation -->
{% endmacro %}
```

### Layer 4: Page Templates (`pages/`)
**Purpose**: Content-focused templates with page-specific functionality only

**Responsibilities:**
- Page content and structure
- Page-specific data display
- Content-specific styling (via extra_css block)
- Page-specific JavaScript (via extra_js block)

**Import Rules:**
- ✅ Extend appropriate layout
- ✅ Use component macros provided by layout
- ✅ Include page-specific CSS/JS only
- ❌ **NO** direct component imports
- ❌ **NO** component CSS/JS imports

## Component Development Standards

### Creating New Components

#### 1. Create Component Package
```
templates/components/new_component/
├── _new_component.html      # Template + macros + asset imports
├── new_component.css        # Styles (BEM methodology)
└── new_component.js         # Behavior (auto-initialization)
```

#### 2. Component Template Structure
```jinja2
{# Asset imports - component manages its own assets #}
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/new_component.css') }}">
<script src="{{ url_for('static', filename='js/components/new_component.js') }}"></script>

{# Component initialization - if needed #}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Component auto-initialization
});
</script>

{# Reusable macros #}
{% macro component_macro(param1, param2="default") %}
<!-- Component HTML structure -->
{% endmacro %}
```

#### 3. Component CSS (BEM Methodology)
```css
/* Component: new_component.css */
.new-component {
    /* Base component styles */
}

.new-component__element {
    /* Component element styles */
}

.new-component--modifier {
    /* Component modifier styles */
}

.new-component__element--modifier {
    /* Element modifier styles */
}

/* Responsive design included */
@media (max-width: 768px) {
    .new-component {
        /* Mobile styles */
    }
}
```

#### 4. Component JavaScript (Auto-initialization)
```javascript
// Component: new_component.js
class NewComponent {
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
        // Component initialization
    }
    
    // Public API methods
}

// Auto-initialization
document.addEventListener('DOMContentLoaded', function() {
    const elements = document.querySelectorAll('[data-new-component]');
    elements.forEach(el => new NewComponent(el));
});

// Export for manual use
window.NewComponent = NewComponent;
```

### Component Integration in Layouts

#### Include Component in Layout
```jinja2
{# In layouts/simple.html #}
{% extends "base.html" %}

{# Include components (assets loaded automatically) #}
{% include 'components/search/_search.html' %}
{% include 'components/character_icons/_character_icons.html' %}

{% block nav_extras %}
{# Use component macros #}
{{ search.navbar_form() }}
{% endblock %}

{% block content_wrapper %}
<div class="container mt-4">
    {# Character icons available automatically #}
    {% block content %}{% endblock %}
</div>
{% endblock %}
```

## Current Component Packages

### `search` Component Package ✅ IMPLEMENTED
**Purpose**: Player search functionality across all layouts

**Files:**
- `_search.html` - Search form macros + asset imports
- `search.css` - Search form styling
- `search.js` - Search behavior and URL encoding

**Macros:**
- `navbar_form()` - Navigation bar search
- `main_search()` - Homepage hero search  
- `filter_search()` - Player page filtering

**Usage:**
```jinja2
{% include 'components/search/_search.html' %}
{{ search.navbar_form("Find Player...") }}
{{ search.main_search("Search Players") }}
```

### `character_icons` Component Package ✅ IMPLEMENTED
**Purpose**: Character portrait display system

**Files:**
- `_character_icons.html` - Icon initialization + asset imports
- `character_icons.css` - Icon styling and fallbacks
- `character_icons.js` - Icon loading and management

**Features:**
- Automatic icon loading via `data-character-name` attribute
- Fallback styling for missing characters
- Responsive icon sizing (24x24 inline, 96x96 banners)
- Support for all 26 Melee characters

**Usage:**
```html
<!-- Automatic icon loading -->
<span data-character-name="Fox" class="character-container"></span>
```

### `player_title` Component Package ✅ IMPLEMENTED
**Purpose**: Dynamic player header with stats and navigation

**Files:**
- `_player_title.html` - Title container + asset imports
- `player_title.css` - Player header styling
- `player_title.js` - Dynamic title generation

**Features:**
- Real-time "last played" calculation
- Player status badges (Active/Inactive)
- Quick stats display
- Navigation tabs with proper URL encoding

**Usage:**
```jinja2
{% include 'components/player_title/_player_title.html' %}
<!-- Container populated by JavaScript -->
<div id="player-title-container"></div>
```

### `game_table` Component Package 🔄 PLANNED
**Purpose**: Consistent game data table display

**Planned Files:**
- `_game_table.html` - Table macros + asset imports
- `game_table.css` - Table styling
- `game_table.js` - Table interactions

**Planned Macros:**
- `recent_games_table()` - Homepage format
- `player_games_table()` - Player page format
- `detailed_games_table()` - Filterable format

## Data Structure Standards

### Backend Data Contract
All components use **standardized data structures** from the backend service layer:

#### Recent Games Data Structure
```json
{
  "game_id": "unique_identifier",
  "start_time": "2025-06-21T03:18:28Z",
  "stage_id": 32,
  "result": "Win - PLAYER1 vs PLAYER2",
  
  // Homepage format (player1/player2)
  "player1": "PLAYER#123",
  "player1_tag_encoded": "PLAYER%23123", 
  "character1": "Fox",
  "player2": "OPPONENT#456",
  "player2_tag_encoded": "OPPONENT%23456",
  "character2": "Falco",
  
  // Player page format (player/opponent)
  "player": {
    "player_tag": "PLAYER#123",
    "character_name": "Fox"
  },
  "opponent": {
    "player_tag": "OPPONENT#456", 
    "character_name": "Falco",
    "encoded_tag": "OPPONENT%23456"
  }
}
```

#### Player Statistics Data Structure
```json
{
  "total_games": 1995,
  "wins": 997,
  "win_rate": 0.5,             // Decimal format (0.0-1.0)
  "most_played_character": "Fox",
  "character_stats": {
    "Fox": {
      "games": 500,
      "wins": 300,
      "win_rate": 0.6
    }
  }
}
```

## Page Template Examples

### Homepage Template (`pages/index.html`)
```jinja2
{% extends "layouts/simple.html" %}

{% block title %}Slippi Stats - Homepage{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/index.css') }}">
{% endblock %}

{% block content %}
<!-- Hero Section -->
<div class="hero-section text-center mb-5">
    <h1 class="display-4 fw-bold mb-3">Slippi Stats</h1>
    <p class="lead mb-4">Track your Super Smash Bros. Melee performance</p>
    
    {# Use search component macro from layout #}
    {{ search.main_search("Find a Player", "Enter player tag...") }}
</div>

<!-- Recent Games -->
{% if recent_games %}
<div class="section mb-5">
    <h2>Recent Games</h2>
    <div class="table-responsive">
        <table class="table">
            <tbody>
                {% for game in recent_games %}
                <tr>
                    <td>
                        <a href="/player/{{ game.player1_tag_encoded }}">{{ game.player1 }}</a>
                        vs
                        <a href="/player/{{ game.player2_tag_encoded }}">{{ game.player2 }}</a>
                    </td>
                    <td>
                        {# Character icons work automatically from layout #}
                        <span data-character-name="{{ game.character1 }}" class="character-container"></span>{{ game.character1 }}
                        vs
                        <span data-character-name="{{ game.character2 }}" class="character-container"></span>{{ game.character2 }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endif %}
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/index.js') }}"></script>
{% endblock %}
```

### Players Page Template (`pages/players.html`)
```jinja2
{% extends "layouts/simple.html" %}

{% block title %}All Players - Slippi Stats{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/players.css') }}">
{% endblock %}

{% block content %}
<h1>All Players</h1>

{# Use filter search from layout #}
{{ search.filter_search("playersTable", "Search players...") }}

<div class="table-responsive">
    <table class="table" id="playersTable">
        <thead>
            <tr>
                <th>Player</th>
                <th>Games</th>
                <th>Win Rate</th>
                <th>Most Played</th>
            </tr>
        </thead>
        <tbody>
            {% for player in players %}
            <tr class="player-row">
                <td>
                    <a href="/player/{{ player.code_encoded }}">{{ player.name }}</a>
                </td>
                <td>{{ player.games }}</td>
                <td>{{ (player.win_rate * 100) | round(1) }}%</td>
                <td>
                    {# Character icons work automatically #}
                    <span data-character-name="{{ player.most_played_character }}" class="character-container"></span>
                    {{ player.most_played_character }}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/players.js') }}"></script>
{% endblock %}
```

### Player Profile Template (`pages/player_basic.html`)
```jinja2
{% extends "layouts/player.html" %}

{% block title %}{{ player_code }} - Player Profile{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/player_basic.css') }}">
{% endblock %}

{% block content %}
{# Player title component container - populated by layout JavaScript #}
<!-- Title populated automatically by player_title component -->

<!-- Player Stats -->
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5>Games Played</h5>
                <h2>{{ stats.total_games }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5>Win Rate</h5>
                <h2>{{ (stats.win_rate * 100) | round(1) }}%</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h5>Main Character</h5>
                <div>
                    {# Character icon works automatically #}
                    <span data-character-name="{{ stats.most_played_character }}" class="character-container"></span>
                    {{ stats.most_played_character }}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Games -->
{# Future: Use game_table component macro #}
<div class="card">
    <div class="card-header">
        <h5>Recent Games</h5>
    </div>
    <div class="table-responsive">
        <table class="table mb-0">
            <thead>
                <tr>
                    <th>Opponent</th>
                    <th>Characters</th>
                    <th>Result</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for game in recent_games[:10] %}
                <tr>
                    <td>
                        <a href="/player/{{ game.opponent.encoded_tag }}">{{ game.opponent.player_tag }}</a>
                    </td>
                    <td>
                        <span data-character-name="{{ game.player.character_name }}" class="character-container"></span>{{ game.player.character_name }}
                        vs
                        <span data-character-name="{{ game.opponent.character_name }}" class="character-container"></span>{{ game.opponent.character_name }}
                    </td>
                    <td>
                        <span class="badge bg-{{ 'success' if game.result == 'Win' else 'danger' }}">
                            {{ game.result }}
                        </span>
                    </td>
                    <td>{{ game.start_time }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/pages/player_basic.js') }}"></script>
{% endblock %}
```

## Component Usage Patterns

### Data Attribute Integration
Components use data attributes for configuration:

```html
<!-- Character icons -->
<span data-character-name="Fox" class="character-container"></span>

<!-- Search forms -->
<form data-search-type="player" data-target="#results"></form>

<!-- Player title -->
<div id="player-title-container" data-player-code="{{ player_code }}"></div>
```

### JSON Data Scripts
For complex data, use JSON script tags to pass data to components:

```jinja2
<!-- Player data for JavaScript components -->
<script type="application/json" id="player-data">
{
    "playerCode": {{ (player_code | tojson) if player_code is defined else '""' }},
    "stats": {{ (stats | tojson) if stats is defined else '{}' }},
    "recentGames": {{ (recent_games | tojson) if recent_games is defined else '[]' }}
}
</script>
```

### Component Macro Usage
```jinja2
<!-- Basic usage -->
{{ search.navbar_form() }}

<!-- With parameters -->
{{ search.main_search("Find a Player", "Enter player tag...") }}

<!-- With options -->
{{ search.filter_search("playersTable", "Search...", show_count=true) }}
```

## Best Practices

### Template Organization
1. **Single Responsibility**: Each template focuses on one concern
2. **Component Isolation**: Components are self-contained packages
3. **Layout Orchestration**: Layouts manage component integration
4. **Page Content Focus**: Pages only handle content and page-specific needs

### Component Development
1. **Self-Contained**: Each component manages its own assets
2. **Data Attribute Driven**: Use `data-*` attributes for configuration
3. **Auto-Initialization**: Components initialize themselves on page load
4. **Public APIs**: Expose clean interfaces for external use
5. **Responsive Design**: All components work across device sizes

### Data Handling
1. **Backend Conformance**: Use data structures as provided by services
2. **No Data Transformation**: Templates display data, services process data
3. **Safe Defaults**: Always check if variables exist before using
4. **Consistent Formatting**: Use established patterns for display

### Asset Management
1. **Component-Level Assets**: Components import their own CSS/JS
2. **Page-Level Assets**: Pages import only page-specific CSS/JS
3. **Base-Level Assets**: Base imports only global foundation assets
4. **No Asset Duplication**: Each asset imported only where needed

## Migration Strategy

### From Current to Component Architecture

#### 1. Create Component Packages
- Extract existing component CSS/JS into component packages
- Create component templates with asset imports
- Add component macros for reusability

#### 2. Update Layouts
- Remove direct CSS/JS imports
- Include component templates
- Use component macros instead of hardcoded HTML

#### 3. Update Pages
- Remove component imports from pages
- Use component macros provided by layouts
- Keep only page-specific assets

#### 4. Test Integration
- Verify all components load correctly
- Test component functionality across pages
- Ensure no duplicate asset loading

## Current Status

### ✅ Foundation Complete
- **Base template**: Minimal foundation with Bootstrap only
- **Layout inheritance**: Clean separation of concerns
- **Data structures**: Standardized backend integration

### 🔄 Component Migration In Progress
- **search component**: Partially implemented
- **character_icons component**: Implemented
- **player_title component**: Implemented
- **game_table component**: Planned

### 📋 Next Steps
1. Complete search component package
2. Create game_table component package
3. Update layouts to use component packages
4. Update pages to use component macros
5. Test end-to-end functionality

The template system provides a solid foundation for the component-based architecture while maintaining clean separation between presentation and business logic.