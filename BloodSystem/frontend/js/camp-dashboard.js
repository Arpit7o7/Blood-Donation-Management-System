// Camp Dashboard JavaScript
class CampDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.currentApplicationId = null;
        this.init();
    }

    init() {
        this.checkAuth();
        this.loadDashboard();
        this.setupEventListeners();
    }

    checkAuth() {
        const token = localStorage.getItem('access_token');
        const userRole = localStorage.getItem('user_role');
        
        if (!token || userRole !== 'CAMP') {
            window.location.href = '../auth/login.html';
            return;
        }
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiBase}/camp/dashboard/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDashboardStats(data);
                this.loadActiveCamps();
                this.loadRecentApplications();
            } else if (response.status === 403) {
                const errorData = await response.json();
                if (errorData.status && errorData.status !== 'APPROVED') {
                    this.showVerificationPending(errorData.status);
                    return;
                }
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateDashboardStats(data) {
        document.getElementById('organizationName').textContent = data.organization || 'Organization';
        document.getElementById('totalCamps').textContent = data.stats.total_camps || 0;
        document.getElementById('activeCamps').textContent = data.stats.active_camps || 0;
        document.getElementById('pendingApplications').textContent = data.stats.pending_applications || 0;
        
        // Update user initials
        const initials = data.organization ? data.organization.substring(0, 2).toUpperCase() : 'C';
        document.getElementById('userInitials').textContent = initials;
    }

    async loadActiveCamps() {
        try {
            const response = await fetch(`${this.apiBase}/camp/camps/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderActiveCamps(data.results.filter(camp => camp.status === 'ACTIVE'));
            }
        } catch (error) {
            console.error('Error loading camps:', error);
        }
    }

    renderActiveCamps(camps) {
        const container = document.getElementById('activeCampsGrid');
        
        if (camps.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🏕️</div>
                    <h3>No Active Camps</h3>
                    <p>Create your first blood donation camp to get started.</p>
                    <button class="btn btn-primary" onclick="campDashboard.openCreateCampModal()">Create Camp</button>
                </div>
            `;
            return;
        }

        container.innerHTML = camps.map(camp => `
            <div class="camp-card">
                <div class="camp-header">
                    <h3 class="camp-name">${camp.name}</h3>
                    <span class="camp-status status-${camp.status.toLowerCase()}">${camp.status}</span>
                </div>
                <div class="camp-details">
                    <div class="detail-item">
                        <span class="detail-icon">📅</span>
                        <span>${this.formatDate(camp.date)} at ${camp.start_time}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon">📍</span>
                        <span>${camp.location}, ${camp.city}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon">👥</span>
                        <span>${camp.applications_count}/${camp.expected_donors} applications</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-icon">🩸</span>
                        <span>${camp.blood_groups_needed.join(', ')}</span>
                    </div>
                </div>
                <div class="camp-actions">
                    <button class="btn btn-outline btn-sm" onclick="campDashboard.viewCampDetails(${camp.id})">
                        View Details
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="campDashboard.viewApplications(${camp.id})">
                        Applications (${camp.applications_count})
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadRecentApplications() {
        try {
            const response = await fetch(`${this.apiBase}/camp/applications/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderRecentApplications(data.results.slice(0, 6));
            }
        } catch (error) {
            console.error('Error loading applications:', error);
        }
    }

    renderRecentApplications(applications) {
        const container = document.getElementById('recentApplicationsGrid');
        
        if (applications.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <h3>No Applications Yet</h3>
                    <p>Donor applications will appear here once your camps are active.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = applications.map(app => `
            <div class="application-card">
                <div class="application-header">
                    <div class="donor-info">
                        <h4 class="donor-name">${app.donor_name}</h4>
                        <span class="blood-group">${app.donor_blood_group}</span>
                    </div>
                    <span class="application-status status-${app.status.toLowerCase()}">${app.status}</span>
                </div>
                <div class="application-details">
                    <div class="detail-item">
                        <span class="detail-label">Camp:</span>
                        <span>${app.camp_name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Age:</span>
                        <span>${app.age} years</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Weight:</span>
                        <span>${app.weight} kg</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Applied:</span>
                        <span>${this.formatDate(app.applied_at)}</span>
                    </div>
                </div>
                ${app.status === 'PENDING' ? `
                    <div class="application-actions">
                        <button class="btn btn-outline btn-sm" onclick="campDashboard.reviewApplication(${app.id})">
                            Review
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Create Camp Modal
        document.getElementById('createCampBtn').addEventListener('click', () => this.openCreateCampModal());
        document.getElementById('closeCampModal').addEventListener('click', () => this.closeCreateCampModal());
        document.getElementById('cancelCampCreation').addEventListener('click', () => this.closeCreateCampModal());
        document.getElementById('createCampForm').addEventListener('submit', (e) => this.handleCreateCamp(e));

        // Application Review Modal
        document.getElementById('closeReviewModal').addEventListener('click', () => this.closeReviewModal());
        document.getElementById('cancelReview').addEventListener('click', () => this.closeReviewModal());
        document.getElementById('approveApplication').addEventListener('click', () => this.handleApplicationReview('APPROVED'));
        document.getElementById('rejectApplication').addEventListener('click', () => this.handleApplicationReview('REJECTED'));

        // Quick Actions
        document.getElementById('reviewApplicationsBtn').addEventListener('click', () => this.viewAllApplications());
        document.getElementById('markAttendanceBtn').addEventListener('click', () => this.showAttendanceFeature());
        document.getElementById('campReportsBtn').addEventListener('click', () => this.showReportsFeature());

        // View All buttons
        document.getElementById('viewAllCampsBtn').addEventListener('click', () => this.viewAllCamps());
        document.getElementById('viewAllApplicationsBtn').addEventListener('click', () => this.viewAllApplications());

        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('campDate').min = today;
    }

    openCreateCampModal() {
        document.getElementById('createCampModal').classList.remove('hidden');
    }

    closeCreateCampModal() {
        document.getElementById('createCampModal').classList.add('hidden');
        document.getElementById('createCampForm').reset();
    }

    async handleCreateCamp(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const bloodGroups = Array.from(document.querySelectorAll('input[name="blood_groups"]:checked'))
            .map(cb => cb.value);
        
        const campData = {
            name: formData.get('name'),
            description: formData.get('description'),
            date: formData.get('date'),
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            location: formData.get('location'),
            address: formData.get('address'),
            city: formData.get('city'),
            state: formData.get('state'),
            pincode: formData.get('pincode'),
            expected_donors: parseInt(formData.get('expected_donors')),
            blood_groups_needed: bloodGroups,
            contact_person: formData.get('contact_person'),
            contact_phone: formData.get('contact_phone'),
            contact_email: formData.get('contact_email')
        };

        console.log('Creating camp with data:', campData);

        try {
            const response = await fetch(`${this.apiBase}/camp/camps/create/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(campData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Camp created successfully:', result);
                this.showSuccess('Camp created successfully!');
                this.closeCreateCampModal();
                this.loadDashboard();
            } else {
                const errorData = await response.json();
                console.error('Camp creation failed:', errorData);
                this.showError(errorData.error || 'Failed to create camp');
            }
        } catch (error) {
            console.error('Error creating camp:', error);
            this.showError('Failed to create camp');
        }
    }

    async reviewApplication(applicationId) {
        this.currentApplicationId = applicationId;
        
        try {
            const response = await fetch(`${this.apiBase}/camp/applications/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                // Find the specific application by ID
                const application = data.results.find(app => app.id === applicationId);
                
                if (application) {
                    this.showApplicationDetails(application);
                    document.getElementById('applicationReviewModal').classList.remove('hidden');
                } else {
                    this.showError('Application not found');
                }
            } else {
                this.showError('Failed to load application details');
            }
        } catch (error) {
            console.error('Error loading application:', error);
            this.showError('Failed to load application details');
        }
    }

    showApplicationDetails(application) {
        const detailsContainer = document.getElementById('applicationDetails');
        detailsContainer.innerHTML = `
            <div class="application-review-details">
                <div class="donor-section">
                    <h4>Donor Information</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Name:</label>
                            <span>${application.donor_name}</span>
                        </div>
                        <div class="info-item">
                            <label>Phone:</label>
                            <span>${application.donor_phone}</span>
                        </div>
                        <div class="info-item">
                            <label>Blood Group:</label>
                            <span class="blood-group">${application.donor_blood_group}</span>
                        </div>
                        <div class="info-item">
                            <label>Age:</label>
                            <span>${application.age} years</span>
                        </div>
                        <div class="info-item">
                            <label>Weight:</label>
                            <span>${application.weight} kg</span>
                        </div>
                        <div class="info-item">
                            <label>Last Donation:</label>
                            <span>${application.last_donation_date || 'Never'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="medical-section">
                    <h4>Medical Information</h4>
                    <div class="info-item">
                        <label>Health Status:</label>
                        <span class="health-status ${application.health_status}">${application.health_status}</span>
                    </div>
                    ${application.health_issues ? `
                        <div class="info-item">
                            <label>Health Issues:</label>
                            <span>${application.health_issues}</span>
                        </div>
                    ` : ''}
                    ${application.medications ? `
                        <div class="info-item">
                            <label>Medications:</label>
                            <span>${application.medications}</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="camp-section">
                    <h4>Camp Details</h4>
                    <div class="info-item">
                        <label>Camp:</label>
                        <span>${application.camp_name}</span>
                    </div>
                    <div class="info-item">
                        <label>Date:</label>
                        <span>${this.formatDate(application.camp_date)}</span>
                    </div>
                    <div class="info-item">
                        <label>Applied:</label>
                        <span>${this.formatDate(application.applied_at)}</span>
                    </div>
                </div>
            </div>
        `;
    }

    closeReviewModal() {
        document.getElementById('applicationReviewModal').classList.add('hidden');
        this.currentApplicationId = null;
        document.getElementById('reviewNotes').value = '';
    }

    async handleApplicationReview(decision) {
        if (!this.currentApplicationId) return;

        const notes = document.getElementById('reviewNotes').value;

        try {
            const response = await fetch(`${this.apiBase}/camp/applications/review/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    application_id: this.currentApplicationId,
                    decision: decision,
                    notes: notes
                })
            });

            if (response.ok) {
                this.showSuccess(`Application ${decision.toLowerCase()} successfully!`);
                this.closeReviewModal();
                this.loadDashboard();
                
                // Refresh notifications for the donor (this won't work directly, but good practice)
                // The donor will see the notification when they refresh or navigate
                console.log('Application reviewed - donor should receive notification');
            } else {
                const errorData = await response.json();
                this.showError(errorData.error || 'Failed to review application');
            }
        } catch (error) {
            console.error('Error reviewing application:', error);
            this.showError('Failed to review application');
        }
    }

    viewCampDetails(campId) {
        // TODO: Implement camp details view
        this.showInfo('Camp details feature coming soon!');
    }

    viewApplications(campId) {
        // TODO: Implement applications view for specific camp
        this.showInfo('Camp applications view coming soon!');
    }

    viewAllCamps() {
        // TODO: Implement all camps view
        this.showInfo('All camps view coming soon!');
    }

    viewAllApplications() {
        // TODO: Implement all applications view
        this.showInfo('All applications view coming soon!');
    }

    showAttendanceFeature() {
        this.showInfo('Attendance marking feature coming soon!');
    }

    showReportsFeature() {
        this.showInfo('Camp reports feature coming soon!');
    }

    showVerificationPending(status) {
        const container = document.querySelector('.dashboard-main');
        container.innerHTML = `
            <div class="verification-pending">
                <div class="verification-icon">⏳</div>
                <h2>Organization Verification ${status}</h2>
                <p>Your organization is currently under review by our admin team.</p>
                <p>You'll be able to access the full dashboard once your organization is approved.</p>
                <div class="verification-status">
                    <span class="status-badge status-${status.toLowerCase()}">${status}</span>
                </div>
            </div>
        `;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }
}

// Initialize dashboard when page loads
const campDashboard = new CampDashboard();