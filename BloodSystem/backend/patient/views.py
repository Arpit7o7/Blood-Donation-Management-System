from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import BloodRequest
from accounts.models import PatientProfile, HospitalProfile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_dashboard(request):
    """Patient dashboard endpoint"""
    if request.user.role != 'PATIENT':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        patient_profile = request.user.patient_profile
        
        # Get dashboard stats
        total_requests = BloodRequest.objects.filter(patient=patient_profile).count()
        active_requests = BloodRequest.objects.filter(
            patient=patient_profile,
            status__in=['PENDING', 'APPROVED']
        ).count()
        emergency_requests = BloodRequest.objects.filter(
            patient=patient_profile,
            request_type__in=['EMERGENCY', 'DISASTER']
        ).count()
        
        return Response({
            'message': 'Patient dashboard',
            'patient': patient_profile.user.get_full_name(),
            'stats': {
                'total_requests': total_requests,
                'active_requests': active_requests,
                'emergency_requests': emergency_requests
            }
        })
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blood_requests(request):
    """Get patient's blood requests"""
    if request.user.role != 'PATIENT':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        patient_profile = request.user.patient_profile
        
        requests = BloodRequest.objects.filter(
            patient=patient_profile
        ).select_related('hospital')
        
        request_data = []
        for req in requests:
            request_data.append({
                'id': req.id,
                'hospital_name': req.hospital.hospital_name,
                'blood_group': req.blood_group,
                'units_needed': req.units_needed,
                'request_type': req.request_type,
                'emergency_reason': req.emergency_reason,
                'required_by': req.required_by,
                'status': req.status,
                'created_at': req.created_at,
                'admin_approved': req.admin_approved,
                'requires_admin_approval': req.requires_admin_approval
            })
        
        return Response({
            'results': request_data,
            'count': len(request_data)
        })
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blood_request(request):
    """Create a new blood request"""
    if request.user.role != 'PATIENT':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        patient_profile = request.user.patient_profile
        hospital_id = request.data.get('hospital_id')
        
        if not hospital_id:
            return Response({'error': 'Hospital ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            hospital = HospitalProfile.objects.get(id=hospital_id, verification_status='APPROVED')
        except HospitalProfile.DoesNotExist:
            return Response({'error': 'Hospital not found or not verified'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate emergency request
        request_type = request.data.get('request_type', 'NORMAL')
        if request_type in ['EMERGENCY', 'DISASTER']:
            emergency_justification = request.data.get('emergency_justification', '').strip()
            if len(emergency_justification) < 50:
                return Response({
                    'error': 'Emergency requests require detailed justification (minimum 50 characters)'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request = BloodRequest.objects.create(
            patient=patient_profile,
            hospital=hospital,
            blood_group=request.data.get('blood_group'),
            units_needed=request.data.get('units_needed'),
            request_type=request_type,
            emergency_reason=request.data.get('emergency_reason', ''),
            emergency_justification=request.data.get('emergency_justification', ''),
            required_by=request.data.get('required_by'),
            doctor_name=request.data.get('doctor_name', ''),
            doctor_contact=request.data.get('doctor_contact', ''),
            medical_condition=request.data.get('medical_condition', '')
        )
        
        # For emergency requests, mark as pending admin approval
        response_message = 'Blood request submitted successfully'
        if blood_request.requires_admin_approval:
            response_message += '. Emergency requests require admin approval before processing.'
        
        return Response({
            'message': response_message,
            'request_id': blood_request.id,
            'status': blood_request.status,
            'requires_admin_approval': blood_request.requires_admin_approval
        }, status=status.HTTP_201_CREATED)
        
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_hospitals(request):
    """Get nearby hospitals for blood requests"""
    if request.user.role != 'PATIENT':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        patient_profile = request.user.patient_profile
        
        # Get verified hospitals in the same city/state
        hospitals = HospitalProfile.objects.filter(
            verification_status='APPROVED',
            city__iexact=patient_profile.city
        )
        
        hospital_data = []
        for hospital in hospitals:
            hospital_data.append({
                'id': hospital.id,
                'hospital_name': hospital.hospital_name,
                'address_line': hospital.address_line,
                'area': hospital.area,
                'city': hospital.city,
                'phone': hospital.user.phone,
                'has_blood_bank': hospital.has_blood_bank,
                'emergency_contact': hospital.authorized_person_mobile
            })
        
        return Response({
            'results': hospital_data,
            'count': len(hospital_data)
        })
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_blood_request(request):
    """Cancel a blood request"""
    if request.user.role != 'PATIENT':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        patient_profile = request.user.patient_profile
        request_id = request.data.get('request_id')
        
        if not request_id:
            return Response({'error': 'Request ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request = BloodRequest.objects.get(
            id=request_id,
            patient=patient_profile,
            status__in=['PENDING', 'APPROVED']
        )
        
        blood_request.status = 'CANCELLED'
        blood_request.updated_at = timezone.now()
        blood_request.save()
        
        return Response({
            'message': 'Blood request cancelled successfully',
            'request_id': blood_request.id,
            'status': blood_request.status
        })
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found or cannot be cancelled'}, status=status.HTTP_404_NOT_FOUND)
    except PatientProfile.DoesNotExist:
        return Response({'error': 'Patient profile not found'}, status=status.HTTP_404_NOT_FOUND)