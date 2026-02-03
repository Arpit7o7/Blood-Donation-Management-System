from django.db import models
from django.conf import settings
from accounts.models import HospitalProfile, PatientProfile

class BloodStock(models.Model):
    """Hospital blood stock management"""
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='blood_stock')
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_available = models.PositiveIntegerField(default=0)
    units_reserved = models.PositiveIntegerField(default=0)
    expiry_alerts = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospital_blood_stock'
        unique_together = ['hospital', 'blood_group']
    
    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.blood_group}: {self.units_available} units"
    
    @property
    def status(self):
        if self.units_available >= 10:
            return 'GOOD'
        elif self.units_available >= 5:
            return 'LOW'
        else:
            return 'CRITICAL'


class HospitalPatientRequest(models.Model):
    """Patient blood requests managed by hospitals"""
    REQUEST_TYPES = [
        ('NORMAL', 'Normal'),
        ('EMERGENCY', 'Emergency'),
        ('DISASTER', 'Disaster'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='hospital_requests')
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='patient_blood_requests')
    
    # Blood requirements
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='NORMAL')
    
    # Emergency details
    emergency_reason = models.TextField(blank=True)
    required_by = models.DateTimeField()
    doctor_name = models.CharField(max_length=200, blank=True)
    doctor_contact = models.CharField(max_length=15, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_hospital_requests')
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'hospital_patient_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.blood_group} ({self.units_needed} units)"


class HospitalNetwork(models.Model):
    """Inter-hospital blood exchange network"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    URGENCY_CHOICES = [
        ('LOW', 'Low'),
        ('EMERGENCY', 'Emergency'),
        ('DISASTER', 'Disaster'),
    ]
    
    requesting_hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='blood_requests_sent')
    providing_hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='blood_requests_received')
    
    # Blood details
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_requested = models.PositiveIntegerField()
    units_approved = models.PositiveIntegerField(default=0)
    
    # Request details
    reason = models.TextField()
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='LOW')
    required_by = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Staff
    requested_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='network_requests_made')
    responded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='network_requests_handled')
    
    # Notes
    response_notes = models.TextField(blank=True)
    completion_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'hospital_network'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.requesting_hospital.hospital_name} → {self.providing_hospital.hospital_name} ({self.blood_group})"