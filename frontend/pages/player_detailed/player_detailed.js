// Enhanced Player Detailed Page JavaScript with Search-Filter Coordination
// frontend/pages/player_detailed/player_detailed.js

let playerData = null;
let playerTitleComponent = null;
let originalPlayerStats = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Player detailed page initializing with search-filter coordination...');
    
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
    
    // ✅ COMPONENT COORDINATION: Setup search-enhanced filters
    setupSearchEnhancedFilters();
    
    // ✅ BUSINESS LOGIC: Load initial data
    fetchPlayerData();
    
    console.log('Player detailed page loaded with search integration');
});

/**
 * ✅ COMPONENT COORDINATION: Setup enhanced filters with search integration
 */
function setupSearchEnhancedFilters() {
    if (!window.advancedFilters) {
        console.warn('Advanced filters component not available');
        return;
    }
    
    // Connect filters component to page functionality
    window.advancedFilters.onFilterChange((filters) => {
        console.log('Filters changed with search integration:', filters);
        fetchPlayerData(filters);
    });
    
    // ✅ PAGE ORCHESTRATION: Setup keyboard shortcuts for filter search
    setupFilterSearchShortcuts();
    
    console.log('Search-enhanced filters coordination established');
}

/**
 * ✅ PAGE ORCHESTRATION: Setup keyboard shortcuts for filter search
 */
function setupFilterSearchShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Shift + 1 - Focus character search
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '1') {
            e.preventDefault();
            focusFilterSearch('characterSearch');
        }
        
        // Ctrl/Cmd + Shift + 2 - Focus opponent search
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '2') {
            e.preventDefault();
            focusFilterSearch('opponentSearch');
        }
        
        // Ctrl/Cmd + Shift + 3 - Focus opponent character search
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === '3') {
            e.preventDefault();
            focusFilterSearch('opponentCharSearch');
        }
    });
}

/**
 * ✅ COMPONENT INTERACTION: Focus specific filter search input
 */
function focusFilterSearch(searchInputId) {
    const searchInput = document.getElementById(searchInputId);
    if (searchInput && searchInput.offsetParent !== null) {
        searchInput.focus();
        searchInput.select();
        
        // Expand filters if collapsed
        const filterCollapse = document.getElementById('filterCollapse');
        if (filterCollapse && !filterCollapse.classList.contains('show')) {
            const collapseButton = document.querySelector('[data-bs-target="#filterCollapse"]');
            if (collapseButton) {
                collapseButton.click();
            }
        }
    }
}

/**
 * ✅ PAGE ORCHESTRATION: Enhanced filter options management with search
 */
function enhanceFilterOptionsWithSearch(filterOptions) {
    if (!window.advancedFilters || !filterOptions) {
        return;
    }
    
    console.log('Enhancing filter options with search capabilities:', {
        characters: filterOptions.characters?.length || 0,
        opponents: filterOptions.opponents?.length || 0,
        opponent_characters: filterOptions.opponent_characters?.length || 0
    });
    
    // ✅ COMPONENT INTERACTION: Populate filters with enhanced search
    window.advancedFilters.populateFilterOptions(filterOptions);
    
    // ✅ PAGE LOGIC: Add search hints for large option sets
    addSearchHintsForLargeOptionSets(filterOptions);
    
    // ✅ PAGE LOGIC: Setup auto-clear for specific searches
    setupSmartSearchBehavior(filterOptions);
}

/**
 * ✅ PAGE LOGIC: Add helpful hints when option sets are large
 */
function addSearchHintsForLargeOptionSets(filterOptions) {
    const hints = {
        characters: filterOptions.characters?.length || 0,
        opponents: filterOptions.opponents?.length || 0,
        opponent_characters: filterOptions.opponent_characters?.length || 0
    };
    
    // Add hints for large option sets
    Object.entries(hints).forEach(([type, count]) => {
        if (count > 20) {
            const searchInputId = getSearchInputId(type);
            const searchInput = document.getElementById(searchInputId);
            
            if (searchInput) {
                // Update placeholder with helpful hint
                const originalPlaceholder = searchInput.placeholder;
                searchInput.placeholder = `Search ${count} ${type.replace('_', ' ')}...`;
                
                // Add tooltip or small text hint
                addSearchHintText(searchInput, count, type);
            }
        }
    });
}

/**
 * ✅ PAGE LOGIC: Get search input ID for filter type
 */
function getSearchInputId(filterType) {
    const mapping = {
        'characters': 'characterSearch',
        'opponents': 'opponentSearch', 
        'opponent_characters': 'opponentCharSearch'
    };
    return mapping[filterType] || 'characterSearch';
}

/**
 * ✅ PAGE LOGIC: Add search hint text below input
 */
function addSearchHintText(searchInput, count, type) {
    const container = searchInput.closest('.filter-search-input');
    if (!container) return;
    
    // Remove existing hint
    const existingHint = container.querySelector('.search-hint');
    if (existingHint) {
        existingHint.remove();
    }
    
    // Add new hint if count is large
    if (count > 50) {
        const hint = document.createElement('small');
        hint.className = 'search-hint text-muted mt-1';
        hint.innerHTML = `💡 <strong>Tip:</strong> ${count} options available - use search to filter`;
        hint.style.display = 'block';
        hint.style.fontSize = '0.75rem';
        container.appendChild(hint);
    }
}

/**
 * ✅ PAGE LOGIC: Setup smart search behavior for better UX
 */
function setupSmartSearchBehavior(filterOptions) {
    // Auto-focus first search input if opponents list is very large
    if (filterOptions.opponents && filterOptions.opponents.length > 100) {
        setTimeout(() => {
            const opponentSearch = document.getElementById('opponentSearch');
            if (opponentSearch) {
                // Add a subtle visual cue
                opponentSearch.style.boxShadow = '0 0 0 2px rgba(13, 110, 253, 0.25)';
                setTimeout(() => {
                    opponentSearch.style.boxShadow = '';
                }, 2000);
            }
        }, 1000);
    }
    
    // Setup smart defaults for character searches
    setupCharacterSearchDefaults(filterOptions);
}

/**
 * ✅ PAGE LOGIC: Setup smart defaults for character searches  
 */
function setupCharacterSearchDefaults(filterOptions) {
    // If there are many characters, pre-populate with common ones
    const commonCharacters = [
        'Fox', 'Falco', 'Marth', 'Sheik', 'Jigglypuff', 
        'Peach', 'Captain Falcon', 'Ice Climbers'
    ];
    
    if (filterOptions.characters && filterOptions.characters.length > 25) {
        // Add quick filter buttons for common characters
        addQuickCharacterFilters(commonCharacters, filterOptions.characters);
    }
}

/**
 * ✅ PAGE ENHANCEMENT: Add quick filter buttons for common characters
 */
function addQuickCharacterFilters(commonChars, allChars) {
    const availableCommon = commonChars.filter(char => allChars.includes(char));
    
    if (availableCommon.length === 0) return;
    
    // Add quick filters to character section
    const characterContainer = document.getElementById('characterCheckboxes');
    if (!characterContainer) return;
    
    const quickFiltersContainer = document.createElement('div');
    quickFiltersContainer.className = 'quick-filters mb-2';
    quickFiltersContainer.innerHTML = `
        <small class="text-muted d-block mb-1">Quick filters:</small>
        <div class="d-flex flex-wrap gap-1">
            ${availableCommon.map(char => 
                `<button type="button" class="btn btn-outline-primary btn-xs quick-char-filter" data-character="${char}">
                    ${char}
                </button>`
            ).join('')}
        </div>
    `;
    
    // Insert before the search input
    const searchInput = characterContainer.querySelector('.filter-search-input');
    if (searchInput) {
        characterContainer.insertBefore(quickFiltersContainer, searchInput);
    } else {
        characterContainer.insertBefore(quickFiltersContainer, characterContainer.firstChild);
    }
    
    // Setup quick filter functionality
    quickFiltersContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('quick-char-filter')) {
            const character = e.target.dataset.character;
            const characterSearch = document.getElementById('characterSearch');
            if (characterSearch) {
                characterSearch.value = character;
                characterSearch.dispatchEvent(new Event('input'));
            }
        }
    });
}

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

// ✅ BUSINESS LOGIC: Enhanced API calls and data management with search coordination
async function fetchPlayerData(filters = {}) {
    showLoading();
    
    try {
        const playerTemplateData = getPlayerDataFromTemplate();
        const playerCode = playerTemplateData.playerCode;
        const encodedPlayerCode = playerTemplateData.encodedPlayerCode;
        
        if (!playerCode) {
            throw new Error('No player code available');
        }
        
        console.log('Fetching data for player with search-enhanced filters:', playerCode, filters);
        
        // Save current filter selections AND search states before making API call
        const savedSelections = {};
        const savedSearches = {};
        
        if (window.advancedFilters) {
            savedSelections.characters = window.advancedFilters.getSelectedCheckboxValues('characterCheckboxes');
            savedSelections.opponents = window.advancedFilters.getSelectedCheckboxValues('opponentCheckboxes');
            savedSelections.opponentChars = window.advancedFilters.getSelectedCheckboxValues('opponentCharCheckboxes');
            
            // Save search states
            savedSearches.character = document.getElementById('characterSearch')?.value || '';
            savedSearches.opponent = document.getElementById('opponentSearch')?.value || '';
            savedSearches.opponentChar = document.getElementById('opponentCharSearch')?.value || '';
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
        console.log("Received detailed data with filter options:", data);
        
        playerData = data;
        
        // ✅ COMPONENT COORDINATION: Enhanced filter population with search
        if (data.filter_options) {
            console.log('Populating search-enhanced filters with options:', data.filter_options);
            enhanceFilterOptionsWithSearch(data.filter_options);
            
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
            
            // Restore search states
            Object.entries(savedSearches).forEach(([type, value]) => {
                if (value) {
                    const inputId = getSearchInputId(type === 'opponentChar' ? 'opponent_characters' : type + 's');
                    const input = document.getElementById(inputId);
                    if (input) {
                        input.value = value;
                        input.dispatchEvent(new Event('input'));
                    }
                }
            });
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

// Extract filter options from API data
function extractFilterOptions(data) {
    return {
        characters: Object.keys(data.character_stats || {}).filter(c => c !== 'Unknown'),
        opponents: Object.keys(data.opponent_stats || {}).filter(o => o !== 'Unknown'),
        opponent_characters: Object.keys(data.opponent_character_stats || {}).filter(c => c !== 'Unknown')
    };
}

// ✅ COMPONENT COORDINATION: Update UI using component APIs
function updateUI(data) {
    console.log('Updating UI with search-filtered data:', data);
    
    // Update overall stats
    const overallWinRate = data.overall_winrate || 0;
    const overallWinRateCircle = document.getElementById('overall-win-rate-circle');
    const overallWinRateText = document.getElementById('overall-win-rate');
    const overallStats = document.getElementById('overall-stats');
    
    if (overallWinRateCircle) overallWinRateCircle.style.setProperty('--win-rate', overallWinRate);
    if (overallWinRateText) overallWinRateText.textContent = `${(overallWinRate * 100).toFixed(1)}%`;
    if (overallStats) {
        overallStats.innerHTML = `
            <strong>${data.wins || 0}</strong> wins out of <strong>${data.total_games || 0}</strong> games
        `;
    }
    
    // Update filter summary
    updateFilterSummary(data);

    // Populate filter options
    if (window.advancedFilters && typeof window.advancedFilters.populateFilterOptions === 'function') {
        const filterOptions = extractFilterOptions(data);
        window.advancedFilters.populateFilterOptions(filterOptions);
        console.log('Populated filter options:', filterOptions);
    }    
    
    // ✅ COMPONENT INTERACTION: Update stats tables using component
    if (window.TablesComponent) {
        // Update character stats table
        if (data.character_stats) {
            window.TablesComponent.updateStatsTable('character-stats', 'character-count', data.character_stats, true);
        }
        
        // Update opponent stats table
        if (data.opponent_stats) {
            window.TablesComponent.updateStatsTable('opponent-stats', 'opponent-count', data.opponent_stats, false);
        }
        
        // Update matchup stats table
        if (data.opponent_character_stats) {
            window.TablesComponent.updateStatsTable('matchup-stats', 'matchup-count', data.opponent_character_stats, true);
        }
    } else {
        console.warn('TablesComponent not available');
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
    setTimeout(() => {
        if (typeof initializeCharacterIcons === 'function') {
            initializeCharacterIcons();
        }
    }, 100);
}

function updateFilterSummary(data) {
    const charactersPlayingAs = document.getElementById('charactersPlayingAs');
    const opponentsPlayingAgainst = document.getElementById('opponentsPlayingAgainst');
    const charactersPlayingAgainst = document.getElementById('charactersPlayingAgainst');
    const totalGamesCount = document.getElementById('totalGamesCount');
    
    if (data.applied_filters) {
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
    }
    
    if (totalGamesCount) totalGamesCount.textContent = data.total_games || 0;
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