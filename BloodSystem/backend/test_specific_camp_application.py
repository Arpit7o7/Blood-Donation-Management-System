#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User
from camp.models import Camp

def test_specific_camp_application():
    print("=== TESTING SPECIFIC CAMP APPLICATION ===")
    
    # Find the testcamp user's camp
    camp_user = User.objects.filter(email='testcamp1770017280@test.com').first()
    if not camp_user:
        print("Camp user not found!")
        return
    
    camp = Camp.objects.filter(organizer__user=camp_user).first()
    if not camp:
        print("No camp found for this user!")
        return
    
    print(f"Target camp: {camp.name} (ID: {camp.id}) by {camp.organizer.organization_name}")
    
    # Use test donor
    donor_user = User.objects.filter(email='testdonor@test.com').first()
    if not donor_user:
        print("Test donor not found!")
        return
    
    print(f"Using donor: {donor_user.email}")
    
    # Login as donor
    login_data = {
        'email': donor_user.email,
        'password': 'TestPass123!'
    }
    
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json=login_data,
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    access_token = login_response.json().get('tokens', {}).get('access')
    if not access_token:
        print("No access token received")
        return
    
    print("Donor login successful!")
    
    # Submit application to specific camp
    application_data = {
        'camp_id': camp.id,
        'age': 28,
        'weight': 75.0,
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
    
    app_response = requests.post('http://localhost:8000/api/donor/camps/apply/',
                               json=application_data,
                               headers=headers)
    
    print(f"Application response: {app_response.status_code} - {app_response.text}")
    
    if app_response.status_code == 201:
        print("✅ Application submitted successfully!")
        
        # Now test camp dashboard
        print("\n--- Testing Camp Dashboard ---")
        
        # Login as camp user
        camp_login_data = {
            'email': camp_user.email,
            'password': 'TestPass123!'
        }
        
        camp_login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                          json=camp_login_data,
                                          headers={'Content-Type': 'application/json'})
        
        if camp_login_response.status_code != 200:
            print(f"Camp login failed: {camp_login_response.status_code}")
            return
        
        camp_access_token = camp_login_response.json().get('tokens', {}).get('access')
        if not camp_access_token:
            print("No camp access token received")
            return
        
        print("Camp login successful!")
        
        camp_headers = {
            'Authorization': f'Bearer {camp_access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test applications endpoint
        applications_response = requests.get('http://localhost:8000/api/camp/applications/', 
                                           headers=camp_headers)
        
        print(f"Applications response: {applications_response.status_code}")
        if applications_response.status_code == 200:
            apps_data = applications_response.json()
            print(f"Found {apps_data['count']} applications")
            for app in apps_data['results']:
                print(f"  - {app['donor_name']} ({app['donor_blood_group']}) -> {app['camp_name']} [{app['status']}]")
        else:
            print(f"Applications error: {applications_response.text}")

if __name__ == '__main__':
    test_specific_camp_application()