// Base JavaScript functionality for all pages
// Navbar functionality has been moved to navbar component

/**
 * Global error handling
 */
function handleGlobalError(error, context = 'unknown') {
    console.error(`Global error in ${context}:`, error);
    
    // Could add error reporting here in the future
    // trackError(error, context);
}

/**
 * Common utilities available on all pages
 */
window.SlippiUtils = {
    /**
     * Encode player tag for URL use
     */
    encodePlayerTag: function(tag) {
        return encodeURIComponent(tag);
    },
    
    /**
     * Decode player tag from URL
     */
    decodePlayerTag: function(encodedTag) {
        return decodeURIComponent(encodedTag);
    },
    
    /**
     * Format time difference (e.g., "2 hours ago")
     */
    formatTimeAgo: function(dateString) {
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            
            if (diffMinutes < 60) {
                return diffMinutes <= 1 ? 'Just now' : `${diffMinutes} minutes ago`;
            } else if (diffHours < 24) {
                return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
            } else if (diffDays === 1) {
                return 'Yesterday';
            } else {
                return `${diffDays} days ago`;
            }
        } catch (error) {
            console.error('Error formatting time:', error);
            return 'Unknown';
        }
    },
    
    /**
     * Show loading state on an element
     */
    showLoading: function(element, text = 'Loading...') {
        if (element) {
            element.innerHTML = `<i class="spinner-border spinner-border-sm me-2"></i>${text}`;
            element.disabled = true;
        }
    },
    
    /**
     * Hide loading state on an element
     */
    hideLoading: function(element, originalText) {
        if (element) {
            element.innerHTML = originalText;
            element.disabled = false;
        }
    },
    
    /**
     * Safe navigation with loading states
     */
    navigateWithLoading: function(url, element = null) {
        if (element) {
            const originalText = element.innerHTML;
            this.showLoading(element, 'Loading...');
            
            // Reset after timeout in case navigation fails
            setTimeout(() => {
                this.hideLoading(element, originalText);
            }, 3000);
        }
        
        window.location.href = url;
    }
};

/**
 * Common initialization that runs on all pages
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons and links (excluding navbar which handles its own)
    const buttons = document.querySelectorAll('.btn:not(.navbar .btn)');
    const externalLinks = document.querySelectorAll('a[href]:not(.navbar a):not([href^="#"]):not([href^="javascript:"])');
    
    // Add loading states to buttons
    buttons.forEach(button => {
        if (button.getAttribute('type') === 'button' && button.onclick) {
            const originalClick = button.onclick;
            button.onclick = function(e) {
                const originalText = this.innerHTML;
                window.SlippiUtils.showLoading(this);
                
                // Execute original click handler
                const result = originalClick.call(this, e);
                
                // Reset after delay if still enabled
                setTimeout(() => {
                    if (!this.disabled) {
                        window.SlippiUtils.hideLoading(this, originalText);
                    }
                }, 1000);
                
                return result;
            };
        }
    });
    
    // Add loading states to external navigation links
    externalLinks.forEach(link => {
        if (link.href && !link.href.includes('#') && !link.classList.contains('no-loading')) {
            link.addEventListener('click', function(e) {
                const originalText = this.innerHTML;
                
                // Only show loading for links that will navigate away
                if (!e.ctrlKey && !e.metaKey && !e.shiftKey && this.target !== '_blank') {
                    setTimeout(() => {
                        window.SlippiUtils.showLoading(this, 'Loading...');
                        
                        // Reset after timeout in case navigation fails
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 3000);
                    }, 100);
                }
            });
        }
    });
    
    // Setup global error handling
    window.addEventListener('error', function(event) {
        handleGlobalError(event.error, 'window');
    });
    
    // Setup unhandled promise rejection handling
    window.addEventListener('unhandledrejection', function(event) {
        handleGlobalError(event.reason, 'promise');
    });
    
    console.log('Base functionality initialized');
});