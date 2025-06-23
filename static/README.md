# Static Directory

This directory contains all client-side assets (CSS, JavaScript, images) organized by type and functionality for optimal maintainability and performance.

## Directory Structure (Current)

```
static/
├── css/
│   ├── base.css                 # Global styles and CSS variables
│   ├── components/              # Reusable component styles
│   │   ├── cards.css           # Card component styling
│   │   ├── tables.css          # Table component styling
│   │   ├── character_icons.css # Character icon styling
│   │   └── player_title.css    # Player title component styling
│   └── pages/                   # Page-specific styles
│       ├── index.css           # Homepage styles
│       ├── players.css         # Player index page styles
│       ├── player_basic.css    # Basic player page styles
│       └── player_detailed.css # Detailed player page styles
├── js/
│   ├── base.js                 # Global JavaScript utilities
│   ├── components/             # Reusable JavaScript components
│   │   ├── character_icons.js  # Character icon management
│   │   ├── player_title.js     # Dynamic player header component
│   │   ├── search.js           # Player search functionality
│   │   └── player_dropdown.js  # Player navigation dropdown
│   └── pages/                  # Page-specific JavaScript
│       ├── index.js            # Homepage interactivity
│       ├── players.js          # Player index functionality
│       ├── player_basic.js     # Basic player page functionality
│       └── player_detailed.js  # Advanced filtering and charts
└── icons/
    └── character/              # Character icon images (PNG format)
        ├── neutral Fox.png
        ├── neutral Falco.png
        ├── neutral Marth.png
        └── [26 total Melee characters]
```

## CSS Architecture

### Base Styles (`base.css`)
**Purpose**: Provides foundation styles and CSS custom properties used throughout the application

**Contents:**
- CSS custom properties (variables) for colors, spacing, fonts
- Global utility classes
- Base typography and layout styles  
- Responsive breakpoints and mixins
- Bootstrap customizations and overrides

**Key Features:**
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    /* Theme variables for consistent styling */
}
```

### Component Styles (`components/`)
**Purpose**: Self-contained styles for reusable UI components

#### `cards.css` ✅ ACTIVE
- Styling for card-based layouts across all pages
- Stat cards, game cards, info cards
- Hover effects and responsive behavior
- Card grid layouts for homepage and player pages

#### `tables.css` ✅ ACTIVE
- Enhanced table styling beyond Bootstrap defaults
- Game tables on player pages and homepage
- Hover effects and row highlighting
- Responsive table behaviors
- Game result styling (win/loss indicators)

#### `character_icons.css` ✅ ACTIVE
- Character portrait display and positioning
- Icon sizing variants (24x24 for inline, 96x96 for banners)
- Fallback styling for missing characters
- Integration with character_icons.js component

#### `player_title.css` ✅ ACTIVE
- Player header component styling
- Stats display and layout (games, win rate, characters)
- Navigation tabs and status badges
- Responsive player title behavior

### Page Styles (`pages/`)
**Purpose**: Styles specific to individual pages

#### `index.css` ✅ ACTIVE
- Homepage hero section and jumbotron
- Recent games and top players sections
- Stats overview cards
- Search container styling

#### `players.css` ✅ ACTIVE
- Player index page layout
- Player card grid styling
- Search and filter controls

#### `player_basic.css` ✅ ACTIVE
- Basic player profile layout
- Performance overview sections
- Recent games table customizations
- Highlights card styling

#### `player_detailed.css` ✅ ACTIVE
- Advanced filtering interface
- Chart container styling (Chart.js integration)
- Complex stats table layouts
- Filter toggle and checkbox styling
- Loading overlay and animation styles

## JavaScript Architecture

### Base JavaScript (`base.js`) ✅ ACTIVE
**Purpose**: Global utilities and player search functionality used across all pages

**Contents:**
- Player search form handlers
- Global error handling utilities
- Common initialization code

**Key Functions:**
```javascript
// Player search functionality
function initializePlayerSearch() { /* handles search forms */ }

// Auto-initializes on DOMContentLoaded
```

### Component JavaScript (`components/`)
**Purpose**: Reusable JavaScript modules for specific UI components

#### `character_icons.js` ✅ ACTIVE
**Purpose**: Manages character portrait display throughout the application

**Features:**
- Automatic icon loading for elements with `data-character-name` attribute
- Fallback handling for missing characters with styled placeholders
- Character mapping for consistent naming
- Auto-initialization on page load

**Character Support:**
- All 26 Super Smash Bros. Melee characters
- Handles name variations (e.g., "Dr. Mario" vs "Doctor Mario")
- PNG format icons (24x24 and 96x96 sizes)

**Usage:**
```javascript
// Automatic initialization
// Just add data-character-name="Fox" to any element

// Manual initialization for dynamic content
initializeCharacterIcons(containerElement);
```

#### `player_title.js` ✅ ACTIVE
**Purpose**: Dynamic player header component with comprehensive player information

**Features:**
- Player status display (Active/Inactive based on recent games)
- Game statistics overview (games, wins, main character)
- Last played calculation with real-time updates
- Navigation tabs (Overview/Detailed Stats)
- Integration with recent games data for activity status

**Usage:**
```javascript
const playerTitle = new PlayerTitle(playerCode, encodedPlayerCode, {
    currentPage: 'overview',
    stats: playerStats,
    recentGames: recentGames,
    showQuickStats: true
});
```

#### `search.js` ✅ ACTIVE
**Purpose**: Player search functionality for navigation bars

**Features:**
- Player tag URL encoding
- Search form submission handling
- Integration with navigation layouts

**Usage:**
```javascript
// Auto-initializes on DOMContentLoaded
// Works with forms having playerSearchForm ID
```

#### `player_dropdown.js` ✅ ACTIVE
**Purpose**: Enhanced navigation dropdown for player pages

**Features:**
- Dynamic URL generation with proper encoding
- Current page highlighting (basic vs detailed)
- Player code encoding/decoding
- Active state management

### Page JavaScript (`pages/`)
**Purpose**: Page-specific functionality and event handling

#### `index.js` ✅ ACTIVE
**Purpose**: Homepage interactivity and dynamic content

**Features:**
- Last updated time fetching from API
- Main page search functionality (separate from navbar)
- Game time formatting for recent games table
- Player card click analytics
- Keyboard shortcuts (Ctrl+K for search focus)
- Dynamic stats updates every 5 minutes

**API Integration:**
- `/api/stats` endpoint for server statistics
- Real-time last updated display

#### `players.js` ✅ ACTIVE
**Purpose**: Player index page functionality

**Features:**
- Player search and filtering
- Player card interactions
- Sorting and pagination

#### `player_basic.js` ✅ ACTIVE
**Purpose**: Basic player profile page functionality

**Features:**
- Player title component initialization
- Load more games functionality with pagination
- Game table interactions and hover effects
- Dynamic game row creation for AJAX-loaded content

**API Integration:**
- `/api/player/{code}/games` for pagination
- Proper error handling and loading states

#### `player_detailed.js` ✅ ACTIVE
**Purpose**: Advanced player analysis page with comprehensive filtering

**Features:**
- **Advanced Filtering System:**
  - Character filter (multi-select checkboxes)
  - Opponent filter (multi-select)
  - Opponent character filter (multi-select)
  - Filter state persistence and restoration
- **Real-time Chart Updates:**
  - Chart.js integration for time series and character performance
  - Dynamic chart data binding
  - Error handling for missing Chart.js
- **Statistics Recalculation:**
  - Live updating of win rates and game counts
  - Character, opponent, and matchup statistics
  - Date-based performance tracking

**API Integration:**
- `POST /api/player/{code}/detailed` with filter parameters
- Complex filter data processing and validation
- Loading states and error handling

**Chart.js Integration:**
```javascript
// Time series chart for win rate over time
updateTimeChart(dateStats);

// Character performance chart
updateCharacterChart(characterStats);
```

## Current Component System

### Character Icon System ✅ FULLY IMPLEMENTED
**How It Works:**
1. Add `data-character-name="Fox"` to any HTML element
2. `character_icons.js` automatically finds and processes these elements
3. Creates `<img>` elements with proper fallbacks
4. Handles all 26 Melee characters with name variations

**Integration Points:**
- Homepage recent games table
- Player pages (title, games, stats)
- All templates with character references

### Player Title System ✅ FULLY IMPLEMENTED
**Dynamic Features:**
- Real-time "last played" calculation with minute-by-minute updates
- Player status badges (Active/Inactive)
- Quick stats display (games, win rate, characters)
- Character icon integration for main character
- Navigation tabs with proper URL encoding

### Search System ✅ FULLY IMPLEMENTED
**Multi-Level Integration:**
- Global search in navigation (player layout)
- Main page search (homepage)
- Keyboard shortcuts and accessibility
- Proper URL encoding for player tags

### Filtering System ✅ FULLY IMPLEMENTED
**Advanced Capabilities:**
- Multi-select checkboxes with "select all" functionality
- Real-time filter application
- Filter state restoration
- Complex filter combinations (character + opponent + opponent character)

## Data Integration with Backend

### Standardized Data Consumption
All frontend components now consume **standardized data structures** from the backend service layer:

#### Recent Games Format
```javascript
{
  game_id: "unique_id",
  start_time: "2025-06-21T03:18:28Z", 
  player: {
    player_tag: "PLAYER#123",
    character_name: "Fox"
  },
  opponent: {
    player_tag: "OPPONENT#456",
    character_name: "Falco", 
    encoded_tag: "OPPONENT%23456"
  },
  result: "Win|Loss"
}
```

#### Player Statistics Format
```javascript
{
  total_games: 1995,
  wins: 997,
  win_rate: 0.5,  // Decimal format (0.0-1.0)
  most_played_character: "Fox",
  character_stats: { /* character breakdown */ },
  // ... other stats
}
```

### Frontend-Backend Contract
- **Templates display data as-is** - no data transformation in frontend
- **Services process data** - all business logic in backend
- **Consistent formatting** - win rates, URLs, character names
- **Error handling** - graceful degradation when data missing

## External Dependencies

### CSS Libraries
- **Bootstrap 5.3.0**: Primary CSS framework and responsive grid
- **Bootstrap Icons**: Icon font for UI elements throughout the app

### JavaScript Libraries
- **Bootstrap 5.3.0**: JavaScript components (dropdowns, modals, collapse)
- **Chart.js 3.9.1**: Data visualization library for player detailed page

### Browser APIs
- **Fetch API**: For AJAX requests to backend APIs
- **Local Storage**: Not used (by design - stateless frontend)
- **History API**: For navigation without page reloads

## Performance Optimizations

### Current Implementations
- **Component-based loading**: Each page only loads required CSS/JS
- **Character icon lazy loading**: Icons load on demand
- **AJAX pagination**: Load more games without page refresh
- **Debounced updates**: Filter applications don't spam the server
- **Caching**: Browser caching for static assets (icons, CSS, JS)

### Asset Organization
- **Modular CSS**: Base → Components → Pages hierarchy
- **Progressive JavaScript**: Core functionality → Enhanced features
- **CDN Integration**: Bootstrap and Chart.js from CDN
- **Optimized Images**: Character icons in appropriate sizes

## Development Guidelines

### Adding New Components
1. **CSS Component**: Add to `components/` directory
2. **JavaScript Component**: Add to `components/` with auto-initialization
3. **Integration**: Update appropriate layout template
4. **Documentation**: Update this README with component details

### Page-Specific Features
1. **CSS**: Add to `pages/` directory matching template name
2. **JavaScript**: Add to `pages/` with DOMContentLoaded initialization
3. **Template Integration**: Use appropriate block overrides
4. **API Integration**: Follow established patterns for data fetching

### Component Development Standards
1. **Self-Contained**: Components work independently
2. **Data Attribute Driven**: Use `data-*` attributes for configuration
3. **Auto-Initialization**: Components initialize themselves on page load
4. **Error Resilience**: Graceful degradation when dependencies missing
5. **Responsive Design**: All components work across device sizes

### Code Style Standards
- **Modern JavaScript**: ES6+ features, const/let over var
- **CSS Organization**: BEM methodology for component classes  
- **Consistent Naming**: Match backend data structure field names
- **Error Handling**: Try/catch blocks and graceful fallbacks
- **Documentation**: JSDoc for complex functions

## Current Status

### ✅ Fully Implemented Features
- **Component System**: All major UI components working
- **Character Icons**: Complete integration across all pages
- **Player Navigation**: Enhanced dropdowns and search
- **Advanced Filtering**: Complex multi-parameter filtering with real-time updates
- **Charts and Visualization**: Chart.js integration with dynamic data
- **Responsive Design**: Works across all device sizes
- **Backend Integration**: Seamless data consumption from service layer

### Architecture Benefits
- **Maintainable**: Clear separation between components and pages
- **Reusable**: Components work across multiple templates
- **Performant**: Optimized loading and minimal dependencies
- **Scalable**: Easy to add new components and pages
- **Consistent**: Standardized patterns for data handling and display

The static asset architecture now provides a comprehensive, working frontend that seamlessly integrates with the refactored backend while maintaining clean separation of concerns and optimal performance.