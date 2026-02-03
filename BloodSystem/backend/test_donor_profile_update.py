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

def test_donor_profile_update():
    print("=== TESTING DONOR PROFILE UPDATE ===")
    
    # Use test donor
    donor_user = User.objects.filter(email='testdonor@test.com').first()
    if not donor_user:
        print("Test donor not found!")
        return
    
    print(f"Testing with donor: {donor_user.email}")
    
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
    
    print("Login successful!")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test profile update
    update_data = {
        'first_name': 'Updated',
        'last_name': 'Donor',
        'phone': '9999999998',
        'blood_group': 'A+',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'weight': 75.0,
        'gender': 'MALE'
    }
    
    print(f"Updating profile with data: {update_data}")
    
    update_response = requests.put('http://localhost:8000/api/donor/profile/update/',
                                 json=update_data,
                                 headers=headers)
    
    print(f"Update response: {update_response.status_code}")
    print(f"Update result: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✅ Profile update successful!")
        
        # Verify in database
        donor_user.refresh_from_db()
        profile = donor_user.donor_profile
        print(f"Database verification:")
        print(f"  Name: {donor_user.first_name} {donor_user.last_name}")
        print(f"  Phone: {donor_user.phone}")
        print(f"  Blood Group: {profile.blood_group}")
        print(f"  City: {profile.city}")
        print(f"  Weight: {profile.weight}")
    else:
        print("❌ Profile update failed!")

if __name__ == '__main__':
    test_donor_profile_update()