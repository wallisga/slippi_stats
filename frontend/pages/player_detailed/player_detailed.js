// Player Detailed Page JavaScript - BUSINESS LOGIC ONLY

let playerData = null;
let playerTitleComponent = null;
let originalPlayerStats = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Player detailed page initializing...');
    
    // Get template data
    const originalData = getPlayerDataFromTemplate();
    if (!originalData.playerCode) {
        console.error('No player code found in template data');
        return;
    }
    
    // Store original stats
    originalPlayerStats = originalData.stats || {
        total_games: 0,
        wins: 0,
        win_rate: 0,
        most_played_character: null,
        character_stats: {}
    };
    
    // ✅ BUSINESS LOGIC: Initialize player title
    playerTitleComponent = initializePlayerTitle(originalData);
    
    // ✅ COMPONENT INTERACTION: Connect filters component to page functionality
    if (window.advancedFilters) {
        window.advancedFilters.onFilterChange((filters) => {
            console.log('Filters changed:', filters);
            fetchPlayerData(filters);
        });
    }
    
    // ✅ BUSINESS LOGIC: Load initial data
    fetchPlayerData();
    
    console.log('Player detailed page loaded');
});

function initializePlayerTitle(playerData) {
    const container = document.getElementById('player-title-container');
    if (!container) {
        console.error('Player title container not found!');
        return null;
    }
    
    const playerTitle = new PlayerTitle(
        playerData.playerCode, 
        playerData.encodedPlayerCode,
        {
            currentPage: 'detailed',
            stats: playerData.stats,
            recentGames: playerData.recentGames,
            showQuickStats: true,
            showCharacterDropdown: false,
            showActions: false
        }
    );
    
    // ✅ COMPONENT INTERACTION: Initialize character icons after title is created
    setTimeout(() => {
        if (typeof initializeCharacterIcons === 'function') {
            initializeCharacterIcons();
        }
    }, 200);
    
    return playerTitle;
}

function getPlayerDataFromTemplate() {
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
        const playerCode = data.playerCode || '';
        const encodedPlayerCode = playerCode ? encodeURIComponent(playerCode) : '';
        
        const stats = data.stats || {};
        const safeStats = {
            total_games: stats.total_games || 0,
            wins: stats.wins || 0,
            win_rate: stats.win_rate || 0,
            most_played_character: stats.most_played_character || null,
            character_stats: stats.character_stats || {},
            ...stats
        };
        
        return {
            playerCode: playerCode,
            encodedPlayerCode: encodedPlayerCode,
            stats: safeStats,
            recentGames: data.recentGames || []
        };
    } catch (error) {
        console.error('Error parsing player data JSON:', error);
        return {
            playerCode: '',
            encodedPlayerCode: '',
            stats: {},
            recentGames: []
        };
    }
}

// ✅ BUSINESS LOGIC: API calls and data management
async function fetchPlayerData(filters = {}) {
    showLoading();
    
    try {
        const playerTemplateData = getPlayerDataFromTemplate();
        const playerCode = playerTemplateData.playerCode;
        const encodedPlayerCode = playerTemplateData.encodedPlayerCode; // ← Use pre-encoded value
        
        if (!playerCode) {
            throw new Error('No player code available');
        }
        
        console.log('Fetching data for player:', playerCode);
        
        // Save current filter selections before making API call
        const savedSelections = {};
        if (window.advancedFilters) {
            savedSelections.characters = window.advancedFilters.getSelectedCheckboxValues('characterCheckboxes');
            savedSelections.opponents = window.advancedFilters.getSelectedCheckboxValues('opponentCheckboxes');
            savedSelections.opponentChars = window.advancedFilters.getSelectedCheckboxValues('opponentCharCheckboxes');
        }
        
        // Prepare filter data
        const filterData = {
            character: filters.character || 'all',
            opponent: filters.opponent || 'all',
            opponent_character: filters.opponent_character || 'all'
        };
        
        const apiUrl = `/api/player/${encodedPlayerCode}/detailed`;
        console.log("Sending filter data:", filterData);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData)
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("Received detailed data:", data);
        
        playerData = data;
        
        // ✅ COMPONENT INTERACTION: Populate filters component with API data
        if (window.advancedFilters && data.filter_options) {
            console.log('Populating filters with options:', data.filter_options);
            window.advancedFilters.populateFilterOptions(data.filter_options);
            
            // Restore previous selections if they existed
            if (savedSelections.characters && savedSelections.characters.length > 0) {
                window.advancedFilters.restoreCheckboxSelections('characterCheckboxes', savedSelections.characters);
            }
            if (savedSelections.opponents && savedSelections.opponents.length > 0) {
                window.advancedFilters.restoreCheckboxSelections('opponentCheckboxes', savedSelections.opponents);
            }
            if (savedSelections.opponentChars && savedSelections.opponentChars.length > 0) {
                window.advancedFilters.restoreCheckboxSelections('opponentCharCheckboxes', savedSelections.opponentChars);
            }
        }
        
        // ✅ COMPONENT COORDINATION: Update UI with filtered data
        updateUI(data);
        
        // Keep player title with original unfiltered stats
        if (playerTitleComponent && originalPlayerStats) {
            playerTitleComponent.updateStats(originalPlayerStats);
        }
        
        hideLoading();
        return data;
    } catch (error) {
        console.error("Error fetching player data:", error);
        hideLoading();
        alert("Error loading player data. Please try again.");
        throw error;
    }
}

// ✅ COMPONENT COORDINATION: Update UI using component APIs
function updateUI(data) {
    // Update overall stats
    const overallWinRate = data.overall_winrate;
    const overallWinRateCircle = document.getElementById('overall-win-rate-circle');
    const overallWinRateText = document.getElementById('overall-win-rate');
    const overallStats = document.getElementById('overall-stats');
    
    if (overallWinRateCircle) overallWinRateCircle.style.setProperty('--win-rate', overallWinRate);
    if (overallWinRateText) overallWinRateText.textContent = `${(overallWinRate * 100).toFixed(1)}%`;
    if (overallStats) {
        overallStats.innerHTML = `
            <strong>${data.wins}</strong> wins out of <strong>${data.total_games}</strong> games
        `;
    }
    
    // Update filter summary
    updateFilterSummary(data);
    
    // ✅ COMPONENT INTERACTION: Update stats tables using component
    if (window.TablesComponent) {
        window.TablesComponent.updateStatsTable('character-stats-table', 'character-count', data.character_stats, true);
        window.TablesComponent.updateStatsTable('opponent-stats-table', 'opponent-count', data.opponent_stats, false);
        window.TablesComponent.updateStatsTable('matchup-stats-table', 'matchup-count', data.opponent_character_stats, true);
    }
    
    // ✅ COMPONENT INTERACTION: Update charts using component
    if (window.ChartsComponent) {
        if (data.date_stats && Object.keys(data.date_stats).length > 0) {
            window.ChartsComponent.updateTimeChart('timeChart', data.date_stats);
        } else {
            window.ChartsComponent.showChartError('timeChart', 'No time data available');
        }
        
        if (data.character_stats && Object.keys(data.character_stats).length > 0) {
            window.ChartsComponent.updateCharacterChart('characterChart', data.character_stats);
        } else {
            window.ChartsComponent.showChartError('characterChart', 'No character data available');
        }
    } else {
        console.warn('ChartsComponent not available');
    }
    
    // ✅ COMPONENT INTERACTION: Initialize character icons after updating tables
    if (typeof initializeCharacterIcons === 'function') {
        initializeCharacterIcons();
    }
}

function updateFilterSummary(data) {
    const charactersPlayingAs = document.getElementById('charactersPlayingAs');
    const opponentsPlayingAgainst = document.getElementById('opponentsPlayingAgainst');
    const charactersPlayingAgainst = document.getElementById('charactersPlayingAgainst');
    const totalGamesCount = document.getElementById('totalGamesCount');
    
    if (charactersPlayingAs) {
        const charFilter = Array.isArray(data.applied_filters.character) ? 
            data.applied_filters.character.join(', ') : 
            data.applied_filters.character;
        charactersPlayingAs.innerHTML = `
            Playing as: <strong>${charFilter === 'all' ? 'All characters' : charFilter}</strong>
        `;
    }
    
    if (opponentsPlayingAgainst) {
        const oppFilter = Array.isArray(data.applied_filters.opponent) ? 
            data.applied_filters.opponent.join(', ') : 
            data.applied_filters.opponent;
        opponentsPlayingAgainst.innerHTML = `
            Playing against: <strong>${oppFilter === 'all' ? 'All opponents' : oppFilter}</strong>
        `;
    }
    
    if (charactersPlayingAgainst) {
        const oppCharFilter = Array.isArray(data.applied_filters.opponent_character) ? 
            data.applied_filters.opponent_character.join(', ') : 
            data.applied_filters.opponent_character;
        charactersPlayingAgainst.innerHTML = `
            Opposing characters: <strong>${oppCharFilter === 'all' ? 'All characters' : oppCharFilter}</strong>
        `;
    }
    
    if (totalGamesCount) totalGamesCount.textContent = data.total_games;
}

// Helper functions
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.visibility = 'visible';
        overlay.style.opacity = 1;
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.opacity = 0;
        setTimeout(() => {
            overlay.style.visibility = 'hidden';
        }, 200);
    }
}