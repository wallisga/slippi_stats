// Player Detailed Page JavaScript

// Global variables
let timeChart = null;
let characterChart = null;
let playerData = null;
let playerTitleComponent = null;
let originalPlayerStats = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Player detailed page initializing...');
    
    // Get original template data and validate it
    const originalData = getPlayerDataFromTemplate();
    console.log('Original template data:', originalData);
    
    // Validate that we have basic player data
    if (!originalData.playerCode) {
        console.error('No player code found in template data');
        return;
    }
    
    // Store original stats for title component (ensure they exist)
    originalPlayerStats = originalData.stats || {
        total_games: 0,
        wins: 0,
        win_rate: 0,
        most_played_character: null,
        character_stats: {}
    };
    
    console.log('Stored original stats:', originalPlayerStats);
    
    // Initialize player title component
    playerTitleComponent = initializePlayerTitle(originalData);
    
    // Setup page functionality
    setupFilterToggles();
    initializeEventListeners();
    
    // Load detailed data for filtering
    fetchPlayerData();
    
    console.log('Player detailed page loaded');
});

function initializePlayerTitle(playerData) {
    const container = document.getElementById('player-title-container');
    if (!container) {
        console.error('Player title container not found!');
        return null;
    }
    
    console.log('Initializing player title with data:', playerData);
    
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
    
    // Initialize character icons after title is created
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
        console.log('Raw template data:', data);
        
        // Always generate encoded version client-side
        const playerCode = data.playerCode || '';
        const encodedPlayerCode = playerCode ? encodeURIComponent(playerCode) : '';
        
        // Ensure stats object has required properties with defaults
        const stats = data.stats || {};
        const safeStats = {
            total_games: stats.total_games || 0,
            wins: stats.wins || 0,
            win_rate: stats.win_rate || 0,
            most_played_character: stats.most_played_character || null,
            character_stats: stats.character_stats || {},
            ...stats // Preserve any other properties
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

function getSelectedCheckboxValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Fetch detailed player data for filtering
async function fetchPlayerData(filters = {}) {
    showLoading();
    
    try {
        const playerTemplateData = getPlayerDataFromTemplate();
        const playerCode = playerTemplateData.playerCode;
        const encodedPlayerCode = encodeURIComponent(playerCode);
        
        if (!playerCode) {
            throw new Error('No player code available');
        }
        
        console.log('Fetching data for player:', playerCode);
        
        // Save current checkbox selections
        const savedSelections = {};
        
        if (document.getElementById('characterFilterToggle')?.checked) {
            savedSelections.characters = getSelectedCheckboxValues('characterCheckboxes');
        }
        
        if (document.getElementById('opponentFilterToggle')?.checked) {
            savedSelections.opponents = getSelectedCheckboxValues('opponentCheckboxes');
        }
        
        if (document.getElementById('opponentCharFilterToggle')?.checked) {
            savedSelections.opponentChars = getSelectedCheckboxValues('opponentCharCheckboxes');
        }
        
        // Prepare filter data
        const filterData = {};
        
        // Handle filters
        if (document.getElementById('characterFilterToggle')?.checked) {
            const selectedChars = savedSelections.characters;
            if (selectedChars && selectedChars.length > 0 && selectedChars.length < playerData?.filter_options?.characters?.length) {
                filterData.character = selectedChars;
            } else {
                filterData.character = 'all';
            }
        } else if (filters.character && filters.character !== 'all') {
            filterData.character = filters.character;
        } else {
            filterData.character = 'all';
        }
        
        if (document.getElementById('opponentFilterToggle')?.checked) {
            const selectedOpponents = savedSelections.opponents;
            if (selectedOpponents && selectedOpponents.length > 0 && selectedOpponents.length < playerData?.filter_options?.opponents?.length) {
                filterData.opponent = selectedOpponents;
            } else {
                filterData.opponent = 'all';
            }
        } else if (filters.opponent && filters.opponent !== 'all') {
            filterData.opponent = filters.opponent;
        } else {
            filterData.opponent = 'all';
        }
        
        if (document.getElementById('opponentCharFilterToggle')?.checked) {
            const selectedOpponentChars = savedSelections.opponentChars;
            if (selectedOpponentChars && selectedOpponentChars.length > 0 && selectedOpponentChars.length < playerData?.filter_options?.opponent_characters?.length) {
                filterData.opponent_character = selectedOpponentChars;
            } else {
                filterData.opponent_character = 'all';
            }
        } else if (filters.opponent_character && filters.opponent_character !== 'all') {
            filterData.opponent_character = filters.opponent_character;
        } else {
            filterData.opponent_character = 'all';
        }
        
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
        
        // Populate filters and restore selections
        populateFilters(data);
        
        if (savedSelections.characters) {
            restoreCheckboxSelections('characterCheckboxes', savedSelections.characters);
        }
        
        if (savedSelections.opponents) {
            restoreCheckboxSelections('opponentCheckboxes', savedSelections.opponents);
        }
        
        if (savedSelections.opponentChars) {
            restoreCheckboxSelections('opponentCharCheckboxes', savedSelections.opponentChars);
        }
        
        // Update UI with filtered data
        updateUI(data);
        
        // IMPORTANT: Keep player title with original unfiltered stats
        if (playerTitleComponent && originalPlayerStats) {
            console.log('Updating title component with original stats:', originalPlayerStats);
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

// Rest of the functions remain the same...
function restoreCheckboxSelections(containerId, selectedValues) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
    
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    
    checkboxes.forEach(cb => {
        if (selectedValues.includes(cb.value)) {
            cb.checked = true;
        }
    });
    
    updateSelectAllCheckbox(containerId, 
        containerId === 'characterCheckboxes' ? 'selectAllCharacters' : 
        containerId === 'opponentCheckboxes' ? 'selectAllOpponents' : 
        'selectAllOpponentChars');
}

function createCheckboxes(containerId, items, namePrefix, selectAllId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const allOption = container.querySelector('.select-all-option');
    if (allOption) {
        container.innerHTML = '';
        container.appendChild(allOption);
    }
    
    items.forEach((item, index) => {
        const checkDiv = document.createElement('div');
        checkDiv.className = 'checkbox-item';
        
        const formCheck = document.createElement('div');
        formCheck.className = 'form-check';
        
        const input = document.createElement('input');
        input.className = 'form-check-input';
        input.type = 'checkbox';
        input.id = `${namePrefix}_${index}`;
        input.value = item;
        input.checked = true;
        
        input.addEventListener('change', function() {
            updateSelectAllCheckbox(containerId, selectAllId);
        });
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `${namePrefix}_${index}`;
        label.textContent = item;
        
        formCheck.appendChild(input);
        formCheck.appendChild(label);
        checkDiv.appendChild(formCheck);
        container.appendChild(checkDiv);
    });
    
    const selectAllCheckbox = document.getElementById(selectAllId);
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
            });
        });
    }
}

function updateSelectAllCheckbox(containerId, selectAllId) {
    const container = document.getElementById(containerId);
    const selectAll = document.getElementById(selectAllId);
    if (!container || !selectAll) return;
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
    const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
    
    selectAll.checked = checkedCount === checkboxes.length;
    selectAll.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
}

function populateFilters(data) {
    const characterFilter = document.getElementById('characterFilter');
    const opponentFilter = document.getElementById('opponentFilter');
    const opponentCharacterFilter = document.getElementById('opponentCharacterFilter');
    if (!characterFilter || !opponentFilter || !opponentCharacterFilter) return;
    
    // Save current selections
    const currentCharacter = characterFilter.value;
    const currentOpponent = opponentFilter.value;
    const currentOpponentChar = opponentCharacterFilter.value;
    
    // Clear existing options except the first one
    while (characterFilter.options.length > 1) {
        characterFilter.remove(1);
    }
    
    while (opponentFilter.options.length > 1) {
        opponentFilter.remove(1);
    }
    
    while (opponentCharacterFilter.options.length > 1) {
        opponentCharacterFilter.remove(1);
    }
    
    // Add character options
    data.filter_options.characters.forEach(char => {
        const option = document.createElement('option');
        option.value = char;
        option.textContent = char;
        characterFilter.appendChild(option);
    });
    
    // Add opponent options
    data.filter_options.opponents.forEach(opp => {
        const option = document.createElement('option');
        option.value = opp;
        option.textContent = opp;
        opponentFilter.appendChild(option);
    });
    
    // Add opponent character options
    data.filter_options.opponent_characters.forEach(oppChar => {
        const option = document.createElement('option');
        option.value = oppChar;
        option.textContent = oppChar;
        opponentCharacterFilter.appendChild(option);
    });
    
    // Restore previous selections if they exist
    if (currentCharacter !== 'all') {
        const exists = Array.from(characterFilter.options).some(opt => opt.value === currentCharacter);
        if (exists) characterFilter.value = currentCharacter;
    }
    
    if (currentOpponent !== 'all') {
        const exists = Array.from(opponentFilter.options).some(opt => opt.value === currentOpponent);
        if (exists) opponentFilter.value = currentOpponent;
    }
    
    if (currentOpponentChar !== 'all') {
        const exists = Array.from(opponentCharacterFilter.options).some(opt => opt.value === currentOpponentChar);
        if (exists) opponentCharacterFilter.value = currentOpponentChar;
    }
    
    // Apply filters from API response
    characterFilter.value = data.applied_filters.character;
    opponentFilter.value = data.applied_filters.opponent;
    opponentCharacterFilter.value = data.applied_filters.opponent_character;
    
    // Set up checkbox filters
    createCheckboxes(
        'characterCheckboxes', 
        data.filter_options.characters, 
        'char',
        'selectAllCharacters'
    );
    
    createCheckboxes(
        'opponentCheckboxes', 
        data.filter_options.opponents, 
        'opp',
        'selectAllOpponents'
    );
    
    createCheckboxes(
        'opponentCharCheckboxes', 
        data.filter_options.opponent_characters, 
        'opp_char',
        'selectAllOpponentChars'
    );
}

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
    const charactersPlayingAs = document.getElementById('charactersPlayingAs');
    const opponentsPlayingAgainst = document.getElementById('opponentsPlayingAgainst');
    const charactersPlayingAgainst = document.getElementById('charactersPlayingAgainst');
    const totalGamesCount = document.getElementById('totalGamesCount');
    
    if (charactersPlayingAs) {
        charactersPlayingAs.innerHTML = `
            Playing as: <strong>${data.applied_filters.character === 'all' ? 'All characters' : data.applied_filters.character}</strong>
        `;
    }
    
    if (opponentsPlayingAgainst) {
        opponentsPlayingAgainst.innerHTML = `
            Playing against: <strong>${data.applied_filters.opponent === 'all' ? 'All opponents' : data.applied_filters.opponent}</strong>
        `;
    }
    
    if (charactersPlayingAgainst) {
        charactersPlayingAgainst.innerHTML = `
            Opposing characters: <strong>${data.applied_filters.opponent_character === 'all' ? 'All characters' : data.applied_filters.opponent_character}</strong>
        `;
    }
    
    if (totalGamesCount) totalGamesCount.textContent = data.total_games;
    
    // Update stats tables with character icons
    updateStatsTable('character-stats-table', 'character-count', data.character_stats, true);
    updateStatsTable('opponent-stats-table', 'opponent-count', data.opponent_stats, false);
    updateStatsTable('matchup-stats-table', 'matchup-count', data.opponent_character_stats, true);
    
    // Update charts
    if (data.date_stats && Object.keys(data.date_stats).length > 0) {
        try {
            updateTimeChart(data.date_stats);
        } catch (error) {
            console.error("Error updating time chart:", error);
            handleChartError('timeChart');
        }
    }
    
    if (data.character_stats && Object.keys(data.character_stats).length > 0) {
        try {
            updateCharacterChart(data.character_stats);
        } catch (error) {
            console.error("Error updating character chart:", error);
            handleChartError('characterChart');
        }
    }
    
    // Initialize character icons after updating tables
    if (typeof initializeCharacterIcons === 'function') {
        initializeCharacterIcons();
    }
}

function updateStatsTable(tableId, countId, statsData, showCharacterIcons) {
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
}

function handleChartError(chartId) {
    const chartContainer = document.querySelector(`#${chartId}`).parentNode;
    if (chartContainer) {
        chartContainer.innerHTML = '<div class="alert alert-warning">Unable to load chart. Charts require Chart.js library.</div>';
    }
}

function updateTimeChart(dateStats) {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js is not loaded!");
        return;
    }
    
    const timeChartElement = document.getElementById('timeChart');
    if (!timeChartElement) {
        console.error("Time chart element not found!");
        return;
    }
    
    const ctx = timeChartElement.getContext('2d');
    
    const dates = Object.keys(dateStats);
    const winRates = dates.map(date => dateStats[date].win_rate * 100);
    const gamesCounts = dates.map(date => dateStats[date].games);
    
    if (timeChart) {
        timeChart.destroy();
    }
    
    timeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Win Rate (%)',
                    data: winRates,
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Games Played',
                    data: gamesCounts,
                    borderColor: 'rgba(13, 110, 253, 1)',
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderWidth: 2,
                    tension: 0.1,
                    yAxisID: 'y1',
                    type: 'bar'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Win Rate (%)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    title: {
                        display: true,
                        text: 'Games Played'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function updateCharacterChart(characterStats) {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js is not loaded!");
        return;
    }
    
    const characterChartElement = document.getElementById('characterChart');
    if (!characterChartElement) {
        console.error("Character chart element not found!");
        return;
    }
    
    const ctx = characterChartElement.getContext('2d');
    
    const filteredStats = Object.entries(characterStats)
        .filter(([_, stats]) => stats.games > 0)
        .sort((a, b) => b[1].games - a[1].games);
    
    const characters = filteredStats.map(([char, _]) => char);
    const winRates = filteredStats.map(([_, stats]) => stats.win_rate * 100);
    const gamesCounts = filteredStats.map(([_, stats]) => stats.games);
    
    const backgroundColors = winRates.map(rate => {
        if (rate >= 60) return 'rgba(40, 167, 69, 0.6)';
        if (rate >= 40) return 'rgba(255, 193, 7, 0.6)';
        return 'rgba(220, 53, 69, 0.6)';
    });
    
    if (characterChart) {
        characterChart.destroy();
    }
    
    characterChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: characters,
            datasets: [
                {
                    label: 'Win Rate (%)',
                    data: winRates,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                y: {
                    ticks: {
                        autoSkip: false,
                        padding: 15
                    },
                    afterFit: function(scaleInstance) {
                        scaleInstance.width = 120;
                    }
                },
                x: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Win Rate (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const idx = context.dataIndex;
                            return `Games Played: ${gamesCounts[idx]}`;
                        }
                    }
                }
            },
            barPercentage: 0.8,
            categoryPercentage: 0.7
        }
    });
}

function setupFilterToggles() {
    const filterToggles = [
        {
            toggle: 'characterFilterToggle',
            dropdown: 'characterFilter',
            checkboxes: 'characterCheckboxes'
        },
        {
            toggle: 'opponentFilterToggle',
            dropdown: 'opponentFilter',
            checkboxes: 'opponentCheckboxes'
        },
        {
            toggle: 'opponentCharFilterToggle',
            dropdown: 'opponentCharacterFilter',
            checkboxes: 'opponentCharCheckboxes'
        }
    ];
    
    filterToggles.forEach(config => {
        const toggle = document.getElementById(config.toggle);
        const dropdown = document.getElementById(config.dropdown);
        const checkboxes = document.getElementById(config.checkboxes);
        
        if (toggle && dropdown && checkboxes) {
            toggle.addEventListener('change', function() {
                dropdown.style.display = this.checked ? 'none' : 'block';
                checkboxes.style.display = this.checked ? 'block' : 'none';
            });
            
            // Initialize toggle state - start with checkboxes shown
            dropdown.style.display = 'none';
            checkboxes.style.display = 'block';
        }
    });
    
    // Setup filter collapse toggle icon
    const filterCollapse = document.getElementById('filterCollapse');
    const toggleIcon = document.getElementById('filterToggleIcon');
    
    if (filterCollapse && toggleIcon) {
        filterCollapse.addEventListener('hidden.bs.collapse', function() {
            toggleIcon.classList.add('bi-chevron-down');
            toggleIcon.classList.remove('bi-chevron-up');
        });
        
        filterCollapse.addEventListener('shown.bs.collapse', function() {
            toggleIcon.classList.add('bi-chevron-up');
            toggleIcon.classList.remove('bi-chevron-down');
        });
    }
}

function initializeEventListeners() {
    // Apply filters button
    const applyFiltersButton = document.getElementById('applyFilters');
    if (applyFiltersButton) {
        applyFiltersButton.addEventListener('click', function() {
            const characterFilter = document.getElementById('characterFilter');
            const opponentFilter = document.getElementById('opponentFilter');
            const opponentCharacterFilter = document.getElementById('opponentCharacterFilter');
            
            const filters = {};
            if (characterFilter) filters.character = characterFilter.value;
            if (opponentFilter) filters.opponent = opponentFilter.value;
            if (opponentCharacterFilter) filters.opponent_character = opponentCharacterFilter.value;
            
            fetchPlayerData(filters);
        });
    }
    
    // Reset filters button
    const resetFiltersButton = document.getElementById('resetFilters');
    if (resetFiltersButton) {
        resetFiltersButton.addEventListener('click', function() {
            // Reset dropdowns
            const characterFilter = document.getElementById('characterFilter');
            const opponentFilter = document.getElementById('opponentFilter');
            const opponentCharacterFilter = document.getElementById('opponentCharacterFilter');
            
            if (characterFilter) characterFilter.value = 'all';
            if (opponentFilter) opponentFilter.value = 'all';
            if (opponentCharacterFilter) opponentCharacterFilter.value = 'all';
            
            // Reset checkboxes - check all options
            document.querySelectorAll('.filter-checkboxes-horizontal input[type="checkbox"]').forEach(cb => {
                cb.checked = true;
            });
            
            // Reset select all checkboxes
            const selectAllIds = ['selectAllCharacters', 'selectAllOpponents', 'selectAllOpponentChars'];
            selectAllIds.forEach(id => {
                const selectAll = document.getElementById(id);
                if (selectAll) selectAll.checked = true;
            });
            
            fetchPlayerData();
        });
    }
}