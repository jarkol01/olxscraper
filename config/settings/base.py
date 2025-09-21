import os
from os import environ
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]
CSRF_TRUSTED_ORIGINS = []

# Application definition

PROJECT_NAME = "olxscraper"

BASE_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
]

THIRD_PARTY_APPS = [
    "webpush",
    "django_celery_beat",
    "pwa",
    "debug_toolbar",
]

LOCAL_APPS = [
    "searches",
    "notifications",
]
LOCAL_APPS = [f"{PROJECT_NAME}.{app}" for app in LOCAL_APPS]

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / PROJECT_NAME / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Warsaw"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/tmp/debug.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file", "console"],
            "level": "WARNING",  # DEBUG will log all queries, so change it to WARNING.
            "propagate": False,  # Don't propagate to other handlers
        },
        "django.utils.autoreload": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": os.getenv("VAPID_PUBLIC_KEY"),
    "VAPID_PRIVATE_KEY": os.getenv("VAPID_PRIVATE_KEY"),
    "VAPID_ADMIN_EMAIL": os.getenv("VAPID_ADMIN_EMAIL"),
}

DEFAULT_GROUP_NAME = "all"

# Celery settings
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_URL = environ.get(
    "CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672/vhost"
)

# PWA settings
PWA_APP_NAME = "OlxScraper"
PWA_APP_DESCRIPTION = "Monitor OLX listings and get notifications for new items matching your search criteria"
PWA_APP_THEME_COLOR = "#007bff"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "portrait-primary"
PWA_APP_START_URL = "/"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_APP_ICONS = [
    {
        "src": "/static/images/logo.png",
        "sizes": "512x512",
        "type": "image/png",
    },
    {
        "src": "/static/images/icon-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
    },
    {
        "src": "/static/images/icon-96x96.png",
        "sizes": "96x96",
        "type": "image/png",
    },
]
PWA_APP_ICONS_APPLE = [
    {
        "src": "/static/images/apple-touch-icon.png",
        "sizes": "180x180",
        "type": "image/png",
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/images/splash-640x1136.png",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "pl-PL"
PWA_APP_SHORTCUTS = [
    {
        "name": "Admin Panel",
        "url": "/admin/",
        "description": "Access the administration panel",
    }
]

def custom_show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

UNFOLD = {
    "SITE_TITLE": "OlxScraper Admin",
    "SITE_HEADER": "OlxScraper",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": "/static/images/logo.png",
        "dark": "/static/images/logo.png",
    },
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "olxscraper.utils.environment.environment_callback",
    "DASHBOARD_CALLBACK": "olxscraper.utils.dashboard.dashboard_callback",
    "THEME": "dark",
    "LOGIN": {
        "image": "/static/images/logo.png",
        "redirect_after": "/admin/",
    },
    "STYLES": [
        lambda request: "/static/css/style.css",
    ],
    "SCRIPTS": [],
    "COMMANDS": {
        "search_models": True,
    },
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255", 
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "196 181 253",
            "500": "147 51 234",
            "600": "124 58 237",
            "700": "109 40 217",
            "800": "91 33 182",
            "900": "76 29 149",
            "950": "46 16 101"
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": "/admin/",
                    },
                    {
                        "title": "Latest Items", 
                        "icon": "new_releases",
                        "link": "/admin/searches/item/?o=-4",
                    },
                    {
                        "title": "Categories",
                        "icon": "category", 
                        "link": "/admin/searches/category/",
                    },
                ],
            },
            {
                "title": "Search Management",
                "separator": True,
                "items": [
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/searches/category/",
                    },
                    {
                        "title": "Searches",
                        "icon": "search",
                        "link": "/admin/searches/search/",
                    },
                ],
            },
            {
                "title": "Items & Results",
                "separator": True, 
                "items": [
                    {
                        "title": "Items",
                        "icon": "inventory_2",
                        "link": "/admin/searches/item/",
                    },
                    {
                        "title": "Item Updates",
                        "icon": "update",
                        "link": "/admin/searches/itemupdate/",
                    },
                ],
            },
            {
                "title": "System",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                    {
                        "title": "Periodic Tasks",
                        "icon": "schedule",
                        "link": "/admin/django_celery_beat/periodictask/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "searches.category",
                "searches.search", 
            ],
            "items": [
                {
                    "title": "Categories",
                    "link": "/admin/searches/category/",
                },
                {
                    "title": "Searches",
                    "link": "/admin/searches/search/",
                },
            ],
        },
        {
            "models": [
                "searches.item",
                "searches.itemupdate",
            ],
            "items": [
                {
                    "title": "Items", 
                    "link": "/admin/searches/item/",
                },
                {
                    "title": "Updates",
                    "link": "/admin/searches/itemupdate/",
                },
            ],
        },
    ],
}
