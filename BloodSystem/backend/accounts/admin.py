from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DonorProfile, HospitalProfile, CampProfile, PatientProfile, AdminProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'role', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'phone', 'role', 'is_verified')
        }),
    )


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'city', 'total_donations', 'is_eligible', 'created_at')
    list_filter = ('blood_group', 'city', 'is_eligible', 'gender')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
    readonly_fields = ('total_donations', 'created_at')


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ('hospital_name', 'city', 'verification_status', 'has_blood_bank', 'created_at')
    list_filter = ('verification_status', 'has_blood_bank', 'city', 'state')
    search_fields = ('hospital_name', 'registration_number', 'city')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'hospital_name', 'registration_number', 'issuing_authority', 'year_of_registration')
        }),
        ('Address', {
            'fields': ('address_line', 'area', 'city', 'district', 'state', 'pincode')
        }),
        ('Authorized Person', {
            'fields': ('authorized_person_name', 'authorized_person_designation', 'authorized_person_mobile', 'authorized_person_email')
        }),
        ('Blood Bank', {
            'fields': ('has_blood_bank', 'blood_bank_license', 'storage_capacity')
        }),
        ('Documents', {
            'fields': ('registration_certificate', 'blood_bank_license_doc', 'authorization_letter', 'hospital_seal')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verified_by', 'verification_date', 'rejection_reason')
        }),
    )


@admin.register(CampProfile)
class CampProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'organization_type', 'city', 'verification_status', 'created_at')
    list_filter = ('organization_type', 'verification_status', 'city', 'state')
    search_fields = ('organization_name', 'registration_number', 'city')
    readonly_fields = ('created_at',)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'gender', 'created_at')
    list_filter = ('city', 'gender', 'state')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
    readonly_fields = ('created_at',)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'created_at')
    list_filter = ('department', 'designation')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('created_at',)