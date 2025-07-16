from django.urls import path
from . import views
from .views import CustomLoginView

app_name = 'crops'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # User features
    path('my-diagnoses/', views.my_diagnoses, name='my_diagnoses'),
    path('send-message/', views.send_message_to_admin, name='send_message_to_admin'),
    path('upload/', views.upload_image, name='upload_image'),
    path('diagnosis/<uuid:diagnosis_id>/', views.diagnosis_detail, name='diagnosis_detail'),
    path('diagnoses/<int:diagnosis_id>/', views.diagnosis_detail, name='diagnosis_detail'),
    path('diagnoses/', views.diagnosis_history, name='diagnosis_history'),

  
    path('my-diagnoses/', views.my_diagnoses, name='my_diagnoses'),
    path('api/predict-disease/', views.predict_disease, name='predict_disease'),
    path('save-diagnosis/', views.save_diagnosis, name='save_diagnosis'),

    
    # Profile management
    path('profile/', views.profile, name='profile'),
    
    # Admin Panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/send-broadcast/', views.admin_send_broadcast, name='admin_send_broadcast'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/diseases/', views.admin_diseases, name='admin_diseases'),
    path('admin-panel/diagnoses/', views.admin_diagnoses, name='admin_diagnoses'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    
    # API endpoints for ML integration
    path('api/process-image/', views.process_image_api, name='process_image_api'),
    path('api/iot-data/', views.iot_data_api, name='iot_data_api'),
    
    path('dashboard/', views.admin_panel),  # Optional alias for admin_panel
    
     path('auth/login/', CustomLoginView.as_view(), name='login'),
     
     path('mark-message-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
     
     path('all-messages/', views.all_messages, name='all_messages'),
     path('admin-panel/weather/', views.admin_weather, name='admin_weather'),
      path('admin-panel/weather/add-location/', views.admin_add_weather_location, name='admin_add_weather_location'),
      path('admin-panel/weather/api/current/<str:location>/', views.weather_api_current, name='weather_api_current'),
      path('admin-panel/weather/api/forecast/<str:location>/', views.weather_api_forecast, name='weather_api_forecast'),
    

]