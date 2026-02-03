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

def test_camp_dashboard():
    print("=== TESTING CAMP DASHBOARD ===")
    
    # Find a camp user
    camp_user = User.objects.filter(role='CAMP', email='testcamp1770017280@test.com').first()
    if not camp_user:
        print("Camp user not found!")
        return
    
    print(f"Testing with camp user: {camp_user.email}")
    
    # Test login
    login_data = {
        'email': camp_user.email,
        'password': 'TestPass123!'
    }
    
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json=login_data,
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_result = login_response.json()
    access_token = login_result.get('tokens', {}).get('access')
    
    if not access_token:
        print("No access token received")
        return
    
    print("Login successful!")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test camp dashboard
    dashboard_response = requests.get('http://localhost:8000/api/camp/dashboard/', headers=headers)
    print(f"Dashboard response status: {dashboard_response.status_code}")
    print(f"Dashboard response: {dashboard_response.text}")
    
    # Test camp applications
    applications_response = requests.get('http://localhost:8000/api/camp/applications/', headers=headers)
    print(f"Applications response status: {applications_response.status_code}")
    print(f"Applications response: {applications_response.text}")

if __name__ == '__main__':
    test_camp_dashboard()