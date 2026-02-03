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
from donor.models import CampApplication

def test_camp_review():
    print("=== TESTING CAMP APPLICATION REVIEW ===")
    
    # Find a camp user
    camp_user = User.objects.filter(email='testcamp1770017280@test.com').first()
    if not camp_user:
        print("Camp user not found!")
        return
    
    print(f"Testing with camp user: {camp_user.email}")
    
    # Login as camp user
    login_data = {
        'email': camp_user.email,
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
    
    print("Login successful!")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get applications
    applications_response = requests.get('http://localhost:8000/api/camp/applications/', 
                                       headers=headers)
    
    print(f"Applications response: {applications_response.status_code}")
    if applications_response.status_code == 200:
        apps_data = applications_response.json()
        print(f"Found {apps_data['count']} applications")
        
        if apps_data['results']:
            app = apps_data['results'][0]
            print(f"Testing with application: {app['id']} - {app['donor_name']}")
            
            # Test approval
            review_data = {
                'application_id': app['id'],
                'decision': 'APPROVED',
                'notes': 'Test approval from API'
            }
            
            review_response = requests.post('http://localhost:8000/api/camp/applications/review/',
                                          json=review_data,
                                          headers=headers)
            
            print(f"Review response: {review_response.status_code}")
            print(f"Review result: {review_response.text}")
            
            if review_response.status_code == 200:
                print("✅ Application review successful!")
                
                # Check database
                db_app = CampApplication.objects.get(id=app['id'])
                print(f"Database status: {db_app.status}")
            else:
                print("❌ Application review failed!")
        else:
            print("No applications found to test")
    else:
        print(f"Applications error: {applications_response.text}")

if __name__ == '__main__':
    test_camp_review()