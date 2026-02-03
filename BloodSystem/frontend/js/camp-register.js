// Camp Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('campRegistrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    // Password strength validation
    passwordInput.addEventListener('input', function() {
        AuthSystem.updatePasswordStrength(this);
        validatePasswordMatch();
    });
    
    confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    
    // File upload handling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const label = this.nextElementSibling;
            const fileName = this.files[0]?.name;
            if (fileName) {
                label.textContent = `📄 ${fileName}`;
                label.parentElement.classList.add('has-file');
            } else {
                label.textContent = label.getAttribute('data-original') || '📄 Choose File';
                label.parentElement.classList.remove('has-file');
            }
        });
        
        // Store original text
        const label = input.nextElementSibling;
        label.setAttribute('data-original', label.textContent);
    });
    
    // Real-time field validation
    const fieldsToValidate = [
        { field: 'organizationName', rules: ['required', { type: 'minLength', param: 3 }] },
        { field: 'registrationNumber', rules: ['required', { type: 'minLength', param: 5 }] },
        { field: 'contactPersonName', rules: ['required', { type: 'minLength', param: 3 }] },
        { field: 'contactPersonDesignation', rules: ['required'] },
        { field: 'contactPersonMobile', rules: ['required', 'phone'] },
        { field: 'addressLine', rules: ['required', { type: 'minLength', param: 10 }] },
        { field: 'city', rules: ['required'] },
        { field: 'state', rules: ['required'] },
        { field: 'pincode', rules: ['required', { type: 'minLength', param: 6 }] },
        { field: 'email', rules: ['required', 'email'] },
        { field: 'phone', rules: ['required', 'phone'] },
        { field: 'firstName', rules: ['required', { type: 'minLength', param: 2 }] },
        { field: 'lastName', rules: ['required', { type: 'minLength', param: 2 }] }
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
    
    // Pincode validation
    const pincodeInput = document.getElementById('pincode');
    pincodeInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '').substring(0, 6);
        validatePincode(this);
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            handleCampRegistration();
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
    
    function validatePincode(pincodeElement) {
        const pincode = pincodeElement.value;
        
        if (pincode.length !== 6) {
            AuthSystem.formValidator.showFieldError(pincodeElement, 'Pincode must be 6 digits');
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(pincodeElement);
            return true;
        }
    }
    
    function validateRequiredFiles() {
        const requiredFiles = ['organizationCertificate', 'authorizationLetter'];
        let isValid = true;
        
        requiredFiles.forEach(fieldName => {
            const fileInput = document.getElementById(fieldName);
            if (!fileInput.files.length) {
                AuthSystem.formValidator.showFieldError(fileInput, 'This document is required');
                isValid = false;
            }
        });
        
        return isValid;
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
        
        // Validate organization type
        const organizationType = document.getElementById('organizationType');
        if (!organizationType.value) {
            AuthSystem.formValidator.showFieldError(organizationType, 'Organization type is required');
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
        
        // Validate pincode
        if (!validatePincode(pincodeInput)) {
            isValid = false;
        }
        
        // Validate required files
        if (!validateRequiredFiles()) {
            isValid = false;
        }
        
        // Validate checkboxes
        const requiredCheckboxes = ['terms', 'verification', 'medicalCompliance'];
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
    
    async function handleCampRegistration() {
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        
        try {
            const formData = new FormData(form);
            
            // Prepare the data structure
            const data = {
                user: {
                    first_name: formData.get('firstName'),
                    last_name: formData.get('lastName'),
                    email: formData.get('email'),
                    phone: formData.get('phone'),
                    password: formData.get('password'),
                    confirm_password: formData.get('confirmPassword'),
                    role: 'CAMP'
                },
                organization_name: formData.get('organizationName'),
                organization_type: formData.get('organizationType'),
                registration_number: formData.get('registrationNumber'),
                contact_person_name: formData.get('contactPersonName'),
                contact_person_designation: formData.get('contactPersonDesignation'),
                contact_person_mobile: formData.get('contactPersonMobile'),
                address_line: formData.get('addressLine'),
                city: formData.get('city'),
                state: formData.get('state'),
                pincode: formData.get('pincode')
            };
            
            const response = await fetch(`${AuthSystem.authManager.baseURL}/auth/register/camp/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                AuthSystem.notificationManager.show(
                    'Camp organization registration submitted successfully! Awaiting admin verification.', 
                    'success'
                );
                
                // Redirect to login after delay
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 3000);
                
            } else {
                // Handle validation errors
                if (result.errors || result.error) {
                    const errorMessage = result.error || 'Registration failed. Please check your information.';
                    AuthSystem.notificationManager.show(errorMessage, 'error');
                    
                    // Show field-specific errors
                    if (result.errors) {
                        Object.keys(result.errors).forEach(field => {
                            const fieldElement = form.querySelector(`[name="${field}"]`);
                            if (fieldElement) {
                                AuthSystem.formValidator.showFieldError(fieldElement, result.errors[field][0]);
                            }
                        });
                    }
                }
            }
            
        } catch (error) {
            console.error('Camp registration error:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }
});