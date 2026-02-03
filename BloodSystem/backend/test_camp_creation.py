#!/usr/bin/env python
"""
Test script to verify camp creation functionality
"""
import os
import django
import requests
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, CampProfile

API_BASE = 'http://localhost:8000/api'

def create_test_camp_user():
    """Create a test camp user"""
    timestamp = int(datetime.now().timestamp())
    
    # Create user
    user = User.objects.create_user(
        username=f'testcamp{timestamp}@test.com',
        email=f'testcamp{timestamp}@test.com',
        phone=f'+91{timestamp % 10000000000}',
        password='TestPass123!',
        role='CAMP',
        first_name='Test',
        last_name='Camp'
    )
    
    # Create camp profile
    camp_profile = CampProfile.objects.create(
        user=user,
        organization_name=f'Test Camp Org {timestamp}',
        organization_type='NGO',
        registration_number=f'CAMP{timestamp}',
        contact_person_name='Test Contact',
        contact_person_designation='Manager',
        contact_person_mobile=f'+91{(timestamp + 1) % 10000000000}',
        address_line='123 Test Street',
        city='Test City',
        state='Test State',
        pincode='123456',
        verification_status='APPROVED'  # Pre-approve for testing
    )
    
    return user.email, 'TestPass123!'

def test_camp_login_and_creation():
    """Test camp login and creation"""
    
    # Create test camp user
    email, password = create_test_camp_user()
    print(f"Created test camp user: {email}")
    
    # Test login
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f'{API_BASE}/auth/login/', json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.json()}")
        return False
    
    login_result = response.json()
    token = login_result['tokens']['access']
    print("Login successful, got token")
    
    # Test camp creation
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    camp_data = {
        "name": "Test Blood Camp",
        "description": "A test blood donation camp",
        "date": tomorrow,
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "location": "Community Center",
        "address": "123 Main Street",
        "city": "Test City",
        "state": "Test State",
        "pincode": "123456",
        "expected_donors": 100,
        "blood_groups_needed": ["A+", "B+", "O+", "AB+"],
        "contact_person": "Test Contact",
        "contact_phone": "+919999999999",
        "contact_email": "contact@testcamp.com"
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f'{API_BASE}/camp/camps/create/', json=camp_data, headers=headers)
    print(f"Camp creation response: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"Camp created successfully: {result}")
        return True
    else:
        print(f"Camp creation failed: {response.json()}")
        return False

if __name__ == "__main__":
    print("Testing Camp Creation Functionality...")
    print("=" * 50)
    
    success = test_camp_login_and_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Camp creation test PASSED")
    else:
        print("❌ Camp creation test FAILED")