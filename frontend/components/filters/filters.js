// Advanced Filters Component JavaScript
// frontend/components/filters/filters.js

class AdvancedFilters {
    constructor() {
        this.initialized = false;
        this.callbacks = {
            onFilterChange: null
        };
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeFilters());
        } else {
            this.initializeFilters();
        }
        
        this.initialized = true;
    }
    
    initializeFilters() {
        this.setupFilterToggles();
        this.setupFilterButtons();
        this.setupCollapseToggle();
        
        console.log('Advanced filters component initialized');
    }
    
    setupFilterToggles() {
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
                dropdown: 'opponentCharFilter',
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
    }
    
    setupFilterButtons() {
        // Apply filters button
        const applyButton = document.getElementById('applyFilters');
        if (applyButton) {
            applyButton.addEventListener('click', () => {
                const filters = this.getSelectedFilters();
                if (this.callbacks.onFilterChange) {
                    this.callbacks.onFilterChange(filters);
                }
            });
        }
        
        // Reset filters button
        const resetButton = document.getElementById('resetFilters');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                this.resetAllFilters();
                if (this.callbacks.onFilterChange) {
                    this.callbacks.onFilterChange({});
                }
            });
        }
    }
    
    setupCollapseToggle() {
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
    
    getSelectedFilters() {
        const filters = {};
        
        // Get character filter
        if (document.getElementById('characterFilterToggle')?.checked) {
            const selected = this.getSelectedCheckboxValues('characterCheckboxes');
            filters.character = selected.length > 0 ? selected : 'all';
        } else {
            const dropdown = document.getElementById('characterFilter');
            filters.character = dropdown ? dropdown.value : 'all';
        }
        
        // Get opponent filter
        if (document.getElementById('opponentFilterToggle')?.checked) {
            const selected = this.getSelectedCheckboxValues('opponentCheckboxes');
            filters.opponent = selected.length > 0 ? selected : 'all';
        } else {
            const dropdown = document.getElementById('opponentFilter');
            filters.opponent = dropdown ? dropdown.value : 'all';
        }
        
        // Get opponent character filter
        if (document.getElementById('opponentCharFilterToggle')?.checked) {
            const selected = this.getSelectedCheckboxValues('opponentCharCheckboxes');
            filters.opponent_character = selected.length > 0 ? selected : 'all';
        } else {
            const dropdown = document.getElementById('opponentCharFilter');
            filters.opponent_character = dropdown ? dropdown.value : 'all';
        }
        
        return filters;
    }
    
    getSelectedCheckboxValues(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return [];
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }
    
    populateFilterOptions(filterOptions) {
        // Populate dropdowns
        this.populateDropdown('characterFilter', filterOptions.characters);
        this.populateDropdown('opponentFilter', filterOptions.opponents);
        this.populateDropdown('opponentCharFilter', filterOptions.opponent_characters);
        
        // Create checkboxes
        this.createCheckboxes('characterCheckboxes', filterOptions.characters, 'char', 'selectAllCharacters');
        this.createCheckboxes('opponentCheckboxes', filterOptions.opponents, 'opp', 'selectAllOpponents');
        this.createCheckboxes('opponentCharCheckboxes', filterOptions.opponent_characters, 'opp_char', 'selectAllOpponentChars');
    }
    
    populateDropdown(dropdownId, options) {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) return;
        
        // Keep the first option (All...)
        while (dropdown.options.length > 1) {
            dropdown.remove(1);
        }
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            dropdown.appendChild(optionElement);
        });
    }
    
    createCheckboxes(containerId, items, namePrefix, selectAllId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Keep the select-all option
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
            
            input.addEventListener('change', () => {
                this.updateSelectAllCheckbox(containerId, selectAllId);
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
        
        // Setup select-all functionality
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
    
    updateSelectAllCheckbox(containerId, selectAllId) {
        const container = document.getElementById(containerId);
        const selectAll = document.getElementById(selectAllId);
        if (!container || !selectAll) return;
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        const checkedCount = container.querySelectorAll('input[type="checkbox"]:not(.select-all):checked').length;
        
        selectAll.checked = checkedCount === checkboxes.length;
        selectAll.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
    }
    
    resetAllFilters() {
        // Reset dropdowns
        const dropdowns = ['characterFilter', 'opponentFilter', 'opponentCharFilter'];
        dropdowns.forEach(id => {
            const dropdown = document.getElementById(id);
            if (dropdown) dropdown.value = 'all';
        });
        
        // Check all checkboxes
        document.querySelectorAll('.filter-checkboxes-horizontal input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
    }
    
    restoreCheckboxSelections(containerId, selectedValues) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const checkboxes = container.querySelectorAll('input[type="checkbox"]:not(.select-all)');
        
        checkboxes.forEach(cb => {
            cb.checked = selectedValues.includes(cb.value);
        });
        
        const selectAllId = containerId === 'characterCheckboxes' ? 'selectAllCharacters' : 
                           containerId === 'opponentCheckboxes' ? 'selectAllOpponents' : 
                           'selectAllOpponentChars';
        
        this.updateSelectAllCheckbox(containerId, selectAllId);
    }
    
    // Public API
    onFilterChange(callback) {
        this.callbacks.onFilterChange = callback;
    }
}

// Auto-initialize and make available globally
const advancedFilters = new AdvancedFilters();
window.AdvancedFilters = AdvancedFilters;
window.advancedFilters = advancedFilters;