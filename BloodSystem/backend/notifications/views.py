from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get user notifications"""
    # Get all notifications for unread count
    all_notifications = Notification.objects.filter(recipient=request.user)
    
    # Get recent notifications for display
    notifications = all_notifications.order_by('-created_at')[:20]
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at
        })
    
    return Response({
        'results': notification_data,
        'count': len(notification_data),
        'unread_count': all_notifications.filter(is_read=False).count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request):
    """Mark notification as read"""
    notification_id = request.data.get('notification_id')
    
    if not notification_id:
        return Response({'error': 'Notification ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marked as read',
            'notification_id': notification.id
        })
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read"""
    updated_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return Response({
        'message': f'{updated_count} notifications marked as read',
        'updated_count': updated_count
    })


def create_notification(recipient, title, message, notification_type):
    """Helper function to create notifications"""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type
    )


def create_bulk_notifications(recipients, title, message, notification_type):
    """Helper function to create bulk notifications"""
    notifications = []
    for recipient in recipients:
        notifications.append(Notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type
        ))
    
    return Notification.objects.bulk_create(notifications)