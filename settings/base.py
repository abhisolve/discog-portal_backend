# -*- coding: utf-8 -*-

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')96#-&9!b2+8*&^9o+nzwh)zc0&a53jz33r8j3c8+p^)4_ti$n'
INTERNAL_IPS = ['127.0.0.1', ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',

    # third party apps
    'rest_framework',  # https://www.django-rest-framework.org/
    'django_extensions', # https://django-extensions.readthedocs.io/
    'ckeditor', # https://github.com/django-ckeditor/django-ckeditor
    'compressor', # https://django-compressor.readthedocs.io/
    'phonenumber_field', # https://github.com/stefanfoulis/django-phonenumber-field
    'simple_history', # https://django-simple-history.readthedocs.io/en/latest/index.html
    'debug_toolbar', # For debuging in development mode
    'drf_yasg', # API documentation
    'corsheaders', # https://pypi.org/project/django-cors-headers/

    # project based apps 
    'discoauth', # holds a custom user model
    'portal',
    'assignments', # holds majority of DB schema
    'contentmanager', # is used for creating modules and assignments
    'discomail', # handles the mail component
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware', # https://django-simple-history.readthedocs.io/en/latest/index.html
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'discogportal.urls'
AUTH_USER_MODEL = 'discoauth.DiscoUser'

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%d-%m-%Y %H:%M",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'portal.context_processor.uicontext'
            ],
        },
    },
]

WSGI_APPLICATION = 'discogportal.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },
}
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False
LOGIN_URL = '/auth/login'
SENDER_MAIL = 'discogdev@exiverprojects.com'


from datetime import timedelta

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=1),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(seconds=1),
}
