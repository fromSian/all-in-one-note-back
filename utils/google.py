from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from attrs import define


@define
class GoogleRawLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env")

    credentials = GoogleRawLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id,
    )
    return credentials


from random import SystemRandom
from urllib.parse import urlencode
from django.urls import reverse_lazy
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
import jwt
import requests


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str

    def decode_id_token(self) -> dict[str, str]:
        id_token = self.id_token
        decoded_tokem = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_tokem


class GoogleRawLoginFlowService:
    API_URI = "account/google/callback"

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        # "https://www.googleapis.com/auth/userinfo.email",
        # "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self) -> None:
        self._credentials = google_raw_login_get_credentials()

    def _generate_state_session_token(
        self, length=30, chars=UNICODE_ASCII_CHARACTER_SET
    ):
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()
        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": "".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }
        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()
        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise Exception("Failed to obtain access token from Google")

        tokens = response.json()
        google_tokens = GoogleAccessTokens(
            id_token=tokens["id_token"],
            access_token=tokens["access_token"],
        )

        return google_tokens

    def get_user_info(self, *, google_tokens: GoogleAccessTokens):
        access_token = google_tokens.access_token
        response = requests.get(
            self.GOOGLE_USER_INFO_URL, params={"access_token": access_token}
        )

        if not response.ok:
            raise Exception("Failed to obtain user info from Google")

        return response.json()


from rest_framework.views import APIView
from django.shortcuts import redirect


class GoogleLoginAccessView(APIView):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


from rest_framework import status, serializers
from rest_framework.response import Response
from datetime import datetime
from account.views import login_token_logic
from account.serializers import UserSerializer
from account.models import User
from rest_framework.exceptions import ValidationError


class GoogleLoginCallbackView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)
        if code is None or state is None:
            return Response(
                {"message": "Missing code or state"}, status=status.HTTP_400_BAD_REQUEST
            )

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response(
                {"message": "CSRF check failed"}, status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response(
                {"message": "CSRF check failed"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            google_login_flow = GoogleRawLoginFlowService()
            google_tokens = google_login_flow.get_tokens(code=code)

            id_token_decoded = google_tokens.decode_id_token()
            user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

            """
            google user avatar and default user avatar
            """
            user_email = id_token_decoded["email"]

            exp = id_token_decoded["exp"]
            now = int(datetime.now().timestamp())

            """
            check user exist
            if not create a user
            """
            user = User.objects.filter(email=user_email).first()
            if user is None:
                # create user
                create_user_data = {
                    "email": user_email,
                    "image": id_token_decoded["picture"],
                    "type": "google",
                    "password": ''
                }
                create_serializer = UserSerializer(data=create_user_data)
                if create_serializer.is_valid():
                    user = create_serializer.save()
                else:
                    return Response(
                        {
                            "message": "create user from google failed",
                            **create_serializer.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            """
            login logic
            """
            token = login_token_logic(user, valid_seconds=exp - now)

            serializers = UserSerializer(user)

            print(user_email, user_info)

            result = {
                "message": "google oauth2 successfully",
                "token": token,
                **serializers.data,
            }

            """
            id_token_decoded
            {"iss": "https://accounts.google.com","azp": "973500819258-0etd8ouhtgq904uo8p712sr3q0krtdk2.apps.googleusercontent.com","aud": "973500819258-0etd8ouhtgq904uo8p712sr3q0krtdk2.apps.googleusercontent.com","sub": "115314909056023843600","email": "fromsianqian@gmail.com","email_verified": true,"at_hash": "n9JfIKs58hujaQusQustGQ","name": "sian","picture": "https://lh3.googleusercontent.com/a/ACg8ocIReman0S-EsWABKf6Ti3jZn0tME6eVT_z86XlbTnabhV-YVg=s96-c","given_name": "sian","iat": 1718094759,"exp": 1718098359}"""
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            print(e)
            return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
