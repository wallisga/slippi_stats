// Player Basic Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Player basic page initializing...');
    
    // ✅ BUSINESS LOGIC: Initialize player title
    initializePlayerTitle();
    
    // ✅ BUSINESS LOGIC: Setup API interactions
    initializeLoadMore();
    
    console.log('Player basic page loaded');
});

function initializePlayerTitle() {
    // ✅ KEEP: Business logic for title setup
    const container = document.getElementById('player-title-container');
    if (!container) {
        console.error('Player title container not found!');
        return;
    }
    
    const playerData = getPlayerDataFromTemplate();
    
    if (!playerData.playerCode) {
        console.error('No player code found in data');
        return;
    }
    
    const playerTitle = new PlayerTitle(
        playerData.playerCode, 
        playerData.encodedPlayerCode,
        {
            currentPage: 'overview',
            stats: playerData.stats,
            recentGames: playerData.recentGames,
            showQuickStats: true,
            showCharacterDropdown: false,
            showActions: false
        }
    );
    
    // ✅ COMPONENT INTERACTION: Refresh character icons
    setTimeout(() => {
        if (typeof initializeCharacterIcons === 'function') {
            initializeCharacterIcons();
        }
    }, 200);
    
    return playerTitle;
}

function initializeLoadMore() {
    const loadMoreBtn = document.getElementById('loadMoreGames');
    if (!loadMoreBtn) return;
    
    let currentPage = 1;
    let loading = false;
    
    loadMoreBtn.addEventListener('click', async function() {
        if (loading) return;
        
        loading = true;
        this.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Loading...';
        this.disabled = true;
        
        try {
            // ✅ BUSINESS LOGIC: API call
            const playerData = getPlayerDataFromTemplate();
            const response = await fetch(`/api/player/${playerData.encodedPlayerCode}/games?page=${currentPage + 1}`);
            
            if (!response.ok) {
                throw new Error('Failed to load games');
            }
            
            const data = await response.json();
            
            if (data.games && data.games.length > 0) {
                // ✅ COMPONENT INTERACTION: Use component method
                if (window.TablesComponent) {
                    window.TablesComponent.appendGames('gamesTableBody', data.games);
                }
                
                currentPage++;
                
                if (currentPage >= data.total_pages) {
                    this.style.display = 'none';
                }
            } else {
                this.style.display = 'none';
            }
            
        } catch (error) {
            console.error('Error loading more games:', error);
            this.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Error loading games';
            setTimeout(() => {
                this.innerHTML = 'Load More';
                this.disabled = false;
            }, 3000);
        } finally {
            if (this.style.display !== 'none') {
                this.innerHTML = 'Load More';
                this.disabled = false;
            }
            loading = false;
        }
    });
}

function getPlayerDataFromTemplate() {
    // Get data from JSON script tag instead of data attributes
    const dataScript = document.getElementById('player-data');
    if (!dataScript) {
        console.error('Player data script not found');
        return {
            playerCode: '',
            encodedPlayerCode: '',
            stats: {},
            recentGames: []
        };
    }
    
    try {
        const data = JSON.parse(dataScript.textContent);
        console.log('Parsed player data successfully:', data);
        
        // Ensure we have encoded player code
        const playerCode = data.playerCode || '';
        const encodedPlayerCode = playerCode ? encodeURIComponent(playerCode) : '';
        
        return {
            playerCode: playerCode,
            encodedPlayerCode: encodedPlayerCode,
            stats: data.stats || {},
            recentGames: data.recentGames || []
        };
    } catch (error) {
        console.error('Error parsing player data JSON:', error);
        console.error('Raw JSON content:', dataScript.textContent);
        return {
            playerCode: '',
            encodedPlayerCode: '',
            stats: {},
            recentGames: []
        };
    }
}