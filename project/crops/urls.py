from django.urls import path
from . import views
from django.utils.html import json_script


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
    
    # Admin Panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/diseases/', views.admin_diseases, name='admin_diseases'),
    path('admin-panel/diagnoses/', views.admin_diagnoses, name='admin_diagnoses'),
    path('admin-panel/analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/settings/', views.admin_settings, name='admin_settings'),
    
    # API endpoints for ML integration
    path('api/process-image/', views.process_image_api, name='process_image_api'),
    path('api/iot-data/', views.iot_data_api, name='iot_data_api'),
]