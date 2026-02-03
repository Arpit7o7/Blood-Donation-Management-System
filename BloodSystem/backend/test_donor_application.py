#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, DonorProfile
from camp.models import Camp
from donor.models import CampApplication

def test_donor_application():
    print("=== TESTING DONOR CAMP APPLICATION ===")
    
    # Find a donor user
    donor_user = User.objects.filter(email='testdonor@test.com').first()
    if not donor_user:
        print("Test donor not found!")
        return
    
    print(f"Testing with donor: {donor_user.email}")
    
    # Find an active camp for this user
    camp = Camp.objects.filter(status='ACTIVE', organizer__user=donor_user).first()
    if not camp:
        # Find any active camp
        camp = Camp.objects.filter(status='ACTIVE').first()
        if not camp:
            print("No active camps found!")
            return
    
    print(f"Testing with camp: {camp.name} by {camp.organizer.organization_name}")
    
    # Test login first
    login_data = {
        'email': donor_user.email,
        'password': 'TestPass123!'  # Assuming this is the test password
    }
    
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json=login_data,
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_result = login_response.json()
    print(f"Login response: {login_result}")
    access_token = login_result.get('tokens', {}).get('access')
    
    if not access_token:
        print("No access token received")
        print(f"Available keys: {list(login_result.keys())}")
        return
    
    print("Login successful!")
    
    # Test camp application
    application_data = {
        'camp_id': camp.id,
        'age': 25,
        'weight': 70.0,
        'last_donation_date': None,
        'health_status': 'GOOD',
        'health_issues': '',
        'medications': '',
        'consent': True
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"Submitting application data: {application_data}")
    
    app_response = requests.post('http://localhost:8000/api/donor/camps/apply/',
                               json=application_data,
                               headers=headers)
    
    print(f"Application response status: {app_response.status_code}")
    print(f"Application response: {app_response.text}")
    
    if app_response.status_code == 201:
        print("✅ Application submitted successfully!")
        
        # Check database
        applications = CampApplication.objects.filter(donor__user=donor_user, camp=camp)
        print(f"Applications in database: {applications.count()}")
        
        if applications.exists():
            app = applications.first()
            print(f"Application details: ID={app.id}, Status={app.status}")
        
    else:
        print("❌ Application failed!")
        try:
            error_data = app_response.json()
            print(f"Error details: {error_data}")
        except:
            print("Could not parse error response")

if __name__ == '__main__':
    test_donor_application()