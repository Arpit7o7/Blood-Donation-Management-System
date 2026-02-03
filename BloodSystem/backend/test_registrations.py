#!/usr/bin/env python
"""
Test script to verify all registration endpoints work correctly
"""
import os
import django
import requests
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

API_BASE = 'http://localhost:8000/api'

def test_donor_registration():
    """Test donor registration"""
    data = {
        "user": {
            "first_name": "Test",
            "last_name": "Donor",
            "email": f"donor{datetime.now().timestamp()}@test.com",
            "phone": f"+91{int(datetime.now().timestamp()) % 10000000000}",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "DONOR"
        },
        "blood_group": "O+",
        "city": "Test City",
        "state": "Test State",
        "date_of_birth": "1990-01-01",
        "weight": 70.0,
        "gender": "M"
    }
    
    response = requests.post(f'{API_BASE}/auth/register/donor/', json=data)
    print(f"Donor Registration: {response.status_code}")
    if response.status_code != 201:
        print(f"Error: {response.json()}")
    return response.status_code == 201

def test_hospital_registration():
    """Test hospital registration"""
    timestamp = int(datetime.now().timestamp())
    data = {
        "user": {
            "first_name": "Test",
            "last_name": "Hospital",
            "email": f"hospital{timestamp}@test.com",
            "phone": f"+91{timestamp % 10000000000}",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "HOSPITAL"
        },
        "hospital_name": f"Test Hospital {timestamp}",
        "registration_number": f"REG{timestamp}",
        "issuing_authority": "Health Department",
        "year_of_registration": 2020,
        "address_line": "123 Test Street",
        "area": "Test Area",
        "city": "Test City",
        "district": "Test District",
        "state": "Test State",
        "pincode": "123456",
        "authorized_person_name": "Dr. Test",
        "authorized_person_designation": "Director",
        "authorized_person_mobile": f"+91{(timestamp + 1) % 10000000000}",
        "authorized_person_email": f"director{timestamp}@test.com",
        "has_blood_bank": False
    }
    
    response = requests.post(f'{API_BASE}/auth/register/hospital/', json=data)
    print(f"Hospital Registration: {response.status_code}")
    if response.status_code != 201:
        print(f"Error: {response.json()}")
    return response.status_code == 201

def test_patient_registration():
    """Test patient registration"""
    timestamp = int(datetime.now().timestamp())
    data = {
        "user": {
            "first_name": "Test",
            "last_name": "Patient",
            "email": f"patient{timestamp}@test.com",
            "phone": f"+91{(timestamp + 2) % 10000000000}",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "PATIENT"
        },
        "date_of_birth": "1985-01-01",
        "gender": "F",
        "city": "Test City",
        "state": "Test State",
        "emergency_contact": f"+91{(timestamp + 3) % 10000000000}",
        "emergency_contact_name": "Emergency Contact",
        "emergency_contact_relation": "SPOUSE",
        "blood_group": "A+"
    }
    
    response = requests.post(f'{API_BASE}/auth/register/patient/', json=data)
    print(f"Patient Registration: {response.status_code}")
    if response.status_code != 201:
        print(f"Error: {response.json()}")
    return response.status_code == 201

def test_login():
    """Test login functionality"""
    # First create a test user
    timestamp = int(datetime.now().timestamp())
    email = f"logintest{timestamp}@test.com"
    password = "TestPass123!"
    
    # Register donor
    donor_data = {
        "user": {
            "first_name": "Login",
            "last_name": "Test",
            "email": email,
            "phone": f"+91{(timestamp + 4) % 10000000000}",
            "password": password,
            "confirm_password": password,
            "role": "DONOR"
        },
        "blood_group": "B+",
        "city": "Test City",
        "state": "Test State",
        "weight": 65.0,
        "gender": "M"
    }
    
    reg_response = requests.post(f'{API_BASE}/auth/register/donor/', json=donor_data)
    if reg_response.status_code != 201:
        print(f"Failed to create test user: {reg_response.json()}")
        return False
    
    # Test login
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f'{API_BASE}/auth/login/', json=login_data)
    print(f"Login Test: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing Blood System Registration Endpoints...")
    print("=" * 50)
    
    results = {
        "Donor Registration": test_donor_registration(),
        "Hospital Registration": test_hospital_registration(),
        "Patient Registration": test_patient_registration(),
        "Login Test": test_login()
    }
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")