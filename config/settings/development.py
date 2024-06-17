from .base import *


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

GOOGLE_OAUTH2_REDIRECT_SUCCESS_URL = "http://localhost:5173/google/success/"
GOOGLE_OAUTH2_REDIRECT_FAIL_URL = "http://localhost:5173/error/google/fail/"
