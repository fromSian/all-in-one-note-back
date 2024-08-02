import google_auth_oauthlib.flow
from django.shortcuts import redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, serializers, permissions
import requests
import os
import jwt
from datetime import datetime
from account.views import login_token_logic
from account.serializers import UserSerializer
from account.models import User
from rest_framework.exceptions import ValidationError
from django.http import HttpResponseRedirect
from urllib.parse import urlencode

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
domain = settings.BASE_BACKEND_URL
API_URI = "account/google/callback"
callback_uri = f"{domain}{API_URI}"


@permission_classes([permissions.AllowAny])
@api_view(["get"])
def access_view(request):
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
        )
        flow.redirect_uri = callback_uri
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        request.session["state"] = state

        return redirect(authorization_url)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def get_user_info(token):
    response = requests.get(GOOGLE_USER_INFO_URL, params={"access_token": token})

    if not response.ok:
        raise Exception("Failed to obtain user info from Google")

    return response.json()


def decode_id_token(id_token):
    decoded_tokem = jwt.decode(jwt=id_token, options={"verify_signature": False})
    return decoded_tokem


class InputSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    state = serializers.CharField(required=False)


@permission_classes([permissions.AllowAny])
@api_view(["get"])
def callback_view(request):
    try:
        input_serializer = InputSerializer(data=request.query_params)
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
        state = request.session.get("state")
        if not state:
            return Response(
                {"message": "not valid request"}, status=status.HTTP_400_BAD_REQUEST
            )
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = callback_uri
        authorization_response = request.build_absolute_uri(request.get_full_path())
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        credentials_dict = credentials_to_dict(credentials)
        user_info = get_user_info(credentials.token)
        user_email = user_info["email"]
        id_token_decoded = decode_id_token(credentials.id_token)
        exp = id_token_decoded["exp"]
        now = int(datetime.now().timestamp())

        user = User.objects.filter(email=user_email).first()
        if user is None:
            # create user
            create_user_data = {
                "email": user_email,
                "image": user_info["picture"],
                "type": "google",
                "password": "",
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

        query_params = urlencode(
            {
                "token": token,
            }
        )
        url = f"{settings.GOOGLE_OAUTH2_REDIRECT_SUCCESS_URL}?{query_params}"
        return HttpResponseRedirect(url)
    except ValidationError as e:
        print(e)
        query_params = urlencode({"message": e.message})
        url = f"{settings.GOOGLE_OAUTH2_REDIRECT_FAIL_URL}?{query_params}"
        return HttpResponseRedirect(url)
    except Exception as e:
        print(e)
        query_params = urlencode({"message": str(e)})
        url = f"{settings.GOOGLE_OAUTH2_REDIRECT_FAIL_URL}?{query_params}"
        return HttpResponseRedirect(url)


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
