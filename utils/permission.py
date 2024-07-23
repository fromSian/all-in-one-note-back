from rest_framework import permissions


from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.utils.dateparse import parse_datetime
from .encryption import RSAEncryption


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
        # raise Exception("expire_time and action_time must not be blank")
        return False
    now = timezone.now()
    expire = datetime.strptime(expire_time, datetime_timezone_format)
    if expire < now:
        # raise Exception("operation passkey already expired")
        return False

    action = datetime.strptime(action_time, datetime_timezone_format)
    if action < now - timedelta(seconds=10):
        # raise Exception("action timeout")
        return False
    return True


def check_valid(action_time):
    if not action_time.isdigit():
        return False
    now = datetime.now().timestamp()
    action = int(action_time) / 1000.0

    if action < now - 10:
        return False
    return True


class RequestValidPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
        action_time = request.query_params.get("action_time")
        if not action_time:
            return False
        encrypt = RSAEncryption()
        action = encrypt.decrypt(action_time)

        return check_valid(action)
