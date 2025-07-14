# Crop Disease Project Plan and Implementation Strategy

## Project Overview
The Crop Disease project is a Django-based web application that uses a Convolutional Neural Network (CNN) to diagnose crop diseases from uploaded images, provide data-driven recommendations, integrate IoT environmental data, and offer analytics for farmers, agronomists, and extension workers. The project aligns with the BSE2301 Software Engineering Mini Project 2 requirements, focusing on machine learning (ML) and web development with Django.

## Objectives
- Develop a user-friendly web application meeting all functional requirements (FR1–FR15) and non-functional requirements (NFR1–NFR12).
- Implement a CNN model for crop disease detection and classification.
- Integrate IoT data for enhanced recommendations.
- Provide visualizations and analytics for disease patterns.
- Submit a comprehensive report and source code by July 18, 2025.

## Project Plan

### Timeline (July 4, 2025 – July 18, 2025)
- **Week 1 (July 4 – July 11, 2025)**
  - **Day 1–2 (July 4–5)**: Project setup, dataset acquisition, and team role assignment.
  - **Day 3–4 (July 6–7)**: Data exploration, CNN model training, and Django project initialization.
  - **Day 5–7 (July 8–10)**: Implement user management, image upload, and CNN integration.
  - **Day 7 (July 10)**: Schedule and conduct first supervision session via Zoom.
- **Week 2 (July 11 – July 18, 2025)**
  - **Day 8–10 (July 11–13)**: Implement recommendation system, IoT integration, and visualizations.
  - **Day 11–12 (July 14–15)**: Test and optimize system for performance and security.
  - **Day 13 (July 16)**: Prepare final report and documentation.
  - **Day 14 (July 17)**: Conduct physical presentation (date TBD).
  - **Day 15 (July 18)**: Finalize GitHub repository and submit deliverables by 11:59 PM.

### Task Breakdown
Based on the project requirements, the tasks are divided into Data Science/Machine Learning and Web Development components.

#### Data Science and Machine Learning Tasks
1. **Dataset Acquisition and Exploration (Task 0, 1, 4, 7)**
   - Download dataset from https://ryeko.org/datasets/.
   - Explore dataset to identify features, missing values, and data types.
   - Calculate the percentage of missing data for each feature.
2. **Handling Missing Data (Task 2, 3)**
   - Choose an imputation method (e.g., mean/median for numerical data, mode for categorical data) or removal based on missing data percentage.
   - Justify the method and evaluate its impact on data distribution.
3. **Feature Engineering (Task 4, 5, 6)**
   - Identify potential features (e.g., image metadata, environmental factors).
   - Create new features (e.g., normalized pixel values, derived environmental indices).
   - Evaluate feature impact on CNN model performance using metrics like accuracy and F1-score.
4. **Model Development (Task 10, 11)**
   - Train a CNN model using TensorFlow/Keras for disease classification.
   - Split data into training, validation, and test sets (e.g., 70-20-10 split).
   - Perform cross-validation (e.g., 5-fold) to evaluate model robustness.
5. **Visualization and Insights (Task 7, 8, 9, 12)**
   - Use Matplotlib, Seaborn, or Plotly to create visualizations (e.g., confusion matrices, feature importance plots, disease distribution heatmaps).
   - Interpret visualizations to derive actionable insights (e.g., prevalent diseases, regional patterns).
   - Summarize findings in the final report with conclusions and recommendations.

#### Web Development Tasks
1. **Project Setup**
   - Initialize Django project and set up virtual environment.
   - Configure GitHub repository for version control.
2. **User Management (FR1–FR3, NFR3, NFR5, NFR6)**
   - Implement user registration, login, and password reset using Django’s authentication system.
   - Use Django’s RBAC for admin access and secure session management.
   - Design a multilingual, user-friendly interface.
3. **Image Upload and Disease Diagnosis (FR4–FR6, NFR1, NFR7)**
   - Create an endpoint for image uploads.
   - Integrate the trained CNN model to process images and return diagnosis results.
   - Ensure diagnosis results are displayed within 10 seconds.
4. **Recommendation and Advisory System (FR7–FR9, NFR8)**
   - Develop logic to generate recommendations based on diagnosis and environmental data.
   - Simulate IoT data integration (e.g., temperature, humidity) due to hardware constraints.
   - Notify users of preventive measures based on environmental risks.
5. **Historical Data and Analytics (FR10–FR11)**
   - Store diagnosis history in the database.
   - Create dashboards with visualizations (e.g., disease trends over time).
6. **IoT Integration (FR12–FR13, NFR10)**
   - Simulate IoT data collection using mock APIs or static datasets.
   - Use data to enhance recommendation accuracy.
7. **Admin and Model Management (FR14–FR15, NFR5, NFR11)**
   - Build an admin panel for user and content management.
   - Allow model updates via admin interface without downtime.
8. **Non-Functional Requirements**
   - Ensure HTTPS/SSL for secure data transmission (NFR4).
   - Optimize for 1,000 concurrent users (NFR2) using Django’s caching and asynchronous tasks (e.g., Celery).
   - Implement offline mode for diagnosis history (NFR9) using local storage.
   - Ensure 99.5% uptime (NFR8) and GDPR compliance (NFR12).

### Deliverables
1. **Final Report (10 pages max)**
   - Introduction to the dataset and web application.
   - Documentation of data exploration, missing data handling, feature engineering, model training, and visualizations.
   - Screenshots of the web application and visualizations.
   - Conclusions, insights, and recommendations.
2. **Source Code**
   - Django project with CNN model integration.
   - GitHub repository link submitted to jeff.gcoff.mls@gmail.com and ndigozalivingstone2@gmail.com.
3. **Presentation**
   - Physical presentation before July 17, 2025, showcasing the application and results.

## Implementation Strategy

### Technology Stack
- **Backend**: Django with Django REST Framework for APIs.
- **Frontend**: Django templates with Tailwind CSS for styling.
- **Machine Learning**: TensorFlow/Keras for CNN model, NumPy/Pandas for data processing.
- **Visualization**: Matplotlib, Seaborn, Plotly for plots and dashboards.
- **Database**: SQLite (development), PostgreSQL (production for scalability).
- **IoT Simulation**: Mock APIs or static datasets for environmental data.
- **Version Control**: GitHub for collaboration and submission.
- **Deployment**: Local server for testing, optional cloud deployment (e.g., Heroku) for presentation.

### Django Project Structure
Below is the proposed project structure with key code snippets to guide implementation.

```
crop_disease_project/
├── manage.py
├── crop_disease/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── diagnosis/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── ml_model/
│   │   ├── cnn_model.py
│   │   ├── trained_model.h5
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── upload.html
│   ├── results.html
│   ├── dashboard.html
├── static/
│   ├── css/
│   │   ├── tailwind.css
│   ├── js/
│   ├── images/
├── requirements.txt
```

#### Key Code Snippets

1. **CNN Model Training (cnn_model.py)**

```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
import numpy as np

def build_cnn_model(input_shape=(224, 224, 3), num_classes=10):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(X_train, y_train, X_val, y_val):
    model = build_cnn_model()
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=32)
    model.save('diagnosis/ml_model/trained_model.h5')
    return model
```

2. **Django Models (models.py)**

```python
from django.db import models
from django.contrib.auth.models import User

class CropDiagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='crop_images/')
    disease_name = models.CharField(max_length=100)
    severity = models.FloatField()
    plant_part = models.CharField(max_length=50)
    diagnosis_date = models.DateTimeField(auto_now_add=True)
    environmental_data = models.JSONField()  # Store temperature, humidity, etc.
    recommendations = models.TextField()

    def __str__(self):
        return f"{self.disease_name} - {self.user.username}"
```

3. **Django Views for Image Upload and Diagnosis (views.py)**

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CropDiagnosis
from .ml_model.cnn_model import build_cnn_model
import tensorflow as tf
import numpy as np
from PIL import Image
import io

@login_required
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES['crop_image']
        img = Image.open(image).resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        model = tf.keras.models.load_model('diagnosis/ml_model/trained_model.h5')
        prediction = model.predict(img_array)
        disease_idx = np.argmax(prediction)
        disease_name = ['Disease1', 'Disease2', ...][disease_idx]  # Replace with actual disease names
        severity = float(np.max(prediction))

        # Simulate environmental data (replace with IoT integration)
        env_data = {'temperature': 25.0, 'humidity': 60.0}
        recommendations = generate_recommendations(disease_name, severity, env_data)

        diagnosis = CropDiagnosis.objects.create(
            user=request.user,
            image=image,
            disease_name=disease_name,
            severity=severity,
            plant_part='Leaf',  # Simplified; enhance with model output
            environmental_data=env_data,
            recommendations=recommendations
        )
        return redirect('results', diagnosis_id=diagnosis.id)
    return render(request, 'upload.html')

def generate_recommendations(disease_name, severity, env_data):
    # Logic for recommendations based on disease and environmental data
    return f"Recommended treatment for {disease_name}: Apply fungicide and monitor humidity."
```

4. **Django URLs (urls.py)**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('results/<int:diagnosis_id>/', views.results, name='results'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

5. **Template for Image Upload (upload.html)**

```html
{% extends 'base.html' %}
{% block content %}
<div class="max-w-md mx-auto p-4">
    <h1 class="text-2xl font-bold">Upload Crop Image</h1>
    <form method="post" enctype="multipart/form-data" class="mt-4">
        {% csrf_token %}
        <input type="file" name="crop_image" accept="image/*" class="border p-2 w-full">
        <button type="submit" class="bg-blue-500 text-white p-2 mt-2">Diagnose</button>
    </form>
</div>
{% endblock %}
```

6. **Visualization Example (dashboard.py)**

```python
import plotly.express as px
import pandas as pd
from django.shortcuts import render

def dashboard(request):
    diagnoses = CropDiagnosis.objects.filter(user=request.user)
    df = pd.DataFrame.from_records(diagnoses.values('disease_name', 'severity', 'diagnosis_date'))
    fig = px.scatter(df, x='diagnosis_date', y='severity', color='disease_name', title='Disease Trends')
    plot_html = fig.to_html(full_html=False)
    return render(request, 'dashboard.html', {'plot': plot_html})
```

### Implementation Best Practices
- **Modularity**: Separate CNN model training and Django web application logic for maintainability.
- **Security**: Use Django’s CSRF protection, HTTPS, and hashed passwords (NFR3–NFR5).
- **Performance**: Optimize image processing with efficient resizing and caching (NFR1–NFR2).
- **Usability**: Design intuitive interfaces with Tailwind CSS and multilingual support (NFR6).
- **Scalability**: Use PostgreSQL and Celery for handling concurrent users and asynchronous tasks (NFR2, NFR10).
- **Testing**: Test CNN model accuracy, API endpoints, and UI responsiveness.
- **Documentation**: Include detailed comments in code and a clear report structure.

### Risk Mitigation
- **Dataset Issues**: If the dataset from ryeko.org is incomplete, augment with open-source datasets (e.g., PlantVillage).
- **IoT Constraints**: Simulate IoT data with mock APIs to meet FR12–FR13.
- **Time Management**: Prioritize core features (user management, image diagnosis) and incrementally add analytics and IoT integration.
- **Performance Bottlenecks**: Profile and optimize image processing and model inference time.

### GitHub Repository
- Initialize repository with `.gitignore` for sensitive files (e.g., `trained_model.h5`, `settings.py` with secrets).
- Commit regularly with clear messages (e.g., “Add user authentication”, “Integrate CNN model”).
- Include `requirements.txt` for dependencies (e.g., `django`, `tensorflow`, `plotly`, `pandas`).

## Next Steps
1. Assign team roles (e.g., ML engineer, Django developer, UI designer, report writer).
2. Download and explore the dataset from https://ryeko.org/datasets/.
3. Set up the Django project and train the initial CNN model.
4. Schedule supervision session by July 10, 2025.
5. Iterate based on feedback and prepare for the presentation by July 17, 2025.