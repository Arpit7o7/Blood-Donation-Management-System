from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Verifications
    path('pending-verifications/', views.pending_verifications, name='pending_verifications'),
    path('verify-hospital/', views.verify_hospital, name='verify_hospital'),
    path('verify-camp/', views.verify_camp, name='verify_camp'),
    path('hospital-details/<int:hospital_id>/', views.hospital_details, name='hospital_details'),
    path('camp-details/<int:camp_id>/', views.camp_details, name='camp_details'),
    
    # Emergency Requests
    path('emergency-requests/', views.emergency_requests, name='emergency_requests'),
    path('emergency-details/<int:emergency_id>/', views.emergency_details, name='emergency_details'),
    path('review-emergency/', views.review_emergency, name='review_emergency'),
    path('approve-emergency/', views.approve_emergency_request, name='approve_emergency_request'),
    
    # System Overview
    path('blood-stock-overview/', views.blood_stock_overview, name='blood_stock_overview'),
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('stats/', views.system_stats, name='system_stats'),
]