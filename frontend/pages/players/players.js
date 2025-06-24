// Players Page JavaScript - Follows architecture conventions

/**
 * Setup enhanced row interactions for better UX
 */
function setupRowInteractions() {
    const playerRows = document.querySelectorAll('.player-row');
    
    playerRows.forEach(row => {
        // Enhanced hover effects
        row.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.cursor = 'auto';
            this.style.boxShadow = '';
        });
        
        // Make entire row clickable (except when clicking actual links/buttons)
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on interactive elements
            if (e.target.tagName === 'A' || e.target.closest('a') || 
                e.target.tagName === 'BUTTON' || e.target.closest('button') ||
                e.target.tagName === 'I' || e.target.closest('i')) {
                return;
            }
            
            const profileLink = this.querySelector('a[href*="/player/"]');
            if (profileLink) {
                // Add click animation
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                    profileLink.click();
                }, 100);
            }
        });
    });
}

/**
 * Setup loading states for profile links
 */
function setupProfileLinkStates() {
    const profileLinks = document.querySelectorAll('a[href*="/player/"]');
    
    profileLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const originalHTML = this.innerHTML;
            const row = this.closest('tr');
            
            // Add loading state to row
            if (row) {
                row.classList.add('loading');
            }
            
            // Update button text and disable
            if (this.classList.contains('btn')) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Loading...';
                this.disabled = true;
            }
            
            // Remove loading state after navigation timeout
            setTimeout(() => {
                if (row) {
                    row.classList.remove('loading');
                }
                this.innerHTML = originalHTML;
                this.disabled = false;
            }, 3000);
        });
    });
}

/**
 * Initialize table enhancements
 */
function initializeTableEnhancements() {
    const table = document.getElementById('playersTable');
    if (!table) return;
    
    // Add zebra striping enhancement
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach((row, index) => {
        if (index % 2 === 0) {
            row.classList.add('table-row-even');
        }
    });
    
    // Initialize character icons (they should auto-initialize via component)
    // But we can refresh them to ensure they're loaded
    if (window.CharacterIcons && window.CharacterIcons.refresh) {
        window.CharacterIcons.refresh(table);
    }
}

/**
 * Setup accessibility enhancements
 */
function setupAccessibilityEnhancements() {
    const playerRows = document.querySelectorAll('.player-row');
    
    playerRows.forEach((row, index) => {
        // Add ARIA labels for screen readers
        const playerName = row.querySelector('.player-name')?.textContent;
        const winRate = row.querySelector('.win-rate')?.textContent;
        const games = row.querySelector('.game-count')?.textContent;
        
        if (playerName) {
            row.setAttribute('aria-label', 
                `Player ${playerName}, ${games} games, ${winRate} win rate. Click to view profile.`);
            row.setAttribute('role', 'button');
            row.setAttribute('tabindex', '0');
        }
        
        // Keyboard navigation
        row.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const profileLink = this.querySelector('a[href*="/player/"]');
                if (profileLink) {
                    profileLink.click();
                }
            }
        });
    });
}

/**
 * Initialize search integration with component
 * The search component handles the filtering, but we can enhance it
 */
function enhanceSearchIntegration() {
    const searchInput = document.getElementById('playerSearch');
    if (!searchInput) {
        console.warn('Player search input not found - search component may not be loaded');
        return;
    }
    
    // Add enhanced placeholder behavior
    searchInput.addEventListener('focus', function() {
        this.placeholder = 'Type player tag, name, or character...';
    });
    
    searchInput.addEventListener('blur', function() {
        if (!this.value) {
            this.placeholder = 'Search by player tag, name, or character...';
        }
    });
    
    // Add search hints
    const searchContainer = searchInput.closest('.search-container');
    if (searchContainer) {
        const hint = document.createElement('small');
        hint.className = 'text-muted mt-1';
        hint.innerHTML = '💡 <strong>Tip:</strong> Search by player tag (e.g., PLAYER#123), display name, or character name';
        searchContainer.appendChild(hint);
    }
    
    console.log('Search integration enhanced for players page');
}

/**
 * Initialize performance monitoring
 */
function initializePerformanceMonitoring() {
    const playerRows = document.querySelectorAll('.player-row');
    
    console.log(`Players page performance: ${playerRows.length} players loaded`);
    
    // Monitor search performance (if search component is available)
    if (window.UnifiedSearch) {
        const originalFilterPlayers = window.filterPlayers;
        if (originalFilterPlayers) {
            window.filterPlayers = function() {
                const startTime = performance.now();
                originalFilterPlayers();
                const endTime = performance.now();
                
                if (endTime - startTime > 100) {
                    console.warn(`Slow search filter: ${endTime - startTime}ms`);
                }
            };
        }
    }
}

/**
 * Setup error handling for page-specific issues
 */
function setupErrorHandling() {
    // Handle cases where player data might be missing
    const playerRows = document.querySelectorAll('.player-row');
    
    playerRows.forEach(row => {
        const playerName = row.querySelector('.player-name');
        const playerTag = row.querySelector('.player-tag');
        
        if (!playerName || !playerTag || 
            playerName.textContent.trim() === '' || 
            playerTag.textContent.trim() === '') {
            console.warn('Player row with missing data found, hiding:', row);
            row.style.display = 'none';
        }
    });
    
    // Handle empty table state
    const tbody = document.querySelector('#playersTable tbody');
    if (tbody && tbody.children.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = `
            <td colspan="5" class="text-center py-5">
                <i class="bi bi-people display-4 text-muted mb-3"></i>
                <p class="text-muted">No players found</p>
            </td>
        `;
        tbody.appendChild(emptyRow);
    }
}

/**
 * Future enhancement: Table sorting
 */
window.PlayersPage = {
    sortBy: function(column, direction = 'asc') {
        console.log(`Future feature: Sort by ${column} (${direction})`);
        // Implementation would go here
    },
    
    refresh: function() {
        console.log('Future feature: Refresh players table via AJAX');
        // Implementation would go here
    },
    
    exportData: function() {
        console.log('Future feature: Export player data');
        // Implementation would go here
    }
};

// PAGE INITIALIZATION - Always uses DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize page-specific functionality
        setupRowInteractions();
        setupProfileLinkStates();
        initializeTableEnhancements();
        setupAccessibilityEnhancements();
        
        // Enhance search integration (search component should already be loaded)
        setTimeout(enhanceSearchIntegration, 100);
        
        // Initialize monitoring and error handling
        initializePerformanceMonitoring();
        setupErrorHandling();
        
        console.log('Players page initialized successfully');
    } catch (error) {
        console.error('Error initializing players page:', error);
    }
});