from django import forms
from .models import Diagnosis, UserProfile, CropType

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['crop_image', 'crop_type', 'notes', 'temperature', 'humidity', 'soil_ph']
        widgets = {
            'crop_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'crop_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes about the crop condition...'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Temperature (°C)',
                'step': '0.1'
            }),
            'humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Humidity (%)',
                'step': '0.1'
            }),
            'soil_ph': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soil pH',
                'step': '0.1',
                'min': '0',
                'max': '14'
            }),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'location', 'farm_size', 'user_type']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State/Province, Country'
            }),
            'farm_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Farm size in acres',
                'step': '0.01'
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }