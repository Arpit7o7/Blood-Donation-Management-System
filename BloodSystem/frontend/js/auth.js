// Authentication JavaScript Module

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Authentication utilities
class AuthManager {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    // Store tokens in localStorage
    storeTokens(tokens, user) {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user_data', JSON.stringify(user));
        localStorage.setItem('user_role', user.role);
    }

    // Get stored token
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Get user data
    getUserData() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    }

    // Clear authentication data
    clearAuth() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('user_role');
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    }

    // Make authenticated API request
    async makeRequest(endpoint, options = {}) {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Token expired, try to refresh
            const refreshed = await this.refreshToken();
            if (refreshed) {
                // Retry the request with new token
                headers['Authorization'] = `Bearer ${this.getToken()}`;
                return fetch(`${this.baseURL}${endpoint}`, {
                    ...options,
                    headers
                });
            } else {
                // Refresh failed, redirect to login
                this.clearAuth();
                window.location.href = '/auth/login.html';
                return null;
            }
        }

        return response;
    }

    // Refresh access token
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh: refreshToken
                })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        return false;
    }

    // Redirect to appropriate dashboard
    redirectToDashboard(role) {
        const dashboardRoutes = {
            'DONOR': '../donor/dashboard.html',
            'HOSPITAL': '../hospital/dashboard.html',
            'CAMP': '../camp/dashboard.html',
            'PATIENT': '../patient/dashboard.html',
            'ADMIN': '../admin/dashboard.html'
        };

        const route = dashboardRoutes[role] || '../index.html';
        console.log('Redirecting to dashboard:', route, 'for role:', role);
        window.location.href = route;
    }
}

// Form validation utilities
class FormValidator {
    constructor() {
        this.rules = {
            required: (value) => value.trim() !== '',
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            phone: (value) => /^\+?[\d\s\-\(\)]{10,}$/.test(value),
            password: (value) => this.validatePassword(value),
            minLength: (value, min) => value.length >= min,
            maxLength: (value, max) => value.length <= max,
            numeric: (value) => /^\d+$/.test(value),
            alphanumeric: (value) => /^[a-zA-Z0-9]+$/.test(value)
        };
    }

    validatePassword(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        return {
            isValid: Object.values(requirements).every(req => req),
            requirements
        };
    }

    validateField(field, value, rules) {
        const errors = [];

        for (const rule of rules) {
            if (typeof rule === 'string') {
                if (!this.rules[rule](value)) {
                    errors.push(this.getErrorMessage(rule, field));
                }
            } else if (typeof rule === 'object') {
                const { type, param } = rule;
                if (!this.rules[type](value, param)) {
                    errors.push(this.getErrorMessage(type, field, param));
                }
            }
        }

        return errors;
    }

    getErrorMessage(rule, field, param) {
        const messages = {
            required: `${field} is required`,
            email: 'Please enter a valid email address',
            phone: 'Please enter a valid phone number',
            password: 'Password does not meet requirements',
            minLength: `${field} must be at least ${param} characters`,
            maxLength: `${field} must not exceed ${param} characters`,
            numeric: `${field} must contain only numbers`,
            alphanumeric: `${field} must contain only letters and numbers`
        };

        return messages[rule] || `${field} is invalid`;
    }

    showFieldError(fieldElement, message) {
        this.clearFieldError(fieldElement);
        
        fieldElement.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        fieldElement.parentNode.appendChild(errorDiv);
    }

    showFieldSuccess(fieldElement) {
        this.clearFieldError(fieldElement);
        fieldElement.classList.remove('error');
        fieldElement.classList.add('success');
    }

    clearFieldError(fieldElement) {
        fieldElement.classList.remove('error', 'success');
        
        const existingError = fieldElement.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
}

// Notification system
class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        notification.style.cssText = `
            padding: 16px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            background-color: ${colors[type] || colors.info};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease-in-out;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        `;

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>${this.getIcon(type)}</span>
                <span>${message}</span>
            </div>
        `;

        // Add progress bar
        const progressBar = document.createElement('div');
        progressBar.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background-color: rgba(255, 255, 255, 0.3);
            width: 100%;
            transform-origin: left;
            animation: progress ${duration}ms linear;
        `;

        notification.appendChild(progressBar);

        // Add click to dismiss
        notification.addEventListener('click', () => {
            this.remove(notification);
        });

        this.container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove
        setTimeout(() => {
            this.remove(notification);
        }, duration);

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    remove(notification) {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

// Add progress bar animation
const style = document.createElement('style');
style.textContent = `
    @keyframes progress {
        from { transform: scaleX(1); }
        to { transform: scaleX(0); }
    }
`;
document.head.appendChild(style);

// Initialize global instances
const authManager = new AuthManager();
const formValidator = new FormValidator();
const notificationManager = new NotificationManager();

// Password strength indicator
function updatePasswordStrength(passwordInput) {
    const password = passwordInput.value;
    const validation = formValidator.validatePassword(password);
    const requirements = validation.requirements;
    
    // Update requirement indicators
    Object.keys(requirements).forEach(req => {
        const element = document.getElementById(req);
        if (element) {
            element.classList.toggle('valid', requirements[req]);
        }
    });
    
    // Update input styling
    if (password.length > 0) {
        if (validation.isValid) {
            formValidator.showFieldSuccess(passwordInput);
        } else {
            passwordInput.classList.remove('success');
            passwordInput.classList.add('error');
        }
    } else {
        formValidator.clearFieldError(passwordInput);
    }
}

// Form submission handler
async function handleFormSubmission(form, endpoint, successMessage, redirectUrl) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoading.classList.remove('hidden');
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            notificationManager.show(successMessage, 'success');
            
            // Store tokens if provided
            if (result.tokens) {
                authManager.storeTokens(result.tokens, result.user);
            }
            
            // Redirect after short delay
            setTimeout(() => {
                if (redirectUrl) {
                    window.location.href = redirectUrl;
                } else if (result.user && result.user.role) {
                    authManager.redirectToDashboard(result.user.role);
                }
            }, 1500);
            
        } else {
            // Handle validation errors
            if (result.errors || result.error) {
                const errorMessage = result.error || 'Registration failed. Please check your information.';
                notificationManager.show(errorMessage, 'error');
                
                // Show field-specific errors
                if (result.errors) {
                    Object.keys(result.errors).forEach(field => {
                        const fieldElement = form.querySelector(`[name="${field}"]`);
                        if (fieldElement) {
                            formValidator.showFieldError(fieldElement, result.errors[field][0]);
                        }
                    });
                }
            }
        }
        
    } catch (error) {
        console.error('Form submission error:', error);
        notificationManager.show('Network error. Please try again.', 'error');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
    }
}

// Export for global use
window.AuthSystem = {
    authManager,
    formValidator,
    notificationManager,
    updatePasswordStrength,
    handleFormSubmission
};