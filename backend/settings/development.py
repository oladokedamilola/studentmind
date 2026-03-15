"""
Development settings for StudentMind project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS += [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Disable HTTPS requirements in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Development-specific apps
# INSTALLED_APPS += [
#     'django_extensions',  # Optional: for better development tools
# ]

# More relaxed rate limiting for development
# REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
#     'anon': '1000/day',
# }

# Show emails in console instead of sending
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}