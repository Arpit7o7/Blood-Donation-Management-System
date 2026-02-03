#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User

# Create admin user
try:
    admin_user = User.objects.create_superuser(
        username='admin@redconnect.com',
        email='admin@redconnect.com',
        password='admin123',
        phone='+9999999999',
        role='ADMIN',
        first_name='Admin',
        last_name='User'
    )
    print(f"Admin user created: {admin_user.email}")
except Exception as e:
    print(f"Error creating admin user: {e}")