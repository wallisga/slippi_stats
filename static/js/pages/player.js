// Player Page JavaScript

/**
 * Initialize character statistics chart
 */
function initializeCharacterStatsChart() {
    if (!window.PLAYER_DATA || !window.PLAYER_DATA.stats || !window.PLAYER_DATA.stats.character_stats) {
        return;
    }

    const ctx = document.getElementById('characterStatsChart');
    if (!ctx) return;

    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not available, skipping character chart');
        ctx.parentElement.innerHTML = '<div class="alert alert-info">Charts require Chart.js library</div>';
        return;
    }

    const characterStats = window.PLAYER_DATA.stats.character_stats;
    const characters = Object.keys(characterStats);
    const gamesData = characters.map(char => characterStats[char].games);
    const winRateData = characters.map(char => characterStats[char].win_rate * 100);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: characters,
            datasets: [
                {
                    label: 'Games Played',
                    data: gamesData,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Win Rate (%)',
                    data: winRateData,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Games Played'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    max: 100,
                    title: {
                        display: true,
                        text: 'Win Rate (%)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Initialize stage statistics chart
 */
function initializeStageStatsChart() {
    if (!window.PLAYER_DATA || !window.PLAYER_DATA.stats || !window.PLAYER_DATA.stats.stage_stats) {
        return;
    }

    const ctx = document.getElementById('stageStatsChart');
    if (!ctx) return;

    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not available, skipping stage chart');
        ctx.parentElement.innerHTML = '<div class="alert alert-info">Charts require Chart.js library</div>';
        return;
    }

    const stageStats = window.PLAYER_DATA.stats.stage_stats;
    const stageIds = Object.keys(stageStats);
    const winRateData = stageIds.map(stageId => stageStats[stageId].win_rate * 100);
    const gamesData = stageIds.map(stageId => stageStats[stageId].games);

    // Generate colors based on win rate
    const backgroundColors = winRateData.map(rate => {
        if (rate >= 60) return 'rgba(40, 167, 69, 0.6)'; // Green for good stages
        if (rate >= 40) return 'rgba(255, 193, 7, 0.6)'; // Yellow for neutral stages
        return 'rgba(220, 53, 69, 0.6)'; // Red for bad stages
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stageIds.map(id => `Stage ${id}`),
            datasets: [{
                label: 'Win Rate (%)',
                data: winRateData,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Win Rate (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const stageId = stageIds[context.dataIndex];
                            const games = gamesData[context.dataIndex];
                            return `Games played: ${games}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize load more games functionality
 */
function initializeLoadMoreGames() {
    const loadMoreButton = document.getElementById('loadMoreGames');
    if (!loadMoreButton) return;

    let currentPage = 1;
    const playerCode = loadMoreButton.getAttribute('data-player');

    loadMoreButton.addEventListener('click', function() {
        currentPage++;
        
        // Show loading state
        const originalText = loadMoreButton.innerHTML;
        loadMoreButton.innerHTML = '<i class="bi bi-arrow-clockwise spin me-2"></i>Loading...';
        loadMoreButton.disabled = true;

        // Make API request
        const encodedPlayerCode = encodeURIComponent(playerCode);
        const apiUrl = `/api/player/${encodedPlayerCode}/games?page=${currentPage}`;

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.games && data.games.length > 0) {
                    const tableBody = document.getElementById('recentGamesTable');
                    const fragment = document.createDocumentFragment();

                    data.games.forEach(game => {
                        const row = document.createElement('tr');
                        const opponentTagEncoded = encodeURIComponent(game.opponent.player_tag);
                        
                        row.innerHTML = `
                            <td class="game-time">${game.start_time}</td>
                            <td>
                                <span data-character-name="${game.player.character_name}" class="character-container"></span>
                                ${game.player.character_name}
                            </td>
                            <td>
                                <a href="/player/${opponentTagEncoded}" class="player-link">
                                    ${game.opponent.player_name}
                                </a>
                            </td>
                            <td>
                                <span data-character-name="${game.opponent.character_name}" class="character-container"></span>
                                ${game.opponent.character_name}
                            </td>
                            <td>
                                ${game.result === 'Win' 
                                    ? '<span class="badge bg-success"><i class="bi bi-trophy-fill me-1"></i>Win</span>' 
                                    : '<span class="badge bg-danger"><i class="bi bi-x-circle-fill me-1"></i>Loss</span>'}
                            </td>
                            <td class="game-duration">${(game.game_duration_seconds / 60).toFixed(1)}m</td>
                        `;
                        fragment.appendChild(row);
                    });

                    tableBody.appendChild(fragment);

                    // Initialize character icons for new rows
                    if (window.CharacterIcons) {
                        window.CharacterIcons.refresh(tableBody);
                    }

                    // Format new game times
                    formatGameTimes();

                    // Reset button state
                    loadMoreButton.disabled = false;
                    loadMoreButton.innerHTML = originalText;

                    // Check if we've reached the end
                    if (currentPage >= data.total_pages) {
                        loadMoreButton.disabled = true;
                        loadMoreButton.innerHTML = '<i class="bi bi-check-circle me-2"></i>All Games Loaded';
                        loadMoreButton.classList.remove('btn-primary');
                        loadMoreButton.classList.add('btn-success');
                    }
                } else {
                    // No more games
                    loadMoreButton.disabled = true;
                    loadMoreButton.innerHTML = '<i class="bi bi-check-circle me-2"></i>All Games Loaded';
                    loadMoreButton.classList.remove('btn-primary');
                    loadMoreButton.classList.add('btn-success');
                }
            })
            .catch(error => {
                console.error('Error loading more games:', error);
                loadMoreButton.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Error - Try Again';
                loadMoreButton.classList.remove('btn-primary');
                loadMoreButton.classList.add('btn-danger');
                loadMoreButton.disabled = false;
                
                // Reset page counter so user can try again
                currentPage--;
            });
    });
}

/**
 * Format game times to relative format
 */
function formatGameTimes() {
    const gameTimeElements = document.querySelectorAll('.game-time');
    
    gameTimeElements.forEach(element => {
        const originalTime = element.textContent;
        try {
            const date = new Date(originalTime);
            const now = new Date();
            const diffMs = now - date;
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            
            let relativeTime;
            if (diffMinutes < 60) {
                relativeTime = `${diffMinutes}m ago`;
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
            element.title = originalTime; // Keep original time in tooltip
        } catch (error) {
            console.warn('Could not parse date:', originalTime);
        }
    });
}

/**
 * Add CSS for spinning animation
 */
function addSpinAnimation() {
    if (document.querySelector('.spin-animation-style')) {
        return; // Already added
    }
    
    const style = document.createElement('style');
    style.className = 'spin-animation-style';
    style.textContent = `
        .spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Initialize page functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Add spin animation CSS
        addSpinAnimation();
        
        // Initialize charts if data is available
        if (window.PLAYER_DATA && window.PLAYER_DATA.hasCharts) {
            initializeCharacterStatsChart();
            initializeStageStatsChart();
        }
        
        // Initialize load more functionality
        initializeLoadMoreGames();
        
        // Format game times
        formatGameTimes();
        
        console.log('Player page initialized successfully');
    } catch (error) {
        console.error('Error initializing player page:', error);
    }
});