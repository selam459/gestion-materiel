"""
Django settings for gestion_materiel project.
Monnaie : MRU (Ouguiya mauritanienne)
"""

from pathlib import Path
import os
import dj_database_url  # 👈 Ajout pour Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$7tnb36y_j-@9mv(vr5*0!l6=euht8(#3#8)j-rbz#mcu-3xv_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Sera sécurisé via la variable d'env sur Render

# ===========================
# 📦 APPLICATIONS INSTALLÉES
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Doit être avant staticfiles
    'django.contrib.staticfiles',
    'stock',                           # Votre application
    'django_extensions',
]

# ===========================
# 🔄 MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Après SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_materiel.urls'

# ===========================
# 🎨 TEMPLATES
# ===========================
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
                'stock.context_processors.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_materiel.wsgi.application'

# ===========================
# 🗄️ BASE DE DONNÉES
# ===========================
# Configuration pour Render (PostgreSQL) avec fallback SQLite en local
import os
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

import os  # ← En haut du fichier
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),  # ← Lecture de la variable Render
        conn_max_age=600,
        conn_health_checks=True,
    )
}

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ===========================
# 🔐 VALIDATION DES MOTS DE PASSE
# ===========================
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

# ===========================
# 🔐 AUTHENTIFICATION & URLS (AVEC NAMESPACE)
# ===========================
LOGIN_URL = 'stock:login'
LOGIN_REDIRECT_URL = 'stock:dashboard'
LOGOUT_REDIRECT_URL = 'stock:login'

# Nom du cookie de session (optionnel)
SESSION_COOKIE_NAME = 'gestion_mru_session'

# ===========================
# 🌍 INTERNATIONALISATION
# ===========================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Nouakchott'
USE_I18N = True
USE_TZ = True

# ===========================
# 📁 FICHIERS STATIQUES & MEDIA
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Dossier statique local
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     # Collecte des fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # 👈 Déplacé ici

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===========================
# 📢 MESSAGES FRAMEWORK
# ===========================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ===========================
# ⚙️ AUTRES PARAMÈTRES
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'