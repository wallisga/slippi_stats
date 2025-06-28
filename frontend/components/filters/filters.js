// Enhanced Advanced Filters Component JavaScript with Search Integration
// frontend/components/filters/filters.js

class AdvancedFilters {
    constructor() {
        this.onFilterChangeCallback = null;
        this.searchFilters = {
            character: '',
            opponent: '',
            opponent_character: ''
        };
        this.allOptions = {
            characters: [],
            opponents: [],
            opponent_characters: []
        };
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeFilters());
        } else {
            this.initializeFilters();
        }
    }
    
    initializeFilters() {
        this.setupFilterButtons();
        this.setupCollapseToggle();
        this.setupSearchInputs();
        
        console.log('Advanced filters component initialized with search integration');
    }
    
    setupFilterButtons() {
        // Apply filters button
        const applyButton = document.getElementById('applyFilters');
        if (applyButton) {
            applyButton.addEventListener('click', () => {
                const filters = this.getSelectedFilters();
                if (this.onFilterChangeCallback) {
                    this.onFilterChangeCallback(filters);
                }
            });
        }
        
        // Reset filters button
        const resetButton = document.getElementById('resetFilters');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                this.resetAllFilters();
                if (this.onFilterChangeCallback) {
                    this.onFilterChangeCallback({});
                }
            });
        }
    }
    
    setupCollapseToggle() {
        const filterCollapse = document.getElementById('filterCollapse');
        const toggleIcon = document.getElementById('filterToggleIcon');
        
        if (filterCollapse && toggleIcon) {
            filterCollapse.addEventListener('hidden.bs.collapse', () => {
                toggleIcon.className = 'bi bi-chevron-down';
            });
            
            filterCollapse.addEventListener('shown.bs.collapse', () => {
                toggleIcon.className = 'bi bi-chevron-up';
            });
        }
    }
    
    /**
     * NEW: Setup search inputs for filtering options
     */
    setupSearchInputs() {
        // Setup search for character filter
        this.setupSearchInput('characterSearch', 'characterCheckboxes', 'character');
        
        // Setup search for opponent filter
        this.setupSearchInput('opponentSearch', 'opponentCheckboxes', 'opponent');
        
        // Setup search for opponent character filter
        this.setupSearchInput('opponentCharSearch', 'opponentCharCheckboxes', 'opponent_character');
    }
    
    /**
     * NEW: Setup individual search input with debouncing
     */
    setupSearchInput(searchInputId, containerId, filterType) {
        const searchInput = document.getElementById(searchInputId);
        if (!searchInput) return;
        
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.searchFilters[filterType] = searchInput.value.toLowerCase().trim();
                this.filterVisibleOptions(containerId, filterType);
            }, 150);
        });
        
        // Escape key to clear
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                this.searchFilters[filterType] = '';
                this.filterVisibleOptions(containerId, filterType);
                searchInput.blur();
            }
        });
    }
    
    /**
     * NEW: Filter visible options based on search term
     */
    filterVisibleOptions(containerId, filterType) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const searchTerm = this.searchFilters[filterType];
        const checkboxItems = container.querySelectorAll('.checkbox-item:not(.select-all-option)');
        let visibleCount = 0;
        
        checkboxItems.forEach(item => {
            const label = item.querySelector('label');
            if (!label) return;
            
            const text = label.textContent.toLowerCase();
            const matches = !searchTerm || text.includes(searchTerm);
            
            if (matches) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Update search result count
        this.updateSearchResultCount(containerId, visibleCount);
        
        // Update select-all checkbox state
        const selectAllId = {
            'characterCheckboxes': 'selectAllCharacters',
            'opponentCheckboxes': 'selectAllOpponents',
            'opponentCharCheckboxes': 'selectAllOpponentChars'
        }[containerId];
        
        if (selectAllId) {
            this.updateSelectAllCheckbox(containerId, selectAllId);
        }
    }
    
    /**
     * NEW: Update search result count display
     */
    updateSearchResultCount(containerId, visibleCount) {
        const countElement = document.querySelector(`#${containerId} .search-result-count`);
        if (countElement) {
            const totalCount = this.allOptions[this.getOptionsKey(containerId)]?.length || 0;
            if (visibleCount < totalCount) {
                countElement.textContent = `Showing ${visibleCount} of ${totalCount}`;
                countElement.style.display = 'block';
            } else {
                countElement.style.display = 'none';
            }
        }
    }
    
    /**
     * NEW: Get options key for container ID
     */
    getOptionsKey(containerId) {
        const mapping = {
            'characterCheckboxes': 'characters',
            'opponentCheckboxes': 'opponents',
            'opponentCharCheckboxes': 'opponent_characters'
        };
        return mapping[containerId] || 'characters';
    }
    
    getSelectedFilters() {
        return {
            character: this.getSelectedCheckboxValues('characterCheckboxes'),
            opponent: this.getSelectedCheckboxValues('opponentCheckboxes'),
            opponent_character: this.getSelectedCheckboxValues('opponentCharCheckboxes')
        };
    }
    
    getSelectedCheckboxValues(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return 'all';
        
        // Only count visible checkboxes that are checked
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
        const visibleChecked = Array.from(checkboxes).filter(cb => {
            const item = cb.closest('.checkbox-item');
            return item && item.style.display !== 'none';
        });
        
        const selected = visibleChecked.map(cb => cb.value);
        return selected.length > 0 ? selected : 'all';
    }
    
    populateFilterOptions(filterOptions) {
        // Store all options for search filtering
        this.allOptions = {
            characters: filterOptions.characters || [],
            opponents: filterOptions.opponents || [],
            opponent_characters: filterOptions.opponent_characters || []
        };
        
        this.createCheckboxes('characterCheckboxes', filterOptions.characters, 'char', 'selectAllCharacters');
        this.createCheckboxes('opponentCheckboxes', filterOptions.opponents, 'opp', 'selectAllOpponents');
        this.createCheckboxes('opponentCharCheckboxes', filterOptions.opponent_characters, 'opp_char', 'selectAllOpponentChars');
    }
    
    createCheckboxes(containerId, items, namePrefix, selectAllId) {
        const container = document.getElementById(containerId);
        if (!container || !items || items.length === 0) return;
        
        // Keep the select-all option and search input
        const selectAllOption = container.querySelector('.select-all-option');
        const searchInput = container.querySelector('.filter-search-input');
        
        container.innerHTML = '';
        
        // Re-add select-all option
        if (selectAllOption) {
            container.appendChild(selectAllOption);
        }
        
        // Re-add search input
        if (searchInput) {
            container.appendChild(searchInput);
        }
        
        // Create checkboxes for each item
        items.forEach((item, index) => {
            const checkDiv = document.createElement('div');
            checkDiv.className = 'checkbox-item';
            
            const input = document.createElement('input');
            input.className = 'form-check-input';
            input.type = 'checkbox';
            input.id = `${namePrefix}_${index}`;
            input.value = item;
            input.checked = true;
            
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = input.id;
            label.textContent = item;
            
            checkDiv.appendChild(input);
            checkDiv.appendChild(label);
            container.appendChild(checkDiv);
            
            // Add change listener for select-all updates
            input.addEventListener('change', () => {
                this.updateSelectAllCheckbox(containerId, selectAllId);
            });
        });
        
        // Setup select-all functionality
        const selectAllCheckbox = document.getElementById(selectAllId);
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
                const visibleCheckboxes = Array.from(checkboxes).filter(cb => {
                    const item = cb.closest('.checkbox-item');
                    return item && item.style.display !== 'none';
                });
                
                visibleCheckboxes.forEach(cb => {
                    cb.checked = this.checked;
                });
            });
            
            // Initialize select-all state
            this.updateSelectAllCheckbox(containerId, selectAllId);
        }
        
        // Apply any existing search filter
        const filterType = this.getOptionsKey(containerId);
        if (this.searchFilters[filterType]) {
            this.filterVisibleOptions(containerId, filterType);
        }
    }
    
    updateSelectAllCheckbox(containerId, selectAllId) {
        const container = document.getElementById(containerId);
        const selectAll = document.getElementById(selectAllId);
        if (!container || !selectAll) return;
        
        // Only consider visible checkboxes
        const allCheckboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        const visibleCheckboxes = Array.from(allCheckboxes).filter(cb => {
            const item = cb.closest('.checkbox-item');
            return item && item.style.display !== 'none';
        });
        
        const checkedCount = visibleCheckboxes.filter(cb => cb.checked).length;
        
        if (visibleCheckboxes.length === 0) return;
        
        selectAll.checked = checkedCount === visibleCheckboxes.length;
        selectAll.indeterminate = checkedCount > 0 && checkedCount < visibleCheckboxes.length;
    }
    
    resetAllFilters() {
        // Clear all search inputs
        Object.keys(this.searchFilters).forEach(key => {
            this.searchFilters[key] = '';
        });
        
        // Clear search input fields
        ['characterSearch', 'opponentSearch', 'opponentCharSearch'].forEach(id => {
            const input = document.getElementById(id);
            if (input) input.value = '';
        });
        
        // Show all checkboxes and check them
        document.querySelectorAll('.filter-checkboxes-horizontal input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
            const item = cb.closest('.checkbox-item');
            if (item) item.style.display = '';
        });
        
        // Hide search result counts
        document.querySelectorAll('.search-result-count').forEach(count => {
            count.style.display = 'none';
        });
    }
    
    restoreCheckboxSelections(containerId, selectedValues) {
        const container = document.getElementById(containerId);
        if (!container || !Array.isArray(selectedValues)) return;
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        checkboxes.forEach(cb => {
            cb.checked = selectedValues.includes(cb.value);
        });
        
        // Update select-all state
        const selectAllId = {
            'characterCheckboxes': 'selectAllCharacters',
            'opponentCheckboxes': 'selectAllOpponents',
            'opponentCharCheckboxes': 'selectAllOpponentChars'
        }[containerId];
        
        if (selectAllId) {
            this.updateSelectAllCheckbox(containerId, selectAllId);
        }
    }
    
    /**
     * NEW: Clear search for specific filter type
     */
    clearSearch(filterType) {
        const searchInputs = {
            'character': 'characterSearch',
            'opponent': 'opponentSearch',
            'opponent_character': 'opponentCharSearch'
        };
        
        const inputId = searchInputs[filterType];
        if (inputId) {
            const input = document.getElementById(inputId);
            if (input) {
                input.value = '';
                this.searchFilters[filterType] = '';
                
                const containerIds = {
                    'character': 'characterCheckboxes',
                    'opponent': 'opponentCheckboxes',
                    'opponent_character': 'opponentCharCheckboxes'
                };
                
                const containerId = containerIds[filterType];
                if (containerId) {
                    this.filterVisibleOptions(containerId, filterType);
                }
            }
        }
    }
    
    // Public API
    onFilterChange(callback) {
        this.onFilterChangeCallback = callback;
    }
}

// Auto-initialize and make available globally
const advancedFilters = new AdvancedFilters();
window.AdvancedFilters = AdvancedFilters;
window.advancedFilters = advancedFilters;