from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('stats/', views.donor_stats, name='donor_stats'),
    
    # Profile
    path('profile/update/', views.update_donor_profile, name='update_donor_profile'),
    
    # Camps
    path('camps/suggestions/', views.camp_suggestions, name='camp_suggestions'),
    path('camps/apply/', views.apply_to_camp, name='apply_to_camp'),
    
    # Hospital Alerts
    path('hospital-alerts/', views.hospital_alerts, name='hospital_alerts'),
    path('hospital-alerts/respond/', views.respond_to_alert, name='respond_to_alert'),
    
    # Donation History
    path('donation-history/', views.donation_history, name='donation_history'),
]