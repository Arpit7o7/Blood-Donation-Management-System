from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Camp, CampRequirement, CampAttendance
from donor.models import CampApplication
from accounts.models import CampProfile
from notifications.views import create_notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camp_dashboard(request):
    """Camp dashboard endpoint"""
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp_profile = request.user.camp_profile
        
        # Check verification status
        if camp_profile.verification_status != 'APPROVED':
            return Response({
                'error': 'Camp organization not verified',
                'status': camp_profile.verification_status
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get dashboard stats
        total_camps = Camp.objects.filter(organizer=camp_profile).count()
        active_camps = Camp.objects.filter(
            organizer=camp_profile,
            status='ACTIVE',
            date__gte=timezone.now().date()
        ).count()
        pending_applications = CampApplication.objects.filter(
            camp__organizer=camp_profile,
            status='PENDING'
        ).count()
        
        return Response({
            'message': 'Camp dashboard',
            'organization': camp_profile.organization_name,
            'stats': {
                'total_camps': total_camps,
                'active_camps': active_camps,
                'pending_applications': pending_applications
            }
        })
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camps_list(request):
    """Get camps organized by this organization"""
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp_profile = request.user.camp_profile
        
        camps = Camp.objects.filter(
            organizer=camp_profile
        ).order_by('-date')
        
        camp_data = []
        for camp in camps:
            camp_data.append({
                'id': camp.id,
                'name': camp.name,
                'description': camp.description,
                'location': camp.location,
                'address': camp.address,
                'city': camp.city,
                'date': camp.date,
                'start_time': camp.start_time,
                'end_time': camp.end_time,
                'status': camp.status,
                'expected_donors': camp.expected_donors,
                'applications_count': camp.applications_count,
                'approved_applications_count': camp.approved_applications_count,
                'blood_groups_needed': camp.blood_groups_needed,
                'contact_person': camp.contact_person,
                'contact_phone': camp.contact_phone,
                'created_at': camp.created_at
            })
        
        return Response({
            'results': camp_data,
            'count': len(camp_data)
        })
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_camp(request):
    """Create a new blood camp"""
    print("Camp creation request received")
    print("Request data:", request.data)
    print("User:", request.user.email, "Role:", request.user.role)
    
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp_profile = request.user.camp_profile
        print("Camp profile found:", camp_profile.organization_name)
        
        camp = Camp.objects.create(
            organizer=camp_profile,
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            location=request.data.get('location'),
            address=request.data.get('address'),
            city=request.data.get('city'),
            state=request.data.get('state'),
            pincode=request.data.get('pincode'),
            date=request.data.get('date'),
            start_time=request.data.get('start_time'),
            end_time=request.data.get('end_time'),
            blood_groups_needed=request.data.get('blood_groups_needed', []),
            expected_donors=request.data.get('expected_donors', 50),
            contact_person=request.data.get('contact_person'),
            contact_phone=request.data.get('contact_phone'),
            contact_email=request.data.get('contact_email'),
            status='ACTIVE'
        )
        
        print("Camp created successfully:", camp.id)
        
        return Response({
            'message': 'Camp created successfully',
            'camp_id': camp.id,
            'status': camp.status
        }, status=status.HTTP_201_CREATED)
        
    except CampProfile.DoesNotExist:
        print("Camp profile not found for user:", request.user.email)
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error creating camp:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camp_applications(request):
    """Get applications for camps"""
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp_profile = request.user.camp_profile
        camp_id = request.GET.get('camp_id')
        
        applications_query = CampApplication.objects.filter(
            camp__organizer=camp_profile
        ).select_related('donor__user', 'camp')
        
        if camp_id:
            applications_query = applications_query.filter(camp_id=camp_id)
        
        applications = applications_query[:50]
        
        application_data = []
        for app in applications:
            application_data.append({
                'id': app.id,
                'donor_name': app.donor.user.get_full_name(),
                'donor_phone': app.donor.user.phone,
                'donor_blood_group': app.donor.blood_group,
                'camp_name': app.camp.name,
                'camp_date': app.camp.date,
                'age': app.age,
                'weight': app.weight,
                'last_donation_date': app.last_donation_date,
                'health_status': app.health_status,
                'health_issues': app.health_issues,
                'medications': app.medications,
                'status': app.status,
                'applied_at': app.applied_at,
                'reviewed_at': app.reviewed_at,
                'rejection_reason': app.rejection_reason
            })
        
        return Response({
            'results': application_data,
            'count': len(application_data)
        })
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_application(request):
    """Review camp application (approve/reject)"""
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        application_id = request.data.get('application_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not application_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid application ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        application = CampApplication.objects.get(
            id=application_id,
            camp__organizer=request.user.camp_profile
        )
        
        application.status = decision
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.rejection_reason = notes if decision == 'REJECTED' else ''
        application.save()
        
        # Create notification for donor
        if decision == 'APPROVED':
            create_notification(
                recipient=application.donor.user,
                title='Camp Application Approved',
                message=f'Your application for "{application.camp.name}" has been approved! Please check your email for further details.',
                notification_type='CAMP_APPROVAL'
            )
        else:
            create_notification(
                recipient=application.donor.user,
                title='Camp Application Rejected',
                message=f'Your application for "{application.camp.name}" has been rejected. {notes if notes else "Please try applying to other camps."}',
                notification_type='CAMP_REJECTION'
            )
        
        return Response({
            'message': f'Application {decision.lower()} successfully',
            'application_id': application.id,
            'status': application.status
        })
    except CampApplication.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """Mark donor attendance at camp"""
    if request.user.role != 'CAMP':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp_id = request.data.get('camp_id')
        donor_id = request.data.get('donor_id')
        attendance_status = request.data.get('status', 'CHECKED_IN')
        
        camp = Camp.objects.get(id=camp_id, organizer=request.user.camp_profile)
        
        # Get or create attendance record
        attendance, created = CampAttendance.objects.get_or_create(
            camp=camp,
            donor_id=donor_id,
            defaults={
                'status': attendance_status,
                'checked_in_by': request.user
            }
        )
        
        if not created:
            attendance.status = attendance_status
            if attendance_status == 'CHECKED_IN':
                attendance.check_in_time = timezone.now()
                attendance.checked_in_by = request.user
            elif attendance_status == 'DONATED':
                attendance.donation_time = timezone.now()
                attendance.donation_recorded_by = request.user
                attendance.units_donated = request.data.get('units_donated', 1)
            
            attendance.save()
        
        return Response({
            'message': 'Attendance marked successfully',
            'attendance_id': attendance.id,
            'status': attendance.status
        })
    except Camp.DoesNotExist:
        return Response({'error': 'Camp not found'}, status=status.HTTP_404_NOT_FOUND)
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp profile not found'}, status=status.HTTP_404_NOT_FOUND)