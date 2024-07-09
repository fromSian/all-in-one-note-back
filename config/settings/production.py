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


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres.xesbgjafrslmhbctfhnl",
        "PASSWORD": "SotoNote0530001",
        "HOST": "aws-0-ap-southeast-1.pooler.supabase.com",
        "PORT": "6543",
    }
}
