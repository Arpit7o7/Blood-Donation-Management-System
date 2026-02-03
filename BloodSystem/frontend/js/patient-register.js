// Patient Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientRegistrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const dobInput = document.getElementById('dateOfBirth');
    
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
        { field: 'city', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'state', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'emergencyContact', rules: ['required', 'phone'] },
        { field: 'emergencyContactName', rules: ['required', { type: 'minLength', param: 2 }] }
    ];
    
    fieldsToValidate.forEach(({ field, rules }) => {
        const element = document.getElementById(field);
        if (element) {
            element.addEventListener('blur', function() {
                validateField(this, rules);
            });
            
            element.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    AuthSystem.formValidator.clearFieldError(this);
                }
            });
        }
    });
    
    // Date of birth validation
    dobInput.addEventListener('change', function() {
        validateDateOfBirth(this);
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            handlePatientRegistration();
        }
    });
    
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
    
    function validateDateOfBirth(dobElement) {
        const dob = new Date(dobElement.value);
        const today = new Date();
        const age = today.getFullYear() - dob.getFullYear();
        const monthDiff = today.getMonth() - dob.getMonth();
        
        let actualAge = age;
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            actualAge--;
        }
        
        if (actualAge < 0) {
            AuthSystem.formValidator.showFieldError(dobElement, 'Date of birth cannot be in the future');
            return false;
        } else if (actualAge > 120) {
            AuthSystem.formValidator.showFieldError(dobElement, 'Please enter a valid date of birth');
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(dobElement);
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
        
        // Validate required selections
        const requiredSelects = ['gender', 'emergencyContactRelation'];
        requiredSelects.forEach(fieldName => {
            const element = document.getElementById(fieldName);
            if (!element.value) {
                AuthSystem.formValidator.showFieldError(element, `${fieldName.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`);
                isValid = false;
            }
        });
        
        // Validate date of birth
        if (!validateDateOfBirth(dobInput)) {
            isValid = false;
        }
        
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
        
        // Validate required checkboxes
        const requiredCheckboxes = ['medicalDataConsent', 'emergencyContactConsent', 'terms'];
        requiredCheckboxes.forEach(checkboxName => {
            const checkbox = document.getElementById(checkboxName);
            if (checkbox && !checkbox.checked) {
                AuthSystem.notificationManager.show(`Please check the ${checkboxName.replace(/([A-Z])/g, ' $1').toLowerCase()} checkbox`, 'error');
                isValid = false;
            } else if (!checkbox) {
                console.error(`Checkbox with id '${checkboxName}' not found`);
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    async function handlePatientRegistration() {
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        
        try {
            const formData = new FormData(form);
            
            // Debug: Check all form data
            console.log('Form data entries:');
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: "${value}"`);
            }
            
            // Prepare the data structure
            const data = {
                user: {
                    first_name: formData.get('firstName'),
                    last_name: formData.get('lastName'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    password: formData.get('password'),
                    confirm_password: formData.get('confirmPassword'),
                    role: 'PATIENT'
                },
                date_of_birth: formData.get('dateOfBirth'),
                gender: formData.get('gender'),
                city: formData.get('city'),
                state: formData.get('state'),
                emergency_contact: formData.get('emergencyContact'),
                emergency_contact_name: formData.get('emergencyContactName'),
                emergency_contact_relation: formData.get('emergencyContactRelation'),
                medical_conditions: formData.get('medicalConditions') || '',
                blood_group: formData.get('bloodGroup') || ''
            };
            
            // Check for missing required fields
            const requiredFields = [
                'user.first_name', 'user.last_name', 'user.email', 'user.phone', 'user.password',
                'date_of_birth', 'gender', 'city', 'state', 'emergency_contact', 
                'emergency_contact_name', 'emergency_contact_relation'
            ];
            
            const missingFields = [];
            requiredFields.forEach(fieldPath => {
                const keys = fieldPath.split('.');
                let value = data;
                for (let key of keys) {
                    value = value[key];
                }
                if (!value || value.trim() === '') {
                    missingFields.push(fieldPath);
                }
            });
            
            if (missingFields.length > 0) {
                console.error('Missing required fields:', missingFields);
                AuthSystem.notificationManager.show(`Missing required fields: ${missingFields.join(', ')}`, 'error');
                return;
            }
            
            console.log('Sending patient registration data:');
            console.log('User data:', data.user);
            console.log('Patient data:', {
                date_of_birth: data.date_of_birth,
                gender: data.gender,
                city: data.city,
                state: data.state,
                emergency_contact: data.emergency_contact,
                emergency_contact_name: data.emergency_contact_name,
                emergency_contact_relation: data.emergency_contact_relation,
                medical_conditions: data.medical_conditions,
                blood_group: data.blood_group
            });
            
            const response = await fetch(`${AuthSystem.authManager.baseURL}/auth/register/patient/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            console.log('Server response status:', response.status);
            console.log('Server response data:', result);
            
            if (response.ok) {
                // Store tokens and user data
                AuthSystem.authManager.storeTokens(result.tokens, result.user);
                
                AuthSystem.notificationManager.show('Registration successful! Redirecting to dashboard...', 'success');
                
                // Redirect to patient dashboard
                setTimeout(() => {
                    AuthSystem.authManager.redirectToDashboard(result.user.role);
                }, 1500);
                
            } else {
                console.error('Registration failed with status:', response.status);
                console.error('Error response:', result);
                
                // Handle validation errors
                if (result.errors || result.error) {
                    const errorMessage = result.error || 'Registration failed. Please check your information.';
                    AuthSystem.notificationManager.show(errorMessage, 'error');
                    
                    // Show field-specific errors
                    if (result.errors) {
                        console.log('Detailed validation errors:', result.errors);
                        
                        // Handle user field errors (nested)
                        if (result.errors.user) {
                            Object.keys(result.errors.user).forEach(userField => {
                                console.log(`User field error - ${userField}:`, result.errors.user[userField]);
                                const fieldElement = form.querySelector(`[name="${userField}"]`);
                                if (fieldElement) {
                                    const errorMsg = Array.isArray(result.errors.user[userField]) 
                                        ? result.errors.user[userField][0] 
                                        : result.errors.user[userField];
                                    AuthSystem.formValidator.showFieldError(fieldElement, errorMsg);
                                    
                                    // Show specific error messages
                                    if (userField === 'email' && errorMsg.includes('already exists')) {
                                        AuthSystem.notificationManager.show('This email is already registered. Please use a different email.', 'error');
                                    }
                                    if (userField === 'phone' && errorMsg.includes('already exists')) {
                                        AuthSystem.notificationManager.show('This phone number is already registered. Please use a different phone number.', 'error');
                                    }
                                }
                            });
                        }
                        
                        // Handle direct field errors
                        Object.keys(result.errors).forEach(field => {
                            if (field !== 'user') {
                                console.log(`Field error - ${field}:`, result.errors[field]);
                                const fieldElement = form.querySelector(`[name="${field}"]`);
                                if (fieldElement) {
                                    const errorMsg = Array.isArray(result.errors[field]) 
                                        ? result.errors[field][0] 
                                        : result.errors[field];
                                    AuthSystem.formValidator.showFieldError(fieldElement, errorMsg);
                                }
                            }
                        });
                    }
                } else {
                    AuthSystem.notificationManager.show('Registration failed. Please try again.', 'error');
                }
            }
            
        } catch (error) {
            console.error('Patient registration error:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }
    
    // Auto-format phone numbers (simplified)
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(phoneInput => {
        phoneInput.addEventListener('input', function() {
            // Remove any non-digit characters except +
            let value = this.value.replace(/[^\d+]/g, '');
            
            // Ensure it starts with + if it has digits
            if (value.length > 0 && !value.startsWith('+')) {
                value = '+' + value;
            }
            
            this.value = value;
        });
    });
    
    // Set date constraints
    const today = new Date();
    const maxDate = today.toISOString().split('T')[0];
    dobInput.max = maxDate;
    
    const minDate = new Date();
    minDate.setFullYear(minDate.getFullYear() - 120);
    dobInput.min = minDate.toISOString().split('T')[0];
});