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
     * Setup search inputs for filtering options
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
     * Setup individual search input with debouncing
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
     * Filter visible options based on search term
     */
    filterVisibleOptions(containerId, filterType) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const searchTerm = this.searchFilters[filterType];
        const checkboxItems = container.querySelectorAll('.checkbox-item:not(.select-all-option)');
        let visibleCount = 0;
        let hiddenSelectedCount = 0;
        
        checkboxItems.forEach(item => {
            const label = item.querySelector('label');
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (!label) return;
            
            const text = label.textContent.toLowerCase();
            const matches = !searchTerm || text.includes(searchTerm);
            
            if (matches) {
                item.style.display = '';
                item.classList.remove('searched-hidden');
                visibleCount++;
            } else {
                item.style.display = 'none';
                item.classList.add('searched-hidden');
                
                // Count selected items that are hidden by search
                if (checkbox && checkbox.checked) {
                    hiddenSelectedCount++;
                }
            }
        });
        
        // Update search result count
        this.updateSearchResultCount(containerId, visibleCount);
        
        // Show indicator for hidden selected items
        this.updateHiddenSelectedIndicator(container, hiddenSelectedCount);
        
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
     * Show indicator when selected items are hidden by search
     */
    updateHiddenSelectedIndicator(container, hiddenSelectedCount) {
        if (hiddenSelectedCount > 0) {
            container.setAttribute('data-hidden-selected', hiddenSelectedCount);
        } else {
            container.removeAttribute('data-hidden-selected');
        }
    }
    
    /**
     * Update search result count display with selection info
     */
    updateSearchResultCount(containerId, visibleCount) {
        const countElement = document.querySelector(`#${containerId} .search-result-count`);
        if (countElement) {
            const totalCount = this.allOptions[this.getOptionsKey(containerId)]?.length || 0;
            
            // Also show how many are actually selected
            const selectedCount = document.querySelectorAll(`#${containerId} input[type="checkbox"]:not(.select-all):checked`).length;
            
            if (visibleCount < totalCount) {
                countElement.innerHTML = `
                    Showing ${visibleCount} of ${totalCount}
                    <br><small class="text-success">${selectedCount} selected total</small>
                `;
                countElement.style.display = 'block';
            } else {
                countElement.style.display = 'none';
            }
        }
    }
    
    /**
     * Get options key for container ID
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
        const characterFilter = this.getSelectedCheckboxValues('characterCheckboxes');
        const opponentFilter = this.getSelectedCheckboxValues('opponentCheckboxes');
        const opponentCharacterFilter = this.getSelectedCheckboxValues('opponentCharCheckboxes');
        
        // FIXED: Always send all three filters, even if they're 'all'
        const filters = {
            character: characterFilter,
            opponent: opponentFilter,
            opponent_character: opponentCharacterFilter
        };
        
        console.log('🔍 Sending filters to backend:', filters);
        return filters;
    }
    
    getSelectedCheckboxValues(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`❌ Container ${containerId} not found`);
            return 'all';
        }
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);
        
        // Get total number of available options
        const totalCheckboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        
        console.log(`📊 ${containerId}: ${selected.length}/${totalCheckboxes.length} selected`);
        
        // If nothing selected, return 'all'
        if (selected.length === 0) {
            console.log(`   → Returning 'all' (nothing selected)`);
            return 'all';
        }
        
        // If everything selected, return 'all' 
        if (selected.length === totalCheckboxes.length) {
            console.log(`   → Returning 'all' (everything selected)`);
            return 'all';
        }
        
        // Return array of selected items when it's a partial selection
        console.log(`   → Returning array:`, selected.slice(0, 3), selected.length > 3 ? `... +${selected.length - 3} more` : '');
        return selected;
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
            // FIXED: Store reference to 'this' for use in event handler
            const self = this;
            
            selectAllCheckbox.addEventListener('change', function() {
                const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
                
                // FIXED: Apply select-all to ALL checkboxes, not just visible ones
                // The user expects "select all" to mean "select all items", regardless of search
                checkboxes.forEach(cb => {
                    cb.checked = this.checked;
                });
                
                // FIXED: Use 'self' instead of 'that'
                // Update the label after changing selections
                const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
                self.updateSelectAllLabel(this, checkedCount, checkboxes.length, containerId);
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
        
        // FIXED: Base select-all state on ALL checkboxes, not just visible ones
        // This ensures consistent behavior regardless of search state
        const allCheckboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
        
        if (allCheckboxes.length === 0) return;
        
        selectAll.checked = checkedCount === allCheckboxes.length;
        selectAll.indeterminate = checkedCount > 0 && checkedCount < allCheckboxes.length;
        
        // Update the label to show actual count vs visible count
        this.updateSelectAllLabel(selectAll, checkedCount, allCheckboxes.length, containerId);
    }
    
    /**
     * Update select-all label to show actual selection count
     */
    updateSelectAllLabel(selectAllCheckbox, checkedCount, totalCount, containerId) {
        const label = selectAllCheckbox.nextElementSibling;
        if (!label) return;
        
        const baseText = {
            'characterCheckboxes': 'All Characters',
            'opponentCheckboxes': 'All Opponents', 
            'opponentCharCheckboxes': 'All Characters'
        }[containerId] || 'All Items';
        
        // Show actual selection count if not all are selected
        if (checkedCount === totalCount) {
            label.textContent = baseText;
        } else if (checkedCount === 0) {
            label.textContent = `${baseText} (none selected)`;
        } else {
            label.textContent = `${baseText} (${checkedCount}/${totalCount} selected)`;
        }
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
     * Clear search for specific filter type
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