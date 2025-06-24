// Error Pages JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.error-actions .btn');
    
    buttons.forEach(button => {
        if (button.getAttribute('onclick') || button.href) {
            button.addEventListener('click', function() {
                // Add loading state
                this.classList.add('loading');
                
                // Remove loading state after delay (in case navigation fails)
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 3000);
            });
        }
    });
    
    // Enhanced back button functionality
    const backButton = document.querySelector('button[onclick*="history.back"]');
    if (backButton) {
        backButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check if there's history to go back to
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // If no history, go to home page
                window.location.href = '/';
            }
        });
    }
    
    // Auto-retry functionality for 500 errors
    const retryButton = document.querySelector('button[onclick*="reload"]');
    if (retryButton) {
        let retryCount = 0;
        const maxRetries = 3;
        
        retryButton.addEventListener('click', function(e) {
            e.preventDefault();
            retryCount++;
            
            if (retryCount <= maxRetries) {
                this.innerHTML = `<i class="bi bi-arrow-clockwise me-2"></i>Retrying... (${retryCount}/${maxRetries})`;
                this.classList.add('loading');
                
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.innerHTML = '<i class="bi bi-x-circle me-2"></i>Max Retries Reached';
                this.disabled = true;
                this.classList.remove('btn-outline-success');
                this.classList.add('btn-outline-danger');
            }
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Home key or Ctrl+H to go home
        if (e.key === 'Home' || (e.ctrlKey && e.key === 'h')) {
            e.preventDefault();
            window.location.href = '/';
        }
        
        // Backspace or Alt+Left to go back
        if (e.key === 'Backspace' || (e.altKey && e.key === 'ArrowLeft')) {
            e.preventDefault();
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = '/';
            }
        }
        
        // F5 or Ctrl+R to retry (on error pages with retry button)
        if ((e.key === 'F5' || (e.ctrlKey && e.key === 'r')) && retryButton) {
            e.preventDefault();
            retryButton.click();
        }
    });
    
    // Add error reporting functionality (optional)
    const reportError = function(errorType, errorMessage) {
        // This could be enhanced to send error reports to your logging service
        console.log('Error Report:', {
            type: errorType,
            message: errorMessage,
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        });
    };
    
    // Auto-report 500 errors
    const errorMessage = document.querySelector('.alert-danger p');
    if (errorMessage && window.location.pathname.includes('500')) {
        reportError('500_error', errorMessage.textContent);
    }
    
    // Track 404 errors for analytics
    if (window.location.pathname.includes('404')) {
        reportError('404_error', window.location.href);
    }
    
    // Add helpful tips animation
    const tipsList = document.querySelector('.tips-list');
    if (tipsList) {
        const tips = tipsList.querySelectorAll('li');
        tips.forEach((tip, index) => {
            tip.style.opacity = '0';
            tip.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                tip.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                tip.style.opacity = '1';
                tip.style.transform = 'translateY(0)';
            }, 200 * (index + 1));
        });
    }
    
    // Add smooth scrolling for any anchor links
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
    
    console.log('Error page JavaScript loaded');
});