// frontend/components/navbar/navbar.js
// Navbar Component - AUTO-INITIALIZATION

/**
 * Navbar Component Class
 * Handles navbar state management and interactions
 */
class NavbarComponent {
    constructor() {
        this.navbar = document.querySelector('[data-navbar-state]');
        this.state = this.navbar ? this.navbar.getAttribute('data-navbar-state') : 'default';
        this.init();
    }
    
    init() {
        if (!this.navbar) {
            console.warn('Navbar component not found');
            return;
        }
        
        this.setupActiveStates();
        this.setupAccessibility();
        this.setupAnalytics();
        
        console.log(`Navbar initialized with state: ${this.state}`);
    }
    
    /**
     * Set up active states for navigation items
     */
    setupActiveStates() {
        const currentPath = window.location.pathname;
        const navLinks = this.navbar.querySelectorAll('.nav-link:not(.dropdown-toggle)');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href || href === '#') return;
            
            // Remove existing active classes
            link.classList.remove('active');
            
            // Add active class based on current path
            if (href === currentPath) {
                link.classList.add('active');
            } else if (href !== '/' && currentPath.startsWith(href)) {
                link.classList.add('active');
            }
        });
        
        // Handle dropdown active states
        this.updateDropdownActiveStates();
    }
    
    /**
     * Update dropdown active states based on current page
     */
    updateDropdownActiveStates() {
        const dropdowns = this.navbar.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const dropdownItems = dropdown.querySelectorAll('.dropdown-item');
            let hasActiveItem = false;
            
            dropdownItems.forEach(item => {
                if (item.classList.contains('active')) {
                    hasActiveItem = true;
                }
            });
            
            // Update dropdown toggle active state
            const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
            if (dropdownToggle) {
                if (hasActiveItem) {
                    dropdownToggle.classList.add('active');
                } else {
                    dropdownToggle.classList.remove('active');
                }
            }
        });
    }
    
    /**
     * Set up accessibility features
     */
    setupAccessibility() {
        // Add keyboard navigation support
        this.setupKeyboardNavigation();
        
        // Add ARIA labels and descriptions
        this.setupAriaLabels();
        
        // Handle focus management for dropdowns
        this.setupFocusManagement();
    }
    
    /**
     * Set up keyboard navigation
     */
    setupKeyboardNavigation() {
        this.navbar.addEventListener('keydown', (e) => {
            // Handle Escape key to close dropdowns
            if (e.key === 'Escape') {
                const openDropdowns = this.navbar.querySelectorAll('.dropdown-menu.show');
                openDropdowns.forEach(dropdown => {
                    const toggle = dropdown.previousElementSibling;
                    if (toggle) {
                        toggle.click();
                        toggle.focus();
                    }
                });
            }
            
            // Handle Arrow keys for dropdown navigation
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const activeElement = document.activeElement;
                const dropdown = activeElement.closest('.dropdown');
                
                if (dropdown) {
                    e.preventDefault();
                    this.navigateDropdown(dropdown, e.key === 'ArrowDown');
                }
            }
        });
    }
    
    /**
     * Navigate dropdown items with keyboard
     */
    navigateDropdown(dropdown, goDown) {
        const items = dropdown.querySelectorAll('.dropdown-item:not(.disabled)');
        const activeElement = document.activeElement;
        let currentIndex = Array.from(items).indexOf(activeElement);
        
        if (currentIndex === -1) {
            // If no item is focused, focus first or last
            const targetIndex = goDown ? 0 : items.length - 1;
            if (items[targetIndex]) {
                items[targetIndex].focus();
            }
        } else {
            // Move to next/previous item
            const targetIndex = goDown 
                ? (currentIndex + 1) % items.length
                : (currentIndex - 1 + items.length) % items.length;
            
            if (items[targetIndex]) {
                items[targetIndex].focus();
            }
        }
    }
    
    /**
     * Set up ARIA labels for better accessibility
     */
    setupAriaLabels() {
        // Add ARIA labels to navigation
        const nav = this.navbar.querySelector('.navbar-nav');
        if (nav && !nav.getAttribute('aria-label')) {
            nav.setAttribute('aria-label', 'Main navigation');
        }
        
        // Add ARIA labels to dropdowns
        const dropdowns = this.navbar.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(toggle => {
            if (!toggle.getAttribute('aria-label')) {
                const text = toggle.textContent.trim();
                toggle.setAttribute('aria-label', `${text} menu`);
            }
        });
    }
    
    /**
     * Set up focus management for better UX
     */
    setupFocusManagement() {
        // Handle dropdown open/close focus
        const dropdownToggles = this.navbar.querySelectorAll('.dropdown-toggle');
        
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('shown.bs.dropdown', () => {
                // Focus first dropdown item when opened
                const dropdown = toggle.nextElementSibling;
                const firstItem = dropdown?.querySelector('.dropdown-item:not(.disabled)');
                if (firstItem) {
                    setTimeout(() => firstItem.focus(), 100);
                }
            });
            
            toggle.addEventListener('hidden.bs.dropdown', () => {
                // Return focus to toggle when closed
                toggle.focus();
            });
        });
    }
    
    /**
     * Set up analytics tracking
     */
    setupAnalytics() {
        // Track navigation clicks
        const navLinks = this.navbar.querySelectorAll('.nav-link, .dropdown-item');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                const text = link.textContent.trim();
                const isDropdownItem = link.classList.contains('dropdown-item');
                
                // Track navigation analytics
                this.trackNavigation({
                    type: isDropdownItem ? 'dropdown_item' : 'nav_link',
                    text: text,
                    href: href,
                    navbar_state: this.state
                });
            });
        });
        
        // Track search usage if present
        const searchForm = this.navbar.querySelector('.navbar-search form');
        if (searchForm) {
            searchForm.addEventListener('submit', () => {
                this.trackNavigation({
                    type: 'search',
                    navbar_state: this.state
                });
            });
        }
    }
    
    /**
     * Track navigation events
     */
    trackNavigation(data) {
        console.log('Navigation tracked:', data);
        
        // Here you could send to analytics service
        // Example: gtag('event', 'navigation', data);
        // Example: analytics.track('navigation', data);
    }
    
    /**
     * Get current navbar state
     */
    getState() {
        return this.state;
    }
    
    /**
     * Update navbar state (for dynamic changes)
     */
    setState(newState) {
        if (this.navbar) {
            this.navbar.setAttribute('data-navbar-state', newState);
            this.state = newState;
            this.setupActiveStates();
            console.log(`Navbar state updated to: ${newState}`);
        }
    }
    
    /**
     * Refresh navbar (useful after navigation or state changes)
     */
    refresh() {
        this.setupActiveStates();
    }
}

/**
 * Initialize navbar component
 */
function initializeNavbar() {
    window.NavbarComponent = new NavbarComponent();
}

// ✅ AUTO-INITIALIZE (no DOMContentLoaded)
initializeNavbar();

// ✅ EXPORT
window.initializeNavbar = initializeNavbar;