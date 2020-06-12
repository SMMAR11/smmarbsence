"""
Django settings for smmarbsence project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

# Imports
from decouple import config
from decouple import Csv
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast = bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast = Csv())


# Application definition

INSTALLED_APPS = [
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jquery'
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

ROOT_URLCONF = 'smmarbsence.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                #'app.context_processors.get_alert',
                'app.context_processors.get_donn',
                'app.context_processors.get_mess',
                'app.context_processors.init_fm_perm',
                'app.context_processors.init_menus',
                'app.context_processors.set_tasks',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smmarbsence.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER' : config('DB_USER'),
        'PASSWORD' : config('DB_PASSWORD'),
        'HOST' : config('DB_HOST'),
        'PORT' : ''
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Paramètres personnalisés
CF_EMPTY_VALUE = (None, '---------')
ERROR_MESSAGES = {
    'invalid' : 'Veuillez renseigner une valeur valide.',
    'invalid_choice' : 'Veuillez rensigner une valeur valide.',
    'required' : 'Veuillez renseigner une valeur.'
}

USER_STATUS = [
    { 'us' : 100, 'c_max' : 32, 'r_max' : 26 },
    { 'us' : 90, 'c_max' : 29.5, 'r_max' : 23 },
    { 'us' : 80, 'c_max' : 27, 'r_max' : 21 },
    { 'us' : 70, 'c_max' : 24.5, 'r_max' : 18 },
    { 'us' : 60, 'c_max' : 22, 'r_max' : 16 },
    { 'us' : 50, 'c_max' : 19.5, 'r_max' : 13 }
]

ADMINS = [(
    '{0} {1}'.format(config('MAIN_ACCOUNT_FIRSTNAME'), config('MAIN_ACCOUNT_LASTNAME')),
    config('MAIN_ACCOUNT_EMAIL')
)]
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'mail_dumps')

DB_PK_DATAS = {
    'C_PK' : config('C_PK', cast = int),
    'CET_PK' : config('CET_PK', cast = int),
    'RTT_PK' : config('RTT_PK', cast = int)
}

#RTT_QUOTAS = [2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2]
RTT_QUOTAS = config('RTT_QUOTAS', cast = Csv(int))

SMMAR_YEAR_CREATION = 2003

CAN_SEND_EMAILS = config('CAN_SEND_EMAILS', cast = bool)