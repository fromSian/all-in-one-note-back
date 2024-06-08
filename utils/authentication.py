from rest_framework_simplejwt.authentication import JWTAuthentication

from django.core.cache import cache

from rest_framework_simplejwt.exceptions import InvalidToken

from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime


class RedisJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        try:
            email = user[0].email
            token = cache.get(email)
            if token == raw_token.decode("utf-8"):
                return user
            else:
                raise InvalidToken()
        except Exception as e:
            raise InvalidToken(e)


def check_operation_validation(expire_time, action_time):
    """
    check if the operation is valid
    for change pasword or email...

    expire_time and action_time need to be encrypted
    """
    datetime_timezone_format = getattr(
        settings, "DATETIME_TIMEZONE_FORMAT", "%Y-%m-%d %H:%M:%S %z"
    )
    if expire_time is None or action_time is None:
        raise Exception("expire_time and action_time must not be blank")

    now = timezone.now()
    expire = datetime.strptime(expire_time, datetime_timezone_format)
    print(now, expire)
    if expire < now:
        raise Exception("operation passkey already expired")

    action = datetime.strptime(action_time, datetime_timezone_format)
    if action < now - timedelta(seconds=10):
        raise Exception("action timeout")
