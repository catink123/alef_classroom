"""
Production settings for Alef Classroom.
Inherits from base settings but with production-specific overrides.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in project root
# Check both the alef_classroom directory and the parent directory
env_path = BASE_DIR / '.env'
if not env_path.exists():
    env_path = BASE_DIR.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import all base settings
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# For development/testing with production settings, serve static files
# In real production, use a web server (nginx/Apache) to serve static files
SERVE_STATIC_FILES = os.environ.get('SERVE_STATIC_FILES', 'False').lower() == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-dev')

# Allowed hosts - properly parse from environment variable
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '').strip()
if allowed_hosts_env:
    hosts = []
    for host in allowed_hosts_env.replace(',', ' ').split():
        host = host.strip()
        if host:
            if ':' in host:
                host = host.split(':')[0]
            hosts.append(host)
    ALLOWED_HOSTS = hosts if hosts else ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - Use SQLite for all environments
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS settings (uncomment when using HTTPS)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Cache configuration - use database cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Session configuration - use database sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# WhiteNoise configuration for serving static files in production
# This allows Django to serve static files without a separate web server
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
