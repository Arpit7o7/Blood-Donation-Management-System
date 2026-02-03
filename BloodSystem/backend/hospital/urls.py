from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    
    # Blood Stock Management
    path('blood-stock/', views.blood_stock, name='blood_stock'),
    path('blood-stock/update/', views.update_blood_stock, name='update_blood_stock'),
    
    # Patient Requests
    path('patient-requests/', views.patient_requests, name='patient_requests'),
    
    # Emergency Alerts
    path('emergency-alert/create/', views.create_emergency_alert, name='create_emergency_alert'),
    
    # Donor Applications
    path('donor-applications/', views.donor_applications, name='donor_applications'),
    path('donor-applications/review/', views.review_donor_application, name='review_donor_application'),
    
    # Hospital Network
    path('network/', views.hospital_network, name='hospital_network'),
    path('network/hospitals/', views.available_hospitals, name='available_hospitals'),
    path('network/request/', views.create_network_request, name='create_network_request'),
    path('network/respond/', views.respond_network_request, name='respond_network_request'),
]