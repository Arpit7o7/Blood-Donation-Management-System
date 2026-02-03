from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractUser):
    """Custom User model with role-based authentication"""
    
    ROLE_CHOICES = [
        ('DONOR', 'Donor'),
        ('HOSPITAL', 'Hospital'),
        ('CAMP', 'Camp'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'role']
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    class Meta:
        db_table = 'auth_user'


class DonorProfile(models.Model):
    """Extended profile for donors"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    is_eligible = models.BooleanField(default=True)
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions")
    medications = models.TextField(blank=True, help_text="Current medications")
    emergency_contact = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"
    
    class Meta:
        db_table = 'donor_profiles'


class HospitalProfile(models.Model):
    """Extended profile for hospitals"""
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    issuing_authority = models.CharField(max_length=200)
    year_of_registration = models.PositiveIntegerField()
    
    # Address
    address_line = models.TextField()
    area = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Authorized Person
    authorized_person_name = models.CharField(max_length=200)
    authorized_person_designation = models.CharField(max_length=100)
    authorized_person_mobile = models.CharField(max_length=15)
    authorized_person_email = models.EmailField()
    
    # Blood Bank Details
    has_blood_bank = models.BooleanField(default=False)
    blood_bank_license = models.CharField(max_length=100, blank=True)
    storage_capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Storage capacity in units")
    
    # Documents
    registration_certificate = models.FileField(upload_to='hospital_docs/', null=True, blank=True)
    blood_bank_license_doc = models.FileField(upload_to='hospital_docs/', null=True, blank=True)
    authorization_letter = models.FileField(upload_to='hospital_docs/', null=True, blank=True)
    hospital_seal = models.FileField(upload_to='hospital_docs/', null=True, blank=True)
    
    # Status
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_hospitals')
    verification_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hospital_name} - {self.verification_status}"
    
    class Meta:
        db_table = 'hospital_profiles'


class CampProfile(models.Model):
    """Extended profile for camps (Hospital/NGO)"""
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    ORGANIZATION_TYPE = [
        ('HOSPITAL', 'Hospital'),
        ('NGO', 'NGO'),
        ('GOVERNMENT', 'Government'),
        ('CORPORATE', 'Corporate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='camp_profile')
    organization_name = models.CharField(max_length=200)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPE)
    registration_number = models.CharField(max_length=100, unique=True)
    
    # Contact Details
    contact_person_name = models.CharField(max_length=200)
    contact_person_designation = models.CharField(max_length=100)
    contact_person_mobile = models.CharField(max_length=15)
    
    # Address
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Documents
    organization_certificate = models.FileField(upload_to='camp_docs/', null=True, blank=True)
    authorization_letter = models.FileField(upload_to='camp_docs/', null=True, blank=True)
    
    # Status
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_camps')
    verification_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organization_name} - {self.verification_status}"
    
    class Meta:
        db_table = 'camp_profiles'


class PatientProfile(models.Model):
    """Extended profile for patients"""
    
    RELATION_CHOICES = [
        ('SPOUSE', 'Spouse'),
        ('PARENT', 'Parent'),
        ('CHILD', 'Child'),
        ('SIBLING', 'Sibling'),
        ('RELATIVE', 'Relative'),
        ('FRIEND', 'Friend'),
        ('GUARDIAN', 'Guardian'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default='RELATIVE')
    medical_conditions = models.TextField(blank=True)
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"
    
    class Meta:
        db_table = 'patient_profiles'


class AdminProfile(models.Model):
    """Extended profile for admin users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict, help_text="Admin specific permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Admin"
    
    class Meta:
        db_table = 'admin_profiles'