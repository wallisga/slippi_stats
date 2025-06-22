// Players Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('playerSearch');
    const playersTable = document.getElementById('playersTable');
    const noResultsAlert = document.getElementById('noResults');
    const visibleCountElement = document.getElementById('visibleCount');
    const playerCountElement = document.getElementById('playerCount');
    
    if (!searchInput || !playersTable) {
        console.error('Required elements not found');
        return;
    }
    
    const playerRows = playersTable.querySelectorAll('tbody .player-row');
    const totalPlayers = playerRows.length;
    
    // Update initial counts
    if (playerCountElement) playerCountElement.textContent = totalPlayers;
    if (visibleCountElement) visibleCountElement.textContent = totalPlayers;
    
    // Filter functionality
    function filterPlayers() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        let visibleCount = 0;
        
        playerRows.forEach(row => {
            const playerTag = row.querySelector('.player-tag');
            const playerName = row.querySelector('.player-name');
            const playerCharacters = row.querySelector('.player-characters');
            
            if (!playerTag || !playerName) {
                return;
            }
            
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
        if (visibleCountElement) {
            visibleCountElement.textContent = visibleCount;
        }
        
        // Show/hide no results message
        if (noResultsAlert) {
            if (visibleCount === 0 && searchTerm.length > 0) {
                noResultsAlert.style.display = 'block';
            } else {
                noResultsAlert.style.display = 'none';
            }
        }
        
        // Add visual feedback for empty search
        if (visibleCount === 0 && searchTerm.length > 0) {
            searchInput.classList.add('is-invalid');
        } else {
            searchInput.classList.remove('is-invalid');
        }
    }
    
    // Add search event listener with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(filterPlayers, 150);
    });
    
    // Clear search functionality
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            filterPlayers();
            this.blur();
        }
    });
    
    // Enhanced keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            
            // Find first visible player link and click it
            const firstVisibleRow = Array.from(playerRows).find(row => 
                row.style.display !== 'none'
            );
            
            if (firstVisibleRow) {
                const profileLink = firstVisibleRow.querySelector('a[href*="/player/"]');
                if (profileLink) {
                    profileLink.click();
                }
            }
        }
    });
    
    // Add loading state for profile links
    const profileLinks = playersTable.querySelectorAll('a[href*="/player/"]');
    profileLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Add loading state to the clicked row
            const row = this.closest('tr');
            if (row) {
                row.classList.add('loading');
                
                // Remove loading state after a delay (in case navigation fails)
                setTimeout(() => {
                    row.classList.remove('loading');
                }, 3000);
            }
        });
    });
    
    // Add hover effects for better UX
    playerRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.cursor = 'auto';
        });
        
        // Make entire row clickable
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on the actual link
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            const profileLink = this.querySelector('a[href*="/player/"]');
            if (profileLink) {
                profileLink.click();
            }
        });
    });
    
    // Focus search on page load for better UX
    setTimeout(() => {
        searchInput.focus();
    }, 100);
    
    // Add search shortcut (Ctrl/Cmd + K)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }
    });
    
    console.log(`Players page loaded: ${totalPlayers} players found`);
});