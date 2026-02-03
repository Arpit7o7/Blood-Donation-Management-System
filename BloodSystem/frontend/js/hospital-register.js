// Hospital Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hospitalRegistrationForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const hasBloodBankCheckbox = document.getElementById('hasBloodBank');
    const bloodBankDetails = document.getElementById('bloodBankDetails');
    const bloodBankLicenseDoc = document.getElementById('bloodBankLicenseDoc');
    
    // Toggle blood bank details
    hasBloodBankCheckbox.addEventListener('change', function() {
        if (this.checked) {
            bloodBankDetails.classList.remove('hidden');
            bloodBankLicenseDoc.style.display = 'block';
            document.getElementById('bloodBankLicense').required = true;
            document.getElementById('storageCapacity').required = true;
        } else {
            bloodBankDetails.classList.add('hidden');
            bloodBankLicenseDoc.style.display = 'none';
            document.getElementById('bloodBankLicense').required = false;
            document.getElementById('storageCapacity').required = false;
        }
    });
    
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
        { field: 'hospitalName', rules: ['required', { type: 'minLength', param: 3 }] },
        { field: 'registrationNumber', rules: ['required', { type: 'minLength', param: 5 }] },
        { field: 'issuingAuthority', rules: ['required', { type: 'minLength', param: 3 }] },
        { field: 'email', rules: ['required', 'email'] },
        { field: 'phone', rules: ['required', 'phone'] },
        { field: 'emergencyContact', rules: ['required', 'phone'] },
        { field: 'addressLine', rules: ['required', { type: 'minLength', param: 10 }] },
        { field: 'area', rules: ['required'] },
        { field: 'city', rules: ['required'] },
        { field: 'district', rules: ['required'] },
        { field: 'state', rules: ['required'] },
        { field: 'pincode', rules: ['required', { type: 'minLength', param: 6 }] },
        { field: 'authorizedPersonName', rules: ['required', { type: 'minLength', param: 3 }] },
        { field: 'authorizedPersonDesignation', rules: ['required'] },
        { field: 'authorizedPersonMobile', rules: ['required', 'phone'] },
        { field: 'authorizedPersonEmail', rules: ['required', 'email'] },
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
    
    // Year validation
    const yearInput = document.getElementById('yearOfRegistration');
    yearInput.addEventListener('input', function() {
        validateYear(this);
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
            handleHospitalRegistration();
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
    
    function validateYear(yearElement) {
        const year = parseInt(yearElement.value);
        const currentYear = new Date().getFullYear();
        
        if (year < 1900) {
            AuthSystem.formValidator.showFieldError(yearElement, 'Year must be after 1900');
            return false;
        } else if (year > currentYear) {
            AuthSystem.formValidator.showFieldError(yearElement, 'Year cannot be in the future');
            return false;
        } else {
            AuthSystem.formValidator.showFieldSuccess(yearElement);
            return true;
        }
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
        // Files are optional for now - can be uploaded later through admin panel
        return true;
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
        
        // Validate year
        if (!validateYear(yearInput)) {
            isValid = false;
        }
        
        // Validate pincode
        if (!validatePincode(pincodeInput)) {
            isValid = false;
        }
        
        // Validate blood bank details if selected
        if (hasBloodBankCheckbox.checked) {
            const bloodBankLicense = document.getElementById('bloodBankLicense');
            const storageCapacity = document.getElementById('storageCapacity');
            
            if (!bloodBankLicense.value.trim()) {
                AuthSystem.formValidator.showFieldError(bloodBankLicense, 'Blood bank license is required');
                isValid = false;
            }
            
            if (!storageCapacity.value || parseInt(storageCapacity.value) < 1) {
                AuthSystem.formValidator.showFieldError(storageCapacity, 'Valid storage capacity is required');
                isValid = false;
            }
        }
        
        // Validate required files
        if (!validateRequiredFiles()) {
            isValid = false;
        }
        
        // Validate checkboxes
        const requiredCheckboxes = ['terms', 'verification'];
        requiredCheckboxes.forEach(checkboxName => {
            const checkbox = document.getElementById(checkboxName);
            if (checkbox && !checkbox.checked) {
                AuthSystem.notificationManager.show(`Please check the ${checkboxName} checkbox`, 'error');
                isValid = false;
            } else if (!checkbox) {
                console.error(`Checkbox with id '${checkboxName}' not found`);
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    async function handleHospitalRegistration() {
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
                    role: 'HOSPITAL'
                },
                hospital_name: formData.get('hospitalName'),
                registration_number: formData.get('registrationNumber'),
                issuing_authority: formData.get('issuingAuthority'),
                year_of_registration: parseInt(formData.get('yearOfRegistration')),
                address_line: formData.get('addressLine'),
                area: formData.get('area'),
                city: formData.get('city'),
                district: formData.get('district'),
                state: formData.get('state'),
                pincode: formData.get('pincode'),
                authorized_person_name: formData.get('authorizedPersonName'),
                authorized_person_designation: formData.get('authorizedPersonDesignation'),
                authorized_person_mobile: formData.get('authorizedPersonMobile'),
                authorized_person_email: formData.get('authorizedPersonEmail'),
                has_blood_bank: formData.get('hasBloodBank') === 'on',
                blood_bank_license: formData.get('bloodBankLicense') || '',
                storage_capacity: formData.get('storageCapacity') ? parseInt(formData.get('storageCapacity')) : null
            };
            
            console.log('Sending hospital registration data:', data);
            
            const response = await fetch(`${AuthSystem.authManager.baseURL}/auth/register/hospital/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            console.log('Server response:', result);
            
            if (response.ok) {
                AuthSystem.notificationManager.show(
                    'Hospital registration submitted successfully! Awaiting admin verification.', 
                    'success'
                );
                
                // Redirect to login after delay
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 3000);
                
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
                                    
                                    // Show specific error messages
                                    if (field === 'registration_number' && errorMsg.includes('already exists')) {
                                        AuthSystem.notificationManager.show('This registration number is already in use. Please check your registration number.', 'error');
                                    }
                                }
                            }
                        });
                    }
                } else {
                    AuthSystem.notificationManager.show('Registration failed. Please try again.', 'error');
                }
            }
            
        } catch (error) {
            console.error('Hospital registration error:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    }
    
    // Set current year as max for year input
    const currentYear = new Date().getFullYear();
    yearInput.max = currentYear;
});