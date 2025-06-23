// Player Basic Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Player basic page initializing...');
    
    // Initialize player title component
    initializePlayerTitle();
    
    // Initialize load more functionality
    initializeLoadMore();
    
    // Initialize other page-specific features
    initializeGameTable();
    
    console.log('Player basic page loaded');
});

function initializePlayerTitle() {
    // Check for container
    const container = document.getElementById('player-title-container');
    if (!container) {
        console.error('Player title container not found!');
        return;
    }
    
    // Get data from JSON script
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
            showCharacterDropdown: false,  // Disabled character functionality
            showActions: false
        }
    );
    
    // Initialize character icons after title is created
    setTimeout(() => {
        if (typeof initializeCharacterIcons === 'function') {
            initializeCharacterIcons();
        }
    }, 200);
    
    return playerTitle;
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
        
        return {
            playerCode: data.playerCode || '',
            encodedPlayerCode: data.encodedPlayerCode || '',
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
            const playerData = getPlayerDataFromTemplate();
            const response = await fetch(`/api/player/${playerData.encodedPlayerCode}/games?page=${currentPage + 1}`);
            
            if (!response.ok) {
                throw new Error('Failed to load games');
            }
            
            const data = await response.json();
            
            if (data.games && data.games.length > 0) {
                appendGamesToTable(data.games);
                currentPage++;
                
                // Hide button if no more pages
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

function appendGamesToTable(games) {
    const tableBody = document.getElementById('gamesTableBody');
    if (!tableBody) return;
    
    games.forEach(game => {
        const row = createGameRow(game);
        tableBody.appendChild(row);
    });
    
    // Re-initialize character icons for new rows
    if (typeof initializeCharacterIcons === 'function') {
        initializeCharacterIcons(tableBody);
    }
}

function createGameRow(game) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td class="game-time">${formatGameTime(game.start_time)}</td>
        <td>
            <a href="/player/${encodeURIComponent(game.opponent.player_tag)}" class="opponent-link">
                ${game.opponent.player_name}
            </a>
        </td>
        <td>
            <span data-character-name="${game.player.character_name}" class="character-container me-2"></span>${game.player.character_name}
            vs
            <span data-character-name="${game.opponent.character_name}" class="character-container me-2"></span>${game.opponent.character_name}
        </td>
        <td class="stage-name">Stage ${game.stage_id}</td>
        <td>
            <span class="result-${game.result.toLowerCase()}">${game.result}</span>
        </td>
    `;
    return row;
}

function formatGameTime(timeString) {
    try {
        const date = new Date(timeString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } catch (error) {
        return timeString;
    }
}

function initializeGameTable() {
    // Add hover effects and click handlers for game rows
    const gameRows = document.querySelectorAll('.games-table tbody tr');
    
    gameRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
        
        // Add click-to-expand functionality for game details (future feature)
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on a link
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            // Future: expand row to show game details
            console.log('Game row clicked:', this);
        });
    });
}