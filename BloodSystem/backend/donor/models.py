from django.db import models
from django.conf import settings
from accounts.models import User, DonorProfile

class DonationHistory(models.Model):
    """Track donor's donation history"""
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    units_donated = models.PositiveIntegerField(default=1)
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    hemoglobin_level = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'donation_history'
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.donation_date.date()}"


class CampApplication(models.Model):
    """Donor applications to blood camps"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ATTENDED', 'Attended'),
        ('NO_SHOW', 'No Show'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('GOOD', 'Good'),
        ('MINOR', 'Minor Issues'),
    ]
    
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='camp_applications')
    camp = models.ForeignKey('camp.Camp', on_delete=models.CASCADE, related_name='applications')
    
    # Medical Information
    age = models.PositiveIntegerField()
    weight = models.FloatField()
    last_donation_date = models.DateField(null=True, blank=True)
    health_status = models.CharField(max_length=10, choices=HEALTH_STATUS_CHOICES)
    health_issues = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_camp_applications')
    rejection_reason = models.TextField(blank=True)
    
    # Consent
    consent_given = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'camp_applications'
        unique_together = ['donor', 'camp']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.camp.name}"


class DonorHospitalAlert(models.Model):
    """Hospital blood alerts visible to donors"""
    
    URGENCY_CHOICES = [
        ('LOW', 'Low'),
        ('EMERGENCY', 'Emergency'),
        ('DISASTER', 'Disaster'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('FULFILLED', 'Fulfilled'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    hospital = models.ForeignKey('accounts.HospitalProfile', on_delete=models.CASCADE, related_name='donor_alerts')
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='LOW')
    reason = models.TextField()
    
    # Location and timing
    location = models.CharField(max_length=200)
    required_by = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'donor_hospital_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.blood_group} ({self.units_needed} units)"


class DonorHospitalAlertResponse(models.Model):
    """Donor responses to hospital alerts"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]
    
    alert = models.ForeignKey(DonorHospitalAlert, on_delete=models.CASCADE, related_name='donor_responses')
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='hospital_alert_responses')
    
    # Medical Information
    age = models.PositiveIntegerField()
    weight = models.FloatField()
    last_donation_date = models.DateField(null=True, blank=True)
    health_status = models.CharField(max_length=10, choices=CampApplication.HEALTH_STATUS_CHOICES)
    health_issues = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    available_date = models.DateField()
    available_time = models.TimeField()
    
    # Response Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    responded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_donor_alert_responses')
    rejection_reason = models.TextField(blank=True)
    
    # Consent
    consent_given = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'donor_hospital_alert_responses'
        unique_together = ['alert', 'donor']
        ordering = ['-responded_at']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.alert.hospital.hospital_name}"