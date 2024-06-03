from django.shortcuts import render
from rest_framework import viewsets
from .models import User
from .serializers import RegisterSerializer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import BrowsableAPIRenderer
from django.core.mail import send_mail

# Create your views here.


"""
register

params: {
email: email validation
password: using ras encryption
}

"""

"""

send email validation code

params: {
code: using ras encryption
}

"""


@api_view(["POST"])
@renderer_classes([BrowsableAPIRenderer])
def send_vetification_code(request):
    try:
        send_mail(
            subject="notes & todos 😺",
            message="Here is the message.",
            from_email="notetodos@163.com",
            recipient_list=["fromsian@163.com"],
            fail_silently=False,
        )
        print("successfully sentvetification")
        return Response(
            {
                "success": True,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print("fail", e)
        return Response(
            {"success": False, "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""
log in
"""


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
    serializer_class = RegisterSerializer
