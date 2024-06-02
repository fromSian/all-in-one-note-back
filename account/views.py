from django.shortcuts import render
from rest_framework import viewsets
from .models import User
from .serializers import RegisterSerializer
# Create your views here.


'''
register

params: {
email: email validation
password: using ras encryption
}

'''


'''

send email validation code

params: {
code: using ras encryption
}

'''

'''
log in
'''


'''
log out
'''


'''
change password
'''

'''
change email
'''

'''
change avatar
'''

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer