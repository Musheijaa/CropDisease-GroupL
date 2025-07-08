# FloraSight - AI-Powered Crop Disease Detection

A comprehensive Django web application for crop disease detection using artificial intelligence, designed for farmers, agronomists, and agricultural professionals.

## 🌱 Features

- **AI-Powered Disease Detection**: Upload crop images for instant disease analysis
- **User Management**: Registration, authentication, and user profiles
- **Dashboard Analytics**: Comprehensive statistics and insights
- **Diagnosis History**: Track all previous diagnoses and results
- **Responsive Design**: Mobile-friendly interface with Bootstrap
- **Admin Interface**: Complete Django admin for data management
- **API Endpoints**: RESTful APIs for ML model integration
- **IoT Integration**: Support for environmental sensor data

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Clone or download the project files**

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `SECRET_KEY`

5. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser account**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## 📁 Project Structure

```
florasight/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # Project documentation
├── florasight/              # Main project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── crops/                   # Main application
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Django forms
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # App URL patterns
│   ├── apps.py              # App configuration
│   └── migrations/          # Database migrations
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── crops/               # App-specific templates
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   ├── diagnosis_detail.html
│   │   ├── diagnosis_history.html
│   │   └── profile.html
│   └── registration/        # Authentication templates
│       ├── login.html
│       └── register.html
├── static/                  # Static files
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # Custom JavaScript
└── media/                   # User uploaded files
    └── crop_images/         # Uploaded crop images
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Database Setup

The project uses SQLite by default. For production, consider PostgreSQL:

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'florasight',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Models

### Core Models

- **UserProfile**: Extended user information (location, farm size, user type)
- **CropType**: Different types of crops (wheat, corn, tomato, etc.)
- **Disease**: Crop diseases with symptoms and treatments
- **Diagnosis**: Image analysis results with ML predictions
- **Recommendation**: Treatment recommendations for diagnosed diseases
- **IoTDevice**: Connected sensor devices
- **IoTReading**: Environmental sensor data

## 🎨 Frontend

- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icon library
- **Custom CSS**: Modern design with green theme
- **JavaScript**: Interactive features and AJAX

## 🔌 API Endpoints

### ML Integration

- `POST /api/process-image/`: Process uploaded images
- `POST /api/iot-data/`: Receive IoT sensor data

### Authentication

- `/auth/login/`: User login
- `/auth/logout/`: User logout
- `/register/`: User registration

## 👥 User Types

- **Farmer**: Basic users who upload crop images
- **Agronomist**: Agricultural experts with advanced features
- **Extension Worker**: Agricultural extension officers

## 🛠️ Development

### Adding New Features

1. **Models**: Add to `crops/models.py`
2. **Views**: Add to `crops/views.py`
3. **URLs**: Update `crops/urls.py`
4. **Templates**: Create in `templates/crops/`
5. **Migrations**: Run `python manage.py makemigrations`

### Testing

```bash
python manage.py test
```

### Static Files

```bash
python manage.py collectstatic
```

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False`
2. Configure allowed hosts
3. Set up proper database
4. Configure static file serving
5. Set up email backend

### Example Production Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'florasight_prod',
        'USER': 'florasight_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = '/var/www/florasight/static/'
MEDIA_ROOT = '/var/www/florasight/media/'
```

## 📝 Usage

1. **Register**: Create a new account
2. **Login**: Access your dashboard
3. **Upload Image**: Take/upload a crop photo
4. **Get Results**: View AI analysis and recommendations
5. **Track History**: Monitor all your diagnoses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Create an issue for bugs
- Contact the development team

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced ML model integration
- [ ] Real-time IoT dashboard
- [ ] Multi-language support
- [ ] Weather data integration
- [ ] Crop yield prediction
- [ ] Social features for farmers

---

**FloraSight** - Transforming agriculture through AI-powered crop disease detection 🌱