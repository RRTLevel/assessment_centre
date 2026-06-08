import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the debug settings and UI theme from .env
DEBUG = os.getenv("DEBUG", default='False').lower() == 'true'

# Keep the secret key used in production secret
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", default=get_random_secret_key())

# Set the application Name, Version and Environment
APPLICATION_NAME = "Django Template"
APPLICATION_VERSION = "0.0.1"
APPLICATION_ENVIRONMENT = os.getenv("APPLICATION_ENVIRONMENT", default="local")

# A list representing the host/domain names to serve to
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'app_src',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'bulma',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app_site.urls'

# Define templates and context processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app_src.contexts.applicationNameContext',
                'app_src.contexts.applicationVersionContext',
                'app_src.contexts.applicationEnvironmentContext'
            ],
        },
    },
]

WSGI_APPLICATION = 'app_site.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Define a database cache table
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'notes_cache',
    }
}

# Define where logs should be written to
LOG_FOLDER = os.path.join(BASE_DIR.parents[0], "log")

# Define logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'fileformatter': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'log/app.log',
            'formatter': 'fileformatter',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


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
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

# Authentication tries SSO, then LDAP, then local users.
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGOUT_REDIRECT_URL = '/'

EMAIL_FROM = os.getenv("EMAIL_FROM")
SERVER_EMAIL = EMAIL_FROM   
