#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User, DonorProfile, HospitalProfile, CampProfile, PatientProfile
from camp.models import Camp
from donor.models import DonationHistory, CampApplication
from hospital.models import BloodStock, HospitalNetwork
from notifications.models import Notification

def create_dummy_data():
    print("=== CREATING COMPREHENSIVE DUMMY DATA ===")
    
    # Clear existing data (except admin)
    print("\n1. Clearing existing data...")
    User.objects.filter(role__in=['DONOR', 'HOSPITAL', 'CAMP', 'PATIENT']).delete()
    
    # Blood groups for random selection
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']
    states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Maharashtra', 'Gujarat']
    
    created_users = []
    
    # 2. Create Admin Users
    print("\n2. Creating Admin Users...")
    admin_users = [
        {
            'email': 'admin@redconnect.com',
            'password': 'Admin123!',
            'first_name': 'System',
            'last_name': 'Administrator',
            'phone': '9999999999'
        },
        {
            'email': 'superadmin@redconnect.com', 
            'password': 'SuperAdmin123!',
            'first_name': 'Super',
            'last_name': 'Admin',
            'phone': '9999999998'
        }
    ]
    
    for admin_data in admin_users:
        user, created = User.objects.get_or_create(
            email=admin_data['email'],
            defaults={
                'username': admin_data['email'],
                'first_name': admin_data['first_name'],
                'last_name': admin_data['last_name'],
                'phone': admin_data['phone'],
                'role': 'ADMIN',
                'is_verified': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password(admin_data['password'])
            user.save()
            created_users.append({
                'email': admin_data['email'],
                'password': admin_data['password'],
                'role': 'ADMIN',
                'name': f"{admin_data['first_name']} {admin_data['last_name']}"
            })
            print(f"✅ Created admin: {admin_data['email']}")
    
    # 3. Create Hospital Users & Network
    print("\n3. Creating Hospital Network...")
    hospitals_data = [
        {
            'email': 'aiims.delhi@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'All India Institute of Medical Sciences',
            'city': 'Delhi',
            'state': 'Delhi',
            'registration_number': 'AIIMS001',
            'contact_person': 'Dr. Rajesh Kumar',
            'has_blood_bank': True
        },
        {
            'email': 'apollo.mumbai@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Apollo Hospital Mumbai',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'registration_number': 'APL002',
            'contact_person': 'Dr. Priya Sharma',
            'has_blood_bank': True
        },
        {
            'email': 'fortis.bangalore@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Fortis Hospital Bangalore',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'registration_number': 'FOR003',
            'contact_person': 'Dr. Suresh Reddy',
            'has_blood_bank': True
        },
        {
            'email': 'max.delhi@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Max Super Speciality Hospital',
            'city': 'Delhi',
            'state': 'Delhi',
            'registration_number': 'MAX004',
            'contact_person': 'Dr. Anjali Gupta',
            'has_blood_bank': True
        },
        {
            'email': 'manipal.bangalore@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Manipal Hospital Bangalore',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'registration_number': 'MAN005',
            'contact_person': 'Dr. Vikram Singh',
            'has_blood_bank': True
        },
        {
            'email': 'lilavati.mumbai@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Lilavati Hospital Mumbai',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'registration_number': 'LIL006',
            'contact_person': 'Dr. Meera Joshi',
            'has_blood_bank': False
        },
        {
            'email': 'christian.chennai@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Christian Medical College',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'registration_number': 'CMC007',
            'contact_person': 'Dr. Tamil Selvan',
            'has_blood_bank': True
        },
        {
            'email': 'ruby.kolkata@hospital.com',
            'password': 'Hospital123!',
            'hospital_name': 'Ruby General Hospital',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'registration_number': 'RUB008',
            'contact_person': 'Dr. Amit Banerjee',
            'has_blood_bank': True
        }
    ]
    
    hospital_profiles = []
    for hospital_data in hospitals_data:
        user = User.objects.create_user(
            username=hospital_data['email'],
            email=hospital_data['email'],
            password=hospital_data['password'],
            first_name=hospital_data['contact_person'].split()[1],
            last_name=hospital_data['contact_person'].split()[-1],
            phone=f"98765{random.randint(10000, 99999)}",
            role='HOSPITAL',
            is_verified=True
        )
        
        hospital_profile = HospitalProfile.objects.create(
            user=user,
            hospital_name=hospital_data['hospital_name'],
            registration_number=hospital_data['registration_number'],
            issuing_authority='Ministry of Health',
            year_of_registration=random.randint(1990, 2020),
            address_line=f"{random.randint(1, 999)} Medical Street, Medical District {random.randint(1, 10)}",
            area=f"Medical District {random.randint(1, 10)}",
            city=hospital_data['city'],
            district=hospital_data['city'],
            state=hospital_data['state'],
            pincode=f"{random.randint(100000, 999999)}",
            authorized_person_name=hospital_data['contact_person'],
            authorized_person_designation='Chief Medical Officer',
            authorized_person_mobile=f"98765{random.randint(10000, 99999)}",
            authorized_person_email=hospital_data['email'],
            has_blood_bank=hospital_data['has_blood_bank'],
            blood_bank_license=f"BB{hospital_data['registration_number']}" if hospital_data['has_blood_bank'] else '',
            storage_capacity=random.randint(100, 500) if hospital_data['has_blood_bank'] else None,
            verification_status='APPROVED'
        )
        
        hospital_profiles.append(hospital_profile)
        
        # Create blood stock for hospitals with blood banks
        if hospital_data['has_blood_bank']:
            for blood_group in blood_groups:
                BloodStock.objects.create(
                    hospital=hospital_profile,
                    blood_group=blood_group,
                    units_available=random.randint(5, 50),
                    units_reserved=random.randint(0, 5),
                    expiry_alerts=random.randint(0, 3)
                )
        
        created_users.append({
            'email': hospital_data['email'],
            'password': hospital_data['password'],
            'role': 'HOSPITAL',
            'name': hospital_data['hospital_name'],
            'city': hospital_data['city']
        })
        print(f"✅ Created hospital: {hospital_data['hospital_name']}")
    
    # Create hospital network connections
    print("\n   Creating hospital network connections...")
    for i, hospital1 in enumerate(hospital_profiles):
        for j, hospital2 in enumerate(hospital_profiles):
            if i != j and hospital1.city == hospital2.city:
                # Connect hospitals in same city
                network, created = HospitalNetwork.objects.get_or_create(
                    requesting_hospital=hospital1,
                    providing_hospital=hospital2,
                    defaults={
                        'blood_group': random.choice(blood_groups),
                        'units_requested': random.randint(5, 20),
                        'reason': 'Emergency blood requirement',
                        'urgency': 'LOW',
                        'required_by': datetime.now() + timedelta(days=random.randint(1, 7)),
                        'status': 'APPROVED',
                        'requested_by': hospital1.user
                    }
                )
    
    # 4. Create Camp Organizations
    print("\n4. Creating Camp Organizations...")
    camps_data = [
        {
            'email': 'redcross.delhi@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Indian Red Cross Society Delhi',
            'city': 'Delhi',
            'state': 'Delhi',
            'registration_number': 'IRC001'
        },
        {
            'email': 'blooddonors.mumbai@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Mumbai Blood Donors Association',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'registration_number': 'MBDA002'
        },
        {
            'email': 'lifegivers.bangalore@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Life Givers Foundation',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'registration_number': 'LGF003'
        },
        {
            'email': 'savelife.chennai@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Save Life Blood Bank',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'registration_number': 'SLB004'
        },
        {
            'email': 'bloodheroes.hyderabad@camp.org',
            'password': 'Camp123!',
            'organization_name': 'Blood Heroes Hyderabad',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'registration_number': 'BHH005'
        }
    ]
    
    camp_profiles = []
    for camp_data in camps_data:
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
        
        camp_profiles.append(camp_profile)
        
        created_users.append({
            'email': camp_data['email'],
            'password': camp_data['password'],
            'role': 'CAMP',
            'name': camp_data['organization_name'],
            'city': camp_data['city']
        })
        print(f"✅ Created camp organization: {camp_data['organization_name']}")
    
    # 5. Create Blood Camps
    print("\n5. Creating Blood Donation Camps...")
    for camp_profile in camp_profiles:
        for i in range(random.randint(2, 4)):  # 2-4 camps per organization
            camp_date = datetime.now().date() + timedelta(days=random.randint(1, 60))
            
            Camp.objects.create(
                organizer=camp_profile,
                name=f"{camp_profile.organization_name} Blood Drive {i+1}",
                description=f"Community blood donation camp organized by {camp_profile.organization_name}",
                location=random.choice(['Community Center', 'School Hall', 'Hospital Premises', 'Mall Complex', 'Corporate Office']),
                address=f"{random.randint(1, 999)} {random.choice(['Main', 'Central', 'Park', 'Market'])} Street",
                city=camp_profile.city,
                state=camp_profile.state,
                pincode=camp_profile.pincode,
                date=camp_date,
                start_time='09:00',
                end_time='17:00',
                blood_groups_needed=random.sample(blood_groups, random.randint(3, 6)),
                expected_donors=random.randint(50, 200),
                contact_person=camp_profile.contact_person_name,
                contact_phone=camp_profile.contact_person_mobile,
                contact_email=camp_profile.user.email,
                status='ACTIVE'
            )
    
    # 6. Create Donor Users
    print("\n6. Creating Donor Users...")
    donor_names = [
        ('Rahul', 'Sharma'), ('Priya', 'Patel'), ('Amit', 'Singh'), ('Sneha', 'Gupta'),
        ('Vikram', 'Reddy'), ('Anjali', 'Kumar'), ('Suresh', 'Joshi'), ('Meera', 'Agarwal'),
        ('Rajesh', 'Verma'), ('Pooja', 'Malhotra'), ('Arjun', 'Nair'), ('Kavya', 'Iyer'),
        ('Rohit', 'Chopra'), ('Divya', 'Bansal'), ('Karan', 'Mehta'), ('Riya', 'Saxena'),
        ('Aditya', 'Tiwari'), ('Shreya', 'Pandey'), ('Nikhil', 'Jain'), ('Ananya', 'Sinha')
    ]
    
    donor_profiles = []
    for i, (first_name, last_name) in enumerate(donor_names):
        city = random.choice(cities)
        state = states[cities.index(city)]
        
        user = User.objects.create_user(
            username=f"donor{i+1}@redconnect.com",
            email=f"donor{i+1}@redconnect.com",
            password='Donor123!',
            first_name=first_name,
            last_name=last_name,
            phone=f"98765{random.randint(10000, 99999)}",
            role='DONOR',
            is_verified=True
        )
        
        donor_profile = DonorProfile.objects.create(
            user=user,
            blood_group=random.choice(blood_groups),
            city=city,
            state=state,
            date_of_birth=datetime.now().date() - timedelta(days=random.randint(18*365, 60*365)),
            weight=random.randint(55, 90),
            gender=random.choice(['M', 'F'])
        )
        
        donor_profiles.append(donor_profile)
        
        # Create some donation history
        if random.choice([True, False]):  # 50% chance of having donation history
            for j in range(random.randint(1, 5)):
                donation_date = datetime.now() - timedelta(days=random.randint(60, 365*3))
                DonationHistory.objects.create(
                    donor=donor_profile,
                    donation_date=donation_date,
                    location=f"{random.choice(['Hospital', 'Camp', 'Blood Bank'])} - {city}",
                    units_donated=1,
                    blood_group=donor_profile.blood_group,
                    hemoglobin_level=random.uniform(12.0, 16.0),
                    notes='Successful donation'
                )
        
        created_users.append({
            'email': f"donor{i+1}@redconnect.com",
            'password': 'Donor123!',
            'role': 'DONOR',
            'name': f"{first_name} {last_name}",
            'city': city,
            'blood_group': donor_profile.blood_group
        })
        
        if i < 5:  # Print first 5
            print(f"✅ Created donor: {first_name} {last_name} ({donor_profile.blood_group})")
    
    print(f"✅ Created {len(donor_names)} donors total")
    
    # 7. Create Patient Users
    print("\n7. Creating Patient Users...")
    patient_names = [
        ('Ravi', 'Kumar'), ('Sunita', 'Devi'), ('Manoj', 'Yadav'), ('Geeta', 'Sharma'),
        ('Sunil', 'Prasad'), ('Kamala', 'Singh'), ('Deepak', 'Gupta'), ('Usha', 'Patel'),
        ('Ramesh', 'Tiwari'), ('Sita', 'Verma'), ('Ajay', 'Mishra'), ('Rekha', 'Joshi'),
        ('Vinod', 'Agarwal'), ('Pushpa', 'Bansal'), ('Mohan', 'Saxena')
    ]
    
    for i, (first_name, last_name) in enumerate(patient_names):
        city = random.choice(cities)
        state = states[cities.index(city)]
        
        user = User.objects.create_user(
            username=f"patient{i+1}@redconnect.com",
            email=f"patient{i+1}@redconnect.com",
            password='Patient123!',
            first_name=first_name,
            last_name=last_name,
            phone=f"96543{random.randint(10000, 99999)}",
            role='PATIENT',
            is_verified=True
        )
        
        PatientProfile.objects.create(
            user=user,
            blood_group=random.choice(blood_groups),
            city=city,
            state=state,
            date_of_birth=datetime.now().date() - timedelta(days=random.randint(25*365, 80*365)),
            gender=random.choice(['M', 'F']),
            emergency_contact=f"95432{random.randint(10000, 99999)}",
            emergency_contact_name=f"Emergency Contact {i+1}",
            emergency_contact_relation='RELATIVE',
            medical_conditions=random.choice(['Surgery', 'Accident', 'Cancer Treatment', 'Anemia', 'Thalassemia'])
        )
        
        created_users.append({
            'email': f"patient{i+1}@redconnect.com",
            'password': 'Patient123!',
            'role': 'PATIENT',
            'name': f"{first_name} {last_name}",
            'city': city
        })
        
        if i < 5:  # Print first 5
            print(f"✅ Created patient: {first_name} {last_name}")
    
    print(f"✅ Created {len(patient_names)} patients total")
    
    # 8. Create some camp applications
    print("\n8. Creating Camp Applications...")
    camps = Camp.objects.all()
    application_count = 0
    
    for donor_profile in donor_profiles[:10]:  # First 10 donors apply to camps
        available_camps = camps.filter(city=donor_profile.city)[:2]  # Apply to max 2 camps in same city
        
        for camp in available_camps:
            if random.choice([True, False]):  # 50% chance of applying
                CampApplication.objects.create(
                    donor=donor_profile,
                    camp=camp,
                    age=2024 - donor_profile.date_of_birth.year,
                    weight=donor_profile.weight,
                    last_donation_date=None if not donor_profile.donations.exists() else donor_profile.donations.first().donation_date.date(),
                    health_status='GOOD',
                    health_issues='',
                    medications='',
                    status=random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                    consent_given=True
                )
                application_count += 1
    
    print(f"✅ Created {application_count} camp applications")
    
    # 9. Create some notifications
    print("\n9. Creating Sample Notifications...")
    notification_count = 0
    
    for donor_profile in donor_profiles[:5]:  # Create notifications for first 5 donors
        # Application submitted notification
        Notification.objects.create(
            recipient=donor_profile.user,
            title='Welcome to RedConnect!',
            message='Thank you for joining our blood donation community. Start saving lives today!',
            notification_type='CAMP_APPROVAL'
        )
        
        # Random camp approval/rejection
        if random.choice([True, False]):
            Notification.objects.create(
                recipient=donor_profile.user,
                title='Camp Application Approved',
                message=f'Your application for blood donation camp has been approved. Please arrive on time.',
                notification_type='CAMP_APPROVAL'
            )
        else:
            Notification.objects.create(
                recipient=donor_profile.user,
                title='Camp Application Update',
                message='Thank you for your interest. We will notify you about upcoming camps.',
                notification_type='CAMP_REJECTION'
            )
        
        notification_count += 2
    
    print(f"✅ Created {notification_count} notifications")
    
    print("\n=== DUMMY DATA CREATION COMPLETE ===")
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"   👥 Total Users Created: {len(created_users)}")
    print(f"   🏥 Hospitals: {len([u for u in created_users if u['role'] == 'HOSPITAL'])}")
    print(f"   🏕️ Camp Organizations: {len([u for u in created_users if u['role'] == 'CAMP'])}")
    print(f"   🩸 Donors: {len([u for u in created_users if u['role'] == 'DONOR'])}")
    print(f"   🏥 Patients: {len([u for u in created_users if u['role'] == 'PATIENT'])}")
    print(f"   👨‍💼 Admins: {len([u for u in created_users if u['role'] == 'ADMIN'])}")
    print(f"   🏕️ Blood Camps: {Camp.objects.count()}")
    print(f"   📋 Camp Applications: {CampApplication.objects.count()}")
    print(f"   🔔 Notifications: {Notification.objects.count()}")
    
    return created_users

if __name__ == '__main__':
    users = create_dummy_data()
    
    # Print all credentials
    print("\n" + "="*80)
    print("🔑 ALL USER CREDENTIALS")
    print("="*80)
    
    # Group by role
    roles = ['ADMIN', 'HOSPITAL', 'CAMP', 'DONOR', 'PATIENT']
    
    for role in roles:
        role_users = [u for u in users if u['role'] == role]
        if role_users:
            print(f"\n📋 {role} USERS ({len(role_users)}):")
            print("-" * 50)
            
            for user in role_users:
                extra_info = ""
                if 'city' in user:
                    extra_info += f" | {user['city']}"
                if 'blood_group' in user:
                    extra_info += f" | {user['blood_group']}"
                
                print(f"   Email: {user['email']}")
                print(f"   Password: {user['password']}")
                print(f"   Name: {user['name']}{extra_info}")
                print()
    
    print("="*80)
    print("🎉 READY TO TEST! Login with any of the above credentials.")
    print("="*80)