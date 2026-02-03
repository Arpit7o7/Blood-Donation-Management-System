from django.db import models
from django.conf import settings
from accounts.models import PatientProfile, HospitalProfile

class BloodRequest(models.Model):
    """Patient blood requests"""
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
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='blood_requests')
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='received_blood_requests')
    
    # Blood requirements
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='NORMAL')
    
    # Emergency details
    emergency_reason = models.TextField(blank=True)
    emergency_justification = models.TextField(blank=True, help_text="Detailed justification for emergency request")
    required_by = models.DateTimeField()
    
    # Medical details
    doctor_name = models.CharField(max_length=200, blank=True)
    doctor_contact = models.CharField(max_length=15, blank=True)
    medical_condition = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Admin approval for emergency requests
    admin_approved = models.BooleanField(default=False)
    admin_approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_emergency_requests')
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'blood_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.blood_group} ({self.units_needed} units)"
    
    @property
    def requires_admin_approval(self):
        return self.request_type in ['EMERGENCY', 'DISASTER']