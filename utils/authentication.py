from rest_framework_simplejwt.authentication import JWTAuthentication

from django.core.cache import cache

from rest_framework_simplejwt.exceptions import InvalidToken


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
        email = user.email
        token = cache.get(email)
        if token == raw_token.decode("utf-8"):
            return user, validated_token
        else:
            raise InvalidToken()
