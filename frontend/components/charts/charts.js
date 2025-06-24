// Charts Component JavaScript - AUTO-INITIALIZATION
class ChartsComponent {
    static charts = {}; // Track chart instances
    
    static createTimeChart(canvasId, data) {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            this.showChartError(canvasId, 'Chart.js library not available');
            return null;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }
        
        try {
            // Destroy existing chart
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
            }
            
            const ctx = canvas.getContext('2d');
            const dates = Object.keys(data);
            const winRates = dates.map(date => data[date].win_rate * 100);
            const gamesCounts = dates.map(date => data[date].games);
            
            // Create new chart
            this.charts[canvasId] = new Chart(ctx, {
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
            
            return this.charts[canvasId];
        } catch (error) {
            console.error('Error creating time chart:', error);
            this.showChartError(canvasId, 'Failed to create chart');
            return null;
        }
    }
    
    static createCharacterChart(canvasId, characterStats) {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            this.showChartError(canvasId, 'Chart.js library not available');
            return null;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return null;
        }
        
        try {
            // Destroy existing chart
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
            }
            
            const ctx = canvas.getContext('2d');
            
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
            
            this.charts[canvasId] = new Chart(ctx, {
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
            
            return this.charts[canvasId];
        } catch (error) {
            console.error('Error creating character chart:', error);
            this.showChartError(canvasId, 'Failed to create chart');
            return null;
        }
    }
    
    static updateTimeChart(canvasId, data) {
        if (!data || Object.keys(data).length === 0) {
            this.showChartError(canvasId, 'No data available for time chart');
            return;
        }
        
        const chart = this.charts[canvasId];
        if (chart) {
            // Update existing chart
            const dates = Object.keys(data);
            const winRates = dates.map(date => data[date].win_rate * 100);
            const gamesCounts = dates.map(date => data[date].games);
            
            chart.data.labels = dates;
            chart.data.datasets[0].data = winRates;
            chart.data.datasets[1].data = gamesCounts;
            chart.update();
        } else {
            // Create new chart
            this.createTimeChart(canvasId, data);
        }
    }
    
    static updateCharacterChart(canvasId, characterStats) {
        if (!characterStats || Object.keys(characterStats).length === 0) {
            this.showChartError(canvasId, 'No data available for character chart');
            return;
        }
        
        const chart = this.charts[canvasId];
        if (chart) {
            chart.destroy();
        }
        // Always recreate character chart due to dynamic data structure
        this.createCharacterChart(canvasId, characterStats);
    }
    
    static showChartError(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const container = canvas.parentNode;
        if (container) {
            container.innerHTML = `
                <div class="chart-error">
                    <i class="bi bi-exclamation-triangle"></i>
                    <span>${message}</span>
                </div>
            `;
        }
    }
    
    static showChartLoading(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const container = canvas.parentNode;
        if (container) {
            container.innerHTML = `
                <div class="chart-loading">
                    <div class="spinner-border me-2" role="status"></div>
                    <span>Loading chart...</span>
                </div>
            `;
        }
    }
    
    static destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }
    
    static destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

// ✅ AUTO-INITIALIZE
console.log('Charts component initialized');

// ✅ EXPORT
window.ChartsComponent = ChartsComponent;