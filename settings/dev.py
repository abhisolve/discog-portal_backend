from .base import *
import os

ENV = "dev"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", 'alice']
DEBUG = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL ='/static/'

MEDIA_URL = '/media/'
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DISCOG_DEV_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_USER_PASSWORD')
    }
}

EMAIL_SUBJECT_PREFIX = ['DiscoGPortal  Support']
EMAIL_MAX_RETRIES = 3
BCC_EMAILS = []

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]
CKEDITOR_BASE_PATH = os.path.join(BASE_DIR, 'static/ckeditor/ckeditor/')

# we need this specific HOST variable that we use in email templates to link back to our website
# IMPORTANT DONT END THE URL WITH A SLASH
HOST = 'http://localhost:8001'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
FROM_EMAIL = "disco-dev@exiverprojects.com"
EMAIL_HOST = 'smtp.mailgun.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'postmaster@mg.exiverprojects.com'
EMAIL_HOST_PASSWORD = 'd3355741f5e735c31ce891244a4ca649-52b6835e-149823f6'
EMAIL_USE_TLS = True
