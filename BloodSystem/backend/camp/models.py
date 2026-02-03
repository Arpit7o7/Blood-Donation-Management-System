from django.db import models
from django.conf import settings
from accounts.models import CampProfile, DonorProfile

class Camp(models.Model):
    """Blood donation camps"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    organizer = models.ForeignKey(CampProfile, on_delete=models.CASCADE, related_name='camps')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Location
    location = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Timing
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Requirements
    blood_groups_needed = models.JSONField(default=list, help_text="List of blood groups needed")
    expected_donors = models.PositiveIntegerField(default=50)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_active = models.BooleanField(default=True)
    
    # Contact
    contact_person = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'camps'
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.date >= timezone.now().date()
    
    @property
    def applications_count(self):
        return self.applications.count()
    
    @property
    def approved_applications_count(self):
        return self.applications.filter(status='APPROVED').count()


class CampRequirement(models.Model):
    """Specific blood group requirements for camps"""
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='requirements')
    blood_group = models.CharField(max_length=3, choices=settings.BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    units_collected = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'camp_requirements'
        unique_together = ['camp', 'blood_group']
    
    def __str__(self):
        return f"{self.camp.name} - {self.blood_group}: {self.units_needed} units"


class CampAttendance(models.Model):
    """Track donor attendance at camps"""
    
    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('CHECKED_IN', 'Checked In'),
        ('DONATED', 'Donated'),
        ('DEFERRED', 'Deferred'),
        ('NO_SHOW', 'No Show'),
    ]
    
    camp = models.ForeignKey(Camp, on_delete=models.CASCADE, related_name='attendance')
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='camp_attendance')
    
    # Attendance details
    check_in_time = models.DateTimeField(null=True, blank=True)
    donation_time = models.DateTimeField(null=True, blank=True)
    units_donated = models.PositiveIntegerField(default=0)
    
    # Medical screening
    hemoglobin_level = models.FloatField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REGISTERED')
    notes = models.TextField(blank=True)
    
    # Staff
    checked_in_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_donors')
    donation_recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_donations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'camp_attendance'
        unique_together = ['camp', 'donor']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.camp.name}"