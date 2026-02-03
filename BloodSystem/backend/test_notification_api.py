#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from accounts.models import User

def test_notification_api():
    print("=== TESTING NOTIFICATION API ===")
    
    # Login as donor
    donor_user = User.objects.filter(email='testdonor@test.com').first()
    if not donor_user:
        print("❌ Test donor not found!")
        return
    
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json={'email': donor_user.email, 'password': 'TestPass123!'},
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    access_token = login_response.json().get('tokens', {}).get('access')
    print("✅ Login successful")
    
    # Test notifications API
    headers = {'Authorization': f'Bearer {access_token}'}
    
    notifications_response = requests.get('http://localhost:8000/api/notifications/', 
                                        headers=headers)
    
    print(f"Notifications API status: {notifications_response.status_code}")
    
    if notifications_response.status_code == 200:
        data = notifications_response.json()
        print(f"✅ API working - Found {data['count']} notifications")
        print(f"   Unread count: {data.get('unread_count', 0)}")
        
        for i, notif in enumerate(data['results']):
            print(f"   {i+1}. {notif['title']}")
            print(f"      Message: {notif['message']}")
            print(f"      Type: {notif['notification_type']}")
            print(f"      Read: {notif['is_read']}")
            print(f"      Created: {notif['created_at']}")
            print()
    else:
        print(f"❌ API failed: {notifications_response.status_code}")
        print(notifications_response.text)

if __name__ == '__main__':
    test_notification_api()