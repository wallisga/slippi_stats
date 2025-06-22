// Search Component

/**
 * Initialize player search functionality
 */
function initializePlayerSearch() {
    const playerSearchForm = document.getElementById('playerSearchForm');
    const playerCodeInput = document.getElementById('playerCodeInput');
    
    if (!playerSearchForm || !playerCodeInput) {
        return;
    }
    
    playerSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const playerCode = playerCodeInput.value.trim();
        if (!playerCode) {
            return;
        }
        
        // Encode the player tag for URL
        const encodedTag = encodeURIComponent(playerCode);
        window.location.href = `/player/${encodedTag}`;
    });
    
    // Optional: Add autocomplete or suggestions here in the future
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePlayerSearch();
});