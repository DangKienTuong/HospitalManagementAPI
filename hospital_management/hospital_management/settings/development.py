"""
Development settings for Hospital Management System.
"""

from .base import *
import os

# SECURITY WARNING: Debug mode for development only
DEBUG = True

# SECURITY WARNING: Use environment variable in real deployment
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key-change-this-in-production')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '.localhost']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME', 'HospitalDB_Dev'),
        'USER': os.environ.get('DB_USER', 'sa'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'connection_timeout': 30,
        },
    }
}

# CORS Settings - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email Backend - Console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# Debug Toolbar Settings
INTERNAL_IPS = ['127.0.0.1', 'localhost']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_TEMPLATE_CONTEXT': True,
}

# Logging - More verbose in development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['core']['level'] = 'DEBUG'

# Cache - Use dummy cache in development
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
}

# File Upload Settings - Relaxed for development
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# Session Security - Relaxed for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development feature flags
FEATURES.update({
    'DEBUG_MODE': True,
    'ENABLE_PROFILING': True,
    'ENABLE_SQL_LOGGING': True,
})

print("=" * 50)
print("RUNNING IN DEVELOPMENT MODE")
print("=" * 50)
