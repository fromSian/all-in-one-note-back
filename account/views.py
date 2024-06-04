from .models import User
from .serializers import UserSerializer

from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.renderers import BrowsableAPIRenderer

from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken


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
            "success", examples={"success": True, "message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"success": False, "message": "fail"}
        ),
    },
)
@api_view(["POST"])
def register(request):
    try:
        data = request.data

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"success": True, "message": "registered"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                data={"success": False, "message": serializer.error_messages},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        print(e)
        return Response(
            data={"success": False, "message": e.message},
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


@swagger_auto_schema(
    method="POST",
    operation_description="send vertification code to email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "code"],
        properties={
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, description="to email address"
            ),
            "code": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="vertification code",
            ),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            "success", examples={"success": True, "message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"success": False, "message": "fail"}
        ),
    },
)
@api_view(["POST"])
def send_vertification_code(request):
    try:
        email = request.data.get("email")
        code = request.data.get("code")
        if email is None or code is None:
            raise ValidationError("email or code is None")
        email_validator(email)
        code_validator(code)
        send_mail(
            subject="notes & todos 😺",
            message=code,
            from_email="notetodos@163.com",
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(
            {
                "success": True,
                "message": "send vertification code to email success",
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print("fail", e)
        return Response(
            {"success": False, "message": str(e.message)},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
        user = authenticate(username=user_data["email"], password=user_data["password"])
        # if not user or not user.groups.values("name").filter(name="普通用户").exists():
        #     raise ValidationError("用户名或密码错误")
        serializer = UserSerializer(user)
        jwt_token = RefreshToken.for_user(user)
        serializer_data = serializer.data
        print(jwt_token)
        serializer_data["token"] = {
            "access_token": str(jwt_token.access_token),
            "refresh_token": str(jwt_token),
        }
        return Response(
            {"status": True, "message": "登录成功", **serializer_data},
            status=status.HTTP_202_ACCEPTED,
        )

    except Exception as e:
        return Response(
            {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


"""
log out
"""


"""
change password
"""

"""
change email
"""

"""
change avatar
"""


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
