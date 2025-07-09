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
from .models import Diagnosis, UserProfile, CropType, Disease, Recommendation, IoTReading, SystemMessage, SystemSettings
from .forms import DiagnosisForm, UserProfileForm
import json

def home(request):
    """Landing page with hero section and key features"""
    context = {
        'total_diagnoses': Diagnosis.objects.filter(status='completed').count(),
        'total_users': UserProfile.objects.count(),
        'crop_types': CropType.objects.count(),
    }
    return render(request, 'crops/home.html', context)

def about(request):
    """About page with system information"""
    return render(request, 'crops/about.html')

def register(request):
    """User registration with profile creation"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to FloraSight.')
            return redirect('crops:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard with user statistics and recent diagnoses"""
    user_diagnoses = Diagnosis.objects.filter(user=request.user)
    recent_diagnoses = user_diagnoses.order_by('-created_at')[:5]
    
    # Statistics
    total_diagnoses = user_diagnoses.count()
    completed_diagnoses = user_diagnoses.filter(status='completed').count()
    processing_diagnoses = user_diagnoses.filter(status='processing').count()
    
    # Disease distribution
    disease_stats = user_diagnoses.filter(
        predicted_disease__isnull=False
    ).values(
        'predicted_disease__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'recent_diagnoses': recent_diagnoses,
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
        'processing_diagnoses': processing_diagnoses,
        'disease_stats': disease_stats,
    }
    return render(request, 'crops/dashboard.html', context)

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
def diagnosis_history(request):
    """Paginated list of user's diagnosis history"""
    diagnoses = Diagnosis.objects.filter(user=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        diagnoses = diagnoses.filter(
            Q(predicted_disease__name__icontains=search_query) |
            Q(crop_type__name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        diagnoses = diagnoses.filter(status=status_filter)
    
    paginator = Paginator(diagnoses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'crops/diagnosis_history.html', context)

@login_required
def profile(request):
    """User profile management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # ✅ Add these two lines:
    total_diagnoses = request.user.diagnosis_set.count()
    completed_diagnoses = request.user.diagnosis_set.filter(status='completed').count()

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
        'total_diagnoses': total_diagnoses,        
        'completed_diagnoses': completed_diagnoses 
    }
    return render(request, 'crops/profile.html', context)

# Admin Panel Views

@staff_member_required
def admin_panel(request):
    """Admin dashboard with system overview"""
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    total_diagnoses = Diagnosis.objects.count()
    completed_diagnoses = Diagnosis.objects.filter(status='completed').count()
    disease_types = Disease.objects.count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_diagnoses = Diagnosis.objects.order_by('-created_at')[:5]
    recent_messages = SystemMessage.objects.order_by('-created_at')[:5]
    
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
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
        'disease_types': disease_types,
        'recent_users': recent_users,
        'recent_diagnoses': recent_diagnoses,
        'recent_messages': recent_messages,
        'user_growth_data': user_growth_data,
        'disease_stats': disease_stats,
    }
    return render(request, 'crops/admin/dashboard.html', context)

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

    # ✅ Compute total and completed diagnosis counts
    total_diagnoses = user.diagnosis_set.count()
    completed_diagnoses = user.diagnosis_set.filter(status='completed').count()

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
        'total_diagnoses': total_diagnoses,
        'completed_diagnoses': completed_diagnoses,
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

@staff_member_required
def admin_messages(request):
    """Admin system messages"""
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
def admin_settings(request):
    """Admin system settings"""
    settings_list = SystemSettings.objects.order_by('key')
    
    if request.method == 'POST':
        key = request.POST.get('key')
        value = request.POST.get('value')
        description = request.POST.get('description', '')
        
        setting, created = SystemSettings.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description, 'updated_by': request.user}
        )
        
        if not created:
            setting.value = value
            setting.description = description
            setting.updated_by = request.user
            setting.save()
        
        messages.success(request, f'Setting {key} updated successfully!')
        return redirect('crops:admin_settings')
    
    context = {
        'settings_list': settings_list,
    }
    return render(request, 'crops/admin/settings.html', context)

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