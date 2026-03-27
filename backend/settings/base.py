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
    'apps.mood',
    'apps.assessment',
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
    BASE_DIR / 'frontend',  # Your frontend folder with css, js, images
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# For serving manifest.json and service-worker.js correctly
WHITENOISE_ROOT = BASE_DIR / 'frontend'  # whitenoise in production

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
# Generate a fixed key for production. For development, you can generate one:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY_STRING = os.getenv('ENCRYPTION_KEY', None)

# Store as bytes for the cipher
ENCRYPTION_KEY = None
if ENCRYPTION_KEY_STRING:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STRING.encode()
    
# If no key is provided in .env, log a warning
if not ENCRYPTION_KEY:
    import warnings
    warnings.warn("ENCRYPTION_KEY not set in environment variables. Messages may not be decryptable after server restart.")
    
    
# GitHub Models (Microsoft Foundry) settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
AZURE_INFERENCE_ENDPOINT = os.getenv('AZURE_INFERENCE_ENDPOINT', 'https://models.github.ai/inference')
AZURE_MODEL_NAME = os.getenv('AZURE_MODEL_NAME', 'gpt-4o')

# Validate GitHub token is present
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")


# Email Configuration
EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('DJANGO_EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'MindHaven <noreply@mindhaven.com>')

# Add these for better email debugging
EMAIL_TIMEOUT = 30  # seconds
EMAIL_USE_LOCALTIME = True

# Site URL for email links (important for verification emails)
SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')

# Session Settings
SESSION_ENGINE = os.getenv('SESSION_ENGINE', 'django.contrib.sessions.backends.db')
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 86400))  # 24 hours default
SESSION_SAVE_EVERY_REQUEST = os.getenv('SESSION_SAVE_EVERY_REQUEST', 'True').lower() in ('true', '1', 't')
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.getenv('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'False').lower() in ('true', '1', 't')  # Default False now

# Optional: Make sessions more secure
SESSION_COOKIE_SECURE = False  # Default to False, override in production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Token Expiry Times
OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 1))
# Email verification token expiry (uses the same pattern)
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = int(os.getenv('EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS', 24))

# Rate Limiting Settings
RATE_LIMIT_MAX_ATTEMPTS = 3
RATE_LIMIT_BLOCK_HOURS = 1
RATE_LIMIT_WINDOW_HOURS = 1  # Time window before counter resets
