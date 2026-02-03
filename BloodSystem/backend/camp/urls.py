from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.camp_dashboard, name='camp_dashboard'),
    
    # Camps Management
    path('camps/', views.camps_list, name='camps_list'),
    path('camps/create/', views.create_camp, name='create_camp'),
    
    # Applications
    path('applications/', views.camp_applications, name='camp_applications'),
    path('applications/review/', views.review_application, name='review_application'),
    
    # Attendance
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
]