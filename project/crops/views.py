from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.views import LoginView
from .models import Diagnosis, UserProfile, CropType, Disease, Recommendation, IoTReading, SystemMessage, SystemSettings
from .forms import DiagnosisForm, UserProfileForm
import json
import logging
import tensorflow as tf
import numpy as np  


from django.http import JsonResponse

from django.conf import settings
from .services.ml_service import get_predictor, DiseasePredictor
def home(request):
    features = [
        {'icon': 'brain', 'title': 'Advanced AI Detection', 'desc': 'Our AI model analyzes crop images with 99% accuracy...'},
        {'icon': 'camera', 'title': 'Simple Image Upload', 'desc': 'Simply take a photo of your crop and upload it...'},
        {'icon': 'prescription-bottle-alt', 'title': 'Treatment Recommendations', 'desc': 'Receive personalized treatment plans...'},
        {'icon': 'chart-line', 'title': 'Analytics & Insights', 'desc': 'Track disease patterns, monitor crop health trends...'},
        {'icon': 'wifi', 'title': 'IoT Integration', 'desc': 'Connect environmental sensors to monitor soil conditions...'},
        {'icon': 'history', 'title': 'Historical Records', 'desc': 'Maintain comprehensive records of all diagnoses...'},
        {'icon': 'mobile-alt', 'title': 'Mobile Friendly', 'desc': 'Access FloraSight from anywhere...'}
    ]

    # Add other context variables as needed
    if request.user.is_authenticated and request.user.is_staff:
        messages.info(request, "Admins are redirected to the Admin Panel.")
        return redirect('crops:admin_panel')
    return render(request, 'crops/home.html')


def register(request):
    """Progressive user registration with comprehensive profile creation"""
    if request.method == 'POST':
        # Handle step-by-step registration
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Basic account information
            form = UserCreationForm(request.POST)
            if form.is_valid():
                # Store form data in session for step 2
                request.session['registration_data'] = {
                    'username': form.cleaned_data['username'],
                    'password1': form.cleaned_data['password1'],
                    'password2': form.cleaned_data['password2'],
                }
                return render(request, 'registration/register_step2.html')
        
        elif step == '2':
            # Profile and farm information
            reg_data = request.session.get('registration_data')
            if reg_data:
                # Create user account
                user = User.objects.create_user(
                    username=reg_data['username'],
                    password=reg_data['password1']
                )
                
                # Create profile with additional information
                UserProfile.objects.create(
                    user=user,
                    user_type=request.POST.get('user_type', 'farmer'),
                    location=request.POST.get('location', ''),
                    farm_size=request.POST.get('farm_size') or None,
                    phone_number=request.POST.get('phone_number', ''),
                    primary_crops=request.POST.get('primary_crops', ''),
                )
                
                # Clear session data
                del request.session['registration_data']
                
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to FloraSight.')
                return redirect('crops:upload_image')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def my_diagnoses(request):
    """User's diagnosis overview - replaces dashboard for regular users"""
    if request.user.is_staff:
        return redirect('crops:admin_panel')
    
    user_diagnoses = Diagnosis.objects.filter(user=request.user)
    recent_diagnoses = user_diagnoses.order_by('-created_at')[:5]
    
    # Statistics
    total_diagnoses = user_diagnoses.count()
    completed_diagnoses = user_diagnoses.filter(status='completed').count()
    processing_diagnoses = user_diagnoses.filter(status='processing').count()
    
    # Recent system messages for this user
    user_messages = SystemMessage.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')[:5]
    
    context = {
        'recent_diagnoses': recent_diagnoses,
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
        'processing_diagnoses': processing_diagnoses,
        'user_messages': user_messages,
    }
    return render(request, 'crops/my_diagnoses.html', context)

@login_required
def send_message_to_admin(request):
    """Allow users to send messages to admin"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        message_type = request.POST.get('message_type', 'info')
        
        # Create message for admin (staff users will see it)
        SystemMessage.objects.create(
            title=f"From {request.user.username}: {title}",
            message=message,
            message_type=message_type,
            user=None,  # Admin message
            created_by=request.user
        )
        
        messages.success(request, 'Your message has been sent to the administrators.')
        return redirect('crops:my_diagnoses')
    
    return render(request, 'crops/send_message.html')
@login_required
def upload_image(request):
    """Image upload form for crop diagnosis"""
    if request.method == 'POST':
        form = DiagnosisForm(request.POST, request.FILES)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.user = request.user
            diagnosis.save()
            
            # Here the ML team will integrate their model
            # For now, we'll just mark it as processing
            messages.success(request, 'Image uploaded successfully! Processing diagnosis...')
            return redirect('crops:diagnosis_detail', diagnosis_id=diagnosis.id)
    else:
        form = DiagnosisForm()
    
    context = {
        'form': form,
        'crop_types': CropType.objects.all(),
    }
    return render(request, 'crops/upload.html', context)

@login_required
def diagnosis_detail(request, diagnosis_id):
    """Detailed view of a specific diagnosis"""
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id, user=request.user)
    recommendation = None
    
    try:
        recommendation = diagnosis.recommendation
    except Recommendation.DoesNotExist:
        pass
    
    context = {
        'diagnosis': diagnosis,
        'recommendation': recommendation,
    }
    return render(request, 'crops/diagnosis_detail.html', context)
@login_required
def profile(request):
    """User profile management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('crops:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'crops/profile.html', context)

# Admin Panel Views

@staff_member_required
def admin_panel(request):
    """Enhanced admin dashboard with comprehensive system overview and analytics"""
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    total_diagnoses = Diagnosis.objects.count()
    completed_diagnoses = Diagnosis.objects.filter(status='completed').count()
    disease_types = Disease.objects.count()
    pending_messages = SystemMessage.objects.filter(user__isnull=True, is_read=False).count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_diagnoses = Diagnosis.objects.order_by('-created_at')[:5]
    recent_user_messages = SystemMessage.objects.filter(user__isnull=True).order_by('-created_at')[:5]
    
    # User growth data (last 6 months)
    user_growth_data = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        users_count = User.objects.filter(date_joined__lte=date).count()
        user_growth_data.append({
            'month': date.strftime('%b'),
            'total_users': users_count,
            'active_users': User.objects.filter(
                date_joined__lte=date,
                last_login__gte=date - timedelta(days=30)
            ).count()
        })
    user_growth_data.reverse()
    
    # Disease distribution
    disease_stats = Diagnosis.objects.filter(
        predicted_disease__isnull=False
    ).values(
        'predicted_disease__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Monthly diagnosis trends
    monthly_diagnoses = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        count = Diagnosis.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        monthly_diagnoses.append({
            'month': date.strftime('%b %Y'),
            'count': count
        })
    monthly_diagnoses.reverse()
    
    # User type distribution
    user_type_stats = UserProfile.objects.values('user_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Average confidence score
    avg_confidence = Diagnosis.objects.filter(confidence_score__isnull=False).aggregate(
        avg_confidence=Avg('confidence_score')
    )['avg_confidence'] or 0
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
        'disease_types': disease_types,
        'pending_messages': pending_messages,
        'recent_users': recent_users,
        'recent_diagnoses': recent_diagnoses,
        'recent_user_messages': recent_user_messages,
        'user_growth_data': user_growth_data,
        'disease_stats': disease_stats,
        'monthly_diagnoses': monthly_diagnoses,
        'user_type_stats': user_type_stats,
        'avg_confidence': round(avg_confidence, 1),
    }
    return render(request, 'crops/admin/dashboard.html', context)

@staff_member_required
def admin_send_broadcast(request):
    """Allow admin to send broadcast messages to all users"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        message_type = request.POST.get('message_type', 'info')
        target_audience = request.POST.get('target_audience', 'all')
        
        # Create broadcast message
        if target_audience == 'all':
            # Send to all users (user=None means broadcast)
            SystemMessage.objects.create(
                title=title,
                message=message,
                message_type=message_type,
                user=None
            )
        else:
            # Send to specific user type
            users = User.objects.filter(userprofile__user_type=target_audience)
            for user in users:
                SystemMessage.objects.create(
                    title=title,
                    message=message,
                    message_type=message_type,
                    user=user
                )
        
        messages.success(request, f'Broadcast message sent successfully to {target_audience}!')
        return redirect('crops:admin_panel')
    
    return render(request, 'crops/admin/send_broadcast.html')
@staff_member_required
def admin_users(request):
    """Admin user management"""
    users = User.objects.select_related('userprofile').order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter by user type
    user_type_filter = request.GET.get('user_type')
    if user_type_filter:
        users = users.filter(userprofile__user_type=user_type_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
    }
    return render(request, 'crops/admin/users.html', context)

@staff_member_required
def admin_add_user(request):
    """Add new user"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('crops:admin_users')
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()
    
    context = {
        'form': form,
        'profile_form': profile_form,
    }
    return render(request, 'crops/admin/add_user.html', context)

@staff_member_required
def admin_edit_user(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        # Update basic user info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('crops:admin_users')
    else:
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_obj': user,
        'profile_form': profile_form,
    }
    return render(request, 'crops/admin/edit_user.html', context)

@staff_member_required
def admin_delete_user(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('crops:admin_users')
    
    context = {'user_obj': user}
    return render(request, 'crops/admin/delete_user.html', context)

@staff_member_required
def admin_diseases(request):
    """Admin disease management"""
    diseases = Disease.objects.select_related('crop_type').order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        diseases = diseases.filter(
            Q(name__icontains=search_query) |
            Q(crop_type__name__icontains=search_query)
        )
    
    paginator = Paginator(diseases, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'crops/admin/diseases.html', context)

@staff_member_required
def admin_diagnoses(request):
    """Admin diagnosis management"""
    diagnoses = Diagnosis.objects.select_related('user', 'crop_type', 'predicted_disease').order_by('-created_at')
    
    # Search and filter
    search_query = request.GET.get('search')
    if search_query:
        diagnoses = diagnoses.filter(
            Q(user__username__icontains=search_query) |
            Q(predicted_disease__name__icontains=search_query)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        diagnoses = diagnoses.filter(status=status_filter)
    
    paginator = Paginator(diagnoses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'crops/admin/diagnoses.html', context)

@staff_member_required
def admin_messages(request):
    """Admin system messages management"""
    messages_list = SystemMessage.objects.order_by('-created_at')
    
    # Filter by type
    message_type = request.GET.get('type')
    if message_type:
        messages_list = messages_list.filter(message_type=message_type)
    
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'message_type': message_type,
    }
    return render(request, 'crops/admin/messages.html', context)

@staff_member_required
def admin_analytics(request):
    """Admin analytics dashboard"""
    # User analytics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    new_users_this_month = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count()
    
    # Diagnosis analytics
    total_diagnoses = Diagnosis.objects.count()
    completed_diagnoses = Diagnosis.objects.filter(status='completed').count()
    avg_confidence = Diagnosis.objects.filter(confidence_score__isnull=False).aggregate(
        avg_confidence=Avg('confidence_score')
    )['avg_confidence'] or 0
    
    # Disease analytics
    disease_distribution = Diagnosis.objects.filter(
        predicted_disease__isnull=False
    ).values(
        'predicted_disease__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly diagnosis trends
    monthly_diagnoses = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        count = Diagnosis.objects.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).count()
        monthly_diagnoses.append({
            'month': date.strftime('%b %Y'),
            'count': count
        })
    monthly_diagnoses.reverse()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_this_month': new_users_this_month,
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
        'avg_confidence': round(avg_confidence, 1),
        'disease_distribution': disease_distribution,
        'monthly_diagnoses': monthly_diagnoses,
    }
    return render(request, 'crops/admin/analytics.html', context)

# API Endpoints for ML Integration

@csrf_exempt
@require_http_methods(["POST"])
def process_image_api(request):
    """API endpoint for ML team to process uploaded images"""
    try:
        data = json.loads(request.body)
        diagnosis_id = data.get('diagnosis_id')
        
        diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id)
        
        # Update diagnosis with ML results
        diagnosis.predicted_disease_id = data.get('predicted_disease_id')
        diagnosis.confidence_score = data.get('confidence_score')
        diagnosis.severity_level = data.get('severity_level')
        diagnosis.affected_area_percentage = data.get('affected_area_percentage')
        diagnosis.status = 'completed'
        diagnosis.save()
        
        # Create recommendation if provided
        if data.get('recommendation'):
            rec_data = data['recommendation']
            Recommendation.objects.create(
                diagnosis=diagnosis,
                treatment_plan=rec_data.get('treatment_plan', ''),
                preventive_measures=rec_data.get('preventive_measures', ''),
                follow_up_actions=rec_data.get('follow_up_actions', ''),
                estimated_recovery_time=rec_data.get('estimated_recovery_time', ''),
                cost_estimate=rec_data.get('cost_estimate')
            )
        
        return JsonResponse({'status': 'success', 'message': 'Diagnosis updated successfully'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def iot_data_api(request):
    """API endpoint for IoT devices to send sensor data"""
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        
        # Here you would validate the device and store the data
        # This is a placeholder for IoT integration
        
        return JsonResponse({'status': 'success', 'message': 'IoT data received'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_staff:
            return '/admin-panel/'
        return '/'
    
@login_required
def mark_message_read(request, message_id):
    message = get_object_or_404(SystemMessage, id=message_id, user=request.user)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'})
@login_required
def all_messages(request):
    messages = SystemMessage.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')
    
    # Mark all as read when viewing full list
    messages.filter(is_read=False).update(is_read=True)
    
    paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'crops/all_messages.html', {
        'page_obj': page_obj,
        'unread_count': 0  # Since we just marked all as read
    })
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.ml_service import get_predictor

@csrf_exempt
def predict_disease(request):
    """Handle image upload and disease prediction"""
    if request.method == 'POST':
        if 'crop_image' not in request.FILES:
            return JsonResponse({
                'status': 'error',
                'error': 'No image file provided'
            }, status=400)
            
        try:
            image_file = request.FILES['crop_image']
            result = get_predictor().predict_disease(image_file)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'error': 'Only POST requests are allowed'
        }, status=405)
import logging

logger = logging.getLogger(__name__)

@csrf_exempt  # Remove this in production; use proper CSRF handling
def save_diagnosis(request):
    if request.method == 'POST':
        print("Received save_diagnosis request with POST data:", request.POST)
        print("Received file data:", request.FILES)

        predicted_disease_name = request.POST.get('predicted_disease')
        try:
            disease = Disease.objects.get(name=predicted_disease_name)
        except Disease.DoesNotExist:
            print(f"❌ Disease not found: {predicted_disease_name}")
            return JsonResponse({'status': 'error', 'message': f'Disease \"{predicted_disease_name}\" not found.'}, status=400)

        try:
            diagnosis = Diagnosis(
                user=request.user,  # ✅ Assign the current authenticated user
                crop_image=request.FILES.get('crop_image'),
                predicted_disease=disease,
                confidence_score=request.POST.get('confidence_score'),
                treatment=request.POST.get('treatment'),
                prevention=request.POST.get('prevention'),
                crop_type=request.POST.get('crop_type') or None,
                temperature=request.POST.get('temperature') or None,
                humidity=request.POST.get('humidity') or None,
                soil_ph=request.POST.get('soil_ph') or None,
                notes=request.POST.get('notes'),
                status='completed',
            )
            diagnosis.save()
            print("✅ Diagnosis saved successfully")
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"❌ Exception occurred while saving diagnosis:\n{e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def diagnosis_history(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    diagnoses = Diagnosis.objects.all()

    if search_query:
        diagnoses = diagnoses.filter(
            Q(predicted_disease__name__icontains=search_query) |
            Q(crop_type__icontains=search_query)
        )
    if status_filter:
        diagnoses = diagnoses.filter(status=status_filter)

    paginator = Paginator(diagnoses.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crops/diagnosis_history.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter
    })


