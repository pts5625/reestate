document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultsContainer = document.getElementById('results-container');
    const predictionResult = document.getElementById('prediction-result');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide any previous results or errors
        resultsContainer.classList.add('d-none');
        errorContainer.classList.add('d-none');
        
        // Validate the form
        if (!validateForm()) {
            return;
        }
        
        // Collect form data
        const data = {
            location: document.getElementById('location').value,
            floor_area: document.getElementById('floor_area').value,
            bedrooms: document.getElementById('bedrooms').value,
            bathrooms: document.getElementById('bathrooms').value,
            floor_no: document.getElementById('floor_no').value
        };
        
        try {
            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Predicting...';
            submitButton.disabled = true;
            
            // Send prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            // Reset button state
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An error occurred during prediction');
            }
            
            const result = await response.json();
            
            // Display prediction
            if (result.prediction !== undefined) {
                predictionResult.textContent = formatCurrency(result.prediction);
                resultsContainer.classList.remove('d-none');
                
                // Scroll to results
                resultsContainer.scrollIntoView({ behavior: 'smooth' });
            } else if (result.error) {
                showError(result.error);
            }
        } catch (error) {
            showError(error.message || 'An unexpected error occurred');
        }
    });
    
    function validateForm() {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            // Clear previous validation state
            input.classList.remove('is-invalid');
            
            if (input.hasAttribute('required') && !input.value) {
                input.classList.add('is-invalid');
                isValid = false;
            } else if (input.type === 'number') {
                const min = parseFloat(input.getAttribute('min'));
                const value = parseFloat(input.value);
                
                if (isNaN(value) || (min !== null && value < min)) {
                    input.classList.add('is-invalid');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
        errorContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    function formatCurrency(amount) {
        // Format with 2 decimal places and add "lakhs" suffix
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount) + " lakhs";
    }
    
    // Add input validation on blur
    const numericInputs = form.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const min = parseFloat(this.getAttribute('min'));
            const value = parseFloat(this.value);
            
            if (this.value && (isNaN(value) || (min !== null && value < min))) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
});
