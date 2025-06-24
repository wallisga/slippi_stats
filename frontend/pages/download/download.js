// Download Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const downloadButton = document.getElementById('downloadButton');
    
    if (downloadButton) {
        // Add event listener to redirect to the how-to page after clicking download
        downloadButton.addEventListener('click', function(e) {
            // Allow the download to start
            setTimeout(function() {
                window.location.href = '/how-to';
            }, 1000); // Redirect after 1 second to allow the download to start
        });
    }
});