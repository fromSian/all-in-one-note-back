from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [".vercel.app", ".now.sh"]
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://default:SsQIbNcE0hyl4porRqu6TRCGjaQ7Kl9s@redis-16325.c12.us-east-1-4.ec2.redns.redis-cloud.com:16325",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "DB": "cache-LYYW0G8F",
            "PASSWORD": os.environ.get("REDIS_PWD"),
        },
    }
}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres.hrcpfvwjbsrmgoaivjff",
        "PASSWORD": os.environ.get("PGSQL_PWD"),
        "HOST": "aws-0-ap-southeast-1.pooler.supabase.com",
        "PORT": "6543",
    }
}
