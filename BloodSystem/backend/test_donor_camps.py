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

def test_donor_camps():
    print("=== TESTING DONOR CAMP VISIBILITY ===")
    
    # Check camps in database
    print("\n1. Checking camps in database...")
    camps = Camp.objects.all()
    print(f"Total camps: {camps.count()}")
    
    for camp in camps:
        print(f"   Camp: {camp.name}")
        print(f"   City: {camp.city}")
        print(f"   Status: {camp.status}")
        print(f"   Is Active: {camp.is_active}")
        print(f"   Date: {camp.date}")
        print()
    
    # Check donor profiles
    print("\n2. Checking donor profiles...")
    donors = DonorProfile.objects.all()[:5]  # First 5 donors
    
    for donor in donors:
        print(f"   Donor: {donor.user.get_full_name()}")
        print(f"   City: {donor.city}")
        print(f"   Email: {donor.user.email}")
        print()
    
    # Test API with a donor
    print("\n3. Testing camp suggestions API...")
    
    donor_user = User.objects.filter(email='donor3@redconnect.com').first()  # Amit Singh in Delhi
    if not donor_user:
        print("❌ Test donor not found!")
        return
    
    print(f"Testing with donor: {donor_user.get_full_name()} in {donor_user.donor_profile.city}")
    
    # Login as donor
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json={'email': donor_user.email, 'password': 'Donor123!'},
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    access_token = login_response.json().get('tokens', {}).get('access')
    print("✅ Login successful")
    
    # Test camp suggestions API
    camps_response = requests.get('http://localhost:8000/api/donor/camps/suggestions/', 
                                headers={'Authorization': f'Bearer {access_token}'})
    
    print(f"Camp suggestions API status: {camps_response.status_code}")
    
    if camps_response.status_code == 200:
        data = camps_response.json()
        print(f"✅ API working - Found {data['count']} camps")
        
        if data['results']:
            for camp in data['results']:
                print(f"   - {camp['name']} in {camp.get('location', 'Unknown location')}")
                print(f"     Date: {camp.get('date', 'No date')}")
                print(f"     Blood groups: {camp.get('blood_groups_needed', [])}")
        else:
            print("   No camps returned by API")
            
            # Debug: Check what camps should be available
            print("\n   Debug: Checking what camps should be available...")
            donor_city = donor_user.donor_profile.city
            available_camps = Camp.objects.filter(
                status='ACTIVE',
                is_active=True,
                city__iexact=donor_city
            )
            print(f"   Camps in {donor_city} with ACTIVE status: {available_camps.count()}")
            
            for camp in available_camps:
                print(f"     - {camp.name} (Date: {camp.date})")
                
            # Check if date filter is the issue
            from django.utils import timezone
            future_camps = available_camps.filter(date__gte=timezone.now().date())
            print(f"   Future camps in {donor_city}: {future_camps.count()}")
            
    else:
        print(f"❌ API failed: {camps_response.status_code}")
        print(camps_response.text)

if __name__ == '__main__':
    test_donor_camps()