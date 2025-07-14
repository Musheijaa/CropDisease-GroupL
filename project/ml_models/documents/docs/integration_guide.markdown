# Django Integration Guide for Crop Disease Model

## Overview
This guide outlines the step-by-step process to integrate the trained CNN model (`trained_cnn_model.keras`) into your Django project (`CROP_DISEASE`) for plant disease diagnosis. The integration supports the RECESS FINAL PROJECT 2025 requirements (FR5–FR6: accurate diagnosis, NFR6: usability) with a deadline of July 18, 2025. Current date: 07:46 AM EAT, Friday, July 11, 2025.

## Prerequisites
- Trained model: `trained_cnn_model.keras` or `best_model.keras` and `class_indices.txt` from the training script.
- Django project set up with a virtual environment.
- Dependencies: `django==4.2.13`, `tensorflow==2.10.0`, `numpy==1.23.5`, `pillow==9.5.0`.

## Step-by-Step Integration

### Step 1: Set Up the Django Project Environment
1. **Activate Virtual Environment**:
   - Navigate to `/home/ltgwgeorge/Desktop/GeorgeCode/python/RecessPython/CROP_DISEASE/`.
   - Run: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).
2. **Install Required Packages**:
   - Run: `pip install tensorflow==2.10.0 numpy pillow`.
   - Update `requirements.txt`: `echo -e "django==4.2.13\ntensorflow==2.10.0\nnumpy==1.23.5\npillow==9.5.0" > requirements.txt`.
3. **Verify GPU Support (Optional)**:
   - Run: `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`.
   - Ensure CUDA 11.2 and cuDNN 8.1 if using GPU.

### Step 2: Organize Model Files
1. **Create Model Directory**:
   - Run: `mkdir -p diagnosis/ml_model`.
2. **Copy Model and Class Indices**:
   - Run: `cp trained_cnn_model.keras diagnosis/ml_model/`, `cp best_model.keras diagnosis/ml_model/`, `cp class_indices.txt diagnosis/ml_model/`.
   - Verify: `ls diagnosis/ml_model/`.

### Step 3: Update Django Settings
1. **Add Media Directory**:
   - Edit `CROP_DISEASE/settings.py`:
     ```python
     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
     MEDIA_URL = '/media/'
     ```
2. **Update Installed Apps**:
   - Ensure `diagnosis` is in `INSTALLED_APPS`:
     ```python
     INSTALLED_APPS = [
         ...,
         'diagnosis',
     ]
     ```
3. **Configure URLs**:
   - Edit `CROP_DISEASE/urls.py`:
     ```python
     from django.conf import settings
     from django.conf.urls.static import static
     from django.contrib import admin
     from django.urls import path, include

     urlpatterns = [
         path('admin/', admin.site.urls),
         path('', include('diagnosis.urls')),
     ]

     if settings.DEBUG:
         urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
     ```

### Step 4: Create or Update the Diagnosis App
1. **Create URLs**:
   - Create `diagnosis/urls.py`:
     ```python
     from django.urls import path
     from . import views

     urlpatterns = [
         path('', views.upload_image, name='upload_image'),
     ]
     ```
2. **Create Views**:
   - Edit `diagnosis/views.py`:
     ```python
     import os
     import numpy as np
     from django.shortcuts import render
     from django.core.files.storage import FileSystemStorage
     import tensorflow as tf
     import json

     def upload_image(request):
         prediction = None
         image_url = None
         error = None

         if request.method == 'POST' and request.FILES.get('image'):
             uploaded_file = request.FILES['image']
             fs = FileSystemStorage()
             filename = fs.save(uploaded_file.name, uploaded_file)
             uploaded_file_url = fs.url(filename)

             try:
                 model_path = os.path.join('diagnosis', 'ml_model', 'trained_cnn_model.keras')
                 model = tf.keras.models.load_model(model_path)
                 
                 with open(os.path.join('diagnosis', 'ml_model', 'class_indices.txt'), 'r') as f:
                     class_indices = json.load(f)
                 class_names = {v: k for k, v in class_indices.items()}

                 img_path = os.path.join(fs.location, filename)
                 img = tf.keras.preprocessing.image.load_img(img_path, target_size=(224, 224))
                 img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
                 img_array = np.expand_dims(img_array, axis=0)

                 pred = model.predict(img_array)
                 pred_class = np.argmax(pred, axis=1)[0]
                 disease_name = class_names.get(str(pred_class), "Unknown")
                 confidence = float(np.max(pred))
                 prediction = f"Disease: {disease_name} (Confidence: {confidence:.2%})"
                 image_url = uploaded_file_url

             except Exception as e:
                 error = f"Error processing image: {str(e)}"
                 fs.delete(filename)

             if not error:
                 fs.delete(filename)

         return render(request, 'diagnosis/upload.html', {
             'prediction': prediction,
             'image_url': image_url,
             'error': error
         })
     ```
3. **Create Template**:
   - Create `diagnosis/templates/diagnosis/upload.html`:
     ```html
     <!DOCTYPE html>
     <html lang="en">
     <head>
         <meta charset="UTF-8">
         <title>Plant Disease Diagnosis</title>
         <link href="https://cdn.tailwindcss.com" rel="stylesheet">
     </head>
     <body class="bg-gray-100 flex items-center justify-center min-h-screen">
         <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
             <h1 class="text-2xl font-bold text-center mb-4">Plant Disease Diagnosis</h1>
             <form method="post" enctype="multipart/form-data" class="mb-4">
                 {% csrf_token %}
                 <input type="file" name="image" accept="image/*" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                 <button type="submit" class="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 mt-2">Diagnose</button>
             </form>
             {% if error %}
                 <p class="text-red-500 text-center">{{ error }}</p>
             {% endif %}
             {% if prediction %}
                 <p class="text-lg font-semibold text-center mt-4">{{ prediction }}</p>
                 {% if image_url %}
                     <img src="{{ image_url }}" alt="Uploaded Image" class="mt-4 w-full rounded">
                 {% endif %}
             {% endif %}
         </div>
     </body>
     </html>
     ```

### Step 5: Test the Integration
1. **Run Django Server**:
   - Run: `python manage.py runserver`.
   - Open: `http://127.0.0.1:8000/`.
2. **Upload Test Image**:
   - Use images from `dataset/test/test/` or new plant images.
   - Verify predictions match training classes.
3. **Debug Issues**:
   - Check terminal for errors (e.g., file path issues, model loading failures).

### Step 6: Enhance and Document
1. **Add Styling**: Tailwind CSS is included in `upload.html` for NFR6 compliance.
2. **Document in Report**:
   - Include UI screenshots and integration steps in your 10-page report (Task 12).

### Step 7: Deploy (Optional)
- For production, use Gunicorn and Nginx, but `runserver` is sufficient for local testing.

## Troubleshooting
- **Model Loading Error**: Ensure `trained_cnn_model.keras` path is correct in `views.py`.
- **Image Processing Error**: Verify images are 224x224-compatible and not corrupted.
- **Permission Issues**: Check write access to `media/` directory.

## Notes
- Tested on July 11, 2025. Complete integration by July 18, 2025.
- Use `best_model.keras` if it outperforms `trained_cnn_model.keras` (check `training.log`).
- Commit changes to your GitHub repository for submission.