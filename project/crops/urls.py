from django.urls import path
from . import views

app_name = 'crops'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # Dashboard and main features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('diagnosis/<uuid:diagnosis_id>/', views.diagnosis_detail, name='diagnosis_detail'),
    path('diagnoses/', views.diagnosis_history, name='diagnosis_history'),
    
    # Profile management
    path('profile/', views.profile, name='profile'),
    
    # API endpoints for ML integration
    path('api/process-image/', views.process_image_api, name='process_image_api'),
    path('api/iot-data/', views.iot_data_api, name='iot_data_api'),
]