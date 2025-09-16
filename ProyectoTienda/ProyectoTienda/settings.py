from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-insecure-change-me'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'AppTienda',
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

ROOT_URLCONF = 'ProyectoTienda.urls'

TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR / 'AppTienda' / 'templates'],
    'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'ProyectoTienda.wsgi.application'

DATABASES = {
    'default': {'ENGINE':'django.db.backends.sqlite3','NAME': BASE_DIR / 'db.sqlite3'}
    # MySQL (opcional):
    # 'default': {
    #   'ENGINE':'django.db.backends.mysql',
    #   'NAME':'posdb','USER':'root','PASSWORD':'','HOST':'127.0.0.1','PORT':'3306',
    #   'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
    # }
}

AUTH_USER_MODEL = 'AppTienda.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'AppTienda.validators.PasswordComplexityValidator'},
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = []
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Dominios de correo corporativo permitidos
CORPORATE_EMAIL_DOMAINS = ['company.com']  # cámbialo a tu dominio
