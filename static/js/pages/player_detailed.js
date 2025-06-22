// Player Detailed Page JavaScript

// Global variables
let timeChart = null;
let characterChart = null;
let playerData = null;

// Character icon handling
function initializeCharacterIcons(container = document) {
    // Define the character mapping based on the config
    const characterMapping = {
        "Mario": "Mario",
        "Fox": "Fox",
        "Captain Falcon": "Captain Falcon",
        "Donkey Kong": "Donkey Kong",
        "Kirby": "Kirby",
        "Bowser": "Bowser",
        "Link": "Link",
        "Sheik": "Sheik", 
        "Ness": "Ness",
        "Peach": "Peach",
        "Ice Climbers": "Ice Climbers",
        "Yoshi": "Yoshi",
        "Pikachu": "Pikachu",
        "Samus": "Samus",
        "Jigglypuff": "Jigglypuff",
        "Mewtwo": "Mewtwo",
        "Luigi": "Luigi",
        "Marth": "Marth",
        "Zelda": "Zelda",
        "Young Link": "Young Link",
        "Doctor Mario": "Doctor Mario",
        "Dr. Mario": "Doctor Mario",
        "Falco": "Falco",
        "Pichu": "Pichu",
        "Game & Watch": "Game & Watch",
        "Mr. Game & Watch": "Game & Watch",
        "Ganondorf": "Ganondorf",
        "Roy": "Roy"
    };

    // Only select elements that haven't been processed yet
    container.querySelectorAll('[data-character-name]:not([data-icon-processed])').forEach(function(element) {
        // Mark as processed to avoid duplicate icons
        element.setAttribute('data-icon-processed', 'true');
        
        const characterName = element.getAttribute('data-character-name');
        if (characterName && characterMapping[characterName]) {
            // Create the image element
            const img = document.createElement('img');
            img.src = `/static/icons/character/neutral ${characterMapping[characterName]}.png`;
            img.alt = characterName;
            img.width = 24;
            img.height = 24;
            img.className = 'character-icon';
            
            // Add error handling
            img.onerror = function() {
                // If image fails to load, replace with character initial
                this.style.display = 'none';
                const span = document.createElement('span');
                span.className = 'character-icon-fallback';
                span.textContent = characterName.charAt(0);
                // Add the character as data attribute for styling
                span.setAttribute('data-character', characterName.toLowerCase().replace(/ /g, '_'));
                this.parentNode.insertBefore(span, this.nextSibling);
            };
            
            // Add to the DOM
            element.appendChild(img);
        } else {
            // Fallback for unknown characters
            const span = document.createElement('span');
            span.className = 'character-icon-fallback';
            span.textContent = characterName ? characterName.charAt(0) : '?';
            if (characterName) {
                span.setAttribute('data-character', characterName.toLowerCase().replace(/ /g, '_'));
            }
            element.appendChild(span);
        }
    });
}

// Helper function to show loading overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.visibility = 'visible';
        overlay.style.opacity = 1;
    }
}

// Helper function to hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.opacity = 0;
        setTimeout(() => {
            overlay.style.visibility = 'hidden';
        }, 200);
    }
}

// Get selected values from filter checkboxes
function getSelectedCheckboxValues(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Updated fetchPlayerData function to use POST for complex filters
async function fetchPlayerData(filters = {}) {
    showLoading();
    
    try {
        // Get player code from URL or template variable
        const playerCode = window.location.pathname.split('/')[2]; // Extract from URL path
        const encodedPlayerCode = encodeURIComponent(playerCode);
        
        // Save current checkbox selections before making the request
        const savedSelections = {};
        
        if (document.getElementById('characterFilterToggle') && document.getElementById('characterFilterToggle').checked) {
            savedSelections.characters = getSelectedCheckboxValues('characterCheckboxes');
        }
        
        if (document.getElementById('opponentFilterToggle') && document.getElementById('opponentFilterToggle').checked) {
            savedSelections.opponents = getSelectedCheckboxValues('opponentCheckboxes');
        }
        
        if (document.getElementById('opponentCharFilterToggle') && document.getElementById('opponentCharFilterToggle').checked) {
            savedSelections.opponentChars = getSelectedCheckboxValues('opponentCharCheckboxes');
        }
        
        // Prepare filter data for POST request
        const filterData = {};
        
        // Handle checkbox or dropdown filters based on toggle state
        if (document.getElementById('characterFilterToggle') && document.getElementById('characterFilterToggle').checked) {
            // Using checkboxes - send as array
            const selectedChars = savedSelections.characters;
            if (selectedChars && selectedChars.length > 0 && selectedChars.length < playerData?.filter_options.characters.length) {
                filterData.character = selectedChars; // Send as array instead of pipe-separated string
            } else {
                filterData.character = 'all';
            }
        } else if (filters.character && filters.character !== 'all') {
            filterData.character = filters.character;
        } else {
            filterData.character = 'all';
        }
        
        if (document.getElementById('opponentFilterToggle') && document.getElementById('opponentFilterToggle').checked) {
            // Using checkboxes - send as array
            const selectedOpponents = savedSelections.opponents;
            if (selectedOpponents && selectedOpponents.length > 0 && selectedOpponents.length < playerData?.filter_options.opponents.length) {
                filterData.opponent = selectedOpponents; // Send as array
            } else {
                filterData.opponent = 'all';
            }
        } else if (filters.opponent && filters.opponent !== 'all') {
            filterData.opponent = filters.opponent;
        } else {
            filterData.opponent = 'all';
        }
        
        if (document.getElementById('opponentCharFilterToggle') && document.getElementById('opponentCharFilterToggle').checked) {
            // Using checkboxes - send as array
            const selectedOpponentChars = savedSelections.opponentChars;
            if (selectedOpponentChars && selectedOpponentChars.length > 0 && selectedOpponentChars.length < playerData?.filter_options.opponent_characters.length) {
                filterData.opponent_character = selectedOpponentChars; // Send as array
            } else {
                filterData.opponent_character = 'all';
            }
        } else if (filters.opponent_character && filters.opponent_character !== 'all') {
            filterData.opponent_character = filters.opponent_character;
        } else {
            filterData.opponent_character = 'all';
        }
        
        const apiUrl = `/api/player/${encodedPlayerCode}/detailed`;
        
        console.log("POSTing filter data:", filterData);
        
        // Use POST instead of GET to avoid URL length limits
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
        console.log("Received data:", data);
        
        playerData = data;
        
        // First populate filters with new data
        populateFilters(data);
        
        // Then restore saved selections
        if (savedSelections.characters) {
            restoreCheckboxSelections('characterCheckboxes', savedSelections.characters);
        }
        
        if (savedSelections.opponents) {
            restoreCheckboxSelections('opponentCheckboxes', savedSelections.opponents);
        }
        
        if (savedSelections.opponentChars) {
            restoreCheckboxSelections('opponentCharCheckboxes', savedSelections.opponentChars);
        }
        
        // Update UI with new data
        updateUI(data);
        
        hideLoading();
        return data;
    } catch (error) {
        console.error("Error fetching player data:", error);
        hideLoading();
        alert("Error loading player data. Please try again.");
        throw error;
    }
}

// Add this helper function to restore checkbox selections
function restoreCheckboxSelections(containerId, selectedValues) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
    
    // First uncheck all checkboxes
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    
    // Now check only the ones that were selected before
    checkboxes.forEach(cb => {
        if (selectedValues.includes(cb.value)) {
            cb.checked = true;
        }
    });
    
    // Update the "Select All" checkbox state
    updateSelectAllCheckbox(containerId, 
        containerId === 'characterCheckboxes' ? 'selectAllCharacters' : 
        containerId === 'opponentCheckboxes' ? 'selectAllOpponents' : 
        'selectAllOpponentChars');
}

// Create checkbox filters
function createCheckboxes(containerId, items, namePrefix, selectAllId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear existing checkboxes except "Select All"
    const allOption = container.querySelector('.select-all-option');
    if (allOption) {
        container.innerHTML = '';
        container.appendChild(allOption);
    }
    
    // Add individual checkboxes
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
        
        // Add event listener to update "Select All" checkbox
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
    
    // Set up select all functionality
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

// Update the "Select All" checkbox based on individual checkbox states
function updateSelectAllCheckbox(containerId, selectAllId) {
    const container = document.getElementById(containerId);
    const selectAll = document.getElementById(selectAllId);
    if (!container || !selectAll) return;
    
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
    const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
    
    selectAll.checked = checkedCount === checkboxes.length;
    selectAll.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
}

// Populate filter dropdowns
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
    
    // Restore previous selections if they exist in the new options
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
    
    // Apply the filters from the API response
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

// Update UI with player data
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
    
    // Update character stats table - SORTED BY GAMES PLAYED
    const characterStatsTable = document.getElementById('character-stats-table');
    const characterCount = document.getElementById('character-count');
    
    if (characterStatsTable) {
        characterStatsTable.innerHTML = '';
        
        let count = 0;
        
        // Convert object to array and sort by games played
        const sortedCharStats = Object.entries(data.character_stats)
            .filter(([_, stats]) => stats.games > 0)
            .sort((a, b) => b[1].games - a[1].games);
        
        for (const [character, stats] of sortedCharStats) {
            count++;
            
            const row = document.createElement('tr');
            const winRateClass = stats.win_rate >= 0.6 ? 'text-success' : 
                                stats.win_rate >= 0.4 ? 'text-warning' :
                                'text-danger';
            
            row.innerHTML = `
                <td>
                    <span data-character-name="${character}" class="character-container"></span>
                    ${character}
                </td>
                <td>${stats.games}</td>
                <td class="${winRateClass} fw-bold">${(stats.win_rate * 100).toFixed(1)}%</td>
            `;
            
            characterStatsTable.appendChild(row);
        }
        
        if (characterCount) characterCount.textContent = count;
    }
    
    // Update opponent stats table - SORTED BY GAMES PLAYED
    const opponentStatsTable = document.getElementById('opponent-stats-table');
    const opponentCount = document.getElementById('opponent-count');
    
    if (opponentStatsTable) {
        opponentStatsTable.innerHTML = '';
        
        let count = 0;
        
        // Convert object to array and sort by games played
        const sortedOppStats = Object.entries(data.opponent_stats)
            .filter(([_, stats]) => stats.games > 0)
            .sort((a, b) => b[1].games - a[1].games);
        
        for (const [opponent, stats] of sortedOppStats) {
            count++;
            
            const row = document.createElement('tr');
            const winRateClass = stats.win_rate >= 0.6 ? 'text-success' : 
                                stats.win_rate >= 0.4 ? 'text-warning' :
                                'text-danger';
            
            row.innerHTML = `
                <td>${opponent}</td>
                <td>${stats.games}</td>
                <td class="${winRateClass} fw-bold">${(stats.win_rate * 100).toFixed(1)}%</td>
            `;
            
            opponentStatsTable.appendChild(row);
        }
        
        if (opponentCount) opponentCount.textContent = count;
    }
    
    // Update matchup stats table - SORTED BY GAMES PLAYED
    const matchupStatsTable = document.getElementById('matchup-stats-table');
    const matchupCount = document.getElementById('matchup-count');
    
    if (matchupStatsTable) {
        matchupStatsTable.innerHTML = '';
        
        let count = 0;
        
        // Convert object to array and sort by games played
        const sortedMatchupStats = Object.entries(data.opponent_character_stats)
            .filter(([_, stats]) => stats.games > 0)
            .sort((a, b) => b[1].games - a[1].games);
        
        for (const [character, stats] of sortedMatchupStats) {
            count++;
            
            const row = document.createElement('tr');
            const winRateClass = stats.win_rate >= 0.6 ? 'text-success' : 
                                stats.win_rate >= 0.4 ? 'text-warning' :
                                'text-danger';
            
            row.innerHTML = `
                <td>
                    <span data-character-name="${character}" class="character-container"></span>
                    ${character}
                </td>
                <td>${stats.games}</td>
                <td class="${winRateClass} fw-bold">${(stats.win_rate * 100).toFixed(1)}%</td>
            `;
            
            matchupStatsTable.appendChild(row);
        }
        
        if (matchupCount) matchupCount.textContent = count;
    }
    
    // Update time chart - WITH ERROR HANDLING
    if (data.date_stats && Object.keys(data.date_stats).length > 0) {
        try {
            updateTimeChart(data.date_stats);
        } catch (error) {
            console.error("Error updating time chart:", error);
            // Handle error gracefully - maybe display a message in the chart area
            const timeChartContainer = document.querySelector('#timeChart').parentNode;
            if (timeChartContainer) {
                timeChartContainer.innerHTML = '<div class="alert alert-warning">Unable to load chart. Charts require Chart.js library.</div>';
            }
        }
    }
    
    // Update character chart - WITH ERROR HANDLING
    if (data.character_stats && Object.keys(data.character_stats).length > 0) {
        try {
            updateCharacterChart(data.character_stats);
        } catch (error) {
            console.error("Error updating character chart:", error);
            // Handle error gracefully
            const characterChartContainer = document.querySelector('#characterChart').parentNode;
            if (characterChartContainer) {
                characterChartContainer.innerHTML = '<div class="alert alert-warning">Unable to load chart. Charts require Chart.js library.</div>';
            }
        }
    }
    
    // Initialize character icons
    initializeCharacterIcons();
}

// Update the win rate over time chart with error handling
function updateTimeChart(dateStats) {
    // Check if Chart is defined
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
    
    // Extract dates and win rates
    const dates = Object.keys(dateStats);
    const winRates = dates.map(date => dateStats[date].win_rate * 100);
    const gamesCounts = dates.map(date => dateStats[date].games);
    
    // If a chart already exists, destroy it
    if (timeChart) {
        timeChart.destroy();
    }
    
    // Create new chart
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

// Update the character performance chart with increased spacing - WITH ERROR HANDLING
function updateCharacterChart(characterStats) {
    // Check if Chart is defined
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
    
    // Filter to only include characters with games
    const filteredStats = Object.entries(characterStats)
        .filter(([_, stats]) => stats.games > 0)
        .sort((a, b) => b[1].games - a[1].games); // Sort by games played
    
    const characters = filteredStats.map(([char, _]) => char);
    const winRates = filteredStats.map(([_, stats]) => stats.win_rate * 100);
    const gamesCounts = filteredStats.map(([_, stats]) => stats.games);
    
    // Generate colors based on win rate
    const backgroundColors = winRates.map(rate => {
        if (rate >= 60) return 'rgba(40, 167, 69, 0.6)'; // Green
        if (rate >= 40) return 'rgba(255, 193, 7, 0.6)'; // Yellow
        return 'rgba(220, 53, 69, 0.6)'; // Red
    });
    
    // If a chart already exists, destroy it
    if (characterChart) {
        characterChart.destroy();
    }
    
    // Create new chart
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
                        padding: 15 // Increase padding between ticks for better spacing
                    },
                    afterFit: function(scaleInstance) {
                        // Increase the width of the y-axis to give more room for character names
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
            // Add more spacing between bars
            barPercentage: 0.8,
            categoryPercentage: 0.7
        }
    });
}

// Toggle between dropdown and checkbox filters
function setupFilterToggles() {
    const characterFilterToggle = document.getElementById('characterFilterToggle');
    const characterFilter = document.getElementById('characterFilter');
    const characterCheckboxes = document.getElementById('characterCheckboxes');
    
    const opponentFilterToggle = document.getElementById('opponentFilterToggle');
    const opponentFilter = document.getElementById('opponentFilter');
    const opponentCheckboxes = document.getElementById('opponentCheckboxes');
    
    const opponentCharFilterToggle = document.getElementById('opponentCharFilterToggle');
    const opponentCharacterFilter = document.getElementById('opponentCharacterFilter');
    const opponentCharCheckboxes = document.getElementById('opponentCharCheckboxes');
    
    if (characterFilterToggle && characterFilter && characterCheckboxes) {
        characterFilterToggle.addEventListener('change', function() {
            characterFilter.style.display = this.checked ? 'none' : 'block';
            characterCheckboxes.style.display = this.checked ? 'block' : 'none';
        });
        
        // Initialize toggle state
        characterFilter.style.display = 'none';
        characterCheckboxes.style.display = 'block';
    }
    
    if (opponentFilterToggle && opponentFilter && opponentCheckboxes) {
        opponentFilterToggle.addEventListener('change', function() {
            opponentFilter.style.display = this.checked ? 'none' : 'block';
            opponentCheckboxes.style.display = this.checked ? 'block' : 'none';
        });
        
        // Initialize toggle state
        opponentFilter.style.display = 'none';
        opponentCheckboxes.style.display = 'block';
    }
    
    if (opponentCharFilterToggle && opponentCharacterFilter && opponentCharCheckboxes) {
        opponentCharFilterToggle.addEventListener('change', function() {
            opponentCharacterFilter.style.display = this.checked ? 'none' : 'block';
            opponentCharCheckboxes.style.display = this.checked ? 'block' : 'none';
        });
        
        // Initialize toggle state
        opponentCharacterFilter.style.display = 'none';
        opponentCharCheckboxes.style.display = 'block';
    }
}

// Event listeners - with error handling
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Setup filter toggles
        setupFilterToggles();
        
        // Initial data load
        fetchPlayerData();
        
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
                document.querySelectorAll('.filter-checkboxes input[type="checkbox"]').forEach(cb => {
                    cb.checked = true;
                });
                
                // Reset select all checkboxes
                const selectAllChars = document.getElementById('selectAllCharacters');
                const selectAllOpps = document.getElementById('selectAllOpponents');
                const selectAllOppChars = document.getElementById('selectAllOpponentChars');
                
                if (selectAllChars) selectAllChars.checked = true;
                if (selectAllOpps) selectAllOpps.checked = true;
                if (selectAllOppChars) selectAllOppChars.checked = true;
                
                fetchPlayerData();
            });
        }
    } catch (e) {
        console.error("Error in DOM ready handler:", e);
    }
});