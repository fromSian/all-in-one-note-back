from .models import User, Settings
from .serializers import UserSerializer, ImageFileSerializer, SettingsSerializer
from rest_framework.mixins import (
    UpdateModelMixin,
    RetrieveModelMixin,
)
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
from utils.permission import RequestValidPermission
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

from utils.file import handle_uploaded_file, crop
from utils.string import random_word
from utils.encryption import RSAEncryption
from uuid import uuid4
from utils.permission import RequestValidPermission

# Create your views here.

rsa_encryption = RSAEncryption()

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
        data = {
            "email": request.data.get("email"),
            "password": rsa_encryption.decrypt(request.data.get("password")),
            "type": "base",
        }
        print(data["password"])
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": _("sign up successfully")},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data={"message": serializer.errors},
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
                {
                    "message": _(
                        "This email already signed up, please sign in or check your email"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not register and not check_email_exist(email):
            return Response(
                {"message": _("This email does not exist, please register first")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        prev = cache.get(email + "code")
        if prev and cache.ttl(prev) > 59 * 60:
            return Response(
                {"message": _("send too often, please try again after one minute")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = random_word(6)
        cache.set(email + "code", code, timeout=3600)  # 1 hour
        flag = send_mail(
            subject=_("email validation - be markdown notes") + " 😺",
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
                    "message": _("send verification code to email successfully"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": _(
                        "send email failed, please check the email address and try again."
                    )
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
                {"message": _("code verifies successfully")},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": _("code is incorrect")},
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
            setting = Settings.objects.filter(user=user).first()
            if not setting:
                setting = Settings.objects.create(user=user)
            setting_serializer = SettingsSerializer(setting)
            return Response(
                {
                    "message": _("trial successfully"),
                    "token": access_token,
                    **serializer.data,
                    **setting_serializer.data,
                },
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
def login(request):
    try:
        user_data = request.data
        password = rsa_encryption.decrypt(user_data.get("password", ""))
        user = authenticate(username=user_data.get("email", ""), password=password)
        print(user)
        if not user:
            raise ValidationError(_("Invalid email or password"))

        if not user.groups.values("name").filter(name="front").exists():
            raise ValidationError(_("not accessible for front signin"))

        if user.type == "google":
            raise ValidationError(_("please use the sign in with google"))

        if user.type == "trial":
            raise ValidationError(_("sorry, this trial account has destroyed"))
        serializer = UserSerializer(user)
        setting = Settings.objects.filter(user=user).first()
        if not setting:
            setting = Settings.objects.create(user=user)
        setting_serializer = SettingsSerializer(setting)

        access_token = login_token_logic(user, valid_seconds=7 * 24 * 60 * 60)
        serializer_data = serializer.data
        serializer_data["token"] = access_token

        return Response(
            {
                "message": _("sign in successfully"),
                **serializer_data,
                **setting_serializer.data,
            },
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
    isDeleted = cache.expire(key, timeout=8) if cache.has_key(key) else True
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
def logout(request):
    try:
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"message": _("already sign out")}, status.HTTP_400_BAD_REQUEST
            )

        isDeleted = logout_logic(user.email)

        if isDeleted:
            return Response(
                {"message": _("sign out successfully")},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            raise Exception(_("fail to sign out"))
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordView(APIView):
    permission_classes = [RequestValidPermission, permissions.IsAuthenticated]

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
            password = rsa_encryption.decrypt(password)
            user = request.user
            is_pass = user.check_password(password)
            if is_pass:
                return Response(
                    {"message": _("verify password successfully")},
                    status=status.HTTP_200_OK,
                )
            else:
                raise ValidationError(_("wrong password"))
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
            _password = request.data.get("password")
            password = rsa_encryption.decrypt(_password)
            user = request.user
            user.set_password(password)
            user.save()
            password_changed(password, user=user)
            logout_logic(user.email)
            return Response(
                {"message": _("change password successfully")},
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


@swagger_auto_schema(
    method="POST",
    operation_description="update password",
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
def update_password(request):
    try:
        email = request.data.get("email")
        _password = request.data.get("password")
        if not email or not _password:
            raise ValidationError(_("email and password are required"))
        password = rsa_encryption.decrypt(_password)
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError(_("account not found"))
        user.set_password(password)
        user.save()
        password_changed(password, user=user)
        return Response(
            {"message": _("change password successfully")},
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
        email = request.data.get("email")
        user = request.user
        email_bak = user.email

        serializer = UserSerializer(data={"email": email}, instance=user, partial=True)
        if serializer.is_valid():
            serializer.save()
            logout_logic(email_bak)
            return Response(
                {"message": _("update email successfully")},
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
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
def avatar(request):
    try:
        avatar_file = request.data.get("file", None)
        if avatar_file is None:
            raise ValidationError(_("avatar file is required"))
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
                {"message": _("change avatar successfully"), **serializer.data},
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
get account information
"""


@api_view(["GET"])
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
def info(request):
    try:
        user = request.user
        serializer = UserSerializer(instance=user, context={"request": request})
        setting = Settings.objects.filter(user=user).first()
        if not setting:
            setting = Settings.objects.create(user=user)
        setting_serializer = SettingsSerializer(setting)
        return Response(
            {**serializer.data, **setting_serializer.data}, status=status.HTTP_200_OK
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
convert account type to base
"""


@swagger_auto_schema(
    method="POST",
    operation_description="convert account type, trial to base",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "password"],
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="email"),
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
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
def trial_to_base(request):
    try:
        user = request.user
        _password = request.data.get("password", "")
        password = rsa_encryption.decrypt(_password)
        email = request.data.get("email", "")
        email_validator(email)
        if not email or not password:
            return Response(
                {"message": _("email and password is required")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.type == "trial":
            user.email = email
            user.type = "base"
            user.set_password(password)
            user.save()
            password_changed(password, user=user)
            logout_logic(user.email)
            user.save()
            return Response(
                {"message": _("account type converted to official successfully")},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": _("you are not a trial account")},
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


@swagger_auto_schema(
    method="POST",
    operation_description="convert account type, google to base",
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
        status.HTTP_202_ACCEPTED: "success",
        status.HTTP_400_BAD_REQUEST: "fail",
    },
)
@api_view(["POST"])
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
def google_to_base(request):
    try:
        user = request.user
        _password = request.data.get("password", "")
        password = rsa_encryption.decrypt(_password)
        if not password:
            return Response(
                {"message": _("email and password is required")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.type == "google":
            user.type = "base"
            user.set_password(password)
            user.save()
            password_changed(password, user=user)
            logout_logic(user.email)
            user.save()
            return Response(
                {"message": _("account type converted to official successfully")},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": _("you are not a google account")},
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


class SettingView(APIView):
    permission_classes = [RequestValidPermission, permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="update settings",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                "defaultExpanded": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="defaultExpanded"
                ),
                "showExactTime": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="showExactTime"
                ),
                "sortInfo": openapi.Schema(
                    type=openapi.TYPE_STRING, description="sortInfo"
                ),
                "language": openapi.Schema(
                    type=openapi.TYPE_STRING, description="language"
                ),
                "theme": openapi.Schema(type=openapi.TYPE_STRING, description="theme"),
            },
        ),
        responses={
            status.HTTP_202_ACCEPTED: SettingsSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "fail", examples={"message": "fail"}
            ),
        },
    )
    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            settings = Settings.objects.filter(user=user).first()
            if not settings:
                raise ValidationError(_("no settings record found"))
            serializer = SettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
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


class TestViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [RequestValidPermission]


@swagger_auto_schema(
    method="DELETE",
    operation_description="delete user",
)
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
@api_view(["DELETE"])
def delete_user(request):
    try:
        user = request.user
        user.delete()
        logout_logic(user.email)
        return Response(
            {"message": _("user deleted successfully")},
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
