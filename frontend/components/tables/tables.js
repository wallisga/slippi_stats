// frontend/components/tables/tables.js
// Tables Component - SIMPLIFIED AND OPTIMIZED

/**
 * Simplified Tables Component
 * Only includes features that are actually being used
 */
class TablesComponent {
    constructor() {
        this.init();
    }
    
    init() {
        this.formatGameTimes();
        this.setupRowNavigation();
        
        console.log('Tables component initialized (optimized)');
    }
    
    /**
     * Format game times to relative format (e.g., "2h ago")
     */
    formatGameTimes() {
        const gameTimeElements = document.querySelectorAll('.game-time');
        
        gameTimeElements.forEach(element => {
            const timeText = element.textContent.trim();
            if (!timeText) return;
            
            try {
                const date = new Date(timeText);
                const now = new Date();
                const diffMs = now - date;
                const diffMinutes = Math.floor(diffMs / (1000 * 60));
                const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
                const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                
                let relativeTime;
                if (diffMinutes < 60) {
                    relativeTime = diffMinutes <= 1 ? 'Just now' : `${diffMinutes}m ago`;
                } else if (diffHours < 24) {
                    relativeTime = `${diffHours}h ago`;
                } else if (diffDays < 7) {
                    relativeTime = `${diffDays}d ago`;
                } else {
                    relativeTime = date.toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                    });
                }
                
                element.textContent = relativeTime;
                element.title = timeText; // Keep original time in tooltip
            } catch (error) {
                console.warn('Could not parse date:', timeText);
            }
        });
    }
    
    /**
     * Setup click-to-navigate for table rows
     */
    setupRowNavigation() {
        const tableRows = document.querySelectorAll('.games-table tbody tr');
        
        tableRows.forEach(row => {
            const link = row.querySelector('.opponent-link');
            if (link) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', (e) => {
                    // Don't navigate if clicking on a link directly
                    if (e.target.tagName === 'A' || e.target.closest('a')) {
                        return;
                    }
                    window.location.href = link.href;
                });
            }
        });
    }
    
    /**
     * Update stats table with new data (for filtered results)
     */
    updateStatsTable(tableId, countElementId, stats, showCharacterIcons = false) {
        let tbody = document.getElementById(tableId + '-table');
        
        if (!tbody) {
            console.error('Stats table not found:', tableId + '-table');
            return;
        }
        
        // Update count badge
        if (countElementId) {
            const countElement = document.getElementById(countElementId);
            if (countElement) {
                countElement.textContent = Object.keys(stats).length;
            }
        }
        
        // Clear and populate table
        tbody.innerHTML = '';
        
        // Convert stats object to sorted array
        const statsArray = Object.entries(stats)
            .map(([name, data]) => ({
                name: name,
                games: data.games || data.total_games || 0,
                winRate: data.win_rate || 0
            }))
            .sort((a, b) => b.games - a.games);
        
        // Create rows
        statsArray.forEach(stat => {
            const row = document.createElement('tr');
            const winRatePercent = (stat.winRate * 100).toFixed(1);
            
            if (showCharacterIcons) {
                row.innerHTML = `
                    <td>
                        <span data-character-name="${stat.name}" class="character-container me-2"></span>${stat.name}
                    </td>
                    <td>${stat.games}</td>
                    <td>${winRatePercent}%</td>
                `;
            } else {
                row.innerHTML = `
                    <td>${stat.name}</td>
                    <td>${stat.games}</td>
                    <td>${winRatePercent}%</td>
                `;
            }
            
            tbody.appendChild(row);
        });
    }
    
    /**
     * Append new games to games table (for "Load More" functionality)
     */
    appendGames(tableBodyId, games) {
        const tbody = document.getElementById(tableBodyId);
        if (!tbody) {
            console.error('Table body not found:', tableBodyId);
            return;
        }
        
        games.forEach(game => {
            const row = this.createGameRow(game);
            tbody.appendChild(row);
        });
        
        // Re-format new timestamps and setup navigation
        this.formatGameTimes();
        this.setupRowNavigation();
    }
    
    /**
     * Create a game row element
     */
    createGameRow(game) {
        const row = document.createElement('tr');
        const encodedOpponentTag = encodeURIComponent(game.opponent_tag || game.opponent?.player_tag || '');
        const opponentName = game.opponent_tag || game.opponent?.player_tag || 'Unknown';
        const playerChar = game.player_character || 'Unknown';
        const opponentChar = game.opponent_character || 'Unknown';
        const stageName = game.stage_name || `Stage ${game.stage_id || 'Unknown'}`;
        const result = (game.result || 'unknown').toLowerCase();
        
        row.innerHTML = `
            <td class="game-time">${game.start_time || ''}</td>
            <td>
                ${encodedOpponentTag ? 
                    `<a href="/player/${encodedOpponentTag}" class="opponent-link">${opponentName}</a>` :
                    `<span class="opponent-name">${opponentName}</span>`
                }
            </td>
            <td>
                <span data-character-name="${playerChar}" class="character-container me-2"></span>${playerChar}
                <span class="text-muted mx-2">vs</span>
                <span data-character-name="${opponentChar}" class="character-container me-2"></span>${opponentChar}
            </td>
            <td class="stage-name">${stageName}</td>
            <td>
                <span class="result-${result}">${game.result || 'Unknown'}</span>
            </td>
        `;
        
        return row;
    }
}

/**
 * Initialize tables component
 */
function initializeTables() {
    window.TablesComponent = new TablesComponent();
}

// ✅ AUTO-INITIALIZE
initializeTables();

// ✅ EXPORT
window.initializeTables = initializeTables;