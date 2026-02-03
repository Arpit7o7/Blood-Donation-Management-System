from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Blood Requests
    path('blood-requests/', views.blood_requests, name='blood_requests'),
    path('blood-requests/create/', views.create_blood_request, name='create_blood_request'),
    path('blood-requests/cancel/', views.cancel_blood_request, name='cancel_blood_request'),
    
    # Hospitals
    path('hospitals/nearby/', views.nearby_hospitals, name='nearby_hospitals'),
]