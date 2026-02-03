#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import DonorProfile
from camp.models import Camp

def check_donor_city_match():
    print("=== CHECKING DONOR-CAMP CITY MATCHES ===")
    
    # Get all camp cities
    camp_cities = Camp.objects.values_list('city', flat=True).distinct()
    print(f"Cities with camps: {list(camp_cities)}")
    
    # Get all donor cities
    donor_cities = DonorProfile.objects.values_list('city', flat=True).distinct()
    print(f"Cities with donors: {list(donor_cities)}")
    
    # Find matches
    matching_cities = set(camp_cities) & set(donor_cities)
    print(f"Matching cities: {list(matching_cities)}")
    
    print("\n=== DONORS IN CITIES WITH CAMPS ===")
    for city in matching_cities:
        donors_in_city = DonorProfile.objects.filter(city=city)
        camps_in_city = Camp.objects.filter(city=city).count()
        
        print(f"\n{city}:")
        print(f"  Camps: {camps_in_city}")
        print(f"  Donors: {donors_in_city.count()}")
        
        for donor in donors_in_city:
            print(f"    - {donor.user.email} ({donor.user.get_full_name()}) - {donor.blood_group}")
    
    print("\n=== DONORS IN CITIES WITHOUT CAMPS ===")
    cities_without_camps = set(donor_cities) - set(camp_cities)
    for city in cities_without_camps:
        donors_in_city = DonorProfile.objects.filter(city=city)
        print(f"\n{city}:")
        for donor in donors_in_city:
            print(f"    - {donor.user.email} ({donor.user.get_full_name()}) - {donor.blood_group}")

if __name__ == '__main__':
    check_donor_city_match()