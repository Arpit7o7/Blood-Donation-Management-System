from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q, Count, Sum
from accounts.models import HospitalProfile, CampProfile, User, DonorProfile
from patient.models import BloodRequest
from hospital.models import BloodStock
from donor.models import DonationHistory
from notifications.models import Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """Admin dashboard endpoint"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get dashboard stats
    pending_hospitals = HospitalProfile.objects.filter(verification_status='PENDING').count()
    pending_camps = CampProfile.objects.filter(verification_status='PENDING').count()
    pending_verifications = pending_hospitals + pending_camps
    
    emergency_requests = BloodRequest.objects.filter(
        request_type__in=['EMERGENCY', 'DISASTER'],
        admin_approved=False
    ).count()
    
    total_users = User.objects.count()
    total_donations = DonationHistory.objects.count() if 'donor.models' in globals() else 0
    
    # User distribution
    user_distribution = User.objects.values('role').annotate(count=Count('id'))
    user_counts = {stat['role'].lower() + 's': stat['count'] for stat in user_distribution}
    
    return Response({
        'message': 'Admin dashboard',
        'admin': request.user.get_full_name(),
        'stats': {
            'total_users': total_users,
            'pending_verifications': pending_verifications,
            'emergency_requests': emergency_requests,
            'total_donations': total_donations
        },
        'user_distribution': user_counts
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_verifications(request):
    """Get pending hospital and camp verifications"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    results = []
    
    # Get pending hospitals
    pending_hospitals = HospitalProfile.objects.filter(
        verification_status='PENDING'
    ).select_related('user')
    
    for hospital in pending_hospitals:
        results.append({
            'id': hospital.id,
            'type': 'HOSPITAL',
            'name': hospital.hospital_name,
            'contact_person': hospital.authorized_person_name,
            'contact_email': hospital.user.email,
            'contact_phone': hospital.user.phone,
            'registration_number': hospital.registration_number,
            'city': hospital.city,
            'state': hospital.state,
            'has_blood_bank': hospital.has_blood_bank,
            'created_at': hospital.created_at
        })
    
    # Get pending camps
    pending_camps = CampProfile.objects.filter(
        verification_status='PENDING'
    ).select_related('user')
    
    for camp in pending_camps:
        results.append({
            'id': camp.id,
            'type': 'CAMP',
            'name': camp.organization_name,
            'organization_type': camp.organization_type,
            'contact_person': camp.contact_person_name,
            'contact_email': camp.user.email,
            'contact_phone': camp.user.phone,
            'registration_number': camp.registration_number,
            'city': camp.city,
            'state': camp.state,
            'created_at': camp.created_at
        })
    
    return Response({
        'results': results,
        'count': len(results)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_hospital(request):
    """Verify or reject hospital registration"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        organization_id = request.data.get('organization_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not organization_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid organization ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        hospital = HospitalProfile.objects.get(id=organization_id)
        hospital.verification_status = decision
        hospital.verified_by = request.user
        hospital.verification_date = timezone.now()
        hospital.rejection_reason = notes if decision == 'REJECTED' else ''
        hospital.save()
        
        # TODO: Send notification to hospital
        
        return Response({
            'message': f'Hospital {decision.lower()} successfully',
            'hospital_id': hospital.id,
            'status': hospital.verification_status
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_camp(request):
    """Verify or reject camp registration"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        organization_id = request.data.get('organization_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not organization_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid organization ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        camp = CampProfile.objects.get(id=organization_id)
        camp.verification_status = decision
        camp.verified_by = request.user
        camp.verification_date = timezone.now()
        camp.rejection_reason = notes if decision == 'REJECTED' else ''
        camp.save()
        
        # TODO: Send notification to camp
        
        return Response({
            'message': f'Camp {decision.lower()} successfully',
            'camp_id': camp.id,
            'status': camp.verification_status
        })
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def emergency_requests(request):
    """Get emergency blood requests requiring approval"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    emergency_requests = BloodRequest.objects.filter(
        request_type__in=['EMERGENCY', 'DISASTER'],
        admin_approved=False
    ).select_related('patient__user', 'hospital__hospital_profile')
    
    request_data = []
    for req in emergency_requests:
        request_data.append({
            'id': req.id,
            'patient_name': req.patient.user.get_full_name(),
            'patient_phone': req.patient.user.phone,
            'hospital_name': req.hospital.hospital_profile.hospital_name,
            'hospital_location': f"{req.hospital.hospital_profile.city}, {req.hospital.hospital_profile.state}",
            'hospital_contact': req.hospital.user.phone,
            'blood_group': req.blood_group,
            'units_needed': req.units_needed,
            'urgency': req.request_type,
            'emergency_reason': req.emergency_reason,
            'emergency_justification': req.emergency_justification,
            'required_by': req.required_by,
            'doctor_name': req.doctor_name,
            'doctor_contact': req.doctor_contact,
            'medical_condition': req.medical_condition,
            'status': req.status,
            'created_at': req.created_at
        })
    
    return Response({
        'results': request_data,
        'count': len(request_data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_emergency_request(request):
    """Approve or reject emergency blood request"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        request_id = request.data.get('request_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not request_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid request ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request = BloodRequest.objects.get(id=request_id)
        
        if decision == 'APPROVED':
            blood_request.admin_approved = True
            blood_request.admin_approved_by = request.user
            blood_request.admin_approved_at = timezone.now()
            blood_request.admin_notes = notes
            # TODO: Trigger emergency alert broadcasting
        else:
            blood_request.status = 'REJECTED'
            blood_request.rejection_reason = notes
            blood_request.reviewed_by = request.user
            blood_request.reviewed_at = timezone.now()
        
        blood_request.save()
        
        # TODO: Send notification to patient and hospital
        
        return Response({
            'message': f'Emergency request {decision.lower()} successfully',
            'request_id': blood_request.id,
            'admin_approved': blood_request.admin_approved
        })
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_stats(request):
    """Get comprehensive system statistics"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # User statistics
    user_stats = User.objects.values('role').annotate(count=Count('id'))
    user_counts = {stat['role']: stat['count'] for stat in user_stats}
    
    # Verification statistics
    hospital_stats = HospitalProfile.objects.values('verification_status').annotate(count=Count('id'))
    hospital_counts = {stat['verification_status']: stat['count'] for stat in hospital_stats}
    
    camp_stats = CampProfile.objects.values('verification_status').annotate(count=Count('id'))
    camp_counts = {stat['verification_status']: stat['count'] for stat in camp_stats}
    
    # Blood request statistics
    request_stats = BloodRequest.objects.values('status').annotate(count=Count('id'))
    request_counts = {stat['status']: stat['count'] for stat in request_stats}
    
    return Response({
        'users': user_counts,
        'hospitals': hospital_counts,
        'camps': camp_counts,
        'blood_requests': request_counts,
        'total_users': sum(user_counts.values()),
        'total_hospitals': sum(hospital_counts.values()),
        'total_camps': sum(camp_counts.values()),
        'total_requests': sum(request_counts.values())
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_details(request, hospital_id):
    """Get detailed hospital information for verification"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital = HospitalProfile.objects.select_related('user').get(id=hospital_id)
        
        return Response({
            'id': hospital.id,
            'hospital_name': hospital.hospital_name,
            'registration_number': hospital.registration_number,
            'issuing_authority': hospital.issuing_authority,
            'year_of_registration': hospital.year_of_registration,
            'address_line': hospital.address_line,
            'area': hospital.area,
            'city': hospital.city,
            'district': hospital.district,
            'state': hospital.state,
            'pincode': hospital.pincode,
            'authorized_person_name': hospital.authorized_person_name,
            'authorized_person_designation': hospital.authorized_person_designation,
            'authorized_person_mobile': hospital.authorized_person_mobile,
            'authorized_person_email': hospital.authorized_person_email,
            'has_blood_bank': hospital.has_blood_bank,
            'blood_bank_license': hospital.blood_bank_license,
            'storage_capacity': hospital.storage_capacity,
            'verification_status': hospital.verification_status,
            'created_at': hospital.created_at,
            'user': {
                'email': hospital.user.email,
                'phone': hospital.user.phone,
                'first_name': hospital.user.first_name,
                'last_name': hospital.user.last_name
            }
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def camp_details(request, camp_id):
    """Get detailed camp information for verification"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        camp = CampProfile.objects.select_related('user').get(id=camp_id)
        
        return Response({
            'id': camp.id,
            'organization_name': camp.organization_name,
            'organization_type': camp.organization_type,
            'registration_number': camp.registration_number,
            'contact_person_name': camp.contact_person_name,
            'contact_person_designation': camp.contact_person_designation,
            'contact_person_mobile': camp.contact_person_mobile,
            'address_line': camp.address_line,
            'city': camp.city,
            'state': camp.state,
            'pincode': camp.pincode,
            'verification_status': camp.verification_status,
            'created_at': camp.created_at,
            'user': {
                'email': camp.user.email,
                'phone': camp.user.phone,
                'first_name': camp.user.first_name,
                'last_name': camp.user.last_name
            }
        })
    except CampProfile.DoesNotExist:
        return Response({'error': 'Camp not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def emergency_details(request, emergency_id):
    """Get detailed emergency request information"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        emergency = BloodRequest.objects.select_related(
            'patient__user', 'hospital__hospital_profile'
        ).get(id=emergency_id)
        
        return Response({
            'id': emergency.id,
            'patient_name': emergency.patient.user.get_full_name(),
            'patient_phone': emergency.patient.user.phone,
            'hospital_name': emergency.hospital.hospital_profile.hospital_name,
            'hospital_location': f"{emergency.hospital.hospital_profile.city}, {emergency.hospital.hospital_profile.state}",
            'hospital_contact': emergency.hospital.user.phone,
            'blood_group': emergency.blood_group,
            'units_needed': emergency.units_needed,
            'urgency': emergency.request_type,
            'emergency_reason': emergency.emergency_reason,
            'emergency_justification': emergency.emergency_justification,
            'required_by': emergency.required_by,
            'doctor_name': emergency.doctor_name,
            'doctor_contact': emergency.doctor_contact,
            'medical_condition': emergency.medical_condition,
            'status': emergency.status,
            'created_at': emergency.created_at,
            'admin_approved': emergency.admin_approved
        })
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Emergency request not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_emergency(request):
    """Review emergency request (approve/reject)"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        request_id = request.data.get('request_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not request_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid request ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request = BloodRequest.objects.get(id=request_id)
        
        if decision == 'APPROVED':
            blood_request.admin_approved = True
            blood_request.admin_approved_by = request.user
            blood_request.admin_approved_at = timezone.now()
            blood_request.admin_notes = notes
            # TODO: Trigger emergency alert broadcasting
        else:
            blood_request.status = 'REJECTED'
            blood_request.rejection_reason = notes
            blood_request.reviewed_by = request.user
            blood_request.reviewed_at = timezone.now()
        
        blood_request.save()
        
        # TODO: Send notification to patient and hospital
        
        return Response({
            'message': f'Emergency request {decision.lower()} successfully',
            'request_id': blood_request.id,
            'admin_approved': blood_request.admin_approved
        })
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blood_stock_overview(request):
    """Get system-wide blood stock overview"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get blood stock summary across all hospitals
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        stock_summary = {}
        
        for group in blood_groups:
            total_stock = BloodStock.objects.filter(blood_group=group).aggregate(
                total=Sum('units_available')
            )['total'] or 0
            stock_summary[group] = total_stock
        
        return Response({
            'stock_summary': stock_summary,
            'total_units': sum(stock_summary.values())
        })
    except Exception as e:
        return Response({
            'stock_summary': {group: 0 for group in blood_groups},
            'total_units': 0
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """Get recent system activity"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    activities = []
    
    # Recent user registrations
    recent_users = User.objects.order_by('-created_at')[:5]
    for user in recent_users:
        activities.append({
            'type': 'user_registration',
            'description': f'New {user.role.lower()} registered: {user.get_full_name()}',
            'timestamp': user.created_at
        })
    
    # Recent verifications
    recent_hospitals = HospitalProfile.objects.filter(
        verification_status='APPROVED'
    ).order_by('-verification_date')[:3]
    for hospital in recent_hospitals:
        activities.append({
            'type': 'organization_verification',
            'description': f'Hospital verified: {hospital.hospital_name}',
            'timestamp': hospital.verification_date
        })
    
    # Recent emergency requests
    recent_emergencies = BloodRequest.objects.filter(
        request_type__in=['EMERGENCY', 'DISASTER']
    ).order_by('-created_at')[:3]
    for emergency in recent_emergencies:
        activities.append({
            'type': 'emergency_request',
            'description': f'Emergency request for {emergency.blood_group} blood',
            'timestamp': emergency.created_at
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response({
        'activities': activities[:10],
        'count': len(activities)
    })