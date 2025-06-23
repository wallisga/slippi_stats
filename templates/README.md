# Templates Directory

This directory contains all Jinja2 templates organized using a **layered inheritance pattern** for maximum maintainability and code reuse.

## Architecture Overview

```
templates/
├── base.html                    # Foundation layer
├── layouts/                     # Layout layer
│   ├── simple.html             # Minimal layout
│   ├── player.html             # Player-focused layout  
│   └── error.html              # Error handling layout
└── pages/                      # Content layer
    ├── index.html              # Homepage
    ├── player_basic.html       # Basic player profile
    ├── player_detailed.html    # Advanced player statistics
    ├── players.html            # All players listing
    ├── download.html           # Download page
    ├── how_to.html            # Instructions page
    └── error_*.html           # Error pages
```

## Template Inheritance Pattern

### Layer 1: Base Template (`base.html`)
**Purpose**: Provides the foundational HTML structure shared by all pages

**Responsibilities:**
- HTML5 document structure
- Bootstrap CSS/JS integration
- Core navigation bar
- Footer
- Basic responsive layout
- Global JavaScript utilities

**Key Blocks:**
- `title` - Page title
- `layout_css` - Layout-specific stylesheets
- `extra_css` - Page-specific stylesheets  
- `nav_items` - Navigation menu items
- `nav_extras` - Additional navigation elements
- `content_wrapper` - Main content container
- `layout_js` - Layout-specific JavaScript
- `extra_js` - Page-specific JavaScript

### Layer 2: Layout Templates (`layouts/`)
**Purpose**: Extend base template with layout-specific functionality

#### `simple.html`
- **Use Case**: Basic pages (homepage, downloads, instructions)
- **Features**: Minimal navigation, standard container
- **Components**: Character icons, search functionality
- **Pages**: `index.html`, `download.html`, `how_to.html`, `players.html`

#### `player.html` 
- **Use Case**: Player-focused pages requiring enhanced functionality
- **Features**: 
  - Player search form in navigation
  - Player dropdown navigation
  - Character icon support
  - Player title component container
  - Enhanced CSS/JS for player functionality
- **Components**: All simple.html components plus player-specific components
- **Pages**: `player_basic.html`, `player_detailed.html`

#### `error.html`
- **Use Case**: Error pages with specialized styling
- **Features**: Error-specific styling and layout
- **Pages**: `error_status.html`, `error_exception.html`

### Layer 3: Page Templates (`pages/`)
**Purpose**: Final content layer with specific page implementation

**Inheritance Pattern:** `base.html` → `layouts/*.html` → `pages/*.html`

## Current Data Structure Standards

### Backend Data Contract
All templates now use **standardized data structures** from the backend service layer:

#### Recent Games Data Structure (Consistent Across All Pages)
```json
{
  "game_id": "unique_identifier",
  "start_time": "2025-06-21T03:18:28Z",
  "time": "2025-06-21T03:18:28Z",  // Alias for frontend compatibility
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

#### Top Players Data Structure
```json
{
  "name": "PLAYER#123",        // Frontend expects 'name'
  "code": "PLAYER#123",        // Frontend expects 'code'  
  "code_encoded": "PLAYER%23123", // Frontend expects 'code_encoded'
  "games": 150,
  "wins": 75,
  "win_rate": 0.5              // Decimal format (0.0 - 1.0)
}
```

#### Player Statistics Data Structure
```json
{
  "total_games": 1995,
  "wins": 997,
  "win_rate": 0.5,             // Decimal format
  "most_played_character": "Fox",
  "best_character": "Falco", 
  "worst_character": "Ganondorf",
  "character_stats": {
    "Fox": {
      "games": 500,
      "wins": 300,
      "win_rate": 0.6
    }
  },
  "rival": {
    "opponent_tag": "RIVAL#456",
    "opponent_char": "Sheik", 
    "games": 25,
    "wins": 10,
    "win_rate": 0.4
  },
  "rising_star": "Marth",      // Recent best character
  "best_stage": {
    "id": 32,
    "games": 200,
    "wins": 120,
    "win_rate": 0.6
  },
  "worst_stage": {
    "id": 8,
    "games": 100, 
    "wins": 30,
    "win_rate": 0.3
  }
}
```

## Template Usage Guide

### Creating New Pages

1. **Choose Appropriate Layout:**
   ```jinja2
   {% extends "layouts/simple.html" %}      {# For basic pages #}
   {% extends "layouts/player.html" %}     {# For player pages #}
   {% extends "layouts/error.html" %}      {# For error pages #}
   ```

2. **Override Required Blocks:**
   ```jinja2
   {% block title %}Page Title | Slippi Stats{% endblock %}
   {% block content %}
       <!-- Your page content here -->
   {% endblock %}
   ```

3. **Add Page-Specific Assets:**
   ```jinja2
   {% block extra_css %}
   <link rel="stylesheet" href="{{ url_for('static', filename='css/pages/your_page.css') }}">
   {% endblock %}
   
   {% block extra_js %}
   <script src="{{ url_for('static', filename='js/pages/your_page.js') }}"></script>
   {% endblock %}
   ```

### Data Display Conventions

#### Win Rate Display (Consistent Format)
```jinja2
<!-- Convert decimal to percentage for display -->
{{ (player.win_rate * 100) | round(1) }}%

<!-- Color coding based on win rate -->
<span class="text-{{ 'success' if stats.win_rate >= 0.6 else 'warning' if stats.win_rate >= 0.4 else 'danger' }}">
    {{ (stats.win_rate * 100) | round(1) }}%
</span>
```

#### Player Links (Consistent URL Encoding)
```jinja2
<!-- Use pre-encoded URLs when available -->
<a href="/player/{{ player.code_encoded }}">{{ player.name }}</a>

<!-- For opponent data with encoded_tag -->
<a href="/player/{{ game.opponent.encoded_tag }}">{{ game.opponent.player_tag }}</a>

<!-- Manual encoding when needed -->
<a href="/player/{{ player_tag | urlencode }}">{{ player_tag }}</a>
```

#### Character Icons (Consistent Integration)
```jinja2
<!-- Character with icon -->
<span data-character-name="{{ character_name }}" class="character-container me-2"></span>
{{ character_name }}

<!-- Character icons are automatically loaded by character_icons.js -->
```

### Data Passing Conventions

#### Standard Context Variables
- `request` - Flask request object (available in all templates)
- Page-specific data passed from service layer

#### Player Page Context (Standardized)
Player pages receive standardized data structure:
```python
{
    'player_code': str,           # Raw player tag
    'encoded_player_code': str,   # URL-encoded player tag  
    'stats': dict,               # Player statistics (see structure above)
    'recent_games': list,        # Recent game data (see structure above)
    'all_games': list           # Complete game history (if needed)
}
```

#### Homepage Context (Standardized)
```python
{
    'app_stats': {
        'total_games': int,
        'total_players': int, 
        'latest_game_date': str,
        'stats_generated_at': str
    },
    'recent_games': list,        # Recent games (player1/player2 format)
    'top_players': list         # Top players (name/code format)
}
```

#### JSON Data Scripts (For Complex Data)
For complex data, use JSON script tags to avoid HTML attribute limits:
```jinja2
<script type="application/json" id="player-data">
{
    "playerCode": {{ (player_code | tojson) if player_code is defined else '""' }},
    "stats": {{ (stats | tojson) if stats is defined else '{}' }},
    "recentGames": {{ (recent_games | tojson) if recent_games is defined else '[]' }}
}
</script>
```

## Frontend Component Integration

### Character Icons
Character icons are automatically initialized by `character_icons.js` component:
```html
<!-- Any element with data-character-name gets an icon -->
<span data-character-name="Fox" class="character-container"></span>

<!-- Icons are loaded automatically on page load -->
<!-- Call initializeCharacterIcons() after dynamic content changes -->
```

### Player Search
Search functionality is provided by layouts:
- **Simple layout**: No search by default
- **Player layout**: Includes search form in navigation
- **Search component**: Handles player tag encoding and navigation

### Player Title Component
Player pages include an enhanced title component:
```html
<!-- Player title container (populated by JavaScript) -->
<div id="player-title-container">
    <!-- Generated by PlayerTitle component -->
</div>

<!-- Player title shows: name, status, stats, navigation tabs -->
```

## File Descriptions

### Base Template
- **`base.html`**: Core template with navigation, Bootstrap, and basic structure

### Layout Templates
- **`simple.html`**: Basic layout for informational pages with character icons and search
- **`player.html`**: Enhanced layout with player search, navigation, and title component
- **`error.html`**: Specialized layout for error pages with appropriate styling

### Page Templates

#### Core Pages
- **`index.html`**: Homepage with recent games and top players (uses standardized data)
- **`download.html`**: Client download page with instructions
- **`how_to.html`**: Setup and usage instructions
- **`players.html`**: Index of all players with search functionality

#### Player Pages  
- **`player_basic.html`**: Basic player profile with overview stats and recent games
- **`player_detailed.html`**: Advanced analytics with filtering and charts

#### Error Pages
- **`error_status.html`**: HTTP error pages (404, 500, etc.)
- **`error_exception.html`**: Unhandled exception display

## Best Practices

### Template Organization
1. **Single Responsibility**: Each template should have one clear purpose
2. **Proper Inheritance**: Always extend appropriate layout, never base directly
3. **Block Usage**: Override only necessary blocks, maintain parent functionality
4. **Consistent Data**: Use standardized data structures from backend services

### Data Handling Standards
1. **Backend Conformance**: Templates must use data as provided by service layer
2. **No Data Transformation**: Templates display data, services process data
3. **Safe Defaults**: Always check if variables exist before using
4. **Consistent Format**: Use established patterns for win rates, URLs, etc.

### Component Integration
1. **Character Icons**: Use `data-character-name` attribute consistently
2. **Player Links**: Use pre-encoded URLs when available
3. **Search Forms**: Let layout handle search functionality
4. **JSON Data**: Use script tags for complex data structures

### Performance Considerations
1. **Minimize Data**: Only pass necessary data to templates
2. **Lazy Loading**: Use AJAX for optional or heavy data
3. **Component Reuse**: Leverage existing components rather than duplicating
4. **Asset Optimization**: Minimize CSS/JS includes per page

### Maintainability
1. **Consistent Naming**: Follow established naming conventions
2. **Data Contract**: Maintain compatibility with service layer data structures
3. **Component System**: Use modular frontend components
4. **Documentation**: Comment complex template logic

## Current Status

### ✅ Completed Features
- **Layered template inheritance** with proper separation of concerns
- **Standardized data structures** that match backend service layer
- **Consistent component integration** across all pages
- **Proper URL encoding** and player link handling
- **Character icon system** that works across all templates
- **Responsive design** with Bootstrap integration

### Template-Backend Integration
- **Homepage**: Uses standardized recent games and top players data
- **Player Pages**: Uses consistent player statistics and game data structures  
- **All Pages**: Character icons, search, and navigation work consistently
- **Error Handling**: Proper error page templates with backend integration

The template system now provides a solid foundation that works seamlessly with the refactored backend architecture while maintaining clean separation between presentation and business logic.