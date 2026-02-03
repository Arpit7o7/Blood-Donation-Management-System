from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, DonorProfile, HospitalProfile, CampProfile, PatientProfile, AdminProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Base user registration serializer"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # Set username to email since we use email as USERNAME_FIELD
        validated_data['username'] = validated_data['email']
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DonorRegistrationSerializer(serializers.ModelSerializer):
    """Donor registration serializer"""
    user = UserRegistrationSerializer()
    
    class Meta:
        model = DonorProfile
        fields = ['user', 'blood_group', 'city', 'state', 'date_of_birth', 'weight', 'gender']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'DONOR'
        user = UserRegistrationSerializer().create(user_data)
        donor_profile = DonorProfile.objects.create(user=user, **validated_data)
        return donor_profile


class HospitalRegistrationSerializer(serializers.ModelSerializer):
    """Hospital registration serializer"""
    user = UserRegistrationSerializer()
    
    class Meta:
        model = HospitalProfile
        fields = [
            'user', 'hospital_name', 'registration_number', 'issuing_authority', 
            'year_of_registration', 'address_line', 'area', 'city', 'district', 
            'state', 'pincode', 'authorized_person_name', 'authorized_person_designation',
            'authorized_person_mobile', 'authorized_person_email', 'has_blood_bank',
            'blood_bank_license', 'storage_capacity', 'registration_certificate',
            'blood_bank_license_doc', 'authorization_letter', 'hospital_seal'
        ]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'HOSPITAL'
        user = UserRegistrationSerializer().create(user_data)
        hospital_profile = HospitalProfile.objects.create(user=user, **validated_data)
        return hospital_profile


class CampRegistrationSerializer(serializers.ModelSerializer):
    """Camp registration serializer"""
    user = UserRegistrationSerializer()
    
    class Meta:
        model = CampProfile
        fields = [
            'user', 'organization_name', 'organization_type', 'registration_number',
            'contact_person_name', 'contact_person_designation', 'contact_person_mobile',
            'address_line', 'city', 'state', 'pincode', 'organization_certificate',
            'authorization_letter'
        ]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'CAMP'
        user = UserRegistrationSerializer().create(user_data)
        camp_profile = CampProfile.objects.create(user=user, **validated_data)
        return camp_profile


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """Patient registration serializer"""
    user = UserRegistrationSerializer()
    emergency_contact_relation = serializers.CharField(max_length=20, required=False)
    blood_group = serializers.CharField(max_length=3, required=False)
    
    class Meta:
        model = PatientProfile
        fields = [
            'user', 'date_of_birth', 'gender', 'city', 'state', 
            'emergency_contact', 'emergency_contact_name', 'emergency_contact_relation',
            'medical_conditions', 'blood_group'
        ]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'PATIENT'
        user = UserRegistrationSerializer().create(user_data)
        patient_profile = PatientProfile.objects.create(user=user, **validated_data)
        return patient_profile


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'role', 'is_verified', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'created_at']


class DonorProfileSerializer(serializers.ModelSerializer):
    """Donor profile serializer"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = DonorProfile
        fields = '__all__'
        read_only_fields = ['user', 'total_donations', 'created_at']


class HospitalProfileSerializer(serializers.ModelSerializer):
    """Hospital profile serializer"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = HospitalProfile
        fields = '__all__'
        read_only_fields = ['user', 'verification_status', 'verified_by', 'verification_date', 'created_at']


class CampProfileSerializer(serializers.ModelSerializer):
    """Camp profile serializer"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CampProfile
        fields = '__all__'
        read_only_fields = ['user', 'verification_status', 'verified_by', 'verification_date', 'created_at']


class PatientProfileSerializer(serializers.ModelSerializer):
    """Patient profile serializer"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at']