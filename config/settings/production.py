from .base import *
import os

DEBUG = False


ALLOWED_HOSTS = [
    ".localhost",
    "127.0.0.1",
    "fromsian.pythonanywhere.com",
    ".vercel.app",
    ".now.sh",
    "main--bemarkdownnotes.netlify.app",
    "bemarkdownnotes.netlify.app",
]

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
# DATABASES = {
#     "default": {
#         "ENGINE": "djongo",
#         "NAME": "notetodos",
#         "ENFORCE_SCHEMA": False,
#         "CLIENT": {
#             "host": "mongodb+srv://fromsian:{0}@cluster0.yvbadfb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(
#                 os.environ.get("MONGODB_PWD")
#             ),
#             "port": 27017,
#             "username": "fromsian",
#             "password": os.environ.get("MONGODB_PWD"),
#             "authSource": "notetodos",
#             "authMechanism": "SCRAM-SHA-1",
#         },
#     }
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


GOOGLE_OAUTH2_REDIRECT_SUCCESS_URL = (
    "https://bemarkdownnotes.netlify.app/google-success/"
)
GOOGLE_OAUTH2_REDIRECT_FAIL_URL = "https://bemarkdownnotes.netlify.app/google-fail/"


BASE_BACKEND_URL = "https://fromsian.pythonanywhere.com/"
