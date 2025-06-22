// Homepage JavaScript

/**
 * Update last updated time from API
 */
function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('lastUpdated');
    if (!lastUpdatedElement) return;
    
    // Add loading class for animation
    lastUpdatedElement.classList.add('loading');
    
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            lastUpdatedElement.classList.remove('loading');
            
            if (data.last_upload) {
                const date = new Date(data.last_upload);
                const formattedDate = date.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                lastUpdatedElement.textContent = formattedDate;
            } else {
                lastUpdatedElement.textContent = 'No data yet';
                lastUpdatedElement.style.color = '#6c757d';
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            lastUpdatedElement.classList.remove('loading');
            lastUpdatedElement.textContent = 'Error loading';
            lastUpdatedElement.style.color = '#dc3545';
        });
}

/**
 * Initialize main page search functionality
 * This is separate from the navbar search to allow for different behavior
 */
function initializeMainPageSearch() {
    const searchForm = document.getElementById('mainPageSearch');
    const searchInput = document.getElementById('mainPlayerInput');
    
    if (!searchForm || !searchInput) return;
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const playerCode = searchInput.value.trim();
        if (!playerCode) {
            // Add a subtle shake animation for empty input
            searchInput.classList.add('is-invalid');
            setTimeout(() => {
                searchInput.classList.remove('is-invalid');
            }, 2000);
            return;
        }
        
        // Show loading state
        const submitButton = searchForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Searching...';
        submitButton.disabled = true;
        
        // Encode the player tag for URL
        const encodedTag = encodeURIComponent(playerCode);
        
        // Add a small delay to show the loading state
        setTimeout(() => {
            window.location.href = `/player/${encodedTag}`;
        }, 300);
    });
    
    // Clear invalid state when user starts typing
    searchInput.addEventListener('input', function() {
        this.classList.remove('is-invalid');
    });
    
    // Add Enter key handling for better UX
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchForm.dispatchEvent(new Event('submit'));
        }
    });
}

/**
 * Format game times for better readability
 */
function formatGameTimes() {
    const gameTimeElements = document.querySelectorAll('.game-time');
    
    gameTimeElements.forEach(element => {
        const originalTime = element.textContent;
        try {
            const date = new Date(originalTime);
            const now = new Date();
            const diffMs = now - date;
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            
            let relativeTime;
            if (diffMinutes < 60) {
                relativeTime = `${diffMinutes}m ago`;
            } else if (diffHours < 24) {
                relativeTime = `${diffHours}h ago`;
            } else if (diffDays < 7) {
                relativeTime = `${diffDays}d ago`;
            } else {
                // For older dates, show the actual date
                relativeTime = date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                });
            }
            
            element.textContent = relativeTime;
            element.title = originalTime; // Keep original time in tooltip
        } catch (error) {
            // If date parsing fails, keep original text
            console.warn('Could not parse date:', originalTime);
        }
    });
}

/**
 * Add click analytics for player cards
 */
function initializePlayerCardAnalytics() {
    const playerCards = document.querySelectorAll('.player-card');
    
    playerCards.forEach(card => {
        card.addEventListener('click', function() {
            const playerName = this.querySelector('.player-name')?.textContent;
            
            // Log click for analytics (you can replace this with your analytics service)
            console.log('Player card clicked:', playerName);
            
            // Optional: Add Google Analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', 'player_card_click', {
                    'player_name': playerName,
                    'page_location': window.location.href
                });
            }
        });
    });
}

/**
 * Initialize dynamic stats updates
 */
function initializeDynamicStats() {
    // You could periodically refresh stats here
    // For now, we'll just update the last updated time
    updateLastUpdated();
    
    // Optionally refresh stats every 5 minutes
    setInterval(updateLastUpdated, 5 * 60 * 1000);
}

/**
 * Add keyboard shortcuts for power users
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('mainPlayerInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('mainPlayerInput');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

/**
 * Initialize error handling for missing data
 */
function initializeErrorHandling() {
    // Handle cases where player cards might fail to load
    const playerCards = document.querySelectorAll('.player-card');
    
    playerCards.forEach(card => {
        const playerName = card.querySelector('.player-name');
        if (!playerName || playerName.textContent.trim() === '') {
            card.style.display = 'none';
        }
    });
    
    // Handle cases where the recent games table might be empty
    const gamesTable = document.querySelector('#recent-games-section + .card table tbody');
    if (gamesTable && gamesTable.children.length === 0) {
        const noDataMsg = document.createElement('tr');
        noDataMsg.innerHTML = '<td colspan="6" class="text-center text-muted">No recent games available</td>';
        gamesTable.appendChild(noDataMsg);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeMainPageSearch();
        formatGameTimes();
        initializePlayerCardAnalytics();
        initializeDynamicStats();
        initializeKeyboardShortcuts();
        initializeErrorHandling();
        
        console.log('Homepage initialized successfully');
    } catch (error) {
        console.error('Error initializing homepage:', error);
    }
});