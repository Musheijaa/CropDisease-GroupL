from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    primary_crops = models.CharField(max_length=200, blank=True, help_text="Main crops you grow")
    user_type = models.CharField(max_length=20, choices=[
        ('farmer', 'Farmer'),
        ('agronomist', 'Agronomist'),
        ('extension_worker', 'Extension Worker'),
    ], default='farmer')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class CropType(models.Model):
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100)
    crop_type = models.ForeignKey(CropType, on_delete=models.CASCADE)
    description = models.TextField()
    symptoms = models.TextField()
    treatment = models.TextField()
    prevention = models.TextField()
    severity_levels = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.crop_type.name}"

class Diagnosis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop_image = models.ImageField(upload_to='crop_images/')
    crop_type = models.ForeignKey(CropType, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ML Model Results (to be populated by ML team)
    predicted_disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    severity_level = models.CharField(max_length=20, blank=True)
    affected_area_percentage = models.FloatField(null=True, blank=True)
    
    # Environmental data
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    soil_ph = models.FloatField(null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=[
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='processing')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Diagnosis {self.id} - {self.user.username}"

class Recommendation(models.Model):
    diagnosis = models.OneToOneField(Diagnosis, on_delete=models.CASCADE)
    treatment_plan = models.TextField()
    preventive_measures = models.TextField()
    follow_up_actions = models.TextField()
    estimated_recovery_time = models.CharField(max_length=50, blank=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation for {self.diagnosis.id}"

class IoTDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=50, choices=[
        ('soil_sensor', 'Soil Sensor'),
        ('weather_station', 'Weather Station'),
        ('camera', 'Camera'),
    ])
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    last_reading = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.device_type} - {self.device_id}"

class IoTReading(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    soil_moisture = models.FloatField(null=True, blank=True)
    soil_ph = models.FloatField(null=True, blank=True)
    light_intensity = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.device_id} - {self.timestamp}"

class SystemMessage(models.Model):
    MESSAGE_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_messages')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.message_type}"

class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

class WeatherLocation(models.Model):
    API_PROVIDERS = [
        ('openweathermap', 'OpenWeatherMap'),
        ('weatherapi', 'WeatherAPI.com'),
        ('accuweather', 'AccuWeather'),
    ]
    
    name = models.CharField(max_length=100)
    
    api_provider = models.CharField(max_length=20, choices=API_PROVIDERS, default='openweathermap')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
class WeatherData(models.Model):
    location = models.ForeignKey(WeatherLocation, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    precipitation = models.FloatField(default=0)
    description = models.CharField(max_length=100)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.location.name} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"