#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, CampProfile
from camp.models import Camp
from donor.models import CampApplication

print("=== CAMP OWNERSHIP ANALYSIS ===")

print("\nCamp organizations:")
for profile in CampProfile.objects.all():
    print(f"  {profile.user.email} -> {profile.organization_name}")

print("\nCamps and their organizers:")
for camp in Camp.objects.all():
    print(f"  Camp {camp.id}: '{camp.name}' organized by '{camp.organizer.organization_name}' ({camp.organizer.user.email})")

print("\nApplications and their target camps:")
for app in CampApplication.objects.all():
    print(f"  Application {app.id}: {app.donor.user.get_full_name()} -> Camp '{app.camp.name}' by '{app.camp.organizer.organization_name}'")

print("\n=== END ===")