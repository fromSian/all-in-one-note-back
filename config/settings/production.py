from .base import *

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis-17938.c56.east-us.azure.redns.redis-cloud.com:17938",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DB": "cache-LX0NU332",
            "PASSWORD": "MsKFFHE4r8Yiu0C7ldOi6JV7AAcBLUUs",
        },
    }
}