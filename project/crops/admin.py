from django.contrib import admin
from .models import UserProfile, CropType, Disease, Diagnosis, Recommendation, IoTDevice, IoTReading

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'location', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']

@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'created_at']
    search_fields = ['name', 'scientific_name']

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop_type', 'created_at']
    list_filter = ['crop_type', 'created_at']
    search_fields = ['name', 'crop_type__name']

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'crop_type', 'predicted_disease', 'confidence_score', 'status', 'created_at']
    list_filter = ['status', 'crop_type', 'created_at']
    search_fields = ['user__username', 'predicted_disease__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['diagnosis', 'estimated_recovery_time', 'cost_estimate', 'created_at']
    search_fields = ['diagnosis__user__username']

@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'user', 'device_type', 'is_active', 'last_reading']
    list_filter = ['device_type', 'is_active']
    search_fields = ['device_id', 'user__username']

@admin.register(IoTReading)
class IoTReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'temperature', 'humidity', 'soil_moisture', 'timestamp']
    list_filter = ['device__device_type', 'timestamp']
    search_fields = ['device__device_id']