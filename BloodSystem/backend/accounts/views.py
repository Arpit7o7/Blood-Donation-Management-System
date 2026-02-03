from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, DonorProfile, HospitalProfile, CampProfile, PatientProfile
from .serializers import (
    DonorRegistrationSerializer, HospitalRegistrationSerializer,
    CampRegistrationSerializer, PatientRegistrationSerializer,
    LoginSerializer, UserProfileSerializer, DonorProfileSerializer,
    HospitalProfileSerializer, CampProfileSerializer, PatientProfileSerializer
)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def donor_registration(request):
    """Donor registration endpoint"""
    serializer = DonorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        donor_profile = serializer.save()
        user = donor_profile.user
        tokens = get_tokens_for_user(user)
        
        return Response({
            'message': 'Donor registered successfully',
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def hospital_registration(request):
    """Hospital registration endpoint"""
    print("Hospital registration request received")
    print("Request data:", request.data)
    
    serializer = HospitalRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        hospital_profile = serializer.save()
        user = hospital_profile.user
        
        return Response({
            'message': 'Hospital registered successfully. Awaiting admin verification.',
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'status': 'PENDING_VERIFICATION'
        }, status=status.HTTP_201_CREATED)
    
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def camp_registration(request):
    """Camp registration endpoint"""
    serializer = CampRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        camp_profile = serializer.save()
        user = camp_profile.user
        
        return Response({
            'message': 'Camp registered successfully. Awaiting admin verification.',
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'status': 'PENDING_VERIFICATION'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_registration(request):
    """Patient registration endpoint"""
    print("Patient registration request received")
    print("Request data:", request.data)
    
    serializer = PatientRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        patient_profile = serializer.save()
        user = patient_profile.user
        tokens = get_tokens_for_user(user)
        
        return Response({
            'message': 'Patient registered successfully',
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint for all user types"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if hospital/camp is verified
        if user.role in ['HOSPITAL', 'CAMP']:
            profile = None
            if user.role == 'HOSPITAL':
                profile = getattr(user, 'hospital_profile', None)
            elif user.role == 'CAMP':
                profile = getattr(user, 'camp_profile', None)
            
            if profile and profile.verification_status != 'APPROVED':
                return Response({
                    'error': 'Account pending verification',
                    'status': profile.verification_status
                }, status=status.HTTP_403_FORBIDDEN)
        
        tokens = get_tokens_for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout endpoint"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get user profile based on role"""
    user = request.user
    
    if user.role == 'DONOR':
        profile = getattr(user, 'donor_profile', None)
        if profile:
            serializer = DonorProfileSerializer(profile)
        else:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.role == 'HOSPITAL':
        profile = getattr(user, 'hospital_profile', None)
        if profile:
            serializer = HospitalProfileSerializer(profile)
        else:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.role == 'CAMP':
        profile = getattr(user, 'camp_profile', None)
        if profile:
            serializer = CampProfileSerializer(profile)
        else:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.role == 'PATIENT':
        profile = getattr(user, 'patient_profile', None)
        if profile:
            serializer = PatientProfileSerializer(profile)
        else:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        serializer = UserProfileSerializer(user)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    role = user.role.lower()
    
    dashboard_urls = {
        'donor': '/donor/dashboard/',
        'hospital': '/hospital/dashboard/',
        'camp': '/camp/dashboard/',
        'patient': '/patient/dashboard/',
        'admin': '/admin/dashboard/'
    }
    
    return Response({
        'redirect_url': dashboard_urls.get(role, '/'),
        'role': user.role,
        'user': {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email
        }
    }, status=status.HTTP_200_OK)