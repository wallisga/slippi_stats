# Static Directory

This directory contains all client-side assets (CSS, JavaScript, images) organized by type and functionality for optimal maintainability and performance.

## Directory Structure

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
│       ├── player_basic.css    # Basic player page styles
│       ├── player_detailed.css # Detailed player page styles
│       └── index.css           # Homepage styles
├── js/
│   ├── base.js                 # Global JavaScript utilities
│   ├── components/             # Reusable JavaScript components
│   │   ├── character_icons.js  # Character icon management
│   │   ├── player_title.js     # Dynamic player header component
│   │   ├── search.js           # Player search functionality
│   │   └── player_dropdown.js  # Player navigation dropdown
│   └── pages/                  # Page-specific JavaScript
│       ├── player_basic.js     # Basic player page functionality
│       ├── player_detailed.js  # Advanced filtering and charts
│       └── index.js            # Homepage interactivity
└── images/
    └── characters/             # Character portrait images
        ├── fox.png
        ├── falco.png
        └── [other characters]
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
    /* ... other variables */
}
```

### Component Styles (`components/`)
**Purpose**: Self-contained styles for reusable UI components

#### `cards.css`
- Styling for card-based layouts
- Stat cards, game cards, info cards
- Hover effects and responsive behavior
- Card grid layouts

#### `tables.css`
- Enhanced table styling beyond Bootstrap defaults
- Sortable table headers
- Hover effects and row highlighting
- Responsive table behaviors
- Game result styling (win/loss indicators)

#### `character_icons.css`
- Character portrait display and positioning
- Icon sizing variants (small, medium, large)
- Placeholder styling for missing characters
- Responsive character icon behavior

#### `player_title.css`
- Player header component styling
- Stats display and layout
- Action button styling
- Responsive player title behavior

### Page Styles (`pages/`)
**Purpose**: Styles specific to individual pages that don't belong in reusable components

#### `player_basic.css`
- Basic player profile layout
- Recent games table customizations
- Player stats overview styling

#### `player_detailed.css`
- Advanced filtering interface
- Chart container styling
- Complex stats table layouts
- Filter toggle and checkbox styling

#### `index.css`
- Homepage hero section
- Recent activity displays
- Feature highlights styling

## JavaScript Architecture

### Base JavaScript (`base.js`)
**Purpose**: Global utilities and initialization code used across all pages

**Contents:**
- Common utility functions
- Global event listeners
- Bootstrap component initialization
- Error handling utilities
- API request helpers

**Key Functions:**
```javascript
// URL encoding utilities
function encodePlayerTag(tag) { /* ... */ }

// Common AJAX request handler
function apiRequest(url, options) { /* ... */ }

// Global error handling
function handleError(error) { /* ... */ }
```

### Component JavaScript (`components/`)
**Purpose**: Reusable JavaScript modules for specific UI components

#### `character_icons.js`
**Purpose**: Manages character portrait display throughout the application

**Features:**
- Automatic icon loading for character names
- Fallback handling for missing characters
- Lazy loading for performance
- Icon size management

**Usage:**
```javascript
// Initialize icons for all elements with data-character-name
initializeCharacterIcons();

// Initialize icons for specific container
initializeCharacterIcons(containerElement);
```

#### `player_title.js`
**Purpose**: Dynamic player header component with stats and navigation

**Features:**
- Player title display and formatting
- Statistics presentation
- Character dropdown functionality
- Action buttons (view detailed, compare, etc.)

**Usage:**
```javascript
const playerTitle = new PlayerTitle(playerCode, encodedPlayerCode, options);
```

#### `search.js`
**Purpose**: Player search functionality with autocomplete and suggestions

**Features:**
- Real-time search suggestions
- Flexible player name matching
- Keyboard navigation
- Search result formatting

**Usage:**
```javascript
initializePlayerSearch('#searchInput', '#searchResults');
```

#### `player_dropdown.js`
**Purpose**: Enhanced navigation dropdown for player pages

**Features:**
- Dynamic URL generation
- Current page highlighting
- Player code encoding/decoding

### Page JavaScript (`pages/`)
**Purpose**: Page-specific functionality and event handling

#### `player_basic.js`
**Purpose**: Basic player profile page functionality

**Features:**
- Player title component initialization
- Load more games functionality
- Game table interactions
- Character icon initialization

**Key Functions:**
- `initializePlayerTitle()` - Sets up player header
- `initializeLoadMore()` - Handles game pagination
- `appendGamesToTable()` - Adds new games to table

#### `player_detailed.js`
**Purpose**: Advanced player analysis page with filtering and charts

**Features:**
- Complex filtering system (character, opponent, date ranges)
- Real-time chart updates
- Statistics recalculation
- Filter state management

**Key Functions:**
- `fetchPlayerData()` - Gets filtered data from API
- `updateCharts()` - Refreshes Chart.js visualizations
- `applyFilters()` - Processes and applies filter selections
- `updateUI()` - Updates all page elements with new data

#### `index.js`
**Purpose**: Homepage interactivity and dynamic content

**Features:**
- Recent games display
- Top players carousel
- Statistics animations
- Hero section interactions

## Asset Organization Principles

### CSS Organization
1. **Layered Architecture**: Base → Components → Pages
2. **Single Responsibility**: Each file has one clear purpose
3. **Reusability**: Components can be used across multiple pages
4. **Maintainability**: Clear naming and organization patterns

### JavaScript Organization
1. **Modular Design**: Each component is self-contained
2. **Progressive Enhancement**: Core functionality works without JavaScript
3. **Event-Driven**: Components communicate through custom events
4. **Error Resilience**: Graceful degradation when components fail

### Performance Considerations
1. **Minimize HTTP Requests**: Combine related files when possible
2. **Lazy Loading**: Load non-critical assets on demand
3. **Caching**: Leverage browser caching with proper headers
4. **Minification**: Compress assets for production

## Usage Guidelines

### Adding New Styles
1. **Determine Scope**: Is this component-level or page-specific?
2. **Check Existing**: Can existing components/utilities be used?
3. **Follow Patterns**: Use established naming and organization
4. **Document**: Add comments for complex styles

### Adding New JavaScript
1. **Choose Location**: Component (reusable) vs Page (specific)
2. **Dependencies**: Declare required components/libraries
3. **Error Handling**: Include proper try/catch blocks
4. **Documentation**: Comment public functions and complex logic

### Component Development
1. **Self-Contained**: Components should work independently
2. **Configurable**: Use options/parameters for flexibility  
3. **Extensible**: Design for future enhancements
4. **Testable**: Structure for easy unit testing

### File Naming Conventions
- **CSS**: Use descriptive names matching component/page purpose
- **JavaScript**: Match corresponding template/component names
- **Images**: Use clear, descriptive names with appropriate extensions

## External Dependencies

### CSS Libraries
- **Bootstrap 5.3.0**: Primary CSS framework
- **Bootstrap Icons**: Icon font for UI elements

### JavaScript Libraries
- **Bootstrap 5.3.0**: JavaScript components and utilities
- **Chart.js 3.9.1**: Data visualization library for player statistics

### Development Tools
- **Browser DevTools**: Primary debugging and testing environment
- **Responsive Design Mode**: For testing across device sizes

## Best Practices

### CSS Best Practices
1. Use CSS custom properties for maintainable theming
2. Follow BEM methodology for component class naming
3. Prefer flexbox/grid over floats for layouts
4. Use relative units (rem, em, %) for responsive design
5. Minimize nesting depth in stylesheets

### JavaScript Best Practices
1. Use modern ES6+ features where supported
2. Prefer const/let over var
3. Use meaningful variable and function names
4. Handle errors gracefully with try/catch
5. Use JSDoc comments for function documentation

### Performance Best Practices
1. Minimize DOM manipulation
2. Use event delegation for dynamic content
3. Debounce/throttle expensive operations
4. Load non-critical resources asynchronously
5. Optimize images and use appropriate formats