#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, CampProfile
from camp.models import Camp

def add_missing_camps():
    print("=== ADDING CAMPS FOR MISSING CITIES ===")
    
    # Create camp organizations for missing cities
    missing_cities_data = [
        {
            'email': 'bloodbank.pune@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Pune Blood Bank Association',
            'city': 'Pune',
            'state': 'Maharashtra',
            'registration_number': 'PBB009'
        },
        {
            'email': 'redcross.kolkata@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Red Cross Society Kolkata',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'registration_number': 'RCK010'
        }
    ]
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    
    for camp_data in missing_cities_data:
        print(f"\nCreating camp organization for {camp_data['city']}...")
        
        # Create user
        user = User.objects.create_user(
            username=camp_data['email'],
            email=camp_data['email'],
            password=camp_data['password'],
            first_name=camp_data['organization_name'].split()[0],
            last_name='Organization',
            phone=f"97654{random.randint(10000, 99999)}",
            role='CAMP',
            is_verified=True
        )
        
        # Create camp profile
        camp_profile = CampProfile.objects.create(
            user=user,
            organization_name=camp_data['organization_name'],
            organization_type='NGO',
            registration_number=camp_data['registration_number'],
            contact_person_name=f"Mr. {random.choice(['Rajesh', 'Priya', 'Suresh', 'Anjali', 'Vikram'])} {random.choice(['Kumar', 'Sharma', 'Singh', 'Gupta', 'Reddy'])}",
            contact_person_designation='Director',
            contact_person_mobile=f"97654{random.randint(10000, 99999)}",
            address_line=f"{random.randint(1, 999)} NGO Street, Social Sector {random.randint(1, 5)}",
            city=camp_data['city'],
            state=camp_data['state'],
            pincode=f"{random.randint(100000, 999999)}",
            verification_status='APPROVED'
        )
        
        print(f"✅ Created camp organization: {camp_data['organization_name']}")
        
        # Create 2-3 camps for this organization
        for i in range(random.randint(2, 3)):
            camp_date = datetime.now().date() + timedelta(days=random.randint(1, 60))
            
            camp = Camp.objects.create(
                organizer=camp_profile,
                name=f"{camp_data['organization_name']} Blood Drive {i+1}",
                description=f"Community blood donation camp organized by {camp_data['organization_name']}",
                location=random.choice(['Community Center', 'School Hall', 'Hospital Premises', 'Mall Complex', 'Corporate Office']),
                address=f"{random.randint(1, 999)} {random.choice(['Main', 'Central', 'Park', 'Market'])} Street",
                city=camp_data['city'],
                state=camp_data['state'],
                pincode=f"{random.randint(100000, 999999)}",
                date=camp_date,
                start_time='09:00',
                end_time='17:00',
                blood_groups_needed=random.sample(blood_groups, random.randint(3, 6)),
                expected_donors=random.randint(50, 200),
                contact_person=camp_profile.contact_person_name,
                contact_phone=camp_profile.contact_person_mobile,
                contact_email=camp_profile.user.email,
                status='ACTIVE',
                is_active=True
            )
            
            print(f"   ✅ Created camp: {camp.name} on {camp.date}")
    
    print("\n=== CAMPS ADDED SUCCESSFULLY ===")
    
    # Verify the fix
    print("\n=== VERIFICATION ===")
    from accounts.models import DonorProfile
    
    # Check all donor cities now have camps
    donor_cities = DonorProfile.objects.values_list('city', flat=True).distinct()
    camp_cities = Camp.objects.values_list('city', flat=True).distinct()
    
    print(f"Donor cities: {list(set(donor_cities))}")
    print(f"Camp cities: {list(set(camp_cities))}")
    
    missing_cities = set(donor_cities) - set(camp_cities)
    if missing_cities:
        print(f"❌ Still missing camps in: {list(missing_cities)}")
    else:
        print("✅ All donor cities now have camps!")
    
    # Print new credentials
    print("\n=== NEW CAMP ORGANIZATION CREDENTIALS ===")
    for camp_data in missing_cities_data:
        print(f"Email: {camp_data['email']}")
        print(f"Password: {camp_data['password']}")
        print(f"Organization: {camp_data['organization_name']}")
        print(f"City: {camp_data['city']}")
        print()

if __name__ == '__main__':
    add_missing_camps()