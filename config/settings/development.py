from .base import *

DEBUG = True

ALLOWED_HOSTS = []
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

GOOGLE_OAUTH2_REDIRECT_SUCCESS_URL = "http://localhost:5173/google-success/"
GOOGLE_OAUTH2_REDIRECT_FAIL_URL = "http://localhost:5173/google-fail/"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "notetodos",
#         "USER": "postgres",
#         "PASSWORD": "123456",
#         "HOST": "127.0.0.1",
#         "PORT": "5432",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


BASE_BACKEND_URL = "http://localhost:8000/"
