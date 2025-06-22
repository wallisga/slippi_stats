// Base JavaScript functionality for all pages

/**
 * Player search form handler - works for any search form on the page
 */
function initializePlayerSearch() {
    // Handle multiple search forms (navbar and page-specific)
    const searchForms = document.querySelectorAll('form[id*="Search"], form[id*="search"]');
    
    searchForms.forEach(form => {
        const input = form.querySelector('input[type="search"], input[id*="Input"], input[id*="input"]');
        
        if (form && input) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const playerCode = input.value.trim();
                if (!playerCode) {
                    return;
                }
                
                // Encode the player tag for URL
                const encodedTag = encodeURIComponent(playerCode);
                window.location.href = `/player/${encodedTag}`;
            });
        }
    });
}

/**
 * Common initialization that runs on all pages
 */
document.addEventListener('DOMContentLoaded', function() {
    initializePlayerSearch();
    
    // Character icons are handled by their own component
    // Search functionality is handled above
    
    console.log('Base functionality initialized');
});