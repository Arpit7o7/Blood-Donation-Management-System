from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q, Sum
from django.conf import settings
from datetime import timedelta
from .models import BloodStock, HospitalPatientRequest, HospitalNetwork
from donor.models import DonorHospitalAlert, DonorHospitalAlertResponse
from accounts.models import HospitalProfile, DonorProfile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_dashboard(request):
    """Hospital dashboard endpoint"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        # Check verification status
        if hospital_profile.verification_status != 'APPROVED':
            return Response({
                'error': 'Hospital not verified',
                'status': hospital_profile.verification_status
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get dashboard stats
        active_requests = HospitalPatientRequest.objects.filter(
            hospital=hospital_profile,
            status__in=['PENDING', 'APPROVED']
        ).count()
        
        total_stock = BloodStock.objects.filter(
            hospital=hospital_profile
        ).aggregate(total=Sum('units_available'))['total'] or 0
        
        pending_applications = DonorHospitalAlertResponse.objects.filter(
            alert__hospital=hospital_profile,
            status='PENDING'
        ).count()
        
        return Response({
            'message': 'Hospital dashboard',
            'hospital': hospital_profile.hospital_name,
            'stats': {
                'active_requests': active_requests,
                'total_stock': total_stock,
                'pending_applications': pending_applications
            }
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blood_stock(request):
    """Get hospital blood stock"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        # Get or create stock for all blood groups
        stock_data = []
        for blood_group_code, blood_group_name in settings.BLOOD_GROUPS:
            stock, created = BloodStock.objects.get_or_create(
                hospital=hospital_profile,
                blood_group=blood_group_code,
                defaults={'units_available': 0}
            )
            
            stock_data.append({
                'blood_group': blood_group_code,
                'blood_group_name': blood_group_name,
                'units_available': stock.units_available,
                'units_reserved': stock.units_reserved,
                'status': stock.status,
                'last_updated': stock.last_updated
            })
        
        return Response({
            'results': stock_data,
            'total_units': sum(item['units_available'] for item in stock_data)
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_blood_stock(request):
    """Update blood stock levels"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        blood_group = request.data.get('blood_group')
        units = request.data.get('units')
        operation = request.data.get('operation', 'set')  # 'set', 'add', 'subtract'
        
        if not blood_group or units is None:
            return Response({'error': 'Blood group and units are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        stock, created = BloodStock.objects.get_or_create(
            hospital=hospital_profile,
            blood_group=blood_group,
            defaults={'units_available': 0}
        )
        
        if operation == 'set':
            stock.units_available = max(0, int(units))
        elif operation == 'add':
            stock.units_available += int(units)
        elif operation == 'subtract':
            stock.units_available = max(0, stock.units_available - int(units))
        
        stock.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'blood_group': blood_group,
            'units_available': stock.units_available,
            'status': stock.status
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_requests(request):
    """Get patient blood requests"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        requests = HospitalPatientRequest.objects.filter(
            hospital=hospital_profile
        ).select_related('patient__user')[:20]
        
        request_data = []
        for req in requests:
            request_data.append({
                'id': req.id,
                'patient_name': req.patient.user.get_full_name(),
                'patient_id': f"P{req.patient.id:06d}",
                'blood_group': req.blood_group,
                'units_needed': req.units_needed,
                'request_type': req.request_type,
                'emergency_reason': req.emergency_reason,
                'required_by': req.required_by,
                'doctor_name': req.doctor_name,
                'doctor_contact': req.doctor_contact,
                'status': req.status,
                'created_at': req.created_at
            })
        
        return Response({
            'results': request_data,
            'count': len(request_data)
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_emergency_alert(request):
    """Create emergency blood alert"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        alert = DonorHospitalAlert.objects.create(
            hospital=hospital_profile,
            blood_group=request.data.get('blood_group'),
            units_needed=request.data.get('units_needed'),
            urgency=request.data.get('urgency', 'LOW'),
            reason=request.data.get('reason'),
            location=request.data.get('location'),
            required_by=request.data.get('required_by'),
            created_by=request.user
        )
        
        # TODO: Trigger notification system based on urgency
        
        return Response({
            'message': 'Emergency alert created successfully',
            'alert_id': alert.id,
            'urgency': alert.urgency
        }, status=status.HTTP_201_CREATED)
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donor_applications(request):
    """Get donor applications to hospital alerts"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        applications = DonorHospitalAlertResponse.objects.filter(
            alert__hospital=hospital_profile
        ).select_related('donor__user', 'alert')[:20]
        
        application_data = []
        for app in applications:
            application_data.append({
                'id': app.id,
                'donor_name': app.donor.user.get_full_name(),
                'donor_blood_group': app.donor.blood_group,
                'donor_phone': app.donor.user.phone,
                'alert_blood_group': app.alert.blood_group,
                'age': app.age,
                'weight': app.weight,
                'last_donation_date': app.last_donation_date,
                'health_status': app.health_status,
                'health_issues': app.health_issues,
                'medications': app.medications,
                'available_date': app.available_date,
                'available_time': app.available_time,
                'status': app.status,
                'responded_at': app.responded_at
            })
        
        return Response({
            'results': application_data,
            'count': len(application_data)
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_donor_application(request):
    """Review donor application (approve/reject)"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        application_id = request.data.get('application_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        notes = request.data.get('notes', '')
        
        if not application_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid application ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        application = DonorHospitalAlertResponse.objects.get(
            id=application_id,
            alert__hospital=request.user.hospital_profile
        )
        
        application.status = decision
        application.reviewed_at = timezone.now()
        application.reviewed_by = request.user
        application.rejection_reason = notes if decision == 'REJECTED' else ''
        application.save()
        
        # TODO: Send notification to donor
        
        return Response({
            'message': f'Application {decision.lower()} successfully',
            'application_id': application.id,
            'status': application.status
        })
    except DonorHospitalAlertResponse.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hospital_network(request):
    """Get hospital network exchanges"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hospital_profile = request.user.hospital_profile
        
        # Get both sent and received requests
        sent_requests = HospitalNetwork.objects.filter(
            requesting_hospital=hospital_profile
        ).select_related('providing_hospital')[:10]
        
        received_requests = HospitalNetwork.objects.filter(
            providing_hospital=hospital_profile
        ).select_related('requesting_hospital')[:10]
        
        sent_data = []
        for req in sent_requests:
            sent_data.append({
                'id': req.id,
                'type': 'SENT',
                'hospital_name': req.providing_hospital.hospital_name,
                'blood_group': req.blood_group,
                'units_requested': req.units_requested,
                'units_approved': req.units_approved,
                'status': req.status,
                'urgency': req.urgency,
                'reason': req.reason,
                'required_by': req.required_by,
                'requested_at': req.requested_at,
                'responded_at': req.responded_at,
                'response_notes': req.response_notes
            })
        
        received_data = []
        for req in received_requests:
            received_data.append({
                'id': req.id,
                'type': 'RECEIVED',
                'hospital_name': req.requesting_hospital.hospital_name,
                'blood_group': req.blood_group,
                'units_requested': req.units_requested,
                'units_approved': req.units_approved,
                'status': req.status,
                'urgency': req.urgency,
                'reason': req.reason,
                'required_by': req.required_by,
                'requested_at': req.requested_at,
                'responded_at': req.responded_at,
                'response_notes': req.response_notes
            })
        
        return Response({
            'sent_requests': sent_data,
            'received_requests': received_data
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_hospitals(request):
    """Get list of hospitals available for blood exchange"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        current_hospital = request.user.hospital_profile
        
        # Get hospitals in the same city or nearby cities
        hospitals = HospitalProfile.objects.filter(
            verification_status='APPROVED',
            has_blood_bank=True
        ).exclude(id=current_hospital.id).select_related('user')
        
        hospital_data = []
        for hospital in hospitals:
            # Get their blood stock
            stock_data = BloodStock.objects.filter(hospital=hospital)
            total_stock = stock_data.aggregate(total=Sum('units_available'))['total'] or 0
            
            hospital_data.append({
                'id': hospital.id,
                'hospital_name': hospital.hospital_name,
                'city': hospital.city,
                'state': hospital.state,
                'contact_person': hospital.authorized_person_name,
                'contact_phone': hospital.authorized_person_mobile,
                'total_stock': total_stock,
                'blood_stock': [
                    {
                        'blood_group': stock.blood_group,
                        'units_available': stock.units_available,
                        'status': stock.status
                    } for stock in stock_data
                ]
            })
        
        return Response({
            'results': hospital_data,
            'count': len(hospital_data)
        })
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_network_request(request):
    """Create a blood exchange request to another hospital"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        requesting_hospital = request.user.hospital_profile
        providing_hospital_id = request.data.get('providing_hospital_id')
        
        if not providing_hospital_id:
            return Response({'error': 'Providing hospital ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        providing_hospital = HospitalProfile.objects.get(id=providing_hospital_id)
        
        network_request = HospitalNetwork.objects.create(
            requesting_hospital=requesting_hospital,
            providing_hospital=providing_hospital,
            blood_group=request.data.get('blood_group'),
            units_requested=request.data.get('units_requested'),
            reason=request.data.get('reason'),
            urgency=request.data.get('urgency', 'LOW'),
            required_by=request.data.get('required_by'),
            requested_by=request.user
        )
        
        # TODO: Send notification to providing hospital
        
        return Response({
            'message': 'Blood exchange request created successfully',
            'request_id': network_request.id,
            'providing_hospital': providing_hospital.hospital_name
        }, status=status.HTTP_201_CREATED)
        
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_network_request(request):
    """Respond to a blood exchange request (approve/reject)"""
    if request.user.role != 'HOSPITAL':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        request_id = request.data.get('request_id')
        decision = request.data.get('decision')  # 'APPROVED' or 'REJECTED'
        units_approved = request.data.get('units_approved', 0)
        response_notes = request.data.get('response_notes', '')
        
        if not request_id or decision not in ['APPROVED', 'REJECTED']:
            return Response({'error': 'Invalid request ID or decision'}, status=status.HTTP_400_BAD_REQUEST)
        
        network_request = HospitalNetwork.objects.get(
            id=request_id,
            providing_hospital=request.user.hospital_profile
        )
        
        network_request.status = decision
        network_request.units_approved = units_approved if decision == 'APPROVED' else 0
        network_request.response_notes = response_notes
        network_request.responded_at = timezone.now()
        network_request.responded_by = request.user
        network_request.save()
        
        # If approved, update blood stock
        if decision == 'APPROVED' and units_approved > 0:
            # Reduce stock from providing hospital
            providing_stock, _ = BloodStock.objects.get_or_create(
                hospital=network_request.providing_hospital,
                blood_group=network_request.blood_group,
                defaults={'units_available': 0}
            )
            providing_stock.units_available = max(0, providing_stock.units_available - units_approved)
            providing_stock.save()
            
            # Increase stock at requesting hospital
            requesting_stock, _ = BloodStock.objects.get_or_create(
                hospital=network_request.requesting_hospital,
                blood_group=network_request.blood_group,
                defaults={'units_available': 0}
            )
            requesting_stock.units_available += units_approved
            requesting_stock.save()
        
        # TODO: Send notification to requesting hospital
        
        return Response({
            'message': f'Request {decision.lower()} successfully',
            'request_id': network_request.id,
            'status': network_request.status,
            'units_approved': network_request.units_approved
        })
        
    except HospitalNetwork.DoesNotExist:
        return Response({'error': 'Network request not found'}, status=status.HTTP_404_NOT_FOUND)
    except HospitalProfile.DoesNotExist:
        return Response({'error': 'Hospital profile not found'}, status=status.HTTP_404_NOT_FOUND)