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
from notifications.models import Notification
from notifications.views import create_notification

def test_notification_system():
    print("=== TESTING NOTIFICATION SYSTEM ===")
    
    # Test 1: Create a test notification
    print("\n1. Creating test notification...")
    
    donor_user = User.objects.filter(email='testdonor@test.com').first()
    if not donor_user:
        print("❌ Test donor not found!")
        return
    
    # Create a test notification
    notification = create_notification(
        recipient=donor_user,
        title='Test Notification',
        message='This is a test notification to verify the system works.',
        notification_type='CAMP_APPROVAL'
    )
    
    print(f"✅ Created notification: {notification.id}")
    
    # Test 2: Check database
    print("\n2. Checking database...")
    total_notifications = Notification.objects.count()
    user_notifications = Notification.objects.filter(recipient=donor_user).count()
    
    print(f"Total notifications: {total_notifications}")
    print(f"User notifications: {user_notifications}")
    
    # Test 3: Test API endpoint
    print("\n3. Testing notification API...")
    
    # Login as donor
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json={'email': donor_user.email, 'password': 'TestPass123!'},
                                 headers={'Content-Type': 'application/json'})
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    access_token = login_response.json().get('tokens', {}).get('access')
    print("✅ Login successful")
    
    # Get notifications via API
    notifications_response = requests.get('http://localhost:8000/api/notifications/', 
                                        headers={'Authorization': f'Bearer {access_token}'})
    
    print(f"Notifications API response: {notifications_response.status_code}")
    if notifications_response.status_code == 200:
        data = notifications_response.json()
        print(f"✅ Found {data['count']} notifications via API")
        print(f"   Unread count: {data.get('unread_count', 0)}")
        
        for notif in data['results']:
            print(f"   - {notif['title']}: {notif['message']} [{notif['notification_type']}]")
    else:
        print(f"❌ API failed: {notifications_response.text}")
    
    # Test 4: Test complete application flow with notifications
    print("\n4. Testing application flow with notifications...")
    
    # Find a camp
    camp_user = User.objects.filter(email='testcamp1770017280@test.com').first()
    if not camp_user:
        print("❌ Camp user not found!")
        return
    
    # Login as camp user
    camp_login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                      json={'email': camp_user.email, 'password': 'TestPass123!'},
                                      headers={'Content-Type': 'application/json'})
    
    if camp_login_response.status_code != 200:
        print("❌ Camp login failed")
        return
    
    camp_token = camp_login_response.json().get('tokens', {}).get('access')
    
    # Get applications
    apps_response = requests.get('http://localhost:8000/api/camp/applications/', 
                               headers={'Authorization': f'Bearer {camp_token}'})
    
    if apps_response.status_code == 200:
        apps_data = apps_response.json()
        if apps_data['results']:
            app = apps_data['results'][0]
            print(f"Found application: {app['id']} - {app['donor_name']}")
            
            # Review application (this should create notification)
            review_data = {
                'application_id': app['id'],
                'decision': 'APPROVED',
                'notes': 'Approved for notification testing'
            }
            
            review_response = requests.post('http://localhost:8000/api/camp/applications/review/',
                                          json=review_data,
                                          headers={'Authorization': f'Bearer {camp_token}',
                                                 'Content-Type': 'application/json'})
            
            if review_response.status_code == 200:
                print("✅ Application reviewed - notification should be created")
                
                # Check if notification was created
                new_notifications = Notification.objects.filter(recipient=donor_user).count()
                print(f"Donor now has {new_notifications} notifications")
                
                # Test API again
                final_notifications_response = requests.get('http://localhost:8000/api/notifications/', 
                                                          headers={'Authorization': f'Bearer {access_token}'})
                
                if final_notifications_response.status_code == 200:
                    final_data = final_notifications_response.json()
                    print(f"✅ Final API check: {final_data['count']} notifications")
                    print(f"   Unread count: {final_data.get('unread_count', 0)}")
                    
                    for notif in final_data['results']:
                        print(f"   - {notif['title']}: {notif['message']}")
            else:
                print(f"❌ Application review failed: {review_response.text}")
        else:
            print("No applications found to test")
    else:
        print(f"❌ Failed to get applications: {apps_response.text}")
    
    print("\n=== NOTIFICATION TEST COMPLETE ===")

if __name__ == '__main__':
    test_notification_system()