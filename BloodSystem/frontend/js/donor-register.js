// Donor Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('donorRegistrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    // Password strength validation
    passwordInput.addEventListener('input', function() {
        AuthSystem.updatePasswordStrength(this);
        validatePasswordMatch();
    });
    
    confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    
    // Real-time field validation
    const fieldsToValidate = [
        { field: 'firstName', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'lastName', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'email', rules: ['required', 'email'] },
        { field: 'phone', rules: ['required', 'phone'] },
        { field: 'weight', rules: ['required', 'numeric'] },
        { field: 'city', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'state', rules: ['required', { type: 'minLength', param: 2 }] }
    ];
    
    fieldsToValidate.forEach(({ field, rules }) => {
        const element = document.getElementById(field);
        if (element) {
            element.addEventListener('blur', function() {
                validateField(this, rules);
            });
            
            element.addEventListener('input', function() {
                // Clear error on input
                if (this.classList.contains('error')) {
                    AuthSystem.formValidator.clearFieldError(this);
                }
            });
        }
    });
    
    // Age validation for date of birth
    const dobInput = document.getElementById('dateOfBirth');
    dobInput.addEventListener('change', function() {
        validateAge(this);
    });
    
    // Weight validation
    const weightInput = document.getElementById('weight');
    weightInput.addEventListener('input', function() {
        validateWeight(this);
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            const formData = prepareFormData();
            
            // Custom submission for donor registration with nested data
            submitDonorRegistration(formData);
        }
    });
    
    async function submitDonorRegistration(data) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        
        try {
            const response = await fetch('http://localhost:8000/api/auth/register/donor/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                AuthSystem.notificationManager.show('Registration successful! Redirecting to dashboard...', 'success');
                
                // Store tokens
                if (result.tokens) {
                    AuthSystem.authManager.storeTokens(result.tokens, result.user);
                }
                
                // Redirect to donor dashboard
                setTimeout(() => {
                    // Simple relative path redirect
                    console.log('Current location:', window.location.href);
                    console.log('Attempting redirect to: ../donor/dashboard.html');
                    
                    // Use relative path from auth/ to donor/
                    window.location.href = '../donor/dashboard.html';
                }, 2000);
            } else {
                // Show validation errors
                if (result.user) {
                    Object.keys(result.user).forEach(field => {
                        const element = document.getElementById(getFieldId(field));
                        if (element && result.user[field]) {
                            AuthSystem.formValidator.showFieldError(element, result.user[field][0]);
                        }
                    });
                }
                
                // Show general errors
                Object.keys(result).forEach(field => {
                    if (field !== 'user' && result[field]) {
                        const element = document.getElementById(getFieldId(field));
                        if (element) {
                            AuthSystem.formValidator.showFieldError(element, result[field][0]);
                        }
                    }
                });
                
                AuthSystem.notificationManager.show('Please fix the errors and try again', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            AuthSystem.notificationManager.show('Registration failed. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }
    
    function getFieldId(fieldName) {
        const fieldMap = {
            'first_name': 'firstName',
            'last_name': 'lastName',
            'blood_group': 'bloodGroup',
            'date_of_birth': 'dateOfBirth'
        };
        return fieldMap[fieldName] || fieldName;
    }
    
    function validateField(element, rules) {
        const value = element.value.trim();
        const fieldName = element.getAttribute('name');
        const errors = AuthSystem.formValidator.validateField(fieldName, value, rules);
        
        if (errors.length > 0) {
            AuthSystem.formValidator.showFieldError(element, errors[0]);
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(element);
            return true;
        }
    }
    
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword.length > 0) {
            if (password !== confirmPassword) {
                AuthSystem.formValidator.showFieldError(confirmPasswordInput, 'Passwords do not match');
                return false;
            } else {
                AuthSystem.formValidator.showFieldSuccess(confirmPasswordInput);
                return true;
            }
        }
        return true;
    }
    
    function validateAge(dobElement) {
        const dob = new Date(dobElement.value);
        const today = new Date();
        const age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            age--;
        }
        
        if (age < 18) {
            AuthSystem.formValidator.showFieldError(dobElement, 'You must be at least 18 years old to donate blood');
            return false;
        } else if (age > 65) {
            AuthSystem.formValidator.showFieldError(dobElement, 'Donors must be under 65 years old');
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(dobElement);
            return true;
        }
    }
    
    function validateWeight(weightElement) {
        const weight = parseFloat(weightElement.value);
        
        if (weight < 50) {
            AuthSystem.formValidator.showFieldError(weightElement, 'Minimum weight requirement is 50 kg');
            return false;
        } else if (weight > 200) {
            AuthSystem.formValidator.showFieldError(weightElement, 'Please enter a valid weight');
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(weightElement);
            return true;
        }
    }
    
    function validateForm() {
        let isValid = true;
        
        // Validate all required fields
        fieldsToValidate.forEach(({ field, rules }) => {
            const element = document.getElementById(field);
            if (element && !validateField(element, rules)) {
                isValid = false;
            }
        });
        
        // Validate password
        const passwordValidation = AuthSystem.formValidator.validatePassword(passwordInput.value);
        if (!passwordValidation.isValid) {
            AuthSystem.formValidator.showFieldError(passwordInput, 'Password does not meet requirements');
            isValid = false;
        }
        
        // Validate password match
        if (!validatePasswordMatch()) {
            isValid = false;
        }
        
        // Validate age
        if (!validateAge(dobInput)) {
            isValid = false;
        }
        
        // Validate weight
        if (!validateWeight(weightInput)) {
            isValid = false;
        }
        
        // Validate required selections
        const requiredSelects = ['bloodGroup', 'gender'];
        requiredSelects.forEach(fieldName => {
            const element = document.getElementById(fieldName);
            if (!element.value) {
                AuthSystem.formValidator.showFieldError(element, `${fieldName} is required`);
                isValid = false;
            }
        });
        
        // Validate terms checkbox
        const termsCheckbox = document.getElementById('terms');
        if (termsCheckbox && !termsCheckbox.checked) {
            AuthSystem.notificationManager.show('Please accept the terms and conditions', 'error');
            isValid = false;
        } else if (!termsCheckbox) {
            console.error('Terms checkbox not found');
            isValid = false;
        }
        
        return isValid;
    }
    
    function prepareFormData() {
        const formData = new FormData(form);
        const data = {};
        
        // Prepare user data
        data.user = {
            first_name: formData.get('firstName'),
            last_name: formData.get('lastName'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            password: formData.get('password'),
            confirm_password: formData.get('confirmPassword'),
            role: 'DONOR'
        };
        
        // Prepare donor profile data
        data.blood_group = formData.get('bloodGroup');
        data.city = formData.get('city');
        data.state = formData.get('state');
        data.date_of_birth = formData.get('dateOfBirth');
        data.weight = parseFloat(formData.get('weight'));
        data.gender = formData.get('gender');
        
        return data;
    }
    
    // Auto-format phone number
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value.length > 0 && !value.startsWith('1')) {
            value = '1' + value;
        }
        if (value.length > 1) {
            value = '+' + value;
        }
        this.value = value;
    });
    
    // Set max date for date of birth (18 years ago)
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() - 18);
    dobInput.max = maxDate.toISOString().split('T')[0];
    
    // Set min date for date of birth (100 years ago)
    const minDate = new Date();
    minDate.setFullYear(minDate.getFullYear() - 100);
    dobInput.min = minDate.toISOString().split('T')[0];
});