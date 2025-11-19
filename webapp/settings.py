from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv  # ✅ add this

# Load environment variables from .env (must come before using them)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # ✅ add this


def get_env(name: str, default: str | None = None, *, required: bool = False) -> str | None:
    """Read environment variables and error when required ones are missing."""
    value = os.environ.get(name, default)
    if required and value in (None, ""):
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "dev-secret-change-me")  # ✅ change this line
DEBUG = get_env("DJANGO_DEBUG", "True") == "True"  # ✅ change this line

# Allowed hosts & CSRF (Render uses onrender.com)
ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost,http://127.0.0.1,https://*.onrender.com"
).split(",")

# If behind a proxy (Render), honor X-Forwarded-Proto for HTTPS detection
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # ✅ add this (our app)
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

ROOT_URLCONF = 'webapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # we’ll add template folders later
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webapp.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


STATIC_URL = 'static/'  # ✅ keep or add this
STATIC_ROOT = BASE_DIR / 'staticfiles'  # ✅ add for deployment later

# Store sessions in signed cookies (no database table needed)
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = get_env("DJANGO_DEBUG", "True") != "True"  # Only secure in production

# Supabase configuration
SUPABASE_URL = get_env("SUPABASE_URL", required=True)
SUPABASE_ANON_KEY = get_env("SUPABASE_ANON_KEY", required=True)
SUPABASE_SERVICE_ROLE_KEY = get_env("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_CLIENT = None

if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client, Client

        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as exc:  # pragma: no cover - import/setup guard
        import logging

        logging.getLogger(__name__).warning("Supabase client failed to initialize: %s", exc)