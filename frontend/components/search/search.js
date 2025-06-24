// Unified Search Component - Replaces both base.js and search.js functionality
// File: static/js/components/search.js

/**
 * Unified search functionality that works with all search form macros
 * Handles both player navigation and local filtering
 */
class UnifiedSearch {
    constructor() {
        this.initialized = false;
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        // Initialize all search forms when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeForms());
        } else {
            this.initializeForms();
        }
        
        this.initialized = true;
    }
    
    initializeForms() {
        // 1. Initialize navbar search (playerSearchForm)
        this.initializeNavbarSearch();
        
        // 2. Initialize main page search (mainPageSearch)
        this.initializeMainSearch();
        
        // 3. Initialize filter search (for players page)
        this.initializeFilterSearch();
        
        // 4. Initialize any compact search forms
        this.initializeCompactSearch();
        
        // 5. Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    /**
     * Initialize navbar search form (in layouts)
     */
    initializeNavbarSearch() {
        const form = document.getElementById('playerSearchForm');
        const input = document.getElementById('playerCodeInput');
        
        if (form && input) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.navigateToPlayer(input.value.trim());
            });
            
            console.log('Navbar search initialized');
        }
    }
    
    /**
     * Initialize main page search (homepage)
     */
    initializeMainSearch() {
        const form = document.getElementById('mainPageSearch');
        const input = document.getElementById('mainSearchInput');
        
        if (form && input) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.navigateToPlayer(input.value.trim());
            });
            
            // Add enhanced styling and effects for main search
            input.addEventListener('focus', () => {
                form.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                form.classList.remove('focused');
            });
            
            console.log('Main page search initialized');
        }
    }
    
    /**
     * Initialize filter search (players page)
     */
    initializeFilterSearch() {
        const input = document.getElementById('playerSearch');
        const targetId = input?.getAttribute('data-target');
        
        if (input && targetId) {
            // Make filter function globally available for clear button
            window.filterPlayers = () => this.filterPlayers();
            
            // Add debounced search
            let searchTimeout;
            input.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => this.filterPlayers(), 150);
            });
            
            // Escape key to clear
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    input.value = '';
                    this.filterPlayers();
                    input.blur();
                }
                
                // Enter key - navigate to first result
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.navigateToFirstResult();
                }
            });
            
            // Initialize counts
            this.updatePlayerCounts();
            
            console.log('Filter search initialized');
        }
    }
    
    /**
     * Initialize compact search forms
     */
    initializeCompactSearch() {
        const compactForms = document.querySelectorAll('.compact-search');
        
        compactForms.forEach(form => {
            const input = form.querySelector('input[type="search"]');
            
            if (input) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.navigateToPlayer(input.value.trim());
                });
            }
        });
        
        if (compactForms.length > 0) {
            console.log(`${compactForms.length} compact search forms initialized`);
        }
    }
    
    /**
     * Setup global keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K - Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });
    }
    
    /**
     * Navigate to player profile
     */
    navigateToPlayer(playerCode) {
        if (!playerCode) {
            console.warn('Empty player code provided');
            return;
        }
        
        const encodedTag = encodeURIComponent(playerCode);
        const url = `/player/${encodedTag}`;
        
        console.log(`Navigating to player: ${playerCode} -> ${url}`);
        window.location.href = url;
    }
    
    /**
     * Filter players on players page
     */
    filterPlayers() {
        const searchInput = document.getElementById('playerSearch');
        const playersTable = document.getElementById('playersTable');
        const noResultsAlert = document.getElementById('noResults');
        
        if (!searchInput || !playersTable) return;
        
        const searchTerm = searchInput.value.toLowerCase().trim();
        const playerRows = playersTable.querySelectorAll('tbody .player-row');
        let visibleCount = 0;
        
        playerRows.forEach(row => {
            const playerTag = row.querySelector('.player-tag');
            const playerName = row.querySelector('.player-name');
            const playerCharacters = row.querySelector('.player-characters');
            
            if (!playerTag || !playerName) return;
            
            const tagText = playerTag.textContent.toLowerCase();
            const nameText = playerName.textContent.toLowerCase();
            const charactersText = playerCharacters ? playerCharacters.textContent.toLowerCase() : '';
            
            const matches = tagText.includes(searchTerm) || 
                          nameText.includes(searchTerm) || 
                          charactersText.includes(searchTerm);
            
            if (matches) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update visible count
        this.updateVisibleCount(visibleCount);
        
        // Show/hide no results message
        if (noResultsAlert) {
            noResultsAlert.style.display = (visibleCount === 0 && searchTerm.length > 0) ? 'block' : 'none';
        }
        
        // Visual feedback for search input
        if (visibleCount === 0 && searchTerm.length > 0) {
            searchInput.classList.add('is-invalid');
        } else {
            searchInput.classList.remove('is-invalid');
        }
    }
    
    /**
     * Navigate to first visible result
     */
    navigateToFirstResult() {
        const playersTable = document.getElementById('playersTable');
        if (!playersTable) return;
        
        const firstVisibleRow = Array.from(playersTable.querySelectorAll('tbody .player-row'))
            .find(row => row.style.display !== 'none');
        
        if (firstVisibleRow) {
            const profileLink = firstVisibleRow.querySelector('a[href*="/player/"]');
            if (profileLink) {
                profileLink.click();
            }
        }
    }
    
    /**
     * Focus the most appropriate search input
     */
    focusSearch() {
        // Priority order: main search, navbar search, filter search
        const searchInputs = [
            document.getElementById('mainSearchInput'),
            document.getElementById('playerCodeInput'), 
            document.getElementById('playerSearch')
        ];
        
        for (const input of searchInputs) {
            if (input && input.offsetParent !== null) { // visible check
                input.focus();
                input.select();
                break;
            }
        }
    }
    
    /**
     * Update player counts (for filter search)
     */
    updatePlayerCounts() {
        const playersTable = document.getElementById('playersTable');
        const playerCountElement = document.getElementById('playerCount');
        
        if (playersTable && playerCountElement) {
            const totalPlayers = playersTable.querySelectorAll('tbody .player-row').length;
            playerCountElement.textContent = totalPlayers;
            this.updateVisibleCount(totalPlayers);
        }
    }
    
    /**
     * Update visible count display
     */
    updateVisibleCount(count) {
        const visibleCountElement = document.getElementById('visibleCount');
        if (visibleCountElement) {
            visibleCountElement.textContent = count;
        }
    }
}

// Auto-initialize the unified search system
const unifiedSearch = new UnifiedSearch();

// Export for manual initialization if needed
window.UnifiedSearch = UnifiedSearch;