from rest_framework import serializers
from utils.mixin.EncryptSerializerMixin import EncryptSerializerMixin
from .models import User


class RegisterSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
        encrypt_fields = ("password",)

