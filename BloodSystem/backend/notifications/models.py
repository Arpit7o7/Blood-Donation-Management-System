from django.db import models
from accounts.models import User

class Notification(models.Model):
    """System notifications"""
    NOTIFICATION_TYPES = [
        ('CAMP_APPROVAL', 'Camp Approval'),
        ('CAMP_REJECTION', 'Camp Rejection'),
        ('HOSPITAL_APPROVAL', 'Hospital Approval'),
        ('HOSPITAL_REJECTION', 'Hospital Rejection'),
        ('EMERGENCY_ALERT', 'Emergency Alert'),
        ('DISASTER_ALERT', 'Disaster Alert'),
        ('ATTENDANCE_MARKED', 'Attendance Marked'),
        ('BLOOD_REQUEST', 'Blood Request'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"