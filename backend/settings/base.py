"""
Base settings for StudentMind project.
This file contains settings common to all environments.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

# Load environment variables
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-change-in-production')

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    # 'corsheaders',
    
    # Local apps (to be created)
    'apps.accounts',
    'apps.chat',
    'apps.openai_integration',
    'apps.emergency',
    'apps.resources',
    'apps.university',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/css',
    BASE_DIR / 'frontend/js',
    BASE_DIR / 'frontend/images',
]
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Will change to session-based later
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',  # Rate limiting for anonymous users
    }
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# OpenAI settings (to be configured)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = 'gpt-3.5-turbo'  # Default model

# Session settings (for anonymous users)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True

# Encryption settings (for sensitive data)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', None)  # Will be generated if None

# GitHub Models (Microsoft Foundry) settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
AZURE_INFERENCE_ENDPOINT = os.getenv('AZURE_INFERENCE_ENDPOINT', 'https://models.github.ai/inference')
AZURE_MODEL_NAME = os.getenv('AZURE_MODEL_NAME', 'gpt-4o')

# Validate GitHub token is present
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")