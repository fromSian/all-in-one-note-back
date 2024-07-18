from .models import User
from .serializers import UserSerializer, ImageFileSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import (
    api_view,
    renderer_classes,
    permission_classes,
    parser_classes,
)
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from rest_framework.renderers import BrowsableAPIRenderer

from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException, SMTPSenderRefused, SMTPRecipientsRefused
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import password_changed, validate_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken

from datetime import timedelta

from utils.authentication import check_operation_validation
from utils.file import handle_uploaded_file, crop
from utils.string import random_word
from uuid import uuid4

# Create your views here.


"""
register

params: {
email: email validation
password: using ras encryption
}

"""


@swagger_auto_schema(
    method="POST",
    operation_description="register a new user with emial and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "password"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="to email address"
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="password",
            ),
        },
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            "success", examples={"message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"message": "fail"}
        ),
    },
)
@api_view(["POST"])
def register(request):
    try:
        data = request.data
        data["type"] = "base"

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "registered"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data={"message": serializer.error_messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print(e)
        return Response(
            data={"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print(e)
        return Response(
            data={"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""

send email validation code

params: {
code: using ras encryption
}

"""

email_validator = EmailValidator()


def code_validator(value):
    regex = _lazy_re_compile(r"^[a-zA-Z0-9]{6}")
    regex_matches = regex.search(str(value))
    if not regex_matches:
        raise ValidationError(
            _(
                "not the valid type, please enter a six character string only include letters or numbers."
            ),
            params={"value": value},
        )


def check_email_exist(email):
    return User.objects.filter(email=email).exists()


@swagger_auto_schema(
    method="POST",
    operation_description="send vertification code to email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="to email address"
            ),
            "register": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="is for register"
            ),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            "success", examples={"message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"message": "fail"}
        ),
    },
)
@api_view(["POST"])
def send_code(request):
    try:
        email = request.data.get("email", "")
        register = request.data.get("register", True)
        email_validator(email)
        if register and check_email_exist(email):
            return Response(
                {"message": "email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = random_word(6)
        cache.set(email + "code", code, timeout=3600)  # 1 hour
        flag = send_mail(
            subject="email validation - notes & todos 😺",
            message="",
            html_message="""
            Hi, it is be-notes. glad to have you signed up.
            <p>verification code: <strong>{0}</strong></p>
            <p>this code expires in <strong>1 hour</strong></p>
            <p>please copy and paste this code into the input field in the app.</p>
            """.format(
                code
            ),
            from_email="notetodos@163.com",
            recipient_list=[email],
            fail_silently=True,
        )
        if flag:
            return Response(
                {
                    "message": "send verification code to email success",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "send email failed, please check the email address and try again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print("fail", e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@swagger_auto_schema(
    method="POST",
    operation_description="verify code",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "code"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="to email address"
            ),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="code"),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            "success", examples={"message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"message": "fail"}
        ),
    },
)
@api_view(["POST"])
def verify_code(request):
    try:
        email = request.data.get("email", "")
        email_validator(email)
        enter_code = request.data.get("code", "")
        code_validator(enter_code)
        code = cache.get(email + "code")
        if code == enter_code:
            cache.delete(email + "code")
            return Response(
                {"message": "code is correct"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "code is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print("fail", e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print("fail", e)
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""
create trial user
"""


@api_view(["POST"])
def trial(request):
    try:
        data = {
            "email": "{0}@benotes.com".format(uuid4()),
            "type": "trial",
            "password": "",
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            access_token = login_token_logic(user, 60 * 60 * 1)
            return Response(
                {"message": "trial success", "token": access_token, **serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print("fail", e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print("fail", e)
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


def login_token_logic(user, valid_seconds):
    jwt_token = RefreshToken.for_user(user)
    access_token = str(jwt_token.access_token)
    cache.set(user.email, access_token, valid_seconds)

    return access_token


"""
log in
"""


@swagger_auto_schema(
    method="POST",
    operation_description="log in with email and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "password"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="email address"
            ),
            "password": openapi.Schema(
                type=openapi.TYPE_STRING, description="password"
            ),
        },
    ),
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    try:
        user_data = request.data
        user = authenticate(username=user_data["email"], password=user_data["password"])
        if not user:
            raise ValidationError("Invalid username or password")

        if not user.groups.values("name").filter(name="front").exists():
            raise ValidationError("not accessible for this login")

        if user.type == "google":
            raise ValidationError("please use the sign in with google")

        if user.type == "trial":
            raise ValidationError("sorry, you are not allowed to login")
        serializer = UserSerializer(user)
        access_token = login_token_logic(user, valid_seconds=7 * 24 * 60 * 60)
        serializer_data = serializer.data
        serializer_data["token"] = access_token

        return Response(
            {"message": "log in successfully", **serializer_data},
            status=status.HTTP_202_ACCEPTED,
        )
    except ValidationError as e:
        print(e)
        return Response({"message": e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


"""
log out
"""


def logout_logic(key):
    isDeleted = cache.delete(key) if cache.has_key(key) else True
    return isDeleted


@swagger_auto_schema(
    method="POST",
    operation_description="log out",
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        user = request.user
        if not user:
            return Response({"message": "not login"}, status.HTTP_400_BAD_REQUEST)

        isDeleted = logout_logic(user.email)

        if isDeleted:
            return Response(
                {"message": "logout success"},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            raise Exception("log out failed")
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="verify password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["password"],
            properties={
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="password"
                ),
            },
        ),
        responses={
            status.HTTP_202_ACCEPTED: openapi.Response(
                "success", examples={"message": "success"}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "fail", examples={"message": "fail"}
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        verify password
        """
        try:
            password = request.data.get("password")
            user = request.user
            is_pass = user.check_password(password)
            if is_pass:
                return Response(
                    {"message": "Password verified"},
                    status=status.HTTP_200_OK,
                )
            else:
                raise ValidationError("Invalid password")
        except ValidationError as e:
            print(e)
            return Response(
                {"message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_description="update password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["password"],
            properties={
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="password"
                ),
            },
        ),
        responses={
            status.HTTP_202_ACCEPTED: openapi.Response(
                "success", examples={"message": "success"}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "fail", examples={"message": "fail"}
            ),
        },
    )
    def put(self, request, *args, **kwargs):
        """
        change password
        use old password or email verify

        encrypt params
        params: {
        'expire_time': date time str with time zone
        'action_time': date time str with time zone
        }

        if success log out
        """
        try:
            password = request.data.get("password")
            user = request.user
            user.set_password(password)
            user.save()
            password_changed(password, user=user)
            logout_logic(user.email)
            return Response(
                {"message": "password changed"},
                status=status.HTTP_202_ACCEPTED,
            )
        except ValidationError as e:
            print(e)
            return Response(
                {"message": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""
change email
use old password or email verify
encrypt params
        params: {
        'expire_time': date time str with time zone
        'action_time': date time str with time zone
        }
if success log out
"""


@swagger_auto_schema(
    method="PUT",
    operation_description="change email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email"],
        properties={
            "expire_time": openapi.Schema(
                type=openapi.TYPE_STRING, description="email address"
            ),
            "action_time": openapi.Schema(
                type=openapi.TYPE_STRING, description="email address"
            ),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="email address"
            ),
        },
    ),
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["PUT"])
def email(request):
    try:
        expire_time = request.data.get("expire_time")
        action_time = request.data.get("action_time")
        check_operation_validation(expire_time, action_time)

        email = request.data.get("email")
        user = request.user
        email_bak = user.email

        serializer = UserSerializer(data={"email": email}, instance=user, partial=True)
        if serializer.is_valid():
            serializer.save()
            logout_logic(email_bak)
            return Response(
                {"message": "email updated successfully"},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print(123, e)
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""
change avatar
"""


@swagger_auto_schema(
    method="PUT",
    operation_description="change avatar",
    manual_parameters=[
        openapi.Parameter(
            name="file",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="avatar file",
        ),
        openapi.Parameter(
            name="left",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=True,
            description="left",
        ),
        openapi.Parameter(
            name="upper",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=True,
            description="upper",
        ),
        openapi.Parameter(
            name="right",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=True,
            description="right",
        ),
        openapi.Parameter(
            name="lower",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=True,
            description="lower",
        ),
    ],
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["PUT"])
@parser_classes([parsers.MultiPartParser])
@permission_classes([permissions.IsAuthenticated])
def avatar(request):
    try:
        avatar_file = request.data.get("file", None)
        if avatar_file is None:
            raise ValidationError("avatar file is required")
        user = request.user
        # if user.type == "trial":
        #     raise ValidationError("trial user can't change avatar")
        crop_tuple = (
            float(request.data.get("left", 0)),
            float(request.data.get("upper", 0)),
            float(request.data.get("right", 100)),
            float(request.data.get("lower", 100)),
        )
        file_path = crop(avatar_file, crop_tuple)
        url = request.build_absolute_uri(file_path)
        serializer = UserSerializer(instance=user, data={"image": url}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "avatar changed", **serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""
change bio
"""


@swagger_auto_schema(
    method="PUT",
    operation_description="change bio",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["bio"],
        properties={
            "bio": openapi.Schema(type=openapi.TYPE_STRING, description="bio"),
        },
    ),
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def bio(request):
    try:
        bio = request.data.get("bio", "")
        user = request.user
        serializer = UserSerializer(instance=user, data={"bio": bio}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "bio changed"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""
get account information
"""


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def info(request):
    try:
        user = request.user
        serializer = UserSerializer(instance=user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TestViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


"""
upload avatar image file view
return image_url
"""


@swagger_auto_schema(
    method="POST",
    operation_description="upload avatar file",
    manual_parameters=[
        openapi.Parameter(
            name="file",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True,
            description="avatar file",
        )
    ],
    responses={
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["POST"])
@parser_classes([parsers.MultiPartParser])
def upload_avatar(request):
    try:
        file = request.data.get("file", None)
        if file is None:
            raise ValidationError("avatar file is required")
        serialzer = ImageFileSerializer(data={"file": file})
        if serialzer.is_valid():
            loaded_file = serialzer.validated_data.get("file")
            path = handle_uploaded_file(loaded_file, loaded_file.name)
            print(path)
            return Response(
                {"url": request.build_absolute_uri(path)},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": serialzer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
