// Homepage JavaScript - Simplified without search functionality

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
 * Format game times for better readability
 */
function formatGameTimes() {
    const gameTimeElements = document.querySelectorAll('.time-cell');
    
    gameTimeElements.forEach(element => {
        const timeData = element.getAttribute('data-time');
        if (!timeData) return;
        
        try {
            const date = new Date(timeData);
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
            
            const timeElement = element.querySelector('small');
            if (timeElement) {
                timeElement.textContent = relativeTime;
                timeElement.title = timeData; // Keep original time in tooltip
            }
        } catch (error) {
            // If date parsing fails, keep original text
            console.warn('Could not parse date:', timeData);
        }
    });
}

/**
 * Initialize action card interactions
 */
function initializeActionCards() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        // Add click handling for cards with buttons
        const button = card.querySelector('.btn');
        if (button) {
            card.addEventListener('click', function(e) {
                // Only trigger if not clicking the button directly
                if (e.target !== button && !button.contains(e.target)) {
                    button.click();
                }
            });
            
            // Add loading state to button clicks
            button.addEventListener('click', function() {
                const originalText = this.innerHTML;
                this.classList.add('loading');
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                this.disabled = true;
                
                // Reset after navigation timeout
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 3000);
            });
        }
        
        // Add hover analytics
        card.addEventListener('mouseenter', function() {
            const cardType = this.querySelector('h5')?.textContent;
            console.log('Action card hovered:', cardType);
        });
    });
}

/**
 * Add click analytics for player cards
 */
function initializePlayerCardAnalytics() {
    const playerCards = document.querySelectorAll('.player-card');
    
    playerCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Only trigger if not clicking a link directly
            if (e.target.tagName !== 'A' && !e.target.closest('a')) {
                const playerLink = this.querySelector('.player-link');
                if (playerLink) {
                    // Add loading state
                    this.classList.add('loading');
                    
                    // Analytics
                    const playerName = playerLink.textContent;
                    console.log('Player card clicked:', playerName);
                    
                    // Navigate after brief delay
                    setTimeout(() => {
                        playerLink.click();
                    }, 150);
                }
            }
        });
        
        // Add loading state to direct link clicks
        const playerLink = card.querySelector('.player-link');
        if (playerLink) {
            playerLink.addEventListener('click', function() {
                card.classList.add('loading');
                
                // Remove loading state after timeout
                setTimeout(() => {
                    card.classList.remove('loading');
                }, 3000);
            });
        }
    });
}

/**
 * Initialize dynamic stats updates
 */
function initializeDynamicStats() {
    // Update stats periodically
    updateLastUpdated();
    
    // Refresh stats every 5 minutes
    setInterval(updateLastUpdated, 5 * 60 * 1000);
    
    // Add count-up animation to stat numbers
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent) || 0;
        if (finalValue > 0) {
            animateCountUp(element, finalValue);
        }
    });
}

/**
 * Animate count-up effect for numbers
 */
function animateCountUp(element, finalValue) {
    const duration = 2000; // 2 seconds
    const steps = 60;
    const increment = finalValue / steps;
    let currentValue = 0;
    
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= finalValue) {
            currentValue = finalValue;
            clearInterval(timer);
        }
        element.textContent = Math.floor(currentValue).toLocaleString();
    }, duration / steps);
}

/**
 * Enhanced keyboard navigation
 */
function initializeKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // Focus navbar search with Ctrl/Cmd + K (handled by search component)
        // Add other homepage-specific shortcuts here if needed
        
        // Quick navigation shortcuts
        if (e.altKey) {
            switch(e.key) {
                case 'p':
                    e.preventDefault();
                    window.location.href = '/players';
                    break;
                case 'd':
                    e.preventDefault();
                    window.location.href = '/download';
                    break;
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
        const playerName = card.querySelector('.player-link');
        if (!playerName || playerName.textContent.trim() === '') {
            card.style.display = 'none';
        }
    });
    
    // Handle cases where the recent games table might be empty
    const gamesTable = document.querySelector('.table tbody');
    if (gamesTable && gamesTable.children.length === 0) {
        const noDataMsg = document.createElement('tr');
        noDataMsg.innerHTML = '<td colspan="4" class="text-center text-muted py-4">No recent games available</td>';
        gamesTable.appendChild(noDataMsg);
    }
    
    // Handle hero stats display
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        if (stat.textContent === '0' || stat.textContent === '') {
            stat.textContent = '0';
            stat.style.opacity = '0.6';
        }
    });
}

/**
 * Initialize intersection observer for animations
 */
function initializeScrollAnimations() {
    // Animate elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe sections for scroll animations
    const sections = document.querySelectorAll('.section, .action-card, .player-card');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'all 0.6s ease';
        observer.observe(section);
    });
}

// PAGE INITIALIZATION - Always uses DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize page functionality
        initializeActionCards();
        initializePlayerCardAnalytics();
        initializeDynamicStats();
        initializeKeyboardNavigation();
        initializeErrorHandling();
        
        // Initialize enhancements
        formatGameTimes();
        initializeScrollAnimations();
        
        console.log('Homepage initialized successfully');
    } catch (error) {
        console.error('Error initializing homepage:', error);
    }
});