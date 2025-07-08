from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Diagnosis, UserProfile, CropType, Disease, Recommendation, IoTReading
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