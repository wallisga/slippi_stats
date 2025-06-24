// Tables Component JavaScript - AUTO-INITIALIZATION
class TablesComponent {
    static initializeTableInteractions() {
        const tableRows = document.querySelectorAll('.games-table tbody tr');
        
        tableRows.forEach(row => {
            if (row.dataset.tableInitialized) return;
            row.dataset.tableInitialized = 'true';
            
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        console.log('Tables component initialized');
    }
    
    static appendGames(tableBodyId, games) {
        const tableBody = document.getElementById(tableBodyId);
        if (!tableBody) return;
        
        games.forEach(game => {
            const row = this.createGameRow(game);
            tableBody.appendChild(row);
        });
        
        // Re-initialize for new rows
        this.initializeTableInteractions();
        
        // Initialize character icons for new content
        if (window.initializeCharacterIcons) {
            window.initializeCharacterIcons(tableBody);
        }
    }
    
    static createGameRow(game) {
        const row = document.createElement('tr');
        const opponentTag = game.opponent?.player_tag || 'Unknown';
        const opponentEncoded = game.opponent?.encoded_tag || encodeURIComponent(opponentTag);
        const playerChar = game.player?.character_name || 'Unknown';
        const opponentChar = game.opponent?.character_name || 'Unknown';
        
        row.innerHTML = `
            <td class="game-time">${this.formatGameTime(game.start_time)}</td>
            <td>
                <a href="/player/${opponentEncoded}" class="opponent-link">
                    ${opponentTag}
                </a>
            </td>
            <td>
                <span data-character-name="${playerChar}" class="character-container me-2"></span>${playerChar}
                vs
                <span data-character-name="${opponentChar}" class="character-container me-2"></span>${opponentChar}
            </td>
            <td class="stage-name">Stage ${game.stage_id}</td>
            <td>
                <span class="result-${game.result.toLowerCase()}">${game.result}</span>
            </td>
        `;
        return row;
    }
    
    static formatGameTime(timeString) {
        try {
            const date = new Date(timeString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } catch (error) {
            return timeString;
        }
    }
    
    static updateStatsTable(tableId, countId, statsData, showCharacterIcons) {
        const table = document.getElementById(tableId);
        const countElement = document.getElementById(countId);
        
        if (!table) return;
        
        table.innerHTML = '';
        let count = 0;
        
        // Convert object to array and sort by games played
        const sortedStats = Object.entries(statsData)
            .filter(([_, stats]) => stats.games > 0)
            .sort((a, b) => b[1].games - a[1].games);
        
        for (const [name, stats] of sortedStats) {
            count++;
            
            const row = document.createElement('tr');
            const winRateClass = stats.win_rate >= 0.6 ? 'text-success' : 
                                stats.win_rate >= 0.4 ? 'text-warning' :
                                'text-danger';
            
            const nameCell = showCharacterIcons ? 
                `<td><span data-character-name="${name}" class="character-container"></span>${name}</td>` :
                `<td>${name}</td>`;
            
            row.innerHTML = `
                ${nameCell}
                <td>${stats.games}</td>
                <td class="${winRateClass} fw-bold">${(stats.win_rate * 100).toFixed(1)}%</td>
            `;
            
            table.appendChild(row);
        }
        
        if (countElement) countElement.textContent = count;
        
        // Initialize character icons for new content
        if (showCharacterIcons && window.initializeCharacterIcons) {
            window.initializeCharacterIcons(table);
        }
    }
}

// ✅ AUTO-INITIALIZE
TablesComponent.initializeTableInteractions();

// ✅ EXPORT
window.TablesComponent = TablesComponent;