#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, DonorProfile

def create_test_donor():
    email = 'testdonor@test.com'
    password = 'TestPass123!'
    
    # Delete existing user if exists
    User.objects.filter(email=email).delete()
    
    # Create new user
    user = User.objects.create_user(
        username=email,  # Use email as username
        email=email,
        password=password,
        first_name='Test',
        last_name='Donor',
        phone='9999999999',
        role='DONOR'
    )
    
    # Create donor profile
    donor_profile = DonorProfile.objects.create(
        user=user,
        blood_group='O+',
        city='Delhi',
        state='Delhi',
        weight=70.0,
        gender='MALE'
    )
    
    print(f"Created test donor: {email} with password: {password}")
    print(f"Profile: {donor_profile.blood_group}, {donor_profile.city}")
    
    return user

if __name__ == '__main__':
    create_test_donor()