// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.currentOrganizationId = null;
        this.currentOrganizationType = null;
        this.currentEmergencyId = null;
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
        
        if (!token || userRole !== 'ADMIN') {
            window.location.href = '../auth/login.html';
            return;
        }
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiBase}/admin/dashboard/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateDashboardStats(data);
                this.loadPendingVerifications();
                this.loadEmergencyRequests();
                this.loadSystemOverview();
            } else {
                console.error('Failed to load dashboard');
                this.showError('Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateDashboardStats(data) {
        document.getElementById('totalUsers').textContent = data.stats?.total_users || 0;
        document.getElementById('pendingVerifications').textContent = data.stats?.pending_verifications || 0;
        document.getElementById('emergencyRequests').textContent = data.stats?.emergency_requests || 0;
        document.getElementById('totalDonations').textContent = data.stats?.total_donations || 0;
        
        // Update user distribution
        if (data.user_distribution) {
            document.getElementById('donorCount').textContent = data.user_distribution.donors || 0;
            document.getElementById('hospitalCount').textContent = data.user_distribution.hospitals || 0;
            document.getElementById('campCount').textContent = data.user_distribution.camps || 0;
            document.getElementById('patientCount').textContent = data.user_distribution.patients || 0;
        }
    }

    async loadPendingVerifications() {
        try {
            const response = await fetch(`${this.apiBase}/admin/pending-verifications/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderPendingVerifications(data.results || []);
            }
        } catch (error) {
            console.error('Error loading verifications:', error);
        }
    }

    renderPendingVerifications(verifications) {
        const container = document.getElementById('verificationsGrid');
        
        if (verifications.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✅</div>
                    <h3>No Pending Verifications</h3>
                    <p>All organizations are currently verified.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = verifications.map(org => `
            <div class="verification-card">
                <div class="verification-header">
                    <div class="org-info">
                        <h4 class="org-name">${org.name}</h4>
                        <span class="org-type">${org.type}</span>
                    </div>
                    <span class="verification-status status-pending">PENDING</span>
                </div>
                <div class="verification-details">
                    <div class="detail-item">
                        <span class="detail-label">Registration:</span>
                        <span>${org.registration_number}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Location:</span>
                        <span>${org.city}, ${org.state}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Contact:</span>
                        <span>${org.contact_email}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Applied:</span>
                        <span>${this.formatDate(org.created_at)}</span>
                    </div>
                </div>
                <div class="verification-actions">
                    <button class="btn btn-outline btn-sm" onclick="adminDashboard.reviewOrganization('${org.id}', '${org.type}')">
                        Review
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadEmergencyRequests() {
        try {
            const response = await fetch(`${this.apiBase}/admin/emergency-requests/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderEmergencyRequests(data.results || []);
            }
        } catch (error) {
            console.error('Error loading emergency requests:', error);
        }
    }

    renderEmergencyRequests(requests) {
        const container = document.getElementById('emergencyGrid');
        
        if (requests.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🚨</div>
                    <h3>No Emergency Requests</h3>
                    <p>No emergency blood requests require admin approval.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = requests.map(req => `
            <div class="emergency-card">
                <div class="emergency-header">
                    <div class="request-info">
                        <h4 class="patient-name">${req.patient_name}</h4>
                        <span class="blood-group">${req.blood_group}</span>
                    </div>
                    <span class="urgency-level urgency-${req.urgency.toLowerCase()}">${req.urgency}</span>
                </div>
                <div class="emergency-details">
                    <div class="detail-item">
                        <span class="detail-label">Hospital:</span>
                        <span>${req.hospital_name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Units:</span>
                        <span>${req.units_needed} units</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Required By:</span>
                        <span>${this.formatDateTime(req.required_by)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Reason:</span>
                        <span class="emergency-reason">${req.emergency_reason}</span>
                    </div>
                </div>
                <div class="emergency-actions">
                    <button class="btn btn-outline btn-sm" onclick="adminDashboard.reviewEmergency('${req.id}')">
                        Review
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadSystemOverview() {
        // Load blood stock overview
        this.loadBloodStockOverview();
        
        // Load recent activity
        this.loadRecentActivity();
    }

    async loadBloodStockOverview() {
        try {
            const response = await fetch(`${this.apiBase}/admin/blood-stock-overview/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderBloodStockOverview(data.stock_summary || {});
            }
        } catch (error) {
            console.error('Error loading blood stock:', error);
            document.getElementById('bloodStockOverview').innerHTML = '<p>Failed to load blood stock data</p>';
        }
    }

    renderBloodStockOverview(stockSummary) {
        const container = document.getElementById('bloodStockOverview');
        const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];
        
        container.innerHTML = bloodGroups.map(group => {
            const stock = stockSummary[group] || 0;
            const statusClass = stock < 10 ? 'low' : stock < 50 ? 'medium' : 'good';
            
            return `
                <div class="blood-stock-item">
                    <span class="blood-group">${group}</span>
                    <span class="stock-count stock-${statusClass}">${stock} units</span>
                </div>
            `;
        }).join('');
    }

    async loadRecentActivity() {
        try {
            const response = await fetch(`${this.apiBase}/admin/recent-activity/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderRecentActivity(data.activities || []);
            }
        } catch (error) {
            console.error('Error loading activity:', error);
            document.getElementById('activityFeed').innerHTML = '<p>Failed to load activity data</p>';
        }
    }

    renderRecentActivity(activities) {
        const container = document.getElementById('activityFeed');
        
        if (activities.length === 0) {
            container.innerHTML = '<p>No recent activity</p>';
            return;
        }

        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">${this.getActivityIcon(activity.type)}</div>
                <div class="activity-content">
                    <div class="activity-text">${activity.description}</div>
                    <div class="activity-time">${this.formatDateTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Verification Modal
        document.getElementById('closeVerificationModal').addEventListener('click', () => this.closeVerificationModal());
        document.getElementById('cancelVerification').addEventListener('click', () => this.closeVerificationModal());
        document.getElementById('approveOrganization').addEventListener('click', () => this.handleOrganizationReview('APPROVED'));
        document.getElementById('rejectOrganization').addEventListener('click', () => this.handleOrganizationReview('REJECTED'));

        // Emergency Modal
        document.getElementById('closeEmergencyModal').addEventListener('click', () => this.closeEmergencyModal());
        document.getElementById('cancelEmergencyReview').addEventListener('click', () => this.closeEmergencyModal());
        document.getElementById('approveEmergency').addEventListener('click', () => this.handleEmergencyReview('APPROVED'));
        document.getElementById('rejectEmergency').addEventListener('click', () => this.handleEmergencyReview('REJECTED'));

        // Quick Actions
        document.getElementById('reviewEmergencyBtn').addEventListener('click', () => this.showEmergencyRequests());
        document.getElementById('verifyOrganizationsBtn').addEventListener('click', () => this.showVerifications());
        document.getElementById('systemStatsBtn').addEventListener('click', () => this.showSystemStats());
        document.getElementById('auditLogsBtn').addEventListener('click', () => this.showAuditLogs());

        // View All buttons
        document.getElementById('viewAllVerificationsBtn').addEventListener('click', () => this.showVerifications());
        document.getElementById('viewAllEmergencyBtn').addEventListener('click', () => this.showEmergencyRequests());
    }

    async reviewOrganization(orgId, orgType) {
        this.currentOrganizationId = orgId;
        this.currentOrganizationType = orgType;
        
        try {
            const endpoint = orgType === 'HOSPITAL' ? 'hospital-details' : 'camp-details';
            const response = await fetch(`${this.apiBase}/admin/${endpoint}/${orgId}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.showOrganizationDetails(data);
                document.getElementById('verificationModal').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading organization:', error);
            this.showError('Failed to load organization details');
        }
    }

    showOrganizationDetails(org) {
        const detailsContainer = document.getElementById('organizationDetails');
        
        if (this.currentOrganizationType === 'HOSPITAL') {
            detailsContainer.innerHTML = `
                <div class="organization-details">
                    <div class="org-section">
                        <h4>Hospital Information</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Hospital Name:</label>
                                <span>${org.hospital_name}</span>
                            </div>
                            <div class="info-item">
                                <label>Registration Number:</label>
                                <span>${org.registration_number}</span>
                            </div>
                            <div class="info-item">
                                <label>Issuing Authority:</label>
                                <span>${org.issuing_authority}</span>
                            </div>
                            <div class="info-item">
                                <label>Year of Registration:</label>
                                <span>${org.year_of_registration}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="org-section">
                        <h4>Contact Information</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Email:</label>
                                <span>${org.user.email}</span>
                            </div>
                            <div class="info-item">
                                <label>Phone:</label>
                                <span>${org.user.phone}</span>
                            </div>
                            <div class="info-item">
                                <label>Authorized Person:</label>
                                <span>${org.authorized_person_name}</span>
                            </div>
                            <div class="info-item">
                                <label>Designation:</label>
                                <span>${org.authorized_person_designation}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="org-section">
                        <h4>Address</h4>
                        <p>${org.address_line}, ${org.area}, ${org.city}, ${org.district}, ${org.state} - ${org.pincode}</p>
                    </div>
                    
                    ${org.has_blood_bank ? `
                        <div class="org-section">
                            <h4>Blood Bank Details</h4>
                            <div class="info-grid">
                                <div class="info-item">
                                    <label>Blood Bank License:</label>
                                    <span>${org.blood_bank_license}</span>
                                </div>
                                <div class="info-item">
                                    <label>Storage Capacity:</label>
                                    <span>${org.storage_capacity} units</span>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            detailsContainer.innerHTML = `
                <div class="organization-details">
                    <div class="org-section">
                        <h4>Organization Information</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Organization Name:</label>
                                <span>${org.organization_name}</span>
                            </div>
                            <div class="info-item">
                                <label>Type:</label>
                                <span>${org.organization_type}</span>
                            </div>
                            <div class="info-item">
                                <label>Registration Number:</label>
                                <span>${org.registration_number}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="org-section">
                        <h4>Contact Information</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Email:</label>
                                <span>${org.user.email}</span>
                            </div>
                            <div class="info-item">
                                <label>Phone:</label>
                                <span>${org.user.phone}</span>
                            </div>
                            <div class="info-item">
                                <label>Contact Person:</label>
                                <span>${org.contact_person_name}</span>
                            </div>
                            <div class="info-item">
                                <label>Designation:</label>
                                <span>${org.contact_person_designation}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="org-section">
                        <h4>Address</h4>
                        <p>${org.address_line}, ${org.city}, ${org.state} - ${org.pincode}</p>
                    </div>
                </div>
            `;
        }
    }

    closeVerificationModal() {
        document.getElementById('verificationModal').classList.add('hidden');
        this.currentOrganizationId = null;
        this.currentOrganizationType = null;
        document.getElementById('verificationNotes').value = '';
    }

    async handleOrganizationReview(decision) {
        if (!this.currentOrganizationId || !this.currentOrganizationType) return;

        const notes = document.getElementById('verificationNotes').value;
        const endpoint = this.currentOrganizationType === 'HOSPITAL' ? 'verify-hospital' : 'verify-camp';

        try {
            const response = await fetch(`${this.apiBase}/admin/${endpoint}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    organization_id: this.currentOrganizationId,
                    decision: decision,
                    notes: notes
                })
            });

            if (response.ok) {
                this.showSuccess(`Organization ${decision.toLowerCase()} successfully!`);
                this.closeVerificationModal();
                this.loadDashboard();
            } else {
                const errorData = await response.json();
                this.showError(errorData.error || 'Failed to review organization');
            }
        } catch (error) {
            console.error('Error reviewing organization:', error);
            this.showError('Failed to review organization');
        }
    }

    async reviewEmergency(emergencyId) {
        this.currentEmergencyId = emergencyId;
        
        try {
            const response = await fetch(`${this.apiBase}/admin/emergency-details/${emergencyId}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.showEmergencyDetails(data);
                document.getElementById('emergencyModal').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading emergency:', error);
            this.showError('Failed to load emergency details');
        }
    }

    showEmergencyDetails(emergency) {
        const detailsContainer = document.getElementById('emergencyDetails');
        detailsContainer.innerHTML = `
            <div class="emergency-review-details">
                <div class="emergency-section">
                    <h4>Patient Information</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Patient Name:</label>
                            <span>${emergency.patient_name}</span>
                        </div>
                        <div class="info-item">
                            <label>Blood Group:</label>
                            <span class="blood-group">${emergency.blood_group}</span>
                        </div>
                        <div class="info-item">
                            <label>Units Needed:</label>
                            <span>${emergency.units_needed} units</span>
                        </div>
                        <div class="info-item">
                            <label>Required By:</label>
                            <span>${this.formatDateTime(emergency.required_by)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="emergency-section">
                    <h4>Hospital Information</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Hospital:</label>
                            <span>${emergency.hospital_name}</span>
                        </div>
                        <div class="info-item">
                            <label>Location:</label>
                            <span>${emergency.hospital_location}</span>
                        </div>
                        <div class="info-item">
                            <label>Contact:</label>
                            <span>${emergency.hospital_contact}</span>
                        </div>
                    </div>
                </div>
                
                <div class="emergency-section">
                    <h4>Emergency Details</h4>
                    <div class="info-item">
                        <label>Urgency Level:</label>
                        <span class="urgency-level urgency-${emergency.urgency.toLowerCase()}">${emergency.urgency}</span>
                    </div>
                    <div class="info-item">
                        <label>Reason:</label>
                        <span>${emergency.emergency_reason}</span>
                    </div>
                    <div class="info-item">
                        <label>Justification:</label>
                        <div class="emergency-justification">${emergency.emergency_justification}</div>
                    </div>
                    <div class="info-item">
                        <label>Medical Condition:</label>
                        <div class="medical-condition">${emergency.medical_condition || 'Not specified'}</div>
                    </div>
                </div>
                
                <div class="emergency-section">
                    <h4>Request Timeline</h4>
                    <div class="info-item">
                        <label>Requested:</label>
                        <span>${this.formatDateTime(emergency.created_at)}</span>
                    </div>
                    <div class="info-item">
                        <label>Status:</label>
                        <span class="request-status status-${emergency.status.toLowerCase()}">${emergency.status}</span>
                    </div>
                </div>
            </div>
        `;
    }

    closeEmergencyModal() {
        document.getElementById('emergencyModal').classList.add('hidden');
        this.currentEmergencyId = null;
        document.getElementById('emergencyNotes').value = '';
    }

    async handleEmergencyReview(decision) {
        if (!this.currentEmergencyId) return;

        const notes = document.getElementById('emergencyNotes').value;

        try {
            const response = await fetch(`${this.apiBase}/admin/review-emergency/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_id: this.currentEmergencyId,
                    decision: decision,
                    notes: notes
                })
            });

            if (response.ok) {
                this.showSuccess(`Emergency request ${decision.toLowerCase()} successfully!`);
                this.closeEmergencyModal();
                this.loadDashboard();
            } else {
                const errorData = await response.json();
                this.showError(errorData.error || 'Failed to review emergency request');
            }
        } catch (error) {
            console.error('Error reviewing emergency:', error);
            this.showError('Failed to review emergency request');
        }
    }

    showEmergencyRequests() {
        this.showInfo('Detailed emergency requests view coming soon!');
    }

    showVerifications() {
        this.showInfo('Detailed verifications view coming soon!');
    }

    showSystemStats() {
        this.showInfo('Detailed system statistics coming soon!');
    }

    showAuditLogs() {
        this.showInfo('Audit logs view coming soon!');
    }

    getActivityIcon(type) {
        const icons = {
            'user_registration': '👤',
            'organization_verification': '✅',
            'emergency_request': '🚨',
            'blood_donation': '🩸',
            'camp_creation': '🏕️',
            'system_alert': '⚠️'
        };
        return icons[type] || '📝';
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

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
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
const adminDashboard = new AdminDashboard();