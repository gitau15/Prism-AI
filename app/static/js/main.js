// Simple loading indicator functions
function showLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

// Enhanced form submission handlers
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions with loading indicators
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
            }
            showLoading();
        });
    });
    
    // Handle file upload area hover effect
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = 'var(--hover-blue)';
        });
        
        uploadArea.addEventListener('dragleave', function() {
            this.style.borderColor = 'var(--light-blue)';
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = 'var(--light-blue)';
        });
    }
});