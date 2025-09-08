"""
Django settings for authentication project.

Updated for:
- DRF & JWT authentication
- Cloudinary media storage
- Email via Gmail SMTP
- OTP handling
- DRF Spectacular for API docs
- CORS handling
"""

from pathlib import Path
from datetime import timedelta
import os
from decouple import config, Csv
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl
load_dotenv()

# -------------------------------
# Base Directory
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# Security
# -------------------------------
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DJANGO_DEBUG', cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv())

# -------------------------------
# Applications
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',

    # Local apps
    'accounts',
    'rest_framework_simplejwt.token_blacklist',
]

# -------------------------------
# Middleware
# -------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # <-- CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------
# URLs & WSGI
# -------------------------------
ROOT_URLCONF = 'authentication.urls'

WSGI_APPLICATION = 'authentication.wsgi.application'

# -------------------------------
# Templates
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],  # add templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------------------
# Database
# -------------------------------
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# -------------------------------
# Authentication
# -------------------------------
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# -------------------------------
# Password validation
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# -------------------------------
# Internationalization
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# This is for development (your local static files)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# This is required for collectstatic in production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # <-- new

# Media files (uploads, profile photos, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# -------------------------------
# Cloudinary Storage
# -------------------------------
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config('CLOUDINARY_CLOUD_NAME'),
    "API_KEY": config('CLOUDINARY_API_KEY'),
    "API_SECRET": config('CLOUDINARY_API_SECRET')
}

# -------------------------------
# Email (Gmail SMTP)
# -------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Replace the DATABASES section of your settings.py with this
tmpPostgres = urlparse(config("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
        'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
    }
}

# -------------------------------
# OTP Secret
# -------------------------------
SITE_OTP_SECRET = config('SITE_OTP_SECRET')

# -------------------------------
# CORS
# -------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://api-test-291i.onrender.com"
]
CORS_ALLOW_ALL_ORIGINS = True

# -------------------------------
# DRF Spectacular
# -------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Authentication API",
    "DESCRIPTION": "API documentation for my authentication system",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Local Dev"},
        {"url": "https://api-test-291i.onrender.com", "description": "Production on Render"},
    ],
}


# -------------------------------
# Default primary key
# -------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
