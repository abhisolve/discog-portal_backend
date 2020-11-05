# -*- coding: utf-8 -*-

import os
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import dj_database_url
import django_heroku


ENV = "sandbox"
DEBUG = False
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },
}

CORS_ORIGIN_ALLOW_ALL = True
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}

if os.environ.get('SENTRY_DSN', None):
    # if sentry DSN is provided in the settings
    # file we will use that DSN. Otherwise we will
    # not use this setting and no stack trace will
    # we sent to sentry in such case
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )
else:
    # sentry DSN doen't exists in the environment
    # variables. don't do anything just pass.
    pass


if os.environ.get('DJANGO_ALLOWED_HOSTS', None) is not None:
    # we will only use those hosts which are set in
    # the environment variables otherwise we will
    # set up ALLLOWED_HOSTS to match the localhost.
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1',]


# static and media file settings
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]



# environment specific settings
# AWS on heroku and local database settings
# in both heroku, docker and others.
if os.environ.get("PLATFORM", None) == "heroku":
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    
    
    AWS_STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
    

    AWS_MEDIA_LOCATION= 'media'
    MEDIA_URL  = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

    DEFAULT_FILE_STORAGE = 'discogportal.discostorages.MediaStorage'
    STATICFILES_STORAGE = 'discogportal.discostorages.StaticStorage'
    
    # Database settings will be generated using
    # the environment variable in heroku used to store
    # the HerokuPostgrs dynmo settings. Check the heroku
    # dashboard application setting for config variables.
    DATABASES = {
        'default': dj_database_url.config()
    }

    # Activate Django-heroku settings except
    # for logging
    django_heroku.settings(locals(), logging=False, staticfiles=False)

else:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('SQL_DATABASE'),
            'USER': os.environ.get('SQL_USER'),
            'PASSWORD': os.environ.get('SQL_PASSWORD'),
            'HOST': os.environ.get('SQL_HOST'),
            'PORT': os.environ.get('SQL_PORT')
        }
    }


CKEDITOR_BASE_PATH = STATIC_URL + 'ckeditor/ckeditor/'

# we need this specific HOST variable that we use in email templates to link back to our website
# IMPORTANT DONT END THE URL WITH A SLASH
HOST = 'https://discog-sandbox.exiverprojects.com'

#Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
FROM_EMAIL = "discogsandbox@exiverprojects.com"
BCC_EMAILS = []
EMAIL_HOST = 'smtp.mailgun.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'postmaster@mg.exiverprojects.com'
EMAIL_HOST_PASSWORD = 'd3355741f5e735c31ce891244a4ca649-52b6835e-149823f6'
EMAIL_USE_TLS = True
