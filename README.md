
# FloraSight - AI-Powered Crop Disease Detection

A comprehensive Django web application for crop disease detection using artificial intelligence, designed for farmers, agronomists, and agricultural professionals.

---

## 🌱 Features

- **AI-Powered Disease Detection**: Upload crop images for instant disease analysis
- **User Management**: Registration, authentication, and user profiles
- **Dashboard Analytics**: Comprehensive statistics and insights
- **Diagnosis History**: Track all previous diagnoses and results
- **Responsive Design**: Mobile-friendly interface with Bootstrap
- **Admin Interface**: Complete Django admin for data management
- **API Endpoints**: RESTful APIs for ML model integration
- **IoT Integration**: Support for environmental sensor data
- **Local HTTPS Support**: Run securely in development with self-signed certificates

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- OpenSSL (for HTTPS dev support)

### Installation

1. **Clone the project**

   ```bash
   git clone https://github.com/your-username/FloraSight.git
   cd CropDisease-GroupL/project
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scriptsctivate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your `SECRET_KEY`, `DEBUG`, and other values.

5. **Apply migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **(Optional) Generate SSL Certificates for HTTPS (Development Only)**

   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

   > Place both `key.pem` and `cert.pem` in the `project/` directory (same level as `manage.py`).

8. **Start the development server with HTTPS**

   ```bash
   python manage.py runserver_plus --cert-file cert.pem --key-file key.pem 8080
   ```

9. **Access the application**

   - Site: https://127.0.0.1:8080/
   - Admin panel: https://127.0.0.1:8080/admin

   > You may see a security warning due to self-signed certs. Click "Advanced" → "Proceed".

---

## 📁 Project Structure

```
CropDisease-GroupL/
├── chatbot_backend/
│   ├── agronova.py
│   └── chat_requirements.txt
└── project/
    ├── chatbot/                 # Chatbot app
    ├── crops/                   # Core app
    ├── florasight/              # Django project settings
    ├── ml_models/               # ML model files (Keras, config)
    ├── static/                  # CSS and JS assets
    ├── templates/               # HTML templates (auth + app)
    ├── cert.pem                 # Dev SSL certificate (DO NOT COMMIT)
    ├── key.pem                  # Dev SSL key (DO NOT COMMIT)
    ├── manage.py
    ├── requirements.txt
    └── README.md
```

---

## 🔧 Configuration

### Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

### Database (default: SQLite)

To use PostgreSQL:

```python
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

---

## 📊 Core Models

- **UserProfile**: Extended user info (type, location, etc.)
- **CropType**: Types of crops (wheat, corn, etc.)
- **Disease**: Disease name, symptoms, treatment
- **Diagnosis**: Image + prediction
- **Recommendation**: Based on diagnosis
- **IoTDevice**: Registered sensor device
- **IoTReading**: Sensor data (temperature, humidity, etc.)

---

## 🎨 Frontend

- **Bootstrap 5**
- **Font Awesome**
- **Custom CSS/JS**
- **AJAX interactions**

---

## 🔌 API Endpoints

### ML Integration

- `POST /api/process-image/`: Submit image for prediction
- `POST /api/iot-data/`: Submit environmental data

### Authentication

- `/auth/login/`, `/auth/logout/`, `/register/`

---

## 👥 User Roles

- **Farmer**: Upload crops, view results
- **Agronomist**: Expert users with advanced tools
- **Extension Worker**: Agricultural extension services

---

## 🛠️ Development Tips

### Add a Feature

1. Add models in `crops/models.py`
2. Add views in `crops/views.py`
3. Define URL paths in `crops/urls.py`
4. Create templates in `templates/crops/`
5. Apply migrations: `python manage.py makemigrations && migrate`

### Static Files

```bash
python manage.py collectstatic
```

### Testing

```bash
python manage.py test
```

---

## 🚀 Deployment (Production)

1. Set `DEBUG=False`
2. Add `ALLOWED_HOSTS` in `settings.py`
3. Use PostgreSQL instead of SQLite
4. Set up Nginx + Gunicorn + HTTPS (Let’s Encrypt)
5. Collect static files with `collectstatic`

Example `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

STATIC_ROOT = '/var/www/florasight/static/'
MEDIA_ROOT = '/var/www/florasight/media/'
```

---

## 📝 Usage Guide

1. Register or log in
2. Upload a crop image
3. View diagnosis results
4. Get AI-powered recommendations
5. Track your history

---

## 🤝 Contributing

1. Fork this repo
2. Create a feature branch
3. Commit and push your changes
4. Open a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

- Create an issue for bugs
- Contact the dev team
- Contribute to documentation
- PRs welcome ❤️

---

## 🔮 Future Roadmap

- [ ] Android mobile app
- [ ] Real-time weather integration
- [ ] Crop yield prediction
- [ ] ML model improvements
- [ ] Multi-language support
- [ ] Social features for farmers

---

**FloraSight** – Revolutionizing agriculture through AI 🌱
