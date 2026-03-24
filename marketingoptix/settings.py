"""
Django settings for marketingoptix project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-f777^c!7ok4sl^iqh=%b^fotgds_a#x2b07*3u3=wwo)q6m=sk')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# APPLICATIONS
INSTALLED_APPS = [

    # Modern Admin UI
    "jazzmin",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'user',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'marketingoptix.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'user/templates'],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'user.context_processors.unread_counts',
            ],
        },
    },
]


WSGI_APPLICATION = 'marketingoptix.wsgi.application'


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Update database configuration from $DATABASE_URL.
if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)


# PASSWORD VALIDATION
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


# LANGUAGE
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "user/static"
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------------------------
# JAZZMIN ADMIN UI SETTINGS (Professional UI)
# ------------------------------------------------

JAZZMIN_SETTINGS = {

    "site_title": "MarketingOptix Admin",

    "site_header": "MarketingOptix",

    "site_brand": "MarketingOptix Dashboard",

    "welcome_sign": "Welcome to MarketingOptix Admin",

    "copyright": "MarketingOptix Ltd",

    "search_model": ["auth.User"],

    "show_sidebar": True,

    "navigation_expanded": True,

    "icons": {

        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",

        "user.user": "fas fa-user",
        "user.project": "fas fa-briefcase",
        "user.category": "fas fa-list",
        "user.review": "fas fa-star",

    },

}


JAZZMIN_UI_TWEAKS = {

    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,

    "brand_colour": "navbar-dark",

    "accent": "accent-info",

    "navbar": "navbar-dark",

    "navbar_fixed": True,

    "sidebar": "sidebar-dark-primary",

    "sidebar_fixed": True,

    "sidebar_nav_compact_style": True,

    "theme": "darkly",

    "dark_mode_theme": "darkly",

}