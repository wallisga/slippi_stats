// Character Icons Component

// Character mapping configuration
const CHARACTER_MAPPING = {
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

/**
 * Initialize character icons for elements with data-character-name attribute
 * @param {Element} container - Container to search within (defaults to document)
 */
function initializeCharacterIcons(container = document) {
    // Only select elements that haven't been processed yet
    const elements = container.querySelectorAll('[data-character-name]:not([data-icon-processed])');
    
    elements.forEach(function(element) {
        // Mark as processed to avoid duplicate icons
        element.setAttribute('data-icon-processed', 'true');
        
        const characterName = element.getAttribute('data-character-name');
        
        if (characterName && CHARACTER_MAPPING[characterName]) {
            createCharacterIcon(element, characterName);
        } else {
            createFallbackIcon(element, characterName);
        }
    });
}

/**
 * Create character icon image element
 * @param {Element} element - Element to add icon to
 * @param {string} characterName - Name of the character
 */
function createCharacterIcon(element, characterName) {
    const img = document.createElement('img');
    img.src = `/frontend/icons/character/neutral ${CHARACTER_MAPPING[characterName]}.png`;
    img.alt = characterName;
    img.className = 'character-icon';
    
    // Set size based on container
    const isBanner = element.closest('.character-banner') || element.closest('.character-badge');
    if (isBanner) {
        img.width = 96;
        img.height = 96;
    } else {
        img.width = 24;
        img.height = 24;
    }
    
    // Add error handling for failed image loads
    img.onerror = function() {
        this.style.display = 'none';
        createFallbackIcon(element, characterName, isBanner);
    };
    
    element.appendChild(img);
}

/**
 * Create fallback icon when image is not available
 * @param {Element} element - Element to add icon to
 * @param {string} characterName - Name of the character
 * @param {boolean} isBanner - Whether this is for a banner/large display
 */
function createFallbackIcon(element, characterName, isBanner = false) {
    const span = document.createElement('span');
    span.className = 'character-icon-fallback';
    span.textContent = characterName ? characterName.charAt(0) : '?';
    
    if (characterName) {
        span.setAttribute('data-character', characterName.toLowerCase().replace(/ /g, '_'));
    }
    
    // Set size for banner elements
    if (isBanner || element.closest('.character-banner') || element.closest('.character-badge')) {
        span.style.width = '96px';
        span.style.height = '96px';
        span.style.lineHeight = '96px';
        span.style.fontSize = '36px';
        span.style.margin = '0 auto 15px auto';
        span.style.display = 'block';
    }
    
    element.appendChild(span);
}

/**
 * Refresh character icons in a specific container
 * Useful when new content is loaded dynamically
 * @param {Element} container - Container to refresh icons in
 */
function refreshCharacterIcons(container = document) {
    // Remove processed flag from all elements in container
    const processedElements = container.querySelectorAll('[data-icon-processed]');
    processedElements.forEach(el => el.removeAttribute('data-icon-processed'));
    
    // Reinitialize icons
    initializeCharacterIcons(container);
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCharacterIcons();
});

// Export functions for use by other components
window.CharacterIcons = {
    initialize: initializeCharacterIcons,
    refresh: refreshCharacterIcons
};