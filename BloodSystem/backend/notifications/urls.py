from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_notifications, name='get_notifications'),
    path('mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]