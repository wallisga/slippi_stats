// Player Dropdown Component

/**
 * Initialize player dropdown navigation links
 */
function initializePlayerDropdown() {
    // Get current page path for active state detection
    const currentPath = window.location.pathname;
    
    // Process player links
    const playerLinks = document.querySelectorAll('.player-link');
    playerLinks.forEach(link => {
        const path = link.getAttribute('data-path');
        const playerCode = link.getAttribute('data-code');
        const suffix = link.getAttribute('data-suffix') || '';
        const view = link.getAttribute('data-view');
        
        if (!path || !playerCode) return;
        
        // Build the properly encoded URL
        const encodedPlayerCode = encodeURIComponent(playerCode);
        const fullUrl = `${path}${encodedPlayerCode}${suffix}`;
        
        // Set the href attribute with properly encoded URL
        link.setAttribute('href', fullUrl);
        
        // Active state detection - handle both views correctly
        if (view === 'basic' && currentPath === `${path}${encodedPlayerCode}`) {
            link.classList.add('active');
        } else if (view === 'detailed' && currentPath === `${path}${encodedPlayerCode}${suffix}`) {
            link.classList.add('active');
        }
    });
    
    // Process character links
    const characterLinks = document.querySelectorAll('.character-link');
    characterLinks.forEach(link => {
        const path = link.getAttribute('data-path');
        const playerCode = link.getAttribute('data-code');
        const character = link.getAttribute('data-character');
        
        if (!path || !playerCode || !character) return;
        
        // Build the properly encoded URL
        const encodedPlayerCode = encodeURIComponent(playerCode);
        const encodedCharacter = encodeURIComponent(character);
        const fullUrl = `${path}${encodedPlayerCode}/character/${encodedCharacter}`;
        
        // Set the href attribute with properly encoded URL
        link.setAttribute('href', fullUrl);
        
        // Set active class if this is the current page
        if (currentPath === fullUrl) {
            link.classList.add('active');
        }
    });
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePlayerDropdown();
});