// Login JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    // Form validation
    emailInput.addEventListener('blur', function() {
        validateEmail(this);
    });
    
    passwordInput.addEventListener('blur', function() {
        validatePassword(this);
    });
    
    // Clear errors on input
    [emailInput, passwordInput].forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                AuthSystem.formValidator.clearFieldError(this);
            }
        });
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            handleLogin();
        }
    });
    
    function validateEmail(emailElement) {
        const email = emailElement.value.trim();
        
        if (!email) {
            AuthSystem.formValidator.showFieldError(emailElement, 'Email is required');
            return false;
        }
        
        if (!AuthSystem.formValidator.rules.email(email)) {
            AuthSystem.formValidator.showFieldError(emailElement, 'Please enter a valid email address');
            return false;
        }
        
        AuthSystem.formValidator.showFieldSuccess(emailElement);
        return true;
    }
    
    function validatePassword(passwordElement) {
        const password = passwordElement.value;
        
        if (!password) {
            AuthSystem.formValidator.showFieldError(passwordElement, 'Password is required');
            return false;
        }
        
        AuthSystem.formValidator.showFieldSuccess(passwordElement);
        return true;
    }
    
    function validateForm() {
        const emailValid = validateEmail(emailInput);
        const passwordValid = validatePassword(passwordInput);
        
        return emailValid && passwordValid;
    }
    
    async function handleLogin() {
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        
        try {
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            
            const response = await fetch(`${AuthSystem.authManager.baseURL}/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Store tokens and user data
                AuthSystem.authManager.storeTokens(result.tokens, result.user);
                
                AuthSystem.notificationManager.show('Login successful! Redirecting...', 'success');
                
                // Redirect to appropriate dashboard
                setTimeout(() => {
                    AuthSystem.authManager.redirectToDashboard(result.user.role);
                }, 1500);
                
            } else {
                // Handle login errors
                if (result.error) {
                    AuthSystem.notificationManager.show(result.error, 'error');
                } else if (result.status === 'PENDING_VERIFICATION') {
                    AuthSystem.notificationManager.show('Your account is pending verification. Please wait for admin approval.', 'warning');
                } else {
                    AuthSystem.notificationManager.show('Login failed. Please check your credentials.', 'error');
                }
                
                // Clear password field on error
                passwordInput.value = '';
                passwordInput.focus();
            }
            
        } catch (error) {
            console.error('Login error:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }
    
    // Check if user is already logged in
    if (AuthSystem.authManager.isAuthenticated()) {
        const userData = AuthSystem.authManager.getUserData();
        if (userData) {
            AuthSystem.notificationManager.show('You are already logged in. Redirecting...', 'info');
            setTimeout(() => {
                AuthSystem.authManager.redirectToDashboard(userData.role);
            }, 2000);
        }
    }
});