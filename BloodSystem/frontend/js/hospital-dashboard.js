// Hospital Dashboard JavaScript

class HospitalDashboard {
    constructor() {
        this.bloodStock = [];
        this.patientRequests = [];
        this.donorApplications = [];
        this.hospitalProfile = null;
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

        this.hospitalProfile = window.DashboardSystem.dashboardManager.user;
        this.setupEventListeners();
        await this.loadDashboardData();
    }

    setupEventListeners() {
        // Quick action buttons
        document.getElementById('createEmergencyAlertBtn')?.addEventListener('click', () => {
            this.showEmergencyAlertModal();
        });

        document.getElementById('manageStockBtn')?.addEventListener('click', () => {
            this.showStockManagement();
        });

        document.getElementById('reviewApplicationsBtn')?.addEventListener('click', () => {
            this.showAllApplications();
        });

        document.getElementById('hospitalNetworkBtn')?.addEventListener('click', () => {
            this.showHospitalNetwork();
        });

        // View all buttons
        document.getElementById('manageAllStockBtn')?.addEventListener('click', () => {
            this.showStockManagement();
        });

        document.getElementById('viewAllRequestsBtn')?.addEventListener('click', () => {
            this.showAllRequests();
        });

        document.getElementById('viewAllApplicationsBtn')?.addEventListener('click', () => {
            this.showAllApplications();
        });

        // Modal event listeners
        this.setupModalListeners();
    }

    setupModalListeners() {
        // Emergency alert modal
        const closeEmergencyModal = document.getElementById('closeEmergencyModal');
        const cancelEmergencyAlert = document.getElementById('cancelEmergencyAlert');
        const emergencyAlertForm = document.getElementById('emergencyAlertForm');
        const urgencySelect = document.getElementById('urgency');

        closeEmergencyModal?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('emergencyAlertModal');
        });

        cancelEmergencyAlert?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('emergencyAlertModal');
        });

        // Urgency change handler
        urgencySelect?.addEventListener('change', (e) => {
            this.handleUrgencyChange(e.target.value);
        });

        // Form submission
        emergencyAlertForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEmergencyAlertSubmission(e);
        });

        // Stock management modal
        const closeStockModal = document.getElementById('closeStockModal');
        const cancelStockUpdate = document.getElementById('cancelStockUpdate');
        const stockUpdateForm = document.getElementById('stockUpdateForm');
        const previewStockUpdate = document.getElementById('previewStockUpdate');

        closeStockModal?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('stockManagementModal');
        });

        cancelStockUpdate?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('stockManagementModal');
        });

        previewStockUpdate?.addEventListener('click', () => {
            this.previewStockUpdate();
        });

        stockUpdateForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleStockUpdateSubmission(e);
        });

        // Stock form change handlers
        const stockBloodGroup = document.getElementById('stockBloodGroup');
        const stockOperation = document.getElementById('stockOperation');
        const stockUnits = document.getElementById('stockUnits');

        [stockBloodGroup, stockOperation, stockUnits].forEach(element => {
            element?.addEventListener('change', () => {
                this.hideStockPreview();
            });
        });

        // Hospital network modal
        const closeNetworkModal = document.getElementById('closeNetworkModal');
        const cancelNetworkRequest = document.getElementById('cancelNetworkRequest');
        const networkRequestForm = document.getElementById('networkRequestForm');

        closeNetworkModal?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('hospitalNetworkModal');
        });

        cancelNetworkRequest?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('hospitalNetworkModal');
        });

        networkRequestForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleNetworkRequestSubmission(e);
        });

        // Network tabs
        const networkTabs = document.querySelectorAll('.tab-btn');
        networkTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchNetworkTab(e.target.dataset.tab);
            });
        });

        // Network response modal
        const closeResponseModal = document.getElementById('closeResponseModal');
        const cancelResponse = document.getElementById('cancelResponse');
        const networkResponseForm = document.getElementById('networkResponseForm');

        closeResponseModal?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('networkResponseModal');
        });

        cancelResponse?.addEventListener('click', () => {
            window.DashboardSystem.modalManager.closeModal('networkResponseModal');
        });

        networkResponseForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleNetworkResponseSubmission(e);
        });

        // Response decision change handler
        const decisionRadios = document.querySelectorAll('input[name="decision"]');
        decisionRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleDecisionChange(e.target.value);
            });
        });
    }

    async loadDashboardData() {
        // Load hospital stats
        await this.loadHospitalStats();
        
        // Load data in parallel
        await Promise.all([
            this.loadBloodStock(),
            this.loadPatientRequests(),
            this.loadDonorApplications()
        ]);
    }

    async loadHospitalStats() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/dashboard/');
            if (response && response.ok) {
                const data = await response.json();
                this.updateHospitalStats(data.stats);
                
                // Update hospital name
                const hospitalNameEl = document.getElementById('hospitalName');
                if (hospitalNameEl) {
                    hospitalNameEl.textContent = data.hospital || 'Hospital';
                }
            }
        } catch (error) {
            console.error('Failed to load hospital stats:', error);
        }
    }

    updateHospitalStats(stats) {
        const activeRequestsEl = document.getElementById('activeRequests');
        const totalStockEl = document.getElementById('totalStock');
        const pendingApplicationsEl = document.getElementById('pendingApplications');

        if (activeRequestsEl) activeRequestsEl.textContent = stats.active_requests || 0;
        if (totalStockEl) totalStockEl.textContent = stats.total_stock || 0;
        if (pendingApplicationsEl) pendingApplicationsEl.textContent = stats.pending_applications || 0;
    }

    async loadBloodStock() {
        window.DashboardSystem.dashboardManager.showLoading('stockGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/blood-stock/');
            if (response && response.ok) {
                const data = await response.json();
                this.bloodStock = data.results || [];
                this.renderBloodStock();
            } else {
                window.DashboardSystem.dashboardManager.showError('stockGrid', 'Failed to load blood stock');
            }
        } catch (error) {
            console.error('Failed to load blood stock:', error);
            window.DashboardSystem.dashboardManager.showError('stockGrid', 'Failed to load blood stock');
        }
    }

    renderBloodStock() {
        const stockGrid = document.getElementById('stockGrid');
        if (!stockGrid) return;

        if (this.bloodStock.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('stockGrid', 'No blood stock data available');
            return;
        }

        stockGrid.innerHTML = this.bloodStock.map(stock => `
            <div class="stock-card">
                <div class="blood-type">${stock.blood_group}</div>
                <div class="stock-amount">${stock.units_available}</div>
                <div class="stock-label">Units Available</div>
                <div class="stock-status ${stock.status.toLowerCase()}">${stock.status}</div>
            </div>
        `).join('');
    }

    async loadPatientRequests() {
        window.DashboardSystem.dashboardManager.showLoading('requestsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/patient-requests/');
            if (response && response.ok) {
                const data = await response.json();
                this.patientRequests = data.results || [];
                this.renderPatientRequests();
            } else {
                window.DashboardSystem.dashboardManager.showError('requestsGrid', 'Failed to load patient requests');
            }
        } catch (error) {
            console.error('Failed to load patient requests:', error);
            window.DashboardSystem.dashboardManager.showError('requestsGrid', 'Failed to load patient requests');
        }
    }

    renderPatientRequests() {
        const requestsGrid = document.getElementById('requestsGrid');
        if (!requestsGrid) return;

        if (this.patientRequests.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('requestsGrid', 'No patient requests');
            return;
        }

        requestsGrid.innerHTML = this.patientRequests.slice(0, 3).map(request => `
            <div class="request-card ${request.request_type.toLowerCase()}">
                <div class="request-header">
                    <div class="patient-info">
                        <div class="patient-name">${request.patient_name}</div>
                        <div class="patient-id">${request.patient_id}</div>
                    </div>
                    <div class="request-priority priority-${request.request_type.toLowerCase()}">
                        ${request.request_type}
                    </div>
                </div>
                <div class="request-details">
                    <div class="detail-row">
                        <span class="detail-label">Blood Group:</span>
                        <span class="detail-value blood-type-large">${request.blood_group}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Units Needed:</span>
                        <span class="detail-value">${request.units_needed}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Required By:</span>
                        <span class="detail-value">${window.DashboardSystem.dashboardManager.formatDateTime(request.required_by)}</span>
                    </div>
                    ${request.doctor_name ? `
                        <div class="detail-row">
                            <span class="detail-label">Doctor:</span>
                            <span class="detail-value">${request.doctor_name}</span>
                        </div>
                    ` : ''}
                    ${request.emergency_reason ? `
                        <div class="detail-row">
                            <span class="detail-label">Emergency Reason:</span>
                            <span class="detail-value">${request.emergency_reason}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="request-actions">
                    <button class="btn btn-primary btn-small" onclick="hospitalDashboard.approveRequest(${request.id})">
                        Approve
                    </button>
                    <button class="btn btn-outline btn-small" onclick="hospitalDashboard.viewRequestDetails(${request.id})">
                        Details
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadDonorApplications() {
        window.DashboardSystem.dashboardManager.showLoading('applicationsGrid');
        
        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/donor-applications/');
            if (response && response.ok) {
                const data = await response.json();
                this.donorApplications = data.results || [];
                this.renderDonorApplications();
            } else {
                window.DashboardSystem.dashboardManager.showError('applicationsGrid', 'Failed to load donor applications');
            }
        } catch (error) {
            console.error('Failed to load donor applications:', error);
            window.DashboardSystem.dashboardManager.showError('applicationsGrid', 'Failed to load donor applications');
        }
    }

    renderDonorApplications() {
        const applicationsGrid = document.getElementById('applicationsGrid');
        if (!applicationsGrid) return;

        if (this.donorApplications.length === 0) {
            window.DashboardSystem.dashboardManager.showEmpty('applicationsGrid', 'No donor applications');
            return;
        }

        applicationsGrid.innerHTML = this.donorApplications.slice(0, 3).map(application => `
            <div class="application-card">
                <div class="donor-info">
                    <div class="donor-avatar">
                        ${application.donor_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </div>
                    <div class="donor-details">
                        <h4>${application.donor_name}</h4>
                        <p>${application.donor_blood_group} • ${application.donor_phone}</p>
                    </div>
                </div>
                <div class="medical-summary">
                    <h5>Medical Summary</h5>
                    <div class="medical-item">
                        <span class="medical-label">Age:</span>
                        <span class="medical-value">${application.age} years</span>
                    </div>
                    <div class="medical-item">
                        <span class="medical-label">Weight:</span>
                        <span class="medical-value">${application.weight} kg</span>
                    </div>
                    <div class="medical-item">
                        <span class="medical-label">Last Donation:</span>
                        <span class="medical-value">${application.last_donation_date ? window.DashboardSystem.dashboardManager.formatDate(application.last_donation_date) : 'Never'}</span>
                    </div>
                    <div class="medical-item">
                        <span class="medical-label">Health Status:</span>
                        <span class="medical-value">${application.health_status}</span>
                    </div>
                </div>
                <div class="request-actions">
                    <button class="btn btn-primary btn-small" onclick="hospitalDashboard.approveApplication(${application.id})">
                        Approve
                    </button>
                    <button class="btn btn-outline btn-small" onclick="hospitalDashboard.rejectApplication(${application.id})">
                        Reject
                    </button>
                </div>
            </div>
        `).join('');
    }

    showEmergencyAlertModal() {
        // Set minimum required by date (current time + 1 hour)
        const requiredByInput = document.getElementById('requiredBy');
        if (requiredByInput) {
            const minDate = new Date();
            minDate.setHours(minDate.getHours() + 1);
            requiredByInput.min = minDate.toISOString().slice(0, 16);
            requiredByInput.value = minDate.toISOString().slice(0, 16);
        }

        window.DashboardSystem.modalManager.openModal('emergencyAlertModal');
    }

    handleUrgencyChange(urgency) {
        const emergencyWarning = document.getElementById('emergencyWarning');
        
        if (urgency === 'EMERGENCY' || urgency === 'DISASTER') {
            emergencyWarning.style.display = 'flex';
        } else {
            emergencyWarning.style.display = 'none';
        }
    }

    async handleEmergencyAlertSubmission(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const alertData = {
                blood_group: formData.get('bloodGroup'),
                units_needed: parseInt(formData.get('unitsNeeded')),
                urgency: formData.get('urgency'),
                required_by: formData.get('requiredBy'),
                reason: formData.get('reason'),
                location: formData.get('location')
            };

            const response = await AuthSystem.authManager.makeRequest('/hospital/emergency-alert/create/', {
                method: 'POST',
                body: JSON.stringify(alertData)
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                window.DashboardSystem.modalManager.closeModal('emergencyAlertModal');
                
                // Refresh dashboard data
                await this.loadHospitalStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to create alert', 'error');
            }
            
        } catch (error) {
            console.error('Failed to create emergency alert:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    async approveApplication(applicationId) {
        if (!confirm('Are you sure you want to approve this donor application?')) {
            return;
        }

        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/donor-applications/review/', {
                method: 'POST',
                body: JSON.stringify({
                    application_id: applicationId,
                    decision: 'APPROVED'
                })
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Refresh applications
                await this.loadDonorApplications();
                await this.loadHospitalStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to approve application', 'error');
            }
            
        } catch (error) {
            console.error('Failed to approve application:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    async rejectApplication(applicationId) {
        const reason = prompt('Please provide a reason for rejection:');
        if (!reason) return;

        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/donor-applications/review/', {
                method: 'POST',
                body: JSON.stringify({
                    application_id: applicationId,
                    decision: 'REJECTED',
                    notes: reason
                })
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Refresh applications
                await this.loadDonorApplications();
                await this.loadHospitalStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to reject application', 'error');
            }
            
        } catch (error) {
            console.error('Failed to reject application:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    approveRequest(requestId) {
        AuthSystem.notificationManager.show('Patient request approval coming soon!', 'info');
    }

    viewRequestDetails(requestId) {
        AuthSystem.notificationManager.show('Request details view coming soon!', 'info');
    }

    showStockManagement() {
        // Load current stock data into modal
        this.loadStockSummary();
        window.DashboardSystem.modalManager.openModal('stockManagementModal');
    }

    async loadStockSummary() {
        const stockSummaryGrid = document.getElementById('stockSummaryGrid');
        if (!stockSummaryGrid) return;

        stockSummaryGrid.innerHTML = '<div class="stock-loading">Loading stock data...</div>';

        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/blood-stock/');
            if (response && response.ok) {
                const data = await response.json();
                this.renderStockSummary(data.results || []);
            } else {
                stockSummaryGrid.innerHTML = '<div class="stock-empty">Failed to load stock data</div>';
            }
        } catch (error) {
            console.error('Failed to load stock summary:', error);
            stockSummaryGrid.innerHTML = '<div class="stock-empty">Failed to load stock data</div>';
        }
    }

    renderStockSummary(stockData) {
        const stockSummaryGrid = document.getElementById('stockSummaryGrid');
        if (!stockSummaryGrid) return;

        if (stockData.length === 0) {
            stockSummaryGrid.innerHTML = '<div class="stock-empty">No stock data available</div>';
            return;
        }

        stockSummaryGrid.innerHTML = stockData.map(stock => `
            <div class="stock-summary-card">
                <div class="blood-type">${stock.blood_group}</div>
                <div class="stock-amount">${stock.units_available}</div>
                <div class="stock-label">Units</div>
                <div class="stock-status ${stock.status.toLowerCase()}">${stock.status}</div>
            </div>
        `).join('');

        // Store stock data for preview calculations
        this.currentStockData = stockData;
    }

    previewStockUpdate() {
        const bloodGroup = document.getElementById('stockBloodGroup').value;
        const operation = document.getElementById('stockOperation').value;
        const units = parseInt(document.getElementById('stockUnits').value);

        if (!bloodGroup || !operation || isNaN(units)) {
            AuthSystem.notificationManager.show('Please fill in all required fields', 'error');
            return;
        }

        // Find current stock for this blood group
        const currentStock = this.currentStockData?.find(stock => stock.blood_group === bloodGroup);
        const currentUnits = currentStock ? currentStock.units_available : 0;

        let newUnits = currentUnits;
        let operationText = '';

        switch (operation) {
            case 'set':
                newUnits = units;
                operationText = `Set to ${units} units`;
                break;
            case 'add':
                newUnits = currentUnits + units;
                operationText = `Add ${units} units`;
                break;
            case 'subtract':
                newUnits = Math.max(0, currentUnits - units);
                operationText = `Remove ${units} units`;
                break;
        }

        // Update preview
        document.getElementById('previewBloodGroup').textContent = bloodGroup;
        document.getElementById('previewCurrentStock').textContent = `${currentUnits} units`;
        document.getElementById('previewOperation').textContent = operationText;
        document.getElementById('previewNewStock').textContent = `${newUnits} units`;

        // Show preview
        const stockPreview = document.getElementById('stockPreview');
        if (stockPreview) {
            stockPreview.style.display = 'block';
        }
    }

    hideStockPreview() {
        const stockPreview = document.getElementById('stockPreview');
        if (stockPreview) {
            stockPreview.style.display = 'none';
        }
    }

    async handleStockUpdateSubmission(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const stockData = {
                blood_group: formData.get('bloodGroup'),
                operation: formData.get('operation'),
                units: parseInt(formData.get('units')),
                notes: formData.get('notes') || ''
            };

            if (!stockData.blood_group || !stockData.operation || isNaN(stockData.units)) {
                AuthSystem.notificationManager.show('Please fill in all required fields', 'error');
                return;
            }

            const response = await AuthSystem.authManager.makeRequest('/hospital/blood-stock/update/', {
                method: 'POST',
                body: JSON.stringify(stockData)
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Reset form and hide preview
                form.reset();
                this.hideStockPreview();
                
                // Refresh stock data
                await this.loadStockSummary();
                await this.loadBloodStock();
                await this.loadHospitalStats();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to update stock', 'error');
            }
            
        } catch (error) {
            console.error('Failed to update stock:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    showAllRequests() {
        AuthSystem.notificationManager.show('All requests view coming soon!', 'info');
    }

    showAllApplications() {
        AuthSystem.notificationManager.show('All applications view coming soon!', 'info');
    }

    showHospitalNetwork() {
        // Load network data and show modal
        this.loadNetworkData();
        window.DashboardSystem.modalManager.openModal('hospitalNetworkModal');
    }

    async loadNetworkData() {
        // Load available hospitals for exchange tab
        await this.loadAvailableHospitals();
        
        // Load network requests for other tabs
        await this.loadNetworkRequests();
    }

    async loadAvailableHospitals() {
        const hospitalsGrid = document.getElementById('hospitalsGrid');
        if (!hospitalsGrid) return;

        hospitalsGrid.innerHTML = '<div class="loading-placeholder">Loading partner hospitals...</div>';

        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/network/hospitals/');
            if (response && response.ok) {
                const data = await response.json();
                this.availableHospitals = data.results || [];
                this.renderAvailableHospitals();
            } else {
                hospitalsGrid.innerHTML = '<div class="loading-placeholder">Failed to load hospitals</div>';
            }
        } catch (error) {
            console.error('Failed to load available hospitals:', error);
            hospitalsGrid.innerHTML = '<div class="loading-placeholder">Failed to load hospitals</div>';
        }
    }

    renderAvailableHospitals() {
        const hospitalsGrid = document.getElementById('hospitalsGrid');
        if (!hospitalsGrid) return;

        if (this.availableHospitals.length === 0) {
            hospitalsGrid.innerHTML = '<div class="loading-placeholder">No partner hospitals available</div>';
            return;
        }

        hospitalsGrid.innerHTML = this.availableHospitals.map(hospital => `
            <div class="hospital-card" data-hospital-id="${hospital.id}" onclick="hospitalDashboard.selectHospital(${hospital.id})">
                <div class="hospital-header">
                    <div>
                        <div class="hospital-name">${hospital.hospital_name}</div>
                        <div class="hospital-location">${hospital.city}, ${hospital.state}</div>
                    </div>
                    <div class="hospital-stock-indicator ${hospital.total_stock >= 50 ? 'stock-good' : 'stock-low'}">
                        ${hospital.total_stock} Units
                    </div>
                </div>
                <div class="hospital-details">
                    <div class="detail-item">
                        <span class="detail-label">Contact:</span>
                        <span class="detail-value">${hospital.contact_person}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Phone:</span>
                        <span class="detail-value">${hospital.contact_phone}</span>
                    </div>
                </div>
                <div class="blood-stock-summary">
                    <h6>Available Blood Groups</h6>
                    <div class="blood-groups-list">
                        ${hospital.blood_stock.filter(stock => stock.units_available > 0).map(stock => `
                            <div class="blood-group-item">
                                <span class="blood-group-type">${stock.blood_group}:</span>
                                <span class="blood-group-units">${stock.units_available}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    }

    selectHospital(hospitalId) {
        // Remove previous selection
        document.querySelectorAll('.hospital-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Select new hospital
        const selectedCard = document.querySelector(`[data-hospital-id="${hospitalId}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        // Find hospital data
        const hospital = this.availableHospitals.find(h => h.id === hospitalId);
        if (hospital) {
            this.selectedHospital = hospital;
            this.showSelectedHospital(hospital);
        }
    }

    showSelectedHospital(hospital) {
        const selectedHospitalDiv = document.getElementById('selectedHospital');
        const selectedHospitalCard = document.getElementById('selectedHospitalCard');
        
        if (selectedHospitalDiv && selectedHospitalCard) {
            selectedHospitalCard.innerHTML = `
                <div class="hospital-header">
                    <div>
                        <div class="hospital-name">${hospital.hospital_name}</div>
                        <div class="hospital-location">${hospital.city}, ${hospital.state}</div>
                    </div>
                    <div class="hospital-stock-indicator ${hospital.total_stock >= 50 ? 'stock-good' : 'stock-low'}">
                        ${hospital.total_stock} Units Available
                    </div>
                </div>
                <div class="hospital-details">
                    <div class="detail-item">
                        <span class="detail-label">Contact Person:</span>
                        <span class="detail-value">${hospital.contact_person}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Contact Phone:</span>
                        <span class="detail-value">${hospital.contact_phone}</span>
                    </div>
                </div>
            `;
            selectedHospitalDiv.style.display = 'block';
        }
    }

    async handleNetworkRequestSubmission(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        if (!this.selectedHospital) {
            AuthSystem.notificationManager.show('Please select a hospital first', 'error');
            return;
        }

        try {
            const requestData = {
                providing_hospital_id: this.selectedHospital.id,
                blood_group: formData.get('bloodGroup'),
                units_requested: parseInt(formData.get('units')),
                urgency: formData.get('urgency'),
                required_by: formData.get('requiredBy'),
                reason: formData.get('reason')
            };

            const response = await AuthSystem.authManager.makeRequest('/hospital/network/request/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Reset form and selection
                form.reset();
                this.selectedHospital = null;
                document.getElementById('selectedHospital').style.display = 'none';
                document.querySelectorAll('.hospital-card').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Refresh requests data
                await this.loadNetworkRequests();
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to send request', 'error');
            }
            
        } catch (error) {
            console.error('Failed to send network request:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }

    switchNetworkTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Content`).classList.add('active');

        // Load data for the selected tab
        if (tabName === 'requests' || tabName === 'incoming') {
            this.loadNetworkRequests();
        } else if (tabName === 'exchange') {
            this.loadAvailableHospitals();
        }
    }

    async loadNetworkRequests() {
        try {
            const response = await AuthSystem.authManager.makeRequest('/hospital/network/');
            if (response && response.ok) {
                const data = await response.json();
                this.renderSentRequests(data.sent_requests || []);
                this.renderReceivedRequests(data.received_requests || []);
            }
        } catch (error) {
            console.error('Failed to load network requests:', error);
        }
    }

    renderSentRequests(requests) {
        const sentRequestsList = document.getElementById('sentRequestsList');
        if (!sentRequestsList) return;

        if (requests.length === 0) {
            sentRequestsList.innerHTML = '<div class="loading-placeholder">No outgoing requests</div>';
            return;
        }

        sentRequestsList.innerHTML = requests.map(request => `
            <div class="network-request-card ${request.urgency.toLowerCase()}">
                <div class="request-card-header">
                    <div class="request-hospital-info">
                        <h5>${request.hospital_name}</h5>
                        <p>Requested on ${window.DashboardSystem.dashboardManager.formatDateTime(request.requested_at)}</p>
                    </div>
                    <div class="request-status status-${request.status.toLowerCase()}">${request.status}</div>
                </div>
                <div class="request-card-body">
                    <div class="request-detail-group">
                        <h6>Blood Requirements</h6>
                        <div class="request-detail-item">
                            <span class="detail-label">Blood Group:</span>
                            <span class="detail-value">${request.blood_group}</span>
                        </div>
                        <div class="request-detail-item">
                            <span class="detail-label">Units Requested:</span>
                            <span class="detail-value">${request.units_requested}</span>
                        </div>
                        ${request.units_approved > 0 ? `
                            <div class="request-detail-item">
                                <span class="detail-label">Units Approved:</span>
                                <span class="detail-value">${request.units_approved}</span>
                            </div>
                        ` : ''}
                    </div>
                    <div class="request-detail-group">
                        <h6>Request Details</h6>
                        <div class="request-detail-item">
                            <span class="detail-label">Urgency:</span>
                            <span class="detail-value">${request.urgency}</span>
                        </div>
                        <div class="request-detail-item">
                            <span class="detail-label">Required By:</span>
                            <span class="detail-value">${window.DashboardSystem.dashboardManager.formatDateTime(request.required_by)}</span>
                        </div>
                        ${request.response_notes ? `
                            <div class="request-detail-item">
                                <span class="detail-label">Response Notes:</span>
                                <span class="detail-value">${request.response_notes}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="request-reason">
                    <strong>Reason:</strong> ${request.reason}
                </div>
            </div>
        `).join('');
    }

    renderReceivedRequests(requests) {
        const receivedRequestsList = document.getElementById('receivedRequestsList');
        if (!receivedRequestsList) return;

        if (requests.length === 0) {
            receivedRequestsList.innerHTML = '<div class="loading-placeholder">No incoming requests</div>';
            return;
        }

        receivedRequestsList.innerHTML = requests.map(request => `
            <div class="network-request-card ${request.urgency.toLowerCase()}">
                <div class="request-card-header">
                    <div class="request-hospital-info">
                        <h5>${request.hospital_name}</h5>
                        <p>Received on ${window.DashboardSystem.dashboardManager.formatDateTime(request.requested_at)}</p>
                    </div>
                    <div class="request-status status-${request.status.toLowerCase()}">${request.status}</div>
                </div>
                <div class="request-card-body">
                    <div class="request-detail-group">
                        <h6>Blood Requirements</h6>
                        <div class="request-detail-item">
                            <span class="detail-label">Blood Group:</span>
                            <span class="detail-value">${request.blood_group}</span>
                        </div>
                        <div class="request-detail-item">
                            <span class="detail-label">Units Requested:</span>
                            <span class="detail-value">${request.units_requested}</span>
                        </div>
                        <div class="request-detail-item">
                            <span class="detail-label">Urgency:</span>
                            <span class="detail-value">${request.urgency}</span>
                        </div>
                        <div class="request-detail-item">
                            <span class="detail-label">Required By:</span>
                            <span class="detail-value">${window.DashboardSystem.dashboardManager.formatDateTime(request.required_by)}</span>
                        </div>
                    </div>
                </div>
                <div class="request-reason">
                    <strong>Reason:</strong> ${request.reason}
                </div>
                ${request.status === 'PENDING' ? `
                    <div class="request-card-actions">
                        <button class="btn btn-primary btn-small" onclick="hospitalDashboard.respondToRequest(${request.id}, '${request.hospital_name}', '${request.blood_group}', ${request.units_requested})">
                            Respond
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    respondToRequest(requestId, hospitalName, bloodGroup, unitsRequested) {
        // Set up response modal
        document.getElementById('responseRequestId').value = requestId;
        
        const requestDetails = document.getElementById('responseRequestDetails');
        requestDetails.innerHTML = `
            <h5>Request from ${hospitalName}</h5>
            <div class="request-detail-item">
                <span class="detail-label">Blood Group:</span>
                <span class="detail-value">${bloodGroup}</span>
            </div>
            <div class="request-detail-item">
                <span class="detail-label">Units Requested:</span>
                <span class="detail-value">${unitsRequested}</span>
            </div>
        `;
        
        // Set max units for approval
        const unitsApprovedInput = document.getElementById('unitsApproved');
        if (unitsApprovedInput) {
            unitsApprovedInput.max = unitsRequested;
            unitsApprovedInput.value = unitsRequested;
        }
        
        window.DashboardSystem.modalManager.openModal('networkResponseModal');
    }

    handleDecisionChange(decision) {
        const unitsApprovedGroup = document.getElementById('unitsApprovedGroup');
        if (decision === 'APPROVED') {
            unitsApprovedGroup.style.display = 'block';
            document.getElementById('unitsApproved').required = true;
        } else {
            unitsApprovedGroup.style.display = 'none';
            document.getElementById('unitsApproved').required = false;
        }
    }

    async handleNetworkResponseSubmission(event) {
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const responseData = {
                request_id: parseInt(formData.get('requestId')),
                decision: formData.get('decision'),
                units_approved: formData.get('decision') === 'APPROVED' ? parseInt(formData.get('unitsApproved')) : 0,
                response_notes: formData.get('responseNotes') || ''
            };

            const response = await AuthSystem.authManager.makeRequest('/hospital/network/respond/', {
                method: 'POST',
                body: JSON.stringify(responseData)
            });

            if (response && response.ok) {
                const result = await response.json();
                AuthSystem.notificationManager.show(result.message, 'success');
                
                // Close modal and refresh data
                window.DashboardSystem.modalManager.closeModal('networkResponseModal');
                form.reset();
                await this.loadNetworkRequests();
                await this.loadBloodStock(); // Refresh stock if approved
                
            } else {
                const error = await response.json();
                AuthSystem.notificationManager.show(error.error || 'Failed to submit response', 'error');
            }
            
        } catch (error) {
            console.error('Failed to submit network response:', error);
            AuthSystem.notificationManager.show('Network error. Please try again.', 'error');
        }
    }
}

// Initialize hospital dashboard
const hospitalDashboard = new HospitalDashboard();