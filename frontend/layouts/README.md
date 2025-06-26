# Layouts Architecture

This directory contains layout templates that orchestrate components and define page structure. Layouts follow the **"Layouts Share"** principle - they import components and make them available to pages.

## Core Principle: Layouts Share

Layouts are responsible for:
- **✅ Component orchestration** - Import and configure components for pages
- **✅ Page structure definition** - Navigation, content areas, footers
- **✅ Template composition** - Combine components into reusable patterns
- **✅ Macro provision** - Make component macros available to pages
- **❌ NOT business logic** - No data processing or API calls
- **❌ NOT their own assets** - No layout-specific CSS/JS files
- **❌ NOT direct DOM manipulation** - Components handle interactions

## Directory Structure

```
frontend/layouts/
├── README.md              # This file
├── simple.html            # Simple layout with basic navigation
├── player.html            # Player-specific layout with search
├── admin.html             # Admin layout with additional navigation
└── minimal.html           # Minimal layout for landing pages
```

## Layout Template Pattern

Every layout follows this pattern:

```jinja2
{% extends "base.html" %}

{# ============================================================================= #}
{# COMPONENT IMPORTS - Make macros available to pages #}
{# ============================================================================= #}
{% from 'components/search/_search.html' import navbar_search, filter_search %}
{% from 'components/cards/_cards.html' import hero_stats_card, action_card %}
{% from 'components/navbar/_navbar.html' import navbar %}

{# ============================================================================= #}
{# COMPONENT INCLUDES - Load component assets #}
{# ============================================================================= #}
{% include 'components/search/_search.html' %}
{% include 'components/cards/_cards.html' %}
{% include 'components/navbar/_navbar.html' %}

{# ============================================================================= #}
{# LAYOUT CONFIGURATION #}
{# ============================================================================= #}
{% block navbar_config %}
{{ navbar("simple", {
    'search_enabled': true,
    'brand_text': 'Slippi Stats'
}) }}
{% endblock %}

{# ============================================================================= #}
{# NO LAYOUT-SPECIFIC ASSETS #}
{# Components manage their own CSS/JS via includes above #}
{# ============================================================================= #}
```

## Existing Layouts

### Simple Layout (`simple.html`)
**Purpose**: Basic layout for most pages with standard navigation and search

**Components Used**:
- Navbar with search functionality
- Search components (navbar and filter variants)
- Basic card components
- Character icons

**Available Macros for Pages**:
```jinja2
{# Navigation and search #}
{{ navbar_search(show, placeholder) }}
{{ filter_search(target, placeholder, show_count) }}

{# Content cards #}
{{ hero_stats_card(stats) }}
{{ action_card(title, content, actions) }}
```

**Page Usage Example**:
```jinja2
{% extends "layouts/simple.html" %}
{% block content %}
{{ filter_search("playersTable", "Search players...") }}
<div class="content">...</div>
{% endblock %}
```

### Player Layout (`player.html`)
**Purpose**: Specialized layout for player profile pages

**Additional Components**:
- Advanced filtering components
- Player-specific navigation
- Statistics visualization components

**Enhanced Features**:
- Player context in navigation
- Breadcrumb navigation
- Related player suggestions

### Admin Layout (`admin.html`)
**Purpose**: Administrative interface layout

**Additional Components**:
- Admin navigation sidebar
- Data management components
- System status indicators

**Security Features**:
- Admin-only navigation items
- System health monitoring
- User management