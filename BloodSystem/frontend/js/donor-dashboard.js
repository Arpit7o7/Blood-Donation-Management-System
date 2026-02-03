// Donor Dashboard JavaScript

class DonorDashboard {
    constructor() {
        this.camps = [];
        this.alerts = [];
        this.donorProfile = null;
        this.currentCampId = null;
        this.init();
    }

    async init() {
        // Wait for dashboard manager to initialize
        await new Promise(resolve => {
            const checkDashboard = () => {
                if (window.DashboardSystem?.dashboardManager?.user) {
                    resolve();
                } else {
                    setTimeout(checkDashboard, 100);
                }
            };
            checkDashboard();
        });

        this.donorProfile = window.DashboardSystem.dashboardManager.user;
        this.setupEventListeners();
        await this.loadDashboardData();
    }

    setupEventListeners() {
        // Quick action buttons
        document.getElementById('findCampsBtn')?.addEventListener('click', () => {
            this.showAllCamps();
        });

        document.getElementById('hospitalAlertsBtn')?.addEventListener('click', () => {
            this.showAllAlerts();
        });

        document.getElementById('donationHistoryBtn')?.addEventListener('click', () => {
            this.showDonationHistory();
        });

        // View all buttons
        document.getElementById('viewAllCampsBtn')?.addEventListener('click', () => {
            this.showAllCamps();
        });

        document.getElementById('viewAllAlertsBtn')?.addEventListener('click', () => {
            this.showAllAlerts();
        });

        document.getElementById('viewAllNotificationsBtn')?.addEventListener('click', () => {
            this.showAllNotifications();
        });

        // Modal event listeners
        this.setupModalListeners();
    }

    setupModalListeners() {
        // Camp application modal
        const closeCampModal = document.getElementById('closeCampModal');
        const cancelApplication = document.getElementById('cancelApplication');
        const campApplicationForm = document.getElementById('campApplicationForm');

        closeCampModal?.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Close modal button clicked');
            window.DashboardSystem.modalManager.closeModal('campApplicationModal');
        });

        cancelApplication?.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Cancel application button clicked');
            window.DashboardSystem.modalManager.closeModal('campApplicationModal');
        });

        campApplicationForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCampApplication(e);
        });
    }

    async loadDashboardData() {
        // Load donor stats
        await this.loadDonorStats();
        
        // Load camps and alerts in parallel
        await Promise.all([
            this.loadNearbyCamps(),
            this.loadHospitalAlerts(),
            this.loadRecentNotifications()
        ]);
    }

    async loadDonorStats() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/donor/stats/');
            if (response && response.ok) {
                const stats = await response.json();
                this.updateDonorStats(stats);
            } else {
                // Mock data for now
                this.updateDonorStats({
                    total_donations: this.donorProfile.total_donations || 0,
                    last_donation_date: this.donorProfile.last_donation_date,
                    next_eligible_date: this.calculateNextEligibleDate()
                });
            }
        } catch (error) {
            console.error('Failed to load donor stats:', error);
            // Use profile data as fallback
            this.updateDonorStats({
                total_donations: this.donorProfile.total_donations || 0,
                last_donation_date: this.donorProfile.last_donation_date,
                next_eligible_date: this.calculateNextEligibleDate()
            });
        }
    }

    updateDonorStats(stats) {
        const totalDonationsEl = document.getElementById('totalDonations');
        const lastDonationEl = document.getElementById('lastDonation');
        const nextEligibleEl = document.getElementById('nextEligible');

        if (totalDonationsEl) {
            totalDonationsEl.textContent = stats.total_donations || 0;
        }

        if (lastDonationEl) {
            if (stats.last_donation_date) {
                lastDonationEl.textContent = window.DashboardSystem.dashboardManager.formatDate(stats.last_donation_date);
            } else {
                lastDonationEl.textContent = 'Never';
            }
        }

        if (nextEligibleEl) {
            if (stats.next_eligible_date) {
                const nextDate = new Date(stats.next_eligible_date);
                const today = new Date();
                if (nextDate <= today) {
                    nextEligibleEl.textContent = 'Now';
                    nextEligibleEl.style.color = 'var(--primary-red)';
                } else {
                    nextEligibleEl.textContent = window.DashboardSystem.dashboardManager.formatDate(stats.next_eligible_date);
                }
            } else {
                nextEligibleEl.textContent = 'Now';
                nextEligibleEl.style.color = 'var(--primary-red)';
            }
        }
    }

    calculateNextEligibleDate() {
        if (!this.donorProfile.last_donation_date) return null;
        
        const lastDate = new Date(this.donorProfile.last_donation_date);
        const nextDate = new Date(lastDate);
        nextDate.setDate(nextDate.getDate() + 56);
        
        return nextDate.toISOString().split('T')[0];
    }

    async loadNearbyCamps() {
        window.DashboardSystem.dashboardManager.showLoading('campsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/donor/camps/suggestions/');
            if (response && response.ok) {
                const data = await response.json();
                this.camps = data.results || [];
                this.renderCamps();
            } else {
                // Mock data for demonstration
                this.camps = this.getMockCamps();
                this.renderCamps();
            }
        } catch (error) {
            console.error('Failed to load camps:', error);
            window.DashboardSystem.dashboardManager.showError('campsGrid', 'Failed to load camps');
        }
    }

    getMockCamps() {
        return [
            {
                id: 1,
                name: 'City Hospital Blood Drive',
                organizer: 'City General Hospital',
                location: 'Downtown Community Center',
                date: '2024-02-15',
                start_time: '09:00',
                end_time: '17:00',
                blood_groups_needed: ['O+', 'A+', 'B+'],
                is_active: true
            },
            {
                id: 2,
                name: 'Red Cross Mobile Camp',
                organizer: 'American Red Cross',
                location: 'University Campus',
                date: '2024-02-18',
                start_time: '10:00',
                end_time: '16:00',
                blood_groups_needed: ['O-', 'AB+'],
                is_active: true
            }
        ];
    }

    renderCamps() {
        const campsGrid = document.getElementById('campsGrid');
        if (!campsGrid) return;

        if (this.camps.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('campsGrid', 'No nearby camps available');
            return;
        }

        campsGrid.innerHTML = this.camps.slice(0, 3).map(camp => `
            <div class="camp-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">${camp.name}</div>
                        <div class="card-subtitle">${camp.organizer}</div>
                    </div>
                    <div class="card-badge badge-active">Active</div>
                </div>
                <div class="card-info">
                    <div class="info-item">
                        <span class="info-icon">📍</span>
                        <span>${camp.location}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">📅</span>
                        <span>${window.DashboardSystem.dashboardManager.formatDate(camp.date)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">⏰</span>
                        <span>${camp.start_time} - ${camp.end_time}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">🩸</span>
                        <span>Need: ${camp.blood_groups_needed?.join(', ') || 'All types'}</span>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary btn-small" onclick="donorDashboard.applyCamp(${camp.id})">
                        Apply Now
                    </button>
                    <button class="btn btn-outline btn-small" onclick="donorDashboard.viewCampDetails(${camp.id})">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadHospitalAlerts() {
        window.DashboardSystem.dashboardManager.showLoading('alertsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/donor/hospital-alerts/');
            if (response && response.ok) {
                const data = await response.json();
                this.alerts = data.results || [];
                this.renderAlerts();
            } else {
                // Mock data for demonstration
                this.alerts = this.getMockAlerts();
                this.renderAlerts();
            }
        } catch (error) {
            console.error('Failed to load alerts:', error);
            window.DashboardSystem.dashboardManager.showError('alertsGrid', 'Failed to load hospital alerts');
        }
    }

    getMockAlerts() {
        return [
            {
                id: 1,
                hospital_name: 'Metro General Hospital',
                blood_group: 'O-',
                units_needed: 5,
                urgency: 'EMERGENCY',
                location: 'Downtown Metro',
                created_at: '2024-02-10T10:30:00Z',
                reason: 'Emergency surgery patient'
            },
            {
                id: 2,
                hospital_name: 'Children\'s Medical Center',
                blood_group: 'A+',
                units_needed: 3,
                urgency: 'URGENT',
                location: 'Pediatric Wing',
                created_at: '2024-02-10T14:15:00Z',
                reason: 'Pediatric patient needs'
            }
        ];
    }

    renderAlerts() {
        const alertsGrid = document.getElementById('alertsGrid');
        if (!alertsGrid) return;

        if (this.alerts.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('alertsGrid', 'No hospital alerts at this time');
            return;
        }

        alertsGrid.innerHTML = this.alerts.slice(0, 3).map(alert => `
            <div class="alert-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">${alert.hospital_name}</div>
                        <div class="card-subtitle">${alert.reason || 'Blood needed urgently'}</div>
                    </div>
                    <div class="card-badge ${alert.urgency === 'EMERGENCY' ? 'badge-emergency' : 'badge-urgent'}">
                        ${alert.urgency}
                    </div>
                </div>
                <div class="card-info">
                    <div class="info-item">
                        <span class="info-icon">🩸</span>
                        <span>${alert.blood_group} - ${alert.units_needed} units</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">📍</span>
                        <span>${alert.location}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-icon">⏰</span>
                        <span>${window.DashboardSystem.dashboardManager.formatTimeAgo(alert.created_at)}</span>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary btn-small" onclick="donorDashboard.respondToAlert(${alert.id})">
                        Respond
                    </button>
                    <button class="btn btn-outline btn-small" onclick="donorDashboard.viewAlertDetails(${alert.id})">
                        Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadRecentNotifications() {
        const notificationsList = document.getElementById('notificationsList');
        if (!notificationsList) return;

        window.DashboardSystem.dashboardManager.showLoading('notificationsList');
        
        try {
            // Load fresh notifications from API
            const response = await AuthSystem.authManager.makeRequest('/notifications/');
            let notifications = [];
            
            if (response && response.ok) {
                const data = await response.json();
                notifications = data.results || [];
                // Update the dashboard manager's notifications
                window.DashboardSystem.dashboardManager.notifications = notifications;
                window.DashboardSystem.dashboardManager.updateNotificationBadge();
            } else {
                // Fallback to dashboard manager notifications
                notifications = window.DashboardSystem.dashboardManager.notifications.slice(0, 5);
            }
            
            if (notifications.length === 0) {
                window.DashboardSystem.dashboardManager.showEmpty('notificationsList', 'No recent notifications');
                return;
            }

            notificationsList.innerHTML = notifications.slice(0, 5).map(notification => `
                <div class="notification-item ${!notification.is_read ? 'unread' : ''}">
                    <div class="notification-icon ${this.getNotificationIconClass(notification.notification_type)}">
                        ${this.getNotificationIcon(notification.notification_type)}
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">${notification.title}</div>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${window.DashboardSystem.dashboardManager.formatTimeAgo(notification.created_at)}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load notifications:', error);
            window.DashboardSystem.dashboardManager.showError('notificationsList', 'Failed to load notifications');
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'CAMP_APPROVAL': '✅',
            'CAMP_REJECTION': '❌',
            'HOSPITAL_APPROVAL': '🏥',
            'HOSPITAL_REJECTION': '❌',
            'EMERGENCY_ALERT': '🚨',
            'DISASTER_ALERT': '⚠️',
            'ATTENDANCE_MARKED': '✓',
            'BLOOD_REQUEST': '🩸'
        };
        return icons[type] || 'ℹ️';
    }

    getNotificationIconClass(type) {
        if (type.includes('APPROVAL') || type.includes('ATTENDANCE')) return 'success';
        if (type.includes('REJECTION')) return 'error';
        if (type.includes('ALERT')) return 'error';
        return 'info';
    }

    // Action handlers
    applyCamp(campId) {
        const camp = this.camps.find(c => c.id === campId);
        if (!camp) return;

        this.showCampApplicationModal(camp);
    }

    showCampApplicationModal(camp) {
        // Store the current camp ID for form submission
        this.currentCampId = camp.id;
        
        // Populate camp details
        const campDetails = document.getElementById('campDetails');
        if (campDetails) {
            campDetails.innerHTML = `
                <div class="camp-info-card">
                    <h4>${camp.name}</h4>
                    <p><strong>Organizer:</strong> ${camp.organizer}</p>
                    <p><strong>Location:</strong> ${camp.location}</p>
                    <p><strong>Date:</strong> ${window.DashboardSystem.dashboardManager.formatDate(camp.date)}</p>
                    <p><strong>Time:</strong> ${camp.start_time} - ${camp.end_time}</p>
                    <p><strong>Blood Groups Needed:</strong> ${camp.blood_groups_needed?.join(', ') || 'All types'}</p>
                </div>
            `;
        }

        // Pre-fill form with donor data
        if (this.donorProfile) {
            const ageInput = document.getElementById('age');
            const weightInput = document.getElementById('weight');
            const lastDonationInput = document.getElementById('lastDonationDate');

            if (ageInput && this.donorProfile.date_of_birth) {
                const age = this.calculateAge(this.donorProfile.date_of_birth);
                ageInput.value = age;
            }

            if (weightInput && this.donorProfile.weight) {
                weightInput.value = this.donorProfile.weight;
            }

            if (lastDonationInput && this.donorProfile.last_donation_date) {
                lastDonationInput.value = this.donorProfile.last_donation_date;
            }
        }

        window.DashboardSystem.modalManager.openModal('campApplicationModal');
    }

    calculateAge(birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    }

    async handleCampApplication(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        // Get the camp ID from the modal or form
        const campId = this.currentCampId;
        if (!campId) {
            AuthSystem.notificationManager.show('Camp information missing. Please try again.', 'error');
            return;
        }
        
        try {
            const applicationData = {
                camp_id: campId,
                age: parseInt(formData.get('age')),
                weight: parseFloat(formData.get('weight')),
                last_donation_date: formData.get('lastDonationDate') || null,
                health_status: formData.get('healthStatus'),
                health_issues: formData.get('healthIssues') || '',
                medications: formData.get('medications') || '',
                consent: formData.get('consent') === 'on'
            };

            console.log('Submitting camp application:', applicationData);

            const response = await AuthSystem.authManager.makeRequest('/donor/camps/apply/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(applicationData)
            });

            if (response && response.ok) {
                const result = await response.json();
                console.log('Application submitted successfully:', result);
                AuthSystem.notificationManager.show('Camp application submitted successfully!', 'success');
                window.DashboardSystem.modalManager.closeModal('campApplicationModal');
                
                // Refresh camps to show updated status
                await this.loadNearbyCamps();
            } else {
                const errorData = await response.json();
                console.error('Application submission failed:', errorData);
                AuthSystem.notificationManager.show(errorData.error || 'Failed to submit application. Please try again.', 'error');
            }
            
        } catch (error) {
            console.error('Failed to submit camp application:', error);
            AuthSystem.notificationManager.show('Failed to submit application. Please try again.', 'error');
        }
    }

    viewCampDetails(campId) {
        AuthSystem.notificationManager.show('Camp details view coming soon!', 'info');
    }

    respondToAlert(alertId) {
        AuthSystem.notificationManager.show('Hospital alert response coming soon!', 'info');
    }

    viewAlertDetails(alertId) {
        AuthSystem.notificationManager.show('Alert details view coming soon!', 'info');
    }

    showProfileUpdate() {
        // Use the dashboard manager's profile modal
        window.DashboardSystem.dashboardManager.showProfileModal();
    }

    showAllCamps() {
        AuthSystem.notificationManager.show('All camps view coming soon!', 'info');
    }

    showAllAlerts() {
        AuthSystem.notificationManager.show('All alerts view coming soon!', 'info');
    }

    showDonationHistory() {
        AuthSystem.notificationManager.show('Donation history coming soon!', 'info');
    }

    showProfileUpdate() {
        AuthSystem.notificationManager.show('Profile update coming soon!', 'info');
    }

    showAllNotifications() {
        AuthSystem.notificationManager.show('All notifications view coming soon!', 'info');
    }
}

// Initialize donor dashboard
const donorDashboard = new DonorDashboard();