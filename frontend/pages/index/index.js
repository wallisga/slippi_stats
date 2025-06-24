// Homepage JavaScript - CLEANED VERSION

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Only keep page-specific functionality that components don't handle
        initializeDynamicStats();
        initializeKeyboardNavigation();
        
        console.log('Homepage initialized successfully');
    } catch (error) {
        console.error('Error initializing homepage:', error);
    }
});

/**
 * Initialize dynamic stats updates
 */
function initializeDynamicStats() {
    // Update stats periodically if there's an API endpoint
    updateLastUpdated();
    
    // Refresh stats every 5 minutes
    setInterval(updateLastUpdated, 5 * 60 * 1000);
    
    // Add count-up animation to stat numbers (if they exist and aren't handled by components)
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent) || 0;
        if (finalValue > 0) {
            animateCountUp(element, finalValue);
        }
    });
}

/**
 * Update last updated time from API (if this feature exists)
 */
function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('lastUpdated');
    if (!lastUpdatedElement) return;
    
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
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
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
            lastUpdatedElement.textContent = 'Error loading';
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
