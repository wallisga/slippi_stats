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
    ├── player_index.html       # All players listing
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
- **Pages**: `index.html`, `download.html`, `how_to.html`

#### `player.html` 
- **Use Case**: Player-focused pages requiring enhanced functionality
- **Features**: 
  - Player search form in navigation
  - Player dropdown navigation
  - Character icon support
  - Player title component container
  - Enhanced CSS/JS for player functionality
- **Pages**: `player_basic.html`, `player_detailed.html`

#### `error.html`
- **Use Case**: Error pages with specialized styling
- **Features**: Error-specific styling and layout
- **Pages**: `error_status.html`, `error_exception.html`

### Layer 3: Page Templates (`pages/`)
**Purpose**: Final content layer with specific page implementation

**Inheritance Pattern:** `base.html` → `layouts/*.html` → `pages/*.html`

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

### Data Passing Conventions

#### Standard Context Variables
- `request` - Flask request object (available in all templates)
- Page-specific data passed from route handlers

#### Player Page Context
Player pages receive standardized data structure:
```python
{
    'player_code': str,           # Raw player tag
    'encoded_player_code': str,   # URL-encoded player tag  
    'stats': dict,               # Player statistics
    'recent_games': list,        # Recent game data
    'all_games': list           # Complete game history (if needed)
}
```

#### JSON Data Scripts
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

## File Descriptions

### Base Template
- **`base.html`**: Core template with navigation, Bootstrap, and basic structure

### Layout Templates
- **`simple.html`**: Basic layout for informational pages
- **`player.html`**: Enhanced layout with player search and navigation features  
- **`error.html`**: Specialized layout for error pages with appropriate styling

### Page Templates

#### Core Pages
- **`index.html`**: Homepage with recent games and top players
- **`download.html`**: Client download page with instructions
- **`how_to.html`**: Setup and usage instructions

#### Player Pages  
- **`player_basic.html`**: Basic player profile with overview stats and recent games
- **`player_detailed.html`**: Advanced analytics with filtering and charts
- **`players.html`**: Index of all players with search functionality

#### Error Pages
- **`error_status.html`**: HTTP error pages (404, 500, etc.)
- **`error_exception.html`**: Unhandled exception display

## Best Practices

### Template Organization
1. **Single Responsibility**: Each template should have one clear purpose
2. **Proper Inheritance**: Always extend appropriate layout, never base directly
3. **Block Usage**: Override only necessary blocks, maintain parent functionality
4. **Asset Management**: Use appropriate CSS/JS blocks for each layer

### Data Handling
1. **Context Validation**: Always check if variables exist before using
2. **Safe Defaults**: Provide fallback values for optional data
3. **JSON Encoding**: Use `| tojson` filter for complex data structures
4. **URL Encoding**: Use `| urlencode` for player tags in URLs

### Performance Considerations
1. **Minimize Data**: Only pass necessary data to templates
2. **Lazy Loading**: Use AJAX for optional or heavy data
3. **Caching**: Consider template caching for static content
4. **Asset Optimization**: Minimize CSS/JS includes per page

### Maintainability
1. **Consistent Naming**: Follow established naming conventions
2. **Documentation**: Comment complex template logic
3. **Modularity**: Keep templates focused and reusable
4. **Testing**: Ensure templates work with various data scenarios