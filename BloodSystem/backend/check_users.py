#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, DonorProfile
from camp.models import Camp

print("=== USER INFORMATION ===")

print("\nDonor users:")
for user in User.objects.filter(role='DONOR'):
    try:
        profile = user.donor_profile
        print(f"  {user.email} - {user.get_full_name()} - {profile.blood_group} - {profile.city}")
    except:
        print(f"  {user.email} - {user.get_full_name()} - No profile")

print("\nCamp users:")
for user in User.objects.filter(role='CAMP'):
    try:
        profile = user.camp_profile
        print(f"  {user.email} - {profile.organization_name} - Status: {profile.verification_status}")
    except:
        print(f"  {user.email} - No profile")

print("\nActive camps:")
for camp in Camp.objects.filter(status='ACTIVE'):
    print(f"  {camp.id}: {camp.name} by {camp.organizer.organization_name}")

print("\n=== END ===")