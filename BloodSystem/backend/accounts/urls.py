from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Registration endpoints
    path('register/donor/', views.donor_registration, name='donor_registration'),
    path('register/hospital/', views.hospital_registration, name='hospital_registration'),
    path('register/camp/', views.camp_registration, name='camp_registration'),
    path('register/patient/', views.patient_registration, name='patient_registration'),
    
    # Authentication endpoints
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile endpoints
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]