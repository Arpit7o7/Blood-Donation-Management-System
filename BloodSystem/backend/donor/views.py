from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import DonationHistory, CampApplication, DonorHospitalAlert, DonorHospitalAlertResponse
from camp.models import Camp
from accounts.models import DonorProfile
from notifications.views import create_notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donor_dashboard(request):
    """Donor dashboard endpoint"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        
        # Get donor stats
        total_donations = DonationHistory.objects.filter(donor=donor_profile).count()
        last_donation = DonationHistory.objects.filter(donor=donor_profile).first()
        
        # Calculate next eligible date
        next_eligible_date = None
        if last_donation:
            next_eligible_date = last_donation.donation_date.date() + timedelta(days=56)
        
        return Response({
            'message': 'Donor dashboard',
            'user': request.user.get_full_name(),
            'stats': {
                'total_donations': total_donations,
                'last_donation_date': last_donation.donation_date.date() if last_donation else None,
                'next_eligible_date': next_eligible_date
            }
        })
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donor_stats(request):
    """Get donor statistics"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        
        # Get donation history
        donations = DonationHistory.objects.filter(donor=donor_profile)
        total_donations = donations.count()
        last_donation = donations.first()
        
        # Calculate next eligible date
        next_eligible_date = None
        if last_donation:
            next_eligible_date = last_donation.donation_date.date() + timedelta(days=56)
        
        return Response({
            'total_donations': total_donations,
            'last_donation_date': last_donation.donation_date.date() if last_donation else None,
            'next_eligible_date': next_eligible_date,
            'is_eligible': next_eligible_date is None or next_eligible_date <= timezone.now().date()
        })
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camp_suggestions(request):
    """Get nearby camp suggestions for donor"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        
        # Get active camps in donor's city
        camps = Camp.objects.filter(
            status='ACTIVE',
            is_active=True,
            city__iexact=donor_profile.city,
            date__gte=timezone.now().date()
        ).exclude(
            # Exclude camps where donor already applied
            applications__donor=donor_profile
        )[:10]
        
        camp_data = []
        for camp in camps:
            camp_data.append({
                'id': camp.id,
                'name': camp.name,
                'organizer': camp.organizer.organization_name,
                'location': camp.location,
                'address': camp.address,
                'date': camp.date,
                'start_time': camp.start_time,
                'end_time': camp.end_time,
                'blood_groups_needed': camp.blood_groups_needed,
                'expected_donors': camp.expected_donors,
                'applications_count': camp.applications_count,
                'contact_person': camp.contact_person,
                'contact_phone': camp.contact_phone
            })
        
        return Response({
            'results': camp_data,
            'count': len(camp_data)
        })
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_camp(request):
    """Apply to a blood camp"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        camp_id = request.data.get('camp_id')
        
        if not camp_id:
            return Response({'error': 'Camp ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            camp = Camp.objects.get(id=camp_id, status='ACTIVE', is_active=True)
        except Camp.DoesNotExist:
            return Response({'error': 'Camp not found or not active'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already applied
        if CampApplication.objects.filter(donor=donor_profile, camp=camp).exists():
            return Response({'error': 'Already applied to this camp'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create application
        application = CampApplication.objects.create(
            donor=donor_profile,
            camp=camp,
            age=request.data.get('age'),
            weight=request.data.get('weight'),
            last_donation_date=request.data.get('last_donation_date'),
            health_status=request.data.get('health_status', 'GOOD'),
            health_issues=request.data.get('health_issues', ''),
            medications=request.data.get('medications', ''),
            consent_given=request.data.get('consent', False)
        )
        
        # Create notification for donor
        create_notification(
            recipient=donor_profile.user,
            title='Camp Application Submitted',
            message=f'Your application for "{camp.name}" has been submitted successfully. You will be notified once it is reviewed.',
            notification_type='CAMP_APPROVAL'  # Using existing type, could add new type
        )
        
        return Response({
            'message': 'Application submitted successfully',
            'application_id': application.id,
            'status': application.status
        }, status=status.HTTP_201_CREATED)
        
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_alerts(request):
    """Get hospital blood alerts for donor"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        
        # Get active alerts matching donor's blood group and location
        alerts = DonorHospitalAlert.objects.filter(
            status='ACTIVE',
            required_by__gte=timezone.now(),
            hospital__city__iexact=donor_profile.city
        ).filter(
            Q(blood_group=donor_profile.blood_group) |
            Q(blood_group='O-')  # O- can donate to anyone
        ).exclude(
            # Exclude alerts where donor already responded
            donor_responses__donor=donor_profile
        )[:10]
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'hospital_name': alert.hospital.hospital_name,
                'blood_group': alert.blood_group,
                'units_needed': alert.units_needed,
                'urgency': alert.urgency,
                'reason': alert.reason,
                'location': alert.location,
                'required_by': alert.required_by,
                'created_at': alert.created_at
            })
        
        return Response({
            'results': alert_data,
            'count': len(alert_data)
        })
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_alert(request):
    """Respond to a hospital alert"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        alert_id = request.data.get('alert_id')
        
        if not alert_id:
            return Response({'error': 'Alert ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            alert = DonorHospitalAlert.objects.get(id=alert_id, status='ACTIVE')
        except DonorHospitalAlert.DoesNotExist:
            return Response({'error': 'Alert not found or not active'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already responded
        if DonorHospitalAlertResponse.objects.filter(donor=donor_profile, alert=alert).exists():
            return Response({'error': 'Already responded to this alert'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create response
        response = DonorHospitalAlertResponse.objects.create(
            alert=alert,
            donor=donor_profile,
            age=request.data.get('age'),
            weight=request.data.get('weight'),
            last_donation_date=request.data.get('last_donation_date'),
            health_status=request.data.get('health_status', 'GOOD'),
            health_issues=request.data.get('health_issues', ''),
            medications=request.data.get('medications', ''),
            available_date=request.data.get('available_date'),
            available_time=request.data.get('available_time'),
            consent_given=request.data.get('consent', False)
        )
        
        return Response({
            'message': 'Response submitted successfully',
            'response_id': response.id,
            'status': response.status
        }, status=status.HTTP_201_CREATED)
        
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donation_history(request):
    """Get donor's donation history"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        
        donations = DonationHistory.objects.filter(donor=donor_profile)
        
        donation_data = []
        for donation in donations:
            donation_data.append({
                'id': donation.id,
                'donation_date': donation.donation_date,
                'location': donation.location,
                'units_donated': donation.units_donated,
                'blood_group': donation.blood_group,
                'hemoglobin_level': donation.hemoglobin_level,
                'notes': donation.notes
            })
        
        return Response({
            'results': donation_data,
            'count': len(donation_data)
        })
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_donor_profile(request):
    """Update donor profile"""
    if request.user.role != 'DONOR':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        donor_profile = request.user.donor_profile
        user = request.user
        
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone']
        for field in user_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        # Update donor profile fields
        profile_fields = ['blood_group', 'city', 'state', 'weight', 'gender']
        for field in profile_fields:
            if field in request.data:
                setattr(donor_profile, field, request.data[field])
        
        # Save changes
        user.save()
        donor_profile.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone
            },
            'profile': {
                'blood_group': donor_profile.blood_group,
                'city': donor_profile.city,
                'state': donor_profile.state,
                'weight': donor_profile.weight,
                'gender': donor_profile.gender
            }
        })
        
    except DonorProfile.DoesNotExist:
        return Response({'error': 'Donor profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)