// Cards Component JavaScript - AUTO-INITIALIZATION
function initializeCardInteractions() {
    const cards = document.querySelectorAll('.stat-card, .player-card');
    
    cards.forEach(card => {
        // Prevent double initialization
        if (card.dataset.cardInitialized) return;
        card.dataset.cardInitialized = 'true';
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    console.log('Cards component initialized');
}

// ✅ AUTO-INITIALIZE (no DOMContentLoaded)
initializeCardInteractions();

// ✅ EXPORT for manual use
window.initializeCardInteractions = initializeCardInteractions;