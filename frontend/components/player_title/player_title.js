// Player Title Component JavaScript

class PlayerTitle {
    constructor(playerCode, encodedPlayerCode, options = {}) {
        this.playerCode = playerCode;
        this.encodedPlayerCode = encodedPlayerCode;
        this.options = {
            currentPage: 'overview',
            stats: null,
            characterList: [],
            recentGames: [],
            showQuickStats: true,
            showCharacterDropdown: true,
            showActions: true,
            ...options
        };
        
        this.lastPlayedInfo = null;
        this.init();
    }
    
    init() {
        this.calculateLastPlayed();
        this.createTitle();
        this.setupEventListeners();
        this.startLastPlayedUpdates();
    }
    
    calculateLastPlayed() {
        console.log('Calculating last played with recent games:', this.options.recentGames);
        
        if (!this.options.recentGames || this.options.recentGames.length === 0) {
            console.log('No recent games available');
            this.lastPlayedInfo = {
                status: 'unknown',
                text: 'No recent games',
                icon: 'bi-question-circle'
            };
            return;
        }
        
        // Get the most recent game
        const lastGame = this.options.recentGames[0];
        console.log('Most recent game:', lastGame);
        
        if (!lastGame || !lastGame.start_time) {
            console.log('Most recent game has no start_time');
            this.lastPlayedInfo = {
                status: 'unknown',
                text: 'Invalid game data',
                icon: 'bi-question-circle'
            };
            return;
        }
        
        // Parse the date - handle different formats
        let lastPlayedDate;
        try {
            // Handle ISO format or other date formats
            lastPlayedDate = new Date(lastGame.start_time);
            
            // Check if date is valid
            if (isNaN(lastPlayedDate.getTime())) {
                console.error('Invalid date format:', lastGame.start_time);
                this.lastPlayedInfo = {
                    status: 'unknown',
                    text: 'Invalid date format',
                    icon: 'bi-question-circle'
                };
                return;
            }
        } catch (error) {
            console.error('Error parsing date:', lastGame.start_time, error);
            this.lastPlayedInfo = {
                status: 'unknown',
                text: 'Date parsing error',
                icon: 'bi-question-circle'
            };
            return;
        }
        
        const now = new Date();
        const diffMs = now - lastPlayedDate;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        
        console.log(`Time difference: ${diffDays} days, ${diffHours} hours, ${diffMinutes} minutes`);
        console.log(`Last played date: ${lastPlayedDate}, Now: ${now}`);
        
        let status, text, icon;
        
        // Handle edge case: game from the future (clock skew or bad data)
        if (diffMs < 0) {
            console.warn('Game date is in the future:', lastGame.start_time);
            status = 'recent';
            text = 'Just now';
            icon = 'bi-clock-fill';
        } else if (diffMinutes < 60) {
            status = 'recent';
            text = diffMinutes <= 1 ? 'Just now' : `${diffMinutes} minutes ago`;
            icon = 'bi-clock-fill';
        } else if (diffHours < 24) {
            status = 'recent';
            text = diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
            icon = 'bi-clock';
        } else if (diffDays === 1) {
            status = 'recent';
            text = 'Yesterday';
            icon = 'bi-calendar-day';
        } else if (diffDays <= 3) {
            status = 'stale';
            text = `${diffDays} days ago`;
            icon = 'bi-calendar-week';
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            status = 'inactive';
            text = weeks === 1 ? '1 week ago' : `${weeks} weeks ago`;
            icon = 'bi-calendar-month';
        } else {
            const months = Math.floor(diffDays / 30);
            status = 'inactive';
            text = months === 1 ? '1 month ago' : `${months} months ago`;
            icon = 'bi-calendar-x';
        }
        
        console.log(`Calculated last played: ${text} (status: ${status})`);
        
        this.lastPlayedInfo = { status, text, icon };
    }
    
    createTitle() {
        const container = document.getElementById('player-title-container');
        if (!container) {
            console.error('Player title container not found');
            return;
        }
        
        container.innerHTML = this.generateTitleHTML();
    }
    
    generateTitleHTML() {
        return `
            <div class="player-title-section">
                <div class="d-flex justify-content-between align-items-start flex-wrap">
                    <div class="player-title-main">
                        <h1 class="player-main-title">
                            <span class="player-code">${this.playerCode}</span>
                            ${this.generatePlayerStatusBadge()}
                        </h1>
                        
                        <div class="player-subtitle">
                            ${this.generateSubtitleItems()}
                        </div>
                    </div>
                </div>
                
                ${this.options.showQuickStats && this.options.stats ? 
                    this.generateQuickStatsHTML() : ''}
                
                ${this.generateTabsHTML()}
            </div>
        `;
    }
    
    generatePlayerStatusBadge() {
        if (!this.lastPlayedInfo) return '';
        
        const statusClass = this.lastPlayedInfo.status === 'recent' ? 'online' : 'offline';
        const statusText = this.lastPlayedInfo.status === 'recent' ? 'Active' : 'Inactive';
        
        return `<span class="player-status ${statusClass}">${statusText}</span>`;
    }
    
    generateSubtitleItems() {
        const items = [];
        
        // Total games
        if (this.options.stats && this.options.stats.total_games) {
            items.push(`
                <div class="subtitle-item">
                    <i class="bi bi-controller"></i>
                    <span>${this.options.stats.total_games} games played</span>
                </div>
            `);
        }
        
        // Main character
        if (this.options.stats && this.options.stats.most_played_character) {
            items.push(`
                <div class="subtitle-item">
                    <i class="bi bi-person-circle"></i>
                    <span>Mains 
                        <span data-character-name="${this.options.stats.most_played_character}" class="character-container me-1"></span>
                        ${this.options.stats.most_played_character}
                    </span>
                </div>
            `);
        }
        
        // Last played
        if (this.lastPlayedInfo) {
            items.push(`
                <div class="subtitle-item">
                    <div class="last-played-info ${this.lastPlayedInfo.status}">
                        <i class="${this.lastPlayedInfo.icon}"></i>
                        <span>Last played ${this.lastPlayedInfo.text}</span>
                    </div>
                </div>
            `);
        }
        
        return items.join('');
    }
    
    generateQuickStatsHTML() {
        if (!this.options.stats) return '';
        
        const winRate = (this.options.stats.win_rate * 100).toFixed(1);
        const losses = this.options.stats.total_games - this.options.stats.wins;
        
        return `
            <div class="player-quick-stats">
                <div class="quick-stat-item">
                    <span class="quick-stat-value">${winRate}%</span>
                    <span class="quick-stat-label">Win Rate</span>
                </div>
                <div class="quick-stat-item">
                    <span class="quick-stat-value">${this.options.stats.wins}</span>
                    <span class="quick-stat-label">Wins</span>
                </div>
                <div class="quick-stat-item">
                    <span class="quick-stat-value">${losses}</span>
                    <span class="quick-stat-label">Losses</span>
                </div>
                <div class="quick-stat-item">
                    <span class="quick-stat-value">${Object.keys(this.options.stats.character_stats || {}).length}</span>
                    <span class="quick-stat-label">Characters</span>
                </div>
            </div>
        `;
    }
    
    generateCharacterDropdownHTML() {
        // Character stats functionality removed - return empty string
        return '';
    }
    
    generateTabsHTML() {
        // FIXED: Always encode the player code client-side instead of trusting server-provided encoding
        const safeEncodedCode = encodeURIComponent(this.playerCode);
        
        const tabs = [
            { key: 'overview', label: 'Overview', href: `/player/${safeEncodedCode}` },
            { key: 'detailed', label: 'Detailed Stats', href: `/player/${safeEncodedCode}/detailed` }
        ];
        
        return `
            <div class="player-tabs-container">
                <nav class="player-tabs">
                    <ul class="nav nav-tabs">
                        ${tabs.map(tab => `
                            <li class="nav-item">
                                <a class="nav-link ${this.options.currentPage === tab.key ? 'active' : ''}" 
                                   href="${tab.href}">
                                    ${tab.label}
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                </nav>
            </div>
        `;
    }
    
    setupEventListeners() {
        // Tab navigation only (character dropdown removed)
        document.querySelectorAll('.player-tabs .nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                if (!this.classList.contains('active')) {
                    const originalText = this.textContent.trim();
                    this.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>' + originalText;
                }
            });
        });
    }
    
    startLastPlayedUpdates() {
        // Update last played info every minute
        setInterval(() => {
            this.calculateLastPlayed();
            this.updateLastPlayedDisplay();
        }, 60000);
    }
    
    updateLastPlayedDisplay() {
        const lastPlayedElement = document.querySelector('.last-played-info');
        if (lastPlayedElement && this.lastPlayedInfo) {
            lastPlayedElement.className = `last-played-info ${this.lastPlayedInfo.status}`;
            lastPlayedElement.innerHTML = `
                <i class="${this.lastPlayedInfo.icon}"></i>
                <span>Last played ${this.lastPlayedInfo.text}</span>
            `;
        }
        
        // Update status badge
        const statusBadge = document.querySelector('.player-status');
        if (statusBadge && this.lastPlayedInfo) {
            const statusClass = this.lastPlayedInfo.status === 'recent' ? 'online' : 'offline';
            const statusText = this.lastPlayedInfo.status === 'recent' ? 'Active' : 'Inactive';
            statusBadge.className = `player-status ${statusClass}`;
            statusBadge.textContent = statusText;
        }
    }
    
    updateStats(newStats) {
        this.options.stats = newStats;
        const quickStatsContainer = document.querySelector('.player-quick-stats');
        if (quickStatsContainer) {
            quickStatsContainer.outerHTML = this.generateQuickStatsHTML();
        }
    }
    
    updateRecentGames(newGames) {
        this.options.recentGames = newGames;
        this.calculateLastPlayed();
        this.updateLastPlayedDisplay();
    }
}

// Export for use in other files
window.PlayerTitle = PlayerTitle;