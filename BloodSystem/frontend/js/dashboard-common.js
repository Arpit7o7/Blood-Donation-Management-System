// Dashboard Common JavaScript

// Dashboard utilities and common functionality
class DashboardManager {
    constructor() {
        this.user = null;
        this.notifications = [];
        this.init();
    }

    async init() {
        // Check authentication
        if (!AuthSystem.authManager.isAuthenticated()) {
            window.location.href = '/auth/login.html';
            return;
        }

        // Load user data
        await this.loadUserData();
        
        // Setup common event listeners
        this.setupEventListeners();
        
        // Load notifications
        await this.loadNotifications();
    }

    async loadUserData() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/auth/profile/');
            if (response && response.ok) {
                const userData = await response.json();
                this.user = userData;
                this.updateUserInterface();
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
            AuthSystem.notificationManager.show('Failed to load user data', 'error');
        }
    }

    updateUserInterface() {
        if (!this.user) return;

        // Update user name
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            userNameElement.textContent = this.user.user?.first_name || 'User';
        }

        // Update user initials
        const userInitialsElement = document.getElementById('userInitials');
        if (userInitialsElement && this.user.user) {
            const firstName = this.user.user.first_name || '';
            const lastName = this.user.user.last_name || '';
            const initials = (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || 'U';
            userInitialsElement.textContent = initials;
        }
    }

    setupEventListeners() {
        // User menu toggle
        const userAvatar = document.getElementById('userAvatar');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userAvatar && userDropdown) {
            userAvatar.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('User avatar clicked');
                userDropdown.classList.toggle('hidden');
                console.log('Dropdown hidden class:', userDropdown.classList.contains('hidden'));
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                userDropdown.classList.add('hidden');
            });
        } else {
            console.log('User avatar or dropdown not found');
        }

        // Logout functionality
        const logoutLink = document.getElementById('logoutLink');
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        }

        // Notification bell
        const notificationBell = document.getElementById('notificationBell');
        if (notificationBell) {
            notificationBell.addEventListener('click', () => {
                this.showNotificationsPanel();
            });
        }

        // Profile link
        const profileLink = document.getElementById('profileLink');
        if (profileLink) {
            profileLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showProfileModal();
            });
        }
    }

    async handleLogout() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                await AuthSystem.authManager.makeRequest('/auth/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh: refreshToken })
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            AuthSystem.authManager.clearAuth();
            AuthSystem.notificationManager.show('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '../index.html';
            }, 1000);
        }
    }

    async loadNotifications() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/notifications/');
            if (response && response.ok) {
                const data = await response.json();
                this.notifications = data.results || [];
                this.updateNotificationBadge();
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    async refreshNotifications() {
        // Force refresh notifications from API
        await this.loadNotifications();
    }

    updateNotificationBadge() {
        const notificationCount = document.getElementById('notificationCount');
        if (notificationCount) {
            const unreadCount = this.notifications.filter(n => !n.is_read).length;
            if (unreadCount > 0) {
                notificationCount.textContent = unreadCount;
                notificationCount.classList.remove('hidden');
            } else {
                notificationCount.classList.add('hidden');
            }
        }
    }

    showNotificationsPanel() {
        // This would open a notifications panel/modal
        AuthSystem.notificationManager.show('Notifications panel coming soon!', 'info');
    }

    showProfileModal() {
        // Load current user data into the form
        this.loadProfileData();
        
        // Open the profile modal
        window.DashboardSystem.modalManager.openModal('profileModal');
        
        // Setup modal close events
        const closeProfileModal = document.getElementById('closeProfileModal');
        const cancelProfileUpdate = document.getElementById('cancelProfileUpdate');
        
        if (closeProfileModal) {
            closeProfileModal.onclick = () => {
                window.DashboardSystem.modalManager.closeModal('profileModal');
            };
        }
        
        if (cancelProfileUpdate) {
            cancelProfileUpdate.onclick = () => {
                window.DashboardSystem.modalManager.closeModal('profileModal');
            };
        }
        
        // Setup form submission (remove existing listener first)
        const profileForm = document.getElementById('profileUpdateForm');
        if (profileForm) {
            // Remove existing event listeners
            const newForm = profileForm.cloneNode(true);
            profileForm.parentNode.replaceChild(newForm, profileForm);
            
            // Add new event listener
            newForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleProfileUpdate(e);
            });
        }
    }

    async loadProfileData() {
        if (!this.user) return;

        // Populate user fields
        const fields = {
            'profileFirstName': this.user.user?.first_name || '',
            'profileLastName': this.user.user?.last_name || '',
            'profileEmail': this.user.user?.email || '',
            'profilePhone': this.user.user?.phone || '',
            'profileBloodGroup': this.user.blood_group || '',
            'profileWeight': this.user.weight || '',
            'profileCity': this.user.city || '',
            'profileState': this.user.state || '',
            'profileGender': this.user.gender || ''
        };

        Object.keys(fields).forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.value = fields[fieldId];
            }
        });
    }

    async handleProfileUpdate(e) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        console.log('Updating profile with data:', data);

        try {
            const response = await AuthSystem.authManager.makeRequest('/donor/profile/update/', {
                method: 'PUT',
                body: JSON.stringify(data)
            });

            if (response && response.ok) {
                const result = await response.json();
                console.log('Profile update successful:', result);
                AuthSystem.notificationManager.show('Profile updated successfully!', 'success');
                window.DashboardSystem.modalManager.closeModal('profileModal');
                // Reload user data
                await this.loadUserData();
            } else {
                const errorData = await response.json();
                console.error('Profile update failed:', errorData);
                AuthSystem.notificationManager.show(errorData.error || 'Failed to update profile', 'error');
            }
        } catch (error) {
            console.error('Profile update error:', error);
            AuthSystem.notificationManager.show('Failed to update profile. Please try again.', 'error');
        }
    }

    // Utility methods for child classes
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="loading-placeholder">
                    <div class="loading-spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
        }
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="error-placeholder">
                    <div class="error-icon">⚠️</div>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    showEmpty(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="empty-placeholder">
                    <div class="empty-icon">📭</div>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 604800) {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days > 1 ? 's' : ''} ago`;
        } else {
            return this.formatDate(dateString);
        }
    }

    calculateNextEligibleDate(lastDonationDate) {
        if (!lastDonationDate) return null;
        
        const lastDate = new Date(lastDonationDate);
        const nextDate = new Date(lastDate);
        nextDate.setDate(nextDate.getDate() + 56); // 56 days gap
        
        return nextDate;
    }

    isEligibleToDonate(lastDonationDate) {
        if (!lastDonationDate) return true;
        
        const nextEligibleDate = this.calculateNextEligibleDate(lastDonationDate);
        return new Date() >= nextEligibleDate;
    }
}

// Modal utilities
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.setupGlobalListeners();
    }

    setupGlobalListeners() {
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.closeModal(this.activeModal);
            }
        });

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.style.display = 'flex'; // Ensure it's visible
            this.activeModal = modal;
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        console.log('closeModal called with:', modal);
        
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }
        
        if (modal) {
            console.log('Closing modal:', modal.id);
            // Use multiple methods to ensure modal closes
            modal.classList.add('hidden');
            modal.style.display = 'none';
            this.activeModal = null;
            document.body.style.overflow = '';
        } else {
            console.log('Modal not found');
        }
    }

    closeActiveModal() {
        if (this.activeModal) {
            this.closeModal(this.activeModal);
        }
    }
}

// Initialize global instances
const dashboardManager = new DashboardManager();
const modalManager = new ModalManager();

// Export for use in other scripts
window.DashboardSystem = {
    dashboardManager,
    modalManager
};