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

def test_camp_creation():
    print("=== TESTING CAMP CREATION API ===")
    
    # Use working camp user
    camp_user = User.objects.filter(email='testcamp1770017280@test.com').first()
    if not camp_user:
        print("Camp user not found!")
        return
    
    print(f"Testing with camp user: {camp_user.email}")
    
    # Login
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
    
    # Test camp creation
    camp_data = {
        'name': 'New Test Camp',
        'description': 'A test camp for API testing',
        'date': '2024-03-15',
        'start_time': '09:00',
        'end_time': '17:00',
        'location': 'Community Center',
        'address': '123 Main Street',
        'city': 'Delhi',
        'state': 'Delhi',
        'pincode': '110001',
        'expected_donors': 100,
        'blood_groups_needed': ['O+', 'A+', 'B+'],
        'contact_person': 'John Doe',
        'contact_phone': '9876543210',
        'contact_email': 'contact@test.com'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"Creating camp with data: {camp_data}")
    
    create_response = requests.post('http://localhost:8000/api/camp/camps/create/',
                                  json=camp_data,
                                  headers=headers)
    
    print(f"Camp creation response: {create_response.status_code}")
    print(f"Response body: {create_response.text}")
    
    if create_response.status_code == 201:
        print("✅ Camp created successfully!")
    else:
        print("❌ Camp creation failed!")

if __name__ == '__main__':
    test_camp_creation()