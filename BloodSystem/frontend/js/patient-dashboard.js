// Patient Dashboard JavaScript

class PatientDashboard {
    constructor() {
        this.bloodRequests = [];
        this.hospitals = [];
        this.patientProfile = null;
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

        this.patientProfile = window.DashboardSystem.dashboardManager.user;
        this.setupEventListeners();
        await this.loadDashboardData();
    }

    setupEventListeners() {
        // Quick action buttons
        document.getElementById('requestBloodBtn')?.addEventListener('click', () => {
            this.showBloodRequestModal('NORMAL');
        });

        document.getElementById('emergencyRequestBtn')?.addEventListener('click', () => {
            this.showBloodRequestModal('EMERGENCY');
        });

        document.getElementById('findHospitalsBtn')?.addEventListener('click', () => {
            this.showAllHospitals();
        });

        document.getElementById('requestHistoryBtn')?.addEventListener('click', () => {
            this.showRequestHistory();
        });

        // View all buttons
        document.getElementById('viewAllRequestsBtn')?.addEventListener('click', () => {
            this.showAllRequests();
        });

        document.getElementById('viewAllHospitalsBtn')?.addEventListener('click', () => {
            this.showAllHospitals();
        });

        // Modal event listeners
        this.setupModalListeners();
    }

    setupModalListeners() {
        // Blood request modal
        const closeRequestModal = document.getElementById('closeRequestModal');
        const cancelRequest = document.getElementById('cancelRequest');
        const bloodRequestForm = document.getElementById('bloodRequestForm');
        const requestTypeSelect = document.getElementById('requestType');

        closRequestModal?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('bloodRequestModal');
        });

        cancelRequest?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('bloodRequestModal');
        });

        // Request type change handler
        requestTypeSelect?.addEventListener('change', (e) => {
            this.handleRequestTypeChange(e.target.value);
        });

        // Form submission
        bloodRequestForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBloodRequestSubmission(e);
        });

        // Emergency justification validation
        const emergencyJustification = document.getElementById('emergencyJustification');
        emergencyJustification?.addEventListener('input', (e) => {
            this.validateEmergencyJustification(e.target);
        });
    }

    async loadDashboardData() {
        // Load patient stats
        await this.loadPatientStats();
        
        // Load data in parallel
        await Promise.all([
            this.loadActiveRequests(),
            this.loadNearbyHospitals()
        ]);
    }

    async loadPatientStats() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/patient/dashboard/');
            if (response && response.ok) {
                const data = await response.json();
                this.updatePatientStats(data.stats);
                
                // Update patient name
                const patientNameEl = document.getElementById('patientName');
                if (patientNameEl) {
                    patientNameEl.textContent = data.patient || 'Patient';
                }
            }
        } catch (error) {
            console.error('Failed to load patient stats:', error);
        }
    }

    updatePatientStats(stats) {
        const totalRequestsEl = document.getElementById('totalRequests');
        const activeRequestsEl = document.getElementById('activeRequests');
        const emergencyRequestsEl = document.getElementById('emergencyRequests');

        if (totalRequestsEl) totalRequestsEl.textContent = stats.total_requests || 0;
        if (activeRequestsEl) activeRequestsEl.textContent = stats.active_requests || 0;
        if (emergencyRequestsEl) emergencyRequestsEl.textContent = stats.emergency_requests || 0;
    }

    async loadActiveRequests() {
        window.DashboardSystem.dashboardManager.showLoading('activeRequestsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/patient/blood-requests/');
            if (response && response.ok) {
                const data = await response.json();
                this.bloodRequests = data.results || [];
                this.renderActiveRequests();
            } else {
                window.DashboardSystem.dashboardManager.showError('activeRequestsGrid', 'Failed to load requests');
            }
        } catch (error) {
            console.error('Failed to load blood requests:', error);
            window.DashboardSystem.dashboardManager.showError('activeRequestsGrid', 'Failed to load requests');
        }
    }

    renderActiveRequests() {
        const activeRequestsGrid = document.getElementById('activeRequestsGrid');
        if (!activeRequestsGrid) return;

        const activeRequests = this.bloodRequests.filter(req => 
            ['PENDING', 'APPROVED'].includes(req.status)
        ).slice(0, 3);

        if (activeRequests.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('activeRequestsGrid', 'No active blood requests');
            return;
        }

        activeRequestsGrid.innerHTML = activeRequests.map(request => `
            <div class="request-card ${request.request_type.toLowerCase()}">
                <div class="request-header">
                    <div class="request-info">
                        <h3>${request.hospital_name}</h3>
                        <p>Request ID: #${request.id}</p>
                    </div>
                    <div class="request-status status-${request.status.toLowerCase()}">
                        ${request.status}
                    </div>
                </div>
                <div class="request-details">
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Blood Group</div>
                            <div class="detail-value blood-type-display">${request.blood_group}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Units Needed</div>
                            <div class="detail-value">${request.units_needed}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Request Type</div>
                            <div class="detail-value">${request.request_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Required By</div>
                            <div class="detail-value">${window.DashboardSystem.dashboardManager.formatDateTime(request.required_by)}</div>
                        </div>
                    </div>
                    ${request.emergency_reason ? `
                        <div class="detail-item">
                            <div class="detail-label">Emergency Reason</div>
                            <div class="detail-value">${request.emergency_reason}</div>
                        </div>
                    ` : ''}
                    ${request.requires_admin_approval && !request.admin_approved ? `
                        <div class="admin-approval-notice">
                            <span class="icon">⏳</span>
                            <span class="text">Awaiting admin approval for emergency request</span>
                        </div>
                    ` : ''}
                </div>
                <div class="request-actions">
                    <button class="btn btn-outline btn-small" onclick="patientDashboard.viewRequestDetails(${request.id})">
                        View Details
                    </button>
                    ${request.status === 'PENDING' ? `
                        <button class="btn btn-outline btn-small" onclick="patientDashboard.cancelRequest(${request.id})">
                            Cancel
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    async loadNearbyHospitals() {
        window.DashboardSystem.dashboardManager.showLoading('hospitalsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/patient/hospitals/nearby/');
            if (response && response.ok) {
                const data = await response.json();
                this.hospitals = data.results || [];
                this.renderNearbyHospitals();
            } else {
                window.DashboardSystem.dashboardManager.showError('hospitalsGrid', 'Failed to load hospitals');
            }
        } catch (error) {
            console.error('Failed to load hospitals:', error);
            window.DashboardSystem.dashboardManager.showError('hospitalsGrid', 'Failed to load hospitals');
        }
    }

    renderNearbyHospitals() {
        const hospitalsGrid = document.getElementById('hospitalsGrid');
        if (!hospitalsGrid) return;

        if (this.hospitals.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('hospitalsGrid', 'No nearby hospitals found');
            return;
        }

        hospitalsGrid.innerHTML = this.hospitals.slice(0, 3).map(hospital => `
            <div class="hospital-card">
                <div class="hospital-header">
                    <div class="hospital-icon">🏥</div>
                    <div class="hospital-info">
                        <h3>${hospital.hospital_name}</h3>
                        <p>${hospital.area}, ${hospital.city}</p>
                    </div>
                </div>
                <div class="hospital-features">
                    <div class="feature-list">
                        ${hospital.has_blood_bank ? '<span class="feature-tag blood-bank">Blood Bank</span>' : ''}
                        <span class="feature-tag">Verified</span>
                        <span class="feature-tag">24/7 Emergency</span>
                    </div>
                </div>
                <div class="hospital-contact">
                    <span class="contact-icon">📞</span>
                    <span>${hospital.phone}</span>
                </div>
                <div class="hospital-contact">
                    <span class="contact-icon">🚨</span>
                    <span>${hospital.emergency_contact}</span>
                </div>
                <div class="hospital-actions">
                    <button class="btn btn-primary btn-small" onclick="patientDashboard.requestBloodFromHospital(${hospital.id})">
                        Request Blood
                    </button>
                    <button class="btn btn-outline btn-small" onclick="patientDashboard.viewHospitalDetails(${hospital.id})">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    showBloodRequestModal(requestType = 'NORMAL') {
        // Load hospitals into select
        this.loadHospitalsIntoSelect();
        
        // Set request type
        const requestTypeSelect = document.getElementById('requestType');
        if (requestTypeSelect) {
            requestTypeSelect.value = requestType;
            this.handleRequestTypeChange(requestType);
        }

        // Set minimum required by date (current time + 1 hour)
        const requiredByInput = document.getElementById('requiredBy');
        if (requiredByInput) {
            const minDate = new Date();
            minDate.setHours(minDate.getHours() + 1);
            requiredByInput.min = minDate.toISOString().slice(0, 16);
            requiredByInput.value = minDate.toISOString().slice(0, 16);
        }

        window.DashboardSystem.modalManager.openModal('bloodRequestModal');
    }

    loadHospitalsIntoSelect() {
        const hospitalSelect = document.getElementById('hospitalSelect');
        if (!hospitalSelect) return;

        hospitalSelect.innerHTML = '<option value="">Choose Hospital</option>';
        
        this.hospitals.forEach(hospital => {
            const option = document.createElement('option');
            option.value = hospital.id;
            option.textContent = hospital.hospital_name;
            hospitalSelect.appendChild(option);
        });
    }

    handleRequestTypeChange(requestType) {
        const emergencySection = document.getElementById('emergencySection');
        const emergencyWarning = document.getElementById('emergencyWarning');
        const emergencyReason = document.getElementById('emergencyReason');
        const emergencyJustification = document.getElementById('emergencyJustification');

        if (requestType === 'EMERGENCY' || requestType === 'DISASTER') {
            emergencySection.style.display = 'block';
            emergencyWarning.classList.remove('hidden');
            emergencyReason.required = true;
            emergencyJustification.required = true;
        } else {
            emergencySection.style.display = 'none';
            emergencyWarning.classList.add('hidden');
            emergencyReason.required = false;
            emergencyJustification.required = false;
        }
    }

    validateEmergencyJustification(textarea) {
        const minLength = 50;
        const currentLength = textarea.value.trim().length;
        
        if (currentLength < minLength) {
            textarea.classList.add('error');
            AuthSystem.formValidator.showFieldError(textarea, `Minimum ${minLength} characters required (${currentLength}/${minLength})`);
            return false;
        } else {
            textarea.classList.remove('error');
            AuthSystem.formValidator.showFieldSuccess(textarea);
            return true;
        }
    }

    async handleBloodRequestSubmission(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        // Validate emergency justification if needed
        const requestType = formData.get('request_type');
        if (requestType === 'EMERGENCY' || requestType === 'DISASTER') {
            const emergencyJustification = document.getElementById('emergencyJustification');
            if (!this.validateEmergencyJustification(emergencyJustification)) {
                return;
            }
        }

        try {
            const requestData = {
                hospital_id: parseInt(formData.get('hospital_id')),
                blood_group: formData.get('blood_group'),
                units_needed: parseInt(formData.get('units_needed')),
                request_type: formData.get('request_type'),
                required_by: formData.get('required_by'),
                emergency_reason: formData.get('emergency_reason') || '',
                emergency_justification: formData.get('emergency_justification') || '',
                doctor_name: formData.get('doctor_name') || '',
                doctor_contact: formData.get('doctor_contact') || '',
                medical_condition: formData.get('medical_condition') || ''
            };

            const response = await AuthSystem.authManager.makeRequest('/patient/blood-requests/create/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                window.DashboardSystem.modalManager.closeModal('bloodRequestModal');
                
                // Refresh active requests
                await this.loadActiveRequests();
                await this.loadPatientStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to submit request', 'error');
            }
            
        } catch (error) {
            console.error('Failed to submit blood request:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    async cancelRequest(requestId) {
        if (!confirm('Are you sure you want to cancel this blood request?')) {
            return;
        }

        try {
            const response = await AuthSystem.authManager.makeRequest('/patient/blood-requests/cancel/', {
                method: 'POST',
                body: JSON.stringify({ request_id: requestId })
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Refresh data
                await this.loadActiveRequests();
                await this.loadPatientStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to cancel request', 'error');
            }
            
        } catch (error) {
            console.error('Failed to cancel request:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    requestBloodFromHospital(hospitalId) {
        // Pre-select hospital and show modal
        this.showBloodRequestModal('NORMAL');
        
        setTimeout(() => {
            const hospitalSelect = document.getElementById('hospitalSelect');
            if (hospitalSelect) {
                hospitalSelect.value = hospitalId;
            }
        }, 100);
    }

    viewRequestDetails(requestId) {
        AuthSystem.notificationManager.show('Request details view coming soon!', 'info');
    }

    viewHospitalDetails(hospitalId) {
        AuthSystem.notificationManager.show('Hospital details view coming soon!', 'info');
    }

    showAllRequests() {
        AuthSystem.notificationManager.show('All requests view coming soon!', 'info');
    }

    showAllHospitals() {
        AuthSystem.notificationManager.show('All hospitals view coming soon!', 'info');
    }

    showRequestHistory() {
        AuthSystem.notificationManager.show('Request history coming soon!', 'info');
    }
}

// Initialize patient dashboard
const patientDashboard = new PatientDashboard();