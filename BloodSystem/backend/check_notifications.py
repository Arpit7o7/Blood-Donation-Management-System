#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from notifications.models import Notification
from accounts.models import User

print("=== NOTIFICATION SYSTEM CHECK ===")

print(f"\nTotal notifications in database: {Notification.objects.count()}")

print("\nNotifications by user:")
for user in User.objects.all():
    count = Notification.objects.filter(recipient=user).count()
    if count > 0:
        print(f"  {user.email}: {count} notifications")

print("\nAll notifications:")
for notification in Notification.objects.all():
    print(f"  {notification.id}: {notification.recipient.email} - {notification.title} [{notification.notification_type}] {'(unread)' if not notification.is_read else '(read)'}")

print("\n=== END CHECK ===")