// Advanced Filters Component JavaScript - SIMPLIFIED
// frontend/components/filters/filters.js

class AdvancedFilters {
    constructor() {
        this.onFilterChangeCallback = null;
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
        
        console.log('Advanced filters component initialized');
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
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);
        
        return selected.length > 0 ? selected : 'all';
    }
    
    populateFilterOptions(filterOptions) {
        this.createCheckboxes('characterCheckboxes', filterOptions.characters, 'char', 'selectAllCharacters');
        this.createCheckboxes('opponentCheckboxes', filterOptions.opponents, 'opp', 'selectAllOpponents');
        this.createCheckboxes('opponentCharCheckboxes', filterOptions.opponent_characters, 'opp_char', 'selectAllOpponentChars');
    }
    
    createCheckboxes(containerId, items, namePrefix, selectAllId) {
        const container = document.getElementById(containerId);
        if (!container || !items || items.length === 0) return;
        
        // Keep the select-all option
        const allOption = container.querySelector('.select-all-option');
        container.innerHTML = '';
        if (allOption) {
            container.appendChild(allOption);
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
                checkboxes.forEach(cb => {
                    cb.checked = this.checked;
                });
            });
            
            // Initialize select-all state
            this.updateSelectAllCheckbox(containerId, selectAllId);
        }
    }
    
    updateSelectAllCheckbox(containerId, selectAllId) {
        const container = document.getElementById(containerId);
        const selectAll = document.getElementById(selectAllId);
        if (!container || !selectAll) return;
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
        
        if (checkboxes.length === 0) return;
        
        selectAll.checked = checkedCount === checkboxes.length;
        selectAll.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
    }
    
    resetAllFilters() {
        // Check all checkboxes
        document.querySelectorAll('.filter-checkboxes-horizontal input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
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
    
    // Public API
    onFilterChange(callback) {
        this.onFilterChangeCallback = callback;
    }
}

// Auto-initialize and make available globally
const advancedFilters = new AdvancedFilters();
window.AdvancedFilters = AdvancedFilters;
window.advancedFilters = advancedFilters;