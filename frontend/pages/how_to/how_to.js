// How-To Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Progressive step animation
    animateSteps();
    
    // Add smooth scrolling for better UX
    addSmoothScrolling();
    
    // Add copy functionality for paths and commands
    addCopyFunctionality();
    
    // Add progress indicator
    addProgressIndicator();
    
    // Add keyboard navigation
    addKeyboardNavigation();
    
    console.log('How-to page JavaScript loaded');
});

// Animate steps on scroll
function animateSteps() {
    const steps = document.querySelectorAll('.step-container');
    
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    steps.forEach(step => {
        observer.observe(step);
    });
}

// Add smooth scrolling for anchor links
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Add copy functionality for code blocks and paths
function addCopyFunctionality() {
    const codeElements = document.querySelectorAll('.path-code');
    
    codeElements.forEach(code => {
        code.style.cursor = 'pointer';
        code.title = 'Click to copy';
        
        code.addEventListener('click', function() {
            const text = this.textContent;
            
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    showCopyFeedback(this);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    fallbackCopy(text);
                });
            } else {
                fallbackCopy(text);
            }
        });
    });
}

// Fallback copy method for older browsers
function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        textArea.remove();
        console.log('Copied using fallback method');
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        textArea.remove();
    }
}

// Show visual feedback when copying
function showCopyFeedback(element) {
    const originalText = element.textContent;
    const originalBg = element.style.backgroundColor;
    
    element.textContent = 'Copied!';
    element.style.backgroundColor = '#d1edff';
    element.style.color = '#0f5132';
    
    setTimeout(() => {
        element.textContent = originalText;
        element.style.backgroundColor = originalBg;
        element.style.color = '';
    }, 1500);
}

// Add reading progress indicator
function addProgressIndicator() {
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.id = 'reading-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 76px;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, #0d6efd, #198754);
        z-index: 1000;
        transition: width 0.2s ease;
    `;
    document.body.appendChild(progressBar);
    
    // Update progress on scroll
    function updateProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        progressBar.style.width = Math.min(scrollPercent, 100) + '%';
    }
    
    window.addEventListener('scroll', updateProgress);
    updateProgress(); // Initial call
}

// Add keyboard navigation
function addKeyboardNavigation() {
    let currentStepIndex = -1;
    const steps = document.querySelectorAll('.step-container');
    
    document.addEventListener('keydown', function(e) {
        // Navigate steps with arrow keys
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
            e.preventDefault();
            currentStepIndex = Math.min(currentStepIndex + 1, steps.length - 1);
            scrollToStep(currentStepIndex);
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
            e.preventDefault();
            currentStepIndex = Math.max(currentStepIndex - 1, 0);
            scrollToStep(currentStepIndex);
        }
        
        // Quick navigation shortcuts
        if (e.key === 'Home') {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            currentStepIndex = -1;
        } else if (e.key === 'End') {
            e.preventDefault();
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            currentStepIndex = steps.length - 1;
        }
        
        // Dashboard shortcut (D key)
        if (e.key === 'd' || e.key === 'D') {
            const dashboardLink = document.querySelector('a[href="/"]');
            if (dashboardLink && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                dashboardLink.click();
            }
        }
    });
}

// Scroll to specific step with highlighting
function scrollToStep(index) {
    const steps = document.querySelectorAll('.step-container');
    if (index >= 0 && index < steps.length) {
        const step = steps[index];
        
        // Remove previous highlights
        steps.forEach(s => s.style.backgroundColor = '');
        
        // Highlight current step
        step.style.backgroundColor = '#f8f9fa';
        step.style.borderRadius = '8px';
        step.style.transition = 'background-color 0.3s ease';
        
        // Scroll to step
        step.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        // Remove highlight after delay
        setTimeout(() => {
            step.style.backgroundColor = '';
        }, 2000);
    }
}

// Add enhanced button interactions
document.querySelectorAll('.cta-button').forEach(button => {
    button.addEventListener('click', function() {
        // Add loading state
        const originalHTML = this.innerHTML;
        const isExternal = this.href && !this.href.includes(window.location.origin);
        
        if (!isExternal) {
            this.innerHTML = '<i class="spinner-border spinner-border-sm me-2"></i>Loading...';
            this.style.pointerEvents = 'none';
            
            // Reset after delay (in case navigation fails)
            setTimeout(() => {
                this.innerHTML = originalHTML;
                this.style.pointerEvents = 'auto';
            }, 3000);
        }
    });
});

// Add image lazy loading and error handling enhancement
document.querySelectorAll('.screenshot').forEach(img => {
    img.addEventListener('error', function() {
        // Create a placeholder div when image fails to load
        const placeholder = document.createElement('div');
        placeholder.className = 'screenshot-placeholder';
        placeholder.style.cssText = `
            background-color: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            color: #6c757d;
            margin: 1.5rem 0;
        `;
        placeholder.innerHTML = `
            <i class="bi bi-image" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
            <p>Screenshot: ${this.alt}</p>
            <small>Image will be available in a future update</small>
        `;
        
        this.parentNode.replaceChild(placeholder, this);
    });
});

// Add helpful tooltips for interactive elements
function addTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.title;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                document.body.removeChild(this._tooltip);
                delete this._tooltip;
            }
        });
    });
}

// Initialize tooltips
addTooltips();