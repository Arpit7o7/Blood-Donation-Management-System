#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from donor.models import CampApplication
from camp.models import Camp
from accounts.models import DonorProfile

print("=== CAMP APPLICATION STATUS ===")
print(f"Total camps: {Camp.objects.count()}")
print(f"Total applications: {CampApplication.objects.count()}")

print("\nApplications by status:")
for status in ['PENDING', 'APPROVED', 'REJECTED']:
    count = CampApplication.objects.filter(status=status).count()
    print(f"  {status}: {count}")

print("\nCamps with application counts:")
for camp in Camp.objects.all():
    app_count = camp.applications.count()
    print(f"  {camp.id}: {camp.name} - {app_count} applications")

print("\nDonor profiles:")
donor_count = DonorProfile.objects.count()
print(f"Total donors: {donor_count}")

if CampApplication.objects.exists():
    print("\nExisting applications:")
    for app in CampApplication.objects.all():
        print(f"  App {app.id}: {app.donor.user.get_full_name()} -> {app.camp.name} ({app.status})")
else:
    print("\nNo applications found in database!")

print("\n=== INVESTIGATION COMPLETE ===")