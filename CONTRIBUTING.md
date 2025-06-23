# Contributing to Slippi Stats Server

We welcome contributions to improve the Slippi Stats Server! This guide will help you get started with development and understand our workflow.

## Quick Development Setup

### Windows Users
The fastest way to get started on Windows:

1. **Clone the repository:**
   ```cmd
   git clone <repository-url>
   cd slippi_stats
   ```

2. **Run the setup script:**
   ```cmd
   start_dev_server.bat
   ```

The `start_dev_server.bat` script handles everything automatically:
- ✅ Creates Python virtual environment (`venv/`)
- ✅ Installs all dependencies from `requirements.txt`
- ✅ Sets Flask development environment variables
- ✅ Initializes SQLite database
- ✅ Starts development server at `http://127.0.0.1:5000`

### Manual Setup (All Platforms)
```bash
# Clone and navigate
git clone <repository-url>
cd slippi_stats

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Start development server
python app.py
```

## Development Workflow

### 1. Fork and Clone
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/slippi_stats.git
cd slippi_stats

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/slippi_stats.git
```

### 2. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/bug-description
```

### 3. Development Process
1. **Make your changes** following the code style guidelines below
2. **Test thoroughly** - ensure existing functionality still works
3. **Update documentation** if you've changed APIs or added features
4. **Add/update tests** for new functionality

### 4. Commit and Push
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add detailed player filtering API endpoint

- Implement POST /api/player/<code>/detailed route
- Support complex filtering by character, opponent, date
- Return comprehensive statistics for filtered data
- Add error handling and validation"

# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create Pull Request
1. **Go to GitHub** and create a pull request from your fork
2. **Fill out the PR template** with detailed description
3. **Link any related issues** using `Fixes #123` or `Related to #456`
4. **Request review** from maintainers

### 6. Address Review Feedback
```bash
# Make requested changes
git add .
git commit -m "Address review feedback: improve error handling"
git push origin feature/your-feature-name
```

## Code Style Guidelines

### Python (Backend)
- **Follow PEP 8** for Python code style
- **Use meaningful variable names** - `player_code` not `pc`
- **Add docstrings** to functions and classes
- **Handle errors gracefully** with try/catch blocks
- **Use type hints** where appropriate

**Example:**
```python
def get_player_games(player_code: str) -> list:
    """
    Get all games for a specific player.
    
    Args:
        player_code (str): The player tag to look up
        
    Returns:
        list: List of game dictionaries for the specified player
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error getting games for player {player_code}: {str(e)}")
        return []
```

### Frontend (HTML/CSS/JavaScript)
- **Maintain template inheritance** - extend appropriate layouts, not base
- **Use component-based CSS** - follow existing patterns in `static/css/components/`
- **Write modular JavaScript** - create reusable components in `static/js/components/`
- **Follow naming conventions** - use descriptive, consistent names

**CSS Example:**
```css
/* Component-specific styles */
.player-title-component {
    /* Use CSS custom properties from base.css */
    color: var(--primary-color);
}

/* Use BEM methodology for complex components */
.player-stats__card {
    /* Card styles */
}

.player-stats__card--highlighted {
    /* Modified card styles */
}
```

**JavaScript Example:**
```javascript
/**
 * Initialize player search functionality
 * @param {string} inputSelector - CSS selector for search input
 * @param {string} resultsSelector - CSS selector for results container
 */
function initializePlayerSearch(inputSelector, resultsSelector) {
    try {
        // Implementation here
    } catch (error) {
        console.error('Error initializing player search:', error);
    }
}
```

## Architecture Guidelines

### Frontend Architecture (Successful Pattern - Follow This!)
```
templates/
├── base.html          # Foundation
├── layouts/           # Layout layer
└── pages/            # Content layer

static/
├── css/
│   ├── base.css      # Global styles
│   ├── components/   # Reusable styles
│   └── pages/       # Page-specific styles
└── js/
    ├── base.js      # Global utilities
    ├── components/  # Reusable modules
    └── pages/      # Page-specific code
```

**Key Principles:**
- **Template Inheritance:** `base.html` → `layouts/*.html` → `pages/*.html`
- **Component Reusability:** Create reusable CSS/JS components
- **Single Responsibility:** Each file has one clear purpose
- **Progressive Enhancement:** Core functionality works without JavaScript

### Backend Architecture (Currently Refactoring)
**Current State:** Monolithic `app.py` with modular `config.py` and `database.py`

**Target State:**
```
├── app.py              # Entry point
├── config.py           # Configuration (✅ Done)
├── database.py         # Database operations (✅ Done)
└── [Future modules]
    ├── routes/         # Route handlers
    ├── services/       # Business logic
    └── utils/          # Shared utilities
```

**Guidelines for Backend Changes:**
- **Keep database operations in `database.py`** - don't add database code to `app.py`
- **Use existing configuration patterns** from `config.py`
- **Follow logging patterns** established in existing code
- **Maintain backward compatibility** when possible

## Types of Contributions

### 🐛 Bug Fixes
- **Small fixes** welcome without prior discussion
- **Large fixes** should have an issue first
- **Include reproduction steps** in your PR description

### ✨ New Features
- **Create an issue first** to discuss the feature
- **Follow existing patterns** for similar functionality
- **Update documentation** for user-facing features

### 📚 Documentation
- **Improve existing docs** - fix typos, add examples, clarify instructions
- **Add missing docs** - document undocumented features
- **Update architecture docs** when making structural changes

### 🏗️ Refactoring
- **Follow the planned architecture** outlined in README.md
- **Maintain backward compatibility** 
- **Extract modular components** following frontend success patterns
- **Move functionality** from `app.py` to appropriate modules

## Testing Guidelines

### Manual Testing
1. **Test your changes** on multiple browsers
2. **Verify existing functionality** still works
3. **Test edge cases** - empty data, invalid inputs, etc.
4. **Check responsive design** on different screen sizes

### Database Testing
- **Use test database** for development (default behavior)
- **Test with realistic data** - import sample game data
- **Verify database operations** don't break existing data

### Frontend Testing
- **Test with JavaScript disabled** - core functionality should work
- **Verify character icons load** correctly
- **Test search functionality** with various inputs
- **Check filtering and pagination** works properly

## Common Development Tasks

### Adding a New Page
1. **Create page template** in `templates/pages/`
2. **Choose appropriate layout** from `templates/layouts/`
3. **Add route handler** in `app.py` (or new route module)
4. **Create page-specific assets** in `static/css/pages/` and `static/js/pages/`
5. **Test thoroughly** and update documentation

### Adding a New API Endpoint
1. **Add database function** in `database.py` if needed
2. **Create route handler** in `app.py` (or appropriate route module)
3. **Add error handling** and validation
4. **Document the endpoint** in README.md
5. **Test with various inputs** including edge cases

### Adding a New Component
1. **Create CSS component** in `static/css/components/`
2. **Create JavaScript component** in `static/js/components/`
3. **Follow existing patterns** for initialization and usage
4. **Document component usage** in relevant README files
5. **Test component** across different pages

## Pull Request Guidelines

### PR Title Format
```
[Type] Brief description

Types: Feature, Fix, Refactor, Docs, Style, Test
Examples:
- Feature: Add advanced player filtering
- Fix: Resolve character icon loading issue
- Refactor: Extract route handlers to separate modules
- Docs: Update API documentation with new endpoints
```

### PR Description Template
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Specific change 1
- Specific change 2
- Specific change 3

## Testing
- [ ] Tested manually on Windows/Mac/Linux
- [ ] Tested with multiple browsers
- [ ] Tested edge cases and error conditions
- [ ] Verified existing functionality still works

## Related Issues
Fixes #123
Related to #456

## Screenshots (if applicable)
[Add screenshots for UI changes]
```

### Review Process
1. **Automated checks** must pass (when implemented)
2. **Manual review** by maintainers
3. **Address feedback** promptly and professionally
4. **Maintain clean commit history** - squash if requested

## Getting Help

### Resources
- **README.md** - Architecture overview and setup instructions
- **templates/README.md** - Template system documentation
- **static/README.md** - Frontend asset organization
- **Existing code** - Follow established patterns

### Questions and Support
- **Create an issue** for questions about contributing
- **Check existing issues** before creating new ones
- **Be specific** about your development environment and steps taken

### Common Issues
- **Virtual environment problems** - Try the Windows batch script or recreate venv
- **Database issues** - Delete existing `.db` files and reinitialize
- **Import errors** - Ensure virtual environment is activated and dependencies installed
- **Port conflicts** - Check if port 5000 is available or change in config

## Code of Conduct

- **Be respectful** and professional in all interactions
- **Welcome newcomers** and help them get started
- **Focus on the code** not the person when giving feedback
- **Be patient** with review process and questions
- **Assume good intentions** from all contributors

Thank you for contributing to Slippi Stats Server! 🎮